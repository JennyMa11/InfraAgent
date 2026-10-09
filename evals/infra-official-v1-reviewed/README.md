# kylin审核后的官方领域题集

120题由用户声明已审核通过；审核者kylin，日期2026-10-01（仅日期，未推断具体时刻）。
本工具登记对话中的审核结论，不代替用户审核，也未批准尚未生成的答案。

来源题集：`evals/infra-official-v1`。题目、证据、评分要点与划分保持一致，仅审核字段更新。
原始导入账本见[imported-question-review.json](imported-question-review.json)，
题集及来源哈希见[dataset-manifest.json](dataset-manifest.json)和[corpus-manifest.json](corpus-manifest.json)。
正式校验已通过；dev60/holdout60，holdout尚未运行。

正式dev协议：[protocol.json](results/protocol-dev-20261001/protocol.json)。
当前模型：固定BGE-small-zh-v1.5/BGE-reranker-base、qwen3:4b；一组oracle＋四种检索条件，
每道dev题5条输出，共300条。每条答案单独评审事实、要点、引用和拒答，不继承题目审批。

命令与评测口径见[离线评测说明](../../docs/official-evaluation.md)。

首轮完整dev已采集300条：[结果与后续边界](results/dev-first-round.md)。
主运行298条正常返回、2条生成服务错误；相同参数重放仍失败。独立的两题重复惩罚诊断
正常返回，但未替代正式结果。未写dev完成标记，holdout未运行；生成答案仍待单独人工审核。
可先查看[优先审核案例](results/dev-20261001/priority-review.md)。
