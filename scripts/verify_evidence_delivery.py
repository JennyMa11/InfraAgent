"""Resolve all deferred spans on the frozen 24 docs and replay source-backed delivery."""

import argparse
import json
import shutil
from collections import defaultdict
from pathlib import Path

from operation_log import ROOT, record_operation
from prepare_corpus_pilot import load, save

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.evidence_delivery import VERSION, pack_delivery, resolve_deferred, validate_resolved


def run(source, output):
    for p, expected in load(source / "artifacts-manifest.json").items():
        if digest(source / p) != expected:
            raise ValueError("Frozen chunk source changed")
    old_protocol = load(source / "protocol.json")
    from transformers import AutoTokenizer

    counters = {}
    for name, spec in old_protocol["tokenizers"].items():
        for path, expected in spec["files"].items():
            if digest(Path(spec["path"]) / path) != expected:
                raise ValueError("Local tokenizer changed")
        tokenizer = AutoTokenizer.from_pretrained(spec["path"], local_files_only=True)
        counters[name] = lambda text, tokenizer=tokenizer: len(
            tokenizer.encode(text, add_special_tokens=False)
        )
    implementation = [Path(__file__).resolve(), ROOT / "src/infra_rag/evidence_delivery.py"]
    save(
        output / "protocol.json",
        {
            "version": VERSION,
            "source": str(source.relative_to(ROOT)),
            "source_manifest_sha256": digest(source / "artifacts-manifest.json"),
            "tokenizers": old_protocol["tokenizers"],
            "limit": 350,
            "new_fragment_char_limit": 1600,
            "delivery_tokens": 1200,
            "delivery_characters": 4000,
            "implementation": {str(p.relative_to(ROOT)): digest(p) for p in implementation},
            "scope": "controlled hit delivery replay, not search/answer evaluation",
            "indexed": False,
            "inference_calls": 0,
        },
    )
    for path in implementation:
        target = output / "implementation" / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and digest(target) != digest(path):
            raise ValueError("Implementation snapshot changed")
        if not target.exists():
            shutil.copy2(path, target)
    docs, checks, requests = [], [], []
    resolved_count = 0
    for row in load(source / "selection.json"):
        old = load(source / "documents" / (row["document_id"] + ".json"))
        new = resolve_deferred(old, counters, provenance=row)
        resolved_count += len(old["deferred"])
        checks.append(validate_resolved(old, new, counters))
        save(output / "documents" / (row["document_id"] + ".json"), new)
        docs.append(new)
        old_context = [c["chunk_id"] for c in old["children"] if c["needs_parent_context"]]
        continued = {}
        for c in new["children"]:
            if "continuation_group" in c:
                continued.setdefault(c["continuation_group"], c["chunk_id"])
        for cid in dict.fromkeys(
            old_context + list(continued.values()) + [new["children"][0]["chunk_id"]]
        ):
            requests.append(
                {
                    "case_id": canonical_hash([new["document_id"], cid])[:24],
                    "document_id": new["document_id"],
                    "hit_ids": [cid],
                }
            )
    save(output / "delivery-schedule.json", requests)
    case_results, examples = [], []
    for i, request in enumerate(requests):
        cursor, pages, delivered = None, [], []
        while True:
            page = pack_delivery(request["hit_ids"], docs, counters, cursor=cursor)
            if page["status"] == "blocked":
                raise ValueError("Unservable child under default delivery budgets")
            if page["used_characters"] > 4000 or any(
                v > 1200 for v in page["token_counts"].values()
            ):
                raise ValueError("Delivery budget overflow")
            if not page["answer_ready"] and not page["warning"]:
                raise ValueError("Partial delivery not disclosed")
            pages.append(page)
            delivered.extend(page["evidence"])
            if page["continuation"] is None:
                break
            if cursor and page["continuation"]["offset"] <= cursor["offset"]:
                raise ValueError("Non-progressing continuation")
            cursor = page["continuation"]
        required = pages[0]["required_chunk_ids"]
        if [e["chunk_id"] for e in delivered] != required:
            raise ValueError("Delivered pages lost or duplicated required chunks")
        by_unit = defaultdict(list)
        for e in delivered:
            for f in e["fragments"]:
                by_unit[(e["document_id"], f["unit_id"])].append(f["unit_char_range"])
        unit_map = {
            (d["document_id"], u["unit_id"]): u
            for d in docs
            for p in d["parents"]
            for u in p["units"]
        }
        for key in pages[0]["required_units"]:
            key = tuple(key)
            intervals = sorted(by_unit[key])
            end = 0
            for a, b in intervals:
                if a > end:
                    raise ValueError("Delivered unit has a source gap")
                end = max(end, b)
            if end != len(unit_map[key]["content"]):
                raise ValueError("Required original source unit not delivered in replay")
        trace = {
            **request,
            "pages": pages,
            "source_units_complete_across_returned_pages": True,
            "all_required_in_first_page": pages[0]["answer_ready"],
            "not_an_answer_accuracy_or_single_context_claim": True,
        }
        save(output / "delivery" / (request["case_id"] + ".json"), trace)
        case_results.append(
            {
                "case_id": request["case_id"],
                "pages": len(pages),
                "first_page_complete": pages[0]["answer_ready"],
            }
        )
        if len(pages) > 1 and len(examples) < 5:
            examples.append(request["case_id"])
        if (i + 1) % 50 == 0:
            print("delivery replay", i + 1, "/", len(requests), flush=True)
    summary = {
        "documents": len(docs),
        "old_deferred_resolved": resolved_count,
        "child_chunks": sum(c["children"] for c in checks),
        "new_continuation_children": sum(c["new_continuation_children"] for c in checks),
        "source_characters": sum(c["source_characters"] for c in checks),
        "source_character_coverage": 1.0,
        "remaining_deferred": 0,
        "delivery_cases": len(case_results),
        "multi_page_cases": sum(c["pages"] > 1 for c in case_results),
        "pages": sum(c["pages"] for c in case_results),
        "first_page_complete_cases": sum(c["first_page_complete"] for c in case_results),
        "full_source_coverage_across_replayed_pages": True,
        "token_or_character_budget_violations": 0,
        "actual_retrieval_evaluated": False,
        "indexed": False,
        "adopted": False,
        "human_review": "pending",
    }
    save(output / "validation.json", summary)
    save(output / "delivery-summary.json", case_results)
    save(
        output / "human-review-template.json",
        [
            {
                "document_id": d["document_id"],
                "status": "pending",
                "reviewer": None,
                "reason": None,
                "checks": dict.fromkeys(
                    [
                        "code_continuations",
                        "table_headers",
                        "condition_continuations",
                        "source_mapping",
                        "pagination_disclosure",
                    ]
                ),
            }
            for d in docs
        ],
    )
    lines = [
        "# 超限续片和上下文交付验证",
        "",
        json.dumps(summary, ensure_ascii=False, indent=2),
        "",
        "所有源字符进入限额内子块；生成围栏和重复表头不计为新增事实。",
        "上下文优先命中片段，补齐同单元续片、关联说明和条件；按1200 token/4000字符分页。",
        "不足一页时answer_ready=false并返回续页游标；末页也不把跨页并集冒充单次模型可见上下文。",
        "这是冻结命中ID的交付回放，不代表实际检索召回或最终回答正确率。",
        "默认API和旧索引未改；上线消费者必须处理answer_ready、continuation及blocked状态。",
        "",
        "## 多页示例",
        "",
    ]
    lines += [f"- [交付轨迹 {cid}](delivery/{cid}.json)" for cid in examples]
    report = "\n".join(lines) + "\n"
    path = output / "README.md"
    if path.exists() and path.read_text() != report:
        raise ValueError("Report changed")
    path.write_text(report)
    for p, expected in load(source / "artifacts-manifest.json").items():
        if digest(source / p) != expected:
            raise ValueError("Original chunk artifacts changed")
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
            "处理超限续片并验证上下文分页交付",
            "避免静默遗漏，保持已交付正文与源区间可核对",
            f"产物{args.output}；{summary}",
            "无；仅独立验证，未接入默认索引或API",
        )
        print(json.dumps(summary, ensure_ascii=False))
    except Exception as exc:
        record_operation(
            "超限续片/交付验证失败", "保留现场，不覆盖原数据", str(args.output), str(exc)
        )
        raise


if __name__ == "__main__":
    main()
