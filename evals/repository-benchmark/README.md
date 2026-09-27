# Infra 三仓库检索数据集 v1

这是从用户指定的三个仓库构建的中文 Infra **文本检索**数据集。问题、参考答案及证据由 AI
根据冻结版本原文编写，尚未经独立人工审核。它可以用于开发检索器和定位失败案例；不能称为
人工标注的权威基准，也不能将检索指标当作最终问答准确率。

已补充[等价证据标注v2](annotations-v2/README.md)，以及使用同一新标注的
[六组dev检索对照](results/dev-v2/comparison.md)。原始题集和本页所述基线均保留。

## 数据规模

| 来源 | 入库正文 | 问题数 |
|---|---:|---:|
| [AIInfraGuide](https://github.com/caomaolufei/AIInfraGuide) | 70 | 50 |
| [JennyMa11.github.io](https://github.com/JennyMa11/JennyMa11.github.io) | 5 | 50 |
| [ai-infra-book](https://github.com/bojieli/ai-infra-book) | 12 | 50 |
| 合计 | 87 | 150 |

正文共 1,673,577 字符；默认 BGE 语义分块生成 11,168 个子块。题目基于 75 个证据单元，
每单元一条知识题、一条场景题。例如解释 DDP Bucket 的通信重叠，或排查反向结束后才开始
同步的问题。覆盖 CUDA、Attention、训练并行、推理缓存调度、量化、网络及恢复。

## 从哪个文件开始

- [dev.json](dev.json)：50题，用于调分块、召回及重排参数。
- [test.json](test.json)：100题，固定评估；修改测试标签或调参后应另记版本。
- [corpus-manifest.json](corpus-manifest.json)：每篇正文的仓库、commit、路径、固定版本链接、哈希。
- [dataset-manifest.json](dataset-manifest.json)：划分规则、数量与数据文件哈希。
- [question-seeds.json](question-seeds.json)：编题依据，可审阅和修改后重新生成。
- [results/comparison.md](results/comparison.md)：真实模型基线；同目录包含逐题结果及分块标签。
- 本地语料：`../../data/datasets/infra-repos-v1/corpus/`；语料与模型索引不纳入版本管理。

每题包含 `query`、`expected_answer`、`group_id`、`question_type`、`reference_paragraph`
和 `relevant_spans`。每段证据记录原文、文件 SHA256、commit、行号及 GitHub 行号链接。
`review_status=pending_human_review` 可作为人工复核入口；参考答案供审核使用，当前指标只评检索。

同一概念分组整体放入 dev 或 test，两个划分的概念组不重叠。同一个资料文件可以出现在两个
划分的证据中，检索语料也由两个划分共享；这是查询层划分，并非文档隔离或未见领域泛化实验。
划分通过固定的组名哈希排序和子集和算法产生，不使用检索分数。

证据在运行检索前固定。部分长段落采用能够表达所问事实的较短原文片段，使证据可映射到
实际子块；不会依据排名替换失败题的正确标签。`results/*-labels.json` 保存分块解析结果。
标签是稀疏证据标注：同主题其他仓库可能存在同样正确的内容但未标注，因此 Precision、Recall
衡量的是这组指定证据，不是全部知识相关性。后续可人工审核并补充跨仓库等价证据。

## 来源筛选

AIInfraGuide只选 `docs/guides/`，不选面试问题；博客选推理手册与四篇相关技术文章；
书籍只选 `manuscripts/01-*.md` 至 `12-*.md`，不选历史稿、翻译及实验产物。
排除11篇不足600字符的页面，并校验精确重复。保留代码、公式及正文标题；以保留行号的
方式清除前置元数据、目录和渲染标签。当前没有近重复去重，也没有图片像素或PDF测试题。

书籍仓库根目录许可证为 Apache-2.0；另两个冻结版本未找到根目录 LICENSE，已在清单标记，
不据此假定它们也采用 Apache-2.0。本项目提供来源清单和本地复现脚本。

## 复现

在项目根目录执行；首次需要网络取得固定版本与模型：

```bash
uv sync --all-extras
uv run python scripts/prepare_repository_corpus.py
uv run python scripts/build_repository_dataset.py
uv run --all-extras python scripts/index_repository_corpus.py
uv run --all-extras python scripts/benchmark_repository_dataset.py --validate-only
uv run --all-extras python scripts/benchmark_repository_dataset.py --rerank
```

索引目录为 `data/repository-index/bge-e4579f5f84b9`，由语料指纹确定。解析及索引只读正文，
不导入 evals 下的问题或参考答案。基线保持默认配置：450字符分块、语义阈值0.72、
BGE-small-zh-v1.5、候选30、RRF、可选bge-reranker-base；没有以test表现调参。
预热后请求Top10，再计算@1/3/5/10。延迟包括请求检索和可选重排，不包括首次加载模型。

可直接试检索：

```bash
uv run --all-extras infra-rag --backend bge \
  --data-dir data/repository-index/bge-e4579f5f84b9 \
  search '请求取消后KV缓存为什么没有释放？' --domain infra --top-k 5
```

人工复核优先检查场景题推导是否被证据支持、参考答案的条件是否完整，以及其他仓库中
应该补充的等价证据。保持test不参与选择检索参数；需要扩大主题或增加图片评测时建立v2。
