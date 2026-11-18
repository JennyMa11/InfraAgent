"""Audit the complete frozen grid and write a descriptive dev report."""

import argparse
from pathlib import Path

from grid_retrieval import BASE, QUALITY, summarize, validate_rows, verify
from operation_log import record_operation
from prepare_corpus_pilot import load, save

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.grid_metrics import feasible


def report(out, destination):
    protocol = verify(out)
    assert (
        digest(out / "index/index.json")
        == protocol["inputs"]["data/native-pagination-v1/run-20261029/index/index.json"]
    )
    for name, sha in protocol["implementation"].items():
        assert digest(out / "implementation" / name) == sha
    cases = {c["id"]: c for c in load(out / "cases.json")}
    stages = {}
    checks = {}
    all_rows = []
    for stage in ("screen", "repeat", "ann"):
        rows = [
            load(p) for p in (out / stage).glob("*.json") if not p.name.endswith(".sha256.json")
        ]
        schedule = load(out / f"{stage}-schedule.json")
        validate_rows(rows, schedule)
        for row in rows:
            path = out / stage / f"{row['id']}-{row['config']}-r{row['rep']}.json"
            assert digest(path) == load(path.with_suffix(".sha256.json"))["sha256"]
            assert row["case_sha256"] == canonical_hash(cases[row["id"]])
            assert row["run_id"] == out.name and row["stage"] == stage
            assert row["rerank_pairs"] <= 90
            actual_pairs = row["diagnostics"]["rerank"].get("pairs", [])
            assert len(actual_pairs) == row["rerank_pairs"]
            assert all(p["would_truncate"] is False for p in actual_pairs)
            assert not any(
                p["would_truncate"] for p in row["diagnostics"]["rerank"].get("pairs", [])
            )
            assert row["hit_ids"] == row["diagnostics"]["returned_chunk_ids"]
        summary = summarize(rows)
        assert summary == load(out / f"{stage}-summary.json")
        changes = {}
        for config in summary:
            groups = {}
            for r in rows:
                if r["config"] == config:
                    groups.setdefault(r["id"], []).append(r)
            changes[config] = {
                "rank_drift_ids": sorted(
                    cid for cid, rs in groups.items() if len({tuple(r["hit_ids"]) for r in rs}) > 1
                ),
                "metric_drift_ids": sorted(
                    cid
                    for cid, rs in groups.items()
                    if len({canonical_hash(r["metrics"]) for r in rs}) > 1
                ),
            }
        checks[stage] = {
            "expected": len(schedule),
            "completed": len(rows),
            "failed": 0,
            "missing": 0,
            "unique_questions": len({r["id"] for r in rows}),
            "drift": changes,
        }
        stages[stage] = summary
        all_rows.extend(rows)
    registry = []
    for r in all_rows:
        raw_path = out / r["stage"] / f"{r['id']}-{r['config']}-r{r['rep']}.json"
        registry.append(
            {
                "run_id": f"{out.parent.name}/{out.name}/{r['stage']}",
                "config_id": r["config"],
                "case_id": r["id"],
                "repetition": r["rep"],
                "raw_path": str(raw_path),
                "raw_sha256": digest(raw_path),
                "status": r["status"],
            }
        )
    identities = {(r["run_id"], r["config_id"], r["case_id"], r["repetition"]) for r in registry}
    assert len(identities) == len(registry)
    save(destination / "output-register.json", registry)
    manifest = load(out / "artifacts-manifest.json")
    mismatch = [name for name, sha in manifest.items() if digest(out / name) != sha]
    # SQLite files may checkpoint when the model process closes; retain that fact explicitly.
    nonvolatile = [name for name in mismatch if not name.startswith("index/chroma/")]
    assert not nonvolatile, nonvolatile
    champion = load(out / "repeat-selection.json")["champion"]
    ann = stages["ann"]
    safe_ann = feasible(ann[champion], ann[BASE])
    quality_gain = any(ann[champion][m] > ann[BASE][m] + 1e-12 for m in QUALITY)
    faster_ann = ann[champion]["p95_ms"] < ann[BASE]["p95_ms"]
    paired = {}
    for stage in ("repeat", "ann"):
        by = {(r["id"], r["config"], r["rep"]): r for r in all_rows if r["stage"] == stage}
        reps = sorted({r["rep"] for r in all_rows if r["stage"] == stage})
        paired[stage] = {}
        for rep in reps:
            paired[stage][str(rep)] = {
                name: sorted(
                    cid
                    for cid in cases
                    if bool(by[(cid, champion, rep)]["metrics"]["complete5"]) == winning
                    and bool(by[(cid, BASE, rep)]["metrics"]["complete5"]) != winning
                )
                for name, winning in (("complete5_gained", True), ("complete5_lost", False))
            }
    screening = [r for r in all_rows if r["stage"] == "screen"]
    screen_by = {(r["id"], r["config"]): r for r in screening}
    quality_tradeoffs = {}
    for c in stages["screen"]:
        quality_tradeoffs[c] = {
            metric: {
                change: sorted(
                    cid
                    for cid in cases
                    if (
                        screen_by[(cid, c)]["metrics"][metric]
                        - screen_by[(cid, BASE)]["metrics"][metric]
                    )
                    * sign
                    > 1e-12
                )
                for change, sign in (("gained", 1), ("lost", -1))
            }
            for metric in ("hit5", "mrr5", "complete5")
        }
    verification = {
        "stages": checks,
        "total_component_searches": len(all_rows),
        "answer_model_calls": 0,
        "semantic_task_success": None,
        "independent_human_review": "pending; no fabricated human review",
        "default_changed": False,
        "test_holdout_read": False,
        "champion": champion,
        "ann_quality_guard_passed": safe_ann,
        "ann_quality_and_latency_improved": safe_ann and quality_gain and faster_ann,
        "paired_complete5": paired,
        "screen_per_case_tradeoffs": quality_tradeoffs,
        "max_actual_rerank_pairs": max(r["rerank_pairs"] for r in all_rows),
        "source_count": len(protocol["sources"]),
        "manifest_volatile_changes": mismatch,
        "stage_results": stages,
        "protocol_sha256": digest(out / "protocol.json"),
    }
    save(destination / "verification.json", verification)
    lines = [
        "# Retrieval Grid v1：60道开发题",
        "",
        f"完成{len(all_rows)}次真实检索。精确检索重复阶段入围配置：`{champion}`。",
        "",
        "**仅为开发集探索。没有运行答案生成，没有测得回答正确率，默认配置未改。**",
        "",
        "## 协议与口径",
        "",
        "- 固定24篇来源、1535个结构片段，原30题加30道AI编写的来源对齐题；新增标签待独立审核。",
        "- 问题全部属于dev；未读取test/holdout。问题和答案未进入知识索引。",
        "- 网格：BM25/Dense对照；Hybrid候选15/30/45；重排关闭或批大小16/32，共11组。",
        "- 固定raw词法、中文原查询、RRF融合、union候选池；最多90个实际重排对。",
        "- source Recall/Hit/MRR基于返回的片段排名@5/@10；重复来源仍占排名。",
        "- Recall是每题命中来源数/已标注相关来源数的宏平均；Hit是至少命中一份相关来源。",
        "- MRR是首个相关来源片段的倒数排名均值。来源命中不代表命中了所问机制。",
        "- 59题只有一个gold来源，1题有两个；所以来源Recall和Hit非常接近。",
        "- 必要证据Recall按来源hash及原文区间计分，完整率要求同一替代组内所有必要项同时覆盖。",
        "- 这些完整率对应排名内原始片段，不是1200token最终正文交付率，也不是答案正确率。",
        "- 延迟是实模RetrievalService.search返回10条的wall时间，含诊断及上下文组装；",
        "  不含模型/索引加载、离线评分、磁盘保存、HTTP和生成。暖启动，无查询结果缓存。",
        "- 单进程串行、同题轮换配置；p50中位数，p95 nearest-rank。重复不是独立问题。",
        "- 预先冻结选择规则：基线+各质量指标领先者+最快非劣配置，最多5组；",
        "  精确检索3轮后，基线和最快非劣入围配置在ANN上2轮复测。非劣还要求原30题完整证据不丢失。",
        "- 不作显著性、置信区间或总体可靠性声明；这是同一dev上选择和比较后的描述性结果。",
        "",
    ]
    for stage, title in (
        ("screen", "11组精确检索初筛"),
        ("repeat", "精确检索重复计时"),
        ("ann", "ANN复测"),
    ):
        lines.extend(
            [
                "## " + title,
                "",
                "|配置|输出数|Recall@5|Hit@5|MRR@5|必要证据Recall@5|完整证据@5|P50 ms|P95 ms|",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for config, s in stages[stage].items():
            lines.append(
                f"|{config}|{s['outputs']}|{s['recall5']:.2%}|{s['hit5']:.2%}|"
                f"{s['mrr5']:.4f}|{s['required_recall5']:.2%}|{s['complete5']:.2%}|"
                f"{s['p50_ms']:.1f}|{s['p95_ms']:.1f}|"
            )
        lines.extend(["", "逐轮P95（ms）：", ""])
        lines.extend(f"- `{c}`：{s['round_p95_ms']}" for c, s in stages[stage].items())
        lines.extend(
            [
                "",
                "|配置|Recall@10|Hit@10|MRR@10|必要证据Recall@10|完整证据@10|",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for c, s in stages[stage].items():
            lines.append(
                f"|{c}|{s['recall10']:.2%}|{s['hit10']:.2%}|{s['mrr10']:.4f}|"
                f"{s['required_recall10']:.2%}|{s['complete10']:.2%}|"
            )
        lines.append("")
    baseline, chosen = ann[BASE], ann[champion]
    lines.extend(
        [
            "## 结论",
            "",
            f"ANN复测非劣质量门槛：{safe_ann}；质量和延迟同时改善："
            f"{verification['ann_quality_and_latency_improved']}。",
            f"`{BASE}` → `{champion}`：Recall@5 {baseline['recall5']:.2%} → "
            f"{chosen['recall5']:.2%}；Hit@5 {baseline['hit5']:.2%} → {chosen['hit5']:.2%}；"
            f"MRR@5 {baseline['mrr5']:.4f} → {chosen['mrr5']:.4f}。",
            f"检索P95 {baseline['p95_ms']:.1f} → {chosen['p95_ms']:.1f} ms；"
            f"变化 {(chosen['p95_ms'] / baseline['p95_ms'] - 1):+.1%}。",
            f"必要证据完整率@5 {baseline['complete5']:.2%} → {chosen['complete5']:.2%}。",
            f"逐轮完整证据得失：{paired}。",
            "",
            "本轮只完成组件调参；保持当前默认。先审核新增标签、检查个例及ANN重复波动，"
            "再在预先固定的确认集评测，方可讨论采用。",
            "",
        ]
    )
    lines.extend(["## 入围配置逐题得失（精确检索初筛）", ""])
    for c in load(out / "shortlist.json")["configs"]:
        if c == BASE:
            continue
        for metric, delta in quality_tradeoffs[c].items():
            lines.append(f"- `{c}` {metric}：增加 {delta['gained']}；丢失 {delta['lost']}。")
    lines.append("")
    lines.extend(
        [
            "## 完整性与限制",
            "",
            f"- 预定输出全部完成：{len(all_rows)}；失败0、缺失0。",
            f"- 实际最大重排对{verification['max_actual_rerank_pairs']}，没有重排输入截断。",
            "- 比例的分子、分母、值及coverage见verification.json的proportions；",
            "  分母是每配置实际输出数，重复3轮的180次输出仍只有60道独立题。",
            "- Recall和MRR的numerator为逐题归一化分数之和，并非证据数量的微平均。",
            "- 保存候选、排名、组件耗时、返回ID、重排对与来源映射。未运行端到端答案评测。",
            "- 稀疏标签可能漏计替代来源；部分整段标签偏宽，expand-046的why题标签待审。",
            "- 同一24篇来源导致样本相关；60道dev题的最优配置须经独立审核及固定确认集再考虑采用。",
            "- 本地串行暖启动延迟不能代表部署硬件、冷启动、并发负载或HTTP端到端延迟。",
            f"- 原始产物manifest中SQLite关闭后变化：{mismatch}；所有稳定产物hash已核验。",
            "",
            "## 产物与重现",
            "",
            f"- 运行目录：`{out}`；冻结协议SHA256：`{verification['protocol_sha256']}`。",
            (
                "- 运行命令：`uv run --extra models python scripts/grid_retriev"
                "al.py --output <全新目录> --phase <freeze|screen|repeat|ann>`。"
            ),
            (
                "- 依次执行四个阶段；报告命令：`uv run --extra models python scripts/rep"
                "ort_retrieval_grid.py --output <运行目录> --report <全新报告目录>`。"
            ),
            "- 依赖版本、模型文件hash、实现快照、源文件hash、调度和逐输出hash均保留。",
            "- output-register.json以实验/运行/阶段组成run_id，绑定原始输出hash；",
            "  再与config_id、case_id、repetition组成唯一标识，保留原始stage字段。",
        ]
    )
    lines.extend(
        ["", "## 重复检索波动", "", "|阶段|配置|排名变化题数|指标变化题数|", "|---|---|---:|---:|"]
    )
    for stage, check in checks.items():
        for c, drift in check["drift"].items():
            lines.append(
                f"|{stage}|{c}|{len(drift['rank_drift_ids'])}|{len(drift['metric_drift_ids'])}|"
            )
    lines.extend(["", "变化题目ID见verification.json；没有把ANN排名变化当作可删除失败。"])
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / "README.md"
    with target.open("x") as stream:
        stream.write("\n".join(lines) + "\n")
    save(
        destination / "manifest.json",
        {p.name: digest(p) for p in destination.iterdir() if p.is_file()},
    )
    return {k: v for k, v in verification.items() if k not in ("stage_results", "stages")}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    result = report(args.output.resolve(), args.report.resolve())
    record_operation("审计并汇总检索Grid", "核对冻结调度、hash、质量与计时分母", str(result))
    print(result)
