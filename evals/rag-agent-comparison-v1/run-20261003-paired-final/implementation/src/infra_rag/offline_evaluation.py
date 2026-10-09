"""Three-layer, isolated QA evaluation using the existing answer prompt and validation."""

import json
import math
import statistics
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from .assistant import AnswerService, ConversationStore
from .benchmarking import (
    VARIANTS,
    automatic_answer_checks,
    bootstrap_groups,
    canonical_hash,
    normalized,
    span_coverage,
)
from .chunking import stable_id
from .evaluation import evidence_metrics, metrics


def enrich_questions(questions, dataset_dir):
    enriched = json.loads(json.dumps(questions))
    for q in enriched:
        for group in q["evidence_alternatives"]:
            for span in group["spans"]:
                span["absolute_source"] = str((Path(dataset_dir) / span["source"]).resolve())
    return enriched


def oracle_context(question):
    """First annotated complete alternative, selected independently of retrieval output."""
    if not question["answerable"]:
        return {"evidence": [], "condition_note": "no annotated support for this question"}
    spans = question["evidence_alternatives"][0]["spans"]
    evidence = []
    for span in spans:
        evidence.append(
            {
                "citation_id": "E" + stable_id(span["document_id"], span["text"]),
                "content": span["text"],
                "source": span["absolute_source"],
                "locator": span["source_url"],
                "document_id": span["document_id"],
            }
        )
    return {"evidence": evidence, "condition_note": "annotated evidence; not actual retrieval"}


class RecordingModel:
    def __init__(self, client):
        self.client, self.model, self.calls = client, client.model, []
        self.provider = getattr(client, "provider", "ollama")

    def generate(self, messages):
        call = {"messages": json.loads(json.dumps(messages))}
        self.calls.append(call)
        started = perf_counter()
        try:
            call["raw"] = self.client.generate(messages)
            return call["raw"]
        except Exception as exc:
            call["error"] = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            if getattr(self.client, "last_call", None) is not None:
                call["provider_response"] = self.client.last_call
            call["latency_ms"] = (perf_counter() - started) * 1000


class FrozenRetrieval:
    """Supply an already-frozen context to AnswerService, without changing production behavior."""

    def __init__(self, settings, context):
        self.settings, self.context = settings, context

    def search(self, query, *, context_pack, **kwargs):
        context_pack.update(self.context)
        return []


def generate_answer(question, context, settings, client):
    recorder = RecordingModel(client)
    started = perf_counter()
    with TemporaryDirectory(prefix="infra-offline-qa-") as directory:
        assistant = AnswerService(
            FrozenRetrieval(settings, context),
            model=recorder,
            store=ConversationStore(Path(directory) / "conversations.sqlite3"),
        )
        try:
            response = assistant.answer(question["query"])
            # Preserve the actual last model output; formatting retry failure is not a fact label.
            raw = (
                recorder.calls[-1].get("raw", "")
                if recorder.calls
                else json.dumps({"supported": False, "answer": response["answer"], "citations": []})
            )
            checks = automatic_answer_checks(raw, context["evidence"])
            checks["refused"] = response["status"] == "no_evidence"
            return {
                "response": response,
                "calls": recorder.calls,
                "checks": checks,
                "latency_ms": (perf_counter() - started) * 1000,
                "skipped_no_evidence": not recorder.calls,
                "error": None,
            }
        except Exception as exc:
            return {
                "response": None,
                "calls": recorder.calls,
                "checks": automatic_answer_checks("", context["evidence"]),
                "latency_ms": (perf_counter() - started) * 1000,
                "error": f"{type(exc).__name__}: {exc}",
            }


def resolve_evidence(service, questions):
    """Keep authored spans fixed when a sentence crosses child boundaries within a parent."""
    resolved = {}
    for question in questions:
        relevant, alternatives = set(), []
        for group in question["evidence_alternatives"]:
            requirements = []
            for span in group["spans"]:
                target = normalized(span["text"])
                source_chunks = [
                    c
                    for c in service.chunks
                    if c.source == span["absolute_source"]
                    or any(
                        a["source"] == span["absolute_source"]
                        for a in c.metadata.get("source_aliases", [])
                    )
                ]
                complete = [c.id for c in source_chunks if target in normalized(c.content)]
                if complete:
                    requirements.append(complete)
                    relevant.update(complete)
                    continue
                matches = []
                parents = dict.fromkeys(c.parent_id for c in source_chunks)
                for parent in parents:
                    chunks = [c for c in source_chunks if c.parent_id == parent]
                    texts = [normalized(c.content) for c in chunks]
                    merged = "".join(texts)
                    offset = merged.find(target)
                    if offset < 0:
                        continue
                    cursor, ids = 0, []
                    for chunk, text in zip(chunks, texts, strict=True):
                        if cursor < offset + len(target) and cursor + len(text) > offset:
                            ids.append(chunk.id)
                        cursor += len(text)
                    matches.append(ids)
                if not matches:
                    raise ValueError(
                        f"{question['id']}: authored evidence does not resolve: "
                        f"{span['document_id']}"
                    )
                if len(matches) != 1:
                    raise ValueError(
                        "ambiguous fragmented evidence; annotate explicit alternatives"
                    )
                requirements.extend([[cid] for cid in matches[0]])
                relevant.update(matches[0])
            alternatives.append({**group, "requirements": requirements})
        resolved[question["id"]] = {
            **question,
            "relevant": sorted(relevant),
            "evidence_alternatives": alternatives,
        }
    return resolved


def evaluation_rows(service, questions, dataset_dir, *, client=None, variants=VARIANTS):
    questions = enrich_questions(questions, dataset_dir)
    positives = [q for q in questions if q["answerable"]]
    resolved = resolve_evidence(service, positives)
    for question in questions:
        if client is not None:
            context = oracle_context(question)
            row = output_row(question, "oracle", "oracle", context)
            row["generation"] = generate_answer(question, context, service.settings, client)
            yield row

        for variant in variants:
            strategy = variant.replace("_rerank", "")
            service.settings = replace(service.settings, rerank=variant.endswith("_rerank"))
            diagnostics, ranking_context, delivered_context = {}, {}, {}
            started = perf_counter()
            hits = service.search(
                question["query"],
                top_k=10,
                domain="infra",
                modality="text",
                strategy=strategy,
                diagnostics=diagnostics,
                context_pack=ranking_context,
            )
            elapsed = (perf_counter() - started) * 1000
            # Evaluate actual top5 delivery separately from the top10 retrieval metrics.
            service.search(
                question["query"],
                top_k=5,
                domain="infra",
                modality="text",
                strategy=strategy,
                context_pack=delivered_context,
            )
            positions = {chunk.id: i for i, chunk in enumerate(service.chunks)}
            for context in (ranking_context, delivered_context):
                for evidence in context["evidence"]:
                    evidence["source_position"] = positions[evidence["chunk_id"]]
            ids = [h.chunk.id for h in hits]
            row = output_row(question, variant, "retrieved", delivered_context)
            row.update(
                retrieved=ids,
                diagnostics=diagnostics,
                retrieval_latency_ms=elapsed,
                ranking_context=ranking_context,
                at_k=None,
                candidate_hit=None,
                candidate_complete=None,
                resolved_gold=None,
            )
            if question["answerable"]:
                gold = resolved[question["id"]]
                row["resolved_gold"] = {
                    "relevant": gold["relevant"],
                    "evidence_alternatives": gold["evidence_alternatives"],
                }
                candidates = diagnostics.get("candidates", [])
                row["candidate_hit"] = float(bool(set(candidates) & set(gold["relevant"])))
                row["candidate_complete"] = evidence_metrics(
                    candidates, gold, max(1, len(candidates))
                )["complete_evidence_hit"]
                row["at_k"] = {
                    str(k): {**metrics(ids, gold["relevant"], k), **evidence_metrics(ids, gold, k)}
                    for k in (5, 10)
                }
            if client is not None:
                row["generation"] = generate_answer(
                    question, delivered_context, service.settings, client
                )
            yield row


def output_row(question, variant, condition, context):
    return {
        "id": question["id"],
        "group_id": question["group_id"],
        "question_type": question["question_type"],
        "query": question["query"],
        "answerable": question["answerable"],
        "variant": variant,
        "condition": condition,
        "review_key": f"{question['id']}:{variant}:{condition}",
        "required_points": question["answer_key"]["required_points"],
        "forbidden_claims": question["answer_key"]["forbidden_claims"],
        "context": context,
        "delivered": span_coverage(context["evidence"], question),
        "generation": None,
    }


def latency_summary(values):
    if not values:
        return None
    values = sorted(values)
    return {
        "p50_ms": statistics.median(values),
        "p95_ms": values[max(0, math.ceil(0.95 * len(values)) - 1)],
    }


def summarize(rows):
    result = {}
    for variant in dict.fromkeys(row["variant"] for row in rows):
        selected = [row for row in rows if row["variant"] == variant]
        positives = [row for row in selected if row["answerable"]]
        summaries = {}
        if variant != "oracle":
            for k in ("5", "10"):
                summaries[k] = (
                    {
                        key: statistics.mean(row["at_k"][k][key] for row in positives)
                        for key in positives[0]["at_k"][k]
                    }
                    if positives
                    else {}
                )
        flat = [
            {
                "group_id": row["group_id"],
                "delivered_complete": row["delivered"]["complete"] if row["delivered"] else None,
                "retrieval_complete": row["at_k"]["5"]["complete_evidence_hit"]
                if row.get("at_k")
                else None,
            }
            for row in selected
        ]
        generated = [row["generation"] for row in selected if row["generation"] is not None]
        result[variant] = {
            "questions": len(selected),
            "answerable": len(positives),
            "at_k": summaries,
            "context_complete_ci95": bootstrap_groups(flat, "delivered_complete"),
            "retrieval_complete_at_5_ci95": bootstrap_groups(flat, "retrieval_complete"),
            "retrieval_ci95": {
                k: {
                    key: bootstrap_groups(
                        [
                            {"group_id": row["group_id"], "value": row["at_k"][k][key]}
                            for row in positives
                        ],
                        "value",
                    )
                    for key in ("recall", "mrr", "ndcg", "complete_evidence_hit")
                }
                for k in ("5", "10")
            }
            if variant != "oracle"
            else {},
            "candidate_hit": statistics.mean(row["candidate_hit"] for row in positives)
            if positives and variant != "oracle"
            else None,
            "candidate_complete": statistics.mean(row["candidate_complete"] for row in positives)
            if positives and variant != "oracle"
            else None,
            "retrieval_latency": latency_summary(
                [row["retrieval_latency_ms"] for row in selected if "retrieval_latency_ms" in row]
            ),
            "generation_latency": latency_summary([g["latency_ms"] for g in generated]),
            "generation_with_model_latency": latency_summary(
                [g["latency_ms"] for g in generated if g["calls"]]
            ),
            "generation_errors": sum(bool(g["error"]) for g in generated),
            "format_valid": sum(g["checks"]["format_valid"] for g in generated),
            "citation_ids_valid": sum(g["checks"]["citation_ids_valid"] for g in generated),
            "fact_correct": None,
        }
    return result


def answer_review_template(rows):
    return [
        {
            "review_key": row["review_key"],
            "answer_sha256": canonical_hash(row["generation"]),
            "status": "pending",
            "method": "independent_human",
            "reviewer": "",
            "reviewed_at": "",
            "notes": "",
            "fact_correct": None,
            "contradiction": None,
            "unsupported_claim": None,
            "refusal_appropriate": None,
            "points_total": len(row["required_points"]),
            "points_supported": None,
            "citation_claims": None,
            "citation_supported": None,
        }
        for row in rows
        if row["generation"] is not None
    ]


def review_markdown(rows):
    lines = [
        "# 答案独立人工复核",
        "",
        "填写 answer-review.json；事实字段留空表示尚未评分。",
        "引用 ID 合法不代表陈述受到证据支持。",
        "",
    ]
    for row in rows:
        if row["generation"] is None:
            continue
        lines.extend(
            [
                f"## {row['review_key']}",
                "",
                row["query"],
                "",
                "必要要点：" + "；".join(row["required_points"]),
                "",
                "禁止误读：" + "；".join(row["forbidden_claims"]),
                "",
                "```json",
                json.dumps(row["generation"]["response"], ensure_ascii=False, indent=2),
                "```",
                "",
                "实际输入证据：",
                "",
            ]
        )
        for evidence in row["context"]["evidence"]:
            lines.extend(
                [
                    f"### {evidence['citation_id']}",
                    "",
                    evidence["locator"],
                    "",
                    "```text",
                    evidence["content"],
                    "```",
                    "",
                ]
            )
    return "\n".join(lines) + "\n"


def report_markdown(summary):
    lines = [
        "# 官方语料分层离线评测",
        "",
        f"状态：{summary['status']}。",
        "尚未完成人工答案评分；检索覆盖、格式和引用 ID 不是事实准确率。",
        "",
        "| 配置 | 题数 | Recall@5 | MRR@5 | nDCG@5 | 完整证据@5 | 生成错误 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, result in summary["summaries"].items():
        metrics5 = result["at_k"].get("5", {})
        values = [
            f"{metrics5[key]:.3f}" if key in metrics5 else "—"
            for key in ("recall", "mrr", "ndcg", "complete_evidence_hit")
        ]
        lines.append(
            f"| {name} | {result['questions']} | "
            + " | ".join(values)
            + f" | {result['generation_errors']} |"
        )
    lines.extend(
        [
            "",
            f"索引构建/恢复：{summary['index_build_or_restore_ms']:.1f} ms。",
            f"首次预热：{summary['first_warmup_ms']:.1f} ms。",
            "",
            "计时边界：" + summary["latency_scope"],
            "",
            "分题型结果及bootstrap区间见 summary.json；逐题排名、上下文及回答见 rows.jsonl。",
            "填写 answer-review.json 后以 score 命令生成独立人工评分结果。",
        ]
    )
    return "\n".join(lines) + "\n"
