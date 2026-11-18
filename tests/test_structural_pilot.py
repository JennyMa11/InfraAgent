"""Source conservation and explicit context/deferred handling in chunk pilots."""

import copy

import pytest

from infra_rag.corpus_pilot import prepare_document
from infra_rag.structural_pilot import chunk_document, select_documents, validate_document


def prepared(text):
    artifact = prepare_document(text.encode())
    artifact["status"] = "auto_pass"
    for i, unit in enumerate(artifact["units"]):
        unit["unit_id"] = f"u{i}"
    return artifact


def row(cid="doc"):
    return {
        "document_id": cid,
        "input_sha256": "hash",
        "source_url": "source",
        "commit": "commit",
        "coordinate_type": "source_lines",
    }


def test_source_coverage_and_protected_atoms_are_never_truncated():
    artifact = prepared(
        "# KV\n\nOnly if enabled; not in older versions.\n\n"
        "```python\n" + "x=100\n" * 40 + "```\n\n"
        "| A | B |\n|---|---|\n| 1 | 2 |\n\n$$\nx=1\n$$\n"
    )
    counter = {"test": len}
    result = chunk_document(row(), artifact, counter, limit=100)
    # Validator uses the frozen budget from each output, not a separate assumed limit.
    before = copy.deepcopy(artifact)
    summary = validate_document(artifact, result, counter)
    assert artifact == before
    assert summary["deferred_fragments"] >= 1
    assert (
        summary["child_body_characters"] + summary["deferred_characters"]
        == summary["unit_body_characters"]
    )
    assert any(f["kind"] == "code" and "x=100" in f["content"] for f in result["deferred"])
    assert result == chunk_document(row(), artifact, counter, limit=100)


def test_token_count_includes_heading_and_long_sentence_is_deferred():
    artifact = prepared("# A very long heading\n\n" + "a" * 100 + "\n")
    result = chunk_document(row(), artifact, {"test": len}, limit=40)
    assert any(f["kind"] == "paragraph" for f in result["deferred"])
    assert all(len(c["retrieval_text"]) <= 40 for c in result["children"])
    validate_document(artifact, result, {"test": len})


def test_description_and_condition_can_require_parent_context():
    artifact = prepared("# A\n\nIf enabled, use exactly this parameter.\n\n```py\nx=1\n```\n")
    result = chunk_document(row(), artifact, {"test": len}, limit=50)
    child = next(c for c in result["children"] if any(f["kind"] == "code" for f in c["fragments"]))
    assert child["needs_parent_context"]
    assert child["context_unit_ids"]
    validate_document(artifact, result, {"test": len})


def test_mutated_fragment_or_token_count_fails_validation():
    artifact = prepared("# A\n\nA short sentence.\n")
    result = chunk_document(row(), artifact, {"test": len}, limit=100)
    bad = copy.deepcopy(result)
    bad["children"][0]["fragments"][0]["content"] += "BAD"
    with pytest.raises(ValueError):
        validate_document(artifact, bad, {"test": len})
    bad = copy.deepcopy(result)
    bad["children"][0]["token_counts"]["test"] = 0
    with pytest.raises(ValueError):
        validate_document(artifact, bad, {"test": len})


def test_selection_only_auto_pass_two_per_repository_and_order_independent():
    rows = [
        {
            "document_id": str(i),
            "repository": "r" + str(i // 4),
            "features": ["code"] if i % 2 else [],
        }
        for i in range(8)
    ]
    artifacts = {
        r["document_id"]: {"status": "auto_pass" if int(r["document_id"]) % 4 != 3 else "review"}
        for r in rows
    }
    selection = select_documents(rows, artifacts)
    assert len(selection) == 4
    assert selection == select_documents(list(reversed(rows)), artifacts)
    assert all(artifacts[r["document_id"]]["status"] == "auto_pass" for r in selection)


def test_pending_input_is_rejected_and_inline_math_not_split():
    artifact = prepared("# A\n\nKeep $x=1$ and `a;b` together.\n")
    result = chunk_document(row(), artifact, {"test": len}, limit=100)
    assert all(f["unit_char_range"][0] == 0 for c in result["children"] for f in c["fragments"])
    artifact["status"] = "review"
    with pytest.raises(ValueError):
        chunk_document(row(), artifact, {"test": len})


def test_unmapped_child_suffix_and_altered_retrieval_are_rejected():
    artifact = prepared("# A\n\nExact source text.\n")
    result = chunk_document(row(), artifact, {"test": len}, limit=100)
    for field in ("content", "retrieval_text"):
        bad = copy.deepcopy(result)
        bad["children"][0][field] += " UNGROUNDED"
        with pytest.raises(ValueError, match="Unmapped"):
            validate_document(artifact, bad, {"test": len})


def test_deferred_must_actually_exceed_budget():
    artifact = prepared("# A\n\n" + "a" * 100 + "\n")
    result = chunk_document(row(), artifact, {"test": len}, limit=40)
    result["deferred"][0]["token_counts"]["test"] = 0
    with pytest.raises(ValueError, match="Deferred budget"):
        validate_document(artifact, result, {"test": len})
