import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from infra_rag.config import Settings
from infra_rag.evidence_selection import FrozenSelectionRetrieval, parse_facets, select_order
from infra_rag.models import Chunk, Hit


def hit(cid, score, parent=None):
    chunk = Chunk(cid, parent or cid, "source.md", f"{cid} evidence.", "infra", locator=cid)
    return Hit(chunk, 0.1, rerank_score=score)


def test_coverage_recovers_other_product_instead_of_duplicate_overview():
    hits = [hit("overview", 0.9), hit("duplicate", 0.8), hit("second-product", 0.3)]
    matrix = [[0.95, 0.94, 0.1], [0.1, 0.1, 0.8]]
    averaged, _ = select_order(hits, "F", matrix=matrix)
    covered, trace = select_order(hits, "G", matrix=matrix)
    assert [h.chunk.id for h in averaged[:2]] == ["overview", "duplicate"]
    assert [h.chunk.id for h in covered[:2]] == ["overview", "second-product"]
    assert trace[1]["facet_coverage"] == [0.95, 0.8]
    assert [h.rerank_score for h in hits] == [0.9, 0.8, 0.3]


def test_mmr_keeps_first_frozen_hit_and_penalizes_redundancy():
    hits = [hit("a", 0.9), hit("b", 0.89), hit("c", 0.8)]
    vectors = {"a": [1, 0], "b": [1, 0], "c": [-1, 0]}
    selected, trace = select_order(hits, "M", vectors=vectors)
    assert [h.chunk.id for h in selected] == ["a", "c", "b"]
    assert trace[1]["redundancy"] == 0


def test_single_facet_and_ties_are_deterministic():
    hits = [hit("z", 0.5), hit("b", 0.6), hit("a", 0.6)]
    for policy in ("F", "G"):
        result, _ = select_order(hits, policy, matrix=[[0.7, 0.7, 0.7]])
        assert [h.chunk.id for h in result] == ["a", "b", "z"]
    assert select_order([], "G") == ([], [])
    assert select_order(hits, "T")[0] == hits


@pytest.mark.parametrize("matrix", [[[0.1]], [[float("nan"), 0.1]], [[1.1, 0.1]]])
def test_invalid_matrix_is_rejected(matrix):
    with pytest.raises(ValueError):
        select_order([hit("a", 1), hit("b", 0.9)], "G", matrix=matrix)


@pytest.mark.parametrize("raw", ["bad json", "{}", '{"facets":[]}', '{"facets":[null]}'])
def test_malformed_facets_fall_back_without_answer_information(raw):
    facets, error = parse_facets(raw, "比较两产品", "Compare two products")
    assert facets == [{"question": "Compare two products", "anchor_quote": "比较两产品"}]
    assert error == "invalid_facets"


def test_facet_anchor_must_be_verbatim():
    raw = json.dumps({"facets": [{"question": "Compare A", "anchor_quote": "A版本"}]})
    assert parse_facets(raw, "比较A版本", "Compare version A")[1] is None
    assert parse_facets(raw, "比较B版本", "Compare version B")[1] == "invalid_facets"


def test_replay_packs_neighbors_but_quarantine_blocks_candidates_and_neighbors(tmp_path):
    hits = [hit("first", 0.9, "parent"), hit("risk", 0.8, "parent")]
    neighbor = hit("neighbor", 0.1, "parent").chunk
    chunks = [h.chunk for h in hits] + [neighbor]
    base = SimpleNamespace(
        chunks=chunks,
        vectors=[[1, 0], [1, 0], [0, 1]],
        parent_index={"parent": chunks},
        settings=Settings(data_dir=tmp_path, context_chars=4000, context_tokens=1200),
        _encoder=lambda: SimpleNamespace(token_length=len),
    )
    bundle = {
        "query": {
            "hits": [
                {"chunk_id": h.chunk.id, "score": h.score, "rerank_score": h.rerank_score}
                for h in hits
            ],
            "sha256": "frozen",
        }
    }
    allowed = FrozenSelectionRetrieval(base, bundle, "T", None)
    context = {}
    allowed.search("query", top_k=1, domain="infra", modality="text", context_pack=context)
    assert {e["chunk_id"] for e in context["evidence"]} == {"first", "risk", "neighbor"}
    blocked = FrozenSelectionRetrieval(base, bundle, "T", None, blocked_ids=["risk"])
    context, diagnostics = {}, {}
    result = blocked.search(
        "query", domain="infra", modality="text", context_pack=context, diagnostics=diagnostics
    )
    assert [h.chunk.id for h in result] == ["first"]
    assert {e["chunk_id"] for e in context["evidence"]} == {"first", "neighbor"}
    assert diagnostics["candidates"] == ["first"]
    assert result[0].chunk.locator == "first"
    assert bundle["query"]["hits"][1]["chunk_id"] == "risk"


def test_source_quarantine_covers_deduplicated_alias_and_retains_module_sum(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    benchmark = importlib.import_module("benchmark_selection_v3")
    monkeypatch.setattr(benchmark, "ROOT", tmp_path)
    source = tmp_path / "original.md"
    quote = "模型总参数量 = 64 个专家的参数量之和"
    valid = "将嵌入、注意力、专家、其余组件的各类参数相加即为模型总参数量"
    source.write_text(quote + "\n" + valid)
    risk_path = tmp_path / "evals/merged-corpus-v2/known-risk-review.json"
    risk_path.parent.mkdir(parents=True)
    risk_path.write_text(
        json.dumps(
            [
                {"source": str(source), "line": 1, "quote": quote},
                {"source": str(source), "line": 2, "quote": valid},
            ]
        )
    )
    chunks = [hit("alias", 1).chunk, hit("valid", 0.9).chunk]
    chunks[0].metadata["source_aliases"] = [
        {"source": str(source), "start_line": 1, "end_line": None}
    ]
    chunks[1].source, chunks[1].start_line, chunks[1].end_line = str(source), 2, 2
    base = SimpleNamespace(
        chunks=chunks, vectors=[[1, 0], [0, 1]], parent_index={c.parent_id: [c] for c in chunks}
    )
    run = tmp_path / "run"
    run.mkdir()
    (run / "decision.json").write_text('{"quarantine_arm":"P0-T"}')
    captured = []

    def evaluate(wrapper, *args, **kwargs):
        captured.append(wrapper.blocked_ids)
        assert "alias" not in {c.id for cs in wrapper.parents.values() for c in cs}
        return []

    monkeypatch.setattr(benchmark, "evaluation_rows", evaluate)
    monkeypatch.setattr(benchmark, "paired_statistics", lambda *args: {})
    monkeypatch.setattr(benchmark, "summarize", lambda *args: {})
    monkeypatch.setattr(benchmark, "client", lambda *args: None)
    benchmark.quarantine_phase(
        run,
        {"repository": (tmp_path, [], {})},
        {("repository", "P0"): {}},
        base,
        None,
    )
    assert captured == [{"alias"}]
    policy = json.loads((run / "quarantine-policy.json").read_text())
    assert len(policy["selected_risks"]) == len(policy["skipped_risks"]) == 1
