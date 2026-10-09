"""Posthoc mechanical verification of every frozen v9 candidate and evidence body."""

import argparse
import math
from pathlib import Path

from benchmark_document_local_v9 import METHODS, POOLS, prepare, read_rows
from operation_log import record_operation
from prepare_corpus_v2 import ROOT

from infra_rag.benchmarking import digest, span_coverage, write_new
from infra_rag.chunking import stable_id
from infra_rag.document_local import DocumentLocalBM25
from infra_rag.evaluation import evidence_metrics


def audit_rows(rows, references, chunks, count, *, real=False):
    index = DocumentLocalBM25(list(chunks.values()))
    positions = {cid: i for i, cid in enumerate(chunks)}
    expected_cases = {(ds, cid) for ds, cid, pool in references if pool == "B"}
    actual = [(r["dataset"], r["id"], r["arm"]) for r in rows]
    arms = {r["arm"] for r in rows}
    expected_arms = arms if real else {f"{p}-{m}" for p in POOLS for m in METHODS}
    if real and (
        len(arms) != 2 or "B-O15" not in arms or not any(a.startswith("Doc-") for a in arms)
    ):
        raise ValueError("Unknown actual runtime arms")
    expected = {(*key, arm) for key in expected_cases for arm in expected_arms}
    if set(actual) != expected or len(actual) != len(set(actual)):
        raise ValueError("Incomplete, unknown or duplicate outputs")
    indexed = {key: r for key, r in zip(actual, rows, strict=True)}
    checked, exact = 0, 0
    deltas = {}
    for row in rows:
        before = references[row["dataset"], row["id"], row["pool"] if row["pool"] != "Doc" else "B"]
        for field in ("query", "scoring_query", "group_id", "answerable", "resolved_gold"):
            if before[field] != row[field]:
                raise ValueError("Changed query or label: " + field)
        ids = row["candidate_ids"]
        if len(ids) != len(set(ids)) or len(ids) > 90:
            raise ValueError("Candidate identity/cap violated")
        if [h["chunk_id"] for h in row["ranked_hits"]] != ids:
            raise ValueError("Candidate ranking inconsistent")
        if row["pool"] == "Doc":
            if real:
                baseline = indexed[row["dataset"], row["id"], "B-O15"]
                base_hits = baseline["ranked_hits"]
            else:
                base_hits = references[row["dataset"], row["id"], "B"]["ranked_hits"]
            pool, trace = index.supplement(base_hits, row["scoring_query"])
            saved_trace = row["local_trace"]
            same_trace = all(trace[k] == saved_trace[k] for k in trace if k != "channels")
            same_channels = len(trace["channels"]) == len(saved_trace["channels"])
            for actual_channel, saved_channel in zip(
                trace["channels"], saved_trace["channels"], strict=True
            ):
                if len(actual_channel) != len(saved_channel):
                    same_channels = False
                    continue
                same_channels &= all(
                    a["chunk_id"] == s["chunk_id"]
                    and a["rank"] == s["rank"]
                    and math.isclose(a["score"], s["score"], rel_tol=1e-12, abs_tol=1e-12)
                    for a, s in zip(actual_channel, saved_channel, strict=True)
                )
            if not same_trace or not same_channels or {cid for cid, _ in pool} != set(ids):
                raise ValueError("Document-local candidate scope not reproducible")
            old_scores = {h["chunk_id"]: h["rerank_score"] for h in base_hits}
            if any(
                h["chunk_id"] in old_scores and h["rerank_score"] != old_scores[h["chunk_id"]]
                for h in row["ranked_hits"]
            ):
                raise ValueError("Baseline rerank score changed")
        elif not real and row["ranked_hits"] != before["ranked_hits"]:
            raise ValueError("Reference ranking changed")
        if real and (row["actual_rerank_pairs"] > 90 or row["result_cache_enabled"]):
            raise ValueError("Actual runtime work/cache cap violated")
        context = row["context"]
        if (
            count(context["context"]) != context["used_tokens"]
            or len(context["context"]) != context["used_characters"]
            or context["used_tokens"] > 1200
            or context["used_characters"] > 4000
            or len(context["evidence"]) > 8
        ):
            raise ValueError("Body budget/counter mismatch")
        eids = [e["chunk_id"] for e in context["evidence"]]
        if len(eids) != len(set(eids)) or not set(eids) <= set(ids):
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
                or not c.content.startswith(evidence["content"])
                or evidence["truncated"] != (c.content != evidence["content"])
                or "```" in c.content
                and c.content != evidence["content"]
            ):
                raise ValueError("Evidence body/provenance/citation invalid")
            checked += 1
        if not real and row["pool"] != "Doc" and row["method"] == "O15":
            if context != before["context"]:
                raise ValueError("Reference context changed")
            exact += 1
        gold = row["resolved_gold"] if row["answerable"] else None
        if (
            gold
            and evidence_metrics(ids, gold, 90)["complete_evidence_hit"]
            != row["candidate_complete"]
        ):
            raise ValueError("Candidate metric mismatch")
        metric = span_coverage(
            context["evidence"],
            {**row, "evidence_alternatives": gold["evidence_alternatives"] if gold else []},
        )
        if metric != row["delivered"]:
            raise ValueError("Actual text metric mismatch")
        key = f"{row['dataset']}:{row['arm']}"
        delta = deltas.setdefault(key, {"gained_ids": [], "lost_ids": []})
        base = indexed[row["dataset"], row["id"], "B-O15"]
        if gold and metric["complete"] > base["delivered"]["complete"]:
            delta["gained_ids"].append(row["id"])
        if gold and metric["complete"] < base["delivered"]["complete"]:
            delta["lost_ids"].append(row["id"])
    return {
        "rows_checked": len(rows),
        "evidence_checked": checked,
        "exact_reference_contexts": exact,
        "all_mechanical_invariants_passed": True,
        "delivery_deltas_vs_B_O15": deltas,
        "semantic_review": None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--output", type=Path, help="New directory for a revised posthoc audit")
    args = parser.parse_args()
    run = args.run.resolve()
    output = args.output.resolve() if args.output else run
    if args.output:
        output.mkdir(parents=True, exist_ok=False)
    _, references, chunks, count = prepare(run)
    names = ["protocol.json", "rows.jsonl", "quality-summary.json", "quality-selection.json"]
    if (run / "runtime.jsonl").exists():
        names.append("runtime.jsonl")
    write_new(
        output / "audit-protocol.json",
        {
            "posthoc": True,
            "trace_float_tolerance": 1e-12,
            "rank_and_candidate_identity_tolerance": 0,
            "implementation_sha256": digest(__file__),
            "inputs": {n: digest(run / n) for n in names},
        },
    )
    result = {"quality": audit_rows(read_rows(run / "rows.jsonl"), references, chunks, count)}
    if "runtime.jsonl" in names:
        result["runtime"] = audit_rows(
            read_rows(run / "runtime.jsonl"), references, chunks, count, real=True
        )
    write_new(output / "integrity-audit.json", result)
    print(
        {
            phase: {k: v for k, v in data.items() if k != "delivery_deltas_vs_B_O15"}
            for phase, data in result.items()
        }
    )
    record_operation(
        f"逐题机械审计v9 {run.relative_to(ROOT)}",
        "验收原文、source-release范围及候选与交付账目",
        "逐题指标与全部机械不变量复核通过",
        "独立语义审核pending；不是答案正确性审核",
    )


if __name__ == "__main__":
    main()
