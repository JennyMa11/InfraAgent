"""One dense point per stable ID; conflicting duplicate identities are never accepted."""

from dataclasses import asdict


def canonical_points(chunks, vectors):
    if len(chunks) != len(vectors):
        raise ValueError("Chunk/vector length mismatch")
    seen = {}
    unique = []
    values = []
    duplicates = []
    for row, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True)):
        if chunk.id in seen:
            first, position = seen[chunk.id]
            if asdict(chunk) != asdict(unique[position]) or list(vector) != list(values[position]):
                raise ValueError("Conflicting duplicate ID: " + chunk.id)
            duplicates.append(
                {
                    "id": chunk.id,
                    "first_row": first,
                    "duplicate_row": row,
                    "chunk_and_vector_identical": True,
                }
            )
        else:
            seen[chunk.id] = (row, len(unique))
            unique.append(chunk)
            values.append(vector)
    return unique, values, duplicates
