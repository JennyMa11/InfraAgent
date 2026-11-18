"""Record an explicitly AI-authored rubric audit after reading all 60 actual answers."""

import argparse
import json
import re
import shutil
from collections import Counter
from pathlib import Path

from operation_log import record_operation

from infra_rag.benchmarking import digest, write_new
from infra_rag.grid_metrics import latency


def load(path):
    return json.loads(path.read_text())


def judgment(row):
    """Post-run AI review, not a frozen automatic scorer or independent human label."""
    case, turn, rep, config = (row[k] for k in ("case_id", "turn", "repetition", "config_id"))
    if case == "bc01":
        return "partial", "固定递推状态、6/414MiB正确；缺MLA单层9MiB、24层216MiB。"
    if case == "bc07":
        return "partial", (
            "144MiB与约41倍正确，但新选择丢失12800→524288及原有循环/指数/缩放说明；"
            "404→260完整表格及算例条件仍未齐。"
            if config == "complete"
            else "144MiB、12800→524288与小矩阵/更新开销正确；404→260及硬件/缓冲条件仍缺。"
        )
    if case == "bc12":
        return "partial", (
            "核心机制与14.9ms反例正确；严格按原冻结rubric，未完整给出13.5/9.9/14.9对照。"
            "两组均部分，不能照搬历史单轮的complete标签。"
        )
    if case == "bc13":
        return "complete", "正确拒答未知生产P99，没有编造测量值。"
    if case == "bc08":
        return "complete", "快照8192恢复至10752，重算2560；未混同文本匹配与可恢复状态。"
    if case == "bc14" and turn == 1:
        return "complete", "区分KDA固定递推矩阵与MLA随上下文增长的低维历史。"
    if config == "prefix":
        if case == "bc02":
            return "partial", "共享头与压缩表示核心正确，但缺512/64分支构成及NoPE条件。"
        if case == "bc09" or case == "bc14":
            return "failed", "可回答问题错误拒答；关键快照正文未完整交付。"
        if case == "bc10":
            return "failed", "112.5GiB正确，但错误断言不同adapter同prompt即可共享KV。"
    if case == "bc02":
        return "complete", "头数与表示维度的区别、512+64分支、NoPE及64分支不旋转均写出。"
    if case == "bc09":
        return "complete", "明确物理页映射与递推快照机制不同，并给出8192/10752/2560。"
    if case == "bc10":
        return "complete", "区分adapter与112.5GiB KV容量；明确不同adapter不能仅凭同prompt共享。"
    if case == "bc14" and rep == 2:
        return "partial", "取舍正确；引用107/1714MiB却省略TP=8、每卡口径，数值条件不完整。"
    if case == "bc14":
        return "complete", "承接历史，明确快照更密减少重算但增加状态存储，没有引入无条件数值。"
    raise ValueError((case, turn, rep, config))


def report(run, out):
    if out.exists():
        raise ValueError("Fresh report directory required")
    manifest = load(run / "manifest.json")
    for name, sha in manifest.items():
        assert digest(run / name) == sha, name
    protocol = load(run / "protocol.json")
    paths = sorted((run / "outputs").glob("*.json"))
    rows = [load(p) for p in paths]
    assert len(rows) == 60
    assert len({(r["config_id"], r["case_id"], r["turn"], r["repetition"]) for r in rows}) == 60
    reviews, templates, stats = [], [], {}
    answers = ["# 实际回答与AI辅助审核", "", "60轮真实HTTP输出；不是独立人工事实审核。", ""]
    for path, row in zip(paths, rows, strict=True):
        assert row["case_sha256"] == protocol["case_hashes"][row["case_id"]]
        response = row.get("response", {})
        allowed = {c["citation_id"] for c in response.get("citations", [])}
        mentions = set(re.findall(r"\[(E[A-Za-z0-9_-]+)\]", response.get("answer", "")))
        assert mentions <= allowed
        grade, reason = judgment(row)
        identity = {
            k: row[k]
            for k in ("run_id", "config_id", "case_id", "turn", "repetition", "case_sha256")
        }
        identity.update(trace=str(path.resolve()), trace_sha256=digest(path))
        reviews.append(
            {
                **identity,
                "reviewer": "AI source/trace-based auxiliary review",
                "independent": False,
                "rubric_completeness": grade,
                "reason": reason,
                "citation_ids_legal": True,
                "independent_task_success": None,
            }
        )
        templates.append(
            {
                **identity,
                "status": "pending",
                "reviewer": None,
                "reviewed_at": None,
                "claim_inventory_complete": None,
                "claims": None,
                "citation_support": None,
                "task_success": None,
            }
        )
        answers += [
            f"## {path.stem}",
            "",
            row["question"],
            "",
            response.get("answer", ""),
            "",
            f"AI完整度：{grade}。{reason}",
            "",
        ]
    for config in ("prefix", "complete"):
        selected = [r for r in rows if r["config_id"] == config]
        audit = [r for r in reviews if r["config_id"] == config]
        calls = [c for r in selected for c in r.get("server_record", {}).get("model_calls", [])]
        usages = [
            c["provider_metadata"]["usage"]
            for c in calls
            if c.get("provider_metadata", {}).get("usage")
        ]
        stats[config] = {
            "actual_outputs": len(selected),
            "unique_scenarios": 9,
            "unique_turns": 10,
            "repetitions": 3,
            "http_status": dict(Counter(r["http_status"] for r in selected)),
            "response_status": dict(Counter(r["response"]["status"] for r in selected)),
            "abstention": {
                "correct_refusal": {
                    "numerator": sum(
                        r["case_id"] == "bc13" and r["response"]["status"] == "no_evidence"
                        for r in selected
                    ),
                    "denominator": 3,
                },
                "wrong_refusal_on_answerable": {
                    "numerator": sum(
                        r["case_id"] != "bc13" and r["response"]["status"] == "no_evidence"
                        for r in selected
                    ),
                    "denominator": 27,
                },
            },
            "ai_rubric_completeness": dict(Counter(r["rubric_completeness"] for r in audit)),
            "independent_task_success": {
                "numerator": None,
                "denominator": len(selected),
                "value": None,
                "reviewed": 0,
            },
            "latency_ms": latency([r["elapsed_ms"] for r in selected]),
            "actual_model_attempts": len(calls),
            "provider_usage_coverage": len(usages),
            "provider_usage_totals": dict(
                sum(
                    (
                        Counter({k: v for k, v in u.items() if isinstance(v, (int, float))})
                        for u in usages
                    ),
                    Counter(),
                )
            ),
            "model_cost_usd": None,
            "truncated_evidence_items": sum(
                e["truncated"]
                for r in selected
                for q in r["server_record"]["retrieval"]
                for e in q["evidence"]
            ),
        }
    by_id = {(r["config_id"], r["case_id"], r["turn"], r["repetition"]): r for r in rows}
    identical_ranks = 0
    for row in rows:
        if row["config_id"] != "prefix":
            continue
        pair = by_id[("complete", row["case_id"], row["turn"], row["repetition"])]
        identical_ranks += (
            row["server_record"]["retrieval"][0]["hit_ids"]
            == pair["server_record"]["retrieval"][0]["hit_ids"]
        )
    stats["paired_top5_identical"] = {"numerator": identical_ranks, "denominator": 30}
    stats["decision"] = "Do not adopt: bc07 loses exact counts; bc01/bc07 unsolved; human pending"
    out.mkdir(parents=True)
    shutil.copyfile(Path(__file__), out / "report-script.py")
    for name, value in [
        ("stats.json", stats),
        ("ai-review.json", reviews),
        ("human-review-template.json", templates),
    ]:
        write_new(out / name, value)
    (out / "answer-results.md").write_text("\n".join(answers))
    p, c = stats["prefix"], stats["complete"]
    pc, cc = p["ai_rubric_completeness"], c["ai_rubric_completeness"]
    text = f"""# 完整证据打包P0实验

结论：保持默认prefix，complete-v2仅为可关闭实验。bc02、bc09、bc10与bc14追问得到实质改善，
但bc07丢失原有精确更新次数，bc01与bc07的指定数值段仍未送达，因此未通过整体采用门槛。

## 范围与口径

9个用户开发场景、10轮问题、每组3重复，共60个真实HTTP输出、60次实际模型请求；没有重试。
原15场景并未全部重测。AI完整度不是独立准确率，30输出也不是30个独立问题。
按原冻结rubric，bc12机制正确但本轮两组均省略13.5/9.9完整对照，判partial；历史评分不改写。
bc14开启组第3次给107/1714MiB却未写TP=8每卡口径，判partial。独立人工60/60待审。

两组候选K=30、union、BGE/reranker不变、Top5不变、正文预算1200token/4000字符；
batch32、检索结果缓存0、检索模型已预热、temperature=0。交替配置顺序，重复轮保持独立会话。
新增选择仅使用已有重排池前15个完整chunk，不新检索、不新调用模型、不用答案标签打分。
全量Top5配对一致 {identical_ranks}/30。来源头/系统提示不是正文预算，实际provider usage另存。

## 分组结果（AI按原rubric辅助审核）

| 指标 | prefix | complete-v2 |
|---|---:|---:|
| complete / partial / failed（30轮/组） | {pc} | {cc} |
| 响应状态 | {p["response_status"]} | {c["response_status"]} |
| p50 / p95 ms（全部30输出） | {p["latency_ms"]} | {c["latency_ms"]} |
| 模型尝试 | {p["actual_model_attempts"]} | {c["actual_model_attempts"]} |
| 截断证据项 | {p["truncated_evidence_items"]} | {c["truncated_evidence_items"]} |

延迟只是这60轮的描述性观测，不声明加速：旧主进程与新实验进程的历史、模型供应商缓存不可完全配平。
引用ID全部合法仅表示ID契约通过，不代表每条主张受到支持。费用未知，未猜测USD。

## 逐题结论与剩余工作

- bc02：3/3写出512+64、64维QK分支及NoPE；原组3/3缺少关键组成。
- bc09：3/3区别物理块映射与递推快照，给出8192/10752/2560；原组3/3错误拒答。
- bc10：3/3正确限制不同adapter共享KV；原组3/3错误允许共享。
  兼容条件在08-L310，候选排第8，属于已召回后未选中。
- bc14第二轮：3/3能解释重算/存储取舍；其中1次数字条件遗漏。原组3/3错误拒答。
- bc01：两组都缺完整MLA占用，02-L420排第6。仍未解决。
- bc07：两组都不完整；新组3/3还丢12800→524288及原有具体开销说明。
  这是真实子目标回退，不能因同为partial隐藏。
- bc08、bc13保持正确机制/拒答；bc12两组机制正确但严格数值对照不完整。
- bc03召回、bc04歧义、bc05/06/11生成条件以及bc15代码拼接，本轮未实模重测，不声称解决。

下一项独立修复应把表格表头/数值行与说明、适用条件作为结构包选择，防止查询词覆盖偏向次要段落；
为已交付的精确次数建立保留检查。代码完整性另做结构拼接验收，不能只检查代码围栏闭合。

## 冻结与限制

组件r1因AutoTokenizer加载方式与运行时计数不一致而中止；r2/r3未全过主门槛，全部保留。
r4用同款BGEEncoder复现旧16轮证据，bc02/bc09主门槛通过；这是已知开发题上的修订，非独立验证。
`final`是完整重排池，不能读成返回Top5。bc01/表格段排6、bc14快照段排11。
默认8000没有切换，未覆盖既有答案、AI审核或pending人工模板，没有接入分页或研究Agent。

原始运行：{run.resolve()}

完整60份实际回答见[answer-results.md](answer-results.md)；全部usage、候选、排名和正文在原始trace。
新AI审核与pending人工模板绑定case/trace SHA256；review-manifest记录产物哈希。
"""
    (out / "report.md").write_text(text)
    write_new(
        out / "review-manifest.json",
        {
            "run_manifest_sha256": digest(run / "manifest.json"),
            "protocol_sha256": digest(run / "protocol.json"),
            "case_sha256": digest(run / "cases.json"),
            "report_script_sha256": digest(Path(__file__)),
            "review_type": "AI auxiliary, not independent human",
            "files": {str(p.relative_to(out)): digest(p) for p in out.iterdir() if p.is_file()},
        },
    )
    record_operation(
        "完成60轮真实问答AI辅助审核与报告",
        "区分证据送达、生成完整度与默认采用",
        f"报告 {out}；完整度与回退分项登记；独立人工pending，不采用默认",
        "bc01/bc07未解决且bc07子目标回退；bc14一次数值条件遗漏；费用未知",
    )
    print(json.dumps(stats, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report(args.run, args.out)


if __name__ == "__main__":
    main()
