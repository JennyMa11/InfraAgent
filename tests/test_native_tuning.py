import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def runner(monkeypatch):
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location(
        "native_tuning_test", scripts / "tune_native_retrieval.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rows(runner):
    return [
        {
            "id": f"diag-{i}" if i < 30 else f"expand-{i}",
            "config": c,
            "top5": {"complete": True},
            "first_page": {"complete": True},
            "candidate": {"complete": True},
            "pairs": 60 if c.startswith("k30") else 90,
        }
        for i in range(60)
        for c in runner.CONFIGS
    ]


def test_ties_prefer_lower_cost_and_baseline(runner):
    assert runner.choose(rows(runner))["winner"] == runner.BASE


def test_rejects_original_regression_despite_new_case_gain(runner):
    data = rows(runner)
    for r in data:
        if r["id"] == "diag-0" and r["config"] == "k45-raw":
            r["top5"]["complete"] = False
    result = runner.choose(data)
    assert result["winner"] != "k45-raw"
    assert result["stats"]["k45-raw"]["original30_top5_lost"] == ["diag-0"]
    with pytest.raises(ValueError):
        runner.choose(data[:-1])
