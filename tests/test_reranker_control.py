"""A changed reranker cannot silently change evidence, query or scoring budget."""

import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from infra_rag.models import Chunk


def scorer(monkeypatch, tmp_path, outputs):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    driver = importlib.import_module("benchmark_reranker_v10")
    obj = driver.Scorer.__new__(driver.Scorer)
    obj.run, obj.protocol = tmp_path, {"m3": {"revision": "fixed"}}
    obj.chunks = {
        cid: Chunk(cid, "p", "doc.md", text, "infra")
        for cid, text in (("a", "First condition"), ("b", "Second condition"))
    }
    calls = []

    def predict(pairs, **kwargs):
        calls.append(pairs)
        return outputs[: len(pairs)]

    obj.model = SimpleNamespace(
        predict=predict, tokenizer=SimpleNamespace(encode=lambda q, text: [0] * len(q + text))
    )
    obj.cache, obj.calls, obj.actual_pairs, obj.dtype = {}, [], 0, "torch.float32"
    source = {
        "dataset": "test",
        "id": "q1",
        "query": "Whole question",
        "scoring_query": "whole English question",
        "resolved_gold": {"unchanged": True},
        "ranked_hits": [
            {"chunk_id": "a", "score": 0.1, "rerank_score": 0.9},
            {"chunk_id": "b", "score": 0.2, "rerank_score": 0.1},
        ],
    }
    return obj, source, calls


def test_only_rerank_changes_and_raw_logits_are_sigmoid_normalized(monkeypatch, tmp_path):
    obj, source, calls = scorer(monkeypatch, tmp_path, [-2.0, 2.0])
    result = obj.score(source)
    assert [h["chunk_id"] for h in result["hits"]] == ["b", "a"]
    assert calls == [
        [
            ("whole English question", "First condition"),
            ("whole English question", "Second condition"),
        ]
    ]
    assert source["ranked_hits"][0]["rerank_score"] == 0.9
    assert {h["chunk_id"]: h["score"] for h in result["hits"]} == {"a": 0.1, "b": 0.2}
    assert all(0 < h["rerank_score"] < 1 for h in result["hits"])
    assert obj.calls[0]["raw_logits"] == [-2.0, 2.0]
    assert obj.actual_pairs == 2


def test_cache_requires_same_query_body_and_model_and_runtime_executes_again(monkeypatch, tmp_path):
    obj, source, calls = scorer(monkeypatch, tmp_path, [0.0, 0.0])
    obj.score(source)
    obj.score(source)
    assert len(calls) == 1
    obj.score(source, cached=False)
    assert len(calls) == 2 and obj.actual_pairs == 4
    obj.chunks["a"].content += " changed"
    obj.score(source)
    assert len(calls[-1]) == 1 and obj.actual_pairs == 5
    obj.protocol["m3"]["revision"] = "another"
    obj.score(source)
    assert len(calls[-1]) == 2


def test_nonfinite_logits_are_rejected(monkeypatch, tmp_path):
    obj, source, _ = scorer(monkeypatch, tmp_path, [float("nan"), 0.0])
    with pytest.raises(ValueError, match="Nonfinite"):
        obj.score(source)
