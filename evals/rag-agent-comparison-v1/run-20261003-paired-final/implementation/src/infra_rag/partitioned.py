"""Independent source quotas, language routing and bounded official-version preference."""

import re
from time import perf_counter

from .chunking import stable_id
from .context import pack_context
from .evidence_metadata import metadata_text
from .models import Hit


class RoutedQuery(str):
    def __new__(cls, original, english):
        obj = super().__new__(cls, original)
        obj.english = english
        return obj


class RoutedTranslator:
    def __init__(self, translator):
        self.translator = translator

    def expand(self, query):
        english, trace = self.translator.expand(query)
        trace["mode"] = "by_collection"
        return RoutedQuery(query, english), trace


def explicit_versions(query):
    return [
        (product.lower(), version.lstrip("vV"))
        for product, version in re.findall(
            r"\b(vLLM|SGLang|CUDA)\s*(?:版本\s*)?(v?\d+\.\d+(?:\.\d+)?)\b", str(query), re.I
        )
    ]


def version_matches(chunk, requested):
    meta = chunk.metadata
    return meta.get("collection") == "official" and any(
        str(meta.get("product", "")).lower() == product
        and str(meta.get("release", "")).lstrip("vV") == version
        for product, version in requested
    )


def prefer_versions(hits, query, top_k, enabled, *, scope="top10"):
    if scope not in {"top10", "all"}:
        raise ValueError("version scope must be top10 or all")
    requested = explicit_versions(query)
    matching = [h for h in hits if version_matches(h.chunk, requested)]
    eligible = hits[:10] if scope == "top10" else hits
    protected = [h for h in eligible if version_matches(h.chunk, requested)][: min(2, top_k)]
    selected = list(protected) if enabled and requested else []
    ids = {h.chunk.id for h in selected}
    selected += [h for h in hits if h.chunk.id not in ids][: max(0, top_k - len(selected))]
    return selected, {
        "requested": requested,
        "enabled": enabled,
        "scope": scope,
        "protected_ids": [h.chunk.id for h in protected] if enabled else [],
        "missing_version_evidence": bool(requested and not protected),
        "candidate_missing_version_evidence": bool(requested and not matching),
        "version_evidence_outside_top10": bool(
            requested
            and matching
            and not any(version_matches(h.chunk, requested) for h in hits[:10])
        ),
    }


class PartitionedRetrieval:
    def __init__(
        self,
        base,
        banks,
        rewrites=None,
        *,
        language_route=False,
        version_priority=False,
        community_recall_language=None,
        rerank_language=None,
        version_scope="top10",
        include_metadata=False,
    ):
        self.base, self.banks = base, banks
        self.rewrites = rewrites or {}
        self.language_route, self.version_priority = language_route, version_priority
        self.community_recall_language = community_recall_language or (
            "original" if language_route else "english"
        )
        self.rerank_language = rerank_language or ("by_collection" if language_route else "english")
        if self.community_recall_language not in {"original", "english"}:
            raise ValueError("community recall language must be original or english")
        if self.rerank_language not in {"by_collection", "english"}:
            raise ValueError("rerank language must be by_collection or english")
        if version_scope not in {"top10", "all"}:
            raise ValueError("version scope must be top10 or all")
        self.version_scope, self.include_metadata = version_scope, include_metadata
        self.corpus_identity = stable_id(*(c.id + "\n" + c.content for c in self.base.chunks))

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
        candidate_snapshot=None,
    ):
        if top_k < 1:
            raise ValueError("top_k must be positive")
        started = perf_counter()
        original = str(query)
        english = getattr(query, "english", self.rewrites.get(original, original))
        by_id = {c.id: c for c in self.chunks}
        key = {
            "original": original,
            "english": english,
            "domain": domain,
            "modality": modality,
            "strategy": strategy,
            "community_recall_language": self.community_recall_language,
            "corpus_identity": self.corpus_identity,
            "banks": {
                name: {
                    "candidate_k": service.settings.candidate_k,
                    "fusion_candidates": service.settings.fusion_candidates,
                    "lexical_query_mode": service.settings.lexical_query_mode,
                    "fingerprint": service.settings.fingerprint(),
                }
                for name, service in self.banks.items()
            },
        }
        if candidate_snapshot:
            if candidate_snapshot["key"] != key:
                raise ValueError("Candidate snapshot does not match recall configuration")
            bank_debug, records = candidate_snapshot["banks"], candidate_snapshot["records"]
        else:
            bank_debug, records = {}, []
            for name, service in self.banks.items():
                actual = (
                    original
                    if (self.community_recall_language == "original" and name == "community")
                    else english
                )
                detail = {}
                # Read the entire fused list, independently of the child's returned top_k.
                service.search(
                    actual,
                    top_k=min(30, top_k),
                    domain=domain,
                    modality=modality,
                    strategy=strategy,
                    diagnostics=detail,
                )
                bank_debug[name] = {"query": actual, **detail}
                fused = {row["chunk_id"]: row["rrf_score"] for row in detail.get("fusion", [])}
                records.extend(
                    {"chunk_id": cid, "score": fused.get(cid, 0), "bank": name}
                    for cid in detail.get("candidates", [])
                )
            if candidate_snapshot is not None:
                candidate_snapshot.update(key=key, banks=bank_debug, records=records)
        candidates = {}
        for record in records:
            name = record["bank"]
            hit = Hit(by_id[record["chunk_id"]], record["score"], channels=[name])
            rerank_query = (
                original
                if (self.rerank_language == "by_collection" and name == "community")
                else english
            )
            candidates[hit.chunk.id] = (hit, rerank_query)
        ordered = sorted(candidates.values(), key=lambda pair: (-pair[0].score, pair[0].chunk.id))
        before = {h.chunk.id: i for i, (h, _) in enumerate(ordered, 1)}
        pairs = [
            (
                actual,
                metadata_text(hit.chunk.metadata) + hit.chunk.content
                if self.include_metadata
                else hit.chunk.content,
            )
            for hit, actual in ordered
        ]
        if self.settings.rerank and ordered:
            if self.base.reranker is None:
                from sentence_transformers import CrossEncoder

                self.base.reranker = CrossEncoder(self.settings.reranker_model)
            scores = self.base.reranker.predict(pairs)
            for (hit, _), score in zip(ordered, scores, strict=True):
                hit.rerank_score = float(score)
            ordered.sort(key=lambda pair: (-pair[0].rerank_score, -pair[0].score, pair[0].chunk.id))
        hits = [h for h, _ in ordered]
        selected, version_debug = prefer_versions(
            hits, original, top_k, self.version_priority, scope=self.version_scope
        )
        packed = pack_context(
            selected,
            self.parent_index,
            self.base._encoder().token_length
            if hasattr(self.base._encoder(), "token_length")
            else len,
            self.settings.context_tokens,
            self.settings.context_chars,
            domain,
            modality,
        )
        self.decorate_context(packed)
        if context_pack is not None:
            context_pack.clear()
            context_pack.update(packed)
        if diagnostics is not None:
            diagnostics.update(
                {
                    "banks": bank_debug,
                    "candidates": list(candidates),
                    "candidate_collections": {
                        cid: h.channels[0] for cid, (h, _) in candidates.items()
                    },
                    "version_preference": version_debug,
                    "query_expansion": {
                        "original": original,
                        "english": english,
                        "mode": "by_collection" if self.language_route else "english",
                        "community_recall_language": self.community_recall_language,
                        "rerank_language": self.rerank_language,
                    },
                    "include_metadata": self.include_metadata,
                    "final": [
                        {
                            "chunk_id": h.chunk.id,
                            "rank": i,
                            "before_rerank_rank": before[h.chunk.id],
                            "rerank_score": h.rerank_score,
                        }
                        for i, h in enumerate(hits, 1)
                    ],
                    "returned_chunk_ids": [h.chunk.id for h in selected],
                    "timings_ms": {"total": (perf_counter() - started) * 1000},
                }
            )
        return selected

    def decorate_context(self, packed):
        for evidence in packed["evidence"]:
            evidence["provenance"] = evidence["metadata"]
        if self.include_metadata:
            packed["include_evidence_metadata"] = True

    def ingest(self, *args, **kwargs):
        raise ValueError("Frozen partitioned profile: rebuild the corpus instead of importing")

    def delete(self, source):
        raise ValueError("Frozen partitioned profile: rebuild the corpus instead of deleting")

    def status(self):
        return {
            **self.base.status(),
            "source_partitioning": True,
            "bank_candidate_k": 30,
            "language_route": self.language_route,
            "version_priority": self.version_priority,
            "community_recall_language": self.community_recall_language,
            "rerank_language": self.rerank_language,
            "version_scope": self.version_scope,
            "include_metadata": self.include_metadata,
        }
