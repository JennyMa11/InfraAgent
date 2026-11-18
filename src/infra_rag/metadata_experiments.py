"""Corpus-only metadata navigation for isolated offline retrieval controls."""

from collections import defaultdict
from pathlib import Path

from .benchmarking import canonical_hash, digest
from .encoding import dot
from .lexical import BM25Index
from .models import Chunk
from .recall_experiments import rank_fusion, supplement
from .service import lexical_statistics

VERSION = "structure-only-document-navigation-v1"
ARMS = ("B", "D", "H", "M")


def document_views(chunks, root):
    """Never use chunk bodies, labels, or machine-specific absolute paths as search text."""
    grouped = defaultdict(list)
    hashes = {}
    owners = {}
    for chunk in chunks:
        source = Path(chunk.source).resolve()
        relative = source.relative_to(root.resolve()).as_posix()
        if source not in hashes:
            hashes[source] = digest(source)
        key = canonical_hash([relative, hashes[source], chunk.metadata.get("release")])
        grouped[key].append((chunk, relative))
        owners[chunk.id] = key
    views = []
    records = {}
    for key, items in sorted(grouped.items()):
        first, relative = items[0]
        fields = {"title": Path(relative).stem, "path": relative}
        for field in ("product", "release"):
            fields[field] = sorted(
                {str(c.metadata[field]) for c, _ in items if c.metadata.get(field)}
            )
        fields["headings"] = sorted({c.heading for c, _ in items if c.heading})
        text = "\n".join(
            f"{name}: {', '.join(value) if isinstance(value, list) else value}"
            for name, value in fields.items()
            if value
        )
        views.append(Chunk(key, key, first.source, text, "infra"))
        records[key] = {"fields": fields, "source_sha256": hashes[Path(first.source).resolve()]}
    return views, owners, records


class MetadataNavigator:
    def __init__(self, chunks, vectors, encoder, root):
        self.chunks = list(chunks)
        self.vectors = list(vectors)
        if len(self.chunks) != len(self.vectors):
            raise ValueError("body vectors must match corpus order")
        self.encoder = encoder
        self.views, self.owners, self.records = document_views(self.chunks, root)
        self.lexical = BM25Index(self.chunks, statistics=lexical_statistics(self.chunks))
        self.meta_lexical = BM25Index(self.views, statistics=lexical_statistics(self.views))
        self.meta_vectors = encoder.encode([v.content for v in self.views])

    @staticmethod
    def dense(items, vectors, query, allowed=None, k=30):
        scores = [
            (c.id, dot(query, vector))
            for c, vector in zip(items, vectors, strict=True)
            if allowed is None or c.id in allowed
        ]
        return sorted((s for s in scores if s[1] > 0), key=lambda s: (-s[1], s[0]))[:k]

    def retrieve(self, query):
        vector = self.encoder.encode([query], query=True)[0]
        meta_channels = [
            self.meta_lexical.search(query, 30),
            self.dense(self.views, self.meta_vectors, vector),
        ]
        documents = [
            cid
            for cid, _ in rank_fusion(
                [[{"chunk_id": cid} for cid, _ in ranking] for ranking in meta_channels]
            )[:5]
        ]
        allowed = {cid for cid, owner in self.owners.items() if owner in documents}
        # Filter after global BM25 scoring: IDF/length statistics stay unchanged.
        lexical = [(cid, score) for cid, score in self.lexical.search(query) if cid in allowed][:30]
        dense = self.dense(self.chunks, self.vectors, vector, allowed)
        channels = [
            [{"chunk_id": cid, "score": score} for cid, score in r] for r in (lexical, dense)
        ]
        pool = rank_fusion(channels)
        return pool, {
            "documents": documents,
            "metadata_channels": meta_channels,
            "body_channels": channels,
            "eligible_body_count": len(allowed),
            "global_lexical_documents": len(self.chunks),
            "empty_reason": "no_metadata_hit" if not documents else None,
        }


def candidate_pool(arm, base, hierarchy=(), deeper=()):
    if arm == "B":
        pool = [(h["chunk_id"], h["score"]) for h in base]
    elif arm == "H":
        pool = list(hierarchy)
    elif arm in {"D", "M"}:
        ranking = deeper if arm == "D" else hierarchy
        pool = supplement(base, [[{"chunk_id": cid} for cid, _ in ranking]], limit=30)
    else:
        raise ValueError("unknown experiment arm")
    if len(pool) > 90 or len({cid for cid, _ in pool}) != len(pool):
        raise ValueError("candidate budget or uniqueness violation")
    return pool


def loss_stage(row, document_complete=None):
    if not row["answerable"]:
        return None
    if document_complete is False:
        return "document_filter"
    if not row["candidate_complete"]:
        return "body_recall"
    if not row["top15_complete"]:
        return "rerank"
    if not row["delivered"]["complete"]:
        return "delivery"
    return "complete"
