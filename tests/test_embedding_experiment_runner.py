"""Freeze, request-budget and independent-review invariants for the experiment CLI."""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.config import Settings
from infra_rag.models import Chunk
from infra_rag.service import RetrievalService


@pytest.fixture
def runner(monkeypatch):
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location(
        "embedding_runner_test", scripts / "benchmark_embedding_chunks.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_frozen_artifacts_are_idempotent_but_never_replaced(runner, tmp_path):
    target = tmp_path / "artifact.json"
    runner.save(target, {"value": 1})
    runner.save(target, {"value": 1})
    with pytest.raises(ValueError, match="Frozen artifact differs"):
        runner.save(target, {"value": 2})
    assert runner.load(target) == {"value": 1}


def test_resume_rejects_changed_implementation_protocol_or_phase(runner, monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    source = tmp_path / "source.py"
    source.write_text("original")
    run = tmp_path / "run"
    protocol = {
        "kind": runner.VERSION,
        "implementation": {"source.py": digest(source)},
        "inputs": {},
        "models": {},
    }
    runner.save(run / "protocol.json", protocol)
    (run / "protocol.sha256").write_text(digest(run / "protocol.json"))
    assert runner.verify(run) == protocol
    source.write_text("changed")
    with pytest.raises(ValueError, match="Implementation changed"):
        runner.verify(run)
    source.write_text("original")
    artifact = run / "output.json"
    artifact.write_text("original")
    runner.finish(run, "prepare", [artifact])
    artifact.write_text("tampered")
    with pytest.raises(ValueError, match="phase output changed"):
        runner.verify(run)
    (run / "protocol.json").write_text("{}")
    with pytest.raises(ValueError, match="protocol changed"):
        runner.verify(run)


def test_failed_http_calls_consume_budget_and_ledger_redacts_secrets(runner, tmp_path):
    class Client:
        model, provider, _token = "test", "test", "fake-secret"
        last_call = None

        def generate(self, messages):
            raise RuntimeError("failure fake-secret")

    client = runner.LedgerClient(Client(), tmp_path, {"id": "case"}, maximum=1)
    with pytest.raises(RuntimeError):
        client.generate([{"role": "user", "content": "question"}])
    with pytest.raises(ValueError, match="budget exhausted"):
        client.generate([{"role": "user", "content": "question"}])
    ledger = runner.rows(tmp_path / "model-calls.jsonl")
    assert [r["event"] for r in ledger] == ["started", "finished"]
    assert "fake-secret" not in (tmp_path / "model-calls.jsonl").read_text()


def test_reused_vectors_require_same_fingerprint_and_exact_provenance(runner, tmp_path):
    service = RetrievalService(Settings(data_dir=tmp_path / "new"))
    chunk = Chunk("id", "parent", "source", "original evidence", "infra")
    state = {
        "fingerprint": service.settings.fingerprint(),
        "chunks": runner.serialize_chunks([chunk]),
        "vectors": [[1.0, 0.0]],
    }
    path = tmp_path / "old.json"
    path.write_text(json.dumps(state))
    runner.seed_verified_index(service, [chunk], {"snapshot": str(path)})
    assert service.vectors == [[1.0, 0.0]]
    changed = Chunk("id", "parent", "source", "changed evidence", "infra")
    with pytest.raises(ValueError, match="provenance mismatch"):
        runner.seed_verified_index(service, [changed], {"snapshot": str(path)})
    state["fingerprint"]["backend"] = "bge"
    path.write_text(json.dumps(state))
    with pytest.raises(ValueError, match="fingerprint mismatch"):
        runner.seed_verified_index(service, [chunk], {"snapshot": str(path)})


def test_warmup_uses_the_exact_measured_filter_cache_key(runner, monkeypatch, tmp_path):
    calls = []
    service = SimpleNamespace(settings=Settings(), search=lambda *a, **kw: calls.append(kw))
    monkeypatch.setattr(runner, "MODEL_ARMS", ("bge",))
    monkeypatch.setattr(runner, "CHUNK_ARMS", ("structure",))
    monkeypatch.setattr(runner, "BudgetTokenizer", lambda *a: None)
    monkeypatch.setattr(runner, "encoder_for", lambda *a: None)
    monkeypatch.setattr(runner, "release", lambda: None)
    monkeypatch.setattr(runner, "sync", lambda *a: None)
    monkeypatch.setattr(runner, "service_for", lambda *a: service)
    monkeypatch.setattr(
        runner, "prepared", lambda *a: ({}, [{"dataset": "official", "id": "case"}])
    )
    monkeypatch.setattr(runner, "evaluate_query", lambda *a: {"dataset": "official", "id": "case"})
    monkeypatch.setitem(
        __import__("sys").modules,
        "sentence_transformers",
        SimpleNamespace(CrossEncoder=lambda *a, **kw: None),
    )
    protocol = {
        "device": "cpu",
        "models": {"bge": {"path": "unused"}, "reranker": {"path": "unused"}},
    }
    runner.retrieve(tmp_path, protocol, timing=True)
    assert len(calls) == 2
    assert all(
        c["modality"] == "text" and c["domain"] == "infra" and c["top_k"] == 5 for c in calls
    )


def answer_record():
    citation = "E" + "a" * 24
    answer = "A fact. [" + citation + "]"
    record = {
        "dataset": "official",
        "id": "case",
        "config": "test",
        "repetition": 1,
        "case_sha256": "case-hash",
        "case": {"answerable": True},
        "context": {"evidence": [{"citation_id": citation}]},
        "generation": {"error": None, "response": {"status": "answered", "answer": answer}},
    }
    record["trace_sha256"] = canonical_hash(record)
    return record


def completed_review(record):
    return {
        k: record[k]
        for k in ("dataset", "id", "config", "repetition", "case_sha256", "trace_sha256")
    } | {
        "status": "reviewed",
        "reviewer": "independent-test-reviewer",
        "reviewed_at": "2026-10-23T12:00:00+08:00",
        "reason": "synthetic test fixture only",
        "claim_inventory_complete": True,
        "independent_human_review": True,
        "answer_correct": True,
        "claims": [
            {
                "id": "c1",
                "text": "A fact.",
                "answer_span": [0, 7],
                "supported": True,
                "contradiction": False,
            }
        ],
        "citation_edges": [{"claim_id": "c1", "citation_id": "E" + "a" * 24, "supported": True}],
    }


def test_reviews_remain_unknown_until_complete_independent_judgment(runner, tmp_path):
    output = answer_record()
    runner.append(tmp_path / "answers.jsonl", output)
    pending = runner.review(tmp_path, {})
    assert pending["answer_correctness"]["value"] is None
    assert pending["review_coverage"]["numerator"] == 0
    review = completed_review(output)
    path = tmp_path / "human.json"
    path.write_text(json.dumps([review]))
    result = runner.review(tmp_path, {}, path)
    assert result["answer_correctness"]["value"] == 1
    assert result["review_coverage"]["denominator"] == 80
    assert result["citation_precision"]["value"] == 1
    assert result["independent_review"] == "pending"


@pytest.mark.parametrize(
    "change", ["stale", "empty", "edge", "span", "unsupported", "duplicate", "duplicate_edge"]
)
def test_reviews_reject_stale_or_incomplete_claim_evidence(runner, tmp_path, change):
    output = answer_record()
    runner.append(tmp_path / "answers.jsonl", output)
    review = completed_review(output)
    values = [review]
    if change == "stale":
        review["trace_sha256"] = "stale"
    elif change == "empty":
        review["claims"] = []
    elif change == "edge":
        review["citation_edges"] = []
    elif change == "span":
        review["claims"][0]["answer_span"] = [1, 8]
    elif change == "unsupported":
        review["claims"][0]["supported"] = False
    elif change == "duplicate":
        values.append(review)
    elif change == "duplicate_edge":
        review["citation_edges"].append(review["citation_edges"][0])
    path = tmp_path / "human.json"
    path.write_text(json.dumps(values))
    with pytest.raises(ValueError):
        runner.review(tmp_path, {}, path)
