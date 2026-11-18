import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Barrier

import pytest
from fastapi.testclient import TestClient

from infra_rag.api import create_app
from infra_rag.assistant import AnswerService
from infra_rag.config import Settings
from infra_rag.runtime import (
    ACTIVE_REQUEST,
    AccountedModel,
    RuntimeRetrieval,
    install_request_journal,
)
from infra_rag.service import RetrievalService


@pytest.fixture
def runtime(tmp_path):
    service = RetrievalService(Settings(data_dir=tmp_path / "index", chunk_size=100))
    source = tmp_path / "notes.md"
    source.write_text("# KV Cache\n\nPagedAttention 使用分页 KV Cache，减少显存碎片。")
    service.ingest(source, "inference")
    return RuntimeRetrieval(service, cache_size=2), source


def test_cached_context_is_isolated_and_invalidated_on_ingest_settings_and_filter(runtime):
    runtime, source = runtime
    first = {}
    hits = runtime.search("KV Cache", top_k=1, diagnostics=first)
    assert not first["retrieval_cache"]["hit"]
    hits[0].chunk.content = "caller mutation"
    assert "caller mutation" not in runtime.service.chunks[0].content
    context = {}
    detail = {}
    again = runtime.search("KV Cache", top_k=1, diagnostics=detail, context_pack=context)
    assert detail["retrieval_cache"]["hit"]
    assert "caller mutation" not in again[0].chunk.content
    context["evidence"].clear()
    runtime.search("KV Cache", top_k=1, context_pack=context)
    assert context["evidence"]
    runtime.search("KV Cache", top_k=1, domain="not-present", diagnostics=detail)
    assert not detail["retrieval_cache"]["hit"]
    runtime.service.settings = replace(runtime.settings, context_tokens=99)
    runtime.search("KV Cache", top_k=1, diagnostics=detail)
    assert not detail["retrieval_cache"]["hit"]
    source.write_text("# KV Cache\n\n新的 KV Cache 正文。")
    runtime.ingest(source, "inference")
    result = runtime.search("KV Cache", top_k=1, diagnostics=detail)
    assert not detail["retrieval_cache"]["hit"]
    assert "新的" in result[0].chunk.content


def test_bounded_cache_eviction_and_concurrent_reuse(runtime):
    runtime, _ = runtime
    for query in ("KV Cache", "PagedAttention", "分页"):
        runtime.search(query)
    detail = {}
    runtime.search("KV Cache", diagnostics=detail)
    assert not detail["retrieval_cache"]["hit"]
    barrier = Barrier(3)

    def request():
        barrier.wait()
        d = {}
        hits = runtime.search("KV Cache", diagnostics=d)
        return hits[0].chunk.id, d["retrieval_cache"]["hit"]

    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(lambda _: request(), range(3)))
    assert len({r[0] for r in rows}) == 1
    assert all(r[1] for r in rows)


def test_model_usage_is_request_local_across_concurrent_calls():
    barrier = Barrier(2)

    class Model:
        model = "fake"
        provider = "test"
        last_call = None

        def generate(self, messages):
            marker = messages[0]["content"]
            self.last_call = {"usage": {"marker": marker}}
            barrier.wait()
            return marker

    model = AccountedModel(Model())

    def request(marker):
        journal = {"model_calls": []}
        token = ACTIVE_REQUEST.set(journal)
        try:
            model.generate([{"role": "user", "content": marker}])
            return journal["model_calls"][0]["provider_metadata"]["usage"]["marker"]
        finally:
            ACTIVE_REQUEST.reset(token)

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert list(pool.map(request, ["one", "two"])) == ["one", "two"]


def test_http_journal_accounts_every_attempt_and_fresh_generation_on_retrieval_hit(
    runtime, tmp_path
):
    runtime, _ = runtime

    class Model:
        provider = "test"
        model = "fake"

        def generate(self, messages):
            self.last_call = {"usage": {"output_tokens": 3}}
            return json.dumps({"supported": False, "answer": "证据不足", "citations": []})

    app = create_app(runtime, AnswerService(runtime, model=AccountedModel(Model())))
    journal = tmp_path / "requests.jsonl"
    install_request_journal(app, journal)
    with TestClient(app) as client:
        responses = [client.post("/chat", json={"message": "KV Cache"}) for _ in range(2)]
        assert all(r.status_code == 200 for r in responses)
        invalid = client.post("/chat", json={"message": ""})
        assert invalid.status_code == 422
    rows = [json.loads(line) for line in journal.read_text().splitlines()]
    assert len(rows) == 3
    assert rows[0]["request_id"] == responses[0].headers["X-Request-ID"]
    assert not rows[0]["retrieval"][0]["diagnostics"]["retrieval_cache"]["hit"]
    assert rows[1]["retrieval"][0]["diagnostics"]["retrieval_cache"]["hit"]
    assert all(len(r["model_calls"]) == 1 for r in rows[:2])
    assert not rows[2]["model_calls"] and rows[2]["http_status"] == 422
