"""Real storage/parser integration; encoders are explicitly deterministic test doubles."""

import pytest

from infra_rag.config import Settings
from infra_rag.encoding import DemoEncoder
from infra_rag.service import RetrievalService


def test_real_chroma_lifecycle_with_test_encoder(tmp_path):
    pytest.importorskip("chromadb")
    service = RetrievalService(Settings(data_dir=tmp_path / "db", backend="bge"))
    service.encoder = DemoEncoder()
    document = tmp_path / "cache.md"
    document.write_text("# KV Cache\n\nPagedAttention reduces fragmentation.")
    service.ingest(document, "inference")
    assert service.text_collection.count() == len(service.chunks)
    assert service.search("PagedAttention", domain="inference", strategy="dense")
    assert not service.search("PagedAttention", domain="network", strategy="dense")
    restored = RetrievalService(service.settings)
    restored.encoder = DemoEncoder()
    assert restored.search("PagedAttention", strategy="dense")
    document.write_text("# NCCL\n\nAllReduce gradient synchronization.")
    previous_ids = {c.id for c in service.chunks}
    service.ingest(document, "training")
    assert not previous_ids.intersection(c.id for c in service.chunks)
    assert service.search("AllReduce", strategy="dense")[0].chunk.domain == "training"
    service.delete(str(document.resolve()))
    assert service.text_collection.count() == 0


def test_real_pdf_text_and_scan_rejection(tmp_path):
    fitz = pytest.importorskip("pymupdf")
    file = tmp_path / "paper.pdf"
    with fitz.open() as document:
        page = document.new_page()
        page.insert_text((72, 72), "PagedAttention KV Cache fragmentation")
        document.save(file)
    service = RetrievalService(Settings(data_dir=tmp_path / "db"))
    service.ingest(file, "inference")
    hit = service.search("PagedAttention")[0]
    assert hit.chunk.page == 1
    assert hit.chunk.locator.endswith("#page=1")
    empty = tmp_path / "scan.pdf"
    with fitz.open() as document:
        document.new_page()
        document.save(empty)
    with pytest.raises(ValueError, match="OCR"):
        service.ingest(empty)
    assert len(service.chunks) == 1


def test_clip_collection_and_caption_fusion_with_test_encoder(tmp_path):
    pytest.importorskip("chromadb")
    image_module = pytest.importorskip("PIL.Image")
    settings = Settings(data_dir=tmp_path / "db", backend="bge", multimodal=True)
    service = RetrievalService(settings)
    service.encoder = DemoEncoder()

    class TestCLIP:
        def encode_images(self, paths):
            return [[1.0, 0.0] for path in paths]

        def encode_query(self, query):
            return [[1.0, 0.0]]

        def encode_texts(self, texts):
            return [[1.0, 0.0] for text in texts]

    service.clip = TestCLIP()
    image = tmp_path / "gpu.png"
    image_module.new("RGB", (20, 20), "blue").save(image)
    image.with_suffix(".png.txt").write_text("GPU architecture memory hierarchy")
    result = service.ingest(tmp_path, "gpu")
    assert result["files"] == 1  # caption sidecars are not separate knowledge sources
    hit = service.search("GPU architecture", modality="image", top_k=1)[0]
    assert set(hit.channels) == {"bm25", "dense", "clip"}
    assert image_module.open(hit.chunk.image_path).size == (20, 20)
    assert hit.chunk.caption_source == "sidecar"
    assert not service.search("GPU", modality="text")


def test_chroma_cleanup_keeps_active_and_unrelated_collections(tmp_path):
    chroma = pytest.importorskip("chromadb")
    service = RetrievalService(Settings(data_dir=tmp_path / "db", backend="bge"))
    service.encoder = DemoEncoder()
    document = tmp_path / "a.md"
    document.write_text("Original evidence.")
    service.ingest(document)
    original = service.text_collection.name
    service.client.get_or_create_collection("unrelated-user-collection")
    document.write_text("Updated evidence.")
    service.ingest(document)
    active = service.text_collection.name
    preview = service.cleanup()
    assert preview["collections"] == [original]
    assert service.client.get_collection(original).count() == 1
    service.cleanup(apply=True)
    assert service.client.get_collection(active).count() == 1
    assert service.client.get_collection("unrelated-user-collection") is not None
    with pytest.raises(chroma.errors.NotFoundError):
        service.client.get_collection(original)
    restored = RetrievalService(service.settings)
    restored.encoder = DemoEncoder()
    assert restored.search("Updated", strategy="dense")


def test_sidecar_change_invalidates_source_but_reuses_clip_pixels(tmp_path):
    pytest.importorskip("chromadb")
    image_module = pytest.importorskip("PIL.Image")
    settings = Settings(data_dir=tmp_path / "db", backend="bge", multimodal=True)
    service = RetrievalService(settings)
    service.encoder = DemoEncoder()

    class Clip:
        def encode_images(self, paths):
            return [[1.0, 0.0] for _ in paths]

        def encode_texts(self, texts):
            return [[0.0, 1.0] for _ in texts]

    service.clip = Clip()
    image = tmp_path / "diagram.PNG"
    image_module.new("RGB", (20, 20), "blue").save(image)
    caption = image.with_suffix(".PNG.txt")
    caption.write_text("OriginalArchitecture")
    assert service.ingest(tmp_path)["files"] == 1
    restored = RetrievalService(settings)
    restored.encoder, restored.clip = DemoEncoder(), Clip()
    assert restored.ingest(tmp_path)["skipped_files"] == 1
    caption.write_text("ChangedArchitecture")
    result = restored.ingest(tmp_path)
    assert result["files"] == 1 and result["changed_files"] == 1
    assert result["vectors"]["clip_vectors"]["encoded"] == 0
    assert not restored.search("OriginalArchitecture", strategy="bm25")
    assert restored.search("ChangedArchitecture", strategy="bm25")
