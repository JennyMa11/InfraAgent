"""Postprocess frozen selection outputs; no retrieval, generation or configuration tuning."""

import argparse
import json
from collections import Counter
from pathlib import Path

from infra_rag.benchmarking import digest

CASES = [
    "official-002-1",
    "official-002-2",
    "official-002-4",
    "official-004-4",
    "official-005-2",
    "official-012-2",
    "official-012-3",
    "official-010-4",
    "official-020-2",
    "official-028-4",
]


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2))


def analyze(run):
    rows = read_rows(run / "rows.jsonl")
    answers = read_rows(run / "answers.jsonl")
    summary = json.loads((run / "summary.json").read_text())
    decision = json.loads((run / "decision.json").read_text())
    pairs = json.loads((run / "paired-statistics.json").read_text())
    latency = json.loads((run / "latency-summary.json").read_text())
    quarantine = json.loads((run / "quarantine-policy.json").read_text())
    q_summary = json.loads((run / "quarantine-summary.json").read_text())
    cost = json.loads((run / "cost-accounting.json").read_text())
    assert len(rows) == 880 and len(answers) == 48
    assert all(r["context"]["used_tokens"] <= 1200 for r in rows)
    assert all(r["context"]["used_characters"] <= 4000 for r in rows)
    cases = []
    for row in rows:
        if row["dataset"] != "official" or row["id"] not in CASES:
            continue
        relevant = set(row["resolved_gold"]["relevant"])
        cases.append(
            {
                "id": row["id"],
                "arm": row["arm"],
                "candidate_complete": row["candidate_complete"],
                "top5_complete": row["at_k"]["5"]["complete_evidence_hit"],
                "delivered_complete": row["delivered"]["complete"],
                "gold_ranks": [r for r in row["diagnostics"]["final"] if r["chunk_id"] in relevant],
                "facets": row["diagnostics"]["facets"],
                "selected_ids": row["retrieved"][:5],
                "delivered_ids": [e["chunk_id"] for e in row["context"]["evidence"]],
                "selection_trace": row["diagnostics"]["selection_trace"][:5],
            }
        )
    write_json(run / "case-traces.json", cases)
    generation = {}
    for arm in sorted({r["arm"] for r in answers}):
        selected = [r for r in answers if r["arm"] == arm]
        counts = Counter(records=len(selected))
        refusals = []
        for row in selected:
            counts["answerable" if row["answerable"] else "unanswerable"] += 1
            g = row["generation"]
            counts["generation_errors"] += bool(g["error"])
            response = g["response"]
            if not response:
                continue
            refused = response["status"] == "no_evidence"
            counts["refused" if refused else "answered"] += 1
            if row["answerable"]:
                complete = row["delivered"]["complete"]
                label = "gold_complete" if complete else "gold_incomplete"
                counts[label] += 1
                if refused:
                    counts["answerable_refusal"] += 1
                    counts[label + "_refusal"] += 1
                    refusals.append(row["id"])
            elif refused:
                counts["unanswerable_refusal"] += 1
            else:
                counts["unanswerable_answered"] += 1
            if not refused:
                counts["answered_valid_citations"] += g["checks"]["citation_ids_valid"]
        generation[arm] = {
            **counts,
            "answerable_refusal_ids": refusals,
            "independent_fact_correct": None,
        }
    write_json(run / "generation-breakdown.json", generation)
    lines = [
        "# 证据选择实验执行报告",
        "",
        "AI编写、稀疏来源标签；完整证据交付不等于回答正确率，独立事实审核仍待完成。",
        "默认保持processed_global30。冻结协议、实现、条件锚点、评分矩阵和上下文均已保存。",
        "",
        "## 实际执行",
        "",
        "- 两套候选池×四种选择策略，共880条dev检索；两池原始分数不变，F/G共享条件矩阵。",
        "- 23道固定样本×基线/诊断配置，加两道来源证据oracle，共48条生成记录。",
        "- 源文隔离单独运行110条检索、2条生成；性能对照23题×两配置，禁用相关缓存。",
        "- 初次启动的通用校验器加载过holdout作完整性校验，未进行推理、检索或调参。",
        "  已停止并归档为setup-aborted-20261002；正式启动只读取dev，110份条件原样复用。",
        "",
        "## 交付与排序",
        "",
        "| 配置 | 官方交付 | 仓库交付 | 官方Top5/10 | 官方MRR@5 | 官方nDCG@5 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for arm in ("P0-T", "P0-M", "P0-F", "P0-G", "P1-T", "P1-M", "P1-F", "P1-G"):
        o, r = summary[f"official:{arm}"], summary[f"repository:{arm}"]
        k = o["summary"]["at_k"]["5"]
        lines.append(
            f"| {arm} | {o['delivered_complete']:g}/54 | "
            f"{r['delivered_complete']:g}/50 | {o['top5_complete']:g}/"
            f"{o['top10_complete']:g} | {k['mrr']:.4f} | {k['ndcg']:.4f} |"
        )
    lines += [
        "",
        "P0-T应复现43/54与40/50；P1-T关闭旧版本保护，历史42/54不是新控制组。",
        "候选完整在同池内保持不变；来源构成、类型和截断另见breakdown.json。",
        "",
        "## 预注册主检验",
        "",
        "| 对照 | 改善/退化 | 净差 | 配对率差95% CI | Holm p |",
        "|---|---:|---:|---|---:|",
    ]
    for key in ("official:P1:G_vs_F", "official:P0:G_vs_T"):
        item = pairs[key]
        ci = " 至 ".join(f"{v:.2%}" for v in item["delta_rate_ci95"])
        lines.append(
            f"| {key} | {len(item['recovered_ids'])}/{len(item['lost_ids'])} | "
            f"{item['delta_count']:+g} | {ci} | {item['holm_p']:.6f} |"
        )
    lines += [
        "",
        "按问题簇配对bootstrap 10000次、seed42；主实验用精确簇置换。",
        "其他对照是探索性；CI跨0或未显著不能解释成已经证明无效。",
        f"开发门槛胜出配置：{decision['winner'] or '无'}。确认阶段结果见confirmation-status.json。",
        "",
        "## 失败位置与回归样本",
        "",
    ]
    for arm in ("P0-T", decision["diagnostic_arm"]):
        positive = [
            r for r in rows if r["dataset"] == "official" and r["arm"] == arm and r["answerable"]
        ]
        failed = [r for r in positive if not r["delivered"]["complete"]]
        missing = sum(not r["candidate_complete"] for r in failed)
        packing = sum(r["at_k"]["5"]["complete_evidence_hit"] for r in failed)
        lines.append(
            f"- {arm}：失败{len(failed)}题；候选不足{missing}，"
            f"候选完整但选择未覆盖{len(failed) - missing - packing:g}，打包丢失{packing:g}。"
        )
    lines += ["", "| 样本 | P0-T | 诊断配置 |", "|---|---:|---:|"]
    for cid in CASES:
        items = {r["arm"]: r for r in cases if r["id"] == cid}
        lines.append(
            f"| {cid} | {items['P0-T']['delivered_complete']:g} | "
            f"{items[decision['diagnostic_arm']]['delivered_complete']:g} |"
        )
    lines += [
        "",
        "gold排名、条件和真实选择轨迹见case-traces.json；不据此再次调整本轮参数。",
        "两池G与各自T的官方逐题交付均相同；G相对F的恢复不能表述为超过原问题控制组。",
        "",
        "## 生成诊断",
        "",
        "| 配置 | 可回答题拒答 | gold完整时拒答 | gold缺失时拒答 | 不可回答题拒答 | 错误 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for arm, item in generation.items():
        lines.append(
            f"| {arm} | {item.get('answerable_refusal', 0)}/{item['answerable']} | "
            f"{item.get('gold_complete_refusal', 0)}/{item.get('gold_complete', 0)} | "
            f"{item.get('gold_incomplete_refusal', 0)}/{item.get('gold_incomplete', 0)} | "
            f"{item.get('unanswerable_refusal', 0)}/{item.get('unanswerable', 0)} | "
            f"{item.get('generation_errors', 0)} |"
        )
    lines += [
        "",
        "拒答与缺少原始gold只作诊断；等价证据与引用支持仍需逐条核验。",
        "格式/引用ID合法不等于事实正确；审核模板保留pending。",
        "002-2的oracle仍拒答；002-4的oracle原始gold第二段在implements处结束，"
        "且回答未覆盖模型支持前置，需检查标注的语义充分性。详见answer-observations.md。",
        "",
        "## 源文隔离",
        "",
        f"选入{len(quarantine['selected_risks'])}项源文范围疑点，"
        f"跳过{len(quarantine['skipped_risks'])}项不符合专家范围等式的旧标记；"
        f"阻止{len(quarantine['blocked_ids'])}个片段及其邻接/别名入口。",
        "风险由原始行号、逐字引用和文件哈希确定，与benchmark题目无关；原文未修改。",
        "",
    ]
    for ds, item in q_summary.items():
        lines.append(
            f"- {ds}：隔离相对{decision['quarantine_arm']}交付净差"
            f"{item['comparison']['delta_count']:+g}；原始gold命中隔离的题："
            f"{', '.join(item['original_gold_intersects_quarantine']) or '无'}。"
        )
    lines += [
        "",
        "AI源文风险与Q1回答均待独立核验，Q1不自动进入生产或确认集。",
        "",
        "## 实测开销",
        "",
        "| 配置 | 检索p50 ms | 条件API p50 ms | 条件评分p50 ms | 总耗时p50/p95 ms |",
        "|---|---:|---:|---:|---:|",
    ]
    for arm in ("baseline", "candidate"):
        item = latency[arm]
        lines.append(
            f"| {arm} | {item['retrieval_ms']['p50_ms']:.1f} | "
            f"{item['facet_api_ms']['p50_ms']:.1f} | "
            f"{item['facet_rerank_ms']['p50_ms']:.1f} | "
            f"{item['end_to_end_ms']['p50_ms']:.1f}/"
            f"{item['end_to_end_ms']['p95_ms']:.1f} |"
        )
    lines += [
        "",
        "预热后固定23题交错执行，不使用重放计时；英文翻译两组共用，未计入该阶段。",
        "测量路径先生成Top10候选再选Top5，含候选生成函数的内部打包开销；"
        "这是实验路径延迟，不代表线上服务SLA。",
        f"开发条件评分新增{cost['additional_bge_pairs']}对，"
        f"其中{cost['bge_pairs_would_truncate']}对超过模型输入限长；F/G及两池共享结果。",
        "API usage按供应商原始响应汇总在cost-accounting.json，计价未测量。",
        "",
        "原始协议见protocol.json，逐题记录见rows.jsonl；完整生成提示与供应商usage已保存。",
    ]
    (run / "execution-report.md").write_text("\n".join(lines) + "\n")
    inputs = [
        "protocol.json",
        "rows.jsonl",
        "answers.jsonl",
        "summary.json",
        "paired-statistics.json",
        "latency.jsonl",
        "quarantine-rows.jsonl",
        "quarantine-answers.jsonl",
        "cost-accounting.json",
    ]
    write_json(
        run / "postprocessing-protocol.json",
        {
            "kind": "read_only_postprocessing",
            "script_sha256": digest(Path(__file__)),
            "inputs": {name: digest(run / name) for name in inputs},
            "independent_fact_correct": None,
            "defaults_changed": False,
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    analyze(parser.parse_args().output.resolve())


if __name__ == "__main__":
    main()
