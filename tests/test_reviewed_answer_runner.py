import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def runner(monkeypatch):
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location(
        "reviewed_answers", scripts / "benchmark_reviewed_answers.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_actual_page_content_and_citation_ids_preserved(runner):
    e = {"citation_id": "E123", "content": "Only if enabled", "source_url": "source"}
    context = runner.page_context({"evidence": [e]})
    assert context["evidence"][0]["content"] == e["content"]
    assert context["evidence"][0]["citation_id"] == "E123"
    assert "locator" not in e


def test_interrupted_call_is_not_reissued(runner, tmp_path):
    job = {"id": "q", "arm": "a", "page": 0}
    runner.save(tmp_path / "rows/q-a-p0.started.json", {"status": "started"})
    with pytest.raises(ValueError, match="Interrupted"):
        runner.execute(job, tmp_path)


def test_resume_rejects_tampered_answer_trace(runner, tmp_path):
    path = tmp_path / "rows/q-a-p0.json"
    runner.save(path, {"original": True})
    runner.save(path.with_suffix(".sha256.json"), {"sha256": "incorrect"})
    with pytest.raises(ValueError, match="Checkpoint"):
        runner.execute({"id": "q", "arm": "a", "page": 0}, tmp_path)
