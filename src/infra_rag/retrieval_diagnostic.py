"""Source-span scoring for diagnostic retrieval; no answer correctness inference."""

from collections import defaultdict


def intervals(children):
    result = defaultdict(list)
    for c in children:
        for f in c["fragments"]:
            result[(c["document_id"], f["unit_id"])].append(f["unit_char_range"])
        rendering = c.get("rendering") or {}
        repeated = rendering.get("repeated_header_source_range")
        if repeated and c["fragments"]:
            result[(c["document_id"], c["fragments"][0]["unit_id"])].append(repeated)
    return result


def score(ranges, case):
    coverage = []
    for group in case["evidence_alternatives"]:
        found = 0
        for requirement in group["requirements"]:
            start, end = requirement["char_range"]
            cursor = start
            for a, b in sorted(
                ranges.get((requirement["document_id"], requirement["unit_id"]), [])
            ):
                if a > cursor:
                    break
                if b > cursor:
                    cursor = b
            found += cursor >= end
        coverage.append(found / len(group["requirements"]))
    return {"complete": max(coverage) == 1, "coverage": max(coverage)}


def fusion(rankings):
    scores = defaultdict(float)
    for ranking in rankings:
        for rank, (cid, _) in enumerate(ranking, 1):
            scores[cid] += 1 / (60 + rank)
    return sorted(scores.items(), key=lambda x: (-x[1], x[0]))


def validate_cases(cases, documents):
    units = {
        (d["document_id"], u["unit_id"]): u
        for d in documents
        for p in d["parents"]
        for u in p["units"]
    }
    doc_hashes = {d["document_id"]: {c["input_sha256"] for c in d["children"]} for d in documents}
    ids = set()
    for case in cases:
        if case["id"] in ids or not case["query"].strip():
            raise ValueError("Duplicate/empty diagnostic case")
        ids.add(case["id"])
        if not case["evidence_alternatives"]:
            raise ValueError("Empty evidence alternatives")
        for group in case["evidence_alternatives"]:
            if not group["requirements"]:
                raise ValueError("Empty evidence group")
            for r in group["requirements"]:
                unit = units[(r["document_id"], r["unit_id"])]
                if doc_hashes[r["document_id"]] != {r["input_sha256"]}:
                    raise ValueError("Gold source hash mismatch")
                a, b = r["char_range"]
                if not 0 <= a < b <= len(unit["content"]) or unit["content"][a:b] != r["quote"]:
                    raise ValueError("Gold quote/position mismatch")
                if (
                    r["source_lines"] != unit["source_lines"]
                    or r["input_lines"] != unit["input_lines"]
                ):
                    raise ValueError("Gold source coordinates mismatch")
