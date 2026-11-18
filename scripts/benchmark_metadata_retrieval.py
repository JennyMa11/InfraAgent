"""Dev-only B/D/H/M navigation experiment; no generation or service changes."""

import argparse
import json
from pathlib import Path
from time import perf_counter

from benchmark_original_rag_v7 import (
    V6,
    Engine,
    append,
    evaluation,
    freeze,
    prepare,
    read_rows,
    write_json,
)
from operation_log import record_operation
from prepare_corpus_v2 import ROOT

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.evaluation import evidence_metrics
from infra_rag.metadata_experiments import (
    ARMS,
    VERSION,
    MetadataNavigator,
    candidate_pool,
    loss_stage,
)
from infra_rag.offline_evaluation import latency_summary
from infra_rag.paired_statistics import holm, paired_statistics
from infra_rag.recall_experiments import rank_fusion


def ratio(numerator, denominator):
    return {
        "numerator": numerator,
        "denominator": denominator,
        "value": numerator / denominator if denominator else None,
    }


def baseline_gate(mapping, bundles, chunks, count):
    reference = {
        (r["dataset"], r["id"]): r
        for r in read_rows(V6 / "rows.jsonl")
        if r["arm"] == "B-k8-l0-p1-n0"
    }
    history = ROOT / "evals/merged-corpus-v2/original-rag-v7/run-20261003-v3"
    manifest = json.loads((history / "artifacts-manifest.json").read_text())["files"]
    if digest(history / "rows.jsonl") != manifest["rows.jsonl"]:
        raise ValueError("Historical v7 rows changed")
    candidates = {
        (r["dataset"], r["id"]): r for r in read_rows(history / "rows.jsonl") if r["arm"] == "B"
    }
    outputs = {}
    for key, row in mapping.items():
        bundle = bundles[key]["B5"]
        output = evaluation(row, "B", bundle, chunks, count)
        if output["context"] != reference[key]["context"]:
            raise ValueError(f"Baseline delivery mismatch: {key}")
        if set(output["candidate_ids"]) != set(candidates[key]["candidate_ids"]):
            raise ValueError(f"Baseline candidates mismatch: {key}")
        outputs[key] = output
    return outputs


def measure(row, arm, bundle, chunks, count, trace=None, owners=None):
    output = evaluation(row, arm, bundle, chunks, count)
    output["top15_complete"] = (
        evidence_metrics(output["candidate_ids"], row["resolved_gold"], 15)["complete_evidence_hit"]
        if row["answerable"]
        else None
    )
    document_complete = None
    if trace is not None and row["answerable"]:
        allowed = [cid for cid, owner in owners.items() if owner in trace["documents"]]
        document_complete = bool(
            evidence_metrics(allowed, row["resolved_gold"], max(1, len(allowed)))[
                "complete_evidence_hit"
            ]
        )
    output.update(
        navigation=trace,
        document_complete=document_complete,
        loss_stage=loss_stage(output, document_complete if arm == "H" else None),
    )
    return output


def build(engine, navigator, arm, base, query, cached):
    started = perf_counter()
    if not cached and arm != "H":
        recall = engine.recall(query, "base", 30, cached=False)
        fused = rank_fusion([v["ranking"] for v in recall["channels"].values()])
        base = {"scoring_query": query, "hits": [{"chunk_id": cid, "score": s} for cid, s in fused]}
    hierarchy, deeper, trace = [], [], None
    if arm in {"H", "M"}:
        hierarchy, trace = navigator.retrieve(query)
    elif arm == "D":
        recall = engine.recall(query, "base", 60, cached=cached)
        deeper = rank_fusion([v["ranking"] for v in recall["channels"].values()])
        trace = {"deeper_recall": recall}
    pool = candidate_pool(arm, base["hits"], hierarchy, deeper)
    # H must not execute an unused baseline retrieval in timed runs.
    before = engine.new_pairs
    bundle = engine.score(pool, query, [], cached=cached)
    if engine.new_pairs - before > 90:
        raise ValueError("Actual rerank pairs exceed 90")
    work = {
        "candidate_pairs": len(pool),
        "actual_new_pairs": engine.new_pairs - before,
        "pair_cap": 90,
        "retrieval_and_rerank_ms": (perf_counter() - started) * 1000,
    }
    return bundle, trace, work


def report(run, rows, latency):
    summary, stats, pending = {}, {}, []
    for dataset in ("official", "repository"):
        base = [r for r in rows if r["dataset"] == dataset and r["arm"] == "B"]
        for arm in ARMS:
            selected = [r for r in rows if r["dataset"] == dataset and r["arm"] == arm]
            positive = [r for r in selected if r["answerable"]]
            summary[f"{dataset}:{arm}"] = {
                name: ratio(sum(bool(r[name]) for r in positive), len(positive))
                for name in ("candidate_complete", "top5_complete", "top15_complete")
            }
            summary[f"{dataset}:{arm}"]["delivered_complete"] = ratio(
                sum(bool(r["delivered"]["complete"]) for r in positive), len(positive)
            )
            summary[f"{dataset}:{arm}"]["negative_cases"] = len(selected) - len(positive)
            summary[f"{dataset}:{arm}"]["negative_answer_quality"] = None
            if arm != "B":
                stat = paired_statistics(base, selected)
                stats[f"{dataset}:{arm}"] = stat
                for cid in stat["lost_ids"] + stat["recovered_ids"]:
                    pending.append(
                        {
                            "dataset": dataset,
                            "arm": arm,
                            "id": cid,
                            "status": "pending",
                            "reason": None,
                        }
                    )
    adjusted = holm({k: v["cluster_permutation_p"] for k, v in stats.items()})
    for key in stats:
        stats[key]["holm_p"] = adjusted[key]
    timing = (
        {
            arm: latency_summary([r["latency_ms"] for r in latency if r["arm"] == arm])
            for arm in ARMS
        }
        if len(latency) == 440
        else None
    )
    gains = sum(stats[f"{ds}:M"]["delta_count"] for ds in ("official", "repository"))
    quality = gains >= 2 and all(
        summary[f"{ds}:M"][metric]["numerator"] >= summary[f"{ds}:B"][metric]["numerator"]
        for ds in ("official", "repository")
        for metric in ("candidate_complete", "delivered_complete")
    )
    for dataset in ("official", "repository"):
        base_rows = {r["id"]: r for r in rows if r["dataset"] == dataset and r["arm"] == "B"}
        for arm in ARMS:
            selected = [
                r for r in rows if r["dataset"] == dataset and r["arm"] == arm and r["answerable"]
            ]
            item = summary[f"{dataset}:{arm}"]
            item["candidate_coverage"] = ratio(
                sum(r["candidate_coverage"] for r in selected), len(selected)
            )
            if arm in {"H", "M"}:
                item["document_complete"] = ratio(
                    sum(r["document_complete"] for r in selected), len(selected)
                )
            item["loss_stages"] = {
                stage: sum(r["loss_stage"] == stage for r in selected)
                for stage in ("document_filter", "body_recall", "rerank", "delivery", "complete")
            }
            for row in selected:
                before = base_rows[row["id"]]
                metrics = ("candidate_complete", "top5_complete", "top15_complete")
                if arm != "B" and any(row[m] != before[m] for m in metrics):
                    pending.append(
                        {
                            "dataset": dataset,
                            "arm": arm,
                            "id": row["id"],
                            "status": "pending",
                            "reason": "stage_metric_change",
                        }
                    )
    result = {
        "results": summary,
        "paired_delivery": stats,
        "warm_latency": timing,
        "quality_outputs": len(rows),
        "latency_outputs": len(latency),
        "latency_complete": len(latency) == 440,
        "development_quality_gate": quality,
        "independent_review": "pending",
        "adopted": False,
        "generation_calls": 0,
        "latency_gate": (timing["M"]["p95_ms"] <= 1.5 * timing["B"]["p95_ms"] if timing else None),
    }
    write_json(run / "summary.json", result)
    write_json(run / "review-template.json", pending)
    lines = [
        "# 元数据检索开发集实验",
        "",
        "仅检索与证据交付；独立审核pending，不采用配置。",
        "",
        "|数据集/组|候选完整|Top5|Top15|正文完整|",
        "|---|---|---|---|---|",
    ]
    for key, value in summary.items():
        cells = [
            f"{value[m]['numerator']}/{value[m]['denominator']}"
            for m in ("candidate_complete", "top5_complete", "top15_complete", "delivered_complete")
        ]
        lines.append("|" + "|".join([key, *cells]) + "|")
    lines += [
        "",
        "逐题阶段归因及原文见rows.jsonl；胜负变化人工审核见review-template.json。",
        f"质量输出{len(rows)}/440；延迟输出{len(latency)}/440；不完整延迟不作总体结论。",
        "开发集筛选不是独立确认；未生成答案，不能报告回答正确率。",
    ]
    (run / "report.md").write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=("quality", "latency", "all"), default="quality")
    args = parser.parse_args()
    run = args.output.resolve()
    run.mkdir(parents=True, exist_ok=True)
    try:
        protocol, mapping, bundles, _, chunks, count = prepare(run / "frozen-inputs")
        extra = {
            str(p.relative_to(ROOT)): digest(p)
            for p in (Path(__file__).resolve(), ROOT / "src/infra_rag/metadata_experiments.py")
        }
        freeze(
            run,
            "protocol.json",
            {
                "version": VERSION,
                "arms": ARMS,
                "base_protocol": protocol,
                "implementation": extra,
                "document_top_k": 5,
                "metadata_channel_k": 30,
                "body_channel_k": 30,
                "generation_calls": 0,
                "independent_review": "pending",
                "h_diagnostic_only": True,
                "holdout_read": False,
            },
        )
        for relative in extra:
            dest = run / "implementation" / relative
            if dest.exists() and digest(dest) != extra[relative]:
                raise ValueError("Implementation snapshot changed")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((ROOT / relative).read_bytes())
        baseline_gate(mapping, bundles, chunks, count)
        print("baseline gate passed: 110 frozen cases", flush=True)
        engine = Engine(run, protocol, chunks)
        engine.models()
        engine.encoder.batch_size = None
        service = engine.service("base")
        started = perf_counter()
        body = [c for c in service.chunks if c.domain == "infra" and c.modality == "text"]
        vectors = {c.id: v for c, v in zip(service.chunks, service.vectors, strict=True)}
        navigator = MetadataNavigator(body, [vectors[c.id] for c in body], engine.encoder, ROOT)
        freeze(run, "metadata-index.json", navigator.records)
        freeze(
            run,
            "index-build.json",
            {
                "documents": len(navigator.views),
                "index_identity": canonical_hash(navigator.records),
                "vector_sha256": canonical_hash(navigator.meta_vectors),
            },
        )
        write_json(
            run / "index-build-measurement.json",
            {
                "elapsed_ms": (perf_counter() - started) * 1000,
                "vector_values": sum(map(len, navigator.meta_vectors)),
                "metadata_bytes": len(json.dumps(navigator.records).encode()),
                "field_coverage": {
                    field: ratio(
                        sum(bool(r["fields"].get(field)) for r in navigator.records.values()),
                        len(navigator.records),
                    )
                    for field in ("title", "path", "headings", "product", "release")
                },
            },
        )
        done = {(r["dataset"], r["id"], r["arm"]) for r in read_rows(run / "rows.jsonl")}
        for key, row in mapping.items():
            for arm in ARMS:
                if (*key, arm) in done:
                    continue
                if args.phase == "latency":
                    raise ValueError("Run quality phase before latency")
                base = bundles[key]["B5"]
                bundle, trace, work = build(
                    engine, navigator, arm, base, base["scoring_query"], True
                )
                output = measure(
                    row,
                    arm,
                    bundle,
                    chunks,
                    count,
                    trace if arm in {"H", "M"} else None,
                    navigator.owners,
                )
                output.update(work=work, recall_trace=trace)
                if arm == "B":
                    expected = baseline_gate({key: row}, bundles, chunks, count)[key]
                    if output["context"] != expected["context"]:
                        raise ValueError(f"Scored baseline differs: {key}")
                append(run, output)
            print(f"quality {key}", flush=True)
        write_json(run / "rerank-scores.json", engine.scores)
        latency = read_rows(run / "latency.jsonl")
        if args.phase in {"all", "latency"}:
            # Warm all retrieval/model paths; no query/rerank result cache is used below.
            first = next(iter(bundles.values()))["B5"]
            for arm in ARMS:
                build(engine, navigator, arm, first, first["scoring_query"], False)
            completed = {(r["dataset"], r["id"], r["arm"]) for r in latency}
            for i, (key, row) in enumerate(mapping.items()):
                for arm in ARMS[i % 4 :] + ARMS[: i % 4]:
                    if (*key, arm) in completed:
                        continue
                    started = perf_counter()
                    base = bundles[key]["B5"]
                    bundle, trace, work = build(
                        engine, navigator, arm, base, base["scoring_query"], False
                    )
                    output = measure(
                        row,
                        arm,
                        bundle,
                        chunks,
                        count,
                        trace if arm in {"H", "M"} else None,
                        navigator.owners,
                    )
                    elapsed = (perf_counter() - started) * 1000
                    if arm == "B":
                        frozen_ids = {h["chunk_id"] for h in base["hits"]}
                        if set(output["candidate_ids"]) != frozen_ids:
                            write_json(
                                run / "baseline-mismatch.json",
                                {
                                    "dataset": key[0],
                                    "id": key[1],
                                    "frozen": base,
                                    "live": output,
                                    "work": work,
                                },
                            )
                            raise ValueError(f"Live baseline candidate mismatch: {key}")
                        if (
                            output["context"]
                            != baseline_gate({key: row}, bundles, chunks, count)[key]["context"]
                        ):
                            raise ValueError(f"Live baseline delivery mismatch: {key}")
                    result = {
                        "dataset": key[0],
                        "id": key[1],
                        "arm": arm,
                        "latency_ms": elapsed,
                        "work": work,
                        "output": output,
                    }
                    with (run / "latency.jsonl").open("a") as stream:
                        stream.write(json.dumps(result, ensure_ascii=False) + "\n")
                    latency.append(result)
                print(f"latency {key}", flush=True)
        rows = read_rows(run / "rows.jsonl")
        if len(rows) != 440:
            raise ValueError("Expected 440 quality outputs")
        if latency and len(latency) != 440:
            raise ValueError("Incomplete latency outputs")
        report(run, rows, latency)
        write_json(
            run / "artifacts-manifest.json",
            {
                str(p.relative_to(run)): digest(p)
                for p in sorted(run.rglob("*"))
                if p.is_file() and p.name != "artifacts-manifest.json"
            },
        )
        record_operation(
            "元数据B/D/H/M开发集实验",
            "验证文档导航与证据损失",
            f"产物：{run}；440质量输出；延迟输出{len(latency)}；独立审核pending",
        )
    except Exception as exc:
        write_json(run / "aborted.json", {"error": str(exc), "completed": False})
        quality = read_rows(run / "rows.jsonl")
        if len(quality) == 440:
            report(run, quality, read_rows(run / "latency.jsonl"))
        write_json(
            run / "incomplete-artifacts-manifest.json",
            {
                str(p.relative_to(run)): digest(p)
                for p in sorted(run.rglob("*"))
                if p.is_file()
                and p.name not in {"artifacts-manifest.json", "incomplete-artifacts-manifest.json"}
            },
        )
        record_operation(
            "元数据对照实验中止", "保留实际失败，不伪造完成", f"产物保留于{run}", str(exc)
        )
        raise


if __name__ == "__main__":
    main()
