"""Frozen 24-document chunk pilot; local tokenizers only, no retrieval or model inference."""

import argparse
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path

from operation_log import ROOT, record_operation
from prepare_corpus_pilot import load, save

from infra_rag.benchmarking import digest
from infra_rag.structural_pilot import (
    LIMIT,
    VERSION,
    chunk_document,
    select_documents,
    validate_document,
)

MODEL_PROTOCOL = ROOT / "evals/merged-corpus-v2/original-rag-v7/run-20261003-v3/protocol.json"


def run(source, output):
    for name, expected in load(source / "artifacts-manifest.json").items():
        if digest(source / name) != expected:
            raise ValueError("Expanded source artifact changed: " + name)
    rows = load(source / "selected.json")
    artifacts = {
        r["document_id"]: load(source / "documents" / (r["document_id"] + ".json")) for r in rows
    }
    pilot = select_documents(rows, artifacts)
    if len(pilot) != 24 or len({r["repository"] for r in pilot}) != 12:
        raise ValueError("Expected two documents per source, 24 total")
    from transformers import AutoTokenizer

    models = load(MODEL_PROTOCOL)["models"]
    counters, identities = {}, {}
    for name in ("embedding", "reranker"):
        spec = models[name]
        files = {
            p: expected
            for p, expected in spec["files"].items()
            if "token" in p or p in {"vocab.txt", "config.json", "sentence_bert_config.json"}
        }
        for path, expected in files.items():
            if digest(Path(spec["path"]) / path) != expected:
                raise ValueError("Tokenizer snapshot differs")
        tokenizer = AutoTokenizer.from_pretrained(spec["path"], local_files_only=True)
        counters[name] = lambda text, tokenizer=tokenizer: len(
            tokenizer.encode(text, add_special_tokens=False)
        )
        if LIMIT + 128 + tokenizer.num_special_tokens_to_add(pair=True) > min(
            tokenizer.model_max_length, 512
        ):
            raise ValueError("Reserved query budget incompatible with tokenizer")
        identities[name] = {
            "model": spec["model"],
            "path": spec["path"],
            "files": files,
            "query_reserve": 128,
            "native_max_length": tokenizer.model_max_length,
        }
    implementation = [Path(__file__).resolve(), ROOT / "src/infra_rag/structural_pilot.py"]
    protocol = {
        "version": VERSION,
        "source": str(source.relative_to(ROOT)),
        "source_manifest_sha256": digest(source / "artifacts-manifest.json"),
        "model_protocol_sha256": digest(MODEL_PROTOCOL),
        "tokenizers": identities,
        "limit_including_heading": LIMIT,
        "documents": 24,
        "seed": 42,
        "query_budget_note": (
            "conditional budget for future queries <=128 tokens; no query executed"
        ),
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in implementation},
        "model_inference_calls": 0,
        "indexed": False,
        "retrieval_evaluated": False,
    }
    save(output / "protocol.json", protocol)
    for path in implementation:
        target = output / "implementation" / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and digest(target) != digest(path):
            raise ValueError("Implementation snapshot changed")
        if not target.exists():
            shutil.copy2(path, target)
    save(output / "selection.json", pilot)
    summaries = []
    previews = [
        "# 结构分块验证",
        "",
        "24份自动通过正文，12个来源各2份；不是检索或回答准确率实验。",
        "",
        (
            "正文和标题共同接受两种tokenizer的350 token上限检查；"
            "不适合拆开的超限单元保留在父章节并登记deferred。"
        ),
        "字段context_unit_ids指向需要补读的邻近条件或说明，不代表人工确认的语义必要证据。",
        "",
    ]
    for row in pilot:
        cid = row["document_id"]
        prepared = artifacts[cid]
        cleaned = source / "cleaned" / (cid + ".md")
        if hashlib.sha256(prepared["text"].encode()).hexdigest() != digest(cleaned):
            raise ValueError("Prepared and cleaned text differ")
        result = chunk_document(row, prepared, counters)
        first = validate_document(prepared, result, counters)
        if result != chunk_document(row, prepared, counters):
            raise ValueError("Chunk output not deterministic")
        save(output / "documents" / (cid + ".json"), result)
        summaries.append({"document_id": cid, "repository": row["repository"], **first})
        previews += [
            f"## {row['repository']} / {row['relative_path']}",
            "",
            f"子块{len(result['children'])}；超限保留片段{len(result['deferred'])}；[完整记录](documents/{cid}.json)",
            "",
        ]
        for child in sorted(
            result["children"], key=lambda c: (-c["needs_parent_context"], c["chunk_id"])
        )[:2]:
            previews += [
                f"### {child['chunk_id']} · tokens={child['token_counts']}",
                "",
                f"需要父上下文：{child['needs_parent_context']}",
                "",
                child["content"],
                "",
            ]
    totals = {
        key: sum(r[key] for r in summaries)
        for key in summaries[0]
        if key not in {"document_id", "repository"}
    }
    if (
        totals["child_body_characters"] + totals["deferred_characters"]
        != totals["unit_body_characters"]
    ):
        raise ValueError("Coverage accounting mismatch")
    summary = {
        "documents": 24,
        "repositories": dict(Counter(r["repository"] for r in pilot)),
        "totals": totals,
        "child_character_coverage": totals["child_body_characters"]
        / totals["unit_body_characters"],
        "source_accounting_including_deferred": 1.0,
        "token_limit_violations": 0,
        "human_review": "pending",
        "adopted": False,
        "indexed": False,
        "per_document": summaries,
    }
    save(output / "validation.json", summary)
    save(
        output / "human-review-template.json",
        [
            {
                "document_id": r["document_id"],
                "repository": r["repository"],
                "status": "pending",
                "reviewer": None,
                "reason": None,
                "checks": dict.fromkeys(
                    [
                        "conditions",
                        "code_descriptions",
                        "tables",
                        "source_mapping",
                        "deferred_handling",
                    ]
                ),
            }
            for r in pilot
        ],
    )
    text = "\n".join(previews) + "\n"
    report = output / "README.md"
    if report.exists() and report.read_text() != text:
        raise ValueError("Preview changed")
    report.write_text(text)
    for name, expected in load(source / "artifacts-manifest.json").items():
        if digest(source / name) != expected:
            raise ValueError("Source mutated")
    save(
        output / "artifacts-manifest.json",
        {
            p.relative_to(output).as_posix(): digest(p)
            for p in sorted(output.rglob("*"))
            if p.is_file() and p.name != "artifacts-manifest.json"
        },
    )
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        summary = run(args.source.resolve(), args.output.resolve())
        record_operation(
            "结构分块与token边界验证",
            "下一步验证来源、条件及保护单元完整性，不接入线上索引",
            f"产物{args.output}；{summary['totals']}；覆盖率{summary['child_character_coverage']:.3f}",
            "超限单元单独保留，人工审核pending；不代表检索或回答质量",
        )
        print(
            json.dumps(
                {k: v for k, v in summary.items() if k != "per_document"}, ensure_ascii=False
            )
        )
    except Exception as exc:
        record_operation("分块验证失败", "保留失败，不改原文", str(args.output), str(exc))
        raise


if __name__ == "__main__":
    main()
