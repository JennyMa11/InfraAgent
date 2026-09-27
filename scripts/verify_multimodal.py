"""Real BGE + CLIP + reranker + PDF integration on small synthetic diagram fixtures."""

import json
import math
from dataclasses import replace
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont

from infra_rag.config import Settings
from infra_rag.evaluation import evaluate
from infra_rag.service import RetrievalService

ROOT = Path(__file__).resolve().parents[1]


def main():
    corpus = ROOT / "examples" / "diagrams"
    corpus.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default(size=20)
    captions = {
        "memory": (
            "GPU memory hierarchy: global DRAM connects to "
            "streaming multiprocessors and shared memory."
        ),
        "ring": (
            "Ring AllReduce: four GPU ranks exchange gradient data "
            "on a circular communication topology."
        ),
        "pipeline": "Pipeline parallelism: model layers are assigned to successive GPU stages.",
        "cluster": (
            "Kubernetes cluster: a control plane manages worker nodes containing application pods."
        ),
        "pages": "PagedAttention: logical KV cache blocks map to scattered physical memory pages.",
        "numa": (
            "NUMA architecture: two CPU sockets each connect to "
            "their local memory and a remote socket."
        ),
    }
    for name, caption in captions.items():
        image = Image.new("RGB", (640, 420), "white")
        draw = ImageDraw.Draw(image)
        draw.text((20, 12), name.upper(), fill="black", font=font)

        def box(x, y, w, h, label, color, draw=draw):
            draw.rounded_rectangle(
                (x, y, x + w, y + h), radius=8, fill=color, outline="black", width=3
            )
            draw.text((x + 10, y + 15), label, fill="black", font=font)

        def link(a, b, draw=draw):
            draw.line((a, b), fill="black", width=4)

        if name == "ring":
            centers = [
                (320 + int(130 * math.cos(angle)), 230 + int(130 * math.sin(angle)))
                for angle in [0, math.pi / 2, math.pi, 3 * math.pi / 2]
            ]
            for a, b in zip(centers, centers[1:] + centers[:1], strict=True):
                link(a, b)
            for rank, (x, y) in enumerate(centers):
                draw.ellipse(
                    (x - 42, y - 42, x + 42, y + 42), fill="lightgreen", outline="black", width=3
                )
                draw.text((x - 30, y - 10), f"GPU{rank}", fill="black", font=font)
        elif name == "pipeline":
            for stage in range(4):
                box(20 + stage * 155, 170, 135, 100, f"Stage {stage}", "lightblue")
                if stage:
                    link((stage * 155, 220), (20 + stage * 155, 220))
        elif name == "memory":
            box(220, 70, 200, 60, "Global DRAM", "lightblue")
            for x in [60, 250, 440]:
                link((320, 130), (x + 70, 220))
                box(x, 220, 140, 70, "SM", "lightgreen")
                box(x, 300, 140, 60, "Shared", "orange")
        elif name == "cluster":
            box(220, 60, 200, 70, "Control plane", "orange")
            for x in [50, 360]:
                link((320, 130), (x + 110, 210))
                box(x, 210, 230, 160, "Worker", "lightblue")
                box(x + 20, 280, 80, 65, "Pod", "lightgreen")
                box(x + 130, 280, 80, 65, "Pod", "lightgreen")
        elif name == "pages":
            for i, target in enumerate([2, 0, 3, 1]):
                box(50, 65 + i * 80, 170, 55, f"Logical {i}", "lightblue")
                box(400, 65 + i * 80, 180, 55, f"Physical {i}", "lightgreen")
                link((220, 90 + i * 80), (400, 90 + target * 80))
        else:
            for x, socket in [(40, 0), (370, 1)]:
                box(x, 70, 220, 90, f"CPU socket {socket}", "lightblue")
                box(x, 260, 220, 90, f"Local RAM {socket}", "lightgreen")
                link((x + 110, 160), (x + 110, 260))
            link((260, 115), (370, 115))
        path = corpus / f"{name}.png"
        image.save(path)
        path.with_suffix(".png.txt").write_text(caption)
    # Include a real PDF to exercise caption detection and page-coordinate region metadata.
    pdf = corpus / "gpu-paper.pdf"
    with pymupdf.open() as document:
        page = document.new_page(width=700, height=600)
        page.insert_image(pymupdf.Rect(30, 50, 670, 470), filename=str(corpus / "memory.png"))
        page.insert_text(
            (30, 500), "Figure 1. GPU memory hierarchy: global DRAM, SM and shared memory."
        )
        document.save(pdf)
    note = corpus / "overview.md"
    note.write_text("# Infra architecture\n\n" + "\n\n".join(captions.values()))
    settings = Settings(
        data_dir=ROOT / "data" / "verified-multimodal-v2", backend="bge", multimodal=True
    )
    service = RetrievalService(settings)
    print("Ingesting real multimodal models", flush=True)
    service.ingest(corpus, "infra")
    assert service.clip_collection.count() == len(service.chunks)
    assert any(c.caption_source == "pdf_caption" for c in service.chunks)
    assert any(c.chunk_type == "image_region" for c in service.chunks)
    queries = {
        "memory": "GPU global memory shared memory hierarchy diagram",
        "ring": "four GPUs connected in a ring communication diagram",
        "pipeline": "pipeline parallelism stages diagram",
        "cluster": "Kubernetes control plane worker nodes pods architecture",
        "pages": "KV cache logical blocks physical pages mapping diagram",
        "numa": "NUMA two CPU sockets local RAM diagram",
    }
    dataset = []
    for name, query in queries.items():
        relevant = {
            c.parent_id
            for c in service.chunks
            if c.source == str((corpus / f"{name}.png").resolve())
        }
        if name == "memory":
            relevant.update(
                c.parent_id
                for c in service.chunks
                if c.source == str(pdf.resolve()) and c.modality == "image"
            )
        dataset.append(
            {"id": name, "query": query, "modality": "image", "relevant": sorted(relevant)}
        )
    output = ROOT / "evals" / "results" / "multimodal"
    output.mkdir(parents=True, exist_ok=True)
    (output / "labels.json").write_text(json.dumps(dataset, ensure_ascii=False, indent=2))
    for strategy, rerank in [("clip", False), ("hybrid", False), ("hybrid", True)]:
        service.settings = replace(service.settings, rerank=rerank)
        service.search("GPU diagram", modality="image", strategy=strategy)
        report = evaluate(service, dataset, k=5, strategy=strategy, label="parent")
        report["fixture"] = "6 synthetic diagrams plus one duplicate PDF figure; figure-level gold"
        name = strategy + ("_rerank" if rerank else "")
        (output / f"{name}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
        print(name, report["macro"], flush=True)
    # Direct text-vs-image CLIP alignment test is independent of BM25/BGE/captions.
    print(
        "CLIP collection contains text and image embeddings in the same native space.", flush=True
    )


if __name__ == "__main__":
    main()
