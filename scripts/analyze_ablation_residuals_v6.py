"""Explain the remaining v6 failures with frozen bodies and real tokenizer budgets."""

import argparse
import json
from pathlib import Path

from infra_rag.benchmarking import digest
from infra_rag.chunking import stable_id


def analyze(run):
    root = Path(__file__).resolve().parents[1]
    protocol = json.loads((run / "protocol.json").read_text())
    path = root / protocol["directory"] / "chunks.json"
    assert digest(path) == protocol["chunks_sha256"]
    chunks = {c["id"]: c for c in json.loads(path.read_text())}
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        protocol["models"]["embedding"]["path"],
        local_files_only=True,
        **protocol["tokenizer_options"],
    )
    rows = [json.loads(line) for line in (run / "rows.jsonl").read_text().splitlines()]
    arm = json.loads((run / "decision.json").read_text())["context_arm"]
    traces = []
    for r in rows:
        if r["arm"] != arm or not r["answerable"] or r["delivered"]["complete"]:
            continue
        gold = {
            cid
            for a in r["resolved_gold"]["evidence_alternatives"]
            for requirement in a["requirements"]
            for cid in requirement
        }
        ranks = {h["chunk_id"]: h for h in r["diagnostics"]["final"]}
        details = []
        for cid in sorted(gold):
            c = chunks[cid]
            header = f"[E{stable_id(cid)}] {c['heading']}\n"
            combined = "\n\n".join([r["context"]["context"], header + c["content"]])
            n = len(tokenizer.encode(combined, add_special_tokens=False))
            details.append(
                {
                    "chunk_id": cid,
                    "rank": ranks.get(cid, {}).get("rank"),
                    "rerank_score": ranks.get(cid, {}).get("rerank_score"),
                    "candidate": cid in r["diagnostics"]["candidates"],
                    "eligible": cid in r["packing_trace"]["eligible_ids"],
                    "selected": cid in r["selected_ids"],
                    "body_characters": len(c["content"]),
                    "fits_if_appended": n <= 1200 and len(combined) <= 4000,
                    "appended_tokens": n,
                    "appended_characters": len(combined),
                    "locator": c["locator"],
                }
            )
        traces.append(
            {
                "dataset": r["dataset"],
                "id": r["id"],
                "query": r["query"],
                "candidate_complete": r["candidate_complete"],
                "packing_pool_complete": r["packing_pool_complete"],
                "selected_complete": r["selected_complete"],
                "selected_count": len(r["selected_ids"]),
                "used_tokens": r["context"]["used_tokens"],
                "gold_details": details,
            }
        )
    result = {
        "strategy": arm,
        "tokenizer_options": protocol["tokenizer_options"],
        "postprocessor_sha256": digest(Path(__file__)),
        "failures": traces,
    }
    (run / "residual-failure-traces.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    )
    for r in traces:
        if r["packing_pool_complete"]:
            print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run", type=Path, default=Path("evals/merged-corpus-v2/budget-ablation-v6/run-20261003")
    )
    analyze(parser.parse_args().run.resolve())
