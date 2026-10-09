"""Frozen dev experiments implementing E0/E1/E2 of the bottleneck analysis."""

import argparse
import copy
import json
import shutil
from functools import lru_cache
from pathlib import Path
from time import perf_counter

from benchmark_original_rag_v7 import Engine
from operation_log import record_operation
from prepare_corpus_v2 import ROOT

from infra_rag.benchmarking import digest, span_coverage, write_new
from infra_rag.budget_ablation import AblationPacker
from infra_rag.budget_evidence import is_heading
from infra_rag.budget_search import BudgetSearch, full_block_oracle
from infra_rag.models import Chunk, Hit
from infra_rag.offline_evaluation import latency_summary
from infra_rag.paired_statistics import holm, paired_statistics

PRIOR = ROOT / "evals/merged-corpus-v2/original-rag-v7/run-20261003-v3"
PLAN = ROOT / "evals/merged-corpus-v2/budget-search-v8/experiment-plan.md"
POOLS = ("B", "T", "Ladj")
METHODS = ("O15", "O30", "U30", "X30")
DATASETS = ("official", "repository")


def read_rows(path):
    if not path.exists():
        return []
    with path.open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def append(path, value):
    with path.open("a") as stream:
        stream.write(json.dumps(value, ensure_ascii=False) + "\n")


def prepare(run):
    archive = json.loads((PRIOR / "artifacts-manifest.json").read_text())["files"]
    inputs = {}
    for name in ("protocol.json", "rows.jsonl", "label-review-pending.json", "summary.json"):
        path = PRIOR / name
        if digest(path) != archive[name]:
            raise ValueError("Changed prior input: " + name)
        inputs[str(path.relative_to(ROOT))] = digest(path)
    prior = json.loads((PRIOR / "protocol.json").read_text())
    corpus = ROOT / prior["directory"] / "chunks.json"
    if digest(corpus) != prior["inputs"][str(corpus.relative_to(ROOT))]:
        raise ValueError("Changed chunks")
    inputs[str(corpus.relative_to(ROOT))] = digest(corpus)
    chunks = {r["id"]: Chunk(**r) for r in json.loads(corpus.read_text())}
    rows = {}
    with (PRIOR / "rows.jsonl").open() as stream:
        for line in stream:
            row = json.loads(line)
            if row["arm"] in POOLS:
                key = row["dataset"], row["id"], row["arm"]
                if key in rows:
                    raise ValueError("Duplicate frozen row")
                rows[key] = row
    if len(rows) != 330:
        raise ValueError("Expected three pools times 110 cases")
    for key, row in rows.items():
        if not set(rows[*key[:2], "B"]["candidate_ids"]) <= set(row["candidate_ids"]):
            raise ValueError("Baseline candidates not retained")
        if len(row["candidate_ids"]) > 90:
            raise ValueError("Candidate cap exceeded")
    for kind in ("embedding", "reranker"):
        model = prior["models"][kind]
        for name, expected in model["files"].items():
            if digest(Path(model["path"]) / name) != expected:
                raise ValueError("Changed model file")
    source_audit = ROOT / "evals/merged-corpus-v2/recall-delivery-v4/run-20261002/source-audit.json"
    audit = json.loads(source_audit.read_text())
    for item in audit["source_files"]:
        if digest(item["source"]) != item["expected"]:
            raise ValueError("Changed source: " + item["source"])
    inputs[str(source_audit.relative_to(ROOT))] = digest(source_audit)
    implementation = {
        str(p.relative_to(ROOT)): digest(p)
        for p in [
            *sorted((ROOT / "src/infra_rag").glob("*.py")),
            Path(__file__),
            ROOT / "scripts/benchmark_original_rag_v7.py",
            ROOT / "scripts/operation_log.py",
            ROOT / "scripts/prepare_corpus_v2.py",
        ]
    }
    protocol = {
        "kind": "budget_search_v8_dev_only",
        "pools": POOLS,
        "methods": METHODS,
        "expected_rows": 1320,
        "inputs": inputs,
        "implementation": implementation,
        "models": prior["models"],
        "directory": prior["directory"],
        "plan_sha256": digest(PLAN),
        "token_budget": 1200,
        "char_budget": 4000,
        "candidate_cap": 90,
        "selected_cap": 8,
        "exchange_rounds": 2,
        "exchange_proposal_cap": 5000,
        "oracle_combination_cap": 100000,
        "dev_gain_min": 2,
        "latency_ratio_cap": 1.5,
        "bootstrap_samples": 10000,
        "seed": 42,
        "independent_review": "pending",
        "generation_api_calls": 0,
        "default_changed": False,
        "holdout_test_read": False,
        "reuse_run": None,
    }
    encoded = json.loads(json.dumps(protocol))
    if (run / "protocol.json").exists():
        if json.loads((run / "protocol.json").read_text()) != encoded:
            raise ValueError("Protocol changed; use a new directory")
    else:
        run.mkdir(parents=True, exist_ok=False)
        write_new(run / "protocol.json", protocol)
        shutil.copyfile(PLAN, run / "experiment-plan.md")
        for name in implementation:
            dest = run / "implementation" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
        shutil.copyfile(PRIOR / "label-review-pending.json", run / "label-review-pending.json")
    from transformers import AutoTokenizer

    model = Path(prior["models"]["embedding"]["path"])
    options = json.loads((model / "sentence_bert_config.json").read_text())
    tokenizer = AutoTokenizer.from_pretrained(
        model, local_files_only=True, do_lower_case=options["do_lower_case"]
    )

    @lru_cache(maxsize=32768)
    def count(text):
        return len(tokenizer.encode(text, add_special_tokens=False))

    return protocol, rows, chunks, count


def choose(row, chunks, count, method):
    hits = [
        Hit(chunks[h["chunk_id"]], h["score"], rerank_score=h["rerank_score"])
        for h in row["ranked_hits"]
    ]
    query = row["query"] + "\n" + row["scoring_query"]
    if method.startswith("O"):
        packer = AblationPacker(
            hits, {"evidence": []}, chunks, query, count, frontier_limit=int(method[1:])
        )
        return packer.pack(limit=8, length_power=0.0, protect=1, neighbors=False)
    return BudgetSearch(hits, query, count).pack(policy="greedy" if method == "U30" else "exchange")


def output(row, chunks, count, method):
    chosen, context, trace = choose(row, chunks, count, method)
    result = {
        k: copy.deepcopy(row[k])
        for k in (
            "id",
            "dataset",
            "query",
            "group_id",
            "answerable",
            "resolved_gold",
            "required_points",
            "candidate_ids",
            "candidate_count",
            "candidate_complete",
            "candidate_coverage",
            "top5_complete",
            "ranked_hits",
            "scoring_query",
        )
    }
    positions = {cid: i for i, cid in enumerate(chunks)}
    for evidence in context["evidence"]:
        evidence["source_position"] = positions[evidence["chunk_id"]]
        chunk = chunks[evidence["chunk_id"]]
        if evidence["source"] != chunk.source or evidence["locator"] != chunk.locator:
            raise ValueError("Changed source or locator")
        if not chunk.content.startswith(evidence["content"]):
            raise ValueError("Evidence not an original prefix")
        if "```" in chunk.content and evidence["content"] != chunk.content:
            raise ValueError("Partial fenced code")
    if context["used_tokens"] > 1200 or context["used_characters"] > 4000:
        raise ValueError("Exceeded context budget")
    if len(context["evidence"]) > 8:
        raise ValueError("Exceeded selected cap")
    wire = "\n\n".join(
        f"[{e['citation_id']}] 来源：{e['locator']}\n{e['content']}" for e in context["evidence"]
    )
    result.update(
        pool=row["arm"],
        method=method,
        arm=f"{row['arm']}-{method}",
        selected_ids=[hit.chunk.id for hit in chosen],
        context=context,
        packing_trace=trace,
        delivered=span_coverage(
            context["evidence"],
            {
                **row,
                "evidence_alternatives": row["resolved_gold"]["evidence_alternatives"]
                if row["answerable"]
                else [],
            },
        ),
        answer_service_evidence_serialization={
            "text": wire,
            "tokens": count(wire),
            "characters": len(wire),
            "overhead_tokens_vs_packer": count(wire) - context["used_tokens"],
            "not_full_prompt_or_generation_usage": True,
        },
    )
    if method == "O15" and context != row["context"]:
        raise ValueError("Frozen O15 context differs")
    return result


def replay(run, rows, chunks, count):
    done = {(r["dataset"], r["id"], r["arm"]) for r in read_rows(run / "rows.jsonl")}
    for i, (key, row) in enumerate(rows.items(), 1):
        count.cache_clear()
        for method in METHODS:
            arm = f"{key[2]}-{method}"
            if (*key[:2], arm) in done:
                continue
            started = perf_counter()
            result = output(row, chunks, count, method)
            result["cached_component_replay_ms"] = (perf_counter() - started) * 1000
            append(run / "rows.jsonl", result)
        if i % 10 == 0:
            print("replay", i, len(rows), flush=True)


def oracle(run, rows, chunks, count):
    done = {(r["dataset"], r["id"], r["pool"]) for r in read_rows(run / "oracle.jsonl")}
    for key, row in rows.items():
        if not row["answerable"] or key in done:
            continue
        count.cache_clear()
        measures = {}
        for frontier in (15, 30, 90):
            ids = [cid for cid in row["candidate_ids"][:frontier] if not is_heading(chunks[cid])]
            for protect in (False, True):
                measure = full_block_oracle(
                    ids, row["resolved_gold"], chunks, count, protect_first=protect
                )
                witness = measure["best_full_block_witness"]
                if witness:
                    evidence = [
                        {
                            "chunk_id": cid,
                            "source": chunks[cid].source,
                            "content": chunks[cid].content,
                            "locator": chunks[cid].locator,
                            "source_position": list(chunks).index(cid),
                        }
                        for cid in witness["ids"]
                    ]
                    measure["witness_span_coverage"] = span_coverage(
                        evidence,
                        {
                            **row,
                            "evidence_alternatives": row["resolved_gold"]["evidence_alternatives"],
                        },
                    )
                measures[f"F{frontier}-P{int(protect)}"] = measure
        append(
            run / "oracle.jsonl",
            {
                "dataset": key[0],
                "id": key[1],
                "pool": key[2],
                "measures": measures,
                "diagnostic_only": True,
            },
        )
    print("oracle complete", flush=True)


def metric(n, denominator):
    return {
        "numerator": n,
        "denominator": denominator,
        "value": n / denominator if denominator else None,
    }


def summarize(rows):
    summary = {}
    for ds in DATASETS:
        for arm in sorted({r["arm"] for r in rows}):
            selected = [r for r in rows if r["dataset"] == ds and r["arm"] == arm]
            positive = [r for r in selected if r["answerable"]]
            n = len(positive)
            summary[f"{ds}:{arm}"] = {
                "runs": len(selected),
                "n": n,
                "candidate_complete": metric(sum(r["candidate_complete"] for r in positive), n),
                "delivered_complete": metric(sum(r["delivered"]["complete"] for r in positive), n),
                "mechanical_coverage": metric(n, n),
                "semantic_review_coverage": metric(0, len(selected)),
                "answer_correctness": None,
                "negative_cases": len(selected) - n,
            }
    return summary


def select_winner(summary):
    candidates = []
    for arm in sorted({key.split(":")[1] for key in summary} - {"B-O15"}):
        no_loss = all(
            summary[f"{ds}:{arm}"][field]["numerator"] >= summary[f"{ds}:B-O15"][field]["numerator"]
            for ds in DATASETS
            for field in ("candidate_complete", "delivered_complete")
        )
        gain = sum(
            summary[f"{ds}:{arm}"]["delivered_complete"]["numerator"]
            - summary[f"{ds}:B-O15"]["delivered_complete"]["numerator"]
            for ds in DATASETS
        )
        if no_loss and gain >= 2:
            candidates.append(
                (
                    arm,
                    gain,
                    summary[f"official:{arm}"]["delivered_complete"]["numerator"],
                    summary[f"repository:{arm}"]["delivered_complete"]["numerator"],
                )
            )
    return min(candidates, key=lambda v: (-v[1], -v[2], -v[3], v[0]))[0] if candidates else None


def quality_report(run):
    rows = read_rows(run / "rows.jsonl")
    keys = {(r["dataset"], r["id"], r["arm"]) for r in rows}
    if len(rows) != 1320 or len(keys) != len(rows):
        raise ValueError("Incomplete or duplicate planned runs")
    summary, stats = summarize(rows), {}
    pvalues = {}
    for ds in DATASETS:
        for pool in POOLS:
            for left, right in (("O15", "O30"), ("O30", "U30"), ("U30", "X30")):
                before = [r for r in rows if r["dataset"] == ds and r["arm"] == f"{pool}-{left}"]
                after = [r for r in rows if r["dataset"] == ds and r["arm"] == f"{pool}-{right}"]
                key = f"{ds}:{pool}:{right}_vs_{left}"
                stats[key] = paired_statistics(before, after)
                pvalues[key] = stats[key]["cluster_permutation_p"]
    for key, value in holm(pvalues).items():
        stats[key]["holm_p"] = value
    winner = select_winner(summary)
    write_new(run / "quality-summary.json", {"results": summary, "statistics": stats})
    write_new(run / "quality-selection.json", {"winner": winner, "not_adoption": True})
    print("quality winner", winner, flush=True)
    for arm in sorted({r["arm"] for r in rows}):
        print(
            arm,
            *(summary[f"{ds}:{arm}"]["delivered_complete"]["numerator"] for ds in DATASETS),
            flush=True,
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=("quality", "latency", "report"), default="quality")
    args = parser.parse_args()
    run = args.output.resolve()
    protocol, rows, chunks, count = prepare(run)
    if args.phase == "quality":
        oracle(run, rows, chunks, count)
        replay(run, rows, chunks, count)
        quality_report(run)
    elif args.phase == "latency":
        latency(run, protocol, rows, chunks, count)
    else:
        report(run)
    record_operation(
        f"执行原有RAG v8 {args.phase}，输出{run.relative_to(ROOT)}",
        "按分析报告开展固定候选前沿与有限交换对照",
        "该阶段完成；gold、历史结果及默认服务未更改",
        "独立审核pending；不读holdout/test，不把证据交付当回答正确率",
    )


def latency(run, protocol, rows, chunks, count):
    winner = json.loads((run / "quality-selection.json").read_text())["winner"]
    if winner is None:
        write_new(run / "latency-status.json", {"status": "not_run_no_quality_eligible_method"})
        return
    # Real queries and scoring, with no query/result score caches. Freeze quality selection first.
    engine = Engine(run, protocol, chunks)
    mappings = {(ds, qid): row for (ds, qid, pool), row in rows.items() if pool == "B"}
    engine.technical = None

    def execute(arm, row):
        pool, method = arm.split("-")
        base = {"scoring_query": row["scoring_query"], "hits": row["ranked_hits"]}
        # T has no facet API dependency. Ladj needs an isolated index of frozen views.
        bundle = engine.bundle(pool, base, row, [], cached=False)
        live = {**row, "ranked_hits": bundle["hits"], "arm": pool}
        return choose(live, chunks, count, method)

    first = next(iter(mappings.values()))
    for arm in ("B-O15", winner):
        execute(arm, first)
    done = {(r["dataset"], r["id"], r["arm"]) for r in read_rows(run / "latency.jsonl")}
    for i, (key, row) in enumerate(mappings.items()):
        order = ("B-O15", winner) if i % 2 == 0 else (winner, "B-O15")
        for arm in order:
            if (*key, arm) in done:
                continue
            count.cache_clear()
            before = engine.new_pairs
            started = perf_counter()
            _, context, trace = execute(arm, row)
            duration = (perf_counter() - started) * 1000
            pairs = engine.new_pairs - before
            if pairs > 90:
                raise ValueError("Exceeded cumulative 90 actual scoring pairs")
            append(
                run / "latency.jsonl",
                {
                    "dataset": key[0],
                    "id": key[1],
                    "arm": arm,
                    "latency_ms": duration,
                    "actual_rerank_pairs": pairs,
                    "selected_ids": [e["chunk_id"] for e in context["evidence"]],
                    "used_tokens": context["used_tokens"],
                    "search_trace": trace,
                    "scope": "warm retrieval+rerank+packing; no translation/generation/init",
                    "result_cache_enabled": False,
                },
            )
        engine.save()
        print("latency", i + 1, len(mappings), flush=True)


def report(run):
    selection = json.loads((run / "quality-selection.json").read_text())
    rows = read_rows(run / "latency.jsonl")
    times = {
        arm: {
            "n": sum(r["arm"] == arm for r in rows),
            **latency_summary([r["latency_ms"] for r in rows if r["arm"] == arm]),
        }
        for arm in {r["arm"] for r in rows}
    }
    winner = selection["winner"]
    latency_pass = (
        None
        if winner is None
        else (
            times.get(winner, {}).get("n") == 110
            and times.get("B-O15", {}).get("n") == 110
            and times[winner]["p95_ms"] <= 1.5 * times["B-O15"]["p95_ms"]
        )
    )
    write_new(
        run / "decision.json",
        {
            "dev_quality_winner": winner,
            "quality_gate": bool(winner),
            "latency_gate": latency_pass,
            "warm_latency": times,
            "independent_review_gate": None,
            "independent_review": "pending",
            "adoption_allowed": False,
            "default_changed": False,
            "confirmation_allowed": False,
            "holdout_test_read": False,
            "generation_api_calls": 0,
        },
    )
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


if __name__ == "__main__":
    main()
