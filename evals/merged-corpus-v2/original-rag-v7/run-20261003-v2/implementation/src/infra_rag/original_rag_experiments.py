"""Offline controls for the adopted RAG; never imported by the serving path."""

import heapq
import re
from collections import Counter, defaultdict
from dataclasses import replace

from .benchmarking import canonical_hash
from .budget_ablation import AblationPacker
from .encoding import tokenize
from .lexical import BM25Index
from .models import Hit
from .recall_experiments import context_views, score_bundle, supplement

TECHNICAL_VERSION = "suffix-and-underscore-v1"
ADJACENCY_VERSION = "same-source-release-parent-prev-next-160-v1"


def technical_tokens(text):
    """Keep literal tokens, adding deterministic forms; no answer-derived aliases."""
    result = []
    for token in tokenize(text):
        result.append(token)
        parts = token.split("_") if "_" in token else [token]
        for part in parts:
            if part != token and part:
                result.append(part)
            if not re.fullmatch(r"[a-z]{6,}", part):
                continue
            # Deliberately bounded morphology, not a semantic synonym dictionary.
            stem = re.sub(r"(?:ations?|ated|ating|ing|ed|es|s)$", "", part)
            if len(stem) >= 4 and stem != part:
                result.append(stem)
    return result


class TechnicalBM25(BM25Index):
    def __init__(self, chunks):
        documents = [Counter(technical_tokens(c.content + " " + c.heading)) for c in chunks]
        frequencies = Counter(term for doc in documents for term in doc)
        lengths = [sum(doc.values()) for doc in documents]
        average = sum(lengths) / (len(documents) or 1) or 1
        super().__init__(chunks, statistics=(documents, frequencies, lengths, average))
        self.identity = canonical_hash(
            [TECHNICAL_VERSION, [(c.id, c.content, c.heading) for c in chunks]]
        )

    def search(self, query, top_k=None):
        scores = defaultdict(float)
        for term in set(technical_tokens(query)):
            for index, frequency in self.postings.get(term, ()):
                scores[index] += (
                    self.idf[term] * frequency * 2.5 / (frequency + self.normalizers[index])
                )
        pairs = [(self.ids[index], score) for index, score in scores.items() if score > 0]
        return (
            heapq.nsmallest(top_k, pairs, key=lambda v: (-v[1], v[0]))
            if top_k
            else sorted(pairs, key=lambda v: (-v[1], v[0]))
        )


def adjacency_map(chunks):
    """Only immediate, ordered siblings of the same source and release are eligible."""
    groups = defaultdict(list)
    for c in chunks:
        if c.start_line is not None and c.end_line is not None:
            groups[c.source, c.parent_id, c.metadata.get("release")].append(c)
    result = {c.id: [] for c in chunks}
    for group in groups.values():
        ordered = sorted(group, key=lambda c: (c.start_line, c.end_line, c.id))
        for i, c in enumerate(ordered):
            for other in ordered[max(0, i - 1) : i] + ordered[i + 1 : i + 2]:
                if other.end_line < c.start_line or c.end_line < other.start_line:
                    result[c.id].append(other.id)
    return result


def adjacent_views(chunks):
    views, records = context_views(chunks)
    original = {c.id: c for c in chunks}
    adjacent = adjacency_map(chunks)
    result = []
    for view in views:
        c = original[view.id]
        # Reuse the corpus-only metadata prefix, but replace the old one-line antecedent.
        lines = [s for s in records[c.id]["prefix"].splitlines() if s.strip()]
        lines = [s for s in lines if not s.startswith("Previous source line:")]
        for cid in adjacent[c.id]:
            other = original[cid]
            direction = "Previous" if other.end_line < c.start_line else "Next"
            lines.append(f"{direction} source context: {other.content[:160]}")
        prefix = "\n".join(lines) + "\n\n"
        records[c.id] = {
            "prefix": prefix,
            "adjacent_ids": adjacent[c.id],
            "original_body_sha256": canonical_hash(c.content),
            "search_body_sha256": canonical_hash(prefix + c.content),
        }
        result.append(
            replace(
                view,
                content=prefix + c.content,
                metadata={**view.metadata, "search_view_version": ADJACENCY_VERSION},
            )
        )
    return result, records


def bounded_focused_queries(original, scoring, facets):
    """Use each facet's literal anchor, never attach another product's global version."""
    try:
        if not isinstance(facets, list) or not 1 <= len(facets) <= 4:
            raise ValueError("one to four facets required")
        queries = []
        for facet in facets:
            anchor, question = facet.get("anchor_quote"), facet.get("question")
            if not isinstance(anchor, str) or not anchor or anchor not in original:
                raise ValueError("invalid verbatim anchor")
            if not isinstance(question, str) or not question.strip():
                raise ValueError("empty focused question")
            # Versions must occur in the authored question; reject invented releases.
            versions = re.findall(r"\bv?\d+\.\d+(?:\.\d+)?\b", question)
            if any(version not in original for version in versions):
                raise ValueError("invented facet version")
            queries.append("Question anchor: " + anchor + "\nSpecific requirement: " + question)
        return list(dict.fromkeys(queries)), None
    except (ValueError, TypeError, AttributeError) as exc:
        return [scoring], str(exc)


def additive_pool(base_hits, channels, limit=30):
    if len(base_hits) > 60 or len({h["chunk_id"] for h in base_hits}) != len(base_hits):
        raise ValueError("baseline must contain at most 60 unique candidates")
    if not 0 <= limit <= 30:
        raise ValueError("at most 30 supplementary candidates")
    return supplement(base_hits, channels, limit=limit)


def pack_bundle(bundle, chunks, query, count, *, frontier_ids=None):
    hits = [
        Hit(chunks[h["chunk_id"]], h["score"], rerank_score=h["rerank_score"])
        for h in bundle["hits"]
    ]
    if frontier_ids is not None:
        allowed = set(frontier_ids)
        hits = [h for h in hits if h.chunk.id in allowed]
    p = AblationPacker(
        hits,
        {"evidence": []},
        chunks,
        query,
        count,
        frontier_limit=max(1, len(hits)) if frontier_ids is not None else 15,
    )
    return p.pack(limit=8, length_power=0.0, protect=1, neighbors=False)


def neighbor_bundle(bundle, selected, adjacent, chunks, model, scorer, cache):
    retained = {h["chunk_id"] for h in bundle["hits"]}
    channels = [
        [{"chunk_id": cid} for cid in adjacent[h.chunk.id] if cid not in retained] for h in selected
    ]
    # All previously reranked candidates count against the 90-pair limit.
    pool = supplement(bundle["hits"], channels, limit=min(30, 90 - len(retained)))
    scored = score_bundle(
        pool, bundle["scoring_query"], chunks, model, scorer, cache, bundle["hits"]
    )
    added = [h["chunk_id"] for h in scored["hits"] if h["chunk_id"] not in retained]
    return scored, added
