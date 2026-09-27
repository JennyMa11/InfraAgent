# 增量处理、检索诊断与上下文交付

本轮围绕三个已有问题改进：单篇更新触发全库重复编码、难以判断证据在何处丢失、
同一父块的上下文重复返回。没有调整模型、召回策略、融合参数、分块阈值或固定题集。

## 增量处理与持久向量缓存

`index.json` 新增来源清单，保存原文件 SHA256、图片图注 sidecar SHA256、领域和解析版本。
未变化来源直接跳过解析和索引发布；重启后同样生效，跳过操作不需要加载模型。
图片资产缺失会触发重新解析。处理过程中来源发生变化会报错，不发布混合版本。
目录导入不会自动删除缺失文件；删除仍使用明确的来源删除操作。

`vectors.sqlite3` 按模型/后端/模态/池化方式与实际编码内容缓存向量。
BGE 分块阶段和最终索引阶段均可复用；CLIP 文本按内容缓存，图片按实际图片资产字节哈希缓存。
图注改变会重新编码文本说明，但可复用未变图片的 CLIP 向量。
缓存命中不重写已有向量。旧快照没有来源清单时首次重新解析；其中已有索引向量可以作为缓存种子。
模型与分块配置仍受原索引指纹约束，不能在同一个索引中混用。

缓存写入不代表发布索引。所有来源解析完成、向量集合准备完成后，才原子替换 JSON 快照并切换
活动内存状态；失败可以留下未引用缓存/集合，但原索引仍有效。API/CLI 仍不能同时写同一目录。
增量收益在解析和编码阶段；新版本 Chroma 集合仍完整写入，JSON 快照也完整序列化。
不是原地增量更新，也没有解决大库写入开销或跨进程事务。

`ingest` 输出 `changed_files`、`skipped_files` 和分阶段向量 `encoded/reused` 计数。
`encoded` 是本阶段新增的唯一编码输入数；重复内容和已有缓存都计入 `reused`。
分块阶段输入与最终子块不一定相同，所以不能只看最终索引计数代表全部模型计算。
图片区域检测阶段的视觉编码不包含在最终 CLIP 缓存计数内。

```bash
uv run infra-rag --data-dir data/my-index ingest examples/corpus --domain infra
# 再次运行时按文件哈希跳过未变化来源
uv run infra-rag --data-dir data/my-index ingest examples/corpus --domain infra

# 默认仅预览；apply 才清理生成物。服务应停止写入，不能与其他进程同时操作。
uv run infra-rag --data-dir data/my-index cleanup
uv run infra-rag --data-dir data/my-index cleanup --apply
```

清理仅处理本索引目录下按内部命名规则生成的历史 text/clip 集合、未被活动块引用的 PNG 资产、
非活动向量缓存。保留活动集合、活动图片与不符合命名规则的用户文件；不处理符号链接资产。
过期服务对象与当前磁盘快照不一致时拒绝清理。缓存删除后 VACUUM 回收空间；
Chroma 历史集合删除后底层文件的磁盘回收由 Chroma 管理。

## 检索阶段诊断

CLI `search --debug` 或 API 请求 `debug=true` 返回诊断；普通请求不包含诊断字段。
诊断不参与排名，记录：

- 各通道原始排名、分数与分数类型。
- RRF 排名、候选是否保留、重排前候选 ID。
- 重排前后排名、分数、返回 Top-k ID。
- 过滤、BM25、BGE、CLIP、融合、重排、上下文与总耗时，以及等待服务锁的时间。
- BGE 查询 token 数、窗口上限和实际窗口数；长输入使用窗口编码平均，不直接截断。
- reranker 输入 pair token 数与是否超过输入上限；未知 tokenizer/上限明确留空。

Chroma 通道返回的是 cosine distance（越小越近），demo 是 cosine similarity（越大越近），
BM25 分数独立。RRF 只使用排名；这些分数不能直接相加或当作置信概率。
重排只处理文字和图片图注。计时包括所在阶段的首次模型加载/缓存构建；
debug 自身的长度诊断也有开销，不能把一次 debug 请求作为受控性能测量。

```bash
uv run infra-rag --data-dir data/my-index search 'KV Cache' --debug --with-context
```

```json
{"query":"KV Cache","top_k":5,"domain":"infra","debug":true}
```

输出能定位“某通道没有召回”“融合候选截断”“重排后下降”。
是否属于真正的证据遗漏仍需与评估金标对照，诊断不会自行认定相关性或补造标签。

## 上下文去重与预算

默认 `context_mode=neighbors`，整个响应共用 1200 个计数单位与 4000 字符的双重预算。
BGE 使用自身 tokenizer（不包括下游 LLM 的模板与特殊 token）；demo/测试编码器没有 tokenizer 时
按 Unicode 字符计数，输出 `token_count_method=unicode_characters`，不冒充真实 LLM token。
预算是交付证据文本的限制，不是下游所有模型通用的 token 保证。

所有 Top-k 命中子块先进入证据候选，再按距命中块的距离加入相邻兄弟块。
同一 chunk 只入选一次，同父块上下文只放在首个命中结果中；其他命中用 `context_ref=parent_id`
引用该组。返回 `sibling_ids` 只列实际交付的证据，而不是所有兄弟块。
上下文不会改变返回的 Top-k 子块与检索分数。

每段证据带稳定 `citation_id`、chunk/parent ID、source、locator、页码/父块行号、模态、
bbox/坐标系、图片路径、图注来源和实际内容。行号仍是原父块范围，不能描述为句子级定位。
超预算时优先保留完整句子前缀，显式标记 `truncated`；不能容纳完整 fenced code 时省略该块，
不会返回半段代码。所有省略的候选 ID 在 `omitted_chunk_ids` 中保留。
很小的预算可能连命中块都放不下；不能把“命中返回”误认为“证据已交付”。

API 返回唯一的规范上下文 `context_pack`；CLI 加 `--with-context` 获取同样结构。
Agent 应消费 `context_pack.context` 与其 evidence 引用映射，而不是再次拼接全部 hit 上下文。

```bash
uv run infra-rag --data-dir data/my-index --context-tokens 800 --context-chars 3000 \
  search 'KV Cache' --with-context
# 原逐 hit 父块拼接方式可用于历史对照，无共享 token 预算
uv run infra-rag --data-dir data/my-index --context-mode legacy search 'KV Cache'
```

这些上下文参数只影响请求处理，不改变索引指纹，已有索引不需要重建。
旧评估报告保留其原运行协议；新默认上下文耗时不可直接替换旧报告的端到端延迟。

## 验证与边界

回归覆盖来源跳过/重启/领域变化/sidecar 更新、删除无重复编码、模型配置隔离、旧快照迁移、
解析期间来源变化、发布失败恢复、Chroma 清理保留活动数据、诊断排名一致性、候选截断、
重排输入截断、共享预算、父块去重、邻居排序、来源过滤、引用定位与代码省略。

隔离验证脚本实际运行 BGE、CLIP、reranker 和 Chroma；全部临时索引自动销毁，报告写入独立目录：

```bash
uv run --extra dev pytest -q
uv run --extra dev ruff check src tests scripts
uv run --extra dev python scripts/verify_retrieval_updates.py \
  --output evals/results/retrieval-updates/demo.json
uv run --all-extras python scripts/verify_retrieval_updates.py --backend bge --multimodal \
  --output evals/results/retrieval-updates/bge-multimodal.json
```

小语料包含 8 篇合成双语 Infra 笔记（初始 16 块）和可选合成图片，用于功能与完整重建一致性验收。
在单篇新增一个小节的真实模型试验中，最终 BGE 与 CLIP 索引各新编码 1 个输入、复用 16 个；
分块阶段另有 2 个新编码输入。完整重建与增量处理的向量最大差值 0，Top-5 一致。
仅改图注时最终 CLIP 新编码 0 个、复用 19 个。删除不重新编码剩余文本向量。
真实长查询分别验证了 BGE 多窗口编码与 reranker pair 超限诊断。

这些不是准确率实验；计时是小语料单次顺序运行，不能据此宣称大库提速倍数。
中文真实仓库 dev50 另验证新/旧上下文模式的 BM25 Top-5 ID、分数一致，固定题集与快照哈希不变。
并发读写、后台任务、召回模型升级、OCR 与代码符号解析仍为后续工作。
