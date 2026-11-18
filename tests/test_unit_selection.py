import json

import pytest

from infra_rag.paged_answers import select_within_budget, verify_selections


def test_ids_only_exact_source_and_duplicate_rejection():
    source = [
        {
            "citation_id": "canonical",
            "content": "Only if enabled.\n```py\nx=1\n```",
            "locator": "url",
        }
    ]
    selected = verify_selections(
        json.dumps({"selections": [{"id": "E1", "relevance": "direct"}]}), source
    )
    assert selected[0]["content"] == source[0]["content"]
    assert selected[0]["citation_id"] == "canonical"
    for ids in (["E2"], ["E1", "E1"]):
        with pytest.raises(ValueError):
            verify_selections(
                json.dumps({"selections": [{"id": cid, "relevance": "direct"} for cid in ids]}),
                source,
            )


def test_whole_units_priority_dedup_and_budget():
    a = {
        "citation_id": "E1",
        "content": "a" * 60,
        "locator": "url",
        "selection_relevance": "background",
    }
    b = {
        "citation_id": "E2",
        "content": "b" * 60,
        "locator": "url",
        "selection_relevance": "direct",
    }
    context, omitted = select_within_budget([a, b, b], {"t": len}, 100, 100)
    assert context["evidence"][0]["content"] == "b" * 60
    assert omitted == [{"citation_id": "E1", "reason": "budget"}]
    with pytest.raises(ValueError):
        select_within_budget([b], {"t": len}, 10, 10)
