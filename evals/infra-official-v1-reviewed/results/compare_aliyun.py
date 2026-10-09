"""Compare three fixed-input dev runs, preserving all raw results and pending human labels."""

import json
from pathlib import Path

from compare_aihubmix import FIXED_FIELDS, extra_stats
from compare_deepseek import load, status

ROOT = Path(__file__).resolve().parent
RUNS = {
    "本地Qwen3 4B": "dev-20261001",
    "DeepSeek官方": "dev-deepseek-flash-20261001",
    "阿里云DeepSeek": "dev-aliyun-deepseek-20261001",
}
VARIANTS = ("oracle", "bm25", "dense", "hybrid", "hybrid_rerank")


def main():
    rows = {key: load(ROOT / directory) for key, directory in RUNS.items()}
    assert all(len(value) == 300 for value in rows.values())
    current = {r["review_key"]: r for r in rows["阿里云DeepSeek"]}
    assert len(current) == 300
    mismatches, transitions = [], {}
    for key, value in rows.items():
        if key == "阿里云DeepSeek":
            continue
        previous = {r["review_key"]: r for r in value}
        assert set(previous) == set(current)
        changes = []
        for rid, row in current.items():
            old = previous[rid]
            for field in FIXED_FIELDS:
                if old.get(field) != row.get(field):
                    mismatches.append({"baseline": key, "review_key": rid, "field": field})
            oc, nc = old["generation"]["calls"], row["generation"]["calls"]
            if oc and nc and oc[0]["messages"] != nc[0]["messages"]:
                mismatches.append({"baseline": key, "review_key": rid, "field": "first_messages"})
            if status(old) != status(row):
                changes.append(
                    {
                        "review_key": rid,
                        "baseline_status": status(old),
                        "new_status": status(row),
                        "answerable": row["answerable"],
                    }
                )
        transitions[key] = changes
    summaries = {
        key: json.loads((ROOT / d / "summary.json").read_text()) for key, d in RUNS.items()
    }
    protocol_dir = ROOT / "protocol-aliyun-deepseek-20261001"
    protocol = json.loads((protocol_dir / "protocol.json").read_text())
    overall = {key: extra_stats(value) for key, value in rows.items()}
    result = {
        "experiment_status": "dev_completed"
        if (protocol_dir / "dev-completed.json").exists()
        else "dev_collected_with_errors",
        "protocol_generation": protocol["generation"],
        "matched_rows_per_run": 300,
        "fixed_input_mismatches": mismatches,
        "overall": overall,
        "by_variant": {
            v: {
                key: extra_stats([r for r in value if r["variant"] == v])
                for key, value in rows.items()
            }
            for v in VARIANTS
        },
        "status_transitions": transitions,
        "human_semantic_metrics": None,
        "priority_review_keys": [
            r["review_key"]
            for r in rows["阿里云DeepSeek"]
            if r["generation"]["error"]
            or (r["answerable"] and r["delivered"]["complete"] == 1 and status(r) == "no_evidence")
            or (not r["answerable"] and status(r) == "answered")
        ],
        "notes": [
            "Question approval does not approve generated answers.",
            "Same frozen corpus, labels, ranking, delivered context and first RAG messages.",
            "Aliyun max_tokens=1024; reasoning not explicitly disabled; original API 650/disabled.",
            "Provider names in responses do not verify immutable model weights.",
            "Usage includes measured retries and excludes readiness/warmup.",
            "Failed AIHubMix trial-quota experiment is excluded from model comparison.",
            "No holdout evaluation; no benchmark questions/answers ingested into corpus.",
        ],
    }
    (ROOT / "aliyun-comparison.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    )
    lines = [
        "# 阿里云百炼DeepSeek：完整dev实验记录",
        "",
        "2026-10-01，审核后的60道dev题×Oracle与四种检索配置，共300条执行记录。",
        "每种配置54道可回答题、6道不可回答题；题目已经审批，答案仍待独立人工评审。",
        "",
        "请求模型`deepseek-v4-flash`；北京业务空间OpenAI兼容接口。",
        f"实验状态：`{result['experiment_status']}`。源码、模型快照、语料与协议已冻结归档。",
        f"与两组基线的输入/排名/交付/首轮提示词差异：{len(mismatches)}项。",
        "",
        "| 模型/服务 | 作答 | 拒答 | 调用错误 | 重试题数 | 生成P50秒 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for key, value in overall.items():
        c = value["states"]
        lines.append(
            f"| {key} | {c.get('answered', 0)} | {c.get('no_evidence', 0)} | "
            f"{c.get('error', 0)} | {value['retry_rows']} | "
            f"{value['generation_ms_median_with_calls'] / 1000:.2f} |"
        )
    lines += [
        "",
        "耗时仅统计发生模型调用的题目，包含格式/引用重试；不等于问答端到端耗时。",
        "",
        "| 配置 | 本地作答/拒答/错误 | DeepSeek官方作答/拒答/错误 | 阿里云作答/拒答/错误 |",
        "|---|---:|---:|---:|",
    ]
    for v, values in result["by_variant"].items():
        cells = [
            "/".join(
                str(values[k]["states"].get(s, 0)) for s in ("answered", "no_evidence", "error")
            )
            for k in RUNS
        ]
        lines.append(f"| {v} | {' | '.join(cells)} |")
    lines += ["", "| 配置 | 阿里云生成P50秒 | 阿里云生成P95秒 |", "|---|---:|---:|"]
    for v in VARIANTS:
        latency = summaries["阿里云DeepSeek"]["summaries"][v]["generation_with_model_latency"]
        lines.append(f"| {v} | {latency['p50_ms'] / 1000:.2f} | {latency['p95_ms'] / 1000:.2f} |")
    lines += [
        "",
        "原始输出结构诊断（排除最后一轮请求失败、平台额度提示）：",
        "",
        "| 模型/服务 | JSON/schema合法 | 非JSON | 未知引用ID | 内联ID未列入citations |",
        "|---|---:|---:|---:|---:|",
    ]
    for key, value in overall.items():
        c = value["last_raw_structure"]
        lines.append(
            f"| {key} | {c.get('valid_schema', 0)}/{value['quality_eligible_raw_rows']} | "
            f"{c.get('non_json', 0)} | {c.get('unknown_citation_ids', 0)} | "
            f"{c.get('inline_ids_missing_from_list', 0)} |"
        )
    current_stats = overall["阿里云DeepSeek"]
    lines += [
        "",
        "实际返回模型名：`" + json.dumps(current_stats["returned_models"]) + "`。",
        "结束原因：`" + json.dumps(current_stats["stop_reasons"]) + "`。",
        "服务端usage字段求和：`" + json.dumps(current_stats["provider_usage_sum"]) + "`。",
        f"其中reasoning_tokens={current_stats['reasoning_tokens_from_provider']}，"
        f"cached_prompt_tokens={current_stats['cached_prompt_tokens_from_provider']}。",
        "reasoning_tokens是completion_tokens细分项，不能重复相加；用量包含校验重试、排除预热。",
        "没有按未知账号价格推算费用。",
        "",
        "检索分母54题，四种检索配置的排名与输入完全不变，指标仍为：",
        "",
        "| 配置 | Recall@5 | MRR@10 | nDCG@10 | 完整证据@5 | 实际完整交付 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for v in VARIANTS[1:]:
        s = summaries["阿里云DeepSeek"]["summaries"][v]
        a, b = s["at_k"]["5"], s["at_k"]["10"]
        lines.append(
            f"| {v} | {a['recall']:.3f} | {b['mrr']:.3f} | {b['ndcg']:.3f} | "
            f"{a['complete_evidence_hit']:.3f} | {s['context_complete_ci95']['mean']:.3f} |"
        )
    lines += [
        "",
        "作答数不是正确率；引用ID合法不代表引用内容支持回答。",
        "事实正确率、要点覆盖、引用支持、幻觉、误拒答等仍为空，需独立人工评分。",
        "不可回答题的answered状态也可能对应正文语义拒答，不能仅按状态判定幻觉。",
        "",
        "阿里云max_tokens=1024，思考未显式关闭，usage报告reasoning_tokens；"
        "此前官方DeepSeek max_tokens=650且关闭thinking；"
        "本地num_predict=650、think=false、format=json、num_ctx=8192。各端temperature=0。",
        "因此本实验比较服务及配置整体行为，不能将差异单独归因于模型或服务商。",
        "模型名是服务端声明，没有不可变权重摘要。",
        "",
        "AIHubMix的试用额度失败实验单独保留，不纳入模型质量/速度排名。",
        "",
        "[原始报告](dev-aliyun-deepseek-20261001/report.md)、"
        "[逐条数据](dev-aliyun-deepseek-20261001/rows.jsonl)、"
        "[人工评审材料](dev-aliyun-deepseek-20261001/answer-review.md)、"
        "[待填评审账本](dev-aliyun-deepseek-20261001/answer-review.json)。",
        "[逐条对照与诊断](aliyun-comparison.json)、"
        "[冻结协议](protocol-aliyun-deepseek-20261001/protocol.json)。",
        "",
        "旧基线未覆盖，未执行holdout，未将问题或答案加入知识库。",
    ]
    (ROOT / "aliyun-comparison.md").write_text("\n".join(lines) + "\n")
    print(
        json.dumps(
            {
                "status": result["experiment_status"],
                "overall": {
                    k: {
                        f: v[f]
                        for f in (
                            "states",
                            "retry_rows",
                            "generation_ms_median_with_calls",
                            "returned_models",
                            "stop_reasons",
                            "provider_usage_sum",
                            "reasoning_tokens_from_provider",
                        )
                    }
                    for k, v in overall.items()
                },
                "fixed_input_mismatches": mismatches,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
