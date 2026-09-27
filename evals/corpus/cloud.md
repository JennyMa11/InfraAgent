# Infra 学习笔记：cloud

## Kubernetes Requests

Kubernetes requests 描述调度时的资源需求，调度器依据请求量安排 Pod。requests 不等同于容器的硬性使用上限，限制运行时使用需要理解 limits。

## Kubernetes Limits

Kubernetes limits 约束容器运行时资源使用。CPU 达到 limit 可能被 throttling；内存超过限制可能触发 OOMKilled。requests 和 limits 对应不同职责。

## Readiness Probe

Readiness Probe 判断容器当前是否适合接收业务流量。就绪探针失败会影响常规 Service 流量路由，但失败本身不表示 kubelet 必须重启容器。

## Liveness Probe

Liveness Probe 判断容器是否需要被重启，重复失败达到阈值可以触发 kubelet 重启。应避免把慢启动简单当作死锁；启动过程可由 Startup Probe 保护。

## Startup Probe

Startup Probe 用于检查容器初始化是否完成。在启动探针成功之前，liveness 和 readiness 探针不会执行，适合保护初始化时间较长的应用。
