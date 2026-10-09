# 证据集合选择实验：已实现并完成，未采用

冻结设计保留在[experiment-plan.md](experiment-plan.md)，其中的“尚未实现”是预注册时的状态。当前结果见[执行报告](run-20261002/execution-report.md)、[定性生成观察](run-20261002/answer-observations.md)和[统计记录](run-20261002/paired-statistics.json)。默认继续使用`processed_global30`。

两套冻结候选池各比较原问题排序T、MMR去重M、条件平均排序F和贪心最大覆盖G。880条主检索、48条生成诊断、110条隔离检索、2条隔离生成及46条无相关缓存延迟记录均已完成。官方最高43/54，未达到44/54门槛；没有运行确认集检索或模型评测。独立人工事实审核仍待完成，交付指标不等于回答正确率。

初次启动的通用校验器读取过holdout作完整性校验，没有对其进行检索、推理、评分或调参。原启动保存在[setup-aborted-20261002](setup-aborted-20261002/deviation.md)。正式运行使用仅dev加载器，复用110份字节不变的条件调用，未事后调整提示、权重、gold或来源。正式冻结实现与归档哈希一致。

实验入口是`scripts/benchmark_selection_v3.py`，支持分阶段恢复；只读汇总入口是`scripts/analyze_selection_v3.py`。模型权重及源数据哈希均验证，生成模型凭据从忽略的`.env.llm`读取，不写入产物。

```bash
HF_HUB_OFFLINE=1 uv run --all-extras python scripts/benchmark_selection_v3.py --phase all
uv run python scripts/analyze_selection_v3.py evals/merged-corpus-v2/evidence-selection-v3/run-20261002
```

独立新运行需指定新的`--output`目录。已完成记录会复用；源代码或协议哈希不同会拒绝在同目录继续，以免混合实验。145项pytest、Ruff和包构建通过，详见[验证记录](run-20261002/validation.json)。结论已追加到`日志.log`。
