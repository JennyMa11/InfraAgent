"""Analyze paired frozen-candidate routing runs without modifying evidence labels."""

import argparse
import json
from pathlib import Path

from infra_rag.benchmarking import canonical_hash, digest

PAIRS = {
    "rerank_language_with_english_recall": (
        "recall_en_rerank_en",
        "recall_en_rerank_by_collection",
    ),
    "rerank_language_with_chinese_recall": (
        "recall_zh_rerank_en",
        "recall_zh_rerank_by_collection",
    ),
    "recall_language_with_english_rerank": ("recall_en_rerank_en", "recall_zh_rerank_en"),
    "recall_language_with_collection_rerank": (
        "recall_en_rerank_by_collection",
        "recall_zh_rerank_by_collection",
    ),
    "version_scope": ("recall_zh_rerank_en", "version_all"),
    "metadata_input": ("version_all", "version_all_metadata"),
}


def analyze(rows, run):
    indexed = {(r["dataset"], r["arm"], r["id"]): r for r in rows}
    if len(indexed) != len(rows):
        raise ValueError("Duplicate evaluation rows")
    result = {}
    for dataset in ("official", "repository"):
        for name, (before, after) in PAIRS.items():
            pairs = [
                (row, indexed[dataset, after, qid])
                for (ds, arm, qid), row in indexed.items()
                if ds == dataset and arm == before and row["answerable"]
            ]
            candidate_equal = all(
                a["diagnostics"]["candidates"] == b["diagnostics"]["candidates"] for a, b in pairs
            )
            scores_equal = all(
                a["diagnostics"]["final"] == b["diagnostics"]["final"] for a, b in pairs
            )
            if name.startswith("rerank_language") or name in {"version_scope", "metadata_input"}:
                if not candidate_equal:
                    raise ValueError(f"{dataset}/{name}: paired candidates differ")
                for a, b in pairs:
                    sa, sb = (
                        a["diagnostics"]["candidate_snapshot"],
                        b["diagnostics"]["candidate_snapshot"],
                    )
                    if sa != sb or digest(run / sa["path"]) != sa["sha256"]:
                        raise ValueError("Candidate snapshot hash mismatch")
            if name == "version_scope" and not scores_equal:
                raise ValueError("Version experiment unexpectedly changed reranking")
            old = sum(a["delivered"]["complete"] for a, _ in pairs)
            new = sum(b["delivered"]["complete"] for _, b in pairs)
            result[f"{dataset}:{name}"] = {
                "before": before,
                "after": after,
                "n": len(pairs),
                "candidate_sets_equal": candidate_equal,
                "rankings_and_scores_equal": scores_equal,
                "delivered_before": old,
                "delivered_after": new,
                "delta": new - old,
                "lost_ids": [
                    a["id"]
                    for a, b in pairs
                    if a["delivered"]["complete"] and not b["delivered"]["complete"]
                ],
                "recovered_ids": [
                    a["id"]
                    for a, b in pairs
                    if not a["delivered"]["complete"] and b["delivered"]["complete"]
                ],
            }
    cases = []
    for row in rows:
        if row["dataset"] != "official" or row["id"] not in {
            "official-002-1",
            "official-002-2",
            "official-004-4",
            "official-026-4",
        }:
            continue
        gold = set(row["resolved_gold"]["relevant"])
        cases.append(
            {
                "id": row["id"],
                "arm": row["arm"],
                "query": row["query"],
                "candidate_complete": row["candidate_complete"],
                "delivered": row["delivered"],
                "gold_ranks": [
                    hit for hit in row["diagnostics"]["final"] if hit["chunk_id"] in gold
                ],
                "version_preference": row["diagnostics"].get("version_preference"),
                "selected_ids": row["retrieved"][:5],
            }
        )
    interaction = {}
    for dataset in ("official", "repository"):
        totals = {
            arm: sum(
                r["delivered"]["complete"]
                for r in rows
                if r["dataset"] == dataset and r["arm"] == arm and r["answerable"]
            )
            for arm in (
                "recall_en_rerank_en",
                "recall_en_rerank_by_collection",
                "recall_zh_rerank_en",
                "recall_zh_rerank_by_collection",
            )
        }
        interaction[dataset] = {
            "totals": totals,
            "interaction_delta": totals["recall_zh_rerank_by_collection"]
            - totals["recall_zh_rerank_en"]
            - totals["recall_en_rerank_by_collection"]
            + totals["recall_en_rerank_en"],
        }
    return {
        "paired_comparisons": result,
        "cases": cases,
        "language_interaction": interaction,
        "rows_sha256": digest(run / "rows.jsonl"),
        "analysis_script_sha256": digest(Path(__file__)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = [json.loads(x) for x in (args.output / "rows.jsonl").read_text().splitlines()]
    result = analyze(rows, args.output)
    (args.output / "paired-analysis.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2)
    )
    lines = [
        "# 同候选成对因果分析",
        "",
        "改变重排语言、版本保护或元数据时验证候选快照哈希；版本实验另验证完整排名与分数一致。",
        "差值为固定dev上完整原始证据交付数，不是回答正确率；中文仓库无英文译文。",
        "",
        "| 对照 | 原交付 | 新交付 | 差值 | 候选完全相同 |",
        "|---|---:|---:|---:|---|",
    ]
    for name, item in result["paired_comparisons"].items():
        lines.append(
            f"| {name} | {item['delivered_before']:g}/{item['n']} | "
            f"{item['delivered_after']:g}/{item['n']} | {item['delta']:+g} | "
            f"{item['candidate_sets_equal']} |"
        )
    lines.extend(
        [
            "",
            "关键案例完整原始排名、分数和版本保护记录见 paired-analysis.json。",
            f"官方语言交互差值为{result['language_interaction']['official']['interaction_delta']:+g}题："
            "一种改动的效果取决于另一种设置，不能把总下降唯一拆分成两个独立份额。",
            "改变重排语言的影响可以由本对照识别；其内部是否属于分数校准问题仍需进一步实验。",
        ]
    )
    archived = args.output / "implementation/scripts/analyze_routing_v2.py"
    archived.parent.mkdir(parents=True, exist_ok=True)
    archived.write_bytes(Path(__file__).read_bytes())
    (args.output / "paired-analysis.md").write_text("\n".join(lines) + "\n")
    print("paired analysis hash", canonical_hash(result))


if __name__ == "__main__":
    main()
