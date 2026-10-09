# 预算消融与来源隔离 v6

已完成四因素全交叉及独立来源隔离：3960条主回放、220条隔离对照、100条新生成/100次API调用、46条交错打包计时。

[冻结计划](experiment-plan.md) · [审阅结论](run-20261003/review-report.md) · [全部组合](run-20261003/execution-report.md) · [逐案观察](run-20261003/answer-observations.md) · [完整性审计](run-20261003/integrity-audit.json)

冻结组合B-k8-l0-p1-n0：Top1保护、最多8段、无长度惩罚、无旧邻接弱先验。官方交付45/54、仓库41/50，对照43/54、40/50；冻结候选召回仍46/54、42/50。来源隔离3片段维持45/54、41/50，两类已知错误未在固定两题各两次Q1生成中复述。单因素主检验Holm p均1；这是多轮dev的证据交付结果，不是回答正确率或独立确认。默认global30未改，holdout/test未读取，独立人工审核pending。

181测试、Ruff、构建通过；660个旧上下文精确复现，34559条原文定位核对，127源文件hash保持。

实现：src/infra_rag/budget_ablation.py、source_quarantine.py；驱动及诊断如下。

```bash
HF_HUB_OFFLINE=1 uv run --all-extras python scripts/benchmark_ablation_v6.py
uv run python scripts/analyze_ablation_v6.py
HF_HUB_OFFLINE=1 uv run --all-extras python scripts/analyze_ablation_residuals_v6.py
uv run --extra dev pytest -q
uv run --extra dev ruff check src tests scripts
uv build
```

驱动支持原路径恢复且拒绝冻结输入/实现hash变化；恢复时已完成的生成不会重复调用，打包计时也不重复。完整产物SHA见run-20261003/artifacts-manifest.json。只读诊断脚本另存hash，不能用于主结果后修改选择规则。

下一轮优先验证已有补召回候选搭配固定打包，再单独验证有条件邻接、预算内交换选择和来源审核。残余失败16题缺完整标注候选、2题在预算内未选齐；稀疏标签仍可能漏掉合法替代证据。
