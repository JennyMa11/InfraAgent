"""Deterministic Grid v2 variants and paired delivery gates (independent of v1)."""

from dataclasses import asdict, dataclass, replace
from math import log2


def source_ndcg(ranked_sources, relevant, k):
    if not relevant:
        return None
    seen, dcg = set(), 0.0
    for rank, source in enumerate(ranked_sources[:k], 1):
        if source in relevant and source not in seen:
            dcg += 1 / log2(rank + 1)
        seen.add(source)
    ideal = sum(1 / log2(i + 2) for i in range(min(k, len(relevant))))
    return dcg / ideal


@dataclass(frozen=True)
class Arm:
    index: str = "I0"
    strategy: str = "hybrid"
    k: int = 30
    rrf: int = 60
    rerank: bool = False
    depth: int = 90
    fusion: str = "union"
    policy: str = "prefix"
    neighbors: bool = True

    def identity(self):
        return "-".join(str(v) for v in asdict(self).values())


def recall_arms(index):
    return (
        [Arm(index, strategy, k) for strategy in ("bm25", "dense") for k in (20, 50)]
        + [Arm(index, "hybrid", k, rrf) for k in (20, 50) for rrf in (30, 60)]
        + [Arm(index)]
    )


def refinements(arm):
    result = []
    if arm.strategy == "hybrid":
        result += [replace(arm, rrf=n) for n in (30, 60, 100) if n != arm.rrf]
        result += [replace(arm, fusion="truncate" if arm.fusion == "union" else "union")]
    if arm.rerank:
        result += [replace(arm, depth=n) for n in (30, 60, 90) if n != arm.depth]
    result += [replace(arm, policy="complete" if arm.policy == "prefix" else "prefix")]
    if arm.policy == "prefix":
        result += [replace(arm, neighbors=not arm.neighbors)]
    return result


def delivery_gate(candidate, baseline):
    """No repeated outputs or negative questions enter the paired positive denominator."""

    def key(r):
        return r["dataset"], r["id"]

    old = {key(r): r for r in baseline if r["answerable"]}
    new = {key(r): r for r in candidate if r["answerable"]}
    if (
        len(old) != sum(r["answerable"] for r in baseline)
        or len(new) != sum(r["answerable"] for r in candidate)
        or old.keys() != new.keys()
    ):
        raise ValueError("Expected one paired output per positive dev question")
    losses = [
        k for k in old if old[k]["delivery5"]["complete"] and not new[k]["delivery5"]["complete"]
    ]
    delta = {
        ds: sum(
            new[k]["delivery5"]["complete"] - old[k]["delivery5"]["complete"]
            for k in old
            if k[0] == ds
        )
        for ds in {k[0] for k in old}
    }
    return {
        "eligible": not losses and all(v >= 0 for v in delta.values()),
        "losses": losses,
        "delta": delta,
        "net": sum(delta.values()),
    }
