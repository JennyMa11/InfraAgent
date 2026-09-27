# LLM 推理服务

## PagedAttention 与 KV Cache
PagedAttention 使用分页管理 KV Cache，将逻辑连续的缓存映射到非连续物理块，减少内存碎片。KV Cache 保存历史 token 的 Key 和 Value，避免 decode 阶段重复计算。分页管理本身不改变注意力计算的语义。

## Continuous Batching
Continuous Batching 在迭代边界动态加入和移除请求，提高 GPU 利用率。Prefill 处理输入 token，Decode 逐步生成输出 token。长 prefill 可能增加其他请求的 decode 延迟，需要调度隔离或 chunked prefill。

## 推理指标
TTFT 是从请求提交到首 token 返回的时间，TPOT 是输出 token 间的平均时间。吞吐提升不必然意味着尾延迟降低，必须结合 P95、P99 和并发水平分析。
