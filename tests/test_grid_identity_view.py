from dataclasses import replace

import pytest

from infra_rag.grid_identity_view import canonical_points
from infra_rag.models import Chunk


def test_only_identical_id_duplicates_are_canonicalized_with_alias_positions():
    a = Chunk("a", "p", "source", "body", "infra")
    b = replace(a, id="b")
    chunks, vectors, duplicates = canonical_points([a, a, b], [[1.0, 0.0], [1.0, 0.0], [1.0, 0.0]])
    assert [c.id for c in chunks] == ["a", "b"]
    assert len(vectors) == 2 and duplicates == [
        {"id": "a", "first_row": 0, "duplicate_row": 1, "chunk_and_vector_identical": True}
    ]


def test_conflicting_content_locator_metadata_or_vector_is_not_silently_dropped():
    a = Chunk("a", "p", "source", "body", "infra")
    for other in [
        replace(a, content="different"),
        replace(a, locator="another"),
        replace(a, metadata={"version": "different"}),
    ]:
        with pytest.raises(ValueError, match="Conflicting"):
            canonical_points([a, other], [[1.0, 0.0], [1.0, 0.0]])
    with pytest.raises(ValueError, match="Conflicting"):
        canonical_points([a, a], [[1.0, 0.0], [0.0, 1.0]])
