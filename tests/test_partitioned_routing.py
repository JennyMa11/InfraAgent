import copy
import importlib
from dataclasses import replace
from pathlib import Path

import pytest
from test_preprocessed_retrieval import chunk

from infra_rag.evidence_metadata import metadata_text
from infra_rag.models import Hit
from infra_rag.partitioned import PartitionedRetrieval, RoutedQuery, prefer_versions


@pytest.fixture
def services(tmp_path):
    from infra_rag.config import Settings
    from infra_rag.service import RetrievalService

    config = Settings(data_dir=tmp_path / "base", candidate_k=30)
    base = RetrievalService(config)
    items = [
        chunk("o", "official.md", "cache hash english"),
        chunk("c", "community.md", "中文缓存 cache", collection="community"),
    ]
    base._commit(items)
    banks = {}
    for name, item in zip(("official", "community"), items, strict=True):
        bank = RetrievalService(replace(config, data_dir=tmp_path / name))
        bank._commit([item])
        banks[name] = bank

    class Reranker:
        def predict(self, pairs):
            self.pairs = pairs
            return [0.5] * len(pairs)

    base.settings = replace(base.settings, rerank=True)
    base.reranker = Reranker()
    return base, banks


@pytest.mark.parametrize("recall", ["original", "english"])
@pytest.mark.parametrize("rerank", ["english", "by_collection"])
def test_recall_and_rerank_languages_are_independent(services, recall, rerank):
    base, banks = services
    service = PartitionedRetrieval(
        base,
        banks,
        community_recall_language=recall,
        rerank_language=rerank,
    )
    detail = {}
    service.search(RoutedQuery("中文缓存", "cache hash"), strategy="bm25", diagnostics=detail)
    assert detail["banks"]["community"]["query"] == (
        "中文缓存" if recall == "original" else "cache hash"
    )
    for query, text in base.reranker.pairs:
        assert query == (
            "中文缓存" if "中文" in text and rerank == "by_collection" else "cache hash"
        )


def test_snapshot_replay_freezes_candidates_and_validates_recall(services, monkeypatch):
    base, banks = services
    query = RoutedQuery("中文缓存", "cache hash")
    snapshot, first = {}, {}
    english = PartitionedRetrieval(base, banks)
    english.search(query, strategy="bm25", candidate_snapshot=snapshot, diagnostics=first)
    saved = copy.deepcopy(snapshot)

    def forbidden(*args, **kwargs):
        raise AssertionError("Snapshot replay must not search the banks")

    for bank in banks.values():
        monkeypatch.setattr(bank, "search", forbidden)
    routed = PartitionedRetrieval(base, banks, rerank_language="by_collection")
    second = {}
    routed.search(query, strategy="bm25", candidate_snapshot=snapshot, diagnostics=second)
    assert second["candidates"] == first["candidates"]
    assert snapshot == saved
    assert ("中文缓存", "中文缓存 cache") in base.reranker.pairs
    with pytest.raises(ValueError, match="recall configuration"):
        routed.search("different query", strategy="bm25", candidate_snapshot=snapshot)
    changed = PartitionedRetrieval(base, banks, community_recall_language="original")
    with pytest.raises(ValueError, match="recall configuration"):
        changed.search(query, strategy="bm25", candidate_snapshot=snapshot)


def test_all_candidate_version_preference_recovers_rank_eleven_without_duplicates():
    hits = [Hit(chunk(str(i), f"{i}.md", "cache", collection="community"), 1) for i in range(12)]
    hits[10] = Hit(chunk("official", "official.md", "cache"), 1)
    query = "vLLM v0.10.2 缓存"
    old, info = prefer_versions(hits, query, 5, True)
    assert [h.chunk.id for h in old] == [str(i) for i in range(5)]
    assert info["missing_version_evidence"]
    assert not info["candidate_missing_version_evidence"]
    assert info["version_evidence_outside_top10"]
    selected, info = prefer_versions(hits, query, 5, True, scope="all")
    assert selected[0].chunk.id == "official"
    assert len({h.chunk.id for h in selected}) == len(selected) == 5
    assert not info["missing_version_evidence"]
    assert len(prefer_versions(hits, query, 1, True, scope="all")[0]) == 1
    selected, info = prefer_versions(hits, "CUDA v12.0", 5, True, scope="all")
    assert selected == hits[:5]
    assert info["candidate_missing_version_evidence"]
    assert not info["version_evidence_outside_top10"]
    assert prefer_versions(hits, query, 5, False, scope="all")[0] == hits[:5]


def test_metadata_input_and_top5_repacking_preserve_opt_in(services, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    memo = importlib.import_module("benchmark_corpus_v2").MemoizedRetrieval
    base, banks = services
    service = PartitionedRetrieval(base, banks, include_metadata=True)
    wrapper = memo(service)
    query = RoutedQuery("中文缓存", "cache hash")
    wrapper.search(query, top_k=10, strategy="bm25", context_pack={}, diagnostics={})
    assert all(
        "元数据：" in text and '"release": "v0.10.2"' in text for _, text in base.reranker.pairs
    )
    packed = {}
    wrapper.search(query, top_k=5, strategy="bm25", context_pack=packed)
    assert packed["include_evidence_metadata"] is True
    assert all("provenance" in item for item in packed["evidence"])
    assert all("元数据：" not in item["content"] for item in packed["evidence"])
    assert metadata_text({"collection": "community", "release": None, "unrelated": "secret"}) == (
        '元数据：{"collection": "community"}\n'
    )
    assert metadata_text({}) == ""


@pytest.mark.parametrize("enabled", [True, False])
def test_answer_prompt_metadata_is_explicit_and_optional(services, tmp_path, enabled):
    from test_assistant import FakeModel

    from infra_rag.assistant import AnswerService, ConversationStore
    from infra_rag.offline_evaluation import FrozenRetrieval

    base, _ = services
    item = {
        "citation_id": "E" + "a" * 24,
        "locator": "official.md#L1",
        "content": "cache",
        "metadata": {"collection": "official", "release": "v0.10.2", "scope": "page-locked"},
    }
    context = {"evidence": [item], "include_evidence_metadata": enabled}
    model = FakeModel()
    service = AnswerService(
        FrozenRetrieval(base.settings, context),
        model=model,
        store=ConversationStore(tmp_path / "answers.sqlite3"),
    )
    service.answer("cache")
    prompt = model.messages[0][-1]["content"]
    assert ("元数据：" in prompt) is enabled
    if enabled:
        assert '"scope": "page-locked"' in prompt


def test_frozen_reranker_reuses_identical_inputs_only(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    frozen = importlib.import_module("benchmark_routing_v2").FrozenReranker

    class Reranker:
        calls = 0

        def predict(self, pairs):
            self.calls += 1
            return [0.1] * len(pairs)

    model = Reranker()
    wrapper = frozen(model, "model", tmp_path)
    assert wrapper.predict([("query", "evidence")]) == [0.1]
    assert wrapper.predict([("query", "evidence")]) == [0.1]
    assert model.calls == 1
    wrapper.predict([("other language", "evidence")])
    assert model.calls == 2


def test_report_logging_accepts_relative_output_directory(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    benchmark = importlib.import_module("benchmark_routing_v2")
    monkeypatch.chdir(tmp_path)
    directory = Path("relative-output")
    directory.mkdir()
    stats = {
        f"{dataset}:{arm}": {
            "n": 1,
            "candidate_complete": 1,
            "top5_complete": 1,
            "delivered_complete": 1,
            "top5_collections": {"official": 1, "community": 0, "unknown": 0},
        }
        for dataset in ("official", "repository")
        for arm in ("processed_global30", *benchmark.ARMS)
    }
    monkeypatch.setattr(benchmark, "comparison", lambda rows: stats)
    logged = []
    monkeypatch.setattr(benchmark, "record_operation", lambda *args: logged.append(args))
    benchmark.write_report(directory, [])
    assert (directory / "report.md").exists()
    assert str(directory.resolve()) in logged[0][2]
