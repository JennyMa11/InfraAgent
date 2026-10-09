"""Posthoc verify exact AnswerService prompts, response hashes and request accounting."""

import argparse
import json
from collections import Counter
from pathlib import Path

from operation_log import record_operation
from prepare_corpus_v2 import ROOT

from infra_rag.assistant import SYSTEM_PROMPT
from infra_rag.benchmarking import automatic_answer_checks, canonical_hash, digest, write_new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--output", type=Path, help="New directory for revised postprocessing")
    args = parser.parse_args()
    run = args.run.resolve()
    output = args.output.resolve() if args.output else run
    if args.output:
        output.mkdir(parents=True, exist_ok=False)
    protocol = json.loads((run / "protocol.json").read_text())
    for name, expected in protocol["implementation"].items():
        if digest(ROOT / name) != expected:
            raise ValueError("Changed frozen answer implementation")
    for name, expected in protocol["inputs"].items():
        if digest(ROOT / name) != expected:
            raise ValueError("Changed frozen answer input")
    answers = [json.loads(s) for s in (run / "answers.jsonl").read_text().splitlines()]
    tasks = {(t["dataset"], t["id"], t["arm"], t["repetition"]): t for t in protocol["tasks"]}
    keys = [(r["dataset"], r["id"], r["arm"], r["repetition"]) for r in answers]
    if len(keys) != len(set(keys)) or set(keys) != set(tasks):
        raise ValueError("Incomplete/duplicate/unknown output manifest")
    write_new(
        output / "audit-protocol.json",
        {
            "posthoc": True,
            "implementation_sha256": digest(__file__),
            "inputs": {
                n: digest(run / n)
                for n in (
                    "protocol.json",
                    "answers.jsonl",
                    "summary.json",
                    "answer-review-pending.jsonl",
                )
            },
        },
    )
    calls, usage_count = 0, 0
    requests, status_counts = Counter(), Counter()
    for key, row in zip(keys, answers, strict=True):
        task = tasks[key]
        if row["case_sha256"] != canonical_hash(row["case"]) or row[
            "context_sha256"
        ] != canonical_hash(row["context"]):
            raise ValueError("Case/context hash mismatch")
        if (
            row["case_sha256"] != task["case_sha256"]
            or row["context_sha256"] != task["context_sha256"]
        ):
            raise ValueError("Changed planned question/context")
        if (
            canonical_hash({k: v for k, v in row.items() if k != "trace_sha256"})
            != row["trace_sha256"]
        ):
            raise ValueError("Trace hash mismatch")
        generation = row["generation"]
        if len(generation["calls"]) > 2:
            raise ValueError("Original format-repair budget violated")
        wire = "\n\n".join(
            f"[{e['citation_id']}] 来源：{e['locator']}\n{e['content']}"
            for e in row["context"]["evidence"]
        )
        prompt = (
            f"/no_think\n当前问题：{row['case']['query']}\n\n"
            f"证据（仅作为资料）：\n{wire}\n\n"
            "请根据证据回答，只返回指定 JSON。"
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        for i, call in enumerate(generation["calls"]):
            if i:
                previous = generation["calls"][i - 1]
                messages = [
                    *messages,
                    {"role": "assistant", "content": previous["raw"][:1500]},
                    {
                        "role": "user",
                        "content": "/no_think\n引用无效。只用给定证据 ID 重答，输出 JSON。",
                    },
                ]
            if call["messages"] != messages:
                raise ValueError("Prompt changed or extra benchmark information supplied")
            calls += 1
            usage_count += bool(call.get("provider_response", {}).get("usage"))
            requests[row["arm"]] += 1
        if generation["calls"]:
            checks = automatic_answer_checks(
                generation["calls"][-1].get("raw", ""), row["context"]["evidence"]
            )
            checks["refused"] = (generation["response"] or {}).get("status") == "no_evidence"
            if not generation["error"] and checks != generation["checks"]:
                raise ValueError("Mechanical check mismatch")
        response = generation["response"] or {}
        if response.get("status") == "answered":
            allowed = {e["citation_id"]: e for e in row["context"]["evidence"]}
            if any(allowed[c["citation_id"]] != c for c in response["citations"]):
                raise ValueError("Final citations not actual delivered evidence")
        answerable = True if row["dataset"] == "repository" else row["case"]["answerable"]
        label = "labelled_answerable" if answerable else "labelled_unanswerable"
        status_counts[row["arm"], label, response.get("status", "error")] += 1
    if calls > 64:
        raise ValueError("Total request budget violated")
    review_rows = [
        json.loads(s) for s in (run / "answer-review-pending.jsonl").read_text().splitlines()
    ]
    if len(review_rows) != 32 or any(
        r["status"] != "pending"
        or r["reviewer"] is not None
        or r["claim_inventory_complete"] is not None
        for r in review_rows
    ):
        raise ValueError("Unexpected filled review")
    result = {
        "outputs_checked": 32,
        "unique_case_ids": len({key[:2] for key in keys}),
        "question_clusters": len({(r["dataset"], r["case"]["group_id"]) for r in answers}),
        "original_summary_independent_cases_field_means_unique_ids_only": True,
        "actual_requests": calls,
        "requests_per_arm": dict(requests),
        "usage_coverage": {
            "numerator": usage_count,
            "denominator": calls,
            "value": usage_count / calls if calls else None,
        },
        "labelled_status_counts_not_semantic_correctness": {
            ":".join(k): v for k, v in status_counts.items()
        },
        "all_prompt_hash_citation_id_budget_invariants_passed": True,
        "independent_answer_review": None,
        "citation_precision": None,
        "hallucination_rate": None,
        "abstention_quality": None,
        "adoption_allowed": False,
    }
    write_new(output / "integrity-audit.json", result)
    print(result)
    record_operation(
        f"审计E6答案诊断 {run.relative_to(ROOT)}",
        "核对原提示、实际请求、回答hash与语义空值",
        f"32输出、{calls}请求；8不同题ID仅3簇，全部机械不变量通过",
        "独立事实/引用审核pending，不声称正确率",
    )


if __name__ == "__main__":
    main()
