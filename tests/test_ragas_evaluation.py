import asyncio
from dataclasses import replace
from types import SimpleNamespace

import pytest

from infra_rag.config import Settings
from infra_rag.models import Chunk, Hit
from infra_rag.ragas_ablation import CONFIGS, collect_records
from infra_rag.ragas_evaluation import (
    METRICS,
    score_records,
    summarize,
    usage_summary,
    validate_cases,
)


class Judge:
    last_calls = []

    async def score(self, name, sample):
        self.last_calls = [{"usage": {"total_tokens": 7}}]
        assert sample["retrieved_contexts"] == ["Delivered truncated text."]
        if name == "faithfulness":
            raise TimeoutError
        if name == "context_recall":
            return float("nan")
        return 0.75


def test_judge_failure_and_nonfinite_keep_null_and_usage():
    records = [
        {
            "query": "Q",
            "reference": "Gold",
            "response": "Answer",
            "config_id": "dense",
            "evidence": [{"content": "Delivered truncated text."}],
            "latency_ms": 10,
            "retrieval": {"recall": 1, "mrr": 1, "ndcg": 1},
        }
    ]
    rows = asyncio.run(score_records(records, Judge()))
    assert rows[0]["ragas"]["faithfulness"] is None
    assert rows[0]["ragas"]["context_recall"] is None
    assert len(rows[0]["judge_calls"]) == 4
    summary = summarize(rows)["dense"]
    assert summary["ragas"]["faithfulness"]["coverage"] == 0
    assert summary["ragas"]["context_precision"]["value"] == 0.75
    assert summary["judge_usage"]["total_tokens"] == 28


def test_failed_generation_stays_in_denominator():
    record = {
        "query": "Q",
        "reference": "Gold",
        "response": None,
        "config_id": "dense",
        "error": "generation_failed",
        "latency_ms": 15,
    }
    rows = asyncio.run(score_records([record], Judge()))
    summary = summarize(rows)["dense"]
    assert summary["outputs"] == summary["failures"] == 1
    assert all(rows[0]["ragas"][m] is None for m in METRICS)
    assert summary["retrieval"]["recall"]["value"] is None
    assert rows[0]["judge_calls"] == []


def test_partial_usage_does_not_claim_total_cost():
    result = usage_summary([{"usage": {"total_tokens": 4}}, {}])
    assert result["known_total_tokens"] == 4
    assert result["total_tokens"] is None
    assert result["coverage"] == 0.5
    assert result["cost_usd"] is None


def test_cases_validate_before_running():
    case = {"id": "a", "query": "Q", "reference": "Gold", "relevant": []}
    validate_cases([case])
    with pytest.raises(ValueError):
        validate_cases([case, case])
    with pytest.raises(ValueError):
        validate_cases([{**case, "reference": ""}])


class Service:
    def __init__(self):
        self.settings = Settings(neighbor_expansion=False, candidate_k=2)
        self.context_counter = len
        self.chunks = [Chunk(c, c, "source", c + ".", "infra") for c in ("a", "b")]
        self.parent_index = {c.id: [c] for c in self.chunks}
        self.calls = []

    def search(self, query, *, strategy, **kwargs):
        self.calls.append((strategy, self.settings.rerank))
        chunks = self.chunks if strategy == "dense" else self.chunks[::-1]
        return [Hit(c, 1) for c in chunks]


def test_four_paired_configs_restore_settings_and_deliver_actual_text(monkeypatch):
    def generate(case, context, settings, client):
        assert context["evidence"]
        return {"error": None, "response": {"answer": "A"}, "calls": []}

    monkeypatch.setattr("infra_rag.ragas_ablation.generate_answer", generate)
    service = Service()
    original = service.settings
    cases = [{"id": "q", "query": "Q", "reference": "A", "relevant": ["a"]}]
    rows = list(collect_records(service, cases, SimpleNamespace(), run_id="test", k=2))
    assert [r["config_id"] for r in rows] == list(CONFIGS)
    assert all(r["retrieval"]["recall"] == 1 for r in rows)
    assert service.settings is original
    assert service.calls == [
        ("dense", False),
        ("bm25", False),
        ("dense", False),
        ("hybrid", False),
        ("hybrid", True),
    ]
    assert rows[1]["retrieved"] == ["a", "b"]  # Borda tie uses stable chunk ID.


def test_collection_failure_is_retained_and_settings_restored(monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("private message")

    service = Service()
    original = service.settings
    monkeypatch.setattr(service, "search", fail)
    cases = [{"id": "q", "query": "Q", "reference": "A", "relevant": []}]
    rows = list(collect_records(service, cases, None, run_id="test"))
    assert len(rows) == 4
    assert all(r["error"] == "RuntimeError" for r in rows)
    assert service.settings is original
    assert "private message" not in str(rows)


def test_unknown_gold_is_rejected_and_no_settings_changed():
    service = Service()
    original = service.settings
    with pytest.raises(ValueError, match="gold"):
        list(collect_records(service, [{"relevant": ["missing"]}], None, run_id="test"))
    assert service.settings == original
    service.settings = replace(original, context_policy="complete")
    with pytest.raises(ValueError, match="context"):
        list(collect_records(service, [], None, run_id="test"))


def test_real_ragas_collections_with_mock_provider(monkeypatch):
    """Exercise the pinned SDK/metric interfaces without spending model tokens."""
    import importlib.util

    if importlib.util.find_spec("ragas") is None:
        pytest.skip("install the evaluation extra for the SDK compatibility test")
    import json

    import httpx

    from infra_rag.ragas_evaluation import RagasJudge

    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-test-key")
    monkeypatch.setenv("RAGAS_DO_NOT_TRACK", "true")
    # httpx parses NO_PROXY entries as URL patterns; brackets in [::1] fail on some hosts.
    monkeypatch.delenv("NO_PROXY", raising=False)
    monkeypatch.delenv("no_proxy", raising=False)

    async def respond(request):
        payload = json.loads(request.content)
        if request.url.path.endswith("/embeddings"):
            inputs = payload["input"]
            if isinstance(inputs, str):
                inputs = [inputs]
            return httpx.Response(
                200,
                json={
                    "object": "list",
                    "model": "fixture-embedding",
                    "data": [
                        {"object": "embedding", "index": i, "embedding": [1.0, 0.0]}
                        for i in range(len(inputs))
                    ],
                    "usage": {"prompt_tokens": 2, "total_tokens": 2},
                },
            )
        assert payload["max_tokens"] == 2048
        assert payload["thinking"] == {"type": "disabled"}
        outputs = {
            "ContextPrecisionOutput": {"reason": "fixture", "verdict": 1},
            "ContextRecallOutput": {
                "classifications": [{"statement": "A", "reason": "fixture", "attributed": 1}]
            },
            "StatementGeneratorOutput": {"statements": ["A"]},
            "NLIStatementOutput": {
                "statements": [{"statement": "A", "reason": "fixture", "verdict": 1}]
            },
            "AnswerRelevanceOutput": {"question": "Q", "noncommittal": 0},
        }
        messages = json.dumps(payload["messages"])
        output_name = next(name for name in outputs if name in messages)
        arguments = outputs[output_name]
        return httpx.Response(
            200,
            json={
                "id": "fixture",
                "object": "chat.completion",
                "created": 0,
                "model": "fixture",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": json.dumps(arguments)},
                    }
                ],
                "usage": {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5},
            },
        )

    async def run():
        judge = RagasJudge("fixture", "fixture-embedding", max_tokens=2048, disable_thinking=True)
        # Keep real request/response hooks; replace only the network transport.
        judge.http._transport = httpx.MockTransport(respond)
        judge.http._mounts = {}
        try:
            return await score_records(
                [
                    {
                        "query": "Q",
                        "reference": "A",
                        "response": "A",
                        "config_id": "dense",
                        "evidence": [{"content": "A"}],
                        "latency_ms": 1,
                    }
                ],
                judge,
            )
        finally:
            await judge.close()

    rows = asyncio.run(run())
    assert rows[0]["judge_errors"] == {}
    assert all(rows[0]["ragas"][m] == pytest.approx(1) for m in METRICS)
    assert rows[0]["judge_calls"]
    assert all(c["usage"] and c["status_code"] == 200 for c in rows[0]["judge_calls"])


@pytest.mark.parametrize("damage", ["duplicate", "missing", "tamper"])
def test_cli_rejects_incomplete_or_changed_collection(tmp_path, monkeypatch, damage):
    import importlib.util
    import json
    from pathlib import Path

    from infra_rag.ragas_evaluation import digest

    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location("benchmark_ragas", scripts / "benchmark_ragas.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cases = [{"id": "q", "query": "Q", "reference": "A", "relevant": []}]
    protocol = {
        "run_id": "test",
        "configurations": list(CONFIGS),
        "repetitions": 1,
        "cases_sha256": digest(cases),
    }
    records = [{"run_id": "test", "config_id": c, "case_id": "q", "repetition": 0} for c in CONFIGS]
    if damage == "duplicate":
        records.append(records[0])
    elif damage == "missing":
        records.pop()
    raw = "\n".join(json.dumps(r) for r in records)
    complete = {"records_sha256": digest(raw), "protocol_sha256": digest(protocol)}
    for filename, data in (
        ("protocol.json", protocol),
        ("cases.json", cases),
        ("complete.json", complete),
    ):
        (tmp_path / filename).write_text(json.dumps(data))
    (tmp_path / "records.jsonl").write_text(raw + ("\n" if damage == "tamper" else ""))
    output = tmp_path / "score"
    with pytest.raises(ValueError, match="hashes|duplicate or missing"):
        module.score(SimpleNamespace(run=tmp_path, output=output))
    assert not output.exists()


def test_anthropic_usage_includes_cached_input_without_double_counting_openai():
    result = usage_summary(
        [
            {
                "usage": {
                    "input_tokens": 10,
                    "output_tokens": 2,
                    "cache_read_input_tokens": 20,
                    "cache_creation_input_tokens": 5,
                }
            },
            {
                "usage": {
                    "prompt_tokens": 30,
                    "completion_tokens": 4,
                    "total_tokens": 34,
                    "prompt_tokens_details": {"cached_tokens": 20},
                }
            },
        ]
    )
    assert result["total_tokens"] == 71
    assert result["measured_calls"] == 2
    assert result["coverage"] == 1
