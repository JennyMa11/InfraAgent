"""TechQA context-pool pilot and C-Eval evidence-mapping candidates, not official scores."""

import json
import re
import statistics
import time

from benchmark_public_retrieval import document_metrics, write
from index_repository_corpus import index_settings
from operation_log import ROOT, record_operation

from infra_rag.lexical import BM25Index
from infra_rag.models import Chunk
from infra_rag.service import RetrievalService, lexical_statistics

BASE = ROOT / "evals/public-benchmarks"
DATA = ROOT / "data/public-evals/prepared/ragbench-techqa"


def load_lines(path):
    return [json.loads(line) for line in path.open()]


def techqa():
    corpus = {}
    for split in ["validation", "test"]:
        corpus.update({doc["id"]: doc for doc in load_lines(DATA / f"{split}-contexts.jsonl")})
    chunks = [Chunk(k, k, k, doc["content"], "infra") for k, doc in corpus.items()]
    index = BM25Index(chunks, statistics=lexical_statistics(chunks))
    summary = {}
    for split in ["validation", "test"]:
        records = load_lines(DATA / f"{split}-records.jsonl")
        by_question = {}
        for record in records:
            by_question.setdefault(record["question_id"], []).append(record)
        queries = json.loads((BASE / f"ragbench-techqa/{split}-queries.json").read_text())
        rows, excluded = [], []
        for q in queries:
            annotations = by_question[q["id"]]
            if any(r["sentence_label_status"] != "resolved" for r in annotations):
                excluded.append({"id": q["id"], "reason": "invalid upstream sentence IDs"})
                continue
            gold_sets = []
            for record in annotations:
                gold_sets.append(
                    {
                        record["context_doc_ids"][int(re.match(r"\d+", key)[0])]
                        for key in record["all_relevant_sentence_keys"]
                    }
                )
            if not gold_sets[0] or any(gold != gold_sets[0] for gold in gold_sets):
                excluded.append({"id": q["id"], "reason": "empty or disagreeing model labels"})
                continue
            start = time.perf_counter()
            ranked = index.search(q["query"], top_k=10)
            rows.append(
                {
                    "id": q["id"],
                    "query": q["query"],
                    "gold": sorted(gold_sets[0]),
                    "retrieved": [doc for doc, _ in ranked],
                    "latency_ms": (time.perf_counter() - start) * 1000,
                    "at_k": {
                        str(k): document_metrics([doc for doc, _ in ranked], gold_sets[0], k)
                        for k in [5, 10]
                    },
                }
            )
        result = {
            "protocol": "pooled provided contexts; positive document if any labeled sentence; "
            "both model records must agree; not official TechQA retrieval",
            "label_source": "upstream model annotations, not independently human validated",
            "split": split,
            "input_questions": len(queries),
            "evaluated_questions": len(rows),
            "excluded_questions": len(excluded),
            "context_pool_documents": len(chunks),
            "at_k": {
                str(k): {
                    metric: statistics.mean(r["at_k"][str(k)][metric] for r in rows)
                    for metric in ["recall", "hit", "mrr", "ndcg"]
                }
                for k in [5, 10]
            },
            "latency_p50_ms": statistics.median(r["latency_ms"] for r in rows),
        }
        write(
            BASE / f"ragbench-techqa/results/{split}-context-pilot.json",
            {**result, "rows": rows, "excluded": excluded},
        )
        summary[split] = result
        print(json.dumps(result, ensure_ascii=False), flush=True)
    record_operation(
        "TechQA所给上下文池BM25试验",
        "测量外部技术支持场景并过滤异常/冲突标签",
        json.dumps(summary, ensure_ascii=False),
        "这是模型注释的上下文池试验，不是完整语料或官方TechQA成绩",
    )


def ceval():
    service = RetrievalService(index_settings())
    queries = json.loads((BASE / "ceval-computing/val-queries.json").read_text())
    rows = []
    for q in queries:
        # Never include the answer label or answer text in the search request.
        query = q["query"] + "\n" + "\n".join(q["choices"].values())
        hits = service.search(query, strategy="bm25", top_k=5, domain="infra", modality="text")
        rows.append(
            {
                **q,
                "search_query": query,
                "coverage_decision": "pending_review",
                "candidates": [
                    {
                        "chunk_id": hit.chunk.id,
                        "source": hit.chunk.source,
                        "heading": hit.chunk.heading,
                        "content": hit.chunk.content,
                        "locator": hit.chunk.locator,
                    }
                    for hit in hits
                ],
            }
        )
    write(BASE / "ceval-computing/evidence-review-candidates.json", rows)
    record_operation(
        "为C-Eval59题生成中文Infra语料Top5证据复核候选",
        "推进公开中文选择题与冻结知识库的证据映射",
        "59题检索完成；未向查询加入答案标签；全部仍待证据/覆盖性复核",
        "无检索金标，不能把候选数、相似度或答题正确率当作检索召回",
    )


if __name__ == "__main__":
    try:
        techqa()
        ceval()
    except Exception as error:
        record_operation("外部辅助试验", "测试TechQA并生成C-Eval证据候选", "失败", repr(error))
        raise
