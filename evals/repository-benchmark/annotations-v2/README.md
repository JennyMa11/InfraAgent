# 等价证据标注 v2

原始 `../dev.json`、`../test.json` 和基线报告保持原样。本版本保留150道题的ID、问法、
概念分组及原始证据，补充27条内容判断，涉及dev25题、test12题。

## 文件与审核

- `dev.json` / `test.json`：新标注；源文件路径相对此目录解析。
- `adjudication-ledger.json`：接纳的原文引用、来源、行号和理由。
- `manifest.json`：版本、原始/新文件哈希与范围。
- `../equivalent-evidence-decisions.json`：可复现的判断输入，使用固定源文档ID及引用行号。

判断依据是原文是否支持具体问题，而非排名高低。仅提到相同主题却未说明所问事实的内容不
接纳，例如一般KV释放描述不能替代“取消路径的幂等清理”，一般MTP介绍不能替代“训练模块
是前提”。所有新增判断由AI执行，尚需独立人工审核。

补标来自既有检索候选的内容核查，仍存在候选池覆盖偏差。它补正了已识别的漏标，**不是全库
所有相关内容的穷尽标注**；不要将其当作独立人工基准。新方案运行前固定标注哈希。

## 替代证据的判定

`evidence_alternatives` 表示可以替代的证据组：组间是“或”，同组的多个原文片段是“且”。
每个片段可以映射到若干包含该片段的分块，找到其中任一个即可。

`complete_evidence_hit@5` 判断前五块是否覆盖任意一组中的全部片段；`evidence_mrr@5`
使用最早完成该覆盖的排名。它们评估证据覆盖，不评估模型生成答案。

`relevant_spans` 同时保存全部正例，兼容旧子块指标。新增替代证据扩大了子块Recall分母，
因此v2的子块Recall不能直接与v1对比；不同分块策略也应优先比较固定原文证据的完整覆盖。

## 复现与验证集对照

```bash
uv run python scripts/prepare_repository_corpus.py
uv run python scripts/build_repository_dataset.py
uv run python scripts/augment_repository_labels.py
uv run --all-extras python scripts/compare_dev_retrieval.py
```

对照脚本仅执行50道dev题，自动构建/复用独立索引。六组配置为原始/标题分块各自的
BM25＋重排、混合截断＋重排、完整混合并集＋重排。模型及语料固定，每路候选30。
预热后计时Top10请求，报告@1/3/5/10；先按完整证据命中@5选择，再按证据MRR、延迟决胜。
选择规则不能在看到结果后修改。Test问题不会在此脚本中执行。

标题方案同时改进Markdown标题栈、文件主题/层级标题的模型输入及纯结构块清理；本轮
尚未隔离每一项贡献。它使用 `heading_context=True` 的独立指纹，原始索引可以继续使用。

结果位于 `../results/dev-v2/`；操作记录追加至项目根目录的 `日志.log`。
