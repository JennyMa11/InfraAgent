"""Frozen component replay with fresh Chinese whole-query reranking; no default adoption."""

import argparse
import shutil
from pathlib import Path

from operation_log import ROOT, record_operation
from prepare_corpus_pilot import load, save

from infra_rag.benchmarking import digest
from infra_rag.bilingual_retrieval import link_preceding_explanations, supplement
from infra_rag.evidence_delivery import pack_delivery
from infra_rag.paired_statistics import holm, paired_statistics
from infra_rag.retrieval_diagnostic import fusion, intervals, score

PREVIOUS = ROOT / "data/query-language-v1/run-20261028"
SOURCE = ROOT / "data/evidence-delivery-v1/run-20261028-v2"
ARMS = ("zh_baseline", "zh_fill60", "bilingual_fill60", "bilingual_context")
FIELDS = ("candidate", "top5", "first_page", "all_pages")


def run(out, freeze_only=False):
    for directory in (PREVIOUS, SOURCE):
        for name, sha in load(directory / "artifacts-manifest.json").items():
            if digest(directory / name) != sha:
                raise ValueError("Frozen input changed")
    cases = load(PREVIOUS / "questions.json")
    children = load(PREVIOUS / "corpus.json")
    docs = [load(p) for p in sorted((SOURCE / "documents").glob("*.json"))]
    linked, links = link_preceding_explanations(docs)
    implementation = [
        Path(__file__).resolve(),
        ROOT / "src/infra_rag/bilingual_retrieval.py",
        ROOT / "src/infra_rag/evidence_delivery.py",
        ROOT / "src/infra_rag/retrieval_diagnostic.py",
        ROOT / "src/infra_rag/paired_statistics.py",
    ]
    models = load(PREVIOUS / "protocol.json")["models"]
    protocol = {
        "inputs": {
            str(p.relative_to(ROOT)): digest(p)
            for p in (PREVIOUS / "artifacts-manifest.json", SOURCE / "artifacts-manifest.json")
        },
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in implementation},
        "models": models,
        "arms": ARMS,
        "cap": 60,
        "top_k": 5,
        "design": (
            "Replay measured CN/EN Top30; fresh Chinese whole-query rerank. "
            "Chinese fill uses next dense ranks from original vectors."
        ),
        "context_rule": "Same-section preceding paragraph for structured units; no gold access",
        "statistics": "Six tests; 10000 source-cluster bootstrap seed42; Holm correction",
        "retries": 0,
        "page_tokens": 1200,
        "page_characters": 4000,
        "independent_review": "pending",
        "default_changed": False,
        "timing": "component replay, not end-to-end latency",
        "adoption": "No adoption before independent review and held-out confirmation",
    }
    save(out / "protocol.json", protocol)
    save(out / "questions.json", cases)
    save(out / "context-links.json", links)
    save(out / "schedule.json", [{"id": c["id"], "arm": a} for c in cases for a in ARMS])
    for p in implementation:
        dest = out / "implementation" / p.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and digest(dest) != digest(p):
            raise ValueError("Implementation changed")
        if not dest.exists():
            shutil.copy2(p, dest)
    if freeze_only:
        return {"phase": "frozen", "planned": 120}
    import numpy as np
    from sentence_transformers import CrossEncoder
    from transformers import AutoTokenizer

    for kind in ("embedding", "reranker"):
        spec = models[kind]
        for name, sha in spec["files"].items():
            if digest(Path(spec["path"]) / name) != sha:
                raise ValueError("Model changed")
    tokenizers = {
        k: AutoTokenizer.from_pretrained(models[k]["path"], local_files_only=True)
        for k in ("embedding", "reranker")
    }
    counters = {
        k: lambda text, t=t: len(t.encode(text, add_special_tokens=False, verbose=False))
        for k, t in tokenizers.items()
    }
    reranker = CrossEncoder(models["reranker"]["path"], local_files_only=True, max_length=512)
    by_id = {c["chunk_id"]: c for c in children}
    # Existing exact dense index allows a matched-size Chinese-only fill control.
    from sentence_transformers import SentenceTransformer

    from infra_rag.encoding import BGEEncoder

    encoder = BGEEncoder.__new__(BGEEncoder)
    encoder.model = SentenceTransformer(models["embedding"]["path"], local_files_only=True)
    encoder.instruction = "为这个句子生成表示以用于检索相关文章："
    encoder.batch_size = 16
    vectors = np.load(
        ROOT / "data/retrieval-diagnostic-v1/run-20261028/vectors.npy", allow_pickle=False
    )
    rows = []
    for case in cases:
        zh = load(PREVIOUS / "rows" / f"{case['id']}-hybrid_rerank-zh.json")
        en = load(PREVIOUS / "rows" / f"{case['id']}-hybrid_rerank-en.json")
        base = fusion([zh["channels"]["bm25"], zh["channels"]["dense"]])
        vector = np.asarray(encoder.encode([case["query"]], query=True)[0], dtype=np.float32)
        values = vectors @ vector
        extended = sorted(
            zip([c["chunk_id"] for c in children], map(float, values), strict=True),
            key=lambda x: (-x[1], x[0]),
        )[:60]
        sets = {
            "zh_baseline": [cid for cid, _ in base],
            "zh_fill60": supplement(base, [extended]),
            "bilingual_fill60": supplement(
                base, [en["channels"]["bm25"], en["channels"]["dense"]], [extended]
            ),
        }
        rankings = {}
        for arm in ARMS:
            target = out / "rows" / f"{case['id']}-{arm}.json"
            if target.exists():
                raise ValueError("Use a fresh run directory; no implicit retries")
            row = {
                "id": case["id"],
                "arm": arm,
                "group_id": case["group_id"],
                "source_language": case["source_language"],
                "source_role": case["source_role"],
            }
            try:
                source_arm = "bilingual_fill60" if arm == "bilingual_context" else arm
                ids = sets[source_arm]
                if arm == "bilingual_context":
                    ranked = rankings[source_arm]
                else:
                    pairs = [(case["query"], by_id[cid]["retrieval_text"]) for cid in ids]
                    assert len(pairs) <= 60 and set(zh["candidate_ids"]) <= set(ids)
                    for t in tokenizers.values():
                        assert all(
                            len(t.encode(q, text_pair=b, verbose=False, truncation=False)) <= 512
                            for q, b in pairs
                        )
                    scores = reranker.predict(pairs, show_progress_bar=False)
                    if not np.isfinite(scores).all():
                        raise ValueError("Nonfinite scores")
                    ranked = sorted(
                        zip(ids, map(float, scores), strict=True), key=lambda x: (-x[1], x[0])
                    )
                    rankings[arm] = ranked
                hits = [cid for cid, _ in ranked[:5]]
                pages = []
                cursor = None
                while True:
                    page = pack_delivery(
                        hits,
                        linked if arm == "bilingual_context" else docs,
                        counters,
                        cursor=cursor,
                    )
                    pages.append(page)
                    if page["status"] == "blocked" or page["continuation"] is None:
                        break
                    if len(pages) > 707:
                        raise ValueError("No pagination progress")
                    cursor = page["continuation"]
                row.update(
                    status="completed",
                    candidate_ids=ids,
                    ranking=ranked,
                    hit_ids=hits,
                    pages=pages,
                    actual_rerank_pairs=0 if arm == "bilingual_context" else len(ids),
                    ranking_reused_from=source_arm if arm == "bilingual_context" else None,
                    candidate=score(intervals([by_id[cid] for cid in ids]), case),
                    top5=score(intervals([by_id[cid] for cid in hits]), case),
                    first_page=score(intervals(pages[0]["evidence"]), case),
                    all_pages=score(intervals([e for p in pages for e in p["evidence"]]), case),
                )
            except Exception as exc:
                row.update(status="failed", error=str(exc))
            save(target, row)
            save(target.with_suffix(".sha256.json"), {"sha256": digest(target)})
            rows.append(row)
        print(case["id"], flush=True)
    assert len(rows) == 120
    summary = {
        "outputs": 120,
        "human_review": "pending",
        "answer_accuracy": None,
        "default_changed": False,
        "results": {},
        "comparisons": {},
    }
    for arm in ARMS:
        selected = [r for r in rows if r["arm"] == arm]
        summary["results"][arm] = {
            f: {
                "numerator": sum(r.get(f, {}).get("complete", False) for r in selected),
                "denominator": 30,
            }
            for f in FIELDS
        }
        summary["results"][arm]["failures"] = sum(r["status"] != "completed" for r in selected)
        summary["results"][arm]["pages"] = sum(len(r.get("pages", [])) for r in selected)
        summary["results"][arm]["actual_rerank_pairs"] = sum(
            r.get("actual_rerank_pairs", 0) for r in selected
        )
    for before, after in [
        ("zh_baseline", "bilingual_fill60"),
        ("zh_fill60", "bilingual_fill60"),
        ("bilingual_fill60", "bilingual_context"),
    ]:
        for f in ("first_page", "all_pages"):
            pair = [
                [
                    {
                        "id": r["id"],
                        "group_id": r["group_id"],
                        "answerable": True,
                        "delivered": {"complete": r.get(f, {}).get("complete", False)},
                    }
                    for r in rows
                    if r["arm"] == a
                ]
                for a in (before, after)
            ]
            summary["comparisons"][f"{before}->{after}:{f}"] = paired_statistics(*pair)
    adjusted = holm({k: v["cluster_permutation_p"] for k, v in summary["comparisons"].items()})
    for k, v in summary["comparisons"].items():
        v["holm_p"] = adjusted[k]
    save(out / "summary.json", summary)
    save(
        out / "artifacts-manifest.json",
        {
            p.relative_to(out).as_posix(): digest(p)
            for p in out.rglob("*")
            if p.is_file() and p.name != "artifacts-manifest.json"
        },
    )
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--freeze-only", action="store_true")
    args = parser.parse_args()
    try:
        result = run(args.output.resolve(), args.freeze_only)
        record_operation(
            "双语保护召回与前置说明交付实验",
            "固定标签及正文，比较60对候选预算",
            str(result),
            "组件回放＋真实中文重排；人工审核pending，不采用默认配置",
        )
        print(result)
    except Exception as exc:
        record_operation("双语实验中止", "保留现场", str(args.output), str(exc))
        raise
