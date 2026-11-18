import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def runner(monkeypatch):
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location(
        "targeted_schedule", scripts / "benchmark_targeted_repairs.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_full_schedule_has_90_unique_pairs_and_alternating_order(runner):
    cases = {f"diag-{i:03}": {} for i in range(1, 31)}
    plan = runner.experiment_schedule(cases, "A", "full")
    assert len(plan) == 90 and len({(j["id"], j["arm"]) for j in plan}) == 90
    assert [j["arm"] for j in plan[:6]] == ["off", "old", "new", "new", "old", "off"]
    assert {j["id"] for j in plan} == set(cases)


def test_original_scope_preserved_and_full_not_oracle_expansion(runner):
    cases = {f"diag-{i:03}": {} for i in range(1, 31)}
    assert len(runner.experiment_schedule(cases, "A")) == 24
    assert len(runner.experiment_schedule(cases, "B")) == 4
    with pytest.raises(ValueError):
        runner.experiment_schedule(cases, "B", "full")
