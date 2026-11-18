from dataclasses import replace

import pytest

from infra_rag.config import Settings
from infra_rag.context import pack_context
from infra_rag.embedding_experiments import source_document
from infra_rag.grid_delivery import score_delivery
from infra_rag.grid_v2 import Arm, delivery_gate, recall_arms, refinements, source_ndcg
from infra_rag.models import Chunk, Hit
from infra_rag.service import RetrievalService, fuse


def test_runtime_knobs_preserve_index_and_validate_limits():
    base = Settings()
    other = replace(
        base, rrf_constant=30, rerank_top_n=30, candidate_pool_cap=90, neighbor_expansion=False
    )
    assert base.fingerprint() == other.fingerprint()
    for kw in ({"rrf_constant": 0}, {"rerank_top_n": 91}, {"candidate_pool_cap": 100}):
        with pytest.raises(ValueError):
            replace(base, **kw)
    rankings = {"a": [("a", 1), ("b", 1)], "b": [("b", 1)]}
    assert fuse(rankings) == fuse(rankings, 60)
    assert fuse(rankings, 30)[0] != fuse(rankings, 60)[0]


def test_depth_sorts_only_scored_prefix_and_caps_union(tmp_path, monkeypatch):
    service = RetrievalService(
        Settings(
            data_dir=tmp_path, rerank=True, candidate_k=5, candidate_pool_cap=4, rerank_top_n=2
        )
    )
    service._commit([Chunk(str(i), str(i), "s.md", f"word {i}", "infra") for i in range(6)])
    monkeypatch.setattr("infra_rag.service.bm25", lambda *a: [(str(i), 6 - i) for i in range(6)])

    class Reranker:
        def predict(self, pairs):
            assert len(pairs) == 2
            return [0.1, 0.9]

    service.reranker = Reranker()
    detail = {}
    hits = service.search("word", top_k=4, strategy="bm25", diagnostics=detail)
    assert [h.chunk.id for h in hits] == ["1", "0", "2", "3"]
    assert [h.rerank_score for h in hits] == [0.9, 0.1, None, None]
    assert len(detail["candidates"]) == 4 and len(detail["fusion"]) == 5


def test_neighbor_ablation_keeps_shared_budget_and_descriptions_out():
    a = Chunk("a", "p", "s.md", "Matched.", "infra", metadata={"description_lines": [2, 2]})
    b = Chunk("b", "p", "s.md", "Neighbor.", "infra", start_line=2)
    hits = [Hit(a, 1)]
    packed = pack_context(hits, {"p": [a, b]}, len, 100, 100, neighbor_expansion=False)
    assert [e["chunk_id"] for e in packed["evidence"]] == ["a"]
    assert packed["used_tokens"] <= 100


def test_delivery_does_not_join_across_truncated_gap():
    docs = {"s": source_document("First missing\nSecond", "hash")}
    a = Chunk("a", "p", "s", "First missing", "infra", start_line=1, end_line=1)
    b = Chunk("b", "p", "s", "Second", "infra", start_line=2, end_line=2)
    q = {
        "id": "q",
        "answerable": True,
        "evidence_alternatives": [
            {"spans": [{"absolute_source": "s", "text": "First missing\nSecond"}]}
        ],
    }
    evidence = [
        {"chunk_id": "a", "source": "s", "content": "First"},
        {"chunk_id": "b", "source": "s", "content": "Second"},
    ]
    assert not score_delivery(evidence, q, {"a": a, "b": b}, docs)["complete"]
    evidence[0]["content"] = a.content
    assert score_delivery(evidence, q, {"a": a, "b": b}, docs)["complete"]


def test_grid_axes_and_ndcg_do_not_count_duplicates_as_extra_evidence():
    assert len({a.identity() for a in recall_arms("I0")}) == 9
    assert len(refinements(Arm(rerank=True))) == 7
    assert all(a.neighbors is not False for a in refinements(Arm(policy="complete")))
    assert source_ndcg(["a", "a", "b"], {"a", "b"}, 2) < 1
    assert source_ndcg(["a", "b"], {"a", "b"}, 2) == 1
    assert source_ndcg(["a"], set(), 5) is None


def test_paired_gate_keeps_partial_regressions_and_negative_denominators_separate():
    before = [
        {"dataset": "d", "id": "a", "answerable": True, "delivery5": {"complete": 1}},
        {"dataset": "d", "id": "b", "answerable": True, "delivery5": {"complete": 0}},
        {"dataset": "d", "id": "negative", "answerable": False, "delivery5": None},
    ]
    after = [
        {**r, "delivery5": {"complete": 1 - r["delivery5"]["complete"]}} if r["answerable"] else r
        for r in before
    ]
    gate = delivery_gate(after, before)
    assert not gate["eligible"] and gate["net"] == 0 and gate["losses"] == [("d", "a")]
    with pytest.raises(ValueError, match="paired"):
        delivery_gate(after + after[:1], before)


def test_source_alias_earns_credit_only_from_its_mapped_body():
    c = Chunk(
        "a",
        "p",
        "canonical",
        "alpha",
        "infra",
        start_line=1,
        end_line=1,
        metadata={"source_aliases": [{"source": "alias", "metadata": {"original_lines": [1, 1]}}]},
    )
    docs = {s: source_document("alpha", "hash") for s in ("canonical", "alias")}
    q = {
        "id": "q",
        "answerable": True,
        "evidence_alternatives": [{"spans": [{"absolute_source": "alias", "text": "alpha"}]}],
    }
    evidence = [{"chunk_id": "a", "source": "canonical", "content": "alpha"}]
    assert score_delivery(evidence, q, {"a": c}, docs)["complete"]
    evidence[0]["content"] = "al"
    assert not score_delivery(evidence, q, {"a": c}, docs)["complete"]


def test_window_alias_uses_its_own_character_offsets():
    c = Chunk(
        "a",
        "p",
        "canonical",
        "alpha",
        "infra",
        start_line=2,
        end_line=2,
        metadata={
            "text_char_range": [2, 7],
            "source_aliases": [
                {
                    "source": "alias",
                    "metadata": {"text_char_range": [0, 5], "original_lines": [1, 1]},
                }
            ],
        },
    )
    docs = {
        "canonical": source_document("x\nalpha", "hash1"),
        "alias": source_document("alpha", "hash2"),
    }
    q = {
        "id": "q",
        "answerable": True,
        "evidence_alternatives": [{"spans": [{"absolute_source": "alias", "text": "alpha"}]}],
    }
    evidence = [{"chunk_id": "a", "source": "canonical", "content": "alpha"}]
    assert score_delivery(evidence, q, {"a": c}, docs)["complete"]
