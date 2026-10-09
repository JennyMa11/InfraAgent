"""Create pending retrieval-evidence review material, never fill human judgments."""

import argparse
import json
import shutil
from pathlib import Path

from benchmark_budget_search_v8 import read_rows
from operation_log import record_operation
from prepare_corpus_v2 import ROOT

from infra_rag.benchmarking import canonical_hash, digest, write_new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    run, output = args.run.resolve(), args.output.resolve()
    manifest = json.loads((run / "artifacts-manifest.json").read_text())["files"]
    for name, expected in manifest.items():
        if digest(run / name) != expected:
            raise ValueError("Changed frozen run artifact")
    audit = json.loads((run / "runtime-integrity-audit.json").read_text())
    if not audit["all_budget_and_cache_invariants_passed"]:
        raise ValueError("Mechanical audit required before handoff")
    datasets = {
        "official": ROOT / "evals/infra-official-v1-reviewed/dev.json",
        "repository": ROOT / "evals/repository-benchmark/dev.json",
    }
    protocol = json.loads((run / "protocol.json").read_text())
    # The original cases are loaded only from these two frozen dev files.
    cases, case_files = {}, {}
    for ds, path in datasets.items():
        relative = str(path.relative_to(ROOT))
        expected = protocol["inputs"].get(relative)
        if expected is None:
            parent = json.loads(
                (
                    ROOT / "evals/merged-corpus-v2/original-rag-v7/run-20261003-v3/protocol.json"
                ).read_text()
            )
            expected = parent["inputs"][relative]
        if digest(path) != expected:
            raise ValueError("Changed dev cases")
        case_files[relative] = expected
        for case in json.loads(path.read_text()):
            key = ds, case["id"]
            if key in cases:
                raise ValueError("Duplicate dev case")
            cases[key] = case
    evidence = {
        (r["dataset"], r["id"], r["arm"]): r
        for r in read_rows(run / "runtime-evidence-audit.jsonl")
    }
    timings = read_rows(run / "latency.jsonl")
    selected = [r for r in timings if r["arm"] == "Ladj-X30"]
    if len(selected) != 110 or {(r["dataset"], r["id"]) for r in selected} != set(cases):
        raise ValueError("Incomplete candidate evidence for review")
    source_audit = ROOT / "evals/merged-corpus-v2/recall-delivery-v4/run-20261002/source-audit.json"
    source_hashes = {
        r["source"]: r["expected"] for r in json.loads(source_audit.read_text())["source_files"]
    }
    output.mkdir(parents=True, exist_ok=False)
    write_new(
        output / "protocol.json",
        {
            "kind": "pending_original_rag_retrieval_evidence_handoff",
            "is_agent_trace_or_agent_review_ledger": False,
            "is_generated_answer": False,
            "case_files": case_files,
            "inputs": {
                str((run / n).relative_to(ROOT)): digest(run / n)
                for n in (
                    "artifacts-manifest.json",
                    "runtime-integrity-audit.json",
                    "runtime-evidence-audit.jsonl",
                    "latency.jsonl",
                    "decision.json",
                )
            },
            "implementation_sha256": digest(__file__),
            "reviewer": None,
            "human_review_complete": False,
            "independent_review_coverage": {"numerator": 0, "denominator": 110, "value": 0.0},
            "semantic_review_required": True,
        },
    )
    shutil.copyfile(__file__, output / "implementation.py")
    with (output / "evidence-review-pending.jsonl").open("x") as stream:
        for record in selected:
            case = cases[record["dataset"], record["id"]]
            actual = evidence[record["dataset"], record["id"], record["arm"]]
            used = {e["source"] for e in actual["context"]["evidence"]}
            trace = {
                "run": str(run.relative_to(ROOT)),
                "dataset": record["dataset"],
                "id": record["id"],
                "arm": record["arm"],
                "actual_runtime_record": record,
                "reconstructed_actual_context": actual["context"],
                "source_files_sha256": {s: source_hashes[s] for s in sorted(used)},
                "is_answer_or_agent_trace": False,
            }
            row = {
                "dataset": record["dataset"],
                "id": record["id"],
                "case": case,
                "case_sha256": canonical_hash(case),
                "trace": trace,
                "trace_sha256": canonical_hash(trace),
                "status": "pending",
                "reviewer": None,
                "reviewed_at": None,
                "reason": None,
                "evidence_rubric": {
                    "source_authenticity_and_factual_scope": None,
                    "version_hardware_quantities_and_units": None,
                    "gold_necessary_and_sufficient": None,
                    "alternative_evidence_and_source_aliases": None,
                    "delivered_text_covers_all_required_conditions": None,
                    "no_contradiction": None,
                },
                "answer_review": None,
                "answer_review_reason": "No answer was generated",
            }
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    write_new(
        output / "artifacts-manifest.json",
        {
            "files": {
                str(p.relative_to(output)): digest(p)
                for p in sorted(output.rglob("*"))
                if p.is_file()
            }
        },
    )
    record_operation(
        f"生成待审证据交接包 {output.relative_to(ROOT)}",
        "让真实人工可核查固定dev问题、来源hash与实际交付",
        "110份pending材料，审核人/时间/理由与全部语义判断为空；hash已绑定",
        "不是Agent评分账本，也不是答案审核；没有代填通过或指定虚构审核人",
    )


if __name__ == "__main__":
    main()
