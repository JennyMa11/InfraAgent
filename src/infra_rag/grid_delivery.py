"""Grid v2 source interval scoring; omitted text cannot bridge adjacent chunks."""

from dataclasses import replace

from .embedding_experiments import delivered_intervals, freeze_gold, interval_score, mapped_chunk


def score_delivery(evidence, question, chunks, documents):
    if not question["answerable"]:
        return None
    mapped = []
    for item in evidence:
        original = chunks[item["chunk_id"]]
        if item["source"] != original.source or not original.content.startswith(item["content"]):
            raise ValueError("Delivered text is not a source chunk prefix")
        chunk = mapped_chunk(original, documents[original.source])
        mapped.append({**item, "metadata": chunk.metadata})
        for alias in original.metadata.get("source_aliases", []):
            source = alias["source"]
            if source not in documents:
                raise ValueError("Frozen source alias missing from document manifest")
            start, end = alias["metadata"]["original_lines"]
            other = replace(
                original, source=source, start_line=start, end_line=end, metadata=alias["metadata"]
            )
            other = mapped_chunk(other, documents[source])
            mapped.append({**item, "source": source, "metadata": other.metadata})
    return interval_score(delivered_intervals(mapped, documents), freeze_gold(question, documents))
