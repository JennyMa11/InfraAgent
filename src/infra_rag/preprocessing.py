"""Conservative source-preserving cleanup, structural chunks and duplicate audit."""

import hashlib
import re
from collections import defaultdict

from .chunking import stable_id
from .models import Chunk
from .text_chunking import bounded_units, fits

VERSION = "rules-structure-v2-fences"


def fence_open(line):
    # Protect fences nested inside Markdown lists, including indentation beyond 3 spaces.
    match = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
    if not match:
        return None
    marker, rest = match.groups()
    inline = bool(
        rest.strip() and re.search(re.escape(marker[0]) + "{" + str(len(marker)) + r",}\s*$", rest)
    )
    return marker, inline


def fence_close(line, marker):
    return bool(
        re.fullmatch(r"\s*" + re.escape(marker[0]) + "{" + str(len(marker)) + r",}\s*", line)
    )


def clean_lines(text):
    lines = text.splitlines()
    changes = []
    fenced, frontmatter, toc = None, False, False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if i == 0 and stripped == "---":
            frontmatter = True
        elif frontmatter and stripped == "---":
            frontmatter = False
            changes.append({"line": i + 1, "reason": "frontmatter"})
            lines[i] = ""
            continue
        if fenced:
            if fence_close(line, fenced):
                fenced = None
            continue
        opening = fence_open(line)
        if opening:
            marker, inline = opening
            fenced = None if inline else marker
            continue
        heading = re.match(r"^#{1,6}\s+(.+)", stripped)
        if heading:
            toc = bool(re.fullmatch(r"(?:[📑📚]\s*)?(?:目录|Table of Contents)", heading[1], re.I))
        reason = (
            "frontmatter"
            if frontmatter
            else "navigation"
            if toc
            else "render_only"
            if re.fullmatch(r"\s*(?:import .+|export .+|<!--.*-->)\s*", line)
            else None
        )
        if reason:
            changes.append({"line": i + 1, "reason": reason})
            lines[i] = ""
    return lines, changes


def source_metadata(document, collection):
    return {
        "collection": collection,
        "document_id": document["id"],
        "url": document["url"],
        "commit": document.get("commit"),
        "release": document.get("release"),
        "sha256": document["sha256"],
        "product": document.get("project"),
        "metadata_method": "frozen_manifest",
        "preprocessing_version": VERSION,
    }


def units(lines):
    """Fences and tables stay separate; all units retain exact source coordinates."""
    result, heading, stack = [], "", []
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        start = i
        line = lines[i]
        title = re.match(r"^(#{1,6})\s+(.+)", line)
        if title:
            level = len(title[1])
            stack = [(n, t) for n, t in stack if n < level] + [(level, title[2])]
            heading = " > ".join(t for _, t in stack)
            i += 1
            kind = "heading"
        elif opening := fence_open(line):
            marker, inline = opening
            i += 1
            while not inline and i < len(lines):
                closing = fence_close(lines[i], marker)
                i += 1
                if closing:
                    break
            kind = "code"
        elif "|" in line and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            i += 2
            while i < len(lines) and lines[i].strip() and "|" in lines[i]:
                i += 1
            kind = "table"
        else:
            i += 1
            while (
                i < len(lines)
                and lines[i].strip()
                and not re.match(r"^\s*(?:#{1,6}\s|```|~~~)", lines[i])
            ):
                if (
                    i + 1 < len(lines)
                    and "|" in lines[i]
                    and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1])
                ):
                    break
                i += 1
            kind = (
                "condition"
                if re.search(
                    r"\b(?:if|unless|only|not|except|requires?)\b|如果|仅|不得|不能|不应|条件|限制",
                    "\n".join(lines[start:i]),
                    re.I,
                )
                else "explanation"
            )
        result.append(
            {
                "content": "\n".join(lines[start:i]),
                "start": start + 1,
                "end": i,
                "heading": heading,
                "kind": kind,
            }
        )
    return result


def split_unit(unit, encoder, size):
    content = unit["content"]
    if fits(content, size, encoder):
        return [content]
    if unit["kind"] == "table":
        rows = content.splitlines()
        prefix = "\n".join(rows[:2])
        pieces, current = [], prefix
        for row in rows[2:]:
            if current != prefix and not fits(current + "\n" + row, size, encoder):
                pieces.append(current)
                current = prefix
            current += "\n" + row
        if current != prefix:
            pieces.append(current)
        # Extremely wide rows remain complete; encoding uses token windows.
        return pieces or [content]
    if unit["kind"] == "code":
        lines = content.splitlines()
        if len(lines) < 3 or not lines[-1].strip().startswith(lines[0].strip()[:3]):
            return [content]
        opener, closer = lines[0], lines[-1]
        pieces, current = [], []
        for line in lines[1:-1]:
            if current and not fits("\n".join([opener, *current, line, closer]), size, encoder):
                pieces.append("\n".join([opener, *current, closer]))
                current = []
            current.append(line)
        if current:
            pieces.append("\n".join([opener, *current, closer]))
        return pieces or [content]
    # A short condition paragraph is never separated by semantic similarity heuristics.
    pieces, current = [], ""
    for sentence in bounded_units(content, size, encoder):
        combined = current + ("\n" if current else "") + sentence
        if current and not fits(combined, size, encoder):
            pieces.append(current)
            current = sentence
        else:
            current = combined
    if current:
        pieces.append(current)
    return pieces


def preprocess(text, source, metadata, encoder, settings, original_chunks=()):
    lines, changes = clean_lines(text)
    old = defaultdict(list)
    for chunk in original_chunks:
        old[chunk.content].append(chunk)
    chunks, mappings = [], []
    section = ""
    parent = None
    previous = None
    for unit in units(lines):
        if unit["heading"] != section or parent is None:
            section = unit["heading"]
            parent = stable_id(source, VERSION, "section", unit["start"], section)
        # Keep adjacent heading/description as context, without inserting new assertions.
        description = previous if unit["kind"] in {"code", "table"} else None
        for index, content in enumerate(split_unit(unit, encoder, settings.chunk_size)):
            candidates = old.get(content, [])
            exact = next(
                (
                    c
                    for c in candidates
                    if c.heading == section
                    and c.start_line == unit["start"]
                    and c.end_line == unit["end"]
                ),
                None,
            )
            cid = exact.id if exact else stable_id(source, VERSION, unit["start"], index, content)
            info = {
                **metadata,
                "body_type": unit["kind"],
                "original_lines": [unit["start"], unit["end"]],
                "topic": section,
                "hardware_mentions": sorted(
                    set(
                        re.findall(
                            r"\b(?:Ampere|Hopper|Ada Lovelace|MI300X?|H100|A100|AMD|NVIDIA)\b",
                            content,
                            re.I,
                        )
                    )
                ),
            }
            if description:
                info["description_lines"] = [description["start"], description["end"]]
            aliases = [
                c.id
                for c in original_chunks
                if c.start_line is not None
                and c.start_line <= unit["end"]
                and c.end_line >= unit["start"]
            ]
            info["original_chunk_ids"] = aliases
            chunk = Chunk(
                id=cid,
                parent_id=parent,
                source=source,
                content=content,
                domain="infra",
                heading=section,
                start_line=unit["start"],
                end_line=unit["end"],
                locator=f"{source}#L{unit['start']}-L{unit['end']}",
                chunk_type=unit["kind"],
                metadata=info,
            )
            chunks.append(chunk)
            mappings.append(
                {
                    "chunk_id": cid,
                    "original_chunk_ids": aliases,
                    "original_lines": info["original_lines"],
                }
            )
        previous = unit if unit["kind"] not in {"code", "table"} else previous
    return chunks, {
        "line_map": list(range(1, len(lines) + 1)),
        "changes": changes,
        "chunks": mappings,
        "processed_text": "\n".join(lines) + "\n",
    }


def protected_signature(chunk):
    """Do not merge facts across versions, identifiers, numbers or negation."""
    m = chunk.metadata
    tokens = sorted(set(re.findall(r"[A-Za-z_][A-Za-z_0-9.]*|\d+(?:\.\d+)*", chunk.content)))
    negatives = sorted(
        re.findall(r"\b(?:not|unless|never|only|except)\b|不|仅|无|除非", chunk.content, re.I)
    )
    return m.get("product"), m.get("release"), tuple(tokens), tuple(negatives)


def duplicate_audit(chunks):
    seen, retained, aliases = {}, [], []
    for chunk in chunks:
        text = chunk.content.strip()
        known_version = chunk.metadata.get("release")
        key = (
            hashlib.sha256(text.encode()).hexdigest(),
            chunk.metadata.get("product"),
            known_version if known_version else chunk.source,
        )
        previous = seen.get(key)
        if len(text) >= 100 and previous and previous.source != chunk.source:
            alias = {
                "id": chunk.id,
                "source": chunk.source,
                "locator": chunk.locator,
                "metadata": chunk.metadata,
                "content": chunk.content,
            }
            previous.metadata.setdefault("source_aliases", []).append(alias)
            aliases.append({"removed_id": chunk.id, "canonical_id": previous.id, "alias": alias})
        else:
            seen.setdefault(key, chunk)
            retained.append(chunk)
    # Inverted shingles avoid quadratic comparisons across all chunks. This is audit only.
    postings, candidates = defaultdict(list), defaultdict(int)
    shingles = []
    for index, chunk in enumerate(retained):
        text = "".join(chunk.content.split())
        grams = {text[i : i + 20] for i in range(max(0, len(text) - 19))}
        shingles.append(grams)
        for gram in grams:
            for other in postings[gram] if len(postings[gram]) <= 8 else []:
                candidates[other, index] += 1
            postings[gram].append(index)
    near = []
    for (left, right), count in candidates.items():
        a, b = retained[left], retained[right]
        ratio = count / max(1, min(len(shingles[left]), len(shingles[right])))
        if a.source != b.source and ratio >= 0.8 and min(len(a.content), len(b.content)) >= 100:
            near.append(
                {
                    "left": a.id,
                    "right": b.id,
                    "containment": ratio,
                    "protected_fields_match": protected_signature(a) == protected_signature(b),
                    "action": "audit_only_no_semantic_deletion",
                }
            )
    return retained, {"exact_aliases": aliases, "near_candidates": near}
