"""Verify fixed-candidate model control against recorded logits and original evidence."""

import argparse
import json
import math
from pathlib import Path

from benchmark_reranker_v10 import METHODS, POOLS, prepare, read_rows
from operation_log import record_operation
from prepare_corpus_v2 import ROOT

from infra_rag.benchmarking import canonical_hash, digest, span_coverage, write_new
from infra_rag.chunking import stable_id
from infra_rag.evaluation import evidence_metrics


def audit(run, protocol, references, chunks, count):
    rows = read_rows(run / "rows.jsonl")
    expected = {
        (*key[:2], f"{pool}{model}-{method}")
        for key in references
        for pool in POOLS
        for model in ("", "-m3")
        for method in METHODS
    }
    actual = [(r["dataset"], r["id"], r["arm"]) for r in rows]
    if set(actual) != expected or len(actual) != len(set(actual)):
        raise ValueError("Incomplete/unknown/duplicate quality rows")
    cache = json.loads((run / "m3-score-cache.json").read_text())
    calls = read_rows(run / "model-calls.jsonl")
    score_witnesses, scored_pairs, truncated = {}, 0, 0
    for call in calls:
        arrays = [
            call[k]
            for k in (
                "chunk_ids",
                "body_hashes",
                "raw_logits",
                "scores",
                "input_tokens",
                "would_truncate",
            )
        ]
        if not all(len(values) == call["actual_pairs"] for values in arrays):
            raise ValueError("Incomplete model-call accounting")
        if call["actual_pairs"] > 90 or call["dtype"] != "torch.float32" or call["device"] != "mps":
            raise ValueError("Model budget/device changed")
        for cid, body_hash, logit, score, tokens, cutoff in zip(*arrays, strict=True):
            if canonical_hash(chunks[cid].content) != body_hash:
                raise ValueError("Model scored changed body")
            expected_score = (
                1 / (1 + math.exp(-logit))
                if logit >= 0
                else math.exp(logit) / (1 + math.exp(logit))
            )
            if not math.isfinite(logit) or score != expected_score or cutoff != (tokens > 512):
                raise ValueError("Logit transform or input accounting mismatch")
            key = canonical_hash([protocol["m3"], call["query"], chunks[cid].content])
            if cache[key] != score:
                raise ValueError("Score cache differs from actual model call")
            score_witnesses[key] = score
            scored_pairs += 1
            truncated += cutoff
    positions = {cid: i for i, cid in enumerate(chunks)}
    exact, checked, ranking_changes = 0, 0, []
    for row in rows:
        before = references[row["dataset"], row["id"], f"{row['pool']}-{row['method']}"]
        for field in (
            "query",
            "scoring_query",
            "resolved_gold",
            "group_id",
            "answerable",
            "local_trace",
        ):
            if row[field] != before[field]:
                raise ValueError("Changed original query/label/scope: " + field)
        if set(row["candidate_ids"]) != set(before["candidate_ids"]) or row["candidate_count"] > 90:
            raise ValueError("Changed fixed candidate set")
        fusion = {h["chunk_id"]: h["score"] for h in before["ranked_hits"]}
        if (
            len(row["ranked_hits"]) != len(row["candidate_ids"])
            or [h["chunk_id"] for h in row["ranked_hits"]] != row["candidate_ids"]
        ):
            raise ValueError("Ranking/candidate identity mismatch")
        for hit in row["ranked_hits"]:
            cid = hit["chunk_id"]
            if hit["score"] != fusion[cid]:
                raise ValueError("Fusion score changed")
            if row["model"] == "m3":
                key = canonical_hash([protocol["m3"], row["scoring_query"], chunks[cid].content])
                if hit["rerank_score"] != score_witnesses[key]:
                    raise ValueError("Score not backed by recorded inference")
        if row["model"] == "base":
            if row["context"] != before["context"] or row["ranked_hits"] != before["ranked_hits"]:
                raise ValueError("Base control changed")
            exact += 1
        context = row["context"]
        if (
            count(context["context"]) != context["used_tokens"]
            or len(context["context"]) != context["used_characters"]
        ):
            raise ValueError("Body counters mismatch")
        if (
            context["used_tokens"] > 1200
            or context["used_characters"] > 4000
            or len(context["evidence"]) > 8
        ):
            raise ValueError("Body budget exceeded")
        eids = [e["chunk_id"] for e in context["evidence"]]
        if len(eids) != len(set(eids)) or not set(eids) <= set(row["candidate_ids"]):
            raise ValueError("Evidence identity invalid")
        for evidence in context["evidence"]:
            c = chunks[evidence["chunk_id"]]
            if (
                evidence["source"] != c.source
                or evidence["locator"] != c.locator
                or evidence["metadata"] != c.metadata
                or evidence["parent_id"] != c.parent_id
                or evidence["source_position"] != positions[c.id]
                or evidence["citation_id"] != "E" + stable_id(c.id)
            ):
                raise ValueError("Evidence provenance changed")
            if (
                not c.content.startswith(evidence["content"])
                or evidence["truncated"] != (c.content != evidence["content"])
                or "```" in c.content
                and c.content != evidence["content"]
            ):
                raise ValueError("Evidence body changed")
            checked += 1
        gold = row["resolved_gold"] if row["answerable"] else None
        if (
            gold
            and evidence_metrics(row["candidate_ids"], gold, 90)["complete_evidence_hit"]
            != row["candidate_complete"]
        ):
            raise ValueError("Candidate metric mismatch")
        if (
            span_coverage(
                context["evidence"],
                {**row, "evidence_alternatives": gold["evidence_alternatives"] if gold else []},
            )
            != row["delivered"]
        ):
            raise ValueError("Text delivery metric mismatch")
        if gold and row["model"] == "m3":
            ranking_changes.append(
                {
                    "dataset": row["dataset"],
                    "id": row["id"],
                    "arm": row["arm"],
                    "frontier_complete": evidence_metrics(
                        row["packing_trace"]["eligible_ids"], gold, 90
                    )["complete_evidence_hit"],
                    "delivered": row["delivered"]["complete"],
                    "delta_vs_same_pool_method": row["delivered"]["complete"]
                    - before["delivered"]["complete"],
                }
            )
    return {
        "rows_checked": len(rows),
        "base_contexts_exact": exact,
        "evidence_checked": checked,
        "recorded_model_calls": len(calls),
        "actual_scored_pairs": scored_pairs,
        "truncated_pairs": truncated,
        "all_mechanical_invariants_passed": True,
        "ranking_delivery_details": ranking_changes,
        "semantic_review": None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    args = parser.parse_args()
    run = args.run.resolve()
    protocol, references, chunks, count = prepare(run)
    write_new(
        run / "audit-protocol.json",
        {
            "posthoc": True,
            "implementation_sha256": digest(__file__),
            "inputs": {
                n: digest(run / n)
                for n in ("protocol.json", "rows.jsonl", "m3-score-cache.json", "model-calls.jsonl")
            },
        },
    )
    result = audit(run, protocol, references, chunks, count)
    write_new(run / "integrity-audit.json", result)
    print({k: v for k, v in result.items() if k != "ranking_delivery_details"})
    record_operation(
        f"机械审计v10 {run.relative_to(ROOT)}",
        "确认模型独立变量、实际logit与原文交付",
        f"{result['rows_checked']}条记录及{result['evidence_checked']}条证据通过复核",
        "独立语义审核pending",
    )


if __name__ == "__main__":
    main()
