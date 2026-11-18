import pytest

from infra_rag.grid_metrics import dominates, feasible, latency, rank_metrics


def test_chunk_rank_is_not_deduplicated_but_source_recall_is():
    assert rank_metrics(["wrong", "wrong", "right", "right"], {"right", "other"}, 4) == {
        "recall": 0.5,
        "hit": 1,
        "mrr": 1 / 3,
    }
    assert rank_metrics(["wrong"], {"right"}, 5) == {"recall": 0, "hit": 0, "mrr": 0}
    with pytest.raises(ValueError):
        rank_metrics([], set(), 5)


def test_latency_nearest_rank_includes_all_samples():
    assert latency(list(range(1, 21))) == {"n": 20, "p50_ms": 10.5, "p95_ms": 19}
    assert latency([])["p95_ms"] is None


def test_fast_but_incomplete_config_is_not_a_safe_improvement():
    a = dict(
        recall5=1,
        hit5=1,
        mrr5=1,
        required_recall5=1,
        complete5=1,
        p95_ms=100,
        original_complete_losses=[],
    )
    b = {**a, "p95_ms": 50, "complete5": 0.5}
    assert not dominates(b, a) and not feasible(b, a)
    assert dominates({**a, "p95_ms": 50}, a)


@pytest.fixture
def runner(monkeypatch):
    import importlib.util
    from pathlib import Path

    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location("grid_test", scripts / "grid_retrieval.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_schedule_covers_balanced_paired_runs_and_rejects_missing(runner):
    schedule = runner.grid_schedule(["a", "b", "c"], ["base", "other"], 3)
    assert len(schedule) == 18
    assert schedule == runner.grid_schedule(["a", "b", "c"], ["base", "other"], 3)
    rows = [{**r, "status": "completed"} for r in schedule]
    runner.validate_rows(rows, schedule)
    with pytest.raises(ValueError):
        runner.validate_rows(rows[:-1], schedule)
    with pytest.raises(ValueError):
        runner.validate_rows([*rows, rows[0]], schedule)
    rows[0]["status"] = "failed"
    with pytest.raises(ValueError):
        runner.validate_rows(rows, schedule)


def test_summary_keeps_repetitions_and_original_case_losses(runner):
    rows = []
    for rep in range(2):
        for config in (runner.BASE, "fast"):
            for cid in ("diag-001", "expand-031"):
                complete = int(not (config == "fast" and cid == "diag-001"))
                rows.append(
                    {
                        "id": cid,
                        "rep": rep,
                        "config": config,
                        "metrics": {
                            "recall5": 1.0,
                            "hit5": 1,
                            "mrr5": 1.0,
                            "required_recall5": complete,
                            "complete5": complete,
                        },
                        "elapsed_ms": 10 + rep * 10,
                        "rerank_pairs": 30,
                    }
                )
    summary = runner.summarize(rows)
    assert summary["fast"]["outputs"] == 4
    assert summary["fast"]["proportions"]["complete5"] == {
        "numerator": 2,
        "denominator": 4,
        "value": 0.5,
        "measurable_coverage": 1.0,
    }
    assert summary["fast"]["original_complete_losses"] == ["diag-001"]
    assert summary["fast"]["p95_ms"] == 20
    assert not feasible(summary["fast"], summary[runner.BASE])
