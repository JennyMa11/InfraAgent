"""Materialize AI-authored candidates; import explicit human review into a new frozen version."""

import argparse
import random
import re
from collections import Counter
from pathlib import Path

from operation_log import ROOT, record_operation
from prepare_official_benchmark import DATASET

from infra_rag.benchmarking import canonical_hash, digest, load_json, validate_dataset, write_new


def locate_span(doc, anchor, corpus):
    text = (corpus / doc["source"]).read_text()
    pattern = r"\s+".join(re.escape(word) for word in anchor.split())
    matches = list(re.finditer(pattern, text))
    if len(matches) != 1:
        raise ValueError(f"anchor must be unique in {doc['id']}: {anchor}: {len(matches)} matches")
    match = matches[0]
    support = match.group()
    return {
        "document_id": doc["id"],
        "source": "../../" + str((corpus / doc["source"]).relative_to(ROOT)),
        "text": support,
        "sha256": doc["sha256"],
        "commit": doc.get("commit"),
        "release": doc["release"],
        "line_start": text.count("\n", 0, match.start()) + 1,
        "line_end": text.count("\n", 0, match.end()) + 1,
        "source_url": doc["url"],
        "coordinate": "normalized frozen document lines",
    }


def question_review_template(questions):
    return [
        {
            "id": q["id"],
            "question_sha256": canonical_hash(
                {key: value for key, value in q.items() if key != "review"}
            ),
            "status": "pending",
            "method": "independent_human",
            "reviewer": "",
            "reviewed_at": "",
            "notes": "",
        }
        for q in questions
    ]


def save_dataset(output, manifest, splits, *, reviews=None):
    if output.exists() and any(
        (output / name).exists() for name in ("dev.json", "holdout.json", "dataset-manifest.json")
    ):
        raise FileExistsError("dataset already exists; use a new version directory")
    if not (output / "corpus-manifest.json").exists():
        write_new(output / "corpus-manifest.json", manifest)
    for split, rows in splits.items():
        write_new(output / f"{split}.json", rows)
    record = {
        "version": output.name,
        "questions": sum(map(len, splits.values())),
        "seed": 42,
        "split_unit": "whole scenario groups, shared evidence and paraphrases",
        "corpus_manifest_sha256": digest(output / "corpus-manifest.json"),
        "annotation_method": "AI authored; approval requires independent human review",
        "splits": {
            name: {
                "questions": len(rows),
                "sha256": digest(output / f"{name}.json"),
                "types": dict(Counter(q["question_type"] for q in rows)),
            }
            for name, rows in splits.items()
        },
    }
    if reviews:
        record["imported_reviews_sha256"] = digest(reviews)
        record["imported_reviews_file"] = "imported-question-review.json"
        with (output / record["imported_reviews_file"]).open("xb") as stream:
            stream.write(reviews.read_bytes())
    write_new(output / "dataset-manifest.json", record)
    write_new(
        output / "question-review.json",
        load_json(reviews)
        if reviews
        else question_review_template([q for rows in splits.values() for q in rows]),
    )
    export_review(output, splits)


def export_review(output, splits):
    lines = [
        "# 领域题集独立人工审核",
        "",
        "题目由AI编写。核对版本、原文、答案要点和证据后填写 question-review.json。",
        "未审核时保持pending；争议题需修订并建立新版本。",
        "",
    ]
    for split, questions in splits.items():
        for q in questions:
            lines.extend(
                [
                    f"## {q['id']} · {split} · {q['question_type']}",
                    "",
                    q["query"],
                    "",
                    "条件：" + str(q["conditions"]),
                    "",
                    "参考要点：" + "；".join(q["answer_key"]["required_points"]),
                    "",
                    "禁止误读：" + "；".join(q["answer_key"]["forbidden_claims"]),
                    "",
                ]
            )
            if not q["answerable"]:
                lines.extend(
                    [
                        "证据缺失理由：" + q["missing_information"],
                        "",
                        "须审查冻结语料，不能依据检索失败判定。",
                        "",
                    ]
                )
            for group in q["evidence_alternatives"]:
                lines.extend(["证据组（组内全部需要）：" + group["id"], ""])
                for span in group["spans"]:
                    lines.extend(
                        [
                            span["source_url"],
                            "",
                            f"规范化行 {span['line_start']}-{span['line_end']}；"
                            f"SHA256 {span['sha256']}",
                            "",
                            "```text",
                            span["text"],
                            "```",
                            "",
                        ]
                    )
    with (output / "human-review.md").open("x", encoding="utf-8") as stream:
        stream.write("\n".join(lines) + "\n")


def build(dataset=DATASET):
    if dataset.resolve().parent != (ROOT / "evals").resolve():
        raise ValueError("dataset versions must be direct children of evals")
    manifest = load_json(dataset / "corpus-manifest.json")
    documents = {doc["id"]: doc for doc in manifest["documents"]}
    corpus = ROOT / manifest["corpus_root"]
    seeds = load_json(dataset / "question-seeds.json")
    groups = []
    for i, seed in enumerate(seeds):
        doc = documents[seed["document_id"]]
        spans = [
            locate_span(documents[ref["document_id"]], ref["text"], corpus)
            for ref in seed["supports"]
        ]
        questions = []
        for j, authored in enumerate(seed["questions"]):
            answerable = authored["type"] != "unanswerable"
            selected = spans if authored["type"] == "multi_hop" else spans[:1]
            question = {
                "id": f"official-{i + 1:03d}-{j + 1}",
                "group_id": seed["group_id"],
                "query": authored["query"],
                "question_type": authored["type"],
                "domain": "infra",
                "modality": "text",
                "answerable": answerable,
                "conditions": {
                    "project": doc["project"],
                    "release": doc["release"],
                    "hardware": seed.get("hardware", "not specified; do not infer"),
                },
                "answer_key": {
                    "required_points": authored.get("points", seed["points"])
                    if answerable
                    else ["缺少测量或环境信息，不能推断精确答案。"],
                    "forbidden_claims": authored.get("forbidden", seed["forbidden"])
                    if answerable
                    else ["编造未提供的配置、测量值或运行日志。"],
                },
                "expected_answer": "；".join(authored.get("points", seed["points"]))
                if answerable
                else "冻结资料缺少这台机器的测量或环境信息，无法可靠确定。",
                "relevant_spans": selected if answerable else [],
                "evidence_alternatives": [{"id": "primary", "spans": selected}]
                if answerable
                else [],
                "reasoning_steps": authored.get("reasoning_steps", []) if answerable else [],
                "missing_information": authored.get("missing_information", "")
                if not answerable
                else "",
                "review": {
                    "status": "pending",
                    "method": "AI-authored",
                    "reviewer": "",
                    "reviewed_at": "",
                    "notes": "",
                },
                "annotation_method": "Codex-authored from frozen official source; not human gold",
            }
            questions.append(question)
        groups.append(questions)
    if len(groups) != 30 or any(len(group) != 4 for group in groups):
        raise ValueError("expected 30 scenario groups of four questions")
    # Pair groups with the same type composition, then seed which member enters dev.
    # Each pair has four questions; 15 whole pairs produce exactly 60/60 and 6 negatives each.
    rng = random.Random(42)
    splits = {"dev": [], "holdout": []}
    for i in range(0, len(groups), 2):
        pair = groups[i : i + 2]
        rng.shuffle(pair)
        splits["dev"].extend(pair[0])
        splits["holdout"].extend(pair[1])
    save_dataset(dataset, manifest, splits)
    validate_dataset(dataset, ROOT)
    record_operation(
        "生成120题官方语料候选集",
        "补充版本条件、否定、代码、排障和拒答评测",
        "dev60/holdout60，30场景组，全部pending",
        "需要独立人工审核；未运行holdout",
    )


def review(args):
    if args.output.resolve().parent != args.dataset.resolve().parent:
        raise ValueError("reviewed version must be a sibling directory to preserve source locators")
    manifest, splits = validate_dataset(args.dataset, ROOT)
    reviews = load_json(args.reviews)
    rows = [q for questions in splits.values() for q in questions]
    by_id = {q["id"]: q for q in rows}
    seen = set()
    for record in reviews:
        q = by_id.get(record["id"])
        if q is None or record["id"] in seen:
            raise ValueError("unknown or duplicate question review")
        seen.add(record["id"])
        question_hash = canonical_hash({k: v for k, v in q.items() if k != "review"})
        if question_hash != record["question_sha256"]:
            raise ValueError("review is for a different question revision")
        if record["status"] not in {"pending", "approved", "rejected", "disputed"}:
            raise ValueError("unknown review status")
        if record["status"] == "approved":
            if (
                record.get("method") != "independent_human"
                or not record.get("reviewer")
                or not record.get("reviewed_at")
                or not record.get("notes")
            ):
                raise ValueError("explicit human reviewer, time and rationale required")
        q["review"] = {k: v for k, v in record.items() if k not in ("id", "question_sha256")}
    if len(seen) != len(rows):
        raise ValueError("review ledger must include every question, including pending ones")
    save_dataset(args.output, manifest, splits, reviews=args.reviews)
    validate_dataset(args.output, ROOT)
    print(
        "Created new dataset version; all review decisions and the original ledger were preserved"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    built = commands.add_parser("build")
    built.add_argument("--dataset", type=Path, default=DATASET)
    imported = commands.add_parser("import-review")
    imported.add_argument("--dataset", type=Path, default=DATASET)
    imported.add_argument("--reviews", type=Path, required=True)
    imported.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "build":
        build(args.dataset)
    else:
        review(args)


if __name__ == "__main__":
    main()
