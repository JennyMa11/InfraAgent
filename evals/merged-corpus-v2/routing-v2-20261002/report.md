# 中文路由独立消融与第一轮修复

固定dev、冻结英文译文、真实BGE模型；每种召回语言只生成一次候选。
官方60题中54题可回答；中文仓库50题原生中文，无冻结英文译文，语言对照为回退条件。
Top5、正文预算1200 token/4000字符不变；元数据提示增加的输入开销另计。

| 数据集／配置 | 完整候选 | Top5完整 | 完整交付 | Top5官方／社区／未知 |
|---|---:|---:|---:|---:|
| official:processed_global30 | 46/54 | 41/54 | 43/54 | 263/6/1 |
| official:recall_en_rerank_en | 48/54 | 39/54 | 42/54 | 205/65/0 |
| official:recall_en_rerank_by_collection | 48/54 | 34/54 | 36/54 | 143/127/0 |
| official:recall_zh_rerank_en | 48/54 | 37/54 | 40/54 | 172/98/0 |
| official:recall_zh_rerank_by_collection | 48/54 | 25/54 | 26/54 | 85/185/0 |
| official:version_all | 48/54 | 37/54 | 40/54 | 176/94/0 |
| official:version_all_metadata | 48/54 | 37/54 | 39/54 | 240/30/0 |
| repository:processed_global30 | 42/50 | 40/50 | 40/50 | 0/250/0 |
| repository:recall_en_rerank_en | 42/50 | 40/50 | 40/50 | 4/246/0 |
| repository:recall_en_rerank_by_collection | 42/50 | 40/50 | 40/50 | 4/246/0 |
| repository:recall_zh_rerank_en | 42/50 | 40/50 | 40/50 | 4/246/0 |
| repository:recall_zh_rerank_by_collection | 42/50 | 40/50 | 40/50 | 4/246/0 |
| repository:version_all | 42/50 | 40/50 | 40/50 | 4/246/0 |
| repository:version_all_metadata | 42/50 | 39/50 | 39/50 | 2/248/0 |

逐题得失见 comparison.json；完整排名和交付证据见 rows.jsonl。
候选完整与交付均基于原始稀疏来源标签，不等于回答正确率。
版本all仅扩大检查范围，至多保护2段；不保证多条件完整。
材料未改写或隔离；默认global30保持不变；独立人工事实审核尚未完成。

成对验证见paired-analysis.md；54条回答与AI定性观察见answer-observations.md。
两份数据集均由AI编写且未独立人工核验，gold仅覆盖已标注来源。
基线来源占比中的1个unknown为打包上下文未提供该片段元数据，不代表索引没有来源记录。
验证：127项pytest、Ruff及包构建通过；未运行test/holdout评测。
检索完成后的日志路径修复及AST一致性检查见postprocessing-protocol.json。
