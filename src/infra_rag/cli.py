import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .config import Settings
from .context import response_payload
from .evaluation import evaluate, resolve_spans
from .service import RetrievalService


def main():
    parser = argparse.ArgumentParser(description="Infra RAG retrieval service")
    parser.add_argument("--data-dir", type=Path, default=Path("data/default-v2"))
    parser.add_argument("--backend", choices=["demo", "bge"], default="demo")
    parser.add_argument("--embedding-model", default="BAAI/bge-small-zh-v1.5")
    parser.add_argument("--rerank", action="store_true")
    parser.add_argument("--multimodal", action="store_true")
    parser.add_argument("--heading-context", action="store_true")
    parser.add_argument("--fusion-candidates", choices=["truncate", "union"], default="truncate")
    parser.add_argument("--lexical-query-mode", choices=["raw", "technical"], default="raw")
    parser.add_argument("--candidate-k", type=int, default=30)
    parser.add_argument("--context-mode", choices=["legacy", "neighbors"], default="neighbors")
    parser.add_argument("--context-tokens", type=int, default=1200)
    parser.add_argument("--context-chars", type=int, default=4000)
    parser.add_argument("--chunk-size", type=int, default=450)
    parser.add_argument("--chunk-strategy", choices=["semantic", "window"], default="semantic")
    sub = parser.add_subparsers(dest="command", required=True)
    ingest = sub.add_parser("ingest")
    ingest.add_argument("path", type=Path)
    ingest.add_argument("--domain", default="general")
    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--debug", action="store_true")
    search.add_argument("--with-context", action="store_true")
    search.add_argument("--top-k", type=int, default=5)
    search.add_argument("--domain")
    search.add_argument("--modality", choices=["text", "image"])
    search.add_argument("--strategy", choices=["bm25", "dense", "hybrid", "clip"], default="hybrid")
    sub.add_parser("status")
    cleanup = sub.add_parser("cleanup")
    cleanup.add_argument(
        "--apply", action="store_true", help="Remove unused generated assets/cache"
    )
    serve = sub.add_parser("serve")
    serve.add_argument("--port", type=int, default=8000)
    evaluation = sub.add_parser("evaluate")
    evaluation.add_argument("dataset", type=Path)
    evaluation.add_argument("--top-k", type=int, default=5)
    evaluation.add_argument("--label", choices=["source", "chunk", "parent"], default="source")
    evaluation.add_argument(
        "--strategy", choices=["bm25", "dense", "hybrid", "clip"], default="hybrid"
    )
    evaluation.add_argument("--output", type=Path)
    args = parser.parse_args()
    service = RetrievalService(
        Settings(
            data_dir=args.data_dir,
            backend=args.backend,
            embedding_model=args.embedding_model,
            rerank=args.rerank,
            multimodal=args.multimodal,
            heading_context=args.heading_context,
            fusion_candidates=args.fusion_candidates,
            lexical_query_mode=args.lexical_query_mode,
            candidate_k=args.candidate_k,
            context_mode=args.context_mode,
            context_tokens=args.context_tokens,
            context_chars=args.context_chars,
            chunk_size=args.chunk_size,
            chunk_strategy=args.chunk_strategy,
        )
    )
    if args.command == "ingest":
        result = service.ingest(args.path, args.domain)
    elif args.command == "search":
        diagnostics = {} if args.debug else None
        context = {} if args.with_context else None
        hits = service.search(
            args.query,
            args.top_k,
            args.domain,
            args.modality,
            args.strategy,
            diagnostics=diagnostics,
            context_pack=context,
        )
        result = (
            response_payload(hits, diagnostics, context)
            if args.debug or args.with_context
            else [asdict(hit) for hit in hits]
        )
    elif args.command == "cleanup":
        result = service.cleanup(apply=args.apply)
    elif args.command == "status":
        result = service.status()
    elif args.command == "evaluate":
        dataset = json.loads(args.dataset.read_text())
        if args.label == "chunk" and all("relevant_spans" in item for item in dataset):
            dataset = resolve_spans(service, dataset, args.dataset.parent)
        for item in dataset:
            if args.label == "source":
                item["relevant"] = [
                    str((args.dataset.parent / p).resolve()) if not Path(p).is_absolute() else p
                    for p in item["relevant"]
                ]
        result = evaluate(service, dataset, args.top_k, args.strategy, args.label)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        import uvicorn

        from .api import create_app

        uvicorn.run(create_app(service), host="127.0.0.1", port=args.port)
        return
    print(json.dumps(result, ensure_ascii=False, indent=2))
