# DeepSeek官方API与本地4B的dev对照

2026-10-01，审核后的60道dev题×5种配置，完整300条。模型路由为`deepseek-flash`。

只替换回答模型；保留语料、划分、BGE、重排器、候选/上下文预算、提示词与两次校验流程。
逐条输入/排名/交付/首轮提示词核验：差异0项。

| 配置 | 本地作答/拒答/错误 | API作答/拒答/错误 | 本地生成中位秒 | API生成中位秒 |
|---|---:|---:|---:|---:|
| oracle | 40/18/2 | 52/8/0 | 4.40 | 0.94 |
| bm25 | 19/41/0 | 34/26/0 | 5.84 | 1.04 |
| dense | 12/48/0 | 16/44/0 | 5.37 | 0.88 |
| hybrid | 21/39/0 | 29/31/0 | 6.36 | 1.06 |
| hybrid_rerank | 28/32/0 | 38/22/0 | 6.84 | 1.10 |

耗时仅统计发生模型调用的题目，包含格式/引用重试；不同服务与本机执行环境影响耗时。

作答数不是正确答案数；证据不足时拒答可能是正确行为。答案事实、引用支持率仍待独立人工评审。
原summary的citation_ids_valid对supported=false返回false，不能将其理解成拒答的引用错误。
附加JSON将原始最后一轮输出的结构、未知ID、内联ID缺失分别计数，不改写历史指标。

Oracle的54道可回答题中52条最终作答，004-2和012-4仍声明证据不足，建议优先评审。
检索配置中交付完整标注证据却最终拒答的API案例为0条；这不等于这些作答都事实正确。
不可回答题BM25有一条024-4状态为answered，但正文明确表示不能给出私有部署的精确P95，
没有编造延迟数值；说明supported/最终状态不能代替语义拒答判断，仍需人工判定。

API显式关闭thinking、temperature=0、max_tokens=650；本地使用think=false、num_predict=650、
format=json、num_ctx=8192。相同数字不保证相同tokenization，API也没有本地JSON传输约束，
因此解码条件不是严格相同。API权重没有不可变摘要，逐次保存实际返回模型和usage。

用量（包含重试，排除预热）：`{"input_tokens": 320948, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 21632, "output_tokens": 27423}`。
不将token用量换算为未知账号价格。

原始结果：[API报告](dev-deepseek-flash-20261001/report.md)、
[API答案评审](dev-deepseek-flash-20261001/answer-review.md)、
[评审账本](dev-deepseek-flash-20261001/answer-review.json)、
[逐条对照与诊断](deepseek-comparison.json)。

未执行holdout，未将题目/答案加入知识库，旧基线未覆盖。
