"""Serve the existing web UI and real RAG API on loopback using a separate runtime index."""

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
from dataclasses import fields, replace
from pathlib import Path
from time import perf_counter

from operation_log import ROOT, record_operation

from infra_rag.benchmarking import digest
from infra_rag.config import Settings

DEFAULT_INDEX = ROOT / "data/merged-corpus-v4/e624132ff5b8a3d6/index.json"
DEFAULT_DATA = ROOT / "data/local-web/index"
LOCAL_PROFILE = ROOT / "data/local-web/launcher.json"


def launcher_paths(index: Path | None, data_dir: Path | None) -> tuple[Path, Path]:
    """Resolve each path independently: explicit flag, then local profile, then built-in default."""
    profile = json.loads(LOCAL_PROFILE.read_text()) if LOCAL_PROFILE.is_file() else {}
    index = index or (ROOT / profile["index"] if "index" in profile else DEFAULT_INDEX)
    data_dir = data_dir or (ROOT / profile["data_dir"] if "data_dir" in profile else DEFAULT_DATA)
    return index, data_dir


def runtime_settings(source: Path, data_dir: Path):
    snapshot = data_dir / "index.json"
    if source.resolve() == snapshot.resolve():
        raise ValueError("Use a separate runtime directory; never serve a frozen index in place")
    if not snapshot.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, snapshot)
        (data_dir / "origin.json").write_text(
            json.dumps({"source": str(source), "sha256": digest(source)}, indent=2) + "\n"
        )
    state = json.loads(snapshot.read_text())
    names = {f.name for f in fields(Settings)} - {"data_dir"}
    options = {key: value for key, value in state["fingerprint"].items() if key in names}
    if options.get("backend") != "bge" or options.get("multimodal"):
        raise ValueError("This local launcher requires the existing text-only BGE index")
    return Settings(
        data_dir=data_dir,
        **options,
        rerank=True,
        candidate_k=30,
        fusion_candidates="union",
        query_language="none",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--background", action="store_true")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--retrieval-cache-size", type=int, default=0)
    parser.add_argument("--prewarm", action="store_true")
    parser.add_argument("--context-policy", choices=["prefix", "complete"], default="prefix")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    if args.batch_size < 1 or args.retrieval_cache_size < 0:
        parser.error("batch size must be positive; cache size must be nonnegative")
    index, data_dir = launcher_paths(args.index, args.data_dir)
    args.index, args.data_dir = index.resolve(), data_dir.resolve()
    if args.background:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", args.port))
        runtime = args.data_dir.parent
        runtime.mkdir(parents=True, exist_ok=True)
        log = runtime / "server.log"
        with log.open("ab") as stream:
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "--index",
                    str(args.index),
                    "--data-dir",
                    str(args.data_dir),
                    "--port",
                    str(args.port),
                    "--batch-size",
                    str(args.batch_size),
                    "--retrieval-cache-size",
                    str(args.retrieval_cache_size),
                    "--context-policy",
                    args.context_policy,
                    *(["--prewarm"] if args.prewarm else []),
                ],
                cwd=ROOT,
                stdin=subprocess.DEVNULL,
                stdout=stream,
                stderr=stream,
                start_new_session=True,
            )
        (runtime / "server.pid").write_text(str(process.pid) + "\n")
        print(f"Starting PID {process.pid}: http://127.0.0.1:{args.port}; logs: {log}")
        record_operation(
            "启动本地问答后台进程",
            "同源提供前端和真实API",
            f"PID={process.pid}",
            "启动已提交，需另行检查health与实际问答",
        )
        return

    import uvicorn
    from fastapi.middleware.cors import CORSMiddleware

    from infra_rag.api import create_app
    from infra_rag.assistant import AnswerService
    from infra_rag.model_clients import configured_model
    from infra_rag.runtime import AccountedModel, RuntimeRetrieval, install_request_journal
    from infra_rag.service import RetrievalService

    # Retrieval models use existing local downloads; answer API configuration stays unchanged.
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    service = RuntimeRetrieval(
        RetrievalService(
            replace(runtime_settings(args.index, args.data_dir), context_policy=args.context_policy)
        ),
        batch_size=args.batch_size,
        cache_size=args.retrieval_cache_size,
    )
    started = perf_counter()
    if args.prewarm:
        service.search("本地知识检索启动预热", top_k=1)
        service.cache.clear()
    runtime = args.data_dir.parent
    (runtime / "startup.json").write_text(
        json.dumps(
            {
                "prewarm": args.prewarm,
                "prewarm_ms": (perf_counter() - started) * 1000,
                "cache_cleared_after_prewarm": True,
                "answer_model_calls": 0,
            },
            indent=2,
        )
        + "\n"
    )
    assistant = AnswerService(service, model=AccountedModel(configured_model()))
    app = create_app(service, assistant, web_dir=ROOT / "web")
    install_request_journal(app, runtime / "requests.jsonl")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
        expose_headers=["Server-Timing", "X-Request-ID"],
    )
    uvicorn.run(app, host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
