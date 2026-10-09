"""Paired dev comparison of existing QA and multi-round Agent; immutable old inputs."""

import argparse
import copy
import json
import shutil
from collections import Counter
from functools import lru_cache
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace

from operation_log import record_operation
from prepare_corpus_v2 import ROOT, configuration

from infra_rag.agent import AGENT_PROMPT, RequestBudget, ResearchAgent, deadline, usage_tokens
from infra_rag.agent_comparison import CoverageResearchAgent, V6ComparisonRetrieval
from infra_rag.assistant import SYSTEM_PROMPT, AnswerService, ConversationStore
from infra_rag.benchmarking import canonical_hash, digest, span_coverage, write_new
from infra_rag.evaluation import evidence_metrics
from infra_rag.model_clients import configured_model
from infra_rag.paired_statistics import paired_statistics
from infra_rag.service import RetrievalService

V6 = ROOT / "evals/merged-corpus-v2/budget-ablation-v6/run-20261003"
V4 = ROOT / "evals/merged-corpus-v2/recall-delivery-v4/run-20261002"
PLAN = ROOT / "evals/rag-agent-comparison-v1/experiment-plan.md"
ARMS = ("legacy-v6", "agent-v6-fifo", "agent-v6-coverage")


def select_pilot(rows):
    selected = []
    for dataset in ("official", "repository"):
        groups = set()
        eligible = [r for r in rows if r["dataset"] == dataset and r["answerable"]]
        eligible.sort(key=lambda r: (canonical_hash(dataset + ":" + r["id"]), r["id"]))
        for row in eligible:
            if row["group_id"] in groups:
                continue
            selected.append(row)
            groups.add(row["group_id"])
            if len(groups) == 3:
                break
        if len(groups) != 3:
            raise ValueError("three independent groups required per dataset")
    return selected


def question(row):
    alternatives = row["resolved_gold"]["evidence_alternatives"] if row["answerable"] else []
    return {**row, "evidence_alternatives": alternatives}


def agent_items(context, hashes):
    return [
        {
            "id": e["citation_id"],
            "chunk_id": e["chunk_id"],
            "parent_id": e["parent_id"],
            "source": e["source"],
            "sha256": hashes[e["source"]],
            "locator": e["locator"],
            "content": e["content"],
            "truncated": e.get("truncated", False),
            "metadata": e.get("metadata", {}),
        }
        for e in context["evidence"]
    ]


def measure(row, evidence, positions):
    # Positions are only used by the unchanged scorer to resolve adjacent source spans.
    actual = [{**e, "source_position": positions[e["chunk_id"]]} for e in evidence]
    return span_coverage(actual, question(row))


def metric(rows, field):
    values = [r[field]["complete"] for r in rows if r["answerable"]]
    return {
        "numerator": int(sum(values)),
        "denominator": len(values),
        "value": sum(values) / len(values) if values else None,
    }


class RecordingClient:
    """Capture exact prompts and provider usage, reserving legacy requests as well."""

    def __init__(self, client, budget=None):
        self.client, self.budget = client, budget
        self.model, self.provider = client.model, client.provider
        self.timeout, self.last_call, self.calls = client.timeout, None, []
        self._token = getattr(client, "_token", None)

    def generate(self, messages):
        if self.budget is not None:
            self.budget.reserve()
        self.client.timeout = min(self.timeout, 45)
        self.client.last_call = None
        call = {"messages": copy.deepcopy(messages)}
        self.calls.append(call)
        started = perf_counter()
        try:
            raw = self.client.generate(messages)
            call["raw"] = raw
            return raw
        except Exception as exc:
            call["error"] = type(exc).__name__
            raise
        finally:
            self.last_call = self.client.last_call
            call["metadata"] = self.last_call
            call["latency_ms"] = (perf_counter() - started) * 1000


def usage(calls, field):
    values = [usage_tokens((c.get("metadata") or {}).get("usage") or {}, field) for c in calls]
    return sum(values) if values and all(v is not None for v in values) else None


def execute(run, live=False):
    if run.exists():
        raise ValueError("Use a new output directory; frozen results cannot be overwritten")
    prior = json.loads((V6 / "protocol.json").read_text())
    inputs = {}
    for folder, names in ((V6, ("protocol.json", "rows.jsonl")), (V4, ("source-audit.json",))):
        manifest = json.loads((folder / "artifacts-manifest.json").read_text())["files"]
        for name in names:
            if digest(folder / name) != manifest[name]:
                raise ValueError("historical artifact changed")
            inputs[str((folder / name).relative_to(ROOT))] = manifest[name]
    directory = ROOT / prior["directory"]
    original_index = directory / "index/index.json"
    inputs[str(original_index.relative_to(ROOT))] = digest(original_index)
    chunks_file = directory / "chunks.json"
    if digest(chunks_file) != prior["chunks_sha256"]:
        raise ValueError("chunks changed")
    inputs[str(chunks_file.relative_to(ROOT))] = digest(chunks_file)
    raw_chunks = json.loads(chunks_file.read_text())
    positions = {c["id"]: i for i, c in enumerate(raw_chunks)}
    rows = [json.loads(line) for line in (V6 / "rows.jsonl").read_text().splitlines()]
    rows = [r for r in rows if r["arm"] == "B-k8-l0-p1-n0"]
    if len(rows) != 110 or len({r["id"] for r in rows}) != 110:
        raise ValueError("expected all 110 original dev cases")
    bundles = {}
    manifest = json.loads((V4 / "artifacts-manifest.json").read_text())["files"]
    for row in rows:
        path = V4 / "bundles" / row["dataset"] / (row["id"] + ".json")
        if digest(path) != manifest[str(path.relative_to(V4))]:
            raise ValueError("candidate bundle changed")
        inputs[str(path.relative_to(ROOT))] = digest(path)
        bundles[row["query"]] = json.loads(path.read_text())["B5"]
    audit = json.loads((V4 / "source-audit.json").read_text())
    hashes = {r["source"]: r["expected"] for r in audit["source_files"]}
    for source, expected in hashes.items():
        if digest(source) != expected:
            raise ValueError("frozen source changed")
    for model in prior["models"].values():
        if not isinstance(model, dict) or "path" not in model:
            continue
        for name, expected in model["files"].items():
            if digest(Path(model["path"]) / name) != expected:
                raise ValueError("frozen model changed")
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        prior["models"]["embedding"]["path"],
        local_files_only=True,
        **prior["tokenizer_options"],
    )

    @lru_cache(maxsize=32768)
    def count(text):
        return len(tokenizer.encode(text, add_special_tokens=False))

    pilot = select_pilot(rows)
    client = configured_model() if live else None
    if client:
        client.max_tokens = 650
    run.mkdir(parents=True)
    source_files = list((ROOT / "src/infra_rag").glob("*.py")) + [Path(__file__), PLAN]
    source_files += list((ROOT / "tests").glob("test_agent_comparison*.py"))
    for path in source_files:
        target = run / "implementation" / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    write_new(run / "cases.json", [question(r) for r in rows])
    schedule = [
        {"case_id": r["id"], "arm": ARMS[(j + i) % 3]}
        for i, r in enumerate(pilot)
        for j in range(3)
    ]
    freeze = {
        "kind": "paired_original_dev_executor_comparison",
        "scope": "component replay 110 dev; live pilot 6 positive dev, not confirmation",
        "inputs": inputs,
        "models": prior["models"],
        "source_hashes": hashes,
        "tokenizer_options": prior["tokenizer_options"],
        "plan_sha256": digest(PLAN),
        "cases_sha256": digest(run / "cases.json"),
        "pilot_ids": [r["id"] for r in pilot],
        "schedule": schedule,
        "max_model_requests": 48,
        "context_tokens": 1200,
        "context_chars": 4000,
        "answer_model": client.configuration() if live else None,
        "prompt_hashes": {
            "legacy": canonical_hash(SYSTEM_PROMPT),
            "research": canonical_hash(AGENT_PROMPT),
        },
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in source_files},
        "live_requested": live,
        "default_changed": False,
        "holdout_read": False,
    }
    write_new(run / "freeze.json", freeze)
    record_operation(
        "冻结原有RAG与新Agent配对实验",
        "在执行前锁定题集、选择规则及预算",
        f"原开发110题；实模pilot {freeze['pilot_ids']}；上限48请求；{run}",
    )
    from infra_rag.models import Chunk

    chunks = {c["id"]: Chunk(**c) for c in raw_chunks}
    index_directory = ROOT / "data/rag-agent-comparison-v1" / run.name
    if index_directory.exists():
        raise ValueError("Use a new run name and isolated index directory")
    settings = configuration(index_directory)
    dummy = SimpleNamespace(
        settings=settings,
        _encoder=lambda: SimpleNamespace(token_length=count),
    )
    fifo = ResearchAgent(dummy, SimpleNamespace())
    replay_base = SimpleNamespace(chunks=list(chunks.values()), settings=settings)
    adapter = V6ComparisonRetrieval(replay_base, bundles, count)
    components = []
    for row in rows:
        context = {}
        adapter.search(row["query"], domain="infra", context_pack=context)
        for item in context["evidence"]:
            item["source_position"] = positions[item["chunk_id"]]
        # Compare before enabling prompt metadata; preserve the original archive exactly.
        if context != row["context"]:
            raise ValueError(f"v6 exact replay failed: {row['id']}")
        packed = fifo._pack({e["id"]: e for e in agent_items(context, hashes)})
        components.append(
            {
                "id": row["id"],
                "group_id": row["group_id"],
                "dataset": row["dataset"],
                "answerable": row["answerable"],
                "original": row["delivered"],
                "agent_repack": measure(row, packed, positions),
                "exact_v6_replay": True,
                "original_evidence": context["evidence"],
                "agent_evidence": packed,
            }
        )
    write_new(run / "component-replay.json", components)
    summary = {}
    for ds in ("official", "repository"):
        subset = [r for r in components if r["dataset"] == ds]
        before = [{**r, "delivered": r["original"]} for r in subset]
        after = [{**r, "delivered": r["agent_repack"]} for r in subset]
        summary[ds] = {
            "original": metric(subset, "original"),
            "agent_repack": metric(subset, "agent_repack"),
            "paired": paired_statistics(before, after),
        }
    write_new(run / "component-summary.json", summary)
    record_operation(
        "回放全部110题的新增证据交付环节",
        "隔离执行器之外的二次打包损失",
        json.dumps(summary, ensure_ascii=False),
        "仅机械回放，不是多轮Agent实模成绩",
    )
    live_rows = []
    budget = RequestBudget(48)
    if live:
        # Copy the snapshot to a new ignored index; original indexes are never opened for writes.
        settings.data_dir.mkdir(parents=True)
        shutil.copyfile(original_index, settings.data_dir / "index.json")
        base = RetrievalService(settings)
        from sentence_transformers import CrossEncoder

        from infra_rag.encoding import BGEEncoder

        base.encoder = BGEEncoder(prior["models"]["embedding"]["path"])
        base.reranker = CrossEncoder(prior["models"]["reranker"]["path"])
        retrieval = V6ComparisonRetrieval(base, bundles, count, include_metadata=True)
        by_id = {r["id"]: r for r in pilot}
        for scheduled in schedule:
            row, arm = by_id[scheduled["case_id"]], scheduled["arm"]
            folder = run / "live" / row["id"] / arm
            before = len(retrieval.search_records)
            model = RecordingClient(client, budget if arm == "legacy-v6" else None)
            started = perf_counter()
            error, trace, response = None, None, None
            try:
                if arm == "legacy-v6":
                    folder.mkdir(parents=True)
                    assistant = AnswerService(
                        retrieval,
                        model=model,
                        store=ConversationStore(folder / "conversations.sqlite3"),
                    )
                    with deadline(180):
                        response = assistant.answer(row["query"], domain="infra")
                    evidence = retrieval.search_records[-1]["context"]["evidence"]
                else:
                    cls = CoverageResearchAgent if arm.endswith("coverage") else ResearchAgent
                    options = (
                        {
                            "scoring_query": row["query"]
                            + "\n"
                            + bundles[row["query"]]["scoring_query"]
                        }
                        if cls is not ResearchAgent
                        else {}
                    )
                    trace = cls(retrieval, model, budget=budget, domain="infra", **options).run(
                        row["query"],
                        folder,
                        case_id=row["id"],
                        run_id=run.name,
                        config_id=arm,
                    )
                    response = trace["final"]
                    evidence = trace["evidence"]["delivered"]
            except Exception as exc:
                error = type(exc).__name__
                evidence = trace["evidence"]["delivered"] if trace else []
            searches = retrieval.search_records[before:]
            candidates = list(
                dict.fromkeys(cid for s in searches for cid in s["diagnostics"]["candidates"])
            )
            candidate_complete = evidence_metrics(
                candidates, row["resolved_gold"], max(1, len(candidates))
            )["complete_evidence_hit"]
            result = {
                "id": row["id"],
                "group_id": row["group_id"],
                "dataset": row["dataset"],
                "arm": arm,
                "query": row["query"],
                "answerable": row["answerable"],
                "delivered": measure(row, evidence, positions),
                "evidence": evidence,
                "cumulative_candidate_complete": candidate_complete,
                "searches": searches,
                "response": response,
                "error": error,
                "model_calls": len(model.calls),
                "input_tokens": usage(model.calls, "input_tokens"),
                "output_tokens": usage(model.calls, "output_tokens"),
                "latency_ms": (perf_counter() - started) * 1000,
                "source_hashes_verified": True,
                "semantic_review": "pending",
                "events": trace["events"] if trace else [],
            }
            # A provider must never echo credentials into the exported recording.
            recorded = json.dumps(model.calls, ensure_ascii=False)
            if model._token:
                recorded = recorded.replace(model._token, "[redacted]")
            write_new(folder / "model-calls.json", json.loads(recorded))
            write_new(folder / "comparison.json", result)
            live_rows.append(result)
            record_operation(
                f"执行配对pilot {row['id']} {arm}",
                "同题同语料比较执行器与累计交付",
                f"交付{result['delivered']}；模型{len(model.calls)}次；累计{budget.used}/48",
                error or ",".join(result["events"]) or "无",
            )
            print(
                json.dumps(
                    {
                        "id": row["id"],
                        "arm": arm,
                        "delivery": result["delivered"],
                        "status": (response or {}).get("status"),
                        "used": budget.used,
                    }
                ),
                flush=True,
            )
    write_new(run / "live-results.json", live_rows)
    write_new(
        run / "reviews.json",
        [
            {
                "case_id": r["id"],
                "arm": r["arm"],
                "status": "pending",
                "case_sha256": canonical_hash(
                    question(next(q for q in pilot if q["id"] == r["id"]))
                ),
                "result_sha256": canonical_hash(r),
                "reviewer": None,
                "judgments": None,
            }
            for r in live_rows
        ],
    )
    live_summary = {
        arm: {
            "delivery": metric([r for r in live_rows if r["arm"] == arm], "delivered"),
            "requests": sum(r["model_calls"] for r in live_rows if r["arm"] == arm),
            "states": dict(
                Counter(
                    (r["response"] or {}).get("status", "error")
                    for r in live_rows
                    if r["arm"] == arm
                )
            ),
        }
        for arm in ARMS
    }
    write_new(run / "live-summary.json", live_summary)
    integrity = {name: digest(ROOT / name) == expected for name, expected in inputs.items()}
    if not all(integrity.values()):
        raise ValueError("historical inputs changed during experiment")
    write_new(
        run / "integrity.json",
        {
            "inputs": integrity,
            "requests": budget.used,
            "max_requests": 48,
            "independent_reviews_pending": len(live_rows),
        },
    )
    lines = [
        "# 原有问答链路与多轮 Agent 的同题交付比较",
        "",
        "原有系统已经有Agent；本轮比较执行器及实际证据交付。默认路径未改变。",
        "",
        "## 原题集组件回放",
        "",
        "110题全部精确重现v6，上下文预算1200token/4000字符。",
        "该表只测同一证据经过Agent再次打包，不代表多轮Agent实际效果。",
        "",
        "| 数据集 | 原v6交付 | Agent二次打包 | 丢失题 |",
        "|---|---:|---:|---|",
    ]
    for ds, s in summary.items():
        lines.append(
            f"| {ds} | {s['original']['numerator']}/{s['original']['denominator']} | "
            f"{s['agent_repack']['numerator']}/{s['agent_repack']['denominator']} | "
            f"{', '.join(s['paired']['lost_ids']) or '无'} |"
        )
    lines += [
        "",
        "## 三组实模配对pilot",
        "",
        "按预定哈希从原题集每库取3题且group不重复；开发小样本，每组一次。",
        "三组共用检索语料和v6选择规则；模型可自选新查询，累计候选与最终交付分别计。",
        "覆盖组额外做本地重排；提示、控制调用和缓存状态不同，延迟不能单独归因于执行器。",
        "",
        "| 组 | 完整交付 | 模型请求 | 最终状态 |",
        "|---|---:|---:|---|",
    ]
    for arm, s in live_summary.items():
        lines.append(
            f"| {arm} | {s['delivery']['numerator']}/{s['delivery']['denominator']} | "
            f"{s['requests']} | {s['states']} |"
        )
    lines += [
        "",
        f"实际模型请求{budget.used}/48；没有追加失败重跑或自审。",
        "",
        "| 题目 | 原链路 | 新Agent FIFO | 新Agent覆盖排序 |",
        "|---|---:|---:|---:|",
    ]
    for q in pilot:
        values = [
            next(
                (
                    r["delivered"]["complete"]
                    for r in live_rows
                    if r["id"] == q["id"] and r["arm"] == arm
                ),
                None,
            )
            for arm in ARMS
        ]
        lines.append(f"| {q['id']} | {values[0]} | {values[1]} | {values[2]} |")
    lines += [
        "",
        "事实与引用独立审核全部pending；交付完整不等于回答正确。",
        "本轮是开发诊断，不是独立确认。失败和协议错误见逐案comparison.json及模型调用记录。",
        "未测场景、稀疏标签和单次模型波动限制结论；不依据本轮自动采用新Agent或覆盖策略。",
        "",
    ]
    (run / "review-report.md").write_text("\n".join(lines))
    write_new(
        run / "artifacts-manifest.json",
        {
            "files": {
                str(p.relative_to(run)): digest(p)
                for p in sorted(run.rglob("*"))
                if p.is_file() and "index" not in p.relative_to(run).parts
            }
        },
    )
    record_operation(
        "完成同题RAG/Agent交付比较并保存报告",
        "给用户可核验的配对证据",
        f"{run / 'review-report.md'}；110题组件回放，{len(live_rows)}条实模输出，"
        f"{budget.used}/48模型请求",
        "独立语义审核pending；pilot不代表全量多轮收益",
    )
    return {"component": summary, "live": live_summary, "requests": budget.used}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    print(json.dumps(execute(args.output.resolve(), args.live), ensure_ascii=False))


if __name__ == "__main__":
    main()
