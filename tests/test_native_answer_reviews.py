import importlib.util
from pathlib import Path

import pytest


def fixture(monkeypatch, tmp_path):
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location(
        "native_answer_scores", scripts / "score_native_pagination_answers.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    jobs = [{"id": str(i), "enabled": a} for i in range(30) for a in (False, True)]
    mod.save(tmp_path / "schedule.json", jobs)
    mod.save(
        tmp_path / "questions.json", [{"id": str(i), "group_id": str(i // 2)} for i in range(30)]
    )
    reviews = []
    for j in jobs:
        path = tmp_path / "rows" / f"{j['id']}-{j['enabled']}.json"
        mod.save(path, {"case_sha256": "case", "http_status": 200})
        reviews.append(
            {
                **j,
                "case_sha256": "case",
                "trace_sha256": mod.digest(path),
                "method": "independent_human",
                "status": "approved",
                "reviewer": "fixture",
                "reviewed_at": "date",
                "reason": "fixture only",
                "strict_correct": j["enabled"],
                "all_required_claims": True,
                "citations_supported": True,
                "source_claim_inventory_complete": True,
            }
        )
    return mod, reviews


def test_scores_fixed_pairs_with_source_clusters(monkeypatch, tmp_path):
    mod, reviews = fixture(monkeypatch, tmp_path)
    result = mod.score(tmp_path, reviews)
    assert result["paired_statistics"]["clusters"] == 15
    assert result["strict_accuracy"]["True"]["value"] == 1


@pytest.mark.parametrize(
    "field,value",
    [("method", "ai_semantic_review"), ("trace_sha256", "stale"), ("strict_correct", None)],
)
def test_rejects_ai_stale_or_unknown_judgments(monkeypatch, tmp_path, field, value):
    mod, reviews = fixture(monkeypatch, tmp_path)
    reviews[0][field] = value
    with pytest.raises(ValueError):
        mod.score(tmp_path, reviews)
