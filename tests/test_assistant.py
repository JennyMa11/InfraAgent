import json
import re

from fastapi.testclient import TestClient

from infra_rag.api import create_app
from infra_rag.assistant import AnswerService, ModelUnavailable
from infra_rag.config import Settings
from infra_rag.service import RetrievalService


class FakeModel:
    model = "fake-local"

    def __init__(self, invalid_first=False):
        self.messages = []
        self.invalid_first = invalid_first
        self.preloads = 0

    def preload(self):
        self.preloads += 1

    def generate(self, messages):
        self.messages.append(messages)
        if self.invalid_first and len(self.messages) == 1:
            return json.dumps(
                {
                    "supported": True,
                    "answer": "无效引用",
                    "citations": ["E000000000000000000000000"],
                }
            )
        citation = next(
            (
                match
                for message in messages
                if (match := re.search(r"\[(E[a-f0-9]{24})\]", message["content"]))
            ),
            None,
        )
        return json.dumps(
            {"supported": True, "answer": "分页减少碎片。", "citations": [citation.group(1)]}
        )


def make_client(tmp_path, model):
    service = RetrievalService(Settings(data_dir=tmp_path / "index", chunk_size=100))
    document = tmp_path / "notes.md"
    document.write_text("# PagedAttention\n\nPagedAttention 用分页管理 KV Cache，减少显存碎片。")
    service.ingest(document, "inference")
    assistant = AnswerService(service, model=model)
    return TestClient(create_app(service, assistant)), service


def test_chat_returns_grounded_answer_and_persists_follow_up(tmp_path):
    model = FakeModel()
    client, service = make_client(tmp_path, model)
    with client:
        assert client.post("/warmup").json()["ready"] is True
        assert model.preloads == 1
        first = client.post("/chat", json={"message": "PagedAttention 有什么作用？"})
        assert first.status_code == 200
        result = first.json()
        assert result["status"] == "answered"
        assert result["citations"][0]["source"].endswith("notes.md")
        assert result["citations"][0]["citation_id"] in result["answer"]
        assert [step["step"] for step in result["trace"]] == ["retrieve", "generate"]
        second = client.post(
            "/chat",
            json={"message": "它为什么减少碎片？", "conversation_id": result["conversation_id"]},
        )
        assert second.status_code == 200
        assert second.json()["trace"][0]["query"].startswith("PagedAttention 有什么作用？")
        assert len(model.messages[1]) >= 4  # system, previous exchange, current evidence
        history = client.get(f"/conversations/{result['conversation_id']}").json()
        assert [turn["role"] for turn in history["turns"]] == [
            "user",
            "assistant",
            "user",
            "assistant",
        ]
        assert history["turns"][1]["citations"] == result["citations"]
    restored = AnswerService(service, model=model)
    assert len(restored.conversation(result["conversation_id"])["turns"]) == 4


def test_chat_retries_unknown_citation_and_refuses_without_evidence(tmp_path):
    model = FakeModel(invalid_first=True)
    client, _ = make_client(tmp_path, model)
    with client:
        result = client.post("/chat", json={"message": "PagedAttention 是什么？"}).json()
        assert result["status"] == "answered"
        assert len(model.messages) == 2
        missing = client.post(
            "/chat", json={"message": "PagedAttention 是什么？", "domain": "not-in-index"}
        ).json()
        assert missing["status"] == "no_evidence"
        assert missing["citations"] == []
        assert len(model.messages) == 2


def test_default_api_uses_existing_answer_service(tmp_path, monkeypatch):
    from infra_rag import agent, model_clients

    model = FakeModel()
    _, service = make_client(tmp_path, model)
    monkeypatch.setattr(model_clients, "configured_model", lambda: model)

    def unexpected(*args, **kwargs):
        raise AssertionError("Default API must not initialize the retired research Agent")

    monkeypatch.setattr(agent.ResearchAgent, "__init__", unexpected)
    with TestClient(create_app(service)) as client:
        response = client.post("/chat", json={"message": "PagedAttention 有什么作用？"})
    assert response.status_code == 200
    assert response.json()["status"] == "answered"
    assert [step["step"] for step in response.json()["trace"]] == ["retrieve", "generate"]
    assert len(model.messages) == 1
    assert response.json()["citations"][0]["source"].endswith("notes.md")


def test_chat_validation_and_model_failure(tmp_path):
    class BrokenModel:
        model = "broken"

        def generate(self, messages):
            raise ModelUnavailable("model offline")

    client, _ = make_client(tmp_path, BrokenModel())
    with client:
        assert client.post("/chat", json={"message": "   "}).status_code == 422
        assert (
            client.post("/chat", json={"message": "KV Cache", "conversation_id": "bad"}).status_code
            == 422
        )
        assert client.post("/chat", json={"message": "PagedAttention"}).status_code == 503
        assert client.get("/conversations/00000000-0000-0000-0000-000000000000").status_code == 404


def test_chat_normalizes_term_for_retrieval_but_keeps_original_question(tmp_path, monkeypatch):
    model = FakeModel()
    client, service = make_client(tmp_path, model)
    queries = []
    search = service.search

    def observed(query, **kwargs):
        queries.append(query)
        return search(query, **kwargs)

    monkeypatch.setattr(service, "search", observed)
    question = "Page Attention是什么"
    with client:
        result = client.post("/chat", json={"message": question}).json()
        assert result["status"] == "answered"
        assert queries == ["PagedAttention是什么"]
        assert [s["step"] for s in result["trace"]] == ["query_normalize", "retrieve", "generate"]
        assert result["trace"][0]["original_query"] == question
        assert f"当前问题：{question}" in model.messages[0][-1]["content"]
        assert "检索术语规范化" in model.messages[0][-1]["content"]
        history = client.get(f"/conversations/{result['conversation_id']}").json()
        assert history["turns"][0]["content"] == question
        assert len(model.messages) == 1


def test_term_alias_does_not_bypass_missing_evidence_or_invalid_citations(tmp_path):
    class InvalidCitationModel(FakeModel):
        def generate(self, messages):
            self.messages.append(messages)
            return json.dumps({"supported": True, "answer": "无效引用", "citations": ["Ebad"]})

    model = InvalidCitationModel()
    client, _ = make_client(tmp_path, model)
    with client:
        missing = client.post(
            "/chat",
            json={
                "message": "Page Attention是什么",
                "domain": "not-in-index",
            },
        ).json()
        assert missing["status"] == "no_evidence" and missing["citations"] == []
        assert not model.messages
        invalid = client.post("/chat", json={"message": "Page Attention是什么"}).json()
        assert invalid["status"] == "no_evidence" and invalid["citations"] == []
        assert len(model.messages) == 2
