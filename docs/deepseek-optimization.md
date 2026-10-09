# DeepSeek 检索优化

当前 `.env.llm` 使用官方 `deepseek-flash`，入口为 `https://api.deepseek.com/anthropic`。
其他服务文件保留；`.env.llm` 优先，环境变量与 `INFRA_RAG_LLM_ENV_FILE` 可覆盖。
密钥不进入源码或报告。更换配置后重启服务。

中文问题先由 DeepSeek 翻译成英文查询，再进入英文技术资料的 BM25+Dense+RRF+重排。
翻译只接收问题，不接收答案或 gold evidence；最终回答仍接收原始中文问题并校验引用 ID。
同一实例缓存最近128条译文，翻译失败时使用原文，trace显示 `fallback_original`。
翻译输出上限220token，回答650token，temperature0，官方接口关闭thinking。

启动已测配置（加载40篇已冻结、已审核的官方正文，独立索引，不导入评测问答）：

```bash
uv run python scripts/serve_deepseek_optimized.py --port 8000
```

如已有服务占用端口，先停止旧服务或选择另一个端口。`/chat` 使用翻译；
`/search` 保持字面检索，用于观察原始检索。`/health` 显示模型与配置。
启动脚本固定英文查询、BGE、重排、每路30候选并集及1200token/4000字符上下文预算。
通用CLI按 `.env.llm` 中 `INFRA_RAG_QUERY_LANGUAGE=english` 开启聊天翻译，但仍需显式选择BGE和重排：

```bash
uv run infra-rag --backend bge --rerank --fusion-candidates union \
  --query-language english --data-dir data/deepseek-optimized serve
```

关闭查询翻译：设置 `INFRA_RAG_QUERY_LANGUAGE=none`，或 CLI `--query-language none`。
切回本地 Ollama 时同时将查询翻译设为 `none`；当前在线翻译仅支持官方 DeepSeek。
修改查询策略不改变索引指纹；embedding、正文、分块和来源定位均沿用现有实现。
本轮保留原中文embedding；英文查询在当前dev提升不代表它是英文资料的最佳embedding。

结果见[优化实验报告](../evals/infra-official-v1-reviewed/results/deepseek-optimization.md)。
只使用固定 dev60 调优，holdout未运行；翻译为AI生成，尚未独立审核。
作答数不是正确率，事实正确率、忠实性与引用支持率等待独立人工评分。
正式复测重放冻结译文，每题的原文、实际检索查询、排名、证据与API生成元数据均保留。
离线检索计时不包含独立翻译请求；线上首次提问有额外翻译延迟。

复测协议：`evals/infra-official-v1-reviewed/results/protocol-deepseek-optimized-20261001/protocol.json`。
结果目录：`evals/infra-official-v1-reviewed/results/dev-deepseek-optimized-20261001`。
分析复现：`uv run python scripts/analyze_deepseek_optimization.py`。
旧基线与失败方案均保留在独立目录，不覆盖已有成绩。
