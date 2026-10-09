# 官方语料分层离线评测

状态：human_reviewed_questions。
尚未完成人工答案评分；检索覆盖、格式和引用 ID 不是事实准确率。

| 配置 | 题数 | Recall@5 | MRR@5 | nDCG@5 | 完整证据@5 | 生成错误 |
|---|---:|---:|---:|---:|---:|---:|
| oracle | 60 | — | — | — | — | 0 |
| bm25 | 60 | 0.772 | 0.609 | 0.634 | 0.741 | 0 |
| dense | 60 | 0.247 | 0.198 | 0.199 | 0.222 | 0 |
| hybrid | 60 | 0.494 | 0.419 | 0.423 | 0.444 | 0 |
| hybrid_rerank | 60 | 0.762 | 0.547 | 0.590 | 0.722 | 0 |

索引构建/恢复：18002.5 ms。
首次预热：2624.6 ms。

计时边界：warm retrieval top10 includes diagnostic collection; generation includes validation retries

分题型结果及bootstrap区间见 summary.json；逐题排名、上下文及回答见 rows.jsonl。
填写 answer-review.json 后以 score 命令生成独立人工评分结果。
