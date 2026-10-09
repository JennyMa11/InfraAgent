"""Fixed Chinese source-coverage smoke test from repository dev, never test questions."""

import json
from dataclasses import replace

from merge_corpus import OUT, ROOT, ProvenanceRetrieval, settings

from infra_rag.benchmarking import digest
from infra_rag.model_clients import AnthropicClient
from infra_rag.offline_evaluation import generate_answer
from infra_rag.service import RetrievalService


def main():
    dataset = ROOT / "evals/repository-benchmark/dev.json"
    questions = json.loads(dataset.read_text())
    selected = []
    for repository in sorted({q["relevant_spans"][0]["repository"] for q in questions}):
        for kind in ("knowledge", "scenario"):
            selected.append(
                sorted(
                    (
                        q
                        for q in questions
                        if q["relevant_spans"][0]["repository"] == repository
                        and q["question_type"] == kind
                    ),
                    key=lambda q: q["id"],
                )[0]
            )
    output = OUT / "coverage-dev-20261002"
    output.mkdir(exist_ok=False)
    (output / "protocol.json").write_text(
        json.dumps(
            {
                "dev_sha256": digest(dataset),
                "ids": [q["id"] for q in selected],
                "selection": "first ID per repository and question type; fixed before retrieval",
                "query_language": "original Chinese in both arms; isolates corpus difference",
                "scope": "six-question dev smoke test; AI-authored references; no accuracy claim",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    manifest = json.loads((OUT / "corpus-manifest.json").read_text())
    directory = ROOT / manifest["index_dir"]
    model = AnthropicClient.from_environment(path=ROOT / ".env.llm", max_tokens=650)
    services = [
        ("official_chinese", RetrievalService(settings(ROOT / "data/deepseek-optimized"))),
        ("merged_chinese", ProvenanceRetrieval(settings(directory))),
    ]
    with (output / "answers.jsonl").open("x") as stream:
        for arm, service in services:
            for q in selected:
                context = {}
                service.search(
                    q["query"], top_k=5, domain="infra", strategy="hybrid", context_pack=context
                )
                answer = generate_answer(
                    q, context, replace(service.settings, query_language="none"), model
                )
                row = {"arm": arm, "question": q, "context": context, "generation": answer}
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                stream.flush()
                print(arm, q["id"], flush=True)


if __name__ == "__main__":
    main()
