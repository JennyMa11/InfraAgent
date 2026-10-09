import copy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from infra_rag.agent import ResearchAgent
from infra_rag.agent_comparison import CoverageResearchAgent, V6ComparisonRetrieval
from infra_rag.budget_ablation import AblationPacker
from infra_rag.config import Settings
from infra_rag.models import Chunk, Hit


def fixture(tmp_path):
    chunks = [
        Chunk(str(i), f"p{i}", "source", text, "infra", heading="Facts", locator="source#L1")
        for i, text in enumerate(("cache salt only tenant", "full block condition"))
    ]
    scores = [0.9, 0.8]
    base = SimpleNamespace(
        chunks=chunks,
        settings=Settings(data_dir=tmp_path),
        _encoder=lambda: SimpleNamespace(token_length=len),
    )
    bundle = {
        "cache": {
            "scoring_query": "cache",
            "hits": [
                {"chunk_id": c.id, "rerank_score": score}
                for c, score in zip(chunks, scores, strict=True)
            ],
        }
    }
    return base, bundle, chunks, scores


def test_same_v6_context_for_both_executors_without_labels_or_input_mutation(tmp_path):
    base, bundle, chunks, scores = fixture(tmp_path)
    saved = copy.deepcopy(bundle)
    adapter = V6ComparisonRetrieval(base, bundle, len)
    context, diag = {}, {}
    adapter.search("cache", domain="infra", context_pack=context, diagnostics=diag)
    expected = AblationPacker(
        [Hit(c, 0, rerank_score=s) for c, s in zip(chunks, scores, strict=True)],
        {"evidence": []},
        {c.id: c for c in chunks},
        "cache\ncache",
        len,
    ).pack(length_power=0, neighbors=False)[1]
    assert context == expected
    assert bundle == saved
    assert set(diag["final"][0]) == {"chunk_id", "rerank_score"}
    assert set(diag["candidates"]) == {"0", "1"}


def test_self_generated_followup_query_uses_actual_same_backend(tmp_path):
    base, bundle, chunks, _ = fixture(tmp_path)
    queries = []

    def search(query, **kwargs):
        queries.append(query)
        kwargs["diagnostics"].update(final=[{"chunk_id": "1", "rerank_score": 0.95}])
        return [Hit(chunks[1], 0, rerank_score=0.95)]

    base.search = search
    adapter = V6ComparisonRetrieval(base, bundle, len)
    diag = {}
    hits = adapter.search("full block", domain="infra", diagnostics=diag)
    assert queries == ["full block"]
    assert hits[0].chunk.id == "1"
    assert diag["comparison_provenance"] == "new_live_retrieval"
    adapter.search("full block", domain="infra")
    assert queries == ["full block"]


def test_coverage_selection_cannot_restore_unseen_or_truncated_text(tmp_path):
    base, bundle, chunks, _ = fixture(tmp_path)
    actual_pairs = []

    def predict(pairs):
        actual_pairs.extend(pairs)
        return [0.9] * len(pairs)

    base.reranker = SimpleNamespace(predict=predict)
    adapter = V6ComparisonRetrieval(base, bundle, len)
    available = {
        "E0": {
            "id": "E0",
            "chunk_id": "0",
            "parent_id": "p0",
            "source": "source",
            "locator": "source#L1",
            "content": "cache salt",
            "truncated": True,
        }
    }
    saved = copy.deepcopy(available)
    agent = CoverageResearchAgent(adapter, SimpleNamespace(), scoring_query="tenant")
    packed = agent._pack(available)
    assert packed == list(available.values())
    assert packed[0]["content"] == "cache salt" and packed[0]["truncated"]
    assert actual_pairs == [("tenant", "cache salt")]
    assert available == saved
    assert "full block" not in json.dumps(packed)


def test_coverage_reordering_preserves_actual_locator_header_budget(tmp_path):
    base, bundle, _, _ = fixture(tmp_path)
    base.settings = Settings(
        data_dir=tmp_path, chunk_size=100, context_tokens=100, context_chars=100
    )
    base.reranker = SimpleNamespace(predict=lambda pairs: [0.9] * len(pairs))
    adapter = V6ComparisonRetrieval(base, bundle, len)
    available = {
        "E0": {
            "id": "E0",
            "chunk_id": "0",
            "parent_id": "p0",
            "source": "source",
            "locator": "a" * 90,
            "content": "cache salt only tenant",
            "truncated": False,
        }
    }
    new = CoverageResearchAgent(adapter, SimpleNamespace(), scoring_query="cache")._pack(available)
    old = ResearchAgent(base, SimpleNamespace())._pack(available)
    assert new == old
    rendered = "\n\n".join(f"[{e['id']}] {e['locator']}\n{e['content']}" for e in new)
    assert len(rendered) <= 100


def test_comparison_rejects_filters_outside_frozen_scope(tmp_path):
    base, bundle, _, _ = fixture(tmp_path)
    with pytest.raises(ValueError, match="filters"):
        V6ComparisonRetrieval(base, bundle, len).search("cache", domain="other")


def test_pilot_selection_is_order_independent_and_cluster_distinct():
    import importlib.util
    import sys

    scripts = Path(__file__).resolve().parents[1] / "scripts"
    sys.path.insert(0, str(scripts))
    try:
        spec = importlib.util.spec_from_file_location(
            "comparison_benchmark", scripts / "benchmark_rag_agent_comparison.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        rows = [
            {
                "id": f"{ds}-{i}",
                "group_id": i // 2,
                "dataset": ds,
                "answerable": True,
                "delivered": {"complete": i % 2},
            }
            for ds in ("official", "repository")
            for i in range(10)
        ]
        selected = module.select_pilot(rows)
        altered = [
            {**r, "delivered": {"complete": 1 - r["delivered"]["complete"]}} for r in reversed(rows)
        ]
        assert [r["id"] for r in selected] == [r["id"] for r in module.select_pilot(altered)]
        for ds in ("official", "repository"):
            assert len({r["group_id"] for r in selected if r["dataset"] == ds}) == 3
    finally:
        sys.path.remove(str(scripts))
