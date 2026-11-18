import importlib.util
import io
from pathlib import Path
from urllib.error import HTTPError

import pytest


@pytest.fixture
def runner(monkeypatch):
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location(
        "runtime_runner", scripts / "benchmark_runtime_e2e.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_full_http_workload_denominator_and_distinct_cases(runner):
    cases = runner.cases()
    assert len(cases) == len({c["id"] for c in cases}) == 22
    assert sum(len(c["turns"]) for c in cases) == 23
    assert (23 + 1 + 4) * 4 == 112
    assert cases[0]["turns"][0]["message"] == "Page Attention是什么"


def test_failed_parent_turn_is_not_silently_reissued_as_new_conversation(runner, monkeypatch):
    calls = []

    def failed(base, payload):
        calls.append(payload)
        return {"http_status": 503, "response": {"detail": "unavailable"}, "elapsed_ms": 100}

    monkeypatch.setattr(runner, "request", failed)
    case = next(c for c in runner.cases() if c["id"] == "follow_up")
    rows = runner.run_case("http://local", case, "test", "serial")
    assert len(calls) == 1
    assert rows[0]["http_status"] == 503 and rows[0]["attempted"]
    assert rows[1]["attempted"] is False and rows[1]["elapsed_ms"] is None


def test_non_json_http_error_preserves_actual_status_and_elapsed(runner, monkeypatch):
    def failed(*args, **kwargs):
        raise HTTPError("http://local", 500, "failure", {}, io.BytesIO(b"server error"))

    monkeypatch.setattr(runner.urllib.request, "urlopen", failed)
    result = runner.request("http://local", {"message": "test"})
    assert result["http_status"] == 500
    assert result["response"]["invalid_json"]
    assert result["elapsed_ms"] >= 0
