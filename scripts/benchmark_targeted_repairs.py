"""Separate frozen stability and mechanism diagnostics; no default adoption."""

import argparse
import copy
import importlib.util
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from benchmark_native_pagination import ObservedRetrieval, local_models, settings
from fastapi.testclient import TestClient
from operation_log import ROOT, record_operation
from prepare_corpus_pilot import load, save

from infra_rag.api import create_app
from infra_rag.assistant import AnswerService, ConversationStore
from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.chunking import stable_id
from infra_rag.config import Settings
from infra_rag.model_clients import configured_model
from infra_rag.offline_evaluation import FrozenRetrieval, RecordingModel
from infra_rag.service import RetrievalService

SOURCE = ROOT / "data/native-pagination-v1/run-20261029"
IDS = (
    "diag-005",
    "diag-008",
    "diag-011",
    "diag-015",
    "diag-021",
    "diag-030",
    "diag-013",
    "diag-025",
)
OLD = SOURCE / "implementation/src/infra_rag/experimental_pages.py"
ALIGN = """
回答前核对题目要求的触发条件、处理对象、处理动作和恢复后的行为。
证据仅支持相关但不同的机制时，不得用该机制替代所问行为；缺少必要支持则supported=false并说明缺口。
不得凭常识补齐，也不要将相同产品或术语视作支持同一机制。
"""


def old_consumer():
    spec = importlib.util.spec_from_file_location("infra_rag._frozen_page_consumer", OLD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.consume_pages


class OldAnswer(AnswerService):
    def _consume_pages(self, *args):
        return old_consumer()(*args)


class AlignedAnswer(AnswerService):
    def _generate_checked(self, messages, allowed, model=None):
        messages = copy.deepcopy(messages)
        messages[0]["content"] += ALIGN
        return super()._generate_checked(messages, allowed, model=model)


def experiment_schedule(cases, experiment, case_set="focused"):
    if case_set not in {"focused", "full"}:
        raise ValueError("Unknown case set")
    if experiment == "A":
        ids = sorted(cases) if case_set == "full" else IDS
        return [
            {"id": cid, "arm": arm}
            for i, cid in enumerate(ids)
            for arm in (("off", "old", "new") if i % 2 == 0 else ("new", "old", "off"))
        ]
    if case_set == "full":
        raise ValueError("Full case set applies only to stability experiment A")
    return [
        {"id": "diag-024", "arm": f"{evidence}_{prompt}"}
        for evidence in ("actual", "oracle")
        for prompt in ("base", "aligned")
    ]


def freeze(out, experiment, case_set="focused"):
    source_protocol = load(SOURCE / "protocol.json")
    if digest(SOURCE / "index/index.json") != load(SOURCE / "index-manifest.json")["index_sha256"]:
        raise ValueError("Native index changed")
    for row in source_protocol["sources"]:
        if digest(ROOT / row["input_path"]) != row["input_sha256"]:
            raise ValueError("Source changed")
    files = [
        Path(__file__).resolve(),
        ROOT / "scripts/benchmark_native_pagination.py",
        *[
            ROOT / f"src/infra_rag/{n}.py"
            for n in (
                "assistant",
                "experimental_pages",
                "paged_answers",
                "api",
                "service",
                "model_clients",
                "offline_evaluation",
            )
        ],
    ]
    protocol = {
        "experiment": experiment,
        "inputs": {
            str(p.relative_to(ROOT)): digest(p)
            for p in (
                SOURCE / "index/index.json",
                SOURCE / "questions.json",
                SOURCE / "protocol.json",
                OLD,
            )
        },
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in files},
        "model": configured_model().configuration(),
        "models": source_protocol["models"],
        "call_cap": (900 if case_set == "full" else 240) if experiment == "A" else 8,
        "case_set": case_set,
        "transport_retries": 0,
        "answer_review": "pending; AI and independent human separated",
        "default_enabled": False,
        "selection_order": "direct/background; source/page order tie-break",
        "body_budget": "1200token/4000chars; no split units; explicit failure if nothing fits",
        "alignment_prompt": ALIGN if experiment == "B" else None,
    }
    cases = {c["id"]: c for c in load(SOURCE / "questions.json")}
    plan = experiment_schedule(cases, experiment, case_set)
    save(out / "protocol.json", protocol)
    save(out / "schedule.json", plan)
    for p in files:
        dest = out / "implementation" / p.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and digest(dest) != digest(p):
            raise ValueError("Implementation snapshot changed")
        if not dest.exists():
            dest.write_bytes(p.read_bytes())
    if not (out / "index").exists():
        shutil.copytree(SOURCE / "index", out / "index")
    return protocol, plan, cases


def run(out, experiment, freeze_only, case_set="focused"):
    protocol, plan, cases = freeze(out, experiment, case_set)
    if freeze_only:
        return {"phase": "frozen", "experiment": experiment, "requests": len(plan)}
    service = RetrievalService(settings(out, protocol["models"]))
    local_models(service, protocol["models"])
    service.text_collection, service.clip_collection = service._collections(
        service.chunks, service.vectors
    )
    if experiment == "B":
        import numpy as np

        query = cases["diag-024"]["query"]
        diagnostics = {}
        context = {}
        service.search(
            query, top_k=5, strategy="hybrid", diagnostics=diagnostics, context_pack=context
        )
        vector = np.asarray(service._encoder().encode([query], query=True)[0])
        dense = sorted(
            zip(
                [c.id for c in service.chunks],
                map(float, np.asarray(service.vectors) @ vector),
                strict=True,
            ),
            key=lambda x: (-x[1], x[0]),
        )
        sparse = service.lexical_cache[(None, None, "raw")].search(query)
        target = cases["diag-024"]["group_id"] + ".md"
        target_ids = {c.id for c in service.chunks if Path(c.source).name == target}
        save(
            out / "retrieval-diagnostic.json",
            {
                "query": query,
                "actual_diagnostics": diagnostics,
                "exact_dense_full_ranking": dense,
                "bm25_full_ranking": sparse,
                "target_ids": sorted(target_ids),
                "target_in_candidates": sorted(target_ids & set(diagnostics["candidates"])),
                "note": "full-ranking analysis only; never supplies extra candidates to actual arm",
            },
        )
        quote = cases["diag-024"]["evidence_alternatives"][0]["requirements"][0]
        source = SOURCE / "corpus" / target
        if quote["quote"] not in source.read_text():
            raise ValueError("Oracle quote not exact source")
        oracle = {
            "evidence": [
                {
                    "citation_id": "E" + stable_id(quote["document_id"], quote["quote"]),
                    "content": quote["quote"],
                    "source": str(source),
                    "locator": quote["source_url"],
                    "input_sha256": quote["input_sha256"],
                }
            ]
        }
        save(
            out / "contexts.json",
            {
                "actual": context,
                "oracle": oracle,
                "oracle_note": "gold evidence diagnostic, not retrieval",
            },
        )
    rows = []
    for job in plan:
        target = out / "rows" / f"{job['id']}-{job['arm']}.json"
        if target.exists() or target.with_suffix(".started.json").exists():
            raise ValueError("Use fresh run; no implicit retry")
        save(target.with_suffix(".started.json"), job)
        recorder = RecordingModel(configured_model())
        observed = None
        if experiment == "A":
            observed = ObservedRetrieval(service)
            retrieval = observed
            cls = OldAnswer if job["arm"] == "old" else AnswerService
        else:
            retrieval = FrozenRetrieval(
                Settings(), context if job["arm"].startswith("actual") else oracle
            )
            cls = AlignedAnswer if job["arm"].endswith("aligned") else AnswerService
        started = perf_counter()
        with TemporaryDirectory() as tmp:
            assistant = cls(retrieval, recorder, ConversationStore(Path(tmp) / "history.sqlite"))
            response = TestClient(create_app(retrieval, assistant)).post(
                "/chat",
                json={
                    "message": cases[job["id"]]["query"],
                    "experimental_pagination": experiment == "A" and job["arm"] != "off",
                },
            )
        row = {
            **job,
            "http_status": response.status_code,
            "response": response.json(),
            "calls": recorder.calls,
            "retrieval": observed.events if observed else [],
            "elapsed_ms": (perf_counter() - started) * 1000,
            "case_sha256": canonical_hash(cases[job["id"]]),
            "strict_correct": None,
            "oracle": experiment == "B" and job["arm"].startswith("oracle"),
        }
        save(target, row)
        save(target.with_suffix(".sha256.json"), {"sha256": digest(target)})
        rows.append(row)
        if response.status_code != 200:
            raise ValueError("HTTP failure; stopped with trace")
        if observed:
            assert len(observed.events) == 1
            allowed = {
                e["citation_id"]
                for t in row["response"]["trace"]
                if t["step"] == "pack_verified_quotes"
                for e in t["evidence"]
            }
            if job["arm"] == "off":
                allowed = {e["citation_id"] for e in observed.events[0]["context"]["evidence"]}
            assert all(e["citation_id"] in allowed for e in row["response"]["citations"])
            for t in row["response"]["trace"]:
                if t["step"] == "pack_verified_quotes":
                    assert t["characters"] <= 4000 and all(
                        n <= 1200 for n in t["token_counts"].values()
                    )
            paired = [r for r in rows if r["id"] == job["id"]]
            assert all(
                r["retrieval"][0]["diagnostics"]["ranked_ids"]
                == observed.events[0]["diagnostics"]["ranked_ids"]
                for r in paired
            )
        print(experiment, job["id"], job["arm"], row["response"].get("status"), flush=True)
    calls = sum(len(r["calls"]) for r in rows)
    assert calls <= protocol["call_cap"]
    summary = {
        "experiment": experiment,
        "requests": len(rows),
        "model_calls": calls,
        "strict_accuracy": None,
        "states": [
            {
                "id": r["id"],
                "arm": r["arm"],
                "status": r["response"]["status"],
                "calls": len(r["calls"]),
            }
            for r in rows
        ],
    }
    save(out / "summary.json", summary)
    save(
        out / "review-template.json",
        [
            {
                "id": r["id"],
                "arm": r["arm"],
                "status": "pending",
                "reviewer": None,
                "case_sha256": r["case_sha256"],
                "trace_sha256": digest(out / "rows" / f"{r['id']}-{r['arm']}.json"),
                "strict_correct": None,
                "conditions_preserved": None,
                "citations_support_requested_mechanism": None,
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
    p.add_argument("--experiment", choices=("A", "B"), required=True)
    p.add_argument("--freeze-only", action="store_true")
    p.add_argument("--case-set", choices=("focused", "full"), default="focused")
    a = p.parse_args()
    try:
        result = run(a.output.resolve(), a.experiment, a.freeze_only, a.case_set)
        record_operation(
            "定向修复实验" + a.experiment,
            "分开检验稳定性和机制相关性",
            str(result),
            "独立语义审核pending；默认关闭",
        )
        print(result)
    except Exception as exc:
        record_operation("定向实验中止", "保留失败和预算", str(a.output), str(exc))
        raise
