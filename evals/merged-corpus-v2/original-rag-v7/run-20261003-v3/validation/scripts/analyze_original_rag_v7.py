"""Audit completed v7 dev experiments without changing gold or invoking models."""

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from benchmark_original_rag_v7 import DATASETS, V4, V6, summaries
from benchmark_selection_v3 import read_rows, write_json
from operation_log import record_operation
from prepare_corpus_v2 import ROOT

from infra_rag.benchmarking import digest
from infra_rag.models import Chunk


def ratio(numerator, denominator):
    return {
        "numerator": numerator,
        "denominator": denominator,
        "value": numerator / denominator if denominator else None,
    }


def analyze(run):
    protocol = json.loads((run / "protocol.json").read_text())
    for name, expected in protocol["inputs"].items():
        if digest(ROOT / name) != expected:
            raise ValueError("Frozen input changed: " + name)
    for name, expected in protocol["implementation"].items():
        if digest(ROOT / name) != expected:
            raise ValueError("Implementation changed: " + name)
    for source in json.loads((V4 / "source-audit.json").read_text())["source_files"]:
        if digest(source["source"]) != source["expected"]:
            raise ValueError("Source changed after experiment")
    for kind in ("base", "context"):
        path = run / f"index-{kind}.json"
        # A fully verified channel replay need not instantiate its index in this run.
        record = (
            json.loads(path.read_text())
            if path.exists()
            else json.loads((V4 / "context-index.json").read_text())
        )
        original = (
            ROOT / protocol["directory"] / "index"
            if kind == "base"
            else ROOT / json.loads((V4 / "context-index.json").read_text())["directory"]
        )
        if digest(original / "index.json") != record["index_sha256"]:
            raise ValueError("Original index changed after experiment")
    corpus = ROOT / protocol["directory"] / "chunks.json"
    chunks = {r["id"]: Chunk(**r) for r in json.loads(corpus.read_text())}
    rows = read_rows(run / "rows.jsonl")
    indexed = {(r["dataset"], r["id"], r["arm"]): r for r in rows}
    if len(indexed) != len(rows):
        raise ValueError("Duplicate experimental rows")
    arms = sorted({r["arm"] for r in rows})
    for arm in arms:
        for ds, n in (("official", 60), ("repository", 50)):
            if sum(r["dataset"] == ds and r["arm"] == arm for r in rows) != n:
                raise ValueError("Incomplete experiment arm: " + arm)
    validity = {
        "candidate_cap_violations": [],
        "baseline_evictions": [],
        "body_or_locator_errors": [],
        "budget_violations": [],
        "selection_count_violations": [],
    }
    failures, deltas, metrics = [], {}, {}
    for r in rows:
        key, arm = (r["dataset"], r["id"]), r["arm"]
        base = indexed[*key, "B"]
        if len(r["candidate_ids"]) > 90 or len(set(r["candidate_ids"])) != r["candidate_count"]:
            validity["candidate_cap_violations"].append([*key, arm])
        if not arm.startswith("R-") and not set(base["candidate_ids"]) <= set(r["candidate_ids"]):
            validity["baseline_evictions"].append([*key, arm])
        context = r["context"]
        if context["used_tokens"] > 1200 or context["used_characters"] > 4000:
            validity["budget_violations"].append([*key, arm])
        if len(context["evidence"]) > 8:
            validity["selection_count_violations"].append([*key, arm])
        for e in context["evidence"]:
            c = chunks[e["chunk_id"]]
            if (
                e["source"] != c.source
                or e["locator"] != c.locator
                or (
                    not c.content.startswith(e["content"])
                    or e["truncated"] != (c.content != e["content"])
                )
            ):
                validity["body_or_locator_errors"].append([*key, arm, c.id])
        if not r["answerable"] or r["delivered"]["complete"]:
            continue
        missing_groups = []
        for group in r["resolved_gold"]["evidence_alternatives"]:
            missing = []
            for choices in group["requirements"]:
                if set(choices) & set(r["candidate_ids"]):
                    continue
                options = []
                for cid in choices:
                    channel_ranks = []
                    for trace in r["recall_traces"]:
                        for channel, ranking in trace.get("channels", {}).items():
                            position = next(
                                (x["rank"] for x in ranking["ranking"] if x["chunk_id"] == cid),
                                None,
                            )
                            channel_ranks.append(
                                {"channel": channel, "query": trace.get("query"), "rank": position}
                            )
                    c = chunks[cid]
                    options.append(
                        {
                            "chunk_id": cid,
                            "source": c.source,
                            "locator": c.locator,
                            "body": c.content,
                            "channel_ranks": channel_ranks,
                            "source_found": any(
                                chunks[x].source == c.source for x in r["candidate_ids"]
                            ),
                            "parent_found": any(
                                (chunks[x].source, chunks[x].parent_id) == (c.source, c.parent_id)
                                for x in r["candidate_ids"]
                            ),
                        }
                    )
                missing.append(options)
            missing_groups.append({"group": group.get("id"), "missing_requirements": missing})
        failures.append(
            {
                "dataset": key[0],
                "id": key[1],
                "arm": arm,
                "query": r["query"],
                "group_id": r["group_id"],
                "failure_stage": "selection_or_budget"
                if r["candidate_complete"]
                else "candidate_recall",
                "missing_groups": missing_groups,
                "delivered": r["delivered"],
                "selected_ids": r["selected_ids"],
            }
        )
    summary = summaries(rows)
    for arm in arms:
        for ds in DATASETS:
            selected = [
                r for r in rows if r["dataset"] == ds and r["arm"] == arm and r["answerable"]
            ]
            stats = summary[f"{ds}:{arm}"]
            metrics[f"{ds}:{arm}"] = {
                "candidate_complete_rate": ratio(stats["candidate_complete"], stats["n"]),
                "top5_complete_rate": ratio(stats["top5_complete"], stats["n"]),
                "evidence_delivery_rate": ratio(stats["delivered_complete"], stats["n"]),
                "candidate_complete_delivery_failed": sum(
                    r["candidate_complete"] and not r["delivered"]["complete"] for r in selected
                ),
                "candidate_incomplete_delivery_failed": sum(
                    not r["candidate_complete"] and not r["delivered"]["complete"] for r in selected
                ),
                "prompt_overhead_tokens": [
                    r["answer_service_evidence_serialization"]["overhead_tokens_vs_packer"]
                    for r in selected
                ],
                "truncated_evidence_count": sum(
                    e["truncated"] for r in selected for e in r["context"]["evidence"]
                ),
            }
            changes = {}
            for metric in ("candidate_complete", "top5_complete", "delivered"):
                recovered, lost = [], []
                for r in selected:
                    base = indexed[ds, r["id"], "B"]
                    before = base[metric]["complete"] if metric == "delivered" else base[metric]
                    after = r[metric]["complete"] if metric == "delivered" else r[metric]
                    if after and not before:
                        recovered.append(r["id"])
                    if before and not after:
                        lost.append(r["id"])
                changes[metric] = {
                    "recovered": recovered,
                    "lost": lost,
                    "net_gain": len(recovered) - len(lost),
                }
            deltas[f"{ds}:{arm}"] = changes
    # Accounting entries are cumulative checkpoints within each process invocation.
    # Actual inference input records are append-only, so use them as the primary total.
    inference = read_rows(run / "score-inputs.jsonl")
    accounting = read_rows(run / "accounting.jsonl")
    latest = accounting[-1] if accounting else {}
    all_scores = json.loads((run / "rerank-scores.json").read_text())
    frozen_scores = json.loads((V4 / "rerank-scores.json").read_text())
    versions = []
    for r in rows:
        if not r["answerable"]:
            continue
        expected = defaultdict(set)
        for group in r["resolved_gold"]["evidence_alternatives"]:
            for options in group["requirements"]:
                for cid in options:
                    c = chunks[cid]
                    if c.metadata.get("product") and c.metadata.get("release"):
                        expected[c.metadata["product"]].add(c.metadata["release"])
        for e in r["context"]["evidence"]:
            meta = e["metadata"]
            product, release = meta.get("product"), meta.get("release")
            if product in expected and release and release not in expected[product]:
                versions.append(
                    {
                        "dataset": r["dataset"],
                        "id": r["id"],
                        "arm": r["arm"],
                        "chunk_id": e["chunk_id"],
                        "product": product,
                        "delivered_release": release,
                        "gold_releases": sorted(expected[product]),
                        "status": "scope_mismatch_pending_independent_review",
                        "numeric_version_mismatch": bool(
                            re.fullmatch(r"v?\d+(?:\.\d+){1,2}", release)
                            and all(
                                re.fullmatch(r"v?\d+(?:\.\d+){1,2}", v) for v in expected[product]
                            )
                        ),
                    }
                )
    old_manifest = json.loads((V6 / "protocol.json").read_text())
    if digest(corpus) != old_manifest["chunks_sha256"]:
        raise ValueError("Original corpus changed after experiment")
    audit = {
        "complete_arms": arms,
        "rows": len(rows),
        "metrics": metrics,
        "paired_deltas": deltas,
        "failures": failures,
        "validity": validity,
        "potential_version_scope_mismatches": versions,
        "numeric_version_mismatch_count": sum(v["numeric_version_mismatch"] for v in versions),
        "historical_scope_flags_are_not_verified_version_errors": True,
        "new_rerank_pairs_recorded": sum(len(r["pairs"]) for r in inference),
        "new_unique_rerank_cache_entries": len(set(all_scores) - set(frozen_scores)),
        "latest_cumulative_invocation_checkpoint": latest,
        "generation_api_calls": 0,
        "label_changes": 0,
        "holdout_test_read": False,
        "independent_review": "pending",
    }
    write_json(run / "failure-deltas.json", audit)
    if any(validity.values()):
        raise ValueError("Experiment invariants failed: " + json.dumps(validity))
    record_operation(
        "审核原有RAG v7逐题得失与实验不变量",
        "区分真实候选缺失与选择预算失败",
        f"{len(rows)}条记录；所有已运行配置完整；原文/定位/预算/候选保留检查通过",
        "替代标签及版本范围保持独立审核pending，不修改gold",
    )
    return {"rows": len(rows), "validity": validity, "metrics": metrics}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.run.resolve())
    print(json.dumps({"rows": result["rows"], "validity": result["validity"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
