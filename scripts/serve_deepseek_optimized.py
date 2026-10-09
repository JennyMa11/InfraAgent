"""Serve the measured DeepSeek/English-query configuration with approved corpus only."""

import argparse
from pathlib import Path

from infra_rag.api import create_app
from infra_rag.assistant import AnswerService
from infra_rag.benchmarking import validate_dataset
from infra_rag.config import Settings
from infra_rag.model_clients import AnthropicClient
from infra_rag.service import RetrievalService


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--data-dir", type=Path, default=Path("data/deepseek-optimized"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    corpus, _ = validate_dataset(root / "evals/infra-official-v1-reviewed", root, formal=True)
    model = AnthropicClient.from_environment(path=root / ".env.llm")
    if not model.deepseek or model.model != "deepseek-flash":
        raise ValueError("This profile expects the official deepseek-flash configuration")
    service = RetrievalService(
        Settings(
            data_dir=args.data_dir,
            backend="bge",
            rerank=True,
            fusion_candidates="union",
            candidate_k=30,
            context_tokens=1200,
            context_chars=4000,
            query_language="english",
        )
    )
    service.ingest(root / corpus["corpus_root"], "infra")
    import uvicorn

    uvicorn.run(
        create_app(service, AnswerService(service, model=model)), host="127.0.0.1", port=args.port
    )


if __name__ == "__main__":
    main()
