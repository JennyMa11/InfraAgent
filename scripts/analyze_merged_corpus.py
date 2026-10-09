"""Write measured comparisons and explicitly AI-authored qualitative answer observations."""

import json
from collections import Counter

from merge_corpus import OUT, ROOT
from operation_log import record_operation

from infra_rag.benchmarking import digest


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def main():
    official = OUT / "dev-20261002"
    coverage = OUT / "coverage-dev-20261002"
    retrieval = read_rows(official / "retrieval.jsonl")
    answers = read_rows(official / "answers.jsonl")
    extra = read_rows(coverage / "answers.jsonl")
    manifest = json.loads((OUT / "corpus-manifest.json").read_text())
    summary = json.loads((official / "summary.json").read_text())
    changes = []
    baseline = {r["id"]: r for r in retrieval if r["arm"] == "official_english"}
    for row in retrieval:
        old = baseline[row["id"]]
        if row["arm"] != "official_english" and row["answerable"]:
            if row["delivered"]["complete"] != old["delivered"]["complete"]:
                changes.append(
                    {
                        "id": row["id"],
                        "arm": row["arm"],
                        "query": row["query"],
                        "before": old["delivered"]["complete"],
                        "after": row["delivered"]["complete"],
                    }
                )
    findings = [
        {
            "review_key": "official-002-2:merged_english",
            "issue": "missed_adapter_condition",
            "note": "回答给出不能只按文本共享的结论，但仅解释cache_salt，未解释LoRA ID。"
            "引用本身支持租户隔离，却未回答两个适配器身份问题；增加作答数不能视为改善。",
        },
        {
            "review_key": "official-002-1:merged_bilingual",
            "issue": "incomplete_answer",
            "note": "只回答parent_hash和extra字段，未明确LoRA ID、多模态输入哈希、租户盐。",
        },
        {
            "review_key": "official-002-4:merged_bilingual",
            "issue": "version_support_unclear",
            "note": "LoRA身份的核心解释由中文社区材料补充，但相关缓存约束"
            "不是对v0.10.2的独立版本验证。",
        },
        {
            "review_key": "repo-053-1:merged_chinese",
            "issue": "source_simplification",
            "note": "引用原文把模型总参数简化为专家FFN参数和，回答重复该措辞；"
            "复核完整模型规模时需区分专家层参数与其他模块，核心稀疏激活解释有证据。",
        },
        {
            "review_key": "repo-053-2:merged_chinese",
            "issue": "source_simplification",
            "note": "同上，模型总参数与专家FFN参数的范围需明确；核心存储/激活规模差异有原文证据。",
        },
    ]
    review = []
    for row in answers:
        response = row["generation"]["response"]
        notes = [x for x in findings if x["review_key"] == row["review_key"]]
        review.append(
            {
                "review_key": row["review_key"],
                "method": "AI qualitative source audit",
                "status": response["status"],
                "expected_answerable": row["answerable"],
                "observation": notes
                or [
                    {
                        "note": "已对照题意、答案要点及所引片段；"
                        "拒答与答案正确性需区分，未形成独立人工评分。"
                    }
                ],
                "fact_correct": None,
            }
        )
    for row in extra:
        key = f"{row['question']['id']}:{row['arm']}"
        response = row["generation"]["response"]
        review.append(
            {
                "review_key": key,
                "method": "AI qualitative source audit",
                "status": response["status"],
                "observation": [x for x in findings if x["review_key"] == key]
                or [{"note": "官方原生中文组拒答；合并原生中文组核心回答与中文参考片段一致。"}],
                "fact_correct": None,
            }
        )
    report = {
        "method": "AI qualitative audit, not independent human scoring",
        "findings": findings,
        "rows": review,
        "evidence_delivery_changes": changes,
        "input_hashes": {
            str(p.relative_to(ROOT)): digest(p)
            for p in [
                official / "answers.jsonl",
                coverage / "answers.jsonl",
                official / "retrieval.jsonl",
            ]
        },
    }
    (OUT / "ai-answer-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    lines = [
        "# 合并索引结果",
        "",
        "已建立127来源的独立索引，保留原文路径、行号、来源URL与固定版本。",
        "删除18个跨文档完全重复片段，保留13,187片段；相似或不同版本正文保留。",
        "",
        "固定中文dev60，54道可回答题；每路候选30、并集重排、top5交付、"
        "1200token/4000字符预算，复用相同冻结英文译文。",
        "",
        "| 配置 | Recall@5 | MRR@10 | nDCG@10 | 完整证据题数 |",
        "|---|---:|---:|---:|---:|",
    ]
    for arm, result in summary.items():
        complete = sum(
            r["delivered"]["complete"] for r in retrieval if r["arm"] == arm and r["answerable"]
        )
        lines.append(
            f"| {arm} | {result['at_k']['5']['recall']:.2%} | "
            f"{result['at_k']['10']['mrr']:.4f} | "
            f"{result['at_k']['10']['ndcg']:.4f} | {int(complete)}/54 |"
        )
    lines.extend(
        [
            "",
            "合并英文组有1道完整证据改善、1道退步，总体交付数不变；"
            "双语直接拼接在本dev集明显退步，启动器默认保留英文翻译，允许显式切换。",
            "新增等价证据未穷尽标注，以上指标仅针对原官方gold。",
            "",
            "另外从旧仓库dev按仓库及题型预先固定6题，保持两组都使用原生中文查询，"
            "隔离语料扩充的影响。题目覆盖CUDA Warp访存、GQA/MQA、MoE。",
            "官方组6题均拒答；合并组6题均作答。AI逐题复核发现核心答案有中文正文支持；"
            "MoE两题重复了源文对模型总参数的简化措辞。这不是默认英文翻译流程的成绩，"
            "也不能由6题推出总体正确率。",
            "",
            "官方dev预先固定12题×3配置的回答样本，另加中文覆盖6题×2组，"
            "总计48条，生成错误0，JSON格式全部通过。",
        ]
    )
    for arm in summary:
        counts = Counter(r["generation"]["response"]["status"] for r in answers if r["arm"] == arm)
        lines.append(f"- {arm}：作答{counts['answered']}，拒答{counts['no_evidence']}。")
    lines.extend(["", "这些作答数不是正确率。AI复核的具体问题：", ""])
    lines.extend(f"- `{f['review_key']}`：{f['note']}" for f in findings)
    lines.extend(
        [
            "",
            "旧拒答题针对未提供环境与测量的私有P95，两种合并方式的抽样均未编造数值。",
            "另一次真实API提问“PagedAttention为什么允许KV Cache物理块不连续”返回证据不足；"
            "原始翻译、检索与拒答记录保存在chat-pagedattention-refusal.json，说明新增语料"
            "并未消除检索或生成的拒答问题。版本明确的缓存额外哈希问答冒烟通过。",
            "完整AI审阅及逐题证据变化见 `ai-answer-audit.json`；独立人工评分模板仍保留空值。",
            "",
            "结论：合并扩大了中文主题覆盖；原官方版本题没有获得整体检索提升。"
            "合并索引可独立使用，现有默认索引不切换，保留版本明确问题的来源核对。",
            "",
            f"索引：`{manifest['index_dir']}`。",
            "启动：`uv run --all-extras python scripts/merge_corpus.py --serve --port 8001`。",
            "原生中文：加 `--query-language none`；双语拼接：加 `--query-language bilingual`。",
            "",
            "验证：109项pytest、Ruff、构建通过；真实/chat冒烟的引用携带来源URL、版本与文件hash。",
        ]
    )
    (OUT / "comparison.md").write_text("\n".join(lines) + "\n")
    record_operation(
        "完成合并语料回答复核与中文覆盖检查",
        "区分新增覆盖、证据排名与实际回答质量",
        "dev60合并英文Recall@5 75.31%/完整40/54；双语48.77%/25/54；"
        "48条生成无错误；中文覆盖6题合并组均作答，保存AI逐题审阅与失败案例",
        "中文覆盖仅原生中文6题；LoRA遗漏与MoE源文简化已标记；未跑holdout，独立人工事实评分仍为空",
    )


if __name__ == "__main__":
    main()
