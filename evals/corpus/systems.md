# Infra 学习笔记：systems

## NUMA

NUMA 系统的内存访问代价与 CPU 和内存所在节点有关。远端节点访问可能更昂贵；CPU 绑定和内存分配局部性应结合工作负载测量，而不是只绑定线程就保证优化。

## epoll Edge Triggered

epoll edge-triggered 模式下通常采用非阻塞 I/O，持续读取直到 EAGAIN。只读一次可能留下未处理数据，又等不到新的边沿通知；它与 level-triggered 行为不同。
