"""Controlled embedding/chunk experiments: source intervals, sampling and paired gates."""

from bisect import bisect_right
from collections import defaultdict
from dataclasses import asdict, replace
from difflib import SequenceMatcher

from .benchmarking import canonical_hash
from .chunking import chunk_text, stable_id
from .config import Settings
from .models import Chunk
from .preprocessing import clean_lines, units

CHUNK_ARMS = ("structure", "window", "overlap")
MODEL_ARMS = ("bge", "qwen")
BASELINE = "bge-structure-hybrid_rerank"
VERSION = "embedding-chunks-v1"


def normalize(text):
    """Only whitespace is ignored; retain case, punctuation, negation and numbers."""
    return "".join(text.split())


def source_document(text, sha256):
    lines, changes = clean_lines(text)
    cleaned = "\n".join(lines)
    normalized_offsets, cursor = [], 0
    for line in lines:
        normalized_offsets.append(cursor)
        cursor += len(normalize(line))
    normalized_offsets.append(cursor)
    return {
        "text": cleaned,
        "normalized": normalize(cleaned),
        "line_normalized_offsets": normalized_offsets,
        "sha256": sha256,
        "changes": changes,
    }


def mapped_chunk(chunk, document):
    """Map only actual body characters to frozen source; synthetic fences earn no credit."""
    text = normalize(chunk.content)
    if "text_char_range" in chunk.metadata:
        start, end = chunk.metadata["text_char_range"]
        if document["text"][start:end] != chunk.content:
            raise ValueError("window body differs from the frozen source interval")
        ranges = [[0, len(normalize(document["text"][:start])), len(text)]] if text else []
    else:
        offsets = document["line_normalized_offsets"]
        if not chunk.start_line or not chunk.end_line:
            raise ValueError("structural chunks require source line intervals")
        start, end = offsets[chunk.start_line - 1], offsets[chunk.end_line]
        original = document["normalized"][start:end]
        match = original.find(text)
        if match >= 0:
            ranges = [[0, start + match, len(text)]] if text else []
        else:
            ranges = [
                [m.a, start + m.b, m.size]
                for m in SequenceMatcher(None, text, original, autojunk=False).get_matching_blocks()
                if m.size
            ]
    for body_start, source_start, size in ranges:
        if (
            text[body_start : body_start + size]
            != document["normalized"][source_start : source_start + size]
        ):
            raise ValueError("source mapping mismatch")
    return replace(
        chunk,
        metadata={
            **chunk.metadata,
            "source_normalized_ranges": ranges,
            "source_sha256": document["sha256"],
            "range_version": VERSION,
        },
    )


def chunk_variants(original_chunks, documents, counter):
    """Hold cleanup/token limits fixed; never use the embedding under test to split."""
    result = {"structure": [mapped_chunk(c, documents[c.source]) for c in original_chunks]}
    metadata = {c.source: c.metadata for c in original_chunks}
    for arm, strategy, overlap in (("window", "window", 0), ("overlap", "window_overlap", 90)):
        chunks = []
        for source in sorted(documents):
            document = documents[source]
            lines = document["text"].splitlines()
            structural = units(lines)
            sections = [(u["start"], u["heading"]) for u in structural if u["kind"] == "heading"]
            starts = [s[0] for s in sections]
            settings = Settings(chunk_strategy=strategy, chunk_size=450, chunk_overlap=overlap)
            for chunk in chunk_text(document["text"], source, "infra", counter, settings):
                section = bisect_right(starts, chunk.start_line) - 1
                line, heading = sections[section] if section >= 0 else (1, "")
                chunk.heading = heading
                chunk.parent_id = stable_id(source, VERSION, "section", line, heading)
                chunk.metadata = {
                    **{
                        k: v
                        for k, v in metadata[source].items()
                        if k
                        in {
                            "collection",
                            "document_id",
                            "url",
                            "commit",
                            "release",
                            "sha256",
                            "product",
                        }
                    },
                    **chunk.metadata,
                    "preprocessing_version": VERSION,
                    "body_type": arm,
                }
                chunks.append(mapped_chunk(chunk, document))
        result[arm] = chunks
    return result


def merge_intervals(intervals):
    result = []
    for start, end in sorted(intervals):
        if end <= start:
            continue
        if result and start <= result[-1][1]:
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    return result


def delivered_intervals(evidence, documents):
    """Credit only mapped, delivered prefixes; merge overlap without bridging gaps."""
    intervals = defaultdict(list)
    for row in evidence:
        source, metadata = row["source"], row.get("metadata", {})
        document = documents[source]
        if metadata.get("source_sha256") != document["sha256"]:
            raise ValueError("evidence source hash does not match frozen source")
        body = normalize(row["content"])
        for body_start, source_start, size in metadata["source_normalized_ranges"]:
            size = min(size, len(body) - body_start)
            if size <= 0:
                continue
            if (
                body[body_start : body_start + size]
                != document["normalized"][source_start : source_start + size]
            ):
                raise ValueError("delivered body differs from mapped source")
            intervals[source].append((source_start, source_start + size))
    return {source: merge_intervals(ranges) for source, ranges in intervals.items()}


def freeze_gold(question, documents):
    if not question["answerable"]:
        return []
    groups = []
    for group in question["evidence_alternatives"]:
        requirements = []
        for span in group["spans"]:
            source, target = span["absolute_source"], normalize(span["text"])
            original = documents[source]["normalized"]
            offsets, cursor = [], 0
            while target and (offset := original.find(target, cursor)) >= 0:
                offsets.append([offset, offset + len(target)])
                cursor = offset + 1
            if not offsets:
                raise ValueError(f"{question['id']}: frozen gold absent from cleaned source")
            requirements.append({"source": source, "occurrences": offsets})
        if not requirements:
            raise ValueError("empty evidence alternative")
        groups.append(requirements)
    return groups


def interval_score(intervals, gold):
    if not gold:
        return None
    coverages = []
    for group in gold:
        found = 0
        for requirement in group:
            covered = intervals.get(requirement["source"], [])
            found += any(
                any(a <= start and b >= end for a, b in covered)
                for start, end in requirement["occurrences"]
            )
        coverages.append(found / len(group))
    return {"complete": int(max(coverages) == 1), "coverage": max(coverages)}


def score_evidence(evidence, question, documents):
    return interval_score(delivered_intervals(evidence, documents), question["gold_intervals"])


def chunk_evidence(chunk):
    return {"source": chunk.source, "content": chunk.content, "metadata": chunk.metadata}


def deterministic_sample(cases):
    selected = []
    for dataset, answerable, count in (
        ("official", True, 8),
        ("official", False, 2),
        ("repository", True, 10),
    ):
        buckets = defaultdict(list)
        for case in cases:
            if case["dataset"] == dataset and case["answerable"] == answerable:
                buckets[case["question_type"]].append(case)
        for bucket in buckets.values():
            bucket.sort(key=lambda c: canonical_hash([42, c["dataset"], c["id"]]))
        layer = []
        while len(layer) < count:
            progress = False
            for kind in sorted(buckets):
                if buckets[kind] and len(layer) < count:
                    layer.append(buckets[kind].pop(0))
                    progress = True
            if not progress:
                raise ValueError("not enough cases for the frozen answer sample")
        selected.extend((c["dataset"], c["id"]) for c in layer)
    return selected


def ratio(numerator, denominator):
    return {
        "numerator": numerator,
        "denominator": denominator,
        "value": numerator / denominator if denominator else None,
    }


def select_candidate(summaries):
    """Quality gates are per dataset; latency is measured, never guessed from replay."""
    base = summaries[BASELINE]
    gates, qualified = {}, []
    for arm in CHUNK_ARMS:
        name = f"qwen-{arm}-hybrid_rerank"
        row = summaries[name]
        net = sum(
            row[ds]["delivery"]["numerator"] - base[ds]["delivery"]["numerator"]
            for ds in ("official", "repository")
        )
        quality = (
            all(
                row[ds]["delivery"]["numerator"] >= base[ds]["delivery"]["numerator"]
                for ds in ("official", "repository")
            )
            and net >= 2
        )
        timing = row.get("warm_latency")
        baseline_timing = base.get("warm_latency")
        latency = (
            None
            if not timing or not baseline_timing
            else (timing["p95_ms"] <= 1.5 * baseline_timing["p95_ms"])
        )
        gates[name] = {"quality": quality, "latency": latency, "net_delivery": net}
        if quality and latency is True and not row.get("errors"):
            qualified.append(name)
    if not qualified:
        return {
            "candidate": "qwen-structure-hybrid_rerank",
            "qualified": False,
            "gates": gates,
            "reason": "No Qwen arm passed all gates; structure is diagnostic only.",
        }
    qualified.sort(
        key=lambda name: (
            -gates[name]["net_delivery"],
            -sum(
                summaries[name][ds]["candidate_complete"]["numerator"]
                for ds in ("official", "repository")
            ),
            summaries[name]["warm_latency"]["p95_ms"],
            name,
        )
    )
    return {"candidate": qualified[0], "qualified": True, "gates": gates}


def serialize_chunks(chunks):
    return [asdict(chunk) for chunk in chunks]


def deserialize_chunks(rows):
    return [Chunk(**row) for row in rows]
