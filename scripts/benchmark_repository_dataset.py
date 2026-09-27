"""Validate provenance and run fixed-corpus retrieval baselines, without tuning on test."""

import argparse
import hashlib
import importlib.metadata
import json
import platform
from collections import defaultdict
from dataclasses import replace
from datetime import UTC, datetime
from statistics import mean

from index_repository_corpus import DATASET, ROOT, build_index

from infra_rag.evaluation import evaluate, metrics, resolve_spans


def write_run_manifest(results, rerank):
    files = sorted((ROOT / "src" / "infra_rag").glob("*.py")) + sorted(
        (ROOT / "scripts").glob("*repository*.py")
    )
    manifest = {
        "created_at": datetime.now(UTC).isoformat(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "packages": {
            name: importlib.metadata.version(name)
            for name in ["torch", "sentence-transformers", "chromadb", "jieba"]
        },
        "implementation_sha256": hashlib.sha256(
            b"".join(str(f.relative_to(ROOT)).encode() + f.read_bytes() for f in files)
        ).hexdigest(),
        "rerank": rerank,
        "protocol": "default parameters, no test-based tuning, warm top-10 queries",
    }
    (results / "run-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))


def validate():
    manifest = json.loads((DATASET / "corpus-manifest.json").read_text())
    record = json.loads((DATASET / "dataset-manifest.json").read_text())
    documents = {d["id"]: d for d in manifest["documents"]}
    texts = {}
    for document in documents.values():
        file = ROOT / manifest["corpus_root"] / document["source"]
        assert hashlib.sha256(file.read_bytes()).hexdigest() == document["sha256"]
        texts[document["id"]] = file.read_text()
    splits = {}
    for split in ["dev", "test"]:
        file = DATASET / f"{split}.json"
        assert hashlib.sha256(file.read_bytes()).hexdigest() == record["splits"][split]["sha256"]
        splits[split] = json.loads(file.read_text())
        for question in splits[split]:
            assert question["query"].strip() and question["expected_answer"].strip()
            for span in question["relevant_spans"]:
                doc = documents[span["document_id"]]
                assert span["sha256"] == doc["sha256"] and span["commit"] == doc["commit"]
                assert (DATASET / span["source"]).resolve() == (
                    ROOT / manifest["corpus_root"] / doc["source"]
                ).resolve()
                text = texts[doc["id"]]
                lines = text.splitlines()[span["line_start"] - 1 : span["line_end"]]
                assert span["text"] in "\n".join(lines)
                assert question["query"] not in text
    assert not ({q["group_id"] for q in splits["dev"]} & {q["group_id"] for q in splits["test"]})
    assert len({q["id"] for items in splits.values() for q in items}) == record["questions"]
    print(
        "Validated source hashes, evidence lines, unique IDs and disjoint concept groups",
        flush=True,
    )
    return splits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--rerank", action="store_true")
    args = parser.parse_args()
    splits = validate()
    service = build_index()
    results = DATASET / "results"
    results.mkdir(exist_ok=True)
    resolved = {}
    for split, questions in splits.items():
        resolved[split] = resolve_spans(service, questions, DATASET)
        (results / f"{split}-labels.json").write_text(
            json.dumps(resolved[split], ensure_ascii=False, indent=2)
        )
    if args.validate_only:
        print("All 150 questions resolve to actual indexed evidence chunks", flush=True)
        return
    summaries = []
    for name in ["bm25", "dense", "hybrid"] + (["hybrid_rerank"] if args.rerank else []):
        strategy = name.replace("_rerank", "")
        service.settings = replace(service.settings, rerank=name.endswith("_rerank"))
        service.search(
            "KV Cache 分页", top_k=10, domain="infra", modality="text", strategy=strategy
        )
        for split, questions in resolved.items():
            report = evaluate(service, questions, k=10, strategy=strategy, label="chunk")
            report["at_k"] = {}
            for k in [1, 3, 5, 10]:
                rows = [metrics(row["retrieved"], row["relevant"], k) for row in report["rows"]]
                report["at_k"][str(k)] = {key: mean(row[key] for row in rows) for key in rows[0]}
            report["evidence_hit_at_5"] = mean(
                bool(set(row["retrieved"][:5]) & set(row["relevant"])) for row in report["rows"]
            )
            by_type = defaultdict(list)
            for question, row in zip(questions, report["rows"], strict=True):
                by_type[question["question_type"]].append(
                    metrics(row["retrieved"], row["relevant"], 5)
                )
            report["by_question_type_at_5"] = {
                kind: {key: mean(r[key] for r in rows) for key in rows[0]}
                for kind, rows in by_type.items()
            }
            report["corpus_sha256"] = json.loads((DATASET / "corpus-manifest.json").read_text())[
                "corpus_sha256"
            ]
            report["dataset_sha256"] = hashlib.sha256(
                (DATASET / f"{split}.json").read_bytes()
            ).hexdigest()
            report["latency_scope"] = "warm process, top-10 query, including optional reranker"
            report["qrels_scope"] = (
                "sparse authored source evidence; other relevant chunks may be unlabeled"
            )
            (results / f"{split}-{name}.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2)
            )
            row = report["at_k"]["5"]
            summaries.append((split, name, report, row))
            print(split, name, row, flush=True)
    lines = [
        "# 三仓库真实语料检索基线",
        "",
        "87篇正文，11,168个分块；AI构建150题，dev50/test100；固定默认配置，未根据test调参。",
        "标签是原文证据分块的稀疏标注，未穷尽同主题的其他正确文档；不等于问答准确率。",
        "命中率指至少找到一个标注证据块。Recall分母是全部标注证据块，二者不同。",
        "",
        "| 划分 | 方法 | Recall@5 | Precision@5 | F1@5 | MRR@5 | 证据命中率@5 | P50 ms |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for split, name, report, row in summaries:
        lines.append(
            f"| {split} | {name} | {row['recall']:.3f} | {row['precision']:.3f} | "
            f"{row['f1']:.3f} | {row['mrr']:.3f} | {report['evidence_hit_at_5']:.3f} | "
            f"{report['latency_p50_ms']:.1f} |"
        )
    (results / "comparison.md").write_text("\n".join(lines) + "\n")
    write_run_manifest(results, args.rerank)


if __name__ == "__main__":
    main()
