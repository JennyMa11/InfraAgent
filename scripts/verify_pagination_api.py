"""Frozen-page replay through /chat with real models and the experimental switch."""

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from fastapi.testclient import TestClient
from operation_log import ROOT, record_operation
from prepare_corpus_pilot import load, save

from infra_rag.api import create_app
from infra_rag.assistant import AnswerService, ConversationStore
from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.config import Settings
from infra_rag.model_clients import configured_model
from infra_rag.offline_evaluation import RecordingModel

SOURCE = ROOT / "data/bilingual-protected-v1/run-20261028"
REVIEW = ROOT / "data/citation-pages-v1/run-20261029-v3-reviewed/review-manifest.json"


class ReplayRetrieval:
    def __init__(self, pages, count):
        self.pages = pages
        self.context_counter = count
        self.settings = Settings()
        self.search_calls = 0

    def search(self, query, *, context_pack, **kwargs):
        self.search_calls += 1
        context_pack.update(self.pages[0])
        return []

    def evidence_pages(self, hits, domain=None):
        return self.pages


def run(out, freeze_only):
    for name, sha in load(SOURCE / "artifacts-manifest.json").items():
        if digest(SOURCE / name) != sha:
            raise ValueError("Frozen retrieval changed")
    review = load(REVIEW)
    for entry in [review["template"], *review["inputs"].values(), *review["outputs"].values()]:
        if digest(ROOT / entry["path"]) != entry["sha256"]:
            raise ValueError("Review input changed")
    files = [
        Path(__file__).resolve(),
        *[
            ROOT / f"src/infra_rag/{name}.py"
            for name in (
                "api",
                "assistant",
                "experimental_pages",
                "paged_answers",
                "service",
                "offline_evaluation",
            )
        ],
    ]
    protocol = {
        "inputs": {
            str(p.relative_to(ROOT)): digest(p)
            for p in (SOURCE / "artifacts-manifest.json", REVIEW)
        },
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in files},
        "model": configured_model().configuration(),
        "case_ids": ["diag-013", "diag-025", "diag-029"],
        "variants": [False, True],
        "max_calls": 33,
        "retries": "no transport retries, max2 answer formatting attempts",
        "scope": "API route and AnswerService with frozen-page replay, not live retrieval",
        "limits": "12 pages,180sec per enabled request,1200token/4000chars per page and final",
        "answer_review": "pending; prior review AI only",
        "default_changed": False,
    }
    save(out / "protocol.json", protocol)
    for p in files:
        target = out / "implementation" / p.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and digest(target) != digest(p):
            raise ValueError("Implementation changed")
        if not target.exists():
            target.write_bytes(p.read_bytes())
    if freeze_only:
        return {"phase": "frozen", "requests": 6}
    from transformers import AutoTokenizer

    specs = load(ROOT / "data/query-language-v1/run-20261028/protocol.json")["models"]
    tokenizers = [
        AutoTokenizer.from_pretrained(specs[k]["path"], local_files_only=True)
        for k in ("embedding", "reranker")
    ]

    def count(text):
        return max(len(t.encode(text, add_special_tokens=False, verbose=False)) for t in tokenizers)

    cases = {c["id"]: c for c in load(SOURCE / "questions.json")}
    rows = []
    for cid in protocol["case_ids"]:
        original = load(SOURCE / "rows" / f"{cid}-bilingual_context.json")
        pages = [
            {
                "evidence": [
                    {**e, "locator": e["source_url"], "source": e["source_url"]}
                    for e in page["evidence"]
                ]
            }
            for page in original["pages"]
        ]
        for enabled in (False, True):
            target = out / "rows" / f"{cid}-{enabled}.json"
            if target.exists() or target.with_suffix(".started.json").exists():
                raise ValueError("Use a fresh output; no implicit model retries")
            save(target.with_suffix(".started.json"), {"status": "started"})
            model = RecordingModel(configured_model())
            retrieval = ReplayRetrieval(pages, count)
            started = perf_counter()
            with TemporaryDirectory() as tmp:
                service = AnswerService(
                    retrieval, model, ConversationStore(Path(tmp) / "conversation.sqlite")
                )
                api = TestClient(create_app(retrieval, service))
                payload = {"message": cases[cid]["query"], "experimental_pagination": enabled}
                response = api.post("/chat", json=payload)
            row = {
                "id": cid,
                "enabled": enabled,
                "request": payload,
                "http_status": response.status_code,
                "response": response.json(),
                "calls": model.calls,
                "search_calls": retrieval.search_calls,
                "elapsed_ms": (perf_counter() - started) * 1000,
                "case_sha256": canonical_hash(cases[cid]),
                "source_trace_sha256": digest(SOURCE / "rows" / f"{cid}-bilingual_context.json"),
                "semantic_correct": None,
            }
            save(target, row)
            save(target.with_suffix(".sha256.json"), {"sha256": digest(target)})
            rows.append(row)
            print(cid, enabled, response.status_code, row["response"].get("status"), flush=True)
    result = {
        "requests": 6,
        "model_calls": sum(len(r["calls"]) for r in rows),
        "answer_accuracy": None,
        "statuses": [
            {
                "id": r["id"],
                "enabled": r["enabled"],
                "status": r["response"].get("status"),
                "calls": len(r["calls"]),
            }
            for r in rows
        ],
    }
    save(out / "summary.json", result)
    save(
        out / "human-review-template.json",
        [
            {
                "id": r["id"],
                "enabled": r["enabled"],
                "status": "pending",
                "case_sha256": r["case_sha256"],
                "trace_sha256": digest(out / "rows" / f"{r['id']}-{r['enabled']}.json"),
                "reviewer": None,
                "all_required_claims": None,
                "citations_supported": None,
                "reason": None,
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
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--freeze-only", action="store_true")
    args = p.parse_args()
    try:
        result = run(args.output.resolve(), args.freeze_only)
        record_operation(
            "跨页实验API开关真实模型验证",
            "固定检索回放，对照关闭与开启",
            str(result),
            "审核为AI；新回答待审；不作为新鲜检索或总体正确率",
        )
        print(result)
    except Exception as exc:
        record_operation("跨页API验证中止", "保留失败和请求标记", str(args.output), str(exc))
        raise
