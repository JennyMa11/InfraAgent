"""Frozen dev-only 2x3 embedding/chunk comparison and bounded answer probe.

Run --phase freeze before any evaluation. Every subsequent phase verifies inputs and
implementation. New code/configuration requires a new output directory, never --force.
"""

import argparse
import copy
import gc
import importlib.metadata
import json
import os
import re
import resource
import shutil
from collections import Counter
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from operation_log import record_operation

from infra_rag.assistant import SYSTEM_PROMPT
from infra_rag.benchmarking import canonical_hash, digest, write_new
from infra_rag.config import Settings
from infra_rag.embedding_experiments import (
    BASELINE,
    CHUNK_ARMS,
    MODEL_ARMS,
    VERSION,
    chunk_evidence,
    chunk_variants,
    delivered_intervals,
    deserialize_chunks,
    deterministic_sample,
    freeze_gold,
    interval_score,
    ratio,
    score_evidence,
    select_candidate,
    serialize_chunks,
    source_document,
)
from infra_rag.encoding import BGEEncoder, QwenEncoder, dot
from infra_rag.evaluation import metrics
from infra_rag.model_clients import configured_model
from infra_rag.offline_evaluation import generate_answer, latency_summary
from infra_rag.paired_statistics import holm, paired_statistics
from infra_rag.service import RetrievalService

ROOT = Path(__file__).resolve().parents[1]
PRIOR = ROOT / "evals/merged-corpus-v2/recall-delivery-v4/run-20261002"
MODEL_IDS = {
    "bge": "BAAI/bge-small-zh-v1.5",
    "qwen": "Qwen/Qwen3-Embedding-0.6B",
    "reranker": "BAAI/bge-reranker-base",
}
PHASES = ("freeze", "prepare", "index", "retrieve", "latency", "answer", "review", "report")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path, value):
    path = Path(path)
    if path.exists():
        if load(path) != value:
            raise ValueError(f"Frozen artifact differs: {path}; use a new run directory")
    else:
        write_new(path, value)


def append(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def rows(path):
    return (
        [json.loads(line) for line in Path(path).read_text().splitlines()]
        if Path(path).exists()
        else []
    )


def release():
    gc.collect()
    import torch

    if torch.backends.mps.is_available():
        torch.mps.empty_cache()


def sync(device):
    if device == "mps":
        import torch

        torch.mps.synchronize()


def peak_rss():
    # macOS reports bytes; Linux reports KiB. This is a process lifetime high-water mark.
    import sys

    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (
        1 if sys.platform == "darwin" else 1024
    )


class BudgetTokenizer:
    """Keep chunk boundaries and evidence budgets independent of the tested embedding."""

    token_limit = 510

    def __init__(self, path):
        from transformers import AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)

    def token_length(self, text):
        return len(self.tokenizer.encode(text, add_special_tokens=False))


def encoder_for(protocol, name):
    info = protocol["models"][name]
    cls = BGEEncoder if name == "bge" else QwenEncoder
    return cls(info["path"], device=protocol["device"], batch_size=2)


def resolve_model(name, revision=None):
    from huggingface_hub import snapshot_download

    folder = Path(
        snapshot_download(
            MODEL_IDS[name],
            revision=revision,
            local_files_only=True,
            allow_patterns=["*.json", "*.safetensors", "*.txt", "*.model", "*.tiktoken"],
        )
    )
    files = {
        str(p.relative_to(folder)): digest(p)
        for p in sorted(folder.rglob("*"))
        if p.is_file() and p.suffix in {".json", ".safetensors", ".txt", ".model"}
    }
    if not any(k.endswith(".safetensors") for k in files):
        raise ValueError(f"{name}: complete official model snapshot is required")
    return {"model": MODEL_IDS[name], "path": str(folder), "revision": folder.name, "files": files}


def normalized_cases():
    cases, inputs = [], {}
    for dataset, folder in (
        ("official", "infra-official-v1-reviewed"),
        ("repository", "repository-benchmark"),
    ):
        path = ROOT / "evals" / folder / "dev.json"
        inputs[str(path)] = digest(path)
        for original in load(path):
            case = copy.deepcopy(original)
            case["dataset"] = dataset
            case.setdefault("answerable", True)
            if "evidence_alternatives" not in case:
                case["evidence_alternatives"] = [
                    {"id": "original", "spans": case["relevant_spans"]}
                ]
            for group in case["evidence_alternatives"]:
                for span in group["spans"]:
                    span["absolute_source"] = str((path.parent / span["source"]).resolve())
            case["case_sha256"] = canonical_hash(original)
            cases.append(case)
    if len(cases) != 110 or sum(c["answerable"] for c in cases) != 104:
        raise ValueError("Expected unchanged 60/50 dev cases and 104 answerable cases")
    return cases, inputs


def reuse_profiles(source, models):
    """Reuse only verified vectors, never quality/timing/answer results from another run."""
    old = load(source / "protocol.json")
    if (source / "protocol.sha256").read_text().strip() != digest(source / "protocol.json"):
        raise ValueError("reuse protocol hash mismatch")
    if old["models"] != models:
        raise ValueError("reuse requires identical frozen model files")
    for name, expected in old["implementation"].items():
        if name == "scripts/benchmark_embedding_chunks.py":
            continue
        if digest(ROOT / name) != expected:
            raise ValueError(f"encoding/chunk implementation changed; cannot reuse {name}")
    for name, expected in old["inputs"].items():
        if digest(name) != expected:
            raise ValueError("reuse source input changed")
    inputs = {str(source / "protocol.json"): digest(source / "protocol.json")}
    for stage in ("prepare", "index"):
        manifest = source / f"{stage}-manifest.json"
        inputs[str(manifest)] = digest(manifest)
        for name, expected in load(manifest).items():
            path = source / name
            if digest(path) != expected:
                raise ValueError(f"reuse artifact changed: {path}")
            inputs[str(path)] = expected
    profiles = {}
    for model in MODEL_ARMS:
        for arm in CHUNK_ARMS:
            key = f"{model}-{arm}"
            profiles[key] = {
                "snapshot": str(source / "indexes" / key / "index.json"),
                "info": str(source / "index-info" / f"{key}.json"),
                "chunks_sha256": digest(source / "chunks" / f"{arm}.json"),
            }
    return profiles, inputs


def seed_verified_index(service, chunks, profile):
    state = load(profile["snapshot"])
    if state["fingerprint"] != service.settings.fingerprint():
        raise ValueError("reuse index fingerprint mismatch")
    if canonical_hash(state["chunks"]) != canonical_hash(serialize_chunks(chunks)):
        raise ValueError("reuse chunk content/provenance mismatch")
    if len(state["vectors"]) != len(chunks):
        raise ValueError("reuse vector count mismatch")
    # _commit validates vector dimensions/finiteness via VectorCache, then creates a
    # fresh Chroma collection. No old search results or HNSW runtime state is reused.
    service.chunks = deserialize_chunks(state["chunks"])
    service.vectors = state["vectors"]


def freeze(run, reuse=None):
    if (run / "protocol.json").exists():
        return verify(run)
    if run.exists() and any(run.iterdir()):
        raise ValueError("freeze requires a fresh output directory")
    prior = load(PRIOR / "protocol.json")
    models = {
        name: resolve_model(
            name,
            prior["models"]["embedding" if name == "bge" else name]["revision"]
            if name != "qwen"
            else None,
        )
        for name in MODEL_IDS
    }
    cases, inputs = normalized_cases()
    corpus = ROOT / prior["directory"] / "chunks.json"
    inputs[str(corpus)] = digest(corpus)
    audit = load(PRIOR / "source-audit.json")
    if digest(corpus) != audit["prepared_chunks_sha256"]:
        raise ValueError("historical structural chunks differ from frozen source audit")
    inputs[str(PRIOR / "protocol.json")] = digest(PRIOR / "protocol.json")
    inputs[str(PRIOR / "source-audit.json")] = digest(PRIOR / "source-audit.json")
    for item in audit["source_files"]:
        if digest(item["source"]) != item["expected"]:
            raise ValueError("frozen corpus source changed")
        inputs[item["source"]] = item["expected"]
    client = configured_model()
    if not hasattr(client, "configuration"):
        raise ValueError("This protocol requires the currently configured external answer API")
    client.timeout = 45
    protocol = {
        "kind": VERSION,
        "run_id": run.name,
        "created_at": datetime.now(UTC).isoformat(),
        "models": models,
        "inputs": inputs,
        "original_chunks": str(corpus),
        "source_audit": str(PRIOR / "source-audit.json"),
        "cases": cases,
        "answer_sample": deterministic_sample(cases),
        "answer_configuration": client.configuration(),
        "answer_prompt_sha256": canonical_hash(SYSTEM_PROMPT),
        "seed": 42,
        "bootstrap_samples": 10000,
        "query_language": "none",
        "chunk_arms": list(CHUNK_ARMS),
        "chunk_size_characters": 450,
        "overlap_characters": 90,
        "batch_size": 2,
        "dtype": "float32",
        "qwen_max_length": 8192,
        "candidates_per_channel": 30,
        "fusion": "union",
        "rrf_constant": 60,
        "rank_k": 5,
        "context_tokens": 1200,
        "context_characters": 4000,
        "context_tokenizer": models["bge"]["revision"],
        "retrieval_configs": [
            f"{m}-{c}-{s}"
            for m in MODEL_ARMS
            for c in CHUNK_ARMS
            for s in ("dense", "hybrid_rerank")
        ]
        + [f"bm25-{c}" for c in CHUNK_ARMS],
        "repetitions": 2,
        "answer_expected_outputs": 80,
        "max_generation_requests": 160,
        "generation_timeout_seconds": 45,
        "max_generation_attempts_per_output": 2,
        "quality_gate": "per-dataset delivery nondecreasing and combined net gain >=2",
        "latency_gate": "warm p95 <= 1.5x baseline",
        "holdout_test_read": False,
        "default_changed": False,
        "independent_review": "pending",
        "implementation": {
            str(p.relative_to(ROOT)): digest(p)
            for p in [
                *sorted((ROOT / "src/infra_rag").glob("*.py")),
                Path(__file__),
                ROOT / "scripts/operation_log.py",
                ROOT / "pyproject.toml",
                ROOT / "uv.lock",
            ]
        },
        "packages": {
            p: importlib.metadata.version(p)
            for p in ("torch", "transformers", "sentence-transformers", "chromadb", "jieba")
        },
    }
    if reuse is not None:
        profiles, reuse_inputs = reuse_profiles(reuse, models)
        protocol["reuse_indexes"] = profiles
        protocol["inputs"].update(reuse_inputs)
    import torch

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    smoke = []
    # Device selection happens before any benchmark result exists. On failure, retry
    # both models on CPU, never combine timings measured on different devices.
    for candidate_device in dict.fromkeys((device, "cpu")):
        protocol["device"] = candidate_device
        passed = True
        for name in MODEL_ARMS:
            encoder = None
            started = perf_counter()
            try:
                encoder = encoder_for(protocol, name)
                docs = encoder.encode(
                    ["PagedAttention stores KV Cache in blocks.", "AllReduce combines gradients."]
                )
                query = encoder.encode(["How does PagedAttention manage KV Cache?"], query=True)[0]
                sync(candidate_device)
                smoke.append(
                    {
                        "model": name,
                        "device": candidate_device,
                        "dimension": len(query),
                        "similarities": [dot(query, v) for v in docs],
                        "error": None,
                        "elapsed_seconds": perf_counter() - started,
                    }
                )
            except Exception as exc:
                passed = False
                smoke.append(
                    {
                        "model": name,
                        "device": candidate_device,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
            finally:
                del encoder
                release()
        if passed:
            break
    else:
        raise ValueError(f"Both-model preflight failed: {smoke}")
    protocol["preflight"] = smoke
    run.mkdir(parents=True, exist_ok=True)
    save(run / "protocol.json", protocol)
    (run / "protocol.sha256").write_text(digest(run / "protocol.json") + "\n")
    for name in protocol["implementation"]:
        target = run / "implementation" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    return protocol


def verify(run):
    if (run / "protocol.sha256").read_text().strip() != digest(run / "protocol.json"):
        raise ValueError("frozen protocol changed")
    protocol = load(run / "protocol.json")
    if protocol["kind"] != VERSION:
        raise ValueError("wrong experiment protocol")
    for name, expected in protocol["implementation"].items():
        if digest(ROOT / name) != expected:
            raise ValueError(f"Implementation changed: {name}; create a new run")
    for name, expected in protocol["inputs"].items():
        if digest(name) != expected:
            raise ValueError(f"Frozen input changed: {name}")
    for model in protocol["models"].values():
        for name, expected in model["files"].items():
            if digest(Path(model["path"]) / name) != expected:
                raise ValueError(f"Frozen model file changed: {name}")
    for stage in ("prepare", "index", "retrieve", "latency", "answer"):
        manifest = run / f"{stage}-manifest.json"
        if manifest.exists():
            for name, expected in load(manifest).items():
                if digest(run / name) != expected:
                    raise ValueError(f"Frozen phase output changed: {name}")
    return protocol


def finish(run, stage, paths):
    save(run / f"{stage}-manifest.json", {str(p.relative_to(run)): digest(p) for p in paths})


def prepared(run):
    return load(run / "sources.json"), load(run / "cases.json")


def prepare(run, protocol):
    if (run / "prepare-manifest.json").exists():
        return
    original = deserialize_chunks(load(protocol["original_chunks"]))
    documents = {
        source: source_document(Path(source).read_text(), protocol["inputs"][source])
        for source in sorted({c.source for c in original})
    }
    counter = BudgetTokenizer(protocol["models"]["bge"]["path"])
    variants = chunk_variants(original, documents, counter)
    cases = copy.deepcopy(protocol["cases"])
    for case in cases:
        case["gold_intervals"] = freeze_gold(case, documents)
    paths = [run / "sources.json", run / "cases.json"]
    save(paths[0], documents)
    save(paths[1], cases)
    for name, chunks in variants.items():
        path = run / "chunks" / f"{name}.json"
        save(path, serialize_chunks(chunks))
        paths.append(path)
        full_intervals = delivered_intervals([chunk_evidence(c) for c in chunks], documents)
        for case in cases:
            if case["answerable"]:
                score = interval_score(full_intervals, case["gold_intervals"])
                if not score["complete"]:
                    raise ValueError(f"{name}/{case['id']}: full corpus does not cover frozen gold")
        print("prepared", name, len(chunks), flush=True)
    finish(run, "prepare", paths)


def settings_for(run, protocol, model, arm):
    info = protocol["models"][model]
    return Settings(
        backend=model,
        embedding_model=info["model"],
        embedding_revision=info["revision"],
        embedding_device=protocol["device"],
        embedding_batch_size=2,
        data_dir=run / "indexes" / f"{model}-{arm}",
        preprocessing_version=f"{VERSION}-{arm}",
        chunk_strategy="window_overlap"
        if arm == "overlap"
        else "window"
        if arm == "window"
        else "semantic",
        chunk_overlap=90 if arm == "overlap" else 0,
        fusion_candidates="union",
        query_language="none",
    )


def index(run, protocol):
    if (run / "index-manifest.json").exists():
        return
    paths = []
    for model in MODEL_ARMS:
        encoder = encoder_for(protocol, model)
        if model == "qwen":
            # Validate the complete input set before publishing any Qwen index.
            for arm in CHUNK_ARMS:
                for c in load(run / "chunks" / f"{arm}.json"):
                    if encoder.token_length(c["content"]) + 2 > encoder.model.max_seq_length:
                        raise ValueError("Qwen corpus input exceeds frozen limit")
            for case in protocol["cases"]:
                if encoder.token_length(encoder.query_prompt + case["query"]) + 2 > 8192:
                    raise ValueError("Qwen query exceeds frozen limit")
        for arm in CHUNK_ARMS:
            info_path = run / "index-info" / f"{model}-{arm}.json"
            settings = settings_for(run, protocol, model, arm)
            chunks = deserialize_chunks(load(run / "chunks" / f"{arm}.json"))
            service = RetrievalService(settings)
            if info_path.exists():
                if canonical_hash(serialize_chunks(service.chunks)) != canonical_hash(
                    serialize_chunks(chunks)
                ):
                    raise ValueError("resumed index has different chunks")
            else:
                service.encoder = encoder
                reuse = protocol.get("reuse_indexes", {}).get(f"{model}-{arm}")
                if reuse:
                    if digest(run / "chunks" / f"{arm}.json") != reuse["chunks_sha256"]:
                        raise ValueError("prepared chunks differ from reusable index")
                    seed_verified_index(service, chunks, reuse)
                started = perf_counter()
                service._commit(chunks)
                sync(protocol["device"])
                save(
                    info_path,
                    {
                        "fingerprint": settings.fingerprint(),
                        "chunks": len(chunks),
                        "dimension": len(service.vectors[0]),
                        "build_seconds": perf_counter() - started,
                        "vector_cache": service.last_update,
                        "reused_vectors_from": reuse["snapshot"] if reuse else None,
                        "origin_build_info": load(reuse["info"]) if reuse else None,
                        "peak_process_rss_bytes": peak_rss(),
                        "snapshot_sha256": digest(service.snapshot),
                        "directory_bytes": sum(
                            p.stat().st_size for p in settings.data_dir.rglob("*") if p.is_file()
                        ),
                    },
                )
                print("indexed", model, arm, len(chunks), flush=True)
            paths.extend((info_path, service.snapshot))
            del service
            release()
        del encoder
        release()
    finish(run, "index", paths)


def service_for(run, protocol, model, arm, counter, encoder, reranker=None):
    service = RetrievalService(
        settings_for(run, protocol, model, arm), context_counter=counter.token_length
    )
    service.encoder, service.reranker = encoder, reranker
    service._frozen_chunks = {c.id: c for c in service.chunks}
    return service


def evaluate_query(service, case, name, strategy, documents):
    diagnostics, context = {}, {}
    started = perf_counter()
    try:
        service.search(
            case["query"],
            top_k=5,
            domain="infra",
            modality="text",
            strategy=strategy,
            diagnostics=diagnostics,
            context_pack=context,
        )
        sync(service.settings.embedding_device)
        elapsed = (perf_counter() - started) * 1000
        chunks = service._frozen_chunks
        ranked = diagnostics.get("ranked_ids", [])
        candidate_evidence = [
            chunk_evidence(chunks[cid]) for cid in diagnostics.get("candidates", [])
        ]
        top_evidence = [chunk_evidence(chunks[cid]) for cid in ranked[:5]]
        relevant = []
        if case["answerable"]:
            gold_sources = {r["source"] for g in case["gold_intervals"] for r in g}
            for chunk in service.chunks:
                if chunk.source not in gold_sources:
                    continue
                ranges = delivered_intervals([chunk_evidence(chunk)], documents).get(
                    chunk.source, []
                )
                if any(
                    a < end and b > start
                    for g in case["gold_intervals"]
                    for r in g
                    if r["source"] == chunk.source
                    for start, end in r["occurrences"]
                    for a, b in ranges
                ):
                    relevant.append(chunk.id)
        return {
            "dataset": case["dataset"],
            "id": case["id"],
            "group_id": case["group_id"],
            "config": name,
            "answerable": case["answerable"],
            "error": None,
            "candidate_complete": score_evidence(candidate_evidence, case, documents),
            "ranked_complete": score_evidence(top_evidence, case, documents),
            "delivered": score_evidence(context["evidence"], case, documents),
            "at_k": {str(k): metrics(ranked, relevant, k) for k in (5, 10)} if relevant else None,
            "ranked_ids": ranked,
            "candidate_ids": diagnostics.get("candidates", []),
            "actual_context": context,
            "diagnostics": diagnostics,
            "latency_ms": elapsed,
            "peak_process_rss_bytes": peak_rss(),
        }
    except Exception as exc:
        return {
            "dataset": case["dataset"],
            "id": case["id"],
            "group_id": case["group_id"],
            "config": name,
            "answerable": case["answerable"],
            "error": f"{type(exc).__name__}: {exc}",
            "candidate_complete": {"complete": 0},
            "ranked_complete": {"complete": 0},
            "delivered": {"complete": 0},
            "actual_context": None,
            "latency_ms": (perf_counter() - started) * 1000,
        }


def retrieve(run, protocol, *, timing=False):
    stage = "latency" if timing else "retrieve"
    if (run / f"{stage}-manifest.json").exists():
        return
    documents, cases = prepared(run)
    counter = BudgetTokenizer(protocol["models"]["bge"]["path"])
    paths = []
    for model in MODEL_ARMS:
        encoder = encoder_for(protocol, model)
        from sentence_transformers import CrossEncoder

        reranker = CrossEncoder(protocol["models"]["reranker"]["path"], device=protocol["device"])
        for arm in CHUNK_ARMS:
            service = service_for(run, protocol, model, arm, counter, encoder, reranker)
            strategies = [
                (f"{model}-{arm}-dense", "dense", False),
                (f"{model}-{arm}-hybrid_rerank", "hybrid", True),
            ]
            if not timing and model == "bge":
                strategies.append((f"bm25-{arm}", "bm25", False))
            for name, strategy, rerank in strategies:
                path = run / stage / f"{name}.jsonl"
                done_rows = rows(path)
                keys = [(r["dataset"], r["id"], r.get("repetition", 1)) for r in done_rows]
                expected = {
                    (c["dataset"], c["id"], repetition)
                    for c in cases
                    for repetition in ((1, 2) if timing else (1,))
                }
                if len(keys) != len(set(keys)) or not set(keys) <= expected:
                    raise ValueError("unknown/duplicate retrieval task")
                done = set(keys)
                service.settings = replace(service.settings, rerank=rerank)
                if timing:
                    service.search(
                        "KV Cache", top_k=5, domain="infra", modality="text", strategy=strategy
                    )
                    sync(protocol["device"])
                for repetition in (1, 2) if timing else (1,):
                    ordered = cases if repetition == 1 else cases[::-1]
                    for case in ordered:
                        if (case["dataset"], case["id"], repetition) in done:
                            continue
                        row = evaluate_query(service, case, name, strategy, documents)
                        row["run_id"] = protocol.get("run_id", run.name)
                        row["repetition"] = repetition
                        append(path, row)
                paths.append(path)
                print(stage, name, len(rows(path)), flush=True)
            del service
            release()
        del encoder, reranker
        release()
    finish(run, stage, paths)


def summaries(run, protocol):
    result = {}
    for name in protocol["retrieval_configs"]:
        records = rows(run / "retrieve" / f"{name}.jsonl")
        if len(records) != 110:
            raise ValueError(f"Incomplete retrieval configuration: {name}")
        row = {"errors": sum(bool(r["error"]) for r in records)}
        for dataset in ("official", "repository"):
            selected = [r for r in records if r["dataset"] == dataset and r["answerable"]]
            row[dataset] = {
                metric: ratio(sum(r[field]["complete"] for r in selected), len(selected))
                for metric, field in (
                    ("delivery", "delivered"),
                    ("candidate_complete", "candidate_complete"),
                    ("ranked_complete", "ranked_complete"),
                )
            }
            row[dataset]["auxiliary_chunk_metrics"] = {
                str(k): {
                    metric: ratio(
                        sum((r.get("at_k") or {}).get(str(k), {}).get(metric, 0) for r in selected),
                        len(selected),
                    )
                    for metric in ("recall", "precision", "mrr", "ndcg")
                }
                for k in (5, 10)
            }
            row[dataset]["auxiliary_note"] = (
                "Overlap with authored source spans; chunk granularity dependent"
            )
        timed = rows(run / "latency" / f"{name}.jsonl")
        row["warm_latency"] = (
            latency_summary([r["latency_ms"] for r in timed]) if len(timed) == 220 else None
        )
        row["warm_latency_n"] = len(timed)
        if any(r["error"] for r in timed):
            row["errors"] += sum(bool(r["error"]) for r in timed)
        result[name] = row
    return result


class LedgerClient:
    """Reserve request slots durably before HTTP; never repay a failed attempt's budget."""

    def __init__(self, client, run, task, maximum=160):
        self.client, self.run, self.task, self.maximum = client, run, task, maximum
        self.provider, self.model = client.provider, client.model
        self.last_call = None

    def generate(self, messages):
        ledger = self.run / "model-calls.jsonl"
        started_calls = [r for r in rows(ledger) if r["event"] == "started"]
        if len(started_calls) >= self.maximum:
            raise ValueError("frozen generation request budget exhausted")
        call_id = len(started_calls) + 1
        start = perf_counter()
        append(
            ledger,
            {
                "event": "started",
                "run_id": self.run.name,
                "call_id": call_id,
                "task": self.task,
                "messages_sha256": canonical_hash(messages),
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )
        self.client.last_call = None
        record = {"event": "finished", "call_id": call_id, "task": self.task}
        try:
            response = self.client.generate(messages)
            record["raw"] = response
            return response
        except Exception as exc:
            record["error"] = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            self.last_call = self.client.last_call
            record.update(
                provider_response=self.last_call,
                latency_ms=(perf_counter() - start) * 1000,
                model_cost_usd=None,
            )
            append(ledger, redact(record, getattr(self.client, "_token", "")))


def redact(value, token):
    if not token:
        return value
    return json.loads(json.dumps(value, ensure_ascii=False).replace(token, "[redacted]"))


def answer(run, protocol):
    if (run / "answer-manifest.json").exists():
        return
    summary = summaries(run, protocol)
    decision = select_candidate(summary)
    save(run / "decision.json", decision)
    configs = (BASELINE, decision["candidate"])
    contexts = {
        name: {(r["dataset"], r["id"]): r for r in rows(run / "retrieve" / f"{name}.jsonl")}
        for name in configs
    }
    _, cases = prepared(run)
    cases = {(c["dataset"], c["id"]): c for c in cases}
    tasks = []
    for repetition in (1, 2):
        for i, pair in enumerate(protocol["answer_sample"]):
            for config in configs if (i + repetition) % 2 else configs[::-1]:
                tasks.append(
                    {"dataset": pair[0], "id": pair[1], "config": config, "repetition": repetition}
                )
    save(run / "answer-tasks.json", tasks)
    client = configured_model()
    client.timeout = 45
    if client.configuration() != protocol["answer_configuration"]:
        raise ValueError("answer provider/model/options changed since freeze")
    previous = rows(run / "answers.jsonl")
    expected = {canonical_hash(t) for t in tasks}
    keys = [canonical_hash({k: r[k] for k in tasks[0]}) for r in previous]
    if len(keys) != len(set(keys)) or not set(keys) <= expected:
        raise ValueError("unknown/duplicate answer output")
    if any(
        re.search(r"HTTP (401|402|403|429)", r.get("generation", {}).get("error") or "")
        for r in previous
    ):
        raise ValueError("frozen authentication/quota/rate stop reached; do not resume calls")
    started = {r["task_sha256"] for r in rows(run / "answer-started.jsonl")}
    for task in tasks:
        key = canonical_hash(task)
        if key in keys:
            continue
        case = cases[task["dataset"], task["id"]]
        retrieved = contexts[task["config"]][task["dataset"], task["id"]]
        context = retrieved["actual_context"]
        if key in started:
            result = {
                "error": "interrupted output; request slots remain reserved",
                "calls": [],
                "response": None,
                "checks": {},
                "latency_ms": None,
            }
        elif retrieved["error"]:
            result = {
                "error": "retrieval failed: " + retrieved["error"],
                "calls": [],
                "response": None,
                "checks": {},
                "latency_ms": None,
            }
        else:
            append(run / "answer-started.jsonl", {"task_sha256": key})
            wrapped = LedgerClient(client, run, task)
            result = generate_answer(
                case, copy.deepcopy(context), Settings(query_language="none"), wrapped
            )
        record = {
            **task,
            "run_id": protocol.get("run_id", run.name),
            "case_sha256": case["case_sha256"],
            "case": case,
            "context": context,
            "context_sha256": canonical_hash(context),
            "generation": result,
        }
        record = redact(record, getattr(client, "_token", ""))
        record["trace_sha256"] = canonical_hash(record)
        append(run / "answers.jsonl", record)
        print(
            "answer",
            task["dataset"],
            task["id"],
            task["config"],
            task["repetition"],
            "calls",
            len(result["calls"]),
            "error",
            result["error"],
            flush=True,
        )
        if re.search(r"HTTP (401|402|403|429)", result["error"] or ""):
            break
    if len(rows(run / "answers.jsonl")) == 80:
        finish(
            run,
            "answer",
            [
                run / name
                for name in (
                    "decision.json",
                    "answer-tasks.json",
                    "answers.jsonl",
                    "answer-started.jsonl",
                )
            ]
            + ([run / "model-calls.jsonl"] if (run / "model-calls.jsonl").exists() else []),
        )


def review(run, protocol, review_path=None):
    answers = rows(run / "answers.jsonl")
    templates = [
        {k: a[k] for k in ("dataset", "id", "config", "repetition", "case_sha256", "trace_sha256")}
        | {
            "status": "pending",
            "reviewer": None,
            "reviewed_at": None,
            "reason": None,
            "claim_inventory_complete": None,
            "independent_human_review": None,
            "answer_correct": None,
            "claims": [],
            "citation_edges": [],
        }
        for a in answers
    ]
    template_path = run / f"review-template-{len(templates)}.json"
    save(template_path, templates)
    judgments = load(review_path) if review_path else []
    indexed = {a["trace_sha256"]: a for a in answers}
    if len(indexed) != len(answers):
        raise ValueError("duplicate answer trace")
    for output in answers:
        if (
            canonical_hash({k: v for k, v in output.items() if k != "trace_sha256"})
            != output["trace_sha256"]
        ):
            raise ValueError("answer changed after trace hash was computed")
    seen = set()
    for judgment in judgments:
        trace = judgment["trace_sha256"]
        if trace not in indexed or trace in seen:
            raise ValueError("unknown/duplicate review")
        seen.add(trace)
        original = indexed[trace]
        for key in ("dataset", "id", "config", "repetition", "case_sha256"):
            if judgment[key] != original[key]:
                raise ValueError("review binding mismatch")
        if judgment["status"] != "reviewed" or not all(
            judgment.get(k)
            for k in ("reviewer", "reviewed_at", "reason", "claim_inventory_complete")
        ):
            raise ValueError("complete independent review required")
        if (
            judgment.get("independent_human_review") is not True
            or judgment["claim_inventory_complete"] is not True
        ):
            raise ValueError(
                "independent human review and complete claim inventory must be affirmed"
            )
        reviewed_at = datetime.fromisoformat(judgment["reviewed_at"])
        if reviewed_at.tzinfo is None:
            raise ValueError("review timestamp requires a timezone")
        if type(judgment["answer_correct"]) is not bool:
            raise ValueError("answer_correct requires explicit human judgment")
        response = original["generation"].get("response") or {}
        answer_text = response.get("answer", "")
        if judgment["answer_correct"] and (
            original["generation"].get("error")
            or response.get("status")
            != ("answered" if original["case"]["answerable"] else "no_evidence")
        ):
            raise ValueError("known generation/refusal failure cannot receive a correct judgment")
        claim_ids = set()
        for claim in judgment["claims"]:
            if not claim.get("text") or any(
                type(claim.get(k)) is not bool for k in ("supported", "contradiction")
            ):
                raise ValueError("every claim requires explicit support/contradiction review")
            if not claim.get("id") or claim["id"] in claim_ids:
                raise ValueError("claims require unique IDs")
            claim_ids.add(claim["id"])
            first, last = claim["answer_span"]
            if (
                not 0 <= first < last <= len(answer_text)
                or answer_text[first:last] != claim["text"]
            ):
                raise ValueError("claim span must point to the actual answer")
            if judgment["answer_correct"] and (not claim["supported"] or claim["contradiction"]):
                raise ValueError(
                    "unsupported/contradictory claims cannot receive a correct judgment"
                )
        if response.get("status") == "answered" and not claim_ids:
            raise ValueError("answered output requires a nonempty human claim inventory")
        allowed = {e["citation_id"] for e in (original["context"] or {}).get("evidence", [])}
        mentioned = set(re.findall(r"\[(E[a-f0-9]{24})\]", answer_text))
        reviewed_citations = set()
        reviewed_edges = set()
        for edge in judgment["citation_edges"]:
            if (
                edge.get("citation_id") not in allowed & mentioned
                or edge.get("claim_id") not in claim_ids
                or type(edge.get("supported")) is not bool
            ):
                raise ValueError(
                    "citation edge requires an actual delivered citation and human judgment"
                )
            pair = (edge["claim_id"], edge["citation_id"])
            if pair in reviewed_edges:
                raise ValueError("duplicate claim-citation edge")
            reviewed_edges.add(pair)
            reviewed_citations.add(edge["citation_id"])
        if reviewed_citations != mentioned:
            raise ValueError("every mentioned citation needs a claim-citation review")
    claims = [c for j in judgments for c in j["claims"]]
    edges = [e for j in judgments for e in j["citation_edges"]]
    result = {
        "expected_outputs": 80,
        "outputs": len(answers),
        "reviewed": len(judgments),
        "review_coverage": ratio(len(judgments), 80),
        "answer_correctness": ratio(sum(j["answer_correct"] for j in judgments), len(judgments)),
        "citation_precision": ratio(sum(e["supported"] for e in edges), len(edges)),
        "hallucination_rate": ratio(
            sum(not c["supported"] or c["contradiction"] for c in claims), len(claims)
        ),
        "independent_review": "pending" if len(judgments) < 80 else "complete",
    }
    result["by_configuration"] = {}
    for name in sorted({a["config"] for a in answers}):
        outputs = [a for a in answers if a["config"] == name]
        reviewed = [j for j in judgments if j["config"] == name]
        claim_rows = [c for j in reviewed for c in j["claims"]]
        edge_rows = [e for j in reviewed for e in j["citation_edges"]]
        result["by_configuration"][name] = {
            "outputs": len(outputs),
            "independent_cases": len({(a["dataset"], a["id"]) for a in outputs}),
            "output_coverage": ratio(len(outputs), 40),
            "review_coverage": ratio(len(reviewed), 40),
            "answer_correctness": ratio(sum(j["answer_correct"] for j in reviewed), len(reviewed)),
            "citation_precision": ratio(sum(e["supported"] for e in edge_rows), len(edge_rows)),
            "hallucination_rate": ratio(
                sum(not c["supported"] or c["contradiction"] for c in claim_rows), len(claim_rows)
            ),
            "generation_errors": sum(bool(a["generation"]["error"]) for a in outputs),
            "generation_latency": latency_summary(
                [
                    a["generation"]["latency_ms"]
                    for a in outputs
                    if a["generation"].get("latency_ms") is not None
                ]
            ),
            "refused_status_by_answerability": {
                str(answerable): ratio(
                    sum(
                        (a["generation"].get("response") or {}).get("status") == "no_evidence"
                        for a in outputs
                        if a["case"]["answerable"] == answerable
                    ),
                    sum(a["case"]["answerable"] == answerable for a in outputs),
                )
                for answerable in (True, False)
            },
        }
    suffix = digest(review_path)[:12] if review_path else f"pending-{len(answers)}"
    save(run / f"review-summary-{suffix}.json", result)
    return result


def report(run, protocol, review_path=None):
    summary = summaries(run, protocol)
    statistics, p_values = {}, {}
    for model in MODEL_ARMS:
        for arm in CHUNK_ARMS:
            name = f"{model}-{arm}-hybrid_rerank"
            if name == BASELINE:
                continue
            before = rows(run / "retrieve" / f"{BASELINE}.jsonl")
            after = rows(run / "retrieve" / f"{name}.jsonl")
            for dataset in ("official", "repository"):
                key = f"{name}:{dataset}"
                stats = paired_statistics(
                    [r for r in before if r["dataset"] == dataset],
                    [r for r in after if r["dataset"] == dataset],
                )
                statistics[key] = stats
                p_values[key] = stats["cluster_permutation_p"]
    adjusted = holm(p_values)
    for key, value in adjusted.items():
        statistics[key]["holm_adjusted_p"] = value
    answers = rows(run / "answers.jsonl")
    ledger = rows(run / "model-calls.jsonl")
    starts = [r for r in ledger if r["event"] == "started"]
    finished = [r for r in ledger if r["event"] == "finished"]
    usage, covered = Counter(), 0
    for call in finished:
        observed = (call.get("provider_response") or {}).get("usage")
        if observed:
            covered += 1
            usage.update({k: v for k, v in observed.items() if type(v) in (int, float)})
    if len(starts) > 160:
        raise ValueError("request budget exceeded")
    report_data = {
        "kind": VERSION,
        "run_id": protocol.get("run_id", run.name),
        "retrieval": summary,
        "paired_statistics": statistics,
        "decision": select_candidate(summary),
        "answer_outputs": len(answers),
        "expected_answer_outputs": 80,
        "generation_request_slots_reserved": len(starts),
        "generation_calls_finished": len(finished),
        "usage": dict(usage),
        "usage_recording_coverage": ratio(covered, len(starts)),
        "model_cost_usd": None,
        "answer_review": review(run, protocol, review_path),
        "default_changed": False,
        "holdout_test_read": False,
        "limitations": [
            "dev selection is not independent confirmation",
            "sparse relevance labels",
            "generation uses frozen actual contexts, not live end-to-end",
            "peak RSS is a process lifetime high-water mark",
            "2GB deployment not tested",
        ],
    }
    builds = {}
    for model in MODEL_ARMS:
        for arm in CHUNK_ARMS:
            name = f"{model}-{arm}"
            current = load(run / "index-info" / f"{name}.json")
            origin = current
            while origin.get("origin_build_info"):
                origin = origin["origin_build_info"]
            builds[name] = {"this_run": current, "original_uncached_build": origin}
    report_data["index_builds"] = builds
    suffix = digest(review_path)[:12] if review_path else f"pending-{len(answers)}"
    save(run / f"summary-{suffix}.json", report_data)
    lines = [
        "# Qwen embedding / chunk dev comparison",
        "",
        "No holdout/test read; defaults unchanged. Evidence delivery is not answer correctness.",
        "",
        "| Configuration | Official delivery | Repository delivery | Warm P50 ms | Warm P95 ms |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, row in summary.items():
        timing = row["warm_latency"] or {}

        def fraction(metric):
            return f"{metric['numerator']}/{metric['denominator']}"

        lines.append(
            f"| {name} | {fraction(row['official']['delivery'])} | "
            f"{fraction(row['repository']['delivery'])} | {timing.get('p50_ms', 'unknown')} | "
            f"{timing.get('p95_ms', 'unknown')} |"
        )
    lines += [
        "",
        "Candidate: " + report_data["decision"]["candidate"],
        f"Qualified: {report_data['decision']['qualified']}",
        f"Answer outputs: {len(answers)}/80; "
        f"human review: {report_data['answer_review']['reviewed']}/80.",
        "Model cost is unknown without verified provider pricing; raw usage is retained.",
    ]
    lines += [
        "",
        "## Index construction",
        "",
        "Original uncached builds and verified-vector reuse are reported separately.",
        "",
        "| Index | Chunks | Dimensions | Uncached build seconds | Directory bytes |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, build in builds.items():
        original = build["original_uncached_build"]
        lines.append(
            f"| {name} | {original['chunks']} | {original['dimension']} | "
            f"{original['build_seconds']:.1f} | {original['directory_bytes']} |"
        )
    path = run / f"comparison-{suffix}.md"
    text = "\n".join(lines) + "\n"
    if path.exists() and path.read_text() != text:
        raise ValueError("report already frozen; use a new report version")
    path.write_text(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=(*PHASES, "all"), default="all")
    parser.add_argument("--reviews", type=Path)
    parser.add_argument("--reuse-indexes", type=Path, help="Verified prior run; vectors only")
    args = parser.parse_args()
    run = args.output.resolve()
    phases = PHASES if args.phase == "all" else (args.phase,)
    for phase in phases:
        started = perf_counter()
        try:
            protocol = (
                freeze(run, args.reuse_indexes.resolve() if args.reuse_indexes else None)
                if phase == "freeze"
                else verify(run)
            )
            prerequisite = {
                "index": "prepare",
                "retrieve": "index",
                "latency": "retrieve",
                "answer": "latency",
            }.get(phase)
            if prerequisite and not (run / f"{prerequisite}-manifest.json").exists():
                raise ValueError(f"complete {prerequisite} before {phase}")
            if phase in {"prepare", "index"}:
                globals()[phase](run, protocol)
            elif phase in {"retrieve", "latency"}:
                retrieve(run, protocol, timing=phase == "latency")
            elif phase == "answer":
                answer(run, protocol)
            elif phase in {"review", "report"}:
                globals()[phase](run, protocol, args.reviews)
            record_operation(
                f"Qwen/Chunk 实验阶段 {phase}",
                "执行用户批准的六组 dev 对照协议",
                f"阶段完成；输出 {run}；耗时 {perf_counter() - started:.1f}s；不切默认、不读test",
                "无",
            )
            print("phase complete", phase, flush=True)
        except Exception as exc:
            record_operation(
                f"Qwen/Chunk 实验阶段 {phase}",
                "执行已冻结实验协议",
                f"阶段失败或未完成；输出 {run}",
                f"{type(exc).__name__}: {exc}",
            )
            raise


if __name__ == "__main__":
    main()
