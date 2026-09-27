# Repository Guidelines

## Project Structure & Module Organization

- `src/infra_rag/` contains the Python package: document parsing and chunking, model encoders, retrieval service, evaluation, CLI, and FastAPI endpoints.
- `tests/` contains pytest tests for retrieval, evidence labels, optional backends, and semantic image processing.
- `scripts/` provides corpus preparation, dataset generation, indexing, model verification, and benchmark commands.
- `examples/` holds sample documents and diagrams. `evals/` holds datasets, provenance manifests, and experiment reports. `docs/` documents implementation and evaluation limits.
- `data/` stores downloaded repositories, processed corpora, and indexes; it is ignored. Record experiment conclusions in `日志.log`.

## Build, Test, and Development Commands

Use Python 3.12+ and `uv` from the repository root.

```bash
uv sync --extra dev                 # Install core and development dependencies
uv sync --all-extras                # Include real models, PDF, and image support
uv run infra-rag ingest examples/corpus
uv run infra-rag search 'KV Cache' --top-k 3
uv run infra-rag serve              # API documentation at localhost:8000/docs
uv run --extra dev pytest -q
uv run --extra dev ruff check src tests scripts
uv run --extra dev ruff format src tests scripts
uv build                           # Build package distributions
```

Global CLI options precede subcommands. Real model mode uses `--backend bge`; its initial execution downloads models.

## Coding Style & Naming Conventions

Use four-space indentation, `snake_case` functions and modules, and `PascalCase` classes. Follow Ruff's configured 100-character line limit and import ordering. Keep parsing, encoding, retrieval, and evaluation responsibilities in their existing modules. Preserve stable IDs, source locators, and index fingerprints.

## Testing Guidelines

Name tests `tests/test_*.py` and functions `test_*`. Use pytest fixtures and temporary directories for isolated indexes. Add meaningful regression tests for changed behavior, especially filtering, persistence, cache invalidation, and evidence resolution. No numerical coverage threshold is configured. Use verification scripts for actual model behavior; demo embeddings only validate plumbing.

## Commit & Pull Request Guidelines

This workspace has no Git history available, so no existing commit convention can be verified. Use concise imperative messages, such as `Fix lexical cache invalidation`. PRs should describe the problem, behavior changes, validation commands, and relevant issues. For retrieval changes, include dataset and configuration details alongside measured results.

## Dataset & Configuration Discipline

Use dev queries for tuning; keep test queries fixed. Preserve repository commits, hashes, and evidence provenance. Label AI-authored datasets accurately and disclose sparse relevance judgments. Never ingest benchmark questions or answers into the knowledge corpus. Use separate index directories when changing fingerprinted settings. Keep credentials in ignored `.env` files.
