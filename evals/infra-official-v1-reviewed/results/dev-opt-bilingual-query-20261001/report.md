# Dev 查询语言消融

检索实验；尚未进行人工回答评分。

| 配置 | Recall@5 | MRR@10 | nDCG@10 | 完整证据交付 |
|---|---:|---:|---:|---:|
| bm25 | 0.7654 | 0.6258 | 0.6682 | 0.7593 |
| dense | 0.2593 | 0.2191 | 0.2432 | 0.2407 |
| hybrid | 0.5185 | 0.4245 | 0.5077 | 0.5000 |
| hybrid_rerank | 0.6451 | 0.5162 | 0.5692 | 0.6481 |

计时：warm retrieval; excludes separate query translation

Only dev queries translated; no answers or gold evidence supplied to translator.
Questions/labels/corpus are unchanged; translations are not ingested.
This is retrieval-only tuning, not an answer quality score.
