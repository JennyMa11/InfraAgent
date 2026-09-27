# Infra 学习笔记：communication

## AllReduce

AllReduce 对各 rank 的张量执行规约，并将规约结果分发给所有 rank。数据并行中它常用于梯度同步；结果不是按 rank 顺序拼接所有原始张量。

## AllGather

AllGather 收集各 rank 的输入分片，使每个 rank 得到全部分片。它收集而不执行求和规约，适合从分片参数构造完整视图。

## ReduceScatter

ReduceScatter 对输入执行规约，再把不同结果分片分发到对应 rank。与 AllReduce 不同，每个 rank 只保留规约结果的一部分。
