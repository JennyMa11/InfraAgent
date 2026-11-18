"""Validate, freeze and evaluate official-source QA without touching online indexes."""

import argparse
import importlib.metadata
import json
import platform
import urllib.request
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

from operation_log import ROOT, record_operation
from prepare_official_benchmark import DATASET

from infra_rag.benchmarking import (
    VARIANTS,
    bootstrap_groups,
    canonical_hash,
    create_run,
    digest,
    human_summary,
    load_json,
    validate_dataset,
    write_new,
)
from infra_rag.config import Settings
from infra_rag.legacy_model_clients import AnthropicClient, OllamaClient, OpenAICompatibleClient
from infra_rag.offline_evaluation import (
    answer_review_template,
    evaluation_rows,
    report_markdown,
    review_markdown,
    summarize,
)
from infra_rag.service import RetrievalService


def implementation_hash():
    files = sorted((ROOT / "src/infra_rag").glob("*.py")) + [
        Path(__file__).resolve(),
        ROOT / "scripts/build_official_dataset.py",
        ROOT / "scripts/prepare_official_benchmark.py",
    ]
    return canonical_hash([[str(p.relative_to(ROOT)), digest(p)] for p in files])


def snapshot(model):
    from huggingface_hub import snapshot_download

    directory = Path(snapshot_download(model, local_files_only=True)).resolve()
    files = sorted(p for p in directory.rglob("*") if p.is_file())
    return {
        "model": model,
        "path": str(directory),
        "files": {str(p.relative_to(directory)): digest(p) for p in files},
    }


def verify_snapshot(record):
    for filename, expected in record["files"].items():
        if digest(Path(record["path"]) / filename) != expected:
            raise ValueError("model snapshot changed")


def ollama_identity(base_url, name):
    # Local benchmark services must bypass configured HTTP proxies.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(base_url.rstrip("/") + "/api/tags", timeout=10) as response:
        models = json.load(response)["models"]
    match = [m for m in models if m["name"] == name]
    if len(match) != 1:
        raise ValueError(f"Ollama model unavailable: {name}")
    return {"model": name, "digest": match[0]["digest"]}


class LocalClient(OllamaClient):
    def _request(self, payload):
        request = urllib.request.Request(
            self.base_url + "/api/chat",
            method="POST",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(request, timeout=self.timeout) as response:
            return json.load(response)


def freeze(args):
    _, splits = validate_dataset(args.dataset, ROOT, formal=not args.diagnostic)
    query_expansion = None
    if args.query_rewrites:
        from infra_rag.query_expansion import load_rewrites

        load_rewrites(args.query_rewrites, splits["dev"])
        query_expansion = {
            "mode": args.query_language,
            "rewrites_path": str(args.query_rewrites.resolve()),
            "rewrites_sha256": digest(args.query_rewrites),
            "scope": "dev only; frozen AI translations, not independently reviewed",
        }
    models = {
        "embedding": snapshot("BAAI/bge-small-zh-v1.5"),
        "reranker": snapshot("BAAI/bge-reranker-base"),
    }
    settings = asdict(
        Settings(
            backend="bge",
            fusion_candidates=args.fusion_candidates,
            candidate_k=args.candidate_k,
            context_tokens=args.context_tokens,
            context_chars=args.context_chars,
        )
    )
    settings.pop("data_dir")
    settings["embedding_model"] = models["embedding"]["path"]
    settings["reranker_model"] = models["reranker"]["path"]
    if args.generation == "dual" and args.provider in {"anthropic", "openai"}:
        client_class = OpenAICompatibleClient if args.provider == "openai" else AnthropicClient
        api_client = client_class.from_environment(
            path=args.env_file, model=args.answer_model, base_url=args.api_base_url
        )
        api_client.preload()
        generation = {
            "mode": args.generation,
            **api_client.configuration(),
            "identity": {
                "model": api_client.model,
                "returned_model": api_client.last_call.get("model"),
                "immutable_weights": False,
            },
            "readiness_response": api_client.last_call,
        }
    else:
        generation = {
            "mode": args.generation,
            "provider": "ollama",
            "base_url": args.ollama_url,
            "options": {"temperature": 0, "num_predict": 650, "num_ctx": 8192},
            "identity": ollama_identity(args.ollama_url, "qwen3:4b")
            if args.generation == "dual"
            else None,
        }
    directory = create_run(args.output, {"kind": "protocol"})
    write_new(
        directory / "protocol.json",
        {
            "dataset": str(args.dataset.resolve()),
            "diagnostic": args.diagnostic,
            "dataset_manifest_sha256": digest(args.dataset / "dataset-manifest.json"),
            "corpus_manifest_sha256": digest(args.dataset / "corpus-manifest.json"),
            "implementation_sha256": implementation_hash(),
            "models": models,
            "settings": settings,
            "variants": list(VARIANTS),
            "top_k": [5, 10],
            "generation": generation,
            "query_expansion": query_expansion,
            "seed": 42,
            "bootstrap_samples": 2000,
            "human_scoring": "explicit independent review; missing labels remain null",
            "environment": {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "packages": {
                    name: importlib.metadata.version(name)
                    for name in ("sentence-transformers", "chromadb", "torch", "jieba")
                },
            },
        },
    )
    print(directory / "protocol.json")


def run(args):
    protocol = load_json(args.protocol)
    dataset = Path(protocol["dataset"])
    if protocol["implementation_sha256"] != implementation_hash():
        raise ValueError("implementation changed after protocol freeze; create a new dev protocol")
    if (
        digest(dataset / "dataset-manifest.json") != protocol["dataset_manifest_sha256"]
        or digest(dataset / "corpus-manifest.json") != protocol["corpus_manifest_sha256"]
    ):
        raise ValueError("dataset changed after protocol freeze")
    corpus, splits = validate_dataset(dataset, ROOT, formal=not protocol["diagnostic"])
    query_expansion = protocol.get("query_expansion")
    if query_expansion and args.split != "dev":
        raise ValueError("Dev translation ablation cannot evaluate holdout; freeze a new protocol")
    if args.split == "holdout":
        if protocol["diagnostic"]:
            raise ValueError("candidate diagnostics cannot evaluate holdout")
        completed = load_json(args.protocol.parent / "dev-completed.json")
        if (
            completed["protocol_sha256"] != digest(args.protocol)
            or digest(Path(completed["run"]) / "summary.json") != completed["summary_sha256"]
        ):
            raise ValueError("matching completed dev run required before holdout")
        if args.limit or args.variant:
            raise ValueError("formal holdout must use all questions and configurations")
    if (args.limit or args.variant) and not protocol["diagnostic"]:
        raise ValueError("partial runs are diagnostic only")
    for record in protocol["models"].values():
        verify_snapshot(record)
    generation = protocol["generation"]
    client = None
    if generation["mode"] == "dual":
        if generation.get("provider", "ollama") in {"anthropic-compatible", "openai-compatible"}:
            if generation["options"]["temperature"] != 0:
                raise ValueError("unsupported frozen API generation options")
            client_class = (
                OpenAICompatibleClient
                if generation["provider"] == "openai-compatible"
                else AnthropicClient
            )
            client = client_class.from_environment(
                path=args.env_file,
                model=generation["identity"]["model"],
                base_url=generation["base_url"],
                max_tokens=generation["options"]["max_tokens"],
            )
            if client.configuration()["options"] != generation["options"]:
                raise ValueError("API generation options changed")
        else:
            if ollama_identity(generation["base_url"], "qwen3:4b") != generation["identity"]:
                raise ValueError("Ollama model changed")
            client = LocalClient(base_url=generation["base_url"])
    output = create_run(
        args.output,
        {
            "protocol_sha256": digest(args.protocol),
            "split": args.split,
            "diagnostic": protocol["diagnostic"],
            "limit": args.limit,
            "variant": args.variant,
        },
    )
    if args.split == "holdout":
        write_new(
            args.protocol.parent / "holdout-started.json",
            {"run": str(output.resolve()), "protocol_sha256": digest(args.protocol)},
        )
    settings = Settings(
        **protocol["settings"],
        data_dir=ROOT
        / "data/official-evals/indexes"
        / canonical_hash([corpus["corpus_sha256"], protocol["settings"]])[:24],
    )
    started = perf_counter()
    service = RetrievalService(settings)
    service.ingest(ROOT / corpus["corpus_root"], "infra")
    index_ms = (perf_counter() - started) * 1000
    variants = [args.variant] if args.variant else protocol["variants"]
    # Fixed non-benchmark query; load every selected path before latency measurement.
    from dataclasses import replace

    started = perf_counter()
    for variant in variants:
        service.settings = replace(service.settings, rerank=variant.endswith("_rerank"))
        service.search("KV cache memory", top_k=10, strategy=variant.replace("_rerank", ""))
    if client:
        client.preload()
    warmup_ms = (perf_counter() - started) * 1000
    questions = splits[args.split][: args.limit] if args.limit else splits[args.split]
    if query_expansion:
        from infra_rag.query_expansion import ExpandedRetrieval, load_rewrites

        rewrites_path = Path(query_expansion["rewrites_path"])
        if digest(rewrites_path) != query_expansion["rewrites_sha256"]:
            raise ValueError("Frozen query translations changed")
        rewrites = load_rewrites(rewrites_path, splits["dev"])
        service = ExpandedRetrieval(service, rewrites, query_expansion["mode"])
    rows = []
    try:
        with (output / "rows.jsonl").open("x", encoding="utf-8") as stream:
            for row in evaluation_rows(
                service, questions, dataset, client=client, variants=variants
            ):
                rows.append(row)
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                stream.flush()
                print(row["review_key"], flush=True)
    except Exception as exc:
        write_new(
            output / "failure.json",
            {"error": f"{type(exc).__name__}: {exc}", "completed_rows": len(rows)},
        )
        raise
    write_new(
        output / "summary.json",
        {
            "status": "candidate_diagnostic"
            if protocol["diagnostic"]
            else "human_reviewed_questions",
            "index_build_or_restore_ms": index_ms,
            "first_warmup_ms": warmup_ms,
            "summaries": summarize(rows),
            "by_type": {
                kind: summarize([r for r in rows if r["question_type"] == kind])
                for kind in sorted({r["question_type"] for r in rows})
            },
            "human_answers": human_summary([r for r in rows if r["generation"] is not None], []),
            "latency_scope": "warm retrieval top10 includes diagnostic "
            "collection; generation includes validation retries",
        },
    )
    write_new(output / "answer-review.json", answer_review_template(rows))
    summary = load_json(output / "summary.json")
    for filename, content in (
        ("report.md", report_markdown(summary)),
        ("answer-review.md", review_markdown(rows)),
    ):
        with (output / filename).open("x", encoding="utf-8") as stream:
            stream.write(content)
    if (
        args.split == "dev"
        and not protocol["diagnostic"]
        and not any(r["generation"] and r["generation"]["error"] for r in rows)
    ):
        write_new(
            args.protocol.parent / "dev-completed.json",
            {
                "protocol_sha256": digest(args.protocol),
                "run": str(output.resolve()),
                "summary_sha256": digest(output / "summary.json"),
            },
        )
    record_operation(
        "官方语料分层离线评测",
        "区分召回、交付与生成错误",
        f"{args.split}: {len(questions)}题，{len(rows)}条输出，{output}",
        "答案事实评分仍需独立人工审核",
    )


def score(args):
    rows = [json.loads(line) for line in (args.run / "rows.jsonl").read_text().splitlines()]
    rows = [r for r in rows if r["generation"] is not None]
    reviews = load_json(args.reviews)
    result = {
        "run_manifest_sha256": digest(args.run / "manifest.json"),
        "rows_sha256": digest(args.run / "rows.jsonl"),
        "reviews_sha256": digest(args.reviews),
        "summary": human_summary(rows, reviews),
        "by_variant": {
            variant: human_summary(
                [r for r in rows if r["variant"] == variant],
                [
                    v
                    for v in reviews
                    if v["review_key"] in {r["review_key"] for r in rows if r["variant"] == variant}
                ],
            )
            for variant in sorted({r["variant"] for r in rows})
        },
        "by_type": {
            kind: human_summary(
                [r for r in rows if r["question_type"] == kind],
                [
                    v
                    for v in reviews
                    if v["review_key"]
                    in {r["review_key"] for r in rows if r["question_type"] == kind}
                ],
            )
            for kind in sorted({r["question_type"] for r in rows})
        },
        "answer_correctness_ci95": {
            variant: bootstrap_groups(
                [
                    {"group_id": r["group_id"], "value": float(v["fact_correct"])}
                    for r in rows
                    for v in reviews
                    if r["variant"] == variant
                    and r["answerable"]
                    and r["review_key"] == v["review_key"]
                    and v.get("status") == "approved"
                ],
                "value",
            )
            for variant in sorted({r["variant"] for r in rows})
        },
    }
    write_new(args.output, result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("validate")
    check.add_argument("--dataset", type=Path, default=DATASET)
    check.add_argument("--formal", action="store_true")
    locked = commands.add_parser("freeze")
    locked.add_argument("--dataset", type=Path, default=DATASET)
    locked.add_argument("--output", type=Path, required=True)
    locked.add_argument("--diagnostic", action="store_true")
    locked.add_argument("--generation", choices=["none", "dual"], default="dual")
    locked.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    locked.add_argument("--provider", choices=["ollama", "anthropic", "openai"], default="ollama")
    locked.add_argument("--answer-model")
    locked.add_argument("--api-base-url")
    locked.add_argument("--env-file", type=Path)
    locked.add_argument("--fusion-candidates", choices=["truncate", "union"], default="truncate")
    locked.add_argument("--candidate-k", type=int, default=30)
    locked.add_argument("--context-tokens", type=int, default=1200)
    locked.add_argument("--context-chars", type=int, default=4000)
    locked.add_argument("--query-rewrites", type=Path)
    locked.add_argument("--query-language", choices=["english", "bilingual"], default="english")
    evaluate = commands.add_parser("run")
    evaluate.add_argument("--protocol", type=Path, required=True)
    evaluate.add_argument("--output", type=Path, required=True)
    evaluate.add_argument("--split", choices=["dev", "holdout"], default="dev")
    evaluate.add_argument("--limit", type=int)
    evaluate.add_argument("--variant", choices=VARIANTS)
    evaluate.add_argument("--env-file", type=Path)
    scoring = commands.add_parser("score")
    scoring.add_argument("--run", type=Path, required=True)
    scoring.add_argument("--reviews", type=Path, required=True)
    scoring.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "validate":
        validate_dataset(args.dataset, ROOT, formal=args.formal)
        print("Validated frozen corpus, splits, evidence and review status")
    elif args.command == "freeze":
        freeze(args)
    elif args.command == "run":
        if args.limit is not None and args.limit < 1:
            parser.error("--limit must be positive")
        run(args)
    else:
        score(args)


if __name__ == "__main__":
    main()
