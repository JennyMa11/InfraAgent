"""Summarize fixed dev ablations, preserve failures and record AI-only qualitative review."""

import json
from collections import Counter
from pathlib import Path

from operation_log import record_operation
from prepare_corpus_v2 import OUT

from infra_rag.benchmarking import digest


def rows(path):
    return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []


def main():
    run = OUT / "dev-v2"
    retrieval = rows(run / "rows.jsonl")
    answers = rows(run / "answers.jsonl")
    summary = json.loads((run / "summary.json").read_text())
    manifest = json.loads((OUT / "corpus-manifest.json").read_text())
    audit = rows(OUT / "ai-material-audit.jsonl")
    audit += rows(OUT / "ai-risk-audit.jsonl")
    known_risks = []
    for document in manifest["documents"]:
        source = Path(document["source"])
        lines = source.read_text().splitlines()
        for i, line in enumerate(lines):
            if "模型总参数量" in line and "专家" in line:
                known_risks.append(
                    {
                        "source": str(source),
                        "line": i + 1,
                        "quote": line,
                        "context": lines[max(0, i - 3) : i + 3],
                        "method": "AI qualitative source-scope review; pending human review",
                        "issue": "此处模型总参数量与专家FFN参数和的范围可能混用，"
                        "需审核其他模块是否包含。",
                        "action": "retain original; do not ingest suggested corrections",
                    }
                )
    (OUT / "known-risk-review.json").write_text(
        json.dumps(known_risks, ensure_ascii=False, indent=2)
    )
    observations = []
    for row in answers:
        response = row["generation"]["response"]
        issues = []
        answer = response["answer"] if response else ""
        if row["id"] == "official-002-1" and response and response["status"] == "answered":
            if not all(word in answer for word in ["LoRA", "多模态"]):
                issues.append("未完整说明LoRA身份、多模态输入与租户隔离盐的额外哈希。")
        if row["id"] == "official-002-2" and response and response["status"] == "answered":
            if (
                "LoRA" not in answer
                and "适配器身份" not in answer
                and "adapter" not in answer.lower()
            ):
                issues.append("只解释租户盐，未回答两个适配器身份为何必须区分。")
        if (
            row["id"] in {"repo-053-1", "repo-053-2"}
            and "模型总参数量" in answer
            and "专家" in answer
        ):
            issues.append("复述了源文模型总参数/专家FFN参数范围的简化，需核对完整模型范围。")
        if response and response["status"] == "no_evidence" and row["answerable"]:
            issues.append("对原标注可回答题拒答，需区分证据未交付与生成模型未使用证据。")
        observations.append(
            {
                "review_key": row["review_key"],
                "method": "AI qualitative source/answer audit, not independent scoring",
                "status": response["status"] if response else "error",
                "issues": issues,
                "fact_correct": None,
                "answer_record_sha256": digest(run / "answers.jsonl"),
            }
        )
    (OUT / "ai-answer-audit.json").write_text(
        json.dumps(observations, ensure_ascii=False, indent=2)
    )
    final = summary["official:final"]
    async_case = next(
        r
        for r in retrieval
        if r["dataset"] == "official" and r["arm"] == "final" and r["id"] == "official-026-4"
    )
    final_complete = int(
        sum(
            r["delivered"]["complete"]
            for r in retrieval
            if r["dataset"] == "official" and r["arm"] == "final" and r["answerable"]
        )
    )
    new_errors = [
        r
        for r in observations
        if r["review_key"].endswith(":final")
        and r["issues"]
        and any(k in r["issues"][0] for k in ["未完整", "只解释"])
    ]
    smoke = json.loads((OUT / "api-smoke.json").read_text())
    online_answer = smoke["chat"]["answer"]
    online_incomplete = not all(word in online_answer for word in ["LoRA", "多模态"])
    acceptance = {
        "official_recall_at_5": final["at_k"]["5"]["recall"] >= 0.7623,
        "official_complete_at_least_40": final_complete >= 40,
        "cuda_async_evidence_restored": bool(async_case["delivered"]["complete"]),
        "no_detected_core_omission": not new_errors and not online_incomplete,
        "independent_human_quality_score": None,
    }
    adoption = {
        "checks": acceptance,
        "promote_default": False,
        "reason": "default unchanged; qualitative failures and incomplete human scoring retained",
    }
    (OUT / "acceptance.json").write_text(json.dumps(adoption, ensure_ascii=False, indent=2))
    lines = [
        "# 预处理与分库检索结果",
        "",
        f"127篇冻结正文形成{manifest['retained_chunks']:,}片段；原文、版本、hash、行号与旧片段映射保留。",
        f"近重复候选{len(manifest['duplicate_audit']['near_candidates'])}组，只审计不删除；"
        f"明确同版本完全重复别名{len(manifest['duplicate_audit']['exact_aliases'])}组。",
        "",
        "## 固定官方dev60",
        "",
        "| 配置 | Recall@5 | MRR@10 | 完整证据交付 |",
        "|---|---:|---:|---:|",
    ]
    for key, value in summary.items():
        if not key.startswith("official:"):
            continue
        arm = key.split(":")[1]
        complete = int(
            sum(
                r["delivered"]["complete"]
                for r in retrieval
                if r["dataset"] == "official" and r["arm"] == arm and r["answerable"]
            )
        )
        lines.append(
            f"| {arm} | {value['at_k']['5']['recall']:.2%} | "
            f"{value['at_k']['10']['mrr']:.4f} | {complete}/54 |"
        )
    lines += [
        "",
        "global30/60表示全局每通道30/60候选；split表示每库每通道30候选；"
        "version追加版本优先，final追加按材料语言路由与重排。"
        "global60和split的最大候选预算相同，均为120。",
        "所有官方配置使用固定英文译文，final中文库使用原始中文；"
        "模型、正文来源与1200token/4000字符预算固定。"
        "分块粒度改变会影响chunk级Recall，原始证据完整交付更适合衡量前后覆盖。",
        "最终语言路由同时改变中文库候选和重排查询，不能由本实验单独归因于某一个因素。"
        "额外哈希题的直接官方证据已进入候选，但统一重排落到第11名（约0.676）；"
        "前列中文概述得分约0.907—0.993，且官方证据不在前10名，版本保留规则未触发。"
        "这是完整组合失效的具体案例，需要另测跨语言分数可比性与版本相关性资格。",
        "",
        "## 中文仓库dev50",
        "",
        "| 配置 | Recall@5 | MRR@10 | 完整证据交付 |",
        "|---|---:|---:|---:|",
    ]
    for key, value in summary.items():
        if not key.startswith("repository:"):
            continue
        arm = key.split(":")[1]
        complete = int(
            sum(
                r["delivered"]["complete"]
                for r in retrieval
                if r["dataset"] == "repository" and r["arm"] == arm
            )
        )
        lines.append(
            f"| {arm} | {value['at_k']['5']['recall']:.2%} | "
            f"{value['at_k']['10']['mrr']:.4f} | {complete}/50 |"
        )
    lines += [
        "",
        "仓库组全部使用原生中文，官方分库没有额外英文译文；"
        "属于翻译缺失时的回退条件，不应称为完整在线翻译路由的成绩。"
        "新增材料的等价证据未穷尽标注，固定来源gold不是所有正确答案的集合。",
        "",
        "## 材料与回答审阅",
        "",
        "主审计覆盖127文档，补充范围审计另存；共保留"
        f"{sum(len(r['accepted']['findings']) for r in audit)}条"
        "AI审计提示。审计基于抽样摘录，不是全文核验；逐字引用和行号验证仅确认来源，不能确认判断正确。",
        f"明确MoE参数范围疑点{len(known_risks)}处，原文保留，建议不入库。",
        f"生成样本{len(answers)}条，错误{sum(bool(r['generation']['error']) for r in answers)}条；"
        "事实评分为空，AI定性观察与独立人工模板分开。",
    ]
    for dataset, arm in dict.fromkeys((r["dataset"], r["arm"]) for r in answers):
        statuses = Counter(
            r["generation"]["response"]["status"] if r["generation"]["response"] else "error"
            for r in answers
            if r["dataset"] == dataset and r["arm"] == arm
        )
        lines.append(f"- {dataset}/{arm}：{dict(statuses)}；作答数不是正确率。")
    for observation in observations:
        if observation["issues"]:
            lines.append(f"- `{observation['review_key']}`：{'；'.join(observation['issues'])}")
    lines += [
        "",
        "真实API完成/search、/chat、元数据和冻结来源管理检查。"
        "在线缓存额外哈希冒烟仍只解释通用哈希结构，漏掉具体额外项，保留原始响应于api-smoke.json。",
        "",
        "## 采用检查",
        "",
    ]
    lines.extend(f"- {name}：{value}" for name, value in acceptance.items())
    lines += [
        "",
        "现有服务与默认索引不切换。可独立启动实验配置，保留失败结果；"
        "达到检索门槛也不能替代回答正确性审核。",
        "",
        "复现命令、接口行为和限制见README.md；原始排名及回答见dev-v2目录。"
        "冻结的实现位于dev-v2/implementation，后续仅context.py的Ruff格式变化，AST保持一致。",
        "验证：116项pytest、Ruff、构建和真实API通过；未运行holdout或test。",
    ]
    (OUT / "comparison.md").write_text("\n".join(lines) + "\n")
    record_operation(
        "实现预处理、分库召回、版本优先及中文dev对照",
        "修复语料混合后的证据竞争，区分清理与检索策略效果",
        f"127来源/{manifest['retained_chunks']}片段；官方最终Recall@5 "
        f"{final['at_k']['5']['recall']:.2%}，完整{final_complete}/54；"
        f"{len(answers)}条回答；报告evals/merged-corpus-v2/comparison.md",
        "AI审计未独立审核、稀疏gold及粒度限制；在线额外哈希回答遗漏保留；默认未切换",
    )


if __name__ == "__main__":
    main()
