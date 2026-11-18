"""Request accounting and bounded, index-aware retrieval reuse for the local HTTP service."""

import copy
import json
from collections import OrderedDict
from contextvars import ContextVar
from hashlib import sha256
from pathlib import Path
from threading import Lock
from time import perf_counter
from uuid import uuid4

ACTIVE_REQUEST = ContextVar("infra_rag_request", default=None)


class BatchReranker:
    def __init__(self, model, batch_size):
        self.model, self.batch_size = model, batch_size

    def __getattr__(self, name):
        return getattr(self.model, name)

    def predict(self, pairs):
        return self.model.predict(pairs, batch_size=self.batch_size, show_progress_bar=False)


class AccountedModel:
    """Keep provider usage request-local, including validation retries and transport failures."""

    def __init__(self, model):
        self.model_client = model

    def __getattr__(self, name):
        return getattr(self.model_client, name)

    def generate(self, messages):
        # Real compatible clients store last_call on themselves. A shallow request-local
        # copy isolates that field while retaining the same immutable transport settings.
        model = copy.copy(self.model_client)
        model.last_call = None
        event = {"provider": getattr(model, "provider", "unknown"), "model": model.model}
        started = perf_counter()
        try:
            raw = model.generate(messages)
            event.update(status="returned", output_sha256=sha256(raw.encode()).hexdigest())
            return raw
        except Exception as exc:
            event.update(status="failed", error=type(exc).__name__)
            raise
        finally:
            event.update(
                duration_ms=(perf_counter() - started) * 1000,
                provider_metadata=copy.deepcopy(getattr(model, "last_call", None)),
            )
            journal = ACTIVE_REQUEST.get()
            if journal is not None:
                journal["model_calls"].append(event)


class RuntimeRetrieval:
    """Reuse only retrieval results; every answer still makes fresh model requests."""

    def __init__(self, service, *, batch_size=32, cache_size=0):
        if batch_size < 1 or cache_size < 0:
            raise ValueError("Positive batch size and nonnegative cache size required")
        self.service = service
        self.batch_size, self.cache_size = batch_size, cache_size
        self.cache = OrderedDict()
        self.generation = None

    def __getattr__(self, name):
        return getattr(self.service, name)

    def _generation(self):
        return (
            self.service.chunks,
            self.service.vectors,
            self.service.settings,
            self.service.context_counter,
            self.service.encoder,
            self.service.reranker,
        )

    def _unchanged(self, new):
        old = self.generation
        return old is not None and all(
            a == b if i == 2 else a is b for i, (a, b) in enumerate(zip(old, new, strict=True))
        )

    def search(self, query, *, diagnostics=None, context_pack=None, **kwargs):
        started = perf_counter()
        with self.service.lock:
            queue_ms = (perf_counter() - started) * 1000
            if not self._unchanged(self._generation()):
                self.cache.clear()
            key = (
                query,
                kwargs.get("top_k", 5),
                kwargs.get("domain"),
                kwargs.get("modality"),
                kwargs.get("strategy", "hybrid"),
                self.batch_size,
            )
            if self.cache_size and key in self.cache:
                cached = self.cache.pop(key)
                self.cache[key] = cached
                hits, detail, context = copy.deepcopy(cached)
                detail["rerank"] = {"enabled": False, "cached_scores": True, "pairs": []}
                detail["timings_ms"] = {
                    "runtime_queue": queue_ms,
                    "total": (perf_counter() - started) * 1000,
                }
                cache_hit = True
            else:
                if self.service.settings.rerank and self.service.reranker is None:
                    from sentence_transformers import CrossEncoder

                    self.service.reranker = BatchReranker(
                        CrossEncoder(
                            self.service.settings.reranker_model,
                            local_files_only=True,
                            max_length=512,
                        ),
                        self.batch_size,
                    )
                detail, context = {}, {}
                hits = self.service.search(
                    query, diagnostics=detail, context_pack=context, **kwargs
                )
                detail["timings_ms"]["runtime_queue"] = queue_ms
                cache_hit = False
                self.generation = self._generation()
                if self.cache_size:
                    self.cache[key] = copy.deepcopy((hits, detail, context))
                    if len(self.cache) > self.cache_size:
                        self.cache.popitem(last=False)
                    hits = copy.deepcopy(hits)
            detail["retrieval_cache"] = {
                "hit": cache_hit,
                "capacity": self.cache_size,
                "ranking_origin": "cached" if cache_hit else "fresh",
            }
            if diagnostics is not None:
                diagnostics.clear()
                diagnostics.update(detail)
            if context_pack is not None:
                context_pack.clear()
                context_pack.update(context)
            journal = ACTIVE_REQUEST.get()
            if journal is not None:
                journal["retrieval"].append(
                    {
                        "query": query,
                        "elapsed_ms": (perf_counter() - started) * 1000,
                        "diagnostics": detail,
                        "hit_ids": [h.chunk.id for h in hits],
                        "evidence": copy.deepcopy(context.get("evidence", [])),
                        "context_selection": {
                            k: copy.deepcopy(context[k])
                            for k in (
                                "policy",
                                "selection_pool_ids",
                                "selection_trace",
                                "budget",
                                "used_tokens",
                                "used_characters",
                                "omitted_chunk_ids",
                                "omissions",
                                "delivery_only_chunk_ids",
                                "token_count_method",
                            )
                            if k in context
                        },
                    }
                )
            return hits

    def status(self):
        return {
            **self.service.status(),
            "runtime": {
                "reranker_batch_size": self.batch_size,
                "retrieval_cache_capacity": self.cache_size,
                "answer_cache": False,
            },
        }


def install_request_journal(app, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = Lock()

    @app.middleware("http")
    async def account(request, call_next):
        if request.url.path != "/chat":
            return await call_next(request)
        journal = {"request_id": str(uuid4()), "path": "/chat", "model_calls": [], "retrieval": []}
        token = ACTIVE_REQUEST.set(journal)
        started = perf_counter()
        try:
            response = await call_next(request)
            journal["http_status"] = response.status_code
            response.headers["X-Request-ID"] = journal["request_id"]
            response.headers["Server-Timing"] = f"app;dur={(perf_counter() - started) * 1000:.2f}"
            return response
        except Exception as exc:
            journal.update(http_status=500, error=type(exc).__name__)
            raise
        finally:
            journal["server_ms"] = (perf_counter() - started) * 1000
            ACTIVE_REQUEST.reset(token)
            with lock, path.open("a") as stream:
                stream.write(json.dumps(journal, ensure_ascii=False, allow_nan=False) + "\n")
