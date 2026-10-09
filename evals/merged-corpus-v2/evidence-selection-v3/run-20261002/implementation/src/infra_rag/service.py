import json
import math
import os
import re
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from threading import RLock
from time import perf_counter

from .chunking import IMAGE_SUFFIXES, TEXT_SUFFIXES, parse_file, stable_id
from .config import Settings
from .context import pack_context
from .encoding import BGEEncoder, CLIPEncoder, DemoEncoder, dot, tokenize
from .lexical import BM25Index
from .models import Chunk, Hit
from .vector_cache import CachedEncoder, VectorCache, content_hash


def search_text(chunk):
    return f"{Path(chunk.source).stem}\n{chunk.heading}\n{chunk.content}"


def lexical_statistics(chunks, heading_context=False):
    documents = [
        Counter(tokenize(search_text(c) if heading_context else c.content + " " + c.heading))
        for c in chunks
    ]
    frequencies = Counter(term for doc in documents for term in doc)
    lengths = [sum(doc.values()) for doc in documents]
    average = sum(lengths) / (len(documents) or 1) or 1
    return documents, frequencies, lengths, average


def bm25(query, chunks, statistics=None, top_k=None):
    if isinstance(statistics, BM25Index):
        return statistics.search(query, top_k=top_k)
    documents, frequencies, lengths, average = statistics or lexical_statistics(chunks)
    terms = set(tokenize(query))
    results = []
    for chunk, doc, length in zip(chunks, documents, lengths, strict=True):
        score = 0.0
        for term in terms:
            frequency = doc[term]
            if not frequency:
                continue
            idf = math.log(
                1 + (len(documents) - frequencies[term] + 0.5) / (frequencies[term] + 0.5)
            )
            score += idf * frequency * 2.5 / (frequency + 1.5 * (0.25 + 0.75 * length / average))
        if score > 0:
            results.append((chunk.id, score))
    return sorted(results, key=lambda item: (-item[1], item[0]))


def fuse(rankings, constant=60):
    scores, channels = defaultdict(float), defaultdict(list)
    for channel, ranking in rankings.items():
        seen = set()
        for rank, (chunk_id, _) in enumerate(ranking, 1):
            if chunk_id in seen:
                continue
            seen.add(chunk_id)
            scores[chunk_id] += 1 / (constant + rank)
            channels[chunk_id].append(channel)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0])), channels


class RetrievalService:
    def __init__(self, settings=None):
        settings = settings or Settings()
        self.settings = settings
        self.index_fingerprint = settings.fingerprint()
        self.lock = RLock()
        self.snapshot = settings.data_dir / "index.json"
        self.chunks, self.vectors = [], []
        self.source_manifest = {}
        self.vector_cache = VectorCache(settings.data_dir / "vectors.sqlite3")
        self.last_update = {}
        self.encoder = None
        self.lexical_cache = {}
        self.clip = None
        self.reranker = None
        self.client = None
        self.text_collection = self.clip_collection = None
        if self.snapshot.exists():
            state = json.loads(self.snapshot.read_text())
            if state["fingerprint"] != settings.fingerprint():
                raise ValueError("index configuration mismatch; use a separate --data-dir")
            self.chunks = [Chunk(**item) for item in state["chunks"]]
            self.vectors = state["vectors"]
            self.source_manifest = state.get("sources", {})
        self._index_parents()

    def _index_parents(self):
        self.parent_index = defaultdict(list)
        for chunk in self.chunks:
            self.parent_index[chunk.parent_id].append(chunk)

    def get_parent(self, parent_id):
        with self.lock:
            return list(self.parent_index.get(parent_id, []))

    def _encoder(self):
        if self.encoder is None:
            self.encoder = (
                DemoEncoder()
                if self.settings.backend == "demo"
                else BGEEncoder(self.settings.embedding_model)
            )
        return self.encoder

    def _clip(self):
        if self.clip is None:
            self.clip = CLIPEncoder(self.settings.clip_image_model, self.settings.clip_text_model)
        return self.clip

    def _collections(self, chunks, vectors):
        import chromadb

        if self.client is None:
            self.client = chromadb.PersistentClient(path=str(self.settings.data_dir / "chroma"))
        version = stable_id(
            json.dumps(self.settings.fingerprint(), sort_keys=True),
            json.dumps([asdict(c) for c in chunks], sort_keys=True),
        )
        text_collection = self.client.get_or_create_collection(
            "text-" + version,
            embedding_function=None,
            metadata={"hnsw:space": "cosine"},
        )
        if chunks and text_collection.count() != len(chunks):
            for start in range(0, len(chunks), 128):
                batch = chunks[start : start + 128]
                text_collection.upsert(
                    ids=[c.id for c in batch],
                    embeddings=vectors[start : start + 128],
                    documents=[c.content for c in batch],
                    metadatas=[
                        {
                            "domain": c.domain,
                            "modality": c.modality,
                            "parent_id": c.parent_id,
                            "chunk_type": c.chunk_type,
                        }
                        for c in batch
                    ],
                )
        clip_collection = None
        if self.settings.multimodal:
            clip_collection = self.client.get_or_create_collection(
                "clip-" + version,
                embedding_function=None,
                metadata={"hnsw:space": "cosine"},
            )
            if chunks and clip_collection.count() != len(chunks):
                cached = self._clip_vectors(chunks)
                for start in range(0, len(chunks), 64):
                    batch = chunks[start : start + 64]
                    ordered = batch
                    clip_collection.upsert(
                        ids=[c.id for c in ordered],
                        embeddings=[cached[c.id] for c in ordered],
                        documents=[c.content for c in ordered],
                        metadatas=[
                            {
                                "domain": c.domain,
                                "modality": c.modality,
                                "parent_id": c.parent_id,
                                "chunk_type": c.chunk_type,
                            }
                            for c in ordered
                        ],
                    )
        return text_collection, clip_collection

    def _text_namespace(self):
        return {
            "backend": self.settings.backend,
            "model": self.settings.embedding_model if self.settings.backend == "bge" else "hash-v1",
            "pooling": "token-window-mean-v1",
        }

    def _clip_vectors(self, chunks):
        vectors = {}
        statistics = {"encoded": 0, "reused": 0}
        for modality in ("text", "image"):
            group = [c for c in chunks if c.modality == modality]
            inputs = [c.image_path if modality == "image" else c.content for c in group]
            namespace = {
                "model": self.settings.clip_image_model
                if modality == "image"
                else self.settings.clip_text_model,
                "modality": modality,
                "pooling": "token-window-mean-v1",
            }
            identities = [content_hash(path) for path in inputs] if modality == "image" else inputs
            encoded, counts = (
                self.vector_cache.encode(
                    namespace,
                    inputs,
                    lambda values, modality=modality: (
                        self._clip().encode_images(values)
                        if modality == "image"
                        else self._clip().encode_texts(values)
                    ),
                    identities=identities,
                )
                if group
                else ([], {"encoded": 0, "reused": 0})
            )
            vectors.update(zip([c.id for c in group], encoded, strict=True))
            for key in statistics:
                statistics[key] += counts[key]
        self.last_update["clip_vectors"] = statistics
        return vectors

    def _commit(self, chunks, source_manifest=None):
        if self.settings.fingerprint() != self.index_fingerprint:
            raise ValueError("index configuration mismatch; use a separate --data-dir")
        namespace = self._text_namespace()

        def text(c):
            return search_text(c) if self.settings.heading_context else c.content

        seeds = {
            self.vector_cache.key(namespace, text(c)): v
            for c, v in zip(self.chunks, self.vectors, strict=True)
        }
        vectors, counts = (
            self.vector_cache.encode(
                namespace,
                [text(c) for c in chunks],
                lambda values: self._encoder().encode(values),
                seeds=seeds,
            )
            if chunks
            else ([], {"encoded": 0, "reused": 0})
        )
        manifest = self.source_manifest if source_manifest is None else source_manifest
        collections = None
        if self.settings.backend == "bge":
            collections = self._collections(chunks, vectors)
        self.settings.data_dir.mkdir(parents=True, exist_ok=True)
        temporary = self.snapshot.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(
                {
                    "fingerprint": self.settings.fingerprint(),
                    "chunks": [asdict(c) for c in chunks],
                    "vectors": vectors,
                    "sources": manifest,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        os.replace(temporary, self.snapshot)
        self.chunks, self.vectors = chunks, vectors
        self.source_manifest = manifest
        self.last_update["text_vectors"] = counts
        self.lexical_cache.clear()
        self._index_parents()
        if collections:
            self.text_collection, self.clip_collection = collections

    def ingest(self, path: Path, domain="general"):
        with self.lock:
            if self.settings.fingerprint() != self.index_fingerprint:
                raise ValueError("index configuration mismatch; use a separate --data-dir")
            files = (
                [path]
                if path.is_file()
                else sorted(
                    p
                    for p in path.rglob("*")
                    if p.is_file()
                    and self.settings.data_dir.resolve() not in p.resolve().parents
                    and p.suffix.lower() in TEXT_SUFFIXES | IMAGE_SUFFIXES | {".pdf"}
                    and not any(part.startswith(".") for part in p.relative_to(path).parts)
                    and not p.name.lower().endswith(
                        tuple(suffix + ".txt" for suffix in IMAGE_SUFFIXES)
                    )
                )
            )
            if not files:
                raise ValueError(f"no supported documents found: {path}")
            incoming, changed = [], []
            cached_encoder = None
            manifest = dict(self.source_manifest)
            missing_assets = {
                c.source for c in self.chunks if c.image_path and not Path(c.image_path).exists()
            }
            for file in files:
                source = str(file.resolve())
                record = self._source_record(file, domain)
                if manifest.get(source) == record and source not in missing_assets:
                    continue
                if cached_encoder is None:
                    cached_encoder = CachedEncoder(
                        self._encoder(), self.vector_cache, self._text_namespace()
                    )
                incoming.extend(
                    parse_file(
                        file,
                        domain,
                        cached_encoder,
                        self.settings,
                        self._clip()
                        if self.settings.multimodal
                        and file.suffix.lower() in IMAGE_SUFFIXES | {".pdf"}
                        else None,
                    )
                )
                if self._source_record(file, domain) != record:
                    raise ValueError(f"source changed during ingestion: {file}")
                manifest[source] = record
                changed.append(source)
            self.last_update = {
                "parsing_text_vectors": cached_encoder.counts
                if cached_encoder
                else {
                    "encoded": 0,
                    "reused": 0,
                }
            }
            if changed:
                changed_sources = set(changed)
                chunks = [c for c in self.chunks if c.source not in changed_sources] + incoming
                self._commit(chunks, manifest)
            return {
                "files": len(files),
                "changed_files": len(changed),
                "skipped_files": len(files) - len(changed),
                "chunks": len(incoming),
                "total_chunks": len(self.chunks),
                "vectors": self.last_update,
            }

    def _source_record(self, file, domain):
        sidecar = file.with_suffix(file.suffix + ".txt")
        return {
            "sha256": content_hash(file),
            "domain": domain,
            "sidecar_sha256": content_hash(sidecar)
            if file.suffix.lower() in IMAGE_SUFFIXES and sidecar.exists()
            else None,
            "parser_version": 1,
        }

    def delete(self, source):
        with self.lock:
            remaining = [c for c in self.chunks if c.source != source]
            count = len(self.chunks) - len(remaining)
            if count:
                manifest = {k: v for k, v in self.source_manifest.items() if k != source}
                self.last_update = {}
                self._commit(remaining, manifest)
            return count

    def search(
        self,
        query,
        top_k=5,
        domain=None,
        modality=None,
        strategy="hybrid",
        diagnostics=None,
        context_pack=None,
    ):
        started = perf_counter()
        timings = {}
        if diagnostics is not None:
            diagnostics.clear()
            diagnostics.update(
                {
                    "channels": {},
                    "timings_ms": timings,
                    "rerank": {"enabled": False},
                }
            )
        if not query.strip() or not 1 <= top_k <= 100:
            raise ValueError("query must be nonempty; top_k must be in [1, 100]")
        if strategy not in {"bm25", "dense", "hybrid", "clip"}:
            raise ValueError("unknown retrieval strategy")
        if modality not in {None, "text", "image"}:
            raise ValueError("modality must be text or image")
        if strategy == "clip" and not self.settings.multimodal:
            raise ValueError("clip retrieval requires multimodal mode")
        with self.lock:
            timings["lock_wait"] = (perf_counter() - started) * 1000
            phase = perf_counter()
            eligible = [
                c
                for c in self.chunks
                if (domain is None or c.domain == domain)
                and (modality is None or c.modality == modality)
            ]
            timings["filter"] = (perf_counter() - phase) * 1000
            if diagnostics is not None:
                diagnostics["eligible_chunks"] = len(eligible)
            if not eligible:
                if context_pack is not None:
                    context_pack.clear()
                    context_pack.update({"evidence": [], "context": ""})
                if diagnostics is not None:
                    diagnostics.update({"fusion": [], "candidates": [], "final": []})
                    timings["total"] = (perf_counter() - started) * 1000
                return []
            candidate_k = max(top_k, self.settings.candidate_k)
            rankings = {}
            phase = perf_counter()
            if strategy in {"bm25", "hybrid"}:
                cache_key = (domain, modality, self.settings.lexical_query_mode)
                if cache_key not in self.lexical_cache:
                    self.lexical_cache[cache_key] = BM25Index(
                        eligible,
                        statistics=lexical_statistics(eligible, self.settings.heading_context),
                        query_mode=self.settings.lexical_query_mode,
                    )
                rankings["bm25"] = bm25(
                    query, eligible, self.lexical_cache[cache_key], candidate_k
                )[:candidate_k]
            timings["bm25"] = (perf_counter() - phase) * 1000
            phase = perf_counter()
            if strategy in {"dense", "hybrid", "clip"}:
                if self.settings.backend == "demo":
                    vector = self._encoder().encode([query], query=True)[0]
                    allowed = {c.id for c in eligible}
                    rankings["dense"] = sorted(
                        [
                            (c.id, dot(vector, v))
                            for c, v in zip(self.chunks, self.vectors, strict=True)
                            if c.id in allowed and dot(vector, v) > 0
                        ],
                        key=lambda item: (-item[1], item[0]),
                    )[:candidate_k]
                else:
                    if self.text_collection is None:
                        self.text_collection, self.clip_collection = self._collections(
                            self.chunks,
                            self.vectors,
                        )
                    filters = []
                    if domain:
                        filters.append({"domain": domain})
                    if modality:
                        filters.append({"modality": modality})
                    where = (
                        (filters[0] if len(filters) == 1 else {"$and": filters})
                        if filters
                        else None
                    )
                    if strategy != "clip":
                        result = self.text_collection.query(
                            query_embeddings=self._encoder().encode([query], query=True),
                            n_results=min(candidate_k, len(eligible)),
                            where=where,
                        )
                        rankings["dense"] = list(
                            zip(
                                result["ids"][0],
                                result["distances"][0],
                                strict=True,
                            )
                        )
                    timings["dense"] = (perf_counter() - phase) * 1000
                    phase = perf_counter()
                    if self.clip_collection is not None and strategy in {"clip", "hybrid"}:
                        result = self.clip_collection.query(
                            query_embeddings=self._clip().encode_query(query),
                            n_results=min(candidate_k, len(eligible)),
                            where=where,
                        )
                        rankings["clip"] = list(
                            zip(
                                result["ids"][0],
                                result["distances"][0],
                                strict=True,
                            )
                        )
            if self.settings.backend == "demo":
                timings["dense"] = (perf_counter() - phase) * 1000
            elif "clip" in rankings:
                timings["clip"] = (perf_counter() - phase) * 1000
            phase = perf_counter()
            if diagnostics is not None:
                diagnostics["candidate_k"] = candidate_k
                diagnostics["channels"] = {
                    name: {
                        "score_kind": "cosine_distance"
                        if name in {"dense", "clip"} and self.settings.backend == "bge"
                        else "bm25_score"
                        if name == "bm25"
                        else "cosine_similarity",
                        "ranking": [
                            {"chunk_id": cid, "rank": rank, "score": float(score)}
                            for rank, (cid, score) in enumerate(ranking, 1)
                        ],
                    }
                    for name, ranking in rankings.items()
                }
            if diagnostics is not None and "dense" in rankings:
                encoder = self._encoder()
                if hasattr(encoder, "token_length"):
                    input_text = getattr(encoder, "instruction", "") + query
                    length = encoder.token_length(input_text)
                    limit = encoder.token_limit
                    diagnostics["dense_query"] = {
                        "input_tokens": length,
                        "window_limit": limit,
                        "windows": max(1, math.ceil(length / limit)),
                        "handling": "token_window_mean",
                    }
                else:
                    diagnostics["dense_query"] = {"handling": "deterministic_hash"}
            fused, channels = fuse(rankings)
            by_id = {c.id: c for c in eligible}
            candidates = (
                fused if self.settings.fusion_candidates == "union" else fused[:candidate_k]
            )
            hits = [
                Hit(by_id[chunk_id], score, channels[chunk_id]) for chunk_id, score in candidates
            ]
            timings["fusion"] = (perf_counter() - phase) * 1000
            if diagnostics is not None:
                kept = {cid for cid, _ in candidates}
                diagnostics["fusion"] = [
                    {"chunk_id": cid, "rank": rank, "rrf_score": score, "retained": cid in kept}
                    for rank, (cid, score) in enumerate(fused, 1)
                ]
                diagnostics["candidates"] = [h.chunk.id for h in hits]
            before_rerank = {h.chunk.id: rank for rank, h in enumerate(hits, 1)}
            phase = perf_counter()
            if self.settings.rerank and hits:
                if self.reranker is None:
                    from sentence_transformers import CrossEncoder

                    self.reranker = CrossEncoder(self.settings.reranker_model)
                pairs = [
                    (
                        query,
                        search_text(hit.chunk)
                        if self.settings.heading_context
                        else hit.chunk.content,
                    )
                    for hit in hits
                ]
                if diagnostics is not None:
                    diagnostics["rerank"] = self._rerank_diagnostics(pairs)
                scores = self.reranker.predict(pairs)
                for hit, score in zip(hits, scores, strict=True):
                    hit.rerank_score = float(score)
                hits.sort(key=lambda h: (-h.rerank_score, -h.score, h.chunk.id))
            timings["rerank"] = (perf_counter() - phase) * 1000
            phase = perf_counter()
            selected_hits = hits[:top_k]
            if self.settings.context_mode == "neighbors":
                encoder = self._encoder()
                count = getattr(encoder, "token_length", len)
                packed = pack_context(
                    selected_hits,
                    self.parent_index,
                    count,
                    self.settings.context_tokens,
                    self.settings.context_chars,
                    domain,
                    modality,
                )
                packed["token_count_method"] = (
                    "embedding_tokenizer"
                    if hasattr(encoder, "token_length")
                    else "unicode_characters"
                )
                if context_pack is not None:
                    context_pack.clear()
                    context_pack.update(packed)
            else:
                for hit in hits[:top_k]:
                    # Put the matched child first, so long parents never truncate away the evidence.
                    siblings = [
                        c
                        for c in self.parent_index[hit.chunk.parent_id]
                        if c.id != hit.chunk.id
                        and (domain is None or c.domain == domain)
                        and (modality is None or c.modality == modality)
                    ]
                    selected = [hit.chunk] + siblings
                    hit.context = "\n\n".join(c.content for c in selected)[
                        : self.settings.context_chars
                    ]
                    hit.sibling_ids = [c.id for c in selected]
                if context_pack is not None:
                    context_pack.clear()
                    context_pack.update(
                        {"mode": "legacy", "per_hit_character_budget": self.settings.context_chars}
                    )
            timings["context"] = (perf_counter() - phase) * 1000
            timings["total"] = (perf_counter() - started) * 1000
            if diagnostics is not None:
                diagnostics["final"] = [
                    {
                        "chunk_id": h.chunk.id,
                        "rank": rank,
                        "before_rerank_rank": before_rerank[h.chunk.id],
                        "rerank_score": h.rerank_score,
                    }
                    for rank, h in enumerate(hits, 1)
                ]
                diagnostics["returned_chunk_ids"] = [h.chunk.id for h in selected_hits]
            return selected_hits

    def _rerank_diagnostics(self, pairs):
        tokenizer = getattr(self.reranker, "tokenizer", None)
        limit = getattr(self.reranker, "max_length", None)
        if limit is None and tokenizer is not None:
            limit = getattr(tokenizer, "model_max_length", None)
        result = {
            "enabled": True,
            "pair_limit": limit if limit and limit < 1000000 else None,
            "pairs": [],
            "scope": "text_and_image_captions",
        }
        if tokenizer is not None:
            for query, document in pairs:
                length = len(tokenizer.encode(query, document, truncation=False))
                result["pairs"].append(
                    {
                        "input_tokens": length,
                        "would_truncate": length > limit if result["pair_limit"] else None,
                    }
                )
        return result

    def cleanup(self, apply=False):
        """Collect only generated objects unreachable from the active snapshot."""
        with self.lock:
            if self.snapshot.exists():
                current = json.loads(self.snapshot.read_text())
                if (
                    current["chunks"] != [asdict(c) for c in self.chunks]
                    or current["fingerprint"] != self.index_fingerprint
                    or self.settings.fingerprint() != self.index_fingerprint
                ):
                    raise ValueError("active snapshot changed; restart before cleanup")
            elif self.chunks:
                raise ValueError("cannot clean an unpublished index")
            version = stable_id(
                json.dumps(self.settings.fingerprint(), sort_keys=True),
                json.dumps([asdict(c) for c in self.chunks], sort_keys=True),
            )
            active = {"text-" + version, "clip-" + version}
            unused_collections = []
            if self.settings.backend == "bge" and (self.settings.data_dir / "chroma").exists():
                import chromadb

                if self.client is None:
                    self.client = chromadb.PersistentClient(
                        path=str(self.settings.data_dir / "chroma")
                    )
                names = [getattr(c, "name", c) for c in self.client.list_collections()]
                unused_collections = [
                    name
                    for name in names
                    if re.fullmatch(r"(?:text|clip)-[a-f0-9]{24}", name) and name not in active
                ]
            assets = self.settings.data_dir / "assets"
            referenced = {Path(c.image_path).resolve() for c in self.chunks if c.image_path}
            unused_assets = (
                [
                    p
                    for p in assets.glob("*.png")
                    if not p.is_symlink()
                    and re.fullmatch(r"[a-f0-9]{24}\.png", p.name)
                    and p.resolve() not in referenced
                ]
                if assets.exists() and not assets.is_symlink()
                else []
            )
            keys = {
                self.vector_cache.key(
                    self._text_namespace(),
                    search_text(c) if self.settings.heading_context else c.content,
                )
                for c in self.chunks
            }
            if self.settings.multimodal:
                for c in self.chunks:
                    namespace = {
                        "model": self.settings.clip_image_model
                        if c.modality == "image"
                        else self.settings.clip_text_model,
                        "modality": c.modality,
                        "pooling": "token-window-mean-v1",
                    }
                    identity = content_hash(c.image_path) if c.modality == "image" else c.content
                    keys.add(self.vector_cache.key(namespace, identity))
            cache = self.vector_cache.prune(keys, apply=apply)
            if apply:
                for name in unused_collections:
                    self.client.delete_collection(name)
                for asset in unused_assets:
                    asset.unlink()
            return {
                "applied": apply,
                "collections": sorted(unused_collections),
                "assets": sorted(str(p) for p in unused_assets),
                "cache": cache,
            }

    def status(self):
        return {
            "backend": self.settings.backend,
            "semantic_model": self.settings.backend == "bge",
            "embedding_model": self.settings.embedding_model
            if self.settings.backend == "bge"
            else "deterministic-hash",
            "reranker_model": self.settings.reranker_model if self.settings.rerank else None,
            "reranker_scope": "text_and_image_captions",
            "candidate_k": self.settings.candidate_k,
            "fusion_candidates": self.settings.fusion_candidates,
            "lexical_query_mode": self.settings.lexical_query_mode,
            "heading_context": self.settings.heading_context,
            "context_chars": self.settings.context_chars,
            "context_tokens": self.settings.context_tokens,
            "context_mode": self.settings.context_mode,
            "rerank": self.settings.rerank,
            "multimodal": self.settings.multimodal,
            "chunks": len(self.chunks),
            "sources": len({c.source for c in self.chunks}),
            "fingerprint": self.settings.fingerprint(),
        }
