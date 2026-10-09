# 生成与选择定性观察

审核方法：AI只读对照实际上下文与原始输出；独立人工事实审核pending。此文件不修改gold、风险清单或主实验成绩，不计算回答正确率。

## 完整标注证据时的拒答

002-2的P0-T与P1-G均缺少完整原始gold且拒答；来源证据oracle完整装入原始标注的Extra hashes句仍拒答。raw解释是“未直接说明两个适配器使用相同文本时能否只按文本共享缓存”。这给出检索以外的诊断样本，但标签语义充分性、适配器与LoRA身份映射及模型蕴含判断仍待核验，不能仅据自动coverage确认为模型错误。

002-4的oracle能够引用直接Extra hashes句解释LoRA ID进入缓存键；却未回答模型支持LoRA的前置要求。第二段原始gold只到“implements”，未带完整接口名；oracle保留原句，未发生预算截断。这也提醒完整gold覆盖不等于每个回答条件均充分。

## 直接因果证据与支持前置

002-4的P1-G虽未完整交付原始官方gold，但社区缓存键段明确列出LoRA ID，与旧“从LoRARequest ID推断缓存键”的情况不同。缓存身份子结论有直接上下文依据；然而“用启动参数确认模型支持LoRA”把启用方式作为能力条件，未核对模型接口支持。故不能将这条整体计为正确。P0-T此次对002-4拒答，不再沿用旧轮回答的判断。

## 跨来源与条件评分

004-4：P0-T引用两份直接材料并写出e4m3fnuz；P1-G仅写一般E4M3/E5M2，未交付PR特定格式。固定候选中正确PR片段原始排11，F排17，G排12；三项条件分数分别约0.0011、0.1084、0.0029。G第二步认为第二条件覆盖达到0.9575，但该值并不代表PR事实支持。条件三缺少产品/硬件消歧上下文，以及相关分数与具体回答条件脱节，是后续可检验假设，不能据本案例单独证明因果。

官方P0-G与P0-T逐题交付完全一致；P1-G与P1-T也完全一致。G相对F恢复的5题都是F新增丢失，未提高同池原问题控制组交付。单条件题G在第一次选择后全部边际增益为0，后续回到原问题排序；相关分数饱和需与facet-observations.md及case-traces.json一起检查。

## 源文隔离

Q0中repo-053-2复述“模型总参数量是64个专家参数量之和”。Q1排除原始585行所在片段、同时过滤邻接和别名，两个固定MoE样本仍作答，053-2不再复述该等式。官方/仓库原始gold交付均无变化；110题中该风险片段实际交付暴露由仓库1题降到0题。原始源文不改；风险定性仍待人工确认，不能把两次输出当稳定事实准确率。

## 固定原始输出节选

### official:official-002-2:P0-T

原始gold完整：0；状态：no_evidence。

当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

### official:official-002-2:P1-G

原始gold完整：0；状态：no_evidence。

当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

### official:official-002-2:oracle

原始gold完整：1；状态：no_evidence。

当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

### official:official-002-4:P0-T

原始gold完整：0；状态：no_evidence。

当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

### official:official-002-4:P1-G

原始gold完整：0；状态：answered。

服务模型支持 LoRA 可通过启动时使用 --enable-lora 并配合 --lora-modules {name}={path} 指定 LoRA 模块来确认 [E71173cb7177e423f64b908eb][E5e801c761a85c7d2f8d43c6d]。即使两个 LoRA 请求的文本相同，缓存键仍需额外区分身份，是因为缓存键除父块哈希和本块内 Token 序列外，还包含额外标识，如 LoRA ID [Ea29cb2825b53d79065d6fadc]。

### official:official-002-4:oracle

原始gold完整：1；状态：answered。

前缀缓存中，除前缀 token 外，还需要额外哈希（Extra hashes）来使块唯一，其中就包括 LoRA ID；因此即使两个 LoRA 请求的文本相同，也需通过 LoRA ID 区分身份，避免不同 LoRA 适配器的缓存块被混用。[E1ea8fd1c1607655904749488]

### official:official-004-4:P0-T

原始gold完整：1；状态：answered。

vLLM 对 Ampere GPU 的 FP8 支持为 W8A16（weight-only FP8，使用 Marlin kernels），而 W8A8 仅官方支持 Hopper 和 Ada Lovelace GPU [E6922656a68144517af890f74]。因此不能把 vLLM 的 Ampere FP8 精度组合照搬到 SGLang AMD DeepSeekV3；SGLang 相关 PR 针对 AMD 的 FP8 格式是 e4m3fnuz，应核对 PR 中的 e4m3fnuz 格式 [Ea8fb12bdee8f6b3e805f4fe3]。

### official:official-004-4:P1-G

原始gold完整：0；状态：answered。

vLLM 的 FP8 支持中，Ampere GPU 仅支持 W8A16（weight-only FP8，使用 Marlin kernels），而 W8A8 官方仅支持 Hopper 和 Ada Lovelace GPU [E6922656a68144517af890f74]。因此不能把 Ampere 的 FP8 支持照搬到 SGLang AMD DeepSeekV3 场景。FP8 在硬件中通常有两种表示：E4M3（1 符号位、4 指数位、3 尾数位，最大约 ±448）和 E5M2（1 符号位、5 指数位、2 尾数位，最大约 ±57344）[E8c0a6d8da59e340ff546c81b][E510da03c4c044d4ae38ed9f5]。核对 PR 中的 FP8 格式时应确认其使用的是 E4M3 还是 E5M2 [E510da03c4c044d4ae38ed9f5]。

### repository:repo-053-2:P0-T

原始gold完整：1；状态：answered。

这种差异来自 MoE 的条件计算：MoE 把参数分配给多个专家，由路由器为每个 token 选择少数专家，因此“模型保存多少参数”与“一个 token 激活多少参数”可以分别调整 [E00864d864ecb201e2ea3d144]。例如一个 MoE 层可包含 64 个专家 FFN，但每个 token 只选择其中 2 个专家（Top-2）前向计算，于是模型总参数量是 64 个专家参数量之和（很大），而每个 token 的计算量只是 2 个专家的计算量（很小）[Ed7f22cd859de27f70086f9f8]。这就实现了“参数量大但计算量小”：模型有足够容量存储知识，但推理和训练时的计算成本可控 [Ea5dd196eebeaa10b858a92b6]。因此不能认为参数更多每个 token 的计算量就一定更大，总参数决定完整模型的容量，而当前工作由选中的专家、注意力机制类型和调用形状决定 [E92a3cf54c8cecf07cfbb7813]。

### repository:repo-053-2:P1-G

原始gold完整：1；状态：answered。

这种差异来自 MoE 的条件计算：MoE 把参数分配给多个专家，由路由器为每个 token 选择少数专家，因此“模型保存多少参数”与“一个 token 激活多少参数”可以分别调整 [E00864d864ecb201e2ea3d144]。例如一个 MoE 层可包含 64 个专家 FFN，但每个 token 只选择其中 2 个专家（Top-2）前向计算，于是模型总参数量是 64 个专家参数量之和（很大），而每个 token 的计算量只是 2 个专家的计算量（很小）[Ed7f22cd859de27f70086f9f8]。这实现了“参数量大但计算量小”：模型有足够容量存储知识，推理和训练的计算成本可控 [Ea5dd196eebeaa10b858a92b6]。因此不能认为参数更多每个 token 的计算量就一定更大，总参数决定完整模型容量，而当前工作由选中的专家、注意力机制类型和调用形状决定 [E92a3cf54c8cecf07cfbb7813]。

### repository:repo-053-2:Q1

原始gold完整：1；状态：answered。

这种差异可以用 MoE（混合专家）的条件计算来解释：MoE 把参数分配给多个专家，由路由器为每个 token 选择少数专家，因此“模型保存多少参数”与“一个 token 激活多少参数”可以分别调整，batch 内各 token 的选择也会影响实际访问的权重集合 [E00864d864ecb201e2ea3d144]。所以总参数决定完整模型的容量，而每个 token 的实际计算量由选中的专家、注意力机制类型和调用形状决定，参数更多并不必然意味着每 token 计算量更大 [E92a3cf54c8cecf07cfbb7813]。FFN 本身承担“知识库”角色，占据模型大部分参数量以提供存储容量 [E62a5d84042411b933fcd93d4]，而按需激活少数专家就实现了“参数量大但计算量小”的目标——模型有足够容量存储知识，但推理和训练时的计算成本可控 [Ea5dd196eebeaa10b858a92b6]。

