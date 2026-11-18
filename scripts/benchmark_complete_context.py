"""Paired live /chat development check; no automatic semantic pass or default adoption."""

import argparse
import json
import shutil
import urllib.request
from pathlib import Path

from benchmark_runtime_e2e import request
from operation_log import ROOT, record_operation

from infra_rag.benchmarking import canonical_hash, digest, write_new
from infra_rag.model_clients import configured_model

SERVICES = {
    "prefix": {"port": 8000, "journal": "data/local-web/requests.jsonl"},
    "complete": {"port": 8002, "journal": "data/complete-context-v1/runtime/requests.jsonl"},
}
IDS = {"bc01", "bc02", "bc07", "bc08", "bc09", "bc10", "bc12", "bc13", "bc14"}
CASES = ROOT / "evals/user-badcases-v1/cases-20261029.json"
INDEX = ROOT / "data/local-web/index/index.json"


def load(path):
    return json.loads(path.read_text())


def health(port):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=15) as response:
        return json.load(response)


def freeze(out):
    if out.exists():
        raise ValueError("Fresh experiment directory required")
    selected = [c for c in load(CASES) if c["id"] in IDS]
    assert len(selected) == 9 and sum(len(c["questions"]) for c in selected) == 10
    configs = {name: health(spec["port"]) for name, spec in SERVICES.items()}
    for config in configs.values():
        assert config["runtime"]["reranker_batch_size"] == 32
        assert config["runtime"]["retrieval_cache_capacity"] == 0
        assert config["candidate_k"] == 30 and config["context_tokens"] == 1200
        assert config["context_chars"] == 4000
    assert configs["prefix"].get("context_policy", "prefix") == "prefix"
    assert configs["complete"]["context_policy"] == "complete"
    assert configs["complete"]["fingerprint"] == configs["prefix"]["fingerprint"]
    assert digest(INDEX) == digest(ROOT / "data/complete-context-v1/runtime/index/index.json")
    out.mkdir(parents=True)
    code = [
        Path(__file__).resolve(),
        ROOT / "scripts/serve_local.py",
        *sorted((ROOT / "src/infra_rag").glob("*.py")),
    ]
    for path in code:
        target = out / "implementation" / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    source_manifest = load(ROOT / "data/user-badcases-v1/run-20261029/protocol.json")[
        "source_sha256"
    ]
    write_new(out / "cases.json", selected)
    write_new(
        out / "protocol.json",
        {
            "kind": "Paired live HTTP dev check after component tuning; no heldout claim",
            "configs": configs,
            "services": SERVICES,
            "cases_sha256": digest(CASES),
            "case_hashes": {c["id"]: canonical_hash(c) for c in selected},
            "index_sha256": digest(INDEX),
            "sources": source_manifest,
            "implementation": {str(p.relative_to(ROOT)): digest(p) for p in code},
            "model": configured_model().configuration(),
            "scenarios": 9,
            "turns_per_config_per_repetition": 10,
            "repetitions": 3,
            "planned_http": 60,
            "max_model_attempts": 120,
            "http_retries": 0,
            "warm_state": "Both embedding/reranker prewarmed by search; no generation prewarm",
            "order": "Alternate paired config order by case+repetition parity; sequential turns",
            "quality_gate": "AI review separately; bc02/bc09 must consume required full evidence. "
            "Controls bc08/bc12 and correct refusal bc13 must not regress.",
            "human_review": "pending",
            "adoption": "Default prefix unchanged pending review",
            "pagination": False,
            "latency": "All attempts, nearest-rank p95, descriptive only",
            "cost_usd": None,
            "holdout_read": False,
        },
    )


def run(out):
    protocol = load(out / "protocol.json")
    assert digest(CASES) == protocol["cases_sha256"]
    assert digest(INDEX) == protocol["index_sha256"]
    for name, sha in protocol["implementation"].items():
        assert digest(ROOT / name) == sha, name
    for name, sha in protocol["sources"].items():
        assert digest(name) == sha, name
    for name, spec in SERVICES.items():
        assert health(spec["port"]) == protocol["configs"][name]
    rows = []
    for rep in range(3):
        for i, case in enumerate(load(out / "cases.json")):
            order = ["prefix", "complete"] if (rep + i) % 2 == 0 else ["complete", "prefix"]
            for config in order:
                conversation = None
                for turn, question in enumerate(case["questions"], 1):
                    target = out / "outputs" / f"{config}-{case['id']}-t{turn}-r{rep}.json"
                    if target.exists():
                        raise ValueError("No overwrite/retry of frozen runs")
                    payload = {"message": question}
                    if turn > 1 and not conversation:
                        row = {"http_status": None, "error": "No preceding conversation"}
                    else:
                        if conversation:
                            payload["conversation_id"] = conversation
                        row = request(f"http://127.0.0.1:{SERVICES[config]['port']}", payload)
                    conversation = row.get("response", {}).get("conversation_id")
                    rid = row.get("request_id")
                    journal = ROOT / SERVICES[config]["journal"]
                    matches = (
                        [
                            json.loads(s)
                            for s in journal.read_text().splitlines()
                            if json.loads(s)["request_id"] == rid
                        ]
                        if rid
                        else []
                    )
                    row.update(
                        run_id=out.name,
                        config_id=config,
                        case_id=case["id"],
                        turn=turn,
                        repetition=rep,
                        question=question,
                        case_sha256=protocol["case_hashes"][case["id"]],
                    )
                    if len(matches) == 1:
                        row["server_record"] = matches[0]
                    write_new(target, row)
                    rows.append(row)
                    print(
                        config,
                        case["id"],
                        turn,
                        rep,
                        row.get("http_status"),
                        row.get("response", {}).get("status"),
                        flush=True,
                    )
    calls = sum(len(r.get("server_record", {}).get("model_calls", [])) for r in rows)
    write_new(
        out / "run-summary.json",
        {
            "outputs": len(rows),
            "planned": 60,
            "actual_model_attempts": calls,
            "missing_journal": sum(not r.get("server_record") for r in rows),
            "answer_correctness": None,
            "human_review": "pending",
        },
    )
    write_new(
        out / "manifest.json",
        {str(p.relative_to(out)): digest(p) for p in out.rglob("*") if p.is_file()},
    )
    assert len(rows) == 60 and calls <= 120


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["freeze", "run"])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    (freeze if args.phase == "freeze" else run)(args.out)
    record_operation(
        f"完整证据实模实验 {args.phase}",
        "固定参数配对重复检查交付是否被消费",
        f"产物 {args.out}；独立人工审核pending，不切默认",
    )


if __name__ == "__main__":
    main()
