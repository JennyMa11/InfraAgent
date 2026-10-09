# 官方语料分层离线评测

状态：human_reviewed_questions_with_post_run_transport_recovery。
尚未完成人工答案评分；检索覆盖、格式和引用 ID 不是事实准确率。

| 配置 | 题数 | Recall@5 | MRR@5 | nDCG@5 | 完整证据@5 | 生成错误 |
|---|---:|---:|---:|---:|---:|---:|
| oracle | 60 | — | — | — | — | 2 |
| bm25 | 60 | 0.491 | 0.346 | 0.378 | 0.463 | 0 |
| dense | 60 | 0.204 | 0.136 | 0.153 | 0.204 | 0 |
| hybrid | 60 | 0.370 | 0.284 | 0.302 | 0.352 | 0 |
| hybrid_rerank | 60 | 0.556 | 0.403 | 0.429 | 0.519 | 0 |

索引构建/恢复：187.5 ms。
首次预热：8320.7 ms。

计时边界：warm retrieval top10 includes diagnostic collection; generation includes validation retries

分题型结果及bootstrap区间见 summary.json；逐题排名、上下文及回答见 rows.jsonl。
填写 answer-review.json 后以 score 命令生成独立人工评分结果。


原始服务错误与重放政策见summary.json的recovery；原始结果未覆盖。恢复视图不是一次连续性能运行。
