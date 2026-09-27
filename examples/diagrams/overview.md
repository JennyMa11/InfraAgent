# Infra architecture

GPU memory hierarchy: global DRAM connects to streaming multiprocessors and shared memory.

Ring AllReduce: four GPU ranks exchange gradient data on a circular communication topology.

Pipeline parallelism: model layers are assigned to successive GPU stages.

Kubernetes cluster: a control plane manages worker nodes containing application pods.

PagedAttention: logical KV cache blocks map to scattered physical memory pages.

NUMA architecture: two CPU sockets each connect to their local memory and a remote socket.