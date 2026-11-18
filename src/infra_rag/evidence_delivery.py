"""Split retained source spans and deliver explicit, budgeted evidence continuations."""

import copy
import re
from collections import defaultdict

from .benchmarking import canonical_hash

VERSION = "evidence-delivery-v1"


def _render(unit, start, end):
    text = unit["content"]
    prefix = suffix = ""
    repeated_header = None
    if unit["kind"] == "code":
        lines = text.splitlines(keepends=True)
        opener = lines[0].rstrip("\r\n")
        closer = lines[-1].strip()
        if start:
            prefix = opener + "\n"
        if end < len(text):
            suffix = ("" if text[start:end].endswith("\n") else "\n") + closer
    elif unit["kind"] == "table":
        header = "".join(text.splitlines(keepends=True)[:2])
        # Explicit text rendering avoids presenting a cut row as a complete Markdown row.
        prefix = "~~~~text\n"
        if start:
            prefix += header
            repeated_header = [0, len(header)]
        suffix = "\n~~~~"
    return prefix, text[start:end], suffix, repeated_header


def split_span(fragment, unit, heading, counters, limit=350, char_limit=1600):
    lo, hi = fragment["unit_char_range"]
    text = unit["content"]
    boundaries = [
        m.end()
        for m in re.finditer(
            r"\n" if unit["kind"] in {"code", "table"} else r"[。！？!?；;]|\.(?=\s|$)|\n", text
        )
    ]

    def fits(start, end):
        prefix, body, suffix, _ = _render(unit, start, end)
        value = heading + "\n\n" + prefix + body + suffix
        return len(value) <= char_limit and all(c(value) <= limit for c in counters.values())

    parts = []
    start = lo
    while start < hi:
        if fits(start, hi):
            end = hi
        else:
            low, high = start + 1, min(hi, start + char_limit)
            while low < high:
                middle = (low + high + 1) // 2
                if fits(start, middle):
                    low = middle
                else:
                    high = middle - 1
            end = low
            while end > start and not fits(start, end):
                end -= 1
            preferred = [n for n in boundaries if start < n <= end]
            if preferred:
                end = max(preferred)
            if end <= start:
                raise ValueError(
                    "A source character plus heading/wrapper cannot fit; no truncation"
                )
        # Never split the opening code fence itself.
        if unit["kind"] == "code" and start == 0 and end < text.find("\n") + 1:
            raise ValueError("Code opener exceeds budget")
        prefix, body, suffix, repeated = _render(unit, start, end)
        part = {
            **fragment,
            "unit_char_range": [start, end],
            "content": body,
            "body_char_range": [len(prefix), len(prefix) + len(body)],
        }
        part.pop("reason", None)
        part.pop("token_counts", None)
        parts.append(
            {
                "fragment": part,
                "prefix": prefix,
                "suffix": suffix,
                "repeated_header_source_range": repeated,
            }
        )
        start = end
    return parts


def resolve_deferred(previous, counters, char_limit=1600, provenance=None):
    result = copy.deepcopy(previous)
    original_children = {c["chunk_id"] for c in previous["children"]}
    units = [u for p in previous["parents"] for u in p["units"]]
    parents = {p["parent_id"]: p for p in previous["parents"]}
    template = previous["children"][0] if previous["children"] else provenance
    if template is None or not all(
        k in template for k in ("input_sha256", "source_url", "commit", "coordinate_type")
    ):
        raise ValueError("Source provenance required before resolving deferred spans")
    if provenance is not None and provenance["document_id"] != previous["document_id"]:
        raise ValueError("Source document identity mismatch")
    for f in previous["deferred"]:
        parent = parents[f["parent_id"]]
        unit = units[f["unit_index"]]
        heading = " > ".join(parent["heading_path"])
        contexts = set()
        description = unit.get("description_unit")
        if description is not None and units[description]["unit_id"] in parent["unit_ids"]:
            contexts.add(units[description]["unit_id"])
        for j in (f["unit_index"] - 1, f["unit_index"] + 1):
            if (
                0 <= j < len(units)
                and units[j]["kind"] == "condition"
                and units[j]["unit_id"] in parent["unit_ids"]
            ):
                contexts.add(units[j]["unit_id"])
        pieces = split_span(f, unit, heading, counters, previous["limit"], char_limit)
        for index, piece in enumerate(pieces):
            fragment = piece["fragment"]
            content = piece["prefix"] + fragment["content"] + piece["suffix"]
            child = {
                k: template[k]
                for k in ("input_sha256", "source_url", "commit", "coordinate_type")
                if k in template
            }
            child.update(
                document_id=previous["document_id"],
                parent_id=f["parent_id"],
                heading_path=parent["heading_path"],
                content=content,
                retrieval_text=heading + "\n\n" + content,
                fragments=[fragment],
                rendering={
                    k: piece[k] for k in ("prefix", "suffix", "repeated_header_source_range")
                },
                context_unit_ids=sorted(contexts),
                needs_parent_context=True,
                continuation_group=unit["unit_id"],
                part_index=index,
                part_count=len(pieces),
                delivery_note="原文续片，需结合其余片段和条件；代码片段不可视为完整可运行示例。",
            )
            child["token_counts"] = {
                name: count(child["retrieval_text"]) for name, count in counters.items()
            }
            child["chunk_id"] = canonical_hash(
                [
                    VERSION,
                    previous["document_id"],
                    f["parent_id"],
                    unit["unit_id"],
                    fragment["unit_char_range"],
                ]
            )[:32]
            result["children"].append(child)
    result["deferred"] = []
    result["previous_version"] = previous["version"]
    result["version"] = VERSION
    result["continued_chunk_ids"] = [
        c["chunk_id"] for c in result["children"] if c["chunk_id"] not in original_children
    ]
    return result


def validate_resolved(previous, result, counters):
    if previous["parents"] != result["parents"] or result["deferred"]:
        raise ValueError("Parent source changed or unresolved deferred")
    before = {c["chunk_id"]: c for c in previous["children"]}
    parent_records = {p["parent_id"]: p for p in result["parents"]}
    units = [u for p in result["parents"] for u in p["units"]]
    covered = defaultdict(list)
    for child in result["children"]:
        if (
            child["document_id"] != previous["document_id"]
            or child["parent_id"] not in parent_records
            or child["heading_path"] != parent_records[child["parent_id"]]["heading_path"]
        ):
            raise ValueError("Child parent or document identity changed")
        if any(
            f["unit_id"] not in parent_records[child["parent_id"]]["unit_ids"]
            for f in child["fragments"]
        ):
            raise ValueError("Source fragment crosses parent context")
        if child["chunk_id"] in before and child != before[child["chunk_id"]]:
            raise ValueError("Existing stable child modified")
        for name, count in counters.items():
            if (
                count(child["retrieval_text"]) > result["limit"]
                or count(child["retrieval_text"]) != child["token_counts"][name]
            ):
                raise ValueError("Token overflow or count mismatch")
        if "rendering" in child:
            rendering = child["rendering"]
            f = child["fragments"][0]
            unit = units[f["unit_index"]]
            expected = _render(unit, *f["unit_char_range"])
            if (
                rendering["prefix"],
                f["content"],
                rendering["suffix"],
                rendering["repeated_header_source_range"],
            ) != expected:
                raise ValueError("Rendering is not source-derived")
            if child["content"] != "".join(expected[:3]):
                raise ValueError("Unexpected synthetic content")
        else:
            if child["content"] != "\n\n".join(f["content"] for f in child["fragments"]):
                raise ValueError("Old source body mismatch")
        if child["retrieval_text"] != " > ".join(child["heading_path"]) + "\n\n" + child["content"]:
            raise ValueError("Heading or body mismatch")
        for f in child["fragments"]:
            unit = units[f["unit_index"]]
            a, b = f["unit_char_range"]
            x, y = f["body_char_range"]
            if (
                unit["unit_id"] != f["unit_id"]
                or f["content"] != unit["content"][a:b]
                or child["content"][x:y] != f["content"]
            ):
                raise ValueError("Source span mismatch")
            if f["source_lines"] != unit["source_lines"] or f["input_lines"] != unit["input_lines"]:
                raise ValueError("Source coordinates changed")
            covered[f["unit_index"]].append((a, b))
    for i, unit in enumerate(units):
        cursor = 0
        for a, b in sorted(covered[i]):
            if a != cursor:
                raise ValueError("Source gap/overlap")
            cursor = b
        if cursor != len(unit["content"]):
            raise ValueError("Incomplete source coverage")
    return {
        "source_characters": sum(len(u["content"]) for u in units),
        "children": len(result["children"]),
        "new_continuation_children": len(result["continued_chunk_ids"]),
        "remaining_deferred": 0,
        "source_character_coverage": 1.0,
    }


def delivery_request(hit_ids, documents):
    children = {c["chunk_id"]: c for d in documents for c in d["children"]}
    unit_children = defaultdict(list)
    for c in children.values():
        for f in c["fragments"]:
            key = (c["document_id"], f["unit_id"])
            if c["chunk_id"] not in unit_children[key]:
                unit_children[key].append(c["chunk_id"])
    queue = list(dict.fromkeys(hit_ids))
    seen = set(queue)
    required_units = set()
    i = 0
    while i < len(queue):
        child = children[queue[i]]
        units = [f["unit_id"] for f in child["fragments"]] + child["context_unit_ids"]
        for uid in units:
            key = (child["document_id"], uid)
            if key not in unit_children:
                raise ValueError("Required context has no source-backed children")
            required_units.add(key)
            for cid in unit_children[key]:
                if cid not in seen:
                    queue.append(cid)
                    seen.add(cid)
        i += 1
    return children, queue, required_units


def pack_delivery(hit_ids, documents, counters, token_budget=1200, char_budget=4000, cursor=None):
    children, queue, required_units = delivery_request(hit_ids, documents)
    request_hash = canonical_hash(
        [
            queue,
            [canonical_hash(children[c]) for c in queue],
            token_budget,
            char_budget,
            sorted(counters),
        ]
    )
    start = 0
    if cursor is not None:
        if cursor.get("request_hash") != request_hash:
            raise ValueError("Continuation belongs to different hits, source or budget")
        start = cursor["offset"]
        if not isinstance(start, int) or not 0 <= start < len(queue):
            raise ValueError("Invalid continuation offset")
    blocks, evidence = [], []
    pos = start
    while pos < len(queue):
        child = children[queue[pos]]
        note = child.get("delivery_note", "请结合关联说明和条件使用本证据。")
        header = f"[E{child['chunk_id']}] {child['source_url']}\n{note}\n"
        combined = "\n\n".join(blocks + [header + child["content"]])
        if len(combined) > char_budget or any(
            c(combined) > token_budget for c in counters.values()
        ):
            break
        blocks.append(header + child["content"])
        evidence.append(
            {
                "citation_id": "E" + child["chunk_id"],
                "chunk_id": child["chunk_id"],
                "document_id": child["document_id"],
                "content": child["content"],
                "source_url": child["source_url"],
                "input_sha256": child["input_sha256"],
                "fragments": copy.deepcopy(child["fragments"]),
                "rendering": copy.deepcopy(child.get("rendering")),
            }
        )
        pos += 1
    more = pos < len(queue)
    blocked = more and pos == start
    delivered = {e["chunk_id"] for e in evidence}
    return {
        "context": "\n\n".join(blocks),
        "evidence": evidence,
        "token_counts": {name: c("\n\n".join(blocks)) for name, c in counters.items()},
        "used_characters": len("\n\n".join(blocks)),
        "required_chunk_ids": queue,
        "required_units": sorted(required_units),
        "remaining_chunk_ids": queue[pos:],
        "previous_page_chunk_ids": queue[:start],
        "page_has_all_required_evidence": bool(queue) and set(queue) <= delivered,
        "answer_ready": bool(queue) and set(queue) <= delivered,
        "status": (
            "no_evidence"
            if not queue
            else "blocked"
            if blocked
            else "needs_continuation"
            if more
            else "final_page"
            if start
            else "complete"
        ),
        "continuation": {"offset": pos, "request_hash": request_hash}
        if more and not blocked
        else None,
        "blocked_chunk_ids": [queue[pos]] if blocked else [],
        "warning": "本页不是完整证据；请核对关联页，不能将跨页并集当作本页模型已见上下文。"
        if more or start
        else None,
    }
