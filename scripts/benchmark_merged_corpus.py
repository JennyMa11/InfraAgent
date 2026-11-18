"""Compare official and merged retrieval on fixed Chinese dev queries, never holdout."""

import json
from dataclasses import replace
from pathlib import Path

from merge_corpus import OUT, ROOT, ProvenanceRetrieval, build, settings
from operation_log import record_operation

from infra_rag.benchmarking import canonical_hash, digest, validate_dataset
from infra_rag.legacy_model_clients import AnthropicClient
from infra_rag.offline_evaluation import (
    answer_review_template,
    enrich_questions,
    evaluation_rows,
    generate_answer,
    review_markdown,
    summarize,
)
from infra_rag.query_expansion import ExpandedRetrieval, load_rewrites
from infra_rag.service import RetrievalService


def main():
    directory = build()
    dataset = ROOT / "evals/infra-official-v1-reviewed"
    _, splits = validate_dataset(dataset, ROOT, formal=True)
    questions = splits["dev"]
    rewrites_path = dataset / "results/dev-opt-english-query-20261001/query-rewrites.jsonl"
    rewrites = load_rewrites(rewrites_path, questions)
    output = OUT / "dev-20261002"
    output.mkdir(parents=True, exist_ok=False)
    # Fix the generation sample before retrieval: first two IDs per type, including refusals.
    selected = set()
    for kind in sorted({q["question_type"] for q in questions}):
        selected.update(
            q["id"]
            for q in sorted(
                (q for q in questions if q["question_type"] == kind), key=lambda q: q["id"]
            )[:2]
        )
    protocol = {
        "kind": "dev_only_merged_corpus_comparison",
        "dataset_manifest_sha256": digest(dataset / "dataset-manifest.json"),
        "dev_sha256": digest(dataset / "dev.json"),
        "merged_manifest_sha256": digest(OUT / "corpus-manifest.json"),
        "rewrites_sha256": digest(rewrites_path),
        "generation_ids": sorted(selected),
        "generation_selection": "first two IDs per type, fixed before retrieval",
        "settings": settings(directory).fingerprint(),
        "retrieval": {
            "candidate_k": 30,
            "fusion_candidates": "union",
            "top_k": 5,
            "context_chars": 4000,
            "context_tokens": 1200,
        },
        "script_sha256": digest(Path(__file__)),
        "notes": [
            "Original sparse official gold only; added equivalent evidence not labeled.",
            "Unanswerable status may change in expanded corpus; review separately.",
            "AI source/answer audit is not independent human scoring.",
        ],
    }
    (output / "protocol.json").write_text(json.dumps(protocol, ensure_ascii=False, indent=2))
    rows = []
    arms = [
        (
            "official_english",
            RetrievalService(settings(ROOT / "data/deepseek-optimized")),
            "english",
        ),
        ("merged_english", ProvenanceRetrieval(settings(directory)), "english"),
        ("merged_bilingual", ProvenanceRetrieval(settings(directory)), "bilingual"),
    ]
    with (output / "retrieval.jsonl").open("x") as stream:
        for arm, service, mode in arms:
            wrapper = ExpandedRetrieval(service, rewrites, mode)
            for row in evaluation_rows(wrapper, questions, dataset, variants=["hybrid_rerank"]):
                row["arm"] = arm
                rows.append(row)
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                stream.flush()
                print(arm, row["id"], flush=True)
    enriched = {q["id"]: q for q in enrich_questions(questions, dataset)}
    model = AnthropicClient.from_environment(path=ROOT / ".env.llm", max_tokens=650)
    protocol["generation_model"] = model.configuration()
    (output / "protocol.json").write_text(json.dumps(protocol, ensure_ascii=False, indent=2))
    answers = []
    with (output / "answers.jsonl").open("x") as stream:
        for row in rows:
            if row["id"] not in selected:
                continue
            row = dict(row)
            row["review_key"] = f"{row['id']}:{row['arm']}"
            row["generation"] = generate_answer(
                enriched[row["id"]],
                row["context"],
                replace(settings(directory), query_language="none"),
                model,
            )
            answers.append(row)
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            stream.flush()
            print("answer", row["review_key"], flush=True)
    summary = {
        arm: summarize([r for r in rows if r["arm"] == arm])["hybrid_rerank"] for arm, _, _ in arms
    }
    for arm, _, _ in arms:
        generated = [r for r in answers if r["arm"] == arm]
        summary[arm]["generation_sample"] = summarize(generated)["hybrid_rerank"]
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    (output / "answer-review.json").write_text(
        json.dumps(answer_review_template(answers), ensure_ascii=False, indent=2)
    )
    (output / "answer-review.md").write_text(review_markdown(answers))
    lines = [
        "# 合并语料 dev 对照",
        "",
        "固定中文 dev60；使用相同冻结译文、模型、重排与上下文预算。",
        "",
        "| 配置 | Recall@5 | MRR@10 | nDCG@10 | 完整证据交付 |",
        "|---|---:|---:|---:|---:|",
    ]
    for arm, result in summary.items():
        lines.append(
            f"| {arm} | {result['at_k']['5']['recall']:.4f} | "
            f"{result['at_k']['10']['mrr']:.4f} | "
            f"{result['at_k']['10']['ndcg']:.4f} | "
            f"{result['context_complete_ci95']['mean']:.4f} |"
        )
    lines.extend(
        [
            "",
            *protocol["notes"],
            "",
            "回答样本为每类型按ID固定选2题，共12题×3配置。",
            "事实评分保持空值，逐题生成与证据见 answers.jsonl。",
        ]
    )
    (output / "report.md").write_text("\n".join(lines) + "\n")
    record_operation(
        "建立合并语料索引并完成中文dev对照",
        "补充中文Infra材料并检验检索与回答",
        f"127来源；结果{output.relative_to(ROOT)}；摘要hash {canonical_hash(summary)}",
        "官方gold为稀疏标注；拒答题需在新增语料上复核；回答尚无独立人工评分",
    )


if __name__ == "__main__":
    main()
