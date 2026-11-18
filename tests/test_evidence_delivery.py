"""Oversize source coverage, safe render attribution and explicit continuation semantics."""

import copy

import pytest

from infra_rag.corpus_pilot import prepare_document
from infra_rag.evidence_delivery import pack_delivery, resolve_deferred, validate_resolved
from infra_rag.structural_pilot import chunk_document


def fixture(text, limit=100):
    prepared = prepare_document(text.encode())
    prepared["status"] = "auto_pass"
    for i, unit in enumerate(prepared["units"]):
        unit["unit_id"] = str(i)
    row = {
        "document_id": "doc",
        "input_sha256": "hash",
        "source_url": "source",
        "commit": "c",
        "coordinate_type": "source_lines",
    }
    counters = {"a": len, "b": lambda s: len(s) + 1 if s else 0}
    old = chunk_document(row, prepared, counters, limit=limit)
    return old, counters


@pytest.mark.parametrize(
    "text",
    [
        "# Code\n\nOnly use if enabled.\n\n```python\n" + "print(1)\n" * 60 + "```\n",
        "# Table\n\n| A | B |\n|---|---|\n" + "| x | y |\n" * 60,
        "# Condition\n\nOnly if enabled, " + "must preserve these conditions. " * 30,
        "# Long line\n\n```text\n" + "x" * 600 + "\n```\n",
    ],
)
def test_deferred_resolved_without_dropping_characters_or_old_ids(text):
    old, counters = fixture(text)
    assert old["deferred"]
    before = copy.deepcopy(old)
    new = resolve_deferred(old, counters)
    result = validate_resolved(old, new, counters)
    assert result["remaining_deferred"] == 0
    assert result["source_character_coverage"] == 1
    assert old == before
    originals = {c["chunk_id"]: c for c in new["children"]}
    assert all(originals[c["chunk_id"]] == c for c in old["children"])
    for c in new["children"]:
        if "rendering" in c:
            assert c["content"].startswith(("```", "~~~~")) or c["fragments"][0]["kind"] not in {
                "table",
                "code",
            }


def test_real_pages_have_no_silent_omissions_and_do_not_claim_single_context_completion():
    old, counters = fixture("# Code\n\nOnly if enabled.\n\n```py\n" + "x=100\n" * 70 + "```\n")
    new = resolve_deferred(old, counters)
    hit = new["continued_chunk_ids"][0]
    cursor, pages, ids = None, [], []
    while True:
        page = pack_delivery(
            [hit], [new], counters, token_budget=300, char_budget=300, cursor=cursor
        )
        assert page["status"] != "blocked"
        assert all(v <= 300 for v in page["token_counts"].values())
        assert page["used_characters"] <= 300
        pages.append(page)
        ids.extend(e["chunk_id"] for e in page["evidence"])
        if not page["continuation"]:
            break
        cursor = page["continuation"]
    assert len(pages) > 1
    assert ids == pages[0]["required_chunk_ids"]
    assert all(not p["answer_ready"] and p["warning"] for p in pages)
    assert pages[-1]["status"] == "final_page"
    assert pages[-1]["remaining_chunk_ids"] == []


def test_small_budget_blocks_explicitly_and_cursor_is_bound_to_source_and_budget():
    old, counters = fixture("# A\n\nOnly if enabled.\n\n```py\n" + "x=1\n" * 50 + "```\n")
    new = resolve_deferred(old, counters)
    hit = new["continued_chunk_ids"][0]
    blocked = pack_delivery([hit], [new], counters, token_budget=1, char_budget=1)
    assert blocked["status"] == "blocked"
    assert blocked["blocked_chunk_ids"] and blocked["remaining_chunk_ids"]
    assert not blocked["answer_ready"] and blocked["continuation"] is None
    page = pack_delivery([hit], [new], counters, token_budget=300, char_budget=300)
    assert page["continuation"]
    with pytest.raises(ValueError, match="different"):
        pack_delivery(
            [hit], [new], counters, token_budget=301, char_budget=300, cursor=page["continuation"]
        )


def test_synthetic_wrapper_or_source_corruption_is_rejected():
    old, counters = fixture("# T\n\n| A | B |\n|---|---|\n" + "| x | y |\n" * 60)
    new = resolve_deferred(old, counters)
    c = next(c for c in new["children"] if "rendering" in c)
    c["rendering"]["prefix"] += "FAKE HEADER"
    with pytest.raises(ValueError, match="Rendering"):
        validate_resolved(old, new, counters)


def test_empty_hits_do_not_authorize_answer():
    result = pack_delivery([], [], {"a": len})
    assert not result["answer_ready"]
    assert result["status"] == "no_evidence"


def test_whole_document_deferred_requires_explicit_source_provenance():
    old, counters = fixture("Only if enabled: " + "x" * 500)
    assert not old["children"]
    with pytest.raises(ValueError, match="provenance"):
        resolve_deferred(old, counters)
    provenance = {
        "document_id": "doc",
        "input_sha256": "hash",
        "source_url": "source",
        "commit": "c",
        "coordinate_type": "source_lines",
    }
    new = resolve_deferred(old, counters, provenance=provenance)
    assert validate_resolved(old, new, counters)["source_character_coverage"] == 1
    assert all(c["source_url"] == "source" for c in new["children"])
