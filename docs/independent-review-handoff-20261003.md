# 原RAG改进的独立审核交接

用户已确认尚未审核。本轮开发质量、预算与暖延迟已通过，但最终采用、确认及回答语义指标仍待真实独立人工审核；当前不切换默认配置。

可使用[110份最新待审证据材料](../evals/merged-corpus-v2/budget-search-v8/evidence-review-handoff-20261004/evidence-review-pending.jsonl)逐题核对。每份包含原冻结dev问题、AI编写的预期事实/标签、直接记录的实际候选/排名/交付正文、source文件SHA256，以及case/trace hash；与未变渲染器及冻结质量逐题核对。旧v8c重建版本材料保留供追溯，最新版本绑定v8d完整实际账目。

审核范围：原来源真实性及事实范围，版本/硬件/数量/单位，gold必要与充分条件，等价证据/来源别名，实际正文是否覆盖全部要求及是否矛盾。来源写过不等于事实正确，合法引用ID也不等于支持；稀疏旧标签不能排除其他合法答案。

模板所有审核人、时间、理由、rubric保持null，状态pending，独立审核覆盖0/110；没有指定虚构负责人。审核者应把真实结果写到新的独立账本，绑定材料中case_sha256/trace_sha256，并记录姓名、时间、判定和理由，保留原pending模板。用例、证据或规则变化后旧审核不能复用；争议项单列，不能只补最优配置的标签。

证据材料不是Agent评分器的reviews/trace格式，也不替代答案审核。E6现已收集[32份真实回答](../evals/merged-corpus-v2/answer-delivery-v11/run-20261004/answers.jsonl)，对应8个题ID/3簇、两正文各2次重复；[答案审核模板](../evals/merged-corpus-v2/answer-delivery-v11/run-20261004/answer-review-pending.jsonl)绑定case/trace hash，主张清单及主张–引用边待真实人工补全，claim_inventory_complete保持null。全部usage已保存；回答正确率、citation precision、hallucination rate仍为null。标签变更另建版本，用同一新版本回放全部对照，再决定是否冻结确认协议。

开发验收见[v8d完整账目报告](../evals/merged-corpus-v2/budget-search-v8/run-20261003-v4/review-report.md)，回答诊断限制见[E6报告](../evals/merged-corpus-v2/answer-delivery-v11/run-20261004/review-report.md)，全部步骤见[进度账本](optimization-implementation-progress-20261003.md)。
