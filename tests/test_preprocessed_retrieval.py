from dataclasses import replace

import pytest

from infra_rag.benchmarking import span_coverage
from infra_rag.config import Settings
from infra_rag.encoding import DemoEncoder
from infra_rag.models import Chunk, Hit
from infra_rag.offline_evaluation import resolve_evidence
from infra_rag.partitioned import PartitionedRetrieval, RoutedQuery, prefer_versions
from infra_rag.preprocessing import clean_lines, duplicate_audit, preprocess, split_unit, units
from infra_rag.service import RetrievalService


def chunk(cid, source, content, *, release="v0.10.2", product="vllm", collection="official"):
    return Chunk(
        id=cid,
        parent_id=cid,
        source=source,
        content=content,
        domain="infra",
        metadata={"release": release, "product": product, "collection": collection},
    )


def test_cleanup_preserves_code_negation_and_raw_lines():
    text = (
        "---\ntitle: demo\n---\n# 目录\n- link\n# CUDA\n不能假定异步。\n```python\nimport os\n```"
    )
    lines, changes = clean_lines(text)
    assert len(lines) == len(text.splitlines())
    assert lines[6] == "不能假定异步。"
    assert lines[8] == "import os"
    assert lines[:5] == [""] * 5
    assert changes


def test_tables_keep_headers_and_code_fences_are_balanced():
    encoder = DemoEncoder()
    table = {
        "kind": "table",
        "content": "| name | meaning |\n|---|---|\n"
        + "\n".join(f"| row{i} | condition is not guaranteed {i} |" for i in range(8)),
    }
    pieces = split_unit(table, encoder, 100)
    assert len(pieces) > 1
    assert all(piece.startswith("| name | meaning |\n|---|---|") for piece in pieces)
    assert all(f"row{i}" in "\n".join(pieces) for i in range(8))
    code = {
        "kind": "code",
        "content": "```python\n" + "\n".join('print("x")' for _ in range(20)) + "\n```",
    }
    assert all(
        p.startswith("```python\n") and p.endswith("\n```") for p in split_unit(code, encoder, 100)
    )


def test_structural_mapping_keeps_distinct_ids_and_code_description():
    text = (
        "# CUDA\n\n如果内存未锁页，Async调用不保证异步。\n\n"
        "```c\ncudaMemcpyAsync();\n```\n\n重复说明。\n\n重复说明。"
    )
    parsed, audit = preprocess(text, "/source.md", {}, DemoEncoder(), Settings(chunk_size=100))
    assert len({c.id for c in parsed}) == len(parsed)
    assert audit["line_map"] == list(range(1, len(text.splitlines()) + 1))
    code = next(c for c in parsed if c.chunk_type == "code")
    assert code.metadata["description_lines"] == [3, 3]
    assert code.start_line == 5
    assert units(clean_lines(text)[0])[1]["kind"] == "condition"


def test_duplicate_versions_unknown_versions_and_negations_are_not_merged():
    text = "This version supports a documented cache key and not any other identity. " * 2
    items = [
        chunk("a", "a.md", text),
        chunk("copy", "b.md", text),
        chunk("old", "old.md", text, release="v0.9.0"),
        chunk("unknown1", "u1.md", text, release=None),
        chunk("unknown2", "u2.md", text, release=None),
        chunk("negation", "n.md", text.replace("not", "only")),
    ]
    kept, audit = duplicate_audit(items)
    assert [c.id for c in kept] == ["a", "old", "unknown1", "unknown2", "negation"]
    assert audit["exact_aliases"][0]["canonical_id"] == "a"
    assert kept[0].metadata["source_aliases"][0]["source"] == "b.md"
    q = {
        "id": "q",
        "answerable": True,
        "evidence_alternatives": [
            {"spans": [{"absolute_source": "b.md", "text": text, "document_id": "b"}]}
        ],
    }
    service = type("Service", (), {"chunks": kept})()
    assert resolve_evidence(service, [q])["q"]["relevant"] == ["a"]
    assert (
        span_coverage([{"source": "a.md", "content": text, "metadata": kept[0].metadata}], q)[
            "complete"
        ]
        == 1
    )


def test_version_preference_is_bounded_and_has_no_unqualified_fallback():
    hits = [Hit(chunk(str(i), f"{i}.md", "cache", collection="community"), 1) for i in range(12)]
    hits[6] = Hit(chunk("official", "official.md", "cache"), 1)
    selected, info = prefer_versions(hits, "vLLM v0.10.2 缓存", 5, True)
    assert selected[0].chunk.id == "official"
    assert info["protected_ids"] == ["official"]
    assert len(selected) == 5
    selected, info = prefer_versions(hits, "vLLM v0.9.0 缓存", 5, True)
    assert [h.chunk.id for h in selected] == ["0", "1", "2", "3", "4"]
    assert info["missing_version_evidence"]
    hits[6].chunk.metadata["collection"] = "community"
    assert prefer_versions(hits, "vLLM v0.10.2 缓存", 5, True)[1]["protected_ids"] == []


def test_partition_quotas_language_routes_and_snapshot_reload(tmp_path):
    config = Settings(data_dir=tmp_path / "base", candidate_k=30)
    base = RetrievalService(config)
    originals = [chunk(f"o{i}", "official.md", f"cache hash english {i}") for i in range(40)]
    communities = [
        chunk(f"c{i}", "community.md", f"中文缓存说明 {i}", collection="community")
        for i in range(40)
    ]
    base._commit(originals + communities)
    banks = {}
    for name, data in [("official", originals), ("community", communities)]:
        bank = RetrievalService(replace(config, data_dir=tmp_path / name))
        bank._commit(data)
        banks[name] = RetrievalService(bank.settings)
    base = RetrievalService(config)
    wrapper = PartitionedRetrieval(base, banks, language_route=True)
    diagnostics, context = {}, {}
    hits = wrapper.search(
        RoutedQuery("中文缓存说明", "cache hash english"),
        strategy="bm25",
        diagnostics=diagnostics,
        context_pack=context,
    )
    assert hits
    assert diagnostics["banks"]["official"]["query"] == "cache hash english"
    assert diagnostics["banks"]["community"]["query"] == "中文缓存说明"
    assert len(diagnostics["banks"]["official"]["candidates"]) == 30
    assert len(diagnostics["banks"]["community"]["candidates"]) == 30
    assert len(diagnostics["candidates"]) == 60
    assert context["evidence"][0]["metadata"]["collection"] in {"official", "community"}

    class Reranker:
        def predict(self, pairs):
            self.pairs = pairs
            return [0.5] * len(pairs)

    base.settings = replace(base.settings, rerank=True)
    base.reranker = Reranker()
    wrapper.search(RoutedQuery("中文缓存说明", "cache hash english"), strategy="bm25")
    assert len(base.reranker.pairs) == 60
    assert all(
        query == ("中文缓存说明" if "中文" in text else "cache hash english")
        for query, text in base.reranker.pairs
    )
    with pytest.raises(ValueError, match="Frozen"):
        wrapper.ingest(tmp_path)
    with pytest.raises(ValueError, match="Frozen"):
        wrapper.delete("official.md")


def test_preprocessing_fingerprint_requires_separate_index(tmp_path):
    old = Settings(data_dir=tmp_path)
    RetrievalService(old)._commit([chunk("a", "a.md", "cache")])
    assert "preprocessing_version" not in old.fingerprint()
    with pytest.raises(ValueError, match="configuration mismatch"):
        RetrievalService(replace(old, preprocessing_version="v2"))
