"""Diagnose the original RAG using frozen dev traces and exact lexical ranking only."""

import argparse
import json
from pathlib import Path

from operation_log import record_operation
from prepare_corpus_v2 import ROOT

from infra_rag.benchmarking import digest, write_new
from infra_rag.lexical import BM25Index, query_terms
from infra_rag.models import Chunk
from infra_rag.service import lexical_statistics

V4 = ROOT / "evals/merged-corpus-v2/recall-delivery-v4/run-20261002"
V6 = ROOT / "evals/merged-corpus-v2/budget-ablation-v6/run-20261003"
ROUTING = ROOT / "evals/merged-corpus-v2/routing-v2-20261002"
ARMS = ("B5", "D5", "Q5", "L5", "E5", "LE5")


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def analyze(output):
    if output.exists():
        raise ValueError("Use a new output; never replace frozen results")
    inputs = {}
    for folder, names in (
        (V4, ("protocol.json", "rows.jsonl", "source-audit.json")),
        (V6, ("protocol.json", "rows.jsonl")),
    ):
        manifest = json.loads((folder / "artifacts-manifest.json").read_text())["files"]
        for name in names:
            if digest(folder / name) != manifest[name]:
                raise ValueError("Historical input hash changed")
            inputs[str((folder / name).relative_to(ROOT))] = manifest[name]
    protocol = json.loads((V4 / "protocol.json").read_text())
    routing_rows = ROUTING / "rows.jsonl"
    if digest(routing_rows) != protocol["routing_rows_sha256"]:
        raise ValueError("Original channel traces changed")
    inputs[str(routing_rows.relative_to(ROOT))] = digest(routing_rows)
    corpus = ROOT / protocol["directory"] / "chunks.json"
    v6 = json.loads((V6 / "protocol.json").read_text())
    if digest(corpus) != v6["chunks_sha256"]:
        raise ValueError("Corpus hash changed")
    inputs[str(corpus.relative_to(ROOT))] = digest(corpus)
    for name in (
        "src/infra_rag/lexical.py",
        "src/infra_rag/encoding.py",
        "src/infra_rag/service.py",
    ):
        if digest(ROOT / name) != protocol["implementation"][name]:
            raise ValueError("Lexical implementation differs from frozen baseline")
    chunks = [Chunk(**r) for r in json.loads(corpus.read_text())]
    if any((c.domain, c.modality) != ("infra", "text") for c in chunks):
        raise ValueError("Unexpected corpus filter scope")
    by_id = {c.id: c for c in chunks}
    rows = read_rows(V4 / "rows.jsonl")
    mapping = {(r["id"], r["arm"]): r for r in rows}
    base = [r for r in rows if r["arm"] == "B5" and r["answerable"]]
    if len(base) != 104:
        raise ValueError("Expected original 54/50 positive dev queries")
    routing = {
        r["id"]: r for r in read_rows(ROUTING / "rows.jsonl") if r["arm"] == "processed_global30"
    }
    selected_v6 = [
        r for r in read_rows(V6 / "rows.jsonl") if r["arm"] == "B-k8-l0-p1-n0" and r["answerable"]
    ]
    index = BM25Index(chunks, statistics=lexical_statistics(chunks), query_mode="raw")
    failures = []
    for r in base:
        if r["candidate_complete"]:
            continue
        bundle_path = V4 / "bundles" / r["dataset"] / (r["id"] + ".json")
        manifest = json.loads((V4 / "artifacts-manifest.json").read_text())["files"]
        if digest(bundle_path) != manifest[str(bundle_path.relative_to(V4))]:
            raise ValueError("Candidate bundle changed")
        inputs[str(bundle_path.relative_to(ROOT))] = digest(bundle_path)
        scoring = json.loads(bundle_path.read_text())["B5"]["scoring_query"]
        channels = routing[r["id"]]["diagnostics"]["channels"]
        if set(r["diagnostics"]["candidates"]) != {
            h["chunk_id"] for c in channels.values() for h in c["ranking"]
        }:
            raise ValueError("Baseline candidates are not the two-channel union")
        full = index.search(scoring)
        if [cid for cid, _ in full[:30]] != [h["chunk_id"] for h in channels["bm25"]["ranking"]]:
            raise ValueError("Exact BM25 Top30 reproduction failed")
        ranks = {cid: i + 1 for i, (cid, _) in enumerate(full)}
        missing = []
        candidates = [by_id[cid] for cid in r["diagnostics"]["candidates"]]
        for cid in sorted(set(r["resolved_gold"]["relevant"]) - {c.id for c in candidates}):
            c = by_id[cid]
            channel_ranks = {
                name: next((h["rank"] for h in channel["ranking"] if h["chunk_id"] == cid), None)
                for name, channel in channels.items()
            }
            if any(v is not None for v in channel_ranks.values()):
                raise ValueError("Missing gold was already in a retrieval channel")
            missing.append(
                {
                    "chunk_id": cid,
                    "source": c.source,
                    "locator": c.locator,
                    "heading": c.heading,
                    "body_type": c.metadata.get("body_type"),
                    "body": c.content,
                    "full_bm25_rank": ranks.get(cid),
                    "frozen_top30_channel_ranks": channel_ranks,
                    "same_source_candidates": sum(x.source == c.source for x in candidates),
                    "same_parent_candidates": sum(
                        (x.source, x.parent_id) == (c.source, c.parent_id) for x in candidates
                    ),
                    "query_body_shared_terms": sorted(
                        query_terms(scoring) & query_terms(c.content)
                    ),
                }
            )
        failures.append(
            {
                "id": r["id"],
                "group_id": r["group_id"],
                "dataset": r["dataset"],
                "query": r["query"],
                "scoring_query": scoring,
                "candidate_count": len(candidates),
                "missing_gold": missing,
                "controls_complete": {
                    a: mapping[r["id"], a]["candidate_complete"] for a in ARMS[1:]
                },
                "actual_delivered_evidence": r["context"]["evidence"],
                "required_points": r["required_points"],
            }
        )
    summaries, deltas = {}, {}
    for ds in ("official", "repository"):
        old = [r for r in base if r["dataset"] == ds]
        summaries[ds] = {
            "positive_questions": len(old),
            "baseline_complete_candidates": int(sum(r["candidate_complete"] for r in old)),
            "baseline_top5_complete": int(
                sum(r["at_k"]["5"]["complete_evidence_hit"] for r in old)
            ),
            "baseline_delivery_complete": int(sum(r["delivered"]["complete"] for r in old)),
            "v6_delivery_complete": int(
                sum(r["delivered"]["complete"] for r in selected_v6 if r["dataset"] == ds)
            ),
        }
        for arm in ARMS[1:]:
            new = {
                r["id"]: r
                for r in rows
                if r["arm"] == arm and r["dataset"] == ds and r["answerable"]
            }
            deltas[f"{ds}:{arm}"] = {
                "complete_candidates": int(sum(r["candidate_complete"] for r in new.values())),
                "recovered": [
                    r["id"]
                    for r in old
                    if not r["candidate_complete"] and new[r["id"]]["candidate_complete"]
                ],
                "lost": [
                    r["id"]
                    for r in old
                    if r["candidate_complete"] and not new[r["id"]]["candidate_complete"]
                ],
            }
    counts = {
        "candidate_incomplete_cases": len(failures),
        "missing_unique_chunks": len({g["chunk_id"] for r in failures for g in r["missing_gold"]}),
        "all_missing_gold_sources_already_recalled": sum(
            all(g["same_source_candidates"] > 0 for g in r["missing_gold"]) for r in failures
        ),
        "all_missing_gold_within_bm25_top75": sum(
            all(
                g["full_bm25_rank"] is not None and g["full_bm25_rank"] <= 75
                for g in r["missing_gold"]
            )
            for r in failures
        ),
        "recoverable_by_at_least_one_prior_control": sum(
            any(r["controls_complete"].values()) for r in failures
        ),
        "exact_bm25_top30_reproductions": len(failures),
    }
    source_audit = json.loads((V4 / "source-audit.json").read_text())
    for record in source_audit["source_files"]:
        if digest(record["source"]) != record["expected"]:
            raise ValueError("Source changed")
    output.mkdir(parents=True)
    write_new(
        output / "diagnostics.json",
        {
            "scope": "original RAG frozen dev B baseline; no new research Agent execution",
            "inputs": inputs,
            "summary": summaries,
            "counts": counts,
            "control_deltas": deltas,
            "failure_cases": failures,
            "new_model_api_requests": 0,
            "new_embedding_calls": 0,
            "new_reranker_calls": 0,
            "index_writes": 0,
            "holdout_read": False,
            "label_changes": 0,
            "lexical_full_rank_is_post_run_diagnostic": True,
            "source_hashes_verified": len(source_audit["source_files"]),
            "implementation_sha256": digest(Path(__file__)),
        },
    )
    script_source = Path(__file__).read_bytes()
    (output / "analysis-script.py").write_bytes(script_source)
    record_operation(
        "完成原RAG候选召回原因机械诊断",
        "核对Top30入口、语料位置和旧补召回对照",
        json.dumps({"summary": summaries, "counts": counts}, ensure_ascii=False),
        "全量BM25位置为事后诊断；稀疏gold可能漏计替代证据，不改标签，不判答案正确率",
    )
    return {"summary": summaries, "counts": counts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(analyze(args.output.resolve()), ensure_ascii=False))


if __name__ == "__main__":
    main()
