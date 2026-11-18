"""Structural metadata controls: no model downloads needed."""

import copy
import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from infra_rag.encoding import DemoEncoder
from infra_rag.metadata_experiments import (
    MetadataNavigator,
    candidate_pool,
    document_views,
    loss_stage,
)
from infra_rag.models import Chunk


def corpus(tmp_path):
    path = tmp_path / "guide.md"
    path.write_text("RAW ORIGINAL")
    return [
        Chunk(
            "a",
            "p",
            str(path),
            "BODY_CANARY alpha",
            "infra",
            heading="Cache",
            metadata={"release": "v1", "summary": "FORBIDDEN"},
        ),
        Chunk(
            "b",
            "p",
            str(path),
            "BODY_TWO beta",
            "infra",
            heading="Cache",
            metadata={"release": "v2"},
        ),
    ]


def test_metadata_versions_and_no_body_or_unapproved_fields(tmp_path):
    chunks = corpus(tmp_path)
    before = copy.deepcopy(chunks)
    views, owners, records = document_views(chunks, tmp_path)
    assert chunks == before
    assert owners["a"] != owners["b"]
    assert len(views) == 2
    assert all("BODY" not in v.content and "FORBIDDEN" not in v.content for v in views)
    assert all(str(tmp_path) not in v.content for v in views)
    assert all(r["source_sha256"] for r in records.values())
    Path(chunks[0].source).write_text("changed")
    assert document_views(chunks, tmp_path)[1] != owners


def test_outside_corpus_root_fails(tmp_path):
    chunks = corpus(tmp_path)
    with pytest.raises(ValueError):
        document_views(chunks, tmp_path / "other")


def test_supplement_keeps_base_deduplicates_and_caps():
    base = [{"chunk_id": str(i), "score": i / 100} for i in range(60)]
    ranked = [(str(i), 1.0) for i in range(100)]
    pool = candidate_pool("M", base, ranked)
    assert len(pool) == 90
    assert {cid for cid, _ in pool} >= {r["chunk_id"] for r in base}
    assert candidate_pool("M", base) == [(r["chunk_id"], r["score"]) for r in base]
    assert candidate_pool("H", base) == []
    with pytest.raises(ValueError):
        candidate_pool("H", [], ranked)


def test_navigation_filters_before_topk_and_does_not_recompute_idf(tmp_path):
    chunks = corpus(tmp_path)
    encoder = DemoEncoder()
    nav = MetadataNavigator(chunks, encoder.encode([c.content for c in chunks]), encoder, tmp_path)
    old = dict(nav.lexical.idf)
    pool, trace = nav.retrieve("Cache v1 alpha")
    assert all(nav.owners[cid] in trace["documents"] for cid, _ in pool)
    assert nav.lexical.idf == old
    nav.meta_lexical.search = lambda *a: []
    nav.meta_vectors = [[0.0] * 384 for _ in nav.views]
    assert nav.retrieve("absent")[0] == []
    assert nav.retrieve("absent")[1]["empty_reason"] == "no_metadata_hit"


def test_failure_is_at_earliest_stage_and_negatives_are_unknown():
    row = {
        "answerable": True,
        "candidate_complete": False,
        "top15_complete": False,
        "delivered": {"complete": False},
    }
    assert loss_stage(row, False) == "document_filter"
    assert loss_stage(row) == "body_recall"
    row["candidate_complete"] = True
    assert loss_stage(row) == "rerank"
    row["top15_complete"] = True
    assert loss_stage(row) == "delivery"
    row["answerable"] = False
    assert loss_stage(row) is None


def runner():
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    sys.path.insert(0, str(scripts))
    spec = importlib.util.spec_from_file_location(
        "metadata_runner", scripts / "benchmark_metadata_retrieval.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_h_timing_does_not_retrieve_unused_baseline():
    module = runner()

    class Engine:
        new_pairs = 0

        def recall(self, *args, **kwargs):
            pytest.fail("H must not retrieve baseline")

        def score(self, pool, *args, **kwargs):
            self.new_pairs += len(pool)
            return {"hits": pool}

    navigator = SimpleNamespace(retrieve=lambda q: ([], {"documents": []}))
    _, _, work = module.build(Engine(), navigator, "H", {"hits": []}, "q", False)
    assert work["actual_new_pairs"] == 0


def test_actual_pair_budget_enforced():
    module = runner()

    class Engine:
        new_pairs = 0

        def score(self, *args, **kwargs):
            self.new_pairs += 91
            return {}

    with pytest.raises(ValueError, match="Actual rerank"):
        module.build(Engine(), None, "B", {"hits": []}, "q", True)


def test_partial_latency_never_produces_overall_latency_gate(tmp_path):
    module = runner()
    rows = []
    for dataset in ("official", "repository"):
        for arm in ("B", "D", "H", "M"):
            rows.append(
                {
                    "dataset": dataset,
                    "arm": arm,
                    "id": "case",
                    "group_id": "g",
                    "answerable": True,
                    "candidate_complete": True,
                    "candidate_coverage": 1.0,
                    "top5_complete": True,
                    "top15_complete": True,
                    "document_complete": True,
                    "loss_stage": "complete",
                    "delivered": {"complete": True},
                }
            )
    module.report(tmp_path, rows, [{"arm": "B", "latency_ms": 123}])
    import json

    summary = json.loads((tmp_path / "summary.json").read_text())
    assert summary["warm_latency"] is None
    assert summary["latency_gate"] is None
    assert summary["latency_complete"] is False
    assert summary["adopted"] is False
