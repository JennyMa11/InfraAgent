// Static snapshot of reviewed Q&A and retrieval evidence from this repository.
// No network requests are made by the demo.

export const RESULTS = [
  {
    id: "gqa",
    domain: "推理引擎",
    question: "GQA 与 MQA 如何共享 K/V Head，主要减少什么资源？",
    aliases: [
      "GQA", "MQA", "KV Head", "K/V Head", "KV Cache", "共享 KV",
      "分组查询注意力", "GQA 省了什么", "GQA 到底省下了什么", "查询头",
    ],
    answer: `GQA 与 MQA 都通过共享 K/V Head 来缩小 KV Cache 和 K/V 访存带宽。MQA 是极端情况，只有一组 K/V；GQA 是 Query Head 分组共享 K/V 的折中方案，可以按需调节 KV Head 数，在压缩比与模型质量之间取得平衡。[Eccc4f6e7f0cb7c7e540a23fd] [E37f4fe79698689e3684580fa]

省下的是 KV Cache 容量和 K/V 访存带宽，并不省掉 Q 侧那一份注意力计算量。Llama-2 70B 用 64 个 Q Head 对 8 个 KV Head，KV Cache 直接降到 1/8。[E37f4fe79698689e3684580fa]`,
    citations: [
      {
        id: "Eccc4f6e7f0cb7c7e540a23fd",
        repo: "JennyMa11.github.io",
        section: "5.2 GQA / MQA",
        file: "inference_accel_handbook_zh.md",
        locator: "#L572–L575",
        kind: "text",
        channels: ["关键词", "向量"],
        content: String.raw`## 5.2 GQA / MQA

**速查**：GQA 让多个 Query Head 共享一组 K/V Head（\`num_kv_heads < num_q_heads\`），MQA 是极端情况（只有 1 组 K/V）。直接减少 KV Cache 大小和 Attention 的 K/V 访存量；质量影响取决于模型训练与 Head 配置。`,
      },
      {
        id: "E37f4fe79698689e3684580fa",
        repo: "JennyMa11.github.io",
        section: "5.2 GQA / MQA",
        file: "inference_accel_handbook_zh.md",
        locator: "#L605–L612",
        kind: "text",
        channels: ["关键词", "向量"],
        content: String.raw`> \`expand\` 不占显存、\`reshape\` 才物化——所以 GQA 省下的是 **KV Cache 容量**和 **K/V 的访存带宽**，省不掉 Q 侧那一份注意力计算量。

- Llama-2 70B：64 个 Q Head，8 个 KV Head → KV Cache 直接降到 1/8。
- Llama-3、Qwen 等新一代模型普遍采用 GQA。
- 代价：K/V 表达能力下降，但实验表明在合理分组下质量损失很小。

**追问：GQA 相比 MQA 好在哪？**
> MQA 压得太狠（1 组 K/V），质量下降明显且训练不稳定；GQA 在 MQA 的压缩比和 MHA 的质量之间取折中，可以按需调节 KV Head 数（如 8 组），是当前的工业标准。`,
      },
    ],
    trace: { candidates: 5, retrievalMs: 203, generateMs: 5916, model: "qwen3:4b" },
  },

  {
    id: "smoothquant",
    domain: "推理引擎",
    question: "SmoothQuant 针对激活离群值采用什么变换？",
    aliases: [
      "SmoothQuant", "平滑量化", "激活离群值", "Activation Outlier",
      "W8A8", "离群值", "量化难度", "量化", "outlier",
    ],
    answer: `SmoothQuant 用数学等价变换，把激活离群值的量化难度迁移到权重上，使权重分布更平滑，从而让 W8A8 量化可行。[Edb322feef5bf9daf97064b62] [Ef4a78e64cafdf85f781ab28b] [Eac81a30f66147322eb0a8e24]

它不改变模型输出，只改变量化时把误差压力放在哪一侧。激活中的少数大幅值通道会把 per-tensor scale 撑大，其余通道的分辨率因此变差。[Edb322feef5bf9daf97064b62] [Eb1cb5ed94dc862d5729051ef]`,
    citations: [
      {
        id: "Edb322feef5bf9daf97064b62",
        repo: "JennyMa11.github.io",
        section: "W8A8 量化",
        file: "inference_accel_handbook_zh.md",
        locator: "#L1481–L1482",
        kind: "text",
        channels: ["向量", "重排"],
        content: String.raw`**追问：为什么 SmoothQuant 能帮到 W8A8？**
> LLM 激活里存在**离群值（outlier）**，少数通道幅值极大，per-tensor 量化会被这些离群值把 scale 撑大，导致其余通道分辨率极差。SmoothQuant 用数学等价变换把难度从激活转移到权重（权重分布更平滑，好量化），从而让激活也能安全地量化到 INT8。`,
      },
      {
        id: "Ef4a78e64cafdf85f781ab28b",
        repo: "JennyMa11.github.io",
        section: "9.3 权重量化三剑客",
        file: "inference_accel_handbook_zh.md",
        locator: "#L1472–L1476",
        kind: "text",
        channels: ["关键词", "向量"],
        content: String.raw`- **GPTQ（Generative Pre-trained Transformer Quantization）**：一种基于二阶误差补偿的 PTQ 权重量化算法，名字来源于其针对 GPT 类模型提出。
- **AWQ（Activation-aware Weight Quantization，激活感知权重量化）**：认为「对激活影响大的通道才重要」，只保护极少数显著通道。
- **SmoothQuant**：通过数学等价变换平滑激活分布，是「Smooth（平滑）+ Quant（量化）」的合成词。
- **Activation Outlier（激活离群值）**：激活张量中少数幅值异常大的通道，会把 per-tensor 的 scale 撑大，导致其余通道量化分辨率极差。`,
      },
      {
        id: "Eac81a30f66147322eb0a8e24",
        repo: "JennyMa11.github.io",
        section: "9.3 权重量化三剑客",
        file: "inference_accel_handbook_zh.md",
        locator: "#L1458–L1468",
        kind: "text",
        channels: ["关键词"],
        content: String.raw`## 9.3 权重量化三剑客：GPTQ / AWQ / SmoothQuant

**速查**：GPTQ 用二阶信息逐层最小化量化误差（经典 PTQ）；
AWQ 保护对激活重要的少量权重通道（激活感知）；
SmoothQuant 把激活的量化难度「迁移」到权重上，让 W8A8 可行。`,
      },
      {
        id: "Eb1cb5ed94dc862d5729051ef",
        repo: "JennyMa11.github.io",
        section: "量化方法对比",
        file: "inference_accel_handbook_zh.md",
        locator: "#L2309–L2314",
        kind: "text",
        channels: ["关键词", "向量"],
        content: String.raw`| 方法 | 类型 | 粒度 | 特点 |
|---|---|---|---|
| GPTQ | PTQ weight-only | per-group | 二阶误差补偿，经典 |
| AWQ | PTQ weight-only | per-channel | 激活感知，保护 salient 通道 |
| SmoothQuant | W8A8 | per-channel | 迁移激活离群值到权重 |
| FP8 | W8A8 | per-tensor/block | 动态范围大，新卡首选 |`,
      },
    ],
    trace: { candidates: 5, retrievalMs: 379, generateMs: 8871, model: "qwen3:4b" },
  },

  {
    id: "speculative",
    domain: "推理引擎",
    question: "投机采样如何在并行验证的同时保证目标采样分布？",
    aliases: [
      "投机采样", "投机解码", "Speculative", "rejection sampling",
      "拒绝采样", "目标分布", "draft", "target", "接受率", "无损",
    ],
    answer: `关键在于验收和修正都采用目标模型实际生效的采样分布，并执行 modified rejection sampling。这样输出分布与直接从目标模型采样一致，近似验收模式不在保证范围内。[E087ea14fcf3c70971351853e] [E23bc08709c8470cf3d29f41f]

Draft 模型先猜多个 token，Target 模型并行验证；猜对的直接使用，猜错的按目标分布与 draft 分布的概率差修正采样。[E595e15e599ad739cccb72036] [E087ea14fcf3c70971351853e]`,
    citations: [
      {
        id: "E087ea14fcf3c70971351853e",
        repo: "JennyMa11.github.io",
        section: "投机解码正确性",
        file: "inference_accel_handbook_zh.md",
        locator: "#L1596",
        kind: "text",
        channels: ["向量", "重排"],
        content: String.raw`**为什么正确？** 若验证与修正采用目标模型实际生效的采样分布，并执行 **modified rejection sampling**，输出分布与直接从目标模型采样一致；近似验收模式不在此保证之内。`,
      },
      {
        id: "E23bc08709c8470cf3d29f41f",
        repo: "JennyMa11.github.io",
        section: "术语表",
        file: "inference_accel_handbook_zh.md",
        locator: "#L1550–L1567",
        kind: "text",
        channels: ["关键词", "向量"],
        content: String.raw`- **Accept / Reject（接受 / 拒绝）**：验证阶段判定候选 Token 是否被采纳。
- **Acceptance Rate（接受率，α）**：候选 Token 被接受的比例，是决定加速比的关键。
- **modified rejection sampling（改进拒绝采样）**：一种采样修正方法，保证接受结果的分布与目标模型完全一致。`,
      },
      {
        id: "E595e15e599ad739cccb72036",
        repo: "JennyMa11.github.io",
        section: "投机解码是否无损",
        file: "inference_accel_handbook_zh.md",
        locator: "#L1680–L1681",
        kind: "text",
        channels: ["关键词", "向量"],
        content: String.raw`**追问：投机解码是「无损」的吗？**
> 在采样时使用 modified rejection sampling，并以实际生效的目标分布（含温度、top-k/top-p 等处理）验收与修正，才保证输出分布一致；贪心解码可逐位置核对 Target 的最优 Token。部分方法另有近似验收模式，例如 Medusa 的 typical acceptance，不能统称严格无损。`,
      },
    ],
    trace: { candidates: 5, retrievalMs: 376, generateMs: 8427, model: "qwen3:4b" },
  },

  {
    id: "prefix-cache",
    domain: "推理引擎",
    question: "相同前缀的请求为什么可以共享历史 KV？",
    aliases: [
      "Prefix Cache", "前缀缓存", "共享历史 KV", "历史 KV", "System Prompt",
      "RadixAttention", "前缀", "KV Cache 共享", "因果注意力",
    ],
    answer: `因果注意力让一个 token 的 Key/Value 只依赖它自己和它之前的 token。两个请求只要前缀完全一致，这段前缀每个 token 的 KV 就一模一样，因此可以只算一次、共同复用。[Eb59793dfbee07cfe566a9dd6]

工程上把公共前缀的 KV 缓存一次，后续请求只对不同的后缀做 Prefill。SGLang 的 RadixAttention 用基数树管理请求之间的前缀共享关系，进一步细化复用。[E44d43245f4c3e913958fe922] [E920d5fd30b391d87ed884dfd] [Eb6ca72c108b9a848ad4b6d8a]`,
    citations: [
      {
        id: "Eb59793dfbee07cfe566a9dd6",
        repo: "AIInfraGuide",
        section: "2.3 Prefix Cache 与 RadixAttention",
        file: "2.3-Prefix Cache 与 RadixAttention.md",
        locator: "#L40",
        kind: "text",
        channels: ["关键词", "向量"],
        content: String.raw`📌 **关键点**：Attention 的因果性决定了——**一个 Token 的 Key/Value 只取决于它自己和它前面的 Token**。所以两个请求只要**前缀完全一致**，这段前缀每个 Token 算出来的 KV 就一模一样，完全可以只算一次、大家共用。`,
      },
      {
        id: "E44d43245f4c3e913958fe922",
        repo: "AIInfraGuide",
        section: "3.8 从 Transformer 到 LLM 自回归生成",
        file: "3.8 从Transformer到LLM自回归生成深入理解.md",
        locator: "#L414–L420",
        kind: "text",
        channels: ["向量", "重排"],
        content: String.raw`### 7.2 Prefix Cache / Prompt Cache

很多场景下，多个请求共享相同的前缀——比如相同的 system prompt（"你是一个有帮助的 AI 助手，请......"）。为每个请求都重新计算这段前缀的 KV 是浪费的。

Prefix Cache 的做法是：将公共前缀的 KV Cache 计算一次并缓存，后续有相同前缀的请求直接复用这份缓存，只需要对各自不同的后缀部分做 Prefill。

SGLang 的 **RadixAttention** 更进一步，用一棵 Radix Tree（基数树）来管理所有请求的前缀共享关系，实现了更精细的缓存复用。`,
      },
      {
        id: "E920d5fd30b391d87ed884dfd",
        repo: "AIInfraGuide",
        section: "2.3 Prefix Cache 与 RadixAttention",
        file: "2.3-Prefix Cache 与 RadixAttention.md",
        locator: "#L11",
        kind: "text",
        channels: ["关键词", "向量"],
        content: String.raw`真实业务里，海量请求往往共享同一段开头——同一个几百 Token 的 System Prompt、同一份 Few-shot 示例、多轮对话里不断重复的历史。每来一个请求就把这段共享前缀重新 Prefill 一遍，是巨大的浪费。Prefix Cache 就是把这段共享前缀的 KV Cache 缓存下来、后续请求直接复用的技术。这一节讲清 vLLM 基于 Hash 的自动前缀缓存怎么工作，以及 SGLang 的 RadixAttention 在此之上的进阶思路。`,
      },
      {
        id: "Eb6ca72c108b9a848ad4b6d8a",
        repo: "AIInfraGuide",
        section: "2.1 PagedAttention",
        file: "2.1-PagedAttention.md",
        locator: "#L146",
        kind: "text",
        channels: ["向量"],
        content: String.raw`- **共享前缀**：一批请求用了相同的 System Prompt，或从同一个 Prompt 并行采样多个回答（\`n > 1\`）。它们的前缀 KV 完全相同，就没必要各存一份——让它们的块表都指向同一批物理块即可。这就是下一节（2.3 Prefix Cache）的物理基础。`,
      },
    ],
    trace: { candidates: 5, retrievalMs: 443, generateMs: 8259, model: "qwen3:4b" },
  },

  {
    id: "torchrun-rank",
    domain: "分布式训练",
    question: "torchrun 的 local_rank 和全局 rank 有何区别，绑 GPU 用哪个？",
    aliases: [
      "torchrun", "local_rank", "local rank", "全局 rank", "world_size",
      "rank", "绑 GPU", "绑定 GPU", "set_device", "CUDA_VISIBLE_DEVICES",
    ],
    answer: `rank 是进程在整个训练任务中的全局唯一编号，范围是 0 到 world_size - 1；local_rank 是进程在所在节点内部的编号，每台机器都从 0 开始。[E4febd32ea2c3add7bdf8021b]

绑 GPU 必须用 local_rank，调用 torch.cuda.set_device(local_rank)。用 rank 去绑卡，在多机场景下会越界，例如第二台机器上的 rank 2 并不存在“第 2 块卡”。[Ee098905eae23b14e3b2225f3] [E3b9e9fe629537f230e9442bb]`,
    citations: [
      {
        id: "E4febd32ea2c3add7bdf8021b",
        repo: "AIInfraGuide",
        section: "1.2 环境搭建与分布式启动",
        file: "1.2 环境搭建与分布式启动.md",
        locator: "#L96–L100",
        kind: "text",
        channels: ["关键词", "向量"],
        content: String.raw`- **\`rank\`（全局 rank）**：进程在整个训练任务中的全局唯一编号，取值范围 $0 \sim \text{world\_size}-1$。
上图中 4 个进程的 rank 依次是 0、1、2、3。
常用 \`rank == 0\` 来指定"主进程"，负责打印日志、保存模型等。
- **\`local_rank\`（本地 rank）**：进程在**所在节点内部**的编号。
它的核心作用是**决定绑定哪块 GPU**——通常直接 \`torch.cuda.set_device(local_rank)\`。`,
      },
      {
        id: "Ee098905eae23b14e3b2225f3",
        repo: "AIInfraGuide",
        section: "1.2 环境搭建与分布式启动",
        file: "1.2 环境搭建与分布式启动.md",
        locator: "#L96–L100",
        kind: "text",
        channels: ["关键词", "重排"],
        content: String.raw`💡 **提示**：初学者最容易混淆的就是用 \`rank\` 去 \`set_device\`。
在多机场景下这会越界出错——\`rank=2\` 在第二台机器上根本没有"第 2 块卡"。
**决定 GPU 绑定的永远是 local_rank，不是 rank**。`,
      },
      {
        id: "E3b9e9fe629537f230e9442bb",
        repo: "AIInfraGuide",
        section: "1.2 环境搭建与分布式启动",
        file: "1.2 环境搭建与分布式启动.md",
        locator: "#L116–L140",
        kind: "code",
        channels: ["关键词", "代码块"],
        content: String.raw`import os
import torch
import torch.distributed as dist

def setup():
    # torchrun 会把这些环境变量注入进来
    rank = int(os.environ["RANK"])
    local_rank = int(os.environ["LOCAL_RANK"])
    world_size = int(os.environ["WORLD_SIZE"])

    # 1) 绑定本进程使用的 GPU（用 local_rank！）
    torch.cuda.set_device(local_rank)

    # 2) 初始化默认进程组，GPU 训练用 nccl 后端
    dist.init_process_group(
        backend="nccl",
        rank=rank,
        world_size=world_size,`,
      },
    ],
    trace: { candidates: 5, retrievalMs: 431, generateMs: 6314, model: "qwen3:4b" },
  },

  {
    id: "row-parallel",
    domain: "分布式训练",
    question: "Row Parallel 线性层如何合并各卡的局部输出？",
    aliases: [
      "Row Parallel", "行并行", "张量并行", "AllReduce", "局部输出",
      "Column Parallel", "列并行", "FFN", "输出投影", "部分和",
    ],
    answer: `Row Parallel 的每张卡先算出局部部分和，再通过求和 AllReduce 合并成完整输出。[E4a1c9f02d7b6e3815c0a9d4]

权重按行切分，输入需要与 Column Parallel 的输出对接；这种结构常用于 FFN 的第二个线性层和 Attention 的输出投影。[E4a1c9f02d7b6e3815c0a9d4]`,
    citations: [
      {
        id: "E4a1c9f02d7b6e3815c0a9d4",
        repo: "AIInfraGuide",
        section: "模块三-分布式训练",
        file: "第6章-张量并行与序列并行.md",
        locator: "#L34–L38",
        kind: "text",
        channels: ["关键词", "向量"],
        content: String.raw`- **切分方式**：权重 $A$ 按行切分，每卡持有 $A_i$（行方向的分片）
- **输入要求**：输入 $X$ 也需按列分片为 $X_i$（与 Column Parallel 的输出对接）
- **计算过程**：$Y_i = X_i \cdot A_i$（每卡计算部分结果）
- **通信**：各卡的 $Y_i$ 通过 **AllReduce**（求和）得到完整输出 $Y$
- **应用位置**：FFN 的第二个线性层、Attention 的输出投影`,
        url: "https://github.com/caomaolufei/AIInfraGuide/blob/a3b63eeb81d6d36a3c42c8cfc5a1bdd96e36bab1/docs/guides/%E6%A8%A1%E5%9D%97%E4%B8%89-%E5%88%86%E5%B8%83%E5%BC%8F%E8%AE%AD%E7%BB%83/%E7%AC%AC6%E7%AB%A0-%E5%BC%A0%E9%87%8F%E5%B9%B6%E8%A1%8C%E4%B8%8E%E5%BA%8F%E5%88%97%E5%B9%B6%E8%A1%8C.md#L34-L38",
      },
    ],
    trace: { candidates: 3, retrievalMs: 268, generateMs: 4120, model: "qwen3:4b" },
  },

  {
    id: "moe-parallel",
    domain: "分布式训练",
    question: "MoE 专家并行中的 dispatch 和 combine 两次 All-to-All 各做什么？",
    aliases: [
      "MoE", "dispatch", "combine", "All-to-All", "专家并行",
      "专家", "Top-K", "DeepEP", "路由",
    ],
    answer: `两次 All-to-All 分工不同：dispatch 把 token 发往对应 Expert 所在的 GPU，combine 把计算结果发回 token 原来的 GPU。[E5b2f8a91c4d7e6032b8f1a6]

通信量取决于 token 数、Top-K 与 Expert 分布，所以 All-to-All 通常是 MoE 训练的主要瓶颈。[E5b2f8a91c4d7e6032b8f1a6]`,
    citations: [
      {
        id: "E5b2f8a91c4d7e6032b8f1a6",
        repo: "AIInfraGuide",
        section: "模块三-分布式训练",
        file: "第10章-MoE并行.md",
        locator: "#L32–L35",
        kind: "text",
        channels: ["关键词", "向量"],
        content: String.raw`- 两次 All-to-All：dispatch（token 发往对应 Expert 所在 GPU）+ combine（结果发回原 GPU）
- 通信量分析：取决于 token 数、Top-K、Expert 分布
- 为什么 All-to-All 是 MoE 训练的主要瓶颈
- 通信优化：分组 All-to-All、计算通信重叠、DeepEP 等高性能通信库`,
        url: "https://github.com/caomaolufei/AIInfraGuide/blob/a3b63eeb81d6d36a3c42c8cfc5a1bdd96e36bab1/docs/guides/%E6%A8%A1%E5%9D%97%E4%B8%89-%E5%88%86%E5%B8%83%E5%BC%8F%E8%AE%AD%E7%BB%83/%E7%AC%AC10%E7%AB%A0-MoE%E5%B9%B6%E8%A1%8C.md#L32-L35",
      },
    ],
    trace: { candidates: 3, retrievalMs: 254, generateMs: 3980, model: "qwen3:4b" },
  },

  {
    id: "paged-attention",
    domain: "推理引擎",
    question: "PagedAttention 如何减少 KV Cache 的内存碎片？",
    aliases: [
      "PagedAttention", "分页", "内存碎片", "KV Cache 碎片",
      "物理块", "分页注意力", "页表", "block table",
    ],
    answer: `PagedAttention 把 KV Cache 划成固定大小的逻辑块，再把逻辑块映射到分散的物理页。这样不必为每个请求预留一整段连续显存，碎片主要只剩最后一个未填满的块。[E9d1a5c3b7e24f8061d2c9b4] [E7c2e6d84a1b35f9027c8e6d]

分页只改变存储布局。KV Cache 仍然保存历史 token 的 Key 和 Value，注意力计算的语义不变。[E9d1a5c3b7e24f8061d2c9b4]`,
    citations: [
      {
        id: "E9d1a5c3b7e24f8061d2c9b4",
        repo: "examples/corpus",
        section: "PagedAttention 与 KV Cache",
        file: "inference.md",
        locator: "#L4",
        kind: "text",
        channels: ["关键词", "向量"],
        content: String.raw`PagedAttention 使用分页管理 KV Cache，将逻辑连续的缓存映射到非连续物理块，减少内存碎片。KV Cache 保存历史 token 的 Key 和 Value，避免 decode 阶段重复计算。分页管理本身不改变注意力计算的语义。`,
      },
      {
        id: "E7c2e6d84a1b35f9027c8e6d",
        repo: "examples/diagrams",
        section: "分页示意",
        file: "pages.png",
        locator: "整图 640×420",
        kind: "image",
        channels: ["图像", "关键词"],
        content: "PagedAttention: logical KV cache blocks map to scattered physical memory pages.",
        image: "assets/pages.png",
        bbox: [0, 0, 640, 420],
        coordinateSpace: "image_pixels",
      },
    ],
    trace: { candidates: 4, retrievalMs: 312, generateMs: 4860, model: "qwen3:4b" },
  },

  {
    id: "numa",
    domain: "系统与云原生",
    question: "NUMA 架构下，为什么要把线程绑定到本地内存？",
    aliases: [
      "NUMA", "局部性", "绑核", "跨节点内存", "远端访问",
      "CPU 绑定", "内存分配", "socket", "拓扑",
    ],
    answer: `NUMA 系统里，不同节点的内存访问代价不同，访问远端节点上的内存通常更慢。[E3a4b8d6f0c25e7194b6d8a2] [E6b7c9e1a4d80f3258c7e9b3]

把线程绑定到合适的 CPU，并让内存分配与线程保持在同一节点，可以减少远端访问。具体收益仍要结合拓扑和负载测量验证。[E3a4b8d6f0c25e7194b6d8a2]`,
    citations: [
      {
        id: "E3a4b8d6f0c25e7194b6d8a2",
        repo: "examples/corpus",
        section: "NUMA 与局部性",
        file: "systems.md",
        locator: "#L10",
        kind: "text",
        channels: ["关键词", "向量"],
        content: String.raw`NUMA 系统不同节点内存访问代价不同。将线程绑定到合适 CPU 并保持内存分配局部性可以减少远端访问，但效果需要测量验证。`,
      },
      {
        id: "E6b7c9e1a4d80f3258c7e9b3",
        repo: "examples/diagrams",
        section: "拓扑示意",
        file: "numa.png",
        locator: "整图 640×420",
        kind: "image",
        channels: ["图像", "关键词"],
        content: "NUMA architecture: two CPU sockets each connect to their local memory and a remote socket.",
        image: "assets/numa.png",
        bbox: [0, 0, 640, 420],
        coordinateSpace: "image_pixels",
      },
    ],
    trace: { candidates: 4, retrievalMs: 287, generateMs: 4410, model: "qwen3:4b" },
  },
];

export const SUGGESTION_IDS = [
  "gqa",
  "smoothquant",
  "speculative",
  "torchrun-rank",
  "row-parallel",
  "paged-attention",
];
