"""Fail-closed dual-dev Stage 0 for Grid v2; never read confirmation questions."""

import argparse
import json
import shutil
from collections import Counter
from dataclasses import fields
from pathlib import Path
from time import perf_counter

from benchmark_native_pagination import local_models
from benchmark_original_rag_v7 import evaluation
from grid_retrieval import BatchedReranker, grid_schedule
from operation_log import ROOT, record_operation

from infra_rag.benchmarking import digest, write_new
from infra_rag.config import Settings
from infra_rag.embedding_experiments import source_document
from infra_rag.exact_search import ExactCollection
from infra_rag.grid_delivery import score_delivery
from infra_rag.models import Chunk

V4 = ROOT / "evals/merged-corpus-v2/recall-delivery-v4/run-20261002"
V6 = ROOT / "evals/merged-corpus-v2/budget-ablation-v6/run-20261003"
V1 = ROOT / "data/retrieval-grid-v1/run-20261029"


def load(path):
    return json.loads(path.read_text())


def rows(path):
    return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]


def freeze(out, query_profile):
    if out.exists():
        raise ValueError("Fresh run required")
    prior = load(V4 / "protocol.json")
    corpus = ROOT / prior["directory"]
    inputs = [
        V4 / "protocol.json",
        V4 / "rows.jsonl",
        V4 / "source-audit.json",
        V6 / "protocol.json",
        V6 / "rows.jsonl",
        V6 / "artifacts-manifest.json",
        corpus / "chunks.json",
        corpus / "index/index.json",
    ]
    for ds, folder in [
        ("official", "infra-official-v1-reviewed"),
        ("repository", "repository-benchmark"),
    ]:
        dev = ROOT / "evals" / folder / "dev.json"
        if digest(dev) != prior["dev_hashes"][ds]:
            raise ValueError("Frozen dev changed")
        inputs.append(dev)
    baseline = [r for r in rows(V4 / "rows.jsonl") if r["arm"] == "B5"]
    assert len(baseline) == 110
    for r in baseline:
        inputs.append(V4 / "bundles" / r["dataset"] / (r["id"] + ".json"))
    inputs += [V1 / "protocol.json", V1 / "index/index.json"]
    source_hashes = {
        r["source"]: r["expected"] for r in load(V4 / "source-audit.json")["source_files"]
    }
    code = [
        Path(__file__).resolve(),
        ROOT / "scripts/benchmark_original_rag_v7.py",
        ROOT / "scripts/benchmark_native_pagination.py",
        ROOT / "scripts/grid_retrieval.py",
        *sorted((ROOT / "src/infra_rag").glob("*.py")),
    ]
    out.mkdir(parents=True)
    for path in code:
        target = out / "implementation" / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    write_new(
        out / "protocol.json",
        {
            "version": "grid-v2-stage0",
            "query_profile": query_profile,
            "inputs": {str(p): digest(p) for p in inputs},
            "implementation": {str(p.relative_to(ROOT)): digest(p) for p in code},
            "sources": source_hashes,
            "models": prior["models"],
            "corpus": str(corpus),
            "expected_historical_delivery": {"official": 45, "repository": 41},
            "expected_positive": {"official": 54, "repository": 50},
            "v1_baseline": {"recall5": 56 / 60, "mrr5": 0.8972222222222223, "complete5": 38 / 60},
            "stage0": "110 historical delivery replays, 110 current dual-dev, 60 v1 baseline",
            "candidate_pool_cap": 90,
            "rerank_top_n": 90,
            "rrf_constant": 60,
            "tokens": 1200,
            "characters": 4000,
            "seed": 42,
            "generation_calls": 0,
            "confirmation_questions_read": False,
            "defaults_changed": False,
            "stop": "Stop on integrity/replay/mapping/truncation/budget failure",
            "later_stages": {
                "A": "4 indexes x110",
                "B": "2x9x110",
                "C": "3x2x110",
                "D": "up to2x7x110",
                "E": "6x110",
                "repeat": "up to3x3x110",
                "ann": "2x3x110",
            },
            "adoption_gate": "Both corpora noninferior, zero baseline-complete losses, net>=2, "
            "p95<=1.5x, pairs<=90, no truncation, all scheduled outputs present",
            "review": "AI gold; independent human review pending; no automatic adoption",
        },
    )
    write_new(out / "cases.json", baseline)
    write_new(
        out / "schedule.json",
        grid_schedule([f"{r['dataset']}:{r['id']}" for r in baseline], ["current-baseline"]),
    )


def verify(out):
    p = load(out / "protocol.json")
    for name, sha in {**p["inputs"], **p["sources"]}.items():
        if digest(name) != sha:
            raise ValueError(f"Frozen input changed: {name}")
    for name, sha in p["implementation"].items():
        if digest(ROOT / name) != sha or digest(out / "implementation" / name) != sha:
            raise ValueError(f"Implementation changed: {name}")
    for model in p["models"].values():
        if "files" in model:
            for name, sha in model["files"].items():
                if digest(Path(model["path"]) / name) != sha:
                    raise ValueError("Model changed")
    return p


def run(out):
    p = verify(out)
    from transformers import AutoTokenizer

    model = p["models"]["embedding"]
    options = load(Path(model["path"]) / "sentence_bert_config.json")
    tokenizer = AutoTokenizer.from_pretrained(
        model["path"], local_files_only=True, do_lower_case=options["do_lower_case"]
    )

    def count(text):
        return len(tokenizer.encode(text, add_special_tokens=False))

    chunks = {c["id"]: Chunk(**c) for c in load(Path(p["corpus"]) / "chunks.json")}
    documents = {
        source: source_document(Path(source).read_text(), sha)
        for source, sha in p["sources"].items()
    }
    totals, positives = Counter(), Counter()
    reference = {
        (r["dataset"], r["id"]): r for r in rows(V6 / "rows.jsonl") if r["arm"] == "B-k8-l0-p1-n0"
    }
    for row in load(out / "cases.json"):
        bundle = load(V4 / "bundles" / row["dataset"] / (row["id"] + ".json"))["B5"]
        result = evaluation(row, "historical-v6", bundle, chunks, count)
        write_new(out / "rows/historical" / row["dataset"] / (row["id"] + ".json"), result)
        if result["context"] != reference[row["dataset"], row["id"]]["context"]:
            raise ValueError(f"v6 exact evidence replay differs: {row['dataset']}:{row['id']}")
        if row["answerable"]:
            positives[row["dataset"]] += 1
            totals[row["dataset"]] += result["delivered"]["complete"]
    write_new(out / "historical-summary.json", {"complete": totals, "positive": positives})
    if (
        dict(totals) != p["expected_historical_delivery"]
        or dict(positives) != p["expected_positive"]
    ):
        raise ValueError(f"Historical delivery mismatch: {dict(totals)} / {dict(positives)}")
    from infra_rag.service import RetrievalService

    index = load(Path(p["corpus"]) / "index/index.json")
    names = {f.name for f in fields(Settings)}
    opts = {k: v for k, v in index["fingerprint"].items() if k in names}
    shutil.copytree(Path(p["corpus"]) / "index", out / "index")
    service = RetrievalService(
        Settings(
            data_dir=out / "index",
            **opts,
            rerank=True,
            fusion_candidates="union",
            candidate_pool_cap=90,
        )
    )
    local_models(service, p["models"])
    service.context_counter = count
    service.reranker = BatchedReranker(service.reranker, 32)
    service.text_collection = ExactCollection(service.chunks, service.vectors)
    cases = {f"{r['dataset']}:{r['id']}": r for r in load(out / "cases.json")}
    for job in load(out / "schedule.json"):
        row = cases[job["id"]]
        diagnostics, context = {}, {}
        start = perf_counter()
        try:
            retrieval_query = row["query"]
            if p["query_profile"] == "frozen":
                retrieval_query = load(V4 / "bundles" / row["dataset"] / (row["id"] + ".json"))[
                    "B5"
                ]["scoring_query"]
            hits = service.search(
                retrieval_query, top_k=5, diagnostics=diagnostics, context_pack=context
            )
            assert len(diagnostics["candidates"]) <= 90
            assert not any(r["would_truncate"] for r in diagnostics["rerank"]["pairs"]), (
                "Reranker input truncation"
            )
            assert context["used_tokens"] <= 1200 and context["used_characters"] <= 4000
            gold = row["resolved_gold"]
            delivered = score_delivery(
                context["evidence"],
                {
                    **row,
                    "evidence_alternatives": gold["evidence_alternatives"]
                    if row["answerable"]
                    else [],
                },
                chunks,
                documents,
            )
            result = {
                "status": "completed",
                "diagnostics": diagnostics,
                "context": context,
                "hit_ids": [h.chunk.id for h in hits],
                "delivered": delivered,
            }
        except Exception as exc:
            result = {
                "status": "failed",
                "error": str(exc),
                "diagnostics": diagnostics,
                "context": context,
            }
        result.update(job, elapsed_ms=(perf_counter() - start) * 1000)
        write_new(out / "rows/current" / row["dataset"] / (row["id"] + ".json"), result)
        print(job["id"], result["status"], flush=True)
        if result["status"] == "failed":
            raise ValueError(result["error"])
    # The v1 replay is required before enabling Stage A; never infer it from v7 results.
    write_new(
        out / "decision.json", {"stage0": "incomplete", "next": "v1 ranking replay", "adopt": False}
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["freeze", "verify", "stage0"])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--query-profile", choices=["literal", "frozen"])
    args = parser.parse_args()
    try:
        if args.phase == "freeze":
            if args.query_profile is None:
                raise ValueError("Freeze requires an explicit --query-profile literal|frozen")
            freeze(args.out, args.query_profile)
        elif args.phase == "verify":
            verify(args.out)
        else:
            run(args.out)
    except Exception as exc:
        if args.out.exists():
            write_new(
                args.out / "aborted.json",
                {
                    "phase": args.phase,
                    "error": str(exc),
                    "stage_A_allowed": False,
                    "generation_calls": 0,
                },
            )
            write_new(
                args.out / "artifacts-manifest.json",
                {
                    str(f.relative_to(args.out)): digest(f)
                    for f in args.out.rglob("*")
                    if f.is_file()
                },
            )
        record_operation(
            f"Grid v2 {args.phase}中止", "执行冻结协议的前置硬门槛", f"产物 {args.out}", str(exc)
        )
        raise
    record_operation(f"Grid v2 {args.phase}", "双库开发网格前置校验", str(args.out))


if __name__ == "__main__":
    main()
