"""Pre-registered frozen-candidate selection experiments; no holdout tuning."""

import argparse
import copy
import hashlib
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from pathlib import Path
from time import perf_counter

from benchmark_corpus_v2 import repo_questions
from operation_log import record_operation
from prepare_corpus_v2 import ROOT, build

from infra_rag.benchmarking import canonical_hash, digest, span_coverage
from infra_rag.context import pack_context, snippet
from infra_rag.evidence_selection import (
    FACET_PROMPT,
    FrozenSelectionRetrieval,
    parse_facets,
    select_order,
)
from infra_rag.model_clients import AnthropicClient
from infra_rag.models import Hit
from infra_rag.offline_evaluation import (
    answer_review_template,
    enrich_questions,
    evaluation_rows,
    generate_answer,
    oracle_context,
    review_markdown,
    summarize,
)
from infra_rag.paired_statistics import holm, paired_statistics
from infra_rag.partitioned import PartitionedRetrieval
from infra_rag.query_expansion import load_rewrites, translate_query

OLD = ROOT / "evals/merged-corpus-v2/routing-v2-20261002"
PLAN = ROOT / "evals/merged-corpus-v2/evidence-selection-v3/experiment-plan.md"
POOL_ARMS = {"P0": "processed_global30", "P1": "recall_en_rerank_en"}
EXTRA_IDS = [
    "official-012-2",
    "official-012-3",
    "official-010-4",
    "official-020-2",
    "official-028-4",
]


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    temporary.replace(path)


def client(max_tokens):
    old = json.loads((OLD / "generation-model.json").read_text())
    return AnthropicClient.from_environment(
        path=ROOT / ".env.llm",
        model=old["model"],
        base_url=old["base_url"],
        max_tokens=max_tokens,
    )


def prepare_run(run):
    run.mkdir(parents=True, exist_ok=True)
    old_protocol = json.loads((OLD / "protocol.json").read_text())
    directory = ROOT / old_protocol["directory"]
    manifest = json.loads((directory / "manifest.json").read_text())
    assert digest(directory / "manifest.json") == old_protocol["manifest_sha256"]
    assert digest(directory / "chunks.json") == manifest["chunks_sha256"]
    official_dir = ROOT / "evals/infra-official-v1-reviewed"
    # The old frozen run already validated corpus/source provenance. Do not call the general
    # validator here: it loads both dev and holdout questions, even in a dev-only experiment.
    official_manifest = json.loads((official_dir / "dataset-manifest.json").read_text())
    assert digest(official_dir / "dev.json") == official_manifest["splits"]["dev"]["sha256"]
    splits = {"dev": json.loads((official_dir / "dev.json").read_text())}
    repo_dir, repository = repo_questions()
    rewrite_path = official_dir / "results/dev-opt-english-query-20261001/query-rewrites.jsonl"
    rewrites = load_rewrites(rewrite_path, splits["dev"])
    datasets = {
        "official": (official_dir, splits["dev"], rewrites),
        "repository": (repo_dir, repository, {}),
    }
    old_rows = read_rows(OLD / "rows.jsonl")
    bundles, questions = {}, {}
    for ds, (dataset, qs, translations) in datasets.items():
        assert (
            digest(dataset / "dev.json")
            == old_protocol["official_dev_sha256" if ds == "official" else "repo_dev_sha256"]
        )
        assert len({q["query"] for q in qs}) == len(qs)
        for q in qs:
            questions[ds, q["query"]] = q
        for pool, arm in POOL_ARMS.items():
            mapped = {}
            for row in old_rows:
                if row["dataset"] != ds or row["arm"] != arm:
                    continue
                diag = row["diagnostics"]
                fusion = {h["chunk_id"]: h["rrf_score"] for h in diag.get("fusion", [])}
                for bank in diag.get("banks", {}).values():
                    fusion.update({h["chunk_id"]: h["rrf_score"] for h in bank.get("fusion", [])})
                hits = [
                    {
                        "chunk_id": h["chunk_id"],
                        "rerank_score": h["rerank_score"],
                        "score": fusion.get(h["chunk_id"], 0),
                    }
                    for h in diag["final"]
                ]
                assert set(h["chunk_id"] for h in hits) == set(diag["candidates"])
                # Never pass labels, answers or failure IDs into the selection wrapper.
                bundle = {
                    "hits": hits,
                    "scoring_query": translations.get(row["query"], row["query"]),
                }
                bundle["sha256"] = canonical_hash(bundle)
                mapped[row["query"]] = bundle
            assert len(mapped) == len(qs)
            bundles[ds, pool] = mapped
    source_files = sorted((ROOT / "src/infra_rag").glob("*.py")) + [
        Path(__file__),
        ROOT / "scripts/benchmark_corpus_v2.py",
        ROOT / "scripts/prepare_corpus_v2.py",
    ]
    protocol = {
        "kind": "dev_only_frozen_selection_v3",
        "plan_sha256": digest(PLAN),
        "old_rows_sha256": digest(OLD / "rows.jsonl"),
        "old_protocol_sha256": digest(OLD / "protocol.json"),
        "directory": str(directory.relative_to(ROOT)),
        "manifest_sha256": digest(directory / "manifest.json"),
        "bundle_hashes": {
            f"{ds}:{pool}": canonical_hash(mapping) for (ds, pool), mapping in bundles.items()
        },
        "models": json.loads((OLD / "models-verified.json").read_text()),
        "facet_model": client(1200).configuration(),
        "answer_model": client(650).configuration(),
        "facet_prompt_sha256": canonical_hash(FACET_PROMPT),
        "policies": ["T", "M", "F", "G"],
        "version_protection": False,
        "metadata_prefix": False,
        "mmr_lambda": 0.7,
        "context_tokens": 1200,
        "context_chars": 4000,
        "top_k": [5, 10],
        "generation_ids": sorted(set(old_protocol["generation_ids"] + EXTRA_IDS)),
        "coverage_ids": old_protocol["coverage_ids"],
        "primary_tests": ["official:P1:G_vs_F", "official:P0:G_vs_T"],
        "bootstrap_samples": 10000,
        "seed": 42,
        "default_changed": False,
        "setup_deviation": (
            "Initial aborted setup loaded official holdout through an integrity validator only; "
            "no holdout retrieval, inference, scoring or tuning. Dev-only loader now used. "
            "Original facet calls imported with unchanged hashes from setup-aborted-20261002."
        ),
        "notes": [
            "AI-authored sparse source judgments, not independent human fact labels",
            "Repository selection uses native Chinese; no language contrast",
            "Facets generated once per dev question; latency calls accounted separately",
            "P1 T disables legacy version preference; old 42/54 is historical reference only",
        ],
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in source_files},
    }
    path = run / "protocol.json"
    if path.exists():
        if json.loads(path.read_text()) != protocol:
            raise ValueError("Protocol changed; use a new output directory")
    else:
        write_json(path, protocol)
        for name in protocol["implementation"]:
            target = run / "implementation" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
    return directory, datasets, bundles, questions, protocol


def extract_one(original, scoring, language):
    model = client(1200)
    messages = [
        {"role": "system", "content": FACET_PROMPT},
        {
            "role": "user",
            "content": json.dumps(
                {"original_query": original, "scoring_query": scoring, "output_language": language},
                ensure_ascii=False,
            ),
        },
    ]
    started = perf_counter()
    try:
        raw = model.generate(messages)
        facets, error = parse_facets(raw, original, scoring)
    except Exception as exc:
        raw, error = "", type(exc).__name__
        facets = [{"question": scoring, "anchor_quote": original}]
    return {
        "original_query": original,
        "scoring_query": scoring,
        "language": language,
        "facets": facets,
        "fallback": error,
        "messages": messages,
        "raw": raw,
        "provider_response": model.last_call,
        "latency_ms": (perf_counter() - started) * 1000,
    }


def facets_phase(run, datasets):
    jobs = []
    for ds, (_, qs, rewrites) in datasets.items():
        for q in qs:
            path = run / "facets" / ds / f"{q['id']}.json"
            if not path.exists():
                jobs.append((ds, q, path, rewrites.get(q["query"], q["query"])))
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(
                extract_one, q["query"], scoring, "English" if ds == "official" else "Chinese"
            ): (ds, q, path)
            for ds, q, path, scoring in jobs
        }
        for future in as_completed(futures):
            ds, q, path = futures[future]
            record = future.result()
            record["sha256"] = canonical_hash(record)
            write_json(path, record)
            print("facets", ds, q["id"], len(record["facets"]), record["fallback"], flush=True)


def load_models(directory, protocol):
    from sentence_transformers import CrossEncoder

    for kind in ("embedding", "reranker"):
        record = protocol["models"][kind]
        assert (Path(record["path"]).parent.parent / "refs/main").read_text().strip() == Path(
            record["path"]
        ).name
        for name, expected in record["files"].items():
            with (Path(record["path"]) / name).open("rb") as stream:
                if hashlib.file_digest(stream, "sha256").hexdigest() != expected:
                    raise ValueError("Frozen model file changed")
    base, banks = build(directory)
    base.reranker = CrossEncoder(protocol["models"]["reranker"]["path"])
    return base, banks


class FeatureStore:
    def __init__(self, run, base, bundles, questions):
        self.run, self.base, self.bundles, self.questions = run, base, bundles, questions
        self.chunks = {c.id: c for c in base.chunks}
        self.loaded = {}

    def get(self, ds, query):
        key = (ds, query)
        if key in self.loaded:
            return self.loaded[key]
        q = self.questions[key]
        facet_path = self.run / "facets" / ds / f"{q['id']}.json"
        facet = json.loads(facet_path.read_text())
        assert facet["original_query"] == query
        ids = sorted(
            {h["chunk_id"] for pool in POOL_ARMS for h in self.bundles[ds, pool][query]["hits"]}
        )
        path = self.run / "features" / ds / f"{q['id']}.json"
        pairs = [(f["question"], self.chunks[cid].content) for f in facet["facets"] for cid in ids]
        identity = canonical_hash([digest(facet_path), pairs, self.base.settings.reranker_model])
        if path.exists():
            record = json.loads(path.read_text())
            assert record["input_sha256"] == identity
            payload = {k: v for k, v in record.items() if k != "sha256"}
            assert canonical_hash(payload) == record["sha256"]
        else:
            diagnostic = self.base._rerank_diagnostics(pairs)
            started = perf_counter()
            scores = [float(value) for value in self.base.reranker.predict(pairs)]
            n = len(ids)
            record = {
                "input_sha256": identity,
                "ids": ids,
                "facets": facet["facets"],
                "matrix": [scores[i * n : (i + 1) * n] for i in range(len(facet["facets"]))],
                "pairs": len(pairs),
                "input_diagnostics": diagnostic,
                "inference_latency_ms": (perf_counter() - started) * 1000,
            }
            record["sha256"] = canonical_hash(record)
            write_json(path, record)
            print("scores", ds, q["id"], len(pairs), flush=True)
        self.loaded[key] = record
        return record


def retrieval_phase(run, datasets, bundles, base, store):
    path = run / "rows.jsonl"
    rows = read_rows(path)
    done = {(r["dataset"], r["arm"], r["id"]) for r in rows}
    with path.open("a") as stream:
        for ds, (dataset, qs, _) in datasets.items():
            for pool in POOL_ARMS:
                for policy in ("T", "M", "F", "G"):
                    arm = f"{pool}-{policy}"
                    wrapper = FrozenSelectionRetrieval(
                        base, bundles[ds, pool], policy, lambda query, ds=ds: store.get(ds, query)
                    )
                    remaining = [q for q in qs if (ds, arm, q["id"]) not in done]
                    for row in evaluation_rows(
                        wrapper, remaining, dataset, variants=["hybrid_rerank"]
                    ):
                        row.update(dataset=ds, arm=arm, review_key=f"{ds}:{row['id']}:{arm}")
                        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                        stream.flush()
                        print("retrieval", ds, arm, row["id"], flush=True)


def analyze_phase(run, datasets):
    rows = read_rows(run / "rows.jsonl")
    assert len(rows) == 880 and len({r["review_key"] for r in rows}) == 880
    results, statistics = {}, {}
    for ds, (_, qs, _) in datasets.items():
        for pool in POOL_ARMS:
            grouped = {
                p: [r for r in rows if r["dataset"] == ds and r["arm"] == f"{pool}-{p}"]
                for p in ("T", "M", "F", "G")
            }
            for policy, selected in grouped.items():
                assert len(selected) == len(qs)
                positive = [r for r in selected if r["answerable"]]
                summary = summarize(selected)["hybrid_rerank"]
                full = sum(r["delivered"]["complete"] for r in positive)
                results[f"{ds}:{pool}-{policy}"] = {
                    "summary": summary,
                    "delivered_complete": full,
                    "n": len(positive),
                    "candidate_complete": sum(r["candidate_complete"] for r in positive),
                    "top5_complete": sum(r["at_k"]["5"]["complete_evidence_hit"] for r in positive),
                    "top10_complete": sum(
                        r["at_k"]["10"]["complete_evidence_hit"] for r in positive
                    ),
                    "packing_failure_ids": [
                        r["id"]
                        for r in positive
                        if r["at_k"]["5"]["complete_evidence_hit"]
                        and not r["delivered"]["complete"]
                    ],
                    "neighbor_rescue_ids": [
                        r["id"]
                        for r in positive
                        if not r["candidate_complete"] and r["delivered"]["complete"]
                    ],
                    "success_ids": [r["id"] for r in positive if r["delivered"]["complete"]],
                }
                old = {r["id"]: r for r in grouped["T"]}
                for r in selected:
                    assert (
                        r["diagnostics"]["candidates"] == old[r["id"]]["diagnostics"]["candidates"]
                    )
                    assert (
                        r["diagnostics"]["source_bundle_sha256"]
                        == old[r["id"]]["diagnostics"]["source_bundle_sha256"]
                    )
                if policy in {"F", "G"}:
                    other = {r["id"]: r for r in grouped["F"]}
                    assert all(
                        r["diagnostics"]["feature_sha256"]
                        == other[r["id"]]["diagnostics"]["feature_sha256"]
                        for r in selected
                    )
            for left, right in [("T", "M"), ("T", "F"), ("T", "G"), ("F", "G")]:
                statistics[f"{ds}:{pool}:{right}_vs_{left}"] = paired_statistics(
                    grouped[left], grouped[right]
                )
    assert results["official:P0-T"]["delivered_complete"] == 43
    assert results["repository:P0-T"]["delivered_complete"] == 40
    primary = ["official:P1:G_vs_F", "official:P0:G_vs_T"]
    corrections = holm({key: statistics[key]["cluster_permutation_p"] for key in primary})
    for key, item in statistics.items():
        item["primary"] = key in primary
        item["holm_p"] = corrections.get(key)
    candidates = []
    for pool in POOL_ARMS:
        for policy in ("M", "F", "G"):
            arm = f"{pool}-{policy}"
            official, repo = results[f"official:{arm}"], results[f"repository:{arm}"]
            qualified = (
                official["delivered_complete"] >= 44
                and repo["delivered_complete"] >= 40
                and all(
                    cid in official["success_ids"] for cid in ["official-002-1", "official-004-4"]
                )
            )
            if qualified:
                candidates.append(arm)
    candidates.sort(
        key=lambda arm: (
            -results[f"official:{arm}"]["delivered_complete"],
            -results[f"repository:{arm}"]["delivered_complete"],
            -results[f"official:{arm}"]["summary"]["at_k"]["5"]["ndcg"],
            0 if arm.startswith("P0") else 1,
            0 if arm.endswith("M") else 1,
            arm,
        )
    )
    winner = candidates[0] if candidates else None
    decision = {
        "qualified_dev_candidates": candidates,
        "winner": winner,
        "diagnostic_arm": winner or "P1-G",
        "quarantine_arm": winner or "P0-T",
        "default_changed": False,
        "independent_human_fact_review": "pending",
        "holdout_status": "eligible_after_freeze" if winner else "not_run_dev_gate_failed",
    }
    write_json(run / "summary.json", results)
    write_json(run / "paired-statistics.json", statistics)
    write_json(run / "decision.json", decision)
    lines = [
        "# 冻结候选的证据集合选择实验",
        "",
        "AI编写、稀疏来源标签；dev-only；指标不是回答正确率。",
        "P1关闭版本保护，不能把旧42/54当作其控制组；全部使用完整候选池。",
        "",
        "| 数据集／组 | 候选完整 | Top5 | Top10 | 交付 | nDCG@5 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, item in results.items():
        lines.append(
            f"| {name} | {item['candidate_complete']:g}/{item['n']} | "
            f"{item['top5_complete']:g} | {item['top10_complete']:g} | "
            f"{item['delivered_complete']:g}/{item['n']} | "
            f"{item['summary']['at_k']['5']['ndcg']:.4f} |"
        )
    lines += [
        "",
        "## 预注册主检验",
        "",
        "| 对照 | 差值 | 配对率差95%CI | 簇置换p | Holm p |",
        "|---|---:|---|---:|---:|",
    ]
    for key in primary:
        item = statistics[key]
        ci = " – ".join(f"{x * 100:.2f}%" for x in item["delta_rate_ci95"])
        lines.append(
            f"| {key} | {item['delta_count']:+g} | {ci} | "
            f"{item['cluster_permutation_p']:.6f} | {item['holm_p']:.6f} |"
        )
    lines += [
        "",
        f"开发门槛：官方≥44/54、仓库≥40/50，并保留002-1与004-4；胜出配置：{winner or '无'}。",
        "按簇配对bootstrap 10000次、seed42；其他对照为探索性，详见paired-statistics.json。",
        "默认global30不变；任何统计增益都不能替代独立事实审核。",
    ]
    (run / "report.md").write_text("\n".join(lines) + "\n")
    return decision


def answers_phase(run, datasets, protocol):
    rows = read_rows(run / "rows.jsonl")
    decision = json.loads((run / "decision.json").read_text())
    path = run / "answers.jsonl"
    answers = read_rows(path)
    done = {r["review_key"] for r in answers}
    model = client(650)
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        protocol["models"]["embedding"]["path"], local_files_only=True
    )
    questions = {
        (ds, q["id"]): q
        for ds, (dataset, qs, _) in datasets.items()
        for q in enrich_questions(qs, dataset)
    }
    wanted = []
    for ds in datasets:
        ids = protocol["generation_ids"] if ds == "official" else protocol["coverage_ids"]
        for arm in ["P0-T", decision["diagnostic_arm"]]:
            wanted.extend(
                copy.deepcopy(r)
                for r in rows
                if r["dataset"] == ds and r["arm"] == arm and r["id"] in ids
            )
    for cid in ["official-002-2", "official-002-4"]:
        q = questions["official", cid]
        context = oracle_context(q)
        blocks, kept = [], []
        for original in context["evidence"]:
            item = copy.deepcopy(original)
            header = f"[{item['citation_id']}]\n"

            def fits(content, header=header, blocks=blocks):
                text = "\n\n".join(blocks + [header + content])
                return (
                    len(text) <= 4000
                    and len(tokenizer.encode(text, add_special_tokens=False)) <= 1200
                )

            content = snippet(item["content"], fits)
            if content:
                item["truncated"] = content != item["content"]
                item["content"] = content
                blocks.append(header + content)
                kept.append(item)
        context["evidence"] = kept
        context["budget"] = {"tokens": 1200, "characters": 4000}
        context["used_tokens"] = len(
            tokenizer.encode("\n\n".join(blocks), add_special_tokens=False)
        )
        context["used_characters"] = len("\n\n".join(blocks))
        # Oracle excerpts remain diagnostic; do not enter candidate caches or the corpus.
        wanted.append(
            {
                "dataset": "official",
                "arm": "oracle",
                "id": cid,
                "query": q["query"],
                "answerable": True,
                "context": context,
                "delivered": span_coverage(context["evidence"], q),
                "required_points": q["answer_key"]["required_points"],
                "forbidden_claims": q["answer_key"]["forbidden_claims"],
                "review_key": f"official:{cid}:oracle",
            }
        )
    with path.open("a") as stream:
        for row in wanted:
            if row["review_key"] in done:
                continue
            row["generation"] = generate_answer(
                questions[row["dataset"], row["id"]],
                row["context"],
                replace(answer_settings(), query_language="none"),
                model,
            )
            answers.append(row)
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            stream.flush()
            print("answer", row["review_key"], row["generation"]["error"], flush=True)
    write_json(run / "answer-review.json", answer_review_template(answers))
    (run / "answer-review.md").write_text(review_markdown(answers))
    counts = Counter()
    for r in answers:
        response = r["generation"]["response"]
        counts["errors"] += bool(r["generation"]["error"])
        if not response:
            continue
        status = response["status"]
        counts[
            "answerable_refusal" if r["answerable"] and status == "no_evidence" else "other"
        ] += 1
        if r["answerable"] and status == "no_evidence":
            counts[
                "refusal_gold_delivered" if r["delivered"]["complete"] else "refusal_gold_missing"
            ] += 1
        if not r["answerable"]:
            counts[
                "unanswerable_refusal" if status == "no_evidence" else "unanswerable_answered"
            ] += 1
    write_json(
        run / "generation-summary.json",
        {
            "records": len(answers),
            "model_calls": sum(len(r["generation"]["calls"]) for r in answers),
            "counts": dict(counts),
            "fact_correct": None,
            "human_review": "pending",
        },
    )


def answer_settings():
    from infra_rag.config import Settings

    return Settings()


def quarantine_phase(run, datasets, bundles, base, store):
    risks = json.loads((ROOT / "evals/merged-corpus-v2/known-risk-review.json").read_text())
    selected, skipped = [], []
    for risk in risks:
        lines = Path(risk["source"]).read_text().splitlines()
        assert risk["quote"] == lines[risk["line"] - 1]
        # Source-only scope check: a statement that explicitly sums several module types is not
        # an expert-only equality. Avoid blindly trusting the old AI audit's uniform issue text.
        if "模型总参数量" in risk["quote"] and "专家" in risk["quote"] and "=" in risk["quote"]:
            selected.append(
                {
                    **risk,
                    "source_sha256": digest(Path(risk["source"])),
                    "status": "AI_scope_risk_pending_human",
                }
            )
        else:
            skipped.append({**risk, "reason": "no_explicit_expert_only_equality_in_quote"})
    blocked = set()
    for c in base.chunks:
        references = [
            {"source": c.source, "start_line": c.start_line, "end_line": c.end_line},
            *c.metadata.get("source_aliases", []),
        ]
        for ref in references:
            for risk in selected:
                if (
                    ref.get("source") == risk["source"]
                    and ref.get("start_line") is not None
                    and ref["start_line"]
                    <= risk["line"]
                    <= (ref.get("end_line") or ref["start_line"])
                ):
                    blocked.add(c.id)
    policy = {
        "selected_risks": selected,
        "skipped_risks": skipped,
        "blocked_ids": sorted(blocked),
        "risk_file_sha256": digest(ROOT / "evals/merged-corpus-v2/known-risk-review.json"),
    }
    policy["sha256"] = canonical_hash(policy)
    write_json(run / "quarantine-policy.json", policy)
    decision = json.loads((run / "decision.json").read_text())
    pool, selector = decision["quarantine_arm"].split("-")
    all_rows = read_rows(run / "rows.jsonl")
    q_path = run / "quarantine-rows.jsonl"
    q_rows = read_rows(q_path)
    done = {(r["dataset"], r["id"]) for r in q_rows}
    with q_path.open("a") as stream:
        for ds, (dataset, qs, _) in datasets.items():
            wrapper = FrozenSelectionRetrieval(
                base,
                bundles[ds, pool],
                selector,
                lambda query, ds=ds: store.get(ds, query),
                blocked_ids=blocked,
            )
            for row in evaluation_rows(
                wrapper,
                [q for q in qs if (ds, q["id"]) not in done],
                dataset,
                variants=["hybrid_rerank"],
            ):
                assert not blocked.intersection(e["chunk_id"] for e in row["context"]["evidence"])
                row.update(
                    dataset=ds,
                    arm="Q1",
                    policy_sha256=policy["sha256"],
                    review_key=f"{ds}:{row['id']}:Q1",
                )
                q_rows.append(row)
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                stream.flush()
    result = {}
    for ds in datasets:
        original = [
            r for r in all_rows if r["dataset"] == ds and r["arm"] == decision["quarantine_arm"]
        ]
        new = [r for r in q_rows if r["dataset"] == ds]
        result[ds] = {
            "comparison": paired_statistics(original, new),
            "original_summary": summarize(original),
            "quarantined_summary": summarize(new),
            "original_gold_intersects_quarantine": [
                r["id"]
                for r in original
                if r["resolved_gold"] and blocked.intersection(r["resolved_gold"]["relevant"])
            ],
        }
    write_json(run / "quarantine-summary.json", result)
    # Fixed source-risk samples are generation diagnostics, not used to choose the quarantine.
    q_answers = read_rows(run / "quarantine-answers.jsonl")
    done = {r["review_key"] for r in q_answers}
    ds = "repository"
    questions = {q["id"]: q for q in enrich_questions(datasets[ds][1], datasets[ds][0])}
    model = client(650)
    with (run / "quarantine-answers.jsonl").open("a") as stream:
        for original in q_rows:
            if (
                original["dataset"] != ds
                or original["id"] not in {"repo-053-1", "repo-053-2"}
                or original["review_key"] in done
            ):
                continue
            row = copy.deepcopy(original)
            row["generation"] = generate_answer(
                questions[row["id"]], row["context"], answer_settings(), model
            )
            q_answers.append(row)
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            stream.flush()
    write_json(run / "quarantine-answer-review.json", answer_review_template(q_answers))
    (run / "quarantine-answer-review.md").write_text(review_markdown(q_answers))


def live_bundle(base, banks, query, scoring, pool):
    diag = {}
    if pool == "P0":
        base.settings = replace(base.settings, candidate_k=30, rerank=True)
        base.search(
            scoring, top_k=10, domain="infra", modality="text", strategy="hybrid", diagnostics=diag
        )
    else:
        wrapper = PartitionedRetrieval(base, banks, {query: scoring}, version_priority=False)
        wrapper.search(
            query, top_k=10, domain="infra", modality="text", strategy="hybrid", diagnostics=diag
        )
    fusion = {h["chunk_id"]: h["rrf_score"] for h in diag.get("fusion", [])}
    for bank in diag.get("banks", {}).values():
        fusion.update({h["chunk_id"]: h["rrf_score"] for h in bank.get("fusion", [])})
    record = {
        "scoring_query": scoring,
        "hits": [
            {
                "chunk_id": h["chunk_id"],
                "rerank_score": h["rerank_score"],
                "score": fusion.get(h["chunk_id"], 0),
            }
            for h in diag["final"]
        ],
    }
    record["sha256"] = canonical_hash(record)
    return record


def latency_phase(run, datasets, base, banks):
    protocol = json.loads((run / "protocol.json").read_text())
    decision = json.loads((run / "decision.json").read_text())
    pool, policy = decision["diagnostic_arm"].split("-")
    path = run / "latency.jsonl"
    records = read_rows(path)
    done = {(r["dataset"], r["id"], r["arm"]) for r in records}
    by_id = {c.id: c for c in base.chunks}
    vectors = dict(zip((c.id for c in base.chunks), base.vectors, strict=True))
    encoder = base._encoder()
    # Warm both encoder and scorer; no reported quality/latency uses the warmup output.
    encoder.encode(["cache"], query=True)
    base.reranker.predict([("cache", "cache")])
    with path.open("a") as stream:
        for ds, (_, qs, translations) in datasets.items():
            ids = protocol["generation_ids"] if ds == "official" else protocol["coverage_ids"]
            for index, q in enumerate(q for q in qs if q["id"] in ids):
                order = ["baseline", "candidate"] if index % 2 == 0 else ["candidate", "baseline"]
                for arm in order:
                    if (ds, q["id"], arm) in done:
                        continue
                    query = q["query"]
                    scoring = translations.get(query, query)
                    started = perf_counter()
                    bundle = live_bundle(
                        base, banks, query, scoring, "P0" if arm == "baseline" else pool
                    )
                    retrieval_ms = (perf_counter() - started) * 1000
                    hits = [
                        Hit(by_id[h["chunk_id"]], h["score"], rerank_score=h["rerank_score"])
                        for h in bundle["hits"]
                    ]
                    facets_ms = rerank_ms = 0.0
                    facet = None
                    matrix = None
                    if arm == "candidate" and policy in {"F", "G"}:
                        facet = extract_one(
                            query, scoring, "English" if ds == "official" else "Chinese"
                        )
                        facets_ms = facet["latency_ms"]
                        phase = perf_counter()
                        pairs = [
                            (f["question"], h.chunk.content) for f in facet["facets"] for h in hits
                        ]
                        scores = [float(x) for x in base.reranker.predict(pairs)]
                        matrix = [
                            scores[i * len(hits) : (i + 1) * len(hits)]
                            for i in range(len(facet["facets"]))
                        ]
                        rerank_ms = (perf_counter() - phase) * 1000
                    phase = perf_counter()
                    selected, _ = select_order(
                        hits, "T" if arm == "baseline" else policy, vectors=vectors, matrix=matrix
                    )
                    pack_context(
                        selected[:5],
                        base.parent_index,
                        encoder.token_length,
                        1200,
                        4000,
                        "infra",
                        "text",
                    )
                    record = {
                        "dataset": ds,
                        "id": q["id"],
                        "arm": arm,
                        "policy": "P0-T" if arm == "baseline" else decision["diagnostic_arm"],
                        "mode": (
                            "uncached_retrieval_facet_api_and_scoring; frozen_translation_shared"
                        ),
                        "retrieval_ms": retrieval_ms,
                        "facet_api_ms": facets_ms,
                        "facet_rerank_ms": rerank_ms,
                        "selection_and_pack_ms": (perf_counter() - phase) * 1000,
                        "end_to_end_ms": (perf_counter() - started) * 1000,
                        "fresh_facets": facet,
                        "candidates": len(hits),
                    }
                    records.append(record)
                    stream.write(json.dumps(record, ensure_ascii=False) + "\n")
                    stream.flush()
                    print("latency", ds, q["id"], arm, round(record["end_to_end_ms"]), flush=True)
    from infra_rag.offline_evaluation import latency_summary

    write_json(
        run / "latency-summary.json",
        {
            arm: {
                metric: latency_summary([r[metric] for r in records if r["arm"] == arm])
                for metric in [
                    "retrieval_ms",
                    "facet_api_ms",
                    "facet_rerank_ms",
                    "selection_and_pack_ms",
                    "end_to_end_ms",
                ]
            }
            for arm in ["baseline", "candidate"]
        },
    )


def confirmation_phase(run, base, banks, protocol):
    decision = json.loads((run / "decision.json").read_text())
    if not decision["winner"]:
        write_json(
            run / "confirmation-status.json",
            {
                "status": "not_run",
                "reason": "pre-registered dev gate failed; no holdout/test queries used",
            },
        )
        return
    # Freeze before reading any confirmation questions; this file cannot be changed on resume.
    directory = run / "confirmation"
    directory.mkdir(exist_ok=True)
    locked = {
        "winner": decision["winner"],
        "protocol_sha256": digest(run / "protocol.json"),
        "decision_sha256": digest(run / "decision.json"),
        "quarantine": "Q0_original_corpus",
        "note": (
            "Q1 remains source-risk diagnostic, pending independent review; "
            "no confirmation-driven tuning"
        ),
    }
    lock = directory / "lock.json"
    if lock.exists():
        assert json.loads(lock.read_text()) == locked
    else:
        write_json(lock, locked)
    official = ROOT / "evals/infra-official-v1-reviewed"
    repository = ROOT / "evals/repository-benchmark"
    holdout = json.loads((official / "holdout.json").read_text())
    test = json.loads((repository / "test.json").read_text())
    test = [
        {
            **q,
            "answerable": True,
            "evidence_alternatives": [{"spans": q["relevant_spans"]}],
            "answer_key": {"required_points": [q["expected_answer"]], "forbidden_claims": []},
        }
        for q in test
    ]
    translation_path = directory / "translations.json"
    translations = json.loads(translation_path.read_text()) if translation_path.exists() else {}
    for q in holdout:
        if q["query"] not in translations:
            model = client(220)
            started = perf_counter()
            scoring = translate_query(q["query"], model)
            translations[q["query"]] = {
                "english": scoring,
                "provider_response": model.last_call,
                "latency_ms": (perf_counter() - started) * 1000,
            }
            write_json(translation_path, translations)
    pool, policy = decision["winner"].split("-")
    rows = read_rows(directory / "rows.jsonl")
    done = {(r["dataset"], r["id"], r["arm"]) for r in rows}
    with (directory / "rows.jsonl").open("a") as stream:
        for ds, dataset, qs in [("official", official, holdout), ("repository", repository, test)]:
            bundles = {"P0": {}, pool: {}}
            for q in qs:
                query = q["query"]
                scoring = translations[query]["english"] if ds == "official" else query
                for p in bundles:
                    path = directory / "candidates" / ds / p / f"{q['id']}.json"
                    if path.exists():
                        bundle = json.loads(path.read_text())
                    else:
                        bundle = live_bundle(base, banks, query, scoring, p)
                        write_json(path, bundle)
                    bundles[p][query] = bundle
                facet_path = directory / "facets" / ds / f"{q['id']}.json"
                if policy in {"F", "G"} and not facet_path.exists():
                    write_json(
                        facet_path,
                        extract_one(query, scoring, "English" if ds == "official" else "Chinese"),
                    )
            shared = {(ds, p): bundles.get(p, bundles[pool]) for p in POOL_ARMS}
            questions = {(ds, q["query"]): q for q in qs}
            store = FeatureStore(directory, base, shared, questions)
            for arm, p, selector in [("baseline", "P0", "T"), ("candidate", pool, policy)]:
                wrapper = FrozenSelectionRetrieval(
                    base,
                    bundles[p],
                    selector,
                    lambda query, ds=ds, store=store: store.get(ds, query),
                )
                for row in evaluation_rows(
                    wrapper,
                    [q for q in qs if (ds, q["id"], arm) not in done],
                    dataset,
                    variants=["hybrid_rerank"],
                ):
                    row.update(dataset=ds, arm=arm, review_key=f"{ds}:{row['id']}:{arm}")
                    rows.append(row)
                    stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                    stream.flush()
                    print("confirmation", ds, arm, row["id"], flush=True)
    write_json(
        directory / "summary.json",
        {
            f"{ds}:{arm}": summarize([r for r in rows if r["dataset"] == ds and r["arm"] == arm])
            for ds in ["official", "repository"]
            for arm in ["baseline", "candidate"]
        },
    )
    write_json(
        directory / "paired-statistics.json",
        {
            ds: paired_statistics(
                [r for r in rows if r["dataset"] == ds and r["arm"] == "baseline"],
                [r for r in rows if r["dataset"] == ds and r["arm"] == "candidate"],
            )
            for ds in ["official", "repository"]
        },
    )
    write_json(
        run / "confirmation-status.json",
        {
            "status": "completed_once",
            "winner": decision["winner"],
            "default_changed": False,
            "human_fact_review": "pending",
        },
    )


def accounting_phase(run):
    """Aggregate observed supplier usage; never substitute local estimates for billed tokens."""
    stages = {}

    def add(stage, responses):
        counts = Counter()
        models = Counter()
        supplied = 0
        responses = list(responses)
        for response in responses:
            if not response:
                continue
            models[response.get("model") or "unreported"] += 1
            if isinstance(response.get("usage"), dict):
                supplied += 1
                for key, value in response["usage"].items():
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        counts[key] += value
        stages[stage] = {
            "attempted_calls": len(responses),
            "calls_with_supplier_usage": supplied,
            "supplier_reported_usage": dict(counts),
            "supplier_reported_models": dict(models),
        }

    add(
        "dev_facets",
        (
            json.loads(p.read_text()).get("provider_response")
            for p in sorted((run / "facets").glob("*/*.json"))
        ),
    )
    for stage, filename in [
        ("answers", "answers.jsonl"),
        ("quarantine_answers", "quarantine-answers.jsonl"),
    ]:
        add(
            stage,
            (
                call.get("provider_response")
                for row in read_rows(run / filename)
                for call in row["generation"]["calls"]
            ),
        )
    add(
        "uncached_latency_facets",
        (
            r["fresh_facets"].get("provider_response")
            for r in read_rows(run / "latency.jsonl")
            if r.get("fresh_facets")
        ),
    )
    features = [json.loads(p.read_text()) for p in (run / "features").glob("*/*.json")]
    write_json(
        run / "cost-accounting.json",
        {
            "source": "supplier_response.usage; monetary price not measured",
            "stages": stages,
            "additional_bge_pairs": sum(f["pairs"] for f in features),
            "bge_pairs_would_truncate": sum(
                p["would_truncate"] is True
                for f in features
                for p in f["input_diagnostics"]["pairs"]
            ),
            "confirmation_accounting": "separate confirmation artifacts, if dev gate passes",
        },
    )
    rows = read_rows(run / "rows.jsonl")
    breakdown = {}
    for ds, arm in sorted({(r["dataset"], r["arm"]) for r in rows}):
        selected = [r for r in rows if (r["dataset"], r["arm"]) == (ds, arm)]
        groups = {}
        for question_type in sorted({r["question_type"] for r in selected}):
            positive = [
                r for r in selected if r["question_type"] == question_type and r["answerable"]
            ]
            groups[question_type] = {
                "n": len(positive),
                "delivered_complete": sum(r["delivered"]["complete"] for r in positive),
            }
        breakdown[f"{ds}:{arm}"] = {
            "question_types": groups,
            "delivered_collections": dict(
                Counter(
                    e["metadata"].get("collection", "unknown")
                    for r in selected
                    for e in r["context"]["evidence"]
                )
            ),
            "context_truncated_evidence": sum(
                e["truncated"] for r in selected for e in r["context"]["evidence"]
            ),
        }
    write_json(run / "breakdown.json", breakdown)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "evals/merged-corpus-v2/evidence-selection-v3/run-20261002",
    )
    parser.add_argument(
        "--phase",
        choices=[
            "all",
            "facets",
            "retrieval",
            "analyze",
            "answers",
            "quarantine",
            "latency",
            "confirmation",
            "accounting",
        ],
        default="all",
    )
    args = parser.parse_args()
    run = args.output.resolve()
    directory, datasets, bundles, questions, protocol = prepare_run(run)
    if args.phase in {"all", "facets"}:
        facets_phase(run, datasets)
    base = banks = store = None
    if args.phase in {"all", "retrieval", "quarantine", "latency", "confirmation"}:
        base, banks = load_models(directory, protocol)
        store = FeatureStore(run, base, bundles, questions)
    if args.phase in {"all", "retrieval"}:
        retrieval_phase(run, datasets, bundles, base, store)
    if args.phase in {"all", "analyze"}:
        analyze_phase(run, datasets)
    if args.phase in {"all", "answers"}:
        answers_phase(run, datasets, protocol)
    if args.phase in {"all", "quarantine"}:
        quarantine_phase(run, datasets, bundles, base, store)
    if args.phase in {"all", "latency"}:
        latency_phase(run, datasets, base, banks)
    if args.phase in {"all", "confirmation"}:
        confirmation_phase(run, base, banks, protocol)
    if args.phase in {"all", "accounting"}:
        accounting_phase(run)
    if args.phase == "all":
        record_operation(
            "完成冻结候选证据选择主实验与隔离支线",
            "验证条件评分和集合覆盖，独立检查源文风险",
            f"结果{run}；默认global30不变",
            "AI标签稀疏；事实审核待人工；确认集仅在冻结且通过dev门槛后运行",
        )


if __name__ == "__main__":
    main()
