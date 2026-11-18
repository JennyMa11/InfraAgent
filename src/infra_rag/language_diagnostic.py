"""Fixed bilingual schedules and paired component diagnostics, never answer accuracy."""

from infra_rag.paired_statistics import holm, paired_statistics

ARMS = ("bm25", "dense", "hybrid_rerank")
FIELDS = ("candidate", "top5", "first_page", "all_pages")


def validate_pairs(cases, original):
    def identity(c):
        return c["id"], c["query"], c["group_id"]
    if not cases or len({c["id"] for c in cases}) != len(cases):
        raise ValueError("Empty or duplicate bilingual cases")
    if list(map(identity, cases)) != list(map(identity, original)):
        raise ValueError("Original question identity changed")
    if any(not c.get("query_en", "").strip() for c in cases):
        raise ValueError("Missing frozen English expression")


def schedule(cases):
    # Alternate order before outcomes; all arms use the same two frozen expressions.
    return [
        {"id": c["id"], "arm": arm, "query_language": language}
        for i, c in enumerate(cases)
        for arm in ARMS
        for language in (("zh", "en") if i % 2 == 0 else ("en", "zh"))
    ]


def metric(rows, field):
    n = len(rows)
    hits = sum(r.get(field, {}).get("complete", False) for r in rows)
    return {"numerator": hits, "denominator": n, "value": hits / n if n else None}


def summarize(rows, cases):
    expected = {(r["id"], r["arm"], r["query_language"]) for r in schedule(cases)}
    actual = [(r["id"], r["arm"], r["query_language"]) for r in rows]
    if len(actual) != len(expected) or set(actual) != expected:
        raise ValueError("Missing, extra or duplicate language outputs")
    cases_by_id = {c["id"]: c for c in cases}
    for r in rows:
        c = cases_by_id[r["id"]]
        if (
            r["group_id"] != c["group_id"]
            or r["query"] != c["query" if r["query_language"] == "zh" else "query_en"]
        ):
            raise ValueError("Trace question identity mismatch")
    results, comparisons = {}, {}
    for arm in ARMS:
        selected = [r for r in rows if r["arm"] == arm]
        results[arm] = {}
        for language in ("zh", "en"):
            group = [r for r in selected if r["query_language"] == language]
            results[arm][language] = {
                **{f: metric(group, f) for f in FIELDS},
                "failures": sum(r["status"] != "completed" for r in group),
                "blocked": sum(r.get("blocked", False) for r in group),
                "by_stratum": {
                    key: {
                        value: {f: metric([r for r in group if r[key] == value], f) for f in FIELDS}
                        for value in sorted({r[key] for r in group})
                    }
                    for key in ("source_language", "source_role", "kind")
                },
            }
        for field in ("first_page", "all_pages"):
            paired = [
                [
                    {
                        "id": r["id"],
                        "group_id": r["group_id"],
                        "answerable": True,
                        "delivered": {"complete": r.get(field, {}).get("complete", False)},
                    }
                    for r in selected
                    if r["query_language"] == language
                ]
                for language in ("zh", "en")
            ]
            comparisons[f"{arm}:{field}"] = paired_statistics(*paired, samples=10000, seed=42)
    adjusted = holm({k: v["cluster_permutation_p"] for k, v in comparisons.items()})
    for k in comparisons:
        comparisons[k]["holm_p_six_primary_tests"] = adjusted[k]
    return {"results": results, "paired_comparisons": comparisons}
