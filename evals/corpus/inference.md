# Infra 学习笔记：inference

## KV Cache

KV Cache 保存已处理 token 的 Key 和 Value，后续 decode 复用历史键值，减少重复计算。缓存容量随序列长度和并发请求数增长，不能用权重显存代替缓存显存估算。

## PagedAttention

PagedAttention 将逻辑 KV Cache 划分为块，通过映射表关联非连续物理块，减少显存碎片与浪费。它改变缓存管理方式，不是把所有请求填充为同样长度。

## Prefix Cache

Prefix Cache 复用相同输入前缀已计算的 KV 状态，减少重复 prefill。它要求前缀兼容，不能据此保证每个后续生成 token 都变快。

## Continuous Batching

Continuous Batching 在迭代边界加入新请求并移除完成请求，不必等待整个静态批次完成。动态批调度改善设备利用率，但需要结合延迟目标管理请求。

## Prefill 与 Decode

Prefill 并行处理输入提示的多个 token；Decode 使用历史缓存逐步生成输出 token。两阶段的工作负载特征不同，吞吐与延迟需要分别测量。

## TTFT 与 TPOT

TTFT 衡量请求提交到首个输出 token 的时间；TPOT 衡量输出 token 之间的平均时间。排队和输入预填充影响首字延迟，不能以吞吐替代两类延迟指标。

## Chunked Prefill

Chunked Prefill 把长提示的预填充拆成较小片段，使调度器能够交错安排 prefill 和 decode。它用于管理长输入与生成任务的竞争，不是将 PDF 分块建立向量索引。
