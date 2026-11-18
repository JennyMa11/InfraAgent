"""Verify the linked A-C and corrected D-E runs; export final dev-only evidence."""

import argparse
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path

from operation_log import ROOT, record_operation
from report_grid_v2 import audit_stage, metrics

from infra_rag.benchmarking import canonical_hash, digest, write_new
from infra_rag.embedding_experiments import freeze_gold, source_document
from infra_rag.grid_metrics import latency
from infra_rag.grid_v2 import delivery_gate
from infra_rag.paired_statistics import holm, paired_statistics


def load(path):
    return json.loads(path.read_text())


def verify_manifest(root, name):
    for path, sha in load(root / name).items():
        if digest(root / path) != sha:
            raise ValueError("Artifact differs: " + str(root / path))


def finalize(parent, run, timing, out):
    if out.exists():
        raise ValueError("Fresh final report directory required")
    verify_manifest(parent, "run-artifacts-manifest.json")
    verify_manifest(run, "run-followup-manifest.json")
    verify_manifest(timing, "run-confirmation-manifest.json")
    confirm = load(timing / "confirmation-protocol.json")
    if confirm["parent_manifest_sha256"] != digest(run / "run-followup-manifest.json"):
        raise ValueError("Timing lineage differs")
    view = load(timing / "exact-view-equivalence.json")
    if view["verified_queries"] != 110 or not view["raw_exact_equals_canonical_exact"]:
        raise ValueError("Logical identity view differs")
    p = load(run / "protocol.json")
    if p["sources"] != load(timing / "protocol.json")["sources"]:
        raise ValueError("Confirmation source set differs")
    if p["models"] != load(timing / "protocol.json")["models"]:
        raise ValueError("Confirmation model set differs")
    follow = load(run / "followup-protocol.json")
    if follow["parent_manifest_sha256"] != digest(parent / "run-artifacts-manifest.json"):
        raise ValueError("Lineage differs")
    for source, sha in p["sources"].items():
        if digest(source) != sha:
            raise ValueError("Source changed")
    for model in p["models"].values():
        if "files" in model:
            for name, sha in model["files"].items():
                if digest(Path(model["path"]) / name) != sha:
                    raise ValueError("Model changed")
    status = {}
    groups = {}
    summaries = {}
    for stage in ("A", "B", "C", "D", "E", "repeat", "ann"):
        root = parent if stage in "ABC" else timing if stage in ("repeat", "ann") else run
        status[stage], groups[stage] = audit_stage(root, stage)
        if not status[stage]["complete"]:
            raise ValueError("Incomplete stage: " + stage)
        summaries[stage] = {name: metrics(rows) for name, rows in groups[stage].items()}
    base_status, base_groups = audit_stage(run, "baseline")
    if not base_status["complete"]:
        raise ValueError("Followup baseline incomplete")
    base_id = next(iter(base_groups))
    baseline = base_groups[base_id]
    summaries["baseline"] = {base_id: metrics(baseline)}
    old_status, old_base = audit_stage(parent, "baseline")
    if not old_status["complete"]:
        raise ValueError("Parent baseline incomplete")
    old = {(r["dataset"], r["id"]): r for r in old_base[base_id]}
    for r in baseline:
        reference = old[r["dataset"], r["id"]]
        for key in ("candidate_ids", "ranked_ids", "pack5", "pack10"):
            if r[key] != reference[key]:
                raise ValueError("BASE raw delivery replay differs: " + key)
    # Parent raw observations were independently rescored by the continuation.
    rescored = load(run / "parent-rescored.json")
    if sum(map(len, rescored.values())) != 2750:
        raise ValueError("Parent rescore coverage differs")
    selection = load(run / "quality-selection.json")
    ablation = load(run / "ablation.json")
    required = {
        "minus_bm25",
        "minus_dense",
        "minus_rrf",
        "minus_reranker",
        "minus_semantic",
        "minus_neighbors",
    }
    labels = set(ablation["labels"])
    if "minus_neighbors" not in labels and ablation["not_applicable"]:
        labels.add("minus_neighbors")
    if labels != required:
        raise ValueError("Missing named ablations")
    for ident in ablation["labels"].values():
        if ident not in groups["E"]:
            raise ValueError("Missing ablation output")
    winner = selection["winner"]
    if winner["index"] != "I0":
        raise ValueError("Expected retained-reference D study")
    indexes = {load(m)["name"]: load(m) for m in (run / "indexes").glob("*/manifest.json")}
    if indexes["I0"]["fingerprint"]["chunk_size"] != indexes["I3"]["fingerprint"]["chunk_size"]:
        raise ValueError("Semantic/window ablation changes chunk size")
    resources = {
        "runs": {},
        "generation_calls": 0,
        "model_cost_usd": None,
        "prediction_ledger_scope": "reranker only; includes native warmups and failed attempts",
        "embedding_actual_operations_all_attempts": None,
        "embedding_accounting_note": "No complete encoder attempt ledger; not inferred as zero",
    }
    for label, root in (("quality_followup", run), ("fresh_confirmation", timing)):
        events = [json.loads(s) for s in (root / "packets/events.jsonl").read_text().splitlines()]
        starts = {e["attempt"]: e for e in events if e["status"] == "started"}
        returned = {e["attempt"]: e for e in events if e["status"] == "returned"}
        if starts.keys() != returned.keys() or any(
            e["status"] in ("failed", "input_rejected") for e in events
        ):
            raise ValueError("Incomplete model accounting: " + label)
        if any(e["requested_pairs"] > 90 for e in starts.values()):
            raise ValueError("Pair cap")
        if label == "fresh_confirmation" and any(
            e["status"] == "cache_hit" or e.get("cache_enabled") is True for e in events
        ):
            raise ValueError("Cached prediction in fresh timing")
        resources["runs"][label] = {
            "packet_events": dict(Counter(e["status"] for e in events)),
            "new_prediction_operations": len(returned),
            "new_actual_pairs": sum(e["actual_pairs"] for e in returned.values()),
            "fresh_timing_operations": sum(
                e.get("cache_enabled") is False for e in returned.values()
            ),
        }
    score_files = [
        f for f in (parent / "cache/scores").glob("*.json") if not f.name.endswith(".sha256.json")
    ]
    from report_grid_v2 import verified

    scores = [verified(f) for f in score_files]
    resources["parent_sealed_prediction_results"] = {
        "operations": len(scores),
        "accounting": "Sealed completed score results; interrupted unknown attempt separate",
        "actual_pairs": sum(len(v["scores"]) for v in scores),
    }
    resources["parent_interrupted_attempt"] = load(
        ROOT / "evals/grid-v2" / parent.name / "interruption.json"
    )
    resources["prior_followup_ANN_initialization"] = {
        "status": "failed",
        "error": "DuplicateIDError",
        "ANN_model_operations": 0,
        "preserved_run": str(run),
    }
    for stage in ("repeat", "ann"):
        for rows in groups[stage].values():
            for r in rows:
                if any(v["would_truncate"] for v in r["diagnostics"]["rerank"].get("pairs", [])):
                    raise ValueError("Observed input truncation")
                if r["context"]["used_tokens"] > 1200 or r["context"]["used_characters"] > 4000:
                    raise ValueError("Observed context budget violation")
    rounds = {
        stage: {
            ident: {
                str(rep): {
                    ds: latency(
                        [r["elapsed_ms"] for r in rs if r["rep"] == rep and r["dataset"] == ds]
                    )
                    for ds in ("official", "repository")
                }
                for rep in range(3)
            }
            for ident, rs in groups[stage].items()
        }
        for stage in ("repeat", "ann")
    }
    confirmation = load(timing / "confirmation-gates.json")
    confirmation_quality = all(
        gate["eligible"] for stage in confirmation.values() for gate in stage["quality"]
    )
    exact_latency = next(iter(confirmation["repeat"]["timing"].values()))
    ann_latency = next(iter(confirmation["ann"]["timing"].values()))
    latency_gate = {
        ds: {
            "ratio": ann_latency[ds]["p95_ms"] / exact_latency[ds]["p95_ms"],
            "passed": ann_latency[ds]["p95_ms"] <= 1.5 * exact_latency[ds]["p95_ms"],
        }
        for ds in ("official", "repository")
    }
    # Export the original pre-frozen labels, not post-output label edits.
    docs = {s: source_document(Path(s).read_text(), h) for s, h in p["sources"].items()}
    gold = []
    for r in load(run / "cases.json"):
        q = {
            **r,
            "evidence_alternatives": r["resolved_gold"]["evidence_alternatives"]
            if r["answerable"]
            else [],
        }
        gold.append(
            {
                "id": r["id"],
                "dataset": r["dataset"],
                "group_id": r["group_id"],
                "answerable": r["answerable"],
                "source_intervals": freeze_gold(q, docs),
                "annotation": "Export of pre-frozen AI source labels; human review pending",
            }
        )
    stats = {}
    for ident, rows in rescored.items():
        if not ident.startswith("C:"):
            continue
        for ds in ("official", "repository"):
            before = [{**r, "delivered": r["delivery5"]} for r in baseline if r["dataset"] == ds]
            after = [{**r, "delivered": r["delivery5"]} for r in rows if r["dataset"] == ds]
            stats[ident + ":" + ds] = paired_statistics(before, after)
    decision = load(timing / "decision.json")
    decision["confirmation_quality_passed"] = confirmation_quality
    decision["ANN_vs_Exact_latency_gate"] = latency_gate
    decision["independent_human_review"] = "pending"
    if decision["adopt"] or decision["test_holdout_read"]:
        raise ValueError("Forbidden adoption/confirmation")
    out.mkdir(parents=True)
    comparisons = {base_id: baseline, **groups["C"], **groups["D"]}
    objective = {}
    eligibility = {}
    for ident, rs in comparisons.items():
        positive = [r for r in rs if r["answerable"]]
        objective[ident] = [
            sum(r["delivery5"]["complete"] for r in positive if r["dataset"] == ds)
            for ds in ("official", "repository")
        ] + [sum(r["rank_metrics10"]["mrr"] for r in positive), -sum(r["pairs"] for r in rs)]
        eligibility[ident] = delivery_gate(rs, baseline)

    def front(keys):
        return [
            a
            for a in keys
            if not any(
                a != b
                and all(x >= y for x, y in zip(objective[b], objective[a], strict=True))
                and any(x > y for x, y in zip(objective[b], objective[a], strict=True))
                for b in keys
            )
        ]

    pareto = {
        "axes": [
            "official_delivery5_count",
            "repo_delivery5_count",
            "MRR10_sum",
            "negative_nominal_pairs",
        ],
        "quality_cost_front": front(list(objective)),
        "eligible_front": front([k for k in objective if eligibility[k]["eligible"]]),
        "eligibility": eligibility,
        "latency_for_unmeasured_configs": None,
        "note": "No latency dominance claim for untimed configurations",
    }
    failures = {}
    cases = {(r["dataset"], r["id"]): r for r in load(run / "cases.json")}
    for ident, rs in comparisons.items():
        counts = Counter()
        by_type = defaultdict(Counter)
        by_source = defaultdict(Counter)
        for r in rs:
            if not r["answerable"]:
                continue
            stage = (
                "delivered"
                if r["delivery5"]["complete"]
                else "candidate_gap"
                if not r["candidate"]["complete"]
                else "rank_gap"
                if not r["ranked_complete5"]["complete"]
                else "packing_gap"
            )
            counts[stage] += 1
            case = cases[r["dataset"], r["id"]]
            by_type[case["question_type"]][stage] += 1
            sources = {
                s["absolute_source"]
                for g in case["resolved_gold"]["evidence_alternatives"]
                for s in g["spans"]
            }
            for source in sources:
                by_source[source][stage] += 1
        failures[ident] = {"counts": dict(counts), "by_type": by_type, "by_gold_source": by_source}
    write_new(out / "pareto.json", pareto)
    write_new(out / "failure-analysis.json", failures)
    (out / "failure-analysis.md").write_text(
        "# 分阶段损失\n\n详细计数见failure-analysis.json。"
        "先查实际交付，再区分候选缺口、排名缺口和打包缺口。"
        "候选缺口不等于知识库没资料；分块完整性另需查索引全文覆盖。"
        "按Gold来源的分类可重叠，不能相加当总题数。未调用答案模型，因此生成错误/答案正确性均未知。\n"
    )
    from transformers import AutoTokenizer

    model = p["models"]["embedding"]
    options = load(Path(model["path"]) / "sentence_bert_config.json")
    tokenizer = AutoTokenizer.from_pretrained(
        model["path"], local_files_only=True, do_lower_case=options["do_lower_case"]
    )
    rt = AutoTokenizer.from_pretrained(p["models"]["reranker"]["path"], local_files_only=True)
    chunk_maps = {
        name: {
            c["id"]: c["content"]
            for c in load(
                next(
                    m.parent / "index.json"
                    for m in (run / "indexes").glob("*/manifest.json")
                    if load(m)["name"] == name
                )
            )["chunks"]
        }
        for name in indexes
    }
    unique_inputs = {}
    nominal_pairs = 0
    max_body_tokens = max_body_characters = 0
    for rs in [baseline, *(rs for stage in "ABCDE" for rs in groups[stage].values())]:
        for r in rs:
            for k in (5, 10):
                pack = r[f"pack{k}"]
                max_body_tokens = max(max_body_tokens, pack["used_tokens"])
                max_body_characters = max(max_body_characters, pack["used_characters"])
                if pack["used_tokens"] > 1200 or pack["used_characters"] > 4000:
                    raise ValueError("Quality pack exceeds budget")
            index = r["config"].split("-", 1)[0]
            nominal_pairs += r["pairs"]
            for cid in r["candidate_ids"][: r["pairs"]]:
                pair = (r["query"], chunk_maps[index][cid])
                if pair not in unique_inputs:
                    unique_inputs[pair] = len(rt.encode(*pair, truncation=False))
    if max(unique_inputs.values(), default=0) > 512:
        raise ValueError("Reconstructed quality input overflow")
    write_new(
        out / "input-and-budget-audit.json",
        {
            "quality_nominal_pairs": nominal_pairs,
            "unique_query_body_inputs": len(unique_inputs),
            "max_reranker_input_tokens": max(unique_inputs.values(), default=0),
            "reranker_limit": 512,
            "max_pack_tokens": max_body_tokens,
            "max_pack_characters": max_body_characters,
            "audit_model_predictions": 0,
            "cost_note": "Nominal configuration pairs are not actual prediction usage",
        },
    )
    wire = []
    for r in baseline:
        e = r["pack5"]["evidence"]
        canonical = "\n\n".join(
            f"[{v['citation_id']}] 来源：{v['locator']}\n{v['content']}" for v in e
        )
        ordinal = "\n\n".join(
            f"[E{i}] 来源：{v['locator']}\n{v['content']}" for i, v in enumerate(e, 1)
        )
        wire.append(
            {
                "dataset": r["dataset"],
                "id": r["id"],
                "body_budget_tokens": r["pack5"]["used_tokens"],
                "canonical_tokens": len(tokenizer.encode(canonical, add_special_tokens=False)),
                "ordinal_tokens": len(tokenizer.encode(ordinal, add_special_tokens=False)),
                "canonical_characters": len(canonical),
                "ordinal_characters": len(ordinal),
            }
        )
    write_new(
        out / "serialization-overhead.json",
        {
            "rows": wire,
            "tokenizer": "frozen embedding tokenizer",
            "full_prompt_or_actual_API_usage": False,
            "provider_aliasing_variants_reported_separately": True,
        },
    )
    write_new(
        out / "human-gold-review-template.json",
        [
            {
                "id": g["id"],
                "dataset": g["dataset"],
                "gold_sha256": canonical_hash(g),
                "status": "pending",
                "reviewer": None,
                "reviewed_at": None,
                "source_supported": None,
            }
            for g in gold
        ],
    )
    for name, value in (
        ("completion-audit.json", status),
        ("confirmation.json", confirmation),
        ("confirmation-rounds.json", rounds),
        ("dense-identity-view.json", load(timing / "dense-identity-view.json")),
        ("summary.json", summaries),
        ("gold.json", gold),
        ("index-manifest.json", indexes),
        ("resources.json", resources),
        ("ablation.json", ablation),
        ("decision.json", decision),
        (
            "statistics-C.json",
            {
                "contrasts": stats,
                "holm": holm({k: v["cluster_permutation_p"] for k, v in stats.items()}),
            },
        ),
    ):
        write_new(out / name, value)
    shutil.copyfile(run / "statistics.json", out / "statistics-D.json")
    shutil.copyfile(Path(__file__), out / "report-script.py")
    write_new(
        out / "lineage.json",
        {
            "A_C": str(parent.resolve()),
            "D_E": str(run.resolve()),
            "timing": str(timing.resolve()),
            "confirmation_manifest_sha256": digest(timing / "run-confirmation-manifest.json"),
            "parent_manifest_sha256": digest(parent / "run-artifacts-manifest.json"),
            "followup_manifest_sha256": digest(run / "run-followup-manifest.json"),
            "rescored_parent_outputs": 2750,
            "raw_BASE_replay_exact": 110,
            "independent_run": False,
        },
    )
    text = [
        "# Grid v2：A–E开发网格结果",
        "",
        "A–C来自r6，D–E来自修正基线保留分支的r7；2750份父级原始交付/候选重新计分，未复制旧决策。",
        "",
        "| 阶段 | 输出数 | 完成 |",
        "|---|---:|---:|",
    ]
    for name, s in status.items():
        text.append(f"| {name} | {s['planned']} | {s['completed']} |")
    text += ["", "| 基线指标 | 官方开发集 | 仓库开发集 |", "|---|---:|---:|"]
    base_metrics = metrics(baseline)
    for field, label in (
        ("candidate_complete", "候选完整"),
        ("ranked_complete5", "排名完整@5"),
        ("delivery5", "实际交付完整@5"),
        ("hit5", "来源Hit@5"),
        ("mrr10", "来源MRR@10"),
    ):
        values = [base_metrics[ds][field] for ds in ("official", "repository")]
        text.append(
            f"| {label} | "
            + " | ".join(
                f"{v['numerator']:.4f}/{v['denominator']} ({v['value']:.2%})" for v in values
            )
            + " |"
        )
    text += ["", "| 消融 | 官方净变化 | 仓库净变化 | 丢失基线题 |", "|---|---:|---:|---:|"]
    for label, gate in ablation["deltas"].items():
        text.append(
            f"| {label} | {gate['delta']['official']:+d} | "
            f"{gate['delta']['repository']:+d} | {len(gate['losses'])} |"
        )
    text += [
        "",
        "110个冻结开发问题（官方60、仓库50），配置与重复不会增加独立样本数。正例分母分别54和50，6道负例不进入正例覆盖率。",
        "",
        "## 结论",
        "",
        "没有发现通过净增至少2题且零基线丢失门槛的新质量冠军，保持修复版450字符结构基线。"
        if not selection["new_quality_champion"]
        else "发现开发集候选，独立审核前不采用。",
        "",
        "- A：结构600字符与450结构候选完整数相同，但片段更少；窗口450保留作策略对照。",
        "- B：入围结构600、Hybrid K50、RRF30；其他入围名额没有强行填满。",
        "- C：重排开启仍净减1题、丢失2道基线题，未通过零丢失门槛。",
        "- D：RRF30/100质量相同；complete净增1但丢失3题。",
        "  深度30/截断候选池各净减4题；关闭邻段净减2题。",
        "- 深度60与90在所有候选池≤60的基线上等价，单列而不重复运行。",
        "- E：六个命名消融映射至实际试验；−RRF复用最佳单路结果，不伪称额外独立实验。",
        "",
        "## 测量与限制",
        "",
        "查询使用历史冻结的英文scoring_query，没有在线翻译调用；这不是原始中文用户查询的表现。",
        "原始查询诊断见r2独立产物，不与本轮网格混算；不能将本轮覆盖率宣传为中文线上问答准确率。",
        "Hit/MRR/nDCG是稀疏来源标签指标，完整交付是必要原文区间指标；两者不能互相替代。",
        "",
        "ANN初次初始化因重复ID失败；原始索引未修改，新确认轮仅对全部字段与向量相同的同ID记录建立逻辑点视图。",
        "110题Raw Exact、逻辑视图Exact和归档Top30全部一致；新的Exact与ANN共享该视图。",
        "重复ID的上游复用问题仍需后续独立修复，本轮未切换产品索引。",
        f"Exact/ANN逐轮完整交付确认：{confirmation_quality}；延迟门槛详见decision.json。",
        f"Exact热启动计时（毫秒）：{exact_latency}。",
        f"ANN热启动计时（毫秒）：{ann_latency}。",
        "",
        "质量回放允许精确模型输入包缓存；repeat/ANN阶段禁用包缓存，每次重新执行检索和模型预测。计时包含同等本地账目开销，不含HTTP和答案生成，不能称为端到端服务P95。",
        "重排模型预测事件与中断另存；编码器的完整尝试账目未知，不记为零。r6中断操作完成对数未知，没有记作零。语料、模型、实现、索引及逐条轨迹有哈希链。",
        "全部结论是稀疏AI gold下的开发结果，独立人工事实审核pending；答案正确率、拒答正确率未知。",
        "没有答案生成、没有读取test/holdout、没有启用后台服务或切换默认配置。",
        "",
    ]
    (out / "report.md").write_text("\n".join(text))
    write_new(
        out / "artifacts-manifest.json",
        {str(f.relative_to(out)): digest(f) for f in out.iterdir() if f.is_file()},
    )
    record_operation(
        "完成Grid v2 A-E联动验收报告",
        "逐阶段、模型账目和原文预算验证后报告",
        str(out),
        "独立人工审核pending，不采用默认配置",
    )
    print({k: status[k]["completed"] for k in status})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--parent", type=Path, required=True)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--timing", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    finalize(a.parent, a.run, a.timing, a.out)


if __name__ == "__main__":
    main()
