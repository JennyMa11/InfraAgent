# 预处理与分库检索结果

127篇冻结正文形成16,320片段；原文、版本、hash、行号与旧片段映射保留。
近重复候选56组，只审计不删除；明确同版本完全重复别名0组。

## 固定官方dev60

| 配置 | Recall@5 | MRR@10 | 完整证据交付 |
|---|---:|---:|---:|
| raw_global30 | 75.31% | 0.5484 | 40/54 |
| processed_global30 | 77.78% | 0.6091 | 43/54 |
| processed_global60 | 75.93% | 0.5822 | 43/54 |
| raw_split | 68.83% | 0.5157 | 35/54 |
| processed_split | 73.15% | 0.5618 | 40/54 |
| processed_version | 75.00% | 0.5863 | 42/54 |
| final | 48.15% | 0.4178 | 26/54 |

global30/60表示全局每通道30/60候选；split表示每库每通道30候选；version追加版本优先，final追加按材料语言路由与重排。global60和split的最大候选预算相同，均为120。
所有官方配置使用固定英文译文，final中文库使用原始中文；模型、正文来源与1200token/4000字符预算固定。分块粒度改变会影响chunk级Recall，原始证据完整交付更适合衡量前后覆盖。
最终语言路由同时改变中文库候选和重排查询，不能由本实验单独归因于某一个因素。额外哈希题的直接官方证据已进入候选，但统一重排落到第11名（约0.676）；前列中文概述得分约0.907—0.993，且官方证据不在前10名，版本保留规则未触发。这是完整组合失效的具体案例，需要另测跨语言分数可比性与版本相关性资格。

## 中文仓库dev50

| 配置 | Recall@5 | MRR@10 | 完整证据交付 |
|---|---:|---:|---:|
| raw_repo_chinese | 76.00% | 0.6232 | 38/50 |
| raw_merged_chinese | 76.00% | 0.6332 | 38/50 |
| processed_merged_chinese | 80.00% | 0.6022 | 40/50 |
| final | 80.00% | 0.6022 | 40/50 |

仓库组全部使用原生中文，官方分库没有额外英文译文；属于翻译缺失时的回退条件，不应称为完整在线翻译路由的成绩。新增材料的等价证据未穷尽标注，固定来源gold不是所有正确答案的集合。

## 材料与回答审阅

主审计覆盖127文档，补充范围审计另存；共保留353条AI审计提示。审计基于抽样摘录，不是全文核验；逐字引用和行号验证仅确认来源，不能确认判断正确。
明确MoE参数范围疑点2处，原文保留，建议不入库。
生成样本36条，错误0条；事实评分为空，AI定性观察与独立人工模板分开。
- official/raw_global30：{'answered': 9, 'no_evidence': 3}；作答数不是正确率。
- official/final：{'no_evidence': 5, 'answered': 7}；作答数不是正确率。
- repository/raw_repo_chinese：{'answered': 5, 'no_evidence': 1}；作答数不是正确率。
- repository/final：{'answered': 6}；作答数不是正确率。
- `official:official-002-2:raw_global30`：只解释租户盐，未回答两个适配器身份为何必须区分。
- `official:official-002-4:raw_global30`：对原标注可回答题拒答，需区分证据未交付与生成模型未使用证据。
- `official:official-002-1:final`：对原标注可回答题拒答，需区分证据未交付与生成模型未使用证据。
- `official:official-002-4:final`：对原标注可回答题拒答，需区分证据未交付与生成模型未使用证据。
- `official:official-004-4:final`：对原标注可回答题拒答，需区分证据未交付与生成模型未使用证据。
- `repository:repo-053-1:raw_repo_chinese`：对原标注可回答题拒答，需区分证据未交付与生成模型未使用证据。
- `repository:repo-053-2:raw_repo_chinese`：复述了源文模型总参数/专家FFN参数范围的简化，需核对完整模型范围。
- `repository:repo-053-2:final`：复述了源文模型总参数/专家FFN参数范围的简化，需核对完整模型范围。

真实API完成/search、/chat、元数据和冻结来源管理检查。在线缓存额外哈希冒烟仍只解释通用哈希结构，漏掉具体额外项，保留原始响应于api-smoke.json。

## 采用检查

- official_recall_at_5：False
- official_complete_at_least_40：False
- cuda_async_evidence_restored：False
- no_detected_core_omission：False
- independent_human_quality_score：None

现有服务与默认索引不切换。可独立启动实验配置，保留失败结果；达到检索门槛也不能替代回答正确性审核。

复现命令、接口行为和限制见README.md；原始排名及回答见dev-v2目录。冻结的实现位于dev-v2/implementation，后续仅context.py的Ruff格式变化，AST保持一致。
验证：116项pytest、Ruff、构建和真实API通过；未运行holdout或test。
