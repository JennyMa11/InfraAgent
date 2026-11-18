"""Small paired AnswerService dev probe on directly recorded delivered contexts."""

import argparse
import copy
import json
import re
import shutil
from collections import Counter
from pathlib import Path

from operation_log import record_operation
from prepare_corpus_v2 import ROOT

from infra_rag.benchmarking import canonical_hash, digest, write_new
from infra_rag.config import Settings
from infra_rag.legacy_model_clients import AnthropicClient
from infra_rag.offline_evaluation import generate_answer, latency_summary

SOURCE = ROOT / "evals/merged-corpus-v2/budget-search-v8/run-20261003-v4"
PLAN = ROOT / "evals/merged-corpus-v2/answer-delivery-v11/experiment-plan.md"
ARMS = ("B-O15", "Ladj-X30")


def rows(path):
    return [json.loads(s) for s in path.read_text().splitlines()] if path.exists() else []


def append(path, value):
    with path.open("a") as stream:
        stream.write(json.dumps(value, ensure_ascii=False) + "\n")


def prepare(run):
    manifest = json.loads((SOURCE / "artifacts-manifest.json").read_text())["files"]
    for name, expected in manifest.items():
        if digest(SOURCE / name) != expected:
            raise ValueError("Changed frozen retrieval artifact")
    decision = json.loads((SOURCE / "decision.json").read_text())
    audit = json.loads((SOURCE / "runtime-integrity-audit.json").read_text())
    if not all(
        (
            decision["quality_gate"],
            decision["latency_gate"],
            audit["actual_candidate_quality_gate"],
            audit["actual_delivery_quality_gate"],
            audit["actual_context_recorded_directly"],
        )
    ):
        raise ValueError("Actual retrieval dev gates required")
    client = AnthropicClient.from_environment(path=ROOT / ".env.deepseek", max_tokens=650)
    client.timeout = 45
    if not client.deepseek or client.model != "deepseek-flash":
        raise ValueError("Frozen official DeepSeek configuration required")
    frozen = json.loads(
        (ROOT / "evals/merged-corpus-v2/original-rag-v7/run-20261003-v3/protocol.json").read_text()
    )
    selected, inputs = [], {}
    for ds, directory in (
        ("official", "infra-official-v1-reviewed"),
        ("repository", "repository-benchmark"),
    ):
        path = ROOT / "evals" / directory / "dev.json"
        name = str(path.relative_to(ROOT))
        if digest(path) != frozen["inputs"][name]:
            raise ValueError("Changed frozen dev cases")
        inputs[name] = digest(path)
        cases = sorted(json.loads(path.read_text()), key=lambda c: c["id"])
        for kind in sorted({c["question_type"] for c in cases}):
            case = next(c for c in cases if c["question_type"] == kind)
            selected.append({"dataset": ds, "case": case})
    if len(selected) != 8:
        raise ValueError("Frozen selection requires8 dev cases")
    contexts = {
        (r["dataset"], r["id"], r["arm"]): r["actual_context"]
        for r in rows(SOURCE / "latency.jsonl")
    }
    tasks = []
    for repetition in (1, 2):
        for i, item in enumerate(selected):
            for arm in ARMS if (i + repetition) % 2 else ARMS[::-1]:
                case = item["case"]
                key = item["dataset"], case["id"], arm
                tasks.append(
                    {
                        "dataset": key[0],
                        "id": key[1],
                        "arm": arm,
                        "repetition": repetition,
                        "case_sha256": canonical_hash(case),
                        "context_sha256": canonical_hash(contexts[key]),
                    }
                )
    implementation = {
        str(p.relative_to(ROOT)): digest(p)
        for p in [
            *sorted((ROOT / "src/infra_rag").glob("*.py")),
            Path(__file__),
            ROOT / "scripts/operation_log.py",
        ]
    }
    protocol = {
        "kind": "original_answer_service_actual_context_dev_probe",
        "expected_outputs": 32,
        "case_count": 8,
        "repetitions": 2,
        "max_actual_requests": 64,
        "timeout_seconds": 45,
        "selection": "first id per dataset/question_type",
        "provider": client.configuration(),
        "plan_sha256": digest(PLAN),
        "implementation": implementation,
        "inputs": {
            **inputs,
            str((SOURCE / "artifacts-manifest.json").relative_to(ROOT)): digest(
                SOURCE / "artifacts-manifest.json"
            ),
        },
        "tasks": tasks,
        "semantic_review_required": True,
        "independent_review": "pending",
        "default_changed": False,
        "holdout_test_read": False,
        "scope": "generation on frozen actual evidence; not live end-to-end",
    }
    if (run / "protocol.json").exists():
        if json.loads((run / "protocol.json").read_text()) != protocol:
            raise ValueError("Changed protocol; use new directory")
    else:
        run.mkdir(parents=True, exist_ok=False)
        write_new(run / "protocol.json", protocol)
        shutil.copyfile(PLAN, run / "experiment-plan.md")
        for name in implementation:
            destination = run / "implementation" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
    return protocol, selected, contexts, client


def generate(run, protocol, selected, contexts, client):
    cases = {(r["dataset"], r["case"]["id"]): r["case"] for r in selected}
    previous = rows(run / "answers.jsonl")
    done = {(r["dataset"], r["id"], r["arm"], r["repetition"]) for r in previous}
    if any(re.search(r"HTTP (401|402|403|429)", r["generation"]["error"] or "") for r in previous):
        raise ValueError("Frozen access/quota stop reached; do not resume requests")
    for task in protocol["tasks"]:
        key = task["dataset"], task["id"], task["arm"], task["repetition"]
        if key in done:
            continue
        case = cases[key[:2]]
        context = copy.deepcopy(contexts[key[:3]])
        result = generate_answer(case, context, Settings(), client)
        if len(result["calls"]) > 2:
            raise ValueError("Exceeded original format-repair request cap")
        record = {
            **task,
            "question_type": case["question_type"],
            "case": case,
            "context": context,
            "generation": result,
            "answer_fact_correct": None,
            "citation_support": None,
            "hallucination_rate": None,
            "is_agent_trace": False,
        }
        record["trace_sha256"] = canonical_hash(record)
        append(run / "answers.jsonl", record)
        print(
            "answer",
            task["dataset"],
            task["id"],
            task["arm"],
            task["repetition"],
            "calls",
            len(result["calls"]),
            "error",
            result["error"],
            flush=True,
        )
        if re.search(r"HTTP (401|402|403|429)", result["error"] or ""):
            break


def report(run, protocol):
    answers = rows(run / "answers.jsonl")
    expected = {(r["dataset"], r["id"], r["arm"], r["repetition"]) for r in protocol["tasks"]}
    actual = [(r["dataset"], r["id"], r["arm"], r["repetition"]) for r in answers]
    if len(actual) != len(set(actual)) or not set(actual) <= expected:
        raise ValueError("Unknown/duplicate answers")
    calls = [call for r in answers for call in r["generation"]["calls"]]
    if len(calls) > 64:
        raise ValueError("Actual request budget exceeded")
    usage = Counter()
    for call in calls:
        for k, value in (call.get("provider_response", {}).get("usage") or {}).items():
            if isinstance(value, (int, float)):
                usage[k] += value
    summary = {}
    groups = {arm: [r for r in answers if r["arm"] == arm] for arm in ARMS}
    for row in answers:
        group = f"{row['arm']}:{row['dataset']}:{row['question_type']}"
        groups.setdefault(group, []).append(row)
    for arm, values in groups.items():
        summary[arm] = {
            "outputs": len(values),
            "independent_cases": len({(r["dataset"], r["id"]) for r in values}),
            "mechanical_json_valid": {
                "numerator": sum(r["generation"]["checks"]["format_valid"] for r in values),
                "denominator": len(values),
            },
            "answered_status": sum(
                (r["generation"]["response"] or {}).get("status") == "answered" for r in values
            ),
            "refused_status": sum(
                (r["generation"]["response"] or {}).get("status") == "no_evidence" for r in values
            ),
            "errors": sum(bool(r["generation"]["error"]) for r in values),
            "generation_latency": latency_summary([r["generation"]["latency_ms"] for r in values])
            if values
            else None,
            "answer_correctness": None,
            "citation_precision": None,
            "hallucination_rate": None,
        }
        metric = summary[arm]["mechanical_json_valid"]
        metric["value"] = (
            metric["numerator"] / metric["denominator"] if metric["denominator"] else None
        )
    write_new(
        run / "summary.json",
        {
            "expected_outputs": 32,
            "actual_outputs": len(answers),
            "missing": [list(k) for k in sorted(expected - set(actual))],
            "results": summary,
            "actual_requests": len(calls),
            "supplier_usage": dict(usage),
            "usage_coverage": {
                "numerator": sum(bool(c.get("provider_response", {}).get("usage")) for c in calls),
                "denominator": len(calls),
                "value": sum(bool(c.get("provider_response", {}).get("usage")) for c in calls)
                / len(calls)
                if calls
                else None,
            },
            "independent_review_coverage": {"numerator": 0, "denominator": 32, "value": 0.0},
            "monetary_cost_usd": None,
            "semantic_review": None,
            "adoption_allowed": False,
        },
    )
    with (run / "answer-review-pending.jsonl").open("x") as stream:
        for r in answers:
            value = {
                "dataset": r["dataset"],
                "id": r["id"],
                "arm": r["arm"],
                "repetition": r["repetition"],
                "case_sha256": r["case_sha256"],
                "trace_sha256": r["trace_sha256"],
                "status": "pending",
                "reviewer": None,
                "reviewed_at": None,
                "reason": None,
                "claim_inventory_complete": None,
                "claims": None,
                "claim_citation_edges": None,
                "source_factual_correctness": None,
                "all_required_goals": None,
                "constraints_satisfied": None,
                "contradiction": None,
                "is_agent_review_ledger": False,
            }
            stream.write(json.dumps(value, ensure_ascii=False) + "\n")
    write_new(
        run / "artifacts-manifest.json",
        {
            "files": {
                str(p.relative_to(run)): digest(p)
                for p in sorted(run.rglob("*"))
                if p.is_file() and p.name not in {"artifacts-manifest.json", "execution.log"}
            }
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--phase", required=True, choices=("generate", "report"))
    args = parser.parse_args()
    run = args.output.resolve()
    protocol, selected, contexts, client = prepare(run)
    if args.phase == "generate":
        generate(run, protocol, selected, contexts, client)
    else:
        report(run, protocol)
    record_operation(
        f"完成v11阶段{args.phase} {run.relative_to(ROOT)}",
        "收集实际交付下原AnswerService输出供独立审核",
        "该阶段产物已保存，原提示、每输出2调用、总64上限不变",
        "格式/引用ID合法不等于正确；语义审核pending，确认与默认采用未允许",
    )


if __name__ == "__main__":
    main()
