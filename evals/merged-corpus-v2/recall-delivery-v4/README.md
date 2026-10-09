# 召回与交付 v4

已实现并完成三个方向的独立开发实验：固定预算Top8、保留原候选的身份上下文子问题补召回、原文标题/来源/前文的搜索视图增强。共7组×110题，主实验源码、dev标签、译文、条件输出和模型快照冻结。

[预注册计划](experiment-plan.md) · [执行报告](run-20261002/execution-report.md) · [生成观察](run-20261002/answer-observations.md) · [审计](run-20261002/execution-audit.json)

## 结论

官方完整候选/交付：B5 46/43，B8 46/44，D5 48/43，Q5 47/44，L5 47/44，E5 47/43，LE5 46/41（分母54）。仓库交付均40/50。Q5按开发数值门槛和冻结并列顺序胜出，但所有官方主检验置信区间跨0、Holm p=1；不能宣称增益确证。

本轮完成770条检索、46条生成和46条延迟记录。Q5生成出现一条经实际引用及NVIDIA一手文档核实的过强必要条件，因此未通过事实门槛，停止确认评测。该题B5/Q5上下文完全相同，单次答案差异不能归因于检索。本轮未读取holdout/test、未事后换胜出配置、默认global30保持不变。独立人工事实审核pending。

实现位于src/infra_rag/recall_experiments.py；驱动脚本为scripts/benchmark_recall_v4.py；报告脚本为scripts/analyze_recall_v4.py。155个测试、Ruff、构建通过。

## 执行入口

```bash
HF_HUB_OFFLINE=1 uv run --all-extras python scripts/benchmark_recall_v4.py --phase all
# 完成并冻结实际答案审阅后，执行协议中的确认门槛；本轮在读确认题之前退出。
HF_HUB_OFFLINE=1 uv run --all-extras python scripts/benchmark_recall_v4.py --phase confirmation
uv run python scripts/analyze_recall_v4.py evals/merged-corpus-v2/recall-delivery-v4/run-20261002
```

all只执行dev阶段，不自动读取确认集。结果缓存绑定精确query/body/model，主代码改变需新协议与独立run。检索增强索引为独立data/merged-corpus-v4/e624132ff5b8a3d6；它不包含benchmark问题或生成答案，搜索视图不用于回答或引用。完整证据指标基于AI编写稀疏来源标签，不等同于事实正确率。
