"""Index only the frozen source corpus; benchmark questions never enter the knowledge base."""

import hashlib
import json
import time
from pathlib import Path

from infra_rag.chunking import parse_file
from infra_rag.config import Settings
from infra_rag.service import RetrievalService

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "evals" / "repository-benchmark"


def index_settings(backend="bge"):
    manifest = json.loads((DATASET / "corpus-manifest.json").read_text())
    return Settings(
        data_dir=ROOT / "data" / "repository-index" / f"{backend}-{manifest['corpus_sha256'][:12]}",
        backend=backend,
    )


def build_index(backend="bge", *, settings=None, record_name="index-record.json"):
    manifest = json.loads((DATASET / "corpus-manifest.json").read_text())
    service = RetrievalService(settings or index_settings(backend))
    corpus = ROOT / manifest["corpus_root"]
    if service.chunks:
        print("Using existing index", service.status(), flush=True)
        return service
    start = time.perf_counter()
    chunks = []
    encoder = service._encoder()
    for index, document in enumerate(manifest["documents"], 1):
        source = corpus / document["source"]
        if hashlib.sha256(source.read_bytes()).hexdigest() != document["sha256"]:
            raise ValueError(f"source hash mismatch: {source}")
        parsed = parse_file(source, "infra", encoder, service.settings)
        chunks.extend(parsed)
        print(
            f"Parsed {index}/{len(manifest['documents'])}: {document['repository']} "
            f"{Path(document['path']).name} -> {len(parsed)} chunks",
            flush=True,
        )
    print("Encoding and persisting", len(chunks), "chunks", flush=True)
    service._commit(chunks)
    record = {
        "corpus_sha256": manifest["corpus_sha256"],
        "configuration": service.status(),
        "index_seconds": time.perf_counter() - start,
        "index_dir": str(service.settings.data_dir.relative_to(ROOT)),
    }
    (DATASET / record_name).write_text(json.dumps(record, ensure_ascii=False, indent=2))
    print("Completed", record, flush=True)
    return service


if __name__ == "__main__":
    build_index()
