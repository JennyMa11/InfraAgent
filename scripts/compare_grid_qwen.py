"""Frozen same-chunk BGE/Qwen embedding comparison; no generation or test reads."""

import argparse
import ast
import importlib.metadata
import json
import os
import shutil
from collections import Counter, defaultdict
from dataclasses import asdict, fields, replace
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from continue_grid_v2 import memoize_alignment
from finalize_grid_v2 import verify_manifest
from grid_retrieval import BatchedReranker, grid_schedule
from operation_log import ROOT, record_operation
from report_grid_v2 import proportion
from run_grid_v2 import cached, save, seal

from infra_rag.benchmarking import canonical_hash, digest, write_new
from infra_rag.config import Settings
from infra_rag.embedding_experiments import source_document
from infra_rag.encoding import BGEEncoder, QwenEncoder
from infra_rag.grid_delivery import score_delivery
from infra_rag.grid_identity_view import canonical_points
from infra_rag.grid_metrics import latency, rank_metrics
from infra_rag.grid_packet_cache import PacketReranker
from infra_rag.grid_v2 import delivery_gate, source_ndcg
from infra_rag.models import Chunk
from infra_rag.paired_statistics import holm, paired_statistics
from infra_rag.service import RetrievalService

PRIOR = ROOT / "evals/embedding-chunks-v1/run-20261023-v3"
GRID = ROOT / "data/grid-v2/run-20261029-r8"
MODELS = ("bge", "qwen")


def load(path):
    return json.loads(Path(path).read_text())


def append(path, value):
    with path.open("a") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")
        stream.flush()


def qwen_contract(path):
    """An explicit model path makes the old literal/default-constant change immaterial."""
    tree = ast.parse(path.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "QwenEncoder")
    init = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "__init__")
    init.args.defaults[0] = ast.Constant("explicit-frozen-model-path")
    prompt = next(
        n.value
        for n in tree.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "QWEN_QUERY_PROMPT" for t in n.targets)
    )
    return canonical_hash([ast.dump(cls), ast.dump(prompt)])


def schedule(cases):
    ids = [f"{r['dataset']}:{r['id']}" for r in cases]
    return [
        {**j, "profile": profile}
        for profile, repetitions in (("frozen_english", 3), ("raw_query", 1))
        for j in grid_schedule(ids, MODELS, repetitions)
    ]


def settings(p, name, out):
    model = p["models"][name]
    options = {k: v for k, v in p["fingerprint"].items() if k in {f.name for f in fields(Settings)}}
    return replace(
        Settings(**options),
        backend=name,
        embedding_model=model["model"],
        embedding_revision=model["revision"] if name == "qwen" else None,
        embedding_device=p["device"],
        embedding_batch_size=2 if name == "qwen" else 16,
        data_dir=out / "indexes" / name,
        rerank=True,
        reranker_model=p["models"]["reranker"]["model"],
        candidate_k=30,
        rrf_constant=60,
        rerank_top_n=90,
        candidate_pool_cap=90,
        fusion_candidates="union",
        context_tokens=1200,
        context_chars=4000,
        context_mode="neighbors",
        context_policy="prefix",
        neighbor_expansion=True,
        lexical_query_mode="raw",
        query_language="none",
    )


def freeze(out):
    if out.exists():
        raise ValueError("Fresh output directory required")
    verify_manifest(GRID, "run-confirmation-manifest.json")
    old = load(PRIOR / "protocol.json")
    if digest(PRIOR / "protocol.json") != (PRIOR / "protocol.sha256").read_text().strip():
        raise ValueError("Prior protocol differs")
    reused = PRIOR / "indexes/qwen-structure/index.json"
    if digest(reused) != load(PRIOR / "index-manifest.json")["indexes/qwen-structure/index.json"]:
        raise ValueError("Prior vector snapshot differs")
    frozen_code = PRIOR / "implementation/src/infra_rag/encoding.py"
    if digest(frozen_code) != old["implementation"]["src/infra_rag/encoding.py"]:
        raise ValueError("Prior encoding snapshot differs")
    if qwen_contract(frozen_code) != qwen_contract(ROOT / "src/infra_rag/encoding.py"):
        raise ValueError("Qwen encoding changed; do not reuse old body vectors")
    packages = {k: importlib.metadata.version(k) for k in old["packages"]}
    if packages != old["packages"] or old["dtype"] != "float32" or old["batch_size"] != 2:
        raise ValueError("Vector encoding dependencies/precision differ")
    gp = load(GRID / "protocol.json")
    models = {
        "bge": gp["models"]["embedding"],
        "qwen": old["models"]["qwen"],
        "reranker": gp["models"]["reranker"],
    }
    for model in models.values():
        for name, sha in model["files"].items():
            if digest(Path(model["path"]) / name) != sha:
                raise ValueError("Model file changed")
    index = next((GRID / "indexes").glob("*/index.json"))
    cases = [
        {
            k: r[k]
            for k in (
                "id",
                "dataset",
                "group_id",
                "question_type",
                "query",
                "answerable",
                "resolved_gold",
            )
        }
        for r in load(GRID / "cases.json")
    ]
    out.mkdir(parents=True)
    save(out / "cases.json", cases)
    save(out / "queries.json", load(GRID / "queries.json"))
    save(out / "schedule.json", schedule(cases))
    code = [
        *sorted((ROOT / "src/infra_rag").glob("*.py")),
        Path(__file__),
        *[
            ROOT / "scripts" / n
            for n in (
                "run_grid_v2.py",
                "continue_grid_v2.py",
                "finalize_grid_v2.py",
                "report_grid_v2.py",
                "grid_retrieval.py",
                "grid_retrieval_v2.py",
                "operation_log.py",
            )
        ],
    ]
    for path in code:
        dest = out / "implementation" / path.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
    p = {
        "kind": "grid-v2-qwen-same-chunks-v1",
        "models": models,
        "device": old["device"],
        "dtype": "float32",
        "reranker_batch": 32,
        "packages": packages,
        "inputs": {
            str(f): digest(f)
            for f in (
                index,
                reused,
                PRIOR / "protocol.json",
                frozen_code,
                GRID / "cases.json",
                GRID / "queries.json",
                GRID / "protocol.json",
                GRID / "run-confirmation-manifest.json",
                out / "cases.json",
                out / "queries.json",
                out / "schedule.json",
            )
        },
        "sources": gp["sources"],
        "implementation": {str(f): digest(f) for f in code},
        "bge_index": str(index),
        "qwen_seed_index": str(reused),
        "fingerprint": load(index)["fingerprint"],
        "native_qwen_contract": qwen_contract(frozen_code),
        "vector_reuse": "identical raw body only; same model files, FP32/MPS, encoding AST/deps",
        "chunk_contract": "Identical raw chunks/IDs/locators for both; no rechunking",
        "dense_identity": "Only identical chunk+vector same-ID duplicates merged; conflicts fail",
        "budget_counter": "Frozen BGE tokenizer for BOTH;1200 tokens/4000 chars",
        "primary": "frozen_english;110dev x2models x3rounds=660 outputs",
        "diagnostic": "raw_query;110dev x2models x1round=220 outputs; separate from primary",
        "native_latency": "warm serial rotated models; search/embedding/ANN/rerank/pack; no HTTP",
        "caches": "immutable body vectors only; no query/retrieval/rerank result caches",
        "hard_gates": "each corpus delivery noninferior, zero losses each round, net>=2, "
        "p95<=1.5x, pairs<=90, no input truncation, all880 outputs",
        "stats": "rep0 primary paired group_id bootstrap10000 seed42; Holm two corpora; "
        "raw diagnostic separate; repeats not independent questions",
        "seed": 42,
        "generation_calls": 0,
        "test_holdout_read": False,
        "default_adoption": False,
        "independent_human_review": "pending",
    }
    save(out / "protocol.json", p)
    save(out / "protocol-sha256.json", {"sha256": digest(out / "protocol.json")})
    record_operation(
        "冻结Qwen3与Grid基线同分块对照",
        "只改变Embedding并单列原始查询诊断",
        str(out),
        "旧编码文件仅模型默认值常量化；AST/依赖/模型核验后复用向量",
    )


def verify(out):
    if digest(out / "protocol.json") != load(out / "protocol-sha256.json")["sha256"]:
        raise ValueError("Protocol differs")
    p = load(out / "protocol.json")
    for name, sha in {**p["inputs"], **p["sources"], **p["implementation"]}.items():
        if digest(name) != sha:
            raise ValueError("Frozen input differs: " + name)
    for model in p["models"].values():
        for name, sha in model["files"].items():
            if digest(Path(model["path"]) / name) != sha:
                raise ValueError("Model differs")
    return p


class LoggedEncoder:
    def __init__(self, encoder, name, out):
        self.encoder, self.name, self.out = encoder, name, out
        self.phase = "index"

    def __getattr__(self, name):
        return getattr(self.encoder, name)

    def encode(self, texts, *, query=False):
        attempt = str(uuid4())
        base = {
            "attempt": attempt,
            "model": self.name,
            "phase": self.phase,
            "query": query,
            "inputs": texts,
            "input_sha256": canonical_hash(texts),
        }
        start = perf_counter()
        append(self.out / "encoder-events.jsonl", {**base, "status": "started"})
        try:
            result = self.encoder.encode(texts, query=query)
            import torch

            if str(self.encoder.model.device) == "mps":
                torch.mps.synchronize()
            append(
                self.out / "encoder-events.jsonl",
                {
                    **base,
                    "status": "returned",
                    "texts": len(result),
                    "dimension": len(result[0]) if result else None,
                    "elapsed_ms": (perf_counter() - start) * 1000,
                },
            )
            return result
        except BaseException as exc:
            append(
                self.out / "encoder-events.jsonl",
                {
                    **base,
                    "status": "failed",
                    "completed_texts": None,
                    "error": type(exc).__name__,
                    "elapsed_ms": (perf_counter() - start) * 1000,
                },
            )
            raise


def vector_seeds(chunks, vectors):
    if len(chunks) != len(vectors):
        raise ValueError("Seed row/vector count mismatch")
    result = {}
    for c, vector in zip(chunks, vectors, strict=True):
        if c["content"] in result and result[c["content"]] != vector:
            raise ValueError("Conflicting vectors for identical seed body")
        result[c["content"]] = vector
    return result


def prepare_services(p, out):
    from sentence_transformers import CrossEncoder
    from transformers import AutoTokenizer

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    import torch

    if p["device"] == "mps" and not torch.backends.mps.is_available():
        raise ValueError("Frozen MPS unavailable; new protocol needed for paired CPU run")
    options = load(Path(p["models"]["bge"]["path"]) / "sentence_bert_config.json")
    budget = AutoTokenizer.from_pretrained(
        p["models"]["bge"]["path"],
        local_files_only=True,
        do_lower_case=options["do_lower_case"],
    )

    def count(text):
        return len(budget.encode(text, add_special_tokens=False))

    snapshot = load(p["bge_index"])
    chunks = [Chunk(**r) for r in snapshot["chunks"]]
    prior = load(p["qwen_seed_index"])
    seeds = vector_seeds(prior["chunks"], prior["vectors"])
    del prior
    reranker = BatchedReranker(
        CrossEncoder(
            p["models"]["reranker"]["path"],
            local_files_only=True,
            max_length=512,
            device=p["device"],
        ),
        32,
    )
    services, manifests = {}, {}
    for name in MODELS:
        start = perf_counter()
        cfg = settings(p, name, out)
        model = p["models"][name]
        real = (
            BGEEncoder(model["path"], device=p["device"], batch_size=16)
            if name == "bge"
            else (QwenEncoder(model["path"], device=p["device"], batch_size=2))
        )
        encoder = LoggedEncoder(real, name, out)
        service = RetrievalService(cfg, context_counter=count)
        service.encoder = encoder
        service.reranker = PacketReranker(
            reranker, out / "reranker-events" / name, p["models"]["reranker"]
        )
        service.reranker.enabled = False
        if name == "bge":
            vectors, missing = snapshot["vectors"], []
        else:
            missing = sorted({c.content for c in chunks} - seeds.keys())
            if missing:
                added = encoder.encode(missing)
                seeds.update(zip(missing, added, strict=True))
            vectors = [seeds[c.content] for c in chunks]
        logical, values, duplicates = canonical_points(chunks, vectors)
        service.chunks, service.vectors = chunks, vectors
        service._index_parents()
        folder = out / "indexes" / name
        folder.mkdir(parents=True, exist_ok=True)
        save(
            folder / "snapshot.json",
            {
                "fingerprint": cfg.fingerprint(),
                "chunks": [asdict(c) for c in chunks],
                "vectors": vectors,
            },
        )
        service.text_collection, service.clip_collection = service._collections(logical, values)
        if service.text_collection.count() != len(logical):
            raise ValueError("ANN point count differs")
        manifests[name] = {
            "fingerprint": cfg.fingerprint(),
            "raw_chunks": len(chunks),
            "logical_points": len(logical),
            "identical_id_aliases": duplicates,
            "raw_chunks_hash": canonical_hash([asdict(c) for c in chunks]),
            "snapshot_sha256": digest(folder / "snapshot.json"),
            "dimension": len(vectors[0]),
            "new_body_encodings": len(missing),
            "body_vectors_reused": len(chunks) - len(missing),
            "build_seconds_including_initialization": perf_counter() - start,
            "cold_build_cost": None,
            "note": "Verified vector reuse; not cold build performance",
        }
        services[name] = service
        print("prepared", name, "new bodies", len(missing), flush=True)
    if manifests["bge"]["raw_chunks_hash"] != manifests["qwen"]["raw_chunks_hash"]:
        raise ValueError("Chunk confounding")
    save(out / "index-manifest.json", manifests)
    return services, chunks


def run(out):
    p = verify(out)
    if (out / "run-started.json").exists():
        raise ValueError("No automatic retry of interrupted native attempts; use new directory")
    save(out / "run-started.json", {"run": out.name, "native_resume": False})
    services, chunks = prepare_services(p, out)
    cs = {c.id: c for c in chunks}
    docs = {s: source_document(Path(s).read_text(), h) for s, h in p["sources"].items()}
    cases = {f"{r['dataset']}:{r['id']}": r for r in load(out / "cases.json")}
    queries = load(out / "queries.json")
    memoize_alignment()
    for service in services.values():
        service.encoder.phase = "warmup"
        for query in (next(iter(queries.values())), next(iter(cases.values()))["query"]):
            service.search(query, top_k=5, strategy="hybrid")
    for n, job in enumerate(load(out / "schedule.json"), 1):
        r = cases[job["id"]]
        service = services[job["config"]]
        service.encoder.phase = job["profile"]
        query = queries[job["id"]] if job["profile"] == "frozen_english" else r["query"]
        path = out / "rows" / job["profile"] / job["config"] / f"{job['id']}-r{job['rep']}.json"
        d, context = {}, {}
        start = perf_counter()
        try:
            service.search(query, top_k=5, strategy="hybrid", diagnostics=d, context_pack=context)
            elapsed = (perf_counter() - start) * 1000
            if len(d["candidates"]) > 90 or any(v["would_truncate"] for v in d["rerank"]["pairs"]):
                raise ValueError("Native input/pair budget violation")
            if context["used_tokens"] > 1200 or context["used_characters"] > 4000:
                raise ValueError("Native pack budget violation")
            q = {
                **r,
                "evidence_alternatives": r["resolved_gold"]["evidence_alternatives"]
                if r["answerable"]
                else [],
            }

            def score(ids, question=q):
                return score_delivery(
                    [
                        {"chunk_id": cid, "source": cs[cid].source, "content": cs[cid].content}
                        for cid in ids
                    ],
                    question,
                    cs,
                    docs,
                )

            relevant = {
                s["absolute_source"] for g in q["evidence_alternatives"] for s in g["spans"]
            }
            row = {
                **job,
                "id": r["id"],
                "dataset": r["dataset"],
                "group_id": r["group_id"],
                "answerable": r["answerable"],
                "run_id": out.name,
                "query": query,
                "status": "completed",
                "elapsed_ms": elapsed,
                "diagnostics": d,
                "context": context,
                "delivery5": score_delivery(context["evidence"], q, cs, docs),
                "candidate": score(d["candidates"]),
                "ranked_complete5": score(d["ranked_ids"][:5]),
                "rank_metrics5": rank_metrics(
                    [cs[cid].source for cid in d["ranked_ids"]], relevant, 5
                )
                if relevant
                else None,
                "rank_metrics10": rank_metrics(
                    [cs[cid].source for cid in d["ranked_ids"]], relevant, 10
                )
                if relevant
                else None,
                "ndcg5": source_ndcg([cs[cid].source for cid in d["ranked_ids"]], relevant, 5),
                "pairs": len(d["rerank"]["pairs"]),
            }
            seal(path, row)
        except BaseException as exc:
            if not path.exists():
                seal(
                    path,
                    {
                        **job,
                        "status": "failed",
                        "error": type(exc).__name__ + ": " + str(exc),
                        "elapsed_ms": (perf_counter() - start) * 1000,
                        "diagnostics": d,
                        "context": context,
                    },
                )
            raise
        if n % 55 == 0:
            print("completed", n, "/880", job["profile"], flush=True)
    report(out)


def summarize(rs):
    result = {}
    for ds in ("official", "repository"):
        group = [r for r in rs if r["dataset"] == ds]
        pos = [r for r in group if r["answerable"]]
        result[ds] = {
            "n": len(group),
            "unique_questions": len({r["id"] for r in group}),
            "candidate_complete": proportion([r["candidate"]["complete"] for r in pos]),
            "required_recall": proportion([r["candidate"]["coverage"] for r in pos]),
            "ranked_complete5": proportion([r["ranked_complete5"]["complete"] for r in pos]),
            "delivery5": proportion([r["delivery5"]["complete"] for r in pos]),
            "hit5": proportion([r["rank_metrics5"]["hit"] for r in pos]),
            "recall5": proportion([r["rank_metrics5"]["recall"] for r in pos]),
            "mrr10": proportion([r["rank_metrics10"]["mrr"] for r in pos]),
            "ndcg5": proportion([r["ndcg5"] for r in pos]),
            "latency_ms": latency([r["elapsed_ms"] for r in group]),
            "pairs": sum(r["pairs"] for r in group),
        }
    return result


def report(out):
    verify(out)
    scheduled = load(out / "schedule.json")
    observed, grouped = set(), defaultdict(list)
    for f in (out / "rows").rglob("*.json"):
        if f.name.endswith(".sha256.json"):
            continue
        r = cached(f)
        if r["status"] != "completed":
            raise ValueError("Failed output retained")
        key = r["profile"], r["config"], f"{r['dataset']}:{r['id']}", r["rep"]
        if key in observed:
            raise ValueError("Duplicate output")
        observed.add(key)
        grouped[r["profile"], r["config"]].append(r)
    expected = {(j["profile"], j["config"], j["id"], j["rep"]) for j in scheduled}
    if observed != expected or len(expected) != 880:
        raise ValueError("Missing/unexpected outputs")
    summary = {
        profile: {name: summarize(grouped[profile, name]) for name in MODELS}
        for profile in ("frozen_english", "raw_query")
    }
    gates, stats = {}, {}
    rounds = {}
    for profile, count in (("frozen_english", 3), ("raw_query", 1)):
        rounds[profile] = {}
        for rep in range(count):
            before = [r for r in grouped[profile, "bge"] if r["rep"] == rep]
            after = [r for r in grouped[profile, "qwen"] if r["rep"] == rep]
            gates[f"{profile}:{rep}"] = delivery_gate(after, before)
            rounds[profile][str(rep)] = {
                name: summarize([r for r in grouped[profile, name] if r["rep"] == rep])
                for name in MODELS
            }
            if rep == 0:
                for ds in ("official", "repository"):
                    stats[f"{profile}:{ds}"] = paired_statistics(
                        [{**r, "delivered": r["delivery5"]} for r in before if r["dataset"] == ds],
                        [{**r, "delivered": r["delivery5"]} for r in after if r["dataset"] == ds],
                    )
    timing_gate = {
        ds: summary["frozen_english"]["qwen"][ds]["latency_ms"]["p95_ms"]
        <= 1.5 * summary["frozen_english"]["bge"][ds]["latency_ms"]["p95_ms"]
        for ds in ("official", "repository")
    }
    quality_pass = all(
        gates[f"frozen_english:{rep}"]["eligible"] and gates[f"frozen_english:{rep}"]["net"] >= 2
        for rep in range(3)
    )
    save(out / "summary.json", summary)
    save(out / "rounds.json", rounds)
    save(out / "paired-changes.json", gates)
    save(
        out / "statistics.json",
        {
            "contrasts": stats,
            "holm_primary": holm(
                {
                    k: v["cluster_permutation_p"]
                    for k, v in stats.items()
                    if k.startswith("frozen_english:")
                }
            ),
            "diagnostic_not_used_for_selection": True,
        },
    )
    resources = {}
    for name, path in [
        ("encoder", out / "encoder-events.jsonl"),
        *[(name, out / "reranker-events" / name / "events.jsonl") for name in MODELS],
    ]:
        es = [json.loads(s) for s in path.read_text().splitlines()]
        starts = {e["attempt"] for e in es if e["status"] == "started"}
        ends = {e["attempt"] for e in es if e["status"] == "returned"}
        if starts != ends or any(
            e["status"] in ("failed", "input_rejected", "cache_hit") for e in es
        ):
            raise ValueError("Model attempt ledger failure")
        resources[name] = {
            "events": dict(Counter(e["status"] for e in es)),
            "returned_texts_or_pairs": sum(
                e.get("texts", e.get("actual_pairs", 0)) for e in es if e["status"] == "returned"
            ),
        }
    save(
        out / "resources.json", {"models": resources, "generation_calls": 0, "model_cost_usd": None}
    )
    save(
        out / "decision.json",
        {
            "adopt": False,
            "quality_pass": quality_pass,
            "latency_pass": timing_gate,
            "candidate_pass": quality_pass and all(timing_gate.values()),
            "independent_human_review": "pending",
            "test_holdout_read": False,
            "answer_correctness": None,
            "generation_calls": 0,
        },
    )
    text = [
        "# Qwen3-Embedding-0.6B 与 Grid 基线对照",
        "",
        "同一450字符结构语料，Hybrid K30/RRF60/union，BGE reranker batch32，Top5+邻段。",
        "预算固定用BGE tokenizer的1200 token/4000字符；未重新分块。",
        "主对照为110个冻结英文查询×2模型×3轮；原始查询110×2另列，仅诊断。",
        "重复不是独立题；正例官方54、仓库50，6道负例不进证据覆盖分母。",
        "",
        "| 查询 | 数据集 | Embedding | 交付完整（输出分母） | Hit@5 | MRR@10 | P95 ms |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for profile, arms in summary.items():
        for name, datasets in arms.items():
            for ds, m in datasets.items():
                v = m["delivery5"]
                text.append(
                    f"| {profile} | {ds} | {name} | {v['numerator']}/{v['denominator']} | "
                    f"{m['hit5']['value']:.3f} | {m['mrr10']['value']:.3f} | "
                    f"{m['latency_ms']['p95_ms']:.1f} |"
                )
    text += [
        "",
        f"主对照质量门槛：{quality_pass}；P95门槛：{timing_gate}。",
        "逐题净变化/丢失见paired-changes，按题组bootstrap/Holm见statistics，分轮见rounds。",
        "计时为同设备暖启动、串行交替、无查询/检索/重排结果缓存；含本地账目开销，",
        "覆盖编码、ANN、重排、打包，不含HTTP或答案生成，不是线上端到端延迟。",
        "文档向量只复用同输入、同模型/实现/依赖/FP32设备的已验哈希数据；新增正文单独编码。",
        "不能把复用建库时间当作冷建库性能；两组有独立索引指纹和目录。",
        "这是AI gold下的开发结果，人工事实审核pending；没有答案正确率。",
        "未读test/holdout，默认不采用。",
        "",
    ]
    (out / "report.md").write_text("\n".join(text))
    record_operation(
        "Qwen3同分块对照完成",
        "比较Embedding收益而不混入分块和预算差异",
        str(out),
        "独立人工审核pending，不采用默认",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("freeze", "run", "report"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        {"freeze": freeze, "run": run, "report": report}[args.phase](args.out)
    except BaseException as exc:
        record_operation(
            "Qwen对照停止",
            "保留失败，不静默重试",
            str(args.out),
            type(exc).__name__ + ": " + str(exc),
        )
        raise
    finally:
        if args.out.exists():
            manifest = args.out / (args.phase + "-manifest.json")
            if not manifest.exists():
                write_new(
                    manifest,
                    {
                        str(f.relative_to(args.out)): digest(f)
                        for f in args.out.rglob("*")
                        if f.is_file()
                    },
                )


if __name__ == "__main__":
    main()
