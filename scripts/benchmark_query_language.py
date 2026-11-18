"""Compare frozen Chinese/English queries over identical corpus, models and body vectors."""

import argparse
import json
import shutil
from pathlib import Path
from time import perf_counter

from operation_log import ROOT, record_operation
from prepare_corpus_pilot import load, save

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.encoding import BGEEncoder
from infra_rag.evidence_delivery import pack_delivery
from infra_rag.language_diagnostic import ARMS, FIELDS, schedule, summarize, validate_pairs
from infra_rag.lexical import BM25Index
from infra_rag.models import Chunk
from infra_rag.retrieval_diagnostic import fusion, intervals, score, validate_cases
from infra_rag.service import lexical_statistics

BASE = ROOT / "data/retrieval-diagnostic-v1/run-20261028"
SOURCE = ROOT / "data/evidence-delivery-v1/run-20261028-v2"


def check_manifest(directory):
    for name, sha in load(directory / "artifacts-manifest.json").items():
        if digest(directory / name) != sha:
            raise ValueError("Frozen artifact changed: " + str(directory / name))


def prepare(audit, out):
    for directory in (BASE, SOURCE, audit):
        check_manifest(directory)
    cases = load(audit / "questions-v2.json")
    validate_pairs(cases, load(BASE / "questions.json"))
    if len(cases) != 30:
        raise ValueError("Expected fixed 30 cases")
    documents = [load(p) for p in sorted((SOURCE / "documents").glob("*.json"))]
    validate_cases(cases, documents)
    children = load(BASE / "corpus.json")
    if children != [c for d in documents for c in d["children"]]:
        raise ValueError("Body corpus/order differs from original vector index")
    index = load(BASE / "index-manifest.json")
    if index["body_identity"] != canonical_hash([c["retrieval_text"] for c in children]):
        raise ValueError("Vector/body identity mismatch")
    if digest(BASE / "vectors.npy") != index["vectors_sha256"]:
        raise ValueError("Original vectors changed")
    models = load(BASE / "protocol.json")["models"]
    from transformers import AutoTokenizer

    tokenizers = {}
    for kind in ("embedding", "reranker"):
        spec = models[kind]
        for name, expected in spec["files"].items():
            if digest(Path(spec["path"]) / name) != expected:
                raise ValueError("Model snapshot changed")
        tokenizers[kind] = AutoTokenizer.from_pretrained(spec["path"], local_files_only=True)
    for case in cases:
        for language in ("zh", "en"):
            query = case["query" if language == "zh" else "query_en"]
            for tokenizer in tokenizers.values():
                if len(tokenizer.encode(query, add_special_tokens=False)) > 128:
                    raise ValueError("Query exceeds reserved 128 tokens")
                for c in children:
                    pair = tokenizer.encode(
                        query,
                        text_pair=c["retrieval_text"],
                        truncation=False,
                        add_special_tokens=True,
                    )
                    if len(pair) > min(512, tokenizer.model_max_length):
                        raise ValueError("Actual query/body pair would be truncated")
    implementation = [
        Path(__file__).resolve(),
        *[
            ROOT / ("src/infra_rag/" + p + ".py")
            for p in (
                "language_diagnostic",
                "paired_statistics",
                "retrieval_diagnostic",
                "evidence_delivery",
                "lexical",
                "encoding",
                "service",
            )
        ],
    ]
    inputs = [
        BASE / "artifacts-manifest.json",
        BASE / "vectors.npy",
        BASE / "index-manifest.json",
        SOURCE / "artifacts-manifest.json",
        audit / "artifacts-manifest.json",
        audit / "questions-v2.json",
    ]
    protocol = {
        "inputs": {str(p.relative_to(ROOT)): digest(p) for p in inputs},
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in implementation},
        "models": models,
        "arms": list(ARMS),
        "languages": ["zh", "en"],
        "candidate_k": 30,
        "top_k": 5,
        "pair_cap": 90,
        "context_tokens_per_page": 1200,
        "context_chars_per_page": 4000,
        "dense_search": "same original normalized 707 body vectors, exact dot product",
        "embedding_instruction_both_languages": "为这个句子生成表示以用于检索相关文章：",
        "variable": "frozen query expression only; whole retrieval/reranker language effect",
        "statistics": {
            "primary_tests": "3 arms x first/all-page = 6; Holm",
            "bootstrap": "10000 source-cluster samples, seed 42, percentile 95% CI",
            "sign_test": "paired source-cluster sign permutation, two sided",
        },
        "repetitions": 1,
        "retry_limit": 0,
        "answer_generation_calls": 0,
        "independent_review": "pending",
        "default_changed": False,
        "adoption_gate": "diagnostic only; no adoption pending independent evidence/query review",
        "all_pages_note": "union across pages uses additional cumulative context; not one prompt",
    }
    save(out / "protocol.json", protocol)
    save(out / "questions.json", cases)
    save(out / "corpus.json", children)
    save(out / "schedule.json", schedule(cases))
    for p in implementation:
        dest = out / "implementation" / p.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and digest(dest) != digest(p):
            raise ValueError("Implementation snapshot differs")
        if not dest.exists():
            shutil.copy2(p, dest)
    return cases, documents, children, models, tokenizers


def run(audit, output, freeze_only=False):
    cases, documents, children, models, tokenizers = prepare(audit, output)
    if freeze_only:
        return {"phase": "frozen", "cases": 30, "outputs_planned": 180}
    import numpy as np
    from sentence_transformers import CrossEncoder, SentenceTransformer

    encoder = BGEEncoder.__new__(BGEEncoder)
    encoder.model = SentenceTransformer(models["embedding"]["path"], local_files_only=True)
    encoder.instruction = "为这个句子生成表示以用于检索相关文章："
    encoder.batch_size = 16
    vectors = np.load(BASE / "vectors.npy", allow_pickle=False)
    if vectors.shape[0] != 707 or not np.isfinite(vectors).all():
        raise ValueError("Invalid original vectors")
    if not np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-4):
        raise ValueError("Original vectors not normalized")
    reranker = CrossEncoder(models["reranker"]["path"], local_files_only=True, max_length=512)
    chunks = [
        Chunk(c["chunk_id"], c["parent_id"], c["source_url"], c["retrieval_text"], "infra")
        for c in children
    ]
    lexical = BM25Index(chunks, statistics=lexical_statistics(chunks))
    by_id = {c["chunk_id"]: c for c in children}
    counters = {
        name: lambda text, t=t: len(t.encode(text, add_special_tokens=False))
        for name, t in tokenizers.items()
    }
    cases_by_id = {c["id"]: c for c in cases}
    for item in schedule(cases):
        case = cases_by_id[item["id"]]
        arm, language = item["arm"], item["query_language"]
        query = case["query" if language == "zh" else "query_en"]
        target = output / "rows" / f"{case['id']}-{arm}-{language}.json"
        if target.exists():
            if digest(target) != load(target.with_suffix(".sha256.json"))["sha256"]:
                raise ValueError("Checkpoint changed")
            saved = load(target)
            if (saved["id"], saved["arm"], saved["query_language"], saved["query"]) != (
                case["id"],
                arm,
                language,
                query,
            ):
                raise ValueError("Checkpoint query mismatch")
            continue
        started = perf_counter()
        row = {
            "id": case["id"],
            "arm": arm,
            "group_id": case["group_id"],
            "kind": case["kind"],
            "source_language": case["source_language"],
            "source_role": case["source_role"],
            "query_language": language,
            "query": query,
        }
        try:
            sparse, dense, scored_pairs = [], [], 0
            if arm in {"bm25", "hybrid_rerank"}:
                sparse = lexical.search(query, 30)
            if arm in {"dense", "hybrid_rerank"}:
                vector = np.asarray(encoder.encode([query], query=True)[0], dtype=np.float32)
                scores = vectors @ vector
                dense = sorted(
                    [(c["chunk_id"], float(s)) for c, s in zip(children, scores, strict=True)],
                    key=lambda x: (-x[1], x[0]),
                )[:30]
            ranked = (
                sparse if arm == "bm25" else dense if arm == "dense" else fusion([sparse, dense])
            )
            candidates = [cid for cid, _ in ranked]
            if arm == "hybrid_rerank":
                pairs = [(query, by_id[cid]["retrieval_text"]) for cid in candidates]
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
        print("retrieved", case["id"], arm, language, row["status"], flush=True)
    rows = [
        load(p)
        for p in sorted((output / "rows").glob("diag-*.json"))
        if not p.name.endswith(".sha256.json")
    ]
    summary = summarize(rows, cases)
    summary.update(
        questions=30,
        source_groups=len({c["group_id"] for c in cases}),
        outputs=len(rows),
        annotation="AI review pending independent human review",
        answer_accuracy=None,
        answer_generation_calls=0,
        default_changed=False,
        timing_scope="warm local model components plus instrumentation, initialization excluded",
        all_pages_note="cross-page union, additional context; not one model prompt",
    )
    for name, sha in load(output / "protocol.json")["inputs"].items():
        if digest(ROOT / name) != sha:
            raise ValueError("Experiment input changed during run")
    for directory in (BASE, SOURCE, audit):
        check_manifest(directory)
    save(output / "summary.json", summary)
    lines = [
        "# 固定30题中英文检索诊断",
        "",
        "同一707片段、原始正文向量、模型、候选/重排/分页预算；仅切换冻结的查询表达。",
        "AI证据复核及英文忠实度待独立审核；无答案生成，证据完整率不等于回答正确率。",
        "",
        "|配置|问法|候选完整|Top5完整|首页完整|跨页完整|失败|",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for arm, variants in summary["results"].items():
        for language, values in variants.items():
            numbers = [str(values[f]["numerator"]) + "/30" for f in FIELDS]
            lines.append("|" + "|".join([arm, language, *numbers, str(values["failures"])]) + "|")
    lines += [
        "",
        "|配对指标|EN−ZH|源文档簇95%CI|Holm校正p|英文新增/丢失题|",
        "|---|---:|---|---:|---|",
    ]
    for key, value in summary["paired_comparisons"].items():
        lo, hi = value["delta_rate_ci95"]
        lines.append(
            f"|{key}|{value['delta_count']}/30|[{lo:.3f}, {hi:.3f}]|"
            f"{value['holm_p_six_primary_tests']:.4f}|"
            f"{','.join(value['recovered_ids'])} / {','.join(value['lost_ids'])}|"
        )
    lines += [
        "",
        "分来源语言、来源角色及题型的完整分母见summary.json；逐题排名及实际分页见rows/。",
        "跨页使用更多总上下文，不能与首页作为同预算比较。保持中文embedding instruction不变。",
        "这是人工英文表达下整条检索/重排链路的语言效应，不能单独归因于embedding，",
        "也不等于自动翻译质量或英文模型升级收益。30题开发诊断不支持总体性能声明。",
        "旧轨迹按旧/新标签重算单列于audit目录，标签变更不算检索改善；默认服务未切换。",
    ]
    text = "\n".join(lines) + "\n"
    report = output / "README.md"
    if report.exists() and report.read_text() != text:
        raise ValueError("Frozen report differs")
    report.write_text(text)
    save(
        output / "artifacts-manifest.json",
        {
            p.relative_to(output).as_posix(): digest(p)
            for p in sorted(output.rglob("*"))
            if p.is_file() and p.name != "artifacts-manifest.json"
        },
    )
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--freeze-only", action="store_true")
    args = parser.parse_args()
    try:
        summary = run(args.audit.resolve(), args.output.resolve(), args.freeze_only)
        record_operation(
            "固定30题中英文真实检索对照",
            "验证跨语言损失，保持索引/预算及原中文不变",
            f"产物{args.output}；计划180条，实际阶段{summary.get('phase', 'completed')}",
            "AI标签/翻译待独立审核；无答案生成；跨页另用累计预算",
        )
        print(json.dumps(summary, ensure_ascii=False))
    except Exception as exc:
        record_operation(
            "中英对照中止", "保留现场，不自适应修改问题或重试失败", str(args.output), str(exc)
        )
        raise
