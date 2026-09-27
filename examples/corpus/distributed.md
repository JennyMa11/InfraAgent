# 分布式训练

## NCCL AllReduce
AllReduce 对每个 rank 的张量进行规约，并把结果分发到所有 rank。数据并行训练常使用 AllReduce 同步梯度；通信与反向计算的重叠可以减少暴露的通信时间。NCCL 是 GPU 集合通信库。

## ZeRO 与显存
ZeRO Stage 1 划分优化器状态，Stage 2 进一步划分梯度，Stage 3 进一步划分参数。降低单卡显存占用需要额外通信，收益取决于模型规模、并行度和网络带宽。

## 并行策略
Tensor Parallel 将张量计算分布到多个设备，Pipeline Parallel 将模型层划分到不同 stage，Data Parallel 为不同数据副本复制模型。流水线气泡与 microbatch 数有关。
