"""Export pinned public evaluations without changing the repository benchmark.

Run: uv run --with pyarrow python scripts/prepare_public_evals.py
Download manifests and Parquet snapshots must exist in data/public-evals/.
"""

import hashlib
import json
import urllib.request

import pyarrow.parquet as pq
from operation_log import ROOT, record_operation

RAW = ROOT / "data/public-evals"
OUT = ROOT / "evals/public-benchmarks"
CORPUS = RAW / "prepared"

# Manual topical selection from original question texts, independent of retrieval results.
INFRA_IDS = {
    "4": "PyTorch inference execution",
    "6": "LLM application integration",
    "8": "HTTP server configuration",
    "23": "Argo and Helm orchestration",
    "31": "FastAPI production configuration",
    "36": "SSH remote execution",
    "39": "RAG context integration",
    "40": "Concurrent HTTP requests",
    "49": "Cloud Foundry environment configuration",
    "50": "Container networking",
    "52": "Cloud authentication",
    "53": "Transformer quantization and dtype",
    "63": "Rust concurrency safety",
    "66": "Docker Swarm deployment",
    "70": "GitHub Actions workflows",
    "79": "LLM structured output",
    "81": "Python dependency installation",
    "87": "JVM memory exhaustion",
    "95": "Kafka client integration",
    "96": "Multithreaded HTTP requests",
    "110": "SFTP file operations",
    "114": "CloudFormation exports",
}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def source_files(name):
    return [entry for entry in DOWNLOADS if f"/{name}/" in entry["local_path"]]


def read(name, prefix):
    entries = [entry for entry in source_files(name) if entry["path"].startswith(prefix)]
    assert len(entries) == 1, (name, prefix)
    return pq.read_table(ROOT / entries[0]["local_path"]).to_pylist()


def export_bright():
    rows = read("bright", "examples/")
    docs = read("bright", "documents/")
    doc_ids = {doc["id"] for doc in docs}
    assert len(doc_ids) == len(docs)
    assert len({row["id"] for row in rows}) == len(rows)
    assert set(INFRA_IDS) <= {row["id"] for row in rows}
    queries, qrels = [], {}
    for row in rows:
        assert row["gold_ids"] and set(row["gold_ids"]) <= doc_ids
        qid = "bright-stackoverflow-" + row["id"]
        qrels[qid] = {doc_id: 1 for doc_id in row["gold_ids"]}
        queries.append(
            {
                "id": qid,
                "original_id": row["id"],
                "query": row["query"],
                "language": "en",
                "split": "upstream_examples_stackoverflow",
                "relevant_doc_ids": row["gold_ids"],
                "excluded_ids": [x for x in row["excluded_ids"] if x != "N/A"],
                "gold_answer": row["gold_answer"],
                "reference_reasoning": row["reasoning"],
                "annotation_method": "upstream published labels; not locally re-adjudicated",
                "infra_selection_reason": INFRA_IDS.get(row["id"]),
            }
        )
    write_json(OUT / "bright-stackoverflow/queries.json", queries)
    write_json(OUT / "bright-stackoverflow/qrels.json", qrels)
    selected = [q for q in queries if q["infra_selection_reason"]]
    write_json(OUT / "bright-stackoverflow/infra-queries.json", selected)
    write_jsonl(CORPUS / "bright-stackoverflow/documents.jsonl", docs)
    return {"queries": len(rows), "documents": len(docs), "infra_queries": len(selected)}


def export_techqa():
    summary, ids_by_split = {}, {}
    for split in ["validation", "test"]:
        rows = read("ragbench", f"techqa/{split}-")
        questions, documents, records = {}, {}, []
        for index, row in enumerate(rows):
            record_id = f"techqa-{split}-{index:04d}"
            qid = row["id"]
            doc_ids = [hashlib.sha256(doc.encode()).hexdigest() for doc in row["documents"]]
            for doc_id, content in zip(doc_ids, row["documents"], strict=True):
                documents[doc_id] = {"id": doc_id, "content": content}
            question = questions.setdefault(
                qid,
                {
                    "id": qid,
                    "query": row["question"],
                    "language": "en",
                    "split": split,
                    "record_ids": [],
                    "retrieval_gold_status": "not_imported",
                },
            )
            assert question["query"] == row["question"]
            question["record_ids"].append(record_id)
            sentence_map = {
                sentence[0]: sentence[1] for doc in row["documents_sentences"] for sentence in doc
            }
            invalid_keys = [
                key for key in row["all_relevant_sentence_keys"] if key not in sentence_map
            ]
            records.append(
                {
                    "record_id": record_id,
                    "question_id": qid,
                    "context_doc_ids": doc_ids,
                    "generated_response": row["response"],
                    "generation_model_name": row["generation_model_name"],
                    "annotating_model_name": row["annotating_model_name"],
                    "documents_sentences": row["documents_sentences"],
                    "all_relevant_sentence_keys": row["all_relevant_sentence_keys"],
                    "invalid_relevant_sentence_keys": invalid_keys,
                    "sentence_label_status": "invalid_keys" if invalid_keys else "resolved",
                    "all_utilized_sentence_keys": row["all_utilized_sentence_keys"],
                    "sentence_support_information": row["sentence_support_information"],
                    "scores": {
                        k: row[k]
                        for k in [
                            "adherence_score",
                            "relevance_score",
                            "utilization_score",
                            "completeness_score",
                        ]
                    },
                }
            )
        write_json(OUT / f"ragbench-techqa/{split}-queries.json", list(questions.values()))
        write_jsonl(CORPUS / f"ragbench-techqa/{split}-records.jsonl", records)
        write_jsonl(CORPUS / f"ragbench-techqa/{split}-contexts.jsonl", documents.values())
        ids_by_split[split] = set(questions)
        summary[split] = {
            "unique_questions": len(questions),
            "records": len(rows),
            "unique_context_documents": len(documents),
            "records_with_invalid_sentence_keys": sum(
                bool(record["invalid_relevant_sentence_keys"]) for record in records
            ),
        }
    overlap = ids_by_split["validation"] & ids_by_split["test"]
    summary["validation_test_question_id_overlap"] = sorted(overlap)
    assert not overlap, "Upstream split overlap: stop before using these as separate splits"
    return summary


def export_ceval():
    rows, counts = [], {}
    for subject in ["computer_architecture", "computer_network", "operating_system"]:
        items = read("ceval", f"{subject}/val-")
        counts[subject] = len(items)
        for item in items:
            assert item["answer"] in "ABCD"
            rows.append(
                {
                    "id": f"ceval-{subject}-val-{item['id']}",
                    "subject": subject,
                    "split": "upstream_val",
                    "query": item["question"],
                    "language": "zh",
                    "choices": {letter: item[letter] for letter in "ABCD"},
                    "answer_label": item["answer"],
                    "answer_text": item[item["answer"]],
                    "explanation": item["explanation"],
                    "retrieval_gold_status": "pending_corpus_evidence_mapping",
                    "license": "CC-BY-NC-SA-4.0",
                }
            )
    assert len({row["id"] for row in rows}) == len(rows)
    write_json(OUT / "ceval-computing/val-queries.json", rows)
    return {"queries": len(rows), "subject_counts": counts}


if __name__ == "__main__":
    try:
        download_manifest = RAW / "downloads.json"
        if download_manifest.exists():
            DOWNLOADS = json.loads(download_manifest.read_text())
        else:
            DOWNLOADS = json.loads((OUT / "manifest.json").read_text())["downloads"]
        for entry in DOWNLOADS:
            path = ROOT / entry["local_path"]
            if not path.exists():
                payload = urllib.request.urlopen(entry["url"], timeout=90).read()
                assert hashlib.sha256(payload).hexdigest() == entry["sha256"], entry["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
                record_operation(
                    f"下载{entry['dataset']}固定版本文件{entry['path']}",
                    "恢复公开数据集以复现导出",
                    f"下载{len(payload)}字节且SHA256一致",
                )
            assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], entry["path"]
        write_json(download_manifest, DOWNLOADS)
        summary = {
            "bright_stackoverflow": export_bright(),
            "ragbench_techqa": export_techqa(),
            "ceval_computing": export_ceval(),
        }
        exported_files = [
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
            }
            for path in sorted(OUT.rglob("*.json"))
            if path.name != "manifest.json"
        ]
        write_json(
            OUT / "manifest.json",
            {
                "version": "public-evals-v1",
                "downloads": DOWNLOADS,
                "summary": summary,
                "exported_files": exported_files,
                "existing_repository_benchmark_modified": False,
                "retrieval_run": False,
            },
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        record_operation(
            "导出公开评测数据到evals/public-benchmarks和data/public-evals/prepared",
            "为Infra项目补充外部题目，保留原生标注并隔离不同评测任务",
            json.dumps(summary, ensure_ascii=False),
            "TechQA模型回复不是参考答案；C-Eval尚无检索证据映射；未运行检索评测",
        )
    except Exception as error:
        record_operation("导出公开评测数据", "构建外部数据集", "失败", repr(error))
        raise
