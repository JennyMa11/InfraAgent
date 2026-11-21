"""Moerouter OpenAI-compatible transport and project-local credential configuration."""

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
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "OPENAI_MODEL",
    "OPENAI_MAX_TOKENS",
    "OPENAI_SYSTEM_IN_USER",
}
DEFAULT_BASE_URL = "https://moerouter.com/v1"
DEFAULT_MODEL = "glm-5.3-flash"
DEFAULT_MAX_TOKENS = 2048


def model_environment(path=None):
    """Read literal assignments without executing shell code; environment takes precedence."""
    default = next(
        (name for name in (".env.llm", ".env.moerouter") if Path(name).exists()),
        ".env.llm",
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


class MoerouterClient:
    """OpenAI Chat Completions client fixed to the project's moerouter entry."""

    provider = "moerouter"

    def __init__(
        self,
        *,
        token,
        model=DEFAULT_MODEL,
        base_url=DEFAULT_BASE_URL,
        max_tokens=DEFAULT_MAX_TOKENS,
        timeout=180,
        system_in_user=True,
        disable_thinking=False,
    ):
        if not token or "替换" in token or token == "YOUR_API_KEY":
            raise ModelUnavailable("Moerouter API Key is missing")
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
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.system_in_user = system_in_user
        self.disable_thinking = disable_thinking
        self.endpoint = self.base_url + (
            "/chat/completions" if self.base_url.endswith("/v1") else "/v1/chat/completions"
        )
        self.last_call = None
        self.opener = urllib.request.build_opener(NoRedirect())

    @classmethod
    def from_environment(
        cls, *, path=None, model=None, base_url=None, max_tokens=None, system_in_user=None
    ):
        env = model_environment(path)
        if system_in_user is None:
            system_in_user = env.get("OPENAI_SYSTEM_IN_USER", "1").lower() in {
                "1",
                "true",
                "yes",
            }
        return cls(
            token=env.get("OPENAI_API_KEY", ""),
            model=model or env.get("OPENAI_MODEL", DEFAULT_MODEL),
            base_url=base_url or env.get("OPENAI_BASE_URL", DEFAULT_BASE_URL),
            max_tokens=max_tokens
            if max_tokens is not None
            else int(env.get("OPENAI_MAX_TOKENS", DEFAULT_MAX_TOKENS)),
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
                "disable_thinking": self.disable_thinking,
            },
            "authentication": "bearer",
            "format": "JSON requested by unchanged system prompt; no transport JSON constraint",
        }

    def _request(self, payload):
        request = urllib.request.Request(
            self.endpoint,
            method="POST",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self._token,
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
                **({"thinking": {"type": "disabled"}} if self.disable_thinking else {}),
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

    def generate(self, messages):
        return self._generate(messages, self.max_tokens)

    def preload(self):
        self._generate([{"role": "user", "content": "Reply only OK."}], 8)


def configured_model(path=None):
    """Construct the one model configuration shared by native and experimental chains."""
    return MoerouterClient.from_environment(path=path)
