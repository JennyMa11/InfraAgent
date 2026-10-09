# 语料预处理与分库检索 v2

基于原来的40篇官方来源和87篇中文仓库正文，创建独立的结构化索引。原始来源不改写；导航和渲染语法按规则清理，标题层级、正文类型、硬件显式提及、原始行号与旧片段映射随片段保存。代码分段带完整围栏，表格分段重复表头；超宽单行保留完整内容，编码采用既有token窗口，重排模型仍可能截断长输入。

完全重复仅在产品和明确版本一致时保留代表与来源别名；未知版本不自动合并。近重复使用20字符片段审计，共享片段过多的常见文本跳过，候选只供审核、不删除；数字、标识符和否定词差异会标记。当前正文来源可通过原始行号定位，处理后的文档及SHA256、行号映射、片段映射和去重结果记录于 `corpus-manifest.json`。索引身份包含处理实现及输入哈希；配置指纹包含 `preprocessing_version`，旧索引仍兼容。

AI审计结果单独保存为 `ai-material-audit.jsonl`，优先检查参数范围的补充审计为 `ai-risk-audit.jsonl`。它们是原文摘录上的AI判断，未独立人工审核，也不是完整文档事实核验。只有逐字引用与输入行号一致的条目保留；未经确认的AI版本提取不用于版本优先，建议不进入检索正文或生成证据。

## 构建与使用

```bash
uv run --all-extras python scripts/prepare_corpus_v2.py prepare
uv run --all-extras python scripts/prepare_corpus_v2.py index
uv run --all-extras python scripts/prepare_corpus_v2.py audit-ai
uv run --all-extras python scripts/prepare_corpus_v2.py audit-risk
uv run --all-extras python scripts/prepare_corpus_v2.py serve --profile global30 --port 8002
```

独立启动入口读取 `.env.llm`，不改现有服务或默认索引。此冻结语料服务不支持直接导入、删除来源；重新运行准备和构建命令来创建新版本。

启动器默认使用单独预处理的 `global30` 实验配置；完整组合 `final` 已测得退步，仅保留供诊断。现有项目默认服务不变。

可选配置：`global30`、`global60`、`split`、`version`、`final`。global组使用英文翻译；split组每库每通道30候选，全部候选并集统一重排；version组追加版本优先；final组进一步用中文问题检索中文库、英文译文检索官方库，并按材料语言重排。明确版本仅识别vLLM、SGLang、CUDA的产品/版本组合；统一重排前10名中最多2个匹配的官方片段保留至Top5，不会强制返回任意版本匹配文档。

`/search` 使用调用者提供的字面查询；`/chat` 调用独立翻译客户端进行语言路由。翻译失败沿用原文并记录回退。API格式保持兼容，证据增加 `metadata`，分库证据另附 `provenance`；debug保存各库查询、通道排名、候选和版本保留记录。

## 评测

```bash
uv run --all-extras python scripts/benchmark_corpus_v2.py
uv run --all-extras python scripts/benchmark_corpus_v2.py --phase answers
```

仅使用固定官方dev60和仓库dev50；原始标签不改，通过内容和来源别名解析新片段。官方组重放既有冻结英文译文；仓库组使用原生中文，未提供译文时官方库也使用原文，属于语言路由回退条件的对照。两组分开报告，不合并成绩。

七组官方消融分离预处理、候选数量、分库名额、版本优先和语言路由；分库30/路/库与全局60/路均最多120候选。Top5交付使用同一份冻结Top10排名重新打包，避免重复ANN检索扰动。上下文预算保持1200token/4000字符。参考证据稀疏且分块粒度变化可能影响Recall分母，完整原文证据交付更适合对比覆盖。

## 独立语言消融与第一轮修复

```bash
uv run --all-extras python scripts/benchmark_corpus_v2.py --suite routing --output evals/merged-corpus-v2/routing-v2-20261002
uv run --all-extras python scripts/benchmark_corpus_v2.py --suite routing --phase answers --output evals/merged-corpus-v2/routing-v2-20261002
```

新套件不覆盖原来的dev-v2，使用预处理global30作基线。四组消融独立控制社区库召回语言（英文／原始中文）和重排问题语言（统一英文／按库语言），版本保护保持原来的top10规则。官方库始终使用冻结英文译文；按库重排在社区库使用原始中文，与社区召回语言独立。

输出目录冻结配置与实现哈希；代码或设置变动后重跑需要新的--output目录。本次检索完成后的日志路径兼容修复不改变已保存的候选、分数或排名，另记于postprocessing-protocol.json。

每种召回语言的候选仅检索一次，写入candidates目录并在各重排组复用；相同问题／正文输入的BGE分数写入rerank-scores目录。version_all复用中文召回、统一英文重排组的分数，只将版本保护检查范围扩大到全部候选，仍至多保留2段匹配版本官方证据。version_all_metadata在此基础上把已有collection、source_type、product、release、applicability、scope字段显式送入重排和回答提示；缺失值不推断，原文不改写。正文预算不变，元数据的提示开销另计。

```bash
uv run --all-extras python scripts/analyze_routing_v2.py --output evals/merged-corpus-v2/routing-v2-20261002
```

成对分析验证候选快照哈希，并检查版本保护实验的完整排名及分数完全相同。输出paired-analysis.md／json，包括重排语言、召回语言、版本范围、元数据的独立得失与三个关键案例。重放组延迟包含缓存读取，不能当作真实模型推理延迟比较。

Python接口新增可选参数community_recall_language、rerank_language、version_scope、include_metadata；原来的language_route及服务配置保持兼容。diagnostics分别记录候选缺少匹配版本、匹配版本在全局前十之外、实际保护ID，以及候选快照路径和哈希。include_metadata仅在实验上下文设置include_evidence_metadata，默认回答提示不变。

两组dev单独报告。中文仓库组没有冻结英文译文，英文模式回退为原始中文，四组语言消融在该组不构成真正的中英文对照。report.md和comparison.json保留来源占比、逐题得失；验收要求官方完整交付至少43/54、中文至少40/50，并待独立人工事实审核。既有12道官方、6道中文生成样本用于基线、version_all、version_all_metadata，共54条；引用合法性与事实审核分开记录。未通过采用评审时默认global30不变。

两份问题／证据标签均为AI编写，尚未独立人工核验；标签只覆盖已标注来源，未穷尽等价证据。以上指标用于固定dev的诊断，不应表述为人工认证的问答正确率。

回答样本沿用此前固定12道官方题和6道中文覆盖题，基线与最终配置共36条。原始回答、证据、调用元数据、独立人工审核模板分别保存；作答数与引用ID合法均不等于事实正确。holdout和test不参与调优。摘要、具体得失及是否达到采用门槛见 `comparison.md`。
