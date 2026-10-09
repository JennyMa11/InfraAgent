"""Audit frozen Agent traces and attribute observed failures without new model calls."""

import argparse
import json
from collections import Counter
from pathlib import Path

from infra_rag.agent_evaluation import score_trace
from infra_rag.benchmarking import canonical_hash, digest, write_new


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def reasons(case, trace, score):
    found = []
    if trace["final"]["status"] != case["expected_status"]:
        found.append("unexpected_final_status")
    if trace["status"] == "timeout":
        found.append("deadline")
    if any(s["kind"] == "model" and s["status"] == "error" for s in trace["steps"]):
        found.extend(
            s.get("error_code") or "model_error"
            for s in trace["steps"]
            if s["kind"] == "model" and s["status"] == "error"
        )
    if trace["fault_injection"]:
        found.append("controlled_fault:" + trace["fault_injection"])
    if score["candidate_complete"] is False:
        cumulative = set(trace["evidence"].get("cumulative_candidate_ids", []))
        complete = any(
            all(set(options) & cumulative for options in group)
            for group in case["candidate_requirements"]
        )
        found.append("latest_round_candidate_gap" if complete else "candidate_recall_gap")
    elif score["ranked_complete"] is False:
        found.append("ranking_top5_gap")
    if score["delivered_complete"] is False:
        found.append(
            "delivery_gap_after_complete_candidates"
            if score["candidate_complete"]
            else "delivery_gap_with_candidate_gap"
        )
    if score["citation_id_validity"]["value"] == 0:
        found.append("invalid_final_citation")
    for event in trace["events"]:
        if event not in {"tool_failure_or_postcondition"}:
            found.append(event)
    if score["task_success"] is None:
        found.append("semantic_review_pending")
    return list(dict.fromkeys(found))


def analyze(run):
    cases, traces = read(run / "cases.jsonl"), read(run / "traces.jsonl")
    freeze = json.loads((run / "freeze.json").read_text())
    assert digest(run / "cases.jsonl") == freeze["case_sha256"]
    assert digest(run / "schedule.json") == freeze["schedule_sha256"]
    source_root = run.parent
    assert digest(source_root / "sources.json") == freeze["source_manifest_sha256"]
    sources = json.loads((source_root / "sources.json").read_text())["sources"]
    for source in sources:
        assert digest(source_root / "corpus" / source["source"]) == source["sha256"]
    for path, expected in freeze["implementation"].items():
        assert digest(run / "implementation" / path) == expected
    by_id = {c["id"]: c for c in cases}
    reviews = {r["trace_sha256"]: r for r in read(run / "reviews.jsonl")}
    artifact_count, rows = 0, []
    for trace in traces:
        c = by_id[trace["case_id"]]
        review = reviews[canonical_hash(trace)]
        assert review["case_sha256"] == canonical_hash(c) and review["status"] == "pending"
        assert json.loads((run / c["id"] / "trace.json").read_text()) == trace
        assert len(trace["ledger"]) == trace["measurement"]["model_requests"] <= 3
        assert trace["measurement"]["actual_tool_calls"] <= c["execution"].get("tool_calls", 4)
        assert (
            sum(s["kind"] == "tool" and s["status"] != "blocked" for s in trace["steps"])
            == (trace["measurement"]["actual_tool_calls"])
        )
        for step in trace["steps"]:
            for artifact in step["artifacts"]:
                assert digest(artifact["path"]) == artifact["sha256"]
                artifact_count += 1
        # Resolve all positives without asking a search engine or the answer model.
        for group in c["evidence_alternatives"] + c.get("diagnostic_spans", []):
            for span in group:
                assert digest(span["source"]) == span["sha256"]
                assert span["text"] in Path(span["source"]).read_text()
        score = score_trace(c, trace)
        rows.append(
            {
                "case_id": c["id"],
                "category": c["category"],
                "expected": c["expected_status"],
                "actual": trace["final"]["status"],
                "task_success": score["task_success"],
                "candidate_complete": score["candidate_complete"],
                "ranked_complete": score["ranked_complete"],
                "delivered_complete": score["delivered_complete"],
                "reasons": reasons(c, trace, score),
                "requests": trace["measurement"]["model_requests"],
                "model_stop_reasons": [r["metadata"].get("stop_reason") for r in trace["ledger"]],
                "trace": f"{c['id']}/trace.json",
            }
        )
    planned = json.loads((run / "schedule.json").read_text())["scheduled"]

    def units(xs):
        return {(x["run_id"], x["config_id"], x["case_id"], x["repetition"]) for x in xs}

    assert len(traces) == len(planned) == 20 and units(traces) == units(planned)
    total = sum(t["measurement"]["model_requests"] for t in traces)
    assert total == json.loads((run / "requests.json").read_text())["actual_model_attempts"] <= 60
    audit = {
        "case_count": len(cases),
        "trace_count": len(traces),
        "artifacts_verified": artifact_count,
        "requests": total,
        "pending_reviews": len(reviews),
        "reason_counts": dict(Counter(r for row in rows for r in row["reasons"])),
        "rows": rows,
        "scope": "mechanical evidence/trajectory audit; no human judgments or new API calls",
    }
    write_new(run / "failure-analysis.json", audit)
    lines = [
        "# Agent 端到端失败原因分析",
        "",
        f"20 条预定运行全部有轨迹；模型决策尝试 {total}/60；逐步产物核对 {artifact_count} 份。",
        "所有独立审核保持 pending。以下是机械路径/证据判断，不是回答正确率。",
        "",
        "| 用例 | 预期/实际 | 候选/Top5/交付完整 | 原因与轨迹 |",
        "|---|---|---|---|",
    ]
    for row in rows:
        stages = "/".join(
            "—" if row[k] is None else "是" if row[k] else "否"
            for k in ("candidate_complete", "ranked_complete", "delivered_complete")
        )
        lines.append(
            f"| {row['case_id']} | {row['expected']}/{row['actual']} | {stages} | "
            f"{', '.join(row['reasons'])} · [trace]({row['trace']}) |"
        )
    lines += [
        "",
        "同一题可以存在多个原因。候选缺失与交付缺失按实际标签区分，",
        "最新一轮 Top5 与累计候选分开解释；资料截断和来源冲突任务不进入正例召回分母。",
        "未审核事实、条件强度、引用蕴含及来源事实质量不作通过判断。",
        "controlled_fault 表示主动注入的故障，不能称为供应商自然故障。",
    ]
    with (run / "failure-analysis.md").open("x") as f:
        f.write("\n".join(lines) + "\n")
    return audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    audit = analyze(args.run.resolve())
    print(json.dumps({k: v for k, v in audit.items() if k != "rows"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
