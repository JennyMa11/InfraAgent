# 预算覆盖与引用支持 v5

已完成两个独立单元：冻结B5/Q5候选上的四种预算打包，以及同上下文的原提示/条件强度提示、两次重复和引用支持核验。

[预注册计划](experiment-plan.md) · [执行报告](run-20261003/execution-report.md) · [逐案观察](run-20261003/answer-observations.md) · [完整性审计](run-20261003/execution-audit.json)

## 结果

880条冻结回放、92条新生成、78条新答案核验、4条旧答案核验探针、46条打包延迟记录完成。实际API调用174次。两池R8/C8官方交付均38/39（分母54），原T5为43/44；仓库R/C均37/50，原T5为40/50。没有新配置过推进门槛，生成使用冻结B-T5。

G0/G1各46条均格式有效。G1两次均拒答缺缓存键前提的样本，G0一次被核验拦截、另一次自身拒答；这不是独立事实正确率增益。CUDA过强必要条件、MoE整模范围风险在两提示中均复述，核验器全部放过；支持判定不等于事实正确。

169个测试、Ruff、构建通过。330条T5/T8原上下文逐题精确复现，7644条交付原文/定位检查通过；原候选、排名、重排分数未改，holdout/test未读取，默认global30不变。独立人工事实审核pending。

## 实现与复现

- src/infra_rag/budget_evidence.py：预算、词面覆盖与同来源父段邻接弱先验。
- src/infra_rag/claim_guard.py：实验性条件强度提示、实际引用核验、拒答后处理；不接入默认回答流程。
- scripts/benchmark_budget_v5.py：冻结与执行驱动。
- scripts/analyze_budget_v5.py：只读审计与失败分解。

```bash
HF_HUB_OFFLINE=1 uv run --all-extras python scripts/benchmark_budget_v5.py
uv run python scripts/analyze_budget_v5.py evals/merged-corpus-v2/budget-support-v5/run-20261003
uv run --extra dev pytest -q
```

正式运行的tokenizer采用冻结sentence_bert_config的大小写选项。准备阶段两次校验分别拦截token计数不一致和遗漏仓库生成ID；修正前均未调用生成API。前者归档setup-aborted-tokenizer-20261003；后者归档generation-aborted-20261003，880条缓存字节一致地复用，打包函数AST及模块hash不变，见retrieval-import.json。

下一轮分别消融8段硬上限、成本奖励、原Top5保护与邻接弱先验；来源风险隔离/修订和独立来源正负例核验须另立协议。当前结果不支持默认切换。
