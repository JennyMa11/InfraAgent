import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .config import BACKENDS, CHUNK_STRATEGIES, Settings, default_embedding_model
from .context import response_payload
from .evaluation import evaluate, resolve_spans
from .service import RetrievalService


def main():
    from .model_clients import model_environment

    parser = argparse.ArgumentParser(description="Infra RAG retrieval service")
    parser.add_argument("--data-dir", type=Path, default=Path("data/default-v2"))
    parser.add_argument("--backend", choices=BACKENDS, default="demo")
    parser.add_argument("--embedding-model")
    parser.add_argument("--embedding-revision")
    parser.add_argument("--embedding-device")
    parser.add_argument("--embedding-batch-size", type=int)
    parser.add_argument("--embedding-max-length", type=int, default=8192)
    parser.add_argument("--rerank", action="store_true")
    parser.add_argument(
        "--query-language",
        choices=["none", "english", "bilingual"],
        default=model_environment().get("INFRA_RAG_QUERY_LANGUAGE", "none"),
        help="Translate chat retrieval queries; search/evaluate keep literal queries",
    )
    parser.add_argument("--multimodal", action="store_true")
    parser.add_argument("--heading-context", action="store_true")
    parser.add_argument("--fusion-candidates", choices=["truncate", "union"], default="truncate")
    parser.add_argument("--lexical-query-mode", choices=["raw", "technical"], default="raw")
    parser.add_argument("--candidate-k", type=int, default=30)
    parser.add_argument(
        "--answer-top-k", type=int, default=5, help="Delivered chunks for chat answers"
    )
    parser.add_argument(
        "--query-decomposition",
        action="store_true",
        help="Generate 1-3 retrieval sub-queries before chat retrieval",
    )
    parser.add_argument("--rrf-constant", type=int, default=60)
    parser.add_argument("--rerank-top-n", type=int, default=90)
    parser.add_argument("--candidate-pool-cap", type=int)
    parser.add_argument("--no-neighbor-expansion", action="store_true")
    parser.add_argument("--context-mode", choices=["legacy", "neighbors"], default="neighbors")
    parser.add_argument("--context-policy", choices=["prefix", "complete"], default="prefix")
    parser.add_argument("--context-tokens", type=int, default=1200)
    parser.add_argument("--context-chars", type=int, default=4000)
    parser.add_argument("--chunk-size", type=int, default=450)
    parser.add_argument("--chunk-strategy", choices=CHUNK_STRATEGIES, default="semantic")
    parser.add_argument("--chunk-overlap", type=int, default=0)
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
    chains = sub.add_parser(
        "chains", help="Run explicitly selected experimental RAG chains (does not change /chat)"
    )
    chains.add_argument("query")
    chains.add_argument(
        "--chain", action="append", choices=["baseline", "graph_rag", "agentic_rag"], required=True
    )
    chains.add_argument("--agent-model", choices=["live", "offline"], default="live")
    chains.add_argument("--env-file", type=Path)
    chains.add_argument("--top-k", type=int, default=5)
    chains.add_argument("--domain")
    chains.add_argument("--output", type=Path)
    chains.add_argument("--run-id", default="interactive")
    comparison = sub.add_parser("compare-rag", help="Paired evaluation with frozen labels")
    comparison.add_argument("dataset", type=Path)
    comparison.add_argument(
        "--chain", action="append", choices=["baseline", "graph_rag", "agentic_rag"], required=True
    )
    comparison.add_argument("--agent-model", choices=["live", "offline"], default="live")
    comparison.add_argument("--env-file", type=Path)
    comparison.add_argument("--top-k", type=int, default=5)
    comparison.add_argument("--label", choices=["source", "chunk", "parent"], default="source")
    comparison.add_argument("--output", type=Path, required=True)
    comparison.add_argument("--run-id", default="paired")
    comparison.add_argument(
        "--require-complete", action="store_true", help="Fail after preserving any failed run"
    )
    args = parser.parse_args()
    service = RetrievalService(
        Settings(
            data_dir=args.data_dir,
            backend=args.backend,
            embedding_model=args.embedding_model or default_embedding_model(args.backend),
            embedding_revision=args.embedding_revision,
            embedding_device=args.embedding_device,
            embedding_batch_size=args.embedding_batch_size,
            embedding_max_length=args.embedding_max_length,
            rerank=args.rerank,
            query_language=args.query_language,
            multimodal=args.multimodal,
            heading_context=args.heading_context,
            fusion_candidates=args.fusion_candidates,
            lexical_query_mode=args.lexical_query_mode,
            candidate_k=args.candidate_k,
            answer_top_k=args.answer_top_k,
            query_decomposition=args.query_decomposition,
            rrf_constant=args.rrf_constant,
            rerank_top_n=args.rerank_top_n,
            candidate_pool_cap=args.candidate_pool_cap,
            neighbor_expansion=not args.no_neighbor_expansion,
            context_mode=args.context_mode,
            context_policy=args.context_policy,
            context_tokens=args.context_tokens,
            context_chars=args.context_chars,
            chunk_size=args.chunk_size,
            chunk_strategy=args.chunk_strategy,
            chunk_overlap=args.chunk_overlap,
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
    elif args.command in {"chains", "compare-rag"}:
        from .benchmarking import create_run, write_new
        from .rag_comparison import OfflineAgentModel, RAGComparisonRunner, prepare_cases

        if "agentic_rag" in args.chain and args.agent_model == "live":
            from .model_clients import configured_model

            if args.env_file is not None:
                # Use the same native model factory, with an explicit environment override.
                model = configured_model(path=args.env_file)
            else:
                model = configured_model()
        else:
            model = OfflineAgentModel()
        runner = RAGComparisonRunner(service, chains=args.chain, model=model, top_k=args.top_k)
        if args.command == "chains":
            run_dir = create_run(
                args.output,
                {
                    "run_id": args.run_id,
                    "chains": args.chain,
                    "index_fingerprint": service.index_fingerprint,
                    "mode": "single_unlabeled_query; no relevance or correctness metric",
                },
            )
            row = runner.run_case(
                {
                    "id": args.run_id,
                    "query": args.query,
                    "domain": args.domain,
                    "group_id": args.run_id,
                },
                output_dir=run_dir,
                run_id=args.run_id,
            )
            write_new(run_dir / "result.json", row)
            if any(item["status"] != "ok" for item in row["results"].values()):
                failures = {
                    name: {"error_type": item["error_type"], "error": item["error"]}
                    for name, item in row["results"].items()
                    if item["status"] != "ok"
                }
                raise RuntimeError(f"chain failed; inspect {run_dir}: {failures}")
            result = row
        else:
            cases = prepare_cases(
                service, json.loads(args.dataset.read_text()), args.dataset, args.label
            )
            result = runner.compare(
                cases,
                args.output,
                dataset_path=args.dataset,
                run_id=args.run_id,
                label=args.label,
                require_complete=args.require_complete,
            )
    else:
        import uvicorn

        from .api import create_app

        uvicorn.run(create_app(service), host="127.0.0.1", port=args.port)
        return
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
