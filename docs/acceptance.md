# 五项能力验收

| 参考能力 | 实现及证据 | 已完成的验证 | 尚不能声称 |
|---|---|---|---|
| 多格式三级分块 | `text_chunking.py`、`chunking.py`、`image_chunking.py` | TXT 标题、语义边界、token 控制；图片裁剪、合并和细化；PDF 图注/坐标测试；真实模型图文导入 | 无条件保证分块语义完整或子图检测准确 |
| 父子块与模态元数据 | `models.py`、`service.py` 的父索引、`GET /parents/{id}` | 分块、重启、替换和删除的索引生命周期 | 多进程或百万级父索引性能 |
| 统一图文向量库 | CLIP 集合存配套文本/视觉向量，BGE 集合独立 | 真实 CLIP 文本查询和图片编码，Chroma 图文集合数量/过滤验收 | BGE 向量经 CLIP 自动映射，或不同模型空间天然等价 |
| 混合检索及重排 | BM25/BGE/CLIP/RRF、Cross-Encoder 图注重排 | 60 题真实文本消融；六图真实多模态验收 | bge-reranker 直接理解图片像素，或重排必然提升 |
| JSON 评估器 | `evaluation.py`、`scripts/benchmark.py` | 来源证据独立映射为子块 ID；Recall/Precision/F1/MRR/nDCG 与逐题记录 | 当前小型同源题集代表真实生产效果 |

运行：`uv run --all-extras pytest -q`（当前 53 项测试，含后续工程回归）及
`uv run --all-extras ruff check src tests scripts`。
真实模型结果保存在 `evals/results/bge/`、`evals/results/multimodal/` 与
`evals/results/model-preflight.json`，复现命令见 README。

实验没有预设“技术越复杂指标越好”。在本次 60 题数据上，融合排序高于单路点估计，
重排的 MRR 下降；没有运行统计显著性检验，不能宣称已经证明泛化提升。
固定窗口与语义分块的相关子块数量不同，Recall/F1 对标签粒度敏感，应连同排序、
上下文长度和具体证据完整性一起审查。

尚未纳入五点范围的工程扩展：OCR、向量图检测、代码符号索引、持久任务队列、鉴权、
跨进程写入锁、历史集合和资产回收、大型真实语料与用户标注。

## 增量处理与证据交付验收

新增来源哈希清单、SQLite 持久向量缓存、可预览的历史生成物清理、检索阶段诊断、
响应级上下文预算与稳定引用。实现、复现命令与边界见
[增量处理、检索诊断与上下文交付](retrieval-updates.md)。

真实模型隔离验收通过：更新只处理变化来源并复用剩余向量，结果与完整重建一致；
图注更新复用图像 CLIP 向量；长查询 BGE 多窗口与重排截断诊断均实际执行。
固定 dev50 的新旧上下文模式 BM25 Top-5 ID/分数相同，快照与题集 SHA256 不变。
报告保存在 `evals/results/retrieval-updates/`。

不宣称本轮提高检索准确率；Chroma 新版本与 JSON 快照仍完整写入，服务仍单进程同步处理。
