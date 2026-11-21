"""Explicit experimental RAG chains and paired, evidence-aware comparison reports.

The production ``/chat`` route is intentionally not changed by this module.  Only the
question and optional domain are passed to a chain; labels remain in the evaluator.
"""

import json
import math
import statistics
from pathlib import Path
from time import perf_counter

from .benchmarking import canonical_hash, create_run, digest, write_new
from .evaluation import metrics, resolve_alternatives, resolve_spans

CHAIN_NAMES = ("baseline", "graph_rag", "agentic_rag")
METRIC_NAMES = ("recall", "precision", "f1", "mrr", "ndcg")


def _elapsed(started):
    return round((perf_counter() - started) * 1000, 3)


def _chunk_id(item):
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        value = item.get("chunk_id", item.get("id"))
        if isinstance(value, str):
            return value
    raise ValueError("chain diagnostics must contain stable chunk IDs")


def _evidence_parts(result):
    """Adapt both the baseline/graph list and the agent evidence ledger."""
    evidence = result.get("evidence", [])
    if isinstance(evidence, dict):
        return (
            evidence.get("delivered", []),
            evidence.get("candidate_ids", []),
            evidence.get("ranked_ids", []),
        )
    return evidence, result.get("candidates", []), result.get("ranked", [])


def delivered_evidence(result):
    evidence = _evidence_parts(result)[0]
    if not isinstance(evidence, list) or any(not isinstance(row, dict) for row in evidence):
        raise ValueError("chain evidence must be a delivered-evidence list or ledger")
    return evidence


class HybridRAGChain:
    """The existing hybrid retrieval path, exposed through the experiment contract."""

    def __init__(self, retrieval, *, top_k=None):
        self.retrieval = retrieval
        self.top_k = top_k or retrieval.settings.answer_top_k

    def retrieve(self, query, *, domain=None):
        started = perf_counter()
        diagnostics, context = {}, {}
        hits = self.retrieval.search(
            query,
            top_k=self.top_k,
            domain=domain,
            strategy="hybrid",
            diagnostics=diagnostics,
            context_pack=context,
        )
        candidates = diagnostics.get("candidates", [])
        ranked = diagnostics.get("returned_chunk_ids", [hit.chunk.id for hit in hits])
        return {
            "chain": "baseline",
            "query": query,
            "domain": domain,
            "index_fingerprint": self.retrieval.index_fingerprint,
            "evidence": context.get("evidence", []),
            "candidates": [{"chunk_id": cid} for cid in candidates],
            "ranked": [{"chunk_id": cid} for cid in ranked],
            "trace": [
                {
                    "step": "hybrid_retrieve",
                    "duration_ms": _elapsed(started),
                    "diagnostics": diagnostics,
                    "context_budget": {
                        key: value
                        for key, value in context.items()
                        if key not in {"evidence", "context"}
                    },
                }
            ],
            "latency_ms": _elapsed(started),
        }


class OfflineAgentModel:
    """Deterministic plumbing fixture, never evidence of live model quality."""

    model = "deterministic-search-and-answer-v1"
    provider = "offline_fixture"
    offline = True

    def __init__(self):
        self.last_call = None

    def generate(self, messages):
        self.last_call = {"usage": {"input_tokens": 0, "output_tokens": 0}}
        state = json.loads(messages[-1]["content"])
        if not state["evidence"]:
            return json.dumps(
                {"action": "tool", "name": "search", "arguments": {"query": state["task"]}}
            )
        evidence = state["evidence"][0]
        return json.dumps(
            {
                "action": "final",
                "status": "answered",
                "answer": f"{evidence['content']} [{evidence['id']}]",
                "claims": [
                    {
                        "id": "fixture-claim",
                        "text": evidence["content"],
                        "evidence_ids": [evidence["id"]],
                    }
                ],
            },
            ensure_ascii=False,
        )


def build_chain(name, retrieval, *, model=None, top_k=None):
    """Lazy imports keep baseline-only runs independent of the other chains."""
    if name == "baseline":
        return HybridRAGChain(retrieval, top_k=top_k)
    if name == "graph_rag":
        from .graph_rag import GraphRAGChain

        return GraphRAGChain(retrieval, top_k=top_k or retrieval.settings.answer_top_k)
    if name == "agentic_rag":
        if model is None:
            raise ValueError("agentic_rag requires an explicit live or offline model")
        from .agentic_rag import AgenticRAGChain

        return AgenticRAGChain(retrieval, model)
    raise ValueError(f"unknown RAG chain: {name}; choose from {', '.join(CHAIN_NAMES)}")


def prepare_cases(retrieval, dataset, dataset_path, label="source"):
    """Resolve frozen labels independently, without exposing them to a chain."""
    if label not in {"source", "chunk", "parent"}:
        raise ValueError("label must be source, chunk or parent")
    path = Path(dataset_path)
    if not isinstance(dataset, list) or not dataset:
        raise ValueError("comparison dataset must be a nonempty JSON list")
    if label == "chunk" and all("relevant_spans" in item for item in dataset):
        dataset = resolve_spans(retrieval, dataset, path.parent)
        if all("evidence_alternatives" in item for item in dataset):
            dataset = resolve_alternatives(retrieval, dataset, path.parent)
    cases, ids = [], set()
    for item in dataset:
        if not isinstance(item, dict) or not isinstance(item.get("query"), str):
            raise ValueError("every comparison case requires a query")
        case_id = item.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in ids:
            raise ValueError("comparison case IDs must be unique nonempty strings")
        ids.add(case_id)
        relevant = item.get("relevant")
        if not isinstance(relevant, list) or not relevant:
            raise ValueError(f"{case_id}: comparison currently requires labeled relevant items")
        if label == "source":
            relevant = [
                str((path.parent / value).resolve()) if not Path(value).is_absolute() else value
                for value in relevant
            ]
        elif not all(isinstance(value, str) for value in relevant):
            raise ValueError(f"{case_id}: chunk/parent labels must be strings")
        cases.append(
            {
                "id": case_id,
                "query": item["query"],
                "domain": item.get("domain"),
                "relevant": relevant,
                "group_id": item.get("group_id", case_id),
                "evidence_alternatives": item.get("evidence_alternatives"),
            }
        )
    return cases


def _label_for_chunk(chunk, label):
    return chunk.id if label == "chunk" else chunk.parent_id if label == "parent" else chunk.source


def _label_for_evidence(row, label):
    if label == "chunk":
        return row.get("chunk_id")
    if label == "parent":
        return row.get("parent_id")
    return row.get("source")


def evidence_integrity(retrieval, evidence):
    """Check actual delivered text against indexed chunks and frozen source hashes."""
    by_id = {chunk.id: chunk for chunk in retrieval.chunks}
    failures = []
    for row in evidence:
        chunk = by_id.get(row.get("chunk_id"))
        if chunk is None:
            failures.append({"chunk_id": row.get("chunk_id"), "error": "unknown_chunk"})
            continue
        for field in ("source", "parent_id", "locator"):
            if row.get(field) != getattr(chunk, field):
                failures.append({"chunk_id": chunk.id, "error": f"{field}_mismatch"})
        content = row.get("content")
        if not isinstance(content, str) or not content or content not in chunk.content:
            failures.append({"chunk_id": chunk.id, "error": "delivered_text_not_in_source_chunk"})
        try:
            if digest(chunk.source) != retrieval.source_manifest[chunk.source]["sha256"]:
                failures.append({"chunk_id": chunk.id, "error": "source_hash_mismatch"})
        except (KeyError, OSError, TypeError):
            failures.append({"chunk_id": chunk.id, "error": "source_unavailable_or_unregistered"})
    return {
        "status": "valid" if not failures else "invalid",
        "checked": len(evidence),
        "failures": failures,
    }


def _empty_metrics():
    return {name: None for name in METRIC_NAMES}


def evaluate_result(retrieval, case, result, *, label, k):
    evidence = delivered_evidence(result)
    _, candidates, ranked = _evidence_parts(result)
    by_id = {chunk.id: chunk for chunk in retrieval.chunks}
    candidate_labels = [_label_for_chunk(by_id[_chunk_id(row)], label) for row in candidates]
    ranked_labels = [_label_for_chunk(by_id[_chunk_id(row)], label) for row in ranked]
    delivered_labels = [_label_for_evidence(row, label) for row in evidence]
    if any(value is None for value in delivered_labels):
        raise ValueError("delivered evidence lacks the requested label")
    integrity = evidence_integrity(retrieval, evidence)
    return {
        "label": label,
        "k": k,
        "candidate": {
            **metrics(candidate_labels, case["relevant"], k),
            "returned": len(candidate_labels),
        },
        "ranked": {
            **metrics(ranked_labels, case["relevant"], k),
            "returned": len(ranked_labels),
        },
        "delivered": {
            **metrics(delivered_labels, case["relevant"], k),
            "returned": len(delivered_labels),
            "truncated": sum(bool(row.get("truncated")) for row in evidence),
        },
        "evidence_integrity": integrity,
        "answer_review": {
            "fact_correct": None,
            "citation_support": None,
            "status": "independent_review_required",
        },
    }


def _resource_usage(chain, result):
    if chain != "agentic_rag":
        return {
            "model_requests": 0,
            "tool_calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "model_cost_usd": 0,
        }
    trace = result.get("trace", {})
    measurement = trace.get("measurement", {})
    resources = trace.get("resources", {})
    return {
        "model_requests": measurement.get("model_requests"),
        "tool_calls": measurement.get("actual_tool_calls"),
        "input_tokens": resources.get("input_tokens"),
        "output_tokens": resources.get("output_tokens"),
        "model_cost_usd": resources.get("model_cost_usd"),
    }


def _error_result(chain, case, exc, latency_ms):
    return {
        "chain": chain,
        "query": case["query"],
        "domain": case.get("domain"),
        "status": "error",
        "error_type": type(exc).__name__,
        "error": str(exc)[:500],
        "latency_ms": latency_ms,
        "evidence": [],
        "candidates": [],
        "ranked": [],
        "trace": [],
        "evaluation": {
            "candidate": _empty_metrics(),
            "ranked": _empty_metrics(),
            "delivered": _empty_metrics(),
            "evidence_integrity": {"status": "not_evaluated", "checked": 0},
            "answer_review": {"fact_correct": None, "status": "not_evaluated"},
        },
    }


def _percentile(values, percentile):
    return values[max(0, math.ceil(percentile * len(values)) - 1)]


def summarize(results, cases):
    summaries = {}
    for chain in CHAIN_NAMES:
        rows = [
            row["results"][chain]
            for row in results
            if chain in row["results"] and row["results"][chain]["status"] == "ok"
        ]
        attempted = [row["results"][chain] for row in results if chain in row["results"]]
        if not attempted:
            continue
        summary = {
            "planned": len(cases),
            "executed": len(attempted),
            "succeeded": len(rows),
            "failed": len(attempted) - len(rows),
            "latency_p50_ms": None,
            "latency_p95_ms": None,
        }
        latencies = sorted(row["latency_ms"] for row in attempted)
        summary["latency_p50_ms"] = statistics.median(latencies)
        summary["latency_p95_ms"] = _percentile(latencies, 0.95)
        for stage in ("candidate", "ranked", "delivered"):
            summary[stage] = {
                name: statistics.mean(row["evaluation"][stage][name] for row in rows)
                if rows
                else None
                for name in METRIC_NAMES
            }
        resources = [_resource_usage(chain, row) for row in attempted]
        summary["resources"] = (
            {
                key: sum(row[key] for row in resources)
                if all(row[key] is not None for row in resources)
                else None
                for key in resources[0]
            }
            if resources
            else {}
        )
        if chain == "agentic_rag":
            summary["agent_status"] = {
                status: sum(row.get("agent_status") == status for row in rows)
                for status in ("answered", "insufficient_evidence", "escalate", "tool_error")
            }
        summaries[chain] = summary
    return summaries


class RAGComparisonRunner:
    """Run selected chains serially on one frozen index and one shared evidence budget."""

    def __init__(self, retrieval, *, chains=CHAIN_NAMES, model=None, top_k=None):
        names = tuple(dict.fromkeys(chains))
        if not names or any(name not in CHAIN_NAMES for name in names):
            raise ValueError(f"chains must be selected from {', '.join(CHAIN_NAMES)}")
        self.retrieval, self.chains = retrieval, names
        self.top_k = top_k or retrieval.settings.answer_top_k
        if not 1 <= self.top_k <= 100:
            raise ValueError("comparison top_k must be in 1..100")
        self.implementations = {
            name: build_chain(name, retrieval, model=model, top_k=self.top_k) for name in names
        }
        if "agentic_rag" in self.implementations:
            self.model = self.implementations["agentic_rag"].agent.model

    def run_case(self, case, *, output_dir=None, run_id="comparison", repetition=1):
        results = {}
        for name in self.chains:
            started = perf_counter()
            try:
                kwargs = {"domain": case.get("domain")}
                if name == "agentic_rag":
                    if output_dir is None:
                        raise ValueError("agentic comparison requires an explicit output_dir")
                    kwargs.update(
                        run_id=run_id,
                        case_id=case["id"],
                        output_dir=Path(output_dir) / name,
                    )
                raw = self.implementations[name].retrieve(case["query"], **kwargs)
                if raw.get("index_fingerprint") != self.retrieval.index_fingerprint:
                    raise ValueError("chain used a different index fingerprint")
                result = dict(raw)
                result["latency_ms"] = _elapsed(started)
                result["status"] = "ok"
                if name == "agentic_rag":
                    result["agent_status"] = raw.get("final", {}).get("status")
                if case.get("relevant"):
                    result["evaluation"] = evaluate_result(
                        self.retrieval, case, raw, label=case["label"], k=self.top_k
                    )
                else:
                    result["evaluation"] = None
            except Exception as exc:
                result = _error_result(name, case, exc, _elapsed(started))
            results[name] = result
        return {"id": case["id"], "group_id": case["group_id"], "results": results}

    def compare(
        self,
        cases,
        output_dir,
        *,
        dataset_path=None,
        run_id="comparison",
        label="source",
        require_complete=False,
    ):
        prepared = [{**case, "label": label} for case in cases]
        manifest = {
            "run_id": run_id,
            "protocol": "paired-rag-chains-v1",
            "scope": "retrieval_and_optional_agent_answer_not_universal_end_to_end",
            "chains": list(self.chains),
            "label": label,
            "top_k": self.top_k,
            "index_fingerprint": self.retrieval.index_fingerprint,
            "configuration": self.retrieval.status(),
            "evidence_budget": {
                "tokens": self.retrieval.settings.context_tokens,
                "characters": self.retrieval.settings.context_chars,
            },
            "dataset_sha256": digest(dataset_path) if dataset_path else canonical_hash(prepared),
            "dataset_case_sha256": canonical_hash(prepared),
            "cases": [
                {"id": case["id"], "group_id": case["group_id"], "domain": case.get("domain")}
                for case in prepared
            ],
            "semantic_review": "required; fact correctness and citation support remain null",
            "timing": "serial wall time including failures; graph cache may be warm after case one",
            "model": (
                self.model.configuration()
                if hasattr(self, "model") and hasattr(self.model, "configuration")
                else {
                    "name": getattr(getattr(self, "model", None), "model", None),
                    "provider": getattr(getattr(self, "model", None), "provider", None),
                    "offline_fixture": getattr(getattr(self, "model", None), "offline", False),
                }
            ),
        }
        run_dir = create_run(output_dir, manifest)
        rows = []
        for case in prepared:
            case_dir = run_dir / "cases" / case["id"]
            case_dir.mkdir(parents=True)
            row = self.run_case(case, output_dir=case_dir, run_id=run_id)
            rows.append(row)
            write_new(case_dir / "result.json", row)
        report = {
            **manifest,
            "summary": summarize(rows, prepared),
            "results": rows,
        }
        write_new(run_dir / "report.json", report)
        if require_complete and any(
            row["results"][name]["status"] != "ok" for row in rows for name in self.chains
        ):
            raise RuntimeError(f"incomplete comparison preserved at {run_dir / 'report.json'}")
        return report
