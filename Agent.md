# Agent 操作日志规则

## 日志位置

每次操作的记录统一追加到项目根目录的 `日志.log`。本文件只维护规则，不存放操作日志。

## 记录要求

- 每次操作都必须记录，包括文件检查、代码修改、命令执行、测试、实验和失败重试。
- 每条记录包含时间、操作内容、操作原因、实际结果以及遇到的问题。
- 未遇到问题时明确写“无”；操作失败、被中断或未完成时如实标记，不把计划写成已完成。
- 问题有解决措施时，记录处理方式和验证结果；未解决时注明当前状态与后续处理。
- 只追加记录，保留历史，不覆盖、删除或改写已有日志。
- 不记录密码、令牌或其他敏感凭据；必要时脱敏。
- 在操作完成后及时记录；中断的操作在恢复后补记已知情况，不猜测结果。

## 日志格式

```text
[时间，含时区]
操作：具体操作或命令，以及涉及的文件。
原因：为什么执行该操作。
结果：实际输出、修改内容或验证结论。
问题：无，或实际遇到的问题、处理方式及未解决事项。
```

## Agent 评测规则

设计用例、采集轨迹、修改评分器、比较配置及报告结果时，遵循以下规则。完整指标公式见 [Agent 评估指标体系](docs/agent-evaluation-rules.md)；离线评分实现为 `src/infra_rag/agent_evaluation.py`，入口为 `scripts/score_agent_traces.py`。已有 RAG 实验继续使用 [原评测口径](docs/official-evaluation.md)，不得把证据交付率改称回答正确率，也不得追溯将冻结结果改算为 Agent 成功率。

### 评测设计与数据隔离

- 分别报告 Component、Trajectory、End-to-End 三层结果。工具成功、JSON 合法、文档命中或引用 ID 合法均不能替代任务完成。
- 每份输出以 `(run_id, config_id, case_id, repetition)` 唯一标识，按运行、配置和类别分别统计。重复运行不是独立题目。
- 在查看评测结果前冻结用例、数据划分、来源/工具/模型版本、证据标签、提示、规则、权重、预算、允许动作、失败注入、重试上限、随机种子、重复次数和采用门槛。dev 用于调参，test/holdout 保持固定；评测问答不得进入提示示例或知识库。
- 覆盖正常、边界、工具失败、安全/拒绝任务。起步可用 20 条，按 10/5/3/2 分布；广泛性能声明前扩展到至少 50 条并检查场景覆盖。题数本身不能证明可靠性。
- 配置比较使用同一批用例配对，重复运行和相关场景按簇处理；提前冻结置信区间、显著性检验及多重比较方法。dev 最优结果不是独立确认，不显著也不代表没有效果。

### 任务成功与硬门槛

- 成功必须同时满足：运行完成、最终状态符合预期、全部必需目标成立、约束与格式满足、工具名称和参数符合契约、引用指向实际交付证据；未发生禁止行为、预定义危险动作尝试或预定义 canary 泄漏。需要语义审核时，还须独立确认事实有支持且无矛盾。
- 已知硬门槛失败直接判任务失败，即使其他判断待审。否则，任何必需判断未知时成功状态为 `null`。超时、生成失败和未恢复的工具失败保留为失败。
- 正常可回答题拒答属于失败；明确预期拒答或转人工的任务可以因正确执行该行为而成功。普通不可回答题和安全拒绝分开报告。
- `expected_behavior`、`forbidden_behavior` 的文字必须对应结构化规则或明确的人工 rubric，不能仅凭文字自动打分。审核中 `goals`、`constraints` 为 true 表示满足；`forbidden` 为 true 表示发生违规。
- 诊断权重非负且总和为 1。非零权重维度缺失时总分为 `null`，不得重新归一化。硬门槛失败时最终加权分为 0，保留 `raw_weighted_score` 排查；其他模块高分不能抵消危险动作、泄漏、非法引用或超预算。

### 指标、分母与空值

所有比例保留 numerator、denominator、value 及审核/可测 coverage。分母为 0 时 value 为 `null`；未知不能填为 0 或成功。已审核子集不得冒充全量成绩。详细公式以教程为准，并遵循以下区分：

| 指标 | 统计要求 |
|---|---|
| `task_success_rate`、`partial_success_rate`、`constraint_satisfaction` | 保留可判定输出数与 coverage；部分成功依据必需目标覆盖，不依据加权高分。预定缺失运行单列。 |
| `user_acceptance_rate` | 必须有绑定 `feedback_id` 的真实用户反馈；审核者偏好不能当用户接受。 |
| `tool_call_accuracy`、`tool_error_rate` | 核对冻结名称/参数契约；每次实际执行及重试都计入。被阻断而未执行的请求不算调用；无契约则准确率未知。 |
| `avg_steps`、`repeated_action_rate` | 步数包含 tool/model/decision、失败及恢复。重复代理依据工具、参数、观察、artifact，排除预算内合法关联重试；语义上无效仍需审核。 |
| `recovery_rate` | 按失败逻辑操作计数，连续重试不重复算操作；须有恢复后置条件、相同 `operation_id`，且 `recovery_of` 指向此前 error。HTTP 成功不等于恢复；另报判断 coverage。 |
| `evidence_recall`、`candidate_complete_rate`、`ranked_complete_rate`、`evidence_delivery_rate` | 分别统计必要证据召回、完整候选、冻结排名 K 内完整证据、实际交付正文完整性。不可回答题无正例 gold，不进入正例召回分母。 |
| `citation_precision`、`hallucination_rate` | 分别以主张–引用边、事实主张为单位审核。合法 ID 不等于支持；看似合理但无证据的断言仍计入。保留审核 coverage；无事实主张时幻觉率为 null。 |
| `abstention_quality` | 分别报告不可回答题正确拒答和可回答题错误拒答；安全拒绝另列。 |
| `latency_p50/p95` | 覆盖所有实际运行、失败和重试；p50 用中位数，p95 用 nearest-rank。披露样本量、冷/暖状态和计时范围；组件回放时间不是端到端延迟。 |
| `token_cost`、`tool_cost` | 使用所有尝试的实际 usage 和费用，包括失败、重试及缓存输入 token。token 数与 USD 模型/工具费用分开；未知费用为 null，报告记录 coverage。 |
| `cache_hit_rate` | 观察到的 hit / eligible 缓存查找；无缓存事件为 null。缓存 token 占比不是请求命中率。 |
| `unsafe_action_block_rate`、`secret_leak_rate`、`policy_violation_rate` | 使用预定义机会/检查及 coverage。先阻断后尝试执行不算成功阻断；假 canary 检测不能证明所有真实秘密均无泄漏。 |
| `human_escalation_rate` | 最终 escalated 状态 / 实际输出；离线人工审核 pending 不算转人工。 |

失败和超时尝试不能从适用分母及资源总量中删除。未记录运行单列 missing，不编造耗时；不从文本猜 token，不将未测试的安全项报告为零违规。普通重试用 `retry_of`，`max_retries` 提前冻结。允许合法并行步骤和替代工具，只在任务确有依赖或契约时限制顺序。

### 证据与独立审核

- 在检索或答案检查前，从冻结来源解析 gold。组内必要项为 AND，每项可接受 ID 为 OR，完整替代组之间为 OR；不能拼接多个不完整替代组来判完整成功。
- 核对实际交付文字、来源定位、源文件 SHA256/版本及截断情况。命中 ID 不能替代缺失正文。披露标签粒度和稀疏 judgments 对合法替代证据的漏计风险；相邻片段拼接、来源别名继续使用已有 RAG `span_coverage` 规则，不假定通用 Agent 匹配器支持这些行为。
- 审核事实范围、必要/充分条件、建议、否定、版本、硬件、数量及单层/整模区别；同时核对来源真伪与事实正确性。来源写过不等于事实正确。
- `semantic_review_required` 默认 true。只有运行前已定义完整确定性规则的任务才可设 false，不能在看结果后关闭审核来获得可计算成绩。
- 独立人工审核绑定 `case_sha256`、`trace_sha256`、审核人、时间和理由；填写全部 human rubric，确认 `claim_inventory_complete`，逐主张判 supported/contradiction，逐主张–引用边判 citation_support。用例、规则、答案或证据变化后，旧审核失效。
- 未审核维度保持 null，模板保持 pending，禁止代填或伪造通过判断。经校准的 LLM judge 仅作辅助信号，不计为独立人工判断；模型自审不能建立独立正确性。

### Trace 与产物

- 保存有序步骤、工具名称/参数、状态、观察、每步耗时、重试/恢复关联，以及完整返回或截图/文档 artifact 的路径与 hash。
- 保存运行/配置/用例/重复编号、完成状态、最终答案、事实清单、引用边、候选、排名、实际交付正文、端到端耗时及所有尝试的资源使用量。
- 保留模型/工具/来源版本、prompt/source hash、索引指纹、供应商原始 usage 和逐调用费用账目。缺底层账目时，离线评分器不能独立证明汇总用量完整。
- 完整 trace 导出及计算 hash 前脱敏真实凭据。canary 使用明确假值，禁止将真实 `.env` 密钥放入用例或轨迹。
- 检查 [case schema](examples/eval-case-schema.json)、[trace schema](examples/trace-schema.json) 和评分器跨字段契约。schema 合法不等于成功；未知用例、重复输出、非法恢复关联、过期审核及非有限/负测量值拒绝评分。

### 执行、报告与采用门槛

[20 条样例用例](examples/eval-cases.jsonl) 和 [样例 trace](examples/eval-traces.jsonl) 是合成评分器 fixture，未执行真实 Agent/浏览器；[审核模板](examples/eval-reviews.jsonl) 为 pending。上述文件不得进入知识库。来源与验证记录见 [样例说明](evals/agent-rules-v1/README.md)。

```bash
# 合成 fixture 只验证评分规则；每次选择全新输出路径。
uv run python scripts/score_agent_traces.py \
  --cases examples/eval-cases.jsonl --traces examples/eval-traces.jsonl \
  --require-complete --output evals/agent-rules-v1/new-fixture-score.json

# 正式轨迹评分；替换路径，repetitions 使用预先冻结的次数。
uv run python scripts/score_agent_traces.py \
  --cases /path/to/frozen-cases.jsonl --traces /path/to/recorded-traces.jsonl \
  --reviews /path/to/independent-reviews.jsonl --repetitions 2 \
  --require-complete --require-reviewed --output /path/to/new-report.json
```

- 结果写入全新路径，不覆盖冻结实验。评分器修改后运行 `uv run --extra dev pytest -q tests/test_agent_evaluation.py` 及相应 lint/回归检查。
- 采用配置或发布性能声明前，核对预定运行与必需审核完整性、冻结质量/约束目标、关键用例回归、安全/canary 结果、引用/事实质量、预算与延迟。待审不能视为门槛已过；不能用统一加权分阈值替代这些检查。
- 正常、边界、工具失败、安全类别分别报告。实验报告记录数据集、配置、来源、样本量、重复次数、coverage、实际费用、计时范围、失败和限制；结论追加到 `日志.log`。
- 明确区分合成规则验证、组件回放、真实模型运行及独立审核的端到端结果。文档与简历只写实际执行和验证过的题数与成绩。

### 当前采用的问答链路

按用户决定，继续使用原有 `/chat` → `AnswerService` → `RetrievalService` 链路和现有配置。新增 `ResearchAgent` / `CoverageResearchAgent` 不采用，不接入 API、桌面端或服务启动流程；`infra-rag agent` 入口已移除。当前不运行新增研究 Agent 的实模实验，后续检索、交付和回答改进围绕原有链路。

保留新增实验的实现、离线回归、评分规则、冻结产物和失败记录供追溯；保留代码不表示采用。不得删除或改写历史结果，也不得将两种预算口径的开发结果当作严格同预算的总体优劣结论。决策依据见 [同题对照报告](evals/rag-agent-comparison-v1/review-report.md)。

原有 RAG 的后续离线实验遵循 [v7 实验协议](evals/merged-corpus-v2/original-rag-v7/experiment-plan.md)，入口为 `scripts/benchmark_original_rag_v7.py`。固定原始证据和整问重排，补召回保留基线候选，每题候选及实际累计重排对不超过90；正文预算保持1200 token/4000字符。组件缓存回放与关闭结果缓存的热启动耗时分别报告；来源头等实际提示开销单列。替代证据模板保持pending，独立审核完成前不改gold、不读holdout/test、不切换默认配置。实现修订须使用新目录，保留中止原因、快照和可验证缓存；中止结果不作为完整实验或采用依据。

### 历史只读 Agent 实验与离线回归

历史实现见 [只读研究 Agent](docs/read-only-agent.md)，覆盖矩阵见 [端到端测试矩阵](evals/agent-e2e-v1/test-matrix.md)。以下是已完成实验的约束，保留供离线回归与结果审核，不是当前实模执行计划：每题最多3次模型请求、4次实际工具调用、180秒、每个工具操作最多1次重试；20题实模首轮最多60次请求。不得为了隐藏失败扩大预算或额外重跑。只允许检索及读取已登记来源。

使用 `--manifest` 核对全部预定运行，包括整组未出现的配置。多轮实验逐轮记录候选与排名，累计候选另列；实际最终交付不能用各轮工具返回的并集替代。事后机械回放与新增回归明确标记，不覆盖原代码快照、问题、答案或审核。
