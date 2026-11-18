"""Collect paired dev ablations, then score their frozen delivered answers with Ragas."""

import argparse
import importlib.metadata
import json
import subprocess
from pathlib import Path

from operation_log import ROOT, record_operation

from infra_rag.config import Settings
from infra_rag.model_clients import configured_model
from infra_rag.ragas_ablation import CONFIGS, collect_records, configuration
from infra_rag.ragas_evaluation import (
    RagasJudge,
    digest,
    run_scoring,
    summarize,
    validate_cases,
)
from infra_rag.service import RetrievalService


def write(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)


def implementation():
    paths = [*sorted((ROOT / "src/infra_rag").glob("*.py")), Path(__file__), ROOT / "uv.lock"]
    return {str(p.relative_to(ROOT)): digest(p.read_text()) for p in paths}


def collect(args):
    cases = json.loads(args.cases.read_text())
    validate_cases(cases)
    values = json.loads(args.settings.read_text())
    values["data_dir"] = Path(values["data_dir"])
    if not (values["data_dir"] / "index.json").is_file():
        raise ValueError("an existing isolated index is required")
    settings = Settings(**values)
    if settings.backend == "demo":
        raise ValueError("real ablations require bge/qwen; demo is only plumbing")
    if settings.multimodal:
        raise ValueError(
            "four-way ablation requires a text index; score captions offline separately"
        )
    if args.k > settings.candidate_k:
        raise ValueError("k must not exceed candidate_k")
    service = RetrievalService(settings)
    client = configured_model()
    args.output.mkdir(parents=True, exist_ok=False)
    manifest = {
        "run_id": args.output.name,
        "split": args.split,
        "cases_sha256": digest(cases),
        "configurations": list(CONFIGS),
        "repetitions": args.repetitions,
        "k": args.k,
        "configuration": configuration(service),
        "index_sha256": digest(service.snapshot.read_text()),
        "source_manifest": service.source_manifest,
        "generation_model": client.model,
        "generation_configuration": client.configuration()
        if hasattr(client, "configuration")
        else {"model": client.model, "identity": "mutable local model tag"},
        "implementation": implementation(),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "limitations": "component experiment; no independent human review or task success; "
        "fixed sequential ordering; analysis reports paired uncertainty separately",
    }
    write(args.output / "protocol.json", manifest)
    write(args.output / "cases.json", cases)
    with (args.output / "records.jsonl").open("x", encoding="utf-8") as stream:
        for row in collect_records(
            service,
            cases,
            client,
            run_id=manifest["run_id"],
            k=args.k,
            repetitions=args.repetitions,
        ):
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
            stream.flush()
    write(
        args.output / "complete.json",
        {
            "records_sha256": digest((args.output / "records.jsonl").read_text()),
            "protocol_sha256": digest(manifest),
        },
    )


def score(args):
    protocol = json.loads((args.run / "protocol.json").read_text())
    complete = json.loads((args.run / "complete.json").read_text())
    raw = (args.run / "records.jsonl").read_text()
    if complete != {"records_sha256": digest(raw), "protocol_sha256": digest(protocol)}:
        raise ValueError("frozen collection hashes do not match")
    cases = json.loads((args.run / "cases.json").read_text())
    if digest(cases) != protocol["cases_sha256"]:
        raise ValueError("frozen cases changed")
    records = [json.loads(line) for line in raw.splitlines()]
    keys = [(r["run_id"], r["config_id"], r["case_id"], r["repetition"]) for r in records]
    expected = {
        (protocol["run_id"], config, case["id"], rep)
        for config in protocol["configurations"]
        for case in cases
        for rep in range(protocol["repetitions"])
    }
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise ValueError("duplicate or missing paired outputs")
    args.output.mkdir(parents=True, exist_ok=False)
    judge = RagasJudge(
        args.judge_model,
        args.embedding_model,
        timeout=args.timeout,
        max_retries=args.max_retries,
        embedding_backend=args.embedding_backend,
        max_tokens=args.judge_max_tokens,
        disable_thinking=args.disable_thinking,
    )
    write(
        args.output / "protocol.json",
        {
            "input": complete,
            "judge": judge.configuration,
            "implementation": implementation(),
            "dependencies": {p: importlib.metadata.version(p) for p in ("ragas", "openai")},
            "scope": "LLM auxiliary scores, not independent human judgments or task success",
        },
    )
    with (args.output / "rows.jsonl").open("x", encoding="utf-8") as stream:

        def persist(row):
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
            stream.flush()

        rows = run_scoring(records, judge, on_row=persist)
    write(args.output / "rows.json", rows)
    write(args.output / "summary.json", summarize(rows))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("collect", help="four paired real-model dev ablations")
    p.add_argument("--cases", type=Path, required=True)
    p.add_argument("--settings", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--k", type=int, default=5)
    p.add_argument("--repetitions", type=int, default=1)
    p.add_argument("--split", default="dev", help="frozen split label recorded in protocol")
    p = sub.add_parser("score", help="score a complete frozen collection")
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--judge-model", required=True)
    p.add_argument("--embedding-model", required=True)
    p.add_argument("--embedding-backend", choices=("openai", "huggingface"), default="openai")
    p.add_argument("--judge-max-tokens", type=int, default=1024)
    p.add_argument("--disable-thinking", action="store_true", help="DeepSeek-compatible extra_body")
    p.add_argument("--timeout", type=float, default=60)
    p.add_argument("--max-retries", type=int, default=0)
    args = parser.parse_args()
    if getattr(args, "k", 1) < 1 or getattr(args, "repetitions", 1) < 1:
        parser.error("k and repetitions must be positive")
    if getattr(args, "judge_max_tokens", 1) < 1:
        parser.error("judge max tokens must be positive")
    if getattr(args, "timeout", 1) <= 0 or getattr(args, "max_retries", 0) < 0:
        parser.error("timeout must be positive and retries nonnegative")
    try:
        (collect if args.command == "collect" else score)(args)
    except BaseException as exc:
        record_operation(
            f"Ragas {args.command}",
            "固定 dev 消融或辅助评分",
            "未完成；保留部分产物",
            type(exc).__name__,
        )
        raise
    record_operation(f"Ragas {args.command}", "固定 dev 消融或辅助评分", str(args.output))


if __name__ == "__main__":
    main()
