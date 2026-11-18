"""Native retrieval end-to-end paired pagination experiment; frozen dev sources only."""

import argparse
import copy
import json
import math
import statistics
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from fastapi.testclient import TestClient
from operation_log import ROOT, record_operation
from prepare_corpus_pilot import load, save

from infra_rag.api import create_app
from infra_rag.assistant import AnswerService, ConversationStore
from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.config import Settings
from infra_rag.encoding import BGEEncoder
from infra_rag.model_clients import configured_model
from infra_rag.offline_evaluation import RecordingModel
from infra_rag.service import RetrievalService

SELECTION = ROOT / "data/structural-chunk-pilot-v1/run-20261028-v2/selection.json"
CASES = ROOT / "data/bilingual-protected-v1/run-20261028/questions.json"
MODELS = ROOT / "data/query-language-v1/run-20261028/protocol.json"
REVIEW = ROOT / "evals/retrieval-diagnostic-v2/audit-20261028-v2-reviewed/review-manifest.json"
SMOKE = ("diag-013", "diag-025", "diag-029", "diag-008")


def schedule(cases):
    ordered = sorted(
        cases, key=lambda c: (SMOKE.index(c["id"]) if c["id"] in SMOKE else 4, c["id"])
    )
    return [
        {"id": c["id"], "enabled": enabled, "stage": "smoke" if c["id"] in SMOKE else "full"}
        for i, c in enumerate(ordered)
        for enabled in ((False, True) if i % 2 == 0 else (True, False))
    ]


def settings(out, models):
    return Settings(
        data_dir=out / "index",
        backend="bge",
        embedding_revision=models["embedding"]["revision"],
        embedding_model=models["embedding"]["model"],
        rerank=True,
        reranker_model=models["reranker"]["model"],
        chunk_size=450,
        chunk_strategy="semantic",
        candidate_k=30,
        fusion_candidates="union",
        context_tokens=1200,
        context_chars=4000,
        context_mode="neighbors",
        query_language="none",
    )


def local_models(service, models):
    from sentence_transformers import CrossEncoder, SentenceTransformer

    encoder = BGEEncoder.__new__(BGEEncoder)
    encoder.model = SentenceTransformer(models["embedding"]["path"], local_files_only=True)
    encoder.instruction = "为这个句子生成表示以用于检索相关文章："
    encoder.batch_size = 16
    service.encoder = encoder
    service.reranker = CrossEncoder(
        models["reranker"]["path"], local_files_only=True, max_length=512
    )


def verify_inputs(protocol):
    for name, sha in {**protocol["inputs"], **protocol["implementation"]}.items():
        if digest(ROOT / name) != sha:
            raise ValueError("Frozen file changed: " + name)
    for row in protocol["sources"]:
        if digest(ROOT / row["input_path"]) != row["input_sha256"]:
            raise ValueError("Source changed")
    if configured_model().configuration() != protocol["answer_model"]:
        raise ValueError("Answer model changed")


def prepare(out):
    sources = load(SELECTION)
    cases = load(CASES)
    models = load(MODELS)["models"]
    if len(sources) != 24 or len(cases) != 30:
        raise ValueError("Expected 24 sources and 30 cases")
    manifest = load(REVIEW)
    for e in (manifest["template"], manifest["human_review"], *manifest["evidence"].values()):
        if digest(ROOT / e["path"]) != e["sha256"]:
            raise ValueError("Review integrity failure")
    reviews = {r["id"]: r for r in load(ROOT / manifest["human_review"]["path"])}
    for c in cases:
        if reviews[c["id"]]["case_sha256"] != canonical_hash(c):
            raise ValueError("Review case mismatch")
    for row in sources:
        source = ROOT / row["input_path"]
        if digest(source) != row["input_sha256"]:
            raise ValueError("Source identity mismatch")
        target = out / "corpus" / (row["document_id"] + ".md")
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and digest(target) != digest(source):
            raise ValueError("Staged source changed")
        if not target.exists():
            target.write_bytes(source.read_bytes())
    for kind in ("embedding", "reranker"):
        for name, sha in models[kind]["files"].items():
            if digest(Path(models[kind]["path"]) / name) != sha:
                raise ValueError("Model changed")
    config = settings(out, models)
    files = [
        Path(__file__).resolve(),
        *[
            ROOT / f"src/infra_rag/{n}.py"
            for n in (
                "api",
                "assistant",
                "service",
                "config",
                "chunking",
                "text_chunking",
                "encoding",
                "context",
                "experimental_pages",
                "paged_answers",
                "model_clients",
                "offline_evaluation",
            )
        ],
    ]
    protocol = {
        "inputs": {str(p.relative_to(ROOT)): digest(p) for p in (SELECTION, CASES, MODELS, REVIEW)},
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in files},
        "sources": sources,
        "models": models,
        "settings": {**asdict(config), "data_dir": str(config.data_dir)},
        "answer_model": configured_model().configuration(),
        "requests": 60,
        "max_model_calls": 480,
        "statistics": "Independent human only; cluster bootstrap10000 seed42 and sign test",
        "timing": "Warm local models, fresh query encoding/search/rerank; no result replay",
        "retries": "No transport retry; max2 format attempts; interrupted requests block resume",
        "gate": "Stop on execution, telemetry, citation, budget or paired-ranking error",
        "human_answer_review": "pending",
        "default_changed": False,
    }
    save(out / "protocol.json", protocol)
    save(out / "questions.json", cases)
    save(out / "schedule.json", schedule(cases))
    for p in files:
        dest = out / "implementation" / p.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and digest(dest) != digest(p):
            raise ValueError("Snapshot changed")
        if not dest.exists():
            dest.write_bytes(p.read_bytes())
    service = RetrievalService(config)
    local_models(service, models)
    service.ingest(out / "corpus", "infra")
    save(
        out / "index-manifest.json",
        {
            "index_sha256": digest(out / "index/index.json"),
            "chunks": len(service.chunks),
            "sources": len(service.source_manifest),
            "fingerprint": service.settings.fingerprint(),
            "staged_sources": {p.name: digest(p) for p in (out / "corpus").glob("*.md")},
        },
    )
    # Gold remains source-bound. Native span judgments are not inferred from old chunk IDs.
    save(
        out / "source-locators.json",
        [
            {
                "document_id": r["document_id"],
                "native_source": str((out / "corpus" / (r["document_id"] + ".md")).resolve()),
                "original_path": r["input_path"],
                "input_sha256": r["input_sha256"],
                "source_url": r["source_url"],
                "commit": r["commit"],
            }
            for r in sources
        ],
    )
    return {
        "phase": "prepared",
        "chunks": len(service.chunks),
        "sources": len(service.source_manifest),
    }


class ObservedRetrieval:
    def __init__(self, service):
        self.service = service
        self.events = []

    def __getattr__(self, name):
        return getattr(self.service, name)

    def search(self, query, **kwargs):
        diagnostics = {}
        hits = self.service.search(query, diagnostics=diagnostics, **kwargs)
        self.events.append(
            {
                "query": query,
                "diagnostics": diagnostics,
                "hits": [asdict(h) for h in hits],
                "context": copy.deepcopy(kwargs["context_pack"]),
            }
        )
        return hits


def summarise(out):
    rows = [
        load(p)
        for p in (out / "rows").glob("*.json")
        if not p.name.endswith((".sha256.json", ".started.json"))
    ]
    summary = {
        "planned": 60,
        "recorded": len(rows),
        "missing": 60 - len(rows),
        "answer_accuracy": None,
        "independent_answer_review": "pending",
        "groups": {},
    }
    for enabled in (False, True):
        group = [r for r in rows if r["enabled"] == enabled]
        lat = sorted(r["elapsed_ms"] for r in group)
        calls = [c for r in group for c in r["calls"]]
        usage = [c.get("provider_response", {}).get("usage") for c in calls]
        summary["groups"][str(enabled)] = {
            "n": len(group),
            "answered": sum(r["response"].get("status") == "answered" for r in group),
            "context_incomplete": sum(
                r["response"].get("status") == "context_incomplete" for r in group
            ),
            "execution_errors": sum(r["http_status"] != 200 for r in group),
            "model_calls": len(calls),
            "usage_measured": sum(u is not None for u in usage),
            "cost_usd": None,
            "measured_input_tokens": sum(u.get("input_tokens", 0) for u in usage if u),
            "measured_output_tokens": sum(u.get("output_tokens", 0) for u in usage if u),
            "p50_ms": statistics.median(lat) if lat else None,
            "p95_ms": lat[math.ceil(0.95 * len(lat)) - 1] if lat else None,
        }
    save(out / f"summary-{len(rows)}.json", summary)
    save(
        out / f"answer-review-template-{len(rows)}.json",
        [
            {
                "id": r["id"],
                "enabled": r["enabled"],
                "status": "pending",
                "case_sha256": r["case_sha256"],
                "trace_sha256": digest(out / "rows" / f"{r['id']}-{r['enabled']}.json"),
                "reviewer": None,
                "strict_correct": None,
                "all_required_claims": None,
                "citations_supported": None,
                "source_claim_inventory_complete": None,
                "reason": None,
            }
            for r in rows
        ],
    )
    return summary


def execute(out, stage):
    protocol = load(out / "protocol.json")
    verify_inputs(protocol)
    if digest(out / "index/index.json") != load(out / "index-manifest.json")["index_sha256"]:
        raise ValueError("Native index changed")
    service = RetrievalService(settings(out, protocol["models"]))
    local_models(service, protocol["models"])
    service._collections(service.chunks, service.vectors)  # native ANN warm-up, no evaluation query
    cases = {c["id"]: c for c in load(out / "questions.json")}
    for job in load(out / "schedule.json"):
        if stage == "smoke" and job["stage"] != "smoke":
            continue
        target = out / "rows" / f"{job['id']}-{job['enabled']}.json"
        if target.exists():
            if digest(target) != load(target.with_suffix(".sha256.json"))["sha256"]:
                raise ValueError("Checkpoint changed")
            continue
        if (out / "gate-failure.json").exists():
            raise ValueError("Run stopped at frozen hard gate")
        if target.with_suffix(".started.json").exists():
            raise ValueError("Interrupted request; audit before resuming")
        save(target.with_suffix(".started.json"), job)
        retrieval = ObservedRetrieval(service)
        model = RecordingModel(configured_model())
        started = perf_counter()
        try:
            with TemporaryDirectory() as tmp:
                assistant = AnswerService(
                    retrieval, model, ConversationStore(Path(tmp) / "history.sqlite")
                )
                response = TestClient(create_app(retrieval, assistant)).post(
                    "/chat",
                    json={
                        "message": cases[job["id"]]["query"],
                        "experimental_pagination": job["enabled"],
                    },
                )
                http, body = response.status_code, response.json()
        except Exception as exc:
            http, body = 500, {"error": type(exc).__name__}
        row = {
            **job,
            "case_sha256": canonical_hash(cases[job["id"]]),
            "http_status": http,
            "response": body,
            "retrieval": retrieval.events,
            "calls": model.calls,
            "elapsed_ms": (perf_counter() - started) * 1000,
            "semantic_correct": None,
        }
        save(target, row)
        save(target.with_suffix(".sha256.json"), {"sha256": digest(target)})
        errors = []
        if http != 200 or len(retrieval.events) != 1:
            errors.append("HTTP or retrieval execution failure")
        if any("error" in c for c in model.calls):
            errors.append("Model execution failure")
        if job["enabled"] and len(model.calls) > 14:
            errors.append("Model call cap")
        allowed = {
            e["citation_id"]
            for e in (
                next(
                    (t for t in body.get("trace", []) if t["step"] == "pack_verified_quotes"), {}
                ).get("evidence", [])
                if job["enabled"]
                else retrieval.events[0]["context"].get("evidence", [])
                if retrieval.events
                else []
            )
        }
        if any(e["citation_id"] not in allowed for e in body.get("citations", [])):
            errors.append("Citation outside actual evidence")
        for t in body.get("trace", []):
            if t["step"] == "pack_verified_quotes" and (
                t["characters"] > 4000 or any(n > 1200 for n in t["token_counts"].values())
            ):
                errors.append("Context budget violation")
        other = out / "rows" / f"{job['id']}-{not job['enabled']}.json"
        if other.exists() and retrieval.events:
            previous = load(other)
            if previous["retrieval"][0]["diagnostics"]["candidates"] != retrieval.events[0][
                "diagnostics"
            ]["candidates"] or [h["chunk"]["id"] for h in previous["retrieval"][0]["hits"]] != [
                h["chunk"]["id"] for h in retrieval.events[0]["hits"]
            ]:
                errors.append("Paired candidate/ranking mismatch")
        print(job["id"], job["enabled"], http, body.get("status"), flush=True)
        if errors:
            save(out / "gate-failure.json", {"job": job, "errors": errors})
            summarise(out)
            raise ValueError("Frozen gate stopped run: " + str(errors))
    verify_inputs(protocol)
    return summarise(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=("prepare", "smoke", "full", "summary"), required=True)
    args = parser.parse_args()
    try:
        out = args.output.resolve()
        result = (
            prepare(out)
            if args.phase == "prepare"
            else summarise(out)
            if args.phase == "summary"
            else execute(out, args.phase)
        )
        record_operation(
            "原生检索跨页配对实验 " + args.phase,
            "固定24来源、原中文、独立索引",
            str(result),
            "答案待独立审核；不与旧双语成绩直接比较",
        )
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        record_operation("原生跨页实验中止", "保留失败请求和冻结协议", str(args.output), str(exc))
        raise
