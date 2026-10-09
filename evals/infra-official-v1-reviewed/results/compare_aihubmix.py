"""Three-way fixed-input dev comparison; no automatic semantic correctness labels."""

import json
from collections import Counter
from pathlib import Path

from compare_deepseek import load, stats, status

ROOT = Path(__file__).resolve().parent
RUNS = {
    "local_4b": "dev-20261001",
    "deepseek_flash": "dev-deepseek-flash-20261001",
    "aihubmix_coding_glm": "dev-aihubmix-glm-20261001",
}
VARIANTS = ("oracle", "bm25", "dense", "hybrid", "hybrid_rerank")
FIXED_FIELDS = (
    "query",
    "answerable",
    "context",
    "delivered",
    "retrieved",
    "at_k",
    "candidate_hit",
    "candidate_complete",
    "resolved_gold",
)


def extra_stats(rows):
    result = stats(rows)
    reasoning = cached = 0
    quota_rows = []
    quota_calls = 0
    unavailable_last_raw = 0
    quota_last_raw = 0
    for row in rows:
        calls = row["generation"]["calls"]
        row_quota = False
        for call in row["generation"]["calls"]:
            quota = "accounts that have not been recharged" in call.get("raw", "").lower()
            quota_calls += quota
            row_quota |= quota
            usage = call.get("provider_response", {}).get("usage") or {}
            reasoning += (usage.get("completion_tokens_details") or {}).get("reasoning_tokens", 0)
            cached += (usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0)
        if row_quota:
            quota_rows.append(row["review_key"])
        if calls:
            raw = calls[-1].get("raw", "")
            unavailable_last_raw += not raw and bool(calls[-1].get("error"))
            quota_last_raw += "accounts that have not been recharged" in raw.lower()
    result["last_raw_structure"]["non_json"] = (
        result["last_raw_structure"].get("non_json", 0) - unavailable_last_raw - quota_last_raw
    )
    result["quality_eligible_raw_rows"] = (
        result["model_invoked_rows"] - unavailable_last_raw - quota_last_raw
    )
    result["platform_quota_message_calls"] = quota_calls
    result["platform_quota_affected_rows"] = quota_rows
    result["last_raw_unavailable_due_call_error"] = unavailable_last_raw
    result["last_raw_is_platform_quota_message"] = quota_last_raw
    result["reasoning_tokens_from_provider"] = reasoning
    result["cached_prompt_tokens_from_provider"] = cached
    result["unanswerable_statuses"] = dict(Counter(status(r) for r in rows if not r["answerable"]))
    result["complete_evidence_refusal_rows"] = [
        r["review_key"]
        for r in rows
        if r["answerable"] and r["delivered"]["complete"] == 1 and status(r) == "no_evidence"
    ]
    return result


def main():
    rows = {key: load(ROOT / name) for key, name in RUNS.items()}
    assert all(len(value) == 300 for value in rows.values())
    maps = {key: {r["review_key"]: r for r in value} for key, value in rows.items()}
    assert all(len(value) == 300 for value in maps.values())
    current = maps["aihubmix_coding_glm"]
    mismatches = []
    transitions = {}
    for key in ("local_4b", "deepseek_flash"):
        assert set(maps[key]) == set(current)
        changes = []
        for rid, row in current.items():
            old = maps[key][rid]
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
    protocol = json.loads((ROOT / "protocol-aihubmix-glm-20261001/protocol.json").read_text())
    result = {
        "experiment_status": "incomplete_model_evaluation_due_provider_quota_and_transport",
        "requested_model": protocol["generation"]["identity"]["model"],
        "readiness_returned_model": protocol["generation"]["identity"]["returned_model"],
        "generation_options": protocol["generation"]["options"],
        "fixed_input_mismatches": mismatches,
        "matched_rows_per_run": 300,
        "overall": {key: extra_stats(value) for key, value in rows.items()},
        "by_variant": {
            v: {
                key: extra_stats([r for r in value if r["variant"] == v])
                for key, value in rows.items()
            }
            for v in VARIANTS
        },
        "status_transitions": transitions,
        "human_semantic_metrics": None,
        "notes": [
            "Same frozen dev questions, retrieval rankings, delivered evidence and first prompts.",
            "AIHubMix requests max_tokens=1024; DeepSeek and local limits are 650.",
            "AIHubMix reasoning is not explicitly disabled; provider reports reasoning tokens.",
            "Returned model names are provider declarations, not verified immutable weights.",
            "Status answered is not factual correctness; no_evidence is not semantic error.",
            "Raw citation validation is structural, not citation support or faithfulness.",
            "Token sums include measured validation retries and exclude readiness/warmup.",
            "Refusal citation_ids_valid=false in original summary is not a citation error rate.",
            "No holdout evaluation; historical rows and labels are not overwritten.",
        ],
    }
    (ROOT / "aihubmix-comparison.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    )
    lines = [
        "# AIHubMix coding-glm-4.6-free：完整dev实验记录",
        "",
        "2026-10-01，同一审核后dev60题×Oracle与四种检索配置，共300条。",
        "本轮收集300条执行记录，但模型评测未成功完成；不能用于比较模型质量或速度。",
        "仅前两条是真实模型输出。随后159次请求在completion正文返回账号额度限制提示；",
        "79条被框架两次格式校验后记为拒答，另1条先收到额度提示、重试又失败。",
        "共213条出现连接或JSON响应错误，现有错误日志未区分这两种具体原因。",
        "原始输出/摘要保持不变，本报告独立识别平台提示；未生成dev-completed标记。",
        "每种配置54道可回答、6道不可回答；人工审批仅覆盖题目，生成答案评分仍待审核。",
        "",
        f"请求路由：`{result['requested_model']}`；预热返回模型："
        f"`{result['readiness_returned_model']}`。底层权重不可验证冻结。",
        f"与两组历史基线的固定输入、检索指标、证据及首轮提示词差异：{len(mismatches)}项。",
        "",
        "原始框架状态（AIHubMix的拒答含平台额度提示，不能解释为模型拒答能力）：",
        "| 模型/路由 | 作答 | 拒答 | 调用错误 | 需重试题数 | 模型调用题数 | 生成P50秒 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for key, value in result["overall"].items():
        c = value["states"]
        latency = (
            "—（实验受阻）"
            if key == "aihubmix_coding_glm"
            else f"{value['generation_ms_median_with_calls'] / 1000:.2f}"
        )
        lines.append(
            f"| {key} | {c.get('answered', 0)} | {c.get('no_evidence', 0)} | "
            f"{c.get('error', 0)} | {value['retry_rows']} | "
            f"{value['model_invoked_rows']} | "
            f"{latency} |"
        )
    lines += [
        "",
        "P50仅统计发生模型调用的题目，包含格式/引用重试；不能当作完整问答端到端耗时。",
        "",
        "| 配置 | 本地作答/拒答/错误 | DeepSeek作答/拒答/错误 | AIHubMix作答/拒答/错误 |",
        "|---|---:|---:|---:|",
    ]
    for variant, values in result["by_variant"].items():
        cells = []
        for key in RUNS:
            cells.append(
                "/".join(
                    str(values[key]["states"].get(k, 0))
                    for k in ("answered", "no_evidence", "error")
                )
            )
        lines.append(f"| {variant} | {' | '.join(cells)} |")
    lines += [
        "",
        "作答数不是正确答案数；不可回答题也可能以answered状态输出语义拒答。",
        "事实正确率、要点支持率、引用支持率、幻觉/误拒答等仍为空，须独立人工评审。",
        "",
        "API原始输出结构检查（排除最后一轮无返回的请求错误和已识别的平台额度提示）：",
        "",
        "| 模型/路由 | JSON/schema合法 | 非JSON | 未知引用ID | 内联ID未列入citations |",
        "|---|---:|---:|---:|---:|",
    ]
    for key, value in result["overall"].items():
        c = value["last_raw_structure"]
        lines.append(
            f"| {key} | {c.get('valid_schema', 0)}/{value['quality_eligible_raw_rows']} | "
            f"{c.get('non_json', 0)} | {c.get('unknown_citation_ids', 0)} | "
            f"{c.get('inline_ids_missing_from_list', 0)} |"
        )
    value = result["overall"]["aihubmix_coding_glm"]
    lines += [
        "",
        "本轮逐次返回的模型名：`" + json.dumps(value["returned_models"]) + "`。",
        "其中glm-5.3-flash为2次真实模型回答；coding-glm-4.6-free为159次额度提示的响应字段，",
        "不能将后者视为159次实际模型生成。",
        "结束原因：`" + json.dumps(value["stop_reasons"]) + "`。",
        "服务端原始usage字段求和：`" + json.dumps(value["provider_usage_sum"]) + "`。",
        f"其中reasoning_tokens={value['reasoning_tokens_from_provider']}，"
        f"cached_prompt_tokens={value['cached_prompt_tokens_from_provider']}。",
        "不同协议的usage字段定义不同，不直接相加跨协议字段，也不推算未知账号费用。",
        "",
        "生成条件差异：AIHubMix max_tokens=1024，思考模式未显式关闭；"
        "DeepSeek max_tokens=650并关闭thinking；本地num_predict=650、think=false、"
        "format=json、num_ctx=8192。各端temperature=0，但不是严格相同解码条件。",
        "",
        "检索配置、冻结语料与题目不变，API回答模型不能改善Recall/MRR/nDCG。"
        "Top5实际完整证据交付率仍为：BM25 48.1%、Dense 20.4%、Hybrid 38.9%、"
        "Hybrid+Reranker 53.7%。",
        "",
        "[本轮原始报告](dev-aihubmix-glm-20261001/report.md)、"
        "[原始逐条数据](dev-aihubmix-glm-20261001/rows.jsonl)、"
        "[答案审核材料](dev-aihubmix-glm-20261001/answer-review.md)、"
        "[待填审核账本](dev-aihubmix-glm-20261001/answer-review.json)。",
        "[三轮逐条对照与诊断](aihubmix-comparison.json)、"
        "[新冻结协议](protocol-aihubmix-glm-20261001/protocol.json)。",
        "",
        "旧基线、题目、标签未覆盖；未执行holdout，未把题目/答案加入知识库。",
    ]
    (ROOT / "aihubmix-comparison.md").write_text("\n".join(lines) + "\n")
    print(
        json.dumps(
            {"overall": result["overall"], "fixed_input_mismatches": mismatches}, ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()
