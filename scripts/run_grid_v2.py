"""Frozen-query dual-dev staged grid. No generation, HTTP serving or confirmation reads."""

import argparse
import copy
import json
import shutil
from bisect import bisect_right
from collections import defaultdict
from dataclasses import asdict, fields, replace
from pathlib import Path
from time import perf_counter

from benchmark_native_pagination import local_models
from grid_retrieval import BatchedReranker, grid_schedule
from grid_retrieval_v2 import V4, V6, freeze, load, rows, verify
from operation_log import ROOT, record_operation

from infra_rag.benchmarking import canonical_hash, digest, write_new
from infra_rag.chunking import chunk_text, stable_id
from infra_rag.complete_context import pack_complete_context
from infra_rag.config import Settings
from infra_rag.context import pack_context
from infra_rag.embedding_experiments import source_document
from infra_rag.exact_search import ExactCollection
from infra_rag.grid_delivery import score_delivery
from infra_rag.grid_metrics import latency, rank_metrics
from infra_rag.grid_token_counter import quality_counter
from infra_rag.grid_v2 import Arm, delivery_gate, recall_arms, refinements, source_ndcg
from infra_rag.models import Chunk, Hit
from infra_rag.paired_statistics import holm, paired_statistics
from infra_rag.preprocessing import VERSION, preprocess, units
from infra_rag.service import RetrievalService
from infra_rag.vector_cache import VectorCache

INDEXES = {
    "I0": ("structure", 450),
    "I1": ("structure", 300),
    "I2": ("structure", 600),
    "I3": ("window", 450),
}
BASE = Arm(rerank=True)


def save(path, value):
    if path.exists():
        if load(path) != json.loads(json.dumps(value)):
            raise ValueError(f"Frozen artifact differs: {path}")
    else:
        write_new(path, value)


def seal(path, value):
    write_new(path, value)
    write_new(path.with_suffix(".sha256.json"), {"sha256": digest(path)})


def cached(path):
    if not path.exists():
        return None
    if digest(path) != load(path.with_suffix(".sha256.json"))["sha256"]:
        raise ValueError(f"Cache/trace integrity mismatch: {path}")
    return load(path)


def prepare(out):
    freeze(out, "frozen")
    script = Path(__file__).resolve()
    target = out / "implementation/scripts/run_grid_v2.py"
    shutil.copyfile(script, target)
    v1 = ROOT / "data/grid-v2/v1-replay-20261029-r1"
    if load(v1 / "decision.json") != {"passed": True, "matched": 60, "expected": 60}:
        raise ValueError("v1 gate not passed")
    write_new(
        out / "grid-spec.json",
        {
            "script_sha256": digest(script),
            "v1_proof": {
                str(v1 / n): digest(v1 / n)
                for n in ("protocol.json", "decision.json", "artifacts-manifest.json")
            },
            "indexes": INDEXES,
            "profile": "historical frozen scoring_query; no translation calls",
            "quality_counter": "Verified BERT blank-line additive memoization; native counter "
            "unchanged in uncached latency runs. Equality audit: "
            "evals/grid-v2/token-counter-equivalence-r5.json",
            "candidate_cache_context": "Transient legacy text is discarded; final Top5/10 packs "
            "are rebuilt under the shared1200-token/4000-character budget. Latency trials "
            "use the real configured packing path, never this cache preparation path.",
            "recipe": "All indexes rebuilt with corrected same-line/matching-length fence parser; "
            "I0 is a NEW repaired baseline, not the historical frozen index. "
            "I1/I2 use same structural recipe, not model semantic splitting.",
            "preprocessing_version": VERSION,
            "A": "4 indexes, hybrid K30, no rerank; choose best and distinct strategy",
            "B": "9 arms/index; choose candidate complete, required recall, fastest non-loss",
            "C": "3 arms x rerank off/on, pack5/10 from one ranking",
            "D": "up to2 feasible champions x up to7 applicable single-factor variants",
            "E": "champion ablations, not used for selection",
            "selection": "paired delivery noninferior per corpus, zero complete losses; "
            "net>=2 for adoption candidate, ties fewer pairs then latency then name",
            "warm_repeat": 3,
            "ann_repeat": 3,
            "pair_cap": 90,
            "build_checkpoint_seconds": 1800,
            "http_services": False,
            "default_adoption": False,
            "generation_calls": 0,
            "bootstrap_samples": 10000,
            "seed": 42,
            "test_holdout_read": False,
        },
    )


class Grid:
    def __init__(self, out):
        self.out, self.p = out, verify(out)
        spec = load(out / "grid-spec.json")
        if digest(Path(__file__)) != spec["script_sha256"]:
            raise ValueError("Runner changed; use a new run")
        for path, sha in spec["v1_proof"].items():
            if digest(path) != sha:
                raise ValueError("v1 proof changed")
        self.identity = canonical_hash([self.p, spec])
        self.cases = {f"{r['dataset']}:{r['id']}": r for r in load(out / "cases.json")}
        self.queries = {
            key: load(V4 / "bundles" / r["dataset"] / (r["id"] + ".json"))["B5"]["scoring_query"]
            for key, r in self.cases.items()
        }
        save(out / "queries.json", self.queries)
        self.docs = {
            s: source_document(Path(s).read_text(), h) for s, h in self.p["sources"].items()
        }
        self.original = [Chunk(**c) for c in load(Path(self.p["corpus"]) / "chunks.json")]
        snapshot = load(Path(self.p["corpus"]) / "index/index.json")
        names = {f.name for f in fields(Settings)}
        opts = {k: v for k, v in snapshot["fingerprint"].items() if k in names}
        opts["preprocessing_version"] = VERSION
        self.settings = Settings(
            **opts, rerank=True, fusion_candidates="union", candidate_pool_cap=90
        )
        self.service = RetrievalService(replace(self.settings, data_dir=out / "model-runtime"))
        local_models(self.service, self.p["models"])
        self.encoder = self.service.encoder
        self.seed_vectors = {
            c["content"]: v for c, v in zip(snapshot["chunks"], snapshot["vectors"], strict=True)
        }
        self.raw_reranker = self.service.reranker
        self.service.reranker = BatchedReranker(self.raw_reranker, 32)
        self.count = quality_counter(self.encoder.model.tokenizer)
        self.indexes = {}
        self.ann_collections = {}
        self.lexical_by_index = {}
        self.exact_collections = {}

    def historical(self):
        from benchmark_original_rag_v7 import evaluation
        from transformers import AutoTokenizer

        model = self.p["models"]["embedding"]
        opts = load(Path(model["path"]) / "sentence_bert_config.json")
        t = AutoTokenizer.from_pretrained(
            model["path"], local_files_only=True, do_lower_case=opts["do_lower_case"]
        )

        def count(s):
            return len(t.encode(s, add_special_tokens=False))

        reference = {
            (r["dataset"], r["id"]): r
            for r in rows(V6 / "rows.jsonl")
            if r["arm"] == "B-k8-l0-p1-n0"
        }
        for key, r in self.cases.items():
            path = self.out / "historical" / (key + ".json")
            if cached(path) is not None:
                continue
            b = load(V4 / "bundles" / r["dataset"] / (r["id"] + ".json"))["B5"]
            result = evaluation(r, "historical-v6", b, {c.id: c for c in self.original}, count)
            seal(path, result)
            if result["context"] != reference[r["dataset"], r["id"]]["context"]:
                raise ValueError(f"Historical context mismatch: {key}")
        save(self.out / "historical-gate.json", {"passed": True, "outputs": 110})

    def index(self, name):
        if name in self.indexes:
            return self.indexes[name]
        kind, size = INDEXES[name]
        cfg = replace(
            self.settings,
            chunk_size=size,
            chunk_strategy="window" if kind == "window" else "semantic",
        )
        folder = self.out / "indexes" / canonical_hash(cfg.fingerprint())[:16]
        folder.mkdir(parents=True, exist_ok=True)
        snapshot = folder / "index.json"
        started = perf_counter()
        if snapshot.exists():
            meta = load(folder / "manifest.json")
            if digest(snapshot) != meta["index_sha256"]:
                raise ValueError("Index integrity mismatch")
            data = load(snapshot)
            chunks = [Chunk(**c) for c in data["chunks"]]
            vectors = data["vectors"]
        else:
            by_source = defaultdict(list)
            for c in self.original:
                by_source[c.source].append(c)
            chunks = []
            for source, old in by_source.items():
                if kind == "structure":
                    meta = {
                        k: v
                        for k, v in old[0].metadata.items()
                        if k
                        in {
                            "collection",
                            "document_id",
                            "url",
                            "commit",
                            "release",
                            "sha256",
                            "product",
                            "metadata_method",
                            "preprocessing_version",
                        }
                    }
                    meta["preprocessing_version"] = VERSION
                    parsed, _ = preprocess(
                        Path(source).read_text(), source, meta, self.encoder, cfg, old
                    )
                else:
                    doc = self.docs[source]
                    parsed = chunk_text(doc["text"], source, old[0].domain, self.encoder, cfg)
                    headings = [
                        (u["start"], u["heading"])
                        for u in units(doc["text"].splitlines())
                        if u["kind"] == "heading"
                    ]
                    starts = [h[0] for h in headings]
                    for c in parsed:
                        pos = bisect_right(starts, c.start_line) - 1
                        line, heading = headings[pos] if pos >= 0 else (1, "")
                        c.heading = heading
                        c.parent_id = stable_id(source, "grid-v2-section", line, heading)
                        c.metadata = {**old[0].metadata, **c.metadata}
                        c.metadata.pop("source_aliases", None)
                        c.metadata["original_lines"] = [c.start_line, c.end_line]
                        c.metadata["preprocessing_version"] = VERSION
                        c.metadata["body_type"] = "window"
                chunks.extend(parsed)
                if perf_counter() - started > 1800:
                    raise TimeoutError(f"Index {name} exceeded build checkpoint")
            # Exact dedup only, matching the preprocessing rule; preserve every source alias.
            seen, retained = {}, []
            for c in chunks:
                k = (
                    c.content.strip(),
                    c.metadata.get("product"),
                    c.metadata.get("release") or c.source,
                )
                if len(c.content.strip()) >= 100 and k in seen and seen[k].source != c.source:
                    seen[k].metadata.setdefault("source_aliases", []).append(
                        {
                            "id": c.id,
                            "source": c.source,
                            "locator": c.locator,
                            "content": c.content,
                            "metadata": c.metadata,
                        }
                    )
                else:
                    seen.setdefault(k, c)
                    retained.append(c)
            chunks = retained
            cache = VectorCache(self.out / "embedding-cache.sqlite3")
            namespace = canonical_hash([self.p["models"]["embedding"], "body-v1"])
            seeds = {cache.key(namespace, body): v for body, v in self.seed_vectors.items()}
            vectors, _ = cache.encode(
                namespace, [c.content for c in chunks], self.encoder.encode, seeds=seeds
            )
            write_new(
                snapshot,
                {
                    "fingerprint": cfg.fingerprint(),
                    "chunks": [asdict(c) for c in chunks],
                    "vectors": vectors,
                },
            )
            save(
                folder / "manifest.json",
                {
                    "index_sha256": digest(snapshot),
                    "name": name,
                    "fingerprint": cfg.fingerprint(),
                    "recipe": kind,
                    "build_seconds": perf_counter() - started,
                    "chunks": len(chunks),
                    "chunk_tokens": {
                        k.replace("_ms", ""): v
                        for k, v in latency([self.count(c.content) for c in chunks]).items()
                    },
                },
            )
        result = (chunks, vectors, folder, cfg)
        self.indexes[name] = result
        return result

    def activate(self, arm, ann=False):
        chunks, vectors, folder, cfg = self.index(arm.index)
        s = self.service
        # Indexes are immutable. Rotation must preserve each index's warmed sparse state.
        s.lexical_cache = self.lexical_by_index.setdefault(arm.index, {})
        s.settings = replace(
            cfg,
            data_dir=folder,
            rerank=arm.rerank,
            candidate_k=arm.k,
            rrf_constant=arm.rrf,
            rerank_top_n=arm.depth,
            fusion_candidates=arm.fusion,
            context_policy=arm.policy,
            neighbor_expansion=arm.neighbors,
        )
        if s.chunks is not chunks:
            s.chunks, s.vectors = chunks, vectors
            s._index_parents()
            if arm.index not in self.exact_collections:
                self.exact_collections[arm.index] = ExactCollection(chunks, vectors)
            s.text_collection = self.exact_collections[arm.index]
        if ann:
            s.index_fingerprint = cfg.fingerprint()
            if arm.index not in self.ann_collections:
                self.ann_collections[arm.index] = s._collections(chunks, vectors)
            s.text_collection, s.clip_collection = self.ann_collections[arm.index]
        return {c.id: c for c in chunks}

    def candidates(self, arm, key):
        signature = canonical_hash(
            [self.identity, arm.index, arm.strategy, arm.k, arm.rrf, arm.fusion, self.queries[key]]
        )
        path = self.out / "cache/candidates" / (signature + ".json")
        result = cached(path)
        if result is None:
            self.activate(replace(arm, rerank=False, policy="prefix"))
            # Search always packs context. Avoid expensive unused neighbor/token packing here;
            # only candidate IDs and ranks enter this cache. Actual delivery is packed below.
            self.service.settings = replace(self.service.settings, context_mode="legacy")
            d = {}
            started = perf_counter()
            self.service.search(self.queries[key], top_k=10, strategy=arm.strategy, diagnostics=d)
            result = {"diagnostics": d, "elapsed_ms": (perf_counter() - started) * 1000}
            seal(path, result)
        return result

    def output(self, arm, key, stage):
        cs = self.activate(arm)
        r = self.cases[key]
        q = {
            **r,
            "evidence_alternatives": r["resolved_gold"]["evidence_alternatives"]
            if r["answerable"]
            else [],
        }
        candidate = self.candidates(arm, key)
        d = candidate["diagnostics"]
        scores = {v["chunk_id"]: v["rrf_score"] for v in d["fusion"]}
        ids = d["candidates"]
        hits = [Hit(cs[cid], scores[cid]) for cid in ids]
        if arm.rerank:
            prefix = hits[: arm.depth]
            pairs = [(self.queries[key], h.chunk.content) for h in prefix]
            details = self.service._rerank_diagnostics(pairs) if pairs else {"pairs": []}
            if any(v["would_truncate"] for v in details["pairs"]):
                raise ValueError(f"Reranker input truncation: {stage}:{arm.identity()}:{key}")
            sig = canonical_hash(
                [
                    self.identity,
                    self.queries[key],
                    [(h.chunk.id, h.chunk.content) for h in prefix],
                    arm.depth,
                    32,
                ]
            )
            path = self.out / "cache/scores" / (sig + ".json")
            scored = cached(path)
            if scored is None:
                started = perf_counter()
                values = list(map(float, self.service.reranker.predict(pairs))) if pairs else []
                scored = {"scores": values, "elapsed_ms": (perf_counter() - started) * 1000}
                seal(path, scored)
            for h, value in zip(prefix, scored["scores"], strict=True):
                h.rerank_score = value
            prefix.sort(key=lambda h: (-h.rerank_score, -h.score, h.chunk.id))
            hits = prefix + hits[len(prefix) :]
        result = {
            "id": r["id"],
            "dataset": r["dataset"],
            "group_id": r["group_id"],
            "answerable": r["answerable"],
            "config": arm.identity(),
            "stage": stage,
            "query": self.queries[key],
            "candidate_ids": ids,
            "ranked_ids": [h.chunk.id for h in hits],
            "pairs": min(len(ids), arm.depth) if arm.rerank else 0,
            "candidate": score_delivery(
                [
                    {"chunk_id": cid, "source": cs[cid].source, "content": cs[cid].content}
                    for cid in ids
                ],
                q,
                cs,
                self.docs,
            ),
            "candidate_wall_ms": candidate["elapsed_ms"],
            "diagnostics": d,
        }
        relevant = {s["absolute_source"] for g in q["evidence_alternatives"] for s in g["spans"]}
        for k in (5, 10):
            selected = copy.deepcopy(hits[:k])
            if arm.policy == "complete":
                packed = pack_complete_context(
                    selected, copy.deepcopy(hits), self.queries[key], self.count, 1200, 4000
                )
            else:
                packed = pack_context(
                    selected,
                    self.service.parent_index,
                    self.count,
                    1200,
                    4000,
                    neighbor_expansion=arm.neighbors,
                )
            if packed["used_tokens"] > 1200 or packed["used_characters"] > 4000:
                raise ValueError("Context budget violation")
            result[f"pack{k}"] = packed
            result[f"delivery{k}"] = score_delivery(packed["evidence"], q, cs, self.docs)
            full = [
                {"chunk_id": h.chunk.id, "source": h.chunk.source, "content": h.chunk.content}
                for h in hits[:k]
            ]
            result[f"ranked_complete{k}"] = score_delivery(full, q, cs, self.docs)
            result[f"rank_metrics{k}"] = (
                rank_metrics([h.chunk.source for h in hits], relevant, k) if relevant else None
            )
            result[f"ndcg{k}"] = source_ndcg([h.chunk.source for h in hits], relevant, k)
        return result

    def stage(self, name, arms):
        arms = {a.identity(): a for a in arms}
        schedule = grid_schedule(self.cases, list(arms))
        save(self.out / "schedules" / (name + ".json"), schedule)
        result = defaultdict(list)
        for job in schedule:
            arm = arms[job["config"]]
            path = self.out / "rows" / name / job["config"] / (job["id"] + ".json")
            row = cached(path)
            if row is None:
                try:
                    row = self.output(arm, job["id"], name)
                    row.update(status="completed", run_id=self.out.name, repetition=0)
                except Exception as exc:
                    seal(
                        path,
                        {**job, "status": "failed", "error": str(exc), "run_id": self.out.name},
                    )
                    raise
                seal(path, row)
            if row["status"] != "completed":
                raise ValueError("Failed output retained; no retries")
            result[job["config"]].append(row)
            if sum(map(len, result.values())) % 55 == 0:
                print(name, sum(map(len, result.values())), "/", len(schedule), flush=True)
        summaries = {key: summary(value) for key, value in result.items()}
        save(self.out / "summaries" / (name + ".json"), summaries)
        record_operation(
            f"Grid v2阶段{name}完成",
            "按冻结配置进行双库开发实验",
            f"{len(schedule)}输出，生成调用0；{self.out}",
        )
        return result

    def timed(self, name, arms, ann=False):
        """Fresh searches only; candidate and score result caches are never consulted."""
        arms = {a.identity(): a for a in arms}
        schedule = grid_schedule(self.cases, list(arms), 3)
        save(self.out / "schedules" / (name + ".json"), schedule)
        for arm in arms.values():
            self.activate(arm, ann=ann)
            self.service.search(next(iter(self.queries.values())), top_k=5, strategy=arm.strategy)
        result = defaultdict(list)
        for job in schedule:
            path = self.out / "rows" / name / job["config"] / f"{job['id']}-r{job['rep']}.json"
            row = cached(path)
            if row is None:
                arm = arms[job["config"]]
                cs = self.activate(arm, ann=ann)
                r = self.cases[job["id"]]
                q = {
                    **r,
                    "evidence_alternatives": r["resolved_gold"]["evidence_alternatives"]
                    if r["answerable"]
                    else [],
                }
                d, context = {}, {}
                start = perf_counter()
                try:
                    self.service.search(
                        self.queries[job["id"]],
                        top_k=5,
                        strategy=arm.strategy,
                        diagnostics=d,
                        context_pack=context,
                    )
                    elapsed = (perf_counter() - start) * 1000
                    assert len(d["candidates"]) <= 90
                    assert not any(p["would_truncate"] for p in d["rerank"].get("pairs", []))
                    score = score_delivery(context["evidence"], q, cs, self.docs)
                    row = {
                        **job,
                        "id": r["id"],
                        "dataset": r["dataset"],
                        "group_id": r["group_id"],
                        "answerable": r["answerable"],
                        "delivery5": score,
                        "diagnostics": d,
                        "context": context,
                        "elapsed_ms": elapsed,
                        "status": "completed",
                    }
                except Exception as exc:
                    seal(
                        path,
                        {
                            **job,
                            "status": "failed",
                            "elapsed_ms": (perf_counter() - start) * 1000,
                            "error": str(exc),
                            "diagnostics": d,
                            "context": context,
                        },
                    )
                    raise
                seal(path, row)
            if row["status"] != "completed":
                raise ValueError("Timed failure retained, no retries")
            result[job["config"]].append(row)
            n = sum(map(len, result.values()))
            if n % 55 == 0:
                print(name, n, "/", len(schedule), flush=True)
        measured = {
            ident: {
                ds: latency([r["elapsed_ms"] for r in values if r["dataset"] == ds])
                for ds in ("official", "repository")
            }
            for ident, values in result.items()
        }
        save(self.out / "summaries" / (name + ".json"), measured)
        return result, measured


def summary(rows_):
    result = {}
    for ds in ("official", "repository"):
        positive = [r for r in rows_ if r["dataset"] == ds and r["answerable"]]

        def proportion(values):
            return {
                "numerator": sum(values),
                "denominator": len(values),
                "value": sum(values) / len(values) if values else None,
                "coverage": 1.0,
            }

        result[ds] = {
            "positive": len(positive),
            "negative": sum(r["dataset"] == ds and not r["answerable"] for r in rows_),
            "candidate_complete": proportion([r["candidate"]["complete"] for r in positive]),
            "required_recall": proportion([r["candidate"]["coverage"] for r in positive]),
            "delivery5": proportion([r["delivery5"]["complete"] for r in positive]),
        }
    result["pairs"] = sum(r["pairs"] for r in rows_)
    result["quality_cache_timing_not_production_latency"] = True
    return result


def quality_order(arm, data):
    s = summary(data[arm.identity()])
    return (
        -sum(s[ds]["delivery5"]["numerator"] for ds in ("official", "repository")),
        s["pairs"],
        arm.identity(),
    )


def run(out):
    g = Grid(out)
    g.historical()
    baseline = g.stage("baseline", [BASE])[BASE.identity()]
    a = g.stage("A", [Arm(index=i) for i in INDEXES])

    def index_order(i):
        rs = a[Arm(index=i).identity()]
        return (
            -sum(r["candidate"]["complete"] for r in rs if r["answerable"]),
            -sum(r["candidate"]["coverage"] for r in rs if r["answerable"]),
            len(g.index(i)[0]),
            i,
        )

    first = min(INDEXES, key=index_order)
    second = min((i for i in INDEXES if INDEXES[i][0] != INDEXES[first][0]), key=index_order)
    save(out / "index-selection.json", [first, second])
    b_arms = [a for i in (first, second) for a in recall_arms(i)]
    b = g.stage("B", b_arms)
    selected = []
    for field in ("complete", "coverage"):
        best = min(
            b_arms,
            key=lambda a: (
                -sum(r["candidate"][field] for r in b[a.identity()] if r["answerable"]),
                a.identity(),
            ),
        )
        if best not in selected:
            selected.append(best)
    # Fastest non-loss is chosen only from actual observed candidate-search timing.
    ref = {(r["dataset"], r["id"]): r for r in baseline if r["answerable"]}
    safe = [
        a
        for a in b_arms
        if all(
            not ref[r["dataset"], r["id"]]["candidate"]["complete"] or r["candidate"]["complete"]
            for r in b[a.identity()]
            if r["answerable"]
        )
    ]
    if safe:
        fastest = min(
            safe,
            key=lambda a: (
                latency([r["candidate_wall_ms"] for r in b[a.identity()]])["p95_ms"],
                a.identity(),
            ),
        )
        if fastest not in selected:
            selected.append(fastest)
    save(out / "recall-selection.json", [asdict(a) for a in selected])
    c_arms = [replace(a, rerank=flag) for a in selected for flag in (False, True)]
    c = g.stage("C", c_arms)
    feasible = [a for a in c_arms if delivery_gate(c[a.identity()], baseline)["eligible"]]
    champions = sorted(feasible, key=lambda a: quality_order(a, c))[:2]
    d_arms = list({a.identity(): a for champ in champions for a in refinements(champ)}.values())
    d = g.stage("D", d_arms) if d_arms else {}
    all_data = {BASE.identity(): baseline, **c, **d}
    all_arms = {a.identity(): a for a in [BASE, *c_arms, *d_arms]}
    eligible = [
        a for a in all_arms.values() if delivery_gate(all_data[a.identity()], baseline)["eligible"]
    ]
    winner = min(eligible, key=lambda a: quality_order(a, all_data))
    save(
        out / "quality-selection.json",
        {
            "winner": asdict(winner),
            "gate": delivery_gate(all_data[winner.identity()], baseline),
            "adopt": False,
        },
    )
    # All ablations are diagnostic, never fed back into selection.
    ablations = [
        replace(winner, strategy="dense"),
        replace(winner, strategy="bm25"),
        replace(winner, rerank=False),
        replace(winner, index="I3"),
        replace(winner, neighbors=False, policy="prefix"),
    ]
    e = g.stage("E", list({a.identity(): a for a in ablations}.values()))
    finalists = list(
        {
            a.identity(): a
            for a in [BASE, *sorted(eligible, key=lambda a: quality_order(a, all_data))[:2]]
        }.values()
    )
    repeats, timing = g.timed("repeat", finalists)
    timing_safe = []
    for arm in finalists:
        ident = arm.identity()
        safe = all(
            timing[ident][ds]["p95_ms"] <= 1.5 * timing[BASE.identity()][ds]["p95_ms"]
            for ds in ("official", "repository")
        )
        for rep in range(3):
            candidate = [r for r in repeats[ident] if r["rep"] == rep]
            reference = [r for r in repeats[BASE.identity()] if r["rep"] == rep]
            safe = safe and delivery_gate(candidate, reference)["eligible"]
        if safe:
            timing_safe.append(arm)
    winner = min(
        timing_safe,
        key=lambda a: (
            quality_order(a, all_data)[0],
            summary(all_data[a.identity()])["pairs"],
            max(timing[a.identity()][ds]["p95_ms"] for ds in ("official", "repository")),
            a.identity(),
        ),
    )
    ann, ann_timing = g.timed(
        "ann", list({a.identity(): a for a in [BASE, winner]}.values()), ann=True
    )
    ann_gates = []
    for rep in range(3):
        ann_gates.append(
            delivery_gate(
                [r for r in ann[winner.identity()] if r["rep"] == rep],
                [r for r in ann[BASE.identity()] if r["rep"] == rep],
            )
        )
    save(out / "ann-gates.json", {"quality": ann_gates, "timing": ann_timing, "adopt": False})
    contrasts = {}
    for ident, data in {**c, **d}.items():
        for ds in ("official", "repository"):
            old = [{**r, "delivered": r["delivery5"]} for r in baseline if r["dataset"] == ds]
            new = [{**r, "delivered": r["delivery5"]} for r in data if r["dataset"] == ds]
            contrasts[ident + ":" + ds] = paired_statistics(old, new)
    save(
        out / "statistics.json",
        {
            "contrasts": contrasts,
            "holm": holm({k: v["cluster_permutation_p"] for k, v in contrasts.items()}),
            "independent_confirmation": False,
        },
    )
    save(
        out / "decision.json",
        {
            "adopt": False,
            "quality_winner": asdict(winner),
            "reason": "Dev grid completed; independent review/confirmation required",
            "generation_calls": 0,
            "confirmation_questions_read": False,
            "ablation_configs": len(e),
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["freeze", "run"])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        (prepare if args.phase == "freeze" else run)(args.out)
    except Exception as exc:
        if args.out.exists():
            save(
                args.out / "stopped.json",
                {
                    "phase": args.phase,
                    "error": str(exc),
                    "adopt": False,
                    "generation_calls": 0,
                    "later_stages_allowed": False,
                },
            )
        record_operation("Grid v2阶段停止", "遵循冻结门槛", str(args.out), str(exc))
        raise
    finally:
        if args.out.exists():
            manifest = {
                str(f.relative_to(args.out)): digest(f)
                for f in args.out.rglob("*")
                if f.is_file() and f.name != "artifacts-manifest.json"
            }
            # Checkpoints are append-only; each phase has its own manifest.
            path = args.out / f"{args.phase}-artifacts-manifest.json"
            if not path.exists():
                write_new(path, manifest)


if __name__ == "__main__":
    main()
