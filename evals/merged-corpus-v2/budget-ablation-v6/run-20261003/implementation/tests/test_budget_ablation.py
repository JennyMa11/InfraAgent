import copy

import pytest

from infra_rag.budget_ablation import AblationPacker
from infra_rag.budget_evidence import budget_pack
from infra_rag.models import Chunk, Hit
from infra_rag.source_quarantine import source_risks


def hit(cid, text, score=0.8, source="notes.md", parent="p", collection="community"):
    c = Chunk(
        cid,
        parent,
        source,
        text,
        "infra",
        heading="Evidence",
        metadata={"body_type": "explanation", "collection": collection, "sha256": "frozen"},
    )
    return Hit(c, 0.0, rerank_score=score)


def test_ablation_base_exactly_replays_v5_without_mutating_inputs():
    hits = [hit("a", "alpha condition", 0.9), hit("b", "beta version", 0.8)]
    neighbor = hit("c", "other explanatory condition", 0.7)
    chunks = {neighbor.chunk.id: neighbor.chunk}
    ctx = {"evidence": [{"chunk_id": "c"}]}
    saved = copy.deepcopy(hits)
    old = budget_pack(hits, ctx, chunks, "alpha beta", len, coverage=True)
    new = AblationPacker(hits, ctx, chunks, "alpha beta", len).pack()
    assert [h.chunk.id for h in old[0]] == [h.chunk.id for h in new[0]]
    assert old[1] == new[1]
    assert old[2]["eligible_ids"] == new[2]["eligible_ids"]
    assert hits == saved


def test_unlimited_count_uses_remaining_budget_and_never_exceeds_either_limit():
    hits = [hit(str(i), f"Fact {i}.", 0.8 - i / 100) for i in range(12)]
    p = AblationPacker(hits, {"evidence": []}, {}, "fact", len)
    limited = p.pack(token_budget=1000, char_budget=1000)
    unlimited = p.pack(limit=None, token_budget=1000, char_budget=1000)
    assert len(limited[0]) == 8 and len(unlimited[0]) == 12
    constrained = p.pack(limit=None, token_budget=220, char_budget=210)
    assert constrained[1]["used_tokens"] <= 220 and constrained[1]["used_characters"] <= 210


def test_removing_cost_penalty_restores_high_relevance_long_fact():
    hits = [hit("first", "Anchor.", 1.0), hit("long", "Specific condition " * 35, 0.9)]
    hits += [hit(str(i), f"Detail_{i}.", 0.8) for i in range(10)]
    p = AblationPacker(hits, {"evidence": []}, {}, "Specific condition", len)
    costly = {h.chunk.id for h in p.pack()[0]}
    relevant = {h.chunk.id for h in p.pack(length_power=0.0)[0]}
    assert "long" not in costly and "long" in relevant


def test_top5_protection_preserves_original_order_before_greedy_choices():
    hits = [hit(str(i), f"Condition {i}. " * (i + 1), 0.9 - i / 100) for i in range(10)]
    result = AblationPacker(hits, {"evidence": []}, {}, "condition", len).pack(protect=5)
    assert [h.chunk.id for h in result[0]][:5] == [str(i) for i in range(5)]
    assert all(e["protected"] for e in result[2]["selection_trace"][:5])


def test_blocked_candidates_and_neighbors_cannot_flow_back_through_parent():
    hits = [hit("a", "safe"), hit("blocked", "dangerous")]
    neighbors = {"blocked": hits[1].chunk, "neighbor": hit("neighbor", "dangerous").chunk}
    context = {"evidence": [{"chunk_id": cid} for cid in neighbors]}
    p = AblationPacker(hits, context, neighbors, "q", len, blocked_ids=neighbors)
    assert [h.chunk.id for h in p.pack(limit=None)[0]] == ["a"]
    assert not p.pack()[2]["neighbor_priors"]


def test_neighbor_toggle_keeps_direct_candidate_that_is_also_old_context():
    direct = hit("direct", "Direct fact")
    neighbor = hit("neighbor", "Another fact")
    p = AblationPacker(
        [direct],
        {"evidence": [{"chunk_id": "direct"}, {"chunk_id": "neighbor"}]},
        {h.chunk.id: h.chunk for h in [direct, neighbor]},
        "fact",
        len,
    )
    assert p.pack(neighbors=False)[2]["eligible_ids"] == ["direct"]
    assert p.pack(neighbors=True)[2]["eligible_ids"] == ["direct", "neighbor"]


def test_source_rules_isolate_explicit_scope_but_keep_recommendations_and_valid_sums():
    texts = [
        "**模型总参数量** = 64 个专家的参数量之和。",
        "模型总参数量约等于64个专家参数之和。",
        "把嵌入、注意力、共享FFN、专家等各类参数相加即为模型总参数量。",
        "合并访问推荐同一个warp的线程应该访问连续地址。",
        "float val = data[random_index]; // 随机访问：完全无法合并",
        "float val = data[threadIdx.x]; // 一次128B事务搞定",
        "合并访问：地址连续，一次事务满足所有线程。",
        "计算能力5.2，float示例一次128B事务。",
    ]
    chunks = [hit(str(i), text).chunk for i, text in enumerate(texts)]
    saved = copy.deepcopy(chunks)
    assert [r["chunk_id"] for r in source_risks(chunks)] == ["0", "4", "5", "6"]
    assert chunks == saved
    assert not source_risks([hit("official", texts[0], collection="official").chunk])


@pytest.mark.parametrize("kwargs", [{"limit": 0}, {"length_power": -1}, {"protect": 2}])
def test_ablation_rejects_unregistered_settings(kwargs):
    p = AblationPacker([hit("a", "fact")], {"evidence": []}, {}, "q", len)
    with pytest.raises(ValueError):
        p.pack(**kwargs)


def test_quarantine_driver_preserves_gold_and_filters_neighbor_reentry(tmp_path, monkeypatch):
    import importlib
    import json
    from pathlib import Path

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    driver = importlib.import_module("benchmark_ablation_v6")
    hits = [hit("risk", "Risk claim.", 0.9), hit("safe", "Safe fact.")]
    neighbor = hit("neighbor", "Risk neighbor.")
    chunks = {h.chunk.id: h.chunk for h in [*hits, neighbor]}
    parents = {"p": list(chunks.values())}
    gold = {
        "evidence_alternatives": [
            {
                "requirements": [["risk"]],
                "spans": [{"absolute_source": "notes.md", "text": "Risk claim."}],
            }
        ]
    }
    mapping, originals = {}, []
    for ds, size in (("official", 60), ("repository", 50)):
        for i in range(size):
            qid = f"{ds}-{i}"
            row = {
                "dataset": ds,
                "id": qid,
                "query": "q",
                "group_id": "group",
                "answerable": True,
                "resolved_gold": gold,
                "candidate_complete": 1.0,
                "diagnostics": {
                    "candidates": ["risk", "safe"],
                    "final": [
                        {"chunk_id": h.chunk.id, "rerank_score": h.rerank_score} for h in hits
                    ],
                },
            }
            chosen, ctx, trace = driver.control_pack("B", "T5", row, chunks, parents, len)
            base = driver.output(
                row, "B-T5", "B", "T5", chosen, ctx, trace, {cid: j for j, cid in enumerate(chunks)}
            )
            row["context"] = base["context"]
            mapping[ds, qid, "B5"] = row
            originals.append(base)
    driver.write_json(tmp_path / "decision.json", {"context_arm": "B-T5"})
    for row in originals:
        driver.append(tmp_path / "rows.jsonl", row)
    saved = copy.deepcopy(mapping)
    driver.quarantine(
        tmp_path,
        mapping,
        chunks,
        parents,
        {},
        len,
        [{"chunk_id": cid} for cid in ("risk", "neighbor")],
    )
    rows = driver.read_rows(tmp_path / "quarantine.jsonl")
    for row in rows:
        assert row["resolved_gold"] == gold and row["gold_risk_intersection"] == ["risk"]
        if row["arm"] == "Q1":
            assert row["candidate_complete"] == 0 and row["original_candidate_complete"] == 1
            assert not row["delivered"]["complete"]
            assert {e["chunk_id"] for e in row["context"]["evidence"]} == {"safe"}
    assert mapping == saved
    summary = json.loads((tmp_path / "quarantine-summary.json").read_text())
    assert summary["official:Q0"]["delivered_complete"] == 60
    assert summary["official:Q1"]["delivered_complete"] == 0


def test_repeat_diagnostics_ignore_generated_conversation_ids(monkeypatch):
    import importlib
    from pathlib import Path

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    analyze = importlib.import_module("analyze_ablation_v6")
    a = {
        "generation": {
            "response": {"status": "answered", "answer": "fact", "conversation_id": "one"}
        }
    }
    b = copy.deepcopy(a)
    b["generation"]["response"]["conversation_id"] = "two"
    assert analyze.reply_text(a) == analyze.reply_text(b)
    b["generation"]["response"]["answer"] = "changed fact"
    assert analyze.reply_text(a) != analyze.reply_text(b)
