"""Compare completed dev tuning runs without labeling answer correctness."""

import json
import statistics
from collections import Counter
from pathlib import Path

from infra_rag.benchmarking import bootstrap_groups, digest

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evals/infra-official-v1-reviewed/results"
RUNS = {
    "原 DeepSeek": "dev-deepseek-flash-20261001",
    "候选并集30": "dev-opt-union30-20261001",
    "候选并集60": "dev-opt-union60-20261001",
    "并集60+双倍预算": "dev-opt-union60-context2400-20261001",
    "英文查询+并集30": "dev-opt-english-query-20261001",
    "双语查询+并集30": "dev-opt-bilingual-query-20261001",
    "最终 DeepSeek 复测": "dev-deepseek-optimized-20261001",
}


def load_rows(name):
    return [json.loads(line) for line in (RESULTS / name / "rows.jsonl").read_text().splitlines()]


def generation_stats(rows):
    states = Counter()
    calls = []
    for row in rows:
        generation = row["generation"]
        states["error" if generation["error"] else generation["response"]["status"]] += 1
        calls.extend(generation["calls"])
    return {
        "states": dict(states),
        "requests": len(calls),
        "retry_rows": sum(len(r["generation"]["calls"]) > 1 for r in rows),
        "returned_models": dict(
            Counter((call.get("provider_response") or {}).get("model") for call in calls)
        ),
        "fact_correct": None,
    }


def main():
    summaries = {
        label: json.loads((RESULTS / name / "summary.json").read_text())
        for label, name in RUNS.items()
    }
    old = load_rows(RUNS["原 DeepSeek"])
    new = load_rows(RUNS["最终 DeepSeek 复测"])
    assert len(old) == len(new) == 300
    previous = {r["review_key"]: r for r in old}
    assert set(previous) == {r["review_key"] for r in new}
    for row in new:
        before = previous[row["review_key"]]
        for field in ("query", "answerable", "required_points", "forbidden_claims"):
            assert row[field] == before[field]
        if row["variant"] == "oracle":
            assert row["context"] == before["context"]
    paired = []
    for row in new:
        if row["variant"] != "hybrid_rerank" or not row["answerable"]:
            continue
        before = previous[row["review_key"]]
        paired.append(
            {
                "group_id": row["group_id"],
                "context_delta": float(row["delivered"]["complete"])
                - float(before["delivered"]["complete"]),
                "recall5_delta": row["at_k"]["5"]["recall"] - before["at_k"]["5"]["recall"],
            }
        )
    translations = [
        json.loads(line)
        for line in (RESULTS / RUNS["英文查询+并集30"] / "query-rewrites.jsonl")
        .read_text()
        .splitlines()
    ]
    result = {
        "scope": "dev tuning; no holdout claims; sparse evidence judgments",
        "runs": {
            label: {
                "summary_sha256": digest(RESULTS / name / "summary.json"),
                "main": summaries[label]["summaries"]["hybrid_rerank"],
            }
            for label, name in RUNS.items()
        },
        "paired_context_delta_ci95": bootstrap_groups(paired, "context_delta"),
        "paired_recall5_delta_ci95": bootstrap_groups(paired, "recall5_delta"),
        "generation": {"before": generation_stats(old), "after": generation_stats(new)},
        "generation_by_variant": {
            name: {
                "before": generation_stats([r for r in old if r["variant"] == name]),
                "after": generation_stats([r for r in new if r["variant"] == name]),
            }
            for name in ("oracle", "bm25", "dense", "hybrid", "hybrid_rerank")
        },
        "translation": {
            "requests": len(translations),
            "p50_ms": statistics.median(r["latency_ms"] for r in translations),
            "prompt_has_only_question": True,
            "independently_reviewed": False,
        },
        "fact_correct": None,
    }
    (RESULTS / "deepseek-optimization.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2)
    )
    lines = [
        "# DeepSeek 查询检索优化（2026-10-01）",
        "",
        "只在固定 dev60 调优；其中54题有答案、6题不可答，holdout未运行。",
        "检索分母为54题；标签稀疏，AI生成查询翻译尚未独立人工审核。",
        "",
        "| 实验（主配置） | Recall@5 | MRR@10 | nDCG@10 | 完整证据交付 |",
        "|---|---:|---:|---:|---:|",
    ]
    for label, run in result["runs"].items():
        main_result = run["main"]
        lines.append(
            f"| {label} | {main_result['at_k']['5']['recall']:.4f} | "
            f"{main_result['at_k']['10']['mrr']:.4f} | "
            f"{main_result['at_k']['10']['ndcg']:.4f} | "
            f"{main_result['context_complete_ci95']['mean']:.4f} |"
        )
    lines.extend(
        [
            "",
            "采用英文查询、每路30候选并集、BM25+Dense+RRF+重排；预算1200token/4000字符。",
            "译文仅用于检索，原问题、答案要求、来源、标注和中文回答提示保留。",
            "候选数60与双倍上下文预算未带来提升；双语查询低于英文查询，均不采用。",
            "",
            "| 题型 | 原完整证据交付 | 新完整证据交付 |",
            "|---|---:|---:|",
        ]
    )
    for kind, values in summaries["最终 DeepSeek 复测"]["by_type"].items():
        after = values["hybrid_rerank"]["context_complete_ci95"]
        before = summaries["原 DeepSeek"]["by_type"][kind]["hybrid_rerank"]["context_complete_ci95"]
        if after:
            lines.append(f"| {kind} | {before['mean']:.4f} | {after['mean']:.4f} |")
    lines.extend(
        [
            "",
            "完整300条（Oracle+4配置）生成状态：",
            "",
            f"- 原配置：{result['generation']['before']['states']}",
            f"- 新配置：{result['generation']['after']['states']}",
            "",
            "作答数量和引用ID校验不等于正确率；事实正确率、忠实性、引用支持率保持空值。",
            f"翻译额外60次API调用，P50 {result['translation']['p50_ms']:.0f}ms；",
            "表中检索耗时不包含翻译，复测重放固定译文；线上未缓存请求需额外支付翻译延迟。",
            "线上翻译缓存128条，失败回退原文并显示trace；这轮未评测故障回退的检索质量。",
            "",
            "配对分组bootstrap差值和逐配置生成记录见deepseek-optimization.json。",
            "优化300条目录：dev-deepseek-optimized-20261001；来源协议、实现归档和译文哈希已冻结。",
            "与英文检索消融相比，独立索引复测中240条排名有6条出现顺序差异，交付证据覆盖未变；",
            "因此MRR/nDCG有小幅波动。近似向量索引重建是可能原因，尚未单独验证其来源。",
            "中文embedding对英文语料的适配、多跳证据聚合仍需后续验证；本轮没有更换embedding。",
        ]
    )
    (RESULTS / "deepseek-optimization.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(result["generation"], ensure_ascii=False))


if __name__ == "__main__":
    main()
