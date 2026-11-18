"""Real-model regression of exact citation aliases and verified continuation consumption."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from benchmark_reviewed_answers import page_context
from operation_log import ROOT, record_operation
from prepare_corpus_pilot import load, save

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.config import Settings
from infra_rag.model_clients import configured_model
from infra_rag.offline_evaluation import RecordingModel, generate_answer
from infra_rag.paged_answers import extraction_messages, final_context, verify_quotes

SOURCE = ROOT / "data/bilingual-protected-v1/run-20261028"


def run(out, freeze):
    for name, sha in load(SOURCE / "artifacts-manifest.json").items():
        if digest(SOURCE / name) != sha:
            raise ValueError("Frozen source changed")
    cases = load(SOURCE / "questions.json")
    files = [
        Path(__file__).resolve(),
        ROOT / "src/infra_rag/assistant.py",
        ROOT / "src/infra_rag/paged_answers.py",
        ROOT / "src/infra_rag/offline_evaluation.py",
        ROOT / "src/infra_rag/model_clients.py",
    ]
    protocol = {
        "inputs": {
            str((SOURCE / "artifacts-manifest.json").relative_to(ROOT)): digest(
                SOURCE / "artifacts-manifest.json"
            )
        },
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in files},
        "model": configured_model().configuration(),
        "source_questions": 30,
        "arms": "30 alias first-page regressions; 025/029 quote-first and quote-all controls",
        "scope": "Frozen retrieval replay, real AnswerService; retrieval parameters unchanged",
        "body_tokens": 1200,
        "body_characters": 4000,
        "extraction_attempts_per_page": 1,
        "format_attempts_per_answer": 2,
        "transport_retries": 0,
        "call_cap": 75,
        "max_workers": 3,
        "answer_review": "pending",
        "default_pagination_enabled": False,
        "statistics": "Targeted development diagnostic; no generalized accuracy claim",
        "selection": "025/029 preselected from audit; no gold in runtime prompts",
    }
    save(out / "protocol.json", protocol)
    for p in files:
        target = out / "implementation" / p.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and digest(target) != digest(p):
            raise ValueError("Snapshot changed")
        if not target.exists():
            target.write_bytes(p.read_bytes())
    schedule = [{"id": c["id"], "arm": "alias_first"} for c in cases] + [
        {"id": cid, "arm": a}
        for cid in ("diag-025", "diag-029")
        for a in ("quote_first", "quote_all")
    ]
    save(out / "schedule.json", schedule)
    if freeze:
        return {"phase": "freeze", "outputs": 34}
    from transformers import AutoTokenizer

    models = load(ROOT / "data/query-language-v1/run-20261028/protocol.json")["models"]
    counters = {}
    for name in ("embedding", "reranker"):
        t = AutoTokenizer.from_pretrained(models[name]["path"], local_files_only=True)
        counters[name] = lambda s, t=t: len(t.encode(s, add_special_tokens=False, verbose=False))

    def answer(case, context, arm):
        path = out / "rows" / f"{case['id']}-{arm}.json"
        if path.exists():
            raise ValueError("Use fresh path; no implicit retries")
        save(path.with_suffix(".started.json"), {"status": "started"})
        result = generate_answer(case, context, Settings(), configured_model())
        row = {
            "id": case["id"],
            "arm": arm,
            "case_sha256": canonical_hash(case),
            "actual_context": context,
            "result": result,
            "semantic_correct": None,
        }
        save(path, row)
        save(path.with_suffix(".sha256.json"), {"sha256": digest(path)})
        print(case["id"], arm, result["error"] or "completed", flush=True)
        return row

    def first(case):
        r = load(SOURCE / "rows" / f"{case['id']}-bilingual_context.json")
        return answer(case, page_context(r["pages"][0]), "alias_first")

    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(first, cases))
    for case in [c for c in cases if c["id"] in ("diag-025", "diag-029")]:
        source = load(SOURCE / "rows" / f"{case['id']}-bilingual_context.json")
        quotes = []
        first_quotes = []
        error = None
        for index, page in enumerate(source["pages"]):
            evidence = page_context(page)["evidence"]
            model = RecordingModel(configured_model())
            target = out / "extractions" / f"{case['id']}-p{index}.json"
            save(target.with_suffix(".started.json"), {"status": "started"})
            try:
                raw = model.generate(extraction_messages(case["query"], evidence))
                selected = verify_quotes(raw, evidence)
                quotes.extend(selected)
                if index == 0:
                    first_quotes = selected
                event = {"page": index, "verified_quotes": selected, "error": None}
            except Exception as exc:
                event = {"page": index, "verified_quotes": [], "error": str(exc)}
                error = str(exc)
            save(
                target, {**event, "calls": model.calls, "source_page_sha256": canonical_hash(page)}
            )
        for arm, selection in [("quote_first", first_quotes), ("quote_all", quotes)]:
            try:
                if error:
                    raise ValueError("Extraction incomplete: " + error)
                context = final_context(selection, counters)
                rows.append(answer(case, context, arm))
            except ValueError as exc:
                row = {"id": case["id"], "arm": arm, "status": "blocked", "error": str(exc)}
                save(out / "rows" / f"{case['id']}-{arm}.json", row)
                rows.append(row)
    assert len(rows) == 34
    summary = {
        "outputs": 34,
        "model_errors": sum(bool(r.get("result", {}).get("error")) for r in rows),
        "blocked": sum(r.get("status") == "blocked" for r in rows),
        "answer_accuracy": None,
        "alias_first_answered": sum(
            (r.get("result", {}).get("response") or {}).get("status") == "answered"
            for r in rows
            if r["arm"] == "alias_first"
        ),
    }
    save(out / "summary.json", summary)
    save(
        out / "answer-review-template.json",
        [
            {
                "id": r["id"],
                "arm": r["arm"],
                "status": "pending",
                "trace_sha256": digest(out / "rows" / f"{r['id']}-{r['arm']}.json"),
                "reviewer": None,
                "all_required_points": None,
                "claims_and_citations_supported": None,
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
    return summary


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--freeze-only", action="store_true")
    a = p.parse_args()
    try:
        result = run(a.output.resolve(), a.freeze_only)
        record_operation(
            "引用ID修复与跨页原文提取验证",
            "冻结检索不变，核对真正送入最终回答的证据",
            str(result),
            "开发诊断；答案语义审核pending，不自动采用跨页逻辑",
        )
        print(result)
    except Exception as exc:
        record_operation("引用/跨页验证中止", "保留失败产物", str(a.output), str(exc))
        raise
