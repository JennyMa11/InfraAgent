# priority-review.md 案例审计

**性质：AI 生成的技术审计，不是独立人工答案评审。** 本文不修改 `rows.jsonl`、`answer-review.json`、
`answer-review.md` 或任何冻结产物；`answer-review.json` 中的事实字段必须由署名人工填写。
审计对象：`priority-review.md` 列出的 14 条案例，数据源为同目录 `rows.jsonl`、`automatic-diagnostics.json`、
`summary.json` 与 `evals/infra-official-v1-reviewed/dev.json`。

## 1. 结论摘要

| 案例 | 机械分类 | 审计判定 | 依据 |
|---|---|---|---|
| official-014-2:hybrid_rerank:retrieved | 输出校验失败 | **确定性缺陷（校验规则误杀）** | 答案内容正确、所引 2 个 ID 全部在交付集内，仅因正文内联 ID 未全部写进 `citations` 被判失败 |
| official-002-1:oracle:oracle | 输出校验失败 | **模型转写错误（内容正确）** | 把 25 字符 ID 写成 26 字符，重试仍未纠正；答案本身命中考点的三项 |
| official-002-2:hybrid:retrieved | 输出校验失败 | **规则自相矛盾（结果恰好正确）** | `supported=false` 时正文提到合法 ID、`citations` 为空即判失败；且交付证据完整度 0，拒答结果本身正确 |
| official-017-3:bm25:retrieved | 输出校验失败 | **结果正确（模型输出崩坏）** | 两次输出回显证据、JSON 被截断；交付证据完整度 0，拒答结果本身正确 |
| official-004-2:oracle / bm25 / dense / hybrid | 声明不足 | **疑似误拒答（4 条同源）** | 交付证据完整度均为 1.0，模型正文已给出正确结论“不能”，却置 `supported=false`，内容被丢弃 |
| official-004-3:dense:retrieved | 声明不足 | **疑似误拒答** | 同上；正文“Ampere 仅支持 W8A16 而非 W8A8”命中要点 |
| official-012-2:bm25 / hybrid | 声明不足 | **疑似误拒答（2 条）** | 正文“#queue-req 为 0 表示客户端提交过慢”即要点原意 |
| official-022-2:hybrid_rerank:retrieved | 声明不足 | **疑似误拒答** | 正文“shared memory 为线程块内可见、线程块间不能直接共享”正确 |
| official-002-2:oracle:oracle | 声明不足 | **疑似误拒答（最弱）** | 正文只说“未明确说明”，未给出“不能只按文本共享”的结论 |
| official-024-2:hybrid_rerank:retrieved | 声明不足 | **疑似误拒答（最弱）** | 正文只说“未明确说明”，未给出“优化不等于取消计算”的结论 |

汇总：14 条中 **1 条是评测框架造成的确定性损失**，**1 条是模型引用 ID 转写错误**，
**2 条拒答结果本身正确**，**10 条为疑似误拒答且其中 8 条正文已含正确结论**。
没有任何一条是“检索没召回”导致的——10 条声明不足案例的 `delivered.complete` 全部为 1.0。

## 2. 全局口径核对

| 项 | 数值 | 说明 |
|---|---:|---|
| 输出总条数 | 300 | 60 题 × 5 配置 |
| 生成服务错误 | 2 | official-016-3:oracle、official-017-3:oracle，HTTP 500 |
| 最终作答 | 120 | 40.0% |
| 最终拒答 | 178 | 59.3% |
| `format_valid` | 297 / 300 | 失败 3 条 = 2 服务错误 + 1 不可解析 |
| `citation_ids_valid` | 120 / 300 | **口径存疑，见 §4.3** |

可回答题（268 条有效）最终拒答 148 条 = 55.2%。分题型拒答率：

| 题型 | 有效条数 | 最终拒答 | 拒答率 |
|---|---:|---:|---:|
| conditional | 60 | 43 | 71.7% |
| multi_hop | 30 | 21 | 70.0% |
| debugging | 60 | 37 | 61.7% |
| code_api | 43 | 19 | 44.2% |
| single_hop | 75 | 28 | 37.3% |

拒答集中在 conditional / multi_hop，与 §4.1 的极性问句问题一致。

## 3. 逐案证据

### 3.1 输出校验失败（4 条）

**official-014-2:hybrid_rerank:retrieved —— 唯一的框架误杀。**
`delivered.complete = 1.0`，8 条交付证据。两次尝试的原始输出完全相同：
`supported = true`，`citations = ["E7a70794e3abe0baba0df156e"]`，正文内联引用
`[E7a70794e3abe0baba0df156e]` 与 `[E9e27ac051ce62af8450419a8]`。
两个 ID 均在交付集内（分别位于第 5、第 2 位），内容“预量化模型不应再传 quantization”正确。
唯一不合法之处：正文内联的 `E9e27ac0…` 没有出现在 `citations` 数组里。

**official-002-1:oracle:oracle —— 模型 ID 转写错误。**
交付证据只有 1 条，正确 ID 为 `E1ea8fd1c1607655904749488`（25 字符）。
第 1 次输出写成 26 字符的 `E1ea8fd1c16076559047494888`，正文内联又写成
`E1ea8fd1c1607559047494888`（第 10 位起开始错位）。第 2 次重试只删掉了正文内联标记，
`citations` 仍是 26 字符的错误 ID。答案内容（LoRA ID、多模态输入哈希、租户隔离盐）完全正确。

**official-017-3:bm25:retrieved —— 模型输出崩坏，但拒答结果正确。**
两次输出都是 `{"current_query": …, "evidence": […]}` 结构：模型把提示词里的“当前问题/证据”
翻译成了 JSON 键，并把整段证据原文回显进 `evidence` 数组，第 1893/1933 字符处被截断，
JSON 不可解析。`delivered.complete = 0.0`——标注 span 是
`` `temperature = 0` corresponds to greedy sampling… `` 这句散文，bm25 交付的是
`sglang-sampling_params.md#L198-L252` 的代码块，`normalized()` 去标点后无法匹配。
边界提示：交付的代码块里确实有 `"temperature": 0`，人工可能判为“可回答”，
但按当前 span 精确匹配口径，它不算完整交付，因此**不能**自动标为误拒答。

**official-002-2:hybrid:retrieved —— 规则自相矛盾。**
`delivered.complete = 0.0`，拒答结果正确。两次输出均为 `supported = false`、
`citations = []`，但正文写了“证据 [E062010e52f86dd5d0e443c52] …”。该 ID 是第 9 条交付证据，
完全合法。失败原因是 `_valid` 的“正文内联 ID 必须 ⊆ citations”规则在 `supported = false` 时同样生效，
而系统提示词又要求“只引用直接支持回答的证据”——模型拒答时自然不把证据写进 `citations`。
两条规则互斥，模型无法同时满足。

### 3.2 交付完整标注证据但模型声明不足（10 条）

10 条的 `delivered.complete` 全部为 1.0（9 条 conditional、1 条 debugging）。
原始输出全部是**结构合法**的 `supported = false`（`validated: true`，未触发重试），
内容随后被 `assistant.py:250-253` 整体替换为固定拒答文案。其中 8 条正文已含正确结论：

- official-004-2（oracle/bm25/dense/hybrid 四配置同源）：“不能将 Ampere 的 W8A16 支持解释为 W8A8”。
  oracle 条件下唯一一条证据就是标注 span，模型仍拒答——**同一错误在四种检索条件下完全复现，
  指向提示词/判定契约，而非检索质量**。
- official-004-3:dense：“Ampere GPU 仅支持 W8A16（权重仅 FP8）而非 W8A8”。
- official-012-2（bm25/hybrid）：“当 #queue-req 为 0 时，表示客户端提交请求过慢”。
- official-022-2：“shared memory 是每个线程块内部可见的，且线程块之间不能直接共享”。

另 2 条（official-002-2:oracle、official-024-2）正文只写“证据未明确说明”，未落到结论，判定应更保守。

## 4. 机制层面的问题

### 4.1 `supported` 无法表达“否”的回答

这 10 道题都是“能否/是否……？”的极性问句，正确答案是“不能/不是”。证据里只有正面陈述
（如 “Ampere GPUs are supported for W8A16 … utilizing Marlin kernels.”），
没有任何一句直接断言否定命题。模型据此把 `supported` 理解为“证据是否正面支持该命题”，
于是答出正确的“不能”却置 `supported = false`；而 `assistant.py:250-253` 对
`supported = false` 一律丢弃正文、输出固定拒答文案。**正确答案被框架改写成“资料不足”。**
`conditional` 71.7% 的拒答率与这一机制高度吻合。

### 4.2 校验规则在拒答路径上自相矛盾（`assistant.py:294-295`）

`mentioned ⊆ citations` 对 `supported = false` 同样生效，与系统提示词
“只引用直接支持回答的证据”冲突（见 §3.1）。两种合理输出都会被判失败：
拒答时引用看过的证据、或作答时正文引用多于数组。后者正是 official-014-2 被误杀的原因。

### 4.3 `citation_ids_valid` 不是“引用 ID 合法”（`benchmarking.py:246`）

该字段要求 `obj["supported"]` 为真，因此所有拒答一律记 False。300 条的失败分解为：

| 原因 | 条数 |
|---|---:|
| `supported=false`，`citations` 为空 | 140 |
| `supported=false`，但 `citations` 中的 ID 其实全部合法 | 35 |
| `supported=true` 但 `citations` 含非交付 ID（official-002-1） | 1 |
| `supported=true` 但正文内联 ID 未进 `citations`（official-014-2） | 1 |
| 格式非法（official-017-3:bm25） | 1 |
| 服务错误 | 2 |

即 `citation_ids_valid = 120/300` 会让读者以为引用 ID 有六成是坏的，**真实引用缺陷只有 2 条**。
字段名与实际语义不符，且会被 `summary.json` 与报告直接引用。

### 4.4 人工复核材料看不到模型原始输出（`offline_evaluation.py:384`）

`review_markdown` 渲染的是 `row["generation"]["response"]`，即**后处理之后的最终回答**。
178 条拒答在 `answer-review.md` 里呈现为同一句“当前检索到的资料不足以可靠回答这个问题”，
评审人只能靠 trace 里的 `validated: true/false` 区分“模型自称不足”与“校验失败”，
看不到模型实际写了什么，无法完成事实/要点评分。这正是需要额外手工导出 `priority-review.md` 的原因。
建议在 `review_markdown` 中并列输出 `generation.calls[-1]["raw"]`、`checks` 与 `trace.validated`。

### 4.5 `priority-review.md` 的证据摘录会误导评审

摘录取自 `context["evidence"][:2]`（交付顺序前两条），**不是**标注 span，也没有“命中/未命中”标记：

- official-014-2 模型引用 `E7a70794e3abe0baba0df156e`（交付列表第 5 位），摘录只显示第 1、2 位，
  评审人会误判为编造引用。
- official-012-2:hybrid 引用 `E63c1f7fb51b02d051c9fafca`（第 3 位）、
  official-002-2:hybrid 引用 `E062010e52f86dd5d0e443c52`（第 9 位），同样不在摘录内。
- official-004-3:dense 摘录第 1 条是与本题无关的 “Cache isolation is not supported in engine V0.”。

三条被引用 ID 全部合法，摘录却让它们看起来像幻觉。

### 4.6 诊断与优先案例清单不可复现

`automatic-diagnostics.json` 与 `priority-review.md` 在仓库内**没有任何生成脚本**
（`grep` 全仓无匹配）。这两份材料目前是手工/会话产物，无法随重跑自动再生，也无法校验。

### 4.7 次要问题

- `official-004-2:oracle` 的 `Ef799598e9c44e1e80614ed21` 与 `official-004-3:dense` 的
  `E9179e0166553b73ef2a10c4b` 等交付证据缺少 `document_id`（`None`），
  而 `priority-review.md` 里又用 `document_id` 指代来源，字段不齐。
- `official-004-2:oracle` 正文出现 “W8A1:6” 笔误，未影响判定，但说明该模型对量化术语的字符级稳定性较差。

## 5. 建议（按性价比排序）

1. **改校验规则**（`assistant.py:284-295`，改动最小、收益最大）：
   正文内联 ID 只要 ⊆ 交付集合即视为合法，并把它并入 `citations`；
   `supported = false` 时不检查 `mentioned ⊆ citations`。
   仅此一项即可挽回 official-014-2，并让 official-002-2:hybrid 这类输出不再被无谓重试。
2. **保留模型正文**（`assistant.py:250-253`）：`supported = false` 时不要丢弃 `answer` 字段，
   至少拼接到固定拒答文案之后，或在 `generation` 中单独留存。
3. **修正指标语义**（`benchmarking.py:246`）：拆成 `citation_ids_in_allowed`（只要有引用就校验）
   与 `answered_with_valid_citations`（额外要求 `supported=true`），并在报告里同时给出。
4. **补齐复核材料**（`offline_evaluation.py:362-404`）：`review_markdown` 增加最后一次原始输出、
   `checks`、`trace.validated`；优先案例摘录改为“标注 span 是否命中交付”并附完整交付 ID 列表。
5. **澄清 `supported` 契约**（`assistant.py:147-155`）：明确“证据支持一个否定结论时，
   `supported` 仍应为 true”，并给出一个极性问句的示例。这是 10 条疑似误拒答的直接诱因。
6. **重试提示词回列允许 ID**（`assistant.py:272-280`）：当前重试只说“引用无效”，
   模型没有可对照的 ID 清单，official-002-1 因此两次犯同一个错。
7. **给诊断加类别**：区分“校验失败但内容可恢复”与“模型自称证据不足”，并补上
   “标注 span 未交付但等价证据已交付”的观察项（如 official-017-3）。
8. **把两份诊断产物脚本化**，纳入离线评测流程，随重跑自动生成。

## 6. 边界声明

- 本文的“疑似误拒答”是审计判断，**不是**已批准的金标；正式误拒答率仍需独立人工在
  `answer-review.json` 中逐条填写并署名。
- 本文未修改任何冻结产物、未重跑评测、未读取 holdout、未触碰线上配置或模型参数。
- 判定依据仅为 `rows.jsonl` 中留存的原始输出与交付证据；未做模型重放。
