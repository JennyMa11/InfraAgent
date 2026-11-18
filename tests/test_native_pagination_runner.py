import importlib.util
from pathlib import Path


def runner(monkeypatch):
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location(
        "native_runner", scripts / "benchmark_native_pagination.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_smoke_is_part_of_complete_alternating_schedule(monkeypatch):
    mod = runner(monkeypatch)
    plan = mod.schedule([{"id": f"diag-{i:03}"} for i in range(1, 31)])
    assert len(plan) == 60 and len({(p["id"], p["enabled"]) for p in plan}) == 60
    assert {p["id"] for p in plan[:8]} == set(mod.SMOKE)
    assert all(p["stage"] == "smoke" for p in plan[:8])
    assert [p["enabled"] for p in plan[:4]] == [False, True, True, False]


def test_missing_outputs_and_unknown_accuracy_remain_explicit(monkeypatch, tmp_path):
    mod = runner(monkeypatch)
    row = {
        "id": "q",
        "enabled": False,
        "case_sha256": "hash",
        "http_status": 500,
        "response": {"error": "offline"},
        "calls": [],
        "elapsed_ms": 100,
    }
    mod.save(tmp_path / "rows/q-False.json", row)
    mod.save(tmp_path / "summary.json", {"frozen": "smoke"})
    summary = mod.summarise(tmp_path)
    assert mod.load(tmp_path / "summary.json") == {"frozen": "smoke"}
    assert (tmp_path / "summary-1.json").exists()
    assert summary["recorded"] == 1 and summary["missing"] == 59
    assert summary["answer_accuracy"] is None
    assert summary["groups"]["False"]["execution_errors"] == 1
    assert summary["groups"]["True"]["p50_ms"] is None
