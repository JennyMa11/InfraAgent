"""Original RAG dev-only recall/delivery experiments; no generation or new Agent."""

import argparse
import copy
import json
import shutil
from dataclasses import replace
from functools import lru_cache
from pathlib import Path
from time import perf_counter

from benchmark_selection_v3 import read_rows, write_json
from operation_log import record_operation
from prepare_corpus_v2 import ROOT, configuration

from infra_rag.benchmarking import canonical_hash, digest, span_coverage
from infra_rag.encoding import BGEEncoder
from infra_rag.evaluation import evidence_metrics
from infra_rag.models import Chunk
from infra_rag.offline_evaluation import latency_summary
from infra_rag.original_rag_experiments import (
    ADJACENCY_VERSION,
    TECHNICAL_VERSION,
    TechnicalBM25,
    additive_pool,
    adjacency_map,
    adjacent_views,
    bounded_focused_queries,
    neighbor_bundle,
    pack_bundle,
)
from infra_rag.paired_statistics import holm, paired_statistics
from infra_rag.recall_experiments import score_bundle
from infra_rag.service import RetrievalService

V4 = ROOT / "evals/merged-corpus-v2/recall-delivery-v4/run-20261002"
V6 = ROOT / "evals/merged-corpus-v2/budget-ablation-v6/run-20261003"
V3 = ROOT / "evals/merged-corpus-v2/evidence-selection-v3/run-20261002"
PLAN = ROOT / "evals/merged-corpus-v2/original-rag-v7/experiment-plan.md"
ARMS = ("B", "D60", "D90", "T", "L", "E", "Ladj", "Eadj", "Q", "Qdepth")
REPLAYS = {"R-B": "B5", "R-D": "D5", "R-Q": "Q5", "R-L": "L5", "R-E": "E5"}
DATASETS = ("official", "repository")


def freeze(run, name, value):
    path = run / name
    encoded = json.loads(json.dumps(value))
    if path.exists():
        if json.loads(path.read_text()) != encoded:
            raise ValueError(f"Frozen {name} differs; use a new run directory")
    else:
        write_json(path, encoded)


def prepare(run, reuse=None):
    inputs = {}

    def verified(folder, name):
        manifest = json.loads((folder / "artifacts-manifest.json").read_text())["files"]
        path = folder / name
        if digest(path) != manifest[name]:
            raise ValueError(f"Frozen input changed: {path}")
        inputs[str(path.relative_to(ROOT))] = digest(path)
        return path

    for folder, names in (
        (V4, ("protocol.json", "rows.jsonl", "source-audit.json", "context-index.json")),
        (V6, ("protocol.json", "rows.jsonl")),
    ):
        for name in names:
            verified(folder, name)
    prior = json.loads((V4 / "protocol.json").read_text())
    corpus = ROOT / prior["directory"] / "chunks.json"
    if digest(corpus) != json.loads((V6 / "protocol.json").read_text())["chunks_sha256"]:
        raise ValueError("Corpus changed")
    inputs[str(corpus.relative_to(ROOT))] = digest(corpus)
    chunks = {r["id"]: Chunk(**r) for r in json.loads(corpus.read_text())}
    mapping = {(r["dataset"], r["id"]): r for r in read_rows(V4 / "rows.jsonl") if r["arm"] == "B5"}
    if len(mapping) != 110:
        raise ValueError("Expected 110 frozen dev questions")
    bundles, facets = {}, {}
    for ds, qid in mapping:
        path = verified(V4, f"bundles/{ds}/{qid}.json")
        bundles[ds, qid] = json.loads(path.read_text())
        facet = V3 / "facets" / ds / (qid + ".json")
        if digest(facet) != prior["facets_sha256"][str(facet.relative_to(V3))]:
            raise ValueError("Frozen facets changed")
        inputs[str(facet.relative_to(ROOT))] = digest(facet)
        facets[ds, qid] = json.loads(facet.read_text())["facets"]
    for ds, name in (
        ("official", "infra-official-v1-reviewed"),
        ("repository", "repository-benchmark"),
    ):
        path = ROOT / "evals" / name / "dev.json"
        if digest(path) != prior["dev_hashes"][ds]:
            raise ValueError("Dev questions changed")
        inputs[str(path.relative_to(ROOT))] = digest(path)
    audit = json.loads((V4 / "source-audit.json").read_text())
    for source in audit["source_files"]:
        if digest(source["source"]) != source["expected"]:
            raise ValueError("Source changed")
    for kind in ("embedding", "reranker"):
        model = prior["models"][kind]
        for name, expected in model["files"].items():
            if digest(Path(model["path"]) / name) != expected:
                raise ValueError("Frozen model changed")
    implementation = {
        str(p.relative_to(ROOT)): digest(p)
        for p in [
            *sorted((ROOT / "src/infra_rag").glob("*.py")),
            Path(__file__),
            ROOT / "scripts/benchmark_selection_v3.py",
            ROOT / "scripts/prepare_corpus_v2.py",
            ROOT / "scripts/operation_log.py",
        ]
    }
    if reuse is not None:
        reuse_manifest = reuse / "aborted-artifacts-manifest.json"
        manifest = json.loads(reuse_manifest.read_text())["files"]
        for name, expected in manifest.items():
            if digest(reuse / name) != expected:
                raise ValueError("Reuse input changed: " + name)
        inputs[str(reuse_manifest.relative_to(ROOT))] = digest(reuse_manifest)
    protocol = {
        "kind": "original_rag_v7_dev_only",
        "scope": "adopted AnswerService/RetrievalService; offline experimental controls",
        "arms": list(ARMS),
        "replay_arms": REPLAYS,
        "plan_sha256": digest(PLAN),
        "inputs": inputs,
        "models": prior["models"],
        "directory": prior["directory"],
        "implementation": implementation,
        "candidate_cap": 90,
        "supplement_cap": 30,
        "context_tokens": 1200,
        "context_chars": 4000,
        "depths": [30, 60, 90],
        "technical_version": TECHNICAL_VERSION,
        "adjacency_version": ADJACENCY_VERSION,
        "seed": 42,
        "bootstrap_samples": 10000,
        "latency_repetitions": 1,
        "latency_p95_ratio_cap": 1.5,
        "dev_delivery_net_gain_min": 2,
        "generation_api_calls": 0,
        "default_changed": False,
        "confirmation_questions_read": False,
        "label_version": "original_frozen_v1",
        "independent_review": "pending",
        "reuse_run": str(reuse) if reuse else None,
        "source_hashes_verified": len(audit["source_files"]),
        "comparison_family": list(ARMS[1:]) + ["COMBO", "NEIGHBOR"],
    }
    run.mkdir(parents=True, exist_ok=True)
    freeze(run, "protocol.json", protocol)
    if not (run / "implementation").exists():
        for name in implementation:
            destination = run / "implementation" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((ROOT / name).read_bytes())
        (run / "experiment-plan.md").write_bytes(PLAN.read_bytes())
    model = prior["models"]["embedding"]
    from transformers import AutoTokenizer

    options = json.loads((Path(model["path"]) / "sentence_bert_config.json").read_text())
    tokenizer = AutoTokenizer.from_pretrained(
        model["path"], local_files_only=True, do_lower_case=options["do_lower_case"]
    )

    @lru_cache(maxsize=32768)
    def count(text):
        return len(tokenizer.encode(text, add_special_tokens=False))

    return protocol, mapping, bundles, facets, chunks, count


def evaluation(row, arm, bundle, chunks, count, *, frontier=None):
    scoring = row["query"] + "\n" + bundle["scoring_query"]
    chosen, context, trace = pack_bundle(bundle, chunks, scoring, count, frontier_ids=frontier)
    positions = {cid: i for i, cid in enumerate(chunks)}
    for evidence in context["evidence"]:
        evidence["source_position"] = positions[evidence["chunk_id"]]
    ids = [h["chunk_id"] for h in bundle["hits"]]
    gold = row.get("resolved_gold")
    metric = evidence_metrics(ids, gold, max(1, len(ids))) if row["answerable"] else None
    output = {
        k: copy.deepcopy(row[k])
        for k in (
            "id",
            "dataset",
            "query",
            "group_id",
            "answerable",
            "resolved_gold",
            "required_points",
        )
        if k in row
    }
    output.update(
        arm=arm,
        candidate_ids=ids,
        candidate_count=len(ids),
        candidate_complete=metric["complete_evidence_hit"] if metric else None,
        candidate_coverage=metric["evidence_coverage"] if metric else None,
        top5_complete=(evidence_metrics(ids, gold, 5)["complete_evidence_hit"] if metric else None),
        selected_ids=[h.chunk.id for h in chosen],
        context=context,
        packing_trace=trace,
        delivered=span_coverage(
            context["evidence"],
            {**row, "evidence_alternatives": gold["evidence_alternatives"] if metric else []},
        ),
        bundle_sha256=canonical_hash(bundle),
        scoring_query=bundle["scoring_query"],
        ranked_hits=bundle["hits"],
        recall_traces=bundle.get("recall_traces", []),
        focus_fallback=bundle.get("focus_fallback"),
    )
    wire = "\n\n".join(
        f"[{e['citation_id']}] 来源：{e['locator']}\n{e['content']}" for e in context["evidence"]
    )
    output["answer_service_evidence_serialization"] = {
        "text": wire,
        "tokens": count(wire),
        "characters": len(wire),
        "includes_metadata": False,
        "overhead_tokens_vs_packer": count(wire) - context["used_tokens"],
        "not_full_prompt_or_generation_usage": True,
    }
    return output


def append(run, row):
    with (run / "rows.jsonl").open("a") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def replay(run, mapping, bundles, chunks, count):
    done = {(r["dataset"], r["id"], r["arm"]) for r in read_rows(run / "rows.jsonl")}
    reference = {
        (r["dataset"], r["id"]): r
        for r in read_rows(V6 / "rows.jsonl")
        if r["arm"] == "B-k8-l0-p1-n0"
    }
    for key, row in mapping.items():
        for arm, old in REPLAYS.items():
            if (*key, arm) in done:
                continue
            started = perf_counter()
            output = evaluation(row, arm, bundles[key][old], chunks, count)
            output["component_replay_ms"] = (perf_counter() - started) * 1000
            if arm == "R-B" and output["context"] != reference[key]["context"]:
                raise ValueError("v6 baseline evidence replay differs")
            append(run, output)
    print("frozen replay complete", flush=True)


class Engine:
    def __init__(self, run, protocol, chunks):
        self.run, self.protocol, self.chunks = run, protocol, chunks
        self.services = {}
        self.encoder = self.reranker = self.technical = None
        self.model = protocol["models"]["reranker"]
        old_manifest = json.loads((V4 / "artifacts-manifest.json").read_text())["files"]
        self.scores = {}
        old_scores = V4 / "rerank-scores.json"
        if digest(old_scores) != old_manifest["rerank-scores.json"]:
            raise ValueError("Old score cache changed")
        self.scores.update(json.loads(old_scores.read_text()))
        self.reuse = Path(protocol["reuse_run"]) if protocol.get("reuse_run") else None
        if self.reuse:
            old_protocol = json.loads((self.reuse / "protocol.json").read_text())
            if old_protocol["models"] != protocol["models"]:
                raise ValueError("Reuse model identity differs")
            if old_protocol["directory"] != protocol["directory"]:
                raise ValueError("Reuse corpus differs")
            for name in (
                "encoding",
                "lexical",
                "service",
                "recall_experiments",
                "original_rag_experiments",
            ):
                path = f"src/infra_rag/{name}.py"
                if old_protocol["implementation"][path] != protocol["implementation"][path]:
                    raise ValueError("Reuse retrieval implementation differs")
            self.scores.update(json.loads((self.reuse / "rerank-scores.json").read_text()))
        self.score_path = run / "rerank-scores.json"
        if self.score_path.exists():
            self.scores.update(json.loads(self.score_path.read_text()))
        self.historical_recalls = []
        for path in sorted((V4 / "recall-cache").glob("*.json")):
            if digest(path) != old_manifest[str(path.relative_to(V4))]:
                raise ValueError("Frozen recall cache changed")
            self.historical_recalls.append(json.loads(path.read_text()))
        if self.reuse:
            self.historical_recalls.extend(
                json.loads(p.read_text())
                for p in sorted((self.reuse / "recall-cache").glob("*.json"))
            )
        self.new_pairs, self.score_hits, self.score_lookups = 0, 0, 0
        self.new_recalls, self.recall_hits, self.recall_lookups = 0, 0, 0
        self.score_inputs = []

    def models(self):
        if self.encoder is None:
            from sentence_transformers import CrossEncoder, SentenceTransformer

            model = self.protocol["models"]["embedding"]
            self.encoder = BGEEncoder.__new__(BGEEncoder)
            self.encoder.model = SentenceTransformer(model["path"], local_files_only=True)
            self.encoder.instruction = "为这个句子生成表示以用于检索相关文章："
            self.reranker = CrossEncoder(self.model["path"], local_files_only=True)

    def service(self, kind):
        if kind in self.services:
            return self.services[kind]
        self.models()
        directory = (
            ROOT
            / "data/original-rag-v7"
            / canonical_hash([self.protocol["inputs"], self.protocol["implementation"], kind])[:16]
            / kind
        )
        if kind in {"base", "context"}:
            if kind == "base":
                source = ROOT / self.protocol["directory"] / "index"
                settings = configuration(directory)
            else:
                prior = json.loads((V4 / "context-index.json").read_text())
                source = ROOT / prior["directory"]
                settings = replace(
                    configuration(directory),
                    preprocessing_version=prior["fingerprint"]["preprocessing_version"],
                )
                if digest(source / "index.json") != prior["index_sha256"]:
                    raise ValueError("Historical context index changed")
            # Work on an isolated copy; never rebuild or write the historical indexes.
            if not directory.exists():
                directory.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(source, directory)
            if digest(source / "index.json") != digest(directory / "index.json"):
                raise ValueError("Copied index differs")
            service = RetrievalService(settings)
        else:
            views, records = adjacent_views(list(self.chunks.values()))
            identity = canonical_hash(records)
            settings = replace(
                configuration(directory),
                preprocessing_version=configuration(directory).preprocessing_version
                + ":"
                + identity,
            )
            if self.reuse and not directory.exists():
                record = json.loads((self.reuse / "index-adjacent.json").read_text())
                source = Path(record["directory"])
                if digest(source / "index.json") != record["index_sha256"]:
                    raise ValueError("Reuse adjacency index changed")
                if record["fingerprint"] != settings.fingerprint():
                    raise ValueError("Reuse adjacency fingerprint differs")
                directory.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(source, directory)
            service = RetrievalService(settings)
            service.encoder = self.encoder
            if not service.chunks:
                print("encoding adjacency views", len(views), flush=True)
                service._commit(views, {})
            if [(c.id, c.content) for c in service.chunks] != [(c.id, c.content) for c in views]:
                raise ValueError("Adjacency index contents differ")
            freeze(self.run, "adjacency-views.json", records)
        service.settings = replace(service.settings, rerank=False)
        service.encoder, service.reranker = self.encoder, self.reranker
        self.services[kind] = service
        freeze(
            self.run,
            f"index-{kind}.json",
            {
                "directory": str(directory),
                "fingerprint": settings.fingerprint(),
                "index_sha256": digest(directory / "index.json"),
            },
        )
        return service

    def recall(self, query, kind, k, *, cached=True):
        self.recall_lookups += int(cached)
        key = canonical_hash([self.protocol["implementation"], query, kind, k])
        path = self.run / "recall-cache" / (key + ".json")
        if cached and path.exists():
            self.recall_hits += 1
            return json.loads(path.read_text())
        if cached:
            candidates = [
                r
                for r in self.historical_recalls
                if r["query"] == query
                and r["candidate_k"] >= k
                and (
                    r.get("kind") == kind
                    or (
                        "index" in r
                        and kind in {"base", "context"}
                        and (("merged-corpus-v4" in r["index"]) == (kind == "context"))
                    )
                )
            ]
            if candidates:
                r = copy.deepcopy(min(candidates, key=lambda r: r["candidate_k"]))
                for channel in r["channels"].values():
                    channel["ranking"] = channel["ranking"][:k]
                r.update(candidate_k=k, cache_origin="verified_v4", latency_ms=None)
                self.recall_hits += 1
                write_json(path, r)
                return r
        service = self.service(kind)
        service.settings = replace(service.settings, candidate_k=k)
        diagnostics = {}
        started = perf_counter()
        service.search(query, top_k=10, domain="infra", modality="text", diagnostics=diagnostics)
        r = {
            "query": query,
            "candidate_k": k,
            "channels": diagnostics["channels"],
            "latency_ms": (perf_counter() - started) * 1000,
            "kind": kind,
        }
        self.new_recalls += 1
        if cached:
            write_json(path, r)
        return r

    def infer(self, pairs):
        self.models()
        diagnostics = self.service("base")._rerank_diagnostics(pairs)
        started = perf_counter()
        values = self.reranker.predict(pairs, show_progress_bar=False)
        self.new_pairs += len(pairs)
        self.score_inputs.append(
            {
                "pairs": pairs,
                "diagnostics": diagnostics,
                "latency_ms": (perf_counter() - started) * 1000,
            }
        )
        return values

    def score(self, pool, query, seeds, *, cached=True):
        self.score_lookups += len(pool) if cached else 0
        if cached:
            seeded = {h["chunk_id"] for h in seeds}
            self.score_hits += sum(
                cid in seeded
                or canonical_hash([self.model, query, self.chunks[cid].content]) in self.scores
                for cid, _ in pool
            )
        return score_bundle(
            pool,
            query,
            self.chunks,
            self.model,
            self.infer,
            self.scores if cached else {},
            seeds if cached else (),
        )

    def bundle(
        self, arm, base, row, facets, *, cached=True, score_candidates=True, base_live=False
    ):
        query = base["scoring_query"]
        # For warm measurements, the baseline retrieval itself must actually execute.
        if not cached and not base_live:
            rec = self.recall(query, "base", 30, cached=False)
            from infra_rag.recall_experiments import rank_fusion

            ids = rank_fusion([c["ranking"] for c in rec["channels"].values()])
            base = {
                "scoring_query": query,
                "hits": [{"chunk_id": cid, "score": value} for cid, value in ids],
            }
        if arm == "B":
            return (
                base
                if cached or not score_candidates
                else self.score(
                    [(h["chunk_id"], h["score"]) for h in base["hits"]], query, [], cached=False
                )
            )
        focus, fallback = bounded_focused_queries(row["query"], query, facets)
        if arm in {"D60", "D90", "Qdepth"}:
            depth = int(arm[1:]) if arm.startswith("D") else 30 * (1 + len(focus))
            traces = [self.recall(query, "base", depth, cached=cached)]
            channels = [c["ranking"] for c in traces[0]["channels"].values()]
        elif arm == "Q":
            traces = [self.recall(q, "base", 30, cached=cached) for q in focus]
            channels = [c["ranking"] for r in traces for c in r["channels"].values()]
        elif arm == "T":
            if self.technical is None:
                self.technical = TechnicalBM25(list(self.chunks.values()))
            ranking = [
                {"chunk_id": cid, "score": score, "rank": i}
                for i, (cid, score) in enumerate(self.technical.search(query, 30), 1)
            ]
            traces = [
                {
                    "kind": "technical_bm25",
                    "identity": self.technical.identity,
                    "query": query,
                    "channels": {"bm25": {"ranking": ranking}},
                }
            ]
            channels = [ranking]
        else:
            kind = "adjacent" if arm.endswith("adj") else "context"
            channel = "bm25" if arm.startswith("L") else "dense"
            rec = self.recall(query, kind, 30, cached=cached)
            # Both components run in the shared service; count the actual work in latency.
            traces, channels = [rec], [rec["channels"][channel]["ranking"]]
        pool = additive_pool(base["hits"], channels)
        scored = (
            self.score(pool, query, base["hits"], cached=cached)
            if score_candidates
            else {
                "scoring_query": query,
                "hits": [{"chunk_id": cid, "score": value} for cid, value in pool],
            }
        )
        scored.update(
            recall_traces=traces,
            focused_queries=focus if arm == "Q" else [],
            focus_fallback=fallback if arm == "Q" else None,
        )
        return scored

    def save(self):
        write_json(self.score_path, self.scores)
        with (self.run / "score-inputs.jsonl").open("a") as stream:
            for r in self.score_inputs:
                stream.write(json.dumps(r, ensure_ascii=False) + "\n")
        self.score_inputs.clear()
        with (self.run / "accounting.jsonl").open("a") as stream:
            stream.write(
                json.dumps(
                    {
                        "new_rerank_pairs": self.new_pairs,
                        "new_retrieval_calls": self.new_recalls,
                        "score_cache_hits": self.score_hits,
                        "score_cache_lookups": self.score_lookups,
                        "recall_cache_hits": self.recall_hits,
                        "recall_cache_lookups": self.recall_lookups,
                        "generation_api_calls": 0,
                    }
                )
                + "\n"
            )


def retrieval(run, engine, mapping, bundles, facets, chunks, count):
    done = {(r["dataset"], r["id"], r["arm"]) for r in read_rows(run / "rows.jsonl")}
    for i, (key, row) in enumerate(mapping.items(), 1):
        for arm in ARMS:
            if (*key, arm) in done:
                continue
            path = run / "bundles" / key[0] / key[1] / (arm + ".json")
            bundle = engine.bundle(arm, bundles[key]["B5"], row, facets[key])
            freeze(run, str(path.relative_to(run)), bundle)
            output = evaluation(row, arm, bundle, chunks, count)
            if arm == "B":
                baseline = next(
                    r
                    for r in read_rows(run / "rows.jsonl")
                    if (r["dataset"], r["id"], r["arm"]) == (*key, "R-B")
                )
                if output["context"] != baseline["context"]:
                    raise ValueError("Baseline changed")
            append(run, output)
        engine.save()
        print("retrieval", i, len(mapping), *key, flush=True)


def summaries(rows):
    result = {}
    for ds in DATASETS:
        for arm in sorted({r["arm"] for r in rows}):
            selected = [r for r in rows if r["dataset"] == ds and r["arm"] == arm]
            positive = [r for r in selected if r["answerable"]]
            result[f"{ds}:{arm}"] = {
                "n": len(positive),
                "runs": len(selected),
                "candidate_complete": sum(r["candidate_complete"] for r in positive),
                "top5_complete": sum(r["top5_complete"] for r in positive),
                "delivered_complete": sum(r["delivered"]["complete"] for r in positive),
                "mean_candidate_coverage": sum(r["candidate_coverage"] for r in positive)
                / len(positive)
                if positive
                else None,
                "candidate_max": max((r["candidate_count"] for r in selected), default=0),
                "negative_cases": len(selected) - len(positive),
                "negative_answer_quality": None,
            }
    return result


def rank_methods(summary, arms, *, include_candidate_only=False):
    eligible = []
    for arm in arms:
        if any(f"{ds}:{arm}" not in summary for ds in DATASETS):
            continue
        gains = [
            sum(summary[f"{ds}:{arm}"][m] - summary[f"{ds}:B"][m] for ds in DATASETS)
            for m in ("delivered_complete", "candidate_complete")
        ]
        no_loss = all(
            summary[f"{ds}:{arm}"][m] >= summary[f"{ds}:B"][m]
            for ds in DATASETS
            for m in ("delivered_complete", "candidate_complete")
        )
        if no_loss and (gains[0] > 0 or include_candidate_only and gains[1] > 0):
            eligible.append((arm, gains))
    return [a for a, _ in sorted(eligible, key=lambda v: (-v[1][0], -v[1][1], v[0]))]


def selection(run, engine, mapping, bundles, facets, chunks, count):
    rows = read_rows(run / "rows.jsonl")
    summary = summaries(rows)
    ranking = rank_methods(summary, ARMS[1:], include_candidate_only=True)
    if not any(
        sum(
            summary[f"{ds}:{arm}"]["delivered_complete"] - summary[f"{ds}:B"]["delivered_complete"]
            for ds in DATASETS
        )
        > 0
        for arm in ranking
    ):
        ranking = []

    # Avoid combining two variants of the same mechanism.
    def family(arm):
        return "depth" if arm in {"D60", "D90", "Qdepth"} else arm[0]

    combine = []
    for arm in ranking:
        if family(arm) not in {family(a) for a in combine}:
            combine.append(arm)
        if len(combine) == 2:
            break
    freeze(run, "combination-selection.json", {"methods": combine if len(combine) == 2 else []})
    done = {(r["dataset"], r["id"], r["arm"]) for r in rows}
    if len(combine) == 2:
        for key, row in mapping.items():
            if (*key, "COMBO") in done:
                continue
            channels = []
            for arm in combine:
                b = json.loads((run / "bundles" / key[0] / key[1] / (arm + ".json")).read_text())
                for rec in b["recall_traces"]:
                    for name, channel in rec["channels"].items():
                        if arm.startswith(("L", "E")) and name != (
                            "bm25" if arm.startswith("L") else "dense"
                        ):
                            continue
                        channels.append(channel["ranking"])
            base = bundles[key]["B5"]
            b = engine.score(
                additive_pool(base["hits"], channels), base["scoring_query"], base["hits"]
            )
            freeze(run, f"bundles/{key[0]}/{key[1]}/COMBO.json", b)
            append(run, evaluation(row, "COMBO", b, chunks, count))
        engine.save()
    summary = summaries(read_rows(run / "rows.jsonl"))
    ranking = rank_methods(summary, (*ARMS[1:], "COMBO"))
    source = ranking[0] if ranking else "B"
    freeze(run, "packing-selection.json", {"source_arm": source, "not_adoption": True})
    adjacent = adjacency_map(list(chunks.values()))
    indexed = {(r["dataset"], r["id"], r["arm"]): r for r in read_rows(run / "rows.jsonl")}
    for key, row in mapping.items():
        if (*key, "NEIGHBOR") in done:
            continue
        path = run / "bundles" / key[0] / key[1] / (source + ".json")
        b = json.loads(path.read_text())
        chosen, _, _ = pack_bundle(b, chunks, row["query"] + "\n" + b["scoring_query"], count)
        scored, added = neighbor_bundle(
            b, chosen, adjacent, chunks, engine.model, engine.infer, engine.scores
        )
        original_frontier = indexed[*key, source]["packing_trace"]["eligible_ids"]
        retained = {h["chunk_id"] for h in scored["hits"]}
        neighbor_frontier = sorted({cid for h in chosen for cid in adjacent[h.chunk.id]} & retained)
        output = evaluation(
            row, "NEIGHBOR", scored, chunks, count, frontier=original_frontier + neighbor_frontier
        )
        output.update(
            packing_source_arm=source,
            added_neighbor_ids=added,
            scored_neighbor_frontier_ids=neighbor_frontier,
        )
        freeze(run, f"bundles/{key[0]}/{key[1]}/NEIGHBOR.json", scored)
        append(run, output)
    engine.save()
    print("combination and neighbor selection complete", source, combine, flush=True)


def latency(run, engine, mapping, bundles, facets, chunks, count):
    summary = summaries(read_rows(run / "rows.jsonl"))
    ranked = rank_methods(summary, (*ARMS[1:], "COMBO", "NEIGHBOR"))
    # Time the best quality method before applying the latency adoption gate.
    winner = ranked[0] if ranked else "B"
    combine = json.loads((run / "combination-selection.json").read_text())["methods"]
    neighbor_source = json.loads((run / "packing-selection.json").read_text())["source_arm"]

    def execute(arm, row, base, fs):
        if arm == "NEIGHBOR":
            b = execute(neighbor_source, row, base, fs)
            chosen, _, trace = pack_bundle(
                b, chunks, row["query"] + "\n" + b["scoring_query"], count
            )
            adjacent = adjacency_map(list(chunks.values()))
            b, added = neighbor_bundle(
                b,
                chosen,
                adjacent,
                chunks,
                engine.model,
                engine.infer,
                {},
            )
            retained = {h["chunk_id"] for h in b["hits"]}
            neighbor_frontier = sorted(
                {cid for h in chosen for cid in adjacent[h.chunk.id]} & retained
            )
            pack_bundle(
                b,
                chunks,
                row["query"] + "\n" + b["scoring_query"],
                count,
                frontier_ids=trace["eligible_ids"] + neighbor_frontier,
            )
            return b
        if arm == "COMBO":
            channels = []
            raw_base = engine.bundle("B", base, row, fs, cached=False, score_candidates=False)
            # Retrieve both supplement channels, then rerank the final union exactly once.
            for method in combine:
                b = engine.bundle(
                    method, raw_base, row, fs, cached=False, score_candidates=False, base_live=True
                )
                for rec in b["recall_traces"]:
                    for name, c in rec["channels"].items():
                        if method.startswith(("L", "E")) and name != (
                            "bm25" if method.startswith("L") else "dense"
                        ):
                            continue
                        channels.append(c["ranking"])
            b = engine.score(
                additive_pool(raw_base["hits"], channels), base["scoring_query"], [], cached=False
            )
        else:
            b = engine.bundle(arm, base, row, fs, cached=False)
        pack_bundle(b, chunks, row["query"] + "\n" + b["scoring_query"], count)
        return b

    # Warm model, lexical statistics, collections, and packing caches outside timing.
    first = next(iter(mapping))
    for arm in dict.fromkeys(("B", winner)):
        execute(arm, mapping[first], bundles[first]["B5"], facets[first])
    records = read_rows(run / "latency.jsonl")
    done = {(r["dataset"], r["id"], r["arm"]) for r in records}
    for i, (key, row) in enumerate(mapping.items()):
        order = ("B", winner) if i % 2 == 0 else (winner, "B")
        for arm in dict.fromkeys(order):
            if (*key, arm) in done:
                continue
            started = perf_counter()
            before_pairs = engine.new_pairs
            b = execute(arm, row, bundles[key]["B5"], facets[key])
            actual_pairs = engine.new_pairs - before_pairs
            if actual_pairs > 90:
                raise ValueError("Warm measurement exceeded 90 cumulative rerank pairs")
            record = {
                "dataset": key[0],
                "id": key[1],
                "arm": arm,
                "latency_ms": (perf_counter() - started) * 1000,
                "candidate_count": len(b["hits"]),
                "rerank_pairs": actual_pairs,
                "warm": True,
                "score_cache_enabled": False,
                "recall_cache_enabled": False,
            }
            with (run / "latency.jsonl").open("a") as stream:
                stream.write(json.dumps(record) + "\n")
        if i % 10 == 0:
            print("warm latency", i + 1, len(mapping), winner, flush=True)
    engine.save()


def report(run):
    rows = read_rows(run / "rows.jsonl")
    summary = summaries(rows)
    stats, p = {}, {}
    for ds in DATASETS:
        base = [r for r in rows if r["dataset"] == ds and r["arm"] == "B"]
        if not base:
            base = [r for r in rows if r["dataset"] == ds and r["arm"] == "R-B"]
        for arm in sorted({r["arm"] for r in rows} - {"B", "R-B"}):
            after = [r for r in rows if r["dataset"] == ds and r["arm"] == arm]
            if len(after) != len(base):
                continue
            stats[f"{ds}:{arm}"] = paired_statistics(base, after)
            if not arm.startswith("R-"):
                p[f"{ds}:{arm}"] = stats[f"{ds}:{arm}"]["cluster_permutation_p"]
    for key, value in holm(p).items():
        stats[key]["holm_p"] = value
    timing = read_rows(run / "latency.jsonl")
    timings = {
        arm: {
            "n": len([r for r in timing if r["arm"] == arm]),
            **latency_summary([r["latency_ms"] for r in timing if r["arm"] == arm]),
        }
        for arm in {r["arm"] for r in timing}
    }
    winner = None
    if "official:B" in summary:
        for arm in rank_methods(summary, (*ARMS[1:], "COMBO", "NEIGHBOR")):
            gain = sum(
                summary[f"{ds}:{arm}"]["delivered_complete"]
                - summary[f"{ds}:B"]["delivered_complete"]
                for ds in DATASETS
            )
            if (
                gain >= 2
                and arm in timings
                and timings[arm]["n"] == 110
                and (timings[arm]["p95_ms"] <= 1.5 * timings["B"]["p95_ms"])
            ):
                winner = arm
                break
    write_json(
        run / "summary.json", {"results": summary, "statistics": stats, "warm_latency": timings}
    )
    write_json(
        run / "decision.json",
        {
            "dev_winner": winner,
            "default_changed": False,
            "independent_review": "pending",
            "confirmation_allowed": False,
            "generation_api_calls": 0,
            "confirmation_questions_read": False,
        },
    )
    write_json(
        run / "confirmation-status.json",
        {"status": "not_run_independent_review_pending", "no_confirmation_questions_read": True},
    )
    lines = [
        "# 原有 RAG v7 实验结果",
        "",
        "开发集检索与正文交付；不是答案正确率。默认服务未改变，未运行新增 Agent。",
        "",
        "| 配置 | 官方候选 /54 | 官方交付 /54 | 仓库候选 /50 | 仓库交付 /50 |",
        "|---|---:|---:|---:|---:|",
    ]
    for arm in sorted({r["arm"] for r in rows}):
        a, b = summary[f"official:{arm}"], summary[f"repository:{arm}"]
        lines.append(
            f"| {arm} | {a['candidate_complete']:g} | {a['delivered_complete']:g} | "
            f"{b['candidate_complete']:g} | {b['delivered_complete']:g} |"
        )
    lines += [
        "",
        f"满足开发集质量及已测延迟门槛的配置：{winner or '无'}。",
        "",
        "每题最多90个候选；正文预算1200 token/4000字符；重排使用同一整问和原正文。",
        "",
        "独立替代证据审核待完成，原标签未修改；holdout/test未读取。开发集选择不能替代独立确认。",
        "",
        "R-*为历史候选组件回放。实际热启动耗时、正文与AnswerService来源头开销、逐题得失和聚类统计见summary.json及rows.jsonl。",
        "",
        "质量筛选与延迟测试分开，评分缓存回放耗时不作端到端耗时。只对质量最优配置执行完整延迟对照，未测配置不能判性能通过。",
    ]
    (run / "review-report.md").write_text("\n".join(lines) + "\n")
    return summary


def audit(run, mapping, chunks):
    cases = []
    for key, row in mapping.items():
        if row["id"] not in {"repo-016-2", "repo-018-1", "repo-032-2", "repo-035-1", "repo-035-2"}:
            continue
        cases.append(
            {
                "dataset": key[0],
                "id": key[1],
                "query": row["query"],
                "case_sha256": canonical_hash(row),
                "trace_sha256": canonical_hash(row["context"]),
                "required_points": row["required_points"],
                "gold": row["resolved_gold"],
                "actually_delivered": row["context"]["evidence"],
                "status": "pending",
                "reviewer": None,
                "reviewed_at": None,
                "accepted_alternatives": None,
                "rubric_scope_valid": None,
                "reason": None,
            }
        )
    freeze(
        run,
        "label-review-pending.json",
        {
            "independent_review_required": True,
            "label_changes": 0,
            "cases": cases,
            "corpus_chunks": len(chunks),
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--reuse-run",
        type=Path,
        help="Reuse verified exact-pair scores, recall and indexes from an aborted run",
    )
    parser.add_argument(
        "--phase",
        choices=("replay", "retrieval", "selection", "latency", "report", "all"),
        default="all",
    )
    args = parser.parse_args()
    run = args.output.resolve()
    reuse = args.reuse_run.resolve() if args.reuse_run else None
    protocol, mapping, bundles, facets, chunks, count = prepare(run, reuse)
    audit(run, mapping, chunks)
    if args.phase in {"replay", "all"}:
        replay(run, mapping, bundles, chunks, count)
    if args.phase in {"retrieval", "selection", "latency", "all"}:
        engine = Engine(run, protocol, chunks)
        if args.phase in {"retrieval", "all"}:
            retrieval(run, engine, mapping, bundles, facets, chunks, count)
        if args.phase in {"selection", "all"}:
            selection(run, engine, mapping, bundles, facets, chunks, count)
        if args.phase in {"latency", "all"}:
            latency(run, engine, mapping, bundles, facets, chunks, count)
    result = report(run)
    record_operation(
        "执行原有RAG v7实验阶段 " + args.phase,
        "实现召回与交付优化计划",
        json.dumps(result, ensure_ascii=False),
        "独立标签审核pending；不读holdout/test，不改默认服务，不判回答正确率",
    )
    write_json(
        run / "artifacts-manifest.json",
        {
            "files": {
                str(p.relative_to(run)): digest(p)
                for p in sorted(run.rglob("*"))
                if p.is_file() and p.name != "artifacts-manifest.json"
            }
        },
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
