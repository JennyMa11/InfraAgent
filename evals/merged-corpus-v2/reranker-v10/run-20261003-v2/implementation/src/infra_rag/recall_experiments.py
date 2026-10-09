"""Query-only expansion and corpus-only context views for controlled retrieval experiments."""

import math
import re
from dataclasses import replace
from pathlib import Path

from .benchmarking import canonical_hash
from .evidence_selection import FrozenSelectionRetrieval

CONTEXT_VERSION = "source-heading-previous-line-v1"


def focused_queries(original, facets):
    """Preserve verbatim identifiers as shared context, without inventing answer terms."""
    identifiers = list(
        dict.fromkeys(re.findall(r"[A-Za-z0-9_]+(?:[.+/-][A-Za-z0-9_]+)*", original))
    )
    header = (
        ("Question context identifiers: " + " | ".join(identifiers) + "\n")
        if identifiers
        else "Original question context: " + original + "\n"
    )
    queries = []
    for facet in facets:
        if not facet.get("anchor_quote") or facet["anchor_quote"] not in original:
            raise ValueError("facet must have a verbatim question anchor")
        question = facet.get("question")
        if not isinstance(question, str) or not question.strip():
            raise ValueError("empty focused query")
        query = header + "Specific requirement: " + question
        if query not in queries:
            queries.append(query)
    if not 1 <= len(queries) <= 4:
        raise ValueError("one to four focused queries required")
    return queries


def context_views(chunks):
    """Build a deterministic search view; original evidence objects remain untouched."""
    previous = {}
    views, records = [], {}
    for chunk in chunks:
        key = (chunk.source, chunk.parent_id)
        prior = previous.get(key)
        lines = [f"Document: {Path(chunk.source).stem}"]
        for field in ("product", "release"):
            if chunk.metadata.get(field):
                lines.append(f"{field}: {chunk.metadata[field]}")
        if chunk.heading:
            lines.append("Section: " + chunk.heading)
        antecedent = ""
        if (
            prior
            and "```" not in prior.content
            and (
                prior.end_line is not None
                and chunk.start_line is not None
                and prior.end_line < chunk.start_line
            )
        ):
            complete_lines = [
                line.strip()
                for line in prior.content.splitlines()
                if line.strip() and len(line.strip()) <= 160
            ]
            if complete_lines:
                antecedent = complete_lines[-1]
                lines.append("Previous source line: " + antecedent)
        prefix = "\n".join(lines) + "\n\n"
        metadata = {
            **chunk.metadata,
            "search_view_version": CONTEXT_VERSION,
            "original_body_sha256": canonical_hash(chunk.content),
        }
        views.append(replace(chunk, content=prefix + chunk.content, metadata=metadata))
        records[chunk.id] = {
            "prefix": prefix,
            "previous_chunk_id": prior.id if antecedent else None,
            "original_body_sha256": canonical_hash(chunk.content),
            "search_body_sha256": canonical_hash(prefix + chunk.content),
        }
        previous[key] = chunk
    return views, records


def rank_fusion(channels):
    scores = {}
    for ranking in channels:
        seen = set()
        for rank, item in enumerate(ranking, 1):
            cid = item["chunk_id"]
            if cid in seen:
                raise ValueError("duplicate ID in channel")
            seen.add(cid)
            scores[cid] = scores.get(cid, 0.0) + 1 / (60 + rank)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))


def supplement(base_hits, channels, limit=30):
    """Never evict original candidates; cap new IDs before full-question reranking."""
    retained = {h["chunk_id"] for h in base_hits}
    added = [(cid, score) for cid, score in rank_fusion(channels) if cid not in retained][:limit]
    return [(h["chunk_id"], h["score"]) for h in base_hits] + added


class DeliveryRetrieval:
    """Evaluate Top10 ranking separately from a fixed Top5/Top8 delivery policy."""

    def __init__(self, base, bundles, delivery_k=5):
        if delivery_k not in {5, 8}:
            raise ValueError("delivery_k must be 5 or 8")
        self.replay = FrozenSelectionRetrieval(base, bundles, "T", None)
        self.delivery_k = delivery_k

    def __getattr__(self, name):
        return getattr(self.replay, name)

    @property
    def settings(self):
        return self.replay.settings

    @settings.setter
    def settings(self, value):
        self.replay.settings = value

    def search(self, query, *, top_k=5, diagnostics=None, **kwargs):
        actual = self.delivery_k if top_k == 5 else top_k
        hits = self.replay.search(query, top_k=actual, diagnostics=diagnostics, **kwargs)
        if diagnostics is not None:
            diagnostics["delivery_k"] = self.delivery_k
        return hits


def score_bundle(ids_and_scores, query, chunks, model_identity, scorer, cache, seeds=()):
    """Cache only exact full-query/body/model pairs, never facet scores or gold labels."""
    if len({cid for cid, _ in ids_and_scores}) != len(ids_and_scores):
        raise ValueError("duplicate candidates")
    seeded = {h["chunk_id"]: h["rerank_score"] for h in seeds}
    hits, missing = [], []
    for cid, fusion in ids_and_scores:
        key = canonical_hash([model_identity, query, chunks[cid].content])
        if key not in cache and cid in seeded:
            cache[key] = float(seeded[cid])
        if key not in cache:
            missing.append((cid, key))
        hits.append({"chunk_id": cid, "score": fusion, "key": key})
    if missing:
        pairs = [(query, chunks[cid].content) for cid, _ in missing]
        values = scorer(pairs)
        for (_, key), value in zip(missing, values, strict=True):
            value = float(value)
            if not math.isfinite(value):
                raise ValueError("nonfinite rerank score")
            cache[key] = value
    for hit in hits:
        hit["rerank_score"] = cache[hit.pop("key")]
    hits.sort(key=lambda h: (-h["rerank_score"], -h["score"], h["chunk_id"]))
    bundle = {"scoring_query": query, "hits": hits}
    bundle["sha256"] = canonical_hash(bundle)
    return bundle
