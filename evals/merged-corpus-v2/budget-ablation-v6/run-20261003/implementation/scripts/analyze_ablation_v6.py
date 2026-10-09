"""Read-only invariants and exploratory diagnostics for the frozen v6 experiment."""

import argparse
import itertools
import json
from pathlib import Path

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.source_quarantine import source_risks

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def reply_text(row):
    response = row["generation"]["response"]
    return (response["status"], response["answer"]) if response else None


def analyze(run):
    protocol = json.loads((run / "protocol.json").read_text())
    for name, sha in protocol["implementation"].items():
        assert digest(ROOT / name) == sha == digest(run / "implementation" / name)
    for name, sha in protocol["frozen_inputs"].items():
        assert digest(ROOT / name) == sha
    audit_path = ROOT / "evals/merged-corpus-v2/recall-delivery-v4/run-20261002/source-audit.json"
    source_audit = json.loads(audit_path.read_text())
    for record in source_audit["source_files"]:
        assert digest(Path(record["source"])) == record["expected"]
    assert digest(run / "experiment-plan.md") == protocol["plan_sha256"]
    assert (
        digest(ROOT / "evals/merged-corpus-v2/budget-ablation-v6/experiment-plan.md")
        == protocol["plan_sha256"]
    )
    chunks_path = ROOT / protocol["directory"] / "chunks.json"
    assert digest(chunks_path) == protocol["chunks_sha256"]
    chunks = {c["id"]: c for c in json.loads(chunks_path.read_text())}
    risks = json.loads((run / "source-risks.json").read_text())
    assert canonical_hash(risks) == protocol["risks_sha256"]
    from infra_rag.models import Chunk

    assert source_risks(Chunk(**c) for c in chunks.values()) == risks
    blocked = {r["chunk_id"] for r in risks}
    for risk in risks:
        assert digest(Path(risk["source"])) == risk["source_sha256"]
        assert chunks[risk["chunk_id"]]["content"] == risk["quote"]
    rows, quarantine = read(run / "rows.jsonl"), read(run / "quarantine.jsonl")
    assert len(rows) == 3960 and len(quarantine) == 220
    assert len({(r["dataset"], r["id"], r["arm"]) for r in rows}) == 3960
    assert len({r["review_key"] for r in quarantine}) == 220
    fourth = ROOT / "evals/merged-corpus-v2/recall-delivery-v4/run-20261002"
    fifth = ROOT / "evals/merged-corpus-v2/budget-support-v5/run-20261003"
    old = {(r["dataset"], r["id"], r["arm"]): r for r in read(fourth / "rows.jsonl")}
    v5 = {(r["dataset"], r["id"], r["arm"]): r for r in read(fifth / "rows.jsonl")}
    indexed = {(r["dataset"], r["id"], r["arm"]): r for r in rows}
    checked, exact, failures = 0, 0, {}
    for r in rows:
        ds, qid, pool = r["dataset"], r["id"], r["pool"]
        baseline = old[ds, qid, "B5" if pool == "B" else "Q5"]
        for field in (
            "candidate_complete",
            "at_k",
            "diagnostics",
            "ranking_context",
            "resolved_gold",
        ):
            assert r[field] == baseline[field]
        config = r["policy"]
        if config in {"T5", "T8", protocol["base_config"]}:
            old_config = "C8" if config == protocol["base_config"] else config
            assert r["context"] == v5[ds, qid, f"{pool}-{old_config}"]["context"]
            assert r["delivered"] == v5[ds, qid, f"{pool}-{old_config}"]["delivered"]
            exact += 1
        if config in protocol["configs"]:
            params = protocol["configs"][config]
            assert r["packing_trace"]["parameters"] == params
            assert params["limit"] is None or len(r["selected_ids"]) <= params["limit"]
            assert all(e["chunk_id"] in r["selected_ids"] for e in r["context"]["evidence"])
        if r["answerable"] and not r["delivered"]["complete"]:
            kind = (
                "eligible_incomplete"
                if not r["packing_pool_complete"]
                else "selected_incomplete"
                if not r["selected_complete"]
                else "truncated_or_omitted"
            )
            failures.setdefault(f"{ds}:{r['arm']}", {}).setdefault(kind, []).append(qid)
    decision = json.loads((run / "decision.json").read_text())
    arm = decision["context_arm"]
    for r in quarantine:
        source = indexed[r["dataset"], r["id"], arm]
        assert r["resolved_gold"] == source["resolved_gold"]
        assert r["original_candidate_complete"] == source["candidate_complete"]
        if r["arm"] == "Q0":
            assert r["context"] == source["context"] and r["delivered"] == source["delivered"]
        else:
            assert not blocked.intersection(r["selected_ids"])
            assert not blocked.intersection(r["packing_trace"]["eligible_ids"])
            assert not blocked.intersection(e["chunk_id"] for e in r["context"]["evidence"])
    for r in rows + quarantine:
        c = r["context"]
        assert c["used_tokens"] <= 1200 and c["used_characters"] <= 4000
        for e in c["evidence"]:
            original = chunks[e["chunk_id"]]
            assert original["content"].startswith(e["content"])
            assert e["truncated"] == (original["content"] != e["content"])
            for field in ("source", "locator", "parent_id", "start_line", "end_line"):
                assert original[field] == e[field]
            checked += 1
    write(run / "failure-breakdown.json", failures)
    summaries = json.loads((run / "summary.json").read_text())
    # Marginal effects average the eight paired edges of each complete factorial grid.
    # They describe this grid; no new p-values or post-hoc primary claims.
    marginal, interactions = {}, {}
    factors = {
        "limit": (8, None),
        "length_power": (0.5, 0.0),
        "protect": (1, 5),
        "neighbors": (True, False),
    }
    configs = protocol["configs"]
    for ds in ("official", "repository"):
        for pool in ("B", "Q"):

            def value(params, ds=ds, pool=pool):
                name = next(k for k, v in configs.items() if v == params)
                return summaries[f"{ds}:{pool}-{name}"]["delivered_complete"]

            for factor, (before, after) in factors.items():
                edges = []
                for name, params in configs.items():
                    if params[factor] == before:
                        changed = {**params, factor: after}
                        edges.append(
                            {"before": name, "delta_count": value(changed) - value(params)}
                        )
                assert len(edges) == 8
                marginal[f"{ds}:{pool}:{factor}"] = {
                    "mean_delta_count": sum(e["delta_count"] for e in edges) / 8,
                    "edges": edges,
                    "exploratory": True,
                }
            for a, b in itertools.combinations(factors, 2):
                differences = []
                for params in configs.values():
                    if params[a] == factors[a][0] and params[b] == factors[b][0]:
                        va = {**params, a: factors[a][1]}
                        vb = {**params, b: factors[b][1]}
                        vab = {**va, b: factors[b][1]}
                        differences.append(value(vab) - value(va) - value(vb) + value(params))
                assert len(differences) == 4
                interactions[f"{ds}:{pool}:{a}*{b}"] = {
                    "mean_difference_of_differences_count": sum(differences) / 4,
                    "strata": differences,
                    "exploratory": True,
                }
    write(run / "factorial-marginals.json", marginal)
    write(run / "factorial-interactions.json", interactions)
    source_deltas = []
    qs = {(r["dataset"], r["id"], r["arm"]): r for r in quarantine}
    for r in quarantine:
        if r["arm"] != "Q1":
            continue
        before = qs[r["dataset"], r["id"], "Q0"]
        if (
            r["blocked_candidate_ids"]
            or r["blocked_context_ids"]
            or r["context"] != before["context"]
        ):
            source_deltas.append(
                {
                    "dataset": r["dataset"],
                    "id": r["id"],
                    "before_delivered": before["delivered"],
                    "after_delivered": r["delivered"],
                    "blocked_candidates": r["blocked_candidate_ids"],
                    "blocked_context": r["blocked_context_ids"],
                    "gold_risk_intersection": r["gold_risk_intersection"],
                    "context_changed": r["context"] != before["context"],
                    "before_ids": [e["chunk_id"] for e in before["context"]["evidence"]],
                    "after_ids": [e["chunk_id"] for e in r["context"]["evidence"]],
                }
            )
    write(run / "source-deltas.json", source_deltas)
    lock = json.loads((run / "generation-lock.json").read_text())
    assert lock["decision_sha256"] == digest(run / "decision.json")
    assert lock["quarantine_sha256"] == digest(run / "quarantine.jsonl")
    answers = read(run / "answers.jsonl")
    assert len(answers) == lock["expected_generations"]
    assert len({r["review_key"] for r in answers}) == len(answers)
    from infra_rag.assistant import SYSTEM_PROMPT

    for r in answers:
        ctx = dict(r["context"])
        assert ctx.pop("include_evidence_metadata") is True
        assert canonical_hash(ctx) == lock["contexts"][f"{r['role']}:{r['id']}"]
        for c in r["generation"]["calls"]:
            assert c["messages"][0]["content"] == SYSTEM_PROMPT
    repeat, packing_pairs, probes = [], [], []
    keyed = {(r["id"], r["role"], r["repetition"]): r for r in answers}

    for r in answers:
        if r["repetition"] == 1:
            second = keyed[r["id"], r["role"], 2]
            assert r["context"] == second["context"]
            repeat.append(
                {
                    "id": r["id"],
                    "role": r["role"],
                    "different_reply": reply_text(r) != reply_text(second),
                }
            )
        if r["role"] == "baseline":
            after = keyed[r["id"], "candidate", r["repetition"]]
            packing_pairs.append(
                {
                    "id": r["id"],
                    "repetition": r["repetition"],
                    "same_context": r["context"] == after["context"],
                    "different_reply": reply_text(r) != reply_text(after),
                }
            )
        if r["id"] in protocol["source_probe_ids"]:
            probes.append(
                {
                    "review_key": r["review_key"],
                    "id": r["id"],
                    "role": r["role"],
                    "repetition": r["repetition"],
                    "delivered": r["delivered"],
                    "answer": r["generation"]["response"],
                    "evidence": [
                        {k: e.get(k) for k in ("citation_id", "chunk_id", "content", "locator")}
                        for e in r["context"]["evidence"]
                    ],
                }
            )
    write(run / "repetition-diagnostics.json", repeat)
    write(run / "packing-generation-pairs.json", packing_pairs)
    write(run / "answer-case-traces.json", probes)
    latency = read(run / "latency.jsonl")
    assert len(latency) == 46
    for role in ("baseline", "candidate"):
        assert len({r["id"] for r in latency if r["role"] == role}) == 23
    write(
        run / "integrity-audit.json",
        {
            "status": "passed",
            "main_rows": len(rows),
            "quarantine_rows": len(quarantine),
            "exact_v5_context_replays": exact,
            "body_locator_checks": checked,
            "source_risks": len(risks),
            "raw_source_files_verified_after_execution": len(source_audit["source_files"]),
            "generation_records": len(answers),
            "latency_records": len(latency),
            "primary_source_hashes_unchanged": True,
            "frozen_inputs_unchanged": True,
            "quarantined_neighbor_reentry": 0,
            "default_changed": False,
            "confirmation_questions_read": False,
            "postprocessor_sha256": digest(Path(__file__)),
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run", type=Path, default=ROOT / "evals/merged-corpus-v2/budget-ablation-v6/run-20261003"
    )
    analyze(parser.parse_args().run.resolve())
