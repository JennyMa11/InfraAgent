"""Budget-search behavior, evidence integrity and frozen acceptance gates."""

import copy
import importlib
from pathlib import Path

import pytest

from infra_rag.budget_search import BudgetSearch, full_block_oracle
from infra_rag.models import Chunk, Hit


def hit(cid, body, score):
    return Hit(
        Chunk(cid, "parent", "source.md", body, "infra", locator=f"source.md:{cid}"),
        0.1,
        rerank_score=score,
    )


def test_exchange_replaces_one_long_block_with_two_complementary_blocks():
    hits = [
        hit("anchor", "Anchor.", 1.0),
        hit("long", "Broad " + "b" * 880 + ".", 0.8),
        hit("condition", "Specific CUDA " + "x" * 490 + ".", 0.49),
        hit("formula", "Formula memory " + "y" * 490 + ".", 0.49),
    ]
    search = BudgetSearch(hits, "", len)
    greedy = search.pack(policy="greedy")
    swapped = search.pack(policy="exchange")
    assert [h.chunk.id for h in greedy[0]] == ["anchor", "long"]
    assert [h.chunk.id for h in swapped[0]] == ["anchor", "condition", "formula"]
    assert swapped[2]["objective"] > greedy[2]["objective"]
    assert swapped[1]["used_tokens"] <= 1200
    assert not any(e["truncated"] for e in swapped[1]["evidence"])
    assert len(swapped[2]["exchanges"]) == 1


def test_search_preserves_inputs_locator_code_and_protected_first():
    hits = [
        hit("anchor", "Short anchor.", 1.0),
        hit("code", "```python\n" + "x = 1\n" * 500 + "```", 0.9),
        hit("body", "Useful necessary condition.", 0.8),
    ]
    saved = copy.deepcopy(hits)
    chosen, context, trace = BudgetSearch(hits, "necessary condition", len).pack(policy="exchange")
    assert hits == saved
    assert chosen[0].chunk.id == "anchor"
    assert "code" not in {e["chunk_id"] for e in context["evidence"]}
    assert all(e["locator"] == f"source.md:{e['chunk_id']}" for e in context["evidence"])
    assert trace["seed_objective"] <= trace["objective"]


def test_search_fallback_keeps_safe_sentence_and_reports_budget_failure():
    body = "Complete sentence. " + "Remaining " * 200
    _, context, trace = BudgetSearch([hit("anchor", body, 1.0)], "q", len).pack(
        token_budget=100, char_budget=100
    )
    assert trace["fallback"] == "protected_block_does_not_fit"
    assert context["used_tokens"] <= 100 and context["used_characters"] <= 100
    assert context["evidence"][0]["content"] == "Complete sentence."


def test_empty_pool_and_search_cap_are_explicit_and_deterministic():
    assert BudgetSearch([], "q", len).pack()[1]["evidence"] == []
    hits = [hit(str(i), f"Fact number {i}.", 1 - i / 100) for i in range(25)]
    search = BudgetSearch(hits, "fact", len)
    result = search.pack(policy="exchange", proposal_cap=1)
    assert result == search.pack(policy="exchange", proposal_cap=1)
    assert result[2]["evaluated_proposals"] == 1
    assert result[2]["proposal_cap_reached"]


def test_objective_pruning_avoids_counting_noncompetitive_exchange_proposals():
    hits = [hit(str(i), f"Distinct fact {i}.", 1 - i / 100) for i in range(25)]
    search = BudgetSearch(hits, "fact", len)
    greedy = search.pack(policy="greedy")
    exchanged = search.pack(policy="exchange")
    assert exchanged[1] == greedy[1]
    assert exchanged[2]["objective"] == greedy[2]["objective"]
    assert exchanged[2]["evaluated_proposals"] > 0
    assert exchanged[2]["feasibility_checks"] == greedy[2]["feasibility_checks"]


@pytest.mark.parametrize("score", [float("nan"), float("inf"), -0.1])
def test_search_rejects_invalid_score_before_deciding(score):
    with pytest.raises(ValueError):
        BudgetSearch([hit("a", "Fact.", score)], "q", len)


def test_oracle_does_not_combine_incomplete_alternative_groups():
    chunks = {cid: hit(cid, f"Fact {cid}.", 0.5).chunk for cid in "abcd"}
    gold = {
        "evidence_alternatives": [
            {"requirements": [["a"], ["b"]]},
            {"requirements": [["c"], ["d"]]},
        ]
    }
    assert full_block_oracle(["a", "d"], gold, chunks, len)["feasible"] is False
    result = full_block_oracle(["c", "d"], gold, chunks, len)
    assert result["feasible"] is True
    assert result["best_full_block_witness"]["ids"] == ["c", "d"]


def test_oracle_distinguishes_budget_protection_and_incomplete_enumeration():
    chunks = {"anchor": hit("anchor", "a" * 1180, 1).chunk, "fact": hit("fact", "Fact.", 0.5).chunk}
    gold = {"evidence_alternatives": [{"requirements": [["fact"]]}]}
    assert full_block_oracle(["anchor", "fact"], gold, chunks, len)["feasible"] is True
    assert (
        full_block_oracle(["anchor", "fact"], gold, chunks, len, protect_first=True)["feasible"]
        is False
    )
    result = full_block_oracle(["fact"], gold, chunks, len, combination_cap=0)
    assert result["feasible"] is None and not result["exhaustive"]


def test_quality_gate_cannot_pass_with_gain_one_or_one_dataset_regression(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    driver = importlib.import_module("benchmark_budget_search_v8")
    summary = {}
    for ds, n in (("official", 45), ("repository", 41)):
        for arm, gain in (("B-O15", 0), ("T-O15", 1 if ds == "official" else 0)):
            summary[f"{ds}:{arm}"] = {
                "candidate_complete": {"numerator": 50},
                "delivered_complete": {"numerator": n + gain},
            }
    assert driver.select_winner(summary) is None
    summary["repository:T-O15"]["delivered_complete"]["numerator"] = 42
    assert driver.select_winner(summary) == "T-O15"
    summary["official:T-O15"]["delivered_complete"]["numerator"] = 44
    summary["repository:T-O15"]["delivered_complete"]["numerator"] = 45
    assert driver.select_winner(summary) is None
