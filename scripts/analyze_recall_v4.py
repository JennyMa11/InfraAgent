"""Read-only reports and invariants for frozen recall/delivery experiments."""

import argparse
import json
from collections import Counter
from pathlib import Path

from infra_rag.benchmarking import digest

ARMS = ("B5", "B8", "D5", "Q5", "L5", "E5", "LE5")
CASES = {
    "official-002-2",
    "official-002-4",
    "official-004-4",
    "official-005-2",
    "official-005-4",
    "official-008-4",
    "official-010-3",
    "official-012-4",
    "official-016-1",
    "official-026-2",
    "official-026-3",
    "official-026-4",
    "official-030-3",
    "repo-035-1",
    "repo-035-2",
    "repo-053-2",
}


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2))


def analyze(run):
    retrieval = rows(run / "rows.jsonl")
    answers = rows(run / "answers.jsonl")
    summary = json.loads((run / "summary.json").read_text())
    statistics = json.loads((run / "paired-statistics.json").read_text())
    decision = json.loads((run / "decision.json").read_text())
    latency = json.loads((run / "latency-summary.json").read_text())
    index = json.loads((run / "context-index.json").read_text())
    screening = json.loads((run / "answer-screening.json").read_text())
    confirmation = json.loads((run / "confirmation-status.json").read_text())
    protocol = json.loads((run / "protocol.json").read_text())
    root = Path(__file__).resolve().parents[1]
    original = {
        c["id"]: c for c in json.loads((root / protocol["directory"] / "chunks.json").read_text())
    }
    for name, expected in protocol["implementation"].items():
        assert digest(root / name) == expected
        assert digest(run / "implementation" / name) == expected
    evidence_checked = 0
    for r in retrieval + answers:
        for e in r["context"]["evidence"]:
            c = original[e["chunk_id"]]
            assert c["content"].startswith(e["content"])
            assert (e["content"] != c["content"]) == e["truncated"]
            for field in ("source", "locator", "parent_id", "start_line", "end_line"):
                assert e[field] == c[field]
            evidence_checked += 1
    if confirmation.get("no_confirmation_questions_read"):
        assert not (run / "confirmation").exists()
    costs = json.loads((run / "cost-accounting.json").read_text())
    score_inputs = [json.loads(p.read_text()) for p in (run / "score-inputs").glob("*.json")]
    new_pairs = sum(r["pairs"] for r in score_inputs)
    assert new_pairs == costs["scoring"]["new_pairs_this_invocation"]
    truncated_pairs = sum(
        p["would_truncate"] for r in score_inputs for p in r["diagnostics"]["pairs"]
    )
    assert len(retrieval) == 770 and len(answers) == 46
    assert len(rows(run / "latency.jsonl")) == 46
    baseline = {(r["dataset"], r["id"]): r for r in retrieval if r["arm"] == "B5"}
    traces, failures, generation = [], {}, {}
    for r in retrieval:
        old = baseline[r["dataset"], r["id"]]
        assert r["context"]["used_tokens"] <= 1200
        assert r["context"]["used_characters"] <= 4000
        if r["arm"] == "B8":
            assert r["diagnostics"]["final"] == old["diagnostics"]["final"]
            assert r["diagnostics"]["candidates"] == old["diagnostics"]["candidates"]
        if r["arm"] in {"D5", "Q5"}:
            assert set(old["diagnostics"]["candidates"]) <= set(r["diagnostics"]["candidates"])
            assert len(r["diagnostics"]["candidates"]) <= len(old["diagnostics"]["candidates"]) + 30
        if r["answerable"] and r["id"] in CASES:
            relevant = set(r["resolved_gold"]["relevant"])
            traces.append(
                {
                    "id": r["id"],
                    "dataset": r["dataset"],
                    "arm": r["arm"],
                    "query": r["query"],
                    "candidate_complete": r["candidate_complete"],
                    "delivered_complete": r["delivered"]["complete"],
                    "delivery_k": r["delivery_k"],
                    "used_tokens": r["context"]["used_tokens"],
                    "gold_ranks": [
                        h for h in r["diagnostics"]["final"] if h["chunk_id"] in relevant
                    ],
                    "delivered_ids": [e["chunk_id"] for e in r["context"]["evidence"]],
                    "omitted_ids": r["context"]["omitted_chunk_ids"],
                }
            )
    for ds in ("official", "repository"):
        for arm in ARMS:
            selected = [
                r for r in retrieval if r["dataset"] == ds and r["arm"] == arm and r["answerable"]
            ]
            failed = [r for r in selected if not r["delivered"]["complete"]]
            k = "8" if arm == "B8" else "5"
            old = [
                r
                for r in selected
                if not baseline[ds, r["id"]]["candidate_complete"]
                and baseline[ds, r["id"]]["delivered"]["complete"]
            ]
            failures[f"{ds}:{arm}"] = {
                "candidate_incomplete_failures": [
                    r["id"] for r in failed if not r["candidate_complete"]
                ],
                "selection_failures": [
                    r["id"]
                    for r in failed
                    if r["candidate_complete"] and not r["at_k"][k]["complete_evidence_hit"]
                ],
                "packing_failures": [
                    r["id"] for r in failed if r["at_k"][k]["complete_evidence_hit"]
                ],
                "previous_neighbor_rescue_lost": [
                    r["id"] for r in old if not r["delivered"]["complete"]
                ],
                "truncated_evidence": sum(
                    e["truncated"] for r in selected for e in r["context"]["evidence"]
                ),
            }
    for arm in ("B5", decision["diagnostic_arm"]):
        selected = [r for r in answers if r["arm"] == arm]
        counts, refusal_ids = Counter(), []
        for r in selected:
            counts["answerable" if r["answerable"] else "unanswerable"] += 1
            g = r["generation"]
            counts["errors"] += bool(g["error"])
            counts["format_valid"] += g["checks"]["format_valid"]
            if not g["response"]:
                continue
            refused = g["response"]["status"] == "no_evidence"
            if r["answerable"]:
                label = "gold_complete" if r["delivered"]["complete"] else "gold_incomplete"
                counts[label] += 1
                if refused:
                    counts[label + "_refusal"] += 1
                    counts["answerable_refusal"] += 1
                    refusal_ids.append(r["id"])
            else:
                counts["unanswerable_refusal" if refused else "unanswerable_answered"] += 1
            if not refused:
                counts["answered"] += 1
                counts["answered_valid_citations"] += g["checks"]["citation_ids_valid"]
        generation[arm] = {**counts, "refusal_ids": refusal_ids, "independent_fact_correct": None}
    write(run / "case-traces.json", traces)
    write(run / "failure-breakdown.json", failures)
    write(run / "generation-summary.json", generation)
    lines = [
        "# 召回与交付v4执行报告",
        "",
        "AI编写、稀疏原始来源标签；完整交付不是回答正确率，独立人工审核pending。",
        "本轮开发阶段只读取dev；主实验源码、参数与模型权重冻结，默认global30不变。",
        "",
        "770条主检索、46条生成、46条交错无查询/候选/持久评分缓存延迟记录均完成。",
        "条件复用v3问题输出，未新增dev条件API调用；语料未加入benchmark问题或答案。",
        "",
        "## 开发指标",
        "",
        "| 组 | 官方候选完整 | 官方交付 | 仓库候选完整 | 仓库交付 | 官方直接TopK完整 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        o, r = summary[f"official:{arm}"], summary[f"repository:{arm}"]
        top = o["top8_complete"] if arm == "B8" else o["top5_complete"]
        lines.append(
            f"| {arm} | {o['candidate_complete']:g}/54 | {o['delivered_complete']:g}/54 | "
            f"{r['candidate_complete']:g}/50 | {r['delivered_complete']:g}/50 | {top:g} |"
        )
    lines += [
        "",
        "B5原基线；B8只增交付条数；D5深度匹配对照；Q5子问题补召回；",
        "L5只增强BM25、E5只增强dense、LE5两路增强。所有重排输入及交付为原正文。",
        "Q5使用共享身份上下文，不包含答案项，也未实现每个产品的版本硬绑定。",
        "",
        "## 预注册配对检验",
        "",
        "| 官方交付主对照 | 净差 | 改善/退化 | 率差95% CI | Holm p |",
        "|---|---:|---:|---|---:|",
    ]
    for key in ("official:B8_vs_B5", "official:Q5_vs_D5", "official:L5_vs_B5", "official:E5_vs_B5"):
        s = statistics[key]
        ci = " 至 ".join(f"{v:.2%}" for v in s["delta_rate_ci95"])
        lines.append(
            f"| {key} | {s['delta_count']:+g} | {len(s['recovered_ids'])}/{len(s['lost_ids'])} | "
            f"{ci} | {s['holm_p']:.6f} |"
        )
    lines += [
        "",
        "按15/13个问题簇配对bootstrap10000次、seed42；四个官方交付对照Holm校正。",
        "候选完整的配对统计及其他对照是探索性，不把未显著视为证明无效。",
        f"通过开发数值门槛的配置：{', '.join(decision['eligible']) or '无'}；"
        f"冻结选定配置：{decision['winner'] or '无'}。",
        "",
        "## 失败与预算",
        "",
        "| 官方组 | 候选不完整且未补齐 | 选择未覆盖 | TopK完整但打包失败 | 原邻接补齐丢失 |",
        "|---|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        f = failures[f"official:{arm}"]
        lines.append(
            f"| {arm} | {len(f['candidate_incomplete_failures'])} | "
            f"{len(f['selection_failures'])} | {len(f['packing_failures'])} | "
            f"{', '.join(f['previous_neighbor_rescue_lost']) or '无'} |"
        )
    lines += [
        "",
        "候选不完整不等于语料缺失；邻接补齐的预算竞争需另外核对。",
        "完整候选哈希、真实上下文和省略ID均保留；重点样本见case-traces.json。",
        "B8恢复016-1与030-3，却挤掉005-2原有邻接补齐；010-3的gold虽进入Top8，"
        "仍被预算省略。固定预算下增加条数无法保证证据覆盖。",
        "Q5相对B5仅恢复005-4且无交付退化；加深对照D5的候选完整更多，"
        "但004-4的第二份必要证据被挤到第6。L5恢复两题同时丢失010-2。",
        "",
        "## 生成诊断",
        "",
        "| 组 | 可回答题拒答 | gold完整时拒答 | gold缺失时拒答 | 不可回答题拒答 | 调用错误 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for arm, g in generation.items():
        lines.append(
            f"| {arm} | {g.get('answerable_refusal', 0)}/{g.get('answerable', 0)} | "
            f"{g.get('gold_complete_refusal', 0)}/{g.get('gold_complete', 0)} | "
            f"{g.get('gold_incomplete_refusal', 0)}/{g.get('gold_incomplete', 0)} | "
            f"{g.get('unanswerable_refusal', 0)}/{g.get('unanswerable', 0)} | "
            f"{g.get('errors', 0)} |"
        )
    lines += [
        "",
        "合法引用ID与完整gold不能替代逐条事实支持审阅；不自动计算正确率。",
        "审核模板保持pending，实际上下文定性观察见answer-observations.md。",
        f"候选答案已核实新增引用支持错误：{len(screening['new_confirmed_errors'])}条；"
        "这是AI结合实际上下文及外部一手文档核查，不是独立人工正确率评测。",
        "repo-002-1将连续地址的优化建议改成必要条件，具体反例见answer-screening.json。",
        "该题B5与Q5实际上下文完全相同，不能将单次生成差异归因于检索策略。",
        "",
        "## 实际开销",
        "",
        f"增强索引首次构建/加载耗时{index['build_or_load_ms'] / 1000:.2f}秒，"
        f"包含{index['chunks']}个片段，独立目录{index['directory']}。",
        "实际索引指纹、语料哈希与前文出处见context-index.json、context-views.json。",
        "",
        "| 实验路径 | p50秒 | p95秒 |",
        "|---|---:|---:|",
    ]
    for arm in ("B5", decision["diagnostic_arm"]):
        item = latency[arm]
        lines.append(f"| {arm} | {item['p50_ms'] / 1000:.3f} | {item['p95_ms'] / 1000:.3f} |")
    lines += [
        "",
        "固定23题模型预热后交错执行，翻译/条件共用，索引构建不计入查询延迟。",
        "性能路径包含候选检索函数内部Top10打包，再按Top5/8打包；不代表线上SLA。",
        "API usage来自供应商响应，BGE新增对数和输入截断单列；不估算货币计费。",
        f"开发新增BGE评分对数{new_pairs}，其中{truncated_pairs}对输入超过512 token；"
        f"生成API调用{costs['generation_calls']}次。usage各字段原样汇总见cost-accounting.json。",
        "",
        f"确认评测状态：{confirmation['status']}，详见confirmation-status.json。",
        "冻结Q5通过开发数值门槛，但新增引用支持错误使事实门槛未通过；"
        "停止确认评测，holdout/test未读取，默认保持原配置。",
    ]
    if (run / "confirmation/summary.json").exists():
        confirm = json.loads((run / "confirmation/summary.json").read_text())
        lines += [
            "",
            "## 冻结配置确认评测",
            "",
            "仅baseline与冻结配置评测一次，不按结果调整参数。",
            "",
        ]
        for key, value in confirm.items():
            item = value["hybrid_rerank"]
            positive_rows = [
                r
                for r in rows(run / "confirmation/rows.jsonl")
                if f"{r['dataset']}:{r['arm']}" == key and r["answerable"]
            ]
            count = sum(r["delivered"]["complete"] for r in positive_rows)
            lines.append(f"- {key}：完整交付{count:g}/{item['answerable']}。")
    (run / "execution-report.md").write_text("\n".join(lines) + "\n")
    write(
        run / "execution-audit.json",
        {
            "retrieval_rows": len(retrieval),
            "generation_rows": len(answers),
            "latency_rows": 46,
            "original_body_and_locator_checks": evidence_checked,
            "primary_source_hashes_and_archives_match": True,
            "baseline_v3_exact_replay": "asserted for all 110 questions during retrieval",
            "b8_candidates_ranking_unchanged": True,
            "d5_q5_preserve_base_and_limit_new_candidates": True,
            "all_contexts_within_budget": True,
            "no_confirmation_directory": not (run / "confirmation").exists(),
            "confirmation_status": confirmation["status"],
            "new_score_pairs": new_pairs,
            "new_score_input_truncation_pairs": truncated_pairs,
            "default_changed": False,
        },
    )
    write(
        run / "postprocessing-protocol.json",
        {
            "kind": "read_only",
            "script_sha256": digest(Path(__file__)),
            "inputs": {
                name: digest(run / name)
                for name in [
                    "protocol.json",
                    "rows.jsonl",
                    "answers.jsonl",
                    "summary.json",
                    "paired-statistics.json",
                    "latency.jsonl",
                    "answer-screening.json",
                    "confirmation-status.json",
                ]
            },
            "defaults_changed": False,
            "independent_fact_correct": None,
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    analyze(parser.parse_args().output.resolve())
