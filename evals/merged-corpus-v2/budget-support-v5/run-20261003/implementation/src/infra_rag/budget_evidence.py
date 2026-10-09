"""Experimental budget allocation over frozen original bodies; no labels enter selection."""

import math
from collections import Counter
from dataclasses import replace

from .chunking import stable_id
from .context import pack_context, snippet
from .lexical import query_terms
from .models import Hit


def is_heading(chunk):
    return chunk.metadata.get("body_type") == "heading"


def budget_pack(
    hits,
    baseline_context,
    chunks,
    query,
    count,
    *,
    coverage=False,
    token_budget=1200,
    char_budget=4000,
):
    if token_budget <= 0 or char_budget <= 0:
        raise ValueError("positive budgets required")
    if len({h.chunk.id for h in hits}) != len(hits):
        raise ValueError("duplicate hits")
    frontier = {h.chunk.id: replace(h) for h in hits[:15] if not is_heading(h.chunk)}
    priors = {}
    for e in baseline_context["evidence"]:
        chunk = chunks[e["chunk_id"]]
        if chunk.id in frontier or is_heading(chunk):
            continue
        parents = [
            h
            for h in hits[:15]
            if (h.chunk.source, h.chunk.parent_id) == (chunk.source, chunk.parent_id)
        ]
        if not parents:
            continue
        value = 0.85 * max(h.rerank_score for h in parents)
        frontier[chunk.id] = Hit(chunk, 0.0, rerank_score=value)
        priors[chunk.id] = "same_source_parent_0.85_prior"
    if not all(math.isfinite(h.rerank_score) and h.rerank_score >= 0 for h in frontier.values()):
        raise ValueError("finite nonnegative relevance required")
    words = {
        cid: {w for w in query_terms(h.chunk.content, "technical") if len(w) > 1}
        for cid, h in frontier.items()
    }
    frequencies = Counter(w for terms in words.values() for w in terms)
    wanted = {w for w in query_terms(query, "technical") if len(w) > 1}
    weights = {w: math.log(1 + len(frontier) / (1 + frequencies[w])) for w in wanted}
    wanted = set(sorted(weights, key=lambda w: (-weights[w], w))[:64])
    total = sum(weights[w] for w in wanted) or 1.0
    chosen, blocks, trace, covered = [], [], [], set()
    remaining = dict(frontier)

    def block(hit, content=None):
        return f"[E{stable_id(hit.chunk.id)}] {hit.chunk.heading}\n" + (
            hit.chunk.content if content is None else content
        )

    def fits(text):
        joined = "\n\n".join(blocks + [text])
        return len(joined) <= char_budget and count(joined) <= token_budget

    first = next((h.chunk.id for h in hits if h.chunk.id in remaining), None)
    if first is not None:
        h = remaining.pop(first)
        content = snippet(h.chunk.content, lambda s: fits(block(h, s)))
        if content:
            chosen.append(h)
            blocks.append(block(h, content))
            covered |= words[first] & wanted
            trace.append(
                {
                    "chunk_id": first,
                    "protected_first": True,
                    "preview_truncated": content != h.chunk.content,
                }
            )
    while remaining and len(chosen) < 8:
        options = []
        for cid, h in remaining.items():
            text = block(h)
            if not fits(text):
                continue
            novelty = sum(weights[w] for w in (words[cid] & wanted) - covered) / total
            redundancy = max(
                (
                    len(words[cid] & words[c.chunk.id])
                    / max(1, len(words[cid] | words[c.chunk.id]))
                    for c in chosen
                ),
                default=0.0,
            )
            value = h.rerank_score / math.sqrt(max(1, count(text)))
            if coverage:
                value *= (1 + 0.5 * novelty) * (1 - 0.5 * redundancy)
            options.append((value, h.rerank_score, cid, novelty, redundancy))
        if not options:
            break
        value, _, cid, novelty, redundancy = min(options, key=lambda x: (-x[0], -x[1], x[2]))
        h = remaining.pop(cid)
        chosen.append(h)
        blocks.append(block(h))
        covered |= words[cid] & wanted
        trace.append(
            {
                "chunk_id": cid,
                "utility": value,
                "novelty": novelty,
                "redundancy": redundancy,
                "score_origin": priors.get(cid, "reranker"),
            }
        )
    parents = {}
    for h in chosen:
        parents.setdefault(h.chunk.parent_id, []).append(h.chunk)
    packed = pack_context(chosen, parents, count, token_budget, char_budget, "infra", "text")
    assert packed["used_tokens"] <= token_budget and packed["used_characters"] <= char_budget
    return (
        chosen,
        packed,
        {
            "eligible_ids": list(frontier),
            "neighbor_priors": priors,
            "selection_trace": trace,
            "query_words": sorted(wanted),
        },
    )
