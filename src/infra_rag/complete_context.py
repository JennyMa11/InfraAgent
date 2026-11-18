"""Opt-in whole-body selection over an already ranked pool; no additional retrieval."""

import math
from collections import Counter
from dataclasses import replace

from .chunking import stable_id
from .context import pack_context
from .lexical import query_terms

POLICY = "complete-v2"
POOL_LIMIT = 15


def pack_complete_context(hits, ranked, query, count, token_budget, char_budget):
    """Preserve returned ranks and source bodies; omit an entire unit if it cannot fit.

    The first ranked hit is protected when it fits. Further units balance original
    uncovered query terms, breaking ties by original relevance per token cost. Labels, expected
    answers, and corpus-specific identifiers never enter selection.
    """
    if token_budget < 1 or char_budget < 1:
        raise ValueError("positive context budgets required")
    frontier = ranked[:POOL_LIMIT]
    if len({h.chunk.id for h in frontier}) != len(frontier):
        raise ValueError("duplicate ranked candidates")
    words = {
        h.chunk.id: {w for w in query_terms(h.chunk.content, "technical") if len(w) > 1}
        for h in frontier
    }
    frequencies = Counter(w for terms in words.values() for w in terms)
    wanted = {w for w in query_terms(query, "technical") if len(w) > 1}
    weights = {
        w: math.log(1 + len(frontier) / (1 + frequencies[w])) for w in wanted if frequencies[w]
    }
    wanted = set(weights)
    total_weight = sum(weights.values()) or 1.0
    remaining = {h.chunk.id: (rank, h) for rank, h in enumerate(frontier, 1)}
    chosen, blocks, trace, covered = [], [], [], set()

    def block(hit):
        c = hit.chunk
        return f"[E{stable_id(c.id)}] {c.heading}\n{c.content}"

    def fits(text):
        combined = "\n\n".join(blocks + [text])
        return len(combined) <= char_budget and count(combined) <= token_budget

    while remaining:
        options = []
        for cid, (rank, hit) in remaining.items():
            text = block(hit)
            if not fits(text):
                continue
            novelty = sum(weights[w] for w in (words[cid] & wanted) - covered) / total_weight
            relevance = (
                max(0.0, hit.rerank_score) if hit.rerank_score is not None else 1 / math.sqrt(rank)
            )
            value = relevance / math.sqrt(max(1, count(text)))
            # Protect the top hit, but never deliver only its prefix.
            priority = 0 if rank == 1 else 1
            options.append((priority, -novelty, -value, rank, cid))
        if not options:
            break
        _, negative_novelty, negative_value, rank, cid = min(options)
        _, hit = remaining.pop(cid)
        chosen.append(replace(hit))
        blocks.append(block(hit))
        covered |= words[cid] & wanted
        trace.append(
            {
                "chunk_id": cid,
                "original_rank": rank,
                "utility": -negative_value,
                "novel_query_coverage": -negative_novelty,
            }
        )

    # The legacy packer supplies the canonical citation and provenance contract.
    # Its candidate set now contains only complete units already checked together.
    parents = {}
    for hit in chosen:
        parents.setdefault(hit.chunk.parent_id, []).append(hit.chunk)
    packed = pack_context(chosen, parents, count, token_budget, char_budget)
    if any(e["truncated"] for e in packed["evidence"]):
        raise RuntimeError("whole-body selection unexpectedly truncated evidence")
    owners = {}
    for hit in hits:
        hit.context, hit.sibling_ids, hit.evidence = "", [], []
        hit.context_ref = hit.chunk.parent_id
        owners.setdefault(hit.chunk.parent_id, hit)
    for hit in chosen:
        if hit.chunk.parent_id in owners and hit.evidence:
            owner = owners[hit.chunk.parent_id]
            owner.context = hit.context
            owner.sibling_ids = list(hit.sibling_ids)
            owner.evidence = list(hit.evidence)
    returned = {h.chunk.id for h in hits}
    packed.update(
        policy=POLICY,
        selection_pool_limit=POOL_LIMIT,
        selection_pool_ids=[h.chunk.id for h in frontier],
        selection_trace=trace,
        omitted_chunk_ids=list(remaining),
        omissions=[
            {"chunk_id": cid, "reason": "whole_body_exceeds_remaining_budget"} for cid in remaining
        ],
        delivery_only_chunk_ids=[h.chunk.id for h in chosen if h.chunk.id not in returned],
    )
    return packed
