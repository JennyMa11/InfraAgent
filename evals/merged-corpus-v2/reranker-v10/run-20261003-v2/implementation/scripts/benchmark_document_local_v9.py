"""Frozen dev controls for document-local recall on the adopted RAG."""

import argparse
import copy
import json
import shutil
from functools import lru_cache
from pathlib import Path
from time import perf_counter

from benchmark_budget_search_v8 import (
    DATASETS,
    PRIOR,
    append,
    choose,
    read_rows,
    select_winner,
    summarize,
)
from benchmark_original_rag_v7 import Engine
from operation_log import record_operation
from prepare_corpus_v2 import ROOT

from infra_rag.benchmarking import digest, span_coverage, write_new
from infra_rag.document_local import DocumentLocalBM25
from infra_rag.evaluation import evidence_metrics
from infra_rag.models import Chunk
from infra_rag.offline_evaluation import latency_summary
from infra_rag.paired_statistics import holm, paired_statistics
from infra_rag.recall_experiments import score_bundle

PLAN = ROOT / "evals/merged-corpus-v2/document-local-v9/experiment-plan.md"
POOLS = ("B", "T", "Doc")
METHODS = ("O15", "X30")


def prepare(run):
    manifest = json.loads((PRIOR / "artifacts-manifest.json").read_text())["files"]
    parent = json.loads((PRIOR / "protocol.json").read_text())
    inputs = {}
    for name in ("protocol.json", "rows.jsonl", "label-review-pending.json"):
        path = PRIOR / name
        if digest(path) != manifest[name]:
            raise ValueError("Changed v7 input: " + name)
        inputs[str(path.relative_to(ROOT))] = digest(path)
    for name, expected in parent["inputs"].items():
        if digest(ROOT / name) != expected:
            raise ValueError("Changed source input: " + name)
        inputs[name] = expected
    audit_path = ROOT / "evals/merged-corpus-v2/recall-delivery-v4/run-20261002/source-audit.json"
    for record in json.loads(audit_path.read_text())["source_files"]:
        if digest(record["source"]) != record["expected"]:
            raise ValueError("Changed source body")
    for kind in ("embedding", "reranker"):
        model = parent["models"][kind]
        for name, expected in model["files"].items():
            if digest(Path(model["path"]) / name) != expected:
                raise ValueError("Changed model")
    corpus = ROOT / parent["directory"] / "chunks.json"
    chunks = {r["id"]: Chunk(**r) for r in json.loads(corpus.read_text())}
    references = {}
    for row in read_rows(PRIOR / "rows.jsonl"):
        if row["arm"] in {"B", "T"}:
            key = row["dataset"], row["id"], row["arm"]
            if key in references:
                raise ValueError("Duplicate reference")
            references[key] = row
    if len(references) != 220:
        raise ValueError("Expected 220 reference rows")
    implementation = {
        str(p.relative_to(ROOT)): digest(p)
        for p in [
            *sorted((ROOT / "src/infra_rag").glob("*.py")),
            Path(__file__),
            ROOT / "scripts/benchmark_budget_search_v8.py",
            ROOT / "scripts/benchmark_original_rag_v7.py",
            ROOT / "scripts/prepare_corpus_v2.py",
            ROOT / "scripts/operation_log.py",
        ]
    }
    protocol = {
        "kind": "document_local_v9_dev_only",
        "pools": list(POOLS),
        "methods": list(METHODS),
        "expected_rows": 660,
        "inputs": inputs,
        "implementation": implementation,
        "models": parent["models"],
        "directory": parent["directory"],
        "plan_sha256": digest(PLAN),
        "scope_top_k": 10,
        "scope_document_cap": 5,
        "supplement_cap": 30,
        "candidate_cap": 90,
        "token_budget": 1200,
        "char_budget": 4000,
        "selected_cap": 8,
        "seed": 42,
        "bootstrap_samples": 10000,
        "dev_gain_min": 2,
        "latency_ratio_cap": 1.5,
        "independent_review": "pending",
        "generation_api_calls": 0,
        "default_changed": False,
        "holdout_test_read": False,
        "reuse_run": None,
    }
    if (run / "protocol.json").exists():
        if json.loads((run / "protocol.json").read_text()) != protocol:
            raise ValueError("Changed protocol; use a new directory")
    else:
        run.mkdir(parents=True, exist_ok=False)
        write_new(run / "protocol.json", protocol)
        shutil.copyfile(PLAN, run / "experiment-plan.md")
        shutil.copyfile(PRIOR / "label-review-pending.json", run / "label-review-pending.json")
        for name in implementation:
            dest = run / "implementation" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
        write_new(
            run / "case-manifest.json",
            [{"dataset": ds, "id": cid} for ds, cid, pool in references if pool == "B"],
        )
    from transformers import AutoTokenizer

    path = Path(parent["models"]["embedding"]["path"])
    options = json.loads((path / "sentence_bert_config.json").read_text())
    tokenizer = AutoTokenizer.from_pretrained(
        path, local_files_only=True, do_lower_case=options["do_lower_case"]
    )

    @lru_cache(maxsize=32768)
    def count(text):
        return len(tokenizer.encode(text, add_special_tokens=False))

    return protocol, references, chunks, count


def evaluate(
    source,
    pool,
    bundle,
    chunks,
    count,
    method,
    local_trace=None,
    *,
    prepared=None,
    verify_reference=False,
):
    row = copy.deepcopy(source)
    row.update(arm=pool, ranked_hits=bundle["hits"], scoring_query=bundle["scoring_query"])
    chosen, context, trace = (
        prepared if prepared is not None else choose(row, chunks, count, method)
    )
    positions = {cid: i for i, cid in enumerate(chunks)}
    for evidence in context["evidence"]:
        original = chunks[evidence["chunk_id"]]
        evidence["source_position"] = positions[original.id]
        if evidence["source"] != original.source or evidence["locator"] != original.locator:
            raise ValueError("Evidence source changed")
        if not original.content.startswith(evidence["content"]):
            raise ValueError("Evidence not original prefix")
        if "```" in original.content and evidence["content"] != original.content:
            raise ValueError("Partial code")
    if verify_reference and pool in {"B", "T"} and method == "O15" and context != source["context"]:
        raise ValueError("Reference context changed")
    if context["used_tokens"] > 1200 or context["used_characters"] > 4000:
        raise ValueError("Body budget exceeded")
    if len(context["evidence"]) > 8:
        raise ValueError("Segment budget exceeded")
    ids = [h["chunk_id"] for h in bundle["hits"]]
    if len(ids) != len(set(ids)) or len(ids) > 90:
        raise ValueError("Candidate budget or identity violated")
    gold = row["resolved_gold"] if row["answerable"] else None
    metric = evidence_metrics(ids, gold, max(1, len(ids))) if gold else None
    row.update(
        arm=f"{pool}-{method}",
        pool=pool,
        method=method,
        candidate_ids=ids,
        candidate_count=len(ids),
        candidate_complete=metric["complete_evidence_hit"] if metric else None,
        candidate_coverage=metric["evidence_coverage"] if metric else None,
        top5_complete=evidence_metrics(ids, gold, 5)["complete_evidence_hit"] if gold else None,
        selected_ids=[h.chunk.id for h in chosen],
        context=context,
        packing_trace=trace,
        delivered=span_coverage(
            context["evidence"],
            {**row, "evidence_alternatives": gold["evidence_alternatives"] if gold else []},
        ),
        local_trace=local_trace,
        answer_correctness=None,
    )
    wire = "\n\n".join(
        f"[{e['citation_id']}] 来源：{e['locator']}\n{e['content']}" for e in context["evidence"]
    )
    row["answer_service_evidence_serialization"] = {
        "text": wire,
        "tokens": count(wire),
        "characters": len(wire),
        "overhead_tokens_vs_packer": count(wire) - context["used_tokens"],
        "not_full_prompt_or_generation_usage": True,
    }
    return row


def local_bundle(index, engine, base, query, *, cached):
    pool, trace = index.supplement(base, query)
    bundle = score_bundle(
        pool,
        query,
        engine.chunks,
        engine.model,
        engine.infer,
        engine.scores if cached else {},
        base,
    )
    return bundle, trace


def quality(run, protocol, references, chunks, count):
    engine, index = Engine(run, protocol, chunks), DocumentLocalBM25(list(chunks.values()))
    done = {(r["dataset"], r["id"], r["arm"]) for r in read_rows(run / "rows.jsonl")}
    cases = [r for key, r in references.items() if key[2] == "B"]
    for i, base in enumerate(cases):
        for pool in POOLS:
            if all((base["dataset"], base["id"], f"{pool}-{m}") in done for m in METHODS):
                continue
            source = references[base["dataset"], base["id"], pool if pool != "Doc" else "B"]
            trace = None
            if pool == "Doc":
                bundle, trace = local_bundle(
                    index, engine, base["ranked_hits"], base["scoring_query"], cached=True
                )
            else:
                bundle = {"hits": source["ranked_hits"], "scoring_query": source["scoring_query"]}
            for method in METHODS:
                if (base["dataset"], base["id"], f"{pool}-{method}") in done:
                    continue
                count.cache_clear()
                row = evaluate(
                    source, pool, bundle, chunks, count, method, trace, verify_reference=True
                )
                append(run / "rows.jsonl", row)
        engine.save()
        if i % 10 == 0:
            print("quality", i + 1, 110, flush=True)


def quality_report(run, references):
    rows = read_rows(run / "rows.jsonl")
    expected = {
        (ds, cid, f"{pool}-{method}")
        for ds, cid, arm in references
        if arm == "B"
        for pool in POOLS
        for method in METHODS
    }
    actual = [(r["dataset"], r["id"], r["arm"]) for r in rows]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError("Incomplete quality outputs")
    summary, stats = summarize(rows), {}
    for ds in DATASETS:
        pairs = [(f"B-{m}", f"{p}-{m}") for m in METHODS for p in ("T", "Doc")]
        for left, right in [*pairs, ("Doc-O15", "Doc-X30")]:
            key = f"{ds}:{right}_vs_{left}"
            stats[key] = paired_statistics(
                [r for r in rows if r["dataset"] == ds and r["arm"] == left],
                [r for r in rows if r["dataset"] == ds and r["arm"] == right],
            )
    for key, adjusted in holm({k: v["cluster_permutation_p"] for k, v in stats.items()}).items():
        stats[key]["holm_p"] = adjusted
    restricted = {
        k: v for k, v in summary.items() if k.split(":")[1] in {"B-O15", "Doc-O15", "Doc-X30"}
    }
    winner = select_winner(restricted)
    write_new(run / "quality-summary.json", {"results": summary, "statistics": stats})
    write_new(run / "quality-selection.json", {"winner": winner, "not_adoption": True})
    print("quality winner", winner, flush=True)
    for key, value in summary.items():
        print(key, value["candidate_complete"], value["delivered_complete"], flush=True)


def runtime(run, protocol, references, chunks, count):
    winner = json.loads((run / "quality-selection.json").read_text())["winner"]
    if winner is None:
        raise ValueError("No quality winner; stop per protocol")
    engine, index = Engine(run, protocol, chunks), DocumentLocalBM25(list(chunks.values()))
    rows = [r for key, r in references.items() if key[2] == "B"]

    def execute(row, arm):
        baseline = engine.bundle(
            "B",
            {"scoring_query": row["scoring_query"], "hits": row["ranked_hits"]},
            row,
            [],
            cached=False,
        )
        pool, method = arm.split("-")
        trace = None
        if pool == "Doc":
            baseline, trace = local_bundle(
                index, engine, baseline["hits"], row["scoring_query"], cached=False
            )
        prepared = choose({**row, "ranked_hits": baseline["hits"]}, chunks, count, method)
        return baseline, trace, prepared

    for arm in ("B-O15", winner):
        execute(rows[0], arm)
    done = {(r["dataset"], r["id"], r["arm"]) for r in read_rows(run / "runtime.jsonl")}
    for i, row in enumerate(rows):
        arms = ("B-O15", winner) if i % 2 == 0 else (winner, "B-O15")
        for arm in arms:
            if (row["dataset"], row["id"], arm) in done:
                continue
            count.cache_clear()
            before, started = engine.new_pairs, perf_counter()
            bundle, trace, prepared = execute(row, arm)
            elapsed = (perf_counter() - started) * 1000
            actual_pairs = engine.new_pairs - before
            if actual_pairs > 90:
                raise ValueError("Actual cumulative pairs exceeded")
            pool, method = arm.split("-")
            result = evaluate(row, pool, bundle, chunks, count, method, trace, prepared=prepared)
            result.update(
                latency_ms=elapsed, actual_rerank_pairs=actual_pairs, result_cache_enabled=False
            )
            append(run / "runtime.jsonl", result)
        engine.save()
        print("runtime", i + 1, 110, flush=True)


def report(run):
    selection = json.loads((run / "quality-selection.json").read_text())["winner"]
    decision = {
        "quality_winner": selection,
        "quality_gate": selection is not None,
        "latency_gate": None,
        "actual_delivery_quality_gate": None,
        "independent_review_gate": None,
        "adoption_allowed": False,
        "default_changed": False,
        "holdout_test_read": False,
        "generation_api_calls": 0,
    }
    if selection is not None:
        rows = read_rows(run / "runtime.jsonl")
        if len(rows) != 220 or len({(r["dataset"], r["id"], r["arm"]) for r in rows}) != 220:
            raise ValueError("Incomplete runtime outputs")
        actual = summarize(rows)
        decision["actual_delivery_quality_gate"] = select_winner(actual) == selection
        times = {
            arm: {"n": 110, **latency_summary([r["latency_ms"] for r in rows if r["arm"] == arm])}
            for arm in ("B-O15", selection)
        }
        ratio = times[selection]["p95_ms"] / times["B-O15"]["p95_ms"]
        decision.update(
            warm_latency=times, p95_ratio=ratio, latency_gate=ratio <= 1.5, actual_results=actual
        )
    else:
        decision["stop_reason"] = (
            "No Doc configuration passed frozen quality gate; no performance extension"
        )
    write_new(run / "decision.json", decision)
    write_new(
        run / "artifacts-manifest.json",
        {
            "files": {
                str(p.relative_to(run)): digest(p)
                for p in sorted(run.rglob("*"))
                if p.is_file() and p.name not in {"artifacts-manifest.json", "execution.log"}
            }
        },
    )
    print(json.dumps(decision, ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--phase", required=True, choices=("quality", "quality-report", "runtime", "report")
    )
    args = parser.parse_args()
    run = args.output.resolve()
    protocol, references, chunks, count = prepare(run)
    if args.phase == "quality":
        quality(run, protocol, references, chunks, count)
    elif args.phase == "quality-report":
        quality_report(run, references)
    elif args.phase == "runtime":
        runtime(run, protocol, references, chunks, count)
    else:
        report(run)
    record_operation(
        f"完成v9阶段{args.phase}，{run.relative_to(ROOT)}",
        "验证文档内定位的候选与交付增量",
        "对应阶段产物已保存，沿用冻结门槛",
        "独立人工审核pending；未采用默认配置",
    )


if __name__ == "__main__":
    main()
