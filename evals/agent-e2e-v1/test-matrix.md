# 规则—测试覆盖矩阵

规则来自 [AGENT.md](../../AGENT.md) 与 [详细评分契约](../../docs/agent-evaluation-rules.md)。此表列软件测试的判断依据，不能替代独立事实审核。

| 范围 | 核心测试与断言 |
|---|---|
| 必需目标与总分 | `test_required_goal_failure_zeroes_final_score_but_keeps_diagnostic`：目标失败最终零分，保留原始诊断分；`test_known_failure_overrides_pending_human_goal`：已知失败优先。 |
| 空值与 coverage | 默认语义待审、缺权重维度不重归一化、零分母 null、无政策/工具契约/缓存记录不报告完美分。 |
| 证据 AND/OR | `test_and_or_candidate_requirements` 与 `test_partial_alternatives_do_not_combine_into_complete_delivery`：别名 OR、必要项 AND、完整替代组 OR。 |
| 来源与截断 | 独立改变 source/hash/content/locator 均不算完整交付；候选/合法 ID 不能替代交付正文；实际来源变更后工具失败关闭。 |
| 单轮与多轮 | 排名必须属于同轮候选，来源读取可增加排名外证据；实际轮次/累计候选分别保存；记录重放验证最终交付队列。 |
| 引用和事实 | 无效 ID 即使被支持标签批准也失败；事实正确但引用不支持不能完成；无事实主张时幻觉率 null。 |
| 独立审核 | LLM judge、过期 case/trace hash、不完整主张清单、缺引用边判断拒绝；真实用户接受必须有 feedback_id。 |
| 工具与恢复 | 首次真实工具故障恢复；持续失败与空成功响应不算恢复；同逻辑操作计一次分母，重试保留错误次数与资源。 |
| 阻断与安全 | 未执行的 blocked 不计实际调用；阻断后执行取消阻断；任意路径、shell、未知参数/工具类型被阻断；假凭据导出脱敏。 |
| 预算与超时 | 单题工具/模型上限、共享请求上限、末轮不得再调工具；信号中断本地慢工具与模型，并保留失败尝试；截止异常不被 OSError 捕获吞掉。 |
| 格式与生成故障 | 截断 JSON 保留全部 usage 且不伪造答案；拒答携带事实清单需修正；`action=refused` 不静默当 final。 |
| 成本与缓存 | 非有限/负数/布尔 token 值拒绝；缓存独立输入计入总量，包含缓存的总字段不重复累加；费用未知 null。 |
| 调度与 CLI | 整组配置漏跑由 manifest 检出；未预定 trace 拒绝；CLI 成功评分、pending 审核阻断、已有结果不覆盖。 |
| 完整执行 | 20题实际索引/工具链、全部调度、逐步 artifact hash、schema、配置及源文件冻结；脚本决策与真实模型明确区分。 |

测试位于 `tests/test_agent_evaluation.py`、`tests/test_agent.py`、`tests/test_agent_e2e.py`。现有服务、持久化、过滤、缓存和模型客户端继续运行完整回归。

实模三个已知失败由离线回归固定行为：截断输出不算有效最终答案；拒答携带事实清单不能进入通过状态；最后一轮仍请求工具时阻断并终止。测试通过证明实现按契约处理失败，不证明模型已经避免这些失败。

未自动覆盖：来源事实真伪、条件强度、主张清单完整性、用户实际接受、真实秘密全覆盖、生产并发/浏览器/运维执行和 API 权重的长期可复现性。上述维度保持待审或不适用。
