"""Audit full HTTP requests, provider usage and paired evidence delivery."""

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from benchmark_runtime_e2e import verify
from operation_log import record_operation
from prepare_corpus_pilot import load, save

from infra_rag.benchmarking import canonical_hash, digest
from infra_rag.grid_metrics import latency


def proportion(numerator, denominator):
    return {
        "numerator": numerator,
        "denominator": denominator,
        "value": numerator / denominator if denominator else None,
    }


def evidence_hash(row):
    return canonical_hash(
        [
            [
                {
                    key: item.get(key)
                    for key in [
                        "citation_id",
                        "chunk_id",
                        "source",
                        "locator",
                        "content",
                        "metadata",
                        "truncated",
                    ]
                }
                for item in call["evidence"]
            ]
            for call in row["server_record"].get("retrieval", [])
        ]
    )


def report(out, destination):
    protocol = verify(out)
    rows, ledger, rounds = [], [], {}
    for schedule in load(out / "schedule.json"):
        run_id = f"{schedule['profile']}-r{schedule['rep']}"
        path = out / run_id
        for name, sha in load(path / "round-manifest.json").items():
            assert digest(path / name) == sha, name
        calls = [json.loads(line) for line in (path / "requests.jsonl").read_text().splitlines()]
        assert len({r["request_id"] for r in calls}) == len(calls)
        by_request = {r["request_id"]: r for r in calls}
        client = [*load(path / "cold.json")]
        for stage in ["serial", "concurrent"]:
            for file in (path / stage).glob("*.json"):
                client.extend(load(file))
        assert len(client) == 28
        for row in client:
            row.update(profile=schedule["profile"], repetition=schedule["rep"])
            row["server_record"] = by_request.get(row.get("request_id"), {})
            response = row.get("response", {})
            if row.get("request_id"):
                assert row["server_record"]["http_status"] == row["http_status"]
            allowed = {c["citation_id"] for c in response.get("citations", [])}
            mentions = set(re.findall(r"\[(E[A-Za-z0-9_-]+)\]", response.get("answer", "")))
            assert mentions <= allowed
            assert all(c.get("content") and c.get("locator") for c in response.get("citations", []))
            for retrieval in row["server_record"].get("retrieval", []):
                assert len(retrieval["diagnostics"]["rerank"].get("pairs", [])) <= 90
        matched = {r.get("request_id") for r in client}
        assert set(by_request) <= matched, "Unmatched server attempts must be accounted separately"
        rounds[run_id] = {
            "expected_requests": 28,
            "recorded_outputs": len(client),
            "actual_http_attempts": sum(r.get("attempted", True) for r in client),
            "server_records": len(calls),
            **load(path / "startup-metrics.json"),
            **load(path / "cold-total.json"),
            "cold_http_ms": client[0]["elapsed_ms"],
            "serial": latency(
                [
                    r["elapsed_ms"]
                    for r in client
                    if r["stage"] == "serial" and r.get("attempted", True)
                ]
            ),
            "concurrent": latency(
                [
                    r["elapsed_ms"]
                    for r in client
                    if r["stage"] == "concurrent" and r.get("attempted", True)
                ]
            ),
        }
        rows.extend(client)
        ledger.extend(calls)
    assert len(rows) == protocol["planned_http_requests"]
    identities = {(r["run_id"], r["stage"], r["case_id"], r["turn"]) for r in rows}
    assert len(identities) == len(rows)
    model_calls = [call for request in ledger for call in request["model_calls"]]
    assert len(model_calls) <= protocol["actual_model_attempt_cap"]
    by = {(r["profile"], r["repetition"], r["stage"], r["case_id"], r["turn"]): r for r in rows}
    differences, status_losses = [], []
    for r in rows:
        if r["profile"] != "optimized":
            continue
        base = by[("baseline", r["repetition"], r["stage"], r["case_id"], r["turn"])]
        key = {
            "repetition": r["repetition"],
            "stage": r["stage"],
            "case_id": r["case_id"],
            "turn": r["turn"],
        }
        if evidence_hash(r) != evidence_hash(base):
            differences.append(key)
        if base.get("response", {}).get("status") == "answered" and (
            r.get("response", {}).get("status") != "answered"
        ):
            status_losses.append(key)
    stats = {}
    for profile in ["baseline", "optimized"]:
        group = [r for r in rows if r["profile"] == profile]
        actual = [r for r in group if r.get("attempted", True)]
        result = {"all_http": latency([r["elapsed_ms"] for r in actual])}
        for stage in ["serial", "concurrent"]:
            subset = [r for r in actual if r["stage"] == stage]
            result[stage] = latency([r["elapsed_ms"] for r in subset])
        answerable = [
            r for r in actual if r["stage"] == "serial" and r.get("expected_status") == "answered"
        ]
        result["answerable_serial"] = latency([r["elapsed_ms"] for r in answerable])
        result["answerable_returned_answer"] = proportion(
            sum(r.get("response", {}).get("status") == "answered" for r in answerable),
            len(answerable),
        )
        result["http_expected"] = proportion(
            sum(r["http_status"] == r.get("expected_http", 200) for r in actual), len(actual)
        )
        result["unexpected_transport_failures"] = [
            {k: r.get(k) for k in ["run_id", "stage", "case_id", "turn", "http_status", "error"]}
            for r in actual
            if r["http_status"] != r.get("expected_http", 200)
        ]
        result["status_mismatches"] = [
            {k: r.get(k) for k in ["run_id", "stage", "case_id", "turn"]}
            for r in actual
            if r.get("expected_status")
            and r.get("response", {}).get("status") != r["expected_status"]
        ]
        result["http_codes"] = dict(Counter(str(r["http_status"]) for r in actual))
        retrievals = [v for r in group for v in r["server_record"].get("retrieval", [])]
        result["cache_hits"] = proportion(
            sum(v["diagnostics"]["retrieval_cache"]["hit"] for v in retrievals), len(retrievals)
        )
        result["retrieval_ms"] = latency([v["elapsed_ms"] for v in retrievals])
        result["runtime_queue_ms"] = latency(
            [v["diagnostics"]["timings_ms"].get("runtime_queue", 0) for v in retrievals]
        )
        calls = [c for r in group for c in r["server_record"].get("model_calls", [])]
        result["model_attempts"] = len(calls)
        result["failed_model_attempts"] = sum(c["status"] == "failed" for c in calls)
        usage = defaultdict(float)
        measurable = 0
        for call in calls:
            raw = (call.get("provider_metadata") or {}).get("usage")
            if isinstance(raw, dict):
                measurable += 1
                for key, value in raw.items():
                    if isinstance(value, (int, float)):
                        usage[key] += value
        result["provider_usage_sums_separate_fields"] = dict(usage)
        result["usage_coverage"] = proportion(measurable, len(calls))
        result["model_latency"] = latency([c["duration_ms"] for c in calls])
        result["model_cost_usd"] = None
        result["actual_rerank_pairs"] = sum(
            len(v["diagnostics"]["rerank"].get("pairs", [])) for v in retrievals
        )
        result["rerank_truncated_pairs"] = sum(
            p["would_truncate"] is True
            for v in retrievals
            for p in v["diagnostics"]["rerank"].get("pairs", [])
        )
        # Compare the exact same requests, classified by the optimized profile's cache result.
        for cache_hit, name in [
            (False, "paired_cache_miss_answerable"),
            (True, "paired_cache_hit_answerable"),
        ]:
            subset = []
            for r in answerable:
                other = by[("optimized", r["repetition"], r["stage"], r["case_id"], r["turn"])]
                rs = other["server_record"].get("retrieval", [])
                if rs and bool(rs[0]["diagnostics"]["retrieval_cache"]["hit"]) == cache_hit:
                    subset.append(r["elapsed_ms"])
            result[name] = latency(subset)
        stats[profile] = result
    # Check actual packed bodies with the same local tokenizer, after serving measurements finish.
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        protocol["retrieval_models"]["embedding"]["path"], local_files_only=True
    )
    index = {c["id"]: c for c in load(out / "snapshot/index.json")["chunks"]}
    max_tokens, max_chars = 0, 0
    for request in ledger:
        for retrieval in request["retrieval"]:
            text = "\n\n".join(
                f"[{e['citation_id']}] {index[e['chunk_id']]['heading']}\n{e['content']}"
                for e in retrieval["evidence"]
            )
            tokens = len(tokenizer.encode(text, add_special_tokens=False))
            max_tokens, max_chars = max(max_tokens, tokens), max(max_chars, len(text))
            assert tokens <= protocol["context_tokens"] and len(text) <= protocol["context_chars"]
            assert all(e["source"] in protocol["source_file_hashes"] for e in retrieval["evidence"])
    summary = {
        "protocol_sha256": digest(out / "protocol.json"),
        "rounds": rounds,
        "profiles": stats,
        "planned_http": 112,
        "recorded_outputs": len(rows),
        "actual_attempts": sum(r.get("attempted", True) for r in rows),
        "missing_dependency_attempts": sum(not r.get("attempted", True) for r in rows),
        "model_attempts": len(model_calls),
        "canonical_evidence_differences": differences,
        "answered_to_nonanswered_regressions": status_losses,
        "max_body_tokens": max_tokens,
        "max_body_chars": max_chars,
        "semantic_strict_accuracy": None,
        "independent_human_review": "pending",
        "test_holdout_read": False,
        "defaults_changed": False,
    }
    save(destination / "summary.json", summary)
    save(
        destination / "request-register.json",
        [
            {
                k: r.get(k)
                for k in [
                    "run_id",
                    "profile",
                    "repetition",
                    "stage",
                    "case_id",
                    "turn",
                    "request_id",
                    "http_status",
                    "elapsed_ms",
                    "case_sha256",
                ]
            }
            for r in rows
        ],
    )
    review = [
        {
            "run_id": r["run_id"],
            "stage": r["stage"],
            "case_id": r["case_id"],
            "turn": r["turn"],
            "case_sha256": r.get("case_sha256"),
            "response_sha256": canonical_hash(r.get("response", {})),
            "request_id": r.get("request_id"),
            "status": "pending",
            "reviewer": None,
            "correct": None,
            "citation_support": None,
            "conditions_complete": None,
            "reason": None,
        }
        for r in rows
        if r.get("response", {}).get("answer")
    ]
    save(destination / "human-review-template.json", review)
    b, o = stats["baseline"], stats["optimized"]
    lines = [
        "# 127篇本地知识库：完整HTTP问答场景优化",
        "",
        "**完整 /chat + BGE + ANN/BM25 + 上下文 + DeepSeek + 会话持久化。**",
        "",
        "本轮为22个开发性质场景：前端常用问题、术语变体、代码/条件/版本、多轮追问、",
        "重复提问、错误请求和拒答；每轮另含首次问答及4请求并发。ABBA共112次HTTP。",
        "当前前端仍是独立问题，多轮场景测试的是现有API能力。全部问题和答案均未入库。",
        "",
        "## 主指标：客户端发起HTTP至完整JSON响应",
        "",
        "|范围|基线P50/P95 ms|优化P50/P95 ms|每配置样本量|",
        "|---|---:|---:|---:|",
    ]
    for key, label in [
        ("serial", "暖启动完整串行流量（含预期错误）"),
        ("answerable_serial", "串行可回答请求"),
        ("concurrent", "四请求并发"),
        ("paired_cache_miss_answerable", "同题对照：优化组缓存未命中"),
        ("paired_cache_hit_answerable", "同题对照：优化组缓存命中"),
    ]:
        x, y = b[key], o[key]
        lines.append(
            f"|{label}|{x['p50_ms']:.1f} / {x['p95_ms']:.1f}|"
            f"{y['p50_ms']:.1f} / {y['p95_ms']:.1f}|{x['n']} / {y['n']}|"
        )
    lines.extend(
        [
            "",
            "## 启动与第一条完整答案",
            "",
            "|轮次|进程启动到health ms|第一问HTTP ms|进程启动到第一答 ms|",
            "|---|---:|---:|---:|",
        ]
    )
    for name, r in rounds.items():
        lines.append(
            f"|{name}|{r['spawn_to_health_ms']:.1f}|{r['cold_http_ms']:.1f}|"
            f"{r['spawn_through_first_answer_ms']:.1f}|"
        )
    lines.extend(
        [
            "",
            "预热把模型加载移到接流量前；必须同时看启动至首答，不能只看第一问变快。",
            "",
            "## 改动与账目",
            "",
            "- 基线：batch32、无检索结果缓存、懒加载；优化：batch16、LRU64、启动检索预热。",
            "- 候选30、union融合、Top5、正文1200token/4000字符、模型/来源/提示均固定。",
            "- 不缓存回答，每次有证据的请求都真实调用模型；LLM格式/引用重试全部入账。",
            "- 缓存按实际检索查询、过滤条件、TopK/策略及索引/配置代际隔离，返回深拷贝。",
            "- 三项改动作为整体服务配置比较，不把总收益归因于单一组件。",
            "- 测试客户端、本地网络、排队、计算、生成、序列化及完整响应时间均纳入HTTP主指标。",
            "- 运行目录准备/索引复制不计入进程启动；实际模型预热计入启动至health。",
            "- 四轮各有22个逻辑串行场景/23次请求、1次首次问答和4次并发请求。",
            "- 复问、多轮与重复运行不是独立新题；只作描述性比较，不作显著性或总体可靠性声明。",
            "- 当前8000服务保持运行，可能有本机其他活动及上游模型波动；逐轮数据保留。",
            "",
            "## 协议与质量核验",
            "",
            f"- 实际HTTP尝试{summary['actual_attempts']}/112；"
            f"依赖缺失{summary['missing_dependency_attempts']}。",
            f"- 实际模型尝试{len(model_calls)}，费用USD未知。",
            f"- 基线HTTP状态计数：{b['http_codes']}；优化：{o['http_codes']}。",
            f"- 可回答串行请求返回answered：基线{b['answerable_returned_answer']}；",
            f"  优化{o['answerable_returned_answer']}。返回answered不等于正确。",
            f"- 基线状态不符：{b['status_mismatches']}；优化：{o['status_mismatches']}。",
            f"- 配对实际交付证据差异：{differences}；answered回退：{status_losses}。",
            f"- 实际正文最大{max_tokens} token、{max_chars}字符，来源hash与引用ID机械核验通过。",
            f"- 重排输入超长对：基线{b['rerank_truncated_pairs']}，"
            f"优化{o['rerank_truncated_pairs']}；",
            "  这是重排阶段的实际输入截断诊断，不能因正文预算合格而忽略。",
            "- strict语义正确率保持null；具名独立人工审核模板保留pending，不以规则或AI自审代填。",
            "- 来源参考和rubric在运行前冻结，AI编写且待独立审核；来源与标签可能不充分。",
            "- 冻结的test/holdout未读取；未覆盖旧Grid或用户会话，主服务默认未切换。",
            "",
            "## 产物",
            "",
            f"- 原始运行：`{out}`。",
            "- summary.json含分母、逐轮结果、缓存命中、实际重排对及供应商原始usage字段汇总。",
            "- 每条HTTP响应和模型尝试由X-Request-ID与requests.jsonl绑定。",
            "- provider usage各字段分别相加，不假定cache token是否已包含在input中，不推算价格。",
            "- human-review-template.json绑定case和response hash，保持pending。",
            "- 复现：先用全新目录执行benchmark_runtime_e2e.py --phase freeze，再执行--phase run。",
            "- 本报告不把这些场景称作独立测试集，也不把工程测试通过数写成问答正确数。",
        ]
    )
    destination.mkdir(parents=True, exist_ok=True)
    with (destination / "README.md").open("x") as stream:
        stream.write("\n".join(lines) + "\n")
    save(
        destination / "manifest.json",
        {p.name: digest(p) for p in destination.iterdir() if p.is_file()},
    )
    return {
        "requests": len(rows),
        "model_attempts": len(model_calls),
        "profiles": stats,
        "evidence_differences": differences,
        "status_losses": status_losses,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    result = report(args.output.resolve(), args.report.resolve())
    record_operation(
        "审计完整HTTP真实场景优化结果",
        "核对全部请求、延迟、usage与实际交付证据",
        str(result),
        "语义正确率保持null，独立人工审核pending",
    )
    print(result)
