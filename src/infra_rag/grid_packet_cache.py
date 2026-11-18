"""Auditable cache of exact ordered local reranker inputs, never evaluation judgments."""

import json
import math
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from .benchmarking import canonical_hash, digest, write_new


class PacketReranker:
    def __init__(self, model, folder, model_identity, *, batch_size=32):
        self.model = model
        self.folder = Path(folder)
        self.identity = {
            "model": model_identity,
            "batch_size": batch_size,
            "contract": "ordered-query-body-predict-defaults-v1",
        }
        self.enabled = True
        self.folder.mkdir(parents=True, exist_ok=True)

    def __getattr__(self, name):
        return getattr(self.model, name)

    def key(self, pairs):
        return canonical_hash([self.identity, pairs])

    def event(self, value):
        with (self.folder / "events.jsonl").open("a") as stream:
            stream.write(json.dumps(value, ensure_ascii=False) + "\n")

    def seed(self, pairs, scores, origin):
        scores = list(map(float, scores))
        if len(scores) != len(pairs) or not all(math.isfinite(s) for s in scores):
            raise ValueError("Invalid cached reranker scores")
        key = self.key(pairs)
        target = self.folder / (key + ".json")
        if not target.exists():
            write_new(
                target,
                {
                    "inputs": pairs,
                    "scores": scores,
                    "origin": origin,
                    "model_identity": self.identity,
                },
            )
            write_new(target.with_suffix(".sha256.json"), {"sha256": digest(target)})
        return key

    def predict(self, pairs):
        if len(pairs) > 90:
            raise ValueError("More than 90 actual reranker input pairs")
        started = perf_counter()
        key = self.key(pairs)
        tokenizer = getattr(self.model, "tokenizer", None)
        limit = getattr(self.model, "max_length", None)
        if tokenizer is not None and limit is not None:
            longest = max(
                (len(tokenizer.encode(q, body, truncation=False)) for q, body in pairs), default=0
            )
            if longest > limit:
                self.event(
                    {
                        "status": "input_rejected",
                        "packet": key,
                        "requested_pairs": len(pairs),
                        "max_input_tokens": longest,
                        "limit": limit,
                        "actual_pairs": 0,
                    }
                )
                raise ValueError("Reranker input exceeds model limit before prediction")
        target = self.folder / (key + ".json")
        if self.enabled and target.exists():
            if (
                digest(target)
                != json.loads(target.with_suffix(".sha256.json").read_text())["sha256"]
            ):
                raise ValueError("Reranker packet hash mismatch")
            value = json.loads(target.read_text())
            if canonical_hash(value["inputs"]) != canonical_hash(pairs):
                raise ValueError("Reranker packet inputs differ")
            self.event(
                {
                    "status": "cache_hit",
                    "packet": key,
                    "actual_pairs": 0,
                    "requested_pairs": len(pairs),
                    "duration_ms": (perf_counter() - started) * 1000,
                }
            )
            return value["scores"]
        attempt = str(uuid4())
        self.event(
            {
                "status": "started",
                "attempt": attempt,
                "packet": key,
                "requested_pairs": len(pairs),
                "cache_enabled": self.enabled,
            }
        )
        try:
            values = list(map(float, self.model.predict(pairs)))
            if len(values) != len(pairs) or not all(math.isfinite(v) for v in values):
                raise ValueError("Invalid reranker result shape or nonfinite score")
            if self.enabled:
                self.seed(pairs, values, {"kind": "new-local-prediction", "attempt": attempt})
            self.event(
                {
                    "status": "returned",
                    "attempt": attempt,
                    "packet": key,
                    "actual_pairs": len(pairs),
                    "duration_ms": (perf_counter() - started) * 1000,
                    "cache_enabled": self.enabled,
                }
            )
            return values
        except BaseException as exc:
            self.event(
                {
                    "status": "failed",
                    "attempt": attempt,
                    "packet": key,
                    "requested_pairs": len(pairs),
                    "completed_pairs": None,
                    "error": type(exc).__name__,
                    "duration_ms": (perf_counter() - started) * 1000,
                }
            )
            raise
