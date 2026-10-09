"""Frozen dev-only budget allocation and repeated cited-support experiments."""

import argparse
import copy
import hashlib
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from pathlib import Path
from time import perf_counter

from benchmark_selection_v3 import client, read_rows, write_json
from operation_log import record_operation
from prepare_corpus_v2 import ROOT

from infra_rag.benchmarking import canonical_hash, digest, span_coverage
from infra_rag.budget_evidence import budget_pack
from infra_rag.claim_guard import (
    STRENGTH_PROMPT,
    VERIFY_PROMPT,
    generate_experimental,
    guarded_response,
    verify_answer,
)
from infra_rag.config import Settings
from infra_rag.context import pack_context
from infra_rag.evaluation import evidence_metrics
from infra_rag.models import Chunk, Hit
from infra_rag.offline_evaluation import answer_review_template, latency_summary, review_markdown
from infra_rag.paired_statistics import holm, paired_statistics

OLD = ROOT / "evals/merged-corpus-v2/recall-delivery-v4/run-20261002"
OUT = ROOT / "evals/merged-corpus-v2/budget-support-v5"
ARMS = [f"{pool}-{policy}" for pool in ("B", "Q") for policy in ("T5", "T8", "R8", "C8")]


def setup(run):
    prior = json.loads((OLD / "protocol.json").read_text())
    prior_artifacts = json.loads((OLD / "artifacts-manifest.json").read_text())["files"]
    for name in ("protocol.json", "rows.jsonl", "answers.jsonl", "source-audit.json"):
        assert digest(OLD / name) == prior_artifacts[name]
    bundle_hashes = {
        str(p.relative_to(OLD)): digest(p) for p in sorted((OLD / "bundles").glob("*/*.json"))
    }
    for name, expected in bundle_hashes.items():
        assert expected == prior_artifacts[name]
    directory = ROOT / prior["directory"]
    assert digest(directory / "manifest.json") == prior["manifest_sha256"]
    manifest = json.loads((directory / "manifest.json").read_text())
    assert digest(directory / "chunks.json") == manifest["chunks_sha256"]
    previous = read_rows(OLD / "rows.jsonl")
    assert len(previous) == 770
    mapping = {(r["dataset"], r["id"], r["arm"]): r for r in previous}
    assert len(mapping) == 770
    for ds, name in (
        ("official", "infra-official-v1-reviewed"),
        ("repository", "repository-benchmark"),
    ):
        # Only hash/read dev. Cached v4 rows already contain frozen evaluation labels.
        assert digest(ROOT / "evals" / name / "dev.json") == prior["dev_hashes"][ds]
    raw = json.loads((directory / "chunks.json").read_text())
    chunks = {c["id"]: Chunk(**c) for c in raw}
    parents = {}
    for c in chunks.values():
        parents.setdefault(c.parent_id, []).append(c)
    source_audit = json.loads((OLD / "source-audit.json").read_text())
    for record in source_audit["source_files"]:
        assert digest(Path(record["source"])) == record["expected"]
    model = prior["models"]["embedding"]
    tokenizer_config = Path(model["path"]) / "sentence_bert_config.json"
    tokenizer_options = {"do_lower_case": json.loads(tokenizer_config.read_text())["do_lower_case"]}
    for name, expected in model["files"].items():
        with (Path(model["path"]) / name).open("rb") as f:
            assert hashlib.file_digest(f, "sha256").hexdigest() == expected
    source_files = sorted((ROOT / "src/infra_rag").glob("*.py")) + [
        Path(__file__),
        ROOT / "scripts/benchmark_selection_v3.py",
        ROOT / "scripts/prepare_corpus_v2.py",
    ]
    protocol = {
        "kind": "dev_only_budget_support_v5",
        "arms": ARMS,
        "plan_sha256": digest(OUT / "experiment-plan.md"),
        "prior_protocol_sha256": digest(OLD / "protocol.json"),
        "prior_rows_sha256": digest(OLD / "rows.jsonl"),
        "prior_answers_sha256": digest(OLD / "answers.jsonl"),
        "bundle_hashes": bundle_hashes,
        "manifest_sha256": prior["manifest_sha256"],
        "chunks_sha256": digest(directory / "chunks.json"),
        "directory": prior["directory"],
        "models": prior["models"],
        "tokenizer_options": tokenizer_options,
        "sentence_bert_config_sha256": digest(tokenizer_config),
        "answer_model": client(650).configuration(),
        "verifier_model": client(1000).configuration(),
        "strength_prompt_sha256": canonical_hash(STRENGTH_PROMPT),
        "verifier_prompt_sha256": canonical_hash(VERIFY_PROMPT),
        "dev_hashes": prior["dev_hashes"],
        "generation_ids": prior["generation_ids"],
        "repetitions": 2,
        "context_tokens": 1200,
        "context_chars": 4000,
        "source_files_verified": len(source_audit["source_files"]),
        "retrieval_calls": 0,
        "rerank_calls": 0,
        "include_metadata_both_generation_arms": True,
        "default_changed": False,
        "confirmation_questions_read": False,
        "implementation": {str(p.relative_to(ROOT)): digest(p) for p in source_files},
    }
    run.mkdir(parents=True, exist_ok=True)
    if (run / "protocol.json").exists():
        assert json.loads((run / "protocol.json").read_text()) == protocol
    else:
        write_json(run / "protocol.json", protocol)
        for name in protocol["implementation"]:
            target = run / "implementation" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        model["path"], local_files_only=True, **tokenizer_options
    )

    @lru_cache(maxsize=8192)
    def count(text):
        return len(tokenizer.encode(text, add_special_tokens=False))

    settings = Settings(
        data_dir=run, backend="bge", context_tokens=1200, context_chars=4000, query_language="none"
    )
    return protocol, mapping, chunks, parents, count, settings


def pack(pool, policy, baseline, chunks, parents, count):
    hits = [
        Hit(chunks[h["chunk_id"]], 0.0, rerank_score=h["rerank_score"])
        for h in baseline["diagnostics"]["final"]
    ]
    if policy in {"T5", "T8"}:
        chosen = hits[: 5 if policy == "T5" else 8]
        context = pack_context(chosen, parents, count, 1200, 4000, "infra", "text")
        eligible = list(
            dict.fromkeys(
                [e["chunk_id"] for e in context["evidence"]] + context["omitted_chunk_ids"]
            )
        )
        trace = {"eligible_ids": eligible, "selection_trace": []}
    else:
        scoring = baseline["query"]
        bundle = json.loads(
            (OLD / "bundles" / baseline["dataset"] / (baseline["id"] + ".json")).read_text()
        )
        scoring += "\n" + bundle["B5" if pool == "B" else "Q5"]["scoring_query"]
        chosen, context, trace = budget_pack(
            hits, baseline["context"], chunks, scoring, count, coverage=policy == "C8"
        )
    positions = {cid: i for i, cid in enumerate(chunks)}
    for e in context["evidence"]:
        e["source_position"] = positions[e["chunk_id"]]
    return chosen, context, trace


def retrieval(run, mapping, chunks, parents, count):
    records = read_rows(run / "rows.jsonl")
    done = {(r["dataset"], r["id"], r["arm"]) for r in records}
    for (ds, qid, old_arm), baseline in mapping.items():
        if old_arm not in {"B5", "Q5"}:
            continue
        pool = "B" if old_arm == "B5" else "Q"
        for policy in ("T5", "T8", "R8", "C8"):
            arm = f"{pool}-{policy}"
            if (ds, qid, arm) in done:
                continue
            started = perf_counter()
            chosen, context, trace = pack(pool, policy, baseline, chunks, parents, count)
            elapsed = (perf_counter() - started) * 1000
            if policy == "T5":
                assert context == baseline["context"]
            if arm == "B-T8":
                assert context == mapping[ds, qid, "B8"]["context"]
            row = copy.deepcopy(baseline)
            question = {
                **row,
                "evidence_alternatives": (
                    row["resolved_gold"]["evidence_alternatives"] if row["answerable"] else []
                ),
            }
            row.update(
                arm=arm,
                pool=pool,
                policy=policy,
                context=context,
                generation=None,
                review_key=f"{ds}:{qid}:{arm}",
                packing_latency_ms=elapsed,
                selected_ids=[h.chunk.id for h in chosen],
                packing_trace=trace,
                delivered=span_coverage(context["evidence"], question),
            )
            row["selected_complete"] = row["packing_pool_complete"] = None
            if row["answerable"]:
                gold = row["resolved_gold"]
                row["selected_complete"] = evidence_metrics(
                    row["selected_ids"], gold, max(1, len(chosen))
                )["complete_evidence_hit"]
                ids = trace["eligible_ids"]
                row["packing_pool_complete"] = evidence_metrics(ids, gold, max(1, len(ids)))[
                    "complete_evidence_hit"
                ]
            with (run / "rows.jsonl").open("a") as stream:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            records.append(row)
            print("packing", ds, qid, arm, flush=True)
    assert len(records) == 880


def analyze(run):
    rows = read_rows(run / "rows.jsonl")
    summary = {}
    for ds in ("official", "repository"):
        for arm in ARMS:
            selected = [r for r in rows if r["dataset"] == ds and r["arm"] == arm]
            positives = [r for r in selected if r["answerable"]]
            summary[f"{ds}:{arm}"] = {
                "questions": len(selected),
                "answerable": len(positives),
                "candidate_complete": sum(r["candidate_complete"] for r in positives),
                "packing_pool_complete": sum(r["packing_pool_complete"] for r in positives),
                "selected_complete": sum(r["selected_complete"] for r in positives),
                "delivered_complete": sum(r["delivered"]["complete"] for r in positives),
                "eligible_total": sum(len(r["packing_trace"]["eligible_ids"]) for r in selected),
                "truncated": sum(
                    e["truncated"] for r in selected for e in r["context"]["evidence"]
                ),
                "mean_tokens": sum(r["context"]["used_tokens"] for r in selected) / len(selected),
            }
    statistics, primary = {}, []
    for ds in ("official", "repository"):
        for pool in ("B", "Q"):
            for before, after in (("T8", "R8"), ("R8", "C8"), ("T5", "R8"), ("T5", "C8")):
                key = f"{ds}:{pool}-{after}_vs_{pool}-{before}"
                statistics[key] = paired_statistics(
                    [r for r in rows if r["dataset"] == ds and r["arm"] == f"{pool}-{before}"],
                    [r for r in rows if r["dataset"] == ds and r["arm"] == f"{pool}-{after}"],
                )
                if ds == "official" and (before, after) in (("T8", "R8"), ("R8", "C8")):
                    primary.append(key)
    for key, value in holm({k: statistics[k]["cluster_permutation_p"] for k in primary}).items():
        statistics[key]["holm_p"] = value
    eligible = []
    for arm in ("B-C8", "B-R8", "Q-C8", "Q-R8"):
        o, r = summary[f"official:{arm}"], summary[f"repository:{arm}"]
        core = [
            v for v in rows if v["arm"] == arm and v["id"] in {"official-002-1", "official-004-4"}
        ]
        if (
            o["delivered_complete"] >= 44
            and r["delivered_complete"] >= 40
            and all(v["delivered"]["complete"] for v in core)
        ):
            eligible.append(arm)
    order = {arm: i for i, arm in enumerate(("B-C8", "B-R8", "Q-C8", "Q-R8"))}
    eligible.sort(
        key=lambda a: (
            -summary[f"official:{a}"]["delivered_complete"],
            -summary[f"repository:{a}"]["delivered_complete"],
            summary[f"official:{a}"]["eligible_total"]
            + summary[f"repository:{a}"]["eligible_total"],
            order[a],
        )
    )
    write_json(run / "summary.json", summary)
    write_json(run / "paired-statistics.json", statistics)
    write_json(
        run / "decision.json",
        {
            "eligible": eligible,
            "context_arm": eligible[0] if eligible else "B-T5",
            "selection_frozen_before_generation": True,
            "default_changed": False,
        },
    )


def generation(run, protocol, settings):
    arm = json.loads((run / "decision.json").read_text())["context_arm"]
    selected = [
        r
        for r in read_rows(run / "rows.jsonl")
        if r["arm"] == arm and r["id"] in protocol["generation_ids"]
    ]
    assert len(selected) == 23
    done = {
        (r["dataset"], r["id"], r["prompt"], r["repetition"])
        for r in read_rows(run / "answers.jsonl")
    }
    lock = {
        "context_arm": arm,
        "decision_sha256": digest(run / "decision.json"),
        "protocol_sha256": digest(run / "protocol.json"),
        "contexts": {r["review_key"]: canonical_hash(r["context"]) for r in selected},
    }
    if (run / "generation-lock.json").exists():
        assert json.loads((run / "generation-lock.json").read_text()) == lock
    else:
        write_json(run / "generation-lock.json", lock)

    def one(row, prompt, repetition):
        row = copy.deepcopy(row)
        row["context"]["include_evidence_metadata"] = True
        row.update(
            prompt=prompt,
            repetition=repetition,
            review_key=f"{row['dataset']}:{row['id']}:{arm}:{prompt}:r{repetition}",
        )
        row["generation"] = generate_experimental(
            row, row["context"], settings, client(650), strength=prompt == "G1"
        )
        row["verification"] = verify_answer(row, row["generation"], row["context"], client(1000))
        row["guarded_response"] = guarded_response(row["generation"], row["verification"])
        return row

    with ThreadPoolExecutor(max_workers=4) as executor:
        jobs = [
            executor.submit(one, r, g, rep)
            for rep in (1, 2)
            for r in selected
            for g in ("G0", "G1")
            if (r["dataset"], r["id"], g, rep) not in done
        ]
        for future in as_completed(jobs):
            r = future.result()
            with (run / "answers.jsonl").open("a") as stream:
                stream.write(json.dumps(r, ensure_ascii=False) + "\n")
            print(
                "answer",
                r["id"],
                r["prompt"],
                r["repetition"],
                r["verification"]["verdict"],
                flush=True,
            )
    answers = read_rows(run / "answers.jsonl")
    assert len(answers) == 92
    write_json(run / "answer-review.json", answer_review_template(answers))
    (run / "answer-review.md").write_text(review_markdown(answers))


def probes(run):
    previous = read_rows(OLD / "answers.jsonl")
    cases = {
        ("repo-002-1", "B5"),
        ("repo-002-1", "Q5"),
        ("repo-053-2", "Q5"),
        ("official-004-4", "Q5"),
    }
    done = {r["review_key"] for r in read_rows(run / "verifier-probes.jsonl")}
    for row in previous:
        if (row["id"], row["arm"]) not in cases or row["review_key"] in done:
            continue
        r = {
            "review_key": row["review_key"],
            "id": row["id"],
            "arm": row["arm"],
            "answer": row["generation"]["response"]["answer"],
            "verification": verify_answer(row, row["generation"], row["context"], client(1000)),
            "not_part_of_prompt_contrast": True,
        }
        with (run / "verifier-probes.jsonl").open("a") as stream:
            stream.write(json.dumps(r, ensure_ascii=False) + "\n")


def latency(run, protocol, mapping, chunks, parents, count):
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
        for arm in ["B-T5", candidate] if i % 2 == 0 else [candidate, "B-T5"]:
            pool, policy = arm.split("-")
            source = mapping[row["dataset"], row["id"], "B5" if pool == "B" else "Q5"]
            started = perf_counter()
            # Remove tokenizer memoization during measured requests.
            count.cache_clear()
            pack(pool, policy, source, chunks, parents, count)
            record = {
                "id": row["id"],
                "arm": arm,
                "baseline": arm == "B-T5",
                "ms": (perf_counter() - started) * 1000,
                "mode": "frozen_scores_pack_only_uncached_token_counts",
            }
            with (run / "latency.jsonl").open("a") as stream:
                stream.write(json.dumps(record) + "\n")


def report(run):
    summary = json.loads((run / "summary.json").read_text())
    decision = json.loads((run / "decision.json").read_text())
    answers = read_rows(run / "answers.jsonl")
    calls = [
        c for r in answers for field in ("generation", "verification") for c in r[field]["calls"]
    ]
    calls += [
        c for r in read_rows(run / "verifier-probes.jsonl") for c in r["verification"]["calls"]
    ]
    usage = Counter()
    for c in calls:
        for k, v in (c.get("provider_response", {}).get("usage") or {}).items():
            if isinstance(v, (float, int)) and not isinstance(v, bool):
                usage[k] += v
    groups = {}
    for prompt in ("G0", "G1"):
        selected = [r for r in answers if r["prompt"] == prompt]
        counts = Counter()
        for r in selected:
            counts["generation_errors"] += bool(r["generation"]["error"])
            counts["format_valid"] += r["generation"]["checks"]["format_valid"]
            counts["verifier_" + r["verification"]["verdict"]] += 1
            counts["verification_errors"] += bool(r["verification"]["error"])
            response = r["generation"]["response"]
            if response:
                refused = response["status"] == "no_evidence"
                counts["answerable_refusal" if r["answerable"] else "unanswerable_refusal"] += (
                    refused
                )
                counts["guard_added_refusal"] += (
                    response["status"] == "answered"
                    and r["guarded_response"]["status"] == "no_evidence"
                )
        variants = {}
        for r in selected:
            variants.setdefault(r["id"], []).append(r["generation"]["response"])
        counts["different_repeat_answers"] = sum(
            bool(
                v[0]
                and v[1]
                and (v[0]["status"], v[0]["answer"]) != (v[1]["status"], v[1]["answer"])
            )
            for v in variants.values()
        )
        groups[prompt] = dict(counts)
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
    latencies = {
        arm: latency_summary([r["ms"] for r in times if r["arm"] == arm])
        for arm in dict.fromkeys(r["arm"] for r in times)
    }
    write_json(run / "latency-summary.json", latencies)
    lines = [
        "# 预算覆盖与引用支持v5执行报告",
        "",
        "仅dev，AI稀疏来源标签。未读holdout/test，默认不变；独立人工事实审核pending。",
        "880条回放，不新增召回/重排调用；92条重复生成，4条旧答案核验探针。",
        "",
        "| 组 | 官方候选完整 | 官方可选池完整 | 官方已选ID完整 | 官方交付 | 仓库交付 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        o, r = summary[f"official:{arm}"], summary[f"repository:{arm}"]
        lines.append(
            f"| {arm} | {o['candidate_complete']:g}/54 | {o['packing_pool_complete']:g}/54 | "
            f"{o['selected_complete']:g}/54 | {o['delivered_complete']:g}/54 | "
            f"{r['delivered_complete']:g}/50 |"
        )
    lines += [
        "",
        "R8/C8最多选择8个原段，原Top10排名不变。邻接段弱先验不是BGE新评分。",
        "可选池只表示原文ID覆盖，正文截断仍按实际交付核对。",
        "",
        f"冻结生成上下文配置：{decision['context_arm']}；开发合格组：{decision['eligible']}。",
        "",
        "| 官方主对照 | 净差 | 率差95% CI | Holm p |",
        "|---|---:|---|---:|",
    ]
    for key, s in json.loads((run / "paired-statistics.json").read_text()).items():
        if "holm_p" in s:
            ci = " 至 ".join(f"{v:.2%}" for v in s["delta_rate_ci95"])
            lines.append(f"| {key} | {s['delta_count']:+g} | {ci} | {s['holm_p']:.6f} |")
    lines += [
        "",
        "G0/G1的来源/版本元数据一致，仅G1添加通用条件强度提示。各23题×2次重复。",
        "V0/V1仅保留核验通过的原答案，其余拒答；机器核验不是独立正确率。",
        "",
        "| 提示 | 格式通过 | 可回答题拒答/42 | 核验不支持 | 核验不确定 | 新增拒答 | 重复变化/23 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for p, g in groups.items():
        lines.append(
            f"| {p} | {g.get('format_valid', 0)}/46 | {g.get('answerable_refusal', 0)} | "
            f"{g.get('verifier_unsupported', 0)} | {g.get('verifier_uncertain', 0)} | "
            f"{g.get('guard_added_refusal', 0)} | {g.get('different_repeat_answers', 0)} |"
        )
    lines += [
        "",
        "核验器仅见实际引用；来源自身错误仍可能通过，详见verifier-probes.jsonl。",
        "同上下文重复变化不应解释成打包造成的事实差异。人工模板见answer-review.json。",
        "",
        f"实际API调用{len(calls)}次，usage见cost-accounting.json；失败与重试原样保留。",
        "打包延迟仅为冻结回放，不包含召回、BGE重排或生成；见latency-summary.json。",
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
    args = parser.parse_args()
    run = args.output.resolve()
    protocol, mapping, chunks, parents, count, settings = setup(run)
    retrieval(run, mapping, chunks, parents, count)
    analyze(run)
    generation(run, protocol, settings)
    probes(run)
    latency(run, protocol, mapping, chunks, parents, count)
    report(run)
    record_operation(
        "完成预算覆盖与引用支持v5开发实验",
        "分离固定候选预算选择与回答条件强度",
        f"880回放/92生成/4核验探针/46打包延迟；产物{run}",
        "机器核验不是事实正确率；dev-only，默认不变",
    )


if __name__ == "__main__":
    main()
