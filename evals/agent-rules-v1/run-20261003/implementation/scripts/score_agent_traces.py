"""Score offline Agent traces without calling tools/models or changing frozen experiments."""

import argparse
import json
from collections import defaultdict
from pathlib import Path

from infra_rag.agent_evaluation import RULE_VERSION, score_trace, summarize, validate_case
from infra_rag.benchmarking import canonical_hash, digest


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def evaluate(cases, traces, reviews=(), *, repetitions=1, complete=False, reviewed=False):
    if repetitions < 1:
        raise ValueError("repetitions must be positive")
    indexed = {c["id"]: c for c in cases}
    if len(indexed) != len(cases) or not cases:
        raise ValueError("nonempty cases with unique IDs required")
    for case in cases:
        validate_case(case)
    review_map = {r["trace_sha256"]: r for r in reviews}
    if len(review_map) != len(reviews):
        raise ValueError("duplicate trace review")
    hashes = {canonical_hash(t) for t in traces}
    if set(review_map) - hashes:
        raise ValueError("unknown reviewed trace")
    done, grouped, scored = set(), defaultdict(list), []
    for trace in traces:
        if trace["case_id"] not in indexed:
            raise ValueError("unknown case")
        key = (trace["run_id"], trace["config_id"], trace["case_id"], trace["repetition"])
        if key in done or not 1 <= trace["repetition"] <= repetitions:
            raise ValueError("duplicate trace or unexpected repetition")
        done.add(key)
        review = review_map.get(canonical_hash(trace))
        if reviewed and (not review or review.get("status") != "approved"):
            raise ValueError("complete independent reviews required")
        row = score_trace(indexed[trace["case_id"]], trace, review)
        grouped[trace["run_id"], trace["config_id"]].append(row)
        scored.append(row)
    if not scored:
        raise ValueError("no traces")
    groups = []
    expected = {(cid, rep) for cid in indexed for rep in range(1, repetitions + 1)}
    for (run_id, config_id), rows in grouped.items():
        actual = {(r["case_id"], r["repetition"]) for r in rows}
        missing = sorted(expected - actual)
        if complete and missing:
            raise ValueError("scheduled case/repetition traces missing")
        groups.append(
            {
                "run_id": run_id,
                "config_id": config_id,
                "scheduled_outputs": len(expected),
                "observed_outputs": len(rows),
                "missing": [{"case_id": cid, "repetition": rep} for cid, rep in missing],
                "metrics": summarize(rows),
                "by_category": {
                    cat: summarize([r for r in rows if r["category"] == cat])
                    for cat in sorted({r["category"] for r in rows})
                },
            }
        )
    return {
        "rule_version": RULE_VERSION,
        "groups": groups,
        "rows": scored,
        "note": "Rates retain denominators/coverage; synthetic fixtures are not Agent results.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--traces", type=Path, required=True)
    parser.add_argument("--reviews", type=Path)
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--require-reviewed", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = evaluate(
        read(args.cases),
        read(args.traces),
        read(args.reviews) if args.reviews else [],
        repetitions=args.repetitions,
        complete=args.require_complete,
        reviewed=args.require_reviewed,
    )
    report["inputs"] = {str(p): digest(p) for p in (args.cases, args.traces, args.reviews) if p}
    report["scorer_sha256"] = digest(
        Path(__file__).resolve().parents[1] / "src/infra_rag/agent_evaluation.py"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Frozen reports must use a new path. Never overwrite a prior experiment.
    with args.output.open("x") as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "groups": len(report["groups"]),
                "traces": len(report["rows"]),
                "rule_version": RULE_VERSION,
            }
        )
    )


if __name__ == "__main__":
    main()
