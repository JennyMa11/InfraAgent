# 合并语料 dev 对照

固定中文 dev60；使用相同冻结译文、模型、重排与上下文预算。

| 配置 | Recall@5 | MRR@10 | nDCG@10 | 完整证据交付 |
|---|---:|---:|---:|---:|
| official_english | 0.7623 | 0.5617 | 0.6272 | 0.7407 |
| merged_english | 0.7531 | 0.5481 | 0.6092 | 0.7407 |
| merged_bilingual | 0.4877 | 0.3419 | 0.3996 | 0.4630 |

Original sparse official gold only; added equivalent evidence not labeled.
Unanswerable status may change in expanded corpus; review separately.
AI source/answer audit is not independent human scoring.

回答样本为每类型按ID固定选2题，共12题×3配置。
事实评分保持空值，逐题生成与证据见 answers.jsonl。
