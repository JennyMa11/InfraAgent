import io
import json
import urllib.error
from types import SimpleNamespace

import pytest

from infra_rag.assistant import ModelUnavailable, OllamaClient
from infra_rag.model_clients import (
    AnthropicClient,
    NoRedirect,
    OpenAICompatibleClient,
    configured_model,
    model_environment,
)
from infra_rag.offline_evaluation import RecordingModel


def client(**kwargs):
    return AnthropicClient(
        token="unit-test-secret",
        model="deepseek-v4-flash",
        base_url="https://example.test",
        **kwargs,
    )


def test_anthropic_wire_format_preserves_system_and_history_without_sending_ollama_options():
    model = client()
    captured = []

    def request(payload):
        captured.append(payload)
        return {
            "model": "routed-model",
            "usage": {"input_tokens": 10, "output_tokens": 3},
            "content": [
                {"type": "thinking", "thinking": "ignored"},
                {"type": "text", "text": '{"supported":false,"answer":"不足","citations":[]}'},
            ],
        }

    model._request = request
    messages = [
        {"role": "system", "content": "unchanged RAG instruction"},
        {"role": "user", "content": "question"},
        {"role": "assistant", "content": "previous output"},
        {"role": "user", "content": "existing citation retry"},
    ]
    recorder = RecordingModel(model)
    assert json.loads(recorder.generate(messages))["supported"] is False
    payload = captured[0]
    assert payload["system"] == messages[0]["content"]
    assert payload["messages"] == messages[1:]
    assert payload["temperature"] == 0 and payload["max_tokens"] == 650
    assert "think" not in payload and "format" not in payload
    assert recorder.calls[0]["provider_response"]["model"] == "routed-model"
    assert recorder.calls[0]["provider_response"]["usage"]["input_tokens"] == 10
    assert "unit-test-secret" not in json.dumps(recorder.calls + [model.configuration()])


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
    assert seen[0].full_url == "https://example.test/v1/messages"
    assert seen[0].get_header("Authorization") == "Bearer unit-test-secret"
    assert seen[0].get_header("Anthropic-version") == "2023-06-01"
    assert model.last_call is None
    assert NoRedirect().redirect_request(None, None, 302, "", {}, "https://other.test") is None


@pytest.mark.parametrize("content", [[], "invalid", ["invalid"], [{"type": "tool_use"}]])
def test_rejects_empty_or_unsupported_api_content(content):
    model = client()
    model._request = lambda payload: {"content": content}
    with pytest.raises(ModelUnavailable):
        model.generate([{"role": "user", "content": "question"}])


def test_env_switch_and_literal_configuration(tmp_path, monkeypatch):
    for name in (
        "ANTHROPIC_AUTH_TOKEN",
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_BASE_URL",
        "ANTHROPIC_MODEL",
        "INFRA_RAG_LLM_PROVIDER",
    ):
        monkeypatch.delenv(name, raising=False)
    path = tmp_path / ".env"
    path.write_text(
        "# local remains available\nINFRA_RAG_LLM_PROVIDER=ollama\n"
        "ANTHROPIC_AUTH_TOKEN='$(touch NEVER_EXECUTE)'\n"
        "ANTHROPIC_MODEL=deepseek-v4-flash\n"
        "ANTHROPIC_BASE_URL=https://example.test/v1\n"
    )
    monkeypatch.setenv("INFRA_RAG_LLM_ENV_FILE", str(path))
    assert model_environment()["ANTHROPIC_AUTH_TOKEN"] == "$(touch NEVER_EXECUTE)"
    assert isinstance(configured_model(), OllamaClient)
    monkeypatch.setenv("INFRA_RAG_LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "unit-test-secret")
    model = configured_model()
    assert isinstance(model, AnthropicClient)
    assert model.endpoint == "https://example.test/v1/messages"
    assert not (tmp_path / "NEVER_EXECUTE").exists()


def test_missing_key_fails_without_any_request(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ModelUnavailable, match="Key is missing"):
        AnthropicClient.from_environment(path=tmp_path / "missing")


def test_preload_does_not_charge_full_answer_budget():
    model = client()
    payloads = []
    model._request = lambda p: payloads.append(p) or {"content": [{"type": "text", "text": "OK"}]}
    model.preload()
    assert payloads[0]["max_tokens"] == 8


def test_deepseek_native_authentication_and_disabled_thinking():
    model = AnthropicClient(
        token="unit-test-secret",
        model="deepseek-flash",
        base_url="https://api.deepseek.com/anthropic",
    )
    seen = []

    def respond(request, timeout):
        seen.append(request)
        return io.BytesIO(b'{"content":[{"type":"text","text":"OK"}]}')

    model.opener = SimpleNamespace(open=respond)
    model.preload()
    assert seen[0].full_url == "https://api.deepseek.com/anthropic/v1/messages"
    assert seen[0].get_header("X-api-key") == "unit-test-secret"
    assert seen[0].get_header("Authorization") is None
    assert json.loads(seen[0].data)["thinking"] == {"type": "disabled"}
    assert model.configuration()["options"]["thinking"] == {"type": "disabled"}


def test_default_prefers_separate_deepseek_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("INFRA_RAG_LLM_ENV_FILE", raising=False)
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)
    (tmp_path / ".env.agentrouter").write_text("ANTHROPIC_MODEL=old-route\n")
    (tmp_path / ".env.deepseek").write_text("ANTHROPIC_MODEL=deepseek-flash\n")
    assert model_environment()["ANTHROPIC_MODEL"] == "deepseek-flash"


def test_aihubmix_wire_format_authentication_and_metadata():
    model = OpenAICompatibleClient(
        token="unit-test-secret",
        model="hy3-free",
        base_url="https://aihubmix.com/v1",
        max_tokens=1024,
    )
    seen = []
    response = {
        "model": "hy3-free",
        "usage": {"prompt_tokens": 4, "completion_tokens": 2},
        "choices": [{"finish_reason": "stop", "message": {"content": "OK"}}],
    }

    def respond(request, timeout):
        seen.append(request)
        return io.BytesIO(json.dumps(response).encode())

    model.opener = SimpleNamespace(open=respond)
    messages = [{"role": "system", "content": "same prompt"}, {"role": "user", "content": "hello"}]
    recorder = RecordingModel(model)
    assert recorder.generate(messages) == "OK"
    assert seen[0].full_url == "https://aihubmix.com/v1/chat/completions"
    assert seen[0].get_header("Authorization") == "Bearer unit-test-secret"
    assert seen[0].get_header("Anthropic-version") is None
    payload = json.loads(seen[0].data)
    assert payload["messages"] == messages
    assert payload["max_tokens"] == 1024 and payload["stream"] is False
    assert "thinking" not in payload
    assert recorder.calls[0]["provider_response"]["stop_reason"] == "stop"
    assert model.configuration()["provider"] == "openai-compatible"


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
    model = OpenAICompatibleClient(
        token="unit-test-secret",
        model="hy3-free",
        base_url="https://example.test/v1",
    )
    model._request = lambda payload: response
    with pytest.raises(ModelUnavailable):
        model.generate([{"role": "user", "content": "hello"}])


def test_aihubmix_default_selection_and_switch_back(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for name in (
        "INFRA_RAG_LLM_ENV_FILE",
        "INFRA_RAG_LLM_PROVIDER",
        "AIHUBMIX_MODEL",
        "AIHUBMIX_API_KEY",
        "AIHUBMIX_MAX_TOKENS",
        "AIHUBMIX_BASE_URL",
    ):
        monkeypatch.delenv(name, raising=False)
    (tmp_path / ".env.deepseek").write_text("INFRA_RAG_LLM_PROVIDER=ollama\n")
    (tmp_path / ".env.aihubmix").write_text(
        "INFRA_RAG_LLM_PROVIDER=openai\nAIHUBMIX_API_KEY=unit-test-secret\n"
        "AIHUBMIX_MODEL=hy3-free\nAIHUBMIX_MAX_TOKENS=1024\n"
    )
    model = configured_model()
    assert isinstance(model, OpenAICompatibleClient)
    assert model.model == "hy3-free" and model.max_tokens == 1024
    monkeypatch.setenv("INFRA_RAG_LLM_ENV_FILE", ".env.deepseek")
    assert isinstance(configured_model(), OllamaClient)


def test_agentrouter_openai_config_uses_its_own_key_and_endpoint(tmp_path, monkeypatch):
    from infra_rag.model_clients import ENV_KEYS

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("INFRA_RAG_LLM_ENV_FILE", raising=False)
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    (tmp_path / ".env.aihubmix").write_text(
        "INFRA_RAG_LLM_PROVIDER=openai\nAIHUBMIX_API_KEY=other-provider-key\n"
    )
    path = tmp_path / ".env.agentrouter.openai"
    path.write_text(
        "INFRA_RAG_LLM_PROVIDER=openai\nOPENAI_API_KEY=router-test-key\n"
        "OPENAI_BASE_URL=https://agentrouter.org/v1\nOPENAI_MODEL=deepseek-v4-flash\n"
        "OPENAI_MAX_TOKENS=1024\n"
    )
    model = configured_model()
    assert model._token == "router-test-key"
    assert model.endpoint == "https://agentrouter.org/v1/chat/completions"
    assert model.model == "deepseek-v4-flash" and model.max_tokens == 1024
    monkeypatch.setenv("OPENAI_MODEL", "explicit-model")
    assert configured_model().model == "explicit-model"
    assert "router-test-key" not in json.dumps(model.configuration())


def test_aliyun_config_takes_precedence_and_preserves_compatible_mode_path(tmp_path, monkeypatch):
    from infra_rag.model_clients import ENV_KEYS

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("INFRA_RAG_LLM_ENV_FILE", raising=False)
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    (tmp_path / ".env.agentrouter.openai").write_text("INFRA_RAG_LLM_PROVIDER=ollama\n")
    (tmp_path / ".env.aliyun").write_text(
        "INFRA_RAG_LLM_PROVIDER=openai\nOPENAI_API_KEY=aliyun-test-key\n"
        "OPENAI_BASE_URL=https://workspace.cn-beijing.maas.aliyuncs.com/compatible-mode/v1\n"
        "OPENAI_MODEL=deepseek-v4-flash\nOPENAI_MAX_TOKENS=1024\n"
    )
    model = configured_model()
    assert model.model == "deepseek-v4-flash"
    assert model.endpoint == (
        "https://workspace.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions"
    )
    assert model._token == "aliyun-test-key"
    monkeypatch.setenv("INFRA_RAG_LLM_ENV_FILE", ".env.agentrouter.openai")
    assert isinstance(configured_model(), OllamaClient)


@pytest.mark.parametrize(
    ("base_url", "expected_token"),
    [
        ("https://workspace.cn-beijing.maas.aliyuncs.com/compatible-mode/v1", "dashscope-key"),
        ("https://agentrouter.org/v1", "other-provider-key"),
    ],
)
def test_dashscope_key_is_used_only_for_aliyun_hosts(
    tmp_path, monkeypatch, base_url, expected_token
):
    from infra_rag.model_clients import ENV_KEYS

    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    path = tmp_path / ".env.aliyun"
    path.write_text(
        "DASHSCOPE_API_KEY=dashscope-key\nOPENAI_API_KEY=other-provider-key\n"
        "OPENAI_MODEL=qwen3.7-flash-2026-07-15\n"
    )
    model = OpenAICompatibleClient.from_environment(path=path, base_url=base_url)
    assert model._token == expected_token
    assert model.model == "qwen3.7-flash-2026-07-15"


def test_active_configuration_overrides_old_provider_files(tmp_path, monkeypatch):
    from infra_rag.model_clients import ENV_KEYS

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("INFRA_RAG_LLM_ENV_FILE", raising=False)
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    (tmp_path / ".env.aliyun").write_text("INFRA_RAG_LLM_PROVIDER=ollama\n")
    (tmp_path / ".env.llm").write_text(
        "INFRA_RAG_LLM_PROVIDER=anthropic\nANTHROPIC_MODEL=deepseek-flash\n"
        "ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic\n"
        "ANTHROPIC_AUTH_TOKEN=deepseek-test-key\n"
    )
    model = configured_model()
    assert isinstance(model, AnthropicClient)
    assert model.model == "deepseek-flash" and model._token == "deepseek-test-key"
    monkeypatch.setenv("INFRA_RAG_LLM_ENV_FILE", ".env.aliyun")
    assert isinstance(configured_model(), OllamaClient)
