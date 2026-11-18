"""Offline paired retrieval ablations using the existing answer chain and context packer."""

from dataclasses import asdict, replace
from time import perf_counter

from .context import pack_context
from .evaluation import metrics
from .models import Hit
from .offline_evaluation import generate_answer

CONFIGS = ("dense", "bm25_dense", "rrf", "rrf_reranker")


def collect_records(service, cases, client, *, run_id, k=5, repetitions=1):
    if k < 1 or repetitions < 1:
        raise ValueError("k and repetitions must be positive")
    if service.settings.context_policy != "prefix" or service.settings.context_mode != "neighbors":
        raise ValueError("ablation requires neighbors/prefix context packing")
    gold_ids = {c.id for c in service.chunks}
    if any(set(c["relevant"]) - gold_ids for c in cases):
        raise ValueError("gold chunk IDs do not resolve in the frozen index")
    original = service.settings
    try:
        for repetition in range(repetitions):
            for case in cases:
                for config in CONFIGS:
                    service.settings = replace(original, rerank=config == "rrf_reranker")
                    row = {
                        "run_id": run_id,
                        "config_id": config,
                        "case_id": case["id"],
                        "repetition": repetition,
                        "query": case["query"],
                        "reference": case["reference"],
                        "relevant": case["relevant"],
                        "response": None,
                        "evidence": [],
                        "retrieved": [],
                        "retrieval": {},
                        "generation_calls": [],
                        "error": None,
                        "diagnostics": {},
                    }
                    started = perf_counter()
                    try:
                        kwargs = {"domain": case.get("domain"), "modality": case.get("modality")}
                        if config == "bm25_dense":
                            # Equal-weight normalized rank sum (Borda); absent candidates score 0.
                            depth = original.candidate_k
                            rankings = []
                            for strategy in ("bm25", "dense"):
                                diagnostic = {}
                                ranking = service.search(
                                    case["query"],
                                    top_k=depth,
                                    strategy=strategy,
                                    diagnostics=diagnostic,
                                    **kwargs,
                                )
                                rankings.append(ranking)
                                row["diagnostics"][strategy] = diagnostic
                            scores, chunks = {}, {}
                            for ranking in rankings:
                                for rank, hit in enumerate(ranking):
                                    cid = hit.chunk.id
                                    chunks[cid] = hit.chunk
                                    scores[cid] = scores.get(cid, 0) + (depth - rank) / depth
                            hits = [
                                Hit(chunks[cid], score, ["bm25_dense_borda"])
                                for cid, score in sorted(
                                    scores.items(), key=lambda p: (-p[1], p[0])
                                )
                            ][:k]
                        else:
                            # Match fused variants' candidate depth before taking the same top-k.
                            depth = original.candidate_k if config == "dense" else k
                            hits = service.search(
                                case["query"],
                                top_k=depth,
                                strategy="dense" if config == "dense" else "hybrid",
                                diagnostics=row["diagnostics"],
                                **kwargs,
                            )
                            if config == "dense":
                                hits = hits[:k]
                        row["retrieved"] = [h.chunk.id for h in hits]
                        if case["relevant"]:
                            row["retrieval"] = metrics(row["retrieved"], case["relevant"], k)
                        encoder = service._encoder() if service.context_counter is None else None
                        count = service.context_counter or getattr(encoder, "token_length", len)
                        context = pack_context(
                            hits,
                            service.parent_index,
                            count,
                            original.context_tokens,
                            original.context_chars,
                            **kwargs,
                            neighbor_expansion=original.neighbor_expansion,
                        )
                        row["evidence"] = context["evidence"]
                        row["context"] = context
                        row["retrieval_latency_ms"] = (perf_counter() - started) * 1000
                        generation = generate_answer(case, context, service.settings, client)
                        row["generation"] = generation
                        row["generation_calls"] = [
                            c.get("provider_response") or {} for c in generation["calls"]
                        ]
                        if generation["error"]:
                            row["error"] = "generation_failed"
                        else:
                            row["response"] = generation["response"]["answer"]
                    except Exception as exc:
                        row["error"] = type(exc).__name__
                    row["latency_ms"] = (perf_counter() - started) * 1000
                    yield row
    finally:
        service.settings = original


def configuration(service):
    settings = asdict(service.settings)
    settings["data_dir"] = str(settings["data_dir"])
    return {
        "settings": settings,
        "index_fingerprint": service.index_fingerprint,
        "variants": {
            "dense": "dense only, no reranker",
            "bm25_dense": "equal-weight Borda: sum((candidate_k-rank+1)/candidate_k)",
            "rrf": "existing hybrid RRF, no reranker",
            "rrf_reranker": "existing hybrid RRF plus existing cross encoder",
        },
        "latency_scope": "cold/mixed retrieval, context packing and answer incl retries; "
        "excludes index load and Ragas judge; includes duplicate channel context work in Borda",
        "multimodal_scope": "delivered text/captions only; no visual faithfulness claim",
    }
