import copy
import json

import pytest

from infra_rag.budget_evidence import budget_pack
from infra_rag.claim_guard import (
    STRENGTH_PROMPT,
    generate_experimental,
    guarded_response,
    parse_verdict,
    verify_answer,
)
from infra_rag.config import Settings
from infra_rag.models import Chunk, Hit


def hit(cid, text, score=0.8, parent="p", source="notes.md", heading=False):
    c = Chunk(
        cid,
        parent,
        source,
        text,
        "infra",
        heading="Evidence",
        metadata={"body_type": "heading" if heading else "explanation"},
    )
    return Hit(c, 0.1, rerank_score=score)


def test_budget_selection_keeps_full_code_and_respects_both_budgets():
    hits = [
        hit("first", "A short fact."),
        hit("code", "```cpp\n" + "x" * 800 + "\n```"),
        hit("late", "Necessary independent fact.", 0.7),
    ]
    selected, context, _ = budget_pack(
        hits, {"evidence": []}, {}, "independent fact", len, token_budget=180, char_budget=120
    )
    assert [h.chunk.id for h in selected] == ["first", "late"]
    assert context["used_characters"] <= 120 and context["used_tokens"] <= 180
    assert all(not e["truncated"] for e in context["evidence"])


def test_budget_neighbor_prior_never_crosses_source_or_parent():
    h = hit("anchor", "Anchor fact.")
    neighbors = [
        hit("good", "Required supporting condition."),
        hit("other", "Other source.", source="other.md"),
        hit("parent", "Other parent.", parent="other"),
    ]
    chunks = {h.chunk.id: h.chunk for h in neighbors}
    original = copy.deepcopy([h] + neighbors)
    selected, _, trace = budget_pack(
        [h], {"evidence": [{"chunk_id": c} for c in chunks]}, chunks, "condition", len
    )
    assert [h.chunk.id for h in selected] == ["anchor", "good"]
    assert list(trace["neighbor_priors"]) == ["good"]
    assert [h] + neighbors == original


def test_coverage_rewards_new_query_information_over_repetition():
    hits = [
        hit("a", "alpha fact"),
        hit("repeat", "alpha fact", 0.8),
        hit("new", "beta detail", 0.75),
    ]
    a = budget_pack(hits, {"evidence": []}, {}, "alpha beta", len)[2]
    b = budget_pack(hits, {"evidence": []}, {}, "alpha beta", len, coverage=True)[2]
    assert a["selection_trace"][1]["chunk_id"] == "repeat"
    assert b["selection_trace"][1]["chunk_id"] == "new"


def test_budget_skips_headings_and_rejects_duplicate_or_nan():
    h = hit("body", "Real fact.")
    selected, _, _ = budget_pack(
        [hit("heading", "# Heading", heading=True), h], {"evidence": []}, {}, "query", len
    )
    assert [x.chunk.id for x in selected] == ["body"]
    for hits in ([h, h], [hit("bad", "bad", float("nan"))]):
        with pytest.raises(ValueError):
            budget_pack(hits, {"evidence": []}, {}, "query", len)


@pytest.mark.parametrize(
    "value",
    [
        {"verdict": "supported", "issues": [{"claim": "actual"}]},
        {"verdict": "unsupported", "issues": []},
        {
            "verdict": "unsupported",
            "issues": [
                {"claim": "invented", "citation_ids": ["E1"], "type": "scope", "reason": "scope"}
            ],
        },
        {
            "verdict": "unsupported",
            "issues": [
                {"claim": "actual", "citation_ids": ["unknown"], "type": "scope", "reason": "scope"}
            ],
        },
        {"verdict": "pass", "issues": []},
    ],
)
def test_verifier_never_passes_invalid_or_unanchored_output(value):
    parsed, error = parse_verdict(json.dumps(value), "actual claim", {"E1"})
    assert parsed["verdict"] == "uncertain" and error


def test_verifier_accepts_anchored_issue_and_guard_preserves_original():
    value = {
        "verdict": "unsupported",
        "issues": [
            {"claim": "actual", "citation_ids": ["E1"], "type": "strength", "reason": "too strong"}
        ],
    }
    parsed, error = parse_verdict(json.dumps(value), "actual claim", {"E1"})
    assert error is None
    g = {"response": {"status": "answered", "answer": "actual claim", "citations": ["E1"]}}
    saved = copy.deepcopy(g)
    assert guarded_response(g, parsed)["status"] == "no_evidence"
    assert guarded_response(g, {"verdict": "supported"}) == g["response"]
    assert g == saved


def test_verifier_refusal_skips_model_and_only_sees_actually_cited_context():
    class Model:
        model = "fake"

        def generate(self, messages):
            self.messages = messages
            return '{"verdict":"supported","issues":[]}'

    model = Model()
    g = {"response": {"status": "no_evidence"}}
    assert not verify_answer({"query": "q"}, g, {}, model)["calls"]
    evidence = [
        {"citation_id": "E1", "content": "cited fact"},
        {"citation_id": "E2", "content": "uncited fact"},
    ]
    g = {"response": {"status": "answered", "answer": "cited fact", "citations": evidence[:1]}}
    result = verify_answer({"query": "q"}, g, {"evidence": evidence}, model)
    assert result["verdict"] == "supported"
    assert "uncited fact" not in model.messages[1]["content"]


def test_strength_prompt_is_opt_in_and_recorded_without_changing_default(tmp_path):
    from infra_rag.assistant import SYSTEM_PROMPT

    cid = "E" + "a" * 24

    class Model:
        model = "fake"

        def generate(self, messages):
            return json.dumps({"supported": True, "answer": f"A fact [{cid}]", "citations": [cid]})

    q = {"query": "q"}
    context = {"evidence": [{"citation_id": cid, "content": "A fact", "locator": "notes.md"}]}
    settings = Settings(data_dir=tmp_path)
    before = copy.deepcopy(context)
    baseline = generate_experimental(q, context, settings, Model())
    guarded = generate_experimental(q, context, settings, Model(), strength=True)
    assert baseline["calls"][0]["messages"][0]["content"] == SYSTEM_PROMPT
    assert guarded["calls"][0]["messages"][0]["content"] == SYSTEM_PROMPT + STRENGTH_PROMPT
    assert baseline["calls"][0]["messages"][1] == guarded["calls"][0]["messages"][1]
    assert context == before and baseline["error"] is None and guarded["error"] is None


def test_verifier_call_error_is_uncertain():
    class Model:
        model = "fake"

        def generate(self, messages):
            raise RuntimeError("offline")

    g = {"response": {"status": "answered", "answer": "a", "citations": []}}
    result = verify_answer({"query": "q"}, g, {"evidence": []}, Model())
    assert result["verdict"] == "uncertain" and len(result["calls"]) == 1
    assert result["error"]
