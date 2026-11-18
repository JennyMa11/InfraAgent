"""Score only complete, hash-bound independent human reviews of native answers."""

import argparse

from operation_log import record_operation
from prepare_corpus_pilot import load, save

from infra_rag.benchmarking import digest
from infra_rag.paired_statistics import paired_statistics


def score(run, reviews):
    schedule = load(run / "schedule.json")
    cases = {c["id"]: c for c in load(run / "questions.json")}
    expected = {(j["id"], j["enabled"]) for j in schedule}
    by_key = {(r["id"], r["enabled"]): r for r in reviews}
    if len(reviews) != len(by_key) or set(by_key) != expected or len(expected) != 60:
        raise ValueError("Complete 60 paired independent reviews required")
    paired = {False: [], True: []}
    for key, r in by_key.items():
        rowpath = run / "rows" / f"{key[0]}-{key[1]}.json"
        row = load(rowpath)
        if (
            r.get("method") != "independent_human"
            or r.get("status") != "approved"
            or not r.get("reviewer")
            or not r.get("reviewed_at")
            or not r.get("reason")
        ):
            raise ValueError("AI/pending/unattributed review cannot be scored as independent")
        if r["case_sha256"] != row["case_sha256"] or r["trace_sha256"] != digest(rowpath):
            raise ValueError("Review hash mismatch")
        for name in (
            "strict_correct",
            "all_required_claims",
            "citations_supported",
            "source_claim_inventory_complete",
        ):
            if not isinstance(r.get(name), bool):
                raise ValueError("Missing explicit semantic judgment")
        if not r["source_claim_inventory_complete"]:
            raise ValueError("Incomplete claim inventory")
        if r["strict_correct"] and (
            not r["all_required_claims"]
            or not r["citations_supported"]
            or row["http_status"] != 200
        ):
            raise ValueError("Correctness contradicts mandatory judgment or execution failure")
        paired[key[1]].append(
            {
                "id": key[0],
                "group_id": cases[key[0]]["group_id"],
                "answerable": True,
                "delivered": {"complete": r["strict_correct"]},
            }
        )
    stats = paired_statistics(paired[False], paired[True], samples=10000, seed=42)
    return {
        "review_coverage": {"numerator": 60, "denominator": 60, "value": 1.0},
        "strict_accuracy": {
            str(a): {
                "numerator": sum(r["delivered"]["complete"] for r in rs),
                "denominator": 30,
                "value": sum(r["delivered"]["complete"] for r in rs) / 30,
            }
            for a, rs in paired.items()
        },
        "paired_statistics": stats,
        "scope": "one preregistered primary test; independent human-reviewed dev results",
        "default_changed": False,
    }


if __name__ == "__main__":
    from pathlib import Path

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--reviews", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        result = score(args.run, load(args.reviews))
        save(args.output, result)
        record_operation("独立审核配对统计", "不将AI辅助审核当人工金标", str(args.output))
    except Exception as exc:
        record_operation("独立审核统计拒绝", "保留未知/待审", str(args.output), str(exc))
        raise
