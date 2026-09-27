"""Diagnostics explain candidates; context budgets preserve retrieval ranking."""

from dataclasses import replace

from fastapi.testclient import TestClient

from infra_rag.api import create_app
from infra_rag.config import Settings
from infra_rag.context import pack_context
from infra_rag.models import Chunk, Hit
from infra_rag.service import RetrievalService


def test_debug_preserves_ranking_and_exposes_truncated_candidates(tmp_path, monkeypatch):
    service = RetrievalService(Settings(data_dir=tmp_path / "index", candidate_k=1))
    service._commit(
        [
            Chunk("a", "a", "a.md", "alpha", "infra"),
            Chunk("b", "b", "b.md", "beta", "infra"),
        ]
    )
    monkeypatch.setattr("infra_rag.service.bm25", lambda *args: [("a", 10)])
    service.vectors = [[0.0] * 384, service._encoder().encode(["beta"])[0]]
    trace = {}
    normal = service.search("beta", top_k=1)
    debug = service.search("beta", top_k=1, diagnostics=trace)
    assert [(h.chunk.id, h.score) for h in normal] == [(h.chunk.id, h.score) for h in debug]
    assert len(trace["fusion"]) == 2
    assert sum(row["retained"] for row in trace["fusion"]) == 1
    assert trace["channels"]["bm25"]["ranking"][0]["score"] == 10
    assert trace["channels"]["dense"]["score_kind"] == "cosine_similarity"
    assert trace["returned_chunk_ids"] == [debug[0].chunk.id]
    assert all(value >= 0 for value in trace["timings_ms"].values())


def test_rerank_trace_shows_rank_change_and_pair_truncation(tmp_path):
    service = RetrievalService(Settings(data_dir=tmp_path / "index", rerank=True))
    service._commit(
        [
            Chunk("a", "a", "a.md", "alpha alpha", "infra"),
            Chunk("b", "b", "b.md", "beta", "infra"),
        ]
    )

    class Tokenizer:
        model_max_length = 8

        def encode(self, query, document, truncation=False):
            assert not truncation
            return list(range(len(query) + len(document) + 3))

    class Reranker:
        tokenizer = Tokenizer()
        max_length = 8

        def predict(self, pairs):
            return [100 if document == "beta" else 0 for _, document in pairs]

    service.reranker = Reranker()
    trace = {}
    hits = service.search("alpha beta", top_k=2, strategy="bm25", diagnostics=trace)
    assert hits[0].chunk.id == "b"
    assert trace["rerank"]["pair_limit"] == 8
    assert all(p["would_truncate"] for p in trace["rerank"]["pairs"])
    assert trace["final"][0]["before_rerank_rank"] == 2


def test_context_shared_parent_dedup_neighbors_filters_and_provenance():
    siblings = [
        Chunk(str(i), "parent", "a.md", f"Evidence {i}.", "infra", locator=f"a.md#L{i}")
        for i in range(8)
    ]
    foreign = Chunk("foreign", "parent", "a.md", "foreign", "other")
    hits = [Hit(siblings[5], 1), Hit(siblings[6], 0.9)]
    packed = pack_context(hits, {"parent": siblings + [foreign]}, len, 250, 250, "infra", "text")
    ids = [e["chunk_id"] for e in packed["evidence"]]
    assert ids[:2] == ["5", "6"]
    assert len(ids) == len(set(ids))
    assert "foreign" not in ids
    assert "4" in ids and "0" not in ids
    assert packed["used_tokens"] <= 250 and packed["used_characters"] <= 250
    assert hits[0].context and not hits[1].context
    assert hits[0].context_ref == hits[1].context_ref == "parent"
    assert hits[0].sibling_ids == ids
    assert packed["evidence"][0]["locator"] == "a.md#L5"
    assert packed["evidence"][0]["citation_id"] in hits[0].context


def test_context_global_budget_and_whole_sentence_trimming():
    first = Chunk("a", "a", "a.md", "First sentence. " + "Long text " * 50, "infra")
    second = Chunk("b", "b", "b.md", "Second evidence.", "infra")
    hits = [Hit(first, 1), Hit(second, 0.9)]
    packed = pack_context(hits, {"a": [first], "b": [second]}, len, 150, 150)
    assert packed["used_tokens"] <= 150
    assert len(packed["evidence"]) == 2
    assert packed["evidence"][0]["content"] == "First sentence."
    assert packed["evidence"][0]["truncated"]
    assert not packed["evidence"][1]["truncated"]


def test_context_does_not_cut_fenced_code_or_fake_full_evidence():
    code = Chunk("a", "a", "a.md", "```python\n" + "x = 1\n" * 100 + "```", "infra")
    hit = Hit(code, 1)
    packed = pack_context([hit], {"a": [code]}, len, 100, 100)
    assert not packed["evidence"] and not hit.sibling_ids and not hit.context
    assert packed["omitted_chunk_ids"] == ["a"]


def test_api_debug_context_and_empty_results(tmp_path):
    service = RetrievalService(Settings(data_dir=tmp_path / "index"))
    file = tmp_path / "a.md"
    file.write_text("# Cache\n\nPagedAttention manages memory.")
    service.ingest(file, "infra")
    with TestClient(create_app(service)) as client:
        default = client.post("/search", json={"query": "PagedAttention"}).json()
        debug = client.post("/search", json={"query": "PagedAttention", "debug": True}).json()
        assert "diagnostics" not in default
        assert debug["hits"] == default["hits"]
        assert debug["context_pack"]["evidence"][0]["source"] == str(file.resolve())
        assert debug["diagnostics"]["channels"]
        empty = client.post("/search", json={"query": "cache", "domain": "missing", "debug": True})
        assert empty.status_code == 200 and not empty.json()["hits"]
        assert not empty.json()["context_pack"]["evidence"]
        assert empty.json()["diagnostics"]["eligible_chunks"] == 0


def test_context_policy_does_not_change_index_fingerprint_or_rank(tmp_path):
    settings = Settings(data_dir=tmp_path / "index")
    legacy = replace(settings, context_mode="legacy", context_tokens=5)
    assert legacy.fingerprint() == settings.fingerprint()
    service = RetrievalService(settings)
    file = tmp_path / "a.md"
    file.write_text("# Cache\n\n" + "PagedAttention saves memory. " * 30)
    service.ingest(file)
    packed = service.search("PagedAttention", top_k=3)
    restored = RetrievalService(legacy)
    old = restored.search("PagedAttention", top_k=3)
    assert [(h.chunk.id, h.score) for h in packed] == [(h.chunk.id, h.score) for h in old]
    assert all(h.context for h in old)
