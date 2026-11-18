"""Dev grid for document Recall/Hit/MRR and retrieval P95; no answer model calls."""

import argparse
import platform
import random
import shutil
from dataclasses import replace
from importlib.metadata import version
from pathlib import Path
from time import perf_counter

from benchmark_native_pagination import local_models, settings
from operation_log import ROOT, record_operation
from prepare_corpus_pilot import load, save
from tune_native_retrieval import inputs

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.embedding_experiments import chunk_evidence, delivered_intervals, interval_score
from infra_rag.exact_search import ExactCollection
from infra_rag.grid_metrics import dominates, feasible, latency, rank_metrics
from infra_rag.service import RetrievalService

SOURCE = ROOT / "data/native-pagination-v1/run-20261029"
DATASET = ROOT / "evals/native-tuning-v1/dataset-20261029"
BASE = "hybrid-k30-b32"
CONFIGS = {
    "bm25-k30": {"strategy": "bm25", "k": 30, "rerank": False, "batch": 32},
    "dense-k30": {"strategy": "dense", "k": 30, "rerank": False, "batch": 32},
    **{
        f"hybrid-k{k}-none": {"strategy": "hybrid", "k": k, "rerank": False, "batch": 32}
        for k in (15, 30, 45)
    },
    **{
        f"hybrid-k{k}-b{b}": {"strategy": "hybrid", "k": k, "rerank": True, "batch": b}
        for k in (15, 30, 45)
        for b in (16, 32)
    },
}
QUALITY = ("recall5", "hit5", "mrr5", "required_recall5", "complete5")


class BatchedReranker:
    def __init__(self, model, batch):
        self.model = model
        self.batch = batch

    def __getattr__(self, name):
        return getattr(self.model, name)

    def predict(self, pairs):
        return self.model.predict(pairs, batch_size=self.batch, show_progress_bar=False)


def grid_schedule(case_ids, configs, repetitions=1):
    schedule = []
    for rep in range(repetitions):
        ids = list(case_ids)
        random.Random(42 + rep).shuffle(ids)
        for i, cid in enumerate(ids):
            order = list(configs)
            offset = (i + rep) % len(order)
            order = order[offset:] + order[:offset]
            schedule.extend({"id": cid, "config": config, "rep": rep} for config in order)
    return schedule


def freeze(out):
    cases, docs, mapped, gold = inputs(DATASET)
    files = [
        Path(__file__).resolve(),
        ROOT / "scripts/tune_native_retrieval.py",
        ROOT / "scripts/benchmark_native_pagination.py",
        *[
            ROOT / f"src/infra_rag/{n}.py"
            for n in (
                "grid_metrics",
                "service",
                "lexical",
                "encoding",
                "context",
                "exact_search",
                "embedding_experiments",
            )
        ],
    ]
    protocol = {
        "inputs": {
            str(p.relative_to(ROOT)): digest(p)
            for p in (
                DATASET / "dev.json",
                DATASET / "dataset-manifest.json",
                SOURCE / "index/index.json",
                SOURCE / "protocol.json",
            )
        },
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in files},
        "models": load(SOURCE / "protocol.json")["models"],
        "configs": CONFIGS,
        "baseline": BASE,
        "sources": {p: d["sha256"] for p, d in docs.items()},
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "packages": {
                n: version(n)
                for n in ("sentence-transformers", "transformers", "torch", "chromadb", "numpy")
            },
        },
        "metrics": (
            "TopK chunk ranks: source recall unique relevant docs / union gold docs; hit any "
            "gold doc; MRR first gold doc chunk rank. Required span recall and complete "
            "alternative reported separately."
        ),
        "cutoffs": [5, 10],
        "timing": (
            "RetrievalService.search top10 including context pack and diagnostics, "
            "no HTTP/LLM; model/index build excluded; warm models and lexical stats"
        ),
        "stages": (
            "screen11x60; shortlist baseline+best recall/hit/mrr+fastest feasible (max5); "
            "exact3x60; ANN2x60 for baseline and lowest-p95 feasible shortlist champion"
        ),
        "quality_guard": (
            "all5 quality metrics >= baseline, no original30 complete5 losses; no forced "
            "winner; Pareto retained"
        ),
        "statistics": (
            "Exploratory dev only. Descriptive metrics and per-round P95, no independent "
            "performance claim. Repetitions are not independent questions."
        ),
        "seed": 42,
        "rerank_pair_cap": 90,
        "query_language": "none",
        "lexical_mode": "raw",
        "context_tokens": 1200,
        "context_chars": 4000,
        "answer_calls": 0,
        "retry_limit": 0,
        "default_changed": False,
        "new_labels": "30 AI source-grounded labels pending review",
    }
    save(out / "protocol.json", protocol)
    save(out / "cases.json", cases)
    save(out / "gold.json", gold)
    save(out / "screen-schedule.json", grid_schedule([c["id"] for c in cases], CONFIGS))
    for p in files:
        dest = out / "implementation" / p.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and digest(dest) != digest(p):
            raise ValueError("Snapshot changed")
        if not dest.exists():
            dest.write_bytes(p.read_bytes())
    if not (out / "index").exists():
        shutil.copytree(SOURCE / "index", out / "index")
    return {"phase": "frozen", "configs": len(CONFIGS), "screen_outputs": len(cases) * len(CONFIGS)}


def verify(out):
    p = load(out / "protocol.json")
    for name, sha in {**p["inputs"], **p["implementation"]}.items():
        if digest(ROOT / name) != sha:
            raise ValueError("Frozen input changed: " + name)
    for name, sha in p["sources"].items():
        if digest(Path(name)) != sha:
            raise ValueError("Source changed: " + name)
    for kind in ("embedding", "reranker"):
        spec = p["models"][kind]
        for name, sha in spec["files"].items():
            if digest(Path(spec["path"]) / name) != sha:
                raise ValueError("Model changed")
    return p


def validate_rows(rows, schedule):
    def identity(row):
        return row["id"], row["config"], row["rep"]

    expected = {identity(r) for r in schedule}
    actual = [identity(r) for r in rows]
    if len(set(actual)) != len(actual) or set(actual) != expected:
        raise ValueError("Missing, unexpected, or duplicate scheduled outputs")
    if any(r["status"] != "completed" for r in rows):
        raise ValueError("Failed outputs retained; complete-stage selection forbidden")


def summarize(rows, baseline=BASE):
    results = {}
    by = {(r["id"], r["config"], r["rep"]): r for r in rows}
    for config in sorted({r["config"] for r in rows}):
        group = [r for r in rows if r["config"] == config]
        n = len(group)
        m = {key: sum(r["metrics"][key] for r in group) / n for key in group[0]["metrics"]}
        m.update(latency([r["elapsed_ms"] for r in group]))
        m["outputs"] = n
        m["proportions"] = {
            key: {
                "numerator": sum(r["metrics"][key] for r in group),
                "denominator": n,
                "value": m[key],
                "measurable_coverage": 1.0,
            }
            for key in group[0]["metrics"]
        }
        m["round_p95_ms"] = {
            str(rep): latency([r["elapsed_ms"] for r in group if r["rep"] == rep])["p95_ms"]
            for rep in sorted({r["rep"] for r in group})
        }
        m["original_complete_losses"] = sorted(
            {
                r["id"]
                for r in group
                if r["id"].startswith("diag-")
                and by[(r["id"], baseline, r["rep"])]["metrics"]["complete5"]
                and not r["metrics"]["complete5"]
            }
        )
        m["rerank_pairs"] = sum(r["rerank_pairs"] for r in group)
        results[config] = m
    return results


def shortlist(summary):
    selected = [BASE]
    for metric in ("recall5", "hit5", "mrr5"):
        best = max(
            summary,
            key=lambda c: (
                summary[c][metric],
                summary[c]["required_recall5"],
                -summary[c]["p95_ms"],
                c,
            ),
        )
        if best not in selected:
            selected.append(best)
    safe = [c for c in summary if feasible(summary[c], summary[BASE])]
    fastest = min(safe, key=lambda c: (summary[c]["p95_ms"], -summary[c]["mrr5"], c))
    if fastest not in selected:
        selected.append(fastest)
    return selected


def run_stage(out, stage):
    protocol = verify(out)
    cases, docs, mapped, gold = inputs(DATASET)
    case_by = {c["id"]: c for c in cases}
    if stage == "screen":
        schedule = load(out / "screen-schedule.json")
    elif stage == "repeat":
        selected = load(out / "shortlist.json")["configs"]
        schedule = grid_schedule(case_by, selected, 3)
        save(out / "repeat-schedule.json", schedule)
    else:
        selected = load(out / "repeat-selection.json")["ann_configs"]
        schedule = grid_schedule(case_by, selected, 2)
        save(out / "ann-schedule.json", schedule)
    service = RetrievalService(settings(out, protocol["models"]))
    local_models(service, protocol["models"])
    if stage == "ann":
        service.text_collection, service.clip_collection = service._collections(
            service.chunks, service.vectors
        )
    else:
        service.text_collection = ExactCollection(service.chunks, service.vectors)
    raw_reranker = service.reranker
    from infra_rag.lexical import BM25Index
    from infra_rag.service import lexical_statistics

    service.lexical_cache[(None, None, "raw")] = BM25Index(
        service.chunks, statistics=lexical_statistics(service.chunks)
    )
    # Non-evaluation warmup: no query/result cache and never counted as a dev observation.
    started = perf_counter()
    service._encoder().encode(["检索计时预热"], query=True)
    for b in (16, 32):
        raw_reranker.predict([("检索计时预热", "索引预热")], batch_size=b, show_progress_bar=False)
    save(
        out / f"{stage}-warmup.json",
        {"elapsed_ms": (perf_counter() - started) * 1000, "evaluation_queries": 0},
    )
    relevant = {cid: {r["source"] for g in groups for r in g} for cid, groups in gold.items()}
    for i, job in enumerate(schedule):
        target = out / stage / f"{job['id']}-{job['config']}-r{job['rep']}.json"
        if target.exists():
            raise ValueError("Fresh stage output required; no result-based retry")
        cfg = CONFIGS[job["config"]]
        service.settings = replace(service.settings, candidate_k=cfg["k"], rerank=cfg["rerank"])
        service.reranker = BatchedReranker(raw_reranker, cfg["batch"])
        d = {}
        context = {}
        start = perf_counter()
        try:
            hits = service.search(
                case_by[job["id"]]["query"],
                top_k=10,
                strategy=cfg["strategy"],
                diagnostics=d,
                context_pack=context,
            )
        except Exception as exc:
            save(
                target,
                {
                    **job,
                    "run_id": out.name,
                    "stage": stage,
                    "status": "failed",
                    "elapsed_ms": (perf_counter() - start) * 1000,
                    "error": str(exc),
                    "diagnostics": d,
                },
            )
            raise
        elapsed = (perf_counter() - start) * 1000
        pairs = len(d["candidates"]) if cfg["rerank"] else 0
        assert pairs <= 90
        assert not any(p["would_truncate"] for p in d["rerank"].get("pairs", []))
        metrics = {}
        for k in (5, 10):
            metrics.update(
                {
                    f"{name}{k}": value
                    for name, value in rank_metrics(
                        [h.chunk.source for h in hits], relevant[job["id"]], k
                    ).items()
                }
            )
            spans = interval_score(
                delivered_intervals([chunk_evidence(mapped[h.chunk.id]) for h in hits[:k]], docs),
                gold[job["id"]],
            )
            metrics[f"required_recall{k}"] = spans["coverage"]
            metrics[f"complete{k}"] = spans["complete"]
        pool = interval_score(
            delivered_intervals([chunk_evidence(mapped[cid]) for cid in d["candidates"]], docs),
            gold[job["id"]],
        )
        row = {
            **job,
            "run_id": out.name,
            "stage": stage,
            "status": "completed",
            "elapsed_ms": elapsed,
            "metrics": metrics,
            "candidate_complete": pool["complete"],
            "candidate_required_recall": pool["coverage"],
            "rerank_pairs": pairs,
            "diagnostics": d,
            "hit_ids": [h.chunk.id for h in hits],
            "case_sha256": canonical_hash(case_by[job["id"]]),
        }
        save(target, row)
        save(target.with_suffix(".sha256.json"), {"sha256": digest(target)})
        if i % 60 == 0:
            print(stage, i + 1, "/", len(schedule), flush=True)
    rows = [load(p) for p in (out / stage).glob("*.json") if not p.name.endswith(".sha256.json")]
    validate_rows(rows, schedule)
    result = summarize(rows)
    save(out / f"{stage}-summary.json", result)
    if stage == "screen":
        save(out / "shortlist.json", {"configs": shortlist(result)})
    if stage == "repeat":
        safe = [c for c in result if feasible(result[c], result[BASE])]
        champion = min(safe, key=lambda c: (result[c]["p95_ms"], -result[c]["mrr5"], c))
        pareto = [
            c
            for c in result
            if not any(dominates(result[other], result[c]) for other in result if other != c)
        ]
        save(
            out / "repeat-selection.json",
            {
                "champion": champion,
                "ann_configs": list(dict.fromkeys([BASE, champion])),
                "pareto": pareto,
                "pareto_dominates_baseline": dominates(result[champion], result[BASE]),
                "quality_and_latency_improved": (
                    any(result[champion][k] > result[BASE][k] for k in QUALITY)
                    and result[champion]["p95_ms"] < result[BASE]["p95_ms"]
                ),
            },
        )
    if stage == "ann":
        save(
            out / "artifacts-manifest.json",
            {
                p.relative_to(out).as_posix(): digest(p)
                for p in out.rglob("*")
                if p.is_file() and p.name != "artifacts-manifest.json"
            },
        )
    return {"phase": stage, "outputs": len(rows), "summary": result}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=("freeze", "screen", "repeat", "ann"), required=True)
    a = parser.parse_args()
    try:
        result = (
            freeze(a.output.resolve())
            if a.phase == "freeze"
            else run_stage(a.output.resolve(), a.phase)
        )
        record_operation(
            "Recall/Hit/MRR/P95 Grid " + a.phase,
            "保持60dev和90重排对预算，无生成调用",
            str(result),
            "探索性开发结果，默认不采用；来源命中不等于完整证据或答对",
        )
        print(result)
    except Exception as exc:
        record_operation("Grid中止", "保留失败现场，不改变冻结网格", str(a.output), str(exc))
        raise
