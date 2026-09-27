"""Incremental ingestion preserves provenance, publication and encoding semantics."""

import json
from dataclasses import replace
from pathlib import Path

import pytest

from infra_rag.config import Settings
from infra_rag.encoding import DemoEncoder
from infra_rag.models import Chunk
from infra_rag.service import RetrievalService
from infra_rag.vector_cache import VectorCache


class CountingEncoder(DemoEncoder):
    def __init__(self):
        self.inputs = []

    def encode(self, texts, **kwargs):
        self.inputs.extend(texts)
        return super().encode(texts, **kwargs)


def test_incremental_skip_restart_change_and_delete(tmp_path, monkeypatch):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    first, second = corpus / "first.md", corpus / "second.md"
    first.write_text("# Cache\n\nPagedAttention reduces fragmentation.")
    second.write_text("# Training\n\nAllReduce synchronizes gradients.")
    service = RetrievalService(Settings(data_dir=tmp_path / "index"))
    service.encoder = CountingEncoder()
    service.ingest(corpus, "infra")
    second_id = next(c.id for c in service.chunks if c.source == str(second.resolve()))
    old_snapshot = service.snapshot.read_bytes()
    restored = RetrievalService(service.settings)
    restored.encoder = CountingEncoder()
    parse = __import__("infra_rag.service", fromlist=["parse_file"]).parse_file
    parsed = []

    def counted_parse(path, *args, **kwargs):
        parsed.append(path)
        return parse(path, *args, **kwargs)

    monkeypatch.setattr("infra_rag.service.parse_file", counted_parse)
    result = restored.ingest(corpus, "infra")
    assert result["skipped_files"] == 2 and not parsed and not restored.encoder.inputs
    assert restored.snapshot.read_bytes() == old_snapshot
    first.write_text("# Cache\n\nContinuousBatching schedules requests.")
    result = restored.ingest(corpus, "infra")
    assert parsed == [first] and result["changed_files"] == 1
    assert result["vectors"]["text_vectors"] == {"encoded": 1, "reused": 1}
    assert result["vectors"]["parsing_text_vectors"]["encoded"] == 1
    assert second_id in {c.id for c in restored.chunks}
    assert "AllReduce synchronizes gradients." not in restored.encoder.inputs
    assert restored.search("ContinuousBatching", strategy="bm25")
    assert not restored.search("PagedAttention", strategy="bm25")
    restored.encoder.inputs.clear()
    restored.delete(str(first.resolve()))
    assert not restored.encoder.inputs
    assert str(first.resolve()) not in RetrievalService(service.settings).source_manifest
    assert RetrievalService(service.settings).search("AllReduce", strategy="bm25")


def test_domain_change_reuses_vectors_and_replaces_metadata(tmp_path):
    file = tmp_path / "a.md"
    file.write_text("# Cache\n\nPagedAttention cache.")
    service = RetrievalService(Settings(data_dir=tmp_path / "index"))
    service.ingest(file, "old")
    result = service.ingest(file, "new")
    assert result["changed_files"] == 1
    assert result["vectors"]["text_vectors"] == {"encoded": 0, "reused": 1}
    assert not service.search("cache", domain="old")
    assert service.search("cache", domain="new")


def test_cache_survives_restart_and_separates_namespaces(tmp_path):
    cache = VectorCache(tmp_path / "vectors.sqlite3")
    first, counts = cache.encode({"model": "a"}, ["same", "same"], lambda texts: [[1.0]])
    assert first == [[1.0], [1.0]] and counts["encoded"] == 1
    restored = VectorCache(cache.path)

    def unexpected(texts):
        raise AssertionError("cached vectors should not be encoded again")

    assert restored.encode({"model": "a"}, ["same"], unexpected)[0] == [[1.0]]
    assert restored.encode({"model": "b"}, ["same"], lambda texts: [[2.0]])[0] == [[2.0]]
    with pytest.raises(ValueError, match="count"):
        restored.encode({"model": "c"}, ["same"], lambda texts: [])
    with pytest.raises(ValueError, match="invalid"):
        restored.encode({"model": "c"}, ["same"], lambda texts: [[float("nan")]])


def test_old_snapshot_reuses_existing_vectors_without_reencoding(tmp_path):
    service = RetrievalService(Settings(data_dir=tmp_path / "index"))
    first, second = tmp_path / "a.md", tmp_path / "b.md"
    first.write_text("Existing content.")
    service.ingest(first)
    state = json.loads(service.snapshot.read_text())
    state.pop("sources")
    service.snapshot.write_text(json.dumps(state))
    service.vector_cache.path.unlink()
    restored = RetrievalService(service.settings)
    restored.encoder = CountingEncoder()
    second.write_text("Additional content.")
    result = restored.ingest(second)
    assert "Existing content." not in restored.encoder.inputs
    assert result["vectors"]["text_vectors"]["reused"] == 2


def test_publication_failure_leaves_manifest_and_index_unchanged(tmp_path, monkeypatch):
    file = tmp_path / "a.md"
    file.write_text("Old evidence.")
    service = RetrievalService(Settings(data_dir=tmp_path / "index"))
    service.ingest(file)
    snapshot = service.snapshot.read_bytes()
    manifest = dict(service.source_manifest)
    file.write_text("New evidence.")

    def fail_publish(*args):
        raise OSError("publication failed")

    with monkeypatch.context() as patch:
        patch.setattr("infra_rag.service.os.replace", fail_publish)
        with pytest.raises(OSError, match="publication"):
            service.ingest(file)
    assert service.snapshot.read_bytes() == snapshot
    assert service.source_manifest == manifest
    assert service.chunks[0].content == "Old evidence."
    assert service.ingest(file)["changed_files"] == 1
    assert RetrievalService(service.settings).chunks[0].content == "New evidence."


def test_cleanup_preview_apply_protects_active_and_foreign_assets(tmp_path):
    service = RetrievalService(Settings(data_dir=tmp_path / "index"))
    file = tmp_path / "a.md"
    file.write_text("Old evidence.")
    service.ingest(file)
    file.write_text("New evidence.")
    service.ingest(file)
    assets = service.settings.data_dir / "assets"
    assets.mkdir()
    orphan = assets / ("a" * 24 + ".png")
    orphan.write_bytes(b"unused")
    active = assets / ("b" * 24 + ".png")
    active.write_bytes(b"active")
    foreign = assets / "my-image.png"
    foreign.write_bytes(b"foreign")
    chunk = replace(service.chunks[0], image_path=str(active))
    service._commit([chunk])
    preview = service.cleanup()
    assert not preview["applied"] and preview["assets"] == [str(orphan)]
    assert preview["cache"]["unused"] == 1 and orphan.exists()
    service.cleanup(apply=True)
    assert not orphan.exists() and active.exists() and foreign.exists()
    assert service.cleanup()["cache"]["unused"] == 0
    assert RetrievalService(service.settings).search("New", strategy="bm25")


def test_cleanup_rejects_stale_service(tmp_path):
    settings = Settings(data_dir=tmp_path / "index")
    service = RetrievalService(settings)
    file = tmp_path / "a.md"
    file.write_text("Old evidence.")
    service.ingest(file)
    other = RetrievalService(settings)
    file.write_text("New evidence.")
    other.ingest(file)
    with pytest.raises(ValueError, match="restart"):
        service.cleanup(apply=True)


def test_clip_cache_uses_pixels_not_path_and_distinguishes_text(tmp_path):
    settings = Settings(data_dir=tmp_path / "index", backend="bge", multimodal=True)
    service = RetrievalService(settings)
    image = tmp_path / "image.png"
    image.write_bytes(b"pixels1")

    class Clip:
        calls = []

        def encode_images(self, paths):
            self.calls.append(list(paths))
            return [[float(len(p.read_bytes())), 0.0] for p in map(Path, paths)]

        def encode_texts(self, texts):
            return [[1.0, 2.0] for _ in texts]

    service.clip = Clip()
    chunks = [Chunk("a", "p", "s", "caption", "gpu", modality="image", image_path=str(image))]
    first = service._clip_vectors(chunks)
    assert first["a"] == [7.0, 0.0]
    service._clip_vectors(chunks)
    assert len(service.clip.calls) == 1
    image.write_bytes(b"different pixels")
    assert service._clip_vectors(chunks)["a"] != first["a"]
    assert len(service.clip.calls) == 2


def test_unchanged_ingest_and_deletion_need_no_model_load(tmp_path, monkeypatch):
    file, second = tmp_path / "a.md", tmp_path / "b.md"
    file.write_text("First evidence.")
    second.write_text("Second evidence.")
    service = RetrievalService(Settings(data_dir=tmp_path / "index"))
    service.ingest(file)
    service.ingest(second)
    restored = RetrievalService(service.settings)

    def unexpected_model_load():
        raise AssertionError("unchanged source or cached deletion should not load a model")

    monkeypatch.setattr(restored, "_encoder", unexpected_model_load)
    assert restored.ingest(file)["skipped_files"] == 1
    assert restored.delete(str(file.resolve())) == 1
    assert restored.last_update["text_vectors"]["encoded"] == 0


def test_model_change_cannot_seed_vectors_from_old_index(tmp_path):
    service = RetrievalService(Settings(data_dir=tmp_path / "index"))
    file = tmp_path / "a.md"
    file.write_text("Evidence.")
    service.ingest(file)
    original = service.snapshot.read_bytes()
    service.settings = replace(service.settings, embedding_model="different-model")
    with pytest.raises(ValueError, match="mismatch"):
        service.ingest(file)
    assert service.snapshot.read_bytes() == original


def test_source_change_during_parse_does_not_publish(tmp_path, monkeypatch):
    service = RetrievalService(Settings(data_dir=tmp_path / "index"))
    file = tmp_path / "a.md"
    file.write_text("Old evidence.")
    service.ingest(file)
    original = service.snapshot.read_bytes()
    file.write_text("Incoming evidence.")
    from infra_rag.service import parse_file

    def changing_parse(path, *args, **kwargs):
        chunks = parse_file(path, *args, **kwargs)
        path.write_text("Changed concurrently.")
        return chunks

    monkeypatch.setattr("infra_rag.service.parse_file", changing_parse)
    with pytest.raises(ValueError, match="changed during"):
        service.ingest(file)
    assert service.snapshot.read_bytes() == original
    assert service.chunks[0].content == "Old evidence."
