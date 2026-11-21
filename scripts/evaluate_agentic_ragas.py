"""Evaluate Agentic RAG only, against the frozen P2 Baseline and its 120 cases.

No gold labels enter retrieval or generation. RAGAS uses the unchanged shared
scorer. The relocated index differs only in manifest source paths, after every
source SHA256 is checked; frozen Baseline artifacts are never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import shutil
import statistics
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

from infra_rag.agentic_rag import AgenticRAGChain
from infra_rag.benchmarking import write_new
from infra_rag.config import Settings
from infra_rag.evaluation import evidence_metrics, metrics
from infra_rag.model_clients import configured_model, model_environment
from infra_rag.rag_comparison import evidence_integrity
from infra_rag.service import RetrievalService

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "evals/ragas-p2-v1/run-20261112"
COLLECTION = ROOT / "evals/ragas-full-v1/run-20261111"
SOURCE_INDEX = ROOT / "data/crosslingual-retrieval-v1/index-bge-m3"
CONFIG_ID = "agentic_rag"
METRICS = ("context_precision", "context_recall", "faithfulness", "response_relevancy")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def records(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def save(path: Path, value) -> None:
    write_new(path, value)


def verify_baseline() -> dict:
    expected = load(FROZEN / "artifact-hashes.json")
    changed = [name for name, digest in expected.items() if sha256(FROZEN / name) != digest]
    if changed:
        raise ValueError(f"frozen_baseline_artifact_mismatch:{changed}")
    protocol = load(FROZEN / "protocol.json")
    complete = load(FROZEN / "complete.json")
    if complete != {
        "records_sha256": sha256(FROZEN / "records.jsonl"),
        "cases_sha256": sha256(FROZEN / "cases.json"),
        "protocol_sha256": sha256(FROZEN / "protocol.json"),
    }:
        raise ValueError("frozen_baseline_complete_hash_mismatch")
    if len(load(FROZEN / "cases.json")) != 120 or len(load(FROZEN / "ragas/rows.json")) != 120:
        raise ValueError("frozen_baseline_requires_120_cases_and_rows")
    if {r["config_id"] for r in load(FROZEN / "ragas/rows.json")} != {"p2_full"}:
        raise ValueError("unexpected_baseline_configuration")
    if protocol["index_sha256"] != sha256(ROOT / protocol["index"]):
        raise ValueError("frozen_index_mismatch")
    return protocol


def relocated_index(target: Path) -> Path:
    target.mkdir(parents=True, exist_ok=False)
    for item in SOURCE_INDEX.iterdir():
        if item.is_file():
            shutil.copy2(item, target / item.name)
    index_path = target / "index.json"
    index = load(index_path)
    sources = index["sources"]
    relocated = {}
    for old_path, metadata in sources.items():
        old = Path(old_path)
        expected = ROOT / "data" / old.relative_to(Path("/Users/jennyma/Projects/InfraAgent/data"))
        if not expected.is_file() or sha256(expected) != metadata["sha256"]:
            raise ValueError(f"relocated_source_missing_or_changed:{expected}")
        relocated[str(expected)] = metadata
        for chunk in index["chunks"]:
            if chunk["source"] == old_path:
                chunk["source"] = str(expected)
                chunk["locator"] = str(expected) + chunk["locator"][len(old_path) :]
    index["sources"] = relocated
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def make_settings(index: Path) -> Settings:
    return Settings(**{**load(FROZEN / "protocol.json")["settings"], "data_dir": index})


def load_cases() -> list[dict]:
    cases = load(FROZEN / "cases.json")
    gold = load(COLLECTION / "resolved-gold.json")
    if len(cases) != 120 or len(gold) != 108:
        raise ValueError("expected_120_cases_and_108_resolved_gold")
    result = []
    for case in cases:
        resolved = gold.get(case["id"], {})
        result.append(
            {
                **case,
                "case_id": case["id"],
                "relevant": resolved.get("relevant", case.get("relevant", [])),
                "evidence_alternatives": resolved.get("evidence_alternatives", []),
            }
        )
    return result


def collection_protocol(index: Path, baseline: dict, model) -> dict:
    return {
        "schema_version": 1,
        "config_id": CONFIG_ID,
        "repetition": 1,
        "cases": {"path": str(FROZEN / "cases.json"), "sha256": sha256(FROZEN / "cases.json")},
        "gold": {
            "path": str(COLLECTION / "resolved-gold.json"),
            "sha256": sha256(COLLECTION / "resolved-gold.json"),
        },
        "baseline": {"config_id": "p2_full", "run": str(FROZEN), "reused_without_rerun": True},
        "index": {
            "path": str(index / "index.json"),
            "sha256": sha256(index / "index.json"),
            "frozen_index_sha256": baseline["index_sha256"],
            "only_manifest_source_paths_relocated_after_sha256_verification": True,
        },
        "settings": {**asdict(make_settings(index)), "data_dir": str(index)},
        "agent_limits": {"model_calls": 3, "tool_calls": 4, "seconds": 180, "retries": 1},
        "agent_search_top_k": 10,
        "generation_model": model.model,
        "generation_configuration": model.configuration(),
        "scope": (
            "120 original questions; Agent-controlled search/read_parent/final; "
            "no hidden translation/decomposition; concise prompt and thinking disabled "
            "to fit the unchanged 2048-token limit"
        ),
    }


def collect(args) -> None:
    baseline = verify_baseline()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    index = relocated_index(output / "index-relocated")
    retrieval = RetrievalService(make_settings(index))
    if retrieval.settings.fingerprint() != retrieval.index_fingerprint:
        raise ValueError("relocated_index_fingerprint_mismatch")
    model = configured_model(Path(args.env_file) if args.env_file else None)
    model.disable_thinking = True
    if model.model != baseline["generation_model"] or model.max_tokens != 2048:
        raise ValueError("generation_model_or_output_budget_differs_from_frozen_baseline")
    save(output / "protocol.json", collection_protocol(index, baseline, model))
    save(output / "cases.json", load(FROZEN / "cases.json"))
    cases = load_cases()
    selected = cases[: args.limit] if args.limit else cases
    with (output / "records.jsonl").open("x", encoding="utf-8") as stream:
        for number, case in enumerate(selected, 1):
            started = perf_counter()
            trace_dir = output / "traces" / f"{number:03d}-{case['case_id']}"
            chain = AgenticRAGChain(retrieval, model, domain=case.get("domain"), top_k=10)
            error = None
            try:
                result = chain.retrieve(
                    case["query"],
                    run_id=f"{CONFIG_ID}-1",
                    case_id=case["case_id"],
                    output_dir=trace_dir,
                )
            except Exception as exc:
                error = type(exc).__name__
                result = {
                    "candidates": [],
                    "ranked": [],
                    "evidence": [],
                    "trace": {},
                    "final": {"status": "error", "answer": None, "citations": []},
                }
            evidence = result.get("evidence", {})
            if isinstance(evidence, dict):
                evidence = evidence.get("delivered", [])
            final = result.get("final", {})
            trace = result.get("trace", {})
            if error is None:
                integrity = evidence_integrity(retrieval, evidence)
                if integrity["status"] != "valid":
                    raise ValueError(f"evidence_integrity_failed:{case['case_id']}:{integrity}")
            cited = {e["evidence_id"] for e in final.get("citations", []) if isinstance(e, dict)}
            if not cited <= {item["id"] for item in evidence}:
                raise ValueError(f"citation_outside_delivered:{case['case_id']}")
            status = final.get("status", "error")
            relevant = case["relevant"]
            retrieved = [
                item["chunk_id"] if isinstance(item, dict) else item
                for item in result.get("ranked", [])
            ]
            candidates = [
                item["chunk_id"] if isinstance(item, dict) else item
                for item in result.get("candidates", [])
            ]
            delivered = [item["chunk_id"] for item in evidence]
            gold = {key: case[key] for key in ("id", "evidence_alternatives")}
            row = {
                "run_id": output.name,
                "config_id": CONFIG_ID,
                "repetition": 1,
                "case_id": case["case_id"],
                "group_id": case["group_id"],
                "query": case["query"],
                "reference": case["reference"],
                "question_type": case["question_type"],
                "split": case["split"],
                "answerable": case["answerable"],
                "relevant": relevant,
                "queries": [
                    r["action"].get("query")
                    for r in trace.get("steps", [])
                    if r.get("action", {}).get("tool") == "search"
                ],
                "candidates": result.get("candidates", []),
                "retrieved": retrieved,
                "evidence": evidence,
                "context": "\n\n".join(e["content"] for e in evidence),
                "retrieval@5": metrics(retrieved, relevant, 5) if relevant else None,
                "retrieval@10": metrics(retrieved, relevant, 10) if relevant else None,
                "candidate_recall@10": metrics(candidates, relevant, 10)["recall"]
                if relevant
                else None,
                "delivered_recall@10": metrics(delivered, relevant, max(1, len(delivered)))[
                    "recall"
                ]
                if relevant
                else None,
                "complete@10": evidence_metrics(retrieved, gold, 10)["complete_evidence_hit"]
                if relevant
                else None,
                "delivered_complete": evidence_metrics(delivered, gold, max(1, len(delivered)))[
                    "complete_evidence_hit"
                ]
                if relevant
                else None,
                "response": final.get("answer"),
                "status": "answered" if status == "answered" else "no_evidence",
                "agent_status": status,
                "citations": final.get("citations", []),
                "trace": {
                    "path": str(trace_dir / "trace.json"),
                    "cumulative_path": str(trace_dir / "agentic_trace.json"),
                    "events": trace.get("events", []),
                    "resources": trace.get("resources", {}),
                    "measurement": trace.get("measurement", {}),
                    "retrieval_rounds": trace.get("retrieval_rounds", []),
                },
                "generation_calls": [c.get("metadata", {}) for c in trace.get("ledger", [])],
                "attempts": 1,
                "error": error,
                "latency_ms": result.get("latency_ms", (perf_counter() - started) * 1000),
            }
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
            stream.flush()
            print(
                f"[{number:03d}/{len(selected)}] {case['case_id']} {status} "
                f"evidence={len(evidence)} calls={len(row['generation_calls'])} "
                f"latency={row['latency_ms'] / 1000:.1f}s error={error}",
                flush=True,
            )
    if not args.limit:
        save(
            output / "complete.json",
            {
                "cases": 120,
                "cases_sha256": sha256(output / "cases.json"),
                "protocol_sha256": sha256(output / "protocol.json"),
                "records_sha256": sha256(output / "records.jsonl"),
            },
        )


def judge(args):
    from infra_rag.ragas_evaluation import RagasJudge

    env = model_environment(Path(args.env_file) if args.env_file else None)
    os.environ["OPENAI_API_KEY"] = env["OPENAI_API_KEY"]
    os.environ["OPENAI_BASE_URL"] = env.get("OPENAI_BASE_URL", "https://moerouter.com/v1")
    return RagasJudge(
        "glm-5.3-flash",
        "BAAI/bge-small-zh-v1.5",
        timeout=60,
        max_retries=3,
        embedding_backend="huggingface",
        max_tokens=4096,
        disable_thinking=True,
    )


def validated_collection(output: Path) -> list[dict]:
    verify_baseline()
    complete = load(output / "complete.json")
    if complete != {
        "cases": 120,
        "cases_sha256": sha256(output / "cases.json"),
        "protocol_sha256": sha256(output / "protocol.json"),
        "records_sha256": sha256(output / "records.jsonl"),
    }:
        raise ValueError("collection_incomplete_or_changed")
    rows = records(output / "records.jsonl")
    if [(r["config_id"], r["case_id"], r["repetition"]) for r in rows] != [
        (CONFIG_ID, c["case_id"], 1) for c in load_cases()
    ]:
        raise ValueError("collection_case_order_mismatch")
    return rows


def validate_judge(scorer, frozen_judge):
    configuration = scorer.configuration
    expected = {
        "model": frozen_judge["judge_model"],
        "embedding_model": frozen_judge["embedding_model"],
        "embedding_backend": "huggingface",
        "max_tokens": frozen_judge["max_tokens"],
        "disable_thinking": frozen_judge["disable_thinking"],
        "timeout_seconds": frozen_judge["timeout_seconds"],
        "max_retries": frozen_judge["http_retries"],
        "ragas_version": frozen_judge["dependencies"]["ragas"],
    }
    if any(configuration.get(key) != value for key, value in expected.items()):
        raise ValueError("ragas_judge_configuration_differs_from_frozen_baseline")
    if frozen_judge["embedding_backend"] != "huggingface CPU":
        raise ValueError("unexpected_frozen_embedding_backend")


def score_shard(args) -> None:
    rows = validated_collection(args.output.resolve())[args.shard :: 8]
    directory = args.output.resolve() / "ragas"
    directory.mkdir(exist_ok=True)
    path = directory / f"rows-shard-{args.shard}.jsonl"
    frozen_judge = load(FROZEN / "ragas/protocol.json")
    scorer = judge(args)
    validate_judge(scorer, frozen_judge)
    from infra_rag.ragas_evaluation import run_scoring

    with path.open("x", encoding="utf-8") as stream:

        def persist(row):
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
            stream.flush()
            print(f"shard={args.shard} case={row['case_id']}", flush=True)

        run_scoring(rows, scorer, on_row=persist)


def unused_path(path: Path) -> Path:
    if not path.exists():
        return path
    for attempt in range(2, 1000):
        candidate = path.with_name(f"{path.stem}-attempt-{attempt}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"too_many_attempt_logs:{path}")


def score(args, shard_ids=range(8)) -> None:
    output = args.output.resolve()
    validated_collection(output)
    (output / "ragas").mkdir(exist_ok=True)
    frozen_protocol = load(FROZEN / "ragas/protocol.json")
    scorer = judge(args)
    validate_judge(scorer, frozen_protocol)
    judge_protocol = {
        **frozen_protocol,
        "source_complete": load(output / "complete.json"),
        "runtime_configuration": scorer.configuration,
    }
    protocol_path = output / "ragas/protocol.json"
    runtime_path = output / "ragas/runtime-configuration.json"
    if protocol_path.exists():
        existing = load(protocol_path)
        if existing.get("runtime_configuration") is not None:
            if existing != judge_protocol:
                raise ValueError("existing_ragas_protocol_mismatch")
        elif existing != frozen_protocol | {"source_complete": load(output / "complete.json")}:
            raise ValueError("existing_ragas_protocol_mismatch")
        if runtime_path.exists() and load(runtime_path) != scorer.configuration:
            raise ValueError("existing_ragas_runtime_configuration_mismatch")
    else:
        save(protocol_path, judge_protocol)
    if not runtime_path.exists():
        save(runtime_path, scorer.configuration)
    processes = []
    for shard in shard_ids:
        env = {**os.environ, "HF_HUB_OFFLINE": "1", "OMP_NUM_THREADS": "2"}
        env["RAGAS_DO_NOT_TRACK"] = "true"
        env["TOKENIZERS_PARALLELISM"] = "false"
        env.pop("NO_PROXY", None)
        env.pop("no_proxy", None)
        command = [
            sys.executable,
            str(Path(__file__).resolve()),
            "score-shard",
            "--output",
            str(output),
            "--shard",
            str(shard),
        ]
        if args.env_file:
            command += ["--env-file", args.env_file]
        log = unused_path(output / f"score-shard-{shard}.log").open("x", encoding="utf-8")
        processes.append(
            (subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT), log)
        )
    failed = []
    for shard, (process, log) in enumerate(processes):
        code = process.wait()
        log.close()
        if code:
            failed.append({"shard": shard, "exit_code": code})
    if failed:
        raise RuntimeError(f"ragas_shards_failed:{failed}; inspect score-shard logs")
    for shard in range(8):
        shard_path = output / "ragas" / f"rows-shard-{shard}.jsonl"
        expected = len(validated_collection(output)[shard::8])
        if len(records(shard_path)) != expected:
            raise RuntimeError(f"ragas_shard_incomplete:{shard}:{expected}")
    finalize_scores(output)


def merge_repaired_rows(original: list[dict], repaired: list[dict]) -> list[dict]:
    by_id = {row["case_id"]: row for row in repaired}
    result = []
    for row in original:
        patch = by_id.get(row["case_id"])
        if patch is None:
            result.append(row)
            continue
        merged = dict(row)
        merged["ragas"] = dict(row["ragas"])
        merged["judge_errors"] = dict(row["judge_errors"])
        merged["judge_calls"] = list(row["judge_calls"])
        merged["ragas_repairs"] = list(row.get("ragas_repairs", []))
        for metric, value in patch["ragas"].items():
            if row["ragas"].get(metric) is not None or value is None:
                continue
            merged["ragas"][metric] = value
            merged["judge_errors"].pop(metric, None)
            calls = patch.get("judge_calls", [])
            merged["judge_calls"].extend(calls)
            merged["ragas_repairs"].append(
                {
                    "metric": metric,
                    "original_error": row["judge_errors"].get(metric),
                    "repaired_calls": len(calls),
                    "judge_latency_ms": patch.get("judge_latency_ms"),
                }
            )
        result.append(merged)
    return result


def finalize_scores(output: Path) -> None:
    shards = [records(output / "ragas" / f"rows-shard-{i}.jsonl") for i in range(8)]
    by_id = {row["case_id"]: row for shard in shards for row in shard}
    ordered = [by_id[r["case_id"]] for r in validated_collection(output)]
    repairs_path = output / "ragas/rows-repaired.jsonl"
    if repairs_path.exists():
        ordered = merge_repaired_rows(ordered, records(repairs_path))
    from infra_rag.ragas_evaluation import summarize

    save(output / "ragas/rows.json", ordered)
    save(output / "ragas/summary.json", summarize(ordered))
    save(
        output / "ragas/process-status.json",
        {
            "rows": len(ordered),
            "shards": 8,
            "rows_with_missing_scores": sum(
                any(v is None for v in r["ragas"].values()) for r in ordered
            ),
        },
    )


def repair_scores(args) -> None:
    output = args.output.resolve()
    rows = load(output / "ragas/rows.json")
    path = output / "ragas/rows-repaired.jsonl"
    from infra_rag.ragas_evaluation import METRICS as SCORER_METRICS
    from infra_rag.ragas_evaluation import score_records

    async def run(scorer):
        result = []
        for row in rows:
            missing = [name for name in METRICS if row["ragas"].get(name) is None]
            if not missing:
                continue
            patch = {**row, "ragas": {name: None for name in SCORER_METRICS}, "judge_errors": {}}
            # Reuse the unchanged scorer; restrict this attempt to missing metrics only.
            original = scorer.scorers
            scorer.scorers = {name: original[name] for name in missing}
            try:
                scored = await score_records([patch], scorer)
                result.extend(scored)
            finally:
                scorer.scorers = original
        return result

    import asyncio

    scorer = judge(args)
    validate_judge(scorer, load(FROZEN / "ragas/protocol.json"))

    async def execute():
        try:
            return await run(scorer)
        finally:
            await scorer.close()

    repaired = asyncio.run(execute())
    with path.open("x", encoding="utf-8") as stream:
        for row in repaired:
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
    print(json.dumps({"repaired_cases": len(repaired)}, indent=2))


def finalize_repair(args) -> None:
    output = args.output.resolve()
    if not (output / "ragas/rows-repaired.jsonl").is_file():
        raise ValueError("no_ragas_repair_file")
    if (output / "ragas/rows-repaired-final.json").exists():
        raise FileExistsError("ragas_repaired_final_already_exists")
    ordered = merge_repaired_rows(
        load(output / "ragas/rows.json"), records(output / "ragas/rows-repaired.jsonl")
    )
    from infra_rag.ragas_evaluation import summarize

    save(output / "ragas/rows-repaired-final.json", ordered)
    save(output / "ragas/summary-repaired.json", summarize(ordered))


def paired(a: list[float], b: list[float], cases: list[dict], draws=10000) -> dict:
    groups = defaultdict(list)
    for case, value_a, value_b in zip(cases, a, b, strict=True):
        groups[case["group_id"]].append((value_a, value_b))
    keys = list(groups)
    rng = random.Random(42)
    observed = statistics.mean(y - x for values in groups.values() for x, y in values)
    bootstrap = []
    for _ in range(draws):
        sampled = [rng.choice(keys) for _ in keys]
        bootstrap.append(statistics.mean(y - x for key in sampled for x, y in groups[key]))
    bootstrap.sort()
    permutation = []
    for _ in range(draws):
        signs = {key: rng.choice((-1, 1)) for key in keys}
        permutation.append(
            statistics.mean(signs[key] * (y - x) for key in keys for x, y in groups[key])
        )
    return {
        "n": len(a),
        "clusters": len(keys),
        "difference": observed,
        "ci95": [bootstrap[int(0.025 * draws)], bootstrap[int(0.975 * draws) - 1]],
        "p_value": (sum(abs(v) >= abs(observed) - 1e-12 for v in permutation) + 1) / (draws + 1),
    }


def mean(values):
    return statistics.mean(values) if values else None


def usage_summary(rows: list[dict]) -> dict:
    calls = [call for row in rows for call in row.get("generation_calls", [])]
    reasoning = sum(
        (call.get("usage") or {}).get("completion_tokens_details", {}).get("reasoning_tokens", 0)
        for call in calls
    )
    return {
        "calls": len(calls),
        "input_tokens": sum(
            (call.get("usage") or {}).get("prompt_tokens", 0)
            for row in rows
            for call in row.get("generation_calls", [])
        ),
        "output_tokens": sum(
            (call.get("usage") or {}).get("completion_tokens", 0)
            for row in rows
            for call in row.get("generation_calls", [])
        ),
        "reasoning_tokens": reasoning,
        "length_truncated_calls": sum(call.get("stop_reason") == "length" for call in calls),
        "cost_usd": None,
    }


def format_score(value):
    return "n/a" if value is None else f"{value:.4f}"


def report(args) -> None:
    verify_baseline()
    output = args.output.resolve()
    baseline = load(FROZEN / "ragas/rows.json")
    agentic_path = output / "ragas/rows-repaired-final.json"
    agentic = load(agentic_path if agentic_path.exists() else output / "ragas/rows.json")
    cases = load_cases()
    if len(agentic) != 120:
        raise ValueError("120_scored_agentic_rows_required")
    b = {r["case_id"]: r for r in baseline}
    a = {r["case_id"]: r for r in agentic}
    if set(a) != set(b):
        raise ValueError("paired_case_ids_mismatch")
    both = [
        c["case_id"]
        for c in cases
        if b[c["case_id"]]["status"] == a[c["case_id"]]["status"] == "answered"
    ]
    scopes = {
        "all_120": [c["case_id"] for c in cases],
        "both_answered": both,
        "answerable_108": [c["case_id"] for c in cases if c["answerable"]],
        "answerable_both_answered": [i for i in both if a[i]["answerable"]],
    }
    comparisons = {}
    for scope, ids in scopes.items():
        selected = [c for c in cases if c["case_id"] in ids]
        comparisons[scope] = {"cases": len(ids), "metrics": {}}
        for metric in METRICS:
            x = [b[i]["ragas"].get(metric) for i in ids]
            y = [a[i]["ragas"].get(metric) for i in ids]
            complete_scores = all(v is not None for v in x + y)
            comparisons[scope]["metrics"][metric] = {
                "baseline_mean": mean(x) if complete_scores else None,
                "agentic_mean": mean(y) if complete_scores else None,
                "delta": mean(y) - mean(x) if complete_scores else None,
                "paired": paired(x, y, selected)
                if complete_scores
                else {"error": "missing scores not imputed"},
            }

    def counts(rows):
        positive = [r for r in rows if r["answerable"]]
        negative = [r for r in rows if not r["answerable"]]
        statuses = [
            r.get("agent_status") or ("refused" if r["status"] == "no_evidence" else "answered")
            for r in rows
        ]

        def refused(status):
            return status in ("refused", "no_evidence")

        def escalated(status):
            return status == "escalated"

        return {
            "answerable": len(positive),
            "answered": sum(r["status"] == "answered" for r in positive),
            "incorrect_refusal": sum(
                refused(status) for r, status in zip(rows, statuses, strict=True) if r["answerable"]
            ),
            "escalated_answerable": sum(
                escalated(status)
                for r, status in zip(rows, statuses, strict=True)
                if r["answerable"]
            ),
            "unanswerable": len(negative),
            "correct_refusal_unanswerable": sum(
                refused(status)
                for r, status in zip(rows, statuses, strict=True)
                if not r["answerable"]
            ),
            "escalated_unanswerable": sum(
                escalated(status)
                for r, status in zip(rows, statuses, strict=True)
                if not r["answerable"]
            ),
            "generation_failures": sum(bool(r.get("error")) for r in rows),
            "complete_delivery": sum(bool(r.get("delivered_complete")) for r in positive),
        }

    groups = {}
    for question_type in sorted({c["question_type"] for c in cases}):
        ids = [c["case_id"] for c in cases if c["question_type"] == question_type]
        groups[question_type] = {
            "cases": len(ids),
            "counts": {
                "baseline": counts([b[i] for i in ids]),
                "agentic": counts([a[i] for i in ids]),
            },
        }
        for metric in METRICS:
            groups[question_type].setdefault("metrics", {})[metric] = {
                name: mean([rows[i]["ragas"].get(metric) for i in ids if rows[i]["answerable"]])
                for name, rows in (("baseline", b), ("agentic", a))
            }
    result = {
        "protocol": (
            "frozen P2 Baseline; Agentic-only live collection; "
            "identical official cases and RAGAS judge"
        ),
        "cases": 120,
        "both_answered_cases": len(both),
        "counts": {"baseline": counts(baseline), "agentic": counts(agentic)},
        "usage": {
            name: usage_summary(rows)
            for name, rows in (("baseline", baseline), ("agentic", agentic))
        },
        "comparisons": comparisons,
        "by_type": groups,
        "agentic_failures_or_refusals": [
            {
                "case_id": r["case_id"],
                "question_type": r["question_type"],
                "split": r["split"],
                "agent_status": r.get("agent_status"),
                "events": r["trace"]["events"],
                "error": r.get("error"),
                "judge_errors": r.get("judge_errors", {}),
            }
            for r in agentic
            if r["status"] != "answered" or r.get("error")
        ],
        "baseline_summary": load(FROZEN / "ragas/summary.json")["p2_full"],
        "agentic_summary": load(
            output
            / "ragas"
            / ("summary-repaired.json" if agentic_path.exists() else "summary.json")
        )[CONFIG_ID],
        "limitations": [
            "RAGAS is a same-provider LLM judge, not independent human factual verification.",
            (
                "Agent uses concise structured-output prompting and disabled thinking; "
                "frozen Baseline did not."
            ),
            (
                "Agent planning/tool/final calls differ from Baseline "
                "translation/decomposition/generation by design."
            ),
            (
                "Only manifest paths were relocated after all source SHA256 checks; "
                "frozen data was not changed."
            ),
            "One live run; holdout was previously consumed. No claim about all Agentic systems.",
        ],
    }
    save(output / "comparison.json", result)
    lines = [
        "# Agentic RAG vs frozen Native RAG：120题 RAGAS 配对报告",
        "",
        (
            "仅运行 Agentic RAG；Baseline 复用 `evals/ragas-p2-v1/run-20261112`。"
            "同一官方120题、BGE-M3索引、Top10、2400 token/8000字符预算、"
            "生成模型与 RAGAS 评分器。"
        ),
        "",
        "| 口径 | 指标 | Baseline | Agentic | 差值 |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for scope, item in comparisons.items():
        for metric in METRICS:
            value = item["metrics"][metric]
            lines.append(
                f"| {scope} | {metric} | {format_score(value['baseline_mean'])} "
                f"| {format_score(value['agentic_mean'])} | {format_score(value['delta'])} |"
            )
    lines += [
        "",
        "## 拒答与执行",
        "",
        "```json",
        json.dumps(result["counts"], ensure_ascii=False, indent=2),
        "```",
        "",
        (
            "逐题指标、配对区间、题型、失败事件和用量见 `comparison.json`、"
            "`ragas/rows.json` 和 `traces/`。"
        ),
        "",
        "RAGAS 不是独立人审；这是单次真实运行，不推断所有 Agentic 系统优劣。holdout 已消耗。",
    ]
    save(output / "report.md", "\n".join(lines) + "\n")
    print(
        json.dumps(
            {"counts": result["counts"], "comparisons": comparisons}, ensure_ascii=False, indent=2
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    commands = (
        "collect",
        "score",
        "score-shards",
        "score-shard",
        "repair-scores",
        "finalize-repair",
        "report",
    )
    for name in commands:
        child = sub.add_parser(name)
        if name == "score-shards":
            child.add_argument("--shards", type=int, nargs="+", required=True)
        child.add_argument("--output", type=Path, required=True)
        if name != "report":
            child.add_argument("--env-file")
        if name == "collect":
            child.add_argument(
                "--limit", type=int, help="isolated smoke; does not write complete.json"
            )
        if name == "score-shard":
            child.add_argument("--shard", type=int, required=True, choices=range(8))
    args = parser.parse_args()
    if args.command == "score-shards":
        args.command = "score"
    if args.command == "score" and hasattr(args, "shards"):
        return score(args, shard_ids=args.shards)
    handlers = {
        "collect": collect,
        "score": score,
        "score-shard": score_shard,
        "repair-scores": repair_scores,
        "finalize-repair": finalize_repair,
        "report": report,
    }
    handlers[args.command](args)


if __name__ == "__main__":
    main()
