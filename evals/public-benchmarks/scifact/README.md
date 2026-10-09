# BEIR SciFact 原生文档检索对照

本轮完成官方5183篇文档、300个test查询的BM25/Dense/RRF/重排对照。
原始语料与查询保存在ignored `data/public-evals/scifact/`；来源文件与哈希见
[source-manifest.json](source-manifest.json)。不切块、不修改官方ID或分级相关性标注。

结果和限制见[实验报告](results/baseline/report.md)，命令见[离线评测说明](../../../docs/official-evaluation.md)。
配置在读取test前冻结，test只用于报告；不以结果调参或更换模型。
`baseline-protocol`是代码定稿前未执行查询的协议，已明确标记retired；实际协议是`baseline-20261001`。
