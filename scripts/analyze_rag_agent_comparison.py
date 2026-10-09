"""Post-run fixed-trajectory evidence analysis; no API requests or new retrieval."""

import argparse
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace

from benchmark_rag_agent_comparison import V4, V6, measure
from operation_log import record_operation
from prepare_corpus_v2 import ROOT

from infra_rag.agent import ResearchAgent
from infra_rag.agent_comparison import CoverageResearchAgent, V6ComparisonRetrieval
from infra_rag.benchmarking import digest, write_new
from infra_rag.evaluation import evidence_metrics
from infra_rag.models import Chunk


def analyze(run, output, verification=None):
    if output.exists():
        raise ValueError("Use a new diagnostic output")
    manifest = json.loads((run / "artifacts-manifest.json").read_text())["files"]
    for name, expected in manifest.items():
        if digest(run / name) != expected:
            raise ValueError("Frozen experiment changed")
    freeze = json.loads((run / "freeze.json").read_text())
    protocol = json.loads((V6 / "protocol.json").read_text())
    raw = json.loads((ROOT / protocol["directory"] / "chunks.json").read_text())
    chunks = [Chunk(**c) for c in raw]
    by_chunk = {c.id: c for c in chunks}
    positions = {c.id: i for i, c in enumerate(chunks)}
    cases = {r["id"]: r for r in json.loads((run / "cases.json").read_text())}
    from sentence_transformers import CrossEncoder
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        freeze["models"]["embedding"]["path"],
        local_files_only=True,
        **freeze["tokenizer_options"],
    )

    @lru_cache(maxsize=32768)
    def count(text):
        return len(tokenizer.encode(text, add_special_tokens=False))

    reranker = CrossEncoder(freeze["models"]["reranker"]["path"], local_files_only=True)
    settings = SimpleNamespace(context_tokens=1200, context_chars=4000)
    base = SimpleNamespace(chunks=chunks, settings=settings, reranker=reranker)
    retrieval = V6ComparisonRetrieval(base, {}, count)
    fifo = ResearchAgent(retrieval, SimpleNamespace())
    component = json.loads((run / "component-replay.json").read_text())
    lost = []
    for row in component:
        if (
            not row["answerable"]
            or not row["original"]["complete"]
            or row["agent_repack"]["complete"]
        ):
            continue
        before, after = row["original_evidence"], row["agent_evidence"]
        old_render = "\n\n".join(
            f"[{e['citation_id']}] {by_chunk[e['chunk_id']].heading}\n{e['content']}"
            for e in before
        )
        new_full = "\n\n".join(
            f"[{e['citation_id']}] {e['locator']}\n{e['content']}" for e in before
        )
        new_actual = "\n\n".join(f"[{e['id']}] {e['locator']}\n{e['content']}" for e in after)
        lost.append(
            {
                "id": row["id"],
                "old_tokens": count(old_render),
                "old_characters": len(old_render),
                "same_bodies_agent_headers_tokens": count(new_full),
                "same_bodies_agent_headers_characters": len(new_full),
                "actual_agent_tokens": count(new_actual),
                "actual_agent_characters": len(new_actual),
                "omitted_ids": [
                    e["chunk_id"]
                    for e in before
                    if e["chunk_id"] not in {n["chunk_id"] for n in after}
                ],
                "shortened_ids": [
                    e["chunk_id"]
                    for e in before
                    for n in after
                    if e["chunk_id"] == n["chunk_id"] and e["content"] != n["content"]
                ],
            }
        )
    diagnostics, input_checks = [], []
    live = json.loads((run / "live-results.json").read_text())
    for r in live:
        folder = run / "live" / r["id"] / r["arm"]
        calls = json.loads((folder / "model-calls.json").read_text())
        row = cases[r["id"]]
        if r["arm"] == "legacy-v6":
            # All provided bodies must appear verbatim in the actual request (including retries).
            texts = [m["content"] for c in calls for m in c["messages"] if m["role"] == "user"]
            exact = all(any(e["content"] in t for t in texts) for e in r["evidence"])
            input_checks.append({"id": r["id"], "arm": r["arm"], "actual_input_verified": exact})
            continue
        trace = json.loads((folder / "trace.json").read_text())
        accumulated = {}
        for step in trace["steps"]:
            if step["kind"] == "tool" and step["status"] == "ok":
                for e in json.loads(step["observation"])["evidence"]:
                    accumulated[e["id"]] = e
        query = (
            row["query"]
            + "\n"
            + json.loads((V4 / "bundles" / row["dataset"] / (row["id"] + ".json")).read_text())[
                "B5"
            ]["scoring_query"]
        )
        coverage = CoverageResearchAgent(retrieval, SimpleNamespace(), scoring_query=query)
        old, new = fifo._pack(accumulated), coverage._pack(accumulated)
        actual = old if r["arm"] == "agent-v6-fifo" else new
        if actual != trace["evidence"]["delivered"]:
            raise ValueError("Actual fixed trajectory failed exact reproduction")
        last_state = json.loads(calls[-1]["messages"][-1]["content"])
        exact = last_state["evidence"] == trace["evidence"]["delivered"] == r["evidence"]
        input_checks.append({"id": r["id"], "arm": r["arm"], "actual_input_verified": exact})
        rounds = []
        for s in r["searches"]:
            ids = s["diagnostics"]["candidates"]
            rounds.append(
                {
                    "query": s["query"],
                    "candidate_complete": evidence_metrics(
                        ids, row["resolved_gold"], max(1, len(ids))
                    )["complete_evidence_hit"],
                    "tool_delivery": measure(row, s["context"]["evidence"], positions),
                }
            )
        diagnostics.append(
            {
                "id": r["id"],
                "arm": r["arm"],
                "actual": r["delivered"],
                "cumulative_candidate_complete": r["cumulative_candidate_complete"],
                "same_tool_returns_fifo": measure(row, old, positions),
                "same_tool_returns_coverage": measure(row, new, positions),
                "exact_actual_replay": True,
                "search_rounds": rounds,
                "events": r["events"],
            }
        )
    if not all(r["actual_input_verified"] for r in input_checks):
        raise ValueError("Actual model input differs from scored delivery")
    # Validate all existing archive manifests without changing any archived files.
    archives = (
        V4,
        V6,
        ROOT / "evals/merged-corpus-v2/budget-support-v5/run-20261003",
        ROOT / "evals/agent-e2e-v1/live-20261003",
    )
    archive_count = 0
    for archive in archives:
        path = archive / "artifacts-manifest.json"
        if not path.exists():
            continue
        files = json.loads(path.read_text())["files"]
        for name, expected in files.items():
            if digest(archive / name) != expected:
                raise ValueError(f"Archive changed: {archive.name}/{name}")
        archive_count += len(files)
    output.mkdir(parents=True)
    write_new(
        output / "diagnostics.json",
        {
            "kind": "post_run_fixed_trajectory_component_analysis",
            "experiment_manifest_sha256": digest(run / "artifacts-manifest.json"),
            "new_model_requests": 0,
            "new_retrieval_calls": 0,
            "header_losses": lost,
            "fixed_trajectory_rows": diagnostics,
            "actual_input_checks": input_checks,
            "historical_archive_file_hashes_verified": archive_count,
        },
    )
    validation = {
        "software_verification": json.loads(verification.read_text()) if verification else None,
        "software_verification_sha256": digest(verification) if verification else None,
        "component_exact_replays": 110,
        "actual_model_inputs_verified": len(input_checks),
        "fixed_trajectory_exact_replays": len(diagnostics),
        "historical_archive_file_hashes_verified": archive_count,
        "live_requests": sum(r["model_calls"] for r in live),
        "request_limit": 48,
        "independent_reviews_pending": len(live),
        "default_changed": False,
    }
    write_new(output / "validation.json", validation)
    component_summary = json.loads((run / "component-summary.json").read_text())
    live_summary = json.loads((run / "live-summary.json").read_text())
    software = "软件检查见所附验证记录。" if verification else "软件检查未提供外部记录，保持未知。"
    component_counts = []
    for dataset, label in (("official", "官方"), ("repository", "仓库")):
        original = component_summary[dataset]["original"]
        after = component_summary[dataset]["agent_repack"]
        component_counts.append(
            f"{label}原v6 {original['numerator']}/{original['denominator']}，"
            f"再次打包 {after['numerator']}/{after['denominator']}"
        )
    pilot_counts = []
    for arm, label in (
        ("legacy-v6", "原链路"),
        ("agent-v6-fifo", "新Agent FIFO"),
        ("agent-v6-coverage", "覆盖排序"),
    ):
        delivery = live_summary[arm]["delivery"]
        pilot_counts.append(f"{label} {delivery['numerator']}/{delivery['denominator']}")
    requests = sum(r["model_calls"] for r in live)
    states = dict(Counter((r["response"] or {}).get("status", "error") for r in live))
    lines = [
        "# 同题交付对照的原因分析",
        "",
        "本轮沿用原有RAG开发题与来源，不把原系统描述为没有Agent。",
        "",
        f"{len(component)}题组件回放：" + "；".join(component_counts) + "。",
        "同题三组实模：" + "；".join(pilot_counts) + "。",
        f"模型请求{requests}/48；最终状态{states}，状态不能代表正确。",
        "",
        "## 二次打包为什么丢证据",
        "",
        "原打包预算头使用短标题；Agent重新打包改用完整本地来源locator。",
        "正文没增加，预算头变长后，原来能放下的完整证据超出1200token或4000字符，后段被截断/省略。",
        "",
        "| 题目 | 原预算token | 同正文换Agent头token | 换头字符 | 实际Agent token |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in lost:
        lines.append(
            f"| {r['id']} | {r['old_tokens']} | "
            f"{r['same_bodies_agent_headers_tokens']} | "
            f"{r['same_bodies_agent_headers_characters']} | {r['actual_agent_tokens']} |"
        )
    lines += [
        "",
        "## 新查询与累计排序要分开看",
        "",
        "| 题目/实模组 | 累计候选完整 | 实际交付 | 固定工具返回 FIFO→覆盖排序 |",
        "|---|---:|---:|---:|",
    ]
    for r in diagnostics:
        lines.append(
            f"| {r['id']}/{r['arm']} | {r['cumulative_candidate_complete']} | "
            f"{r['actual']['complete']} | {r['same_tool_returns_fifo']['complete']}"
            f"→{r['same_tool_returns_coverage']['complete']} |"
        )
    lines += [
        "",
        "实模两种Agent会自行生成不同查询，组间差异不能全部归因于排序。",
        "上表固定工具返回的排序对照没有新增模型请求或检索，只检验正文选择，不证明新答案更好。",
        "仓库题的自选查询多为英文或技术短句；原题为中文。这轮无法单独确定语言、改写、候选预算或稀疏标签中哪项造成缺口。",
        "缺gold仍可能有合法替代证据，需独立审核；不能把标签未交付直接判为答案错误。",
        "",
        "## 下一步",
        "",
        "1. 优先统一证据预算头及序列化，避免单轮合格证据再打包丢失。定位保留在元数据中。",
        "2. 保留原查询的检索通道，模型补查作为追加；独立验证双语查询，保持总预算。",
        "3. 固定工具轨迹比较覆盖选择，再做新的实模配对。实模组间差异不能直接归因于排序。",
        "4. 完成必要条件、版本和引用支持的独立审核，再使用新确认题集评估推广。",
        "",
        f"未切换默认流程；未读取holdout；{len(live)}份独立审核pending。检查见validation.json。",
        software,
        "",
    ]
    (output / "review-report.md").write_text("\n".join(lines))
    write_new(
        output / "artifacts-manifest.json",
        {
            "files": {
                str(p.relative_to(output)): digest(p) for p in output.rglob("*") if p.is_file()
            }
        },
    )
    record_operation(
        "分析同题配对实验及固定工具轨迹",
        "拆分查询召回、二次预算头和累计排序影响",
        f"{output / 'review-report.md'}；110题组件、12条固定轨迹、18条实际输入核对；"
        f"{archive_count}历史文件hash；新增模型/检索调用均0",
        "6题开发pilot及稀疏gold不承担总体正确率或采用结论",
    )
    return validation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verification", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            analyze(args.run.resolve(), args.output.resolve(), args.verification),
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
