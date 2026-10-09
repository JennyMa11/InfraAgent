"""Frozen dev experiments for delivery count, focused recall and contextual search views."""

import argparse
import copy
import json
from dataclasses import replace
from pathlib import Path
from time import perf_counter

from benchmark_corpus_v2 import repo_questions
from benchmark_selection_v3 import client, extract_one, load_models, read_rows, write_json
from operation_log import record_operation
from prepare_corpus_v2 import ROOT

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.context import pack_context
from infra_rag.evaluation import evidence_metrics
from infra_rag.models import Hit
from infra_rag.offline_evaluation import (
    answer_review_template,
    enrich_questions,
    evaluation_rows,
    generate_answer,
    latency_summary,
    review_markdown,
    summarize,
)
from infra_rag.paired_statistics import holm, paired_statistics
from infra_rag.query_expansion import load_rewrites, translate_query
from infra_rag.recall_experiments import (
    CONTEXT_VERSION,
    DeliveryRetrieval,
    context_views,
    focused_queries,
    rank_fusion,
    score_bundle,
    supplement,
)
from infra_rag.service import RetrievalService

OLD = ROOT / "evals/merged-corpus-v2/evidence-selection-v3/run-20261002"
OUT = ROOT / "evals/merged-corpus-v2/recall-delivery-v4"
ARMS = ("B5", "B8", "D5", "Q5", "L5", "E5", "LE5")
PRIMARY = (("B5", "B8"), ("D5", "Q5"), ("B5", "L5"), ("B5", "E5"))


def setup(run):
    prior = json.loads((OLD / "protocol.json").read_text())
    old_rows = read_rows(OLD / "rows.jsonl")
    official = ROOT / "evals/infra-official-v1-reviewed"
    routing = json.loads(
        (ROOT / "evals/merged-corpus-v2/routing-v2-20261002/protocol.json").read_text()
    )
    assert digest(official / "dev.json") == routing["official_dev_sha256"]
    repository, repo = repo_questions()
    assert digest(repository / "dev.json") == routing["repo_dev_sha256"]
    dev = json.loads((official / "dev.json").read_text())
    rewrite_path = official / "results/dev-opt-english-query-20261001/query-rewrites.jsonl"
    assert digest(rewrite_path) == routing["rewrites_sha256"]
    translations = load_rewrites(
        official / "results/dev-opt-english-query-20261001/query-rewrites.jsonl", dev
    )
    datasets = {"official": (official, dev, translations), "repository": (repository, repo, {})}
    source_files = sorted((ROOT / "src/infra_rag").glob("*.py")) + [
        Path(__file__),
        ROOT / "scripts/benchmark_selection_v3.py",
        ROOT / "scripts/benchmark_corpus_v2.py",
        ROOT / "scripts/prepare_corpus_v2.py",
    ]
    protocol = {
        "kind": "recall_delivery_v4",
        "arms": ARMS,
        "plan_sha256": digest(OUT / "experiment-plan.md"),
        "prior_protocol_sha256": digest(OLD / "protocol.json"),
        "prior_rows_sha256": digest(OLD / "rows.jsonl"),
        "rewrites_sha256": digest(rewrite_path),
        "routing_rows_sha256": digest(
            ROOT / "evals/merged-corpus-v2/routing-v2-20261002/rows.jsonl"
        ),
        "directory": prior["directory"],
        "manifest_sha256": prior["manifest_sha256"],
        "models": prior["models"],
        "answer_model": client(650).configuration(),
        "dev_hashes": {ds: digest(d / "dev.json") for ds, (d, _, _) in datasets.items()},
        "facets_sha256": {
            str(p.relative_to(OLD)): digest(p) for p in sorted((OLD / "facets").glob("*/*.json"))
        },
        "generation_ids": prior["generation_ids"],
        "coverage_ids": prior["coverage_ids"],
        "candidate_k": 30,
        "new_candidate_limit": 30,
        "context_tokens": 1200,
        "context_chars": 4000,
        "primary_delivery_tests": PRIMARY,
        "seed": 42,
        "bootstrap_samples": 10000,
        "context_version": CONTEXT_VERSION,
        "default_changed": False,
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in source_files},
    }
    run.mkdir(parents=True, exist_ok=True)
    encoded = json.loads(json.dumps(protocol))
    path = run / "protocol.json"
    if path.exists():
        if json.loads(path.read_text()) != encoded:
            raise ValueError("Frozen implementation or inputs changed; use a new output")
    else:
        write_json(path, encoded)
        for name in protocol["implementation"]:
            destination = run / "implementation" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((ROOT / name).read_bytes())
    baseline = {(r["dataset"], r["query"]): r for r in old_rows if r["arm"] == "P0-T"}
    assert len(baseline) == 110
    assert len(dev) == 60 and len(repo) == 50
    return protocol, datasets, baseline


def build_views(run, base, protocol):
    started = perf_counter()
    views, records = context_views(base.chunks)
    identity = canonical_hash(
        [
            protocol["manifest_sha256"],
            records,
            protocol["models"]["embedding"],
            protocol["implementation"]["src/infra_rag/recall_experiments.py"],
        ]
    )
    directory = ROOT / "data/merged-corpus-v4" / identity[:16]
    settings = replace(
        base.settings,
        data_dir=directory,
        rerank=False,
        preprocessing_version=base.settings.preprocessing_version + ":" + identity,
    )
    service = RetrievalService(settings)
    service.encoder = base._encoder()
    existed = bool(service.chunks)
    if not existed:
        print("context index encoding", len(views), flush=True)
        service._commit(views, base.source_manifest)
    assert [c.id for c in service.chunks] == [c.id for c in views]
    assert all(
        c.content == expected.content for c, expected in zip(service.chunks, views, strict=True)
    )
    record = {
        "identity": identity,
        "directory": str(directory.relative_to(ROOT)),
        "fingerprint": service.settings.fingerprint(),
        "chunks": len(views),
        "index_sha256": digest(directory / "index.json"),
        "build_or_load_ms": (perf_counter() - started) * 1000,
        "loaded_existing": existed,
        "views_sha256": canonical_hash(records),
        "encoder_update": service.last_update,
        "corpus_only": True,
        "original_bodies_used_for_rerank_and_answers": True,
    }
    if not (run / "context-index.json").exists():
        write_json(run / "context-index.json", record)
        write_json(run / "context-views.json", records)
    else:
        saved = json.loads((run / "context-index.json").read_text())
        assert saved["identity"] == identity and saved["index_sha256"] == record["index_sha256"]
    return service


class Candidates:
    def __init__(self, run, base, contextual, baselines, cache=True):
        self.run, self.base, self.contextual, self.baselines = run, base, contextual, baselines
        self.cache = cache
        self.chunks = {c.id: c for c in base.chunks}
        protocol = json.loads((run / "protocol.json").read_text())
        self.model = protocol["models"]["reranker"]
        self.raw_baselines = (
            {
                (r["dataset"], r["query"]): r
                for r in read_rows(ROOT / "evals/merged-corpus-v2/routing-v2-20261002/rows.jsonl")
                if r["arm"] == "processed_global30"
            }
            if cache
            else {}
        )
        self.score_path = run / "rerank-scores.json"
        self.scores = (
            json.loads(self.score_path.read_text()) if cache and self.score_path.exists() else {}
        )
        self.pending = 0

    def recall(self, query, service, k):
        if self.cache:
            key = canonical_hash([query, str(service.settings.data_dir), k])
            path = self.run / "recall-cache" / (key + ".json")
            if path.exists():
                return json.loads(path.read_text())
        diagnostics = {}
        service.settings = replace(service.settings, rerank=False, candidate_k=k)
        started = perf_counter()
        service.search(query, top_k=10, domain="infra", modality="text", diagnostics=diagnostics)
        record = {
            "query": query,
            "candidate_k": k,
            "channels": diagnostics["channels"],
            "latency_ms": (perf_counter() - started) * 1000,
            "index": str(service.settings.data_dir),
        }
        if self.cache:
            write_json(path, record)
        return record

    def base_bundle(self, ds, query, scoring):
        if self.cache:
            row = self.baselines[ds, query]
            old_protocol = json.loads((OLD / "protocol.json").read_text())
            assert old_protocol["models"]["reranker"] == self.model
            raw = self.raw_baselines[ds, query]
            fusion = {h["chunk_id"]: h["rrf_score"] for h in raw["diagnostics"]["fusion"]}
            hits = [
                {
                    "chunk_id": h["chunk_id"],
                    "rerank_score": h["rerank_score"],
                    "score": fusion[h["chunk_id"]],
                }
                for h in row["diagnostics"]["final"]
            ]
            channels = raw["diagnostics"]["channels"]
            bundle = {"scoring_query": scoring, "hits": hits}
            bundle["sha256"] = canonical_hash(bundle)
            return bundle, channels
        rec = self.recall(scoring, self.base, 30)
        pool = rank_fusion([c["ranking"] for c in rec["channels"].values()])
        return self.score(pool, scoring, []), rec["channels"]

    def score(self, pool, query, seeds):
        def infer(pairs):
            self.pending += len(pairs)
            diagnostic = self.base._rerank_diagnostics(pairs)
            values = self.base.reranker.predict(pairs)
            if self.cache:
                path = self.run / "score-inputs" / (canonical_hash([query, pairs]) + ".json")
                write_json(path, {"pairs": len(pairs), "diagnostics": diagnostic})
            return values

        return score_bundle(pool, query, self.chunks, self.model, infer, self.scores, seeds)

    def bundles(self, ds, q, scoring, facets, wanted=ARMS):
        base, channels = self.base_bundle(ds, q["query"], scoring)
        focused = focused_queries(q["query"], facets)
        result = {arm: base for arm in wanted if arm in {"B5", "B8"}}
        for arm in wanted:
            if arm in {"B5", "B8"}:
                continue
            traces = []
            if arm == "D5":
                traces = [self.recall(scoring, self.base, 30 * (1 + len(focused)))]
                pool = supplement(
                    base["hits"], [c["ranking"] for c in traces[0]["channels"].values()]
                )
            elif arm == "Q5":
                traces = [self.recall(query, self.base, 30) for query in focused]
                pool = supplement(
                    base["hits"], [c["ranking"] for rec in traces for c in rec["channels"].values()]
                )
            else:
                traces = [self.recall(scoring, self.contextual, 30)]
                original, new = channels, traces[0]["channels"]
                bm25 = new["bm25"] if arm in {"L5", "LE5"} else original["bm25"]
                dense = new["dense"] if arm in {"E5", "LE5"} else original["dense"]
                pool = rank_fusion([bm25["ranking"], dense["ranking"]])
            scored = self.score(pool, scoring, base["hits"] if self.cache else [])
            result[arm] = {
                **scored,
                "focused_queries": focused,
                "recall_traces": traces,
                "mode": arm,
            }
            if arm in {"D5", "Q5"}:
                assert {h["chunk_id"] for h in base["hits"]} <= {
                    h["chunk_id"] for h in scored["hits"]
                }
                assert len(scored["hits"]) <= len(base["hits"]) + 30
        if self.cache:
            write_json(self.score_path, self.scores)
        return result


def retrieval(run, datasets, baseline, base, contextual):
    builder = Candidates(run, base, contextual, baseline)
    rows = read_rows(run / "rows.jsonl")
    done = {(r["dataset"], r["id"], r["arm"]) for r in rows}
    with (run / "rows.jsonl").open("a") as stream:
        for ds, (dataset, qs, translations) in datasets.items():
            for q in qs:
                path = run / "bundles" / ds / (q["id"] + ".json")
                if path.exists():
                    bundles = json.loads(path.read_text())
                else:
                    facets = json.loads((OLD / "facets" / ds / (q["id"] + ".json")).read_text())[
                        "facets"
                    ]
                    bundles = builder.bundles(
                        ds, q, translations.get(q["query"], q["query"]), facets
                    )
                    write_json(path, bundles)
                for arm in ARMS:
                    if (ds, q["id"], arm) in done:
                        continue
                    wrapper = DeliveryRetrieval(
                        base, {q["query"]: bundles[arm]}, 8 if arm == "B8" else 5
                    )
                    for row in evaluation_rows(wrapper, [q], dataset, variants=["hybrid_rerank"]):
                        row.update(
                            dataset=ds,
                            arm=arm,
                            review_key=f"{ds}:{q['id']}:{arm}",
                            delivery_k=wrapper.delivery_k,
                        )
                        if row["answerable"]:
                            row["at_k"]["8"] = evidence_metrics(
                                row["retrieved"], row["resolved_gold"], 8
                            )
                        if arm == "B5":
                            old = baseline[ds, q["query"]]
                            assert row["retrieved"] == old["retrieved"]
                            assert row["delivered"] == old["delivered"]
                            assert [
                                (e["chunk_id"], e["content"]) for e in row["context"]["evidence"]
                            ] == [(e["chunk_id"], e["content"]) for e in old["context"]["evidence"]]
                        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                        stream.flush()
                    print("retrieval", ds, q["id"], arm, flush=True)
    write_json(
        run / "scoring-accounting.json",
        {
            "exact_pair_cache_entries": len(builder.scores),
            "new_pairs_this_invocation": builder.pending,
        },
    )


def analyze(run):
    rows = read_rows(run / "rows.jsonl")
    assert len(rows) == 770 and len({r["review_key"] for r in rows}) == 770
    results, stats = {}, {}
    for ds in ("official", "repository"):
        grouped = {arm: [r for r in rows if r["dataset"] == ds and r["arm"] == arm] for arm in ARMS}
        for arm, selected in grouped.items():
            positive = [r for r in selected if r["answerable"]]
            k = "8" if arm == "B8" else "5"
            results[f"{ds}:{arm}"] = {
                "n": len(positive),
                "candidate_complete": sum(r["candidate_complete"] for r in positive),
                "delivered_complete": sum(r["delivered"]["complete"] for r in positive),
                "top5_complete": sum(r["at_k"]["5"]["complete_evidence_hit"] for r in positive),
                "top8_complete": sum(r["at_k"]["8"]["complete_evidence_hit"] for r in positive),
                "top10_complete": sum(r["at_k"]["10"]["complete_evidence_hit"] for r in positive),
                "packing_failure_ids": [
                    r["id"]
                    for r in positive
                    if r["at_k"][k]["complete_evidence_hit"] and not r["delivered"]["complete"]
                ],
                "neighbor_rescue_ids": [
                    r["id"]
                    for r in positive
                    if not r["candidate_complete"] and r["delivered"]["complete"]
                ],
                "success_ids": [r["id"] for r in positive if r["delivered"]["complete"]],
                "summary": summarize(selected)["hybrid_rerank"],
            }
        for left, right in set(PRIMARY) | {("B5", arm) for arm in ARMS if arm != "B5"}:
            key = f"{ds}:{right}_vs_{left}"
            stats[key] = paired_statistics(grouped[left], grouped[right])
            recall_left, recall_right = copy.deepcopy(grouped[left]), copy.deepcopy(grouped[right])
            for rr in (recall_left, recall_right):
                for r in rr:
                    r["delivered"] = (
                        {"complete": r["candidate_complete"]} if r["answerable"] else None
                    )
            stats[key]["candidate_complete_exploratory"] = paired_statistics(
                recall_left, recall_right
            )
    corrections = holm(
        {
            f"official:{right}_vs_{left}": stats[f"official:{right}_vs_{left}"][
                "cluster_permutation_p"
            ]
            for left, right in PRIMARY
        }
    )
    for key, value in stats.items():
        value["primary"] = key in corrections
        value["holm_p"] = corrections.get(key)
    eligible = [
        arm
        for arm in ARMS
        if arm != "B5"
        and results[f"official:{arm}"]["delivered_complete"] >= 44
        and results[f"repository:{arm}"]["delivered_complete"] >= 40
        and {"official-002-1", "official-004-4"} <= set(results[f"official:{arm}"]["success_ids"])
    ]
    order = ["B8", "D5", "L5", "E5", "LE5", "Q5"]
    eligible.sort(
        key=lambda arm: (
            -results[f"official:{arm}"]["delivered_complete"],
            -results[f"repository:{arm}"]["delivered_complete"],
            -results[f"official:{arm}"]["summary"]["at_k"]["5"]["ndcg"],
            1 if arm == "Q5" else 0,
            order.index(arm),
        )
    )
    decision = {
        "eligible": eligible,
        "winner": eligible[0] if eligible else None,
        "diagnostic_arm": eligible[0] if eligible else "Q5",
        "default_changed": False,
        "fact_review": "independent_human_pending",
    }
    write_json(run / "summary.json", results)
    write_json(run / "paired-statistics.json", stats)
    write_json(run / "decision.json", decision)
    lines = [
        "# 召回与交付v4开发实验",
        "",
        "AI编写、稀疏原始来源标签；指标不是回答正确率。",
        "",
        "| 组 | 官方候选 | 官方交付 | 仓库候选 | 仓库交付 |",
        "|---|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        o, r = results[f"official:{arm}"], results[f"repository:{arm}"]
        lines.append(
            f"| {arm} | {o['candidate_complete']:g}/54 | {o['delivered_complete']:g}/54 | "
            f"{r['candidate_complete']:g}/50 | {r['delivered_complete']:g}/50 |"
        )
    lines += [
        "",
        "B8交付Top8，其余Top5；预算全部1200 token/4000字符。",
        "",
        "| 交付主对照 | 差值 | 配对率差95% CI | 簇置换p | Holm p |",
        "|---|---:|---|---:|---:|",
    ]
    for left, right in PRIMARY:
        s = stats[f"official:{right}_vs_{left}"]
        ci = " 至 ".join(f"{v:.2%}" for v in s["delta_rate_ci95"])
        lines.append(
            f"| {right}-{left} | {s['delta_count']:+g} | {ci} | "
            f"{s['cluster_permutation_p']:.6f} | {s['holm_p']:.6f} |"
        )
    lines += [
        "",
        f"开发集候选：{decision['winner'] or '无'}；默认global30不变，事实审核待独立人工。",
        "候选完整的检验为探索性，逐题得失见paired-statistics.json。索引增强未改变原正文。",
    ]
    (run / "report.md").write_text("\n".join(lines) + "\n")
    return decision


def generation(run, datasets, protocol):
    decision = json.loads((run / "decision.json").read_text())
    rows, answers = read_rows(run / "rows.jsonl"), read_rows(run / "answers.jsonl")
    done = {r["review_key"] for r in answers}
    questions = {
        (ds, q["id"]): q for ds, (d, qs, _) in datasets.items() for q in enrich_questions(qs, d)
    }
    model = client(650)
    with (run / "answers.jsonl").open("a") as stream:
        for original in rows:
            ids = (
                protocol["generation_ids"]
                if original["dataset"] == "official"
                else protocol["coverage_ids"]
            )
            if (
                original["arm"] not in {"B5", decision["diagnostic_arm"]}
                or original["id"] not in ids
            ):
                continue
            if original["review_key"] in done:
                continue
            row = copy.deepcopy(original)
            row["generation"] = generate_answer(
                questions[row["dataset"], row["id"]],
                row["context"],
                replace(base_settings(), query_language="none"),
                model,
            )
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            stream.flush()
            answers.append(row)
            print("answer", row["review_key"], row["generation"]["error"], flush=True)
    assert len(answers) == 46
    write_json(run / "answer-review.json", answer_review_template(answers))
    (run / "answer-review.md").write_text(review_markdown(answers))


def base_settings():
    from infra_rag.config import Settings

    return Settings()


def latency(run, datasets, baseline, base, contextual, protocol):
    decision = json.loads((run / "decision.json").read_text())
    candidate = decision["diagnostic_arm"]
    records = read_rows(run / "latency.jsonl")
    done = {(r["dataset"], r["id"], r["arm"]) for r in records}
    base._encoder().encode(["cache"], query=True)
    base.reranker.predict([("cache", "cache")])
    with (run / "latency.jsonl").open("a") as stream:
        for ds, (_, qs, translations) in datasets.items():
            ids = protocol["generation_ids"] if ds == "official" else protocol["coverage_ids"]
            for i, q in enumerate(q for q in qs if q["id"] in ids):
                order = ["B5", candidate] if i % 2 == 0 else [candidate, "B5"]
                facets = json.loads((OLD / "facets" / ds / (q["id"] + ".json")).read_text())[
                    "facets"
                ]
                for arm in order:
                    if (ds, q["id"], arm) in done:
                        continue
                    builder = Candidates(run, base, contextual, baseline, cache=False)
                    started = perf_counter()
                    bundle = builder.bundles(
                        ds, q, translations.get(q["query"], q["query"]), facets, wanted=[arm]
                    )[arm]
                    chunks = builder.chunks
                    hits = [
                        Hit(chunks[h["chunk_id"]], h["score"], rerank_score=h["rerank_score"])
                        for h in bundle["hits"][: 8 if arm == "B8" else 5]
                    ]
                    pack_context(
                        hits,
                        base.parent_index,
                        base._encoder().token_length,
                        1200,
                        4000,
                        "infra",
                        "text",
                    )
                    record = {
                        "dataset": ds,
                        "id": q["id"],
                        "arm": arm,
                        "end_to_end_ms": (perf_counter() - started) * 1000,
                        "new_rerank_pairs": builder.pending,
                        "mode": (
                            "uncached_query_candidates_scores; frozen_translations_facets_shared"
                        ),
                    }
                    records.append(record)
                    stream.write(json.dumps(record) + "\n")
                    stream.flush()
                    print("latency", ds, q["id"], arm, round(record["end_to_end_ms"]), flush=True)
    write_json(
        run / "latency-summary.json",
        {
            arm: latency_summary([r["end_to_end_ms"] for r in records if r["arm"] == arm])
            for arm in ("B5", candidate)
        },
    )


def accounting(run):
    answers = read_rows(run / "answers.jsonl")
    usage = {}
    calls = [c for r in answers for c in r["generation"]["calls"]]
    for call in calls:
        for key, value in (call.get("provider_response", {}).get("usage") or {}).items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                usage[key] = usage.get(key, 0) + value
    write_json(
        run / "cost-accounting.json",
        {
            "generation_calls": len(calls),
            "supplier_usage": usage,
            "source": "supplier responses; monetary costs not measured",
            "facet_calls": 0,
            "scoring": json.loads((run / "scoring-accounting.json").read_text()),
        },
    )


def confirmation(run, base, contextual, protocol):
    decision = json.loads((run / "decision.json").read_text())
    winner = decision["winner"]
    if winner is None:
        write_json(
            run / "confirmation-status.json",
            {
                "status": "not_run_dev_gate_failed",
                "no_confirmation_questions_read": True,
                "default_changed": False,
            },
        )
        return
    screening = run / "answer-screening.json"
    if not screening.exists():
        raise ValueError("Freeze actual-context answer screening before confirmation")
    review = json.loads(screening.read_text())
    assert review["winner"] == winner
    if review["new_confirmed_errors"]:
        write_json(
            run / "confirmation-status.json",
            {
                "status": "not_run_new_confirmed_answer_errors",
                "winner": winner,
                "no_confirmation_questions_read": True,
                "default_changed": False,
            },
        )
        return
    directory = run / "confirmation"
    directory.mkdir(exist_ok=True)
    lock = {
        "winner": winner,
        "protocol_sha256": digest(run / "protocol.json"),
        "decision_sha256": digest(run / "decision.json"),
        "answer_screening_sha256": digest(screening),
        "quarantine": "original_corpus",
        "default_changed": False,
    }
    if (directory / "lock.json").exists():
        assert json.loads((directory / "lock.json").read_text()) == lock
    else:
        write_json(directory / "lock.json", lock)
    official = ROOT / "evals/infra-official-v1-reviewed"
    repository = ROOT / "evals/repository-benchmark"
    holdout = json.loads((official / "holdout.json").read_text())
    test = [
        {
            **q,
            "answerable": True,
            "evidence_alternatives": [{"spans": q["relevant_spans"]}],
            "answer_key": {"required_points": [q["expected_answer"]], "forbidden_claims": []},
        }
        for q in json.loads((repository / "test.json").read_text())
    ]
    assert len(holdout) == 60 and len(test) == 100
    rows = read_rows(directory / "rows.jsonl")
    done = {(r["dataset"], r["id"], r["arm"]) for r in rows}
    with (directory / "rows.jsonl").open("a") as stream:
        for ds, dataset, qs in [("official", official, holdout), ("repository", repository, test)]:
            for q in qs:
                if all((ds, q["id"], arm) in done for arm in ("B5", winner)):
                    continue
                path = directory / "bundles" / ds / (q["id"] + ".json")
                if path.exists():
                    bundles = json.loads(path.read_text())
                else:
                    scoring = q["query"]
                    if ds == "official":
                        translation = directory / "translations" / (q["id"] + ".json")
                        if translation.exists():
                            scoring = json.loads(translation.read_text())["english"]
                        else:
                            model = client(220)
                            scoring = translate_query(q["query"], model)
                            write_json(
                                translation,
                                {
                                    "original_query": q["query"],
                                    "english": scoring,
                                    "provider_response": model.last_call,
                                },
                            )
                    facets = [{"question": scoring, "anchor_quote": q["query"]}]
                    if winner in {"D5", "Q5"}:
                        facet_path = directory / "facets" / ds / (q["id"] + ".json")
                        if not facet_path.exists():
                            write_json(
                                facet_path,
                                extract_one(
                                    q["query"],
                                    scoring,
                                    "English" if ds == "official" else "Chinese",
                                ),
                            )
                        facets = json.loads(facet_path.read_text())["facets"]
                    builder = Candidates(run, base, contextual, {}, cache=False)
                    bundles = builder.bundles(ds, q, scoring, facets, wanted=["B5", winner])
                    write_json(path, bundles)
                for arm in ("B5", winner):
                    if (ds, q["id"], arm) in done:
                        continue
                    wrapper = DeliveryRetrieval(
                        base, {q["query"]: bundles[arm]}, 8 if arm == "B8" else 5
                    )
                    for row in evaluation_rows(wrapper, [q], dataset, variants=["hybrid_rerank"]):
                        row.update(
                            dataset=ds,
                            arm=arm,
                            delivery_k=wrapper.delivery_k,
                            review_key=f"{ds}:{q['id']}:{arm}",
                        )
                        rows.append(row)
                        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                        stream.flush()
                    print("confirmation", ds, q["id"], arm, flush=True)
    assert len(rows) == 320
    write_json(
        directory / "summary.json",
        {
            f"{ds}:{arm}": summarize([r for r in rows if r["dataset"] == ds and r["arm"] == arm])
            for ds in ("official", "repository")
            for arm in ("B5", winner)
        },
    )
    write_json(
        directory / "paired-statistics.json",
        {
            ds: paired_statistics(
                [r for r in rows if r["dataset"] == ds and r["arm"] == "B5"],
                [r for r in rows if r["dataset"] == ds and r["arm"] == winner],
            )
            for ds in ("official", "repository")
        },
    )
    write_json(
        run / "confirmation-status.json",
        {
            "status": "completed_once_frozen",
            "winner": winner,
            "default_changed": False,
            "independent_human_fact_review": "pending",
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT / "run-20261002")
    parser.add_argument(
        "--phase",
        choices=[
            "all",
            "retrieval",
            "analyze",
            "generation",
            "latency",
            "accounting",
            "confirmation",
        ],
        default="all",
    )
    args = parser.parse_args()
    run = args.output.resolve()
    protocol, datasets, baseline = setup(run)
    base = contextual = None
    if args.phase in {"all", "retrieval", "latency", "confirmation"}:
        base, _ = load_models(ROOT / protocol["directory"], protocol)
        contextual = build_views(run, base, protocol)
    if args.phase in {"all", "retrieval"}:
        retrieval(run, datasets, baseline, base, contextual)
    if args.phase in {"all", "analyze"}:
        analyze(run)
    if args.phase in {"all", "generation"}:
        generation(run, datasets, protocol)
    if args.phase in {"all", "latency"}:
        latency(run, datasets, baseline, base, contextual, protocol)
    if args.phase in {"all", "accounting"}:
        accounting(run)
    if args.phase == "confirmation":
        confirmation(run, base, contextual, protocol)
    if args.phase == "all":
        decision = json.loads((run / "decision.json").read_text())
        write_json(
            run / "confirmation-status.json",
            {
                "status": "awaiting_frozen_answer_screening"
                if decision["winner"]
                else "not_run_dev_gate_failed",
                "winner": decision["winner"],
                "no_confirmation_questions_read": True,
                "default_changed": False,
            },
        )
        record_operation(
            "完成召回与交付v4开发实验",
            "验证Top8、子问题召回与上下文增强索引",
            f"770检索/46生成/46延迟；结果{run}；候选{decision['winner']}；默认不变",
            "AI来源标签稀疏；确认评测须通过门槛并冻结生成观察；事实独立人工pending",
        )


if __name__ == "__main__":
    main()
