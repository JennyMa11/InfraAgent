import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from infra_rag.benchmarking import digest

ROOT = Path(__file__).resolve().parents[1]


def test_twenty_offline_tasks_execute_real_tools_and_freeze_complete_schedule(
    tmp_path, monkeypatch
):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    benchmark = importlib.import_module("benchmark_agent_e2e")
    scorer = importlib.import_module("score_agent_traces")
    suite = tmp_path / "suite"
    shutil.copytree(ROOT / "evals/agent-e2e-v1/corpus", suite / "corpus")
    shutil.copyfile(ROOT / "evals/agent-e2e-v1/sources.json", suite / "sources.json")
    output = tmp_path / "run"
    result = benchmark.execute(
        output, suite=suite, data_dir=tmp_path / "index", recorder=lambda *args: None
    )
    assert len(result["rows"]) == 20
    assert all(r["task_success"] is None for r in result["rows"])
    assert result["groups"][0]["missing"] == []
    traces = scorer.read(output / "traces.jsonl")
    assert all(t["provenance"] == "offline_agent_execution" for t in traces)
    assert sum(t["measurement"]["model_requests"] for t in traces) == 40
    first = traces[15]
    errors = [s for s in first["steps"] if s["kind"] == "tool"]
    assert [s["status"] for s in errors] == ["error", "ok"]
    assert errors[1]["recovery_of"] == errors[0]["id"]
    assert all(
        s["status"] == "error" for t in traces[16:18] for s in t["steps"] if s["kind"] == "tool"
    )
    assert traces[12]["evidence"]["delivered"] == []
    assert traces[18]["measurement"]["actual_tool_calls"] == 0
    freeze = json.loads((output / "freeze.json").read_text())
    assert freeze["case_sha256"] == digest(output / "cases.jsonl")
    assert freeze["schedule_sha256"] == digest(output / "schedule.json")
    for t in traces:
        for step in t["steps"]:
            for artifact in step["artifacts"]:
                assert digest(artifact["path"]) == artifact["sha256"]
    assert all(r["status"] == "pending" for r in scorer.read(output / "reviews.jsonl"))


def test_scorer_cli_manifest_and_frozen_output_protection(tmp_path):
    source = ROOT / "evals/agent-e2e-v1/offline-20261003"
    output = tmp_path / "score.json"
    command = [
        sys.executable,
        str(ROOT / "scripts/score_agent_traces.py"),
        "--cases",
        str(source / "cases.jsonl"),
        "--traces",
        str(source / "traces.jsonl"),
        "--manifest",
        str(source / "schedule.json"),
        "--require-complete",
        "--output",
        str(output),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    original = output.read_bytes()
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode != 0 and output.read_bytes() == original
    command[command.index(str(output))] = str(tmp_path / "reviewed.json")
    command.extend(["--reviews", str(source / "reviews.jsonl"), "--require-reviewed"])
    assert subprocess.run(command, capture_output=True).returncode != 0
    assert not (tmp_path / "reviewed.json").exists()


def test_actual_agent_traces_match_schema():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((ROOT / "examples/trace-schema.json").read_text())
    path = ROOT / "evals/agent-e2e-v1/offline-20261003/traces.jsonl"
    for line in path.read_text().splitlines():
        jsonschema.validate(json.loads(line), schema)
