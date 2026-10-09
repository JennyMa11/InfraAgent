"""Experimental adapters for paired legacy QA / research Agent comparisons."""

from dataclasses import replace
from types import SimpleNamespace

from .agent import ResearchAgent
from .benchmarking import canonical_hash
from .budget_ablation import AblationPacker
from .models import Hit

V6_PARAMETERS = {"limit": 8, "length_power": 0.0, "protect": 1, "neighbors": False}


class V6ComparisonRetrieval:
    """Use identical v6 selection for either executor; never consume evaluation labels."""

    def __init__(self, base, bundles, count, *, include_metadata=False):
        self.base, self.bundles, self.count = base, bundles, count
        self.include_metadata = include_metadata
        self.by_id = {c.id: c for c in base.chunks}
        self.cache, self.score_cache = {}, {}
        self.search_records = []

    def __getattr__(self, name):
        return getattr(self.base, name)

    def _encoder(self):
        return SimpleNamespace(token_length=self.count)

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
        if (domain, modality, strategy) not in {
            ("infra", None, "hybrid"),
            ("infra", "text", "hybrid"),
        }:
            raise ValueError("comparison only supports frozen infra/text/hybrid filters")
        if not 1 <= top_k <= 100:
            raise ValueError("invalid top_k")
        query = str(query)
        if query not in self.cache:
            bundle = self.bundles.get(query)
            if bundle is None:
                diag = {}
                self.base.search(
                    query,
                    top_k=100,
                    domain="infra",
                    modality="text",
                    strategy="hybrid",
                    diagnostics=diag,
                )
                rows = diag["final"]
                scoring = query
                provenance = "new_live_retrieval"
            else:
                rows, scoring = bundle["hits"], bundle["scoring_query"]
                provenance = "frozen_original_candidates"
            hits = [
                Hit(self.by_id[h["chunk_id"]], h.get("score", 0.0), rerank_score=h["rerank_score"])
                for h in rows
            ]
            chosen, packed, selection = AblationPacker(
                hits, {"evidence": []}, self.by_id, query + "\n" + scoring, self.count
            ).pack(
                **V6_PARAMETERS,
                token_budget=self.settings.context_tokens,
                char_budget=self.settings.context_chars,
            )
            diag = {
                "candidates": [h.chunk.id for h in hits],
                "final": [{"chunk_id": h.chunk.id, "rerank_score": h.rerank_score} for h in chosen],
                "comparison_provenance": provenance,
                "scoring_query": scoring,
                "selection": selection,
            }
            self.cache[query] = (chosen, packed, diag)
        chosen, packed, diag = self.cache[query]
        if diagnostics is not None:
            diagnostics.update(diag)
        if context_pack is not None:
            context_pack.update(packed)
            if self.include_metadata:
                context_pack["include_evidence_metadata"] = True
        self.search_records.append({"query": query, "diagnostics": diag, "context": packed})
        return chosen

    def score_evidence(self, query, evidence):
        pairs = [(query, e["content"]) for e in evidence]
        pending = [
            pair for pair in dict.fromkeys(pairs) if canonical_hash(pair) not in self.score_cache
        ]
        if pending:
            scores = self.base.reranker.predict(pending)
            for pair, score in zip(pending, scores, strict=True):
                self.score_cache[canonical_hash(pair)] = float(score)
        return [self.score_cache[canonical_hash(pair)] for pair in pairs]


class CoverageResearchAgent(ResearchAgent):
    """Reorder only already returned bodies; keep actual Agent headers and budget checks."""

    def __init__(self, retrieval, model, *, scoring_query, **kwargs):
        super().__init__(retrieval, model, **kwargs)
        self.scoring_query = scoring_query

    def _pack(self, evidence):
        items = list(evidence.values())
        if not items:
            return []
        scores = self.retrieval.score_evidence(self.scoring_query, items)
        hits = [
            Hit(
                replace(self.retrieval.by_id[e["chunk_id"]], content=e["content"]),
                0.0,
                rerank_score=score,
            )
            for e, score in zip(items, scores, strict=True)
        ]
        hits.sort(key=lambda h: (-h.rerank_score, h.chunk.id))
        chosen, _, _ = AblationPacker(
            hits, {"evidence": []}, {}, self.scoring_query, self.retrieval.count
        ).pack(
            **V6_PARAMETERS,
            token_budget=self.retrieval.settings.context_tokens,
            char_budget=self.retrieval.settings.context_chars,
        )
        by_chunk = {e["chunk_id"]: e for e in items}
        ordered = {by_chunk[h.chunk.id]["id"]: by_chunk[h.chunk.id] for h in chosen}
        ordered.update({key: value for key, value in evidence.items() if key not in ordered})
        return super()._pack(ordered)
