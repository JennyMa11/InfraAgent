"""Reviewed diagnostic QA: real AnswerService with frozen retrieval-page replay."""

import argparse
import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from operation_log import ROOT, record_operation
from prepare_corpus_pilot import load, save

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.config import Settings
from infra_rag.model_clients import configured_model
from infra_rag.offline_evaluation import generate_answer

SOURCE = ROOT / "data/bilingual-protected-v1/run-20261028"
REVIEW = ROOT / "evals/retrieval-diagnostic-v2/audit-20261028-v2-reviewed"


def page_context(page):
    return {
        "evidence": [
            {**e, "locator": e["source_url"], "source": e["source_url"]} for e in page["evidence"]
        ]
    }


def prepare(out):
    for name, sha in load(SOURCE / "artifacts-manifest.json").items():
        if digest(SOURCE / name) != sha:
            raise ValueError("Retrieval input changed")
    manifest = load(REVIEW / "review-manifest.json")
    for entry in [manifest["template"], manifest["human_review"], *manifest["evidence"].values()]:
        if digest(ROOT / entry["path"]) != entry["sha256"]:
            raise ValueError("Review hash mismatch")
    cases = load(SOURCE / "questions.json")
    reviews = load(REVIEW / "human-review.json")
    reviewed = {r["id"]: r for r in reviews}
    if len(reviewed) != 30 or len(cases) != 30:
        raise ValueError("Expected 30 reviewed cases")
    for c in cases:
        r = reviewed[c["id"]]
        if r["case_sha256"] != canonical_hash(c) or r["status"] != "approved":
            raise ValueError("Review not approved for current case")
    jobs = []
    for c in cases:
        for arm in ("zh_baseline", "bilingual_context"):
            row = load(SOURCE / "rows" / f"{c['id']}-{arm}.json")
            for index, page in enumerate(row["pages"]):
                if arm == "zh_baseline" and index:
                    continue
                jobs.append(
                    {
                        "id": c["id"],
                        "arm": arm,
                        "page": index,
                        "case": c,
                        "context": page_context(page),
                        "page_sha256": canonical_hash(page),
                        "page_evidence_complete": row["first_page"]["complete"]
                        if index == 0
                        else None,
                        "retrieval_trace_sha256": digest(SOURCE / "rows" / f"{c['id']}-{arm}.json"),
                    }
                )
    from transformers import AutoTokenizer

    specs = load(ROOT / "data/query-language-v1/run-20261028/protocol.json")["models"]
    tokenizers = {
        k: AutoTokenizer.from_pretrained(specs[k]["path"], local_files_only=True)
        for k in ("embedding", "reranker")
    }
    for job in jobs:
        body = "\n\n".join(
            f"[{e['citation_id']}] 来源：{e['locator']}\n" + e["content"]
            for e in job["context"]["evidence"]
        )
        if len(body) > 4000 or any(
            len(t.encode(body, add_special_tokens=False, verbose=False)) > 1200
            for t in tokenizers.values()
        ):
            raise ValueError("Actual AnswerService evidence rendering exceeds page budget")
    client = configured_model()
    files = [
        Path(__file__).resolve(),
        ROOT / "src/infra_rag/assistant.py",
        ROOT / "src/infra_rag/model_clients.py",
        ROOT / "src/infra_rag/offline_evaluation.py",
    ]
    protocol = {
        "inputs": {
            str(p.relative_to(ROOT)): digest(p)
            for p in (SOURCE / "artifacts-manifest.json", REVIEW / "review-manifest.json")
        },
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in files},
        "model": client.configuration(),
        "outputs_planned": len(jobs),
        "scope": "Frozen retrieval replay through unchanged AnswerService; real model generation",
        "comparison": "30 paired first pages; later pages are standalone diagnostics",
        "page_tokens": 1200,
        "page_characters": 4000,
        "format_attempt_cap": 2,
        "transport_retries": 0,
        "parallel_workers": 3,
        "answer_call_cap": 2 * len(jobs),
        "answer_review": "pending; input evidence independently approved with notes",
        "statistics": "Semantic scoring pending independent answer review",
        "default_changed": False,
        "usd_cost": None,
        "pagination": "Independent pages; no synthesis or production continuation",
    }
    save(out / "protocol.json", protocol)
    save(out / "schedule.json", jobs)
    for p in files:
        target = out / "implementation" / p.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and digest(target) != digest(p):
            raise ValueError("Implementation changed")
        if not target.exists():
            shutil.copy2(p, target)
    return jobs


def execute(job, out):
    path = out / "rows" / f"{job['id']}-{job['arm']}-p{job['page']}.json"
    if path.exists():
        if digest(path) != load(path.with_suffix(".sha256.json"))["sha256"]:
            raise ValueError("Checkpoint changed")
        return load(path)
    started = path.with_suffix(".started.json")
    if started.exists():
        raise ValueError("Interrupted model request requires explicit audit, no retry")
    save(started, {"id": job["id"], "arm": job["arm"], "page": job["page"], "status": "started"})
    try:
        result = generate_answer(job["case"], job["context"], Settings(), configured_model())
    except Exception as exc:
        result = {"response": None, "calls": [], "error": type(exc).__name__, "latency_ms": None}
    row = {**job, "result": result, "semantic_correct": None, "citation_support": None}
    save(path, row)
    save(path.with_suffix(".sha256.json"), {"sha256": digest(path)})
    print(job["id"], job["arm"], job["page"], result.get("error") or "completed", flush=True)
    return row


def run(out, freeze=False):
    jobs = prepare(out)
    if freeze:
        return {"phase": "frozen", "planned": len(jobs)}
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(lambda j: execute(j, out), jobs))
    assert len(rows) == len(jobs)
    summary = {
        "outputs": len(rows),
        "model_calls": sum(len(r["result"]["calls"]) for r in rows),
        "answer_accuracy": None,
        "answer_review_coverage": 0,
        "default_changed": False,
        "groups": {},
    }
    for name, selected in [
        ("baseline_first", [r for r in rows if r["arm"] == "zh_baseline"]),
        (
            "bilingual_first",
            [r for r in rows if r["arm"] == "bilingual_context" and r["page"] == 0],
        ),
        ("bilingual_later_pages", [r for r in rows if r["page"] > 0]),
    ]:
        summary["groups"][name] = {
            "outputs": len(selected),
            "execution_errors": sum(bool(r["result"]["error"]) for r in selected),
            "answered_status": sum(
                (r["result"].get("response") or {}).get("status") == "answered" for r in selected
            ),
            "no_evidence_status": sum(
                (r["result"].get("response") or {}).get("status") == "no_evidence" for r in selected
            ),
        }
    save(out / "summary.json", summary)
    save(
        out / "answer-review-template.json",
        [
            {
                "id": r["id"],
                "arm": r["arm"],
                "page": r["page"],
                "case_sha256": canonical_hash(r["case"]),
                "trace_sha256": digest(out / "rows" / f"{r['id']}-{r['arm']}-p{r['page']}.json"),
                "status": "pending",
                "reviewer": None,
                "reason": None,
                "checks": dict.fromkeys(
                    [
                        "all_required_points",
                        "conditions_preserved",
                        "claims_supported",
                        "citations_supported",
                        "claim_inventory_complete",
                    ]
                ),
            }
            for r in rows
        ],
    )
    save(
        out / "artifacts-manifest.json",
        {
            p.relative_to(out).as_posix(): digest(p)
            for p in out.rglob("*")
            if p.is_file() and p.name != "artifacts-manifest.json"
        },
    )
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--freeze-only", action="store_true")
    args = parser.parse_args()
    try:
        result = run(args.output.resolve(), args.freeze_only)
        record_operation(
            "审核后真实回答组件实验",
            "确认AnswerService实际消费的证据与答案",
            str(result),
            "回答语义仍待审核；后续页独立诊断，不冒充跨页最终回答",
        )
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        record_operation(
            "真实回答实验中止", "保留输出与请求标记，不隐式重试", str(args.output), str(exc)
        )
        raise
