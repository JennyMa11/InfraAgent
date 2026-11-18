"""Model contracts and provenance regressions, without downloading neural models."""

import json
import sys
from dataclasses import replace
from types import SimpleNamespace

import pytest

from infra_rag.chunking import chunk_text
from infra_rag.config import Settings
from infra_rag.embedding_experiments import (
    BASELINE,
    chunk_evidence,
    chunk_variants,
    delivered_intervals,
    deterministic_sample,
    freeze_gold,
    interval_score,
    mapped_chunk,
    select_candidate,
    source_document,
)
from infra_rag.encoding import DemoEncoder, QwenEncoder
from infra_rag.models import Chunk
from infra_rag.service import RetrievalService
from infra_rag.text_chunking import window_ranges


def qwen_double(monkeypatch):
    np = pytest.importorskip("numpy")

    class Model:
        def __init__(self, *args, **kwargs):
            self.max_seq_length = 32768
            self.tokenizer = SimpleNamespace(encode=lambda text, **kw: list(text))
            self.calls = []

        def __getitem__(self, index):
            return SimpleNamespace(pooling_mode_lasttoken=True)

        def encode(self, texts, **kwargs):
            self.calls.append((texts, kwargs))
            vectors = np.zeros((len(texts), 1024))
            vectors[:, 0] = 1
            return vectors

    monkeypatch.setitem(
        sys.modules, "sentence_transformers", SimpleNamespace(SentenceTransformer=Model)
    )
    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(float32="float32"))
    return QwenEncoder(max_length=200)


def test_qwen_uses_prompt_only_for_queries_and_native_dimension(monkeypatch):
    encoder = qwen_double(monkeypatch)
    assert len(encoder.encode(["document"])[0]) == 1024
    encoder.encode(["query"], query=True)
    assert encoder.model.calls[0][1]["prompt"] == ""
    assert encoder.model.calls[1][1]["prompt"] == encoder.query_prompt
    assert encoder.model.calls[1][1]["normalize_embeddings"]
    assert encoder.model.tokenizer.padding_side == "left"
    assert encoder.encode([]) == []


def test_qwen_checks_prompt_inclusive_length_before_encode(monkeypatch):
    encoder = qwen_double(monkeypatch)
    with pytest.raises(ValueError, match="silent truncation"):
        encoder.encode(["x" * 200], query=True)
    assert encoder.model.calls == []


def test_qwen_rejects_invalid_embeddings(monkeypatch):
    encoder = qwen_double(monkeypatch)
    np = pytest.importorskip("numpy")
    encoder.model.encode = lambda *a, **k: np.ones((1, 1024))
    with pytest.raises(ValueError, match="unnormalized"):
        encoder.encode(["text"])
    encoder.model.encode = lambda *a, **k: np.ones((1, 384))
    with pytest.raises(ValueError, match="1024"):
        encoder.encode(["text"])


def test_old_fingerprint_and_cache_namespace_are_preserved(tmp_path):
    settings = Settings(data_dir=tmp_path)
    fp = settings.fingerprint()
    for field in (
        "embedding_revision",
        "embedding_device",
        "embedding_batch_size",
        "embedding_query_prompt",
        "embedding_max_length",
        "chunk_overlap",
    ):
        assert field not in fp
    assert fp["embedding_pooling"] == "token-window-mean-v1"
    assert RetrievalService(settings)._text_namespace() == {
        "backend": "demo",
        "model": "hash-v1",
        "pooling": "token-window-mean-v1",
    }
    assert replace(settings, embedding_device="cpu", embedding_batch_size=2).fingerprint() == fp


def test_qwen_cache_and_index_isolate_revision_prompt_and_model(tmp_path):
    settings = Settings(
        data_dir=tmp_path, backend="qwen", embedding_model="Qwen/Qwen3-Embedding-0.6B"
    )
    variants = [
        settings,
        replace(settings, embedding_revision="revision-b"),
        replace(settings, embedding_query_prompt="different instruction"),
        replace(settings, embedding_max_length=1024),
    ]
    assert len({json.dumps(s.fingerprint(), sort_keys=True) for s in variants}) == 4
    assert (
        len({json.dumps(RetrievalService(s)._text_namespace(), sort_keys=True) for s in variants})
        == 4
    )


def test_qwen_snapshot_restart_and_incompatible_revision(tmp_path):
    settings = Settings(data_dir=tmp_path / "db", backend="qwen", embedding_model="Qwen/test")
    service = RetrievalService(settings)
    service.encoder = DemoEncoder()
    service._collections = lambda *a: (None, None)
    source = tmp_path / "source.txt"
    source.write_text("# Heading\n\nKV Cache stores keys and values.")
    service.ingest(source)
    restored = RetrievalService(settings)
    assert restored.chunks == service.chunks
    with pytest.raises(ValueError, match="configuration mismatch"):
        RetrievalService(replace(settings, embedding_revision="new"))
    assert restored.status()["semantic_model"]
    assert restored.status()["embedding_model"] == "Qwen/test"


@pytest.mark.parametrize(
    "text", ["中文测试。" * 20, "```python\nx = 1\n```\n" * 10, "| A | B |\n" * 20]
)
def test_overlap_windows_cover_original_text_with_exact_positions(text):
    settings = Settings(chunk_strategy="window_overlap", chunk_size=100, chunk_overlap=20)
    chunks = chunk_text(text, "source.md", "infra", DemoEncoder(), settings)
    covered = set()
    for chunk in chunks:
        first, last = chunk.metadata["text_char_range"]
        assert chunk.content == text[first:last]
        assert len(chunk.content) <= 100
        assert chunk.start_line == text.count("\n", 0, first) + 1
        assert chunk.end_line == text.count("\n", 0, last - 1) + 1
        covered.update(range(first, last))
    assert covered == set(range(len(text)))
    assert len({c.id for c in chunks}) == len(chunks)


def test_window_progress_with_tiny_token_limit_and_empty_input():
    counter = SimpleNamespace(token_length=len, token_limit=3)
    ranges = window_ranges("abcdefgh", 100, counter, overlap=90)
    assert all(b > a for a, b in ranges)
    assert ranges[-1][1] == 8
    assert window_ranges("", 100, counter) == []
    with pytest.raises(ValueError):
        window_ranges("text", 100, counter, overlap=100)


def test_fixed_context_counter_is_used_instead_of_model_tokenizer(tmp_path):
    service = RetrievalService(Settings(data_dir=tmp_path), context_counter=lambda text: len(text))
    source = tmp_path / "source.md"
    source.write_text("# Cache\n\nKV Cache holds keys and values.")
    service.ingest(source)
    pack = {}
    service.search("KV Cache", strategy="bm25", context_pack=pack)
    assert pack["token_count_method"] == "fixed_external_tokenizer"
    assert pack["used_tokens"] == len(pack["context"])


def test_qwen_query_diagnostics_describe_native_pooling_and_include_prompt(tmp_path):
    service = RetrievalService(Settings(data_dir=tmp_path, backend="qwen"), context_counter=len)
    chunk = Chunk("id", "parent", "source", "KV Cache", "infra")
    service.chunks = [chunk]
    service._index_parents()
    service.encoder = SimpleNamespace(
        encode=lambda *a, **kw: [[1.0, 0.0]],
        token_length=len,
        token_limit=8190,
        query_prompt="instruction:",
    )
    service.text_collection = SimpleNamespace(
        query=lambda **kw: {"ids": [["id"]], "distances": [[0.0]]}
    )
    diagnostic = {}
    service.search("Cache", strategy="dense", diagnostics=diagnostic)
    query = diagnostic["dense_query"]
    assert query["input_tokens"] == len("instruction:Cache")
    assert query["handling"] == "native_last_token_reject_overflow"
    assert query["windows"] == 1


def mapped(content, ranges, sha="frozen"):
    return {
        "source": "doc",
        "content": content,
        "metadata": {"source_sha256": sha, "source_normalized_ranges": ranges},
    }


def test_evidence_union_merges_overlap_but_never_bridges_missing_source():
    documents = {"doc": source_document("ABCDEF", "frozen")}
    gold = [[{"source": "doc", "occurrences": [[0, 6]]}]]
    overlap = delivered_intervals(
        [mapped("ABCD", [[0, 0, 4]]), mapped("CDEF", [[0, 2, 4]])], documents
    )
    assert overlap == {"doc": [[0, 6]]}
    assert interval_score(overlap, gold)["complete"] == 1
    gap = delivered_intervals([mapped("AB", [[0, 0, 2]]), mapped("EF", [[0, 4, 2]])], documents)
    assert interval_score(gap, gold)["complete"] == 0


def test_truncated_body_and_synthetic_text_cannot_earn_missing_evidence():
    documents = {"doc": source_document("ABCDEF", "frozen")}
    gold = [[{"source": "doc", "occurrences": [[0, 6]]}]]
    prefix = delivered_intervals([mapped("AB", [[0, 0, 6]])], documents)
    assert interval_score(prefix, gold)["complete"] == 0
    with pytest.raises(ValueError, match="body differs"):
        delivered_intervals([mapped("ABXDEF", [[0, 0, 6]])], documents)
    with pytest.raises(ValueError, match="hash"):
        delivered_intervals([mapped("ABCDEF", [[0, 0, 6]], "different")], documents)


def test_gold_and_mapped_structural_blocks_preserve_source_and_symbols():
    document = source_document("# Title\n\nA must not use +1.\n", "frozen")
    chunk = Chunk("id", "parent", "doc", "A must not use +1.", "infra", start_line=3, end_line=3)
    chunk = mapped_chunk(chunk, document)
    case = {
        "id": "case",
        "answerable": True,
        "evidence_alternatives": [
            {"spans": [{"absolute_source": "doc", "text": "must not use +1"}]}
        ],
    }
    gold = freeze_gold(case, {"doc": document})
    intervals = delivered_intervals([chunk_evidence(chunk)], {"doc": document})
    assert interval_score(intervals, gold)["complete"] == 1
    case["evidence_alternatives"][0]["spans"][0]["text"] = "must not use -1"
    with pytest.raises(ValueError, match="absent"):
        freeze_gold(case, {"doc": document})


def test_variants_reuse_structural_ids_and_common_source_positions():
    text = "# Heading\n\n" + "The source has a necessary condition. " * 40
    doc = source_document(text, "frozen")
    original = Chunk("original", "parent", "doc", "# Heading", "infra", start_line=1, end_line=1)
    counter = SimpleNamespace(token_length=len, token_limit=510)
    variants = chunk_variants([original], {"doc": doc}, counter)
    assert variants["structure"][0].id == "original"
    for arm in ("window", "overlap"):
        assert len({c.id for c in variants[arm]}) == len(variants[arm])
        actual = delivered_intervals([chunk_evidence(c) for c in variants[arm]], {"doc": doc})
        assert actual == {"doc": [[0, len(doc["normalized"])]]}
        assert all(c.heading == "Heading" for c in variants[arm])


def test_answer_sample_is_frozen_independently_of_input_order():
    cases = [
        {
            "dataset": ds,
            "id": f"{ds}-{answerable}-{i}",
            "answerable": answerable,
            "question_type": str(i % 3),
        }
        for ds, answerable, n in (
            ("official", True, 20),
            ("official", False, 6),
            ("repository", True, 20),
        )
        for i in range(n)
    ]
    sample = deterministic_sample(cases)
    assert sample == deterministic_sample(cases[::-1])
    assert len(sample) == len(set(sample)) == 20
    assert sum(ds == "official" for ds, _ in sample) == 10
    assert sum("False" in cid for _, cid in sample) == 2


def test_candidate_requires_measured_latency_and_both_dataset_gates():
    def row(official, repository, p95=None):
        return {
            "errors": 0,
            **{
                ds: {"delivery": {"numerator": n}, "candidate_complete": {"numerator": n}}
                for ds, n in (("official", official), ("repository", repository))
            },
            "warm_latency": {"p95_ms": p95} if p95 else None,
        }

    summary = {
        BASELINE: row(10, 10, 100),
        "qwen-structure-hybrid_rerank": row(12, 10),
        "qwen-window-hybrid_rerank": row(20, 9, 50),
        "qwen-overlap-hybrid_rerank": row(11, 11, 151),
    }
    assert not select_candidate(summary)["qualified"]
    summary["qwen-structure-hybrid_rerank"]["warm_latency"] = {"p95_ms": 150}
    decision = select_candidate(summary)
    assert decision["qualified"]
    assert decision["candidate"] == "qwen-structure-hybrid_rerank"
