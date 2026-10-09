import copy
import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from infra_rag.config import Settings
from infra_rag.models import Chunk
from infra_rag.recall_experiments import (
    DeliveryRetrieval,
    context_views,
    focused_queries,
    rank_fusion,
    score_bundle,
    supplement,
)


def chunk(cid, text, start, end, parent="p", source="document.md"):
    return Chunk(
        cid,
        parent,
        source,
        text,
        "infra",
        heading="Cache conditions",
        start_line=start,
        end_line=end,
        metadata={"product": "vllm", "release": "v0.10.2"},
    )


def test_focused_queries_keep_original_identifiers_without_inventing_answers():
    original = "vLLM v0.10.2对比SGLang AMD DeepSeekV3，应查PR哪种FP8格式？"
    facets = [{"question": "Which FP8 format is in the PR?", "anchor_quote": "应查PR哪种FP8格式"}]
    result = focused_queries(original, facets)
    assert all(token in result[0] for token in ["vLLM", "v0.10.2", "SGLang", "AMD", "DeepSeekV3"])
    assert "e4m3fnuz" not in result[0]
    with pytest.raises(ValueError, match="anchor"):
        focused_queries(original, [{"question": "invented", "anchor_quote": "not in question"}])


def test_chinese_question_context_and_duplicate_queries():
    q = "两种缓存方案应怎样比较？"
    f = {"question": "两种方案如何比较？", "anchor_quote": "两种缓存方案"}
    assert len(focused_queries(q, [f, f])) == 1
    assert q in focused_queries(q, [f])[0]


def test_context_views_preserve_ids_locators_and_original_bodies():
    items = [
        chunk("a", "These hashes identify a block.", 1, 1),
        chunk("b", "Other values make it unique.", 2, 2),
    ]
    saved = copy.deepcopy(items)
    views, records = context_views(items)
    assert items == saved
    assert views[1].id == items[1].id and views[1].source == items[1].source
    assert views[1].content.endswith(items[1].content)
    assert "These hashes identify a block." in records["b"]["prefix"]
    assert records["b"]["previous_chunk_id"] == "a"
    assert "v0.10.2" in views[1].content


@pytest.mark.parametrize("prior", ["```python\nunsafe\n```", "x" * 170])
def test_context_does_not_partially_copy_code_or_long_lines(prior):
    views, records = context_views([chunk("a", prior, 1, 1), chunk("b", "Evidence.", 2, 2)])
    assert records["b"]["previous_chunk_id"] is None
    assert "Previous source line" not in views[1].content


def test_context_never_crosses_parent_source_or_reversed_line_range():
    original = chunk("a", "Private antecedent.", 10, 11)
    for item in [
        chunk("b", "new", 12, 12, parent="other"),
        chunk("b", "new", 12, 12, source="other.md"),
        chunk("b", "new", 9, 9),
    ]:
        assert context_views([original, item])[1]["b"]["previous_chunk_id"] is None


def test_supplement_retains_all_baseline_candidates_and_caps_new_ids():
    base = [{"chunk_id": "old", "score": 0.1}]
    ranks = [[{"chunk_id": "new1"}, {"chunk_id": "old"}, {"chunk_id": "new2"}]]
    result = supplement(base, ranks, limit=1)
    assert [cid for cid, _ in result] == ["old", "new1"]
    with pytest.raises(ValueError, match="duplicate"):
        rank_fusion([[{"chunk_id": "same"}, {"chunk_id": "same"}]])


def test_score_cache_requires_exact_full_query_original_body_and_model():
    items = {"a": chunk("a", "original", 1, 1)}
    cache, calls = {}, []

    def scorer(pairs):
        calls.extend(pairs)
        return [0.8] * len(pairs)

    for query, model in [
        ("full question", "m1"),
        ("full question", "m1"),
        ("new question", "m1"),
        ("full question", "m2"),
    ]:
        score_bundle([("a", 0.1)], query, items, model, scorer, cache)
    assert len(calls) == 3
    items["a"].content = "modified"
    score_bundle([("a", 0.1)], "full question", items, "m1", scorer, cache)
    assert calls[-1] == ("full question", "modified")


def test_top8_delivery_is_separate_from_top10_ranking_and_respects_budget(tmp_path):
    chunks = [chunk(str(i), "Evidence " + str(i) + ".", i, i, parent=str(i)) for i in range(10)]
    base = SimpleNamespace(
        chunks=chunks,
        vectors=[[1] for _ in chunks],
        parent_index={c.id: [c] for c in chunks},
        settings=Settings(data_dir=tmp_path),
        _encoder=lambda: SimpleNamespace(token_length=len),
    )
    bundles = {
        "query": {
            "hits": [
                {"chunk_id": c.id, "score": 0.1, "rerank_score": 1 - i / 10}
                for i, c in enumerate(chunks)
            ],
            "sha256": "frozen",
        }
    }
    wrapper = DeliveryRetrieval(base, bundles, 8)
    diag, context = {}, {}
    ranking = wrapper.search("query", top_k=10, domain="infra", modality="text", diagnostics=diag)
    delivered = wrapper.search(
        "query", top_k=5, domain="infra", modality="text", context_pack=context
    )
    assert len(ranking) == 10 and len(delivered) == len(context["evidence"]) == 8
    assert diag["delivery_k"] == 8 and context["used_tokens"] <= 1200


def test_v4_setup_and_failed_gate_do_not_read_confirmation(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    benchmark = importlib.import_module("benchmark_recall_v4")
    official = tmp_path / "evals/infra-official-v1-reviewed"
    repository = tmp_path / "repo"
    old = tmp_path / "old"
    routing = tmp_path / "evals/merged-corpus-v2/routing-v2-20261002"
    output = tmp_path / "output"
    for directory in (official, repository, old, routing, output):
        directory.mkdir(parents=True)
    qs = [{"id": str(i), "query": f"query {i}"} for i in range(60)]
    (official / "dev.json").write_text(json.dumps(qs))
    (repository / "dev.json").write_text(json.dumps(qs[:50]))
    rewrites = official / "results/dev-opt-english-query-20261001/query-rewrites.jsonl"
    rewrites.parent.mkdir(parents=True)
    rewrites.write_text("[]")
    (routing / "protocol.json").write_text(
        json.dumps(
            {
                "official_dev_sha256": benchmark.digest(official / "dev.json"),
                "repo_dev_sha256": benchmark.digest(repository / "dev.json"),
                "rewrites_sha256": benchmark.digest(rewrites),
            }
        )
    )
    (routing / "rows.jsonl").write_text("")
    (old / "protocol.json").write_text(
        json.dumps(
            {
                "directory": "data",
                "manifest_sha256": "frozen",
                "models": {},
                "generation_ids": [],
                "coverage_ids": [],
            }
        )
    )
    (old / "rows.jsonl").write_text("")
    (output / "experiment-plan.md").write_text("frozen plan")
    script = tmp_path / "scripts/benchmark_recall_v4.py"
    script.parent.mkdir()
    for name in (
        script.name,
        "benchmark_selection_v3.py",
        "benchmark_corpus_v2.py",
        "prepare_corpus_v2.py",
    ):
        (script.parent / name).write_text("# fixture")
    monkeypatch.setattr(benchmark, "ROOT", tmp_path)
    monkeypatch.setattr(benchmark, "OLD", old)
    monkeypatch.setattr(benchmark, "OUT", output)
    monkeypatch.setattr(benchmark, "__file__", str(script))
    monkeypatch.setattr(benchmark, "repo_questions", lambda: (repository, qs[:50]))
    monkeypatch.setattr(benchmark, "load_rewrites", lambda *args: {})
    monkeypatch.setattr(
        benchmark, "client", lambda *args: SimpleNamespace(configuration=lambda: {})
    )
    baseline = [
        {"arm": "P0-T", "dataset": ds, "query": q["query"]}
        for ds, selected in (("official", qs), ("repository", qs[:50]))
        for q in selected
    ]
    monkeypatch.setattr(benchmark, "read_rows", lambda _: baseline)
    read = Path.read_text

    def safe_read(path, *args, **kwargs):
        assert path.name not in {"holdout.json", "test.json"}
        return read(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", safe_read)
    run = output / "run"
    protocol, _, _ = benchmark.setup(run)
    (run / "decision.json").write_text('{"winner":null}')
    benchmark.confirmation(run, None, None, protocol)
    assert json.loads((run / "confirmation-status.json").read_text())[
        "no_confirmation_questions_read"
    ]
