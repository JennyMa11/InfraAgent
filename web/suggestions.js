// Suggested questions only; all answers come from the API.
export const RESULTS = [
  {
    "id": "gqa",
    "domain": "推理引擎",
    "question": "GQA 与 MQA 如何共享 K/V Head，主要减少什么资源？"
  },
  {
    "id": "smoothquant",
    "domain": "推理引擎",
    "question": "SmoothQuant 针对激活离群值采用什么变换？"
  },
  {
    "id": "speculative",
    "domain": "推理引擎",
    "question": "投机采样如何在并行验证的同时保证目标采样分布？"
  },
  {
    "id": "prefix-cache",
    "domain": "推理引擎",
    "question": "相同前缀的请求为什么可以共享历史 KV？"
  },
  {
    "id": "torchrun-rank",
    "domain": "分布式训练",
    "question": "torchrun 的 local_rank 和全局 rank 有何区别，绑 GPU 用哪个？"
  },
  {
    "id": "row-parallel",
    "domain": "分布式训练",
    "question": "Row Parallel 线性层如何合并各卡的局部输出？"
  },
  {
    "id": "moe-parallel",
    "domain": "分布式训练",
    "question": "MoE 专家并行中的 dispatch 和 combine 两次 All-to-All 各做什么？"
  },
  {
    "id": "paged-attention",
    "domain": "推理引擎",
    "question": "PagedAttention 如何减少 KV Cache 的内存碎片？"
  },
  {
    "id": "numa",
    "domain": "系统与云原生",
    "question": "NUMA 架构下，为什么要把线程绑定到本地内存？"
  }
];
export const SUGGESTION_IDS = ["gqa","smoothquant","speculative","torchrun-rank","row-parallel","paged-attention"];
