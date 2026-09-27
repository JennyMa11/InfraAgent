"""Repeatable chunk-level ablations on authored evidence spans and fixed corpus."""

import argparse
import hashlib
import importlib.metadata
import json
import platform
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean

from infra_rag.chunking import stable_id
from infra_rag.config import Settings
from infra_rag.evaluation import evaluate, metrics, resolve_spans
from infra_rag.service import RetrievalService

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["demo", "bge"], default="demo")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--chunk-size", type=int, default=450)
    args = parser.parse_args()
    output = args.output or ROOT / "evals" / "results" / args.backend
    output.mkdir(parents=True, exist_ok=True)
    dataset_file = ROOT / "evals" / "infra-60.json"
    dataset = json.loads(dataset_file.read_text())
    settings = Settings(backend=args.backend, chunk_size=args.chunk_size)
    corpus_dir = ROOT / "evals" / "corpus"
    encoder, reranker, reports = None, None, {}
    for chunk_strategy, strategies in [
        ("window", ["hybrid"]),
        (
            "semantic",
            ["bm25", "dense", "hybrid"] + (["hybrid_rerank"] if args.backend == "bge" else []),
        ),
    ]:
        index_tag = stable_id(
            json.dumps(
                replace(settings, chunk_strategy=chunk_strategy).fingerprint(), sort_keys=True
            )
        )[:8]
        service = RetrievalService(
            replace(
                settings,
                data_dir=ROOT
                / "data"
                / f"benchmark-{args.backend}-{chunk_strategy}-{args.chunk_size}-{index_tag}",
                chunk_strategy=chunk_strategy,
            )
        )
        if encoder is not None:
            service.encoder = encoder
        service.ingest(corpus_dir, "infra")
        encoder = service.encoder
        resolved = resolve_spans(service, dataset, dataset_file.parent)
        (output / f"{chunk_strategy}-labels.json").write_text(
            json.dumps(
                {
                    "fingerprint": service.settings.fingerprint(),
                    "dataset": resolved,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        for strategy_name in strategies:
            strategy = strategy_name.replace("_rerank", "")
            service.settings = replace(service.settings, rerank=strategy_name.endswith("_rerank"))
            service.reranker = reranker
            # Warmup excludes model load from query latency; ingestion timing is separate.
            service.search("KV Cache 历史键值", top_k=10, strategy=strategy)
            reranker = service.reranker
            report = evaluate(service, resolved, k=10, strategy=strategy, label="chunk")
            report["at_k"] = {}
            for k in [1, 3, 5, 10]:
                rows = [metrics(row["retrieved"], row["relevant"], k) for row in report["rows"]]
                report["at_k"][str(k)] = {key: mean(row[key] for row in rows) for key in rows[0]}
            name = f"{chunk_strategy}-{strategy_name}"
            reports[name] = report
            (output / f"{name}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
            print(name, json.dumps(report["at_k"]["5"]), flush=True)
    corpus_hash = hashlib.sha256(
        b"".join(file.name.encode() + file.read_bytes() for file in sorted(corpus_dir.glob("*.md")))
    ).hexdigest()
    manifest = {
        "created_at": datetime.now(UTC).isoformat(),
        "backend": args.backend,
        "dataset_sha256": hashlib.sha256(dataset_file.read_bytes()).hexdigest(),
        "corpus_sha256": corpus_hash,
        "implementation_sha256": hashlib.sha256(
            b"".join(
                file.name.encode() + file.read_bytes()
                for file in sorted((ROOT / "src" / "infra_rag").glob("*.py"))
            )
        ).hexdigest(),
        "questions": len(dataset),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "packages": {
            name: importlib.metadata.version(name)
            for name in ["sentence-transformers", "chromadb", "torch", "jieba"]
        },
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    lines = [
        "# Infra 60 题子块检索消融",
        "",
        f"Backend: `{args.backend}`；AI自编学习笔记；27 个主题，60 题；不代表生产语料效果。",
        "证据短语在检索前解析为子块 ID；不同分块配置分别解析，未使用检索结果生成标签。",
        "延迟为预热后单进程测量，包含检索与可选重排，硬件和依赖见 manifest。",
        "",
        "| 配置 | Recall@5 | Precision@5 | F1@5 | MRR@5 | nDCG@5 | P50 ms | P95 ms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, report in reports.items():
        row = report["at_k"]["5"]
        lines.append(
            f"| {name} | {row['recall']:.3f} | {row['precision']:.3f} | {row['f1']:.3f} | "
            f"{row['mrr']:.3f} | {row['ndcg']:.3f} | {report['latency_p50_ms']:.1f} | "
            f"{report['latency_p95_ms']:.1f} |"
        )
    lines += [
        "",
        "完整 Top-K 指标、逐题结果、配置和证据标签见同目录 JSON。",
        "指标下降同样保留，不预设融合或重排必然提升。",
    ]
    (output / "comparison.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
