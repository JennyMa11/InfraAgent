# 系统与云原生

## Kubernetes 资源约束
Kubernetes requests 影响调度时的资源预留，limits 约束容器资源使用。CPU limits 可能触发 throttling，内存超限可能导致 OOMKilled；调度器主要依据 requests 选择节点。

## Linux epoll
epoll 是 Linux I/O 多路复用机制，支持 level-triggered 和 edge-triggered。edge-triggered 通常要求非阻塞 I/O，持续读取直到 EAGAIN，否则可能遗漏待处理数据。

## NUMA 与局部性
NUMA 系统不同节点内存访问代价不同。将线程绑定到合适 CPU 并保持内存分配局部性可以减少远端访问，但效果需要测量验证。
