# Infra 学习笔记：training

## Data Parallel

Data Parallel 为不同数据分片复制模型，各 rank 处理不同样本并同步梯度。数据并行与参数切分不同，复制模型本身不能降低每个副本的参数显存。

## Tensor Parallel

Tensor Parallel 将同一层的张量计算切分到多个设备，使设备共同完成一层计算。它通常需要设备间通信；不能把层级流水线和层内张量划分混为一谈。

## Pipeline Parallel

Pipeline Parallel 将不同模型层划分到不同 stage，以 microbatch 组织流水线。stage 等待形成流水线气泡；它不是让所有设备同时计算同一个矩阵的分片。

## ZeRO Stage 1

ZeRO Stage 1 在数据并行 rank 间划分优化器状态，避免每个 rank 保存全部优化器状态。梯度和参数的进一步划分属于更高阶段。

## ZeRO Stage 2

ZeRO Stage 2 在优化器状态划分的基础上进一步划分梯度。参数划分属于 Stage 3，不能将降低梯度显存等同于参数已经分片。

## ZeRO Stage 3

ZeRO Stage 3 在优化器状态、梯度划分基础上进一步划分模型参数。执行计算时需要获取所需参数，节约显存可能伴随额外通信成本。
