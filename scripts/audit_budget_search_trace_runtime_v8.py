"""Audit directly recorded actual candidates, ranking, scoring inputs and body."""

import argparse
import json
import math
from collections import Counter
from pathlib import Path

from benchmark_budget_search_trace_runtime_v8 import SOURCE, prepare, read_rows
from operation_log import record_operation
from prepare_corpus_v2 import ROOT

from infra_rag.benchmarking import canonical_hash, digest, span_coverage, write_new
from infra_rag.context import pack_context
from infra_rag.evaluation import evidence_metrics
from infra_rag.models import Hit


def actual_context(record, chunks, count):
    """Reconstruct the deterministic renderer from recorded ordered actual IDs."""
    hits = [Hit(chunks[cid], 0.0, rerank_score=0.0) for cid in record["selected_ids"]]
    parents = {}
    for hit in hits:
        parents.setdefault(hit.chunk.parent_id, []).append(hit.chunk)
    context = pack_context(hits, parents, count, 1200, 4000, "infra", "text")
    if context != record["actual_context"]:
        raise ValueError("Direct actual body differs from deterministic renderer")
    if (
        [e["chunk_id"] for e in context["evidence"]] != record["selected_ids"]
        or context["used_tokens"] != record["used_tokens"]
        or context["used_characters"] != record["used_characters"]
    ):
        raise ValueError("Cannot reproduce actual context using recorded IDs and counters")
    positions = {cid: i for i, cid in enumerate(chunks)}
    for evidence in context["evidence"]:
        evidence["source_position"] = positions[evidence["chunk_id"]]
    return context


def audit(run, old, v7, chunks, count):
    runtime = read_rows(run / "latency.jsonl")
    cases = {(ds, cid) for ds, cid, pool in v7 if pool == "B"}
    expected = {(*key, arm) for key in cases for arm in ("B-O15", "Ladj-X30")}
    actual = [(r["dataset"], r["id"], r["arm"]) for r in runtime]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError("Incomplete/unknown/duplicate real runtime records")
    component_rows = read_rows(run / "components.jsonl")
    component_map = {(r["dataset"], r["id"], r["method"]): r for r in component_rows}
    if len(component_map) != 220 or set(component_map) != {
        (*key, method) for key in cases for method in ("original", "optimized")
    }:
        raise ValueError("Incomplete component comparison")
    for key in cases:
        if (
            component_map[*key, "original"]["context_sha256"]
            != component_map[*key, "optimized"]["context_sha256"]
        ):
            raise ValueError("Timed component results differ")
    references = {(r["dataset"], r["id"], r["arm"]): r for r in old}
    actual_map = {(r["dataset"], r["id"], r["arm"]): r for r in runtime}
    model_calls = read_rows(run / "score-inputs.jsonl")
    if len(model_calls) != 222:
        raise ValueError("Expected two warmup plus220 recorded actual model calls")
    candidate_results = {}
    for record, call in zip(runtime, model_calls[2:], strict=True):
        hits = record["actual_ranked_hits"]
        ids = record["actual_candidate_ids"]
        source = v7[record["dataset"], record["id"], "B"]
        query = record["actual_scoring_query"]
        if query != source["scoring_query"] or ids != [h["chunk_id"] for h in hits]:
            raise ValueError("Actual query/ranking identity mismatch")
        if len(ids) != len(set(ids)) or len(ids) > 90 or len(ids) != record["actual_rerank_pairs"]:
            raise ValueError("Actual candidate/scoring count mismatch")
        if any(not math.isfinite(h["rerank_score"]) or h["rerank_score"] < 0 for h in hits):
            raise ValueError("Actual model score invalid")
        if hits != sorted(hits, key=lambda h: (-h["rerank_score"], -h["score"], h["chunk_id"])):
            raise ValueError("Actual ranking order mismatch")
        if Counter((query, chunks[cid].content) for cid in ids) != Counter(
            tuple(p) for p in call["pairs"]
        ):
            raise ValueError("Actual candidates not bound to recorded original-body model inputs")
        if record["arm"] == "Ladj-X30" and not set(
            actual_map[record["dataset"], record["id"], "B-O15"]["actual_candidate_ids"]
        ) <= set(ids):
            raise ValueError("Actual baseline candidates not retained")
        name = f"{record['dataset']}:{record['arm']}"
        summary = candidate_results.setdefault(name, {"numerator": 0, "denominator": 0})
        if source["answerable"]:
            summary["denominator"] += 1
            summary["numerator"] += evidence_metrics(ids, source["resolved_gold"], 90)[
                "complete_evidence_hit"
            ]
    for metric in candidate_results.values():
        metric["value"] = (
            metric["numerator"] / metric["denominator"] if metric["denominator"] else None
        )
    summaries, differences, records = {}, [], []
    for record in runtime:
        count.cache_clear()
        if record["actual_rerank_pairs"] > 90 or record["result_cache_enabled"]:
            raise ValueError("Runtime scoring/cache contract violated")
        if len(record["selected_ids"]) > 8:
            raise ValueError("Runtime evidence cap violated")
        context = actual_context(record, chunks, count)
        source = v7[record["dataset"], record["id"], "B"]
        metric = span_coverage(
            context["evidence"],
            {
                **source,
                "evidence_alternatives": source["resolved_gold"]["evidence_alternatives"]
                if source["answerable"]
                else [],
            },
        )
        old_row = references[record["dataset"], record["id"], record["arm"]]
        if context != old_row["context"]:
            differences.append(
                {
                    "dataset": record["dataset"],
                    "id": record["id"],
                    "arm": record["arm"],
                    "old": old_row["delivered"],
                    "actual": metric,
                    "old_selected_ids": old_row["selected_ids"],
                    "actual_selected_ids": record["selected_ids"],
                }
            )
        name = f"{record['dataset']}:{record['arm']}"
        summary = summaries.setdefault(
            name, {"runs": 0, "positives": 0, "delivered": 0, "negative_cases": 0}
        )
        summary["runs"] += 1
        if source["answerable"]:
            summary["positives"] += 1
            summary["delivered"] += metric["complete"]
        else:
            summary["negative_cases"] += 1
        records.append(
            {
                "dataset": record["dataset"],
                "id": record["id"],
                "arm": record["arm"],
                "context": context,
                "delivered": metric,
                "context_sha256": canonical_hash(context),
                "reconstruction": "recorded ordered IDs + unchanged deterministic renderer",
                "is_new_generated_answer": False,
            }
        )
    for summary in summaries.values():
        n, d = summary["delivered"], summary["positives"]
        summary["evidence_delivery_rate"] = {
            "numerator": n,
            "denominator": d,
            "value": n / d if d else None,
        }
        summary["mechanical_coverage"] = {"numerator": d, "denominator": d, "value": 1.0}
        summary["independent_answer_review"] = None
    gain = sum(
        summaries[f"{ds}:Ladj-X30"]["delivered"] - summaries[f"{ds}:B-O15"]["delivered"]
        for ds in ("official", "repository")
    )
    no_loss = all(
        summaries[f"{ds}:Ladj-X30"]["delivered"] >= summaries[f"{ds}:B-O15"]["delivered"]
        for ds in ("official", "repository")
    )
    return {
        "runtime_records": 220,
        "actual_candidate_results": candidate_results,
        "actual_candidate_quality_gate": all(
            candidate_results[f"{ds}:Ladj-X30"]["numerator"]
            >= candidate_results[f"{ds}:B-O15"]["numerator"]
            for ds in ("official", "repository")
        ),
        "actual_scoring_inputs_bound": True,
        "actual_context_recorded_directly": True,
        "component_records": 220,
        "components_contexts_equal": True,
        "actual_runtime_contexts_equal_frozen": not differences,
        "differences_from_frozen": differences,
        "actual_evidence_results": summaries,
        "actual_delivery_quality_gate": no_loss and gain >= 2,
        "actual_delivery_net_gain": gain,
        "max_actual_rerank_pairs": max(r["actual_rerank_pairs"] for r in runtime),
        "all_budget_and_cache_invariants_passed": True,
        "scope": "direct actual candidates/ranking/body and model-input audit; no answer claim",
    }, records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    run = args.run.resolve()
    _, old, v7, chunks, count = prepare(run)
    write_new(
        run / "runtime-audit-protocol.json",
        {
            "implementation_sha256": digest(__file__),
            "inputs": {
                name: digest(run / name)
                for name in (
                    "protocol.json",
                    "latency.jsonl",
                    "score-inputs.jsonl",
                    "components.jsonl",
                    "equivalence.json",
                )
            },
            "prior_results": str(SOURCE.relative_to(ROOT)),
            "posthoc": True,
        },
    )
    result, evidence = audit(run, old, v7, chunks, count)
    with (run / "runtime-evidence-audit.jsonl").open("x") as stream:
        for record in evidence:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    write_new(run / "runtime-integrity-audit.json", result)
    print({k: v for k, v in result.items() if k != "actual_evidence_results"}, flush=True)
    record_operation(
        f"核对v8d完整实际运行记录{run.relative_to(ROOT)}",
        "确保实际重排执行仍交付预期证据，组件计时结果一致且完整",
        f"220真实记录及220组件记录通过；实际交付净增{result['actual_delivery_net_gain']}",
        "实际正文依记录ID及未变渲染器确定性重建；不等于新答案或独立语义审核",
    )


if __name__ == "__main__":
    main()
