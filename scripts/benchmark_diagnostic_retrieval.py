"""Freeze 30 AI-authored questions; index 707 body chunks; run 90 real retrieval cases."""

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path
from time import perf_counter

from operation_log import ROOT, record_operation
from prepare_corpus_pilot import load, save

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.encoding import BGEEncoder
from infra_rag.evidence_delivery import pack_delivery
from infra_rag.lexical import BM25Index
from infra_rag.models import Chunk
from infra_rag.retrieval_diagnostic import fusion, intervals, score, validate_cases
from infra_rag.service import lexical_statistics

MODEL_PROTOCOL = ROOT / "evals/merged-corpus-v2/original-rag-v7/run-20261003-v3/protocol.json"
ARMS = ("bm25", "dense", "hybrid_rerank")


def prepare(source, questions, output):
    for path, expected in load(source / "artifacts-manifest.json").items():
        if digest(source / path) != expected:
            raise ValueError("Source manifest integrity failure")
    documents = [load(p) for p in sorted((source / "documents").glob("*.json"))]
    children = [c for d in documents for c in d["children"]]
    if len(children) != 707 or len({c["chunk_id"] for c in children}) != 707:
        raise ValueError("Expected 707 distinct source chunks")
    cases = load(questions)
    validate_cases(cases, documents)
    if len(cases) != 30 or Counter(c["kind"] for c in cases) != {
        "single_document": 24,
        "code_description": 2,
        "table_condition": 2,
        "long_condition": 2,
    }:
        raise ValueError("Unexpected question allocation")
    models = load(MODEL_PROTOCOL)["models"]
    from transformers import AutoTokenizer

    tokenizers = {}
    for kind in ("embedding", "reranker"):
        spec = models[kind]
        for path, expected in spec["files"].items():
            if digest(Path(spec["path"]) / path) != expected:
                raise ValueError("Frozen local model snapshot changed")
        tokenizers[kind] = AutoTokenizer.from_pretrained(spec["path"], local_files_only=True)
    for case in cases:
        for tokenizer in tokenizers.values():
            if len(tokenizer.encode(case["query"], add_special_tokens=False)) > 128:
                raise ValueError(f"Query exceeds reserved budget: {case['id']}")
            for c in children:
                length = len(
                    tokenizer.encode(
                        case["query"],
                        text_pair=c["retrieval_text"],
                        add_special_tokens=True,
                        truncation=False,
                    )
                )
                if length > min(512, tokenizer.model_max_length):
                    raise ValueError("Actual query/body pair would be truncated")
    implementation = [
        Path(__file__).resolve(),
        *[
            ROOT / ("src/infra_rag/" + p + ".py")
            for p in ("retrieval_diagnostic", "evidence_delivery", "lexical", "encoding", "service")
        ],
    ]
    protocol = {
        "source": str(source.relative_to(ROOT)),
        "source_sha256": digest(source / "artifacts-manifest.json"),
        "questions_path": str(questions.relative_to(ROOT)),
        "questions_sha256": digest(questions),
        "models": models,
        "arms": ARMS,
        "candidate_k": 30,
        "top_k": 5,
        "pair_cap": 90,
        "context_tokens_per_page": 1200,
        "context_chars_per_page": 4000,
        "query_language": "frozen original Chinese, no translation/expansion",
        "dense_search": "exact normalized dot product over 707 vectors, not ANN",
        "question_annotation": "AI-authored pending independent human review",
        "answer_generation_calls": 0,
        "default_changed": False,
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in implementation},
    }
    save(output / "protocol.json", protocol)
    save(output / "questions.json", cases)
    save(output / "corpus.json", children)
    save(output / "schedule.json", [{"case_id": c["id"], "arm": a} for c in cases for a in ARMS])
    save(
        output / "question-review-template.json",
        [
            {
                "id": c["id"],
                "case_sha256": canonical_hash(c),
                "status": "pending",
                "reviewer": None,
                "reason": None,
                "checks": dict.fromkeys(["question", "answerability", "evidence", "conditions"]),
            }
            for c in cases
        ],
    )
    for p in implementation:
        dest = output / "implementation" / p.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and digest(dest) != digest(p):
            raise ValueError("Implementation snapshot mismatch")
        if not dest.exists():
            shutil.copy2(p, dest)
    return cases, documents, children, models, tokenizers


def main_run(args):
    output = args.output.resolve()
    cases, documents, children, models, tokenizers = prepare(
        args.source.resolve(), args.questions.resolve(), output
    )
    if args.phase == "freeze":
        return {"phase": "freeze", "questions": 30, "chunks": 707}
    import numpy as np
    from sentence_transformers import CrossEncoder, SentenceTransformer

    encoder = BGEEncoder.__new__(BGEEncoder)
    encoder.model = SentenceTransformer(models["embedding"]["path"], local_files_only=True)
    encoder.instruction = "为这个句子生成表示以用于检索相关文章："
    encoder.batch_size = 16
    bodies = [c["retrieval_text"] for c in children]
    path = output / "vectors.npy"
    meta_path = output / "index-manifest.json"
    if path.exists():
        meta = load(meta_path)
        if digest(path) != meta["vectors_sha256"] or meta["body_identity"] != canonical_hash(
            bodies
        ):
            raise ValueError("Persistent index changed")
        vectors = np.load(path, allow_pickle=False)
    else:
        started = perf_counter()
        vectors = np.asarray(encoder.encode(bodies), dtype=np.float32)
        with path.open("xb") as stream:
            np.save(stream, vectors, allow_pickle=False)
        save(
            meta_path,
            {
                "chunks": len(children),
                "body_identity": canonical_hash(bodies),
                "vectors_sha256": digest(path),
                "embedding_model": models["embedding"],
                "build_ms": (perf_counter() - started) * 1000,
                "document_embedding_inputs": len(bodies),
                "question_inputs": 0,
                "embedding_text": "exact frozen heading plus body",
            },
        )
    if (
        vectors.shape[0] != 707
        or not np.isfinite(vectors).all()
        or not np.array_equal(vectors, np.load(path, allow_pickle=False))
    ):
        raise ValueError("Reloaded vector index differs")
    if not np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-4):
        raise ValueError("Dense vectors must be normalized")
    if args.phase == "index":
        return {"phase": "index", "chunks": 707}
    reranker = CrossEncoder(models["reranker"]["path"], local_files_only=True, max_length=512)
    chunk_objects = [
        Chunk(c["chunk_id"], c["parent_id"], c["source_url"], c["retrieval_text"], "infra")
        for c in children
    ]
    lexical = BM25Index(chunk_objects, statistics=lexical_statistics(chunk_objects))
    by_id = {c["chunk_id"]: c for c in children}
    counters = {
        name: lambda text, t=t: len(t.encode(text, add_special_tokens=False))
        for name, t in tokenizers.items()
    }
    for case in cases:
        for arm in ARMS:
            target = output / "rows" / f"{case['id']}-{arm}.json"
            if target.exists():
                expected = load(target.with_suffix(".sha256.json"))
                if digest(target) != expected["sha256"]:
                    raise ValueError("Checkpoint output changed")
                saved = load(target)
                if (saved["id"], saved["arm"], saved["query"]) != (case["id"], arm, case["query"]):
                    raise ValueError("Checkpoint case identity mismatch")
                continue
            started = perf_counter()
            row = {
                "id": case["id"],
                "arm": arm,
                "group_id": case["group_id"],
                "kind": case["kind"],
                "source_language": case["source_language"],
                "query": case["query"],
            }
            try:
                sparse, dense, scored_pairs = [], [], 0
                if arm in {"bm25", "hybrid_rerank"}:
                    sparse = lexical.search(case["query"], 30)
                if arm in {"dense", "hybrid_rerank"}:
                    vector = np.asarray(
                        encoder.encode([case["query"]], query=True)[0], dtype=np.float32
                    )
                    scores = vectors @ vector
                    dense = sorted(
                        [(c["chunk_id"], float(s)) for c, s in zip(children, scores, strict=True)],
                        key=lambda x: (-x[1], x[0]),
                    )[:30]
                ranked = (
                    sparse
                    if arm == "bm25"
                    else dense
                    if arm == "dense"
                    else fusion([sparse, dense])
                )
                candidates = [cid for cid, _ in ranked]
                if arm == "hybrid_rerank":
                    pairs = [(case["query"], by_id[cid]["retrieval_text"]) for cid in candidates]
                    scored_pairs = len(pairs)
                    if scored_pairs > 90:
                        raise ValueError("Rerank pair cap exceeded")
                    values = reranker.predict(pairs, show_progress_bar=False)
                    if not np.isfinite(values).all():
                        raise ValueError("Nonfinite rerank score")
                    ranked = sorted(
                        zip(candidates, map(float, values), strict=True),
                        key=lambda x: (-x[1], x[0]),
                    )
                search_ms = (perf_counter() - started) * 1000
                ids = [cid for cid, _ in ranked[:5]]
                cursor, pages = None, []
                while True:
                    page = pack_delivery(ids, documents, counters, cursor=cursor)
                    pages.append(page)
                    if page["status"] == "blocked" or page["continuation"] is None:
                        break
                    if len(pages) > len(page["required_chunk_ids"]):
                        raise ValueError("Pagination failed to progress")
                    cursor = page["continuation"]
                candidate_metric = score(intervals([by_id[cid] for cid in candidates]), case)
                top_metric = score(intervals([by_id[cid] for cid in ids]), case)
                first_metric = score(intervals(pages[0]["evidence"]), case)
                all_metric = score(intervals([e for page in pages for e in page["evidence"]]), case)
                row.update(
                    status="completed",
                    channels={"bm25": sparse, "dense": dense},
                    candidate_ids=candidates,
                    ranking=ranked,
                    hit_ids=ids,
                    candidate=candidate_metric,
                    top5=top_metric,
                    first_page=first_metric,
                    all_pages=all_metric,
                    pages=pages,
                    blocked=any(p["status"] == "blocked" for p in pages),
                    rerank_pairs=scored_pairs,
                    search_ms=search_ms,
                    total_page_tokens={
                        name: sum(p["token_counts"][name] for p in pages) for name in counters
                    },
                    total_page_characters=sum(p["used_characters"] for p in pages),
                )
            except Exception as exc:
                row.update(status="failed", error=str(exc))
            row["elapsed_ms_including_scoring"] = (perf_counter() - started) * 1000
            save(target, row)
            save(target.with_suffix(".sha256.json"), {"sha256": digest(target)})
        print("retrieved", case["id"], flush=True)
    rows = [
        load(p)
        for p in sorted((output / "rows").glob("diag-*.json"))
        if not p.name.endswith(".sha256.json")
    ]
    if len(rows) != 90 or len({(r["id"], r["arm"]) for r in rows}) != 90:
        raise ValueError("Incomplete or duplicate schedule outputs")
    results = {}
    for arm in ARMS:
        selected = [r for r in rows if r["arm"] == arm]
        results[arm] = {
            "outputs": len(selected),
            "failures": sum(r["status"] == "failed" for r in selected),
            "blocked": sum(r.get("blocked", False) for r in selected),
        }
        for field in ("candidate", "top5", "first_page", "all_pages"):
            results[arm][field] = {
                "numerator": sum(r.get(field, {}).get("complete", False) for r in selected),
                "denominator": len(selected),
                "coverage_mean": sum(r.get(field, {}).get("coverage", 0) for r in selected)
                / len(selected),
            }
        results[arm]["by_kind"] = {
            k: {
                f: sum(r.get(f, {}).get("complete", False) for r in selected if r["kind"] == k)
                for f in ("candidate", "top5", "first_page", "all_pages")
            }
            for k in sorted({r["kind"] for r in selected})
        }
        results[arm]["by_source_language"] = {
            k: {
                "n": sum(r["source_language"] == k for r in selected),
                "first_page_complete": sum(
                    r.get("first_page", {}).get("complete", False)
                    for r in selected
                    if r["source_language"] == k
                ),
            }
            for k in sorted({r["source_language"] for r in selected})
        }
    summary = {
        "questions": 30,
        "outputs": 90,
        "results": results,
        "human_review": "pending",
        "answer_accuracy": None,
        "default_changed": False,
        "answer_generation_calls": 0,
        "timing_scope": (
            "warm components plus instrumentation; not production latency; "
            "index initialization excluded"
        ),
        "comparison": "whole pipelines differ; not a single-factor attribution",
        "all_pages_budget_note": (
            "cumulative retrieval uses more context than a single page; costs reported per row"
        ),
    }
    for p, expected in load(args.source.resolve() / "artifacts-manifest.json").items():
        if digest(args.source.resolve() / p) != expected:
            raise ValueError("Source mutated during diagnostic run")
    if digest(args.questions.resolve()) != load(output / "protocol.json")["questions_sha256"]:
        raise ValueError("Question source mutated")
    save(output / "summary.json", summary)
    lines = [
        "# 真实检索开发诊断",
        "",
        "30道AI编写题，独立审核pending；不生成答案，不代表正式问答正确率。",
        "",
        "|配置|候选完整|Top5完整|首页正文完整|跨页正文完整|失败|",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for arm, r in results.items():
        values = [
            str(r[f]["numerator"]) + "/30" for f in ("candidate", "top5", "first_page", "all_pages")
        ]
        lines.append("|" + "|".join([arm, *values, str(r["failures"])]) + "|")
    lines += [
        "",
        "跨页结果使用更多总上下文，不能作为同预算收益；每页1200 token/4000字符。",
        "只有中文查询，按来源语言另报；标注证据稀疏且部分跨段标签较粗，独立审核前不得作为总体优劣结论。",
        "逐题轨迹见rows/；问题与证据见questions.json；人工审核另存副本，原模板保持pending。",
    ]
    text = "\n".join(lines) + "\n"
    path = output / "README.md"
    if path.exists() and path.read_text() != text:
        raise ValueError("Report changed")
    path.write_text(text)
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
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=("freeze", "index", "run", "all"), default="all")
    args = parser.parse_args()
    try:
        summary = main_run(args)
        record_operation(
            "独立索引与30题真实检索诊断",
            "验证真实召回、排序和实际交付，不调整默认服务",
            f"产物{args.output}；{summary}",
            "独立审核pending；跨页使用额外总预算，未生成答案",
        )
        print(json.dumps(summary, ensure_ascii=False))
    except Exception as exc:
        record_operation("检索诊断中止", "保留失败产物，不改输入", str(args.output), str(exc))
        raise


if __name__ == "__main__":
    main()
