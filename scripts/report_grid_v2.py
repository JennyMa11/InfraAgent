"""Audit staged Grid v2 outputs without treating partial stages as completed trials."""

import argparse
import json
from collections import defaultdict
from pathlib import Path

from operation_log import record_operation

from infra_rag.benchmarking import digest, write_new
from infra_rag.grid_metrics import latency


def load(path):
    return json.loads(path.read_text())


def verified(path):
    if digest(path) != load(path.with_suffix(".sha256.json"))["sha256"]:
        raise ValueError(f"Trace hash differs: {path}")
    return load(path)


def audit_stage(run, stage):
    schedule_file = run / "schedules" / (stage + ".json")
    if not schedule_file.exists():
        return {"state": "not_scheduled", "complete": False}, {}
    schedule = load(schedule_file)
    expected = {(j["config"], j["id"], j["rep"]) for j in schedule}
    if len(expected) != len(schedule):
        raise ValueError("Duplicate scheduled outputs")
    observed, grouped = set(), defaultdict(list)
    for path in (run / "rows" / stage).rglob("*.json"):
        if path.name.endswith(".sha256.json"):
            continue
        row = verified(path)
        if row["status"] == "completed" and "pairs" in row and row["pairs"] > 90:
            raise ValueError(f"Observed rerank pair cap violation: {path}")
        cid = f"{row['dataset']}:{row['id']}" if "dataset" in row else row["id"]
        key = row.get("config", row.get("config_id")), cid, row.get("rep", row.get("repetition", 0))
        if key not in expected or key in observed:
            raise ValueError(f"Unexpected/duplicate trace: {path}")
        observed.add(key)
        grouped[key[0]].append(row)
    failed = sum(r["status"] != "completed" for rs in grouped.values() for r in rs)
    return {
        "state": "complete" if observed == expected and not failed else "incomplete",
        "complete": observed == expected and not failed,
        "planned": len(expected),
        "observed": len(observed),
        "completed": len(observed) - failed,
        "failed": failed,
        "missing": sorted(expected - observed),
    }, grouped


def proportion(values):
    return {
        "numerator": sum(values),
        "denominator": len(values),
        "value": sum(values) / len(values) if values else None,
        "coverage": 1.0 if values else None,
    }


def metrics(rows):
    result = {}
    for dataset in ("official", "repository"):
        group = [r for r in rows if r.get("dataset") == dataset and r["status"] == "completed"]
        positive = [r for r in group if r["answerable"]]
        value = {
            "outputs": len(group),
            "positive_outputs": len(positive),
            "negative_outputs": len(group) - len(positive),
            "unique_questions": len({r["id"] for r in group}),
        }
        if group and "candidate" in group[0]:
            for name, field in (
                ("candidate_complete", "complete"),
                ("required_recall", "coverage"),
            ):
                value[name] = proportion([r["candidate"][field] for r in positive])
            for k in (5, 10):
                value[f"ranked_complete{k}"] = proportion(
                    [r[f"ranked_complete{k}"]["complete"] for r in positive]
                )
                value[f"delivery{k}"] = proportion(
                    [r[f"delivery{k}"]["complete"] for r in positive]
                )
                for name in ("recall", "hit", "mrr"):
                    value[f"{name}{k}"] = proportion(
                        [r[f"rank_metrics{k}"][name] for r in positive]
                    )
                value[f"ndcg{k}"] = proportion([r[f"ndcg{k}"] for r in positive])
            value["truncated_items5"] = sum(
                e["truncated"] for r in group for e in r["pack5"]["evidence"]
            )
            value["max_delivery_tokens5"] = max(r["pack5"]["used_tokens"] for r in group)
            value["max_delivery_characters5"] = max(r["pack5"]["used_characters"] for r in group)
            if value["max_delivery_tokens5"] > 1200 or value["max_delivery_characters5"] > 4000:
                raise ValueError("Observed delivery budget violation")
        elif group:
            value["delivery5"] = proportion([r["delivery5"]["complete"] for r in positive])
            value["wall_latency_ms"] = latency([r["elapsed_ms"] for r in group])
        result[dataset] = value
    return result


def report(run, out):
    if out.exists():
        raise ValueError("Fresh report directory required")
    stages, results = {}, {}
    for stage in ("baseline", "A", "B", "C", "D", "E", "repeat", "ann"):
        stages[stage], groups = audit_stage(run, stage)
        results[stage] = (
            {
                name: metrics(rs)
                for name, rs in groups.items()
                if all(r["status"] == "completed" for r in rs)
            }
            if stages[stage]["complete"]
            else {}
        )
    score_files = [
        p for p in (run / "cache/scores").glob("*.json") if not p.name.endswith(".sha256.json")
    ]
    scored = [verified(p) for p in score_files]
    summary = {
        "stage_status": stages,
        "metrics": results,
        "A_E_schedules_complete": all(stages[s]["complete"] for s in "ABCDE"),
        "observed_local_predict_operations": len(scored),
        "observed_local_scored_pairs": sum(len(s["scores"]) for s in scored),
        "generation_calls": 0,
        "answer_correctness": None,
        "independent_human_review": "pending",
        "default_adoption": False,
        "test_holdout_read": False,
    }
    out.mkdir(parents=True)
    write_new(out / "audit.json", summary)
    text = [
        "# Grid v2阶段验收",
        "",
        "这是冻结开发题上的检索与交付实验，不是答案正确率。",
        "",
        "| 阶段 | 计划 | 完成 | 失败 | 未记录 |",
        "|---|---:|---:|---:|---:|",
    ]
    for stage, data in stages.items():
        text.append(
            f"| {stage} | {data.get('planned', '—')} | {data.get('completed', 0)} | "
            f"{data.get('failed', 0)} | {len(data.get('missing', []))} |"
        )
    text += [
        "",
        "配置–问题输出不是独立问题；重复轮不增加独立题数。",
        "质量缓存阶段的耗时不作为生产延迟。实际预测资源根据已验哈希的本地评分账目统计。",
        "完整率按必要来源区间的AND/替代组OR计算；人工事实审核仍pending。",
        "缺失、失败及未安排阶段均不视作完成，未自动采用任何配置。",
        "",
    ]
    (out / "report.md").write_text("\n".join(text))
    write_new(
        out / "manifest.json",
        {str(p.relative_to(out)): digest(p) for p in out.iterdir() if p.is_file()},
    )
    record_operation(
        "Grid v2阶段报告与调度验收",
        "区分完整阶段、失败和未记录输出",
        str(out),
        "无；尚未完成阶段保持未完成" if not summary["A_E_schedules_complete"] else "无",
    )
    print(json.dumps({k: v for k, v in summary.items() if k != "metrics"}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report(args.run, args.out)


if __name__ == "__main__":
    main()
