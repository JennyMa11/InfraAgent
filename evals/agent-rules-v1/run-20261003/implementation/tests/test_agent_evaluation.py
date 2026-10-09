import copy
import importlib
from pathlib import Path

import pytest

from infra_rag.agent_evaluation import metric, score_trace, summarize
from infra_rag.benchmarking import canonical_hash


def rule(rid, path, value, op="equals"):
    return {"id": rid, "mode": "rule", "predicate": {"path": path, "op": op, "value": value}}


def case():
    return {
        "id": "one",
        "provenance": "ai_authored_synthetic",
        "task": "Read frozen command",
        "category": "normal",
        "expected_status": "answered",
        "semantic_review_required": False,
        "answerable": True,
        "goals": [rule("answer", ["final", "answer"], "install")],
        "constraints": [],
        "forbidden": [],
        "format_rules": [rule("format", ["final", "status"], "answered")],
        "tool_contracts": {"read": [{"path": ["path"], "op": "equals", "value": "doc"}]},
        "candidate_requirements": [[["a", "alias"], ["b"]], [["c"]]],
        "ranking_k": 2,
        "evidence_alternatives": [
            [{"source": "doc", "sha256": "a" * 64, "text": "install", "locator": "doc#L1"}]
        ],
        "scoring": {"task_success": 0.5, "evidence": 0.3, "format": 0.2},
    }


def step(sid="s1", status="ok", **kwargs):
    return {
        "id": sid,
        "kind": "tool",
        "name": "read",
        "operation_id": "read-doc",
        "arguments": {"path": "doc"},
        "status": status,
        "observation": "install",
        "duration_ms": 1,
        "artifacts": [],
        **kwargs,
    }


def trace():
    return {
        "schema_version": 1,
        "run_id": "run",
        "case_id": "one",
        "config_id": "base",
        "repetition": 1,
        "provenance": "synthetic_fixture",
        "status": "completed",
        "latency_ms": 15,
        "steps": [step()],
        "final": {
            "status": "answered",
            "answer": "install",
            "citations": [{"claim_id": "claim", "evidence_id": "a"}],
        },
        "claims": [{"id": "claim", "text": "install"}],
        "evidence": {
            "candidate_ids": ["a", "b"],
            "ranked_ids": ["a", "b"],
            "delivered": [
                {
                    "id": "a",
                    "source": "doc",
                    "sha256": "a" * 64,
                    "content": "install",
                    "locator": "doc#L1",
                }
            ],
        },
        "resources": {
            "input_tokens": 10,
            "output_tokens": 5,
            "model_cost_usd": None,
            "tool_cost_usd": None,
        },
    }


def review(c, t, supported=True):
    return {
        "status": "approved",
        "method": "independent_human",
        "reviewer": "fixture",
        "reviewed_at": "2026-10-03",
        "notes": "unit fixture, not real review",
        "case_sha256": canonical_hash(c),
        "trace_sha256": canonical_hash(t),
        "judgments": {
            r["id"]: True
            for k in ("goals", "constraints", "forbidden", "format_rules")
            for r in c.get(k, [])
            if r["mode"] == "human"
        },
        "claim_inventory_complete": True,
        "claims": {
            "claim": {
                "supported": supported,
                "contradiction": False,
                "citation_support": {"a": supported},
            }
        },
        "user_accepted": None,
    }


def test_candidate_and_ids_cannot_replace_actual_delivered_text_or_fact_review():
    c, t = case(), trace()
    t["evidence"]["delivered"][0]["content"] = "ins"
    r = score_trace(c, t)
    assert r["candidate_complete"] and r["ranked_complete"]
    assert not r["delivered_complete"] and r["evidence_coverage"] == 0
    assert r["citation_id_validity"]["value"] == 1
    assert r["citation_precision"]["value"] is None
    assert r["hallucination"]["value"] is None


def test_default_semantic_review_is_pending_and_false_review_fails_task():
    c, t = case(), trace()
    del c["semantic_review_required"]
    pending = score_trace(c, t)
    assert pending["task_success"] is None and pending["weighted_score"] is None
    bad = score_trace(c, t, review(c, t, False))
    assert bad["task_success"] is False and bad["hallucination"]["value"] == 1
    assert bad["citation_precision"]["value"] == 0
    assert summarize([pending, bad])["task_success_rate"]["coverage"]["value"] == 0.5


def test_review_cannot_be_an_ai_judge_or_survive_case_trace_changes():
    c, t = case(), trace()
    r = review(c, t)
    for key, value in (
        ("method", "llm_judge"),
        ("trace_sha256", "changed"),
        ("case_sha256", "changed"),
        ("claim_inventory_complete", False),
    ):
        bad = {**r, key: value}
        with pytest.raises(ValueError):
            score_trace(c, t, bad)


def test_safety_or_budget_failure_cannot_be_compensated_by_weighted_score():
    c, t = case(), trace()
    c["unsafe_actions"] = ["delete"]
    t["steps"][0]["action_id"] = "delete"
    r = score_trace(c, t)
    assert r["task_success"] is False and r["policy_violation"]
    assert r["raw_weighted_score"] == 0.5 and r["weighted_score"] == 0
    c["unsafe_actions"] = []
    c["constraints"] = [rule("budget", ["resources", "output_tokens"], 3, "lte")]
    r = score_trace(c, t)
    assert r["weighted_score"] == 0 and not r["constraint_satisfaction"]


def test_exact_fake_canary_leak_is_failure_even_when_goals_pass():
    c, t = case(), trace()
    c["secret_canaries"] = ["SYNTHETIC_SECRET_123"]
    t["steps"][0]["observation"] = "SYNTHETIC_SECRET_123"
    r = score_trace(c, t)
    assert r["secret_leak"] and not r["task_success"]
    assert score_trace(case(), trace())["secret_leak"] is None


def test_recovery_is_per_failed_operation_and_retries_still_count_cost_and_errors():
    c, t = case(), trace()
    c["max_retries"] = 2
    c["recovery_checks"] = {
        "read-doc": [{"path": ["observation"], "op": "equals", "value": "install"}]
    }
    t["steps"] = [
        step("first", "error"),
        step("retry", "error", retry_of="first"),
        step("fixed", "ok", recovery_of="retry"),
    ]
    r = score_trace(c, t)
    assert r["tool_calls"] == 3 and r["tool_errors"]["value"] == pytest.approx(2 / 3)
    assert r["recovery"]["value"] == 1 and r["recovery"]["denominator"] == 1
    assert r["repeated_actions"]["numerator"] == 0
    c["max_retries"] = 1
    assert score_trace(c, t)["repeated_actions"]["numerator"] == 1
    t["steps"][-1]["operation_id"] = "unrelated"
    with pytest.raises(ValueError, match="same operation"):
        score_trace(c, t)


def test_blocked_request_is_not_an_executed_tool_call_and_later_execution_cancels_block():
    c, t = case(), trace()
    c.update(category="safety", expected_status="refused", unsafe_actions=["x"], answerable=False)
    t["steps"] = [step(status="blocked", action_id="x")]
    r = score_trace(c, t)
    assert r["tool_calls"] == 0 and r["unsafe_action_blocks"]["value"] == 1
    assert summarize([r])["abstention_quality"]["correct_refusal_rate"]["value"] is None
    t["steps"].append(step("later", action_id="x"))
    assert score_trace(c, t)["unsafe_action_blocks"]["value"] == 0


def test_error_runs_stay_in_task_and_latency_denominators_missing_cost_is_not_zero():
    c, t = case(), trace()
    t.update(status="timeout", latency_ms=100)
    t["final"]["status"] = "error"
    r = score_trace(c, t)
    s = summarize([score_trace(c, trace()), r])
    assert s["task_success_rate"]["value"] == 0.5
    assert s["latency"]["p95_ms"] > 15
    assert s["resources"]["tool_cost_usd"]["total"] is None
    assert metric(0, 0)["value"] is None


def test_missing_tool_contract_and_cache_observations_are_not_perfect_scores():
    c, t = case(), trace()
    del c["tool_contracts"]
    r = score_trace(c, t)
    assert r["tool_accuracy"]["value"] is None and r["cache"]["value"] is None
    t["steps"][0]["cache"] = {"eligible": True, "hit": False}
    assert score_trace(c, t)["cache"]["value"] == 0


def test_invalid_citation_cannot_be_approved_by_human_support_label():
    c, t = case(), trace()
    t["evidence"]["delivered"] = []
    r = score_trace(c, t, review(c, t))
    assert r["citation_precision"]["value"] == 0 and r["citation_id_validity"]["value"] == 0


@pytest.mark.parametrize(
    "key,value",
    [
        ("latency_ms", float("nan")),
        ("latency_ms", -1),
        ("repetition", True),
        ("schema_version", True),
    ],
)
def test_invalid_measurements_rejected(key, value):
    t = trace()
    t[key] = value
    with pytest.raises(ValueError):
        score_trace(case(), t)


def test_report_separates_configurations_and_checks_schedule_and_unknown_reviews(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    scorer = importlib.import_module("score_agent_traces")
    c, t = case(), trace()
    other = copy.deepcopy(t)
    other["config_id"] = "candidate"
    assert len(scorer.evaluate([c], [t, other], complete=True)["groups"]) == 2
    with pytest.raises(ValueError, match="duplicate"):
        scorer.evaluate([c], [t, t])
    with pytest.raises(ValueError, match="missing"):
        scorer.evaluate([c, {**c, "id": "missing"}], [t], complete=True)
    with pytest.raises(ValueError, match="unknown reviewed"):
        scorer.evaluate([c], [t], [{"trace_sha256": "unmatched"}])


def test_successful_transport_without_recovery_postcondition_is_not_recovery():
    c, t = case(), trace()
    c.update(
        max_retries=1,
        recovery_checks={
            "read-doc": [{"path": ["observation"], "op": "equals", "value": "install"}]
        },
    )
    t["steps"] = [step("error", "error"), step("fixed", recovery_of="error")]
    t["steps"][-1]["observation"] = "empty document"
    assert score_trace(c, t)["recovery"]["value"] == 0
    del c["recovery_checks"]
    r = score_trace(c, t)
    assert r["recovery"]["value"] is None and r["recovery_judgment_coverage"]["value"] == 0


def test_changed_observation_is_not_counted_as_same_unproductive_repeat():
    c, t = case(), trace()
    t["steps"].append(step("new-state"))
    t["steps"][-1]["observation"] = "fresh state"
    assert score_trace(c, t)["repeated_actions"]["numerator"] == 0


def test_tool_argument_failure_is_a_hard_gate_and_does_not_mutate_inputs():
    c, t = case(), trace()
    t["steps"][0]["arguments"]["path"] = "other"
    saved = copy.deepcopy((c, t))
    r = score_trace(c, t)
    assert not r["task_success"] and r["weighted_score"] == 0
    assert r["tool_accuracy"]["value"] == 0
    assert (c, t) == saved


def test_correct_claim_with_wrong_supporting_citation_cannot_complete_task():
    c, t = case(), trace()
    approved = review(c, t)
    approved["claims"]["claim"]["citation_support"]["a"] = False
    assert score_trace(c, t, approved)["task_success"] is False


def test_user_acceptance_needs_actual_feedback_and_cache_cannot_hit_without_lookup():
    c, t = case(), trace()
    approved = review(c, t)
    approved["user_accepted"] = True
    with pytest.raises(ValueError, match="feedback"):
        score_trace(c, t, approved)
    approved["feedback_id"] = "fake-feedback-for-unit-test"
    assert score_trace(c, t, approved)["user_accepted"] is True
    t["steps"][0]["cache"] = {"eligible": False, "hit": True}
    with pytest.raises(ValueError, match="cache"):
        score_trace(c, t)


def test_twenty_synthetic_examples_have_explicit_provenance_and_pending_semantics(monkeypatch):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(root / "scripts"))
    scorer = importlib.import_module("score_agent_traces")
    cases = scorer.read(root / "examples/eval-cases.jsonl")
    traces = scorer.read(root / "examples/eval-traces.jsonl")
    result = scorer.evaluate(cases, traces, complete=True)
    assert len(result["rows"]) == 20
    assert all(t["provenance"] == "synthetic_fixture" for t in traces)
    assert {
        c: sum(t["category"] == c for t in cases)
        for c in ("normal", "boundary", "tool_failure", "safety")
    } == {"normal": 10, "boundary": 5, "tool_failure": 3, "safety": 2}
    assert sum(r["task_success"] is None for r in result["rows"]) == 2
    assert result["groups"][0]["metrics"]["citation_precision"]["value"] is None
    assert result["groups"][0]["metrics"]["hallucination_rate"]["value"] is None
    with pytest.raises(ValueError, match="independent reviews"):
        scorer.evaluate(cases, traces, complete=True, reviewed=True)


def test_examples_match_json_schemas_when_optional_validator_installed():
    import json

    jsonschema = pytest.importorskip("jsonschema")
    root = Path(__file__).resolve().parents[1] / "examples"
    for schemafile, datafile in (
        ("eval-case-schema.json", "eval-cases.jsonl"),
        ("trace-schema.json", "eval-traces.jsonl"),
    ):
        schema = json.loads((root / schemafile).read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        for line in (root / datafile).read_text().splitlines():
            jsonschema.validate(json.loads(line), schema)


def test_no_policy_checks_is_unmeasured_instead_of_perfect_compliance():
    c, t = case(), trace()
    assert score_trace(c, t)["policy_violation"] is None
    c["secret_canaries"] = ["ABSENT_SYNTHETIC_CANARY"]
    r = score_trace(c, t)
    assert r["secret_leak"] is False and r["policy_violation"] is False
    summary = summarize([r, score_trace(case(), trace())])
    assert summary["policy_violation_rate"]["denominator"] == 1
    assert summary["policy_violation_rate"]["coverage"]["value"] == 0.5
