import json

import pytest

from infra_rag.config import Settings
from infra_rag.rag_comparison import (
    CHAIN_NAMES,
    HybridRAGChain,
    OfflineAgentModel,
    RAGComparisonRunner,
    evaluate_result,
    evidence_integrity,
    prepare_cases,
)
from infra_rag.service import RetrievalService


@pytest.fixture
def retrieval(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "cache.md").write_text(
        "# PagedAttention\n\nPagedAttention 管理 KV Cache，降低显存碎片。\n\n"
        "连续分配由另一个独立段落说明。"
    )
    (corpus / "other.md").write_text("# 隔离\n\n另一个域的资料。")
    service = RetrievalService(
        Settings(data_dir=tmp_path / "index", chunk_size=100, context_tokens=1200)
    )
    service.ingest(corpus / "cache.md", "infra")
    service.ingest(corpus / "other.md", "other")
    return service, corpus / "cache.md"


def labeled_case(retrieval, source):
    return {
        "id": "cache",
        "query": "PagedAttention 有什么作用？",
        "domain": "infra",
        "relevant": [str(source.resolve())],
        "group_id": "cache-group",
        "label": "source",
    }


def test_baseline_uses_actual_ranked_and_delivered_layers(retrieval):
    service, source = retrieval
    result = HybridRAGChain(service, top_k=2).retrieve("PagedAttention", domain="infra")
    assert result["chain"] == "baseline"
    assert result["candidates"]
    assert len(result["ranked"]) == 2
    assert result["evidence"]
    indexed = {chunk.id for chunk in service.chunks}
    assert all(row["chunk_id"] in indexed for row in result["evidence"])


def test_chain_does_not_receive_labels_and_case_is_not_mutated(retrieval):
    service, source = retrieval
    case = labeled_case(service, source)
    saved = dict(case)
    result = RAGComparisonRunner(service, chains=["baseline"]).run_case(case)
    assert case == saved
    chain = result["results"]["baseline"]
    assert chain["evaluation"]["candidate"]["recall"] == 1.0
    assert chain["evaluation"]["delivered"]["returned"] > 0
    assert chain["evaluation"]["answer_review"]["fact_correct"] is None
    assert "relevant" not in chain


def test_comparison_is_immutable_and_failed_chains_have_no_fake_zero(retrieval, tmp_path):
    service, source = retrieval
    with pytest.raises(ValueError, match="explicit live or offline model"):
        RAGComparisonRunner(service, chains=["baseline", "agentic_rag"], model=None)

    runner = RAGComparisonRunner(service, chains=["baseline"], top_k=2)
    report = runner.compare(
        [labeled_case(service, source)],
        tmp_path / "run",
        run_id="offline-test",
    )
    assert report["summary"]["baseline"]["succeeded"] == 1
    assert report["summary"]["baseline"]["candidate"]["recall"] == 1.0
    assert (tmp_path / "run" / "manifest.json").exists()
    assert (tmp_path / "run" / "cases" / "cache" / "result.json").exists()
    with pytest.raises(FileExistsError):
        runner.compare([labeled_case(service, source)], tmp_path / "run")


def test_offline_agent_full_trace_and_resources_are_retained(retrieval, tmp_path):
    service, source = retrieval
    runner = RAGComparisonRunner(
        service, chains=["baseline", "agentic_rag"], model=OfflineAgentModel(), top_k=2
    )
    report = runner.compare([labeled_case(service, source)], tmp_path / "offline", run_id="fixture")
    agent = report["results"][0]["results"]["agentic_rag"]
    assert agent["status"] == "ok"
    assert agent["agent_status"] == "answered"
    assert report["model"]["offline_fixture"] is True
    assert report["summary"]["agentic_rag"]["resources"]["model_requests"] == 2
    assert agent["evaluation"]["delivered"]["returned"] > 0
    assert (tmp_path / "offline" / "cases" / "cache" / "agentic_rag").is_dir()
    assert list((tmp_path / "offline" / "cases" / "cache" / "agentic_rag").rglob("trace.json"))


def test_source_chunk_parent_labels_are_resolved_outside_chain(retrieval, tmp_path):
    service, source = retrieval
    chunk = service.chunks[0]
    dataset = [{"id": "one", "query": "KV Cache", "domain": "infra", "relevant": [chunk.id]}]
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(dataset))
    for label in ("chunk", "parent"):
        item = dict(dataset[0])
        item["relevant"] = [chunk.id if label == "chunk" else chunk.parent_id]
        path.write_text(json.dumps([item]))
        cases = prepare_cases(service, [item], path, label)
        assert cases[0]["relevant"] == item["relevant"]
    with pytest.raises(ValueError, match="labeled relevant"):
        prepare_cases(service, [{"id": "bad", "query": "?", "relevant": []}], path)


def test_delivered_text_tampering_is_not_a_valid_citation(retrieval):
    service, source = retrieval
    raw = HybridRAGChain(service).retrieve("PagedAttention", domain="infra")
    assert evidence_integrity(service, raw["evidence"])["status"] == "valid"
    raw["evidence"][0]["content"] = "模型编造的答案"
    integrity = evidence_integrity(service, raw["evidence"])
    assert integrity["status"] == "invalid"
    assert integrity["failures"][0]["error"] == "delivered_text_not_in_source_chunk"


def test_citation_identity_is_checked_not_only_chunk_content(retrieval):
    service, _ = retrieval
    raw = HybridRAGChain(service).retrieve("PagedAttention", domain="infra")
    raw["evidence"][0]["citation_id"] = "E0000000000000000"
    integrity = evidence_integrity(service, raw["evidence"])
    assert integrity["status"] == "invalid"
    assert "citation_id_mismatch" in {item["error"] for item in integrity["failures"]}


def test_cumulative_agent_candidates_not_only_last_round_are_evaluated(retrieval):
    service, _ = retrieval
    first, second = service.chunks[0].id, service.chunks[-1].id
    result = {
        "evidence": {
            "delivered": [],
            "candidate_ids": [second],
            "cumulative_candidate_ids": [first, second],
            "ranked_ids": [second],
        }
    }
    case = {
        "relevant": [first],
        "label": "chunk",
    }
    evaluation = evaluate_result(service, case, result, label="chunk", k=2)
    assert evaluation["candidate"]["recall"] == 1.0
    assert evaluation["ranked"]["recall"] == 0.0


def test_agent_domain_is_applied_and_reset_between_cases(retrieval, tmp_path):
    service, source = retrieval
    runner = RAGComparisonRunner(
        service, chains=["agentic_rag"], model=OfflineAgentModel(), top_k=1
    )
    valid = labeled_case(service, source)
    runner.run_case(valid, output_dir=tmp_path / "valid", run_id="domain")
    other = {"id": "other", "query": "PagedAttention", "domain": "other"}
    runner.run_case(other, output_dir=tmp_path / "other", run_id="domain")
    result = runner.run_case({**valid, "id": "last"}, output_dir=tmp_path / "last", run_id="domain")
    assert result["results"]["agentic_rag"]["evidence"]["delivered"]
    assert all(
        row["source"] == str(source.resolve())
        for row in result["results"]["agentic_rag"]["evidence"]["delivered"]
    )


def test_unsafe_case_path_is_rejected_before_artifact_write(retrieval):
    service, source = retrieval
    case = labeled_case(service, source)
    case["id"] = "../outside"
    with pytest.raises(ValueError, match="safe path"):
        RAGComparisonRunner(service, chains=["baseline"]).run_case(case)


def test_domain_is_passed_to_chain_and_empty_index_is_not_invented(retrieval, tmp_path):
    service, source = retrieval
    result = HybridRAGChain(service).retrieve("隔离", domain="other")
    assert all(row["source"] != str(source.resolve()) for row in result["evidence"])
    assert set(CHAIN_NAMES) == {"baseline", "graph_rag", "agentic_rag"}
