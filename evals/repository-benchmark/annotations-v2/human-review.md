# 等价证据复核清单（AI代审已填写）

复核范围：27条新增判断，涉及37道题。按用户要求由 Codex 代替人工逐题判断；仅记录 AI 复核意见，不自动改动题集、标签或实验结果。

复核人：Codex（AI代审，非独立人工审核）　复核日期：2026-09-26（Asia/Shanghai）

复核结果：37道题中，通过 31，拒绝 0，待补 6。27条证据组中，21条所涉题目全部通过，6条至少有一道待补。
待补题：repo-014-2、repo-020-1、repo-044-2、repo-045-1、repo-049-1、repo-033-2。

### 核查方式与判定范围

- 已读取27条引用的前后段落、章节标题及相关公式；逐题以问题要求为准，参考答案中的延伸内容不自动成为必需事实。
- 本地 `data/upstream/` 三份源仓库 HEAD 与链接 commit 一致；13个被引文件的工作区字节与 `git show <commit>:<path>` 完全相同。补证所用 `06-超节点.md` 同样按固定 commit 校验。核查的是固定版本原文，不依赖可变分支。
- AIInfraGuide：`a3b63eeb81d6d36a3c42c8cfc5a1bdd96e36bab1`；JennyMa11.github.io：`188467456afaff48887869462951a1b5457c0387`；ai-infra-book：`56ecb425b07ea6d16e891cba87bf7db416927d09`。
- 判定针对本清单原有新增证据组。相邻段落可用于理解条件，但未被引用的必需事实必须另行补证；下列建议引用不自动改变当前判定或 v2 标签。多个同一行摘录并非多份独立佐证。
- 不依据检索排名或指标作决定。未重跑检索、选择参数或计算指标。本次不是独立人工标注，原 v2 的“尚需人工核验”状态仍然成立。
- 对 MLA 的实现条件额外核对 [DeepSeek-V2 原论文 v5 §2.1.2–2.1.3](https://arxiv.org/html/2405.04434v5#S2.SS1.SSS2)；其他外部阅读不作为未经映射的新基准证据。

## 判定规则

1. 先读问题，列出必须回答的事实；参考答案也可能有误，不把它当作权威。
2. 打开固定版本的原文链接或经 commit 校验的本地原文，阅读引用前后段落及标题，检查条件、术语、数值、否定和例外。
3. 判断该组全部引用能否共同回答问题。组内是“且”，不同替代组是“或”。只谈同一主题不够。
4. 两种问法逐条判断，不因知识题通过就自动让场景题通过；推导题注明必要计算。
5. 填写通过、拒绝或待补，并写理由。拿不准时标待补，保留来源和缺失事实。

通过：证据支持全部必需事实，且没有依赖无法确认的外部前提。
拒绝：相关但未回答、存在矛盾，或只在不适用的条件下成立。
待补：只有部分事实、需要相邻内容，或发现源文/参考答案可疑。

不得根据是否提高指标决定通过，也不得只凭检索排名判断正确。

## 复核条目

### 01. repo-002-1, repo-002-2

AI接纳理由：明确以Warp内32线程访问模式解释合并事务，支持两种问法。

**repo-002-1**（knowledge）
- 问题：CUDA 全局内存访问合并是以什么线程单位进行的？
- 原参考答案（也需检查）：硬件以Warp为单位将线程的全局内存访问合并为较少事务。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：合并全局内存访问的线程单位是 Warp。
- 判定理由／缺失事实：L338 明确把合并访问放在同一 Warp 内，直接回答线程单位。

**repo-002-2**（scenario）
- 问题：32个CUDA线程同时读显存时，为什么不能简单把它当作32次独立内存事务？
- 原参考答案（也需检查）：硬件以Warp为单位将线程的全局内存访问合并为较少事务。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：同一 Warp 的线程请求可按地址范围合并；事务数由地址、对齐及访问宽度决定。
- 判定理由／缺失事实：引用解释了连续地址可合并成少量事务，不能直接按线程数计事务。题中的32线程须属于同一 Warp；不能保证任意32线程都合并。

**新增原文证据**

- [AIInfraGuide/docs/guides/模块二-CUDA编程与算子优化/CUDA编程入门指南.md，L338–L338](https://github.com/caomaolufei/AIInfraGuide/blob/a3b63eeb81d6d36a3c42c8cfc5a1bdd96e36bab1/docs/guides/%E6%A8%A1%E5%9D%97%E4%BA%8C-CUDA%E7%BC%96%E7%A8%8B%E4%B8%8E%E7%AE%97%E5%AD%90%E4%BC%98%E5%8C%96/CUDA%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8%E6%8C%87%E5%8D%97.md#L338-L338)

> **合并访问（Coalesced Access）** 是全局内存优化的黄金法则：同一个 Warp 内的 32 个线程应该访问连续的内存地址，这样硬件可以将多次访问合并为少量内存事务。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：未发现影响本题结论的错误；适用范围见逐题理由。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 02. repo-014-1, repo-014-2

AI接纳理由：明确局部部分和用AllReduce或ReduceScatter合并；完整输出场景对应归约。

**repo-014-1**（knowledge）
- 问题：Row Parallel线性层如何合并各卡的局部输出？
- 原参考答案（也需检查）：Row Parallel输出是局部部分和，使用求和AllReduce得到完整输出。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：按归约维切分得到部分和，需跨卡求和；完整副本用 AllReduce，分片输出可用 ReduceScatter。
- 判定理由／缺失事实：L2454 明确说明部分和与两种合并方式。参考答案描述完整副本情形，但不应被理解为所有 Row Parallel 都只能用 AllReduce。

**repo-014-2**（scenario）
- 问题：FFN第二层按归约维度切到多卡，各卡只得到部分和，下一层要完整结果时需要什么通信？
- 原参考答案（也需检查）：Row Parallel输出是局部部分和，使用求和AllReduce得到完整输出。
- AI代审判定：□ 通过　□ 拒绝　☑ 待补
- 必需事实／计算：各卡输出相加；若每卡都需完整输出，使用 SUM AllReduce；ReduceScatter 单独只留下分片。
- 判定理由／缺失事实：现有引用并列 AllReduce/ReduceScatter，没有解释输出布局，无法仅凭该组引用确定完整结果为何选 AllReduce。需补完整副本与分片的区别；若只需单一接收卡，通信要求还应另行说明。

**新增原文证据**

- [JennyMa11.github.io/infra/inference_accel_handbook_zh.md，L2454–L2454](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/infra/inference_accel_handbook_zh.md#L2454-L2454)

> Row Parallel 把输入/权重按归约维切分，局部部分和通常通过 AllReduce 或 ReduceScatter 合并。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：参考答案应限定为每个参与 rank 需要完整副本时使用求和 AllReduce；允许下游消费分片时可用 ReduceScatter。

需要补充的原文链接与准确引用：以下为建议补证，尚未写入标签；有待补题的条目在证据组及必要题目修正完成前保留待补判定。

- [固定版本原文 L197–L197](https://github.com/bojieli/ai-infra-book/blob/56ecb425b07ea6d16e891cba87bf7db416927d09/manuscripts/06-%E8%B6%85%E8%8A%82%E7%82%B9.md#L197-L197)
  > 若两张卡都需要完整结果，就执行 AllReduce。若下一个算子可以继续使用分片，则执行 **ReduceScatter（归约后分散）**：先求和，再把求和结果的不同片段留在不同的卡上。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 03. repo-016-1, repo-016-2

AI接纳理由：图注明确dispatch到专家卡、combine返回原卡，并指出两次All-to-All。

**repo-016-1**（knowledge）
- 问题：MoE专家并行中的dispatch和combine两次All-to-All各做什么？
- 原参考答案（也需检查）：dispatch将token发往专家卡，combine将结果发回原卡。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：dispatch 按专家路由发 token 隐状态；combine 将专家输出送回原 token 所在卡。
- 判定理由／缺失事实：图注直接给出两次交换的方向，完整 L308 还明确两次均为 All-to-All；相邻 L304 说明回传后按路由权重合并。

**repo-016-2**（scenario）
- 问题：token按路由跨卡送给专家计算后，还要怎样将结果归回原请求所在卡？
- 原参考答案（也需检查）：dispatch将token发往专家卡，combine将结果发回原卡。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：专家结果经 combine 逆向回传原 token 所在卡，再恢复和合并结果。
- 判定理由／缺失事实：引用明确送回原 A 卡，满足场景所问回传方向；不能把 All-to-All 本身视为自动加权求和。

**新增原文证据**

- [ai-infra-book/manuscripts/09-分布式推理.md，L308–L308](https://github.com/bojieli/ai-infra-book/blob/56ecb425b07ea6d16e891cba87bf7db416927d09/manuscripts/09-%E5%88%86%E5%B8%83%E5%BC%8F%E6%8E%A8%E7%90%86.md#L308-L308)

> 小方块表示一张 A 卡发往一张 B 卡的一组输入，颜色标出它去往哪张 B 卡；dispatch 把各色方块送到同色的 B 卡，combine 再把结果送回原来的 A 卡。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：未发现影响本题结论的错误；适用范围见逐题理由。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 04. repo-018-1, repo-018-2

AI接纳理由：明确将激活离群值的量化难度转移到权重。

**repo-018-1**（knowledge）
- 问题：SmoothQuant针对激活离群值采用什么变换？
- 原参考答案（也需检查）：SmoothQuant用等价变换把激活离群值造成的量化难度转移到权重。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：以等价的通道缩放平滑激活，把离群值造成的量化难度迁移到权重。
- 判定理由／缺失事实：引用直接给出数学等价变换及迁移方向；不要求本题给出缩放系数公式。

**repo-018-2**（scenario）
- 问题：直接W8A8量化被Activation Outlier破坏，哪个方案将量化难度从激活搬到权重？
- 原参考答案（也需检查）：SmoothQuant用等价变换把激活离群值造成的量化难度转移到权重。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：识别 SmoothQuant；其核心是把激活量化难度迁移到权重以支持 W8A8。
- 判定理由／缺失事实：引用明确点名 SmoothQuant 及 INT8 激活，足以选择路线。精度效果仍取决于校准与配置，不能解释为无条件无损。

**新增原文证据**

- [JennyMa11.github.io/infra/inference_accel_handbook_zh.md，L1482–L1482](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/infra/inference_accel_handbook_zh.md#L1482-L1482)

> SmoothQuant 用数学等价变换把难度从激活转移到权重（权重分布更平滑，好量化），从而让激活也能安全地量化到 INT8。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：未发现核心迁移方向错误；“安全地量化到 INT8”是效果概述，不能当作任意配置下无精度损失的保证。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 05. repo-020-1, repo-020-2

AI接纳理由：给出接受和拒绝修正机制，并指出输出服从目标分布的条件。

**repo-020-1**（knowledge）
- 问题：投机采样如何在并行验证的同时保证目标采样分布？
- 原参考答案（也需检查）：Draft猜多个token，Target并行验证，通过拒绝采样保持Target分布。
- AI代审判定：□ 通过　□ 拒绝　☑ 待补
- 必需事实／计算：Draft 生成多候选，Target 一次前向计算候选位置分布，再按序执行接受/拒绝修正；p/q 使用实际采样分布。
- 判定理由／缺失事实：L18 支持严格分布保证和修正规则，却未说明 Target 一次前向并行计算候选位置，缺少问题中的并行验证机制。补 L10、L14 或 L28 后可组成完整证据组。

**repo-020-2**（scenario）
- 问题：小模型先猜若干词再由大模型验证，哪个验收机制才能支持严格的分布正确性？
- 原参考答案（也需检查）：Draft猜多个token，Target并行验证，通过拒绝采样保持Target分布。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：以 min(1,p(x)/q(x)) 接受；拒绝从归一化 [p-q]+ 采样，使用温度和截断处理后实际分布。
- 判定理由／缺失事实：两段引用共同支持接受概率、修正分布与实际采样分布条件，足以回答严格验收机制。

**新增原文证据**

- [JennyMa11.github.io/src/content/blog/speculative-decoding-methods.mdx，L18–L18](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/src/content/blog/speculative-decoding-methods.mdx#L18-L18)

> 精确采样以 $\min(1,p(x)/q(x))$ 的概率接受它；若拒绝，就从归一化后的 $[p-q]_+$ 中采一个修正 Token。

- [JennyMa11.github.io/src/content/blog/speculative-decoding-methods.mdx，L18–L18](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/src/content/blog/speculative-decoding-methods.mdx#L18-L18)

> 这样每一步的结果服从 $p$，前提是使用**实际生效的采样分布**，包括温度、top-k/top-p 等处理。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：未发现影响本题结论的错误；适用范围见逐题理由。

需要补充的原文链接与准确引用：以下为建议补证，尚未写入标签；有待补题的条目在证据组及必要题目修正完成前保留待补判定。

- [固定版本原文 L10–L10](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/src/content/blog/speculative-decoding-methods.mdx#L10-L10)
  > 投机解码先用便宜的方法猜出一串候选，再让目标模型（Target）在一次前向中计算这些位置的分布。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 06. repo-025-1, repo-025-2

AI接纳理由：直接区分全局rank与绑GPU的local_rank，包含多机注意事项。

**repo-025-1**（knowledge）
- 问题：torchrun的local_rank和全局rank有何区别，绑GPU用哪个？
- 原参考答案（也需检查）：local_rank是节点内进程编号，用来绑定本机GPU，不等于全局rank。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：rank 是全局进程编号；local_rank 是节点内编号，常规一卡一进程模式用它绑定本机 CUDA 设备。
- 判定理由／缺失事实：L668 明确区分全局编号和绑卡编号，且警告多机不能用全局 rank 做 set_device。

**repo-025-2**（scenario）
- 问题：第二台机器的进程全局rank为2、3，本机只有GPU0、1，设置CUDA设备应该使用什么编号？
- 原参考答案（也需检查）：local_rank是节点内进程编号，用来绑定本机GPU，不等于全局rank。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：第二台机器使用本机 local_rank=0、1，而非全局 rank=2、3。
- 判定理由／缺失事实：引用的多机警告直接适用；按题设两进程两张可见 GPU 使用节点内编号。设备编号是当前进程可见的 CUDA 编号。

**新增原文证据**

- [AIInfraGuide/docs/guides/模块三-分布式训练/1.2 环境搭建与分布式启动.md，L668–L668](https://github.com/caomaolufei/AIInfraGuide/blob/a3b63eeb81d6d36a3c42c8cfc5a1bdd96e36bab1/docs/guides/%E6%A8%A1%E5%9D%97%E4%B8%89-%E5%88%86%E5%B8%83%E5%BC%8F%E8%AE%AD%E7%BB%83/1.2%20%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA%E4%B8%8E%E5%88%86%E5%B8%83%E5%BC%8F%E5%90%AF%E5%8A%A8.md#L668-L668)

> - `rank` 是全局编号，`local_rank` 决定绑定哪块 GPU（多机时千万别用 rank 去 set_device），`world_size` 是总进程数。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：未发现影响本题结论的错误；适用范围见逐题理由。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 07. repo-032-2

AI接纳理由：明确节省KV容量和访存，足以支持场景题的资源收益问法。

**repo-032-2**（scenario）
- 问题：注意力KV缓存太大但不想减少查询头，分组共享KV头的结构能缓解什么开销？
- 原参考答案（也需检查）：GQA分组共享KV头，MQA仅一组，减少缓存和KV读量。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：分组共享 K/V 头降低 KV Cache 容量和 K/V 读取流量，保留查询头。
- 判定理由／缺失事实：引用直接回答资源收益；不把它扩展为查询侧注意力计算同比下降，也不要求补充未被本题询问的 MQA 定义。

**新增原文证据**

- [JennyMa11.github.io/infra/inference_accel_handbook_zh.md，L605–L605](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/infra/inference_accel_handbook_zh.md#L605-L605)

> > `expand` 不占显存、`reshape` 才物化——所以 GQA 省下的是 **KV Cache 容量**和 **K/V 的访存带宽**，省不掉 Q 侧那一份注意力计算量。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：来源中“reshape 才物化”不是 PyTorch reshape 的普遍规则，是否复制取决于布局；显式展开实现也可能增加临时流量。GQA 缓存减少成立，实际带宽收益取决于内核如何共享读取。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 08. repo-035-2

AI接纳理由：公式包含长度与batch相乘，支持二者翻倍时容量四倍的推导。

**repo-035-2**（scenario）
- 问题：同一模型的序列长度和并发数都翻倍，KV Cache容量大致变为几倍？
- 原参考答案（也需检查）：KV字节数为2×层数×KV头数×头维度×长度×batch×dtype字节数。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：M=C×N×B；N、B 各翻倍，M新/M旧=2×2=4。
- 判定理由／缺失事实：通用公式对序列长度和批大小线性相乘，推导为4倍。模型、KV头数、dtype不变，且不计前缀共享、窗口截断、分页取整等额外因素。

**新增原文证据**

- [AIInfraGuide/docs/guides/模块一-前置知识/transformer/3.8 从Transformer到LLM自回归生成深入理解.md，L349–L349](https://github.com/caomaolufei/AIInfraGuide/blob/a3b63eeb81d6d36a3c42c8cfc5a1bdd96e36bab1/docs/guides/%E6%A8%A1%E5%9D%97%E4%B8%80-%E5%89%8D%E7%BD%AE%E7%9F%A5%E8%AF%86/transformer/3.8%20%E4%BB%8ETransformer%E5%88%B0LLM%E8%87%AA%E5%9B%9E%E5%BD%92%E7%94%9F%E6%88%90%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3.md#L349-L349)

> \text{KV Cache 显存} = 2 \times L \times n_{kv} \times d_h \times N \times B \times b_e

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：参考答案仅给公式，场景答案应补“大致4倍”；公式适用普通全量 K/V 缓存，不能直接套到 MLA latent、共享前缀或滑窗实际占用。

需要补充的原文链接与准确引用：以下为建议补证，尚未写入标签；有待补题的条目在证据组及必要题目修正完成前保留待补判定。

- [固定版本原文 L352–L359](https://github.com/caomaolufei/AIInfraGuide/blob/a3b63eeb81d6d36a3c42c8cfc5a1bdd96e36bab1/docs/guides/%E6%A8%A1%E5%9D%97%E4%B8%80-%E5%89%8D%E7%BD%AE%E7%9F%A5%E8%AF%86/transformer/3.8%20%E4%BB%8ETransformer%E5%88%B0LLM%E8%87%AA%E5%9B%9E%E5%BD%92%E7%94%9F%E6%88%90%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3.md#L352-L359)
  > - $N$：序列长度（seq_len）
  > - $B$：批大小（batch_size）
  > - $b_e$：每个元素的字节数，FP16 为 2 字节，FP8 为 1 字节

本条复核人／日期：Codex（AI代审）／2026-09-26

### 09. repo-044-2

AI接纳理由：明确一次Target验证后仍须顺序接受或拒绝。

**repo-044-2**（scenario）
- 问题：Target一次前向算出了五个候选位置，能否直接提交五个token，验收顺序是什么？
- 原参考答案（也需检查）：减少昂贵Target串行调用，但候选须顺序验证而非一次全部接受。
- AI代审判定：□ 通过　□ 拒绝　☑ 待补
- 必需事实／计算：不能直接提交五个候选；从左到右接受连续前缀，首个拒绝处修正并丢弃后续候选，全通过时才可全部提交。
- 判定理由／缺失事实：引用只说按顺序接受或拒绝，未明确首个拒绝后停止及后续候选作废。它支持顺序处理，但不足以完整回答提交规则。

**新增原文证据**

- [JennyMa11.github.io/infra/inference_accel_handbook_zh.md，L1396–L1396](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/infra/inference_accel_handbook_zh.md#L1396-L1396)

> 投机解码把 Draft 的多个候选交给 Target **一次验证前向**，随后按顺序接受或拒绝。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：原参考答案只说顺序验证，应补首个拒绝后丢弃后续候选及修正，避免误解为仍可逐个验收后续位置。

需要补充的原文链接与准确引用：以下为建议补证，尚未写入标签；有待补题的条目在证据组及必要题目修正完成前保留待补判定。

- [固定版本原文 L14–L14](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/src/content/blog/speculative-decoding-methods.mdx#L14-L14)
  > 一次 Target 前向并行算出候选位置的概率；遇到首个拒绝位置，就丢弃其后的候选。

- [固定版本原文 L18–L18](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/src/content/blog/speculative-decoding-methods.mdx#L18-L18)
  > 若 $\gamma$ 个候选全部通过，还可从 Target 的下一位置再采一个 Token。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 10. repo-045-1

AI接纳理由：给出直接接受概率及正差额归一化修正的等价推导。

**repo-045-1**（knowledge）
- 问题：精确投机采样的接受概率与拒绝后修正分布是什么？
- 原参考答案（也需检查）：以min(1,p/q)接受，拒绝从归一化[p-q]+采样，使用实际温度topk/topp后的分布。
- AI代审判定：□ 通过　□ 拒绝　☑ 待补
- 必需事实／计算：α(x)=min(1,p(x)/q(x))；r(x)=[p(x)-q(x)]+/Σy[p(y)-q(y)]+；p、q 是实际采样分布。
- 判定理由／缺失事实：从 q(x)α(x)=min(p(x),q(x)) 可推得 q(x)>0 时的条件接受概率，修正分布也已给出；但该组未确认温度、top-k/top-p 后的实际分布条件，不能把原始 logits 的 softmax 默认为实际分布。

**新增原文证据**

- [ai-infra-book/manuscripts/08-推理优化.md，L520–L520](https://github.com/bojieli/ai-infra-book/blob/56ecb425b07ea6d16e891cba87bf7db416927d09/manuscripts/08-%E6%8E%A8%E7%90%86%E4%BC%98%E5%8C%96.md#L520-L520)

> 采样到 $x$ 并直接接受它的概率为 $q(x)\alpha(x)=\min(p(x),q(x))$。

- [ai-infra-book/manuscripts/08-推理优化.md，L520–L520](https://github.com/bojieli/ai-infra-book/blob/56ecb425b07ea6d16e891cba87bf7db416927d09/manuscripts/08-%E6%8E%A8%E7%90%86%E4%BC%98%E5%8C%96.md#L520-L520)

> 要达到目标概率 $p(x)$，还差 $[p(x)-q(x)]_+$。

- [ai-infra-book/manuscripts/08-推理优化.md，L520–L520](https://github.com/bojieli/ai-infra-book/blob/56ecb425b07ea6d16e891cba87bf7db416927d09/manuscripts/08-%E6%8E%A8%E7%90%86%E4%BC%98%E5%8C%96.md#L520-L520)

> 因此，拒绝草稿 token 后，将这一正差额归一化，再从得到的分布中重新采样。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：未发现接受/修正公式错误；现有证据组缺实际采样分布条件。q(x)=0 的 token 不会由 q 采出；修正归一化只在发生拒绝时使用。

需要补充的原文链接与准确引用：以下为建议补证，尚未写入标签；有待补题的条目在证据组及必要题目修正完成前保留待补判定。

- [固定版本原文 L18–L18](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/src/content/blog/speculative-decoding-methods.mdx#L18-L18)
  > 这样每一步的结果服从 $p$，前提是使用**实际生效的采样分布**，包括温度、top-k/top-p 等处理。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 11. repo-047-2

AI接纳理由：指出EAGLE从目标中间表示送入较小预测网络，满足场景题的路线选择。

**repo-047-2**（scenario）
- 问题：不想训练完整小语言模型，而想利用Target隐藏特征生成草稿，应考虑哪条投机路线？
- 原参考答案（也需检查）：从Target中间特征预测下一特征并投影候选，需要训练额外网络和对齐特征KV。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：选择利用 Target 隐藏特征的小预测网络路线，例如 EAGLE。
- 判定理由／缺失事实：L564 直接对应目标中间表示送入较小网络。场景只问路线，不要求证据覆盖参考答案中额外的训练和特征 KV 对齐细节。

**新增原文证据**

- [ai-infra-book/manuscripts/08-推理优化.md，L564–L564](https://github.com/bojieli/ai-infra-book/blob/56ecb425b07ea6d16e891cba87bf7db416927d09/manuscripts/08-%E6%8E%A8%E7%90%86%E4%BC%98%E5%8C%96.md#L564-L564)

> EAGLE 类方法将目标模型的中间表示送入较小的预测网络；DFlash 类方法则并行生成多个草稿 token。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：参考答案未点名 EAGLE，建议补方法名；训练额外网络及特征 KV 对齐为扩展描述，不能声称由本组引文全部证明。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 12. repo-049-1, repo-049-2

AI接纳理由：上下文直接匹配重复片段作为草稿，无独立草稿模型生成路径。

**repo-049-1**（knowledge）
- 问题：Prompt Lookup草稿怎样生成，是否需要额外模型权重？
- 原参考答案（也需检查）：Prompt Lookup匹配prompt或历史N-gram取后续token，无额外模型权重，仍需Target验证。
- AI代审判定：□ 通过　□ 拒绝　☑ 待补
- 必需事实／计算：匹配当前后缀 N-gram 在 prompt/历史中的出现位置，取其后续 token；无额外模型权重，仍由 Target 验证。
- 判定理由／缺失事实：引用仅称匹配重复片段、几乎无额外模型开销；未明确取匹配片段的后续 token、零额外模型权重和 Target 验证。不能以“几乎没有”替代明确的权重要求。

**repo-049-2**（scenario）
- 问题：代码编辑输出经常复制上下文且没有显存放草稿模型，应采用什么候选生成路线？
- 原参考答案（也需检查）：Prompt Lookup匹配prompt或历史N-gram取后续token，无额外模型权重，仍需Target验证。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：选择 Prompt Lookup / N-gram，从既有文本匹配并复制候选，适合重复较多的代码编辑。
- 判定理由／缺失事实：本组直接描述从上下文取得候选，属于无需运行独立草稿模型的文本匹配路径，满足路线选择；“几乎没有额外模型开销”不意味着匹配索引、CPU 工作和验证全无成本。

**新增原文证据**

- [JennyMa11.github.io/infra/inference_accel_handbook_zh.md，L1644–L1644](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/infra/inference_accel_handbook_zh.md#L1644-L1644)

> 直接从 Prompt 或历史生成内容中匹配重复片段作为候选，几乎没有额外模型开销。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：“几乎没有额外模型开销”不足以独立证明知识题要求的无额外权重和验证流程；场景路线选择可以据直接文本匹配判断。

需要补充的原文链接与准确引用：以下为建议补证，尚未写入标签；有待补题的条目在证据组及必要题目修正完成前保留待补判定。

- [固定版本原文 L48–L48](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/src/content/blog/speculative-decoding-methods.mdx#L48-L48)
  > 从当前输出末尾取一段 N-gram，在 Prompt 或已生成历史中找相同片段，把它后面的 Token 当作候选。

- [固定版本原文 L48–L48](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/src/content/blog/speculative-decoding-methods.mdx#L48-L48)
  > 它没有额外模型权重，特别适合代码编辑、引用和基于材料的回答；上下文少、措辞新颖时则可能找不到可用片段。

- [固定版本原文 L48–L48](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/src/content/blog/speculative-decoding-methods.mdx#L48-L48)
  > 候选仍交给 Target 验证，匹配成功本身不代表被接受。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 13. repo-050-1, repo-050-2

AI接纳理由：明确输出包括修正/额外token且比接受Draft数多1，并给出0.8/4的3.36例子。

**repo-050-1**（knowledge）
- 问题：投机解码期望输出token数与接受的Draft数为什么不同？
- 原参考答案（也需检查）：平均输出含修正或额外token，多于已接受draft；收益还取决于draft验证调度总耗时。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：每轮输出包含已接受 Draft 前缀，另加首个拒绝处的修正 token 或全通过后的额外 token。
- 判定理由／缺失事实：两段引用直接说明两类额外输出及减1关系，回答为什么输出数不同；参考答案的耗时收益是延伸事实，不是本题必需事实。

**repo-050-2**（scenario）
- 问题：接受率0.8且草稿长4时报告2.36个接受草稿，为何每轮实际期望输出约3.36个？
- 原参考答案（也需检查）：平均输出含修正或额外token，多于已接受draft；收益还取决于draft验证调度总耗时。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：E接受=0.8+0.8²+0.8³+0.8⁴=2.3616；E输出=1+E接受=3.3616≈3.36。
- 判定理由／缺失事实：公式和示例共同支持数值；假设各位置在此前均接受时的条件接受率恒为0.8，并采用每轮增加一个修正/额外 token 的标准流程，无 EOS/长度上限提前停止。

**新增原文证据**

- [JennyMa11.github.io/infra/inference_accel_handbook_zh.md，L1594–L1594](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/infra/inference_accel_handbook_zh.md#L1594-L1594)

> > **期望输出数**（含首个拒绝后的修正 Token，或全接受后的额外 Token）`E = (1 − α^(γ+1)) / (1 − α)`：α=0.8、γ=4 → **3.36**；

- [JennyMa11.github.io/infra/inference_accel_handbook_zh.md，L1594–L1594](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/infra/inference_accel_handbook_zh.md#L1594-L1594)

> 单算被接受的 Draft Token 数，应从这里减去 1。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：参考答案应补每轮多一个 token 及恒定条件接受率假设；EOS、长度限制等提前停止时不能机械套用 +1。

需要补充的原文链接与准确引用：以下为建议补证，尚未写入标签；有待补题的条目在证据组及必要题目修正完成前保留待补判定。

- [固定版本原文 L60–L64](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/src/content/blog/speculative-decoding-methods.mdx#L60-L64)
  > 若每个位置的条件接受率近似为常数 $\alpha$，一次投机轮次的**期望输出 Token 数**（含首个拒绝后的修正 Token，或全接受后的额外 Token）约为
  L64 给出接受 Draft 数；L64 提醒总收益需比较 Draft、Target 验证和调度/构树耗时。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 14. repo-053-1, repo-053-2

AI接纳理由：明确更大总参数与每token少数专家激活的区分。

**repo-053-1**（knowledge）
- 问题：MoE为什么能区分总参数量与每token激活参数量？
- 原参考答案（也需检查）：MoE路由少数专家，使总保存参数和每token激活参数可分别调整。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：总参数包含所有专家；单 token 只路由少数专家，故激活参数量小于总保存参数量。
- 判定理由／缺失事实：引用直接区分较大总量和较小激活量。可通过专家总数与所选数量调节，但两者并非任意独立且完全无约束。

**repo-053-2**（scenario）
- 问题：模型参数很大但每token只运行少数FFN子网络，应该怎样解释其存储与计算规模差异？
- 原参考答案（也需检查）：MoE路由少数专家，使总保存参数和每token激活参数可分别调整。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：存储覆盖全部专家参数，计算只使用本 token 被路由的少数专家及公共部分。
- 判定理由／缺失事实：引用明确每 token 仅激活少数专家，足以解释存储与计算规模差异；不能据此将激活参数量直接等同于总实际延迟。

**新增原文证据**

- [AIInfraGuide/docs/guides/模块一-前置知识/transformer/3.7 Transformer Decoder Block完整解析.md，L716–L716](https://github.com/caomaolufei/AIInfraGuide/blob/a3b63eeb81d6d36a3c42c8cfc5a1bdd96e36bab1/docs/guides/%E6%A8%A1%E5%9D%97%E4%B8%80-%E5%89%8D%E7%BD%AE%E7%9F%A5%E8%AF%86/transformer/3.7%20Transformer%20Decoder%20Block%E5%AE%8C%E6%95%B4%E8%A7%A3%E6%9E%90.md#L716-L716)

> DeepSeek-V3 和 Mixtral 采用混合专家模型，用更大的总参数量但更少的激活参数量（每个 token 只激活少数专家）来提升效果。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：未发现影响本题结论的错误；适用范围见逐题理由。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 15. repo-070-1, repo-070-2

AI接纳理由：说明保留输入、反向重算中间值，实现计算换激活显存。

**repo-070-1**（knowledge）
- 问题：激活重计算如何用额外计算换取训练显存？
- 原参考答案（也需检查）：仅存部分前向激活，反向使用前重算，以额外计算换保存空间。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：前向只保留检查点（如层输入），反向按需重算其他中间激活，以额外计算换保存空间。
- 判定理由／缺失事实：引用直接给出保留输入与重算中间值的机制。所列显存比例和33%计算开销为近似估计，不是普适保证。

**repo-070-2**（scenario）
- 问题：参数已经分片但前向激活仍占太多显存，还可以在哪些中间结果上选择保存或重算？
- 原参考答案（也需检查）：仅存部分前向激活，反向使用前重算，以额外计算换保存空间。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：可保存层/子模块边界输入，舍弃其内部前向中间激活，在反向用到前重算。
- 判定理由／缺失事实：层输入与中间值的保存/重算选择直接回答场景；这减少激活显存，与参数分片处理不同内存项。

**新增原文证据**

- [AIInfraGuide/docs/guides/模块一-前置知识/transformer/3.7 Transformer Decoder Block完整解析.md，L613–L613](https://github.com/caomaolufei/AIInfraGuide/blob/a3b63eeb81d6d36a3c42c8cfc5a1bdd96e36bab1/docs/guides/%E6%A8%A1%E5%9D%97%E4%B8%80-%E5%89%8D%E7%BD%AE%E7%9F%A5%E8%AF%86/transformer/3.7%20Transformer%20Decoder%20Block%E5%AE%8C%E6%95%B4%E8%A7%A3%E6%9E%90.md#L613-L613)

> 使用 Activation Checkpointing（只保存每层输入，反向时重新计算中间值）可以将激活值显存减少到约 1/3 到 1/5，代价是增加约 33% 的计算量。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：来源的1/3至1/5显存和33%计算开销不是通用常数，取决于检查点粒度、实现与模型。核心机制无误。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 16. repo-001-1

AI接纳理由：候选明确给出Warp最小调度单位及32个连续线程。

**repo-001-1**（knowledge）
- 问题：CUDA 中 Warp 是什么单位，通常包含多少线程？
- 原参考答案（也需检查）：Warp 是硬件调度执行的基本单位，包含32个连续线程。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：Warp 是 CUDA 硬件调度执行的基本单位，通常有32个按线性线程编号连续的线程。
- 判定理由／缺失事实：引用直接支持单位和线程数；不把相邻 SIMT 描述扩展为所有架构上所有 lane 永远锁步或不存在分支发散。

**新增原文证据**

- [AIInfraGuide/docs/guides/模块二-CUDA编程与算子优化/CUDA编程入门指南.md，L399–L399](https://github.com/caomaolufei/AIInfraGuide/blob/a3b63eeb81d6d36a3c42c8cfc5a1bdd96e36bab1/docs/guides/%E6%A8%A1%E5%9D%97%E4%BA%8C-CUDA%E7%BC%96%E7%A8%8B%E4%B8%8E%E7%AE%97%E5%AD%90%E4%BC%98%E5%8C%96/CUDA%E7%BC%96%E7%A8%8B%E5%85%A5%E9%97%A8%E6%8C%87%E5%8D%97.md#L399-L399)

> Warp 是 GPU 执行的最小调度单位，由 **32 个连续线程** 组成。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：“32个连续线程”指同一 block 内线性线程编号；相邻的锁步与发散减半比喻不能推广为所有现代架构的严格执行规律。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 17. repo-005-2

AI接纳理由：候选直接给出算术强度FLOPs/Bytes及每字节参与计算的解释。

**repo-005-2**（scenario）
- 问题：矩阵乘计算很快但显存搬运拖慢吞吐，增加tile内数据复用希望改变哪项计算与访存的比例？
- 原参考答案（也需检查）：通过数据复用提高每字节参与的计算量，即算术强度。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：提高算术强度 I=F/V，即每访问一字节数据完成更多 FLOPs。
- 判定理由／缺失事实：引用定义了所问比值，tile 复用减少同一计算所需的外部数据搬运，因此提高 I；不保证提高后吞吐必然同比增加。

**新增原文证据**

- [AIInfraGuide/docs/guides/模块四-推理优化/第1章-LLM推理基础/1.1-LLM推理基础.md，L202–L202](https://github.com/caomaolufei/AIInfraGuide/blob/a3b63eeb81d6d36a3c42c8cfc5a1bdd96e36bab1/docs/guides/%E6%A8%A1%E5%9D%97%E5%9B%9B-%E6%8E%A8%E7%90%86%E4%BC%98%E5%8C%96/%E7%AC%AC1%E7%AB%A0-LLM%E6%8E%A8%E7%90%86%E5%9F%BA%E7%A1%80/1.1-LLM%E6%8E%A8%E7%90%86%E5%9F%BA%E7%A1%80.md#L202-L202)

> \text{算术强度} = \frac{\text{浮点运算次数 (FLOPs)}}{\text{访存字节数 (Bytes)}}

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：未发现影响本题结论的错误；适用范围见逐题理由。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 18. repo-006-2

AI接纳理由：候选给出新最大值下旧指数和乘exp(m_old-m_new)的修正。

**repo-006-2**（scenario）
- 问题：分块处理Softmax时后一个块出现更大的最大值，先前累计的指数和需要怎样处理？
- 原参考答案（也需检查）：一次扫描同时维护max和sum，新最大值出现时修正累计sum。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：m新=max(m旧,当前块最大值)，旧指数和乘 exp(m旧-m新)，再加新块在 m新 基准下的指数和。
- 判定理由／缺失事实：引用明确旧和的换基因子，适用于逐元素也适用于块合并；参考答案缺少具体因子，以上给出可执行的答案。

**新增原文证据**

- [AIInfraGuide/docs/guides/模块一-前置知识/transformer/3.3 Self-Attention机制深入理解.md，L494–L494](https://github.com/caomaolufei/AIInfraGuide/blob/a3b63eeb81d6d36a3c42c8cfc5a1bdd96e36bab1/docs/guides/%E6%A8%A1%E5%9D%97%E4%B8%80-%E5%89%8D%E7%BD%AE%E7%9F%A5%E8%AF%86/transformer/3.3%20Self-Attention%E6%9C%BA%E5%88%B6%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3.md#L494-L494)

> 关键技巧在第二行：当最大值从 $m_{i-1}$ 更新到 $m_i$ 时，之前累积的指数和 $d_{i-1}$ 需要乘以一个修正因子 $\exp(m_{i-1} - m_i)$ 来"换基"。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：参考答案未给所问缩放因子，建议补 exp(m旧-m新)；一次扫描维护统计不代表只扫描一次就输出所有归一化元素。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 19. repo-024-2

AI接纳理由：候选明确说明Nsight Compute深挖确定的Kernel。

**repo-024-2**（scenario）
- 问题：已经看到某个CUDA Kernel变慢，想从全链路trace进一步看Kernel内部指标，应使用哪个工具？
- 原参考答案（也需检查）：torch.profiler算子级，Nsight Systems全链路，Nsight Compute Kernel级。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：已定位 CUDA Kernel 后用 Nsight Compute 查看 Kernel 内部性能指标。
- 判定理由／缺失事实：引用明确 Compute 深挖确定 Kernel，并区分 Systems 时间线和 profiler 的 op 对应，直接适用。

**新增原文证据**

- [JennyMa11.github.io/infra/inference_accel_handbook_zh.md，L2111–L2111](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/infra/inference_accel_handbook_zh.md#L2111-L2111)

> Nsight Systems 看时间线和空隙；Nsight Compute 深挖一个确定的 Kernel；`torch.profiler` 看 PyTorch op 与 Kernel 对应关系。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：未发现影响本题结论的错误；适用范围见逐题理由。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 20. repo-028-2

AI接纳理由：候选明确说明同一地址广播是bank冲突的例外。

**repo-028-2**（scenario）
- 问题：32个线程同时读取同一共享内存地址，会像同bank不同地址那样串行化32次吗？
- 原参考答案（也需检查）：同一bank同一地址访问可广播，不构成不同地址的bank冲突。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：同一 Warp 同时读取同一共享内存地址可广播，不是同 bank 不同地址导致的32路冲突。
- 判定理由／缺失事实：引用明确广播例外，故不会因32线程读同一地址而串行化32次；不扩展为同址写入也具有相同语义。

**新增原文证据**

- [JennyMa11.github.io/infra/inference_accel_handbook_zh.md，L307–L307](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/infra/inference_accel_handbook_zh.md#L307-L307)

> **Bank Conflict**：共享内存同一 Warp 不同地址落同一 bank 会冲突；广播同地址是例外。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：未发现影响本题结论的错误；适用范围见逐题理由。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 21. repo-033-2

AI接纳理由：候选明确说明缓存c_KV需要上投影还原K/V。

**repo-033-2**（scenario）
- 问题：模型缓存的是低维c_KV而不是每个head完整键值，取出后为什么还需上投影？
- 原参考答案（也需检查）：MLA是低秩压缩KV表示，latent需上投影还原，解耦RoPE将位置信息单独处理。
- AI代审判定：□ 通过　□ 拒绝　☑ 待补
- 必需事实／计算：c_KV 是压缩 latent；显式计算路径用上投影得到 K/V，但吸收上投影矩阵的实现可以不物化完整 K/V。
- 判定理由／缺失事实：引用支持未吸收矩阵时的重建解释，却把推理描述为必需还原。问题和参考答案缺少实现条件；DeepSeek-V2 原论文说明可将上投影吸收到 Q/输出投影，避免显式计算 K/V，应先修正前提。

**新增原文证据**

- [JennyMa11.github.io/infra/inference_accel_handbook_zh.md，L628–L628](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/infra/inference_accel_handbook_zh.md#L628-L628)

> - 传统做法缓存 `K` 和 `V` 两个 `[head_dim × num_heads]` 张量；MLA 改为缓存一个低维 `c_KV`（latent），推理时通过上投影矩阵还原出 K/V。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：问题“取出后还需上投影”和参考答案“latent需上投影还原”应限定为显式展开实现；优化的 MLA 可吸收矩阵避免物化 K/V。来源 L632 的“多一次上投影”也过于绝对。

需要补充的原文链接与准确引用：以下为建议补证，尚未写入标签；有待补题的条目在证据组及必要题目修正完成前保留待补判定。

- [DeepSeek-V2 固定论文版本 v5，§2.1.2（式9–11后）及 §2.1.3](https://arxiv.org/html/2405.04434v5#S2.SS1.SSS2)
  转述核查结论：论文给出低秩重建公式，同时说明推理可把 K/V 上投影矩阵分别吸收到查询/输出投影，不必显式计算完整 K/V；解耦 RoPE 保留该优化路径。该来源仅用于指出题目/来源的限制，尚未纳入固定语料证据映射。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 22. repo-034-1

AI接纳理由：候选说明分块更新m、ell和u后丢弃分数概率，省去完整S和P。

**repo-034-1**（knowledge）
- 问题：FlashAttention为什么不需要保存完整N×N注意力矩阵？
- 原参考答案（也需检查）：分块进SRAM并在线softmax，不物化完整N×N注意力矩阵。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：按块计算注意力并递推最大值 m、指数和 ℓ、未归一化输出 u，块内分数/概率用完丢弃。
- 判定理由／缺失事实：两段引用共同说明状态更新与缓冲复用，使完整 S/P 不必保存。是精确注意力的执行方式变化，仍有浮点舍入差异。

**新增原文证据**

- [ai-infra-book/manuscripts/05-算子与运行时.md，L441–L441](https://github.com/bojieli/ai-infra-book/blob/56ecb425b07ea6d16e891cba87bf7db416927d09/manuscripts/05-%E7%AE%97%E5%AD%90%E4%B8%8E%E8%BF%90%E8%A1%8C%E6%97%B6.md#L441-L441)

> FlashAttention 正是利用这一递推关系省去了完整 S 和 P 的存储。

- [ai-infra-book/manuscripts/05-算子与运行时.md，L441–L441](https://github.com/bojieli/ai-infra-book/blob/56ecb425b07ea6d16e891cba87bf7db416927d09/manuscripts/05-%E7%AE%97%E5%AD%90%E4%B8%8E%E8%BF%90%E8%A1%8C%E6%97%B6.md#L441-L441)

> 每处理完一块，就更新 m、$\ell$ 和 u；该块的分数和概率用完即可丢弃，其缓冲可以留给下一块。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：未发现影响本题结论的错误；适用范围见逐题理由。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 23. repo-034-2

AI接纳理由：候选解释分块、在线归约与融合共同减少中间写回。

**repo-034-2**（scenario）
- 问题：希望降低精确Attention的HBM中间矩阵读写，如何把分块和在线Softmax组合起来？
- 原参考答案（也需检查）：分块进SRAM并在线softmax，不物化完整N×N注意力矩阵。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：把当前块放入快速存储，用在线 Softmax 跨块更新统计和输出累加器，融合块内计算以减少 HBM 写回。
- 判定理由／缺失事实：引用明确分块、在线归约与融合的分工，回答如何组合；不把相邻实验中某硬件某形状的加速比推广到所有负载。

**新增原文证据**

- [ai-infra-book/manuscripts/05-算子与运行时.md，L475–L475](https://github.com/bojieli/ai-infra-book/blob/56ecb425b07ea6d16e891cba87bf7db416927d09/manuscripts/05-%E7%AE%97%E5%AD%90%E4%B8%8E%E8%BF%90%E8%A1%8C%E6%97%B6.md#L475-L475)

> 这组完整实现的对照说明了分块、在线归约和融合如何配合：分块使当前数据能放入快速存储，在线归约使 Softmax 可以逐块计算，融合省去块内中间结果的写回。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：未发现影响本题结论的错误；适用范围见逐题理由。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 24. repo-057-2

AI接纳理由：候选直接给出算术强度等于运算次数除以访存字节数。

**repo-057-2**（scenario）
- 问题：评估一个算子每次搬运32MiB数据做多少运算，应计算哪项比值来判断带宽瓶颈？
- 原参考答案（也需检查）：算术强度I=F/V，单位由计算量与数据访问字节量决定。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：I=F/V；若 V=32 MiB，则 I=F/(32×2²⁰) FLOP/Byte。
- 判定理由／缺失事实：公式直接支持所问比值，MiB 必须换成字节。未给 F，不能算出具体强度；判断瓶颈还需与硬件峰值算力/带宽平衡点或实测比较。

**新增原文证据**

- [AIInfraGuide/docs/guides/模块四-推理优化/第1章-LLM推理基础/1.1-LLM推理基础.md，L202–L202](https://github.com/caomaolufei/AIInfraGuide/blob/a3b63eeb81d6d36a3c42c8cfc5a1bdd96e36bab1/docs/guides/%E6%A8%A1%E5%9D%97%E5%9B%9B-%E6%8E%A8%E7%90%86%E4%BC%98%E5%8C%96/%E7%AC%AC1%E7%AB%A0-LLM%E6%8E%A8%E7%90%86%E5%9F%BA%E7%A1%80/1.1-LLM%E6%8E%A8%E7%90%86%E5%9F%BA%E7%A1%80.md#L202-L202)

> \text{算术强度} = \frac{\text{浮点运算次数 (FLOPs)}}{\text{访存字节数 (Bytes)}}

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：无核心公式错误；算术强度单独不能确认带宽瓶颈，需硬件平衡点或测量。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 25. repo-060-2

AI接纳理由：候选指出相同总量因物理路径及网卡字节分布不同而耗时不同。

**repo-060-2**（scenario）
- 问题：两个方案每卡发送相同字节数但通信耗时不同，为什么还要分析实际路径和共享接口？
- 原参考答案（也需检查）：集合算法规定逻辑发送接收，拓扑决定物理路径，共享接口会竞争带宽。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：同样逻辑发送字节可走不同物理路径，分布到不同网卡/共享链路，带宽竞争影响完成时间。
- 判定理由／缺失事实：完整 L1017 比较总量相同但跨机字节和使用网卡数不同，足以说明应分析资源路径；共享竞争的具体限速还需按实际拓扑计算。

**新增原文证据**

- [ai-infra-book/manuscripts/07-数据中心网络.md，L1017–L1017](https://github.com/bojieli/ai-infra-book/blob/56ecb425b07ea6d16e891cba87bf7db416927d09/manuscripts/07-%E6%95%B0%E6%8D%AE%E4%B8%AD%E5%BF%83%E7%BD%91%E7%BB%9C.md#L1017-L1017)

> **误区：发送总量相同，通信耗时就相同。

- [ai-infra-book/manuscripts/07-数据中心网络.md，L1017–L1017](https://github.com/bojieli/ai-infra-book/blob/56ecb425b07ea6d16e891cba87bf7db416927d09/manuscripts/07-%E6%95%B0%E6%8D%AE%E4%B8%AD%E5%BF%83%E7%BD%91%E7%BB%9C.md#L1017-L1017)

> 传输时间取决于数据经过哪些资源，参与者的排列改变了每张网卡分到的字节。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：首段引用只有加粗开标记，属于截取格式问题；源 L1017 的误区标题有完整闭合标记，否定语义完整。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

### 26. repo-065-1

AI接纳理由：候选说明通过块表的物理块号与块内偏移读取分散KV。

**repo-065-1**（knowledge）
- 问题：KV分页的逻辑块与物理块怎样通过块表关联？
- 原参考答案（也需检查）：块表按逻辑token位置映射到物理块，物理可分散，新增块按需分配。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：逻辑 token 位置先确定逻辑块和块内偏移，块表映射到物理块号，从可分散物理块读取 KV。
- 判定理由／缺失事实：L92 直接给出映射和寻址要素，回答块表关联问题。参考答案的新增块按需分配不属于本题必需事实，可另引 L90。

**新增原文证据**

- [AIInfraGuide/docs/guides/模块四-推理优化/第2章-推理引擎核心技术/2.1-PagedAttention.md，L92–L92](https://github.com/caomaolufei/AIInfraGuide/blob/a3b63eeb81d6d36a3c42c8cfc5a1bdd96e36bab1/docs/guides/%E6%A8%A1%E5%9D%97%E5%9B%9B-%E6%8E%A8%E7%90%86%E4%BC%98%E5%8C%96/%E7%AC%AC2%E7%AB%A0-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E%E6%A0%B8%E5%BF%83%E6%8A%80%E6%9C%AF/2.1-PagedAttention.md#L92-L92)

> Attention 计算时，CUDA Kernel 通过 Block Table 拿到每个逻辑位置对应的 `physical_block_number`（物理块号）和 `physical_block_offset`（块内偏移），就能从分散的物理块里正确读到所有历史 KV。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：未发现影响本题结论的错误；适用范围见逐题理由。

需要补充的原文链接与准确引用：以下为建议补证，尚未写入标签；有待补题的条目在证据组及必要题目修正完成前保留待补判定。

- [固定版本原文 L90–L90](https://github.com/caomaolufei/AIInfraGuide/blob/a3b63eeb81d6d36a3c42c8cfc5a1bdd96e36bab1/docs/guides/%E6%A8%A1%E5%9D%97%E5%9B%9B-%E6%8E%A8%E7%90%86%E4%BC%98%E5%8C%96/%E7%AC%AC2%E7%AB%A0-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E%E6%A0%B8%E5%BF%83%E6%8A%80%E6%9C%AF/2.1-PagedAttention.md#L90-L90)
  > 逻辑块 2 还剩 3 格，能再接 3 个 Token；填满后（生成到第 12 个 Token），vLLM 才**按需**再申请一个新物理块挂到逻辑块 3

本条复核人／日期：Codex（AI代审）／2026-09-26

### 27. repo-065-2

AI接纳理由：候选明确给出逻辑块到不连续物理块的映射与碎片定义。

**repo-065-2**（scenario）
- 问题：缓存空闲空间分散而无法分配大连续区域，如何让一条序列跨不连续物理块存储？
- 原参考答案（也需检查）：块表按逻辑token位置映射到物理块，物理可分散，新增块按需分配。
- AI代审判定：☑ 通过　□ 拒绝　□ 待补
- 必需事实／计算：按固定大小块存 KV，用块表关联连续逻辑块与不连续物理块，无须一条序列占连续大区域。
- 判定理由／缺失事实：引用明确逻辑块号到物理块号的映射和物理不连续，直接解决外部碎片场景；不意味着块内空余或所有分配器碎片都消失。

**新增原文证据**

- [JennyMa11.github.io/infra/inference_accel_handbook_zh.md，L801–L801](https://github.com/JennyMa11/JennyMa11.github.io/blob/188467456afaff48887869462951a1b5457c0387/infra/inference_accel_handbook_zh.md#L801-L801)

> Block Table 记录「逻辑块号 → 物理块号」的映射，物理块可以不连续。

原文上下文／适用条件已核查：☑（核对本地固定 commit 原文；判定仅针对上列新增引用，不能把相邻事实自动计入该证据组）

发现参考答案或来源错误：无核心映射错误；分页缓解外部碎片，仍可有末块内部空余。

需要补充的原文链接与准确引用：无必需补充；现有引用已覆盖本题所问核心事实。

本条复核人／日期：Codex（AI代审）／2026-09-26

## 复核后的版本处理

本文件已完成 AI 代审填写，包括全部待补理由与补证建议；尚未生成 v3，也不将 AI 复核改记为人工批准。下述为后续版本处理规则。

保留原始v1和AI补标v2；正式采纳复核意见后另建v3，明确记录 AI 或人工的实际复核方式，记录复核人、时间、决定、理由与原文证据。
拒绝只移除被否定的替代证据，不自动删除问题或原有证据。新增引用重新校验文件hash、行号和分块映射。
用固定v3标注重新计算各组已有逐题结果，区分标注修正与算法提升。需要重新检索时保持配置一致。
dev用于调参；test标注复核以原文事实为准，不能据test表现选择检索参数。
