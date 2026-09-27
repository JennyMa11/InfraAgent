"""Pack traceable evidence once per response, with a shared context budget."""

import re
from dataclasses import asdict

from .chunking import stable_id


def snippet(text, fits):
    """Prefer a complete sentence; never partially return a fenced code block."""
    if fits(text):
        return text
    if "```" in text:
        return ""
    boundaries = [m.end() for m in re.finditer(r"[。！？!?；;]|\.(?=\s|$)|\n", text)]
    selected = ""
    for end in boundaries:
        if fits(text[:end]):
            selected = text[:end]
    return selected.rstrip()


def pack_context(hits, parents, count, token_budget, char_budget, domain=None, modality=None):
    owners, candidates, seen = {}, [], set()
    # All matched evidence has priority over neighboring context.
    for hit in hits:
        parent = hit.chunk.parent_id
        owners.setdefault(parent, hit)
        if hit.chunk.id not in seen:
            candidates.append(hit.chunk)
            seen.add(hit.chunk.id)
        hit.context = ""
        hit.sibling_ids = []
        hit.evidence = []
        hit.context_ref = parent
    for parent in owners:
        siblings = [
            c
            for c in parents[parent]
            if (domain is None or c.domain == domain)
            and (modality is None or c.modality == modality)
        ]
        matched = {h.chunk.id for h in hits if h.chunk.parent_id == parent}
        anchors = [i for i, c in enumerate(siblings) if c.id in matched]
        neighbors = sorted(
            enumerate(siblings),
            key=lambda pair: (min(abs(pair[0] - i) for i in anchors), pair[0]),
        )
        for _, chunk in neighbors:
            if chunk.id not in seen:
                candidates.append(chunk)
                seen.add(chunk.id)
    blocks, selected = [], []
    omitted = []
    for chunk in candidates:
        citation = "E" + stable_id(chunk.id)
        header = f"[{citation}] {chunk.heading}\n"

        def fits(content, header=header):
            combined = "\n\n".join(blocks + [header + content])
            return len(combined) <= char_budget and count(combined) <= token_budget

        content = snippet(chunk.content, fits)
        if not content:
            omitted.append(chunk.id)
            continue
        block = header + content
        blocks.append(block)
        evidence = {
            "citation_id": citation,
            "chunk_id": chunk.id,
            "parent_id": chunk.parent_id,
            "source": chunk.source,
            "locator": chunk.locator,
            "page": chunk.page,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "modality": chunk.modality,
            "bbox": chunk.bbox,
            "coordinate_space": chunk.coordinate_space,
            "image_path": chunk.image_path,
            "caption_source": chunk.caption_source,
            "caption_locator": chunk.caption_locator,
            "content": content,
            "truncated": content != chunk.content,
        }
        owner = owners[chunk.parent_id]
        owner.evidence.append(evidence)
        owner.sibling_ids.append(chunk.id)
        owner.context += ("\n\n" if owner.context else "") + block
        selected.append(evidence)
    combined = "\n\n".join(blocks)
    return {
        "evidence": selected,
        "context": combined,
        "budget": {"tokens": token_budget, "characters": char_budget},
        "used_tokens": count(combined),
        "used_characters": len(combined),
        "omitted_chunk_ids": omitted,
    }


def response_payload(hits, diagnostics=None, context=None):
    result = {"hits": [asdict(hit) for hit in hits]}
    if diagnostics is not None:
        result["diagnostics"] = diagnostics
    if context is not None:
        result["context_pack"] = context
    return result
