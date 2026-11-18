import json
import re
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from infra_rag.api import create_app
from infra_rag.assistant import AnswerService, ConversationStore
from infra_rag.config import Settings
from infra_rag.experimental_pages import PageBudgetError, RequestModel, pages_from_chunks
from infra_rag.models import Chunk
from infra_rag.service import RetrievalService


class Model:
    model = "fixture"
    timeout = 180

    def __init__(self, broken=False):
        self.messages = []
        self.broken = broken

    def generate(self, messages):
        self.messages.append(messages)
        if "selections" in messages[0]["content"]:
            cid = "Ebad" if self.broken else "E1"
            return json.dumps({"selections": [{"id": cid, "relevance": "direct"}]})
        ids = re.findall(r"\[(E[A-Za-z0-9_-]+)\]", messages[-1]["content"])
        return json.dumps(
            {
                "supported": True,
                "answer": "verified " + " ".join(f"[{c}]" for c in ids),
                "citations": list(dict.fromkeys(ids)),
            }
        )


class Retrieval:
    def __init__(self, tmp_path):
        self.settings = Settings(data_dir=tmp_path)
        self.context_counter = len
        self.searches = 0
        self.pages = [
            {
                "evidence": [
                    {"citation_id": "E" + "a" * 32, "locator": "url", "content": "First evidence."}
                ]
            },
            {
                "evidence": [
                    {"citation_id": "E" + "b" * 32, "locator": "url", "content": "Later condition."}
                ]
            },
        ]

    def search(self, query, *, context_pack, **kwargs):
        self.searches += 1
        context_pack.update(self.pages[0])
        return []

    def evidence_pages(self, hits, domain=None):
        return self.pages


def client(tmp_path, broken=False):
    retrieval = Retrieval(tmp_path)
    model = Model(broken)
    assistant = AnswerService(retrieval, model, ConversationStore(tmp_path / "history.sqlite"))
    return TestClient(create_app(retrieval, assistant)), retrieval, model


def test_api_default_does_not_read_later_pages(tmp_path):
    api, retrieval, model = client(tmp_path)
    result = api.post("/chat", json={"message": "question"}).json()
    assert result["status"] == "answered"
    assert len(model.messages) == 1 and retrieval.searches == 1
    assert "Later condition" not in model.messages[0][-1]["content"]
    assert [s["step"] for s in result["trace"]] == ["retrieve", "generate"]


def test_api_opt_in_consumes_both_pages_and_preserves_source_ids(tmp_path):
    api, retrieval, model = client(tmp_path)
    result = api.post("/chat", json={"message": "question", "experimental_pagination": True}).json()
    assert result["status"] == "answered"
    assert retrieval.searches == 1 and len(model.messages) == 3
    prompt = model.messages[-1][-1]["content"]
    assert "First evidence." in prompt and "Later condition." in prompt
    assert {e["citation_id"] for e in result["citations"]} == {"E" + "a" * 32, "E" + "b" * 32}
    assert next(s for s in result["trace"] if s["step"] == "experimental_pagination")["pages"] == 2
    # Toggle off on next request: no extraction calls or sticky global state.
    api.post("/chat", json={"message": "question"})
    assert len(model.messages) == 4


def test_bad_quote_is_explicit_failure_without_partial_final_answer(tmp_path):
    api, retrieval, model = client(tmp_path, True)
    result = api.post("/chat", json={"message": "question", "experimental_pagination": True}).json()
    assert result["status"] == "context_incomplete" and result["citations"] == []
    assert len(model.messages) == 1 and retrieval.searches == 1
    assert result["trace"][1]["status"] == "blocked"


def test_budget_selection_records_omission_without_truncating_units(tmp_path):
    api, retrieval, model = client(tmp_path)
    retrieval.settings = Settings(
        data_dir=tmp_path, chunk_size=100, context_tokens=140, context_chars=140
    )
    # Each full page fits, their combined source headers do not.
    for page in retrieval.pages:
        page["evidence"][0]["content"] = "x" * 60
    result = api.post("/chat", json={"message": "question", "experimental_pagination": True}).json()
    assert result["status"] == "answered"
    packed = next(s for s in result["trace"] if s["step"] == "pack_verified_quotes")
    assert len(packed["omitted_units"]) == 1
    assert packed["omitted_units"][0]["reason"] == "budget"
    assert packed["evidence"][0]["content"] == "x" * 60
    assert len(model.messages) == 3


def test_page_limit_and_oversize_chunks_are_explicit():
    c = Chunk("c", "p", "url", "x" * 200, "infra", locator="url")
    with pytest.raises(PageBudgetError):
        pages_from_chunks([c], len, 100, 100)
    chunks = [Chunk(str(i), "p", "url", "x" * 50, "infra", locator="url") for i in range(13)]
    with pytest.raises(PageBudgetError):
        pages_from_chunks(chunks, len, 120, 120)


def test_page_selection_uses_original_hits_without_filter_leakage(tmp_path):
    retrieval = RetrievalService(Settings(data_dir=tmp_path), context_counter=len)
    a = Chunk("a", "p", "url", "allowed", "ok", locator="url")
    b = Chunk("b", "p", "url", "excluded", "other", locator="url")
    retrieval.chunks = [a, b]
    retrieval._index_parents()
    pages = retrieval.evidence_pages([SimpleNamespace(chunk=a)], domain="ok")
    assert [e["chunk_id"] for p in pages for e in p["evidence"]] == ["a"]


def test_expired_deadline_does_not_call_model():
    model = Model()
    request = RequestModel(model, seconds=-1)
    with pytest.raises(PageBudgetError):
        request.generate([])
    assert not model.messages


def test_final_model_failure_is_recorded_without_partial_answer(tmp_path):
    from infra_rag.assistant import ModelUnavailable

    class FailsAtAnswer(Model):
        def generate(self, messages):
            if "selections" not in messages[0]["content"]:
                self.messages.append(messages)
                raise ModelUnavailable("offline")
            return super().generate(messages)

    retrieval = Retrieval(tmp_path)
    model = FailsAtAnswer()
    assistant = AnswerService(retrieval, model, ConversationStore(tmp_path / "history.sqlite"))
    api = TestClient(create_app(retrieval, assistant))
    result = api.post("/chat", json={"message": "question", "experimental_pagination": True}).json()
    assert result["status"] == "context_incomplete"
    assert result["citations"] == []
    assert len(model.messages) == 3
    assert result["trace"][-1]["status"] == "failed"
