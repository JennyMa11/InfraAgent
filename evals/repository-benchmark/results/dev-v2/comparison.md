# Dev v2 检索对照

同一份50题v2标注、相同BGE与reranker；未运行test查询。
完整证据命中：覆盖任意一组替代证据中的全部原文片段。

| 配置 | 完整证据命中@5 | 证据MRR@5 | 子块Recall@5 | 子块Precision@5 | P50 ms | P95 ms |
|---|---:|---:|---:|---:|---:|---:|
| original-bm25-rerank-truncate | 0.860 | 0.691 | 0.780 | 0.228 | 565.4 | 685.8 |
| original-hybrid-rerank-truncate | 0.820 | 0.695 | 0.750 | 0.224 | 581.8 | 735.4 |
| original-hybrid-rerank-union | 0.820 | 0.700 | 0.750 | 0.224 | 840.4 | 1030.4 |
| headings-bm25-rerank-truncate | 0.840 | 0.684 | 0.740 | 0.216 | 736.4 | 939.5 |
| headings-hybrid-rerank-truncate | 0.840 | 0.705 | 0.770 | 0.228 | 808.9 | 929.3 |
| headings-hybrid-rerank-union | 0.840 | 0.684 | 0.760 | 0.224 | 1240.7 | 1642.9 |

按预定规则选择：`original-bm25-rerank-truncate`。
补标增加替代正确块，子块Recall分母发生变化，不能与v1数值直接比较。
标题方案同时包含标题栈、向量/重排上下文与纯结构块清理，尚未隔离每项贡献。
