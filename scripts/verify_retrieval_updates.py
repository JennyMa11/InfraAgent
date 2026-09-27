"""Verify incremental updates and context packing on an isolated synthetic corpus.

Real mode executes actual BGE/Chroma, with optional CLIP and reranker. It does not
measure retrieval accuracy or modify existing indexes/datasets/benchmark reports.
"""

import argparse
import json
import platform
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from operation_log import record_operation

from infra_rag.config import Settings
from infra_rag.encoding import BGEEncoder, DemoEncoder
from infra_rag.service import RetrievalService
from infra_rag.vector_cache import content_hash


def timed_ingest(service, path):
    start = perf_counter()
    result = service.ingest(path, "infra")
    return {"elapsed_ms": (perf_counter() - start) * 1000, **result}


def run(backend, multimodal):
    encoder = BGEEncoder("BAAI/bge-small-zh-v1.5") if backend == "bge" else DemoEncoder()
    with TemporaryDirectory(prefix="infra-updates-") as temporary:
        root = Path(temporary)
        corpus = root / "corpus"
        corpus.mkdir()
        for i in range(8):
            (corpus / f"doc-{i}.md").write_text(
                f"# KV Cache {i}\n\nPagedAttention 使用分页管理键值缓存，减少显存碎片。\n\n"
                f"# Training {i}\n\nDDP 使用梯度桶和 AllReduce 同步梯度，实现计算通信重叠。",
                encoding="utf-8",
            )
        settings = Settings(data_dir=root / "incremental", backend=backend, multimodal=multimodal)
        service = RetrievalService(settings)
        service.encoder = encoder
        cold = timed_ingest(service, corpus)
        initial_ids = [c.id for c in service.chunks]
        snapshot = service.snapshot.read_bytes()
        unchanged = timed_ingest(service, corpus)
        assert unchanged["changed_files"] == 0 and unchanged["skipped_files"] == 8
        assert snapshot == service.snapshot.read_bytes()
        modified = corpus / "doc-0.md"
        modified.write_text(
            modified.read_text() + "\n\n# Continuous batching\n\n连续批处理在迭代间动态加入请求。",
            encoding="utf-8",
        )
        update = timed_ingest(service, corpus)
        assert update["changed_files"] == 1 and update["skipped_files"] == 7
        fresh = RetrievalService(replace(settings, data_dir=root / "rebuild"))
        fresh.encoder = encoder
        fresh.clip = service.clip
        rebuilt = timed_ingest(fresh, corpus)
        left = {c.id: v for c, v in zip(service.chunks, service.vectors, strict=True)}
        right = {c.id: v for c, v in zip(fresh.chunks, fresh.vectors, strict=True)}
        assert left.keys() == right.keys()
        error = max(abs(a - b) for cid in left for a, b in zip(left[cid], right[cid], strict=True))
        assert error < 1e-6
        trace, context = {}, {}
        query = "PagedAttention 如何减少 KV Cache 显存碎片？"
        hits = service.search(query, top_k=5, diagnostics=trace, context_pack=context)
        reference = fresh.search(query, top_k=5)
        assert [h.chunk.id for h in hits] == [h.chunk.id for h in reference]
        assert context["used_tokens"] <= settings.context_tokens
        assert context["used_characters"] <= settings.context_chars
        assert len({e["chunk_id"] for e in context["evidence"]}) == len(context["evidence"])
        restored = RetrievalService(settings)
        restored.encoder = encoder
        restored.clip = service.clip
        assert restored.ingest(corpus, "infra")["skipped_files"] == 8
        assert [h.chunk.id for h in restored.search(query)] == [h.chunk.id for h in hits]
        multimodal_report = None
        if multimodal:
            from PIL import Image, ImageDraw

            image = corpus / "memory.png"
            canvas = Image.new("RGB", (300, 180), "white")
            ImageDraw.Draw(canvas).rectangle((20, 30, 280, 150), fill="lightblue", outline="black")
            canvas.save(image)
            sidecar = image.with_suffix(".png.txt")
            sidecar.write_text("GPUArchitecture memory hierarchy")
            image_initial = timed_ingest(service, image)
            sidecar.write_text("UpdatedArchitecture GPU shared memory")
            image_updated = timed_ingest(service, image)
            assert image_updated["vectors"]["clip_vectors"]["encoded"] == 0
            assert service.search("UpdatedArchitecture", modality="image", strategy="bm25")
            image_trace = {}
            assert service.search("GPU memory", modality="image", diagnostics=image_trace)
            assert image_trace["channels"]["clip"]["score_kind"] == "cosine_distance"
            multimodal_report = {"initial": image_initial, "sidecar_update": image_updated}
        rerank_report = None
        if backend == "bge":
            service.settings = replace(settings, rerank=True)
            rerank_trace = {}
            service.search(query, diagnostics=rerank_trace)
            assert rerank_trace["rerank"]["enabled"]
            assert rerank_trace["rerank"]["pairs"]
            long_trace = {}
            service.search("长查询背景。" * 120 + query, diagnostics=long_trace)
            assert any(pair["would_truncate"] for pair in long_trace["rerank"]["pairs"])
            assert long_trace["dense_query"]["windows"] > 1
            rerank_report = {
                "short_query": rerank_trace["rerank"],
                "long_query": long_trace["rerank"],
                "long_dense_query": long_trace["dense_query"],
            }
            service.settings = settings
        preview = service.cleanup()
        applied = service.cleanup(apply=True)
        assert preview["collections"] == applied["collections"]
        assert service.search(query)
        deletion_source = str((corpus / "doc-1.md").resolve())
        service.delete(deletion_source)
        assert service.last_update["text_vectors"]["encoded"] == 0
        assert all(c.source != deletion_source for c in RetrievalService(settings).chunks)
        return {
            "code_hashes": {
                str(p.relative_to(Path(__file__).resolve().parents[1])): content_hash(p)
                for p in [Path(__file__).resolve()]
                + sorted((Path(__file__).resolve().parents[1] / "src/infra_rag").glob("*.py"))
            },
            "backend": backend,
            "multimodal": multimodal,
            "python": platform.python_version(),
            "fixture": "8 synthetic bilingual Infra notes; one optional synthetic diagram",
            "scope": "functional verification; sequential timings include parsing/cache/storage; "
            "model load excluded except first CLIP/reranker use; not retrieval quality evaluation",
            "initial_chunks": len(initial_ids),
            "initial": cold,
            "unchanged": unchanged,
            "single_file_update": update,
            "fresh_rebuild_warm_model": rebuilt,
            "max_vector_difference_vs_rebuild": error,
            "same_top5_as_rebuild": True,
            "restart_skip_verified": True,
            "deletion_no_text_reencoding": True,
            "context": {
                key: context[key]
                for key in ("budget", "used_tokens", "used_characters", "token_count_method")
            },
            "diagnostics": trace,
            "multimodal_verification": multimodal_report,
            "rerank_verification": rerank_report,
            "cleanup_preview": preview,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=["demo", "bge"], default="demo")
    parser.add_argument("--multimodal", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.multimodal and args.backend != "bge":
        parser.error("--multimodal requires --backend bge")
    result = run(args.backend, args.multimodal)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "backend",
                    "initial_chunks",
                    "unchanged",
                    "single_file_update",
                    "context",
                )
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )
    record_operation(
        "验证增量处理、持久向量缓存、阶段诊断、共享上下文预算与清理",
        "减少全库重复编码，确保新路径与完整重建一致且可追溯",
        f"backend={args.backend}, multimodal={args.multimodal}; 报告={args.output}; "
        f"vector difference={result['max_vector_difference_vs_rebuild']}; restart/delete passed",
        "合成小语料功能验收，计时包含SQLite和版本集合写入；不代表准确率提升或大库性能",
    )


if __name__ == "__main__":
    main()
