# AIHubMix coding-glm-4.6-free：完整dev实验记录

2026-10-01，同一审核后dev60题×Oracle与四种检索配置，共300条。
本轮收集300条执行记录，但模型评测未成功完成；不能用于比较模型质量或速度。
仅前两条是真实模型输出。随后159次请求在completion正文返回账号额度限制提示；
79条被框架两次格式校验后记为拒答，另1条先收到额度提示、重试又失败。
共213条出现连接或JSON响应错误，现有错误日志未区分这两种具体原因。
原始输出/摘要保持不变，本报告独立识别平台提示；未生成dev-completed标记。
每种配置54道可回答、6道不可回答；人工审批仅覆盖题目，生成答案评分仍待审核。

请求路由：`coding-glm-4.6-free`；预热返回模型：`glm-5.3-flash`。底层权重不可验证冻结。
与两组历史基线的固定输入、检索指标、证据及首轮提示词差异：0项。

原始框架状态（AIHubMix的拒答含平台额度提示，不能解释为模型拒答能力）：
| 模型/路由 | 作答 | 拒答 | 调用错误 | 需重试题数 | 模型调用题数 | 生成P50秒 |
|---|---:|---:|---:|---:|---:|---:|
| local_4b | 120 | 178 | 2 | 10 | 294 | 5.77 |
| deepseek_flash | 169 | 131 | 0 | 0 | 294 | 0.96 |
| aihubmix_coding_glm | 1 | 86 | 213 | 80 | 294 | —（实验受阻） |

P50仅统计发生模型调用的题目，包含格式/引用重试；不能当作完整问答端到端耗时。

| 配置 | 本地作答/拒答/错误 | DeepSeek作答/拒答/错误 | AIHubMix作答/拒答/错误 |
|---|---:|---:|---:|
| oracle | 40/18/2 | 52/8/0 | 1/22/37 |
| bm25 | 19/41/0 | 34/26/0 | 0/16/44 |
| dense | 12/48/0 | 16/44/0 | 0/16/44 |
| hybrid | 21/39/0 | 29/31/0 | 0/16/44 |
| hybrid_rerank | 28/32/0 | 38/22/0 | 0/16/44 |

作答数不是正确答案数；不可回答题也可能以answered状态输出语义拒答。
事实正确率、要点支持率、引用支持率、幻觉/误拒答等仍为空，须独立人工评审。

API原始输出结构检查（排除最后一轮无返回的请求错误和已识别的平台额度提示）：

| 模型/路由 | JSON/schema合法 | 非JSON | 未知引用ID | 内联ID未列入citations |
|---|---:|---:|---:|---:|
| local_4b | 291/292 | 1 | 3 | 2 |
| deepseek_flash | 294/294 | 0 | 0 | 0 |
| aihubmix_coding_glm | 2/2 | 0 | 0 | 0 |

本轮逐次返回的模型名：`{"glm-5.3-flash": 2, "coding-glm-4.6-free": 159}`。
其中glm-5.3-flash为2次真实模型回答；coding-glm-4.6-free为159次额度提示的响应字段，
不能将后者视为159次实际模型生成。
结束原因：`{"stop": 161}`。
服务端原始usage字段求和：`{"prompt_tokens": 1852, "completion_tokens": 697, "total_tokens": 2549}`。
其中reasoning_tokens=471，cached_prompt_tokens=0。
不同协议的usage字段定义不同，不直接相加跨协议字段，也不推算未知账号费用。

生成条件差异：AIHubMix max_tokens=1024，思考模式未显式关闭；DeepSeek max_tokens=650并关闭thinking；本地num_predict=650、think=false、format=json、num_ctx=8192。各端temperature=0，但不是严格相同解码条件。

检索配置、冻结语料与题目不变，API回答模型不能改善Recall/MRR/nDCG。Top5实际完整证据交付率仍为：BM25 48.1%、Dense 20.4%、Hybrid 38.9%、Hybrid+Reranker 53.7%。

[本轮原始报告](dev-aihubmix-glm-20261001/report.md)、[原始逐条数据](dev-aihubmix-glm-20261001/rows.jsonl)、[答案审核材料](dev-aihubmix-glm-20261001/answer-review.md)、[待填审核账本](dev-aihubmix-glm-20261001/answer-review.json)。
[三轮逐条对照与诊断](aihubmix-comparison.json)、[新冻结协议](protocol-aihubmix-glm-20261001/protocol.json)。

旧基线、题目、标签未覆盖；未执行holdout，未把题目/答案加入知识库。
