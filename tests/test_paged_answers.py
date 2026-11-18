import json

import pytest

from infra_rag.paged_answers import final_context, verify_quotes


def evidence():
    return [
        {"citation_id": "Esource", "content": "Only if enabled.\nstate_dict()", "locator": "url"}
    ]


def test_extracts_only_exact_source_quotes():
    good = json.dumps({"quotes": [{"id": "E1", "quote": "Only if enabled."}]})
    verified = verify_quotes(good, evidence())
    assert verified[0]["citation_id"] == "Esource"
    assert verified[0]["original_char_range"] == [0, 16]
    for cid, quote in [("E2", "Only if enabled."), ("E1", "Always enabled.")]:
        with pytest.raises(ValueError):
            verify_quotes(json.dumps({"quotes": [{"id": cid, "quote": quote}]}), evidence())


def test_final_budget_never_silently_discards_conditions():
    quotes = verify_quotes(
        json.dumps(
            {
                "quotes": [
                    {"id": "E1", "quote": "Only if enabled."},
                    {"id": "E1", "quote": "state_dict()"},
                ]
            }
        ),
        evidence(),
    )
    ctx = final_context(quotes, {"test": len}, token_limit=100, char_limit=100)
    assert len(ctx["evidence"]) == 1
    assert "Only if enabled." in ctx["evidence"][0]["content"]
    assert "state_dict()" in ctx["evidence"][0]["content"]
    with pytest.raises(ValueError, match="budget"):
        final_context(quotes, {"test": len}, token_limit=10)


def test_excerpt_mapping_does_not_credit_unseen_source_text():
    source = [
        {
            "citation_id": "Esource",
            "document_id": "d",
            "content": "abcdefghij",
            "locator": "url",
            "fragments": [
                {
                    "unit_id": "u",
                    "content": "abcdefghij",
                    "unit_char_range": [10, 20],
                    "body_char_range": [0, 10],
                }
            ],
        }
    ]
    quotes = verify_quotes(
        json.dumps({"quotes": [{"id": "E1", "quote": "bc"}, {"id": "E1", "quote": "hi"}]}), source
    )
    final = final_context(quotes, {"test": len})["evidence"][0]
    assert [f["unit_char_range"] for f in final["fragments"]] == [[11, 13], [17, 19]]
    for f in final["fragments"]:
        a, b = f["body_char_range"]
        assert final["content"][a:b] == f["content"]
