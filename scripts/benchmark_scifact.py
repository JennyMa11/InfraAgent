"""BEIR SciFact native-document evaluation; freeze configurations before opening test queries."""

import argparse
import hashlib
import io
import json
import platform
import statistics
import urllib.request
import zipfile
from pathlib import Path
from time import perf_counter

from benchmark_official import implementation_hash, snapshot, verify_snapshot
from operation_log import ROOT, record_operation

from infra_rag.benchmarking import (
    VARIANTS,
    create_run,
    digest,
    graded_metrics,
    load_json,
    write_new,
)
from infra_rag.encoding import BGEEncoder, dot
from infra_rag.lexical import BM25Index
from infra_rag.models import Chunk
from infra_rag.offline_evaluation import latency_summary
from infra_rag.service import fuse, lexical_statistics

DATA = ROOT / "data/public-evals/scifact"
META = ROOT / "evals/public-benchmarks/scifact"
URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip"
MD5 = "5f7d1de60b170fc8027bb7898e2efca1"


def prepare():
    DATA.mkdir(parents=True, exist_ok=True)
    path = DATA / "scifact.zip"
    if not path.exists():
        with urllib.request.urlopen(URL, timeout=90) as response:
            raw = response.read()
        if hashlib.md5(raw, usedforsecurity=False).hexdigest() != MD5:
            raise ValueError("SciFact does not match published BEIR checksum")
        with path.open("xb") as stream:
            stream.write(raw)
    raw = path.read_bytes()
    if hashlib.md5(raw, usedforsecurity=False).hexdigest() != MD5:
        raise ValueError("SciFact archive changed")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        # Extract only official evaluation files; reject archive traversal implicitly.
        for name in ("corpus.jsonl", "queries.jsonl", "qrels/train.tsv", "qrels/test.tsv"):
            target = DATA / name
            payload = archive.read("scifact/" + name)
            if target.exists():
                if target.read_bytes() != payload:
                    raise ValueError("native SciFact file changed")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as stream:
                    stream.write(payload)
    manifest = {
        "source": URL,
        "md5": MD5,
        "sha256": digest(path),
        "files": {
            name: digest(DATA / name)
            for name in ("corpus.jsonl", "queries.jsonl", "qrels/train.tsv", "qrels/test.tsv")
        },
        "retrieval_unit": "native document, title + newline + text, no chunking",
        "split": "official test; no tuning on test",
        "qrels": "original graded judgments",
    }
    if (META / "source-manifest.json").exists():
        if load_json(META / "source-manifest.json") != manifest:
            raise ValueError("source manifest changed")
    else:
        write_new(META / "source-manifest.json", manifest)
    print("Verified SciFact archive and native documents")


def freeze(args):
    source = load_json(META / "source-manifest.json")
    for name, expected in source["files"].items():
        if digest(DATA / name) != expected:
            raise ValueError("SciFact input changed")
    directory = create_run(args.output, {"kind": "scifact protocol"})
    write_new(
        directory / "protocol.json",
        {
            "source_manifest_sha256": digest(META / "source-manifest.json"),
            "implementation_sha256": implementation_hash(),
            "runner_sha256": digest(Path(__file__)),
            "variants": list(VARIANTS),
            "embedding": snapshot("BAAI/bge-small-zh-v1.5"),
            "reranker": snapshot("BAAI/bge-reranker-base"),
            "candidate_k": 30,
            "rrf_constant": 60,
            "top_k": [5, 10],
            "language": "original English; current Chinese BGE configuration, no model selection",
            "platform": platform.platform(),
            "ndcg_gain": "linear relevance, matching BEIR/trec_eval convention",
        },
    )
    print(directory / "protocol.json")


def run(args):
    protocol = load_json(args.protocol)
    source = load_json(META / "source-manifest.json")
    if (
        digest(META / "source-manifest.json") != protocol["source_manifest_sha256"]
        or digest(Path(__file__)) != protocol["runner_sha256"]
        or implementation_hash() != protocol["implementation_sha256"]
    ):
        raise ValueError("frozen protocol inputs changed")
    for name, expected in source["files"].items():
        if digest(DATA / name) != expected:
            raise ValueError("SciFact input changed")
    for name in ("embedding", "reranker"):
        verify_snapshot(protocol[name])
    output = create_run(
        args.output,
        {
            "protocol_sha256": digest(args.protocol),
            "dataset": "BEIR SciFact",
            "split": "official test",
        },
    )
    write_new(args.protocol.parent / "test-started.json", {"output": str(output.resolve())})
    docs = [json.loads(line) for line in (DATA / "corpus.jsonl").read_text().splitlines()]
    chunks = [
        Chunk(d["_id"], d["_id"], d["_id"], d["title"] + "\n" + d["text"], "science") for d in docs
    ]
    if len({c.id for c in chunks}) != len(chunks):
        raise ValueError("duplicate native IDs")
    queries = {
        q["_id"]: q["text"]
        for q in (json.loads(line) for line in (DATA / "queries.jsonl").read_text().splitlines())
    }
    qrels = {}
    for line in (DATA / "qrels/test.tsv").read_text().splitlines()[1:]:
        query, doc, relevance = line.split("\t")
        if doc not in {c.id for c in chunks} or query not in queries:
            raise ValueError("qrels contain unknown native IDs")
        qrels.setdefault(query, {})[doc] = float(relevance)
    started = perf_counter()
    encoder = BGEEncoder(protocol["embedding"]["path"])
    index = BM25Index(chunks, statistics=lexical_statistics(chunks))
    from sentence_transformers import CrossEncoder

    reranker = CrossEncoder(protocol["reranker"]["path"])
    vectors = encoder.encode([c.content for c in chunks])
    encoder.encode(["scientific evidence"], query=True)
    reranker.predict([("scientific evidence", "study")])
    preparation_ms = (perf_counter() - started) * 1000
    by_id = {c.id: c for c in chunks}
    rows = []
    with (output / "rows.jsonl").open("x", encoding="utf-8") as stream:
        for qid, gold in qrels.items():
            query = queries[qid]
            started = perf_counter()
            lexical = index.search(query, top_k=protocol["candidate_k"])
            lexical_ms = (perf_counter() - started) * 1000
            started = perf_counter()
            vector = encoder.encode([query], query=True)[0]
            dense = sorted(
                ((c.id, dot(v, vector)) for c, v in zip(chunks, vectors, strict=True)),
                key=lambda pair: (-pair[1], pair[0]),
            )[: protocol["candidate_k"]]
            dense_ms = (perf_counter() - started) * 1000
            started = perf_counter()
            fused, _ = fuse({"bm25": lexical, "dense": dense}, protocol["rrf_constant"])
            fused = fused[: protocol["candidate_k"]]
            fusion_ms = (perf_counter() - started) * 1000
            started = perf_counter()
            scores = reranker.predict([(query, by_id[doc].content) for doc, _ in fused]).tolist()
            reranked = sorted(
                zip([doc for doc, _ in fused], scores, strict=True),
                key=lambda pair: (-pair[1], pair[0]),
            )
            rerank_ms = (perf_counter() - started) * 1000
            variants = {
                "bm25": (lexical, lexical_ms),
                "dense": (dense, dense_ms),
                "hybrid": (fused, lexical_ms + dense_ms + fusion_ms),
                "hybrid_rerank": (reranked, lexical_ms + dense_ms + fusion_ms + rerank_ms),
            }
            for name, (ranking, elapsed) in variants.items():
                row = {
                    "id": qid,
                    "query": query,
                    "variant": name,
                    "ranking": ranking,
                    "qrels": gold,
                    "latency_ms": elapsed,
                    "at_k": {
                        str(k): graded_metrics([doc for doc, _ in ranking], gold, k)
                        for k in (5, 10)
                    },
                }
                rows.append(row)
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            stream.flush()
            print(qid, flush=True)
    summaries = {}
    for name in VARIANTS:
        selected = [row for row in rows if row["variant"] == name]
        summaries[name] = {
            "at_k": {
                str(k): {
                    metric: statistics.mean(row["at_k"][str(k)][metric] for row in selected)
                    for metric in ("recall", "precision", "mrr", "ndcg")
                }
                for k in (5, 10)
            },
            "latency": latency_summary([r["latency_ms"] for r in selected]),
        }
    write_new(
        output / "summary.json",
        {
            "documents": len(chunks),
            "queries": len(qrels),
            "preparation_ms": preparation_ms,
            "latency_scope": "sequential component warm timings; hybrid is sum of timed components",
            "summaries": summaries,
            "limitations": "English native-document retrieval only; "
            "not AI Infra QA accuracy or a leaderboard reproduction",
        },
    )
    record_operation(
        "SciFact原生文档检索对照",
        "补充独立标准检索协议",
        f"{len(chunks)}文档，{len(qrels)}查询，四种配置，{output}",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("prepare")
    locked = commands.add_parser("freeze")
    locked.add_argument("--output", type=Path, required=True)
    evaluate = commands.add_parser("run")
    evaluate.add_argument("--protocol", type=Path, required=True)
    evaluate.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    elif args.command == "freeze":
        freeze(args)
    else:
        run(args)


if __name__ == "__main__":
    main()
