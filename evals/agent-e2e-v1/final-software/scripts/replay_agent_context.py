"""Isolate context ordering using recorded tool returns; no search or model generation."""

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

from sentence_transformers import SentenceTransformer

from infra_rag.agent import ResearchAgent
from infra_rag.benchmarking import digest, write_new


def coverage(case, delivered):
    groups = case["evidence_alternatives"]
    return max(
        sum(
            any(
                e["source"] == s["source"]
                and e["sha256"] == s["sha256"]
                and e["locator"] == s["locator"]
                and s["text"] in e["content"]
                for e in delivered
            )
            for s in group
        )
        / len(group)
        for group in groups
    )


def replay(run):
    freeze = json.loads((run / "freeze.json").read_text())
    code = "src/infra_rag/agent.py"
    assert digest(Path(__file__).resolve().parents[1] / code) == freeze["implementation"][code]
    tokenizer = SentenceTransformer(
        freeze["settings"]["embedding_model"], local_files_only=True
    ).tokenizer
    encoder = SimpleNamespace(
        token_length=lambda t: len(tokenizer.encode(t, add_special_tokens=False))
    )
    service = SimpleNamespace(
        _encoder=lambda: encoder,
        settings=SimpleNamespace(
            context_chars=freeze["settings"]["context_chars"],
            context_tokens=freeze["settings"]["context_tokens"],
        ),
    )
    agent = ResearchAgent(service, SimpleNamespace())
    cases = {c["id"]: c for c in map(json.loads, (run / "cases.jsonl").read_text().splitlines())}
    rows = []
    for cid in ("agent-003", "agent-004", "agent-005", "agent-010"):
        trace = json.loads((run / cid / "trace.json").read_text())
        accumulated, latest = {}, []
        for step in trace["steps"]:
            if step["kind"] != "tool" or step["status"] != "ok":
                continue
            result = json.loads(step["observation"])
            latest = result["evidence"]
            for e in latest:
                accumulated[e["id"]] = e
        actual = agent._pack(accumulated)
        assert actual == trace["evidence"]["delivered"]
        reordered = {e["id"]: accumulated[e["id"]] for e in latest}
        reordered.update({cid: e for cid, e in accumulated.items() if cid not in reordered})
        alternate = agent._pack(reordered)
        rows.append(
            {
                "case_id": cid,
                "actual_coverage": coverage(cases[cid], actual),
                "latest_first_coverage": coverage(cases[cid], alternate),
                "actual_ids": [e["id"] for e in actual],
                "latest_first_ids": [e["id"] for e in alternate],
                "same_budgets": True,
                "exact_actual_replay": True,
            }
        )
    result = {
        "provenance": "post_run_mechanical_diagnostic_only",
        "rows": rows,
        "new_model_requests": 0,
        "new_search_calls": 0,
        "note": "Only evidence queue order changes. No answer or production improvement claim.",
    }
    write_new(run / "context-replay.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    print(json.dumps(replay(args.run.resolve()), ensure_ascii=False))


if __name__ == "__main__":
    main()
