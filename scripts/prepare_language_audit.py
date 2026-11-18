"""Freeze AI evidence review, unchanged questions/translations and source-role separation."""

import argparse
import shutil
from collections import Counter
from pathlib import Path

from operation_log import ROOT, record_operation
from prepare_corpus_pilot import load, save

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.retrieval_diagnostic import intervals, score, validate_cases
from infra_rag.source_roles import source_role

BASE = ROOT / "data/retrieval-diagnostic-v1/run-20261028"
SOURCE = ROOT / "data/evidence-delivery-v1/run-20261028-v2"
INVENTORY = ROOT / "data/corpus-preprocessing-v1/pilot-20261028-v3/inventory.json"
DATASET = ROOT / "evals/retrieval-diagnostic-v2"


def run(out):
    for directory in (BASE, SOURCE):
        for name, sha in load(directory / "artifacts-manifest.json").items():
            if digest(directory / name) != sha:
                raise ValueError("Frozen input changed: " + name)
    cases = load(DATASET / "questions.json")
    old = load(BASE / "questions.json")
    if len(cases) != 30 or [(c["id"], c["query"], c["group_id"]) for c in cases] != [
        (c["id"], c["query"], c["group_id"]) for c in old
    ]:
        raise ValueError("Original Chinese questions/IDs/groups must not change")
    if any(not c["query_en"].strip() for c in cases):
        raise ValueError("Missing English query")
    docs = [load(p) for p in sorted((SOURCE / "documents").glob("*.json"))]
    validate_cases(cases, docs)
    records = load(INVENTORY)
    roles = []
    for row in records:
        path = ROOT / row["input_path"]
        if (
            digest(path) != row["input_sha256"]
            or digest(ROOT / row["original_path"]) != row["input_sha256"]
        ):
            raise ValueError("Source identity changed")
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = ""
        role, reason = source_role(row["relative_path"], text, row["role"])
        roles.append(
            {
                **row,
                "source_role": role,
                "source_role_reason": reason,
                "role_review_method": (
                    "AI-assisted deterministic classification, not human factual approval"
                ),
            }
        )
    by_id = {r["document_id"]: r for r in roles}
    inputs = [
        INVENTORY,
        BASE / "artifacts-manifest.json",
        SOURCE / "artifacts-manifest.json",
        DATASET / "questions.json",
        DATASET / "ai-evidence-review.json",
    ]
    implementation = [
        Path(__file__).resolve(),
        ROOT / "src/infra_rag/source_roles.py",
        ROOT / "src/infra_rag/retrieval_diagnostic.py",
    ]
    save(
        out / "protocol.json",
        {
            "inputs": {str(p.relative_to(ROOT)): digest(p) for p in inputs},
            "implementation": {str(p.relative_to(ROOT)): digest(p) for p in implementation},
            "purpose": "separate annotation revision, source roles and language changes",
            "question_ids_and_chinese_queries_unchanged": True,
            "old_index_unchanged": True,
            "corpus_policy": (
                "paired language experiment retains identical original 707 chunks; "
                "report roles separately"
            ),
            "independent_review": "pending",
            "default_changed": False,
        },
    )
    for p in inputs + implementation:
        dest = out / "snapshots" / p.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and digest(dest) != digest(p):
            raise ValueError("Snapshot differs")
        if not dest.exists():
            shutil.copy2(p, dest)
    save(out / "source-roles.json", roles)
    counts = dict(Counter(r["source_role"] for r in roles))
    for role in counts:
        save(
            out / "source-groups" / role / "manifest.json",
            [r for r in roles if r["source_role"] == role],
        )
    save(
        out / "formal-body-candidates.json",
        [r for r in roles if r["source_role"] == "technical_body_candidate"],
    )
    # Keep original quotes for new groups; never infer source facts from retrieval scores.
    enriched = []
    for case in cases:
        item = {
            **case,
            "source_role": by_id[case["group_id"]]["source_role"],
            "original_case_sha256": canonical_hash(old[len(enriched)]),
        }
        enriched.append(item)
    save(out / "questions-v2.json", enriched)
    save(out / "evidence-review.json", load(DATASET / "ai-evidence-review.json"))
    save(
        out / "human-review-template.json",
        [
            {
                "id": c["id"],
                "case_sha256": canonical_hash(c),
                "status": "pending",
                "reviewer": None,
                "reason": None,
                "checks": dict.fromkeys(
                    [
                        "minimal_evidence",
                        "all_required_claims",
                        "complete_alternative_groups",
                        "source_role",
                        "english_fidelity",
                    ]
                ),
            }
            for c in enriched
        ],
    )
    children = {c["chunk_id"]: c for d in docs for c in d["children"]}
    cases_by_id = {c["id"]: c for c in enriched}
    rescored = []
    for path in sorted((BASE / "rows").glob("diag-*.json")):
        if path.name.endswith(".sha256.json"):
            continue
        row = load(path)
        case = cases_by_id[row["id"]]
        oldscore = {k: row[k] for k in ("candidate", "top5", "first_page", "all_pages")}
        newscore = {
            "candidate": score(intervals([children[cid] for cid in row["candidate_ids"]]), case),
            "top5": score(intervals([children[cid] for cid in row["hit_ids"]]), case),
            "first_page": score(intervals(row["pages"][0]["evidence"]), case),
            "all_pages": score(intervals([e for p in row["pages"] for e in p["evidence"]]), case),
        }
        rescored.append(
            {
                "id": row["id"],
                "arm": row["arm"],
                "old_labels": oldscore,
                "new_labels": newscore,
                "kind": "mechanical rescore only; retrieval and delivery unchanged",
            }
        )
    save(out / "old-traces-rescored.json", rescored)
    label_counts = {
        a: {
            k: {
                "old": sum(r["old_labels"][k]["complete"] for r in rescored if r["arm"] == a),
                "revised": sum(r["new_labels"][k]["complete"] for r in rescored if r["arm"] == a),
            }
            for k in ("candidate", "top5", "first_page", "all_pages")
        }
        for a in ("bm25", "dense", "hybrid_rerank")
    }
    save(
        out / "summary.json",
        {
            "reviewed_cases": 30,
            "role_counts": counts,
            "label_only_changes": label_counts,
            "independent_review": "pending",
            "source_content_modified": False,
        },
    )
    lines = [
        "# 证据复核与来源分层",
        "",
        "原30题的ID、中文问法和分组保持不变；AI复核不替代独立人工审核。",
        "",
        "源文件不移动、不改写，按角色分别输出source-groups/清单；正式正文候选见formal-body-candidates.json。",
        "editorial_record、draft_or_archive、reference_snapshot等不再混为正式技术正文；路径分类不等于事实权威认证。",
        "原707子块在后续中英对照中保持完全相同，非正式来源按角色单列，避免移除困难题或材料造成混淆。",
        "",
        "|来源角色|记录数|",
        "|---|---:|",
    ]
    lines += [f"|{k}|{v}|" for k, v in sorted(counts.items())]
    lines += [
        "",
        "逐题最小证据/替代组及理由见questions-v2.json和evidence-review.json。",
        "已核对完整问法需求；没有确认的替代证据不自动接纳，替代组审核仍非穷尽。",
        "旧轨迹机械重算见old-traces-rescored.json，标签变化与后续语言收益分别报告。",
    ]
    (out / "README.md").write_text("\n".join(lines) + "\n")
    save(
        out / "artifacts-manifest.json",
        {
            p.relative_to(out).as_posix(): digest(p)
            for p in sorted(out.rglob("*"))
            if p.is_file() and p.name != "artifacts-manifest.json"
        },
    )
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        counts = run(args.output.resolve())
        record_operation(
            "复核30题证据、英文表达并分层5767条来源",
            "分别控制标签、来源角色和检索语言变量",
            f"产物{args.output}；{counts}",
            "AI复核待独立审核；不重写原标签或默认服务",
        )
        print(counts)
    except Exception as exc:
        record_operation("复核/分层失败", "保留现场、不改旧产物", str(args.output), str(exc))
        raise
