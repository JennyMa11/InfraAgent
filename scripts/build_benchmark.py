"""Write authored study notes and gold spans. No model generates the questions or labels."""

import json
from collections import defaultdict
from pathlib import Path

# Topic, explanatory note, minimal evidence span, direct question, paraphrase question.
FACTS = [
    (
        "inference",
        "KV Cache",
        (
            "KV Cache 保存已处理 token 的 Key 和 V"
            "alue，后续 decode 复用历史键值，减少重复计算。缓"
            "存容量随序列长度和并发请求数增长，不能用权重显存代替缓存显存"
            "估算。"
        ),
        "复用历史键值",
        "KV Cache 缓存了什么？",
        "生成下一字时怎样避免重新算历史键和值？",
    ),
    (
        "inference",
        "PagedAttention",
        (
            "PagedAttention 将逻辑 KV Cache "
            "划分为块，通过映射表关联非连续物理块，减少显存碎片与浪费"
            "。它改变缓存管理方式，不是把所有请求填充为同样长度。"
        ),
        "非连续物理块",
        "PagedAttention 如何缓解显存碎片？",
        "推理时逻辑连续的缓存必须物理连续吗？",
    ),
    (
        "inference",
        "Prefix Cache",
        (
            "Prefix Cache 复用相同输入前缀已计算的 KV"
            " 状态，减少重复 prefill。它要求前缀兼容，不能据"
            "此保证每个后续生成 token 都变快。"
        ),
        "减少重复 prefill",
        "Prefix Cache 加速哪个阶段？",
        "多个请求共享系统提示时，怎样省去共同输入的重复计算？",
    ),
    (
        "inference",
        "Continuous Batching",
        (
            "Continuous Batching 在迭代边界加入新"
            "请求并移除完成请求，不必等待整个静态批次完成。动态批调度"
            "改善设备利用率，但需要结合延迟目标管理请求。"
        ),
        "迭代边界加入新请求",
        "Continuous Batching 何时加入请求？",
        "一批里有请求提前生成完，怎样马上用空出来的算力接新任务？",
    ),
    (
        "inference",
        "Prefill 与 Decode",
        (
            "Prefill 并行处理输入提示的多个 token；De"
            "code 使用历史缓存逐步生成输出 token。两阶段的"
            "工作负载特征不同，吞吐与延迟需要分别测量。"
        ),
        "逐步生成输出 token",
        "Prefill 和 Decode 的处理方式有什么不同？",
        "输入提示处理完以后，输出文字为什么还是一步一步生成？",
    ),
    (
        "inference",
        "TTFT 与 TPOT",
        (
            "TTFT 衡量请求提交到首个输出 token 的时间；T"
            "POT 衡量输出 token 之间的平均时间。排队和输入"
            "预填充影响首字延迟，不能以吞吐替代两类延迟指标。"
        ),
        "请求提交到首个输出 token",
        "TTFT 和 TPOT 分别衡量什么？",
        "聊天用户等待第一个字的时间应该用哪个指标？",
    ),
    (
        "inference",
        "Chunked Prefill",
        (
            "Chunked Prefill 把长提示的预填充拆成较小片段"
            "，使调度器能够交错安排 prefill 和 decode。它"
            "用于管理长输入与生成任务的竞争，不是将 PDF 分块建立向量"
            "索引。"
        ),
        "交错安排 prefill 和 decode",
        "Chunked Prefill 为什么把长提示拆开？",
        "一个超长输入阻塞其他用户继续出字，调度上能怎样缓解？",
    ),
    (
        "training",
        "Data Parallel",
        (
            "Data Parallel 为不同数据分片复制模型，各 "
            "rank 处理不同样本并同步梯度。数据并行与参数切分不同"
            "，复制模型本身不能降低每个副本的参数显存。"
        ),
        "不同样本并同步梯度",
        "Data Parallel 如何分配训练样本？",
        "每张卡都放一份完整模型，各自处理数据后要同步什么？",
    ),
    (
        "training",
        "Tensor Parallel",
        (
            "Tensor Parallel 将同一层的张量计算切分到"
            "多个设备，使设备共同完成一层计算。它通常需要设备间通信；"
            "不能把层级流水线和层内张量划分混为一谈。"
        ),
        "同一层的张量计算切分",
        "Tensor Parallel 切分的是层内计算还是整层？",
        "一个矩阵太大要让多张卡一起算同一层，属于哪种并行？",
    ),
    (
        "training",
        "Pipeline Parallel",
        (
            "Pipeline Parallel 将不同模型层划分到不同 "
            "stage，以 microbatch 组织流水线。stage"
            " 等待形成流水线气泡；它不是让所有设备同时计算同一个矩阵的分"
            "片。"
        ),
        "不同模型层划分到不同 stage",
        "Pipeline Parallel 怎样分配模型层？",
        "模型前几层在卡一，后几层在卡二，是哪种并行？",
    ),
    (
        "training",
        "ZeRO Stage 1",
        (
            "ZeRO Stage 1 在数据并行 rank 间划分优"
            "化器状态，避免每个 rank 保存全部优化器状态。梯度和"
            "参数的进一步划分属于更高阶段。"
        ),
        "划分优化器状态",
        "ZeRO Stage 1 划分什么状态？",
        "只把 Adam 的状态分摊到多张卡，还没切梯度参数，是哪个阶段？",
    ),
    (
        "training",
        "ZeRO Stage 2",
        (
            "ZeRO Stage 2 在优化器状态划分的基础上进一步"
            "划分梯度。参数划分属于 Stage 3，不能将降低梯度显"
            "存等同于参数已经分片。"
        ),
        "进一步划分梯度",
        "ZeRO Stage 2 相比 Stage 1 多划分什么？",
        "优化器已经分片，再把梯度也分片，要用 ZeRO 哪一阶段？",
    ),
    (
        "training",
        "ZeRO Stage 3",
        (
            "ZeRO Stage 3 在优化器状态、梯度划分基础上进"
            "一步划分模型参数。执行计算时需要获取所需参数，节约显存可"
            "能伴随额外通信成本。"
        ),
        "进一步划分模型参数",
        "ZeRO Stage 3 相比 Stage 2 多划分什么？",
        "模型权重也想分摊存放而不是每卡一整份，应选哪一阶段？",
    ),
    (
        "communication",
        "AllReduce",
        (
            "AllReduce 对各 rank 的张量执行规约，并将"
            "规约结果分发给所有 rank。数据并行中它常用于梯度同步"
            "；结果不是按 rank 顺序拼接所有原始张量。"
        ),
        "规约结果分发给所有 rank",
        "AllReduce 的结果保存在哪些 rank？",
        "所有卡都要拿到梯度求和结果，而不是原始梯度拼接，应该选什么集合通信？",
    ),
    (
        "communication",
        "AllGather",
        (
            "AllGather 收集各 rank 的输入分片，使每个"
            " rank 得到全部分片。它收集而不执行求和规约，适合从"
            "分片参数构造完整视图。"
        ),
        "每个 rank 得到全部分片",
        "AllGather 与 AllReduce 的结果有什么区别？",
        "每个设备手里只有一段参数，要让每张卡拿到所有原始片段，用什么操作？",
    ),
    (
        "communication",
        "ReduceScatter",
        (
            "ReduceScatter 对输入执行规约，再把不同结果"
            "分片分发到对应 rank。与 AllReduce 不同，"
            "每个 rank 只保留规约结果的一部分。"
        ),
        "只保留规约结果的一部分",
        "ReduceScatter 会让每个 rank 保存完整结果吗？",
        "先求和但每张卡只留结果的一段，属于哪种通信？",
    ),
    (
        "gpu",
        "Coalesced Memory",
        (
            "合并访存 coalescing 将 warp 的全局内存访问"
            "组织为更少的内存事务。相邻线程访问相邻地址通常有利于合并；它"
            "处理全局访存布局，不等于解决共享内存 bank confli"
            "ct。"
        ),
        "更少的内存事务",
        "CUDA coalescing 优化哪类访问？",
        "同一个 warp 读全局内存时，怎样减少硬件需要发出的访问事务？",
    ),
    (
        "gpu",
        "Shared Memory Bank",
        (
            "共享内存划分为多个 bank。同一 warp 对同一 ban"
            "k 的不同地址访问可能产生 bank conflict 并串"
            "行化；对同一地址的读取可以广播，不能把广播简单算成冲突。"
        ),
        "不同地址访问可能产生 bank conflict",
        "同一共享内存 bank 的访问什么时候会冲突？",
        "为什么同组线程在共享内存里读不同位置会发生串行？",
    ),
    (
        "gpu",
        "Occupancy",
        (
            "Occupancy 是活动 warp 数与硬件最大活动 "
            "warp 数的比例，受寄存器、共享内存等资源约束。更高占"
            "用率不自动等于更快执行，仍要测量吞吐、延迟与访存瓶颈。"
        ),
        "更高占用率不自动等于更快执行",
        "GPU occupancy 越高一定越快吗？",
        "为了多驻留 warp 降低每线程资源占用，为什么不一定提升性能？",
    ),
    (
        "gpu",
        "Pinned Memory",
        (
            "Pinned Memory 是页锁定的主机内存，可用于高"
            "效主机与设备数据传输。CUDA 异步复制的常见用法需要页"
            "锁定主机缓冲区；它不同于 GPU 上的共享内存。"
        ),
        "页锁定的主机内存",
        "Pinned Memory 位于主机还是 GPU 共享内存？",
        "想让 CPU 到 GPU 的异步拷贝更有效，主机缓冲区应该有什么性质？",
    ),
    (
        "systems",
        "NUMA",
        (
            "NUMA 系统的内存访问代价与 CPU 和内存所在节点有"
            "关。远端节点访问可能更昂贵；CPU 绑定和内存分配局部性"
            "应结合工作负载测量，而不是只绑定线程就保证优化。"
        ),
        "内存分配局部性",
        "NUMA 为什么要关注线程和内存的局部性？",
        "进程跑在一个 CPU 节点却总读另一个节点的内存，怎样排查访问代价？",
    ),
    (
        "systems",
        "epoll Edge Triggered",
        (
            "epoll edge-triggered 模式下通常采用非阻"
            "塞 I/O，持续读取直到 EAGAIN。只读一次可能留下未处"
            "理数据，又等不到新的边沿通知；它与 level-trigge"
            "red 行为不同。"
        ),
        "持续读取直到 EAGAIN",
        "epoll ET 为什么要读到 EAGAIN？",
        "收到可读通知后只读一点就停，为什么边沿触发可能再也不通知？",
    ),
    (
        "cloud",
        "Kubernetes Requests",
        (
            "Kubernetes requests 描述调度时的资源需求"
            "，调度器依据请求量安排 Pod。requests 不等同于容"
            "器的硬性使用上限，限制运行时使用需要理解 limits。"
        ),
        "调度器依据请求量",
        "Kubernetes 调度主要依据 requests 还是 limits？",
        "想让调度器预留足够 CPU 而不是只限制最大使用量，应设置什么？",
    ),
    (
        "cloud",
        "Kubernetes Limits",
        (
            "Kubernetes limits 约束容器运行时资源使用。"
            "CPU 达到 limit 可能被 throttling；内存"
            "超过限制可能触发 OOMKilled。requests 和 "
            "limits 对应不同职责。"
        ),
        "CPU 达到 limit 可能被 throttling",
        "CPU 和内存超过 Kubernetes limits 的后果有什么不同？",
        "容器 CPU 被限流但内存超限可能被杀，应该检查哪类配置？",
    ),
    (
        "cloud",
        "Readiness Probe",
        (
            "Readiness Probe 判断容器当前是否适合接收"
            "业务流量。就绪探针失败会影响常规 Service 流量路"
            "由，但失败本身不表示 kubelet 必须重启容器。"
        ),
        "是否适合接收业务流量",
        "Readiness 探针失败一定重启容器吗？",
        "应用暂时不能服务，想先停止给它转发流量，用哪种健康检查？",
    ),
    (
        "cloud",
        "Liveness Probe",
        (
            "Liveness Probe 判断容器是否需要被重启，重复失"
            "败达到阈值可以触发 kubelet 重启。应避免把慢启动简单"
            "当作死锁；启动过程可由 Startup Probe 保护。"
        ),
        "重复失败达到阈值",
        "Liveness 与 Readiness 的处理动作有什么区别？",
        "服务进程卡死需要自动重启，哪种探针负责判断？",
    ),
    (
        "cloud",
        "Startup Probe",
        (
            "Startup Probe 用于检查容器初始化是否完成。"
            "在启动探针成功之前，liveness 和 readine"
            "ss 探针不会执行，适合保护初始化时间较长的应用。"
        ),
        "初始化是否完成",
        "Startup Probe 如何保护慢启动服务？",
        "模型加载很慢，怎样避免应用初始化期间就被存活探针反复重启？",
    ),
]

ROOT = Path(__file__).resolve().parents[1]
notes, questions = defaultdict(list), []
for domain, heading, note, evidence, direct, paraphrase in FACTS:
    notes[domain].append(f"## {heading}\n\n{note}\n")
    for category, query in [("direct", direct), ("paraphrase", paraphrase)]:
        questions.append(
            {
                "id": f"q{len(questions) + 1:02}",
                "query": query,
                "category": category,
                "relevant_spans": [{"source": f"corpus/{domain}.md", "text": evidence}],
            }
        )
for domain, sections in notes.items():
    (ROOT / "evals" / "corpus" / f"{domain}.md").write_text(
        "# Infra 学习笔记：" + domain + "\n\n" + "\n".join(sections), encoding="utf-8"
    )
for query, gold in [
    (
        "Tensor Parallel 与 Pipeline Parallel 分别在层内还是层间切分？",
        [("training", "同一层的张量计算切分"), ("training", "不同模型层划分到不同 stage")],
    ),
    (
        "ZeRO Stage 2 和 Stage 3 的关键区别是什么？",
        [("training", "进一步划分梯度"), ("training", "进一步划分模型参数")],
    ),
    (
        "Kubernetes 预留资源与运行时限流分别由什么配置决定？",
        [("cloud", "调度器依据请求量"), ("cloud", "CPU 达到 limit 可能被 throttling")],
    ),
    (
        "AllGather 收集原始分片，AllReduce 返回什么？",
        [("communication", "每个 rank 得到全部分片"), ("communication", "规约结果分发给所有 rank")],
    ),
    (
        "Prefix Cache 与 PagedAttention 分别优化重复计算还是内存布局？",
        [("inference", "减少重复 prefill"), ("inference", "非连续物理块")],
    ),
    (
        "Readiness 与 Liveness 的失败动作有哪些差别？",
        [("cloud", "是否适合接收业务流量"), ("cloud", "重复失败达到阈值")],
    ),
]:
    questions.append(
        {
            "id": f"q{len(questions) + 1:02}",
            "query": query,
            "category": "multi_evidence",
            "relevant_spans": [
                {"source": f"corpus/{domain}.md", "text": span} for domain, span in gold
            ],
        }
    )
(ROOT / "evals" / "infra-60.json").write_text(json.dumps(questions, ensure_ascii=False, indent=2))
print(f"Wrote {len(questions)} questions and {len(notes)} authored note files.")
