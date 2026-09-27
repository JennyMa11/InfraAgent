import json
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from infra_rag.api import create_app
from infra_rag.chunking import chunk_text
from infra_rag.config import Settings
from infra_rag.encoding import DemoEncoder
from infra_rag.evaluation import metrics
from infra_rag.service import RetrievalService, bm25, fuse


@pytest.fixture
def service(tmp_path):
    return RetrievalService(Settings(data_dir=tmp_path / "index", chunk_size=100))


def test_chunk_boundaries_and_preamble():
    settings = Settings(chunk_size=100)
    text = "前言不能丢失。\n\n# KV Cache\n\n" + "缓存保存历史 Key Value。" * 30
    chunks = chunk_text(text, "notes.md", "inference", DemoEncoder(), settings)
    assert "前言不能丢失" in chunks[0].content
    assert all(len(c.content) <= 100 for c in chunks)
    assert len({c.id for c in chunks}) == len(chunks)
    cache = [c for c in chunks if c.heading == "KV Cache"]
    assert len(cache) > 1 and len({c.parent_id for c in cache}) == 1
    assert all(c.locator.startswith("notes.md#L") for c in chunks)


def test_ingestion_replacement_persistence_and_filter(service, tmp_path):
    file = tmp_path / "a.md"
    file.write_text("# KV Cache\n\nPagedAttention 缓存分页减少内存碎片。")
    service.ingest(file, "inference")
    original_ids = [c.id for c in service.chunks]
    service.ingest(file, "inference")
    assert [c.id for c in service.chunks] == original_ids
    assert not service.search("KV Cache", domain="network")
    restored = RetrievalService(service.settings)
    assert restored.search("PagedAttention")[0].chunk.source == str(file.resolve())
    file.write_text("# NCCL\n\nAllReduce 同步梯度。")
    service.ingest(file, "training")
    assert not set(original_ids).intersection(c.id for c in service.chunks)
    assert all(c.domain == "training" for c in service.chunks)
    assert service.delete(str(file.resolve())) == len(service.chunks) + 1
    assert not RetrievalService(service.settings).chunks


def test_atomic_parse_failure(service, tmp_path):
    good = tmp_path / "a.md"
    good.write_text("# epoll\n\nEAGAIN 非阻塞 I/O。")
    service.ingest(good)
    snapshot = service.snapshot.read_bytes()
    bad = tmp_path / "bad.md"
    bad.write_bytes(b"\xff")
    with pytest.raises(UnicodeDecodeError):
        service.ingest(tmp_path)
    assert service.snapshot.read_bytes() == snapshot


def test_parent_expansion_keeps_matched_child(service, tmp_path):
    file = tmp_path / "a.md"
    file.write_text("# Cache\n\n" + "缓存缓存缓存。" * 50 + "\n独特term UniqueTerm。")
    service.ingest(file)
    hit = service.search("UniqueTerm", strategy="bm25", top_k=1)[0]
    assert "UniqueTerm" in hit.context
    assert len(hit.sibling_ids) > 1


def test_config_mismatch(service, tmp_path):
    file = tmp_path / "a.txt"
    file.write_text("test")
    service.ingest(file)
    with pytest.raises(ValueError, match="mismatch"):
        RetrievalService(replace(service.settings, chunk_size=200))


def test_rrf_does_not_add_incomparable_raw_scores():
    ranking, channels = fuse({"bm25": [("a", 10000), ("b", 1)], "dense": [("b", 0.9)]})
    assert ranking[0][0] == "b"
    assert channels["b"] == ["bm25", "dense"]


def test_metrics_missing_hits_and_duplicate_labels():
    result = metrics(["a", "a", "x"], ["a", "b"], 5)
    assert result["recall"] == 0.5
    assert result["precision"] == 0.2
    assert result["mrr"] == 1
    assert result["ndcg"] < 1
    with pytest.raises(ValueError):
        metrics([], [], 5)


def test_api_search_and_delete(service, tmp_path):
    file = tmp_path / "a.md"
    file.write_text("# Kubernetes\n\nrequests 调度，limits OOMKilled。")
    with TestClient(create_app(service)) as client:
        assert (
            client.post("/ingest", json={"path": str(file), "domain": "cloud"}).status_code == 200
        )
        response = client.post("/search", json={"query": "OOMKilled", "domain": "cloud"})
        assert response.status_code == 200
        assert response.json()["hits"][0]["chunk"]["locator"]
        assert not response.json()["configuration"]["semantic_model"]
        parent_id = response.json()["hits"][0]["chunk"]["parent_id"]
        parent = client.get(f"/parents/{parent_id}")
        assert parent.status_code == 200 and parent.json()["chunks"]
        assert client.get("/parents/missing").status_code == 404
        for payload in [
            {"query": " "},
            {"query": "a", "top_k": 0},
            {"query": "a", "strategy": "bad"},
        ]:
            assert client.post("/search", json=payload).status_code == 422
        assert client.delete("/sources", params={"source": str(file.resolve())}).json()[
            "deleted_chunks"
        ]


def test_snapshot_fingerprint_is_json_serializable(service):
    json.dumps(service.settings.fingerprint())


def test_new_runtime_policy_preserves_old_index_fingerprint():
    settings = Settings()
    assert "heading_context" not in settings.fingerprint()
    assert replace(settings, fusion_candidates="union").fingerprint() == settings.fingerprint()
    assert replace(settings, heading_context=True).fingerprint() != settings.fingerprint()


def test_heading_context_preserves_ancestors_and_ignores_markdown_lists():
    settings = Settings(heading_context=True, chunk_size=100)
    text = (
        "# CUDA\n\n## __syncthreads\n\n### 基本语义\n\n所有线程到达后继续。"
        "\n\n---\n\n2. 内存可见性规则。"
    )
    chunks = chunk_text(text, "cuda.md", "infra", DemoEncoder(), settings)
    assert chunks
    assert all(c.heading == "CUDA > __syncthreads > 基本语义" for c in chunks)
    assert not any(c.content.strip() == "---" for c in chunks)
    assert any("2. 内存可见性规则" in c.content for c in chunks)


def test_full_union_keeps_single_channel_evidence_for_reranking(tmp_path, monkeypatch):
    from infra_rag.models import Chunk

    settings = Settings(data_dir=tmp_path, candidate_k=2, rerank=True)
    service = RetrievalService(settings)

    class Encoder:
        def encode(self, texts, query=False):
            return [[1.0] for _ in texts] if query else [[1.0], [0.9], [0.1]]

    class Reranker:
        def predict(self, pairs):
            self.count = len(pairs)
            return [1.0 if text == "gold" else 0.0 for _, text in pairs]

    service.encoder = Encoder()
    service.reranker = Reranker()
    chunks = [
        Chunk(id=i, parent_id=i, source="fixture.md", content=text, domain="infra")
        for i, text in [("a", "common"), ("b", "dense"), ("z", "gold")]
    ]
    service._commit(chunks)
    monkeypatch.setattr("infra_rag.service.bm25", lambda *args: [("a", 1.0), ("z", 0.9)])
    assert service.search("query", top_k=1)[0].chunk.id != "z"
    assert service.reranker.count == 2
    service.settings = replace(settings, fusion_candidates="union")
    assert service.search("query", top_k=1)[0].chunk.id == "z"
    assert service.reranker.count == 3


def test_lexical_cache_respects_filters_and_ingestion(service, tmp_path):
    first, second = tmp_path / "first.md", tmp_path / "second.md"
    first.write_text("# CUDA\n\nWarp SharedMemory latency.")
    second.write_text("# training\n\nWarp gradient AllReduce.")
    service.ingest(first, "cuda")
    service.ingest(second, "training")
    hits = service.search("Warp", domain="cuda", strategy="bm25")
    eligible = [c for c in service.chunks if c.domain == "cuda"]
    assert [h.chunk.id for h in hits] == [i for i, _ in bm25("Warp", eligible)]
    assert service.lexical_cache
    first.write_text("# CUDA\n\nNewUniqueTerm kernel.")
    service.ingest(first, "cuda")
    assert not service.lexical_cache
    assert not service.search("SharedMemory", domain="cuda", strategy="bm25")
    assert service.search("NewUniqueTerm", domain="cuda", strategy="bm25")
    service.delete(str(first.resolve()))
    assert not service.search("NewUniqueTerm", domain="cuda", strategy="bm25")


def test_reranker_uses_query_text_pairs(service, tmp_path):
    file = tmp_path / "a.md"
    file.write_text("# epoll\n\nEAGAIN loop.\n\n# scheduling\n\nCPU scheduler.")
    service.ingest(file)
    service.settings = replace(service.settings, rerank=True)

    class TestReranker:
        pairs = None

        def predict(self, pairs):
            self.pairs = pairs
            return [1.0 if "scheduler" in document else 0.0 for query, document in pairs]

    service.reranker = TestReranker()
    hits = service.search("epoll scheduler", top_k=3)
    assert "scheduler" in hits[0].chunk.content
    assert hits[0].rerank_score == 1.0
    assert all(query == "epoll scheduler" for query, document in service.reranker.pairs)
