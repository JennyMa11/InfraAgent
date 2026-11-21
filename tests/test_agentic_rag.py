import json
from pathlib import Path

import pytest

from infra_rag.agent import AgentLimits, RequestBudget
from infra_rag.agentic_rag import AgenticRAGChain
from infra_rag.benchmarking import digest
from infra_rag.config import Settings
from infra_rag.service import RetrievalService


class ScriptedModel:
    model = "agentic-scripted-model"
    provider = "deterministic"
    offline = True

    def __init__(self, actions, *, cached_usage=False):
        self.actions = iter(actions)
        self.cached_usage = cached_usage
        self.states = []
        self.last_call = None
        self.calls = 0

    def generate(self, messages):
        self.calls += 1
        state = json.loads(messages[-1]["content"])
        self.states.append(state)
        action = next(self.actions)
        if callable(action):
            action = action(state)
        usage = {"input_tokens": 10, "output_tokens": 4}
        if self.cached_usage:
            usage.update(cache_read_input_tokens=7, cache_creation_input_tokens=3)
        self.last_call = {"usage": usage}
        return action if isinstance(action, str) else json.dumps(action)


def search(query):
    return {"action": "tool", "name": "search", "arguments": {"query": query}}


def read_parent(state):
    return {
        "action": "tool",
        "name": "read_parent",
        "arguments": {"parent_id": state["registered_parents"][0]},
    }


def answer(state):
    evidence = state["evidence"][0]
    return {
        "action": "final",
        "status": "answered",
        "answer": f"资料结论：{evidence['content']} [{evidence['id']}]",
        "claims": [
            {"id": "c1", "text": evidence["content"], "evidence_ids": [evidence["id"]]}
        ],
    }


def abstain(status="refused"):
    return {"action": "final", "status": status, "answer": "资料不足，不能回答。", "claims": []}


@pytest.fixture
def retrieval(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "cache.md").write_text(
        "# Alpha Cache\n\nAlphaCache 使用独立词 AlphaUnique 管理 KV Cache。\n\n"
        "AlphaCache 的页面可以非连续存放。"
    )
    (corpus / "scheduler.md").write_text(
        "# Beta Scheduler\n\nBetaScheduler 使用独立词 BetaUnique 管理请求队列。\n\n"
        "BetaScheduler 按优先级调度请求。"
    )
    service = RetrievalService(
        Settings(data_dir=tmp_path / "index", chunk_size=100, context_tokens=1200)
    )
    service.ingest(corpus, "infra")
    return service


def run(retrieval, model, output=None, **kwargs):
    return AgenticRAGChain(retrieval, model, **kwargs).retrieve(
        "AlphaCache 与 BetaScheduler 分别管理什么？", output_dir=output
    )


def test_model_directed_multi_step_and_actual_packed_delivery(tmp_path, retrieval):
    model = ScriptedModel(
        [search("AlphaUnique"), search("BetaUnique"), read_parent],
        cached_usage=True,
    )
    result = run(retrieval, model, tmp_path / "run")

    assert set(result) == {
        "chain",
        "query",
        "domain",
        "index_fingerprint",
        "evidence",
        "candidates",
        "ranked",
        "trace",
        "latency_ms",
        "final",
    }
    assert result["chain"] == result["trace"]["config_id"] == "agentic_rag"
    tools = [step for step in result["trace"]["steps"] if step["kind"] == "tool"]
    assert [step["name"] for step in tools] == ["search", "search", "read_parent"]
    assert [step["arguments"] for step in tools[:2]] == [
        {"query": "AlphaUnique"},
        {"query": "BetaUnique"},
    ]
    assert model.states[1]["registered_parents"]
    assert model.states[2]["remaining_tool_calls"] == 2
    # The last model turn is final-only: read_parent is blocked before execution.
    assert tools[-1]["status"] == "blocked"
    # The model nevertheless decides both subqueries and the registered parent ID itself.
    assert tools[-1]["arguments"]["parent_id"] in model.states[2]["registered_parents"]
    assert result["final"]["status"] == "escalated"
    assert result["final"]["citations"] == []
    assert result["trace"]["provenance"] == "offline_agent_execution"
    assert result["trace"]["resources"] == {
        "input_tokens": 60,
        "output_tokens": 12,
        "model_cost_usd": None,
        "tool_cost_usd": 0,
    }
    assert result["trace"]["measurement"] == {
        "model_requests": 3,
        "actual_tool_calls": 2,
        "usage_observed_requests": 3,
    }
    json.dumps(result, ensure_ascii=False, allow_nan=False)

    delivered = result["evidence"]["delivered"]
    assert delivered == result["trace"]["evidence"]["delivered"]
    for step in tools:
        for artifact in step["artifacts"]:
            assert digest(artifact["path"]) == artifact["sha256"]
    trace_path = tmp_path / "run" / "trace.json"
    assert json.loads(trace_path.read_text())["run_id"] == "agentic-interactive"


def test_model_selected_parent_read_delivers_full_parent(tmp_path, retrieval):
    result = run(
        retrieval,
        ScriptedModel([search("AlphaUnique"), read_parent, answer]),
        tmp_path / "run",
    )
    tools = [step for step in result["trace"]["steps"] if step["kind"] == "tool"]
    assert [step["name"] for step in tools] == ["search", "read_parent"]
    assert tools[1]["status"] == "ok"
    first_observation = json.loads(tools[0]["observation"])
    assert tools[1]["arguments"]["parent_id"] in first_observation["parents"]
    assert result["final"]["status"] == "answered"
    parent_observation = json.loads(tools[1]["observation"])
    assert result["evidence"]["delivered"] == parent_observation["evidence"]
    assert result["evidence"]["delivered"] == first_observation["evidence"]


def test_cumulative_candidates_latest_ranking_and_delivery_are_distinct(tmp_path, retrieval):
    model = ScriptedModel([search("AlphaUnique"), search("BetaUnique"), answer])
    result = run(retrieval, model, tmp_path / "run")
    trace = result["trace"]
    assert trace["events"] == [], trace["steps"]
    assert len(trace["retrieval_rounds"]) == 2
    assert result["final"]["status"] == "answered"
    assert result["trace"]["evidence"]["candidate_ids"] == trace["retrieval_rounds"][-1][
        "candidate_ids"
    ]
    assert {item["chunk_id"] for item in result["ranked"]} == set(
        result["evidence"]["ranked_ids"]
    )
    assert all(item["retrieval_round"] == 2 for item in result["ranked"])
    assert {item["chunk_id"] for item in result["candidates"]} == set(
        result["evidence"]["cumulative_candidate_ids"]
    )
    assert set(result["evidence"]["ranked_ids"]).issubset(
        result["evidence"]["cumulative_candidate_ids"]
    )
    round_text = [
        evidence["content"]
        for round_data in trace["retrieval_rounds"]
        for evidence in round_data["delivered"]
    ]
    assert result["evidence"]["delivered"]
    assert all(item["content"] for item in result["evidence"]["delivered"])
    assert sum(len(text) for text in round_text) >= sum(
        len(item["content"]) for item in result["evidence"]["delivered"]
    )
    for item in result["candidates"]:
        assert item["chunk_id"] and isinstance(item["scores"], dict)
        assert isinstance(item["reasons"], list)
    assert all(
        {"chunk_id", "rank", "before_rerank_rank", "rerank_score", "scores", "reasons"}
        <= set(item)
        for item in result["ranked"]
    )
    cited = {edge["evidence_id"] for edge in result["final"]["citations"]}
    assert cited <= {item["id"] for item in result["evidence"]["delivered"]}
    final_model_state = json.loads(
        [step for step in result["trace"]["steps"] if step["kind"] == "model"][-1]["arguments"][
            "messages"
        ][-1]["content"]
    )
    assert cited <= {item["id"] for item in final_model_state["evidence"]}


def test_final_citations_must_reference_exactly_delivered_text(tmp_path, retrieval):
    def wrong(state):
        action = answer(state)
        action["claims"][0]["evidence_ids"] = ["E000000000000000000000000"]
        return action

    result = run(retrieval, ScriptedModel([search("AlphaUnique"), wrong, answer]))
    assert "invalid_claim_or_citation" in result["trace"]["events"]
    assert result["final"]["status"] == "answered"
    assert all(item["text"] for item in result["trace"]["claims"])


@pytest.mark.parametrize(
    "action",
    [
        {"action": "tool", "name": "shell", "arguments": {"command": "pwd"}},
        {"action": "tool", "name": "read_parent", "arguments": {"parent_id": "../../.env"}},
        {
            "action": "tool",
            "name": "search",
            "arguments": {"query": "AlphaUnique", "path": "/etc/passwd"},
        },
    ],
)
def test_unsafe_tools_and_arbitrary_paths_blocked_before_execution(retrieval, action):
    result = run(retrieval, ScriptedModel([action, abstain()]))
    blocked = [step for step in result["trace"]["steps"] if step["status"] == "blocked"]
    assert len(blocked) == 1
    assert result["trace"]["measurement"]["actual_tool_calls"] == 0
    assert result["final"]["status"] == "refused"


def test_retry_accounting_and_persistent_tool_failure(tmp_path, retrieval):
    recovered = run(
        retrieval,
        ScriptedModel([search("AlphaUnique"), answer]),
        tmp_path / "recovered",
        fault="first_error",
    )
    steps = [step for step in recovered["trace"]["steps"] if step["kind"] == "tool"]
    assert [step["status"] for step in steps] == ["error", "ok"]
    assert steps[1]["recovery_of"] == steps[0]["id"]
    assert recovered["trace"]["measurement"]["actual_tool_calls"] == 2

    failed = run(
        retrieval,
        ScriptedModel([search("AlphaUnique"), abstain("escalated")]),
        tmp_path / "failed",
        fault="always_error",
    )
    steps = [step for step in failed["trace"]["steps"] if step["kind"] == "tool"]
    assert [step["status"] for step in steps] == ["error", "error"]
    assert steps[1]["retry_of"] == steps[0]["id"]
    assert failed["evidence"]["delivered"] == []
    assert failed["final"]["status"] == "escalated"


def test_model_failures_and_shared_request_budget_are_graceful(tmp_path, retrieval):
    failed = run(retrieval, ScriptedModel(["not-json", "not-json", "not-json"]))
    assert failed["final"]["status"] == "escalated"
    assert failed["trace"]["measurement"]["model_requests"] == 3
    assert failed["trace"]["resources"]["input_tokens"] == 30

    budget = RequestBudget(1)
    result = run(retrieval, ScriptedModel([search("AlphaUnique"), answer]), budget=budget)
    assert budget.used == 1
    assert result["trace"]["measurement"]["model_requests"] == 1
    assert result["final"]["status"] == "escalated"
    assert "global_request_budget_exhausted" in result["trace"]["events"]


def test_changed_source_fails_closed(retrieval):
    Path(next(iter(retrieval.source_manifest))).write_text("source changed after indexing")
    result = run(retrieval, ScriptedModel([search("AlphaUnique"), abstain("escalated")]))
    assert result["evidence"]["delivered"] == []
    assert result["final"]["status"] == "escalated"
    tools = [step for step in result["trace"]["steps"] if step["kind"] == "tool"]
    assert all(step["status"] == "error" for step in tools)


def test_output_no_overwrite_and_implicit_workspace_is_temporary(tmp_path, retrieval):
    output = tmp_path / "frozen-run"
    run(retrieval, ScriptedModel([abstain()]), output)
    assert (output / "trace.json").is_file()
    model = ScriptedModel([abstain()])
    with pytest.raises(FileExistsError):
        run(retrieval, model, output)
    assert model.calls == 0

    implicit = run(retrieval, ScriptedModel([abstain()]))
    artifact = Path(implicit["trace"]["steps"][0]["artifacts"][0]["path"])
    assert not artifact.exists()
    assert not artifact.parent.exists()


def test_credentials_redacted_from_result_and_artifacts(tmp_path, retrieval):
    model = ScriptedModel([abstain()])
    model._token = "CONTROLLED_TEST_CREDENTIAL"
    model.actions = iter([abstain() | {"answer": model._token}])
    result = run(retrieval, model, tmp_path / "run")
    serialized = json.dumps(result)
    assert model._token not in serialized
    assert model._token not in (tmp_path / "run" / "trace.json").read_text()
    assert model._token not in (tmp_path / "run" / "s1.json").read_text()


def test_budget_limits_are_not_silently_increased(retrieval):
    with pytest.raises(ValueError):
        AgentLimits(model_calls=4)
    model = ScriptedModel([search("AlphaUnique"), search("BetaUnique"), search("third")])
    result = run(retrieval, model, limits=AgentLimits(model_calls=3, tool_calls=4))
    assert result["trace"]["measurement"]["model_requests"] == 3
    assert result["trace"]["measurement"]["actual_tool_calls"] == 2
    assert result["trace"]["steps"][-1]["status"] == "blocked"
    assert result["final"]["status"] == "escalated"
