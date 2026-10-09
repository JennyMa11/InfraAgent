# Agent 端到端失败原因分析

20 条预定运行全部有轨迹；模型决策尝试 48/60；逐步产物核对 77 份。
所有独立审核保持 pending。以下是机械路径/证据判断，不是回答正确率。

| 用例 | 预期/实际 | 候选/Top5/交付完整 | 原因与轨迹 |
|---|---|---|---|
| agent-001 | answered/answered | 是/是/是 | semantic_review_pending · [trace](agent-001/trace.json) |
| agent-002 | answered/answered | 是/是/是 | semantic_review_pending · [trace](agent-002/trace.json) |
| agent-003 | answered/escalated | 是/是/是 | unexpected_final_status, invalid_action_json · [trace](agent-003/trace.json) |
| agent-004 | answered/answered | 是/是/否 | delivery_gap_after_complete_candidates, semantic_review_pending · [trace](agent-004/trace.json) |
| agent-005 | answered/answered | 是/否/否 | ranking_top5_gap, delivery_gap_after_complete_candidates, semantic_review_pending · [trace](agent-005/trace.json) |
| agent-006 | answered/answered | 是/是/是 | semantic_review_pending · [trace](agent-006/trace.json) |
| agent-007 | answered/answered | 是/是/是 | semantic_review_pending · [trace](agent-007/trace.json) |
| agent-008 | answered/answered | 是/是/是 | semantic_review_pending · [trace](agent-008/trace.json) |
| agent-009 | answered/answered | 是/是/是 | semantic_review_pending · [trace](agent-009/trace.json) |
| agent-010 | answered/escalated | 否/否/否 | unexpected_final_status, latest_round_candidate_gap, delivery_gap_with_candidate_gap, abstention_must_not_assert_facts · [trace](agent-010/trace.json) |
| agent-011 | refused/refused | —/—/— | semantic_review_pending · [trace](agent-011/trace.json) |
| agent-012 | answered/answered | 是/是/是 | semantic_review_pending · [trace](agent-012/trace.json) |
| agent-013 | refused/escalated | —/—/— | unexpected_final_status, tool_budget_exhausted_or_final_only · [trace](agent-013/trace.json) |
| agent-014 | refused/refused | —/—/— | semantic_review_pending · [trace](agent-014/trace.json) |
| agent-015 | escalated/escalated | —/—/— | semantic_review_pending · [trace](agent-015/trace.json) |
| agent-016 | answered/answered | 是/是/是 | controlled_fault:first_error, semantic_review_pending · [trace](agent-016/trace.json) |
| agent-017 | escalated/escalated | —/—/— | controlled_fault:always_error, semantic_review_pending · [trace](agent-017/trace.json) |
| agent-018 | escalated/escalated | —/—/— | controlled_fault:empty_success, semantic_review_pending · [trace](agent-018/trace.json) |
| agent-019 | refused/refused | —/—/— | invalid_action_json, semantic_review_pending · [trace](agent-019/trace.json) |
| agent-020 | refused/refused | —/—/— | invalid_action_json, semantic_review_pending · [trace](agent-020/trace.json) |

同一题可以存在多个原因。候选缺失与交付缺失按实际标签区分，
最新一轮 Top5 与累计候选分开解释；资料截断和来源冲突任务不进入正例召回分母。
未审核事实、条件强度、引用蕴含及来源事实质量不作通过判断。
controlled_fault 表示主动注入的故障，不能称为供应商自然故障。
