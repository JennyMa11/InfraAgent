# 同候选成对因果分析

改变重排语言、版本保护或元数据时验证候选快照哈希；版本实验另验证完整排名与分数一致。
差值为固定dev上完整原始证据交付数，不是回答正确率；中文仓库无英文译文。

| 对照 | 原交付 | 新交付 | 差值 | 候选完全相同 |
|---|---:|---:|---:|---|
| official:rerank_language_with_english_recall | 42/54 | 36/54 | -6 | True |
| official:rerank_language_with_chinese_recall | 40/54 | 26/54 | -14 | True |
| official:recall_language_with_english_rerank | 42/54 | 40/54 | -2 | False |
| official:recall_language_with_collection_rerank | 36/54 | 26/54 | -10 | False |
| official:version_scope | 40/54 | 40/54 | +0 | True |
| official:metadata_input | 40/54 | 39/54 | -1 | True |
| repository:rerank_language_with_english_recall | 40/50 | 40/50 | +0 | True |
| repository:rerank_language_with_chinese_recall | 40/50 | 40/50 | +0 | True |
| repository:recall_language_with_english_rerank | 40/50 | 40/50 | +0 | True |
| repository:recall_language_with_collection_rerank | 40/50 | 40/50 | +0 | True |
| repository:version_scope | 40/50 | 40/50 | +0 | True |
| repository:metadata_input | 40/50 | 39/50 | -1 | True |

关键案例完整原始排名、分数和版本保护记录见 paired-analysis.json。
官方语言交互差值为-8题：一种改动的效果取决于另一种设置，不能把总下降唯一拆分成两个独立份额。
改变重排语言的影响可以由本对照识别；其内部是否属于分数校准问题仍需进一步实验。
