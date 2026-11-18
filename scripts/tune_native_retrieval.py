"""Dev-only component search then real QA validation, with frozen evidence and caps."""

import argparse
import shutil
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from benchmark_native_pagination import ObservedRetrieval, local_models, settings
from fastapi.testclient import TestClient
from operation_log import ROOT, record_operation
from prepare_corpus_pilot import load, save

from infra_rag.api import create_app
from infra_rag.assistant import AnswerService, ConversationStore
from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.embedding_experiments import (
    chunk_evidence,
    delivered_intervals,
    freeze_gold,
    interval_score,
    mapped_chunk,
    source_document,
)
from infra_rag.exact_search import ExactCollection
from infra_rag.model_clients import configured_model
from infra_rag.models import Chunk
from infra_rag.offline_evaluation import RecordingModel
from infra_rag.service import RetrievalService

SOURCE = ROOT / "data/native-pagination-v1/run-20261029"
CONFIGS = {
    f"k{k}-{m}": {"candidate_k": k, "lexical_query_mode": m}
    for k in (30, 45)
    for m in ("raw", "technical")
}
BASE = "k30-raw"


def inputs(dataset):
    cases = load(dataset / "dev.json")
    if digest(dataset / "dev.json") != load(dataset / "dataset-manifest.json")["dev_sha256"]:
        raise ValueError("Dataset changed")
    index = load(SOURCE / "index/index.json")
    docs = {
        p: source_document(Path(p).read_text(), digest(p))
        for p in {c["source"] for c in index["chunks"]}
    }
    mapped = {c["id"]: mapped_chunk(Chunk(**c), docs[c["source"]]) for c in index["chunks"]}
    paths = {Path(p).stem: p for p in docs}
    gold = {}
    for c in cases:
        adapted = {
            "answerable": True,
            "id": c["id"],
            "evidence_alternatives": [
                {
                    "spans": [
                        {"absolute_source": paths[r["document_id"]], "text": r["quote"]}
                        for r in g["requirements"]
                    ]
                }
                for g in c["evidence_alternatives"]
            ],
        }
        gold[c["id"]] = freeze_gold(adapted, docs)
    return cases, docs, mapped, gold


def prepare(out, dataset):
    cases, docs, mapped, gold = inputs(dataset)
    if len(cases) != 60:
        raise ValueError("Expected frozen 60-case dev set")
    files = [
        Path(__file__).resolve(),
        ROOT / "scripts/benchmark_native_pagination.py",
        *[
            ROOT / f"src/infra_rag/{n}.py"
            for n in (
                "api",
                "assistant",
                "service",
                "config",
                "encoding",
                "lexical",
                "exact_search",
                "experimental_pages",
                "paged_answers",
                "embedding_experiments",
                "model_clients",
            )
        ],
    ]
    models = load(SOURCE / "protocol.json")["models"]
    for kind in ("embedding", "reranker"):
        for name, sha in models[kind]["files"].items():
            if digest(Path(models[kind]["path"]) / name) != sha:
                raise ValueError("Frozen model changed")
    protocol = {
        "inputs": {
            str(p.relative_to(ROOT)): digest(p)
            for p in (
                dataset / "dev.json",
                dataset / "dataset-manifest.json",
                SOURCE / "index/index.json",
            )
        },
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in files},
        "models": models,
        "model": configured_model().configuration(),
        "configs": CONFIGS,
        "baseline": BASE,
        "dense_search": (
            "Exact cosine over same1535 vectors; fresh query encoding; "
            "dev control, production ANN unchanged"
        ),
        "sources": {p: d["sha256"] for p, d in docs.items()},
        "selection": "No old30 loss; maximize top5/first_page/candidate; fewer pairs; baseline tie",
        "semantics": "Source-span coverage proxy; AI labels pending; no holdout reads",
        "limits": "pairs<=90; top5; body1200tokens/4000chars; Chinese only; pagination fixed",
        "retrieval_outputs": 240,
        "answer_outputs_max": 120,
        "answer_attempt_cap": 1680,
        "defaults_changed": False,
        "confirmation": "No independent confirmation performed; all60 are tuning dev",
    }
    save(out / "protocol.json", protocol)
    save(out / "cases.json", cases)
    save(out / "gold-intervals.json", gold)
    save(
        out / "mapping-summary.json",
        {
            "chunks": len(mapped),
            "mapped_characters": sum(len(c.content) for c in mapped.values()),
            "sources": len(docs),
        },
    )
    save(
        out / "schedule.json",
        [
            {"id": c["id"], "config": name}
            for i, c in enumerate(cases)
            for name in (list(CONFIGS) if i % 2 == 0 else list(reversed(CONFIGS)))
        ],
    )
    for p in files:
        dest = out / "implementation" / p.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and digest(dest) != digest(p):
            raise ValueError("Snapshot changed")
        if not dest.exists():
            dest.write_bytes(p.read_bytes())
    if not (out / "index").exists():
        shutil.copytree(SOURCE / "index", out / "index")
    return {"phase": "frozen", "dev": len(cases), "configs": len(CONFIGS)}


def verify(out):
    p = load(out / "protocol.json")
    for name, sha in {**p["inputs"], **p["implementation"]}.items():
        if digest(ROOT / name) != sha:
            raise ValueError("Frozen input/implementation changed: " + name)
    for path, sha in p["sources"].items():
        if digest(path) != sha:
            raise ValueError("Source changed")
    return p


def choose(rows):
    if len(rows) != 240 or len({(r["id"], r["config"]) for r in rows}) != 240:
        raise ValueError("Cannot select from incomplete grid")
    by = {(r["id"], r["config"]): r for r in rows}
    baseline = [r for r in rows if r["config"] == BASE]
    stats = {}
    for config in CONFIGS:
        selected = [r for r in rows if r["config"] == config]
        lost = [
            r["id"]
            for r in baseline
            if r["id"].startswith("diag-")
            and r["top5"]["complete"]
            and not by[(r["id"], config)]["top5"]["complete"]
        ]
        stats[config] = {
            **{
                f: sum(r[f]["complete"] for r in selected)
                for f in ("candidate", "top5", "first_page")
            },
            "pairs": sum(r["pairs"] for r in selected),
            "original30_top5_lost": lost,
        }
    eligible = [k for k, v in stats.items() if not v["original30_top5_lost"]]
    winner = max(
        eligible,
        key=lambda k: (
            stats[k]["top5"],
            stats[k]["first_page"],
            stats[k]["candidate"],
            -stats[k]["pairs"],
            k == BASE,
        ),
    )
    return {
        "winner": winner,
        "stats": stats,
        "answer_accuracy": None,
        "independent_confirmation": False,
    }


def retrieve(out):
    p = verify(out)
    dataset = ROOT / Path(next(k for k in p["inputs"] if k.endswith("/dev.json"))).parent
    cases, docs, mapped, gold = inputs(dataset)
    service = RetrievalService(settings(out, p["models"]))
    local_models(service, p["models"])
    service.text_collection = ExactCollection(service.chunks, service.vectors)
    service.clip_collection = None
    by_case = {c["id"]: c for c in cases}
    for job in load(out / "schedule.json"):
        path = out / "retrieval" / f"{job['id']}-{job['config']}.json"
        if path.exists():
            if digest(path) != load(path.with_suffix(".sha256.json"))["sha256"]:
                raise ValueError("Checkpoint changed")
            continue
        service.settings = replace(service.settings, **CONFIGS[job["config"]])
        c = by_case[job["id"]]
        d = {}
        context = {}
        started = perf_counter()
        hits = service.search(
            c["query"], top_k=5, strategy="hybrid", diagnostics=d, context_pack=context
        )
        assert len(d["candidates"]) <= 90
        assert not any(x["would_truncate"] for x in d["rerank"]["pairs"])

        def score(evidence, case_id=c["id"]):
            return interval_score(delivered_intervals(evidence, docs), gold[case_id])

        actual = [{**e, "metadata": mapped[e["chunk_id"]].metadata} for e in context["evidence"]]
        row = {
            **job,
            "case_sha256": canonical_hash(c),
            "diagnostics": d,
            "hits": [h.chunk.id for h in hits],
            "candidate": score([chunk_evidence(mapped[cid]) for cid in d["candidates"]]),
            "top5": score([chunk_evidence(mapped[h.chunk.id]) for h in hits]),
            "first_page": score(actual),
            "pairs": len(d["candidates"]),
            "elapsed_ms": (perf_counter() - started) * 1000,
        }
        save(path, row)
        save(path.with_suffix(".sha256.json"), {"sha256": digest(path)})
        if job["config"] == list(CONFIGS)[-1]:
            print("retrieved", c["id"], flush=True)
    rows = [
        load(path)
        for path in (out / "retrieval").glob("*.json")
        if not path.name.endswith(".sha256.json")
    ]
    selection = choose(rows)
    save(out / "selection.json", selection)
    return selection


def answers(out):
    p = verify(out)
    cases = load(out / "cases.json")
    winner = load(out / "selection.json")["winner"]
    configs = list(dict.fromkeys([BASE, winner]))
    service = RetrievalService(settings(out, p["models"]))
    local_models(service, p["models"])
    service.text_collection = ExactCollection(service.chunks, service.vectors)
    service.clip_collection = None
    rows = []
    for i, c in enumerate(cases):
        for config in configs if i % 2 == 0 else list(reversed(configs)):
            path = out / "answers" / f"{c['id']}-{config}.json"
            if path.exists() or path.with_suffix(".started.json").exists():
                raise ValueError("No implicit answer retry")
            save(path.with_suffix(".started.json"), {"status": "started"})
            service.settings = replace(service.settings, **CONFIGS[config])
            observed = ObservedRetrieval(service)
            model = RecordingModel(configured_model())
            started = perf_counter()
            with TemporaryDirectory() as tmp:
                assistant = AnswerService(
                    observed, model, ConversationStore(Path(tmp) / "history.sqlite")
                )
                response = TestClient(create_app(observed, assistant)).post(
                    "/chat", json={"message": c["query"], "experimental_pagination": True}
                )
            row = {
                "id": c["id"],
                "config": config,
                "case_sha256": canonical_hash(c),
                "http_status": response.status_code,
                "response": response.json(),
                "retrieval": observed.events,
                "calls": model.calls,
                "elapsed_ms": (perf_counter() - started) * 1000,
                "strict_correct": None,
            }
            save(path, row)
            save(path.with_suffix(".sha256.json"), {"sha256": digest(path)})
            rows.append(row)
            print("answered", c["id"], config, row["response"].get("status"), flush=True)
            if response.status_code != 200:
                raise ValueError("HTTP failure, stopped with saved output")
            reference = load(out / "retrieval" / f"{c['id']}-{config}.json")
            assert (
                observed.events[0]["diagnostics"]["ranked_ids"]
                == reference["diagnostics"]["ranked_ids"]
            )
    summary = {
        "dev": 60,
        "configs": configs,
        "requests": len(rows),
        "model_calls": sum(len(r["calls"]) for r in rows),
        "answer_accuracy": None,
        "answer_review": "pending",
        "default_changed": False,
    }
    assert summary["model_calls"] <= p["answer_attempt_cap"]
    save(out / "answer-summary.json", summary)
    save(
        out / "answer-review-template.json",
        [
            {
                "id": r["id"],
                "config": r["config"],
                "status": "pending",
                "case_sha256": r["case_sha256"],
                "trace_sha256": digest(out / "answers" / f"{r['id']}-{r['config']}.json"),
                "reviewer": None,
                "strict_correct": None,
                "claims_supported": None,
                "conditions_preserved": None,
            }
            for r in rows
        ],
    )
    save(
        out / "artifacts-manifest.json",
        {
            path.relative_to(out).as_posix(): digest(path)
            for path in out.rglob("*")
            if path.is_file() and path.name != "artifacts-manifest.json"
        },
    )
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--dataset", type=Path, default=ROOT / "evals/native-tuning-v1/dataset-20261029"
    )
    parser.add_argument("--phase", choices=("prepare", "retrieve", "answers"), required=True)
    a = parser.parse_args()
    try:
        result = (
            prepare(a.output.resolve(), a.dataset.resolve())
            if a.phase == "prepare"
            else retrieve(a.output.resolve())
            if a.phase == "retrieve"
            else answers(a.output.resolve())
        )
        record_operation(
            "60题原生参数筛选 " + a.phase,
            "只在dev选择候选，保持预算和来源",
            str(result),
            "组件证据覆盖不等于答案正确；新标签待审，默认不采用",
        )
        print(result)
    except Exception as exc:
        record_operation("参数筛选中止", "保留冻结与失败，不追加试跑", str(a.output), str(exc))
        raise
