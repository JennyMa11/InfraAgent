# 回答样本与事实支持观察

固定12道官方、6道中文题，分别在基线、version_all、version_all_metadata生成，共54条。
调用错误0；JSON格式有效54；作答45、拒答9。45条作答的引用ID检查全部通过，9条拒答的该检查为False是现有指标定义，不是非法引用。
引用ID合法不验证陈述与证据的支持关系，事实正确率仍为空。
以下为AI定性／规则审计，不能替代独立人工评分；审计不修改语料或gold。

- official:official-002-2:processed_global30：原始dev可回答题拒答；需结合实际交付证据判断拒答是否适当。
- official:official-002-4:processed_global30：原始缓存证据未完整交付；回答从LoRA请求ID说明推导缓存身份，须核查该因果关系的直接依据。
- official:official-002-2:version_all：原始官方gold未完整交付，回答使用中文材料；等价支持需人工核验，不能仅按gold缺失认定事实错误。
- official:official-002-4:version_all：原始dev可回答题拒答；需结合实际交付证据判断拒答是否适当。
- official:official-004-4:version_all：未给出AMD DeepSeekV3 PR的e4m3fnuz条件；泛化为E4M3/E5M2不能代替特定PR证据。
- official:official-002-2:version_all_metadata：原始dev可回答题拒答；需结合实际交付证据判断拒答是否适当。
- official:official-002-4:version_all_metadata：原始缓存证据未完整交付；回答从LoRA请求ID说明推导缓存身份，须核查该因果关系的直接依据。
- official:official-004-4:version_all_metadata：未给出AMD DeepSeekV3 PR的e4m3fnuz条件；泛化为E4M3/E5M2不能代替特定PR证据。
- repository:repo-053-2:processed_global30：复述模型总参数量等于全部专家参数之和的范围歧义；未区分专家FFN范围与完整模型范围。
- repository:repo-053-2:version_all：复述模型总参数量等于全部专家参数之和的范围歧义；未区分专家FFN范围与完整模型范围。
- repository:repo-053-2:version_all_metadata：复述模型总参数量等于全部专家参数之和的范围歧义；未区分专家FFN范围与完整模型范围。
