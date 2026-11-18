"""Freeze and run the user's 15 badcase scenarios against both live /chat services."""

import argparse
import json
from pathlib import Path

from benchmark_runtime_e2e import request
from operation_log import ROOT, record_operation
from prepare_corpus_pilot import load, save

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.model_clients import configured_model

BOOK = ROOT / "data/datasets/infra-repos-v1/corpus/ai-infra-book/manuscripts"
SERVICES = {
    "main": {"port": 8000, "folder": "local-web"},
    "optimized": {"port": 8001, "folder": "local-web-optimized"},
}


def cases():
    return load(ROOT / "evals/user-badcases-v1/cases-20261029.json")


def health(port):
    import urllib.request

    with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=10) as r:
        return json.load(r)


def freeze(out):
    if out.exists():
        raise ValueError("Fresh output directory required")
    out.mkdir(parents=True)
    data = cases()
    save(out / "cases.json", data)
    ranges = {
        "02-模型架构.md": [(314, 360), (396, 436)],
        "05-算子与运行时.md": [(437, 465)],
        "06-超节点.md": [(638, 644)],
        "08-推理优化.md": [(108, 118), (250, 274), (306, 330), (396, 426), (470, 494), (544, 570)],
        "09-分布式推理.md": [(246, 278), (840, 845)],
    }
    excerpts = []
    for name, spans in ranges.items():
        p = BOOK / name
        lines = p.read_text().splitlines()
        for start, end in spans:
            excerpts.append(
                {
                    "source": str(p),
                    "source_sha256": digest(p),
                    "start_line": start,
                    "end_line": end,
                    "text": "\n".join(lines[start - 1 : end]),
                }
            )
    save(out / "source-excerpts.json", excerpts)
    services = {name: health(spec["port"]) for name, spec in SERVICES.items()}
    indices = {
        name: digest(ROOT / f"data/{spec['folder']}/index/index.json")
        for name, spec in SERVICES.items()
    }
    assert len(set(indices.values())) == 1
    files = [
        Path(__file__).resolve(),
        ROOT / "scripts/benchmark_runtime_e2e.py",
        ROOT / "scripts/serve_local.py",
        ROOT / "evals/user-badcases-v1/cases-20261029.json",
        *sorted((ROOT / "src/infra_rag").glob("*.py")),
    ]
    import shutil

    for p in files:
        target = out / "implementation" / p.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, target)
    save(
        out / "protocol.json",
        {
            "scope": "User supplied diagnostic badcases, not an independent heldout accuracy claim",
            "scenarios": 15,
            "turns_per_config": 16,
            "configs": services,
            "services": SERVICES,
            "index_sha256": indices,
            "models": configured_model().configuration(),
            "case_hashes": {c["id"]: canonical_hash(c) for c in data},
            "source_sha256": {str(BOOK / name): digest(BOOK / name) for name in ranges},
            "implementation": {str(p.relative_to(ROOT)): digest(p) for p in files},
            "order": "Original scenario order; alternate config order by scenario parity",
            "http_requests": 32,
            "repetitions": 1,
            "http_retries": 0,
            "http_timeout_seconds": 240,
            "max_answer_attempts_per_turn": 2,
            "max_model_attempts": 64,
            "cache_state": "Existing live service state; report observed hits, no answer cache",
            "pagination": False,
            "candidate_k": 30,
            "context_tokens": 1200,
            "context_chars": 4000,
            "gold_policy": "Rubrics and source excerpts frozen before model outputs; no ingestion",
            "review": "AI semantic review separated from pending independent human review",
            "statistics": (
                "Descriptive only; badcase-biased, related questions and multi-turn not independent"
            ),
            "test_holdout_read": False,
            "tuning": False,
            "defaults_changed": False,
        },
    )
    return {"phase": "frozen", "scenarios": 15, "planned_http": 32}


def run(out):
    p = load(out / "protocol.json")
    for name, sha in p["implementation"].items():
        assert digest(ROOT / name) == sha, name
    for name, sha in p["source_sha256"].items():
        assert digest(name) == sha, name
    for name, spec in SERVICES.items():
        assert health(spec["port"]) == p["configs"][name]
        assert digest(ROOT / f"data/{spec['folder']}/index/index.json") == p["index_sha256"][name]
    for i, case in enumerate(load(out / "cases.json")):
        configs = ["main", "optimized"] if i % 2 == 0 else ["optimized", "main"]
        for config in configs:
            conv = None
            for turn, q in enumerate(case["questions"]):
                path = out / "outputs" / f"{config}-{case['id']}-t{turn + 1}.json"
                if path.exists():
                    raise ValueError("No retries or overwrite; use a fresh directory")
                if turn and not conv:
                    save(
                        path,
                        {
                            "config": config,
                            "case_id": case["id"],
                            "turn": turn + 1,
                            "attempted": False,
                            "error": "First turn failed to establish conversation",
                        },
                    )
                    break
                payload = {"message": q}
                if conv:
                    payload["conversation_id"] = conv
                row = request(f"http://127.0.0.1:{SERVICES[config]['port']}", payload)
                conv = row.get("response", {}).get("conversation_id")
                record = {
                    **row,
                    "run_id": out.name,
                    "config": config,
                    "case_id": case["id"],
                    "turn": turn + 1,
                    "attempted": True,
                    "question": q,
                    "case_sha256": p["case_hashes"][case["id"]],
                }
                request_id = row.get("request_id")
                if request_id:
                    log = ROOT / f"data/{SERVICES[config]['folder']}/requests.jsonl"
                    matches = [
                        json.loads(s)
                        for s in log.read_text().splitlines()
                        if json.loads(s)["request_id"] == request_id
                    ]
                    assert len(matches) == 1
                    record["server_record"] = matches[0]
                save(path, record)
                save(path.with_suffix(".sha256.json"), {"sha256": digest(path)})
                print(
                    config,
                    case["id"],
                    turn + 1,
                    row.get("http_status"),
                    row.get("response", {}).get("status"),
                    flush=True,
                )
    rows = [
        load(f) for f in (out / "outputs").glob("*.json") if not f.name.endswith(".sha256.json")
    ]
    assert len(rows) == 32
    calls = sum(len(r.get("server_record", {}).get("model_calls", [])) for r in rows)
    assert calls <= 64
    save(
        out / "run-summary.json",
        {
            "outputs": len(rows),
            "actual_model_attempts": calls,
            "unexpected_missing_ledger": sum(not r.get("server_record") for r in rows),
        },
    )
    save(
        out / "artifacts-manifest.json",
        {
            f.relative_to(out).as_posix(): digest(f)
            for f in out.rglob("*")
            if f.is_file() and f.name != "artifacts-manifest.json"
        },
    )
    return {"phase": "run", "outputs": 32, "actual_model_attempts": calls}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=["freeze", "run"], required=True)
    a = parser.parse_args()
    try:
        result = freeze(a.output.resolve()) if a.phase == "freeze" else run(a.output.resolve())
        record_operation(
            "用户badcase批测 " + a.phase,
            "保留15场景、多轮上下文和双服务真实回答",
            str(result),
            "诊断集非独立测试集；AI审核与人工审核分开，未知语义维度保留null",
        )
        print(result)
    except Exception as exc:
        record_operation(
            "用户badcase批测中止", "保留失败与已执行调用，不覆盖重跑", str(a.output), str(exc)
        )
        raise
