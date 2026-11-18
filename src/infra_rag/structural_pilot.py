"""Traceable structural chunk pilot: exact fragments, explicit deferred units and context."""

import re
from collections import defaultdict

from .benchmarking import canonical_hash

VERSION = "structural-pilot-v1"
LIMIT = 350


def select_documents(rows, artifacts):
    groups = defaultdict(list)
    for row in rows:
        if artifacts[row["document_id"]]["status"] == "auto_pass":
            groups[row["repository"]].append(row)
    selected = []
    for repo, pool in sorted(groups.items()):
        if len(pool) < 2:
            raise ValueError(f"Insufficient automatic-pass documents: {repo}")
        covered = set()
        for _ in range(2):
            choice = min(
                pool,
                key=lambda r: (
                    -len(set(r["features"]) - covered),
                    canonical_hash(["chunk42", r["document_id"]]),
                ),
            )
            selected.append(choice)
            covered.update(choice["features"])
            pool.remove(choice)
    return selected


def chunk_document(row, document, counters, limit=LIMIT):
    if document["status"] != "auto_pass":
        raise ValueError("Only automatic-pass documents admitted in chunk pilot")
    units = document["units"]
    parents, children, deferred = [], [], []
    parent = None
    current, current_heading = [], ""

    def retrieval_text(fragments):
        return current_heading + "\n\n" + "\n\n".join(f["content"] for f in fragments)

    def fits(fragments):
        return all(count(retrieval_text(fragments)) <= limit for count in counters.values())

    def flush():
        nonlocal current
        if not current:
            return
        body, mapped, cursor = [], [], 0
        for f in current:
            if body:
                cursor += 2
            mapped.append({**f, "body_char_range": [cursor, cursor + len(f["content"])]})
            body.append(f["content"])
            cursor += len(f["content"])
        contexts = set()
        for f in current:
            index = f["unit_index"]
            description = units[index].get("description_unit")
            if description is not None and units[description]["unit_id"] in parent["unit_ids"]:
                contexts.add(units[description]["unit_id"])
            for adjacent in (index - 1, index + 1):
                if (
                    0 <= adjacent < len(units)
                    and units[adjacent]["kind"] == "condition"
                    and units[adjacent]["unit_id"] in parent["unit_ids"]
                ):
                    contexts.add(units[adjacent]["unit_id"])
        present = {
            f["unit_id"]
            for f in current
            if sum(
                x["unit_char_range"][1] - x["unit_char_range"][0]
                for x in current
                if x["unit_id"] == f["unit_id"]
            )
            == len(units[f["unit_index"]]["content"])
        }
        child = {
            "document_id": row["document_id"],
            "parent_id": parent["parent_id"],
            "content": "\n\n".join(body),
            "retrieval_text": retrieval_text(current),
            "fragments": mapped,
            "heading_path": parent["heading_path"],
            "context_unit_ids": sorted(contexts),
            "needs_parent_context": bool(contexts - present),
            "token_counts": {
                name: count(retrieval_text(current)) for name, count in counters.items()
            },
            "input_sha256": row["input_sha256"],
            "source_url": row["source_url"],
            "commit": row["commit"],
            "coordinate_type": row["coordinate_type"],
        }
        child["chunk_id"] = canonical_hash(
            [
                VERSION,
                row["document_id"],
                child["parent_id"],
                [(f["unit_id"], f["unit_char_range"]) for f in current],
            ]
        )[:32]
        children.append(child)
        current = []

    sections = []
    for index, unit in enumerate(units):
        if not sections or unit["kind"] == "heading":
            sections.append([])
        sections[-1].append(index)
    for indices in sections:
        flush()
        first = units[indices[0]]
        parent = {
            "parent_id": canonical_hash([VERSION, row["document_id"], first["unit_id"]])[:32],
            "document_id": row["document_id"],
            "heading_path": first["heading_path"],
            "unit_ids": [units[i]["unit_id"] for i in indices],
            "units": [units[i] for i in indices],
        }
        parents.append(parent)
        current_heading = " > ".join(first["heading_path"])
        for index in indices:
            unit = units[index]
            text = unit["content"]
            ranges = [(0, len(text))]
            # Only ordinary paragraphs can split, and only at complete sentence/newline boundaries.
            if unit["kind"] == "paragraph" and not re.search(r"[`$]|\\\(", text):
                boundaries = [m.end() for m in re.finditer(r"[。！？!?；;]|\.(?=\s|$)|\n", text)]
                boundaries = sorted({0, len(text), *boundaries})
                ranges = list(zip(boundaries[:-1], boundaries[1:], strict=True))
            for start, end in ranges:
                f = {
                    "unit_id": unit["unit_id"],
                    "unit_index": index,
                    "kind": unit["kind"],
                    "unit_char_range": [start, end],
                    "content": text[start:end],
                    "input_lines": unit["input_lines"],
                    "source_lines": unit["source_lines"],
                }
                if not fits([f]):
                    flush()
                    deferred.append(
                        {
                            **f,
                            "parent_id": parent["parent_id"],
                            "reason": "indivisible_fragment_exceeds_token_budget",
                            "token_counts": {
                                name: count(retrieval_text([f])) for name, count in counters.items()
                            },
                        }
                    )
                    continue
                if current and not fits(current + [f]):
                    flush()
                current.append(f)
        flush()
    return {
        "document_id": row["document_id"],
        "parents": parents,
        "children": children,
        "deferred": deferred,
        "version": VERSION,
        "limit": limit,
    }


def validate_document(document, output, counters):
    units = document["units"]
    all_parts = defaultdict(list)
    eligible_chars = 0
    parent_records = {p["parent_id"]: p for p in output["parents"]}
    for child in output["children"]:
        if child["parent_id"] not in parent_records:
            raise ValueError("Unknown parent")
        if child["heading_path"] != parent_records[child["parent_id"]]["heading_path"]:
            raise ValueError("Heading metadata mismatch")
        expected_body = "\n\n".join(f["content"] for f in child["fragments"])
        expected_retrieval = " > ".join(child["heading_path"]) + "\n\n" + expected_body
        if child["content"] != expected_body or child["retrieval_text"] != expected_retrieval:
            raise ValueError("Unmapped or altered child text")
        for name, count in counters.items():
            actual = count(child["retrieval_text"])
            if actual > output["limit"] or actual != child["token_counts"][name]:
                raise ValueError("Token limit or recorded count mismatch")
        for f in child["fragments"]:
            start, end = f["body_char_range"]
            if child["content"][start:end] != f["content"]:
                raise ValueError("Child body mapping mismatch")
            eligible_chars += len(f["content"])
            all_parts[f["unit_index"]].append(f)
    for f in output["deferred"]:
        parent = parent_records[f["parent_id"]]
        text = " > ".join(parent["heading_path"]) + "\n\n" + f["content"]
        actual = {name: count(text) for name, count in counters.items()}
        if actual != f["token_counts"] or not any(v > output["limit"] for v in actual.values()):
            raise ValueError("Deferred budget justification mismatch")
        all_parts[f["unit_index"]].append(f)
    for i, unit in enumerate(units):
        cursor = 0
        for f in sorted(all_parts[i], key=lambda f: f["unit_char_range"]):
            if f["unit_id"] != unit["unit_id"] or f["kind"] != unit["kind"]:
                raise ValueError("Unit identity mismatch")
            start, end = f["unit_char_range"]
            if start != cursor or f["content"] != unit["content"][start:end]:
                raise ValueError("Missing, overlapping or altered source fragment")
            if f["source_lines"] != unit["source_lines"] or f["input_lines"] != unit["input_lines"]:
                raise ValueError("Original source coordinates changed")
            if unit["kind"] != "paragraph" and (start, end) != (0, len(unit["content"])):
                raise ValueError("Protected structural unit split")
            cursor = end
        if cursor != len(unit["content"]):
            raise ValueError("Unaccounted source characters")
    if [u for p in output["parents"] for u in p["units"]] != units:
        raise ValueError("Parent context incomplete")
    parent_index = {p["parent_id"]: set(p["unit_ids"]) for p in output["parents"]}
    for child in output["children"]:
        if not set(child["context_unit_ids"]) <= parent_index[child["parent_id"]]:
            raise ValueError("Context reference crosses parent boundary")
    return {
        "unit_body_characters": sum(len(u["content"]) for u in units),
        "child_body_characters": eligible_chars,
        "deferred_characters": sum(len(f["content"]) for f in output["deferred"]),
        "child_chunks": len(output["children"]),
        "deferred_fragments": len(output["deferred"]),
        "children_needing_parent_context": sum(
            c["needs_parent_context"] for c in output["children"]
        ),
    }
