import importlib.util
import json
from pathlib import Path

from infra_rag.config import Settings
from infra_rag.models import Chunk
from infra_rag.service import RetrievalService

spec = importlib.util.spec_from_file_location(
    "merge_corpus", Path(__file__).resolve().parents[1] / "scripts/merge_corpus.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def make_chunk(cid, source, content):
    return Chunk(id=cid, parent_id=cid, source=source, content=content, domain="infra")


def test_exact_cross_source_dedup_preserves_official_id_and_version_difference():
    text = "PagedAttention stores KV cache in noncontiguous physical blocks. " * 3
    chunks = [
        make_chunk("official", "official.md", text),
        make_chunk("copy", "community.md", text),
        make_chunk("version", "old.md", text.replace("noncontiguous", "contiguous")),
        make_chunk("short1", "a.md", "KV cache"),
        make_chunk("short2", "b.md", "KV cache"),
    ]
    kept, vectors, aliases = module.deduplicate(chunks, [[i] for i in range(5)])
    assert [c.id for c in kept] == ["official", "version", "short1", "short2"]
    assert vectors == [[0], [2], [3], [4]]
    assert aliases[0]["removed_id"] == "copy"
    assert aliases[0]["canonical_id"] == "official"
    assert aliases[0]["source"] == "community.md"


def test_provenance_survives_index_reload_and_is_returned_with_evidence(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("# KV Cache\n\nPagedAttention stores KV cache in physical blocks.")
    config = Settings(data_dir=tmp_path / "index")
    service = RetrievalService(config)
    service.ingest(source, "infra")
    provenance = {
        str(source.resolve()): {
            "collection": "official",
            "commit": "frozen-commit",
            "url": "https://example.org/frozen-document",
        }
    }
    (config.data_dir / "provenance.json").write_text(json.dumps({"sources": provenance}))
    reloaded = module.ProvenanceRetrieval(config)
    context = {}
    hits = reloaded.search("KV cache", strategy="bm25", context_pack=context)
    assert hits
    assert context["evidence"][0]["provenance"]["commit"] == "frozen-commit"
    assert hits[0].evidence[0]["provenance"]["url"] == provenance[str(source)]["url"]
