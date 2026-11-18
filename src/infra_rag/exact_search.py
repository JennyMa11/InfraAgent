"""Exact cosine control for local experiments; production ANN remains unchanged."""


class ExactCollection:
    def __init__(self, chunks, vectors):
        import numpy as np

        self.np = np
        self.chunks = chunks
        self.vectors = np.asarray(vectors, dtype=np.float64)
        norms = np.linalg.norm(self.vectors, axis=1)
        if not np.isfinite(self.vectors).all() or (norms <= 0).any():
            raise ValueError("Invalid dense index vectors")
        self.vectors = self.vectors / norms[:, None]

    def query(self, query_embeddings, n_results, where=None):
        np = self.np
        if where is not None:
            raise ValueError("Exact development control does not support filters")
        ids, distances = [], []
        for query in query_embeddings:
            query = np.asarray(query, dtype=np.float64)
            norm = np.linalg.norm(query)
            if not np.isfinite(query).all() or norm <= 0:
                raise ValueError("Invalid query vector")
            scores = self.vectors @ (query / norm)
            ranked = sorted(
                zip(self.chunks, map(float, scores), strict=True),
                key=lambda item: (-item[1], item[0].id),
            )[:n_results]
            ids.append([c.id for c, _ in ranked])
            distances.append([1 - score for _, score in ranked])
        return {"ids": ids, "distances": distances}
