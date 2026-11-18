from dataclasses import replace

import pytest

from infra_rag.complete_context import pack_complete_context
from infra_rag.config import Settings
from infra_rag.models import Chunk, Hit
from infra_rag.runtime import RuntimeRetrieval
from infra_rag.service import RetrievalService


def hit(cid, text, *, parent=None):
    return Hit(
        Chunk(
            cid,
            parent or cid,
            f"{cid}.md",
            text,
            "infra",
            locator=f"{cid}.md#L1",
            start_line=1,
            end_line=1,
        ),
        1.0,
    )


def test_whole_selection_preserves_late_answer_and_skips_redundant_prefixes():
    ranked = [
        hit("a", "Common mechanism. " * 3),
        hit("b", "Common mechanism. " * 5),
        hit("c", "Specific branch: full 512+64 dimensions, no rotation."),
    ]
    packed = pack_complete_context(ranked[:2], ranked, "Specific branch dimensions", len, 180, 180)
    assert [e["chunk_id"] for e in packed["evidence"]] == ["a", "c"]
    assert "512+64" in packed["context"]
    assert packed["delivery_only_chunk_ids"] == ["c"]
    assert packed["omitted_chunk_ids"] == ["b"]
    assert all(not e["truncated"] for e in packed["evidence"])
    assert packed["evidence"][1]["content"] == ranked[2].chunk.content
    assert ranked[0].chunk.content == "Common mechanism. " * 3


def test_oversized_code_omitted_with_reason_and_small_unit_survives():
    ranked = [hit("code", "```python\n" + "x=1\n" * 100 + "```"), hit("b", "Small evidence.")]
    packed = pack_complete_context(ranked, ranked, "code", len, 100, 100)
    assert [e["chunk_id"] for e in packed["evidence"]] == ["b"]
    assert packed["omissions"] == [
        {"chunk_id": "code", "reason": "whole_body_exceeds_remaining_budget"}
    ]
    assert packed["used_characters"] <= 100


def test_parent_dedup_and_stable_citations():
    ranked = [hit("a", "first.", parent="p"), hit("b", "second.", parent="p")]
    packed = pack_complete_context(ranked, ranked, "first second", len, 200, 200)
    assert len(packed["evidence"]) == 2
    assert len({e["citation_id"] for e in packed["evidence"]}) == 2
    assert ranked[0].sibling_ids == [e["chunk_id"] for e in packed["evidence"]]
    assert not ranked[1].evidence


def test_policy_keeps_index_and_ranking_and_invalidates_runtime_cache(tmp_path):
    settings = Settings(data_dir=tmp_path / "index")
    complete = replace(settings, context_policy="complete")
    assert settings.fingerprint() == complete.fingerprint()
    runtime = RuntimeRetrieval(RetrievalService(settings), cache_size=2)
    runtime.service._commit([hit("a", "Specific branch dimensions.").chunk])
    before = runtime.search("Specific branch")
    runtime.service.settings = complete
    diagnostics, context = {}, {}
    after = runtime.search("Specific branch", diagnostics=diagnostics, context_pack=context)
    assert not diagnostics["retrieval_cache"]["hit"]
    assert [(h.chunk.id, h.score) for h in before] == [(h.chunk.id, h.score) for h in after]
    assert context["policy"] == "complete-v2"
    with pytest.raises(ValueError, match="neighbors"):
        replace(complete, context_mode="legacy")
