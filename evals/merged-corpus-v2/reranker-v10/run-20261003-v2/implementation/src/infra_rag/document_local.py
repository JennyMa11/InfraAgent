"""Original-chunk lexical search scoped only by already retrieved documents."""

from collections import defaultdict

from .benchmarking import canonical_hash
from .original_rag_experiments import TechnicalBM25, additive_pool


class DocumentLocalBM25:
    """Offline control; no evidence labels, question IDs or answer text accepted."""

    def __init__(self, chunks):
        self.chunks = {c.id: c for c in chunks}
        if len(self.chunks) != len(chunks):
            raise ValueError("duplicate corpus IDs")
        grouped = defaultdict(list)
        for chunk in chunks:
            grouped[chunk.source, chunk.metadata.get("release")].append(chunk)
        self.indexes = {key: TechnicalBM25(group) for key, group in grouped.items()}
        self.identity = canonical_hash(
            [
                "document-local-technical-top10-scope5-supplement30-v1",
                [(c.id, c.source, c.metadata.get("release"), c.heading, c.content) for c in chunks],
            ]
        )

    def supplement(self, baseline, query):
        ids = [h["chunk_id"] for h in baseline]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate baseline IDs")
        if len(ids) > 60:
            raise ValueError("baseline must contain at most 60 candidates")
        if any(cid not in self.chunks for cid in ids):
            raise ValueError("unknown baseline ID")
        scopes = []
        for cid in ids[:10]:
            chunk = self.chunks[cid]
            key = chunk.source, chunk.metadata.get("release")
            if key not in scopes:
                scopes.append(key)
            if len(scopes) == 5:
                break
        channels = [
            [
                {"chunk_id": cid, "score": score, "rank": i}
                for i, (cid, score) in enumerate(self.indexes[key].search(query, 30), 1)
            ]
            for key in scopes
        ]
        pool = additive_pool(baseline, channels)
        added = [cid for cid, _ in pool if cid not in set(ids)]
        allowed = set(scopes)
        if any(
            (self.chunks[cid].source, self.chunks[cid].metadata.get("release")) not in allowed
            for cid in added
        ):
            raise ValueError("supplement escaped document scope")
        return pool, {
            "index_identity": self.identity,
            "scopes": [{"source": source, "release": release} for source, release in scopes],
            "channels": channels,
            "added_ids": added,
            "baseline_retained": True,
            "baseline_count": len(ids),
            "candidate_count": len(pool),
            "scope_inputs": ids[:10],
        }
