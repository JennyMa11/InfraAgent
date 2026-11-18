"""Freeze source inventory, select 60 documents, clean and validate without models/indexes."""

import argparse
import json
import re
import shutil
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from operation_log import ROOT, record_operation

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.corpus_pilot import (
    QUOTAS,
    VERSION,
    classify,
    duplicate_report,
    ensure_corpus_allowed,
    features,
    identity,
    language,
    prepare_document,
    select_pilot,
)

ARCHIVE = ROOT / "data/全部数据集_20261028"
MANIFESTS = {
    "official": "evals/infra-official-v1-reviewed/corpus-manifest.json",
    "repository": "evals/repository-benchmark/corpus-manifest.json",
    "new_official": "evals/source-collection-v2/batch-20261028/corpus-manifest.json",
    "full_repository": "data/infra-repositories/batch-20261028/manifest.json",
}


def load(path):
    return json.loads(path.read_text())


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if path.exists():
        if path.read_text() != raw:
            raise ValueError(f"Frozen artifact changed: {path}; use a new directory")
    else:
        with path.open("x") as stream:
            stream.write(raw)


def inventory():
    mapped = {}
    for mapping in sorted(ARCHIVE.glob("*/文件映射.json")):
        for entry in load(mapping):
            mapped.setdefault(entry["original_path"], []).append(entry)
    records = []
    for collection, relative in MANIFESTS.items():
        manifest = load(ROOT / relative)
        repos = {r["name"]: r for r in manifest.get("repositories", []) if "name" in r}
        for doc in manifest["documents"]:
            if collection == "full_repository":
                original = str(Path(relative).parent / doc["archive_path"])
                repo, path = doc["repository"], doc["source_path"]
                sha = doc["sha256"]
                raw_sha = sha
                source_map = None
                release = None
                url = doc["source_url"]
                status, role, reason = classify(path)
            else:
                original = doc.get("corpus_path") or str(
                    Path(manifest["corpus_root"]) / doc["source"]
                )
                repo = doc.get("repo") or doc.get("repository") or doc["project"]
                path = doc.get("source_path") or doc.get("path") or doc["source"]
                sha, raw_sha = doc["sha256"], doc.get("raw_sha256", doc["sha256"])
                source_map = doc.get("line_map")
                release = doc.get("release")
                url = doc.get("source_url") or doc["url"]
                status, role, reason = (
                    "retain",
                    doc.get("source_type", "technical_body"),
                    "frozen_source_candidate",
                )
            copies = mapped.get(original)
            if not copies:
                raise ValueError(f"No archive mapping: {original}")
            for entry in copies:
                if entry["sha256"] != sha or digest(ARCHIVE / entry["archive_path"]) != sha:
                    raise ValueError(f"Archive/source hash mismatch: {original}")
            source = ARCHIVE / copies[0]["archive_path"]
            if digest(ROOT / original) != sha:
                raise ValueError(f"Original source changed: {original}")
            raw = source.read_bytes()
            try:
                text = raw.decode("utf-8-sig")
                flags, lang = features(text, source.suffix), language(text)
            except UnicodeDecodeError:
                text, flags, lang = "", ["invalid_utf8"], "unknown"
                status, reason = "review", "decode_error"
            commit = doc.get("commit") or repos.get(repo, {}).get("commit")
            record = {
                "document_id": identity(collection, repo, path, commit, raw_sha),
                "collection": collection,
                "repository": repo,
                "relative_path": path,
                "input_path": str(source.relative_to(ROOT)),
                "original_path": original,
                "commit": commit,
                "release": release
                if release and re.fullmatch(r"v?\d+(?:\.\d+)+(?:[-+][\w.]+)?", release)
                else None,
                "declared_release": release,
                "product": doc.get("project"),
                "source_url": url,
                "raw_sha256": raw_sha,
                "input_sha256": sha,
                "whitespace_sha256": canonical_hash("".join(text.split())),
                "language": lang,
                "status": status,
                "role": role,
                "reason": reason,
                "features": flags,
                "characters": len(text),
                "upstream_line_map": source_map,
                "coordinate_type": doc.get(
                    "line_coordinate",
                    "frozen_source_map" if source_map else "source_markdown_lines",
                ),
                "human_review": "pending",
                "archive_aliases": [e["archive_path"] for e in copies],
            }
            records.append(record)
    if len(records) != 5767 or len({r["document_id"] for r in records}) != 5767:
        raise ValueError("Expected 5767 distinct versioned source records")
    return records


def freeze_run(run):
    paths = [ROOT / p for p in MANIFESTS.values()]
    paths += [ARCHIVE / "总清单.json", *sorted(ARCHIVE.glob("*/文件映射.json"))]
    implementation = [Path(__file__).resolve(), ROOT / "src/infra_rag/corpus_pilot.py"]
    protocol = {
        "version": VERSION,
        "quotas": QUOTAS,
        "seed": 42,
        "inputs": {str(p.relative_to(ROOT)): digest(p) for p in paths},
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in implementation},
        "models_called": 0,
        "indexed": False,
        "chunked": False,
        "human_review": "pending",
    }
    save(run / "protocol.json", protocol)
    for path in implementation:
        target = run / "implementation" / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if digest(target) != digest(path):
                raise ValueError("Implementation snapshot changed")
        else:
            shutil.copy2(path, target)
    return protocol


def process(record):
    try:
        result = prepare_document(
            (ROOT / record["input_path"]).read_bytes(),
            record["upstream_line_map"],
            mdx=Path(record["input_path"]).suffix.casefold() == ".mdx",
        )
    except UnicodeDecodeError as exc:
        result = {
            "status": "error",
            "errors": [{"reason": "invalid_utf8", "detail": str(exc)}],
            "changes": [],
        }
    result["document_id"] = record["document_id"]
    result["input_sha256"] = record["input_sha256"]
    result["coordinate_type"] = record["coordinate_type"]
    result["human_review"] = "pending"
    if result["status"] != "error":
        result["features"] = sorted(set(result["features"]) | set(record["features"]))
        if set(result["features"]) & {"image_dependency", "include_dependency", "mdx_component"}:
            result["status"] = "review"
        result["units"] = [
            {
                **u,
                "unit_id": canonical_hash(
                    [record["document_id"], VERSION, u["input_lines"], u["kind"], u["content"]]
                )[:32],
            }
            for u in result["units"]
        ]
    return result


def validate(run, records, pilot):
    denied = load(run / "denied-inputs.json")
    for row in pilot:
        ensure_corpus_allowed(row, denied["hashes"], denied["paths"])
    results, failures = [], []
    for row in records:
        if digest(ROOT / row["input_path"]) != row["input_sha256"]:
            raise ValueError("Input mutated during run")
        if digest(ROOT / row["original_path"]) != row["input_sha256"]:
            raise ValueError("Original mutated during run")
    for row in pilot:
        path = run / "documents" / (row["document_id"] + ".json")
        result = load(path)
        if result["status"] == "error":
            failures.append({"document_id": row["document_id"], "errors": result["errors"]})
        else:
            expected = process(row)
            if result != expected:
                raise ValueError("Document artifact differs from deterministic preparation")
            text = (run / "cleaned" / (row["document_id"] + ".md")).read_text()
            if text != result["text"]:
                raise ValueError("Cleaned artifact differs")
            lines = text.splitlines()
            if len(lines) != len(result["line_map"]):
                raise ValueError("Line map mismatch")
            for unit in result["units"]:
                start, end = unit["input_lines"]
                if unit["content"] != "\n".join(lines[start - 1 : end]):
                    raise ValueError("Structural source range mismatch")
        results.append(result)
    sampling = []
    for collection in QUOTAS:
        subset = [r for r in pilot if r["collection"] == collection]
        reviewed_repositories = set()
        for _ in range(4):
            row = min(
                subset,
                key=lambda r: (
                    r["repository"] in reviewed_repositories,
                    -len(r["features"]),
                    canonical_hash(["review42", r["document_id"]]),
                ),
            )
            reviewed_repositories.add(row["repository"])
            subset.remove(row)
            sampling.append(
                {
                    "document_id": row["document_id"],
                    "collection": collection,
                    "repository": row["repository"],
                    "source_url": row["source_url"],
                    "status": "pending",
                    "reviewer": None,
                    "reason": None,
                    "checks": dict.fromkeys(
                        ["scope", "format", "protected_content", "source_mapping", "dependencies"]
                    ),
                }
            )
    save(run / "human-review-template.json", sampling)
    summary = {
        "scheduled": 60,
        "outputs": len(results),
        "status_counts": dict(Counter(r["status"] for r in results)),
        "errors": failures,
        "human_review": "pending",
        "human_review_sample": len(sampling),
        "input_integrity": "passed",
        "automatic_validation": "passed",
        "known_evaluation_files_in_pilot": sum(
            r["input_sha256"] in denied["hashes"] or r["original_path"] in denied["paths"]
            for r in pilot
        ),
        "known_non_corpus_hashes_checked": len(denied["hashes"]),
        "corpus_ready_for_expansion": False,
        "models_called": 0,
        "indexed": False,
    }
    save(run / "validation.json", summary)
    return summary


def execute(run, phase):
    run.mkdir(parents=True, exist_ok=True)
    freeze_run(run)
    excluded_files = [
        e
        for p in sorted(ARCHIVE.glob("*/文件映射.json"))
        for e in load(p)
        if Path(e["original_path"]).suffix in {".json", ".jsonl"}
    ]
    save(
        run / "denied-inputs.json",
        {
            "hashes": sorted({e["sha256"] for e in excluded_files}),
            "paths": sorted({e["original_path"] for e in excluded_files}),
            "scope": "known question/annotation/metadata JSON and JSONL from archive mappings; "
            "does not establish absence of semantic leakage in arbitrary Markdown",
        },
    )
    records = inventory()
    save(run / "inventory.json", records)
    groups = load(ARCHIVE / "总清单.json")["datasets"]
    save(
        run / "excluded-collections.json",
        [
            {
                "directory": g["directory"],
                "policy": "separate_protocol_or_non_corpus",
                "detail": g["status"],
            }
            for g in groups
            if g["directory"].split("_")[0] not in {"01", "02", "03", "04"}
        ],
    )
    save(
        run / "inventory-summary.json",
        {
            "records": len(records),
            "status_counts": dict(Counter(r["status"] for r in records)),
            "by_collection": {
                c: dict(Counter(r["status"] for r in records if r["collection"] == c))
                for c in MANIFESTS
            },
            "archived_copies_not_recounted": True,
        },
    )
    if phase == "inventory":
        return None
    pilot = select_pilot(records)
    denied = load(run / "denied-inputs.json")
    for row in pilot:
        ensure_corpus_allowed(row, denied["hashes"], denied["paths"])
    save(run / "pilot.json", pilot)
    if phase == "freeze-pilot":
        return None
    for row in pilot:
        if phase == "validate":
            if not (run / "documents" / (row["document_id"] + ".json")).is_file():
                raise ValueError("Missing process outputs; validate cannot create them")
            continue
        result = process(row)
        save(run / "documents" / (row["document_id"] + ".json"), result)
        if result["status"] != "error":
            target = run / "cleaned" / (row["document_id"] + ".md")
            target.parent.mkdir(exist_ok=True)
            if target.exists() and target.read_text() != result["text"]:
                raise ValueError("Cleaned text changed; use new directory")
            if not target.exists():
                target.write_text(result["text"])
    if phase == "process":
        return None
    texts = {
        row["document_id"]: (ROOT / row["input_path"]).read_text(encoding="utf-8-sig")
        for row in pilot
        if "invalid_utf8" not in row["features"]
    }
    save(run / "duplicate-audit.json", duplicate_report(records, texts))
    summary = validate(run, records, pilot)
    lines = [
        "# 首轮来源清单与预处理试验",
        "",
        f"5,767条来源记录；60份冻结样本；状态：{summary['status_counts']}。",
        "",
        "未分块、未建索引、未调用模型；人工抽查12份保持pending，当前不扩大处理规模。",
        "",
        "|集合|仓库|原文|状态|清洗产物|",
        "|---|---|---|---|---|",
    ]
    for row in pilot:
        result = load(run / "documents" / (row["document_id"] + ".json"))
        cid = row["document_id"]
        lines.append(
            f"|{row['collection']}|{row['repository']}|[{row['relative_path']}]"
            f"({(ROOT / row['input_path']).as_posix()})|{result['status']}|"
            f"[记录](documents/{cid}.json)|"
        )
    lines += [
        "",
        "自动验证不代表事实审核。缺失版本不推断；映射坐标类型见记录。",
        "清理与结构单元、逐行变更见documents/，正文见cleaned/。",
        "原文件没有删除或修改；重复来源仅审计并保留全部别名。",
        "异常样本不替换，错误清单见validation.json；人工抽查见human-review-template.json。",
    ]
    report = "\n".join(lines) + "\n"
    if (run / "README.md").exists() and (run / "README.md").read_text() != report:
        raise ValueError("Report changed")
    (run / "README.md").write_text(report)
    save(
        run / "artifacts-manifest.json",
        {
            p.relative_to(run).as_posix(): digest(p)
            for p in sorted(run.rglob("*"))
            if p.is_file() and p.name != "artifacts-manifest.json"
        },
    )
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--phase",
        choices=["inventory", "freeze-pilot", "process", "validate", "all"],
        default="all",
    )
    args = parser.parse_args()
    run = args.output or ROOT / "data/corpus-preprocessing-v1" / datetime.now(UTC).strftime(
        "pilot-%Y%m%d-%H%M%S"
    )
    try:
        summary = execute(run.resolve(), args.phase)
        record_operation(
            "建立范围清单并执行首轮预处理",
            "按冻结配额检查60份，尚不分块或索引",
            f"产物{run}；阶段{args.phase}；结果{summary}",
            "存在隔离异常" if summary and summary["errors"] else "无；人工审核pending",
        )
        print(json.dumps(summary or {"phase": args.phase, "output": str(run)}, ensure_ascii=False))
        return 1 if summary and summary["errors"] else 0
    except Exception as exc:
        record_operation("预处理执行失败", "保留异常，不覆盖旧数据", f"产物保留于{run}", str(exc))
        raise


if __name__ == "__main__":
    sys.exit(main())
