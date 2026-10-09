"""Verify Aliyun using the official OpenAI SDK without displaying credentials.

Run: uv run --with openai python scripts/verify_aliyun_api.py
Add --legacy to diagnose the documented Beijing legacy endpoint.
"""

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

from infra_rag.model_clients import model_environment


def main():
    from openai import APIStatusError, OpenAI

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=Path(".env.aliyun"))
    parser.add_argument("--legacy", action="store_true")
    args = parser.parse_args()
    env = model_environment(args.env_file)
    token = env.get("DASHSCOPE_API_KEY") or env.get("OPENAI_API_KEY")
    if not token:
        raise SystemExit("DASHSCOPE_API_KEY is missing")
    base_url = (
        "https://dashscope.aliyuncs.com/compatible-mode/v1"
        if args.legacy
        else env.get("OPENAI_BASE_URL", "")
    )
    parsed = urlsplit(base_url)
    hostname = parsed.hostname or ""
    if (
        parsed.scheme != "https"
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or not (hostname.endswith(".maas.aliyuncs.com") or hostname == "dashscope.aliyuncs.com")
    ):
        raise SystemExit("Use the configured HTTPS Aliyun endpoint")
    model = env.get("OPENAI_MODEL")
    if not model:
        raise SystemExit("OPENAI_MODEL is missing")
    client = OpenAI(api_key=token, base_url=base_url, max_retries=0, timeout=30)
    record = {"base_url": base_url, "requested_model": model, "sdk": "OpenAI"}
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Reply only OK."}],
            max_completion_tokens=32,
            extra_body={"enable_thinking": False},
            stream=False,
        )
        record.update(
            success=True,
            model=response.model,
            answer=response.choices[0].message.content,
            finish_reason=response.choices[0].finish_reason,
            usage=response.usage.model_dump() if response.usage else None,
        )
    except APIStatusError as exc:
        body = exc.body if isinstance(exc.body, dict) else {}
        error = body.get("error", body)
        if not isinstance(error, dict):
            error = {}
        record.update(
            success=False,
            http_status=exc.status_code,
            error={key: error.get(key) for key in ("code", "type", "message", "id")},
        )
    except Exception as exc:
        record.update(success=False, error_type=type(exc).__name__)
    print(json.dumps(record, ensure_ascii=False).replace(token, "[redacted]"))
    return 0 if record["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
