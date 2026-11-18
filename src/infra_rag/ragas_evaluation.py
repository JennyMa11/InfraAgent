"""Optional Ragas scoring of frozen, delivered text; never a task-success judge."""

import asyncio
import hashlib
import importlib.metadata
import inspect
import json
import math
import statistics
from pathlib import Path
from time import perf_counter

METRICS = ("context_precision", "context_recall", "faithfulness", "response_relevancy")


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()
    ).hexdigest()


def measurement(values, total):
    measured = [v for v in values if v is not None]
    return {
        "numerator": sum(measured),
        "denominator": len(measured),
        "value": statistics.mean(measured) if measured else None,
        "coverage": len(measured) / total if total else None,
    }


def validate_cases(cases):
    if not cases:
        raise ValueError("cases cannot be empty")
    ids = set()
    for case in cases:
        if not isinstance(case.get("id"), str) or not case["id"] or case["id"] in ids:
            raise ValueError("case IDs must be unique nonempty strings")
        ids.add(case["id"])
        for key in ("query", "reference"):
            if not isinstance(case.get(key), str) or not case[key].strip():
                raise ValueError(f"{case['id']}: {key} must be nonempty text")
        relevant = case.get("relevant")
        if not isinstance(relevant, list) or any(not isinstance(x, str) for x in relevant):
            raise ValueError("relevant must list frozen chunk IDs; [] excludes positive recall")


class RagasJudge:
    """Ragas 0.4 collections API, with explicit clients and no implicit model defaults."""

    def __init__(
        self,
        model,
        embedding_model,
        *,
        timeout=60,
        max_retries=0,
        embedding_backend="openai",
        max_tokens=1024,
        disable_thinking=False,
    ):
        from openai import AsyncOpenAI
        from ragas.embeddings.base import embedding_factory
        from ragas.llms import llm_factory
        from ragas.metrics.collections import (
            AnswerRelevancy,
            ContextPrecision,
            ContextRecall,
            Faithfulness,
        )

        self.calls = []
        # Record every HTTP attempt (including SDK retries), without headers or error bodies.
        import httpx

        async def request_started(request):
            request.extensions["infra_usage_index"] = len(self.calls)
            request.extensions["infra_started"] = perf_counter()
            self.calls.append({"status_code": None, "usage": None, "cost_usd": None})

        async def record(response):
            await response.aread()
            try:
                body = response.json()
            except ValueError:
                body = {}
            self.calls[response.request.extensions["infra_usage_index"]].update(
                {
                    "status_code": response.status_code,
                    "usage": body.get("usage"),
                    "model": body.get("model"),
                    "latency_ms": (perf_counter() - response.request.extensions["infra_started"])
                    * 1000,
                }
            )

        self.http = httpx.AsyncClient(
            event_hooks={"request": [request_started], "response": [record]}, timeout=timeout
        )
        self.client = AsyncOpenAI(http_client=self.http, timeout=timeout, max_retries=max_retries)
        model_options = {"max_tokens": max_tokens}
        if disable_thinking:
            model_options["extra_body"] = {"thinking": {"type": "disabled"}}
        llm = llm_factory(model, client=self.client, temperature=0, max_retries=1, **model_options)
        if embedding_backend == "huggingface":
            from ragas.embeddings.huggingface_provider import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(model=embedding_model, device="cpu")
        elif embedding_backend == "openai":
            embeddings = embedding_factory("openai", model=embedding_model, client=self.client)
        else:
            raise ValueError("embedding_backend must be openai or huggingface")
        self.scorers = {
            "context_precision": ContextPrecision(llm=llm),
            "context_recall": ContextRecall(llm=llm),
            "faithfulness": Faithfulness(llm=llm),
            "response_relevancy": AnswerRelevancy(llm=llm, embeddings=embeddings),
        }
        self.configuration = {
            "ragas_version": importlib.metadata.version("ragas"),
            "model": model,
            "embedding_model": embedding_model,
            "embedding_backend": embedding_backend,
            "temperature": 0,
            "max_tokens": max_tokens,
            "disable_thinking": disable_thinking,
            "timeout_seconds": timeout,
            "max_retries": max_retries,
            "structured_output_retries": 0,
            "prompt_sha256": {
                name: {
                    key: hashlib.sha256(Path(inspect.getfile(type(value))).read_bytes()).hexdigest()
                    for key, value in vars(scorer).items()
                    if "prompt" in key
                }
                for name, scorer in self.scorers.items()
            },
            "identity_note": "provider model names; immutable weights not verified",
        }

    async def score(self, name, sample):
        fields = {
            "context_precision": ("user_input", "reference", "retrieved_contexts"),
            "context_recall": ("user_input", "reference", "retrieved_contexts"),
            "faithfulness": ("user_input", "response", "retrieved_contexts"),
            "response_relevancy": ("user_input", "response"),
        }[name]
        start = len(self.calls)
        try:
            result = await self.scorers[name].ascore(**{k: sample[k] for k in fields})
            return float(result.value)
        finally:
            self.last_calls = self.calls[start:]

    async def close(self):
        await self.client.close()


async def score_records(records, judge, on_row=None):
    """Score sequentially so usage cannot be attributed to the wrong case or metric."""
    rows = []
    for record in records:
        row = {**record, "ragas": {}, "judge_calls": [], "judge_errors": {}}
        sample = {
            "user_input": record["query"],
            "reference": record["reference"],
            "response": record.get("response"),
            "retrieved_contexts": [e["content"] for e in record.get("evidence", [])],
        }
        started = perf_counter()
        for name in METRICS:
            row["ragas"][name] = None
            if record.get("error") or sample["response"] is None:
                row["judge_errors"][name] = "generation_failed"
                continue
            try:
                value = await judge.score(name, sample)
                if not math.isfinite(value):
                    raise ValueError("nonfinite score")
                row["ragas"][name] = value
            except Exception as exc:
                # Exception messages from providers can contain credentials or private bodies.
                row["judge_errors"][name] = type(exc).__name__
            finally:
                row["judge_calls"].extend(getattr(judge, "last_calls", []))
        row["judge_latency_ms"] = (perf_counter() - started) * 1000
        rows.append(row)
        if on_row is not None:
            on_row(row)
    return rows


def summarize(rows):
    summaries = {}
    for config in sorted({r["config_id"] for r in rows}):
        selected = [r for r in rows if r["config_id"] == config]
        n = len(selected)
        latencies = sorted(r["latency_ms"] for r in selected)
        summaries[config] = {
            "outputs": n,
            "failures": sum(bool(r.get("error")) for r in selected),
            "ragas": {m: measurement([r["ragas"][m] for r in selected], n) for m in METRICS},
            "retrieval": {
                m: measurement([r.get("retrieval", {}).get(m) for r in selected], n)
                for m in ("recall", "mrr", "ndcg")
            },
            "latency_p50_ms": statistics.median(latencies),
            "latency_p95_ms": latencies[math.ceil(0.95 * n) - 1],
            "latency_samples": n,
            "generation_usage": usage_summary(
                [c for r in selected for c in r.get("generation_calls", [])]
            ),
            "judge_usage": usage_summary([c for r in selected for c in r["judge_calls"]]),
        }
    return summaries


def usage_summary(calls):
    usage = [c.get("usage") for c in calls]
    totals = []
    for u in usage:
        if isinstance(u, dict):
            total = u.get("total_tokens")
            if total is None and "prompt_tokens" in u and "completion_tokens" in u:
                total = u["prompt_tokens"] + u["completion_tokens"]
            if total is None and "input_tokens" in u and "output_tokens" in u:
                # Anthropic input_tokens excludes cache reads/creation (also DeepSeek adapter).
                total = (
                    u["input_tokens"]
                    + u["output_tokens"]
                    + u.get("cache_read_input_tokens", 0)
                    + u.get("cache_creation_input_tokens", 0)
                )
            totals.append(total)
        else:
            totals.append(None)
    known = [t for t in totals if t is not None]
    return {
        "calls": len(calls),
        "measured_calls": len(known),
        "coverage": len(known) / len(calls) if calls else None,
        "known_total_tokens": sum(known) if known else None,
        "total_tokens": sum(known) if known and len(known) == len(calls) else None,
        "cost_usd": None,
    }


def run_scoring(records, judge, on_row=None):
    async def run():
        try:
            return await score_records(records, judge, on_row=on_row)
        finally:
            await judge.close()

    return asyncio.run(run())
