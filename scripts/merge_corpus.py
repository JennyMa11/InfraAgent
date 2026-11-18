"""Build an isolated provenance-preserving index from the two frozen corpora."""

import argparse
import hashlib
import json
from pathlib import Path

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.config import Settings
from infra_rag.models import Chunk
from infra_rag.service import RetrievalService

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evals/merged-corpus-v1"
INPUTS = [
    ("official", "evals/infra-official-v1/corpus-manifest.json", "data/deepseek-optimized"),
    (
        "community",
        "evals/repository-benchmark/corpus-manifest.json",
        "data/repository-index/bge-e4579f5f84b9",
    ),
]


def deduplicate(chunks, vectors):
    """Remove only exact cross-source copies, preserving first (official-first) IDs."""
    kept, embeddings, aliases, seen = [], [], [], {}
    for chunk, vector in zip(chunks, vectors, strict=True):
        text = chunk.content.strip()
        key = hashlib.sha256(text.encode()).hexdigest()
        previous = seen.get(key)
        if len(text) >= 100 and previous and previous.source != chunk.source:
            aliases.append(
                {
                    "removed_id": chunk.id,
                    "canonical_id": previous.id,
                    "source": chunk.source,
                    "locator": chunk.locator,
                    "sha256": key,
                }
            )
            continue
        seen.setdefault(key, chunk)
        kept.append(chunk)
        embeddings.append(vector)
    return kept, embeddings, aliases


def settings(data_dir):
    return Settings(
        data_dir=data_dir,
        backend="bge",
        rerank=True,
        fusion_candidates="union",
        candidate_k=30,
        query_language="english",
    )


class ProvenanceRetrieval(RetrievalService):
    """Attach frozen source/version metadata to the evidence returned by the API."""

    def __init__(self, configuration):
        super().__init__(configuration)
        self.provenance = json.loads((configuration.data_dir / "provenance.json").read_text())[
            "sources"
        ]

    def search(self, query, **kwargs):
        hits = super().search(query, **kwargs)
        evidence = [e for hit in hits for e in hit.evidence]
        evidence.extend((kwargs.get("context_pack") or {}).get("evidence", []))
        for item in evidence:
            item["provenance"] = self.provenance.get(
                item["source"],
                {"collection": "user_import", "version": "unversioned", "source": item["source"]},
            )
        return hits


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    sources, chunks, vectors, inputs = {}, [], [], []
    fingerprint = settings(Path("unused")).fingerprint()
    for kind, manifest_path, index_path in INPUTS:
        path = ROOT / manifest_path
        manifest = json.loads(path.read_text())
        state = json.loads((ROOT / index_path / "index.json").read_text())
        if state["fingerprint"] != fingerprint:
            raise ValueError("Input index fingerprint differs; cannot reuse embeddings")
        expected = {}
        for document in manifest["documents"]:
            source = (ROOT / manifest["corpus_root"] / document["source"]).resolve()
            if digest(source) != document["sha256"]:
                raise ValueError(f"Frozen source changed: {source}")
            expected[str(source)] = document
            sources[str(source)] = {"collection": kind, **document}
        indexed = {c["source"] for c in state["chunks"]}
        if indexed != set(expected):
            raise ValueError("Input index sources differ from frozen manifest")
        chunks.extend(Chunk(**c) for c in state["chunks"])
        vectors.extend(state["vectors"])
        inputs.append(
            {
                "collection": kind,
                "manifest": manifest_path,
                "manifest_sha256": digest(path),
                "index": index_path,
                "index_sha256": digest(ROOT / index_path / "index.json"),
            }
        )
    kept, embeddings, aliases = deduplicate(chunks, vectors)
    # Similarity audit is deliberately separate from deletion: versions may differ in meaning.
    shingles = {}
    near = []
    for source in sources:
        text = "".join(Path(source).read_text().split())
        shingles[source] = {text[i : i + 40] for i in range(0, max(0, len(text) - 39), 20)}
    names = list(sources)
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            a, b = shingles[left], shingles[right]
            overlap = len(a & b) / max(1, min(len(a), len(b)))
            if overlap >= 0.5:
                near.append(
                    {
                        "left": left,
                        "right": right,
                        "containment": overlap,
                        "action": "retain_versioned_sources",
                    }
                )
    manifest = {
        "version": "merged-corpus-v1",
        "inputs": inputs,
        "sources": sources,
        "deduplication": {
            "policy": "exact stripped cross-source chunks >=100 chars; official first",
            "aliases": aliases,
            "near_document_candidates": near,
            "input_chunks": len(chunks),
            "retained_chunks": len(kept),
        },
        "fingerprint": fingerprint,
    }
    identity = canonical_hash(manifest)
    directory = ROOT / "data/merged-corpus-v1" / identity[:16]
    manifest["index_dir"] = str(directory.relative_to(ROOT))
    manifest["corpus_sha256"] = identity
    service = RetrievalService(settings(directory))
    if not service.chunks:
        service.chunks, service.vectors = kept, embeddings
        service._commit(kept, {s: service._source_record(Path(s), "infra") for s in sources})
    elif [c.id for c in service.chunks] != [c.id for c in kept]:
        raise ValueError("Existing merged index differs from expected chunks")
    (directory / "provenance.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    (OUT / "corpus-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(
        json.dumps(
            {
                "index_dir": str(directory),
                "sources": len(sources),
                "chunks": len(kept),
                "removed_duplicates": len(aliases),
                "near_candidates": len(near),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    return directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument(
        "--query-language", choices=["none", "english", "bilingual"], default="english"
    )
    args = parser.parse_args()
    directory = build()
    if args.serve:
        from dataclasses import replace

        import uvicorn

        from infra_rag.api import create_app
        from infra_rag.assistant import AnswerService
        from infra_rag.legacy_model_clients import AnthropicClient

        service = ProvenanceRetrieval(
            replace(settings(directory), query_language=args.query_language)
        )
        model = AnthropicClient.from_environment(path=ROOT / ".env.llm")
        uvicorn.run(
            create_app(service, AnswerService(service, model=model)),
            host="127.0.0.1",
            port=args.port,
        )


if __name__ == "__main__":
    main()
