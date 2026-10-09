"""Compare frozen dev runs; automatic structural observations are not human fact scores."""

import json
import re
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "dev-20261001"
API = ROOT / "dev-deepseek-flash-20261001"


def load(directory):
    return [json.loads(line) for line in (directory / "rows.jsonl").read_text().splitlines()]


def status(row):
    g = row["generation"]
    return "error" if g["error"] else g["response"]["status"]


def stats(rows):
    states = Counter(status(r) for r in rows)
    calls = [c for r in rows for c in r["generation"]["calls"]]
    invoked = [r for r in rows if r["generation"]["calls"]]
    structural = Counter()
    for r in invoked:
        raw = r["generation"]["calls"][-1].get("raw", "")
        try:
            obj = json.loads(raw)
        except (ValueError, TypeError):
            structural["non_json"] += 1
            continue
        fmt = (
            isinstance(obj, dict)
            and isinstance(obj.get("supported"), bool)
            and isinstance(obj.get("answer"), str)
            and bool(obj["answer"].strip())
            and isinstance(obj.get("citations"), list)
            and all(isinstance(c, str) for c in obj["citations"])
        )
        if not fmt:
            structural["invalid_schema"] += 1
            continue
        structural["valid_schema"] += 1
        allowed = {e["citation_id"] for e in r["context"]["evidence"]}
        structural["unknown_citation_ids"] += bool(set(obj["citations"]) - allowed)
        mentioned = set(re.findall(r"\[(E[a-f0-9]{24})\]", obj["answer"]))
        structural["inline_ids_missing_from_list"] += bool(mentioned - set(obj["citations"]))
        structural["supported_without_citation"] += obj["supported"] and not obj["citations"]
    usage = Counter()
    for c in calls:
        usage.update(
            {
                k: v
                for k, v in (c.get("provider_response", {}).get("usage") or {}).items()
                if isinstance(v, int)
            }
        )
    return {
        "rows": len(rows),
        "states": dict(states),
        "model_invoked_rows": len(invoked),
        "requests_including_validation_retries": len(calls),
        "retry_rows": sum(len(r["generation"]["calls"]) > 1 for r in rows),
        "generation_ms_median_with_calls": statistics.median(
            r["generation"]["latency_ms"] for r in invoked
        ),
        "last_raw_structure": dict(structural),
        "provider_usage_sum": dict(usage),
        "returned_models": dict(
            Counter(
                c["provider_response"].get("model") for c in calls if c.get("provider_response")
            )
        ),
        "stop_reasons": dict(
            Counter(
                c["provider_response"].get("stop_reason")
                for c in calls
                if c.get("provider_response")
            )
        ),
        "fact_correct": None,
    }


def main():
    old, new = load(BASE), load(API)
    assert len(old) == len(new) == 300
    previous = {r["review_key"]: r for r in old}
    assert set(previous) == {r["review_key"] for r in new}
    changes = []
    mismatches = []
    for r in new:
        p = previous[r["review_key"]]
        for field in (
            "query",
            "answerable",
            "context",
            "delivered",
            "retrieved",
            "at_k",
            "candidate_hit",
            "candidate_complete",
            "resolved_gold",
        ):
            if p.get(field) != r.get(field):
                mismatches.append({"review_key": r["review_key"], "field": field})
        # Compare the first request including original prompt/evidence verbatim.
        if p["generation"]["calls"] and r["generation"]["calls"]:
            if p["generation"]["calls"][0]["messages"] != r["generation"]["calls"][0]["messages"]:
                mismatches.append({"review_key": r["review_key"], "field": "first_messages"})
        if status(p) != status(r):
            changes.append(
                {
                    "review_key": r["review_key"],
                    "local_status": status(p),
                    "api_status": status(r),
                    "answerable": r["answerable"],
                }
            )
    result = {
        "local": stats(old),
        "api": stats(new),
        "matched_rows": 300,
        "fixed_input_mismatches": mismatches,
        "status_changes": changes,
        "priority_review_keys": [
            r["review_key"]
            for r in new
            if (r["variant"] == "oracle" and r["answerable"] and status(r) == "no_evidence")
            or (not r["answerable"] and status(r) == "answered")
        ],
        "by_variant": {},
        "human_semantic_metrics": None,
        "notes": [
            "Question approval does not approve answers.",
            "No-evidence bypasses are excluded from raw structure statistics.",
            "citation_ids_valid in original summaries is answer-only validation, "
            "not a citation error rate for refusals.",
            "Usage covers measured calls and validation retries, excludes preloads.",
        ],
    }
    for v in ("oracle", "bm25", "dense", "hybrid", "hybrid_rerank"):
        result["by_variant"][v] = {
            "local": stats([r for r in old if r["variant"] == v]),
            "api": stats([r for r in new if r["variant"] == v]),
        }
    (ROOT / "deepseek-comparison.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    )
    lines = [
        "# DeepSeek官方API与本地4B的dev对照",
        "",
        "2026-10-01，审核后的60道dev题×5种配置，完整300条。模型路由为`deepseek-flash`。",
        "",
        "只替换回答模型；保留语料、划分、BGE、重排器、候选/上下文预算、提示词与两次校验流程。",
        f"逐条输入/排名/交付/首轮提示词核验：差异{len(mismatches)}项。",
        "",
        "| 配置 | 本地作答/拒答/错误 | API作答/拒答/错误 | 本地生成中位秒 | API生成中位秒 |",
        "|---|---:|---:|---:|---:|",
    ]
    for v, pair in result["by_variant"].items():
        cells = []
        for model in ("local", "api"):
            c = pair[model]["states"]
            cells.append("/".join(str(c.get(k, 0)) for k in ("answered", "no_evidence", "error")))
        times = [pair[k]["generation_ms_median_with_calls"] / 1000 for k in ("local", "api")]
        lines.append(f"| {v} | {cells[0]} | {cells[1]} | {times[0]:.2f} | {times[1]:.2f} |")
    lines += [
        "",
        "耗时仅统计发生模型调用的题目，包含格式/引用重试；不同服务与本机执行环境影响耗时。",
        "",
        "作答数不是正确答案数；证据不足时拒答可能是正确行为。答案事实、引用支持率仍待独立人工评审。",
        "原summary的citation_ids_valid对supported=false返回false，不能将其理解成拒答的引用错误。",
        "附加JSON将原始最后一轮输出的结构、未知ID、内联ID缺失分别计数，不改写历史指标。",
        "",
        "Oracle的54道可回答题中52条最终作答，004-2和012-4仍声明证据不足，建议优先评审。",
        "检索配置中交付完整标注证据却最终拒答的API案例为0条；这不等于这些作答都事实正确。",
        "不可回答题BM25有一条024-4状态为answered，但正文明确表示不能给出私有部署的精确P95，",
        "没有编造延迟数值；说明supported/最终状态不能代替语义拒答判断，仍需人工判定。",
        "",
        "API显式关闭thinking、temperature=0、max_tokens=650；本地使用think=false、num_predict=650、",
        "format=json、num_ctx=8192。相同数字不保证相同tokenization，API也没有本地JSON传输约束，",
        "因此解码条件不是严格相同。API权重没有不可变摘要，逐次保存实际返回模型和usage。",
        "",
        "用量（包含重试，排除预热）：`"
        + json.dumps(result["api"]["provider_usage_sum"], ensure_ascii=False)
        + "`。",
        "不将token用量换算为未知账号价格。",
        "",
        "原始结果：[API报告](dev-deepseek-flash-20261001/report.md)、",
        "[API答案评审](dev-deepseek-flash-20261001/answer-review.md)、",
        "[评审账本](dev-deepseek-flash-20261001/answer-review.json)、",
        "[逐条对照与诊断](deepseek-comparison.json)。",
        "",
        "未执行holdout，未将题目/答案加入知识库，旧基线未覆盖。",
    ]
    (ROOT / "deepseek-comparison.md").write_text("\n".join(lines) + "\n")
    print(
        json.dumps(
            {k: result[k] for k in ("local", "api", "fixed_input_mismatches")}, ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()
