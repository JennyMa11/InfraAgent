"""Read-only integrity, failure and generation diagnostics for budget/support v5."""

import argparse
import json
from pathlib import Path

from infra_rag.benchmarking import digest


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def analyze(run):
    root = Path(__file__).resolve().parents[1]
    previous = root / "evals/merged-corpus-v2/recall-delivery-v4/run-20261002"
    protocol = json.loads((run / "protocol.json").read_text())
    retrieval, answers = rows(run / "rows.jsonl"), rows(run / "answers.jsonl")
    probes, latency = rows(run / "verifier-probes.jsonl"), rows(run / "latency.jsonl")
    assert len(retrieval) == 880 and len(answers) == 92 and len(probes) == 4 and len(latency) == 46
    assert len({r["review_key"] for r in answers}) == 92
    assert len({(r["dataset"], r["id"], r["arm"]) for r in retrieval}) == 880
    for name, sha in protocol["implementation"].items():
        assert digest(root / name) == sha == digest(run / "implementation" / name)
    chunks_path = root / protocol["directory"] / "chunks.json"
    assert digest(chunks_path) == protocol["chunks_sha256"]
    chunks = {c["id"]: c for c in json.loads(chunks_path.read_text())}
    old = {(r["dataset"], r["id"], r["arm"]): r for r in rows(previous / "rows.jsonl")}
    checked = 0
    baseline_replays = 0
    failures = {}
    for r in retrieval:
        base = old[r["dataset"], r["id"], "B5" if r["pool"] == "B" else "Q5"]
        assert r["candidate_complete"] == base["candidate_complete"]
        assert r["at_k"] == base["at_k"]
        assert r["diagnostics"]["final"] == base["diagnostics"]["final"]
        if r["policy"] == "T5":
            assert r["context"] == base["context"]
            baseline_replays += 1
        if r["arm"] == "B-T8":
            assert r["context"] == old[r["dataset"], r["id"], "B8"]["context"]
            baseline_replays += 1
        if r["policy"] in {"R8", "C8"}:
            assert len(r["selected_ids"]) <= 8
            assert all(e["chunk_id"] in r["selected_ids"] for e in r["context"]["evidence"])
        c = r["context"]
        assert c["used_tokens"] <= 1200 and c["used_characters"] <= 4000
        for e in c["evidence"]:
            original = chunks[e["chunk_id"]]
            assert original["content"].startswith(e["content"])
            assert (e["content"] != original["content"]) == e["truncated"]
            for field in ("source", "locator", "parent_id", "start_line", "end_line"):
                assert e[field] == original[field]
            checked += 1
        if r["answerable"] and not r["delivered"]["complete"]:
            key = f"{r['dataset']}:{r['arm']}"
            kind = (
                "eligible_incomplete"
                if not r["packing_pool_complete"]
                else "selected_incomplete"
                if not r["selected_complete"]
                else "text_truncated_or_omitted"
            )
            failures.setdefault(key, {}).setdefault(kind, []).append(r["id"])
    write(run / "failure-breakdown.json", failures)
    paired, repetition, blockers = {}, [], []
    keyed = {(r["dataset"], r["id"], r["prompt"], r["repetition"]): r for r in answers}
    for r in answers:
        other = keyed[r["dataset"], r["id"], "G1" if r["prompt"] == "G0" else "G0", r["repetition"]]
        assert r["context"] == other["context"]
        if r["prompt"] == "G0" and r["generation"]["calls"] and other["generation"]["calls"]:
            left = r["generation"]["calls"][0]["messages"]
            right = other["generation"]["calls"][0]["messages"]
            assert left[1:] == right[1:]
            assert right[0]["content"].startswith(left[0]["content"])
        verdict = r["verification"]["verdict"]
        if verdict in {"unsupported", "uncertain"}:
            assert r["guarded_response"]["status"] == "no_evidence"
            blockers.append(
                {
                    "review_key": r["review_key"],
                    "id": r["id"],
                    "prompt": r["prompt"],
                    "repetition": r["repetition"],
                    "verdict": verdict,
                    "issues": r["verification"]["issues"],
                    "verification_error": r["verification"]["error"],
                    "answer": r["generation"]["response"]["answer"],
                }
            )
        if r["prompt"] == "G0":
            a, b = r["verification"]["verdict"], other["verification"]["verdict"]
            key = f"{a}->{b}"
            paired[key] = paired.get(key, 0) + 1
        if r["repetition"] == 1:
            second = keyed[r["dataset"], r["id"], r["prompt"], 2]
            a, b = r["generation"]["response"], second["generation"]["response"]
            repetition.append(
                {
                    "id": r["id"],
                    "prompt": r["prompt"],
                    "first_status": a["status"] if a else None,
                    "second_status": b["status"] if b else None,
                    "answer_identical": bool(a and b and a["answer"] == b["answer"]),
                    "first_verdict": verdict,
                    "second_verdict": second["verification"]["verdict"],
                }
            )
    write(run / "verifier-blockers.json", blockers)
    write(run / "paired-verifier-transitions.json", paired)
    write(run / "repeat-diagnostics.json", repetition)
    if (run / "support-observations.json").exists():
        support = json.loads((run / "support-observations.json").read_text())
        traces = json.loads((run / "budget-case-traces.json").read_text())
        still_fits = sum(
            any(b["can_individually_fit_at_termination"] for b in r["lost_gold"]) for r in traces
        )
        lines = [
            "",
            "## 后续只读核查",
            "",
            f"B-C8相对B-T5丢失的{len(traces)}题，正确原段均在可选池；"
            f"其中{still_fits}题在选满8段后仍能单独放入缺失原段。",
            "段数上限、长度奖励和邻接先验在本轮一起变化，不能把下降单独归因于一个因素。",
            "G0/G1的CUDA风险题各两次复述过强必要条件，4条均被核验器放过；旧负例探针也被放过。",
            "[NVIDIA CUDA 13.0.1 §10.2.1.1]("
            + support["cuda_case"]["primary_reference"]
            + ")给出部分线程参与及访问置换仍能合并的反例，不能要求32线程全部连续访问。",
            "MoE旧来源范围风险在两提示的四条答案及旧探针中仍被复述且核验通过。",
            "official-002-4的G0第一次缺缓存键前提，核验指出缺口并转为拒答；"
            "另一次和G1两次已拒答。这是样本观察，不是全体正确率改善。",
            "official-014-4有一次status=answered，但正文回答不能给出精确P95、未编造数值；"
            "不按状态直接判错。逐案证据见answer-observations.md。",
            "无合格新配置，打包延迟的46条均为B-T5路径重复，不能作候选性能提升比较。",
            "初始tokenizer选项及生成样本入口错误均在API前被校验拦截、修正并归档；"
            "880条回放逐字复用及函数AST核对见retrieval-import.json、experiment-plan.md。",
        ]
        report = run / "execution-report.md"
        original_report = report.read_text().split("\n## 后续只读核查", 1)[0].rstrip()
        report.write_text(original_report + "\n" + "\n".join(lines) + "\n")
    assert not (run / "confirmation").exists()
    write(
        run / "execution-audit.json",
        {
            "retrieval_rows": 880,
            "generation_rows": 92,
            "probe_rows": 4,
            "latency_rows": 46,
            "original_body_locator_checks": checked,
            "exact_old_context_replays": baseline_replays,
            "scores_ranking_candidates_unchanged": True,
            "paired_contexts_and_user_prompts_identical": True,
            "all_budgets_respected": True,
            "primary_source_hashes_and_archives_match": True,
            "default_changed": False,
            "confirmation_questions_read": False,
            "independent_human_fact_correct": None,
        },
    )
    write(
        run / "postprocessing-protocol.json",
        {
            "kind": "read_only",
            "script_sha256": digest(Path(__file__)),
            "input_hashes": {
                n: digest(run / n)
                for n in (
                    "protocol.json",
                    "rows.jsonl",
                    "answers.jsonl",
                    "verifier-probes.jsonl",
                    "latency.jsonl",
                    "support-observations.json",
                    "budget-case-traces.json",
                )
                if (run / n).exists()
            },
        },
    )
    print(
        json.dumps(
            {
                "replays": baseline_replays,
                "bodies_checked": checked,
                "verifier_transitions": paired,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    analyze(parser.parse_args().output.resolve())
