"""Verify identical evidence choices before measuring pruned exchange search."""

import argparse
import importlib.util
import json
import shutil
from functools import lru_cache
from pathlib import Path
from time import perf_counter

from benchmark_budget_search_v8 import choose, output, read_rows
from benchmark_original_rag_v7 import Engine
from operation_log import record_operation
from prepare_corpus_v2 import ROOT, configuration

from infra_rag.benchmarking import canonical_hash, digest, write_new
from infra_rag.models import Chunk, Hit
from infra_rag.offline_evaluation import latency_summary
from infra_rag.original_rag_experiments import adjacent_views
from infra_rag.service import RetrievalService

SOURCE = ROOT / "evals/merged-corpus-v2/budget-search-v8/run-20261003"
V7 = ROOT / "evals/merged-corpus-v2/original-rag-v7/run-20261003-v3"
PLAN = ROOT / "evals/merged-corpus-v2/budget-search-v8/runtime-optimization-plan.md"


def append(path, row):
    with path.open("a") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def prepare(run):
    manifest = json.loads((SOURCE / "artifacts-manifest.json").read_text())["files"]
    for name, expected in manifest.items():
        if digest(SOURCE / name) != expected:
            raise ValueError("Frozen v8 changed: " + name)
    parent = json.loads((SOURCE / "protocol.json").read_text())
    for name, expected in parent["inputs"].items():
        if digest(ROOT / name) != expected:
            raise ValueError("Changed original input: " + name)
    for kind in ("embedding", "reranker"):
        model = parent["models"][kind]
        for name, expected in model["files"].items():
            if digest(Path(model["path"]) / name) != expected:
                raise ValueError("Changed model: " + name)
    source_audit = json.loads(
        (
            ROOT / "evals/merged-corpus-v2/recall-delivery-v4/run-20261002/source-audit.json"
        ).read_text()
    )
    for record in source_audit["source_files"]:
        if digest(record["source"]) != record["expected"]:
            raise ValueError("Changed source file")
    corpus = ROOT / parent["directory"] / "chunks.json"
    chunks = {r["id"]: Chunk(**r) for r in json.loads(corpus.read_text())}
    old = read_rows(SOURCE / "rows.jsonl")
    v7 = {}
    with (V7 / "rows.jsonl").open() as stream:
        for line in stream:
            row = json.loads(line)
            if row["arm"] in {"B", "T", "Ladj"}:
                v7[row["dataset"], row["id"], row["arm"]] = row
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
        "kind": "v8b_identical_selection_runtime_optimization",
        "inputs": {
            **parent["inputs"],
            str((SOURCE / "artifacts-manifest.json").relative_to(ROOT)): digest(
                SOURCE / "artifacts-manifest.json"
            ),
        },
        "models": parent["models"],
        "directory": parent["directory"],
        "implementation": implementation,
        "plan_sha256": digest(PLAN),
        "quality_inheritance_requires_context_equivalence": 330,
        "runtime_arms": ["B-O15", "Ladj-X30"],
        "runtime_expected_records": 220,
        "component_expected_records": 220,
        "latency_ratio_cap": 1.5,
        "context_tokens": 1200,
        "context_chars": 4000,
        "candidate_cap": 90,
        "generation_api_calls": 0,
        "independent_review": "pending",
        "holdout_test_read": False,
        "default_changed": False,
        "reuse_run": None,
    }
    if (run / "protocol.json").exists():
        if json.loads((run / "protocol.json").read_text()) != protocol:
            raise ValueError("Changed protocol; use a new directory")
    else:
        run.mkdir(parents=True, exist_ok=False)
        write_new(run / "protocol.json", protocol)
        shutil.copyfile(PLAN, run / "experiment-plan.md")
        for name in implementation:
            dest = run / "implementation" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
    from transformers import AutoTokenizer

    path = Path(parent["models"]["embedding"]["path"])
    options = json.loads((path / "sentence_bert_config.json").read_text())
    tokenizer = AutoTokenizer.from_pretrained(
        path, local_files_only=True, do_lower_case=options["do_lower_case"]
    )

    @lru_cache(maxsize=32768)
    def count(text):
        return len(tokenizer.encode(text, add_special_tokens=False))

    return protocol, old, v7, chunks, count


def equivalence(run, old, v7, chunks, count):
    references = [r for r in old if r["method"] == "X30"]
    if len(references) != 330:
        raise ValueError("Missing old X30 comparisons")
    trace = []
    for i, ref in enumerate(references):
        count.cache_clear()
        row = output(v7[ref["dataset"], ref["id"], ref["pool"]], chunks, count, "X30")
        for field in ("context", "selected_ids", "delivered", "candidate_ids", "ranked_hits"):
            if row[field] != ref[field]:
                raise ValueError(f"Non-equivalent {field}: {ref['id']}")
        if row["packing_trace"]["objective"] != ref["packing_trace"]["objective"]:
            raise ValueError("Changed selection objective")
        trace.append(
            {
                "dataset": ref["dataset"],
                "id": ref["id"],
                "pool": ref["pool"],
                "context_sha256": canonical_hash(row["context"]),
                "old_feasibility_checks": ref["packing_trace"]["feasibility_checks"],
                "new_feasibility_checks": row["packing_trace"]["feasibility_checks"],
            }
        )
        if i % 30 == 0:
            print("equivalence", i + 1, 330, flush=True)
    write_new(run / "equivalence.json", {"checked": 330, "all_equal": True, "records": trace})


def components(run, v7, chunks, count):
    path = SOURCE / "implementation/src/infra_rag/budget_search.py"
    spec = importlib.util.spec_from_file_location("infra_rag._v8_frozen_budget_search", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows = [r for r in v7.values() if r["arm"] == "Ladj"]
    done = {(r["dataset"], r["id"], r["method"]) for r in read_rows(run / "components.jsonl")}
    for i, row in enumerate(rows):
        methods = ("original", "optimized") if i % 2 == 0 else ("optimized", "original")
        for method in methods:
            if (row["dataset"], row["id"], method) in done:
                continue
            count.cache_clear()
            started = perf_counter()
            if method == "optimized":
                _, context, trace = choose(row, chunks, count, "X30")
            else:
                hits = [
                    Hit(chunks[h["chunk_id"]], h["score"], rerank_score=h["rerank_score"])
                    for h in row["ranked_hits"]
                ]
                search = module.BudgetSearch(
                    hits, row["query"] + "\n" + row["scoring_query"], count
                )
                _, context, trace = search.pack(policy="exchange")
            elapsed = (perf_counter() - started) * 1000
            append(
                run / "components.jsonl",
                {
                    "dataset": row["dataset"],
                    "id": row["id"],
                    "method": method,
                    "latency_ms": elapsed,
                    "context_sha256": canonical_hash(context),
                    "trace": trace,
                    "scope": "fixed candidate packing; no retrieval/rerank/generation",
                },
            )
        if i % 10 == 0:
            print("components", i + 1, 110, flush=True)


class CopiedIndexEngine(Engine):
    """Reuse immutable identical retrieval views, not query or scoring results."""

    def service(self, kind):
        if kind != "adjacent" or kind in self.services:
            return super().service(kind)
        self.models()
        reference = json.loads((SOURCE / "index-adjacent.json").read_text())
        source = Path(reference["directory"])
        if digest(source / "index.json") != reference["index_sha256"]:
            raise ValueError("Changed archived adjacency index")
        views, records = adjacent_views(list(self.chunks.values()))
        directory = ROOT / "data/budget-search-v8-runtime" / canonical_hash(self.protocol)[:16]
        settings = configuration(directory)
        from dataclasses import replace

        settings = replace(
            settings,
            preprocessing_version=settings.preprocessing_version + ":" + canonical_hash(records),
        )
        if settings.fingerprint() != reference["fingerprint"]:
            raise ValueError("Copied view fingerprint differs")
        started = perf_counter()
        if not directory.exists():
            directory.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, directory)
        if digest(directory / "index.json") != reference["index_sha256"]:
            raise ValueError("Copied index differs")
        service = RetrievalService(settings)
        if [(c.id, c.content) for c in service.chunks] != [(c.id, c.content) for c in views]:
            raise ValueError("Copied index body differs")
        service.settings = replace(service.settings, rerank=False)
        service.encoder, service.reranker = self.encoder, self.reranker
        self.services[kind] = service
        write_new(
            self.run / "index-adjacent.json",
            {
                **reference,
                "directory": str(directory),
                "copy_load_ms": (perf_counter() - started) * 1000,
                "reused_query_results": False,
                "reused_rerank_results": False,
            },
        )
        return service


def runtime(run, protocol, v7, chunks, count):
    if not json.loads((run / "equivalence.json").read_text())["all_equal"]:
        raise ValueError("Equivalence gate required")
    engine = CopiedIndexEngine(run, protocol, chunks)
    rows = [r for r in v7.values() if r["arm"] == "B"]

    def execute(arm, row):
        pool, method = arm.split("-")
        base = {"scoring_query": row["scoring_query"], "hits": row["ranked_hits"]}
        bundle = engine.bundle(pool, base, row, [], cached=False)
        return choose({**row, "ranked_hits": bundle["hits"], "arm": pool}, chunks, count, method)

    for arm in protocol["runtime_arms"]:
        execute(arm, rows[0])
    done = {(r["dataset"], r["id"], r["arm"]) for r in read_rows(run / "latency.jsonl")}
    for i, row in enumerate(rows):
        order = ("B-O15", "Ladj-X30") if i % 2 == 0 else ("Ladj-X30", "B-O15")
        for arm in order:
            if (row["dataset"], row["id"], arm) in done:
                continue
            count.cache_clear()
            before = engine.new_pairs
            started = perf_counter()
            _, context, trace = execute(arm, row)
            elapsed = (perf_counter() - started) * 1000
            pairs = engine.new_pairs - before
            if pairs > 90:
                raise ValueError("Exceeded scoring budget")
            append(
                run / "latency.jsonl",
                {
                    "dataset": row["dataset"],
                    "id": row["id"],
                    "arm": arm,
                    "latency_ms": elapsed,
                    "actual_rerank_pairs": pairs,
                    "used_tokens": context["used_tokens"],
                    "used_characters": context["used_characters"],
                    "selected_ids": [e["chunk_id"] for e in context["evidence"]],
                    "search_trace": trace,
                    "result_cache_enabled": False,
                    "scope": "warm retrieval+rerank+packing, excluding init/translation/generation",
                },
            )
        engine.save()
        print("runtime", i + 1, 110, flush=True)


def summary(run):
    equivalence_data = json.loads((run / "equivalence.json").read_text())
    timings = read_rows(run / "latency.jsonl")
    components_data = read_rows(run / "components.jsonl")
    for rows, field in ((timings, "arm"), (components_data, "method")):
        if len(rows) != 220 or len({(r["dataset"], r["id"], r[field]) for r in rows}) != 220:
            raise ValueError("Incomplete performance comparison")
    times = {
        arm: {"n": 110, **latency_summary([r["latency_ms"] for r in timings if r["arm"] == arm])}
        for arm in ("B-O15", "Ladj-X30")
    }
    component_times = {
        m: {
            "n": 110,
            **latency_summary([r["latency_ms"] for r in components_data if r["method"] == m]),
        }
        for m in ("original", "optimized")
    }
    ratio = times["Ladj-X30"]["p95_ms"] / times["B-O15"]["p95_ms"]
    decision = {
        "quality_gate": equivalence_data["all_equal"],
        "equivalence_checked": 330,
        "quality_source": str(SOURCE.relative_to(ROOT)),
        "official_delivery": [47, 54],
        "repository_delivery": [41, 50],
        "latency_gate": ratio <= 1.5,
        "p95_ratio": ratio,
        "warm_latency": times,
        "component_latency": component_times,
        "independent_review_gate": None,
        "independent_review": "pending",
        "adoption_allowed": False,
        "default_changed": False,
        "confirmation_allowed": False,
        "holdout_test_read": False,
        "generation_api_calls": 0,
    }
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
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--phase", choices=("equivalence", "components", "runtime", "report"), required=True
    )
    args = parser.parse_args()
    run = args.output.resolve()
    protocol, old, v7, chunks, count = prepare(run)
    if args.phase == "equivalence":
        equivalence(run, old, v7, chunks, count)
    elif args.phase == "components":
        components(run, v7, chunks, count)
    elif args.phase == "runtime":
        runtime(run, protocol, v7, chunks, count)
    else:
        summary(run)
    record_operation(
        f"完成v8b阶段{args.phase}，{run.relative_to(ROOT)}",
        "保持选择一致并按原门槛验证真实性能",
        "该阶段产物已保存；未覆盖v8结果或改变默认配置",
        "独立审核pending；组件性能不是端到端性能",
    )


if __name__ == "__main__":
    main()
