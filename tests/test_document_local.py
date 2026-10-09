"""Document-local scope must be query-side and preserve baseline evidence."""

import copy

import pytest

from infra_rag.document_local import DocumentLocalBM25
from infra_rag.models import Chunk


def chunk(cid, text, *, source="doc.md", release="v1", heading=""):
    return Chunk(
        cid,
        "parent-" + cid,
        source,
        text,
        "infra",
        heading=heading,
        locator=source + ":" + cid,
        metadata={"release": release},
    )


def hit(cid):
    return {"chunk_id": cid, "score": 0.1, "rerank_score": 0.8}


def test_nonadjacent_local_definition_retains_original_baseline_and_body():
    items = [
        chunk("a", "Cache overview."),
        chunk("b", "Unrelated introduction."),
        chunk("c", "num_kv_heads defines the cache size."),
    ]
    saved = copy.deepcopy(items)
    base = [hit("a")]
    pool, trace = DocumentLocalBM25(items).supplement(base, "num_kv_heads")
    assert [cid for cid, _ in pool] == ["a", "c"]
    assert trace["added_ids"] == ["c"]
    assert items == saved and base == [hit("a")]


def test_local_search_never_crosses_source_or_release():
    items = [
        chunk("a", "overview"),
        chunk("right", "cache formula"),
        chunk("wrong-release", "cache formula", release="v2"),
        chunk("wrong-source", "cache formula", source="other.md"),
    ]
    pool, trace = DocumentLocalBM25(items).supplement([hit("a")], "cache formula")
    assert {cid for cid, _ in pool} == {"a", "right"}
    assert trace["scopes"] == [{"source": "doc.md", "release": "v1"}]


def test_scope_uses_only_top10_and_first5_distinct_documents():
    items = [chunk(str(i), "cache formula", source=f"doc-{i}.md") for i in range(11)]
    index = DocumentLocalBM25(items)
    _, trace = index.supplement([hit(str(i)) for i in range(11)], "cache formula")
    assert trace["scopes"] == [{"source": f"doc-{i}.md", "release": "v1"} for i in range(5)]
    duplicate_scope = [hit("0")] * 2
    with pytest.raises(ValueError, match="duplicate"):
        index.supplement(duplicate_scope, "cache")


def test_supplement_capped_at30_and_cumulative_candidates_at90():
    items = [chunk(str(i), f"overview {i}" if i < 60 else f"cache formula {i}") for i in range(120)]
    pool, trace = DocumentLocalBM25(items).supplement([hit(str(i)) for i in range(60)], "cache")
    assert len(pool) == 90 and len(trace["added_ids"]) == 30
    assert len(pool) == len({cid for cid, _ in pool})
    assert {str(i) for i in range(60)} <= {cid for cid, _ in pool}
    with pytest.raises(ValueError, match="60"):
        DocumentLocalBM25(items).supplement([hit(str(i)) for i in range(61)], "cache")


def test_headings_are_searchable_empty_query_has_no_new_candidates_and_ties_are_stable():
    items = [
        chunk("a", "overview"),
        chunk("c", "same text", heading="num_kv_heads"),
        chunk("b", "same text", heading="num_kv_heads"),
    ]
    index = DocumentLocalBM25(items)
    pool, _ = index.supplement([hit("a")], "num_kv_heads")
    assert [cid for cid, _ in pool] == ["a", "b", "c"]
    assert index.supplement([hit("a")], "")[0] == [("a", 0.1)]
    assert index.supplement([], "num_kv_heads")[0] == []
    with pytest.raises(ValueError, match="unknown"):
        index.supplement([hit("missing")], "cache")
    with pytest.raises(ValueError, match="duplicate"):
        DocumentLocalBM25(items + [items[0]])


def test_index_identity_changes_when_heading_source_release_or_body_changes():
    items = [chunk("a", "body")]
    identity = DocumentLocalBM25(items).identity
    for field, value in [
        ("content", "different"),
        ("heading", "changed"),
        ("source", "other.md"),
        ("metadata", {"release": "v2"}),
    ]:
        changed = copy.deepcopy(items)
        setattr(changed[0], field, value)
        assert DocumentLocalBM25(changed).identity != identity
