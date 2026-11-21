"""Model-directed, bounded read-only retrieval with auditable evidence delivery."""

import json
from contextlib import ExitStack
from pathlib import Path
from tempfile import TemporaryDirectory

from .agent import AgentLimits, RequestBudget, ResearchAgent

__all__ = ["AgenticRAGChain"]


class AgenticRAGChain:
    """Adapt ResearchAgent's real execution trace to the comparison-chain API.

    With no explicit output directory, artifacts are caller-independent and temporary: the
    returned trace remains complete, but its artifact paths are removed when ``retrieve`` returns.
    """

    def __init__(self, retrieval, model, *, domain=None, limits=None, budget=None, fault=None):
        self.retrieval, self.model = retrieval, model
        self.domain, self.limits = domain, limits or AgentLimits()
        self.budget, self.fault = budget or RequestBudget(), fault

    @staticmethod
    def _round_diagnostics(round_data, step):
        """Retain rank diagnostics from the successful tool's frozen observation."""
        diagnostics = json.loads(step["observation"]).get("diagnostics", {})
        scores, reasons = {}, {}
        for channel, detail in diagnostics.get("channels", {}).items():
            for item in detail.get("ranking", []):
                chunk_id = item["chunk_id"]
                scores.setdefault(chunk_id, {})[channel] = item["score"]
                reasons.setdefault(chunk_id, []).append(
                    {"channel": channel, "rank": item["rank"]}
                )
        fusion = {
            item["chunk_id"]: item
            for item in diagnostics.get("fusion", [])
            if item.get("retained", True)
        }
        detail = {
            chunk_id: {
                "chunk_id": chunk_id,
                "scores": scores.get(chunk_id, {}),
                "rrf_score": fusion.get(chunk_id, {}).get("rrf_score"),
                "reasons": reasons.get(chunk_id, []),
            }
            for chunk_id in round_data["candidate_ids"]
        }
        ranked = [
            {**item, **detail.get(item["chunk_id"], {})}
            for item in diagnostics.get("final", [])
        ]
        return detail, ranked

    @staticmethod
    def _diagnostics(trace):
        candidates = {}
        latest_ranked = []
        steps = {step["id"]: step for step in trace["steps"]}
        for round_number, round_data in enumerate(trace["retrieval_rounds"], 1):
            step = steps[round_data["step_id"]]
            round_candidates, latest_ranked = AgenticRAGChain._round_diagnostics(round_data, step)
            for chunk_id, detail in round_candidates.items():
                candidates.setdefault(chunk_id, detail)
            for item in latest_ranked:
                item["retrieval_round"] = round_number
        return list(candidates.values()), latest_ranked

    def retrieve(
        self,
        query,
        *,
        run_id="agentic-interactive",
        case_id="interactive",
        output_dir=None,
    ):
        if output_dir is None:
            workspace = TemporaryDirectory(prefix="infra-rag-agentic-")
            output = Path(workspace.name) / "run"
        else:
            workspace = None
            output = Path(output_dir)
        with ExitStack() as stack:
            if workspace is not None:
                stack.callback(workspace.cleanup)
            # Keep construction inside the temporary workspace so failures also clean it up.
            agent = ResearchAgent(
                self.retrieval,
                self.model,
                domain=self.domain,
                limits=self.limits,
                budget=self.budget,
                fault=self.fault,
            )
            trace = agent.run(
                query,
                output,
                case_id=case_id,
                run_id=run_id,
                config_id="agentic_rag",
            )
            # The complete trace preserves round-local delivery. At the top level expose the
            # cumulative _pack state, which is also the evidence seen by the last model request.
            # Re-packing here avoids mutating ResearchAgent's frozen trace/artifact schema.
            observed = {}
            for step in trace["steps"]:
                if step["kind"] == "tool" and step["status"] == "ok":
                    for item in json.loads(step["observation"]).get("evidence", []):
                        observed[item["id"]] = item
            trace["evidence"]["delivered"] = agent._pack(observed)
            candidates, ranked = self._diagnostics(trace)
            evidence = trace["evidence"]
            return {
                "chain": "agentic_rag",
                "query": query,
                "domain": self.domain,
                "index_fingerprint": self.retrieval.index_fingerprint,
                "evidence": evidence,
                "candidates": candidates,
                "ranked": ranked,
                "trace": trace,
                "latency_ms": trace["latency_ms"],
                "final": trace["final"],
            }
