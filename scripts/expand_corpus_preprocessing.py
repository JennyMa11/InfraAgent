"""Expand approved corpus preparation without mutating pilot or adopting an index."""

import argparse
import hashlib
import heapq
import json
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from operation_log import ROOT, record_operation
from prepare_corpus_pilot import MANIFESTS, inventory, load, process, save

from infra_rag.benchmarking import digest
from infra_rag.corpus_pilot import duplicate_report

CHECKS = {"scope", "format", "protected_content", "source_mapping", "dependencies"}


def verify_review(baseline, reviewed):
    manifest = load(reviewed / "review-manifest.json")
    if (ROOT / manifest["baseline"]).resolve() != baseline.resolve():
        raise ValueError("Review refers to a different baseline")
    protected = load(baseline / "artifacts-manifest.json")
    for name, expected in protected.items():
        if digest(baseline / name) != expected:
            raise ValueError(f"Frozen baseline changed: {name}")
    protocol = load(baseline / "protocol.json")
    for name, expected in protocol["implementation"].items():
        if digest(ROOT / name) != expected:
            raise ValueError(f"Reviewed preparation implementation changed: {name}")
    for item in [manifest["template"], *manifest["evidence"].values()]:
        if digest(ROOT / item["path"]) != item["sha256"]:
            raise ValueError("Review template/evidence hash mismatch")
    if (ROOT / manifest["template"]["path"]).resolve() != (
        baseline / "human-review-template.json"
    ).resolve():
        raise ValueError("Wrong review template")
    template = {r["document_id"]: r for r in load(baseline / "human-review-template.json")}
    evidence = {
        r["document_id"]: r for r in load(ROOT / manifest["evidence"]["json"]["path"])["documents"]
    }
    pilot = {r["document_id"]: r for r in load(baseline / "pilot.json")}
    review = load(reviewed / "human-review.json")
    ids = [r["document_id"] for r in review]
    if len(ids) != len(set(ids)) or set(ids) != set(template) or len(ids) != 12:
        raise ValueError("Review must cover exactly the 12 distinct sample documents")
    if set(evidence) != set(template):
        raise ValueError("Evidence document IDs mismatch")
    counts = {key: Counter() for key in CHECKS}
    for row in review:
        cid = row["document_id"]
        if row["status"] != "approved" or row.get("method") != "independent_human":
            raise ValueError("Review is not approved independent human review")
        if not all(row.get(k) for k in ["reviewer", "reason", "reviewed_at"]):
            raise ValueError("Reviewer, reason and date are required")
        datetime.fromisoformat(row["reviewed_at"])
        if row["reviewer"] != manifest["reviewer"] or row["reviewed_at"] != manifest["reviewed_at"]:
            raise ValueError("Review header differs from manifest")
        if set(row["checks"]) != CHECKS or any(
            v not in {"pass", "pass_with_note"} for v in row["checks"].values()
        ):
            raise ValueError("Review checks incomplete or failed")
        for key in ["collection", "repository", "source_url"]:
            if row[key] != pilot[cid][key] or row[key] != template[cid][key]:
                raise ValueError("Review identity mismatch")
        if row["input_sha256"] != pilot[cid]["input_sha256"]:
            raise ValueError("Review input hash mismatch")
        hashes = evidence[cid]["hashes"]
        if hashes["frozen_input_sha256"] != row["input_sha256"]:
            raise ValueError("Evidence input hash mismatch")
        if digest(baseline / "cleaned" / (cid + ".md")) != hashes["cleaned_sha256"]:
            raise ValueError("Evidence cleaned hash mismatch")
        for key, value in row["checks"].items():
            counts[key][value] += 1
    if manifest["documents"] != 12 or manifest["status_counts"] != {"approved": 12}:
        raise ValueError("Manifest review counts mismatch")
    if manifest["check_counts"] != {key: dict(value) for key, value in counts.items()}:
        raise ValueError("Manifest check counts mismatch")
    return {r["document_id"]: r for r in review}, manifest


def select_candidates(records, denied):
    selected = [r for r in records if r["status"] == "retain"]
    for row in selected:
        if (
            row["collection"] not in MANIFESTS
            or row["input_sha256"] in denied["hashes"]
            or row["original_path"] in denied["paths"]
        ):
            raise ValueError("Non-corpus source selected")
    if len({r["document_id"] for r in selected}) != len(selected):
        raise ValueError("Duplicate candidate identity")
    return selected


def near_audit(rows):
    """Bounded bottom-64 sketches nominate pairs; exact shingle Jaccard confirms only."""
    postings = defaultdict(list)
    candidates = Counter()
    indexed = {r["document_id"]: r for r in rows}
    for row in rows:
        text = "".join((ROOT / row["input_path"]).read_text(encoding="utf-8-sig").split())
        if len(text) < 100:
            continue
        sketch = heapq.nsmallest(
            64,
            {
                hashlib.blake2b(text[i : i + 20].encode(), digest_size=8).digest()
                for i in range(len(text) - 19)
            },
        )
        for gram in sketch:
            for prior in postings[gram]:
                candidates[tuple(sorted([prior, row["document_id"]]))] += 1
            postings[gram].append(row["document_id"])

    def grams(cid):
        text = "".join((ROOT / indexed[cid]["input_path"]).read_text(encoding="utf-8-sig").split())
        return {text[i : i + 20] for i in range(len(text) - 19)}

    matches = []
    nominated = [pair for pair, shared in candidates.items() if shared >= 8]
    for left, right in sorted(nominated):
        a, b = grams(left), grams(right)
        score = len(a & b) / max(1, len(a | b))
        if score >= 0.8:
            matches.append({"left": left, "right": right, "jaccard": score})
    return {
        "method": "bottom64-blake2b64/20char; shared>=8; exact Jaccard>=0.8",
        "documents": len(rows),
        "nominated_pairs": len(nominated),
        "matches": matches,
        "scope": "approximate candidate generation, not exhaustive relevance or semantic dedup",
        "deleted_documents": 0,
    }


def expand(baseline, reviewed, output):
    review, manifest = verify_review(baseline, reviewed)
    records = inventory()
    if records != load(baseline / "inventory.json"):
        raise ValueError("Inventory differs from reviewed pilot; freeze a new pilot first")
    denied = load(baseline / "denied-inputs.json")
    selected = select_candidates(records, denied)
    output.mkdir(parents=True, exist_ok=True)
    dependencies = [
        reviewed / "human-review.json",
        reviewed / "review-manifest.json",
        baseline / "protocol.json",
        baseline / "inventory.json",
        baseline / "denied-inputs.json",
        baseline / "artifacts-manifest.json",
        ROOT / manifest["template"]["path"],
        *[ROOT / item["path"] for item in manifest["evidence"].values()],
    ]
    implementation = [
        Path(__file__).resolve(),
        ROOT / "scripts/prepare_corpus_pilot.py",
        ROOT / "src/infra_rag/corpus_pilot.py",
    ]
    protocol = {
        "baseline": str(baseline.relative_to(ROOT)),
        "reviewer": manifest["reviewer"],
        "scope": "all retained candidates; review/exclude records unchanged",
        "scheduled": len(selected),
        "inputs": {str(p.relative_to(ROOT)): digest(p) for p in dependencies},
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in implementation},
        "chunked": False,
        "indexed": False,
        "model_calls": 0,
    }
    save(output / "protocol.json", protocol)
    for path in dependencies + implementation:
        target = output / "snapshots" / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if digest(target) != digest(path):
                raise ValueError("Snapshot changed")
        else:
            shutil.copy2(path, target)
    save(output / "selected.json", selected)
    save(
        output / "excluded-scope.json",
        {
            "inventory_records": len(records),
            "not_selected": [r["document_id"] for r in records if r["status"] != "retain"],
            "status_counts": dict(Counter(r["status"] for r in records if r["status"] != "retain")),
        },
    )
    save(
        output / "review-validation.json",
        {
            "reviewed_sample": 12,
            "result": "passed",
            "review_source": (
                "supplied independent human review; AI evidence assistance recorded separately"
            ),
            "notes_carried_forward": {cid: r["reason"] for cid, r in review.items()},
        },
    )
    pilot_ids = {r["document_id"] for r in load(baseline / "pilot.json")}
    results = []
    for n, row in enumerate(selected, 1):
        cid = row["document_id"]
        result = process(row)
        if cid in pilot_ids and result != load(baseline / "documents" / (cid + ".json")):
            raise ValueError("Expanded processing differs from frozen pilot")
        if cid in review:
            result["human_review"] = "approved"
            result["review"] = review[cid]
        save(output / "documents" / (cid + ".json"), result)
        if result["status"] != "error":
            target = output / "cleaned" / (cid + ".md")
            target.parent.mkdir(exist_ok=True)
            if (
                target.exists()
                and digest(target) != hashlib.sha256(result["text"].encode()).hexdigest()
            ):
                raise ValueError("Cleaned output changed")
            if not target.exists():
                target.write_text(result["text"])
            lines = result["text"].splitlines()
            if len(lines) != len(result["line_map"]):
                raise ValueError("Line map mismatch")
            for unit in result["units"]:
                a, b = unit["input_lines"]
                if (
                    unit["content"] != "\n".join(lines[a - 1 : b])
                    or unit["source_lines"] != result["line_map"][a - 1 : b]
                ):
                    raise ValueError("Structure/source mapping mismatch")
        results.append(result)
        if n % 50 == 0:
            print(f"processed {n}/{len(selected)}", flush=True)
    save(output / "duplicate-audit.json", duplicate_report(records))
    good_rows = [
        r for r, value in zip(selected, results, strict=True) if value["status"] != "error"
    ]
    save(output / "near-duplicate-audit.json", near_audit(good_rows))
    for row in records:
        if (
            digest(ROOT / row["input_path"]) != row["input_sha256"]
            or digest(ROOT / row["original_path"]) != row["input_sha256"]
        ):
            raise ValueError("Input mutated during expansion")
    verify_review(baseline, reviewed)
    summary = {
        "scheduled": len(selected),
        "outputs": len(results),
        "status_counts": dict(Counter(r["status"] for r in results)),
        "reviewed_documents": len(review),
        "remaining_document_reviews": len(selected) - len(review),
        "by_collection": {
            c: dict(
                Counter(
                    value["status"]
                    for row, value in zip(selected, results, strict=True)
                    if row["collection"] == c
                )
            )
            for c in MANIFESTS
        },
        "errors": [
            {"document_id": r["document_id"], "errors": r["errors"]}
            for r in results
            if r["status"] == "error"
        ],
        "automatic_validation": "passed",
        "sample_review_binding": "passed",
        "known_evaluation_files": sum(
            r["input_sha256"] in denied["hashes"] or r["original_path"] in denied["paths"]
            for r in selected
        ),
        "model_calls": 0,
        "indexed": False,
        "note": (
            "sample approval does not approve every new document; "
            "dependencies retained; errors isolated"
        ),
    }
    save(output / "validation.json", summary)
    save(
        output / "new-document-review-template.json",
        [
            {
                "document_id": r["document_id"],
                "status": "pending",
                "reviewer": None,
                "source_url": r["source_url"],
                "reason": None,
                "checks": dict.fromkeys(sorted(CHECKS)),
            }
            for r in selected
            if r["document_id"] not in review
        ],
    )
    lines = [
        "# 扩大预处理结果",
        "",
        f"已核对12份人工审核记录、模板及证据包绑定。456份保留候选，结果：{summary['status_counts']}。",
        "",
        "原模板、源数据和旧产物未修改；未分块、未建索引、未调用模型。",
        "图片/include/MDX及来源格式备注继续保留，自动通过不等于人工事实审核。",
        "仅原抽查12份继承人工批准，其余文档仍待审；异常未产生cleaned正文。",
        "",
        "|集合|文档|处理状态|原文|清洗|记录|",
        "|---|---|---|---|---|---|",
    ]
    for row, result in zip(selected, results, strict=True):
        cid = row["document_id"]
        cleaned = f"[正文](cleaned/{cid}.md)" if result["status"] != "error" else "隔离"
        lines.append(
            f"|{row['collection']}|{row['repository']}/{row['relative_path']}|{result['status']}|"
            f"[原文]({(ROOT / row['input_path']).as_posix()})|{cleaned}|"
            f"[记录](documents/{cid}.json)|"
        )
    text = "\n".join(lines) + "\n"
    target = output / "README.md"
    if target.exists() and target.read_text() != text:
        raise ValueError("Report changed")
    target.write_text(text)
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
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--reviewed", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        summary = expand(args.baseline.resolve(), args.reviewed.resolve(), args.output.resolve())
        record_operation(
            "核验独立审核后扩大预处理",
            "用户授权扩大清洗、结构提取，保留异常隔离",
            f"产物{args.output}；状态{summary['status_counts']}；12份审核绑定通过",
            f"隔离异常{len(summary['errors'])}份；其余文档人工审核不自动继承",
        )
        print(json.dumps(summary, ensure_ascii=False))
        return 1 if summary["errors"] else 0
    except Exception as exc:
        record_operation(
            "扩大预处理失败", "保留失败产物、不修改原始数据", str(args.output), str(exc)
        )
        raise


if __name__ == "__main__":
    sys.exit(main())
