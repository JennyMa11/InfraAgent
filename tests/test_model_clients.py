import io
import json
import urllib.error
from types import SimpleNamespace

import pytest

from infra_rag.assistant import ModelUnavailable
from infra_rag.model_clients import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODEL,
    ENV_KEYS,
    MoerouterClient,
    NoRedirect,
    configured_model,
    model_environment,
)
from infra_rag.offline_evaluation import RecordingModel


def client(**kwargs):
    return MoerouterClient(
        token="unit-test-secret",
        model=DEFAULT_MODEL,
        base_url=DEFAULT_BASE_URL,
        **kwargs,
    )


def test_chat_completions_wire_format_merges_system_and_records_metadata():
    model = client()
    captured = []

    def request(payload):
        captured.append(payload)
        return {
            "id": "req-1",
            "model": DEFAULT_MODEL,
            "usage": {"prompt_tokens": 10, "completion_tokens": 3},
            "choices": [{"finish_reason": "stop", "message": {"content": "OK"}}],
        }

    model._request = request
    messages = [
        {"role": "system", "content": "unchanged RAG instruction"},
        {"role": "user", "content": "question"},
        {"role": "assistant", "content": "previous output"},
        {"role": "user", "content": "existing citation retry"},
    ]
    recorder = RecordingModel(model)
    assert recorder.generate(messages) == "OK"
    payload = captured[0]
    assert payload["model"] == DEFAULT_MODEL
    assert payload["messages"] == [
        {"role": "user", "content": "unchanged RAG instruction\n\nquestion"},
        {"role": "assistant", "content": "previous output"},
        {"role": "user", "content": "existing citation retry"},
    ]
    assert payload["temperature"] == 0 and payload["max_tokens"] == DEFAULT_MAX_TOKENS
    assert "system" not in payload
    assert recorder.calls[0]["provider_response"]["model"] == DEFAULT_MODEL
    assert recorder.calls[0]["provider_response"]["usage"]["prompt_tokens"] == 10
    assert "unit-test-secret" not in json.dumps(recorder.calls + [model.configuration()])


def test_system_prompt_can_remain_a_separate_message():
    model = client(system_in_user=False)
    captured = {}

    def request(payload):
        captured.update(payload)
        return {"choices": [{"finish_reason": "stop", "message": {"content": "OK"}}]}

    model._request = request
    messages = [{"role": "system", "content": "return JSON"}, {"role": "user", "content": "hello"}]
    assert model.generate(messages) == "OK"
    assert captured["messages"] == messages


def test_http_authentication_and_secret_safe_failure():
    model = client()
    seen = []

    def fail(request, timeout):
        seen.append(request)
        raise urllib.error.HTTPError(
            request.full_url, 401, "unit-test-secret", {}, io.BytesIO(b"unit-test-secret")
        )

    model.opener = SimpleNamespace(open=fail)
    with pytest.raises(ModelUnavailable, match="HTTP 401") as caught:
        model.generate([{"role": "user", "content": "hello"}])
    assert "unit-test-secret" not in str(caught.value)
    assert seen[0].full_url == "https://moerouter.com/v1/chat/completions"
    assert seen[0].get_header("Authorization") == "Bearer unit-test-secret"
    assert model.last_call is None
    assert NoRedirect().redirect_request(None, None, 302, "", {}, "https://other.test") is None


@pytest.mark.parametrize(
    "response",
    [
        {},
        {"choices": []},
        {"choices": [None]},
        {"choices": [{"message": {"content": None}}]},
        {"choices": [{"message": {"content": "", "reasoning_content": "thinking"}}]},
        {"choices": [{"message": {"content": "OK", "tool_calls": [{}]}}]},
    ],
)
def test_chat_completion_rejects_missing_text_and_tools(response):
    model = client()
    model._request = lambda payload: response
    with pytest.raises(ModelUnavailable):
        model.generate([{"role": "user", "content": "hello"}])


def test_env_precedence_and_literal_values(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("INFRA_RAG_LLM_ENV_FILE", raising=False)
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    (tmp_path / ".env.llm").write_text(
        "OPENAI_API_KEY='$(touch NEVER_EXECUTE)'\n"
        "OPENAI_BASE_URL=https://moerouter.com/v1\n"
        f"OPENAI_MODEL={DEFAULT_MODEL}\n"
        f"OPENAI_MAX_TOKENS={DEFAULT_MAX_TOKENS}\n"
        "OPENAI_SYSTEM_IN_USER=1\n"
    )
    (tmp_path / ".env.moerouter").write_text(
        "OPENAI_API_KEY=other-secret\nOPENAI_MODEL=other-model\n"
    )
    assert model_environment()["OPENAI_API_KEY"] == "$(touch NEVER_EXECUTE)"
    assert not (tmp_path / "NEVER_EXECUTE").exists()
    model = configured_model()
    assert isinstance(model, MoerouterClient)
    assert model.model == DEFAULT_MODEL
    assert model.endpoint == "https://moerouter.com/v1/chat/completions"
    assert model.max_tokens == DEFAULT_MAX_TOKENS
    assert model.system_in_user is True
    monkeypatch.setenv("INFRA_RAG_LLM_ENV_FILE", ".env.moerouter")
    assert configured_model().model == "other-model"
    monkeypatch.setenv("OPENAI_MODEL", "explicit-model")
    assert configured_model().model == "explicit-model"


def test_missing_key_fails_without_any_request(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("INFRA_RAG_LLM_ENV_FILE", raising=False)
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(ModelUnavailable, match="Key is missing"):
        MoerouterClient.from_environment(path=tmp_path / "missing")


def test_preload_does_not_charge_full_answer_budget():
    model = client()
    payloads = []
    model._request = lambda payload: (
        payloads.append(payload)
        or {"choices": [{"finish_reason": "stop", "message": {"content": "OK"}}]}
    )
    model.preload()
    assert payloads[0]["max_tokens"] == 8


def test_defaults_and_configuration_redaction():
    model = MoerouterClient(token="unit-test-secret")
    assert model.model == DEFAULT_MODEL
    assert model.base_url == DEFAULT_BASE_URL
    assert model.max_tokens == DEFAULT_MAX_TOKENS
    assert model.configuration()["provider"] == "moerouter"
    assert "unit-test-secret" not in json.dumps(model.configuration())


@pytest.mark.parametrize(
    "base_url",
    [
        "http://moerouter.com/v1",
        "https://user:pass@moerouter.com/v1",
        "https://moerouter.com/v1?debug=1",
    ],
)
def test_base_url_validation_rejects_unsafe_forms(base_url):
    with pytest.raises(ValueError):
        MoerouterClient(token="unit-test-secret", base_url=base_url)
