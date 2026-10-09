"""Audit frozen dev evidence failures; do not change relevance or human answer labels."""

import json
from collections import Counter

from operation_log import ROOT, record_operation

from infra_rag.benchmarking import canonical_hash, digest, span_coverage
from infra_rag.offline_evaluation import enrich_questions

NOTES = {
    "official-002-2": "召回盐隔离段落，却遗漏缓存键中的LoRA IDs；回答转为解释cache_salt。",
    ("official-002-4"): (
        "只交付LoRA支持证据；缓存哈希中的LoRA身份未召回，回答从适配器ID推导缓存身份。"
    ),
    ("official-005-4"): (
        "未召回指定conserving_memory证据，但o"
        "ptimization的代码示例也含tensor_pa"
        "rallel_size；需审查等价证据。"
    ),
    ("official-008-4"): (
        "prefill/decode解耦的否定句与跨项目作用证"
        "据均未召回；译文保留泛指阶段，缺具体prefill/d"
        "ecode。"
    ),
    ("official-010-3"): (
        "PR修复段落BM25第7、重排第10；交付的是Issue旧缓存键问题，回答漏掉修复字段mm_hashes。"
    ),
    ("official-010-4"): (
        "Issue指定长段落未召回，但交付了Issue标题和PR修复段落；需审查短标题能否作为替代证据。"
    ),
    ("official-012-4"): (
        "queue-req诊断段落BM25第2却跌出重排前10；回答引用队列非空的诊断条件，漏掉客户端提交慢。"
    ),
    "official-016-1": "policy列表所在代码块BM25第2、重排第7；查询‘该路由器’缺少明确路由器名称。",
    ("official-017-3"): (
        "temperature表格BM25第1、重排第6；生成引用temperature=0示例，未直接引用贪心语义说明。"
    ),
    ("official-026-3"): (
        "未锁页内存下Async可能同步的短例外句未召回；只交付泛化异步说明，回答缺少关键条件。"
    ),
    ("official-030-1"): (
        "串行host/并行device段落BM25第2、重排第7；回答转为解释异步调用，未回答工作划分。"
    ),
    "official-030-2": "同一工作划分段落BM25第2、重排第8；生成拒答。",
    "official-030-3": "同一工作划分段落BM25第3，却跌出重排前10；否定式问题引向统一内存材料。",
    "official-030-4": "同一工作划分段落BM25第3，却跌出重排前10；只交付利用率总论和统一内存材料。",
}


def main():
    dataset = ROOT / "evals/infra-official-v1-reviewed"
    results = dataset / "results"
    run = results / "dev-deepseek-optimized-20261001"
    rows = [json.loads(line) for line in (run / "rows.jsonl").read_text().splitlines()]
    selected = [r for r in rows if r["variant"] == "hybrid_rerank" and r["answerable"]]
    protocol_path = results / "protocol-deepseek-optimized-20261001/protocol.json"
    protocol = json.loads(protocol_path.read_text())
    corpus = json.loads((dataset / "corpus-manifest.json").read_text())
    index_path = (
        ROOT
        / "data/official-evals/indexes"
        / canonical_hash([corpus["corpus_sha256"], protocol["settings"]])[:24]
        / "index.json"
    )
    chunks = {c["id"]: c for c in json.loads(index_path.read_text())["chunks"]}
    questions = {
        q["id"]: q
        for q in enrich_questions(json.loads((dataset / "dev.json").read_text()), dataset)
    }
    failures = []
    top10_complete = 0
    top10_gains, top10_losses = [], []
    for row in selected:
        top10 = span_coverage(row["ranking_context"]["evidence"], questions[row["id"]])
        top10_complete += int(top10["complete"])
        if top10["complete"] > row["delivered"]["complete"]:
            top10_gains.append(row["id"])
        if top10["complete"] < row["delivered"]["complete"]:
            top10_losses.append(row["id"])
        if row["delivered"]["complete"]:
            continue
        stage = (
            "candidate_incomplete"
            if not row["candidate_complete"]
            else "rerank_top5_incomplete"
            if not row["at_k"]["5"]["complete_evidence_hit"]
            else "context_loss"
        )
        gold = []
        for cid in row["resolved_gold"]["relevant"]:
            chunk = chunks[cid]
            ranks = {
                channel: next(
                    (hit["rank"] for hit in values["ranking"] if hit["chunk_id"] == cid), None
                )
                for channel, values in row["diagnostics"]["channels"].items()
            }
            gold.append(
                {
                    "chunk_id": cid,
                    "source": chunk["source"],
                    "locator": chunk["locator"],
                    "content": chunk["content"],
                    "channel_ranks": ranks,
                    "rerank_top10_rank": next(
                        (i + 1 for i, hit in enumerate(row["retrieved"]) if hit == cid), None
                    ),
                }
            )
        failures.append(
            {
                "id": row["id"],
                "query": row["query"],
                "question_type": row["question_type"],
                "stage": stage,
                "coverage": row["delivered"]["coverage"],
                "english_query": row["diagnostics"]["query_expansion"]["actual"],
                "candidate_complete": row["candidate_complete"],
                "top10_complete": row["at_k"]["10"]["complete_evidence_hit"],
                "generation_status": row["generation"]["response"]["status"],
                "gold": gold,
                "note": NOTES[row["id"]],
                "interpretation": "qualitative diagnostic; not independent human scoring",
            }
        )
    assert len(selected) == 54 and len(failures) == 14
    assert set(NOTES) == {r["id"] for r in failures}
    summary = {
        "source_rows_sha256": digest(run / "rows.jsonl"),
        "source_protocol_sha256": digest(protocol_path),
        "scope": "fixed dev, hybrid_rerank, answerable only; negative queries excluded",
        "answerable": len(selected),
        "failures": len(failures),
        "funnel": {
            "candidate_complete": sum(int(r["candidate_complete"]) for r in selected),
            "top5_complete": sum(int(r["at_k"]["5"]["complete_evidence_hit"]) for r in selected),
            "delivered_complete": sum(int(r["delivered"]["complete"]) for r in selected),
        },
        "stages": dict(Counter(r["stage"] for r in failures)),
        "by_type": dict(Counter(r["question_type"] for r in failures)),
        "failed_but_answered": sum(r["generation_status"] == "answered" for r in failures),
        "reranker_truncated_pairs_in_failures": sum(
            sum(p["would_truncate"] for p in r["diagnostics"]["rerank"]["pairs"])
            for r in selected
            if not r["delivered"]["complete"]
        ),
        "stored_top10_context_check": {
            "complete": top10_complete,
            "gains": top10_gains,
            "losses": top10_losses,
            "note": "existing packed top10 contexts only; not a new generation evaluation",
        },
        "cases": failures,
        "fact_correct": None,
    }
    (results / "retrieval-failures-deepseek-optimized.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2)
    )
    lines = [
        "# 优化后检索失败逐题分析",
        "",
        "范围：固定dev60的hybrid_rerank主配置，54道可答题；6道不可答题不计失败。",
        "按原标注证据完整性交付定义失败，不等于人工判定回答错误。",
        "",
        "漏斗：54题 → 候选证据完整48题 → 重排前5完整39题 → 实际交付完整40题。",
        "邻居扩展补回1题；余下14题：候选缺证据6题、完整候选被重排挤出前5共8题。",
        "没有观察到‘前5标注证据完整、仅因交付预算丢失完整性’的案例；失败候选的重排输入截断为0。",
        "",
        "| 题号 | 题型 | 最早失败阶段 | 覆盖 | 生成状态 | 诊断 |",
        "|---|---|---|---:|---|---|",
    ]
    for row in failures:
        lines.append(
            f"| {row[('id')]} | {row[('question_type')]} | {row[('stage')]} | {
                row[('coverage')]:.0%} | {row[('generation_status')]} | {row[('note')]} |"
        )
    lines.extend(
        [
            "",
            "14道失败题涉及9个scenario，CUDA工作划分的4题共享同一gold段落；不能当作14个独立问题。",
            "10道仍回答、4道拒答。特别应复核002-2、010-3、012-4、026-3、030-1的答案要点遗漏；",
            "005-4、010-4存在潜在等价/部分替代证据，017-3引用了示例但示例未直接解释贪心语义。",
            "这些是诊断意见，未写入人工评分，也未放宽原始qrels。",
            "",
            "主要原因的证据与推断：",
            "",
            (
                "- 重排：policy代码块BM25第2→第7，tem"
                "perature表格第1→第6，CUDA划分段落第2→"
                "第7/8；这是可直接观察的排序损失。"
            ),
            (
                "- 召回：LoRA缓存哈希、Async的未锁页例外、P"
                "D分离否定句不在每路前30；短句/同义词/缺省实体是待"
                "验证原因。"
            ),
            "- 多跳：6题只完整交付1题；5道失败涉及不同资料链，单次整句检索容易只覆盖一个子问题。",
            (
                "- 上下文：当前重排使用chunk正文，heading"
                "_context关闭，未把文件/项目/版本/PR身份统"
                "一送入重排；"
            ),
            "  这能解释部分定位歧义的可能来源，但不能在消融之前断言已证实。",
            "",
            f"已保存top10上下文检查：完整覆盖{
                top10_complete
            }/54，相比top5交付多4题，无退步，新增题号{(', ').join(top10_gains)}。",
            "PR21611关键段落虽然重排第10，top10打包也没补齐；因此扩大K不能解决所有失败。",
            "上述仅为既有上下文离线检查，尚未用top10重新调用模型，不是新的回答质量成绩。",
            "",
            "后续优先验证：",
            "",
            (
                "1. 对候选完整的8题，优先测标题/项目/版本元信息进"
                "入重排、代码表格保留，以及同一相关文档的近邻扩展。"
            ),
            "2. 测top10或按相关文档分散选择种子，比较证据覆盖、噪声和token成本；不直接增大预算。",
            "3. 多跳问题按子问题分别检索后合并；每条子查询只依赖原题，禁止读取答案补词。",
            "4. 保留当前标注，另建等价证据人工复核队列；单独评审漏条件/错误推导/答非所问。",
            "5. 后续可测更适合中英技术资料的embedding，但本轮证据不足以归因于embedding单一因素。",
            "",
            (
                "输入、译文、每路gold排名、gold正文、源文件定位"
                "见同名JSON；未发起模型调用或修改运行配置。"
            ),
        ]
    )
    (results / "retrieval-failures-deepseek-optimized.md").write_text("\n".join(lines) + "\n")
    record_operation(
        "优化后检索失败逐题归因",
        "区分召回、重排与交付问题，避免把拒答或标注未命中直接当作模型错误",
        (
            "固定dev主配置14/54不完整：候选缺证据6、重排前"
            "5损失8；10仍回答，4拒答；top10既有上下文44"
            "/54，新增4且无退步。逐题14案例与源定位JSON/"
            "报告已保存。"
        ),
        (
            "稀疏gold与潜在等价证据仍需独立审核；推测性根因未做"
            "新消融，无事实评分、无配置更改、未跑holdout。"
        ),
    )
    print(
        json.dumps(
            {key: value for key, value in summary.items() if key != "cases"}, ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()
