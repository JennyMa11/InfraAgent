"""Regression controls for offline experiments on the adopted RAG."""

import copy
import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from infra_rag.benchmarking import span_coverage
from infra_rag.evaluation import evidence_metrics
from infra_rag.models import Chunk
from infra_rag.original_rag_experiments import (
    TechnicalBM25,
    additive_pool,
    adjacency_map,
    adjacent_views,
    bounded_focused_queries,
    neighbor_bundle,
    pack_bundle,
    technical_tokens,
)


def chunk(cid, body, line, **kwargs):
    return Chunk(
        cid,
        kwargs.pop("parent_id", "p"),
        kwargs.pop("source", "doc.md"),
        body,
        "infra",
        start_line=line,
        end_line=line,
        locator=f"doc.md:{line}",
        metadata=kwargs.pop("metadata", {"release": "v1"}),
        **kwargs,
    )


def test_technical_matching_keeps_literal_tokens_and_normalizes_both_sides():
    tokens = technical_tokens("recomputation disaggregated num_kv_heads v0.10.2")
    assert {
        "recomputation",
        "recomput",
        "disaggreg",
        "num_kv_heads",
        "kv",
        "heads",
        "v0.10.2",
    } <= set(tokens)
    items = [
        chunk("condition", "Preempted requests are recomputed.", 1),
        chunk("other", "A cache stores data.", 2),
    ]
    index = TechnicalBM25(items)
    assert index.search("recomputation", 1)[0][0] == "condition"
    changed = copy.deepcopy(items)
    changed[0].content += " changed"
    assert index.identity != TechnicalBM25(changed).identity


def test_additive_pool_preserves_baseline_and_enforces_90_cap():
    base = [{"chunk_id": str(i), "score": 0.1} for i in range(60)]
    extra = [[{"chunk_id": str(i)} for i in range(45, 130)]]
    pool = additive_pool(base, extra)
    assert len(pool) == len(set(cid for cid, _ in pool)) == 90
    assert {str(i) for i in range(60)} <= {cid for cid, _ in pool}
    with pytest.raises(ValueError):
        additive_pool(base + [base[0]], extra)
    with pytest.raises(ValueError):
        additive_pool(base, extra, limit=31)


def test_adjacent_views_preserve_originals_and_never_cross_release_or_parent():
    items = [
        chunk("a", "Definition " * 30, 1),
        chunk("b", "KV_bytes = K + V", 2),
        chunk("other_release", "wrong version", 3, metadata={"release": "v2"}),
        chunk("other_parent", "unrelated", 4, parent_id="x"),
    ]
    saved = copy.deepcopy(items)
    views, records = adjacent_views(items)
    assert items == saved
    assert records["b"]["adjacent_ids"] == ["a"]
    assert items[0].content[:160] in records["b"]["prefix"]
    assert "wrong version" not in views[1].content
    assert [(v.id, v.locator) for v in views] == [(c.id, c.locator) for c in items]
    assert all(v.content.endswith(c.content) for v, c in zip(views, items, strict=True))
    items[0].content += " new definition"
    assert records != adjacent_views(items)[1]


def test_context_adjacency_ignores_overlapping_and_unlocated_chunks():
    items = [chunk("a", "a", 1), chunk("b", "b", 1), chunk("c", "c", 2)]
    items.append(Chunk("unknown", "p", "doc.md", "unknown", "infra"))
    adjacent = adjacency_map(items)
    assert adjacent["a"] == [] and adjacent["unknown"] == []
    assert adjacent["b"] == ["c"]


def test_facets_keep_product_version_local_and_fallback_on_invalid_inputs():
    original = "vLLM v0.10.2：根据SGLang解释分离阶段，再检查vLLM吞吐限制。"
    facets = [
        {
            "anchor_quote": "根据SGLang解释分离阶段",
            "question": "What does SGLang disaggregation do?",
        },
        {
            "anchor_quote": "再检查vLLM吞吐限制",
            "question": "Does vLLM v0.10.2 guarantee throughput?",
        },
    ]
    queries, error = bounded_focused_queries(original, "full English query", facets)
    assert error is None and "v0.10.2" not in queries[0] and "vLLM" not in queries[0]
    assert "vLLM v0.10.2" in queries[1]
    for invalid in [
        None,
        [],
        [{}],
        [{"anchor_quote": "missing", "question": "q"}],
        [{"anchor_quote": "vLLM", "question": "vLLM v9.9.9"}],
    ]:
        qs, error = bounded_focused_queries(original, "fallback", invalid)
        assert qs == ["fallback"] and error


def test_neighbor_scoring_uses_original_bodies_and_cumulative_candidate_cap():
    chunks = {str(i): chunk(str(i), f"Condition {i}.", i + 1) for i in range(100)}
    bundle = {
        "scoring_query": "full question",
        "hits": [{"chunk_id": str(i), "score": 0.1, "rerank_score": 0.8} for i in range(89)],
    }
    chosen = pack_bundle(bundle, chunks, "q", len)[0]
    calls = []

    def scorer(pairs):
        calls.extend(pairs)
        return [0.9] * len(pairs)

    adjacent = {h.chunk.id: ["89", "90"] for h in chosen}
    scored, added = neighbor_bundle(bundle, chosen, adjacent, chunks, "model", scorer, {})
    assert len(scored["hits"]) == 90 and len(added) == 1
    assert calls == [("full question", chunks[added[0]].content)]


def test_neighbor_frontier_can_include_low_rank_condition_and_keeps_budget():
    chunks = {str(i): chunk(str(i), f"Condition {i}.", i + 1) for i in range(17)}
    bundle = {
        "hits": [{"chunk_id": str(i), "score": 0.1, "rerank_score": 1 - i / 100} for i in range(17)]
    }
    _, context, trace = pack_bundle(bundle, chunks, "condition", len, frontier_ids=["0", "16"])
    assert trace["eligible_ids"] == ["0", "16"]
    assert context["used_tokens"] <= 1200 and context["used_characters"] <= 4000
    assert len(context["evidence"]) <= 8


def test_gold_groups_and_delivery_require_all_conditions_and_actual_text():
    gold = {
        "evidence_alternatives": [
            {
                "requirements": [["a"], ["b"]],
                "spans": [
                    {"absolute_source": "doc.md", "text": "Necessary condition."},
                    {"absolute_source": "doc.md", "text": "Required formula."},
                ],
            },
            {
                "requirements": [["c"], ["d"]],
                "spans": [
                    {"absolute_source": "other.md", "text": "Alternative one."},
                    {"absolute_source": "other.md", "text": "Alternative two."},
                ],
            },
        ]
    }
    assert evidence_metrics(["a", "d"], gold, 2)["complete_evidence_hit"] == 0
    assert evidence_metrics(["c", "d"], gold, 2)["complete_evidence_hit"] == 1
    question = {**gold, "answerable": True}
    delivered = [
        {"chunk_id": "a", "source": "doc.md", "content": "Necessary condition."},
        {"chunk_id": "b", "source": "doc.md", "content": "Required"},
    ]
    assert not span_coverage(delivered, question)["complete"]


def test_driver_freeze_rejects_changed_inputs_and_ranking_does_not_read_holdout(
    tmp_path, monkeypatch
):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    driver = importlib.import_module("benchmark_original_rag_v7")
    driver.freeze(tmp_path, "protocol.json", {"frozen": 1})
    with pytest.raises(ValueError, match="Frozen"):
        driver.freeze(tmp_path, "protocol.json", {"frozen": 2})
    summary = {
        f"{ds}:{arm}": {"candidate_complete": 4, "delivered_complete": 3 + (arm == "D60")}
        for ds in driver.DATASETS
        for arm in ["B", "D60"]
    }
    assert driver.rank_methods(summary, ["D60"]) == ["D60"]
    summary["official:D60"]["candidate_complete"] = 3
    assert driver.rank_methods(summary, ["D60"]) == []
    summary["official:D60"]["candidate_complete"] = 5
    summary["official:D60"]["delivered_complete"] = 3
    summary["repository:D60"]["delivered_complete"] = 3
    assert driver.rank_methods(summary, ["D60"]) == []
    assert driver.rank_methods(summary, ["D60"], include_candidate_only=True) == ["D60"]


def test_dev_report_keeps_confirmation_closed_without_independent_review(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    driver = importlib.import_module("benchmark_original_rag_v7")
    rows = []
    for ds in driver.DATASETS:
        rows.append(
            {
                "id": ds,
                "dataset": ds,
                "arm": "B",
                "answerable": True,
                "group_id": "g",
                "candidate_complete": 1,
                "candidate_coverage": 1,
                "candidate_count": 1,
                "top5_complete": 1,
                "delivered": {"complete": True},
            }
        )
    (tmp_path / "rows.jsonl").write_text("\n".join(json.dumps(r) for r in rows))
    original_read = Path.read_text

    def guard(path, *args, **kwargs):
        assert path.name not in {"holdout.json", "test.json"}
        return original_read(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guard)
    driver.report(tmp_path)
    decision = json.loads((tmp_path / "decision.json").read_text())
    assert decision["independent_review"] == "pending"
    assert decision["confirmation_allowed"] is False
    assert decision["confirmation_questions_read"] is False
    assert decision["default_changed"] is False


def test_live_combination_channels_do_not_repeat_baseline_or_intermediate_reranking(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    driver = importlib.import_module("benchmark_original_rag_v7")
    engine = driver.Engine.__new__(driver.Engine)
    calls = []

    def recall(query, kind, k, *, cached):
        calls.append((query, kind, k, cached))
        return {
            "channels": {
                "bm25": {"ranking": [{"chunk_id": "a"}]},
                "dense": {"ranking": [{"chunk_id": "b"}]},
            }
        }

    def unexpected_score(*args, **kwargs):
        pytest.fail("Intermediate channel collection must not rerank")

    engine.recall = recall
    engine.score = unexpected_score
    engine.technical = SimpleNamespace(identity="frozen", search=lambda *args: [("c", 1)])
    base = {"scoring_query": "question", "hits": []}
    row, facets = {"query": "question"}, [{"anchor_quote": "question", "question": "question"}]
    live_base = engine.bundle("B", base, row, facets, cached=False, score_candidates=False)
    candidate = engine.bundle(
        "T", live_base, row, facets, cached=False, score_candidates=False, base_live=True
    )
    assert calls == [("question", "base", 30, False)]
    assert {h["chunk_id"] for h in candidate["hits"]} == {"a", "b", "c"}
