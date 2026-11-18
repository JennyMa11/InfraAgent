"""Freeze/replay P0 delivery on existing dev traces, never treating delivery as correctness."""

import argparse
import json
import os
import shutil
from collections import defaultdict
from pathlib import Path

from operation_log import ROOT, record_operation

from infra_rag.benchmarking import digest, write_new
from infra_rag.complete_context import pack_complete_context
from infra_rag.context import pack_context
from infra_rag.models import Chunk, Hit

ORIGINAL = ROOT / "data/user-badcases-v1/run-20261029"
INDEX = ROOT / "data/local-web/index/index.json"
CHECKS = {
    "bc01-t1": ("595eb462cf959a1cd6dc6bda", ["216", "414"]),
    "bc02-t1": ("cc6ac7f5dbad196007268658", ["512+64", "NoPE"]),
    "bc07-t1": ("b0a77153b9384a1c880c5d22", ["404", "260"]),
    "bc09-t1": ("78c3915cc5e2157f8a2be98c", ["10752", "8192", "2560"]),
    "bc10-t1": ("2a37a25b31d13cf693b09c3f", ["adapter"]),
    "bc14-t2": ("78c3915cc5e2157f8a2be98c", ["53.6", "快照"]),
}


def load(path):
    return json.loads(path.read_text())


def freeze(out):
    if out.exists():
        raise ValueError("Fresh output directory required")
    out.mkdir(parents=True)
    inputs = sorted((ORIGINAL / "outputs").glob("main-bc*-t*.json"))
    inputs = [p for p in inputs if not p.name.endswith(".sha256.json")]
    assert len(inputs) == 16
    code = [Path(__file__).resolve(), *sorted((ROOT / "src/infra_rag").glob("*.py"))]
    for path in code:
        target = out / "implementation" / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    write_new(
        out / "protocol.json",
        {
            "kind": "Component replay of frozen development candidates; no model calls",
            "inputs": {str(p): digest(p) for p in inputs},
            "index": {"path": str(INDEX), "sha256": digest(INDEX)},
            "implementation": {str(p): digest(p) for p in code},
            "checks": CHECKS,
            "tokens": 1200,
            "characters": 4000,
            "repetitions": 1,
            "selection_pool": 15,
            "primary_gate": ["bc02-t1", "bc09-t1"],
            "adoption": "Off by default. Delivery gates cannot establish semantic correctness.",
            "human_review": "pending",
            "holdout_read": False,
        },
    )


def run(out):
    p = load(out / "protocol.json")
    for path, sha in {
        **p["inputs"],
        **p["implementation"],
        p["index"]["path"]: p["index"]["sha256"],
    }.items():
        assert digest(path) == sha, path
    os.environ["HF_HUB_OFFLINE"] = "1"
    from infra_rag.encoding import BGEEncoder

    # Match SentenceTransformer's tokenizer configuration, not AutoTokenizer defaults.
    count = BGEEncoder("BAAI/bge-small-zh-v1.5").token_length

    chunks = {c["id"]: Chunk(**c) for c in load(Path(p["index"]["path"]))["chunks"]}
    parents = defaultdict(list)
    for c in chunks.values():
        parents[c.parent_id].append(c)
    rows = []
    for path in p["inputs"]:
        original = load(Path(path))
        d = original["server_record"]["retrieval"][0]
        scores = {r["chunk_id"]: r["rerank_score"] for r in d["diagnostics"]["final"]}
        ranked = [
            Hit(chunks[cid], 0.0, rerank_score=scores[cid])
            for cid in d["diagnostics"]["ranked_ids"]
        ]
        baseline = pack_context(ranked[:5], parents, count, 1200, 4000)
        expected = [(e["chunk_id"], e["content"]) for e in d["evidence"]]
        actual = [(e["chunk_id"], e["content"]) for e in baseline["evidence"]]
        assert actual == expected, f"Cannot reproduce prefix baseline: {path}"
        query = d["query"]
        packed = pack_complete_context(ranked[:5], ranked, query, count, 1200, 4000)
        assert packed["used_tokens"] <= 1200 and packed["used_characters"] <= 4000
        assert all(e["content"] == chunks[e["chunk_id"]].content for e in packed["evidence"])
        key = f"{original['case_id']}-t{original['turn']}"
        check = p["checks"].get(key)

        def delivered(context, check=check):
            return (
                any(
                    e["chunk_id"] == check[0]
                    and all(term in e["content"].replace(",", "") for term in check[1])
                    for e in context["evidence"]
                )
                if check
                else None
            )

        row = {
            "case": key,
            "baseline_reproduced": True,
            "baseline_required_body": delivered(baseline),
            "complete_required_body": delivered(packed),
            "baseline": baseline,
            "complete": packed,
        }
        write_new(out / "outputs" / f"{key}.json", row)
        rows.append({k: v for k, v in row.items() if k not in {"baseline", "complete"}})
    write_new(
        out / "results.json", {"rows": rows, "answer_correctness": None, "actual_model_calls": 0}
    )
    write_new(
        out / "manifest.json",
        {str(f.relative_to(out)): digest(f) for f in out.rglob("*") if f.is_file()},
    )
    print(json.dumps(rows, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["freeze", "run"])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    (freeze if args.phase == "freeze" else run)(args.out)
    record_operation(
        f"完整证据打包组件实验 {args.phase}",
        "冻结候选与预算验证P0交付",
        f"产物 {args.out}；组件回放不表示答案正确性",
    )


if __name__ == "__main__":
    main()
