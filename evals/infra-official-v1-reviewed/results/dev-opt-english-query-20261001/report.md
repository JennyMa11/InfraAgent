# Dev 查询语言消融

检索实验；尚未进行人工回答评分。

| 配置 | Recall@5 | MRR@10 | nDCG@10 | 完整证据交付 |
|---|---:|---:|---:|---:|
| bm25 | 0.7716 | 0.6197 | 0.6639 | 0.7593 |
| dense | 0.2469 | 0.2053 | 0.2216 | 0.2407 |
| hybrid | 0.4938 | 0.4483 | 0.4990 | 0.4630 |
| hybrid_rerank | 0.7623 | 0.5586 | 0.6252 | 0.7407 |

计时：warm retrieval; excludes separate query translation

Only dev queries translated; no answers or gold evidence supplied to translator.
Questions/labels/corpus are unchanged; translations are not ingested.
This is retrieval-only tuning, not an answer quality score.
