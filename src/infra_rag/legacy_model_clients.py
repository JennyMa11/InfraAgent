"""Legacy experiment transports retained for archived scripts.

The application answer chain uses MoerouterClient in model_clients.py only.
These clients are kept so historical scripts still import; they are not selected
by configured_model() and require their original local configuration to run.
"""

import json
import os
import shlex
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

from .assistant import ModelUnavailable

ENV_KEYS = {
    "INFRA_RAG_QUERY_LANGUAGE",
    "INFRA_RAG_LLM_PROVIDER",
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_MODEL",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_API_KEY",
    "AIHUBMIX_API_KEY",
    "AIHUBMIX_BASE_URL",
    "AIHUBMIX_MODEL",
    "AIHUBMIX_MAX_TOKENS",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "OPENAI_MODEL",
    "OPENAI_MAX_TOKENS",
    "OPENAI_SYSTEM_IN_USER",
    "DASHSCOPE_API_KEY",
}


def model_environment(path=None):
    """Read literal assignments without executing shell code; environment takes precedence."""
    default = next(
        (
            name
            for name in (
                ".env.llm",
                ".env.aliyun",
                ".env.agentrouter.openai",
                ".env.aihubmix",
                ".env.deepseek",
            )
            if Path(name).exists()
        ),
        ".env.agentrouter",
    )
    path = Path(path or os.environ.get("INFRA_RAG_LLM_ENV_FILE", default))
    values = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip().removeprefix("export ")
            if not line or line.startswith("#"):
                continue
            key, separator, value = line.partition("=")
            if separator and key.strip() in ENV_KEYS:
                parts = shlex.split(value, comments=True)
                if len(parts) > 1:
                    raise ValueError("Quote configuration values containing spaces")
                values[key.strip()] = parts[0] if parts else ""
    values.update({key: os.environ[key] for key in ENV_KEYS if key in os.environ})
    return values


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class OllamaClient:
    def __init__(self, model="qwen3:4b", base_url="http://127.0.0.1:11434", timeout=180):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.keep_alive = "10m"
        self.num_ctx = 8192

    def preload(self):
        self._request(
            {
                "model": self.model,
                "keep_alive": self.keep_alive,
                "options": {"num_ctx": self.num_ctx},
            }
        )

    def generate(self, messages):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "think": False,
            "format": "json",
            "keep_alive": self.keep_alive,
            "options": {"temperature": 0, "num_predict": 650, "num_ctx": self.num_ctx},
        }
        result = self._request(payload)
        content = result.get("message", {}).get("content", "")
        if not content:
            raise ModelUnavailable("Ollama 没有返回回答，请检查模型是否已安装。")
        return content

    def _request(self, payload):
        request = urllib.request.Request(
            self.base_url + "/api/chat",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                result = json.load(response)
        except (OSError, ValueError, urllib.error.HTTPError) as exc:
            raise ModelUnavailable(f"Ollama 不可用：{exc}") from exc
        return result


class AnthropicClient:
    provider = "anthropic-compatible"

    def __init__(self, *, token, model, base_url, max_tokens=650, timeout=180):
        if not token or "替换" in token or token == "YOUR_API_KEY":
            raise ModelUnavailable("Model API Key is missing")
        parsed = urlsplit(base_url)
        if (
            parsed.scheme not in {"https", "http"}
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
            or (parsed.scheme == "http" and parsed.hostname not in {"localhost", "127.0.0.1"})
        ):
            raise ValueError("Use an HTTPS API base URL without credentials, query or fragment")
        if not model.strip() or max_tokens < 1:
            raise ValueError("Model name and positive output token limit are required")
        self._token = token
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.deepseek = parsed.hostname == "api.deepseek.com"
        self.endpoint = self.base_url + (
            "/messages" if self.base_url.endswith("/v1") else "/v1/messages"
        )
        self.max_tokens, self.timeout = max_tokens, timeout
        self.last_call = None
        self.opener = urllib.request.build_opener(NoRedirect())

    @classmethod
    def from_environment(cls, *, path=None, model=None, base_url=None, max_tokens=650):
        env = model_environment(path)
        return cls(
            token=env.get("ANTHROPIC_AUTH_TOKEN") or env.get("ANTHROPIC_API_KEY", ""),
            model=model or env.get("ANTHROPIC_MODEL", "deepseek-v4-flash"),
            base_url=base_url or env.get("ANTHROPIC_BASE_URL", "https://agentrouter.org"),
            max_tokens=max_tokens,
        )

    def configuration(self):
        return {
            "provider": self.provider,
            "base_url": self.base_url,
            "model": self.model,
            "options": {
                "temperature": 0,
                "max_tokens": self.max_tokens,
                **({"thinking": {"type": "disabled"}} if self.deepseek else {}),
            },
            "authentication": "x-api-key" if self.deepseek else "bearer",
            "api_version": "2023-06-01",
            "format": "JSON requested by unchanged system prompt; no transport JSON constraint",
        }

    def _request(self, payload):
        request = urllib.request.Request(
            self.endpoint,
            method="POST",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                **(
                    {"x-api-key": self._token}
                    if self.deepseek
                    else {"Authorization": "Bearer " + self._token}
                ),
                **(
                    {"anthropic-version": "2023-06-01"}
                    if self.provider == "anthropic-compatible"
                    else {}
                ),
                "User-Agent": "infra-rag/0.2",
            },
        )
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                result = json.load(response)
        except urllib.error.HTTPError as exc:
            # Untrusted upstream error bodies can echo credentials. Never persist them.
            raise ModelUnavailable(
                f"Model API HTTP {exc.code}; check route, access and quota"
            ) from None
        except (OSError, ValueError):
            raise ModelUnavailable("Model API connection or JSON response failed") from None
        return result

    def _generate(self, messages, max_tokens):
        self.last_call = None
        system, conversation = [], []
        for message in messages:
            if message["role"] == "system":
                system.append(message["content"])
            elif message["role"] in {"user", "assistant"}:
                conversation.append(dict(message))
            else:
                raise ValueError("Only text system/user/assistant messages are supported")
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": 0,
            "stream": False,
            "messages": conversation,
        }
        if system:
            payload["system"] = "\n\n".join(system)
        if self.deepseek:
            payload["thinking"] = {"type": "disabled"}
        result = self._request(payload)
        if not isinstance(result, dict):
            raise ModelUnavailable("Model API returned an invalid message")
        self.last_call = {key: result.get(key) for key in ("id", "model", "stop_reason", "usage")}
        # Metadata is diagnostic data, not a verified identity of underlying weights.
        self.last_call = json.loads(json.dumps(self.last_call).replace(self._token, "[redacted]"))
        blocks = result.get("content", [])
        if not isinstance(blocks, list) or any(
            not isinstance(b, dict)
            or b.get("type") == "tool_use"
            or (b.get("type") == "text" and not isinstance(b.get("text"), str))
            for b in blocks
        ):
            raise ModelUnavailable("Model API returned unsupported content blocks")
        content = "\n".join(b["text"] for b in blocks if b.get("type") == "text")
        if not content.strip():
            raise ModelUnavailable("Model API returned no answer text")
        return content

    def generate(self, messages):
        return self._generate(messages, self.max_tokens)

    def preload(self):
        self._generate([{"role": "user", "content": "Reply only OK."}], 8)


class OpenAICompatibleClient(AnthropicClient):
    """Chat Completions wire format, using the existing secret-safe HTTP transport."""

    provider = "openai-compatible"

    def __init__(self, **kwargs):
        self.system_in_user = kwargs.pop("system_in_user", False)
        super().__init__(**kwargs)
        self.deepseek = False
        self.endpoint = self.base_url + (
            "/chat/completions" if self.base_url.endswith("/v1") else "/v1/chat/completions"
        )

    @classmethod
    def from_environment(
        cls, *, path=None, model=None, base_url=None, max_tokens=None, system_in_user=None
    ):
        env = model_environment(path)
        base_url = (
            base_url
            or env.get("OPENAI_BASE_URL")
            or env.get("AIHUBMIX_BASE_URL", "https://aihubmix.com/v1")
        )
        token = env.get("OPENAI_API_KEY") or env.get("AIHUBMIX_API_KEY", "")
        hostname = urlsplit(base_url).hostname or ""
        if hostname.endswith(".maas.aliyuncs.com") or hostname in {
            "dashscope.aliyuncs.com",
            "dashscope-intl.aliyuncs.com",
            "dashscope-us.aliyuncs.com",
        }:
            token = env.get("DASHSCOPE_API_KEY") or token
        if system_in_user is None:
            system_in_user = env.get("OPENAI_SYSTEM_IN_USER", "").lower() in {
                "1",
                "true",
                "yes",
            }
        return cls(
            token=token,
            model=model or env.get("OPENAI_MODEL") or env.get("AIHUBMIX_MODEL", "hy3-free"),
            base_url=base_url,
            max_tokens=max_tokens
            if max_tokens is not None
            else int(env.get("OPENAI_MAX_TOKENS") or env.get("AIHUBMIX_MAX_TOKENS", "1024")),
            system_in_user=system_in_user,
        )

    def configuration(self):
        return {
            "provider": self.provider,
            "base_url": self.base_url,
            "model": self.model,
            "options": {
                "temperature": 0,
                "max_tokens": self.max_tokens,
                "system_in_user": self.system_in_user,
            },
            "authentication": "bearer",
            "format": "JSON requested by unchanged system prompt; no transport JSON constraint",
        }

    def _generate(self, messages, max_tokens):
        self.last_call = None
        if any(
            m.get("role") not in {"system", "user", "assistant"}
            or not isinstance(m.get("content"), str)
            for m in messages
        ):
            raise ValueError("Only text system/user/assistant messages are supported")
        if self.system_in_user:
            instructions = [m["content"] for m in messages if m["role"] == "system"]
            messages = [m for m in messages if m["role"] != "system"]
            if instructions:
                prefix = "\n\n".join(instructions)
                if messages and messages[0]["role"] == "user":
                    messages = [
                        {**messages[0], "content": prefix + "\n\n" + messages[0]["content"]},
                        *messages[1:],
                    ]
                else:
                    messages = [{"role": "user", "content": prefix}, *messages]
        result = self._request(
            {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0,
                "stream": False,
            }
        )
        if not isinstance(result, dict):
            raise ModelUnavailable("Model API returned an invalid message")
        choices = result.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise ModelUnavailable("Model API returned no completion choices")
        choice = choices[0]
        self.last_call = {
            "id": result.get("id"),
            "model": result.get("model"),
            "usage": result.get("usage"),
            "stop_reason": choice.get("finish_reason"),
        }
        self.last_call = json.loads(json.dumps(self.last_call).replace(self._token, "[redacted]"))
        message = choice.get("message")
        if not isinstance(message, dict) or message.get("tool_calls"):
            raise ModelUnavailable("Model API returned unsupported content blocks")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ModelUnavailable("Model API returned no answer text")
        return content

    def preload(self):
        self._generate([{"role": "user", "content": "Reply only OK."}], self.max_tokens)
