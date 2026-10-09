# 只读研究 Agent 与端到端验证

Agent 在本仓库选择工具并执行检索、来源读取和最终回答。入口独立于 `/chat`，原有问答服务与默认检索配置未切换。实现为 `src/infra_rag/agent.py`，通过现有客户端传输 JSON 动作，不使用供应商原生 tool-use 协议。

```bash
# 全局参数在子命令前；索引需已导入对应资料，输出目录必须不存在。
uv run infra-rag --data-dir data/agent-e2e-v1/live --backend bge --rerank \
  agent 'vLLM APC 的性能收益有什么条件？' --domain infra \
  --output-dir evals/agent-e2e-v1/new-interactive-run

# 固定20条开发任务：离线先验证工程路径，再单独执行真实模型。
uv run python scripts/benchmark_agent_e2e.py --output evals/agent-e2e-v1/new-offline-run
uv run python scripts/benchmark_agent_e2e.py --live --output evals/agent-e2e-v1/new-live-run
uv run python scripts/analyze_agent_e2e.py evals/agent-e2e-v1/new-live-run
```

工具仅开放 `search(query)` 和 `read_parent(parent_id)`。父块必须由本轮检索登记，且来自已索引来源；读取时检查源文件 SHA256。模型不能指定文件路径、执行 shell、写入、删除或访问网页。未知工具和非法参数在执行前记录为 blocked，不计为实际调用。评测故障注入只通过运行器显式配置，不由模型控制。

每题上限为 3 次模型请求、4 次实际工具调用、180 秒；每个失败工具操作最多重试一次。最后一次模型请求只允许最终动作，重试及格式修正均计入同一预算。批量运行共享 60 次模型请求上限，无额外预热调用。当前硬截止使用主线程信号，适用于 macOS/Linux 串行 CLI/批处理，不提供线程内或 Windows 执行保证。

最终动作使用 `action=final`，`status` 为 answered/refused/escalated。answered 必须提交事实清单及有效证据边；拒答和转人工不能附带事实清单。该结构只保证可审核性，独立人工仍需判断是否遗漏事实、是否真的有支持以及来源是否正确。不能把协议通过等同于答案正确。

逐次保存完整模型文本、usage 元数据、实际工具返回、参数、状态、时间和 artifact hash。候选/排序按检索轮次保留；通用评分字段表示最新一轮搜索，累计候选另存。最终交付正文表示模型实际获得的累计上下文，不能用各轮工具返回的并集冒充。

上下文预算计证据正文及引用/定位头，使用检索编码器的 token 计数或离线字符计数；它不是生成模型的总输入上限，JSON 字段、来源元数据和任务文字另有开销。模型 usage 汇总包含缓存输入；独立缓存计数字段与已经包含缓存的总字段分别处理，避免漏计或重复计。协议依据见 [缓存输入定义](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) 与 [DeepSeek 兼容接口](https://api-docs.deepseek.com/guides/anthropic_api/)。未获得账单费用时 USD 成本为 null；本地工具外部费用为零，不包含机器算力成本。

真实凭据仅用于已有模型客户端认证，不进入用例和提示。导出前过滤当前客户端凭据；工具无法读取 `.env`。日志不保存上游原始错误体。安全测试只能使用假凭据/canary，不代表所有秘密类型或攻防路径均被覆盖。

评测资料分为已冻结的官方快照和明确标注的控制资料。问题、gold、评分、轨迹与审核文件不入库。离线决策是脚本，不代表模型的计划、事实或拒答能力；真实模型任务、主动故障注入和机械回放分别报告。

评分规则 v2 修正必需目标失败仍有最终加权分、错误来源定位仍算完整交付、排名 ID 不属于候选三项缺陷，并增加可选 `--manifest` 预定清单校验。旧 v1 报告及实模快照保持原口径，审核绑定原 case/trace hash。

结果与限制见 [20题端到端报告](../evals/agent-e2e-v1/review-report.md)，测试覆盖见 [规则—测试矩阵](../evals/agent-e2e-v1/test-matrix.md)。
