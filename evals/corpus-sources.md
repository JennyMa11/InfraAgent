# 语料与标注来源

`corpus/` 为项目作者整理的学习笔记，不是官方文档全文或自动抓取的网页。
`infra-60.json` 为人工编写的 60 道题：27 个主题各一条直接查询和一条改写查询，加 6 道
多证据题。每题在检索前通过来源路径和证据短语解析为相关子块 ID。题集覆盖范围有限，
与笔记写作存在同源偏差；不代表真实用户问法、长论文布局或生产知识库效果。

主要事实的核对资料：

- KV 分页：[PagedAttention 论文](https://arxiv.org/abs/2309.06180)；
  [vLLM Prefix Caching](https://docs.vllm.ai/en/v0.9.1/design/automatic_prefix_caching.html)。
- ZeRO 三阶段：[DeepSpeed 配置说明](https://www.deepspeed.ai/docs/config-json/)与
  [ZeRO 教程](https://github.com/deepspeedai/DeepSpeed/blob/master/docs/_tutorials/zero.md)。
- 集合通信：[NCCL API](https://github.com/NVIDIA/nccl/blob/master/docs/userguide/source/api/colls.rst)。
- GPU 访存、bank conflict 与 occupancy：
  [CUDA SIMT Kernels](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/writing-cuda-kernels.html)；
  pinned memory：[CUDA 系统内存](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/understanding-memory.html)。
- epoll：[Linux epoll(7)](https://man7.org/linux/man-pages/man7/epoll.7.html)。
- Kubernetes：[资源管理](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)与
  [探针语义](https://kubernetes.io/docs/concepts/workloads/pods/probes/)。

图片验收使用 `scripts/verify_multimodal.py` 程序绘制的 6 张示意图和一份含重复图片的
合成 PDF；图注由作者明确编写。它用于验证真实模型和存储链路，不能据此声称复杂技术图
理解准确率。图片评测按整图父 ID 计相关性，保留全部区域命中；返回同一父图的多个区域
会占用 Top-K 名额，去重后的 precision 分母仍为 K。
