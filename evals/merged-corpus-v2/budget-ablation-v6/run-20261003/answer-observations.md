# v6 逐案AI观察（独立人工审核pending）

[实际答案与证据](answer-case-traces.json) · [全量人工待审模板](answer-review.json)

repo-002-1只问“CUDA全局内存访问合并是以什么线程单位进行的？”。baseline两次均额外声称同一warp的32线程必须访问连续地址；候选第一次也这样声称，第二次又复述连续地址一次事务满足所有线程。Q1两次仅答warp单位及硬件尝试合并成最少事务，未添加这两个错误条件，原gold均完整交付。连续地址建议段E520a10cc6fe3aeb315213e6d仍在上下文，规则没有隔离正确建议，因而该修复不能保证以后不会再犯。

技术范围：NVIDIA对CC>=6.0给出32线程访问相邻float时四个32B事务，并允许部分线程参与、同字访问和地址排列变化。因此把“全部32线程连续”当无条件必要条件、或“连续就一次事务”当无架构限制结论都过强。[NVIDIA CUDA13.0.1 §10.2.1.1](https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-best-practices-guide/index.html#a-simple-access-pattern)

repo-053-2问MoE参数容量与每token工作的区别。baseline、候选各两次都复述了源文“一个层64专家”例子中的整模总量等式。Q1两次均说明总参数存储与少数专家激活可以分开调整，不再列出该等式。专家层和整模须区分，整模还包含专家以外的组件；Switch论文图2展示稀疏FFN及自注意力等组件，为范围审核的一个具体架构例，而非所有MoE的固定组成公式。[Switch Transformers论文图2](https://jmlr.org/papers/volume23/21-0998/21-0998.pdf)

official-002-1缓存额外身份和official-004-4跨vLLM/SGLang、GPU架构/FP8格式问题，两配置及Q1各两次保留目标事实、全部完整交付。Q1在这两题与候选上下文相同，两次独立重生成只检验波动，不是隔离带来的效果。

official-002-4两配置都缺缓存键必要证据，两次均拒答，没有复现上轮仅凭LoRA全局ID推导缓存键规则的错误。official-014-4没有私有部署P95资料；baseline一次明确说不能给数值但status为answered、一次拒答，候选两次拒答。不能把前者仅凭status标成捏造事实。

以上为有限AI审阅，不能填写独立人工事实正确率。未隔离候选数值门槛通过但仍有两类已知风险；隔离候选为下一轮开发候选，未切换默认或启动确认集。
