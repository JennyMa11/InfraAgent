"""Only replace rerank scores on frozen original-chunk development candidate pools."""

import argparse
import copy
import importlib.metadata
import json
import math
import shutil
from pathlib import Path
from time import perf_counter

from benchmark_budget_search_v8 import append, read_rows, select_winner, summarize
from benchmark_document_local_v9 import evaluate
from benchmark_document_local_v9 import prepare as prepare_v9
from benchmark_original_rag_v7 import Engine
from operation_log import record_operation
from prepare_corpus_v2 import ROOT

from infra_rag.benchmarking import canonical_hash, digest, write_new
from infra_rag.evaluation import evidence_metrics, metrics
from infra_rag.offline_evaluation import latency_summary
from infra_rag.paired_statistics import holm, paired_statistics

SOURCE = ROOT / "evals/merged-corpus-v2/document-local-v9/run-20261003"
PLAN = ROOT / "evals/merged-corpus-v2/reranker-v10/experiment-plan.md"
REVISION = "953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e"
POOLS = ("B", "Doc")
METHODS = ("O15", "X30")


def prepare(run):
    parent, _, chunks, count = prepare_v9(SOURCE)
    manifest = json.loads((SOURCE / "final-artifacts-manifest.json").read_text())["files"]
    for name, expected in manifest.items():
        if digest(SOURCE / name) != expected:
            raise ValueError("Changed frozen v9 artifact: " + name)
    import torch
    from huggingface_hub import snapshot_download

    if not torch.backends.mps.is_available():
        raise ValueError("Frozen MPS protocol requires MPS")
    model_path = Path(
        snapshot_download("BAAI/bge-reranker-v2-m3", revision=REVISION, local_files_only=True)
    )
    filenames = (
        "config.json",
        "model.safetensors",
        "sentencepiece.bpe.model",
        "special_tokens_map.json",
        "tokenizer.json",
        "tokenizer_config.json",
    )
    model = {
        "id": "BAAI/bge-reranker-v2-m3",
        "revision": REVISION,
        "path": str(model_path),
        "files": {n: digest(model_path / n) for n in filenames},
    }
    inputs = {
        **parent["inputs"],
        str((SOURCE / "final-artifacts-manifest.json").relative_to(ROOT)): digest(
            SOURCE / "final-artifacts-manifest.json"
        ),
    }
    implementation = {
        str(p.relative_to(ROOT)): digest(p)
        for p in [
            *sorted((ROOT / "src/infra_rag").glob("*.py")),
            Path(__file__),
            ROOT / "scripts/benchmark_document_local_v9.py",
            ROOT / "scripts/benchmark_budget_search_v8.py",
            ROOT / "scripts/benchmark_original_rag_v7.py",
            ROOT / "scripts/prepare_corpus_v2.py",
            ROOT / "scripts/operation_log.py",
        ]
    }
    protocol = {
        "kind": "reranker_v10_fixed_candidates_dev_only",
        "inputs": inputs,
        "implementation": implementation,
        "models": parent["models"],
        "m3": model,
        "directory": parent["directory"],
        "plan_sha256": digest(PLAN),
        "expected_rows": 880,
        "pair_max_length": 512,
        "batch_size": 32,
        "activation": "sigmoid",
        "device": "mps",
        "dtype": "float32",
        "candidate_cap": 90,
        "token_budget": 1200,
        "char_budget": 4000,
        "selected_cap": 8,
        "packages": {
            n: importlib.metadata.version(n)
            for n in ("torch", "transformers", "sentence-transformers")
        },
        "independent_review": "pending",
        "default_changed": False,
        "holdout_test_read": False,
        "generation_api_calls": 0,
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
    references = {
        (r["dataset"], r["id"], r["arm"]): r
        for r in read_rows(SOURCE / "rows.jsonl")
        if r["pool"] in POOLS
    }
    if len(references) != 440:
        raise ValueError("Missing fixed candidate references")
    return protocol, references, chunks, count


class Scorer:
    def __init__(self, run, protocol, chunks):
        import torch
        from sentence_transformers import CrossEncoder

        started = perf_counter()
        self.model = CrossEncoder(
            protocol["m3"]["path"],
            local_files_only=True,
            trust_remote_code=False,
            device="mps",
            max_length=512,
            activation_fn=torch.nn.Identity(),
            model_kwargs={"dtype": torch.float32},
        )
        self.run, self.protocol, self.chunks = run, protocol, chunks
        self.cache = {}
        if (run / "m3-score-cache.json").exists():
            self.cache = json.loads((run / "m3-score-cache.json").read_text())
        self.calls = []
        self.actual_pairs = 0
        self.load_ms = (perf_counter() - started) * 1000
        self.dtype = str(next(self.model.model.parameters()).dtype)
        if self.dtype != "torch.float32" or str(self.model.device) != "mps":
            raise ValueError("Frozen device or precision not used")

    def score(self, source, *, cached=True):
        query = source["scoring_query"]
        hits = copy.deepcopy(source["ranked_hits"])
        keys = [
            canonical_hash([self.protocol["m3"], query, self.chunks[h["chunk_id"]].content])
            for h in hits
        ]
        missing = [(i, key) for i, key in enumerate(keys) if not cached or key not in self.cache]
        if missing:
            pairs = [(query, self.chunks[hits[i]["chunk_id"]].content) for i, _ in missing]
            lengths = [len(self.model.tokenizer.encode(q, text)) for q, text in pairs]
            started = perf_counter()
            raw = self.model.predict(pairs, batch_size=32, show_progress_bar=False)
            elapsed = (perf_counter() - started) * 1000
            values = []
            for (_i, key), logit in zip(missing, raw, strict=True):
                logit = float(logit)
                if not math.isfinite(logit):
                    raise ValueError("Nonfinite model logit")
                value = (
                    1 / (1 + math.exp(-logit))
                    if logit >= 0
                    else math.exp(logit) / (1 + math.exp(logit))
                )
                values.append(value)
                self.cache[key] = value
            self.actual_pairs += len(pairs)
            self.calls.append(
                {
                    "dataset": source["dataset"],
                    "id": source["id"],
                    "query": query,
                    "case_sha256": canonical_hash(
                        {k: source[k] for k in ("id", "query", "resolved_gold")}
                    ),
                    "chunk_ids": [hits[i]["chunk_id"] for i, _ in missing],
                    "body_hashes": [canonical_hash(t) for q, t in pairs],
                    "raw_logits": [float(v) for v in raw],
                    "scores": values,
                    "input_tokens": lengths,
                    "would_truncate": [n > 512 for n in lengths],
                    "actual_pairs": len(pairs),
                    "latency_ms": elapsed,
                    "result_cache_enabled": cached,
                    "dtype": self.dtype,
                    "device": "mps",
                }
            )
        for hit, key in zip(hits, keys, strict=True):
            hit["rerank_score"] = self.cache[key]
        hits.sort(key=lambda h: (-h["rerank_score"], -h["score"], h["chunk_id"]))
        return {"hits": hits, "scoring_query": query}

    def save(self):
        with (self.run / "m3-score-cache.json").open("w") as stream:
            json.dump(self.cache, stream)
        for call in self.calls:
            append(self.run / "model-calls.jsonl", call)
        self.calls.clear()


def quality(run, protocol, references, chunks, count):
    scorer = Scorer(run, protocol, chunks)
    done = {(r["dataset"], r["id"], r["arm"]) for r in read_rows(run / "rows.jsonl")}
    cases = [(ds, cid) for ds, cid, arm in references if arm == "B-O15"]
    for i, key in enumerate(cases):
        for pool in POOLS:
            source = references[*key, f"{pool}-O15"]
            if any((*key, f"{pool}-m3-{m}") not in done for m in METHODS):
                bundle = scorer.score(source)
            for method in METHODS:
                before = references[*key, f"{pool}-{method}"]
                if (*key, before["arm"]) not in done:
                    append(run / "rows.jsonl", {**before, "model": "base"})
                arm = f"{pool}-m3-{method}"
                if (*key, arm) in done:
                    continue
                count.cache_clear()
                row = evaluate(source, pool, bundle, chunks, count, method, source["local_trace"])
                row.update(arm=arm, model="m3", component_actual_pairs=len(bundle["hits"]))
                if set(row["candidate_ids"]) != set(source["candidate_ids"]):
                    raise ValueError("Changed fixed candidate set")
                append(run / "rows.jsonl", row)
        scorer.save()
        if i % 10 == 0:
            print("quality", i + 1, 110, flush=True)
    write_new(
        run / "model-load.json", {"ms": scorer.load_ms, "device": "mps", "dtype": scorer.dtype}
    )


def quality_report(run, references):
    rows = read_rows(run / "rows.jsonl")
    expected = {
        (*key[:2], f"{pool}{model}-{method}")
        for key in references
        for pool in POOLS
        for model in ("", "-m3")
        for method in METHODS
    }
    actual = [(r["dataset"], r["id"], r["arm"]) for r in rows]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError("Incomplete/unknown/duplicate planned outputs")
    summary, statistics = summarize(rows), {}
    ranking = {}
    for row in rows:
        if not row["answerable"]:
            continue
        key = f"{row['dataset']}:{row['arm']}"
        ranks = {
            k: evidence_metrics(row["candidate_ids"], row["resolved_gold"], k) for k in (5, 15, 30)
        }
        sparse = metrics(row["candidate_ids"], row["resolved_gold"]["relevant"], 30)
        ranking.setdefault(key, []).append(
            {
                "id": row["id"],
                "complete_ranking": ranks,
                "sparse_judgments_mrr_ndcg": {k: sparse[k] for k in ("mrr", "ndcg")},
            }
        )
    for ds in ("official", "repository"):
        for pool in POOLS:
            for method in METHODS:
                left, right = f"{pool}-{method}", f"{pool}-m3-{method}"
                statistics[f"{ds}:{right}_vs_{left}"] = paired_statistics(
                    [r for r in rows if r["dataset"] == ds and r["arm"] == left],
                    [r for r in rows if r["dataset"] == ds and r["arm"] == right],
                )
    for key, value in holm({k: v["cluster_permutation_p"] for k, v in statistics.items()}).items():
        statistics[key]["holm_p"] = value
    restricted = {k: v for k, v in summary.items() if k.split(":")[1] == "B-O15" or "-m3-" in k}
    winner = select_winner(restricted)
    write_new(
        run / "quality-summary.json",
        {"results": summary, "statistics": statistics, "ranking": ranking},
    )
    write_new(
        run / "quality-selection.json",
        {
            "winner": winner,
            "not_adoption": True,
            "online_doc_scope_budget_passes": False
            if winner and winner.startswith("Doc-")
            else None,
            "reason": "Doc scope and new-model scoring both count toward90 pairs",
        },
    )
    print("quality winner", winner, flush=True)
    for key, value in summary.items():
        print(key, value["delivered_complete"], flush=True)


def runtime(run, protocol, references, chunks, count):
    winner = json.loads((run / "quality-selection.json").read_text())["winner"]
    if winner is None or not winner.startswith("B-m3-"):
        raise ValueError("No runnable budget-compliant model winner")
    scorer, engine = Scorer(run, protocol, chunks), Engine(run, protocol, chunks)
    cases = [r for key, r in references.items() if key[2] == "B-O15"]

    def execute(row, arm):
        bundle = engine.bundle(
            "B",
            {"scoring_query": row["scoring_query"], "hits": row["ranked_hits"]},
            row,
            [],
            cached=False,
            score_candidates=arm == "B-O15",
        )
        if arm != "B-O15":
            bundle = scorer.score({**row, "ranked_hits": bundle["hits"]}, cached=False)
        from benchmark_budget_search_v8 import choose

        prepared = choose(
            {**row, "ranked_hits": bundle["hits"]}, chunks, count, arm.rsplit("-", 1)[1]
        )
        return bundle, prepared

    for arm in ("B-O15", winner):
        execute(cases[0], arm)
    done = {(r["dataset"], r["id"], r["arm"]) for r in read_rows(run / "runtime.jsonl")}
    for i, row in enumerate(cases):
        for arm in ("B-O15", winner) if i % 2 == 0 else (winner, "B-O15"):
            if (row["dataset"], row["id"], arm) in done:
                continue
            count.cache_clear()
            before, started = engine.new_pairs + scorer.actual_pairs, perf_counter()
            bundle, prepared = execute(row, arm)
            elapsed = (perf_counter() - started) * 1000
            pairs = engine.new_pairs + scorer.actual_pairs - before
            if pairs > 90:
                raise ValueError("Actual scoring budget exceeded")
            result = evaluate(
                row, "B", bundle, chunks, count, arm.rsplit("-", 1)[1], prepared=prepared
            )
            result.update(
                arm=arm,
                model="base" if arm == "B-O15" else "m3",
                latency_ms=elapsed,
                actual_rerank_pairs=pairs,
                result_cache_enabled=False,
            )
            append(run / "runtime.jsonl", result)
        engine.save()
        scorer.save()
        print("runtime", i + 1, 110, flush=True)


def report(run):
    selection = json.loads((run / "quality-selection.json").read_text())["winner"]
    decision = {
        "quality_winner": selection,
        "quality_gate": selection is not None,
        "budget_gate": not selection or not selection.startswith("Doc-"),
        "latency_gate": None,
        "actual_delivery_quality_gate": None,
        "independent_review_gate": None,
        "adoption_allowed": False,
        "holdout_test_read": False,
        "default_changed": False,
        "generation_api_calls": 0,
    }
    if selection and selection.startswith("B-m3-"):
        rows = read_rows(run / "runtime.jsonl")
        if len(rows) != 220 or len({(r["dataset"], r["id"], r["arm"]) for r in rows}) != 220:
            raise ValueError("Incomplete runtime comparison")
        actual = summarize(rows)
        times = {
            arm: {"n": 110, **latency_summary([r["latency_ms"] for r in rows if r["arm"] == arm])}
            for arm in ("B-O15", selection)
        }
        ratio = times[selection]["p95_ms"] / times["B-O15"]["p95_ms"]
        decision.update(
            actual_results=actual,
            warm_latency=times,
            p95_ratio=ratio,
            latency_gate=ratio <= 1.5,
            actual_delivery_quality_gate=select_winner(actual) == selection,
        )
    elif selection:
        decision["stop_reason"] = (
            "Doc model control is offline diagnostic; online scope+rerank exceeds90 pairs"
        )
    else:
        decision["stop_reason"] = (
            "No m3 quality winner; stop performance and embedding extension per plan"
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
        f"完成v10阶段{args.phase} {run.relative_to(ROOT)}",
        "固定候选单独检验重排模型",
        "对应阶段产物已保存，正文计数与旧标签不变",
        "独立人工审核pending；不采用默认配置",
    )


if __name__ == "__main__":
    main()
