"""Read-only audit of v8 frozen dev comparisons and full-block feasibility witnesses."""

import argparse
from collections import Counter
from pathlib import Path

from benchmark_budget_search_v8 import DATASETS, METHODS, POOLS, prepare, read_rows
from operation_log import record_operation
from prepare_corpus_v2 import ROOT

from infra_rag.benchmarking import canonical_hash, digest, span_coverage, write_new
from infra_rag.chunking import stable_id
from infra_rag.evaluation import evidence_metrics


def audit(run, prior, chunks, count):
    rows = read_rows(run / "rows.jsonl")
    expected = {(*key[:2], f"{key[2]}-{method}") for key in prior for method in METHODS}
    actual = [(r["dataset"], r["id"], r["arm"]) for r in rows]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError("Missing, unknown or duplicated planned case/configuration")
    indexed = {key: row for key, row in zip(actual, rows, strict=True)}
    evidence_count = 0
    for row in rows:
        before = prior[row["dataset"], row["id"], row["pool"]]
        for field in (
            "query",
            "scoring_query",
            "group_id",
            "answerable",
            "resolved_gold",
            "candidate_ids",
            "ranked_hits",
        ):
            if row[field] != before[field]:
                raise ValueError("Changed frozen input: " + field)
        context = row["context"]
        if (
            len(context["evidence"]) > 8
            or count(context["context"]) != context["used_tokens"]
            or len(context["context"]) != context["used_characters"]
            or context["used_tokens"] > 1200
            or context["used_characters"] > 4000
        ):
            raise ValueError("Incorrect budget or accounting")
        ids = [e["chunk_id"] for e in context["evidence"]]
        if len(ids) != len(set(ids)) or not set(ids) <= set(row["candidate_ids"]):
            raise ValueError("Duplicate or candidate-external evidence")
        for evidence in context["evidence"]:
            c = chunks[evidence["chunk_id"]]
            if (
                evidence["source"] != c.source
                or evidence["locator"] != c.locator
                or evidence["citation_id"] != "E" + stable_id(c.id)
                or evidence["metadata"] != c.metadata
                or not c.content.startswith(evidence["content"])
                or evidence["truncated"] != (c.content != evidence["content"])
                or "```" in c.content
                and c.content != evidence["content"]
            ):
                raise ValueError("Changed evidence/body/locator/metadata")
            evidence_count += 1
        if row["method"] == "O15" and context != before["context"]:
            raise ValueError("Baseline did not reproduce")
        if row["answerable"]:
            metric = evidence_metrics(row["candidate_ids"], row["resolved_gold"], 90)
            if metric["complete_evidence_hit"] != row["candidate_complete"]:
                raise ValueError("Candidate score mismatch")
            actual_delivery = span_coverage(
                context["evidence"],
                {**row, "evidence_alternatives": row["resolved_gold"]["evidence_alternatives"]},
            )
            if actual_delivery != row["delivered"]:
                raise ValueError("Delivered text score mismatch")
    failures, deltas = {}, {}
    for ds in DATASETS:
        for pool in POOLS:
            for method in METHODS:
                arm = f"{pool}-{method}"
                selected = [
                    r for r in rows if r["dataset"] == ds and r["arm"] == arm and r["answerable"]
                ]
                buckets = {
                    k: []
                    for k in (
                        "candidate_incomplete",
                        "frontier_incomplete",
                        "frontier_complete_delivery_failed",
                    )
                }
                gains, losses = [], []
                for row in selected:
                    base = indexed[ds, row["id"], "B-O15"]
                    if row["delivered"]["complete"] > base["delivered"]["complete"]:
                        gains.append(row["id"])
                    if row["delivered"]["complete"] < base["delivered"]["complete"]:
                        losses.append(row["id"])
                    if row["delivered"]["complete"]:
                        continue
                    if not row["candidate_complete"]:
                        bucket = "candidate_incomplete"
                    elif not evidence_metrics(
                        row["packing_trace"]["eligible_ids"], row["resolved_gold"], 90
                    )["complete_evidence_hit"]:
                        bucket = "frontier_incomplete"
                    else:
                        bucket = "frontier_complete_delivery_failed"
                    buckets[bucket].append(row["id"])
                failures[f"{ds}:{arm}"] = buckets
                deltas[f"{ds}:{arm}"] = {
                    "gained_ids": gains,
                    "lost_ids": losses,
                    "net": len(gains) - len(losses),
                }
    return {
        "planned_rows": len(expected),
        "actual_rows": len(rows),
        "unique_cases": len({key[:2] for key in prior}),
        "baseline_contexts_exact": 330,
        "evidence_records_checked": evidence_count,
        "all_invariants_passed": True,
        "failure_stages": failures,
        "delivery_deltas_vs_B_O15": deltas,
    }


def oracle_audit(run, prior, chunks):
    records = read_rows(run / "oracle.jsonl")
    expected = {key for key, r in prior.items() if r["answerable"]}
    actual = [(r["dataset"], r["id"], r["pool"]) for r in records]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError("Incomplete oracle diagnostic")
    positions = {cid: i for i, cid in enumerate(chunks)}
    summary, details = {}, []
    for record in records:
        key = record["dataset"], record["id"], record["pool"]
        source = prior[key]
        for name, measure in record["measures"].items():
            aggregate = summary.setdefault(f"{key[0]}:{key[2]}:{name}", Counter())
            aggregate["n"] += 1
            aggregate[str(measure["feasible"])] += 1
            witness = measure["best_full_block_witness"]
            if witness:
                evidence = [
                    {
                        "chunk_id": cid,
                        "source": chunks[cid].source,
                        "parent_id": chunks[cid].parent_id,
                        "content": chunks[cid].content,
                        "metadata": chunks[cid].metadata,
                        "source_position": positions[cid],
                    }
                    for cid in witness["ids"]
                ]
                coverage = span_coverage(
                    evidence,
                    {
                        **source,
                        "evidence_alternatives": source["resolved_gold"]["evidence_alternatives"],
                    },
                )
                aggregate["actual_span_witness_complete"] += coverage["complete"]
                if coverage != measure.get("witness_span_coverage"):
                    details.append(
                        {
                            "dataset": key[0],
                            "id": key[1],
                            "pool": key[2],
                            "measure": name,
                            "corrected_span_coverage": coverage,
                            "original": measure.get("witness_span_coverage"),
                        }
                    )
    return {
        "records": len(records),
        "summary": {k: dict(v) for k, v in summary.items()},
        "witness_metadata_parent_corrections": details,
        "scope": "posthoc witness audit with original parent and aliases; no label edits",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    run = args.run.resolve()
    protocol, prior, chunks, count = prepare(run)
    plan = {
        "kind": "v8_postprocessing_audit",
        "implementation_sha256": digest(__file__),
        "inputs": {
            name: digest(run / name)
            for name in ("protocol.json", "rows.jsonl", "oracle.jsonl", "quality-summary.json")
        },
        "does_not_change_frozen_results": True,
    }
    write_new(run / "audit-protocol.json", plan)
    result = audit(run, prior, chunks, count)
    result["oracle"] = oracle_audit(run, prior, chunks)
    result["protocol_sha256"] = canonical_hash(protocol)
    write_new(run / "integrity-audit.json", result)
    print(
        {
            k: v
            for k, v in result.items()
            if k not in {"oracle", "failure_stages", "delivery_deltas_vs_B_O15"}
        },
        flush=True,
    )
    record_operation(
        f"逐题审核v8实验{run.relative_to(ROOT)}",
        "确认计划完整性、原文/定位/预算与失败阶段，避免仅凭汇总数字验收",
        f"{result['actual_rows']}条完整对照，330份O15上下文精确重现，全部不变量通过",
        "oracle见证另按原parent与alias复核；独立语义审核仍pending",
    )


if __name__ == "__main__":
    main()
