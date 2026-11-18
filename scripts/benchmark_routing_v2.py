"""Frozen-candidate, dev-only routing and bounded version/metadata ablations."""

import copy
import json
from dataclasses import replace
from pathlib import Path

from benchmark_corpus_v2 import MemoizedRetrieval, answer_settings, repo_questions
from operation_log import record_operation
from prepare_corpus_v2 import OUT, ROOT, build, prepare

from infra_rag.benchmarking import canonical_hash, digest, validate_dataset
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

ARMS = {
    "recall_en_rerank_en": ("english", "english", "top10", False),
    "recall_en_rerank_by_collection": ("english", "by_collection", "top10", False),
    "recall_zh_rerank_en": ("original", "english", "top10", False),
    "recall_zh_rerank_by_collection": ("original", "by_collection", "top10", False),
    "version_all": ("original", "english", "all", False),
    "version_all_metadata": ("original", "english", "all", True),
}


class FrozenReranker:
    """Replay identical model inputs when only version selection changes."""

    def __init__(self, model, name, directory):
        self.model, self.name, self.directory = model, name, directory
        directory.mkdir(parents=True, exist_ok=True)

    def __getattr__(self, name):
        return getattr(self.model, name)

    def predict(self, pairs):
        path = self.directory / f"{canonical_hash([self.name, pairs])}.json"
        if path.exists():
            return json.loads(path.read_text())
        scores = [float(score) for score in self.model.predict(pairs)]
        path.write_text(json.dumps(scores))
        return scores


class SnapshotRetrieval:
    """Persist one candidate set per question/recall language and reuse across rerank arms."""

    def __init__(self, service, directory):
        self.service, self.directory = service, directory
        directory.mkdir(parents=True, exist_ok=True)

    def __getattr__(self, name):
        return getattr(self.service, name)

    @property
    def settings(self):
        return self.service.settings

    @settings.setter
    def settings(self, value):
        self.service.settings = value

    def search(self, query, **kwargs):
        identity = canonical_hash(
            [
                str(query),
                self.service.rewrites.get(str(query), str(query)),
                self.service.community_recall_language,
                kwargs.get("domain"),
                kwargs.get("modality"),
                kwargs.get("strategy"),
            ]
        )
        path = self.directory / f"{identity}.json"
        snapshot = json.loads(path.read_text()) if path.exists() else {}
        hits = self.service.search(query, candidate_snapshot=snapshot, **kwargs)
        if not path.exists():
            path.write_text(json.dumps(snapshot, ensure_ascii=False))
        if kwargs.get("diagnostics") is not None:
            kwargs["diagnostics"]["candidate_snapshot"] = {
                "path": str(path.relative_to(self.directory.parent.parent)),
                "sha256": digest(path),
            }
        return hits


def write_protocol(run, protocol):
    path = run / "protocol.json"
    if path.exists():
        if json.loads(path.read_text()) != protocol:
            raise ValueError("Protocol changed; use a new --output directory")
        return
    path.write_text(json.dumps(protocol, ensure_ascii=False, indent=2))
    for name in protocol["implementation"]:
        target = run / "implementation" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())


def comparison(rows):
    result = {}
    for dataset, arm in dict.fromkeys((r["dataset"], r["arm"]) for r in rows):
        selected = [r for r in rows if r["dataset"] == dataset and r["arm"] == arm]
        positive = [r for r in selected if r["answerable"]]
        by_collection = {"official": 0, "community": 0, "unknown": 0}
        for row in positive:
            # Count the actually selected Top5, including version promotion.
            metadata = {
                e["chunk_id"]: e.get("metadata", {}) for e in row["ranking_context"]["evidence"]
            }
            for cid in row["retrieved"][:5]:
                name = row["diagnostics"].get("candidate_collections", {}).get(cid)
                name = name or metadata.get(cid, {}).get("collection", "unknown")
                by_collection[name if name in by_collection else "unknown"] += 1
        result[f"{dataset}:{arm}"] = {
            "n": len(positive),
            "candidate_complete": sum(r["candidate_complete"] for r in positive),
            "top5_complete": sum(r["at_k"]["5"]["complete_evidence_hit"] for r in positive),
            "delivered_complete": sum(r["delivered"]["complete"] for r in positive),
            "top5_collections": by_collection,
            "succeeded_ids": [r["id"] for r in positive if r["delivered"]["complete"]],
            "candidate_missing_ids": [r["id"] for r in positive if not r["candidate_complete"]],
        }
    for dataset in ("official", "repository"):
        baseline = set(result[f"{dataset}:processed_global30"]["succeeded_ids"])
        for arm in ARMS:
            item = result[f"{dataset}:{arm}"]
            success = set(item["succeeded_ids"])
            item.update(
                lost_ids=sorted(baseline - success), recovered_ids=sorted(success - baseline)
            )
    return result


def write_report(run, rows):
    summary = {
        f"{dataset}:{arm}": summarize(
            [r for r in rows if r["dataset"] == dataset and r["arm"] == arm]
        )["hybrid_rerank"]
        for dataset, arm in dict.fromkeys((r["dataset"], r["arm"]) for r in rows)
    }
    (run / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    stats = comparison(rows)
    (run / "comparison.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2))
    lines = [
        "# 中文路由独立消融与第一轮修复",
        "",
        "固定dev、冻结英文译文、真实BGE模型；每种召回语言只生成一次候选。",
        "官方60题中54题可回答；中文仓库50题原生中文，无冻结英文译文，语言对照为回退条件。",
        "Top5、正文预算1200 token/4000字符不变；元数据提示增加的输入开销另计。",
        "",
        "| 数据集／配置 | 完整候选 | Top5完整 | 完整交付 | Top5官方／社区／未知 |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, item in stats.items():
        counts = "/".join(str(v) for v in item["top5_collections"].values())
        lines.append(
            f"| {name} | {item['candidate_complete']:g}/{item['n']} | "
            f"{item['top5_complete']:g}/{item['n']} | "
            f"{item['delivered_complete']:g}/{item['n']} | {counts} |"
        )
    acceptance = {
        arm: {
            "official_delivery_ge_43": stats[f"official:{arm}"]["delivered_complete"] >= 43,
            "repository_delivery_ge_40": stats[f"repository:{arm}"]["delivered_complete"] >= 40,
            "human_fact_review": "pending",
            "default_changed": False,
        }
        for arm in ARMS
    }
    (run / "acceptance.json").write_text(json.dumps(acceptance, ensure_ascii=False, indent=2))
    lines.extend(
        [
            "",
            "逐题得失见 comparison.json；完整排名和交付证据见 rows.jsonl。",
            "候选完整与交付均基于原始稀疏来源标签，不等于回答正确率。",
            "版本all仅扩大检查范围，至多保护2段；不保证多条件完整。",
            "材料未改写或隔离；默认global30保持不变；独立人工事实审核尚未完成。",
        ]
    )
    (run / "report.md").write_text("\n".join(lines) + "\n")
    record_operation(
        "完成中文召回/重排独立消融与版本/元数据实验",
        "定位候选完整但最终证据丢失的退化环节",
        f"结果{run.resolve()}；比较hash {canonical_hash(stats)}；默认global30不变",
        "原始gold稀疏；中文组缺英文译文；事实正确性待独立人工审核",
    )


def generate_samples(run, rows, official, repositories, official_dataset, repo_dataset):
    protocol = json.loads((run / "protocol.json").read_text())
    model = AnthropicClient.from_environment(path=ROOT / ".env.llm", max_tokens=650)
    (run / "generation-model.json").write_text(
        json.dumps(model.configuration(), ensure_ascii=False, indent=2)
    )
    questions = {("official", q["id"]): q for q in enrich_questions(official, official_dataset)} | {
        ("repository", q["id"]): q for q in enrich_questions(repositories, repo_dataset)
    }
    path = run / "answers.jsonl"
    answers = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    done = {r["review_key"] for r in answers}
    with path.open("a") as stream:
        for original in rows:
            ids = protocol[
                "generation_ids" if original["dataset"] == "official" else "coverage_ids"
            ]
            if (
                original["id"] not in ids
                or original["arm"]
                not in {"processed_global30", "version_all", "version_all_metadata"}
                or original["review_key"] in done
            ):
                continue
            row = copy.deepcopy(original)
            row["generation"] = generate_answer(
                questions[row["dataset"], row["id"]],
                row["context"],
                replace(answer_settings(), query_language="none"),
                model,
            )
            answers.append(row)
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            stream.flush()
            print("answer", row["review_key"], row["generation"]["error"], flush=True)
    (run / "answer-review.json").write_text(
        json.dumps(answer_review_template(answers), ensure_ascii=False, indent=2)
    )
    (run / "answer-review.md").write_text(review_markdown(answers))
    (run / "generation-summary.json").write_text(
        json.dumps(
            {
                "calls": len(answers),
                "errors": sum(bool(r["generation"]["error"]) for r in answers),
                "format_valid": sum(r["generation"]["checks"]["format_valid"] for r in answers),
                "citation_ids_valid": sum(
                    r["generation"]["checks"]["citation_ids_valid"] for r in answers
                ),
                "fact_correct": None,
                "independent_human_review": "pending",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def run_routing(args):
    run = args.output
    run.mkdir(parents=True, exist_ok=True)
    official_dataset = ROOT / "evals/infra-official-v1-reviewed"
    _, splits = validate_dataset(official_dataset, ROOT, formal=True)
    official = splits["dev"]
    repo_dataset, repositories = repo_questions()
    path = run / "rows.jsonl"
    rows = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    if args.phase == "answers":
        generate_samples(run, rows, official, repositories, official_dataset, repo_dataset)
        return
    directory = prepare()
    old = json.loads((OUT / "dev-v2/protocol.json").read_text())
    rewrites_path = official_dataset / "results/dev-opt-english-query-20261001/query-rewrites.jsonl"
    rewrites = load_rewrites(rewrites_path, official)
    sources = sorted((ROOT / "src/infra_rag").glob("*.py")) + [
        ROOT / "scripts/benchmark_corpus_v2.py",
        Path(__file__),
        ROOT / "scripts/prepare_corpus_v2.py",
    ]
    protocol = {
        "kind": "dev_only_independent_routing_v2",
        "directory": str(directory.relative_to(ROOT)),
        "manifest_sha256": digest(directory / "manifest.json"),
        "official_dev_sha256": digest(official_dataset / "dev.json"),
        "repo_dev_sha256": digest(repo_dataset / "dev.json"),
        "rewrites_sha256": digest(rewrites_path),
        "generation_ids": old["generation_ids"],
        "coverage_ids": old["coverage_ids"],
        "arms": ARMS,
        "baseline": "processed_global30",
        "top_k": [5, 10],
        "context_tokens": 1200,
        "context_chars": 4000,
        "models": {"embedding": "BAAI/bge-small-zh-v1.5", "reranker": "BAAI/bge-reranker-base"},
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in sources},
    }
    # JSON turns tuple arm definitions into lists; normalize before resume comparisons.
    protocol = json.loads(json.dumps(protocol))
    write_protocol(run, protocol)
    processed, banks = build(directory)
    processed.settings = replace(processed.settings, candidate_k=30)
    from sentence_transformers import CrossEncoder

    processed.reranker = FrozenReranker(
        CrossEncoder(processed.settings.reranker_model),
        processed.settings.reranker_model,
        run / "rerank-scores",
    )
    done = {(r["dataset"], r["arm"], r["id"]) for r in rows}
    with path.open("a") as stream:
        for dataset, questions, dataset_dir in [
            ("official", official, official_dataset),
            ("repository", repositories, repo_dataset),
        ]:
            for arm in ["processed_global30", *ARMS]:
                if arm == "processed_global30":
                    service = (
                        ExpandedRetrieval(processed, rewrites, "english")
                        if (dataset == "official")
                        else processed
                    )
                else:
                    recall, rerank, scope, metadata = ARMS[arm]
                    service = PartitionedRetrieval(
                        processed,
                        banks,
                        rewrites if dataset == "official" else {},
                        version_priority=True,
                        community_recall_language=recall,
                        rerank_language=rerank,
                        version_scope=scope,
                        include_metadata=metadata,
                    )
                    service = SnapshotRetrieval(service, run / "candidates" / dataset)
                remaining = [q for q in questions if (dataset, arm, q["id"]) not in done]
                for row in (
                    evaluation_rows(
                        MemoizedRetrieval(service),
                        remaining,
                        dataset_dir,
                        variants=["hybrid_rerank"],
                    )
                    if remaining
                    else []
                ):
                    row.update(dataset=dataset, arm=arm, review_key=f"{dataset}:{row['id']}:{arm}")
                    rows.append(row)
                    stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                    stream.flush()
                    print(dataset, arm, row["id"], flush=True)
    write_report(run, rows)
