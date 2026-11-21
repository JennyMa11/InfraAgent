"""Contract tests for the frozen Agentic/RAGAS evaluation adapter."""

import ast
import importlib.util
import json
import random
import statistics
from collections import defaultdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "agentic_ragas_adapter", ROOT / "scripts/evaluate_agentic_ragas.py"
)
adapter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adapter)


def test_frozen_baseline_and_gold_are_exactly_paired():
    protocol = adapter.verify_baseline()
    cases = adapter.load_cases()
    assert protocol["generation_model"] == "glm-5.3-flash"
    assert len(cases) == 120
    assert sum(case["answerable"] for case in cases) == 108
    assert [case["case_id"] for case in cases] == [
        row["id"] for row in json.loads((adapter.FROZEN / "cases.json").read_text())
    ]
    assert all(
        case["relevant"] and case["evidence_alternatives"] for case in cases if case["answerable"]
    )
    assert all(not case["relevant"] for case in cases if not case["answerable"])


def test_relocated_index_preserves_chunks_vectors_and_verifies_sources(tmp_path):
    target = adapter.relocated_index(tmp_path / "index")
    original = adapter.load(adapter.SOURCE_INDEX / "index.json")
    moved = adapter.load(target / "index.json")
    assert [chunk["id"] for chunk in original["chunks"]] == [
        chunk["id"] for chunk in moved["chunks"]
    ]
    assert [chunk["content"] for chunk in original["chunks"]] == [
        chunk["content"] for chunk in moved["chunks"]
    ]
    assert original.get("vectors") == moved.get("vectors")
    assert original["fingerprint"] == moved["fingerprint"]
    assert set(original["sources"]) != set(moved["sources"])
    assert len(moved["sources"]) == 40
    for source, metadata in moved["sources"].items():
        assert Path(source).is_relative_to(ROOT)
        assert adapter.sha256(Path(source)) == metadata["sha256"]
    assert all(chunk["source"] in moved["sources"] for chunk in moved["chunks"])
    retrieval = adapter.RetrievalService(adapter.make_settings(target))
    assert retrieval.settings.fingerprint() == retrieval.index_fingerprint
    assert len(retrieval.chunks) == 2037


def test_paired_stats_match_frozen_cluster_bootstrap_reference():
    source = (ROOT / "evals/ragas-full-v1/run-20261111/report.py").read_text()
    tree = ast.parse(source)
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "paired_stats"
    )
    namespace = {"defaultdict": defaultdict, "random": random, "statistics": statistics}
    exec(
        compile(ast.Module(body=[function], type_ignores=[]), "frozen-paired-stats", "exec"),
        namespace,
    )
    cases = [
        {"case_id": "a", "group_id": "g1"},
        {"case_id": "b", "group_id": "g1"},
        {"case_id": "c", "group_id": "g2"},
    ]
    first, second = [0.1, 0.5, 0.9], [0.3, 0.2, 0.8]
    expected = namespace["paired_stats"](
        {c["case_id"]: v for c, v in zip(cases, first, strict=True)},
        {c["case_id"]: v for c, v in zip(cases, second, strict=True)},
        {c["case_id"]: c for c in cases},
    )
    assert adapter.paired(first, second, cases) == expected


def test_relocated_source_hash_is_not_bypassed(tmp_path, monkeypatch):
    monkeypatch.setattr(adapter, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="relocated_source_missing_or_changed"):
        adapter.relocated_index(tmp_path / "new-index")


def test_refusal_is_scored_and_execution_error_is_not_zero_imputed():
    baseline = adapter.load(adapter.FROZEN / "ragas/rows.json")
    assert any(row["status"] == "no_evidence" for row in baseline)
    assert all(
        row["ragas"]["faithfulness"] is not None
        for row in baseline
        if row["status"] == "no_evidence" and not row["error"]
    )


def test_resume_uses_new_log_without_overwriting_history(tmp_path):
    original = tmp_path / "score-shard-1.log"
    original.write_text("original failure")
    second = adapter.unused_path(original)
    second.write_text("new attempt")
    third = adapter.unused_path(original)
    assert original.read_text() == "original failure"
    assert second.name == "score-shard-1-attempt-2.log"
    assert third.name == "score-shard-1-attempt-3.log"


def test_official_completion_requires_all_120(tmp_path):
    with pytest.raises(FileNotFoundError):
        adapter.validated_collection(tmp_path)
