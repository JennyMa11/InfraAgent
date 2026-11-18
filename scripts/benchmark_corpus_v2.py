"""Dev-only preprocessing/quota/language/version ablations and fixed answer samples."""

import argparse
import copy
import json
from dataclasses import replace
from pathlib import Path

from prepare_corpus_v2 import OUT, ROOT, build, load_unprocessed_banks, prepare

from infra_rag.benchmarking import digest, validate_dataset
from infra_rag.context import pack_context
from infra_rag.legacy_model_clients import AnthropicClient
from infra_rag.offline_evaluation import (
    answer_review_template,
    enrich_questions,
    evaluation_rows,
    generate_answer,
    review_markdown,
    summarize,
)
from infra_rag.partitioned import PartitionedRetrieval
from infra_rag.query_expansion import ExpandedRetrieval, load_rewrites


class MemoizedRetrieval:
    """Reuse a frozen top10 ranking to measure top5 delivery, without reranking twice."""

    def __init__(self, service):
        self.service, self.cached = service, None

    def __getattr__(self, name):
        return getattr(self.service, name)

    @property
    def settings(self):
        return self.service.settings

    @settings.setter
    def settings(self, value):
        self.service.settings = value

    def search(self, query, **kwargs):
        key = (str(query), kwargs.get("domain"), kwargs.get("modality"), kwargs.get("strategy"))
        if kwargs["top_k"] == 5 and self.cached and self.cached[0] == key:
            hits = copy.deepcopy(self.cached[1][:5])
            encoder = self._encoder()
            packed = pack_context(
                hits,
                self.parent_index,
                encoder.token_length if hasattr(encoder, "token_length") else len,
                self.settings.context_tokens,
                self.settings.context_chars,
                kwargs.get("domain"),
                kwargs.get("modality"),
            )
            decorate = getattr(self.service, "decorate_context", None)
            if decorate is not None:
                decorate(packed)
            kwargs["context_pack"].update(packed)
            return hits
        hits = self.service.search(query, **kwargs)
        if kwargs["top_k"] == 10:
            self.cached = (key, copy.deepcopy(hits))
        return hits


def repo_questions():
    dataset = ROOT / "evals/repository-benchmark"
    qs = json.loads((dataset / "dev.json").read_text())
    enriched = []
    for q in qs:
        enriched.append(
            {
                **q,
                "answerable": True,
                "evidence_alternatives": [{"spans": q["relevant_spans"]}],
                "answer_key": {"required_points": [q["expected_answer"]], "forbidden_claims": []},
            }
        )
    return dataset, enriched


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=["retrieval", "answers"], default="retrieval")
    parser.add_argument("--output", type=Path, default=OUT / "dev-v2")
    parser.add_argument("--suite", choices=["original", "routing"], default="original")
    args = parser.parse_args()
    if args.suite == "routing":
        from benchmark_routing_v2 import run_routing

        if args.output == OUT / "dev-v2":
            args.output = OUT / "routing-v2"
        run_routing(args)
        return
    directory = prepare()
    run = args.output
    run.mkdir(parents=True, exist_ok=True)
    official_dataset = ROOT / "evals/infra-official-v1-reviewed"
    _, splits = validate_dataset(official_dataset, ROOT, formal=True)
    official = splits["dev"]
    rewrites_path = official_dataset / "results/dev-opt-english-query-20261001/query-rewrites.jsonl"
    rewrites = load_rewrites(rewrites_path, official)
    repo_dataset, repositories = repo_questions()
    selected = json.loads((ROOT / "evals/merged-corpus-v1/dev-20261002/protocol.json").read_text())[
        "generation_ids"
    ]
    coverage_ids = json.loads(
        (ROOT / "evals/merged-corpus-v1/coverage-dev-20261002/protocol.json").read_text()
    )["ids"]
    if args.phase == "answers":
        rows = [json.loads(line) for line in (run / "rows.jsonl").read_text().splitlines()]
        model = AnthropicClient.from_environment(path=ROOT / ".env.llm", max_tokens=650)
        questions = {
            ("official", q["id"]): q for q in enrich_questions(official, official_dataset)
        } | {("repository", q["id"]): q for q in enrich_questions(repositories, repo_dataset)}
        answer_path = run / "answers.jsonl"
        answers = (
            [json.loads(x) for x in answer_path.read_text().splitlines()]
            if answer_path.exists()
            else []
        )
        done = {r["review_key"] for r in answers}
        with answer_path.open("a") as stream:
            for row in rows:
                wanted = (
                    row["dataset"] == "official"
                    and row["id"] in selected
                    and row["arm"] in {"raw_global30", "final"}
                ) or (
                    row["dataset"] == "repository"
                    and row["id"] in coverage_ids
                    and row["arm"] in {"raw_repo_chinese", "final"}
                )
                if not wanted or row["review_key"] in done:
                    continue
                q = questions[row["dataset"], row["id"]]
                row["generation"] = generate_answer(
                    q, row["context"], replace(answer_settings(), query_language="none"), model
                )
                answers.append(row)
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                stream.flush()
                print("answer", row["review_key"], flush=True)
        (run / "answer-review.json").write_text(
            json.dumps(answer_review_template(answers), ensure_ascii=False, indent=2)
        )
        (run / "answer-review.md").write_text(review_markdown(answers))
        return
    protocol = {
        "kind": "dev_only_v2_ablations",
        "directory": str(directory.relative_to(ROOT)),
        "manifest_sha256": digest(directory / "manifest.json"),
        "official_dev_sha256": digest(official_dataset / "dev.json"),
        "repo_dev_sha256": digest(repo_dataset / "dev.json"),
        "rewrites_sha256": digest(rewrites_path),
        "generation_ids": selected,
        "coverage_ids": coverage_ids,
        "top_k": [5, 10],
        "context_tokens": 1200,
        "context_chars": 4000,
        "arms": [
            "raw_global30",
            "processed_global30",
            "processed_global60",
            "raw_split",
            "processed_split",
            "processed_version",
            "final",
        ],
        "notes": [
            "original sparse evidence fixed; no gold-driven corpus modifications",
            "top5 pack reuses same frozen top10 ranking; avoids repeated ANN variability",
            "split30 per bank/channel and global60 both allow <=120 candidates",
            "AI source audit is excerpt-based and never ingested",
        ],
        "implementation": {
            str(p.relative_to(ROOT)): digest(p)
            for p in sorted((ROOT / "src/infra_rag").glob("*.py"))
        },
    }
    if (run / "protocol.json").exists():
        previous = json.loads((run / "protocol.json").read_text())
        if previous != protocol:
            import ast

            before, after = dict(previous), dict(protocol)
            before.pop("implementation")
            after.pop("implementation")
            equivalent = before == after
            for name, sha in previous["implementation"].items():
                archived = run / "implementation" / name
                if not archived.exists() or digest(archived) != sha:
                    equivalent = False
                    break
                equivalent = equivalent and ast.dump(ast.parse(archived.read_text())) == ast.dump(
                    ast.parse((ROOT / name).read_text())
                )
            if not equivalent:
                raise ValueError("Protocol changed; use a new --output directory")
    else:
        (run / "protocol.json").write_text(json.dumps(protocol, ensure_ascii=False, indent=2))
    processed, banks = build(directory)
    raw, raw_banks = load_unprocessed_banks()
    # Share local encoder/reranker to bound memory across independent collections.
    encoder = processed._encoder()
    for service in [raw, *banks.values(), *raw_banks.values()]:
        service.encoder = encoder

    def global_arm(base, k):
        base.settings = replace(base.settings, candidate_k=k)
        return ExpandedRetrieval(base, rewrites, "english")

    arms = [
        ("raw_global30", lambda: global_arm(raw, 30)),
        ("processed_global30", lambda: global_arm(processed, 30)),
        ("processed_global60", lambda: global_arm(processed, 60)),
        ("raw_split", lambda: PartitionedRetrieval(raw, raw_banks, rewrites)),
        ("processed_split", lambda: PartitionedRetrieval(processed, banks, rewrites)),
        (
            "processed_version",
            lambda: PartitionedRetrieval(processed, banks, rewrites, version_priority=True),
        ),
        (
            "final",
            lambda: PartitionedRetrieval(
                processed, banks, rewrites, version_priority=True, language_route=True
            ),
        ),
    ]
    path = run / "rows.jsonl"
    rows = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    done = {(r["dataset"], r["arm"], r["id"]) for r in rows}
    with path.open("a") as stream:
        for arm, factory in arms:
            wrapper = MemoizedRetrieval(factory())
            remaining = [q for q in official if ("official", arm, q["id"]) not in done]
            for row in (
                evaluation_rows(wrapper, remaining, official_dataset, variants=["hybrid_rerank"])
                if remaining
                else []
            ):
                row.update(arm=arm, dataset="official", review_key=f"official:{row['id']}:{arm}")
                rows.append(row)
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                stream.flush()
                print(arm, row["id"], flush=True)
            # Once loaded, share the same immutable reranker across arms.
            if processed.reranker is not None:
                raw.reranker = processed.reranker
            elif raw.reranker is not None:
                processed.reranker = raw.reranker
        # Check all repo dev queries in native Chinese to isolate preprocessing/split effects.
        for arm, wrapper in [
            ("raw_repo_chinese", raw_banks["community"]),
            ("raw_merged_chinese", raw),
            ("processed_merged_chinese", processed),
            (
                "final",
                PartitionedRetrieval(processed, banks, version_priority=True, language_route=True),
            ),
        ]:
            wrapper.settings = replace(wrapper.settings, rerank=True, candidate_k=30)
            remaining = [q for q in repositories if ("repository", arm, q["id"]) not in done]
            for row in (
                evaluation_rows(
                    MemoizedRetrieval(wrapper), remaining, repo_dataset, variants=["hybrid_rerank"]
                )
                if remaining
                else []
            ):
                row.update(
                    arm=arm, dataset="repository", review_key=f"repository:{row['id']}:{arm}"
                )
                rows.append(row)
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                stream.flush()
                print(arm, row["id"], flush=True)
    summary = {}
    for dataset, arm in dict.fromkeys((r["dataset"], r["arm"]) for r in rows):
        summary[f"{dataset}:{arm}"] = summarize(
            [r for r in rows if r["dataset"] == dataset and r["arm"] == arm]
        )["hybrid_rerank"]
    (run / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))


def answer_settings():
    from infra_rag.config import Settings

    return Settings()


if __name__ == "__main__":
    main()
