"""Isolated factorial budget experiments; preserve the v5 implementation unchanged."""

import math
from collections import Counter
from dataclasses import replace

from .budget_evidence import is_heading
from .chunking import stable_id
from .context import pack_context, snippet
from .lexical import query_terms
from .models import Hit


class AblationPacker:
    def __init__(
        self, hits, baseline_context, chunks, query, count, *, blocked_ids=(), frontier_limit=15
    ):
        if not isinstance(frontier_limit, int) or not 1 <= frontier_limit <= 90:
            raise ValueError("frontier_limit must be between 1 and 90")
        self.frontier_limit = frontier_limit
        blocked = set(blocked_ids)
        self.hits = [h for h in hits if h.chunk.id not in blocked]
        if len({h.chunk.id for h in self.hits}) != len(self.hits):
            raise ValueError("duplicate hits")
        self.context = baseline_context
        self.chunks, self.query, self.count, self.blocked = chunks, query, count, blocked
        self.features = {}

    def prepare(self, neighbors):
        if neighbors in self.features:
            return self.features[neighbors]
        frontier = {
            h.chunk.id: replace(h)
            for h in self.hits[: self.frontier_limit]
            if not is_heading(h.chunk)
        }
        priors = {}
        if neighbors:
            for e in self.context["evidence"]:
                c = self.chunks[e["chunk_id"]]
                if c.id in self.blocked or c.id in frontier or is_heading(c):
                    continue
                parents = [
                    h
                    for h in self.hits[: self.frontier_limit]
                    if (h.chunk.source, h.chunk.parent_id) == (c.source, c.parent_id)
                ]
                if not parents:
                    continue
                score = 0.85 * max(h.rerank_score for h in parents)
                frontier[c.id] = Hit(c, 0.0, rerank_score=score)
                priors[c.id] = "same_source_parent_0.85_prior"
        if not all(
            math.isfinite(h.rerank_score) and h.rerank_score >= 0 for h in frontier.values()
        ):
            raise ValueError("finite nonnegative relevance required")
        words = {
            cid: {w for w in query_terms(h.chunk.content, "technical") if len(w) > 1}
            for cid, h in frontier.items()
        }
        frequencies = Counter(w for terms in words.values() for w in terms)
        wanted = {w for w in query_terms(self.query, "technical") if len(w) > 1}
        weights = {w: math.log(1 + len(frontier) / (1 + frequencies[w])) for w in wanted}
        wanted = set(sorted(weights, key=lambda w: (-weights[w], w))[:64])
        total = sum(weights[w] for w in wanted) or 1.0
        blocks = {
            cid: f"[E{stable_id(cid)}] {h.chunk.heading}\n{h.chunk.content}"
            for cid, h in frontier.items()
        }
        costs = {cid: max(1, self.count(text)) for cid, text in blocks.items()}
        value = (frontier, priors, words, wanted, weights, total, blocks, costs)
        self.features[neighbors] = value
        return value

    def pack(
        self,
        *,
        limit=8,
        length_power=0.5,
        protect=1,
        neighbors=True,
        token_budget=1200,
        char_budget=4000,
    ):
        if limit not in {8, None} or length_power not in {0.0, 0.5} or protect not in {1, 5}:
            raise ValueError("unsupported frozen ablation settings")
        if token_budget <= 0 or char_budget <= 0:
            raise ValueError("positive budgets required")
        frontier, priors, words, wanted, weights, total, texts, costs = self.prepare(neighbors)
        remaining = {cid: replace(h) for cid, h in frontier.items()}
        chosen, blocks, covered, trace = [], [], set(), []

        def fits(text):
            combined = "\n\n".join(blocks + [text])
            return len(combined) <= char_budget and self.count(combined) <= token_budget

        protected = [h.chunk.id for h in self.hits if h.chunk.id in remaining][:protect]
        for cid in protected:
            h = remaining.pop(cid)
            header = f"[E{stable_id(cid)}] {h.chunk.heading}\n"
            content = snippet(h.chunk.content, lambda s, header=header: fits(header + s))
            if not content:
                continue
            chosen.append(h)
            blocks.append(header + content)
            covered |= words[cid] & wanted
            trace.append(
                {
                    "chunk_id": cid,
                    "protected": True,
                    "preview_truncated": content != h.chunk.content,
                }
            )
        while remaining and (limit is None or len(chosen) < limit):
            options = []
            for cid, h in remaining.items():
                if not fits(texts[cid]):
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
                penalty = math.sqrt(costs[cid]) if length_power else 1.0
                utility = h.rerank_score / penalty
                utility *= (1 + 0.5 * novelty) * (1 - 0.5 * redundancy)
                options.append((utility, h.rerank_score, cid, novelty, redundancy))
            if not options:
                break
            utility, _, cid, novelty, redundancy = min(options, key=lambda v: (-v[0], -v[1], v[2]))
            chosen.append(remaining.pop(cid))
            blocks.append(texts[cid])
            covered |= words[cid] & wanted
            trace.append(
                {
                    "chunk_id": cid,
                    "utility": utility,
                    "novelty": novelty,
                    "redundancy": redundancy,
                    "cost_tokens": costs[cid],
                    "score_origin": priors.get(cid, "reranker"),
                }
            )
        parents = {}
        for h in chosen:
            parents.setdefault(h.chunk.parent_id, []).append(h.chunk)
        context = pack_context(
            chosen, parents, self.count, token_budget, char_budget, "infra", "text"
        )
        assert context["used_tokens"] <= token_budget and context["used_characters"] <= char_budget
        assert not self.blocked.intersection(e["chunk_id"] for e in context["evidence"])
        return (
            chosen,
            context,
            {
                "eligible_ids": list(frontier),
                "selection_trace": trace,
                "neighbor_priors": priors,
                "query_words": sorted(wanted),
                "parameters": {
                    "limit": limit,
                    "length_power": length_power,
                    "protect": protect,
                    "neighbors": neighbors,
                },
            },
        )
