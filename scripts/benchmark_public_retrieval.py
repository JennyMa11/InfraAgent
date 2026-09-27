"""BRIGHT native-document benchmark; preserve corpus and separate tuning from holdout."""

import argparse
import hashlib
import json
import math
import pickle
import statistics
import time

from operation_log import ROOT, record_operation

from infra_rag.models import Chunk
from infra_rag.service import bm25, lexical_statistics

BASE = ROOT / "evals/public-benchmarks/bright-stackoverflow"
RESULTS = BASE / "results"
DATA = ROOT / "data/public-evals/prepared/bright-stackoverflow"


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def document_metrics(ids, gold, k):
    found = [x in gold for x in ids[:k]]
    ideal = sum(1 / math.log2(rank + 2) for rank in range(min(k, len(gold))))
    return {
        "recall": sum(found) / len(gold),
        "hit": float(any(found)),
        "mrr": next((1 / (i + 1) for i, hit in enumerate(found) if hit), 0.0),
        "ndcg": sum(hit / math.log2(i + 2) for i, hit in enumerate(found)) / ideal,
    }


def protocol(queries):
    path = RESULTS / "protocol.json"
    if path.exists():
        value = json.loads(path.read_text())
        assert (
            value["queries_sha256"]
            == hashlib.sha256((BASE / "queries.json").read_bytes()).hexdigest()
        )
        return value
    # Connected components prevent shared source-document families crossing splits.
    parent = {q["id"]: q["id"] for q in queries}

    def find(qid):
        while parent[qid] != qid:
            qid = parent[qid]
        return qid

    owner = {}
    for query in queries:
        for doc in query["relevant_doc_ids"]:
            family = doc.rsplit("_", 2)[0]
            if family in owner:
                a, b = find(query["id"]), find(owner[family])
                parent[max(a, b)] = min(a, b)
            owner[family] = query["id"]
    groups = {q["id"]: find(q["id"]) for q in queries}
    split = {
        qid: "holdout"
        if int(hashlib.sha256(group.encode()).hexdigest()[:8], 16) % 3 == 0
        else "dev"
        for qid, group in groups.items()
    }
    value = {
        "queries_sha256": hashlib.sha256((BASE / "queries.json").read_bytes()).hexdigest(),
        "corpus_sha256": hashlib.sha256((DATA / "documents.jsonl").read_bytes()).hexdigest(),
        "grouping": "connected components of shared document families, before retrieval",
        "groups": groups,
        "split_by_id": split,
        "scope": "full 107081 native short documents, original English queries",
        "selection": "dev nDCG@10, then MRR@10, then lower warm latency",
        "split_note": "local split; not an official BRIGHT split",
    }
    write(path, value)
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["dev", "holdout"], default="dev")
    parser.add_argument("--ranker", choices=["scan", "inverted", "technical"], default="scan")
    parser.add_argument("--candidates", type=int, nargs="*", default=[30])
    args = parser.parse_args()
    queries = json.loads((BASE / "queries.json").read_text())
    plan = protocol(queries)
    queries = [q for q in queries if plan["split_by_id"][q["id"]] == args.split]
    print(
        "Queries",
        len(queries),
        "Infra",
        sum(bool(q["infra_selection_reason"]) for q in queries),
        flush=True,
    )
    docs = [json.loads(line) for line in (DATA / "documents.jsonl").open()]
    chunks = [Chunk(d["id"], d["id"], d["id"], d["content"], "infra") for d in docs]
    by_id = {c.id: c for c in chunks}
    cache = DATA / f"lexical-{plan['corpus_sha256'][:12]}.pickle"
    start = time.perf_counter()
    if cache.exists():
        with cache.open("rb") as stream:
            stats = pickle.load(stream)
    else:
        stats = lexical_statistics(chunks)
        with cache.open("wb") as stream:
            pickle.dump(stats, stream)
    print("Lexical statistics ready", round(time.perf_counter() - start, 1), flush=True)
    inverted = None
    if args.ranker != "scan":
        from infra_rag.lexical import BM25Index

        inverted = BM25Index(
            chunks,
            statistics=stats,
            query_mode="technical" if args.ranker == "technical" else "raw",
        )
    ranking_path = RESULTS / f"{args.split}-{args.ranker}-candidates.json"
    if ranking_path.exists():
        rankings = json.loads(ranking_path.read_text())
        assert set(rankings) == {q["id"] for q in queries}
    else:
        rankings = {}
        for i, q in enumerate(queries, 1):
            start = time.perf_counter()
            # Keep enough results to apply per-query exclusions before the top100 cutoff.
            ranking = (
                inverted.search(q["query"], top_k=100 + len(q["excluded_ids"]))
                if inverted
                else bm25(q["query"], chunks, stats)
            )
            excluded = set(q["excluded_ids"])
            ranking = [(doc, score) for doc, score in ranking if doc not in excluded][:100]
            rankings[q["id"]] = {
                "ranking": ranking,
                "latency_ms": (time.perf_counter() - start) * 1000,
            }
            if i % 10 == 0:
                print("Retrieved", i, "/", len(queries), flush=True)
        write(ranking_path, rankings)
    variants = {"bm25": {q["id"]: rankings[q["id"]] for q in queries}}
    if args.candidates:
        from sentence_transformers import CrossEncoder

        model = CrossEncoder("BAAI/bge-reranker-base")
        model.predict([("warmup", "warmup")])
        for count in args.candidates:
            result = {}
            for i, q in enumerate(queries, 1):
                ranking = rankings[q["id"]]["ranking"][:count]
                start = time.perf_counter()
                scores = model.predict([(q["query"], by_id[doc].content) for doc, _ in ranking])
                ordered = sorted(
                    zip(ranking, scores, strict=True),
                    key=lambda x: (-float(x[1]), -x[0][1], x[0][0]),
                )
                result[q["id"]] = {
                    "ranking": [[doc[0], float(score)] for doc, score in ordered],
                    "latency_ms": rankings[q["id"]]["latency_ms"]
                    + (time.perf_counter() - start) * 1000,
                }
                if i % 10 == 0:
                    print("Reranked", count, i, "/", len(queries), flush=True)
            variants[f"bm25-rerank-{count}"] = result
    summaries = []
    for name, result in variants.items():
        rows = []
        for q in queries:
            ids = [r[0] for r in result[q["id"]]["ranking"]]
            rows.append(
                {
                    "id": q["id"],
                    "infra": bool(q["infra_selection_reason"]),
                    "query": q["query"],
                    "retrieved": ids[:10],
                    "gold": q["relevant_doc_ids"],
                    "candidate_gold_count": len(
                        set(q["relevant_doc_ids"])
                        & set(
                            r[0]
                            for r in rankings[q["id"]]["ranking"][: int(name.rsplit("-", 1)[-1])]
                        )
                    )
                    if name != "bm25"
                    else None,
                    "latency_ms": result[q["id"]]["latency_ms"],
                    "at_k": {
                        str(k): document_metrics(ids, set(q["relevant_doc_ids"]), k)
                        for k in [5, 10]
                    },
                }
            )

        def aggregate(items):
            return {
                "questions": len(items),
                "at_k": {
                    str(k): {
                        metric: statistics.mean(r["at_k"][str(k)][metric] for r in items)
                        for metric in ["recall", "hit", "mrr", "ndcg"]
                    }
                    for k in [5, 10]
                },
                "latency_p50_ms": statistics.median(r["latency_ms"] for r in items),
            }

        summary = {
            "name": name,
            "ranker": args.ranker,
            "split": args.split,
            **aggregate(rows),
            "infra": aggregate([r for r in rows if r["infra"]]),
        }
        summaries.append(summary)
        write(RESULTS / f"{args.split}-{args.ranker}-{name}.json", {**summary, "rows": rows})
        print(json.dumps(summary, ensure_ascii=False), flush=True)
    write(RESULTS / f"{args.split}-{args.ranker}-summary.json", summaries)
    record_operation(
        f"BRIGHT {args.split}全语料评测：{args.ranker}，重排候选{args.candidates}",
        "按原生文档级金标验证外部检索与候选上限",
        json.dumps(summaries, ensure_ascii=False),
        "英文技术域，不能与中文Infra分数直接比较；AI筛选22题并非新独立数据集",
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        record_operation("公开检索评测", "运行原生文档协议实验", "失败", repr(error))
        raise
