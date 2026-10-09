"""The Ladj runtime control may omit only channels whose results are unused."""

import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from infra_rag.config import Settings


def driver(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    return importlib.import_module("benchmark_budget_search_demand_runtime_v8")


def test_adjacent_call_executes_only_consumed_bm25_without_result_cache(monkeypatch):
    module = driver(monkeypatch)
    engine = module.CopiedIndexEngine.__new__(module.CopiedIndexEngine)
    calls = []
    service = SimpleNamespace(settings=Settings())

    def search(query, **kwargs):
        calls.append((query, kwargs.copy()))
        kwargs["diagnostics"].update(
            channels={"bm25": {"ranking": [{"chunk_id": "original"}]}}, timings_ms={"bm25": 1.0}
        )

    service.search = search
    engine.service = lambda kind: service
    engine.new_recalls = 0
    result = engine.recall("whole query", "adjacent", 30, cached=False)
    assert result["channels"] == {"bm25": {"ranking": [{"chunk_id": "original"}]}}
    assert calls[0][1]["strategy"] == "bm25"
    assert calls[0][1]["domain"] == "infra" and calls[0][1]["modality"] == "text"
    assert service.settings.context_mode == "legacy" and service.settings.candidate_k == 30
    assert engine.new_recalls == 1
    with pytest.raises(ValueError, match="without result cache"):
        engine.recall("whole query", "adjacent", 30, cached=True)
    assert len(calls) == 1


def test_base_recall_still_uses_original_call_and_cache_contract(monkeypatch):
    module = driver(monkeypatch)
    expected = {"unchanged": True}
    calls = []

    def original(self, query, kind, k, *, cached=True):
        calls.append((query, kind, k, cached))
        return expected

    monkeypatch.setattr(module.Engine, "recall", original)
    engine = module.CopiedIndexEngine.__new__(module.CopiedIndexEngine)
    assert engine.recall("whole query", "base", 30, cached=False) is expected
    assert calls == [("whole query", "base", 30, False)]
