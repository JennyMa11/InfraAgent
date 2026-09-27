"""Fixed v2 annotations, dev-only comparisons; test queries never run here."""

import hashlib
import json
import statistics
import time
from dataclasses import replace

from benchmark_repository_dataset import write_run_manifest
from index_repository_corpus import DATASET, build_index, index_settings
from operation_log import record_operation

from infra_rag.evaluation import evidence_metrics, metrics, resolve_alternatives


def main():
    annotation_dir = DATASET / "annotations-v2"
    file = annotation_dir / "dev.json"
    dataset = json.loads(file.read_text())
    annotation_manifest = json.loads((annotation_dir / "manifest.json").read_text())
    assert (
        hashlib.sha256(file.read_bytes()).hexdigest()
        == annotation_manifest["splits"]["dev"]["sha256"]
    )
    assert len(dataset) == 50
    output = DATASET / "results" / "dev-v2"
    output.mkdir(exist_ok=True)
    encoder, reranker = None, None
    summaries = []
    for heading_context in [False, True]:
        settings = index_settings()
        if heading_context:
            settings = replace(
                settings,
                heading_context=True,
                data_dir=settings.data_dir.with_name(settings.data_dir.name + "-headings-v1"),
            )
        service = build_index(
            settings=settings,
            record_name="heading-index-record.json" if heading_context else "index-record.json",
        )
        if encoder is not None:
            service.encoder = encoder
        if reranker is not None:
            service.reranker = reranker
        resolved = resolve_alternatives(service, dataset, annotation_dir)
        tag = "headings" if heading_context else "original"
        (output / f"{tag}-labels.json").write_text(
            json.dumps(resolved, ensure_ascii=False, indent=2)
        )
        for strategy, policy in [("bm25", "truncate"), ("hybrid", "truncate"), ("hybrid", "union")]:
            name = f"{tag}-{strategy}-rerank-{policy}"
            service.settings = replace(service.settings, rerank=True, fusion_candidates=policy)
            # Model load and lexical statistics construction are excluded from warm query latency.
            service.search(
                "KV Cache 分页", top_k=10, domain="infra", modality="text", strategy=strategy
            )
            rows = []
            for item in resolved:
                start = time.perf_counter()
                hits = service.search(
                    item["query"], top_k=10, domain="infra", modality="text", strategy=strategy
                )
                latency = (time.perf_counter() - start) * 1000
                ids = [h.chunk.id for h in hits]
                row = {
                    "id": item["id"],
                    "query": item["query"],
                    "question_type": item["question_type"],
                    "group_id": item["group_id"],
                    "retrieved": ids,
                    "relevant": item["relevant"],
                    "latency_ms": latency,
                    "at_k": {
                        str(k): {
                            **metrics(ids, item["relevant"], k),
                            **evidence_metrics(ids, item, k),
                        }
                        for k in [1, 3, 5, 10]
                    },
                }
                rows.append(row)
            latencies = sorted(r["latency_ms"] for r in rows)
            report = {
                "name": name,
                "split": "dev",
                "questions": len(rows),
                "configuration": service.status(),
                "rows": rows,
                "dataset_sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
                "corpus_sha256": annotation_manifest["corpus_sha256"],
                "protocol": "v2 evidence fixed before six dev comparisons; no test queries",
                "latency_scope": "warm top10 query, includes retrieval and reranking",
                "latency_p50_ms": statistics.median(latencies),
                "latency_p95_ms": latencies[-3],
                "at_k": {
                    str(k): {
                        metric: statistics.mean(r["at_k"][str(k)][metric] for r in rows)
                        for metric in rows[0]["at_k"][str(k)]
                    }
                    for k in [1, 3, 5, 10]
                },
            }
            report["by_question_type_at_5"] = {
                kind: {
                    metric: statistics.mean(
                        r["at_k"]["5"][metric] for r in rows if r["question_type"] == kind
                    )
                    for metric in rows[0]["at_k"]["5"]
                }
                for kind in ["knowledge", "scenario"]
            }
            (output / f"{name}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
            summary = {
                "name": name,
                **report["at_k"]["5"],
                "latency_p50_ms": report["latency_p50_ms"],
                "latency_p95_ms": report["latency_p95_ms"],
            }
            summaries.append(summary)
            print(json.dumps(summary, ensure_ascii=False), flush=True)
            record_operation(
                f"dev对照：{name}",
                "比较检索、候选并集及标题层级上下文",
                json.dumps(summary, ensure_ascii=False),
            )
        encoder, reranker = service.encoder, service.reranker
    write_run_manifest(output, rerank=True)
    (output / "summary.json").write_text(json.dumps(summaries, ensure_ascii=False, indent=2))
    best = sorted(
        summaries,
        key=lambda r: (-r["complete_evidence_hit"], -r["evidence_mrr"], r["latency_p50_ms"]),
    )[0]
    (output / "selection.json").write_text(
        json.dumps(
            {
                "selection_split": "dev",
                "rule": "complete_evidence_hit@5, evidence_mrr@5, lower latency",
                "selected": best["name"],
                "model_change": "no model replacement in this comparison",
                "limitations": (
                    "AI-reviewed sparse evidence, 50 queries/13 concept groups; "
                    "not test generalization"
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    lines = [
        "# Dev v2 检索对照",
        "",
        "同一份50题v2标注、相同BGE与reranker；未运行test查询。",
        "完整证据命中：覆盖任意一组替代证据中的全部原文片段。",
        "",
        "| 配置 | 完整证据命中@5 | 证据MRR@5 | 子块Recall@5 | 子块Precision@5 | P50 ms | P95 ms |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            f"| {row['name']} | {row['complete_evidence_hit']:.3f} | {row['evidence_mrr']:.3f} | "
            f"{row['recall']:.3f} | {row['precision']:.3f} | {row['latency_p50_ms']:.1f} | "
            f"{row['latency_p95_ms']:.1f} |"
        )
    lines += [
        "",
        f"按预定规则选择：`{best['name']}`。",
        "补标增加替代正确块，子块Recall分母发生变化，不能与v1数值直接比较。",
        "标题方案同时包含标题栈、向量/重排上下文与纯结构块清理，尚未隔离每项贡献。",
    ]
    (output / "comparison.md").write_text("\n".join(lines) + "\n")
    record_operation(
        "完成六组dev对照并按预定规则选择配置",
        "先验证非模型改动，再决定模型替换",
        f"选择{best['name']}；test未执行；原始结果保留。",
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        record_operation("执行dev v2对照", "验证等价补标和检索改动", "未完成", repr(error))
        raise
