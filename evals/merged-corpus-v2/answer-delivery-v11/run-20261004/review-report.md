# E6第一阶段：实际正文下的生成诊断

结论：完成8题×2套实际正文×2次重复，共32份真实AnswerService回答；格式与请求账目通过机械核对，回答正确性与引用支持仍未知。该样本只有3个问题簇，不能证明总体回答质量提升，也未通过最终采用或确认门槛。

选题在生成前固定为各数据集question_type中ID字典序最小的一题，官方6种、仓库knowledge/scenario共8题。使用v8d直接记录的B-O15/Ladj-X30实际正文，原AnswerService提示、空历史、无翻译和无额外元数据保持不变。实际来源locator序列化开销随完整提示进入API，正文仍为原1200旧编码器token/4000字符口径。

| 条件 | 实际输出 | JSON格式合法 | answered状态 | no_evidence状态 | API错误 |
|---|---:|---:|---:|---:|---:|
| B-O15正文 | 16 | 16/16 | 11 | 5 | 0 |
| Ladj-X30正文 | 16 | 16/16 | 10 | 6 | 0 |

标注可回答的14次输出中，B为3次no_evidence，Ladj为4次；标注不可回答的2次输出均为no_evidence。上述只是旧标签与输出状态对应，标签充分性、正确/错误拒答和事实正确尚未独立审核，不能直接当拒答质量结论。32次均一请求完成，没有格式重答；实际32请求低于最多64上限。每条件只有8个不同题ID、同批3簇，两次回答不是两倍独立题目。原summary中independent_cases字段计不同ID，含义由[事后审计](audit-v2/integrity-audit.json)明确更正，未追溯改原输出。

官方DeepSeek Anthropic接口、配置model deepseek-flash、temperature0、thinking disabled、最多650输出token、45秒/请求；无额外warmup、翻译、judge或HTTP重试。完整messages/raw/id/model/stop_reason/usage与终态保存；supplier model元数据不能证明不可变权重。32/32请求有usage，原字段合计input_tokens=13366、cache_read_input_tokens=27904、cache_creation_input_tokens=0、output_tokens=3793；不自行合并为跨接口统一输入计数，不把cache token当request cache hit rate，美元成本未测为null。

生成组件（含全部尝试）B p50/p95约1066.485/1629.819ms，Ladj约1016.547/1248.616ms，n=16/条件。它在冻结正文上执行，未实时检索，不是端到端问答延迟，也不将两个阶段的p95相加。小样本、重复及缓存供应商usage均如实保留，不作总体速度声明。

全部32个trace/case/context hash、原系统/用户提示、原格式修复契约、最终合法引用对象与实际正文一一核对通过；没有把gold/answer_key传入生成prompt。先前审计因仓库schema无answerable字段中止；保留原脚本和audit-protocol.json，在audit-v2按既有仓库全正例规则重试，输出和原summary不变。

[32份答案待审模板](answer-review-pending.jsonl)绑定case/trace hash，reviewer、时间、理由、claim_inventory_complete、主张清单和主张–引用边均null，状态pending，审核覆盖0/32。事实正确率、citation precision、hallucination rate、正确拒答和最终采用仍未知/不允许；合法JSON或answered不代替语义判断。

当前只完成E6实际交付诊断。独立审核后的充分证据、干扰正文、提示策略对照和确认仍未执行；审核之前不继续用这些32份未审答案调提示、不修改gold、不读test/holdout，不切换默认问答。来源真实性与事实范围要先审核，模型自审不代替真实人工。

产物：[冻结计划](experiment-plan.md)、[32格协议](protocol.json)、[真实回答及每调用账目](answers.jsonl)、[机械汇总](summary.json)、[事后审计](audit-v2/integrity-audit.json)。最终manifest额外绑定本报告、中止审计与新版审计，保留原manifest。
