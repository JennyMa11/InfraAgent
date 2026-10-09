import json

import pytest

from infra_rag.assistant import AnswerService, ModelUnavailable
from infra_rag.config import Settings
from infra_rag.query_expansion import QueryTranslator, load_rewrites
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
