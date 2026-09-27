from dataclasses import replace

import pytest

from infra_rag.chunking import chunk_text
from infra_rag.config import Settings
from infra_rag.encoding import DemoEncoder
from infra_rag.text_chunking import heading_line, semantic_refine


class TopicEncoder:
    def encode(self, texts, **kwargs):
        return [[1.0, 0.0] if "缓存" in text else [0.0, 1.0] for text in texts]


def test_plain_txt_heading_requires_isolated_noun_phrase():
    assert heading_line("张量并行", allow_plain=True) == "张量并行"
    assert heading_line("缓存保存历史结果。", allow_plain=True) is None
    assert heading_line("张量并行", allow_plain=False) is None
    chunks = chunk_text(
        "张量并行\n\n将模型张量分配到不同设备。", "a.txt", "training", DemoEncoder(), Settings()
    )
    assert chunks[0].heading == "张量并行"
    assert "将模型" in chunks[0].content


def test_semantic_refinement_breaks_at_topic_shift_and_preserves_punctuation():
    text = "缓存复用历史键值减少重复计算。" * 3 + "网络通过规约通信同步梯度。" * 6
    pieces = semantic_refine(text, 100, TopicEncoder(), 0.5)
    assert len(pieces) >= 2
    assert "网络" not in pieces[0]
    assert "缓存" not in pieces[1]
    assert "".join(pieces).replace("\n", "") == text


def test_model_token_limit_prevents_silent_document_truncation():
    class TinyEncoder(DemoEncoder):
        token_limit = 8

        def token_length(self, text):
            return len(text)

    pieces = semantic_refine("历史缓存键值复用避免重复计算。" * 15, 100, TinyEncoder(), 0.5)
    assert all(len(piece) <= 8 for piece in pieces)


def test_parent_lookup_is_rebuilt_on_replace_delete_and_restart(tmp_path):
    from infra_rag.service import RetrievalService

    service = RetrievalService(Settings(data_dir=tmp_path / "db", chunk_size=100))
    document = tmp_path / "cache.md"
    document.write_text("# KV Cache\n\n" + "缓存键值复用。" * 60)
    service.ingest(document)
    parent_id = service.chunks[-1].parent_id
    assert len(service.get_parent(parent_id)) > 1
    restored = RetrievalService(service.settings)
    assert [c.id for c in restored.get_parent(parent_id)] == [
        c.id for c in service.get_parent(parent_id)
    ]
    document.write_text("# NCCL\n\n通信同步梯度。")
    service.ingest(document)
    assert not service.get_parent(parent_id)
    new_parent = service.chunks[0].parent_id
    service.delete(str(document.resolve()))
    assert not service.get_parent(new_parent)


class VisualEncoder:
    def encode_images(self, paths):
        return [[1.0, 0.0] for path in paths]


def test_image_regions_preserve_geometry_and_parent(tmp_path):
    pytest.importorskip("cv2")
    from PIL import Image, ImageDraw

    from infra_rag.image_chunking import image_chunks

    image = Image.new("RGB", (600, 250), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 30, 200, 210), fill="blue", outline="black", width=3)
    draw.rectangle((400, 30, 580, 210), fill="red", outline="black", width=3)
    path = tmp_path / "panels.png"
    image.save(path)
    settings = Settings(data_dir=tmp_path / "db", image_max_side=128)
    chunks = image_chunks(
        path,
        str(path),
        "gpu",
        settings,
        VisualEncoder(),
        caption="Two GPU panels",
        caption_source="sidecar",
    )
    assert chunks[0].chunk_type == "figure"
    assert len(chunks) > 2
    assert len({chunk.parent_id for chunk in chunks}) == 1
    for chunk in chunks[1:]:
        x0, y0, x1, y1 = chunk.bbox
        assert 0 <= x0 < x1 <= 600 and 0 <= y0 < y1 <= 250
        assert x1 - x0 <= 128 and y1 - y0 <= 128
        with Image.open(chunk.image_path) as crop:
            assert crop.size == (x1 - x0, y1 - y0)
        assert chunk.visual_features["edge_density"] > 0


def test_visual_aggregation_requires_proximity():
    from infra_rag.image_chunking import aggregate_regions

    boxes = [[0, 0, 20, 20], [21, 0, 41, 20], [150, 0, 170, 20]]
    merged = aggregate_regions(boxes, [[1.0, 0.0]] * 3, (200, 100), 0.8)
    assert merged == [[0, 0, 41, 20], [150, 0, 170, 20]]


def test_pdf_caption_and_region_coordinates(tmp_path):
    fitz = pytest.importorskip("pymupdf")
    pytest.importorskip("cv2")
    from PIL import Image, ImageDraw

    from infra_rag.chunking import parse_file

    image = Image.new("RGB", (200, 100), "white")
    ImageDraw.Draw(image).rectangle((20, 20, 180, 80), outline="black", width=4)
    image_path = tmp_path / "diagram.png"
    image.save(image_path)
    pdf = tmp_path / "paper.pdf"
    with fitz.open() as document:
        page = document.new_page()
        page.insert_image(fitz.Rect(50, 50, 450, 250), filename=str(image_path))
        page.insert_text((50, 275), "Figure 1. GPU memory hierarchy")
        page.insert_text((50, 500), "Figure 9. Distant unrelated diagram")
        document.save(pdf)
    settings = Settings(data_dir=tmp_path / "db", backend="bge", multimodal=True)
    chunks = parse_file(pdf, "gpu", DemoEncoder(), settings, VisualEncoder())
    images = [c for c in chunks if c.modality == "image"]
    assert images and all(c.caption_source == "pdf_caption" for c in images)
    assert all("GPU memory hierarchy" in c.content and "Distant" not in c.content for c in images)
    assert images[0].bbox == [50, 50, 450, 250]
    for region in images:
        assert region.coordinate_space == "pdf_points"
        assert 50 <= region.bbox[0] < region.bbox[2] <= 450
        assert 50 <= region.bbox[1] < region.bbox[3] <= 250


def test_window_ablation_has_distinct_configuration():
    semantic = Settings()
    window = replace(semantic, chunk_strategy="window")
    assert semantic.fingerprint() != window.fingerprint()


def test_multimodal_accepts_image_only_pdf_without_claiming_ocr(tmp_path):
    fitz = pytest.importorskip("pymupdf")
    pytest.importorskip("cv2")
    from PIL import Image

    from infra_rag.chunking import parse_file

    path = tmp_path / "scan.png"
    Image.new("RGB", (80, 80), "blue").save(path)
    pdf = tmp_path / "scan.pdf"
    with fitz.open() as document:
        page = document.new_page()
        page.insert_image(fitz.Rect(20, 20, 100, 100), filename=str(path))
        document.save(pdf)
    settings = Settings(data_dir=tmp_path / "db", backend="bge", multimodal=True)
    chunks = parse_file(pdf, "gpu", DemoEncoder(), settings, VisualEncoder())
    assert chunks and all(c.modality == "image" and c.caption_source == "label" for c in chunks)
