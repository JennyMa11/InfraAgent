# E6第一阶段：实际交付正文下的AnswerService生成诊断

开发集小样本诊断，不是独立确认或全量回答正确性评测。独立人工审核pending，因此不构造“已审核充分证据”Oracle，也不根据未审核答案优化提示。本阶段仅比较原B与开发候选Ladj-X30的实际交付正文，原AnswerService提示和生成逻辑保持不变。

选题固定：从官方与仓库冻结dev文件分别按question_type分组，取每组ID字典序最小的一题。官方6类型、仓库knowledge/scenario两类型，共8题；不按召回得失、gold或答案选择。两正文条件×2次配对重复×8题=32个预定输出，重复不是独立题目。样本为起步诊断，不支持总体性能声明，不读取test/holdout。

使用v8d已直接记录且机械审计的context，不重新召回或补入答案。按原AnswerService渲染locator/正文，空历史、无翻译、无额外元数据，原SYSTEM_PROMPT不变。上下文原1200旧编码器token/4000字符正文口径不变；模型实际输入usage与来源头另计。

官方DeepSeek Anthropic接口、当前.env.deepseek的deepseek-flash、temperature0、thinking disabled、max output650；timeout45秒/请求。保存无凭据配置、供应商原始response id/model/stop_reason/usage，返回model仅为供应商元数据，不证明不可变权重。每输出最多2次调用（仅原AnswerService格式重答一次），不新增HTTP重试、warmup、翻译或judge。最多64个实际请求，按实际尝试计usage及失败，不剔除不合法JSON或超时。请求内容不含gold/answer_key或benchmark示例。

保存32格manifest、每次消息/raw/usage/耗时/失败与最终answer/citations/status、实际上下文及hash。机械指标只包括记录完整、JSON/引用ID格式和输出状态；answered或引用合法不等于正确。按条件/类型分别报告，拒答仅报告状态，不未经审核宣称正确拒答。引用支持、事实正确、幻觉、任务成功、用户接受均为null，独立审核覆盖0/32。

出现401/402/403/429访问或配额错误时停止新请求，保留已执行失败，余下输出列missing，不以补跑隐藏问题。其他失败不额外重试，原格式修复计入2次上限。美元费用未测保持null，token与缓存字段按供应商账目原值另报，不能将cache token比例叫request cache hit rate。

执行前冻结全部原输入/来源/模型配置/提示/实现hash和32格manifest；每份答案绑定case/context/trace hash，生成pending独立审核模板，主张清单和主张–引用边由真实人工补全，不以模型自审填通过。独立标签及答案审核前不改gold、不读确认集、不切换默认策略；充分证据和干扰证据对照、提示改动与确认仍待后续独立协议。
