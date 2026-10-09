# 只读 Agent 端到端开发实验 v1

[评审与原因报告](review-report.md) · [测试矩阵](test-matrix.md) · [运行说明](../../docs/read-only-agent.md)

20条新 AI 编写的开发任务按正常/边界/工具失败/安全分为10/5/3/2。5份官方冻结快照经 hash 验证复制，另有3份明确标注的截断、冲突、指令注入控制资料。仅 `corpus/` 中的资料导入独立评测索引，case/gold/trace/审核不入库，未读取 holdout/test。

- `offline-20261003`：初次准备阶段工程运行，保留原代码快照。
- `offline-final-20261003`：最终执行代码的20题离线工具链及审计，决策仍为脚本。
- `live-20261003`：20题真实 DeepSeek + BGE 混合检索与重排，48次模型请求，无额外实模重跑。

每组保存运行前 freeze、全部预定 schedule、解析后的 cases、实际 traces、逐步产物、pending 审核、score 和请求计数。实模后仅进行机械分析与上下文重放；新增回归测试不改变已冻结代码、问题、原轨迹或审核 hash。

这些是开发用例及稀疏证据标签，不能作为独立确认或回答正确率。模型返回身份仅为诊断元数据，无法锁定 API 背后的权重。最终验证与文件 hash 清单见 `validation.json` 和 `artifacts-manifest.json`。
