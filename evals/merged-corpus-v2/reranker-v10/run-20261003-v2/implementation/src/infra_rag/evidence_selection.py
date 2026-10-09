"""Experimental selection over frozen candidates; no gold or source quotas enter scoring."""

import json
import math

from .context import pack_context
from .models import Hit

FACET_PROMPT = (
    "Extract at most four distinct requirements explicitly asked by the question. "
    "Do not answer it, infer examples, add facts, or invent conditions. Preserve products, "
    "versions, identifiers, negation and uncertainty. Each requirement must be a retrieval "
    "question in the requested language, with a verbatim anchor_quote from original_query "
    "covering the relevant clause, not just its product name. Return only JSON: "
    '{"facets":[{"question":"...","anchor_quote":"..."}]}. '
    "If it cannot be decomposed, return one requirement with the complete question."
)


def parse_facets(raw, original, scoring_query):
    try:
        payload = json.loads(raw)
        facets = payload["facets"]
        if not isinstance(facets, list) or not 1 <= len(facets) <= 4:
            raise ValueError("one to four facets required")
        seen = set()
        for item in facets:
            question, anchor = item["question"], item["anchor_quote"]
            if (
                not isinstance(question, str)
                or not question.strip()
                or len(question) > 2000
                or not isinstance(anchor, str)
                or not anchor.strip()
                or anchor not in original
                or question in seen
            ):
                raise ValueError("invalid facet or nonverbatim anchor")
            seen.add(question)
        return facets, None
    except (ValueError, TypeError, KeyError):
        return [{"question": scoring_query, "anchor_quote": original}], "invalid_facets"


def _cosine(left, right):
    denominator = math.sqrt(sum(x * x for x in left) * sum(x * x for x in right))
    return (
        max(0.0, sum(x * y for x, y in zip(left, right, strict=True)) / denominator)
        if denominator
        else 0.0
    )


def select_order(hits, policy, *, vectors=None, matrix=None, limit=10):
    """Return an ordering and selection trace; retain original Hit.rerank_score values."""
    if policy not in {"T", "M", "F", "G"}:
        raise ValueError("unknown selection policy")
    if not hits:
        return [], []
    ids = [hit.chunk.id for hit in hits]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate candidates")
    relevance = {hit.chunk.id: float(hit.rerank_score) for hit in hits}
    if not all(math.isfinite(value) for value in relevance.values()):
        raise ValueError("nonfinite original score")
    if policy == "T":
        return list(hits), []
    if policy in {"F", "G"}:
        if not matrix or any(len(row) != len(hits) for row in matrix):
            raise ValueError("facet matrix does not match candidates")
        if any(not math.isfinite(value) or not 0 <= value <= 1 for row in matrix for value in row):
            raise ValueError("facet scores must be finite probabilities")
    if policy == "F":
        averages = [sum(row[i] for row in matrix) / len(matrix) for i in range(len(hits))]
        order = sorted(range(len(hits)), key=lambda i: (-averages[i], -relevance[ids[i]], ids[i]))
        return [hits[i] for i in order], [
            {"chunk_id": ids[i], "facet_mean": averages[i]} for i in order[:limit]
        ]
    if policy == "M" and (vectors is None or any(cid not in vectors for cid in ids)):
        raise ValueError("candidate vectors required")
    remaining, chosen, trace = set(range(len(hits))), [], []
    coverage = [0.0] * len(matrix) if policy == "G" else []
    redundancy = [0.0] * len(hits)
    for _ in range(min(limit, len(hits))):
        if policy == "G":
            scores = {
                i: sum(max(coverage[j], row[i]) - coverage[j] for j, row in enumerate(matrix))
                for i in remaining
            }
        else:
            scores = {i: 0.7 * relevance[ids[i]] - 0.3 * redundancy[i] for i in remaining}
        # Preserve the original first hit for M, including its frozen RRF tie breaking.
        best = (
            0
            if policy == "M" and not chosen
            else min(remaining, key=lambda i: (-scores[i], -relevance[ids[i]], ids[i]))
        )
        chosen.append(best)
        remaining.remove(best)
        entry = {"chunk_id": ids[best], "selection_score": scores[best]}
        if policy == "G":
            coverage = [max(value, matrix[j][best]) for j, value in enumerate(coverage)]
            entry["facet_coverage"] = list(coverage)
        else:
            entry["redundancy"] = redundancy[best]
            for i in remaining:
                redundancy[i] = max(redundancy[i], _cosine(vectors[ids[i]], vectors[ids[best]]))
        trace.append(entry)
    chosen.extend(sorted(remaining, key=lambda i: (-relevance[ids[i]], ids[i])))
    return [hits[i] for i in chosen], trace


class FrozenSelectionRetrieval:
    """Experimental wrapper replaying query-only bundles, with optional source quarantine."""

    def __init__(self, base, bundles, policy, features, *, blocked_ids=()):
        self.base, self.bundles, self.policy, self.features = base, bundles, policy, features
        self.blocked_ids = set(blocked_ids)
        self.by_id = {c.id: c for c in base.chunks}
        self.vectors = dict(zip((c.id for c in base.chunks), base.vectors, strict=True))
        self.parents = {
            key: [c for c in chunks if c.id not in self.blocked_ids]
            for key, chunks in base.parent_index.items()
        }
        self.cached = {}

    def __getattr__(self, name):
        return getattr(self.base, name)

    @property
    def settings(self):
        return self.base.settings

    @settings.setter
    def settings(self, value):
        self.base.settings = value

    def search(
        self,
        query,
        *,
        top_k=5,
        domain=None,
        modality=None,
        strategy="hybrid",
        diagnostics=None,
        context_pack=None,
    ):
        if not 1 <= top_k <= 10:
            raise ValueError("frozen selection supports top_k 1..10")
        bundle = self.bundles[str(query)]
        if (domain, modality, strategy) != ("infra", "text", "hybrid"):
            raise ValueError("frozen candidate filters/strategy do not match")
        eligible = [row for row in bundle["hits"] if row["chunk_id"] not in self.blocked_ids]
        hits = [
            Hit(self.by_id[row["chunk_id"]], row["score"], rerank_score=row["rerank_score"])
            for row in eligible
        ]
        feature = self.features(str(query)) if self.policy in {"F", "G"} else None
        matrix = None
        if feature:
            positions = {cid: i for i, cid in enumerate(feature["ids"])}
            matrix = [[row[positions[h.chunk.id]] for h in hits] for row in feature["matrix"]]
        if str(query) not in self.cached:
            ordered, trace = select_order(hits, self.policy, vectors=self.vectors, matrix=matrix)
            self.cached[str(query)] = ([h.chunk.id for h in ordered], trace)
        order, trace = self.cached[str(query)]
        by_id = {hit.chunk.id: hit for hit in hits}
        selected = [by_id[cid] for cid in order[:top_k]]
        encoder = self.base._encoder()
        packed = pack_context(
            selected,
            self.parents,
            getattr(encoder, "token_length", len),
            self.settings.context_tokens,
            self.settings.context_chars,
            domain,
            modality,
        )
        if context_pack is not None:
            context_pack.update(packed)
        if diagnostics is not None:
            diagnostics.update(
                {
                    "candidates": [h.chunk.id for h in hits],
                    "source_bundle_sha256": bundle["sha256"],
                    "policy": self.policy,
                    "selection_trace": trace,
                    "facets": feature["facets"] if feature else [],
                    "feature_sha256": feature["sha256"] if feature else None,
                    "candidate_collections": {
                        h.chunk.id: h.chunk.metadata.get("collection") for h in hits
                    },
                    "blocked_ids": sorted(self.blocked_ids),
                    "final": [
                        {"chunk_id": cid, "rank": i, "rerank_score": by_id[cid].rerank_score}
                        for i, cid in enumerate(order, 1)
                    ],
                    "returned_chunk_ids": order[:top_k],
                    "timing_mode": "frozen_candidate_replay",
                }
            )
        return selected
