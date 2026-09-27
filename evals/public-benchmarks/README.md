# 外部公开评测数据 v1

2026-09-26 从作者/发布方的固定版本下载，未改动 `repository-benchmark` 的题目、标签、索引或历史分数。本目录保存题目和来源清单；大体积语料及原始模型输出放在忽略的 `data/public-evals/`。已完成外部补充检索实验，结果和限制见[实验分析](experiment-analysis.md)。

## 数据与适用范围

| 数据集 | 已整理数量 | 用途 | 限制 |
|---|---:|---|---|
| BRIGHT StackOverflow | 117题，107,081原生文档 | 独立的技术文档检索，原生文档级相关性金标 | 英文，包含一般编程；不是纯GPU/LLM Infra |
| BRIGHT Infra相关选题 | 22题，使用上述完整文档库 | PyTorch、量化、容器、并发、云部署、RAG集成等 | AI按主题筛选，未重新审核答案；是117题的子集，不能重复计数 |
| RAGBench TechQA | validation 152题、test 157题 | IBM产品运维/技术支持的上下文相关性及回答忠实性 | 较旧的企业技术场景，不能当现代AI Infra的完整代表 |
| C-Eval计算机科目val | 59题：体系结构21、网络19、操作系统19 | 中文知识题及后续证据映射候选 | 选择题有答案，无检索金标；属于上游val，不称官方test |

来源：[BRIGHT发布方](https://huggingface.co/datasets/xlangai/BRIGHT)、[RAGBench发布方](https://huggingface.co/datasets/galileo-ai/ragbench)、[C-Eval发布方](https://huggingface.co/datasets/ceval/ceval-exam)。

## 文件与复现

- `bright-stackoverflow/queries.json`：117原始问题、答案、标注推理、相关文档ID和排除ID。
- `bright-stackoverflow/infra-queries.json`：22题，逐题记录主题选择理由，未翻译或改写。
- `bright-stackoverflow/qrels.json`：官方 `gold_ids` 转为二元文档相关性，非组内AND证据。
- `ragbench-techqa/{validation,test}-queries.json`：唯一问题及对应模型输出记录ID。
- `ceval-computing/val-queries.json`：原题、四选项、答案和待证据映射状态。
- `manifest.json`：固定版本、下载URL、原始文件SHA256与检查统计。
- `data/public-evals/prepared/bright-stackoverflow/documents.jsonl`：完整短文档库；使用原生ID，保留原边界。
- `data/public-evals/prepared/ragbench-techqa/*-contexts.jsonl`：去重的所给上下文；`*-records.jsonl` 保留每次模型生成与上游注释。

从根目录执行：

```bash
uv run --with pyarrow python scripts/prepare_public_evals.py
```

缺失的原始文件会按清单固定版本下载并校验SHA256。PyArrow为临时依赖，未写入项目运行依赖。

## 评测边界

**BRIGHT实验使用完整107,081文档库，并单列22题选题结果。** `gold_ids` 对应官方短文档，不是重新切分后的chunk ID；按原生文档排名计算 Recall@k、MRR@k、nDCG@k，并应用逐题排除ID。不能把所有gold拼成“必须全部命中才算答对”的证据组。`scripts/benchmark_public_retrieval.py` 已实现独立协议；现有CLI的span匹配不是此协议，不能直接传本目录JSON。上游未提供dev/test拆分，本轮在比较前固定本地dev87/holdout30；没有看到结果后挑选题目。

英文问题与当前中文BGE模型的语言能力不同。英文结果单独报告；翻译版属于新派生数据，需复核，不与原版分数混报。模型换代的主要决定仍应参考现有中文Infra验证集。

**TechQA有618条模型输出记录，但只有309个唯一问题。** 原始validation/test问题ID没有重叠。`generated_response`是模型输出，不是标准答案；`all_relevant_sentence_keys`由上游注释模型给出，不是人工检索金标。validation有11条、test有6条记录含无法解析的相关句子ID，已标记 `sentence_label_status=invalid_keys`，应在句子级评测中排除或另行审核。所给context也不是TechQA完整检索库，不能把context全部视为相关文档，或将上下文池评测称为官方TechQA成绩。

**C-Eval先映射当前冻结语料证据。** 每题填写可回答/语料未覆盖/题目有歧义，并补来源、固定commit、行号和引用；无证据时不计算检索召回。题目和答案不入知识库。分类决定应基于来源事实，不能按检索是否命中决定“未覆盖”。

## 许可证与出处

- BRIGHT、RAGBench发布数据卡声明CC-BY-4.0；保留作者与上游出处。原始文档包含第三方材料，使用时还应保留其原有来源信息。
- C-Eval为CC-BY-NC-SA-4.0，派生版本保留署名、非商业和相同方式共享条款。
- 固定版本：BRIGHT `3066d29c9651a576c8aba4832d249807b181ecae`；RAGBench `97808f3e5fd16ede40bbff6c2949af8139b2eb7b`；C-Eval `617524a00b307ff6f9933702f724131fe12ca7ce`。

另查到 [Φ-Bench](https://huggingface.co/datasets/faibench-Frontier-Infra-Bench/faibench_Frontier_Infra_Bench)，覆盖85个LLM基础设施工程任务，但其评测需要实现内核/系统并运行评分器，缺少可直接使用的检索相关性标注，因此本轮仅列为后续场景题来源，未下载或执行任务包。CMMLU计算机科目亦可补充中文选择题，但与C-Eval用途重复，本轮未导入。
