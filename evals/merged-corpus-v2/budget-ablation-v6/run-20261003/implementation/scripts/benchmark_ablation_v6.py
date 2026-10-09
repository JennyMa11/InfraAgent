"""Frozen four-factor budget ablation and corpus-only quarantine; dev only."""

import argparse
import copy
import hashlib
import itertools
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path
from time import perf_counter

from benchmark_budget_v5 import OLD, client, read_rows, write_json
from benchmark_budget_v5 import pack as control_pack
from prepare_corpus_v2 import ROOT

from infra_rag.benchmarking import canonical_hash, digest, span_coverage
from infra_rag.budget_ablation import AblationPacker
from infra_rag.claim_guard import generate_experimental
from infra_rag.config import Settings
from infra_rag.evaluation import evidence_metrics
from infra_rag.models import Chunk, Hit
from infra_rag.offline_evaluation import answer_review_template, latency_summary, review_markdown
from infra_rag.paired_statistics import holm, paired_statistics
from infra_rag.source_quarantine import source_risks

OUT = ROOT / "evals/merged-corpus-v2/budget-ablation-v6"
V5 = ROOT / "evals/merged-corpus-v2/budget-support-v5/run-20261003"
CONFIGS = {
    f"k{'8' if limit else 'all'}-l{'05' if power else '0'}-p{protect}-n{int(neighbors)}": {
        "limit": limit,
        "length_power": power,
        "protect": protect,
        "neighbors": neighbors,
    }
    for limit, power, protect, neighbors in itertools.product(
        (8, None), (0.5, 0.0), (1, 5), (True, False)
    )
}
BASE = "k8-l05-p1-n1"
PRIMARY = ("kall-l05-p1-n1", "k8-l0-p1-n1", "k8-l05-p5-n1", "k8-l05-p1-n0")
ARMS = [f"{p}-{c}" for p in ("B", "Q") for c in ("T5", "T8", *CONFIGS)]
PROBES = {"repo-002-1", "repo-053-2", "official-002-1", "official-004-4"}


def setup(run):
    started = perf_counter()
    prior = json.loads((OLD / "protocol.json").read_text())
    v5 = json.loads((V5 / "protocol.json").read_text())
    inputs = {}
    for folder, names in (
        (OLD, ["protocol.json", "rows.jsonl", "source-audit.json"]),
        (V5, ["protocol.json", "rows.jsonl", "decision.json"]),
    ):
        manifest = json.loads((folder / "artifacts-manifest.json").read_text())["files"]
        for name in names:
            assert digest(folder / name) == manifest[name]
            inputs[str((folder / name).relative_to(ROOT))] = manifest[name]
    bundles = {}
    old_manifest = json.loads((OLD / "artifacts-manifest.json").read_text())["files"]
    for path in sorted((OLD / "bundles").glob("*/*.json")):
        assert digest(path) == old_manifest[str(path.relative_to(OLD))]
        inputs[str(path.relative_to(ROOT))] = digest(path)
        bundles[path.parent.name, path.stem] = json.loads(path.read_text())
    directory = ROOT / prior["directory"]
    assert digest(directory / "manifest.json") == prior["manifest_sha256"]
    manifest = json.loads((directory / "manifest.json").read_text())
    assert digest(directory / "chunks.json") == manifest["chunks_sha256"] == v5["chunks_sha256"]
    for ds, name in (
        ("official", "infra-official-v1-reviewed"),
        ("repository", "repository-benchmark"),
    ):
        assert digest(ROOT / "evals" / name / "dev.json") == prior["dev_hashes"][ds]
    old = read_rows(OLD / "rows.jsonl")
    fifth = read_rows(V5 / "rows.jsonl")
    mapping = {(r["dataset"], r["id"], r["arm"]): r for r in old}
    reference = {(r["dataset"], r["id"], r["arm"]): r for r in fifth}
    assert len(mapping) == 770 and len(reference) == 880
    chunks = {c["id"]: Chunk(**c) for c in json.loads((directory / "chunks.json").read_text())}
    parents = {}
    for c in chunks.values():
        parents.setdefault(c.parent_id, []).append(c)
    audit = json.loads((OLD / "source-audit.json").read_text())
    for r in audit["source_files"]:
        assert digest(Path(r["source"])) == r["expected"]
    risks = source_risks(chunks.values())
    source_hashes = {r["source"]: r["expected"] for r in audit["source_files"]}
    for r in risks:
        assert r["source_sha256"] == source_hashes[r["source"]]
    model = prior["models"]["embedding"]
    sentence_config = Path(model["path"]) / "sentence_bert_config.json"
    options = {"do_lower_case": json.loads(sentence_config.read_text())["do_lower_case"]}
    for name, expected in model["files"].items():
        with (Path(model["path"]) / name).open("rb") as f:
            assert hashlib.file_digest(f, "sha256").hexdigest() == expected
    files = sorted((ROOT / "src/infra_rag").glob("*.py")) + [
        Path(__file__),
        ROOT / "scripts/benchmark_budget_v5.py",
        ROOT / "scripts/benchmark_selection_v3.py",
        ROOT / "scripts/prepare_corpus_v2.py",
    ]
    protocol = {
        "kind": "dev_only_budget_ablation_v6",
        "arms": ARMS,
        "configs": CONFIGS,
        "primary_official_contrasts": list(PRIMARY),
        "base_config": BASE,
        "plan_sha256": digest(OUT / "experiment-plan.md"),
        "frozen_inputs": inputs,
        "directory": prior["directory"],
        "manifest_sha256": prior["manifest_sha256"],
        "chunks_sha256": digest(directory / "chunks.json"),
        "models": prior["models"],
        "tokenizer_options": options,
        "sentence_bert_config_sha256": digest(sentence_config),
        "answer_model": client(650).configuration(),
        "dev_hashes": prior["dev_hashes"],
        "generation_ids": v5["generation_ids"],
        "source_probe_ids": sorted(PROBES),
        "repetitions": 2,
        "context_tokens": 1200,
        "context_chars": 4000,
        "source_files_verified": len(audit["source_files"]),
        "risks_sha256": canonical_hash(risks),
        "source_references": [
            "https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-best-practices-guide/index.html#a-simple-access-pattern",
            "https://jmlr.org/papers/v23/21-0998.html",
        ],
        "risk_status": "AI_scope_risk_pending_human",
        "retrieval_calls": 0,
        "rerank_calls": 0,
        "include_metadata_all_generation_arms": True,
        "verifier_calls": 0,
        "default_changed": False,
        "confirmation_questions_read": False,
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in files},
    }
    assert len(protocol["generation_ids"]) == 23 and PROBES <= set(protocol["generation_ids"])
    run.mkdir(parents=True, exist_ok=True)
    if (run / "protocol.json").exists():
        assert json.loads((run / "protocol.json").read_text()) == protocol
        assert json.loads((run / "source-risks.json").read_text()) == risks
    else:
        write_json(run / "protocol.json", protocol)
        write_json(run / "source-risks.json", risks)
        (run / "experiment-plan.md").write_bytes((OUT / "experiment-plan.md").read_bytes())
        for name in protocol["implementation"]:
            target = run / "implementation" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
    source_ms = (perf_counter() - started) * 1000
    started = perf_counter()
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model["path"], local_files_only=True, **options)

    @lru_cache(maxsize=32768)
    def count(text):
        return len(tokenizer.encode(text, add_special_tokens=False))

    write_json(
        run / "setup-timing.json",
        {
            "source_input_verification_ms": source_ms,
            "tokenizer_loading_ms": (perf_counter() - started) * 1000,
            "included_in_pack_latency": False,
        },
    )
    settings = Settings(
        data_dir=run, backend="bge", context_tokens=1200, context_chars=4000, query_language="none"
    )
    return protocol, mapping, reference, chunks, parents, bundles, count, settings, risks


def selector(row, pool, chunks, bundles, count, blocked=()):
    hits = [
        Hit(chunks[h["chunk_id"]], 0.0, rerank_score=h["rerank_score"])
        for h in row["diagnostics"]["final"]
    ]
    scoring = (
        row["query"]
        + "\n"
        + bundles[row["dataset"], row["id"]]["B5" if pool == "B" else "Q5"]["scoring_query"]
    )
    return AblationPacker(hits, row["context"], chunks, scoring, count, blocked_ids=blocked)


def packing(row, pool, config, chunks, parents, bundles, count, blocked=()):
    if config in CONFIGS:
        return selector(row, pool, chunks, bundles, count, blocked).pack(**CONFIGS[config])
    if not blocked:
        return control_pack(pool, config, row, chunks, parents, count)
    filtered = copy.deepcopy(row)
    filtered["diagnostics"]["final"] = [
        h for h in row["diagnostics"]["final"] if h["chunk_id"] not in blocked
    ]
    active_parents = {pid: [c for c in cs if c.id not in blocked] for pid, cs in parents.items()}
    return control_pack(pool, config, filtered, chunks, active_parents, count)


def output(row, arm, pool, config, chosen, context, trace, positions):
    row = copy.deepcopy(row)
    for e in context["evidence"]:
        e["source_position"] = positions[e["chunk_id"]]
    question = {
        **row,
        "evidence_alternatives": (
            row["resolved_gold"]["evidence_alternatives"] if row["answerable"] else []
        ),
    }
    row.update(
        arm=arm,
        pool=pool,
        policy=config,
        context=context,
        generation=None,
        review_key=f"{row['dataset']}:{row['id']}:{arm}",
        selected_ids=[h.chunk.id for h in chosen],
        packing_trace=trace,
        delivered=span_coverage(context["evidence"], question),
        selected_complete=None,
        packing_pool_complete=None,
    )
    if row["answerable"]:
        for key, ids in (
            ("selected_complete", row["selected_ids"]),
            ("packing_pool_complete", trace["eligible_ids"]),
        ):
            row[key] = evidence_metrics(ids, row["resolved_gold"], max(1, len(ids)))[
                "complete_evidence_hit"
            ]
    return row


def append(path, row):
    with path.open("a") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def retrieval(run, mapping, reference, chunks, parents, bundles, count):
    records = read_rows(run / "rows.jsonl")
    done = {(r["dataset"], r["id"], r["arm"]) for r in records}
    assert len(done) == len(records)
    positions = {cid: i for i, cid in enumerate(chunks)}
    for (ds, qid, old_arm), row in mapping.items():
        if old_arm not in {"B5", "Q5"}:
            continue
        pool = "B" if old_arm == "B5" else "Q"
        p = selector(row, pool, chunks, bundles, count)
        for config in ("T5", "T8", *CONFIGS):
            arm = f"{pool}-{config}"
            if (ds, qid, arm) in done:
                continue
            started = perf_counter()
            result = (
                p.pack(**CONFIGS[config])
                if config in CONFIGS
                else packing(row, pool, config, chunks, parents, bundles, count)
            )
            chosen, context, trace = result
            elapsed = (perf_counter() - started) * 1000
            record = output(row, arm, pool, config, chosen, context, trace, positions)
            if config in {"T5", "T8", BASE}:
                prior_config = "C8" if config == BASE else config
                assert record["context"] == reference[ds, qid, f"{pool}-{prior_config}"]["context"]
            record["packing_latency_ms_cached_features"] = elapsed
            append(run / "rows.jsonl", record)
            records.append(record)
        print("packed", len(records), ds, qid, pool, flush=True)
    assert len(records) == 3960


def summarize(rows):
    result = {}
    for ds in ("official", "repository"):
        for arm in dict.fromkeys(r["arm"] for r in rows):
            rs = [r for r in rows if r["dataset"] == ds and r["arm"] == arm]
            pos = [r for r in rs if r["answerable"]]
            result[f"{ds}:{arm}"] = {
                "questions": len(rs),
                "answerable": len(pos),
                "candidate_complete": sum(r["candidate_complete"] for r in pos),
                "packing_pool_complete": sum(r["packing_pool_complete"] for r in pos),
                "selected_complete": sum(r["selected_complete"] for r in pos),
                "delivered_complete": sum(r["delivered"]["complete"] for r in pos),
                "mean_evidence_count": sum(len(r["context"]["evidence"]) for r in rs) / len(rs),
                "mean_tokens": sum(r["context"]["used_tokens"] for r in rs) / len(rs),
                "truncated": sum(e["truncated"] for r in rs for e in r["context"]["evidence"]),
            }
    return result


def analyze(run):
    rows = read_rows(run / "rows.jsonl")
    summary = summarize(rows)
    grouped = {
        (ds, arm): [r for r in rows if r["dataset"] == ds and r["arm"] == arm]
        for ds in ("official", "repository")
        for arm in ARMS
    }
    statistics, primary = {}, []
    for pool in ("B", "Q"):
        for config in PRIMARY:
            key = f"official:{pool}-{config}_vs_{pool}-{BASE}"
            statistics[key] = paired_statistics(
                grouped["official", f"{pool}-{BASE}"], grouped["official", f"{pool}-{config}"]
            )
            primary.append(key)
    for k, v in holm({k: statistics[k]["cluster_permutation_p"] for k in primary}).items():
        statistics[k]["holm_p"] = v
    for ds in ("official", "repository"):
        for pool in ("B", "Q"):
            for config in CONFIGS:
                key = f"{ds}:{pool}-{config}_vs_{pool}-T5"
                statistics[key] = paired_statistics(
                    grouped[ds, f"{pool}-T5"], grouped[ds, f"{pool}-{config}"]
                )
                statistics[key]["exploratory"] = True
    eligible = []
    for pool in ("B", "Q"):
        for config in CONFIGS:
            arm = f"{pool}-{config}"
            o, r = summary[f"official:{arm}"], summary[f"repository:{arm}"]
            core = [v for v in grouped["official", arm] if v["id"] in PROBES]
            assert len(core) == 2
            if (
                o["delivered_complete"] >= 44
                and r["delivered_complete"] >= 40
                and all(v["delivered"]["complete"] for v in core)
            ):
                eligible.append(arm)
    eligible.sort(
        key=lambda a: (
            -summary[f"official:{a}"]["delivered_complete"],
            -summary[f"repository:{a}"]["delivered_complete"],
            (
                summary[f"official:{a}"]["mean_evidence_count"] * 60
                + summary[f"repository:{a}"]["mean_evidence_count"] * 50
            )
            / 110,
            0 if a.startswith("B-") else 1,
            a.split("-", 1)[1],
        )
    )
    decision = {
        "eligible": eligible,
        "context_arm": eligible[0] if eligible else "B-T5",
        "selection_frozen_before_generation": True,
        "default_changed": False,
    }
    if (run / "decision.json").exists():
        assert json.loads((run / "decision.json").read_text()) == decision
    write_json(run / "summary.json", summary)
    write_json(run / "paired-statistics.json", statistics)
    write_json(run / "decision.json", decision)


def quarantine(run, mapping, chunks, parents, bundles, count, risks):
    blocked = {r["chunk_id"] for r in risks}
    arm = json.loads((run / "decision.json").read_text())["context_arm"]
    pool, config = arm.split("-", 1)
    original = {
        (r["dataset"], r["id"]): r for r in read_rows(run / "rows.jsonl") if r["arm"] == arm
    }
    records = read_rows(run / "quarantine.jsonl")
    done = {r["review_key"] for r in records}
    positions = {cid: i for i, cid in enumerate(chunks)}
    for (ds, qid), base in original.items():
        frozen = mapping[ds, qid, "B5" if pool == "B" else "Q5"]
        for name in ("Q0", "Q1"):
            key = f"{ds}:{qid}:{name}"
            if key in done:
                continue
            if name == "Q0":
                row = copy.deepcopy(base)
                row.update(arm=name, review_key=key)
            else:
                chosen, ctx, trace = packing(
                    frozen, pool, config, chunks, parents, bundles, count, blocked
                )
                row = output(frozen, name, pool, config, chosen, ctx, trace, positions)
            row["packing_strategy"] = arm
            row["original_candidate_complete"] = frozen["candidate_complete"]
            candidates = list(frozen["diagnostics"]["candidates"])
            row["blocked_candidate_ids"] = sorted(blocked.intersection(candidates))
            row["blocked_context_ids"] = sorted(
                blocked.intersection(e["chunk_id"] for e in base["context"]["evidence"])
            )
            gold_ids = set()
            if row["answerable"]:
                gold_ids = {
                    cid
                    for alt in row["resolved_gold"]["evidence_alternatives"]
                    for requirement in alt["requirements"]
                    for cid in requirement
                }
                active = (
                    candidates
                    if name == "Q0"
                    else [cid for cid in candidates if cid not in blocked]
                )
                row["candidate_complete"] = evidence_metrics(
                    active, row["resolved_gold"], max(1, len(active))
                )["complete_evidence_hit"]
                assert name != "Q0" or row["candidate_complete"] == frozen["candidate_complete"]
            row["gold_risk_intersection"] = sorted(blocked & gold_ids)
            if name == "Q1":
                assert not blocked.intersection(e["chunk_id"] for e in row["context"]["evidence"])
                assert not blocked.intersection(row["packing_trace"]["eligible_ids"])
            append(run / "quarantine.jsonl", row)
            records.append(row)
    assert len(records) == 220
    write_json(run / "quarantine-summary.json", summarize(records))
    write_json(
        run / "quarantine-statistics.json",
        {
            ds: paired_statistics(
                [r for r in records if r["dataset"] == ds and r["arm"] == "Q0"],
                [r for r in records if r["dataset"] == ds and r["arm"] == "Q1"],
            )
            for ds in ("official", "repository")
        },
    )


def generation(run, protocol, settings):
    decision = json.loads((run / "decision.json").read_text())
    arm = decision["context_arm"]
    retrieval = read_rows(run / "rows.jsonl")
    quarantine_rows = read_rows(run / "quarantine.jsonl")
    tasks = []
    if decision["eligible"]:
        for role, context_arm in (("baseline", "B-T5"), ("candidate", arm)):
            selected = [
                r
                for r in retrieval
                if r["arm"] == context_arm and r["id"] in protocol["generation_ids"]
            ]
            assert len(selected) == 23
            tasks += [(r, role, rep) for rep in (1, 2) for r in selected]
        selected = [r for r in quarantine_rows if r["arm"] == "Q1" and r["id"] in PROBES]
        tasks += [(r, "source-Q1", rep) for rep in (1, 2) for r in selected]
        expected = 100
    else:
        selected = [r for r in quarantine_rows if r["id"] in PROBES]
        tasks = [(r, f"source-{r['arm']}", rep) for rep in (1, 2) for r in selected]
        expected = 16
    assert len(tasks) == expected
    lock = {
        "decision_sha256": digest(run / "decision.json"),
        "protocol_sha256": digest(run / "protocol.json"),
        "quarantine_sha256": digest(run / "quarantine.jsonl"),
        "expected_generations": expected,
        "contexts": {f"{role}:{r['id']}": canonical_hash(r["context"]) for r, role, rep in tasks},
        "source_Q0_reuse_candidate": bool(decision["eligible"]),
    }
    if (run / "generation-lock.json").exists():
        assert json.loads((run / "generation-lock.json").read_text()) == lock
    else:
        write_json(run / "generation-lock.json", lock)
    done = {r["review_key"] for r in read_rows(run / "answers.jsonl")}

    def one(row, role, rep):
        row = copy.deepcopy(row)
        row["context"]["include_evidence_metadata"] = True
        row.update(
            role=role,
            repetition=rep,
            prompt="G0",
            review_key=f"{row['dataset']}:{row['id']}:{role}:r{rep}",
        )
        row["generation"] = generate_experimental(
            row, row["context"], settings, client(650), strength=False
        )
        return row

    with ThreadPoolExecutor(max_workers=4) as executor:
        jobs = [
            executor.submit(one, r, role, rep)
            for r, role, rep in tasks
            if f"{r['dataset']}:{r['id']}:{role}:r{rep}" not in done
        ]
        for future in as_completed(jobs):
            row = future.result()
            append(run / "answers.jsonl", row)
            print(
                "answer",
                row["id"],
                row["role"],
                row["repetition"],
                row["generation"]["error"],
                flush=True,
            )
    answers = read_rows(run / "answers.jsonl")
    assert len(answers) == expected and len({r["review_key"] for r in answers}) == expected
    write_json(run / "answer-review.json", answer_review_template(answers))
    (run / "answer-review.md").write_text(review_markdown(answers))


def latency(run, protocol, mapping, chunks, parents, bundles, count):
    if (run / "latency.jsonl").exists():
        assert len(read_rows(run / "latency.jsonl")) == 46
        return
    candidate = json.loads((run / "decision.json").read_text())["context_arm"]
    count("Tokenizer warmup for KV cache.")
    sample = [
        r for (ds, qid, a), r in mapping.items() if a == "B5" and qid in protocol["generation_ids"]
    ]
    assert len(sample) == 23
    for i, row in enumerate(sample):
        roles = [("baseline", "B-T5"), ("candidate", candidate)]
        for role, arm in roles if i % 2 == 0 else roles[::-1]:
            pool, config = arm.split("-", 1)
            source = mapping[row["dataset"], row["id"], "B5" if pool == "B" else "Q5"]
            count.cache_clear()
            started = perf_counter()
            packing(source, pool, config, chunks, parents, bundles, count)
            append(
                run / "latency.jsonl",
                {
                    "id": row["id"],
                    "arm": arm,
                    "role": role,
                    "ms": (perf_counter() - started) * 1000,
                    "mode": "frozen_pack_uncached_token_counts_current_request_features",
                },
            )


def report(run):
    summary = json.loads((run / "summary.json").read_text())
    decision = json.loads((run / "decision.json").read_text())
    answers = read_rows(run / "answers.jsonl")
    calls = [c for r in answers for c in r["generation"]["calls"]]
    usage, groups = Counter(), {}
    for c in calls:
        for k, v in (c.get("provider_response", {}).get("usage") or {}).items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                usage[k] += v
    for role in dict.fromkeys(r["role"] for r in answers):
        rs = [r for r in answers if r["role"] == role]
        groups[role] = {
            "generations": len(rs),
            "errors": sum(bool(r["generation"]["error"]) for r in rs),
            "format_valid": sum(r["generation"]["checks"]["format_valid"] for r in rs),
            "answerable_refusals": sum(
                bool(
                    r["answerable"]
                    and r["generation"]["response"]
                    and r["generation"]["response"]["status"] == "no_evidence"
                )
                for r in rs
            ),
        }
    write_json(run / "generation-summary.json", groups)
    write_json(
        run / "cost-accounting.json",
        {
            "actual_calls": len(calls),
            "supplier_usage": dict(usage),
            "source": "provider response fields; monetary costs not measured",
        },
    )
    times = read_rows(run / "latency.jsonl")
    write_json(
        run / "latency-summary.json",
        {
            role: latency_summary([r["ms"] for r in times if r["role"] == role])
            for role in ("baseline", "candidate")
        },
    )
    lines = [
        "# 预算消融与来源隔离v6执行报告",
        "",
        "dev-only；AI稀疏标签，多轮调参，不是独立确认或回答正确率。默认不变，人工事实审核pending。",
        "3960条冻结回放+220条来源隔离对照；不新增召回或BGE重排。",
        "",
        "| 组 | 官方候选 | 官方可选池 | 官方交付/54 | 仓库交付/50 | 平均交付段数(官方/仓库) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        o, r = summary[f"official:{arm}"], summary[f"repository:{arm}"]
        lines.append(
            f"| {arm} | {o['candidate_complete']:g} | {o['packing_pool_complete']:g} | "
            f"{o['delivered_complete']:g} | {r['delivered_complete']:g} | "
            f"{o['mean_evidence_count']:.2f}/{r['mean_evidence_count']:.2f} |"
        )
    lines += [
        "",
        f"冻结配置：{decision['context_arm']}；合格组：{decision['eligible']}。",
        "",
        "| 官方单因素主对照 | 净差 | 95%簇CI | Holm p |",
        "|---|---:|---|---:|",
    ]
    for k, s in json.loads((run / "paired-statistics.json").read_text()).items():
        if "holm_p" in s:
            ci = " 至 ".join(f"{v:.2%}" for v in s["delta_rate_ci95"])
            lines.append(f"| {k} | {s['delta_count']:+g} | {ci} | {s['holm_p']:.6f} |")
    lines += [
        "",
        "其他组合与相对T5对照均探索性；保护仅尝试保留完整句前缀，不保证整段。",
        "",
        "| 来源隔离 | 官方交付/54 | 仓库交付/50 |",
        "|---|---:|---:|",
    ]
    qs = json.loads((run / "quarantine-summary.json").read_text())
    for name in ("Q0", "Q1"):
        lines.append(
            f"| {name} | {qs['official:' + name]['delivered_complete']:g} | "
            f"{qs['repository:' + name]['delivered_complete']:g} |"
        )
    lines += [
        "",
        "来源隔离规则在回放前冻结；保留原gold并报告风险交集。规则仅AI范围风险，待人工审阅。",
        "来源片段可能仍有未标出的歧义，正确建议也可能被模型复述成必要条件；隔离不能替代事实审核。",
        "",
        f"{len(answers)}条重复生成，{len(calls)}次实际API调用；无同模型自审器。",
        "相同原提示和元数据，实际提示、错误、usage均保存；生成数与机器格式指标不是正确率。",
        "46条交错打包延迟仅冻结候选路径，未含新检索/重排/生成；加载开销另列。",
    ]
    (run / "execution-report.md").write_text("\n".join(lines) + "\n")
    write_json(
        run / "confirmation-status.json",
        {
            "status": "not_run_dev_only_protocol",
            "no_confirmation_questions_read": True,
            "default_changed": False,
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUT / "run-20261003")
    run = parser.parse_args().output.resolve()
    protocol, mapping, reference, chunks, parents, bundles, count, settings, risks = setup(run)
    retrieval(run, mapping, reference, chunks, parents, bundles, count)
    analyze(run)
    quarantine(run, mapping, chunks, parents, bundles, count, risks)
    generation(run, protocol, settings)
    latency(run, protocol, mapping, chunks, parents, bundles, count)
    report(run)


if __name__ == "__main__":
    main()
