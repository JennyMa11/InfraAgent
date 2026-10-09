# BEIR SciFact 固定配置检索实验

原生文档 5183 篇，官方 test 查询 300 个。四配置在读取测试查询前冻结，test 未用于调参。

模型沿用 BAAI/bge-small-zh-v1.5 与 BAAI/bge-reranker-base；候选30，RRF常数60。原生文档统一为title＋换行＋text，不重新切块；ID与分级qrels保持原样。

| 配置 | Recall@5 | MRR@5 | nDCG@5 | Recall@10 | nDCG@10 | 暖P50/P95 (ms) |
|---|---:|---:|---:|---:|---:|---:|
| bm25 | 0.716 | 0.617 | 0.637 | 0.788 | 0.663 | 4.4 / 7.6 |
| dense | 0.249 | 0.183 | 0.194 | 0.290 | 0.207 | 62.9 / 91.8 |
| hybrid | 0.634 | 0.444 | 0.483 | 0.724 | 0.513 | 68.0 / 97.2 |
| hybrid_rerank | 0.761 | 0.674 | 0.689 | 0.827 | 0.712 | 1551.7 / 1930.1 |

混合检索加重排在本次数据上的Recall/nDCG最高；BM25超过Dense和未重排RRF。重排P50约1.55秒，须同时看质量与成本。该结果不支持直接修改线上默认值。

中文BGE在英文科学文献上的Dense结果较低，语言与领域可能影响结果，但本实验没有比较其他embedding，不能据此归因或选模型。没有运行回答生成，因此不能报告QA准确率或faithfulness。

计时为顺序执行暖组件；hybrid为各组件耗时之和，不是API端到端延迟。准备时间含文档编码、词法索引及模型加载，约45.2秒。未控制多次重复/机器温度，不据此宣称稳定生产性能。

原始输出：[rows.jsonl](rows.jsonl)；指标：[summary.json](summary.json)；冻结协议：[protocol.json](../baseline-20261001/protocol.json)。

下载来源、MD5/SHA256和文件哈希见[source-manifest.json](../../source-manifest.json)。发布的归档校验值已验证。nDCG采用BEIR/TREC线性相关性gain。

运行后只补充审计元数据与报告；没有修改本次排名、qrels或参数。历史实现源码归档见[implementation-e057d0728a6b.zip](../../../../infra-official-v1/results/implementation-e057d0728a6b.zip)。当前新增审核账本归档与金标输出后代码哈希已变化，未来实验须建立新协议，不复用此协议。
