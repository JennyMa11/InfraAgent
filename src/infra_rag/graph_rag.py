"""Deterministic, auditable graph expansion over already indexed text chunks."""

import json
import re
from collections import Counter, defaultdict, deque
from dataclasses import asdict
from threading import RLock
from time import perf_counter

from .chunking import stable_id
from .context import snippet

GRAPH_VERSION = "local-chunk-relations-v1"
RELATION_WEIGHTS = {
    "same_parent": 1.0,
    "adjacent_chunk": 0.9,
    "heading_continuity": 0.7,
    "shared_entity": 0.6,
}
ENTITY_PATTERN = re.compile(
    r"(?<![\w])(?:[A-Za-z]+[A-Z][A-Za-z0-9]*|[A-Z][A-Z0-9_+-]{1,}|"
    r"[A-Z][A-Za-z0-9]*(?:[._+-][A-Za-z0-9]+)+|"
    r"[\u4e00-\u9fff]{2,12}(?:缓存|机制|算法|管理器|调度器))(?![\w])"
)


def _entity_key(value):
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]", "", value.casefold())


def _provenance(chunk, relation, snippet_text=None):
    return {
        "chunk_id": chunk.id,
        "source": chunk.source,
        "locator": chunk.locator,
        "relation": relation,
        "evidence_snippet": chunk.content[:240] if snippet_text is None else snippet_text,
        "extraction": "heuristic" if relation == "shared_entity" else "structural",
    }


def _new_edge(source, target, relation, **extra):
    edge = {
        "source": source.id,
        "target": target.id,
        "relation": relation,
        "weight": RELATION_WEIGHTS[relation],
        "provenance": [_provenance(source, relation), _provenance(target, relation)],
    }
    edge.update(extra)
    return edge


class GraphRAGChain:
    """Expand hybrid seeds through source-derived relations, never query-derived edges."""

    def __init__(
        self,
        retrieval,
        *,
        top_k=5,
        max_seed_hits=8,
        max_expanded_chunks=30,
        context_counter=None,
    ):
        if not 1 <= top_k <= 100:
            raise ValueError("top_k must be in [1, 100]")
        if not 1 <= max_seed_hits <= 100:
            raise ValueError("max_seed_hits must be in [1, 100]")
        if max_expanded_chunks < 0:
            raise ValueError("max_expanded_chunks must be nonnegative")
        if context_counter is not None and not callable(context_counter):
            raise TypeError("context_counter must be callable")
        self.retrieval = retrieval
        self.top_k = top_k
        self.max_seed_hits = max_seed_hits
        self.max_expanded_chunks = max_expanded_chunks
        self.context_counter = context_counter
        self._cache = None
        self._lock = RLock()

    def _cache_key(self):
        identity = {
            "graph_version": GRAPH_VERSION,
            "index_fingerprint": self.retrieval.index_fingerprint,
            "chunks": [asdict(chunk) for chunk in self.retrieval.chunks],
            "source_manifest": self.retrieval.source_manifest,
        }
        return stable_id(json.dumps(identity, ensure_ascii=False, sort_keys=True, default=str))

    def _graph(self):
        key = self._cache_key()
        with self._lock:
            if self._cache is not None and self._cache["key"] == key:
                graph = self._cache["graph"]
                return graph, True
            graph = self._build_graph()
            self._cache = {"key": key, "graph": graph}
            return graph, False

    def _build_graph(self):
        chunks = sorted(
            (
                chunk
                for chunk in self.retrieval.chunks
                if chunk.modality == "text" and chunk.content.strip()
            ),
            key=lambda chunk: chunk.id,
        )
        by_id = {chunk.id: chunk for chunk in chunks}
        edges = []

        parents = defaultdict(list)
        for chunk in chunks:
            parents[(chunk.domain, chunk.source, chunk.parent_id)].append(chunk)
        for group in parents.values():
            for position, source in enumerate(group):
                for target in group[position + 1 :]:
                    edges.append(_new_edge(source, target, "same_parent"))

        documents = defaultdict(list)
        for chunk in chunks:
            documents[(chunk.domain, chunk.source)].append(chunk)
        for group in documents.values():
            ordered = sorted(
                group,
                key=lambda chunk: (
                    chunk.page if chunk.page is not None else -1,
                    chunk.start_line if chunk.start_line is not None else -1,
                    chunk.end_line if chunk.end_line is not None else -1,
                    chunk.parent_id,
                    chunk.id,
                ),
            )
            for source, target in zip(ordered, ordered[1:], strict=False):
                edges.append(_new_edge(source, target, "adjacent_chunk"))

        headings = defaultdict(list)
        for chunk in chunks:
            key = _entity_key(chunk.heading)
            if key:
                headings[(chunk.domain, chunk.source, key)].append(chunk)
        for group in headings.values():
            ordered = sorted(group, key=lambda chunk: chunk.id)
            for source, target in zip(ordered, ordered[1:], strict=False):
                edges.append(_new_edge(source, target, "heading_continuity"))

        mentions = defaultdict(list)
        for chunk in chunks:
            found = {}
            searchable_text = f"{chunk.heading}\n{chunk.content}"
            for match in ENTITY_PATTERN.finditer(searchable_text):
                value = match.group()
                key = _entity_key(value)
                if len(key) >= 2:
                    found.setdefault(key, (value, match.start()))
            for key, (value, start) in sorted(found.items()):
                mentions[(chunk.domain, key)].append((chunk, value, start))

        entity_pairs = defaultdict(set)
        entity_provenance = defaultdict(list)
        for (_domain, key), occurrences in mentions.items():
            # Common entities are weak evidence; bounding the clique keeps expansion auditable.
            occurrences = sorted(occurrences, key=lambda item: item[0].id)[:12]
            for position, (source, value, start) in enumerate(occurrences):
                for target, _, _ in occurrences[position + 1 :]:
                    pair = tuple(sorted((source.id, target.id)))
                    entity_pairs[pair].add(key)
                    entity_provenance[pair].append(
                        {
                            "entity": key,
                            "surface": value,
                            "chunk_id": source.id,
                            "source": source.source,
                            "locator": source.locator,
                            "relation": "shared_entity",
                            "evidence_snippet": searchable_chunk_text(source)[
                                max(0, start - 40) : start + 200
                            ],
                            "extraction": "heuristic",
                        }
                    )
        for (source_id, target_id), entities in sorted(entity_pairs.items()):
            edge = _new_edge(by_id[source_id], by_id[target_id], "shared_entity")
            edge["entities"] = sorted(entities)
            edge["provenance"].extend(
                sorted(
                    entity_provenance[(source_id, target_id)],
                    key=lambda item: (item["entity"], item["chunk_id"]),
                )
            )
            edges.append(edge)

        adjacency = {chunk.id: [] for chunk in chunks}
        for edge in edges:
            adjacency[edge["source"]].append(
                {"chunk_id": edge["target"], **_without_endpoints(edge)}
            )
            adjacency[edge["target"]].append(
                {"chunk_id": edge["source"], **_without_endpoints(edge)}
            )
        for relations in adjacency.values():
            relations.sort(
                key=lambda edge: (
                    -RELATION_WEIGHTS[edge["relation"]],
                    edge["relation"],
                    edge["chunk_id"],
                )
            )
        relation_counts = Counter(edge["relation"] for edge in edges)
        return {
            "version": GRAPH_VERSION,
            "chunks": by_id,
            "edges": sorted(
                edges, key=lambda edge: (edge["source"], edge["target"], edge["relation"])
            ),
            "adjacency": adjacency,
            "entity_count": len({key for _domain, key in mentions}),
            "relation_counts": dict(sorted(relation_counts.items())),
        }

    def _counter(self):
        if self.context_counter is not None:
            return self.context_counter
        if getattr(self.retrieval, "context_counter", None) is not None:
            return self.retrieval.context_counter
        encoder = self.retrieval._encoder()
        return getattr(encoder, "token_length", len)

    def retrieve(self, query, *, domain=None):
        started = perf_counter()
        trace = []
        phase = perf_counter()
        diagnostics, base_pack = {}, {}
        hits = self.retrieval.search(
            query,
            top_k=max(self.top_k, self.max_seed_hits),
            domain=domain,
            strategy="hybrid",
            diagnostics=diagnostics,
            context_pack=base_pack,
        )
        seeds = hits[: self.max_seed_hits]
        trace.append(
            {
                "step": "hybrid_seed_retrieval",
                "duration_ms": _elapsed(phase),
                "requested_top_k": max(self.top_k, self.max_seed_hits),
                "actual_seed_count": len(seeds),
                "seed_ids": [hit.chunk.id for hit in seeds],
                "base_diagnostics": diagnostics,
            }
        )

        phase = perf_counter()
        graph, cache_hit = self._graph()
        graph_stats = {
            "graph_version": graph["version"],
            "index_fingerprint": self.retrieval.index_fingerprint,
            "cache_hit": cache_hit,
            "text_nodes": len(graph["chunks"]),
            "edges": len(graph["edges"]),
            "relation_counts": graph["relation_counts"],
            "normalized_entities": graph["entity_count"],
            "domain": domain,
        }
        trace.append(
            {"step": "graph_build", "duration_ms": _elapsed(phase), "graph_stats": graph_stats}
        )

        phase = perf_counter()
        candidates = self._expand(graph, seeds, domain)
        trace.append(
            {
                "step": "graph_expand",
                "duration_ms": _elapsed(phase),
                "max_expanded_chunks": self.max_expanded_chunks,
                "expanded_count": sum(item["origin"] == "expanded" for item in candidates),
                "expansion_reasons": [
                    {
                        "chunk_id": item["chunk_id"],
                        "hop": item["hop"],
                        "reasons": item["expansion_reasons"],
                    }
                    for item in candidates
                    if item["origin"] == "expanded"
                ],
            }
        )

        phase = perf_counter()
        ranked = self._rank(candidates)
        trace.append(
            {
                "step": "rank",
                "duration_ms": _elapsed(phase),
                "algorithm": "base_retrieval_plus_graph_support_v1",
                "formula": (
                    "base_score + graph_score; ties prefer seeds, then base_rank, hop, chunk_id"
                ),
                "candidate_count": len(candidates),
                "ranked_count": len(ranked),
            }
        )

        phase = perf_counter()
        evidence, packing = self._pack(ranked[: self.top_k], graph)
        delivered = {item["chunk_id"] for item in evidence}
        for item in ranked:
            item["delivered"] = item["chunk_id"] in delivered
        trace.append(
            {
                "step": "evidence_pack",
                "duration_ms": _elapsed(phase),
                "selected_count": min(self.top_k, len(ranked)),
                "delivered_count": len(evidence),
                **packing,
            }
        )
        return {
            "chain": "graph_rag",
            "query": query,
            "domain": domain,
            "index_fingerprint": self.retrieval.index_fingerprint,
            "evidence": evidence,
            "candidates": candidates,
            "ranked": ranked,
            "trace": trace,
            "latency_ms": _elapsed(started),
        }

    def _expand(self, graph, seeds, domain):
        candidates = []
        states = {}
        for rank, hit in enumerate(seeds, 1):
            chunk = hit.chunk
            if chunk.modality != "text" or chunk.id not in graph["chunks"]:
                continue
            state = {
                "chunk_id": chunk.id,
                "origin": "seed",
                "hop": 0,
                "base_rank": rank,
                "base_score": float(hit.score),
                "rerank_score": float(hit.rerank_score) if hit.rerank_score is not None else None,
                "channels": list(hit.channels),
                "expansion_reasons": [],
                "graph_score": 0.0,
            }
            states[chunk.id] = state
            candidates.append(state)
        queue = deque(seed["chunk_id"] for seed in candidates)
        expanded = 0
        while queue and expanded < self.max_expanded_chunks:
            source_id = queue.popleft()
            source_state = states[source_id]
            if source_state["hop"] >= 2:
                continue
            for edge in graph["adjacency"].get(source_id, []):
                target_id = edge["chunk_id"]
                target = graph["chunks"][target_id]
                if domain is not None and target.domain != domain:
                    continue
                reason = {
                    "from_chunk_id": source_id,
                    "relation": edge["relation"],
                    "weight": edge["weight"],
                    "entities": edge.get("entities", []),
                    "provenance": edge["provenance"],
                }
                if target_id in states:
                    if reason not in states[target_id]["expansion_reasons"]:
                        states[target_id]["expansion_reasons"].append(reason)
                    continue
                if expanded >= self.max_expanded_chunks:
                    break
                inherited = source_state["base_score"] or 1.0
                if source_state["origin"] == "expanded":
                    inherited = source_state["graph_score"]
                score = inherited * edge["weight"] * (0.5 ** source_state["hop"])
                state = {
                    "chunk_id": target_id,
                    "origin": "expanded",
                    "hop": source_state["hop"] + 1,
                    "base_rank": None,
                    "base_score": 0.0,
                    "rerank_score": None,
                    "channels": [],
                    "expansion_reasons": [reason],
                    "graph_score": score,
                }
                states[target_id] = state
                candidates.append(state)
                queue.append(target_id)
                expanded += 1
                if expanded >= self.max_expanded_chunks:
                    break
        return candidates

    @staticmethod
    def _rank(candidates):
        # One fixed score scale for both origins: base retrieval plus graph support.
        # Expanded chunks have no direct retrieval score, so support must exceed a
        # retained seed's base score to outrank it; no origin gets a reserved slot.
        scored = [
            {
                **candidate,
                "score": candidate["base_score"] + candidate["graph_score"],
            }
            for candidate in candidates
        ]
        ordered = sorted(
            scored,
            key=lambda item: (
                -item["score"],
                0 if item["origin"] == "seed" else 1,
                item["base_rank"] if item["base_rank"] is not None else len(scored) + 1,
                item["hop"],
                item["chunk_id"],
            ),
        )
        return [{**candidate, "rank": rank} for rank, candidate in enumerate(ordered, 1)]

    def _pack(self, ranked, graph):
        token_budget = self.retrieval.settings.context_tokens
        char_budget = self.retrieval.settings.context_chars
        count = self._counter()
        blocks, evidence, omitted = [], [], []
        for item in ranked:
            chunk = graph["chunks"][item["chunk_id"]]
            citation = "E" + stable_id(chunk.id)
            header = f"[{citation}] {chunk.locator}\n{chunk.heading}\n"

            def fits(content, header=header):
                combined = "\n\n".join([*blocks, header + content])
                return len(combined) <= char_budget and count(combined) <= token_budget

            content = snippet(chunk.content, fits)
            if not content:
                omitted.append(chunk.id)
                continue
            blocks.append(header + content)
            evidence.append(
                {
                    "citation_id": citation,
                    "chunk_id": chunk.id,
                    "parent_id": chunk.parent_id,
                    "source": chunk.source,
                    "locator": chunk.locator,
                    "page": chunk.page,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "modality": chunk.modality,
                    "bbox": chunk.bbox,
                    "coordinate_space": chunk.coordinate_space,
                    "image_path": chunk.image_path,
                    "caption_source": chunk.caption_source,
                    "caption_locator": chunk.caption_locator,
                    "content": content,
                    "truncated": content != chunk.content,
                    "metadata": chunk.metadata,
                }
            )
        combined = "\n\n".join(blocks)
        return evidence, {
            "budget": {"tokens": token_budget, "characters": char_budget},
            "used_tokens": count(combined),
            "used_characters": len(combined),
            "omitted_chunk_ids": omitted,
        }


def searchable_chunk_text(chunk):
    return f"{chunk.heading}\n{chunk.content}"


def _without_endpoints(edge):
    return {key: value for key, value in edge.items() if key not in {"source", "target"}}


def _elapsed(started):
    return round((perf_counter() - started) * 1000, 3)
