"""Dev-only English/bilingual query ablation, without altering questions, answers or corpus."""

import argparse
import json
from pathlib import Path
from time import perf_counter

from benchmark_official import implementation_hash, verify_snapshot
from operation_log import ROOT, record_operation

from infra_rag.benchmarking import canonical_hash, create_run, digest, validate_dataset, write_new
from infra_rag.config import Settings
from infra_rag.legacy_model_clients import AnthropicClient
from infra_rag.offline_evaluation import evaluation_rows, summarize
from infra_rag.service import RetrievalService

TRANSLATION_PROMPT = (
    "Translate the user's technical retrieval question into English. Do not answer it. "
    "Preserve every product/version, code/API identifier, condition, negation and uncertainty. "
    "Do not add facts, evidence or an inferred answer. Return only a JSON object with one "
    'nonempty string field: {"english_query":"translated question"}.'
)


def translate(question, model):
    messages = [
        {"role": "system", "content": TRANSLATION_PROMPT},
        {"role": "user", "content": question["query"]},
    ]
    started = perf_counter()
    raw = model.generate(messages)
    obj = json.loads(raw)
    english = obj.get("english_query") if isinstance(obj, dict) else None
    if not isinstance(english, str) or not english.strip() or len(english) > 2000:
        raise ValueError("Invalid English query; stop rather than silently substituting an answer")
    return {
        "id": question["id"],
        "original_query": question["query"],
        "english_query": english.strip(),
        "messages": messages,
        "raw": raw,
        "provider_response": model.last_call,
        "latency_ms": (perf_counter() - started) * 1000,
    }


class ExpandedRetrieval:
    def __init__(self, service, rewrites, mode):
        self.service, self.rewrites, self.mode = service, rewrites, mode

    def __getattr__(self, name):
        return getattr(self.service, name)

    @property
    def settings(self):
        return self.service.settings

    @settings.setter
    def settings(self, settings):
        self.service.settings = settings

    def search(self, query, **kwargs):
        english = self.rewrites.get(query)
        expanded = (
            (english if self.mode == "english" else f"{query}\n{english}") if english else query
        )
        result = self.service.search(expanded, **kwargs)
        if kwargs.get("diagnostics") is not None:
            kwargs["diagnostics"]["query_expansion"] = {
                "original": query,
                "actual": expanded,
                "mode": self.mode,
            }
        return result


def query_report(summary):
    lines = [
        "# Dev 查询语言消融",
        "",
        "检索实验；尚未进行人工回答评分。",
        "",
        "| 配置 | Recall@5 | MRR@10 | nDCG@10 | 完整证据交付 |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, result in summary["summaries"].items():
        if "5" not in result["at_k"]:
            continue
        lines.append(
            f"| {name} | {result['at_k']['5']['recall']:.4f} | "
            f"{result['at_k']['10']['mrr']:.4f} | "
            f"{result['at_k']['10']['ndcg']:.4f} | "
            f"{result['context_complete_ci95']['mean']:.4f} |"
        )
    lines.extend(["", "计时：" + summary["latency_scope"], "", *summary["notes"]])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=["english", "bilingual"], required=True)
    parser.add_argument("--rewrites", type=Path)
    parser.add_argument("--env-file", type=Path, default=Path(".env.llm"))
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text())
    if protocol["implementation_sha256"] != implementation_hash():
        raise ValueError("Freeze current retrieval implementation before the dev ablation")
    dataset = Path(protocol["dataset"])
    corpus, splits = validate_dataset(dataset, ROOT, formal=True)
    assert digest(dataset / "dataset-manifest.json") == protocol["dataset_manifest_sha256"]
    assert digest(dataset / "corpus-manifest.json") == protocol["corpus_manifest_sha256"]
    for model in protocol["models"].values():
        verify_snapshot(model)
    questions = splits["dev"]
    out = create_run(
        args.output,
        {
            "kind": "dev_query_ablation",
            "protocol_sha256": digest(args.protocol),
            "mode": args.mode,
            "script_sha256": digest(Path(__file__)),
        },
    )
    if args.rewrites:
        records = [json.loads(line) for line in args.rewrites.read_text().splitlines()]
        write_new(
            out / "rewrite-source.json",
            {"path": str(args.rewrites), "sha256": digest(args.rewrites)},
        )
    else:
        model = AnthropicClient.from_environment(
            path=args.env_file,
            model="deepseek-flash",
            base_url="https://api.deepseek.com/anthropic",
            max_tokens=220,
        )
        write_new(out / "rewrite-model.json", model.configuration())
        records = []
        with (out / "query-rewrites.jsonl").open("x") as stream:
            for question in questions:
                record = translate(question, model)
                records.append(record)
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
                stream.flush()
                print("translated", record["id"], flush=True)
    assert len(records) == len(questions) == 60
    by_id = {r["id"]: r for r in records}
    assert set(by_id) == {q["id"] for q in questions}
    assert all(by_id[q["id"]]["original_query"] == q["query"] for q in questions)
    translations = {r["original_query"]: r["english_query"] for r in records}
    settings = Settings(
        **protocol["settings"],
        data_dir=ROOT
        / "data/official-evals/indexes"
        / canonical_hash([corpus["corpus_sha256"], protocol["settings"]])[:24],
    )
    service = RetrievalService(settings)
    service.ingest(ROOT / corpus["corpus_root"], "infra")
    from dataclasses import replace

    for variant in protocol["variants"]:
        service.settings = replace(service.settings, rerank=variant.endswith("_rerank"))
        service.search("KV cache memory", top_k=10, strategy=variant.replace("_rerank", ""))
    wrapper = ExpandedRetrieval(service, translations, args.mode)
    rows = []
    with (out / "rows.jsonl").open("x") as stream:
        for row in evaluation_rows(wrapper, questions, dataset, variants=protocol["variants"]):
            row["query_expansion"] = by_id[row["id"]]["english_query"]
            rows.append(row)
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            stream.flush()
            print(row["review_key"], flush=True)
    summary = {
        "status": "dev_query_ablation",
        "mode": args.mode,
        "summaries": summarize(rows),
        "by_type": {
            kind: summarize([r for r in rows if r["question_type"] == kind])
            for kind in sorted({r["question_type"] for r in rows})
        },
        "human_answers": None,
        "latency_scope": "warm retrieval; excludes separate query translation",
        "notes": [
            "Only dev queries translated; no answers or gold evidence supplied to translator.",
            "Questions/labels/corpus are unchanged; translations are not ingested.",
            "This is retrieval-only tuning, not an answer quality score.",
        ],
    }
    write_new(out / "summary.json", summary)
    (out / "report.md").write_text(query_report(summary))
    record_operation(
        "完成英文查询改写检索消融",
        "验证中文问题与英文语料的语言匹配",
        f"{args.mode} dev60×4=240条；独立输出{out}",
        "AI生成翻译未独立人工评审；仅dev调优，不是holdout或回答质量成绩",
    )


if __name__ == "__main__":
    main()
