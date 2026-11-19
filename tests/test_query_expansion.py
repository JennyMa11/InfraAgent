import json

import pytest

from infra_rag.assistant import AnswerService, ModelUnavailable
from infra_rag.config import Settings
from infra_rag.query_expansion import (
    QueryDecomposer,
    QueryTranslator,
    decompose_query,
    load_rewrites,
)
from infra_rag.service import RetrievalService


class TranslatorModel:
    def __init__(self, raw='{"english_query":"PagedAttention KV cache fragmentation"}'):
        self.raw, self.calls = raw, []

    def generate(self, messages):
        self.calls.append(messages)
        return self.raw


def test_translator_cache_is_bounded_and_invalid_results_are_not_cached():
    model = TranslatorModel()
    translator = QueryTranslator(model, cache_size=1)
    assert translator.expand("分页作用")[1]["cached"] is False
    assert translator.expand("分页作用")[1]["cached"] is True
    translator.expand("显存碎片")
    translator.expand("分页作用")
    assert len(model.calls) == 3
    assert model.calls[0][1]["content"] == "分页作用"
    model.raw = '{"english_query":[]}'
    with pytest.raises(ValueError):
        translator.expand("new")
    assert "new" not in translator.cache


def test_chat_translates_retrieval_but_keeps_original_question_and_citations(tmp_path):
    service = RetrievalService(Settings(data_dir=tmp_path / "index", chunk_size=100))
    document = tmp_path / "notes.md"
    document.write_text("# PagedAttention\n\nPagedAttention reduces KV cache fragmentation.")
    service.ingest(document)
    original = "分页注意力有什么作用？"
    translator_model = TranslatorModel()

    class AnswerModel:
        model = "test"

        def generate(self, messages):
            self.messages = messages
            import re

            cid = re.search(r"\[(E[a-f0-9]{24})\]", messages[-1]["content"]).group(1)
            return json.dumps({"supported": True, "answer": "减少碎片。", "citations": [cid]})

    model = AnswerModel()
    assistant = AnswerService(service, model=model, translator=QueryTranslator(translator_model))
    result = assistant.answer(original)
    assert result["status"] == "answered"
    assert result["trace"][1]["query"] == "PagedAttention KV cache fragmentation"
    assert original in model.messages[-1]["content"]
    assert "证据" not in translator_model.calls[0][1]["content"]
    assert assistant.conversation(result["conversation_id"])["turns"][0]["content"] == original
    assert result["citations"][0]["citation_id"] in result["answer"]


def test_translation_failure_uses_original_query_with_visible_trace(tmp_path):
    class BrokenTranslator:
        def expand(self, query):
            raise ModelUnavailable("unavailable")

    class UnusedModel:
        model = "test"

    service = RetrievalService(Settings(data_dir=tmp_path / "index"))
    result = AnswerService(service, model=UnusedModel(), translator=BrokenTranslator()).answer(
        "原题"
    )
    assert result["trace"][0]["status"] == "fallback_original"
    assert result["trace"][1]["query"] == "原题"
    assert result["status"] == "no_evidence"


def test_frozen_translations_reject_duplicate_or_changed_questions(tmp_path):
    path = tmp_path / "rewrites.jsonl"
    record = {"id": "q1", "original_query": "原题", "english_query": "question"}
    path.write_text(json.dumps(record) + "\n" + json.dumps(record))
    with pytest.raises(ValueError, match="duplicates"):
        load_rewrites(path, [{"id": "q1", "query": "原题"}])
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="fixed question"):
        load_rewrites(path, [{"id": "q1", "query": "不同原题"}])
    assert load_rewrites(path, [{"id": "q1", "query": "原题"}]) == {"原题": "question"}


def test_query_language_does_not_change_existing_index_fingerprint():
    assert Settings(query_language="english").fingerprint() == Settings().fingerprint()


def test_delivery_depth_and_decomposition_do_not_change_index_fingerprint():
    changed = Settings(answer_top_k=10, query_decomposition=True)
    assert changed.fingerprint() == Settings().fingerprint()
    with pytest.raises(ValueError, match="answer_top_k"):
        Settings(answer_top_k=0)
    with pytest.raises(ValueError, match="neighbors/prefix"):
        Settings(query_decomposition=True, context_mode="legacy")


def test_decomposer_is_bounded_and_caches_valid_results():
    class Model:
        raw = '{"sub_queries":["first","second"]}'

        def __init__(self):
            self.calls = []

        def generate(self, messages):
            self.calls.append(messages)
            return self.raw

    model = Model()
    decomposer = QueryDecomposer(model, cache_size=1)
    assert decomposer.expand("原题", "question")[0] == ["first", "second"]
    assert decomposer.expand("原题", "question")[1]["cached"] is True
    decomposer.expand("另一题", "")
    decomposer.expand("原题", "question")
    assert len(model.calls) == 3
    model.raw = '{"sub_queries":[]}'
    with pytest.raises(ValueError):
        decomposer.expand("失败题", "")
    assert ("失败题", "") not in decomposer.cache


def test_chat_decomposes_and_delivers_configured_depth(tmp_path, monkeypatch):
    service = RetrievalService(
        Settings(
            data_dir=tmp_path / "index",
            chunk_size=100,
            answer_top_k=2,
            query_decomposition=True,
        )
    )
    document = tmp_path / "notes.md"
    document.write_text("# PagedAttention\n\nPagedAttention reduces KV cache fragmentation.")
    service.ingest(document)
    original = service.search_queries
    calls = []

    def observed(queries, **kwargs):
        calls.append((list(queries), kwargs["top_k"]))
        return original(queries, **kwargs)

    monkeypatch.setattr(service, "search_queries", observed)

    class Model:
        model = "test"

        def generate(self, messages):
            if "sub-queries" in messages[0]["content"]:
                return json.dumps(
                    {"sub_queries": ["PagedAttention KV cache", "KV cache fragmentation"]}
                )
            import re

            cid = re.search(r"\[(E[a-f0-9]{24})\]", messages[-1]["content"]).group(1)
            return json.dumps({"supported": True, "answer": "减少碎片。", "citations": [cid]})

    result = AnswerService(service, model=Model()).answer("分页注意力有什么作用？")
    assert result["status"] == "answered"
    assert calls == [
        (
            ["分页注意力有什么作用？", "PagedAttention KV cache", "KV cache fragmentation"],
            2,
        )
    ]
    assert [step["step"] for step in result["trace"]] == [
        "query_decompose",
        "retrieve",
        "generate",
    ]
    assert result["trace"][1]["top_k"] == 2


def test_decomposition_failure_falls_back_to_single_query(tmp_path):
    class BrokenDecomposer:
        def expand(self, query, english=None):
            raise ModelUnavailable("unavailable")

    service = RetrievalService(Settings(data_dir=tmp_path / "index", query_decomposition=True))
    result = AnswerService(
        service,
        model=type("Model", (), {"model": "test"})(),
        decomposer=BrokenDecomposer(),
    ).answer("原题")
    assert result["trace"][0]["status"] == "fallback_single"
    assert result["trace"][1]["queries"] == ["原题"]
    assert result["status"] == "no_evidence"


def test_decompose_query_accepts_bounded_unique_subqueries():
    model = TranslatorModel(
        raw='{"sub_queries":["What is APC?","Which computation can APC skip?","What is APC?"]}'
    )
    assert decompose_query("APC复用什么", "What does APC reuse?", model) == [
        "What is APC?",
        "Which computation can APC skip?",
    ]
    assert "Original question: APC复用什么" in model.calls[0][1]["content"]


def test_decompose_query_rejects_empty_duplicate_or_unbounded_results():
    for raw in (
        '{"sub_queries":[]}',
        '{"sub_queries":[""]}',
        '{"sub_queries":["a","b","c","d"]}',
        '{"sub_queries":[1]}',
        "not json",
    ):
        with pytest.raises((ValueError, json.JSONDecodeError)):
            decompose_query("q", "q", TranslatorModel(raw=raw))
