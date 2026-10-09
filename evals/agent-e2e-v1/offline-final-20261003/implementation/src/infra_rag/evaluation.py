import math
import statistics
import time


def metrics(retrieved, relevant, k):
    if not relevant:
        raise ValueError("retrieval metrics require at least one labeled relevant item")
    if k < 1:
        raise ValueError("k must be positive")
    # One document is one hit when evaluating source-level labels.
    retrieved = list(dict.fromkeys(retrieved))[:k]
    relevant = set(relevant)
    hits = [1 if item in relevant else 0 for item in retrieved]
    recall = sum(hits) / len(relevant)
    precision = sum(hits) / k
    dcg = sum(hit / math.log2(rank + 2) for rank, hit in enumerate(hits))
    ideal = sum(1 / math.log2(rank + 2) for rank in range(min(k, len(relevant))))
    return {
        "recall": recall,
        "precision": precision,
        "f1": 2 * recall * precision / (recall + precision) if recall + precision else 0,
        "mrr": next((1 / (i + 1) for i, hit in enumerate(hits) if hit), 0),
        "ndcg": dcg / ideal,
    }


def evaluate(service, dataset, k=5, strategy="hybrid", label="source"):
    if label not in {"source", "chunk", "parent"}:
        raise ValueError("label must be source, chunk or parent")
    if not dataset:
        raise ValueError("evaluation dataset cannot be empty")
    rows = []
    for item in dataset:
        start = time.perf_counter()
        hits = service.search(
            item["query"],
            top_k=k,
            domain=item.get("domain"),
            modality=item.get("modality"),
            strategy=strategy,
        )
        elapsed = (time.perf_counter() - start) * 1000
        retrieved = (
            [hit.chunk.id for hit in hits]
            if label == "chunk"
            else [hit.chunk.parent_id for hit in hits]
            if label == "parent"
            else [hit.chunk.source for hit in hits]
        )
        rows.append(
            {
                "id": item["id"],
                "query": item["query"],
                "retrieved": retrieved,
                "latency_ms": elapsed,
                "relevant": item["relevant"],
                **metrics(retrieved, item["relevant"], k),
            }
        )
    latencies = sorted(row["latency_ms"] for row in rows)
    return {
        "latency_p50_ms": statistics.median(latencies),
        "latency_p95_ms": latencies[max(0, math.ceil(0.95 * len(latencies)) - 1)],
        "configuration": service.status(),
        "k": k,
        "strategy": strategy,
        "label": label,
        "macro": {
            key: statistics.mean(row[key] for row in rows)
            for key in ["recall", "precision", "f1", "mrr", "ndcg", "latency_ms"]
        },
        "rows": rows,
    }


def resolve_spans(service, dataset, base_dir):
    """Resolve authored evidence spans independently of query/retrieval outputs."""
    from pathlib import Path

    def normalize(text):
        return "".join(text.split())

    resolved = []
    for item in dataset:
        relevant, matches = set(), []
        for span in item["relevant_spans"]:
            source = str((Path(base_dir) / span["source"]).resolve())
            evidence = normalize(span["text"])
            candidates = [
                c
                for c in service.chunks
                if c.source == source
                and (not span.get("heading") or c.heading == span["heading"])
                and evidence in normalize(c.content)
            ]
            if not candidates:
                raise ValueError(f"{item['id']}: evidence span does not fit any chunk: {span}")
            relevant.update(c.id for c in candidates)
            matches.append({"span": span, "chunk_ids": [c.id for c in candidates]})
        resolved.append({**item, "relevant": sorted(relevant), "gold_matches": matches})
    return resolved


def resolve_alternatives(service, dataset, base_dir):
    """An answer may use any evidence group; all spans within that group are required."""
    resolved = []
    for item in dataset:
        alternatives = []
        relevant = set()
        for group in item["evidence_alternatives"]:
            match = resolve_spans(
                service, [{"id": item["id"], "relevant_spans": group["spans"]}], base_dir
            )[0]
            requirements = [m["chunk_ids"] for m in match["gold_matches"]]
            relevant.update(match["relevant"])
            alternatives.append({**group, "requirements": requirements})
        resolved.append(
            {**item, "relevant": sorted(relevant), "evidence_alternatives": alternatives}
        )
    return resolved


def evidence_metrics(retrieved, item, k):
    """Credit complete coverage of any one independently annotated alternative."""
    retrieved = list(dict.fromkeys(retrieved))[:k]
    alternatives = item["evidence_alternatives"]
    if not alternatives or any(not g["requirements"] for g in alternatives):
        raise ValueError("evidence alternatives must contain nonempty requirements")

    def coverage(ids, group):
        return sum(bool(set(options) & set(ids)) for options in group["requirements"]) / len(
            group["requirements"]
        )

    complete_rank = next(
        (
            rank
            for rank in range(1, len(retrieved) + 1)
            if any(coverage(retrieved[:rank], group) == 1 for group in alternatives)
        ),
        None,
    )
    return {
        "complete_evidence_hit": float(complete_rank is not None),
        "evidence_mrr": 1 / complete_rank if complete_rank else 0.0,
        "evidence_coverage": max(coverage(retrieved, group) for group in alternatives),
    }
