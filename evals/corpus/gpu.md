# Infra 学习笔记：gpu

## Coalesced Memory

合并访存 coalescing 将 warp 的全局内存访问组织为更少的内存事务。相邻线程访问相邻地址通常有利于合并；它处理全局访存布局，不等于解决共享内存 bank conflict。

## Shared Memory Bank

共享内存划分为多个 bank。同一 warp 对同一 bank 的不同地址访问可能产生 bank conflict 并串行化；对同一地址的读取可以广播，不能把广播简单算成冲突。

## Occupancy

Occupancy 是活动 warp 数与硬件最大活动 warp 数的比例，受寄存器、共享内存等资源约束。更高占用率不自动等于更快执行，仍要测量吞吐、延迟与访存瓶颈。

## Pinned Memory

Pinned Memory 是页锁定的主机内存，可用于高效主机与设备数据传输。CUDA 异步复制的常见用法需要页锁定主机缓冲区；它不同于 GPU 上的共享内存。
