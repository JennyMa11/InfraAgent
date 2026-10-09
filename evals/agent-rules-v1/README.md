# Agent 评分规则 v1 软件验证

[教程与指标口径](../../docs/agent-evaluation-rules.md) · [最终合成评分](run-20261003/score.json) · [文件审计](run-20261003/integrity-audit.json)

完成任务、工具、恢复、证据、安全、成本与拒答的离线规则评分。提供20条AI编排case和20条人工构造trace（10正常/5边界/3工具失败/2安全），以及20条pending审核模板。样例故意包含截断证据、超预算、无效重复、失败及假canary泄漏。

这次只验证评分程序，不运行Agent、浏览器或模型，不测真实任务成功率。引用支持、幻觉率和用户接受度在无独立审核/反馈时为空。输出中的合成数值不能用于模型优劣、生产安全或简历成绩。

204个测试、Ruff及构建通过；20条case/trace及schema通过校验；人工模板hash匹配，无批准审核。fixture引用文件hash及上一轮v6的71个归档文件和主实现hash保持。默认RAG流程、语料、gold与索引不变。

最终规则为软件迭代完成后的版本，不是新的模型实验预注册。初始流程产物及规则审计前版本保留在synthetic-fixture-20261003.json和run-20261003/setup-before-rule-audit；仅run-20261003/score.json与其快照对应最终版本。

```bash
uv run python scripts/score_agent_traces.py \
  --cases examples/eval-cases.jsonl --traces examples/eval-traces.jsonl \
  --reviews examples/eval-reviews.jsonl --require-complete \
  --output evals/agent-rules-v1/new-fixture-score.json
```

使用新输出路径；脚本不覆盖已有报告。`--require-reviewed`会拒绝这些pending模板。正式轨迹需要独立采集、冻结规则和来源，并重新生成对应审核hash；不会把旧RAG结果自动换算成Agent评分。
