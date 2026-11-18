"""Write the full paired answers and explicitly AI-authored completeness review."""

import argparse
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from batch_user_badcases import SERVICES
from operation_log import record_operation
from prepare_corpus_pilot import load, save

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.grid_metrics import latency

# AI review after reading all32 actual answers; these are not independent human labels.
JUDGMENTS = {
    "bc01": ("partial", "KDA固定矩阵与6/414MiB正确；漏掉8K紧凑BF16 MLA单层9MiB、24层216MiB。"),
    "bc02": (
        "partial",
        "已区分头共享与潜变量压缩；缺512/64组成及Kimi K3 MLA的NoPE条件。",
    ),
    "bc03": ("failed", "英文查询拒答；交付偏向vLLM FP8校准代码，缺q4_0分组scale与324MiB容量证据。"),
    "bc04": (
        "partial",
        "12/24MiB值正确，但把未调整的原环默认当作交替环，缺少原顺序条件；优化回答另把不调整写成改成交替。",
    ),
    "bc05": (
        "partial",
        "计算/读取取较大项的解释正确；漏掉每专家128token及同/跨插槽带宽、kernel吞吐的算例边界。",
    ),
    "bc06": (
        "partial",
        "16bytes码值+2bytes scale及18/64正确；没有明确算出324MiB总量与36MiB scale。",
    ),
    "bc07": (
        "partial",
        "减少144MiB、更新12800到524288及约41倍正确；未给404到260MiB完整读量与缓冲/序列/维度条件。",
    ),
    "bc08": ("complete", "明确文本匹配与递推快照不同，最近8192快照恢复，再重算2560token。"),
    "bc09": (
        "failed",
        "拒答；交付只有分页物理块相关段落，缺递推快照/恢复位置证据，未比较两种机制。",
    ),
    "bc10": (
        "failed",
        "明确错误：不同adapter却断言同prompt前缀KV相同、可直接共享；漏掉模型/adapter兼容条件。容量112.5GiB虽正确，不能抵消此错误。",
    ),
    "bc11": (
        "partial",
        "开销交点约7000与示例延迟正确；未绑定H100/Llama-3.1-8B，质量部分未区分Q精度及28/26/28算例。",
    ),
    "bc12": (
        "complete",
        "给出串行13.5、并行输出3时9.9、输出降2时14.9ms/token，解释接受输出数可抵消草稿生成收益。",
    ),
    "bc13": (
        "complete",
        "正确拒答，没有编造生产P99；提示仍是通用资料不足，补充缺失测量条件可改善表达。",
    ),
    "bc14": (
        "failed",
        "第一轮状态类型正确；第二轮虽携带历史查询，仍拒答，未完成快照间隔/重算/容量取舍。",
    ),
    "bc15": (
        "failed",
        "拒答，未交付任何完整代码，更未满足必要import与device_count校验；本轮未执行GPU代码。",
    ),
}
LABELS = {"complete": "通过", "partial": "部分", "failed": "未通过"}


def report(out, destination):
    protocol = load(out / "protocol.json")
    for name, sha in load(out / "artifacts-manifest.json").items():
        assert digest(out / name) == sha, name
    cases = load(out / "cases.json")
    rows = [
        load(p)
        for p in sorted((out / "outputs").glob("*.json"))
        if not p.name.endswith(".sha256.json")
    ]
    assert len(rows) == 32
    assert len({(r["config"], r["case_id"], r["turn"]) for r in rows}) == 32
    reviews = []
    templates = []
    register = []
    for r in rows:
        path = out / "outputs" / f"{r['config']}-{r['case_id']}-t{r['turn']}.json"
        assert r["case_sha256"] == protocol["case_hashes"][r["case_id"]]
        assert digest(path) == load(path.with_suffix(".sha256.json"))["sha256"]
        response = r.get("response", {})
        allowed = {c["citation_id"] for c in response.get("citations", [])}
        mentions = set(re.findall(r"\[(E[A-Za-z0-9_-]+)\]", response.get("answer", "")))
        assert mentions <= allowed
        assert r["request_id"] == r["server_record"]["request_id"]
        grade, reason = JUDGMENTS[r["case_id"]]
        if r["case_id"] == "bc14":
            grade = "complete" if r["turn"] == 1 else "failed"
            reason = (
                "KDA固定递推状态与MLA随上下文增长的低维表示区分正确。" if r["turn"] == 1 else reason
            )
        identity = {
            "run_id": "user-badcases-v1/" + out.name,
            "config_id": r["config"],
            "case_id": f"{r['case_id']}-t{r['turn']}",
            "repetition": 0,
            "logical_case_id": r["case_id"],
            "turn": r["turn"],
            "case_sha256": r["case_sha256"],
            "trace_sha256": digest(path),
            "response_sha256": canonical_hash(response),
            "artifact": str(path),
        }
        reviews.append(
            {
                **identity,
                "review_type": "AI source-based completeness review",
                "reviewer": "assistant_ai",
                "reviewed_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
                "verdict": grade,
                "reason": reason,
                "citation_ids_valid": True,
                "independent_human_correct": None,
                "source_truth_verified": None,
            }
        )
        templates.append(
            {
                **identity,
                "status": "pending",
                "reviewer": None,
                "reviewed_at": None,
                "correct": None,
                "citation_support": None,
                "conditions_complete": None,
                "claim_inventory_complete": None,
                "reason": None,
            }
        )
        register.append(
            {
                **identity,
                "request_id": r["request_id"],
                "http_status": r["http_status"],
                "status": response.get("status"),
                "elapsed_ms": r["elapsed_ms"],
            }
        )
    stats = {}
    for config in SERVICES:
        selected = [r for r in rows if r["config"] == config]
        calls = [c for r in selected for c in r["server_record"]["model_calls"]]
        retrieval = [t for r in selected for t in r["server_record"]["retrieval"]]
        scenario = Counter(JUDGMENTS[c["id"]][0] for c in cases)
        turn = Counter(r["verdict"] for r in reviews if r["config_id"] == config)

        def proportions(counts, total):
            return {
                k: {"numerator": counts[k], "denominator": total, "value": counts[k] / total}
                for k in ["complete", "partial", "failed"]
            }

        stats[config] = {
            "actual_http": len(selected),
            "http_status": dict(Counter(str(r["http_status"]) for r in selected)),
            "response_status": dict(Counter(r.get("response", {}).get("status") for r in selected)),
            "ai_scenario_completeness": proportions(scenario, 15),
            "ai_turn_completeness": proportions(turn, 16),
            "independent_strict_accuracy": None,
            "model_attempts": len(calls),
            "usage_coverage": {
                "numerator": sum(
                    isinstance((c.get("provider_metadata") or {}).get("usage"), dict) for c in calls
                ),
                "denominator": len(calls),
                "value": sum(
                    isinstance((c.get("provider_metadata") or {}).get("usage"), dict) for c in calls
                )
                / len(calls)
                if calls
                else None,
            },
            "model_cost_usd": None,
            "latency": latency([r["elapsed_ms"] for r in selected]),
            "cache_hits": sum(t["diagnostics"]["retrieval_cache"]["hit"] for t in retrieval),
        }
    paired = []
    by = {(r["config"], r["case_id"], r["turn"]): r for r in rows}
    for c in cases:
        for turn in range(1, len(c["questions"]) + 1):
            a, b = by["main", c["id"], turn], by["optimized", c["id"], turn]
            ea = [t["evidence"] for t in a["server_record"]["retrieval"]]
            eb = [t["evidence"] for t in b["server_record"]["retrieval"]]
            paired.append(
                {
                    "case_id": c["id"],
                    "turn": turn,
                    "evidence_identical": canonical_hash(ea) == canonical_hash(eb),
                    "answer_identical": a["response"]["answer"] == b["response"]["answer"],
                }
            )
    summary = {
        "scope": "User supplied badcase diagnostic; not heldout accuracy",
        "logical_scenarios": 15,
        "turns_per_config": 16,
        "http_requests": 32,
        "profiles": stats,
        "paired": paired,
        "semantic_review": "AI completeness review, not independent human review",
        "grading": "Full coverage of numeric subquestions and material conditions; "
        "partial when core is right but numeric/conditional fields omitted; "
        "failed for central contradiction, missing answer or incomplete dialogue.",
        "cold_state_note": "main was restarted for accounting, optimized was already warm; "
        "latency is descriptive, not a speed comparison",
        "test_holdout_read": False,
        "tuning": False,
    }
    save(destination / "stats.json", summary)
    save(destination / "ai-review.json", reviews)
    save(destination / "human-review-template.json", templates)
    save(destination / "request-register.json", register)
    lines = [
        "# 用户badcase双服务批测结果",
        "",
        "15个场景、每配置16轮（多轮追问占2轮）、共32次真实HTTP。",
        "使用当前127篇/16,320片段、真实BGE检索和DeepSeek生成。原题、参考要点和来源在生成前冻结。",
        "本轮只诊断，未改知识库、参数、提示或答案；未读独立test/holdout。",
        "",
        "**以下为AI按冻结源文要点进行的完整度初审，不是独立人工正确率。**",
        "“部分”表示核心内容正确但漏掉关键数值、子问或适用条件；不是所有内容都错误。",
        "“未通过”含中心结论错误、可回答任务未完成及多轮第二问失败；生产P99的合理拒答计通过。",
        "",
        "|统计|8000主服务|8001优化服务|",
        "|---|---:|---:|",
        "|HTTP成功|16/16|16/16|",
        f"|返回状态|{stats['main']['response_status']}|{stats['optimized']['response_status']}|",
        "|AI场景完整通过|3/15|3/15|",
        "|AI场景部分完成|7/15|7/15|",
        "|AI场景未通过|5/15|5/15|",
        "|AI逐轮完整通过|4/16|4/16|",
        "|AI逐轮部分完成|7/16|7/16|",
        "|AI逐轮未通过|5/16|5/16|",
        "|独立人工严格正确率|待审/null|待审/null|",
        "",
        "速度优化没有让这批题的完整度判定提升。多轮按两问全部完成才算该场景通过。",
        "",
        "## 逐场景判定",
        "",
        "|ID|场景|主服务|优化服务|关键结果/缺口|",
        "|---|---|---|---|---|",
    ]
    for c in cases:
        verdict, reason = JUDGMENTS[c["id"]]
        lines.append(f"|{c['id']}|{c['category']}|{LABELS[verdict]}|{LABELS[verdict]}|{reason}|")
    lines += [
        "",
        "## 严格完整度口径与解释",
        "",
        "- bc05的机理解释正确，但跨NUMA影响取决于每专家token数及kernel/带宽，漏条件计部分。",
        "- bc06的18/64与scale解释正确，但未显式给324MiB与36MiB，按冻结数字要点计部分。",
        "- bc07给出减少144MiB和约41倍更新，仍缺404→260MiB与算例条件，严格完整度计部分。",
        "- bc04题面未给出原环顺序，未调整不自动等于交替；条件应先说明，不能擅定唯一结果。",
        "- bc13通用拒答未列出所有测量条件，核心未编造生产P99，计正确拒答。",
        "- 来源参考按仓库文档核对，厂商参数与文档事实本身未获得独立验证。",
        "",
        "## 全部原题、实际回答与参考要点",
        "",
    ]
    for c in cases:
        lines += [f"### {c['id']} · {c['category']}", "", "冻结参考要点：", ""]
        lines += ["- " + r for r in c["rubric"]]
        for turn, q in enumerate(c["questions"], 1):
            lines += ["", f"#### 第{turn}轮原题", "", q, ""]
            for config, label in [("main", "8000主服务"), ("optimized", "8001优化服务")]:
                r = by[config, c["id"], turn]
                review = next(
                    x
                    for x in reviews
                    if x["config_id"] == config
                    and x["logical_case_id"] == c["id"]
                    and x["turn"] == turn
                )
                lines += [
                    f"**{label}：{LABELS[review['verdict']]}**",
                    "",
                    r["response"].get("answer", "（无答案）"),
                    "",
                    "引用定位：",
                    "",
                ]
                citations = r["response"].get("citations", [])
                lines += [f"- `{e['citation_id']}` — `{e['locator']}`" for e in citations] or [
                    "- 无引用。"
                ]
                lines += [
                    "",
                    f"HTTP {r['http_status']}；状态 `{r['response']['status']}`；"
                    f"完整响应 {r['elapsed_ms']:.1f} ms；请求ID `{r['request_id']}`。",
                    "",
                ]
    lines += [
        "## 运行与审核材料",
        "",
        f"- 原始运行：`{out}`；协议SHA256 `{digest(out / 'protocol.json')}`。",
        "- 原始输出含实际交付证据、候选/排名、检索与生成耗时及逐次供应商usage；全部输出有hash。",
        "- ai-review.json绑定case、trace和response hash；human-review-template.json保持pending。",
        "- stats.json区分15场景与16轮分母；HTTP成功、引用ID合法不等于语义正确。",
        "- 重启后的主服务有首请求冷加载，优化服务已热；延迟仅用于定位，不据此比较提速。",
        "- 无HTTP重试或结果补跑；引用支持与事实条件的独立人工审核尚未完成。",
    ]
    destination.mkdir(parents=True, exist_ok=True)
    with (destination / "results.md").open("x") as stream:
        stream.write("\n".join(lines) + "\n")
    save(
        destination / "review-manifest.json",
        {
            "protocol_sha256": digest(out / "protocol.json"),
            "raw_manifest_sha256": digest(out / "artifacts-manifest.json"),
            "files": {p.name: digest(p) for p in destination.iterdir() if p.is_file()},
            "human_review": "pending; template not filled",
        },
    )
    return {
        "profiles": stats,
        "evidence_identical": sum(p["evidence_identical"] for p in paired),
        "paired_turns": 16,
        "actual_model_attempts": sum(s["model_attempts"] for s in stats.values()),
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    result = report(a.output.resolve(), a.report.resolve())
    record_operation(
        "生成用户badcase双服务完整结果与AI初审",
        "逐题区分完整、部分与失败，保留全部回答、证据和人工待审模板",
        str(result),
        "AI源文完整度不是独立人工正确率；参考数字及条件执行严格口径，未修改冻结题目或参考",
    )
    print(result)
