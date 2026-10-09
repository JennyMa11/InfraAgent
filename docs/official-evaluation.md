# 官方技术语料与分层离线评测

本流程只增加离线工具，不修改 `/chat`、`/search` 或桌面问答配置。
正式运行的前提是独立人工审核，不将AI代审、格式改善或引用ID合法性当作事实正确率。

## 安装、来源与候选校验

在项目根目录使用 Python3.12+：

```bash
uv sync --all-extras
uv run python scripts/prepare_official_benchmark.py
uv run python scripts/benchmark_official.py validate
uv run python scripts/benchmark_scifact.py prepare
```

已有来源按冻结哈希验证，不覆盖已有快照。缺失的不可变来源可下载恢复；Issues/PR的API文本
可能被编辑，精确恢复需要保存原始快照，哈希不一致时必须建立新版本。
正文目录只允许manifest列出的文件，额外加入评测题、答案或其他文档会被拒绝。

首次生成候选的命令为 `uv run python scripts/build_official_dataset.py build`；交付目录已经
存在时会拒绝覆盖。修订时在 `evals/` 下建立同级目录，复制来源manifest及修订后的seed，
再使用 `build --dataset evals/<new-version>`。

## 人工审核与正式冻结

审核者依据 `human-review.md` 核验题意、条件、证据、答案要点和跨划分相似性，再填写
`question-review.json`。`approved`必须同时提供独立人工身份、时间和理由，题目哈希必须匹配。
格式校验只能验证账本字段及内容绑定，不能验证审核者身份或替代实际审核。
导入保留全部pending/approved/rejected/disputed状态、意见，以及原始审核账本字节与哈希。
缺少硬件、日志或测量的不可回答题要基于冻结全文判定，不能因为检索没命中而标注。

```bash
uv run python scripts/build_official_dataset.py import-review \
  --reviews /path/to/completed-question-review.json \
  --output evals/infra-official-v1-reviewed
uv run python scripts/benchmark_official.py validate \
  --dataset evals/infra-official-v1-reviewed --formal
uv run python scripts/benchmark_official.py freeze \
  --dataset evals/infra-official-v1-reviewed \
  --generation dual --output evals/infra-official-v1-reviewed/results/protocol
```

Ollama需要提供已有 `qwen3:4b`；通过 `--ollama-url`指定服务。冻结时保存Ollama模型digest、
BGE/重排模型本地快照及文件哈希、代码哈希、依赖版本、语料与题集哈希和生成参数。
模型快照需已在Hugging Face缓存中；工具不静默换模型。
生成参数沿用现有客户端：temperature0、8192上下文、650输出token、关闭thinking、JSON格式。

```bash
uv run python scripts/benchmark_official.py run \
  --protocol evals/infra-official-v1-reviewed/results/protocol/protocol.json \
  --split dev --output evals/infra-official-v1-reviewed/results/dev
uv run python scripts/benchmark_official.py run \
  --protocol evals/infra-official-v1-reviewed/results/protocol/protocol.json \
  --split holdout --output evals/infra-official-v1-reviewed/results/holdout
```

正式运行必须包含全部题目和四种配置；holdout只在同一协议的完整dev成功后执行，并记录
一次性启动标记。协议、实现或模型变更须建立新dev实验；不得凭holdout结果调参。
执行失败保留已输出内容与失败信息，不覆盖旧目录；未完成的holdout不能被当作完整成绩。

## 候选诊断与生成冒烟

人工审核未完成时，可使用明确的diagnostic协议，但工具禁止运行holdout：

```bash
uv run python scripts/benchmark_official.py freeze --diagnostic --generation none \
  --output evals/infra-official-v1/results/new-dev-protocol
uv run python scripts/benchmark_official.py run \
  --protocol evals/infra-official-v1/results/new-dev-protocol/protocol.json \
  --output evals/infra-official-v1/results/new-dev-retrieval
```

真实生成冒烟使用 `--generation dual`冻结，并在run时指定 `--limit 2 --variant hybrid`。
每题一次标注证据条件，加一次真实检索条件；完整运行则是一组oracle加四组检索配置，
120题对应600条输出，dev为300条。所有会话独立，临时SQLite在结束时清理。
Oracle只使用预先指定的第一组完整标注证据，不按模型答案挑选最有利的证据组。
不可回答题的oracle条件为空证据，直接走既有拒答路径；这不测试模型在噪声证据下的拒答能力，
后者由真实检索条件评估。

## 指标与答案评分

检索配置为BM25、Dense、BM25＋Dense/RRF及混合检索＋现有重排。保存每路候选、融合截断、
重排顺序与输入长度，计算@5/@10检索指标及完整证据覆盖。不可回答题不进入Recall分母。
Top5交付文本单独检查证据覆盖，不能用Top10命中或未截断chunk ID替代。
默认上下文预算沿用4000字符、1200token；oracle是给定证据对照，不应用检索预算截断金标。

`rows.jsonl`保留完整输入、每次生成/重试、最终回答及错误；`summary.json`保存分题型结果、
候选命中、交付覆盖及按场景组进行的2000次bootstrap，seed42。
检索行还保存固定证据解析到的chunk IDs与AND/OR要求，支持独立重算指标。
暖检索计时包括Top10检索和diagnostic收集，不包含另外执行的Top5交付请求；生成计时包含
格式校验重试。索引构建/恢复、首次预热、包含无模型拒答的生成计时及实际调用模型的计时分别报告。

`answer-review.md`提供实际交付证据和回答；填写`answer-review.json`中的人工判断：

- `fact_correct`：所有必要要点成立，且无矛盾或无依据事实补充才为true。
- `points_supported` / `points_total`：支持的必要要点数量，后者必须与题目评分表一致。
- `contradiction` / `unsupported_claim`：是否有反向解读或无法由证据支持的事实陈述。
- `citation_claims` / `citation_supported`：实际附引用的事实主张数及被引用原文支持的数量。
- `refusal_appropriate`：实际拒答是否合理；未拒答时填false。拒答率以最终响应状态为准。

未审核字段留空，不自动计为正确或错误；失败生成不能标为已审核答案。批准记录绑定完整生成
输出哈希，并必须填写人工审核者、时间、理由。

```bash
uv run python scripts/benchmark_official.py score \
  --run evals/infra-official-v1-reviewed/results/dev \
  --reviews /path/to/completed-answer-review.json \
  --output evals/infra-official-v1-reviewed/results/dev-human-summary.json
```

报告包含总体及分配置、分题型的人工评分和覆盖率，事实准确率不由JSON或ID校验推断。
整体统计以输出为单位，不应把同一道题的多个配置结果当作不同问题；配置间比较使用分表。

## SciFact 标准检索对照

```bash
uv run python scripts/benchmark_scifact.py prepare
uv run python scripts/benchmark_scifact.py freeze \
  --output evals/public-benchmarks/scifact/results/new-protocol
uv run python scripts/benchmark_scifact.py run \
  --protocol evals/public-benchmarks/scifact/results/new-protocol/protocol.json \
  --output evals/public-benchmarks/scifact/results/new-baseline
```

保留官方5183篇原生文档、查询、qrels和ID，正文输入统一为title＋newline＋text，不重新切块。
下载校验BEIR发布MD5，再记录SHA256。保留分级相关性，nDCG采用BEIR/trec_eval的线性relevance gain。
四种配置在读取测试查询前冻结，官方test仅用于报告，不调参。候选30、RRF常数60；并列以ID排序。
当前BGE模型以中文为主，英文SciFact结果不是AI Infra问答质量或官方排行榜复现。
计时为顺序执行的暖组件耗时，混合配置报告组件之和，不是线上端到端延迟。

本轮不训练QLoRA、不选择新embedding、不改线上默认值、不实现多轮检索，也不运行MIRACL/NQ。

## Agent 轨迹与治理评测补充

[Agent评分规则](agent-evaluation-rules.md)补充工具契约、失败恢复关联、安全硬门槛、
实际反馈及成本分母；支持独立trace契约和hash绑定审核。旧RAG采集不自动变成Agent轨迹，
候选/交付覆盖和引用ID检查仍不能代替答案正确率；原冻结实验不追溯修改。
