"""Graph expansion behavior, provenance, isolation, and delivery budgets."""

import copy
import json
from dataclasses import replace

from infra_rag.config import Settings
from infra_rag.graph_rag import GraphRAGChain
from infra_rag.models import Chunk
from infra_rag.service import RetrievalService


def chunk(cid, content, *, parent="parent", source="guide.md", domain="infra", **kwargs):
    line = kwargs.pop("line", 1)
    values = {
        "heading": "Memory",
        "locator": f"{source}#L{line}",
        "start_line": line,
        "end_line": line,
    }
    values.update(kwargs)
    return Chunk(cid, parent, source, content, domain, **values)


def service(tmp_path, chunks, **settings):
    retrieval = RetrievalService(Settings(data_dir=tmp_path / "index", **settings))
    retrieval._commit(chunks)
    return retrieval


def without_timing(value):
    result = copy.deepcopy(value)
    result.pop("latency_ms")
    for step in result.pop("trace"):
        step.pop("duration_ms")
        if step["step"] == "hybrid_seed_retrieval":
            step.pop("base_diagnostics")
        if step["step"] == "graph_build":
            step["graph_stats"].pop("cache_hit")
    return result


def expansion(result, cid):
    return next(item for item in result["candidates"] if item["chunk_id"] == cid)


def graph_step(result):
    return next(step for step in result["trace"] if step["step"] == "graph_build")


def test_graph_is_deterministic_and_serializable_without_mutating_chunks(tmp_path):
    chunks = [
        chunk("a", "PagedAttention manages KVCache.", line=1),
        chunk("b", "A scheduling algorithm follows.", line=2),
        chunk("c", "KVCache is reused by the memory manager.", parent="other", line=3),
    ]
    retrieval = service(tmp_path, chunks)
    before = copy.deepcopy(chunks)
    chain = GraphRAGChain(retrieval, top_k=3, context_counter=len)
    first = chain.retrieve("PagedAttention")
    second = chain.retrieve("PagedAttention")
    assert without_timing(first) == without_timing(second)
    assert graph_step(first)["graph_stats"]["cache_hit"] is False
    assert graph_step(second)["graph_stats"]["cache_hit"] is True
    assert graph_step(first)["graph_stats"]["graph_version"] == "local-chunk-relations-v1"
    assert expansion(first, "a")["base_rank"] == 1
    assert expansion(first, "b")["origin"] == "expanded"
    assert expansion(first, "c")["hop"] >= 1
    assert expansion(first, "c")["expansion_reasons"]
    assert json.loads(json.dumps(first, ensure_ascii=False))["chain"] == "graph_rag"
    assert chunks == before


def test_domain_isolation_applies_to_seeds_edges_entities_and_evidence(tmp_path):
    chunks = [
        chunk("allowed", "UniqueSignal introduces KVCache.", domain="infra"),
        chunk(
            "foreign",
            "KVCache foreign details.",
            parent="parent",
            source="guide.md",
            domain="other",
            line=2,
        ),
        chunk("foreign-adjacent", "Adjacent secret.", domain="other", line=3),
    ]
    result = GraphRAGChain(service(tmp_path, chunks), context_counter=len).retrieve(
        "UniqueSignal", domain="infra"
    )
    assert [item["chunk_id"] for item in result["candidates"]] == ["allowed"]
    assert {item["chunk_id"] for item in result["evidence"]} == {"allowed"}
    assert result["domain"] == "infra"


def test_expansion_is_bounded_and_counts_are_actual(tmp_path):
    chunks = [
        chunk(f"c{index}", "SharedTopic detail.", parent="parent", line=index + 1)
        for index in range(8)
    ]
    result = GraphRAGChain(
        service(tmp_path, chunks),
        top_k=3,
        max_seed_hits=1,
        max_expanded_chunks=2,
        context_counter=len,
    ).retrieve("SharedTopic")
    assert sum(item["origin"] == "expanded" for item in result["candidates"]) == 2
    step = next(step for step in result["trace"] if step["step"] == "graph_expand")
    assert step["expanded_count"] == 2
    assert len(step["expansion_reasons"]) == 2
    assert len(result["ranked"]) == 3


def test_fused_ranking_admits_supported_expansion_without_displacing_stronger_seed(tmp_path):
    chunks = [
        chunk("first", "UniqueSignal first seed.", line=1),
        chunk("second", "UniqueSignal second seed.", line=2),
        chunk("expanded", "SharedTopic supporting context.", line=3),
    ]
    retrieval = service(tmp_path, chunks)
    chain = GraphRAGChain(
        retrieval, top_k=3, max_seed_hits=2, max_expanded_chunks=1, context_counter=len
    )
    result = chain.retrieve("UniqueSignal")
    candidates = {item["chunk_id"]: item for item in result["candidates"]}
    assert candidates["first"]["origin"] == "seed"
    assert candidates["second"]["origin"] == "seed"
    assert candidates["expanded"]["origin"] == "expanded"
    assert candidates["expanded"]["graph_score"] > 0
    selected = result["ranked"][:3]
    assert selected[0]["chunk_id"] == "first"
    assert selected[0]["score"] == candidates["expanded"]["graph_score"]
    assert any(item["chunk_id"] == "expanded" for item in selected)
    delivered_expansion = next(item for item in selected if item["chunk_id"] == "expanded")
    assert delivered_expansion["hop"] >= 1 and delivered_expansion["expansion_reasons"]
    assert {item["chunk_id"] for item in result["evidence"]} == {
        item["chunk_id"] for item in selected
    }

    # Fixed-score fusion has no reserved expansion slot: stronger seeds win ties.
    first_score = candidates["first"]["base_score"]
    second_score = candidates["second"]["base_score"]
    candidates["expanded"]["graph_score"] = min(first_score, second_score) / 2
    fused = chain._rank(list(candidates.values()))
    assert [item["chunk_id"] for item in fused[:2]] == ["first", "second"]
    assert all(item["score"] == item["base_score"] + item["graph_score"] for item in fused)

    # Real retrieval has no reserved expansion slot: strongest support still loses
    # to the best seed, and a single-result cutoff returns that seed.
    limited = GraphRAGChain(
        retrieval, top_k=1, max_seed_hits=2, max_expanded_chunks=1, context_counter=len
    ).retrieve("UniqueSignal")
    assert [item["chunk_id"] for item in limited["ranked"][:1]] == ["first"]
    assert [item["chunk_id"] for item in limited["evidence"]] == ["first"]


def test_adjacent_and_entity_relations_support_multi_hop_expansion(tmp_path):
    chunks = [
        chunk("seed", "AlphaTrigger begins the sequence.", parent="p1", line=1),
        chunk("entity", "TransitionBridge records state.", parent="p2", line=2),
        chunk("target", "TransitionBridge completes the sequence.", parent="p3", line=40),
    ]
    retrieval = service(tmp_path, chunks)
    result = GraphRAGChain(retrieval, top_k=1, max_seed_hits=1, context_counter=len).retrieve(
        "AlphaTrigger"
    )
    assert expansion(result, "entity")["hop"] == 1
    assert expansion(result, "target")["hop"] == 1
    assert any(
        reason["relation"] == "adjacent_chunk"
        for reason in expansion(result, "entity")["expansion_reasons"]
    )

    retrieval._commit(
        [*chunks, chunk("adjacent", "TransitionBridge neighbor.", parent="p4", line=21)]
    )
    multi_hop = GraphRAGChain(retrieval, top_k=1, max_seed_hits=1, context_counter=len).retrieve(
        "AlphaTrigger"
    )
    assert expansion(multi_hop, "adjacent")["hop"] == 2
    assert expansion(multi_hop, "target")["hop"] == 1
    assert any(
        reason["from_chunk_id"] == "entity" and reason["relation"] == "shared_entity"
        for reason in expansion(multi_hop, "adjacent")["expansion_reasons"]
    )
    assert any(
        reason["from_chunk_id"] == "entity" and reason["relation"] == "shared_entity"
        for reason in expansion(multi_hop, "target")["expansion_reasons"]
    )
    target_reasons = expansion(multi_hop, "target")["expansion_reasons"]
    assert any(
        reason["relation"] == "shared_entity" and reason["entities"] == ["transitionbridge"]
        for reason in target_reasons
    )
    shared = next(reason for reason in target_reasons if reason["relation"] == "shared_entity")
    assert all(row["extraction"] == "heuristic" for row in shared["provenance"])
    assert all(row["locator"] for row in shared["provenance"])


def test_provenance_citations_and_locators_match_source_chunks(tmp_path):
    original = chunk(
        "stable-chunk",
        "UniqueSignal is evidence.",
        parent="stable-parent",
        source="original.md",
        heading="Original heading",
        locator="original.md#L7-L9",
        start_line=7,
        end_line=9,
        metadata={"revision": "frozen"},
    )
    result = GraphRAGChain(service(tmp_path, [original]), context_counter=len).retrieve(
        "UniqueSignal"
    )
    item = result["evidence"][0]
    assert item["citation_id"].startswith("E") and len(item["citation_id"]) == 25
    assert item["content"] == original.content
    assert item["truncated"] is False
    assert item["chunk_id"] == original.id
    for field in (
        "parent_id",
        "source",
        "locator",
        "start_line",
        "end_line",
        "metadata",
    ):
        assert item[field] == getattr(original, field)


def test_token_and_character_budgets_include_citation_locator_headers(tmp_path):
    first = chunk("first", "UniqueSignal first. " + "Long trailing text. " * 100)
    second = chunk("second", "UniqueSignal second evidence.", parent="second", line=2)
    retrieval = service(
        tmp_path,
        [first, second],
        context_tokens=70,
        context_chars=480,
    )

    def quadratic_count(text):
        # Deliberately disagree with len to ensure both independent limits are checked.
        return max(1, len(text) // 4)

    result = GraphRAGChain(
        retrieval, top_k=2, max_seed_hits=2, context_counter=quadratic_count
    ).retrieve("UniqueSignal")
    packed = next(step for step in result["trace"] if step["step"] == "evidence_pack")
    assert packed["used_tokens"] <= 70
    assert packed["used_characters"] <= 480
    assert result["evidence"]
    rendered = "\n\n".join(
        f"[{item['citation_id']}] {item['locator']}\nMemory\n{item['content']}"
        for item in result["evidence"]
    )
    assert len(rendered) == packed["used_characters"]
    assert quadratic_count(rendered) == packed["used_tokens"]
    assert any(item["truncated"] for item in result["evidence"])


def test_empty_base_retrieval_returns_no_evidence_or_expansion(tmp_path):
    retrieval = service(
        tmp_path,
        [chunk("a", "Known content.", domain="infra")],
    )
    result = GraphRAGChain(retrieval, context_counter=len).retrieve("Known", domain="missing")
    assert result["candidates"] == result["ranked"] == result["evidence"] == []
    assert (
        next(step for step in result["trace"] if step["step"] == "graph_expand")["expanded_count"]
        == 0
    )


def test_cache_invalidates_when_chunk_or_source_identity_changes(tmp_path):
    retrieval = service(tmp_path, [chunk("a", "UniqueSignal original.")])
    chain = GraphRAGChain(retrieval, context_counter=len)
    original = chain.retrieve("UniqueSignal")
    changed = replace(retrieval.chunks[0], content="UniqueSignal changed.")
    retrieval._commit([changed])
    after_change = chain.retrieve("UniqueSignal")
    assert graph_step(after_change)["graph_stats"]["cache_hit"] is False
    assert after_change["evidence"][0]["content"] == "UniqueSignal changed."
    retrieval.source_manifest = {changed.source: {"sha256": "new-source"}}
    after_manifest = chain.retrieve("UniqueSignal")
    assert graph_step(after_manifest)["graph_stats"]["cache_hit"] is False
    assert graph_step(original)["graph_stats"]["index_fingerprint"] == retrieval.index_fingerprint


def test_image_only_chunks_never_enter_text_graph_or_evidence(tmp_path):
    image = chunk(
        "image",
        "",
        modality="image",
        chunk_type="image",
        image_path="image.png",
    )
    retrieval = service(tmp_path, [image])
    result = GraphRAGChain(retrieval, context_counter=len).retrieve("anything")
    assert result["candidates"] == result["evidence"] == []
    assert graph_step(result)["graph_stats"]["text_nodes"] == 0
