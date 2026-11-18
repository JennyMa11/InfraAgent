"""Protected bilingual candidate supplementation and source-only context links."""

import copy

from .retrieval_diagnostic import fusion


def supplement(baseline, extra_rankings, fallback_rankings=(), cap=60):
    ids = list(dict.fromkeys(cid for cid, _ in baseline))
    if len(ids) > cap:
        raise ValueError("Protected baseline exceeds cap")
    for ranking in (fusion(extra_rankings), fusion(fallback_rankings)):
        for cid, _ in ranking:
            if len(ids) == cap:
                break
            if cid not in ids:
                ids.append(cid)
    return ids


def link_preceding_explanations(documents):
    result = copy.deepcopy(documents)
    links = []
    for doc in result:
        dependencies = {}
        for parent in doc["parents"]:
            for previous, unit in zip(parent["units"], parent["units"][1:], strict=False):
                if previous["kind"] == "paragraph" and unit["kind"] in {
                    "condition",
                    "table",
                    "code",
                }:
                    dependencies[unit["unit_id"]] = previous["unit_id"]
        for child in doc["children"]:
            added = {
                dependencies[f["unit_id"]]
                for f in child["fragments"]
                if f["unit_id"] in dependencies
            } - set(child["context_unit_ids"])
            if added:
                child["context_unit_ids"] = sorted(set(child["context_unit_ids"]) | added)
                child["needs_parent_context"] = True
                links.append({"chunk_id": child["chunk_id"], "unit_ids": sorted(added)})
    return result, links
