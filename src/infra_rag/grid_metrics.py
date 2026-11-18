"""Explicit source-document ranking metrics and nondominated grid selection."""

import math
import statistics


def rank_metrics(ranked_sources, relevant, k):
    if not relevant or k < 1:
        raise ValueError("Nonempty source labels and positive cutoff required")
    ranked = ranked_sources[:k]
    found = set(ranked) & set(relevant)
    first = next((i for i, s in enumerate(ranked, 1) if s in relevant), None)
    return {
        "recall": len(found) / len(set(relevant)),
        "hit": int(bool(found)),
        "mrr": 1 / first if first else 0.0,
    }


def latency(values):
    ordered = sorted(values)
    return {
        "n": len(ordered),
        "p50_ms": statistics.median(ordered) if ordered else None,
        "p95_ms": ordered[math.ceil(0.95 * len(ordered)) - 1] if ordered else None,
    }


def dominates(a, b):
    quality = ("recall5", "hit5", "mrr5", "required_recall5", "complete5")
    weak = all(a[k] >= b[k] for k in quality) and a["p95_ms"] <= b["p95_ms"]
    strict = any(a[k] > b[k] for k in quality) or a["p95_ms"] < b["p95_ms"]
    return weak and strict


def feasible(candidate, baseline):
    return not candidate["original_complete_losses"] and all(
        candidate[k] + 1e-12 >= baseline[k]
        for k in ("recall5", "hit5", "mrr5", "required_recall5", "complete5")
    )
