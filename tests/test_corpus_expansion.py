"""Expansion respects independent review bindings and keeps unrelated data isolated."""

import importlib.util
import json
from pathlib import Path

import pytest


@pytest.fixture
def runner(monkeypatch):
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    monkeypatch.syspath_prepend(str(scripts))
    spec = importlib.util.spec_from_file_location(
        "expansion_runner", scripts / "expand_corpus_preprocessing.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def review_copy(runner, tmp_path, monkeypatch):
    # Synthetic handoff in pytest temp storage; never writes approval to real data.
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    baseline = tmp_path / "pilot"
    reviewed = tmp_path / "reviewed"
    (baseline / "cleaned").mkdir(parents=True)
    reviewed.mkdir()

    def write(path, obj):
        path.write_text(json.dumps(obj))

    template, pilot, rows, evidence = [], [], [], []
    for i in range(12):
        cid = str(i)
        input_hash = f"input-{i}"
        clean = baseline / "cleaned" / (cid + ".md")
        clean.write_text("synthetic technical source")
        identity = {
            "document_id": cid,
            "collection": "official",
            "repository": "synthetic",
            "source_url": f"https://example.invalid/{i}",
        }
        template.append({**identity, "status": "pending"})
        pilot.append({**identity, "input_sha256": input_hash})
        rows.append(
            {
                **identity,
                "input_sha256": input_hash,
                "status": "approved",
                "method": "independent_human",
                "reviewer": "synthetic-test-reviewer",
                "reviewed_at": "2026-10-28T12:00:00+08:00",
                "reason": "synthetic fixture only",
                "checks": {key: "pass" for key in runner.CHECKS},
            }
        )
        evidence.append(
            {
                "document_id": cid,
                "hashes": {
                    "frozen_input_sha256": input_hash,
                    "cleaned_sha256": runner.digest(clean),
                },
            }
        )
    write(baseline / "human-review-template.json", template)
    write(baseline / "pilot.json", pilot)
    write(baseline / "protocol.json", {"implementation": {}})
    write(
        baseline / "artifacts-manifest.json",
        {
            p.relative_to(baseline).as_posix(): runner.digest(p)
            for p in baseline.rglob("*")
            if p.is_file()
        },
    )
    evidence_path = tmp_path / "evidence.json"
    write(evidence_path, {"documents": evidence})
    write(reviewed / "human-review.json", rows)
    write(
        reviewed / "review-manifest.json",
        {
            "baseline": "pilot",
            "reviewer": "synthetic-test-reviewer",
            "reviewed_at": rows[0]["reviewed_at"],
            "documents": 12,
            "status_counts": {"approved": 12},
            "template": {
                "path": "pilot/human-review-template.json",
                "sha256": runner.digest(baseline / "human-review-template.json"),
            },
            "evidence": {"json": {"path": "evidence.json", "sha256": runner.digest(evidence_path)}},
            "check_counts": {key: {"pass": 12} for key in runner.CHECKS},
        },
    )
    return baseline, reviewed


def test_separate_review_accepts_pending_frozen_template(runner, review_copy):
    baseline, reviewed = review_copy
    template = (baseline / "human-review-template.json").read_bytes()
    reviews, _ = runner.verify_review(baseline, reviewed)
    assert len(reviews) == 12
    assert all(r["status"] == "pending" for r in json.loads(template))
    assert (baseline / "human-review-template.json").read_bytes() == template


@pytest.mark.parametrize(
    "mutation", ["input_hash", "failed_check", "duplicate", "missing_check", "evidence_hash"]
)
def test_review_failures_block_expansion(runner, review_copy, mutation):
    baseline, reviewed = review_copy
    path = reviewed / "human-review.json"
    rows = json.loads(path.read_text())
    if mutation == "input_hash":
        rows[0]["input_sha256"] = "wrong"
    elif mutation == "failed_check":
        rows[0]["checks"]["format"] = "fail"
    elif mutation == "missing_check":
        del rows[0]["checks"]["scope"]
    elif mutation == "duplicate":
        rows[-1] = rows[0]
    else:
        manifest = reviewed / "review-manifest.json"
        obj = json.loads(manifest.read_text())
        obj["evidence"]["json"]["sha256"] = "wrong"
        manifest.write_text(json.dumps(obj))
    path.write_text(json.dumps(rows))
    with pytest.raises(ValueError):
        runner.verify_review(baseline, reviewed)


def test_selection_accepts_retained_new_repo_but_blocks_question_hash(runner):
    row = {
        "status": "retain",
        "collection": "full_repository",
        "input_sha256": "h",
        "original_path": "docs/guide.md",
        "document_id": "a",
    }
    excluded = {**row, "status": "exclude", "document_id": "b"}
    pending = {**row, "status": "review", "document_id": "c"}
    assert runner.select_candidates([row, excluded, pending], {"hashes": [], "paths": []}) == [row]
    with pytest.raises(ValueError, match="Non-corpus"):
        runner.select_candidates([row], {"hashes": ["h"], "paths": []})


def test_near_duplicate_audit_preserves_documents(runner, tmp_path):
    rows = []
    for i in range(2):
        path = tmp_path / f"{i}.md"
        path.write_text(
            "This is a technical document with detailed conditions and parameters. " * 20
        )
        rows.append({"document_id": str(i), "input_path": str(path)})
    report = runner.near_audit(rows)
    assert report["deleted_documents"] == 0
    assert report["matches"][0]["jaccard"] == 1
    assert all(Path(row["input_path"]).exists() for row in rows)
