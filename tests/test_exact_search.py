import pytest

from infra_rag.exact_search import ExactCollection
from infra_rag.models import Chunk


def test_exact_scores_normalize_vectors_and_ties_by_id():
    pytest.importorskip("numpy")
    chunks = [
        Chunk("b", "p", "s", "x", "infra"),
        Chunk("a", "p", "s", "x", "infra"),
        Chunk("c", "p", "s", "y", "infra"),
    ]
    collection = ExactCollection(chunks, [[2, 0], [1, 0], [0, 1]])
    result = collection.query([[3, 0]], 2)
    assert result == {"ids": [["a", "b"]], "distances": [[0.0, 0.0]]}
    assert collection.query([[3, 0]], 3)["ids"][0] == ["a", "b", "c"]
    with pytest.raises(ValueError):
        collection.query([[0, 0]], 1)
