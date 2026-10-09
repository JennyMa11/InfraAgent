# 领域题集独立人工审核

题目由AI编写。核对版本、原文、答案要点和证据后填写 question-review.json。
未审核时保持pending；争议题需修订并建立新版本。

## official-002-1 · dev · single_hop

vLLM v0.10.2：缓存块身份除了文本还需要哪些额外哈希？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/design/prefix_caching.md

规范化行 19-19；SHA256 0a8a9e9095055c4f8e0cdaf078e3194ab06428222d65abb9c827f6879607ce61

```text
Extra hashes: Other values required to make this block unique, such as LoRA IDs, multi-modality input hashes (see the example below), and cache salts to isolate caches in multi-tenant environments.
```

## official-002-2 · dev · conditional

vLLM v0.10.2：两个适配器使用相同文本，是否可以只按文本共享缓存？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/design/prefix_caching.md

规范化行 19-19；SHA256 0a8a9e9095055c4f8e0cdaf078e3194ab06428222d65abb9c827f6879607ce61

```text
Extra hashes: Other values required to make this block unique, such as LoRA IDs, multi-modality input hashes (see the example below), and cache salts to isolate caches in multi-tenant environments.
```

## official-002-3 · dev · debugging

vLLM v0.10.2：多租户前缀相同但需要隔离，应检查缓存键中的什么信息？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/design/prefix_caching.md

规范化行 19-19；SHA256 0a8a9e9095055c4f8e0cdaf078e3194ab06428222d65abb9c827f6879607ce61

```text
Extra hashes: Other values required to make this block unique, such as LoRA IDs, multi-modality input hashes (see the example below), and cache salts to isolate caches in multi-tenant environments.
```

## official-002-4 · dev · multi_hop

vLLM v0.10.2：先确认服务模型支持LoRA，再考虑两个LoRA请求文本相同，为什么缓存键仍需额外区分身份？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。；服务模型须支持LoRA；切换适配器时缓存键还需要适配器身份。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/design/prefix_caching.md

规范化行 19-19；SHA256 0a8a9e9095055c4f8e0cdaf078e3194ab06428222d65abb9c827f6879607ce61

```text
Extra hashes: Other values required to make this block unique, such as LoRA IDs, multi-modality input hashes (see the example below), and cache salts to isolate caches in multi-tenant environments.
```

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/lora.md

规范化行 5-5；SHA256 ea46686b99b86733243e952f49574c17f9011b5a96ca270a48f4d140c1a3d6c8

```text
LoRA adapters can be used with any vLLM model that implements
```

## official-004-1 · dev · single_hop

vLLM v0.10.2：Ampere在此版本支持的FP8配置与kernel是什么？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/quantization/fp8.md

规范化行 5-5；SHA256 a8df8bd97e708315f83286e9390250a0e8292d8d205fe4c12e2a1ff23dadfb43

```text
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

## official-004-2 · dev · conditional

vLLM v0.10.2：能否把Ampere的W8A16支持解释为W8A8？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/quantization/fp8.md

规范化行 5-5；SHA256 a8df8bd97e708315f83286e9390250a0e8292d8d205fe4c12e2a1ff23dadfb43

```text
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

## official-004-3 · dev · debugging

vLLM v0.10.2：在Ampere部署FP8模型时把激活也按8bit支持处理，应先核对哪个限制？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/quantization/fp8.md

规范化行 5-5；SHA256 a8df8bd97e708315f83286e9390250a0e8292d8d205fe4c12e2a1ff23dadfb43

```text
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

## official-004-4 · dev · multi_hop

vLLM v0.10.2：先界定vLLM Ampere FP8支持的精度组合，再判断能否把它照搬到SGLang AMD DeepSeekV3，应核对PR中的哪种FP8格式？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：Ampere的该支持是使用Marlin的W8A16权重量化。；Ampere的W8A16不是通用W8A8保证；AMD DeepSeekV3修复另涉及e4m3fnuz，需按硬件和模型核验。

禁止误读：Ampere文档中的该支持等同于W8A8。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/quantization/fp8.md

规范化行 5-5；SHA256 a8df8bd97e708315f83286e9390250a0e8292d8d205fe4c12e2a1ff23dadfb43

```text
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

https://github.com/sgl-project/sglang/pull/2601

规范化行 9-9；SHA256 e28cfb8d7430a6e546c1052f45e6c67fc4244acc4b891214436e8c516f6ac88f

```text
Add proper fix for AMD FP8 ```e4m3fnuz``` to support DeepseekV3 FP8 model
```

## official-005-1 · dev · single_hop

vLLM v0.10.2：KV空间不足导致抢占后，请求如何恢复执行？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/configuration/optimization.md

规范化行 11-12；SHA256 3e1569ff97083516ee6a7df4da07712ace4c5d7cfafb9e7a328ce2583d24dacb

```text
Preempted requests are recomputed when sufficient KV cache space becomes
available again.
```

## official-005-2 · dev · conditional

vLLM v0.10.2：抢占是否意味着后续恢复完全不需要重算？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/configuration/optimization.md

规范化行 11-12；SHA256 3e1569ff97083516ee6a7df4da07712ace4c5d7cfafb9e7a328ce2583d24dacb

```text
Preempted requests are recomputed when sufficient KV cache space becomes
available again.
```

## official-005-3 · dev · debugging

vLLM v0.10.2：并发过高出现preemption警告，应如何解释恢复阶段的额外计算？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/configuration/optimization.md

规范化行 11-12；SHA256 3e1569ff97083516ee6a7df4da07712ace4c5d7cfafb9e7a328ce2583d24dacb

```text
Preempted requests are recomputed when sufficient KV cache space becomes
available again.
```

## official-005-4 · dev · multi_hop

vLLM v0.10.2：先解释KV空间不足时抢占请求的恢复成本，再从内存优化指南找出将模型跨GPU拆分的参数。

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：被抢占请求会在KV空间足够时重新计算。；KV抢占恢复需要重算；内存优化文档提供tensor_parallel_size将模型分布到多GPU的选项。

禁止误读：抢占后请求必然丢弃或无需重新计算。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/configuration/optimization.md

规范化行 11-12；SHA256 3e1569ff97083516ee6a7df4da07712ace4c5d7cfafb9e7a328ce2583d24dacb

```text
Preempted requests are recomputed when sufficient KV cache space becomes
available again.
```

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/configuration/conserving_memory.md

规范化行 7-7；SHA256 647b5b15894217d540c83354e6db5afd01c9a0e7b20555cd0de12152e7972e32

```text
Tensor parallelism (`tensor_parallel_size` option) can be used to split the model across multiple GPUs.
```

## official-008-1 · dev · single_hop

vLLM v0.10.2：文档对解耦prefill的吞吐收益作出什么限制？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/disagg_prefill.md

规范化行 16-16；SHA256 bb703f15614132c96c72fa8dd84c6d65c77343381675b538274728820399ccf1

```text
Disaggregated prefill DOES NOT improve throughput.
```

## official-008-2 · dev · conditional

vLLM v0.10.2：能否仅凭启用prefill/decode解耦就宣称吞吐提升？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/disagg_prefill.md

规范化行 16-16；SHA256 bb703f15614132c96c72fa8dd84c6d65c77343381675b538274728820399ccf1

```text
Disaggregated prefill DOES NOT improve throughput.
```

## official-008-3 · dev · debugging

vLLM v0.10.2：切换解耦prefill后吞吐没有提升，是否违背文档承诺？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/disagg_prefill.md

规范化行 16-16；SHA256 bb703f15614132c96c72fa8dd84c6d65c77343381675b538274728820399ccf1

```text
Disaggregated prefill DOES NOT improve throughput.
```

## official-008-4 · dev · multi_hop

vLLM v0.10.2：根据SGLang说明先识别分离阶段的作用，再依据vLLM限制判断能否把解耦直接当作吞吐提升保证。

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：文档明确不应把解耦prefill描述成吞吐提升。；先识别prefill/decode阶段干扰，再解释分离阶段用于针对性优化，不能据此宣称vLLM该版本吞吐必涨。

禁止误读：该版本解耦prefill必然提高吞吐。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/disagg_prefill.md

规范化行 16-16；SHA256 bb703f15614132c96c72fa8dd84c6d65c77343381675b538274728820399ccf1

```text
Disaggregated prefill DOES NOT improve throughput.
```

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/pd_disaggregation.md

规范化行 14-14；SHA256 ec630b346ab475567b5a119383f98d5e5a5778af16206b195f08d97fdc50fb2b

```text
PD Disaggregation resolves these by separating the two stages, enabling tailored optimizations for each.
```

## official-010-1 · dev · single_hop

历史修复 PR21611：PR21611怎样让connector区分不同多模态输入的KV？

条件：{'project': 'vllm', 'release': 'historical fix', 'hardware': 'not specified; do not infer'}

参考要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/pull/21611

规范化行 17-17；SHA256 7d3033ada2ece1525b5728dc8ffd910fb884c75a2b660c144aa9c29e56048989

```text
It brings in the mm_hashes from the Request to the connector to form a proper key; that can help distinguish kv for different mm input.
```

## official-010-2 · dev · conditional

历史修复 PR21611：相同文本和相同图像尺寸是否足以安全复用多模态KV？

条件：{'project': 'vllm', 'release': 'historical fix', 'hardware': 'not specified; do not infer'}

参考要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/pull/21611

规范化行 17-17；SHA256 7d3033ada2ece1525b5728dc8ffd910fb884c75a2b660c144aa9c29e56048989

```text
It brings in the mm_hashes from the Request to the connector to form a proper key; that can help distinguish kv for different mm input.
```

## official-010-3 · dev · debugging

历史修复 PR21611：SharedStorageConnector因图片变化返回旧答案，应核对修复中的哪项缓存键信息？

条件：{'project': 'vllm', 'release': 'historical fix', 'hardware': 'not specified; do not infer'}

参考要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/pull/21611

规范化行 17-17；SHA256 7d3033ada2ece1525b5728dc8ffd910fb884c75a2b660c144aa9c29e56048989

```text
It brings in the mm_hashes from the Request to the connector to form a proper key; that can help distinguish kv for different mm input.
```

## official-010-4 · dev · multi_hop

历史修复 PR21611：先从Issue21175辨认错误输出与KV复用的关系，再说明PR21611在哪个输入身份信息上修复了connector缓存键。

条件：{'project': 'vllm', 'release': 'historical fix', 'hardware': 'not specified; do not infer'}

参考要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。；Issue描述不同图像请求误复用KV；对应PR通过请求mm_hashes修正connector键。

禁止误读：图像只需尺寸一致便能安全共用KV。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/pull/21611

规范化行 17-17；SHA256 7d3033ada2ece1525b5728dc8ffd910fb884c75a2b660c144aa9c29e56048989

```text
It brings in the mm_hashes from the Request to the connector to form a proper key; that can help distinguish kv for different mm input.
```

https://github.com/vllm-project/vllm/issues/21175

规范化行 11-11；SHA256 ec9fc7e9ae51f94262d64c578ea0adb2f447d977b7521232250110e014e36b49

```text
It wrongly reuses KV for the later request, which cause it wrongly returning an identical output with the previous request.
```

## official-012-1 · dev · single_hop

SGLang v0.5.2：频繁出现queue-req为零提示什么供给问题？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/hyperparameter_tuning.md

规范化行 13-13；SHA256 4db4ce65864acf8211583ec0e68820869cffc9bf7603edf6e9a4afe73a8f9f00

```text
If you frequently see `#queue-req: 0`, it suggests that your client code is submitting requests too slowly.
```

## official-012-2 · dev · conditional

SGLang v0.5.2：能否仅凭queue-req为零就判定GPU太慢？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/hyperparameter_tuning.md

规范化行 13-13；SHA256 4db4ce65864acf8211583ec0e68820869cffc9bf7603edf6e9a4afe73a8f9f00

```text
If you frequently see `#queue-req: 0`, it suggests that your client code is submitting requests too slowly.
```

## official-012-3 · dev · debugging

SGLang v0.5.2：离线吞吐低且队列经常为空，应先检查请求提交的哪一环？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/hyperparameter_tuning.md

规范化行 13-13；SHA256 4db4ce65864acf8211583ec0e68820869cffc9bf7603edf6e9a4afe73a8f9f00

```text
If you frequently see `#queue-req: 0`, it suggests that your client code is submitting requests too slowly.
```

## official-012-4 · dev · multi_hop

SGLang v0.5.2：先根据queue-req诊断客户端供给，再查服务器内存参数默认值，为什么不能把默认0.9当作队列为空的直接根因？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：频繁队列为空提示客户端提交速度可能太慢。；先检查队列供给而非直接加大内存；mem-fraction-static默认0.9不是所有低吞吐现象的解决办法。

禁止误读：队列为空必然说明GPU算力不足。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/hyperparameter_tuning.md

规范化行 13-13；SHA256 4db4ce65864acf8211583ec0e68820869cffc9bf7603edf6e9a4afe73a8f9f00

```text
If you frequently see `#queue-req: 0`, it suggests that your client code is submitting requests too slowly.
```

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/server_arguments.md

规范化行 23-23；SHA256 3e31923a7a8de9baa0fd32e2c175dca1f630ea9003bf81a8f851d5a132544061

```text
The default value is `0.9`.
```

## official-014-1 · dev · single_hop

SGLang v0.5.2：加载预量化模型时应避免哪个重复量化动作？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/quantization.md

规范化行 14-14；SHA256 962c27de0d84fac54f92d0e550bb8442efe52b559bdc6a19be9ed4efa86a6045

```text
If you use a pre-quantized model, do not add `--quantization` to enable online quantization at the same time.
```

## official-014-2 · dev · conditional

SGLang v0.5.2：模型已经离线量化，是否总应再传quantization启用在线量化？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/quantization.md

规范化行 14-14；SHA256 962c27de0d84fac54f92d0e550bb8442efe52b559bdc6a19be9ed4efa86a6045

```text
If you use a pre-quantized model, do not add `--quantization` to enable online quantization at the same time.
```

## official-014-3 · dev · code_api

SGLang v0.5.2：启动预量化模型时应如何处理用于在线量化的quantization参数？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/quantization.md

规范化行 14-14；SHA256 962c27de0d84fac54f92d0e550bb8442efe52b559bdc6a19be9ed4efa86a6045

```text
If you use a pre-quantized model, do not add `--quantization` to enable online quantization at the same time.
```

## official-014-4 · dev · unanswerable

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在quantization场景下精确的P95延迟毫秒值吗？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

证据缺失理由：未提供私有部署的硬件、模型、输入长度、并发和实测延迟；冻结正文不能确定该部署精确P95。

须审查冻结语料，不能依据检索失败判定。

## official-016-1 · dev · single_hop

SGLang v0.5.2：该路由器有哪些policy选项？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/router.md

规范化行 113-113；SHA256 4906500752aa9a178eee16d41b2b852625431831b53573849fb8387e7180cf39

```text
--policy cache_aware  # or random, round_robin, power_of_two
```

## official-016-2 · dev · conditional

SGLang v0.5.2：cache_aware是否是路由器唯一可用策略？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/router.md

规范化行 113-113；SHA256 4906500752aa9a178eee16d41b2b852625431831b53573849fb8387e7180cf39

```text
--policy cache_aware  # or random, round_robin, power_of_two
```

## official-016-3 · dev · code_api

SGLang v0.5.2：启动路由器时希望选择缓存感知策略，policy参数应填什么？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/router.md

规范化行 113-113；SHA256 4906500752aa9a178eee16d41b2b852625431831b53573849fb8387e7180cf39

```text
--policy cache_aware  # or random, round_robin, power_of_two
```

## official-016-4 · dev · unanswerable

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在router场景下精确的P95延迟毫秒值吗？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

证据缺失理由：未提供私有部署的硬件、模型、输入长度、并发和实测延迟；冻结正文不能确定该部署精确P95。

须审查冻结语料，不能依据检索失败判定。

## official-017-1 · dev · single_hop

SGLang v0.5.2：temperature为零与提高温度分别改变什么采样行为？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/basic_usage/sampling_params.md

规范化行 40-40；SHA256 eb278aedc08be30c0453931457c12381f13c2099720ef468bfe9473803c2b7ce

```text
`temperature = 0` corresponds to greedy sampling, a higher temperature leads to more diversity.
```

## official-017-2 · dev · conditional

SGLang v0.5.2：temperature为零是否意味着均匀随机选择下一token？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/basic_usage/sampling_params.md

规范化行 40-40；SHA256 eb278aedc08be30c0453931457c12381f13c2099720ef468bfe9473803c2b7ce

```text
`temperature = 0` corresponds to greedy sampling, a higher temperature leads to more diversity.
```

## official-017-3 · dev · code_api

SGLang v0.5.2：请求JSON中想启用贪心采样，temperature应设置成多少？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/basic_usage/sampling_params.md

规范化行 40-40；SHA256 eb278aedc08be30c0453931457c12381f13c2099720ef468bfe9473803c2b7ce

```text
`temperature = 0` corresponds to greedy sampling, a higher temperature leads to more diversity.
```

## official-017-4 · dev · unanswerable

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在sampling_params场景下精确的P95延迟毫秒值吗？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

证据缺失理由：未提供私有部署的硬件、模型、输入长度、并发和实测延迟；冻结正文不能确定该部署精确P95。

须审查冻结语料，不能依据检索失败判定。

## official-020-1 · dev · single_hop

SGLang v0.5.2：哪个环境变量控制torch.compile，默认值是什么？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/references/environment_variables.md

规范化行 23-23；SHA256 8c46ce4c475139ecb1daa8e9d94a606095e129ee843750eada9185565d73e737

```text
`SGLANG_ENABLE_TORCH_COMPILE` | Enable torch.compile | `true`
```

## official-020-2 · dev · conditional

SGLang v0.5.2：能否假定SGLANG_ENABLE_TORCH_COMPILE默认关闭？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/references/environment_variables.md

规范化行 23-23；SHA256 8c46ce4c475139ecb1daa8e9d94a606095e129ee843750eada9185565d73e737

```text
`SGLANG_ENABLE_TORCH_COMPILE` | Enable torch.compile | `true`
```

## official-020-3 · dev · code_api

SGLang v0.5.2：排查编译开关时，环境变量SGLANG_ENABLE_TORCH_COMPILE的意义和默认值是什么？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/references/environment_variables.md

规范化行 23-23；SHA256 8c46ce4c475139ecb1daa8e9d94a606095e129ee843750eada9185565d73e737

```text
`SGLANG_ENABLE_TORCH_COMPILE` | Enable torch.compile | `true`
```

## official-020-4 · dev · unanswerable

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在amd_gpu场景下精确的P95延迟毫秒值吗？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

证据缺失理由：未提供私有部署的硬件、模型、输入长度、并发和实测延迟；冻结正文不能确定该部署精确P95。

须审查冻结语料，不能依据检索失败判定。

## official-022-1 · dev · single_hop

CUDA 13.0.1：local与shared memory的作用域和生命周期有何区别？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#memory-hierarchy

规范化行 3-3；SHA256 ef0620cf5fe38149d48980cb5f30d4b1936ba18b19785f54bc60eb894491b883

```text
Each thread has private local memory. Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
```

## official-022-2 · dev · conditional

CUDA 13.0.1：能否把一个普通线程块的shared memory当全grid共享空间？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#memory-hierarchy

规范化行 3-3；SHA256 ef0620cf5fe38149d48980cb5f30d4b1936ba18b19785f54bc60eb894491b883

```text
Each thread has private local memory. Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
```

## official-022-3 · dev · code_api

CUDA 13.0.1：代码中的普通线程块shared memory，其可见范围和生命周期应怎样理解？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#memory-hierarchy

规范化行 3-3；SHA256 ef0620cf5fe38149d48980cb5f30d4b1936ba18b19785f54bc60eb894491b883

```text
Each thread has private local memory. Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
```

## official-022-4 · dev · unanswerable

CUDA 13.0.1：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在memory-hierarchy场景下精确的P95延迟毫秒值吗？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

证据缺失理由：未提供私有部署的硬件、模型、输入长度、并发和实测延迟；冻结正文不能确定该部署精确P95。

须审查冻结语料，不能依据检索失败判定。

## official-024-1 · dev · single_hop

CUDA 13.0.1：矩阵乘示例里shared memory作为缓存主要减少哪种访问？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#shared-memory

规范化行 5-5；SHA256 b70b2ef84dca6f5946c119f5f0b34ddb4f898b610f324afb548c48c69f5c56ea

```text
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

## official-024-2 · dev · conditional

CUDA 13.0.1：shared memory优化是否意味着矩阵乘法运算不再执行？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#shared-memory

规范化行 5-5；SHA256 b70b2ef84dca6f5946c119f5f0b34ddb4f898b610f324afb548c48c69f5c56ea

```text
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

## official-024-3 · dev · code_api

CUDA 13.0.1：__shared__缓冲区为何可以作为减少global访问的暂存空间？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#shared-memory

规范化行 5-5；SHA256 b70b2ef84dca6f5946c119f5f0b34ddb4f898b610f324afb548c48c69f5c56ea

```text
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

## official-024-4 · dev · unanswerable

CUDA 13.0.1：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在shared-memory场景下精确的P95延迟毫秒值吗？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

证据缺失理由：未提供私有部署的硬件、模型、输入长度、并发和实测延迟；冻结正文不能确定该部署精确P95。

须审查冻结语料，不能依据检索失败判定。

## official-026-1 · dev · single_hop

CUDA 13.0.1：Async内存拷贝何时仍可能同步？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#asynchronous-concurrent-execution

规范化行 35-35；SHA256 6167d857cfa9fd78264f595af7ef8e0b2dc9add6720cf00c56f97e6cf12d8f28

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

## official-026-2 · dev · code_api

CUDA 13.0.1：调用Async传输却未得到预期重叠，应先检查主机缓冲区的什么属性？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#asynchronous-concurrent-execution

规范化行 35-35；SHA256 6167d857cfa9fd78264f595af7ef8e0b2dc9add6720cf00c56f97e6cf12d8f28

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

## official-026-3 · dev · debugging

CUDA 13.0.1：排查该主题时，有人声称“所有带Async后缀的调用都无条件异步。”，根据文档这个说法哪里需要纠正？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#asynchronous-concurrent-execution

规范化行 35-35；SHA256 6167d857cfa9fd78264f595af7ef8e0b2dc9add6720cf00c56f97e6cf12d8f28

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

## official-026-4 · dev · debugging

CUDA 13.0.1：对asynchronous-concurrent-execution相关代码进行review时，为何不能接受“所有带Async后缀的调用都无条件异步。”作为正确性依据？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#asynchronous-concurrent-execution

规范化行 35-35；SHA256 6167d857cfa9fd78264f595af7ef8e0b2dc9add6720cf00c56f97e6cf12d8f28

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

## official-028-1 · dev · single_hop

CUDA 13.0.1：CUDA Graph如何表达操作关系以及定义与执行？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#cuda-graphs

规范化行 3-3；SHA256 38a73acf853bd504b51cd5863d0073ab54f20298c5ed584da8908772b1ff42c8

```text
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
```

## official-028-2 · dev · code_api

CUDA 13.0.1：审核Graph节点依赖代码时，应怎样区分图定义与实际执行？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#cuda-graphs

规范化行 3-3；SHA256 38a73acf853bd504b51cd5863d0073ab54f20298c5ed584da8908772b1ff42c8

```text
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
```

## official-028-3 · dev · debugging

CUDA 13.0.1：排查该主题时，有人声称“CUDA Graph只是把相互依赖的kernel无条件同时启动。”，根据文档这个说法哪里需要纠正？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#cuda-graphs

规范化行 3-3；SHA256 38a73acf853bd504b51cd5863d0073ab54f20298c5ed584da8908772b1ff42c8

```text
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
```

## official-028-4 · dev · debugging

CUDA 13.0.1：对cuda-graphs相关代码进行review时，为何不能接受“CUDA Graph只是把相互依赖的kernel无条件同时启动。”作为正确性依据？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#cuda-graphs

规范化行 3-3；SHA256 38a73acf853bd504b51cd5863d0073ab54f20298c5ed584da8908772b1ff42c8

```text
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
```

## official-030-1 · dev · single_hop

CUDA 13.0.1：CUDA利用率指南建议怎样划分host与device工作？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#maximize-utilization

规范化行 7-7；SHA256 a9a415a77b13676be9949caf74e7989415ce1e7379adcbfe9eed0ef7a4555044

```text
It should assign to each processor the type of work it does best: serial workloads to the host; parallel workloads to the devices.
```

## official-030-2 · dev · code_api

CUDA 13.0.1：异构代码中的串行控制循环与数据并行运算，按指南应分别放在host还是device？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#maximize-utilization

规范化行 7-7；SHA256 a9a415a77b13676be9949caf74e7989415ce1e7379adcbfe9eed0ef7a4555044

```text
It should assign to each processor the type of work it does best: serial workloads to the host; parallel workloads to the devices.
```

## official-030-3 · dev · debugging

CUDA 13.0.1：排查该主题时，有人声称“所有串行工作都应无条件搬到GPU。”，根据文档这个说法哪里需要纠正？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#maximize-utilization

规范化行 7-7；SHA256 a9a415a77b13676be9949caf74e7989415ce1e7379adcbfe9eed0ef7a4555044

```text
It should assign to each processor the type of work it does best: serial workloads to the host; parallel workloads to the devices.
```

## official-030-4 · dev · debugging

CUDA 13.0.1：对maximize-utilization相关代码进行review时，为何不能接受“所有串行工作都应无条件搬到GPU。”作为正确性依据？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#maximize-utilization

规范化行 7-7；SHA256 a9a415a77b13676be9949caf74e7989415ce1e7379adcbfe9eed0ef7a4555044

```text
It should assign to each processor the type of work it does best: serial workloads to the host; parallel workloads to the devices.
```

## official-001-1 · holdout · single_hop

vLLM v0.10.2：APC复用什么数据，哪部分计算可以跳过？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：共享前缀可复用已有KV并跳过共享部分计算。

禁止误读：没有共享前缀也必然命中APC。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/automatic_prefix_caching.md

规范化行 5-5；SHA256 a939df40f6cde38cc48701cfee6626dbdc73c4f1e5df46921a7b88c496e31580

```text
Automatic Prefix Caching (APC in short) caches the KV cache of existing queries, so that a new query can directly reuse the KV cache if it shares the same prefix with one of the existing queries, allowing the new query to skip the computation of the shared part.
```

## official-001-2 · holdout · conditional

vLLM v0.10.2：两条请求只是长度相同但前缀不同，能据此保证APC命中吗？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：共享前缀可复用已有KV并跳过共享部分计算。

禁止误读：没有共享前缀也必然命中APC。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/automatic_prefix_caching.md

规范化行 5-5；SHA256 a939df40f6cde38cc48701cfee6626dbdc73c4f1e5df46921a7b88c496e31580

```text
Automatic Prefix Caching (APC in short) caches the KV cache of existing queries, so that a new query can directly reuse the KV cache if it shares the same prefix with one of the existing queries, allowing the new query to skip the computation of the shared part.
```

## official-001-3 · holdout · debugging

vLLM v0.10.2：聊天请求前缀相同却重复做prefill，为什么应检查前缀缓存配置？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：共享前缀可复用已有KV并跳过共享部分计算。

禁止误读：没有共享前缀也必然命中APC。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/automatic_prefix_caching.md

规范化行 5-5；SHA256 a939df40f6cde38cc48701cfee6626dbdc73c4f1e5df46921a7b88c496e31580

```text
Automatic Prefix Caching (APC in short) caches the KV cache of existing queries, so that a new query can directly reuse the KV cache if it shares the same prefix with one of the existing queries, allowing the new query to skip the computation of the shared part.
```

## official-001-4 · holdout · multi_hop

vLLM v0.10.2：共享前缀命中和FP8 KV同时开启时，先判断哪部分计算可跳过，再说明为何不能仅凭FP8保证单token延迟下降？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：共享前缀可复用已有KV并跳过共享部分计算。；缓存命中可跳过共享计算；FP8 KV容量收益不能直接当成该版本的单token延迟收益。

禁止误读：没有共享前缀也必然命中APC。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/automatic_prefix_caching.md

规范化行 5-5；SHA256 a939df40f6cde38cc48701cfee6626dbdc73c4f1e5df46921a7b88c496e31580

```text
Automatic Prefix Caching (APC in short) caches the KV cache of existing queries, so that a new query can directly reuse the KV cache if it shares the same prefix with one of the existing queries, allowing the new query to skip the computation of the shared part.
```

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/quantization/quantized_kvcache.md

规范化行 27-27；SHA256 ebe7a216031897781b796d7b8f94c4f4cc274b26436f225debeb3b662a4d216a

```text
However, there are currently no latency improvements as the implementation does not yet include fused dequantization and attention operations.
```

## official-003-1 · holdout · single_hop

vLLM v0.10.2：FP8 KV缓存主要改变哪项容量及吞吐因素？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：FP8 KV缓存减小占用，使缓存能存更多token并改善吞吐。

禁止误读：减小缓存占用等于无条件降低每token延迟。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/quantization/quantized_kvcache.md

规范化行 5-5；SHA256 ebe7a216031897781b796d7b8f94c4f4cc274b26436f225debeb3b662a4d216a

```text
Quantizing the KV cache to FP8 reduces its memory footprint. This increases the number of tokens that can be stored in the cache, improving throughput.
```

## official-003-2 · holdout · conditional

vLLM v0.10.2：FP8让缓存能装更多token，是否就证明每token延迟必然下降？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：FP8 KV缓存减小占用，使缓存能存更多token并改善吞吐。

禁止误读：减小缓存占用等于无条件降低每token延迟。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/quantization/quantized_kvcache.md

规范化行 5-5；SHA256 ebe7a216031897781b796d7b8f94c4f4cc274b26436f225debeb3b662a4d216a

```text
Quantizing the KV cache to FP8 reduces its memory footprint. This increases the number of tokens that can be stored in the cache, improving throughput.
```

## official-003-3 · holdout · debugging

vLLM v0.10.2：长序列并发受KV容量限制时，FP8 KV缓存提供哪种改善路径？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：FP8 KV缓存减小占用，使缓存能存更多token并改善吞吐。

禁止误读：减小缓存占用等于无条件降低每token延迟。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/quantization/quantized_kvcache.md

规范化行 5-5；SHA256 ebe7a216031897781b796d7b8f94c4f4cc274b26436f225debeb3b662a4d216a

```text
Quantizing the KV cache to FP8 reduces its memory footprint. This increases the number of tokens that can be stored in the cache, improving throughput.
```

## official-003-4 · holdout · multi_hop

vLLM v0.10.2：若瓶颈是KV容量，先依据vLLM FP8 KV说明判断改善方向，再在SGLang backend示例中识别对应的TRTLLM MLA配置收益。

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：FP8 KV缓存减小占用，使缓存能存更多token并改善吞吐。；先识别KV容量瓶颈，再关联TRTLLM MLA的FP8 KV配置同样针对占用和并发。

禁止误读：减小缓存占用等于无条件降低每token延迟。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/quantization/quantized_kvcache.md

规范化行 5-5；SHA256 ebe7a216031897781b796d7b8f94c4f4cc274b26436f225debeb3b662a4d216a

```text
Quantizing the KV cache to FP8 reduces its memory footprint. This increases the number of tokens that can be stored in the cache, improving throughput.
```

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/attention_backend.md

规范化行 64-64；SHA256 4dd78b3ecd450f648444ce44ccf00fcad1554f143c7a85e365b68a16e1cfd6af

```text
TRTLLM MLA with FP8 KV Cache (Higher concurrency, lower memory footprint)
```

## official-006-1 · holdout · single_hop

vLLM v0.10.2：该版本推测解码与哪种模型并行不兼容？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：该版本推测解码与流水线并行不兼容。

禁止误读：此版本可以无条件同时启用推测解码和PP。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/spec_decode.md

规范化行 9-9；SHA256 4bde33d57788d27d8750d462352edeb515e5248f850b5164bd1b1e2c3e034462

```text
Currently, speculative decoding in vLLM is not compatible with pipeline parallelism.
```

## official-006-2 · holdout · conditional

vLLM v0.10.2：使用pipeline parallelism时，能直接启用推测解码吗？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：该版本推测解码与流水线并行不兼容。

禁止误读：此版本可以无条件同时启用推测解码和PP。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/spec_decode.md

规范化行 9-9；SHA256 4bde33d57788d27d8750d462352edeb515e5248f850b5164bd1b1e2c3e034462

```text
Currently, speculative decoding in vLLM is not compatible with pipeline parallelism.
```

## official-006-3 · holdout · debugging

vLLM v0.10.2：已经配置PP的部署新增推测解码失败，应先检查哪条兼容性声明？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：该版本推测解码与流水线并行不兼容。

禁止误读：此版本可以无条件同时启用推测解码和PP。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/spec_decode.md

规范化行 9-9；SHA256 4bde33d57788d27d8750d462352edeb515e5248f850b5164bd1b1e2c3e034462

```text
Currently, speculative decoding in vLLM is not compatible with pipeline parallelism.
```

## official-006-4 · holdout · multi_hop

vLLM v0.10.2：先从多节点部署指南识别节点数对应的并行参数，再据推测解码兼容性判断能否直接叠加该功能。

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：该版本推测解码与流水线并行不兼容。；跨节点方案可能引入PP；一旦采用PP，该版本不能直接叠加推测解码。

禁止误读：此版本可以无条件同时启用推测解码和PP。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/spec_decode.md

规范化行 9-9；SHA256 4bde33d57788d27d8750d462352edeb515e5248f850b5164bd1b1e2c3e034462

```text
Currently, speculative decoding in vLLM is not compatible with pipeline parallelism.
```

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/serving/parallelism_scaling.md

规范化行 11-11；SHA256 99147da2d0bf7eef92ac3f28a885aeb401a5cf48d0c2f28c6ec2911d29d81b96

```text
Increase the number of GPUs and nodes until there is enough GPU memory for the model. Set `tensor_parallel_size` to the number of GPUs per node and `pipeline_parallel_size` to the number of nodes.
```

## official-007-1 · holdout · single_hop

vLLM v0.10.2：一级睡眠对权重和KV缓存分别做什么？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：一级睡眠卸载权重并丢弃KV缓存，缓存内容不会保留。

禁止误读：一级睡眠完整保留旧KV内容。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/sleep_mode.md

规范化行 18-18；SHA256 f0316decf7985681413ca5ece1a238725da31e38c6ad228f5461a211e1833b60

```text
Level 1 sleep will offload the model weights and discard the KV cache. The content of KV cache is forgotten.
```

## official-007-2 · holdout · conditional

vLLM v0.10.2：一级睡眠醒来后能否假定之前的KV内容仍然存在？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：一级睡眠卸载权重并丢弃KV缓存，缓存内容不会保留。

禁止误读：一级睡眠完整保留旧KV内容。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/sleep_mode.md

规范化行 18-18；SHA256 f0316decf7985681413ca5ece1a238725da31e38c6ad228f5461a211e1833b60

```text
Level 1 sleep will offload the model weights and discard the KV cache. The content of KV cache is forgotten.
```

## official-007-3 · holdout · debugging

vLLM v0.10.2：睡眠后旧会话缓存无法直接复用，这是否符合一级睡眠的设计？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：一级睡眠卸载权重并丢弃KV缓存，缓存内容不会保留。

禁止误读：一级睡眠完整保留旧KV内容。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/sleep_mode.md

规范化行 18-18；SHA256 f0316decf7985681413ca5ece1a238725da31e38c6ad228f5461a211e1833b60

```text
Level 1 sleep will offload the model weights and discard the KV cache. The content of KV cache is forgotten.
```

## official-007-4 · holdout · multi_hop

vLLM v0.10.2：先判断一级睡眠是否保留KV，再结合前缀缓存只缓存完整块的规则，解释醒来后为何不能直接假定旧完整块仍可复用。

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：一级睡眠卸载权重并丢弃KV缓存，缓存内容不会保留。；一级睡眠忘记KV；前缀缓存的完整块复用前提需要重新建立，不能假定旧KV仍在。

禁止误读：一级睡眠完整保留旧KV内容。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/sleep_mode.md

规范化行 18-18；SHA256 f0316decf7985681413ca5ece1a238725da31e38c6ad228f5461a211e1833b60

```text
Level 1 sleep will offload the model weights and discard the KV cache. The content of KV cache is forgotten.
```

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/design/prefix_caching.md

规范化行 22-22；SHA256 0a8a9e9095055c4f8e0cdaf078e3194ab06428222d65abb9c827f6879607ce61

```text
We only cache full blocks.
```

## official-009-1 · holdout · single_hop

vLLM v0.10.2：LoRA适配器服务的选择粒度是什么？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：适配器可以按请求提供服务。

禁止误读：所有请求只能使用同一个固定适配器。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/lora.md

规范化行 7-7；SHA256 ea46686b99b86733243e952f49574c17f9011b5a96ca270a48f4d140c1a3d6c8

```text
Adapters can be efficiently served on a per request basis with minimal overhead.
```

## official-009-2 · holdout · conditional

vLLM v0.10.2：同一基座服务是否意味着全部请求只能固定用一个LoRA？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：适配器可以按请求提供服务。

禁止误读：所有请求只能使用同一个固定适配器。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/lora.md

规范化行 7-7；SHA256 ea46686b99b86733243e952f49574c17f9011b5a96ca270a48f4d140c1a3d6c8

```text
Adapters can be efficiently served on a per request basis with minimal overhead.
```

## official-009-3 · holdout · debugging

vLLM v0.10.2：需要不同请求选用不同LoRA，应采用什么粒度的适配器服务？

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：适配器可以按请求提供服务。

禁止误读：所有请求只能使用同一个固定适配器。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/lora.md

规范化行 7-7；SHA256 ea46686b99b86733243e952f49574c17f9011b5a96ca270a48f4d140c1a3d6c8

```text
Adapters can be efficiently served on a per request basis with minimal overhead.
```

## official-009-4 · holdout · multi_hop

vLLM v0.10.2：在按请求选择LoRA的服务中，先确定请求级身份，再结合父块哈希规则说明为何不能只以当前块文本识别整个前缀。

条件：{'project': 'vllm', 'release': 'v0.10.2', 'hardware': 'not specified; do not infer'}

参考要点：适配器可以按请求提供服务。；按请求选择LoRA后，需要按请求适配器身份维护缓存键，且块哈希包含前缀父哈希。

禁止误读：所有请求只能使用同一个固定适配器。

证据组（组内全部需要）：primary

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/lora.md

规范化行 7-7；SHA256 ea46686b99b86733243e952f49574c17f9011b5a96ca270a48f4d140c1a3d6c8

```text
Adapters can be efficiently served on a per request basis with minimal overhead.
```

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/design/prefix_caching.md

规范化行 17-17；SHA256 0a8a9e9095055c4f8e0cdaf078e3194ab06428222d65abb9c827f6879607ce61

```text
The hash value of the parent hash block.
```

## official-011-1 · holdout · single_hop

SGLang v0.5.2：FAQ给出的提高输出确定性的两项措施是什么？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：排查时可禁用radix缓存并每次只发送一个请求以提高确定性。

禁止误读：只设temperature=0就保证所有部署完全确定。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/references/faq.md

规范化行 29-29；SHA256 6045b49a4af1ac350e565a549790f66d5cac69d6f2518d27f34fc750d48cd948

```text
To achieve more deterministic outputs in the current code, you can add `--disable-radix-cache` and send only one request at a time.
```

## official-011-2 · holdout · conditional

SGLang v0.5.2：只修改温度而保留并发请求，是否完成FAQ建议的确定性排查？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：排查时可禁用radix缓存并每次只发送一个请求以提高确定性。

禁止误读：只设temperature=0就保证所有部署完全确定。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/references/faq.md

规范化行 29-29；SHA256 6045b49a4af1ac350e565a549790f66d5cac69d6f2518d27f34fc750d48cd948

```text
To achieve more deterministic outputs in the current code, you can add `--disable-radix-cache` and send only one request at a time.
```

## official-011-3 · holdout · debugging

SGLang v0.5.2：相同请求温度为零仍略有差异，应怎样缩小复现实验条件？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：排查时可禁用radix缓存并每次只发送一个请求以提高确定性。

禁止误读：只设temperature=0就保证所有部署完全确定。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/references/faq.md

规范化行 29-29；SHA256 6045b49a4af1ac350e565a549790f66d5cac69d6f2518d27f34fc750d48cd948

```text
To achieve more deterministic outputs in the current code, you can add `--disable-radix-cache` and send only one request at a time.
```

## official-011-4 · holdout · multi_hop

SGLang v0.5.2：先依据FAQ找到确定性排查开关，再查参数表说明它禁用了哪种缓存能力及默认状态。

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：排查时可禁用radix缓存并每次只发送一个请求以提高确定性。；FAQ建议禁用radix缓存并串行请求；参数表说明该开关禁用RadixAttention前缀缓存且默认False。

禁止误读：只设temperature=0就保证所有部署完全确定。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/references/faq.md

规范化行 29-29；SHA256 6045b49a4af1ac350e565a549790f66d5cac69d6f2518d27f34fc750d48cd948

```text
To achieve more deterministic outputs in the current code, you can add `--disable-radix-cache` and send only one request at a time.
```

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/server_arguments.md

规范化行 250-250；SHA256 3e31923a7a8de9baa0fd32e2c175dca1f630ea9003bf81a8f851d5a132544061

```text
`--disable-radix-cache` | Disable RadixAttention for prefix caching. | False
```

## official-013-1 · holdout · single_hop

SGLang v0.5.2：TRTLLM MLA对prefill和decode的覆盖分别是什么？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：TRTLLM MLA负责decode，prefill包括多模态回退到FlashInfer MLA。

禁止误读：TRTLLM MLA独立覆盖全部prefill和decode。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/attention_backend.md

规范化行 20-20；SHA256 4dd78b3ecd450f648444ce44ccf00fcad1554f143c7a85e365b68a16e1cfd6af

```text
TRTLLM MLA only implements decode operations. For prefill operations (including multimodal inputs), it falls back to FlashInfer MLA backend.
```

## official-013-2 · holdout · conditional

SGLang v0.5.2：选TRTLLM MLA后，多模态prefill是否也由同一实现完成？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：TRTLLM MLA负责decode，prefill包括多模态回退到FlashInfer MLA。

禁止误读：TRTLLM MLA独立覆盖全部prefill和decode。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/attention_backend.md

规范化行 20-20；SHA256 4dd78b3ecd450f648444ce44ccf00fcad1554f143c7a85e365b68a16e1cfd6af

```text
TRTLLM MLA only implements decode operations. For prefill operations (including multimodal inputs), it falls back to FlashInfer MLA backend.
```

## official-013-3 · holdout · code_api

SGLang v0.5.2：配置attention backend为TRTLLM MLA后，prefill阶段的实际backend应如何理解？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：TRTLLM MLA负责decode，prefill包括多模态回退到FlashInfer MLA。

禁止误读：TRTLLM MLA独立覆盖全部prefill和decode。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/attention_backend.md

规范化行 20-20；SHA256 4dd78b3ecd450f648444ce44ccf00fcad1554f143c7a85e365b68a16e1cfd6af

```text
TRTLLM MLA only implements decode operations. For prefill operations (including multimodal inputs), it falls back to FlashInfer MLA backend.
```

## official-013-4 · holdout · unanswerable

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在attention_backend场景下精确的P95延迟毫秒值吗？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

证据缺失理由：未提供私有部署的硬件、模型、输入长度、并发和实测延迟；冻结正文不能确定该部署精确P95。

须审查冻结语料，不能依据检索失败判定。

## official-015-1 · holdout · single_hop

SGLang v0.5.2：DP attention中哪些阶段的不均衡会增加decode延迟？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：DP attention不同worker处理不同阶段可能增加decode延迟。

禁止误读：prefill/decode阶段不均衡不会影响decode延迟。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/pd_disaggregation.md

规范化行 12-12；SHA256 ec630b346ab475567b5a119383f98d5e5a5778af16206b195f08d97fdc50fb2b

```text
In data-parallel (DP) attention, one DP worker may process a prefill batch while another handles a decode batch simultaneously, leading to increased decode latency.
```

## official-015-2 · holdout · conditional

SGLang v0.5.2：不同DP worker同时分别跑prefill与decode，能否认为对延迟完全无影响？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：DP attention不同worker处理不同阶段可能增加decode延迟。

禁止误读：prefill/decode阶段不均衡不会影响decode延迟。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/pd_disaggregation.md

规范化行 12-12；SHA256 ec630b346ab475567b5a119383f98d5e5a5778af16206b195f08d97fdc50fb2b

```text
In data-parallel (DP) attention, one DP worker may process a prefill batch while another handles a decode batch simultaneously, leading to increased decode latency.
```

## official-015-3 · holdout · code_api

SGLang v0.5.2：阅读DP attention并行执行代码时，两个worker分别处理prefill和decode会带来什么延迟风险？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：DP attention不同worker处理不同阶段可能增加decode延迟。

禁止误读：prefill/decode阶段不均衡不会影响decode延迟。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/pd_disaggregation.md

规范化行 12-12；SHA256 ec630b346ab475567b5a119383f98d5e5a5778af16206b195f08d97fdc50fb2b

```text
In data-parallel (DP) attention, one DP worker may process a prefill batch while another handles a decode batch simultaneously, leading to increased decode latency.
```

## official-015-4 · holdout · unanswerable

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在pd_disaggregation场景下精确的P95延迟毫秒值吗？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

证据缺失理由：未提供私有部署的硬件、模型、输入长度、并发和实测延迟；冻结正文不能确定该部署精确P95。

须审查冻结语料，不能依据检索失败判定。

## official-018-1 · holdout · single_hop

SGLang v0.5.2：多机部署时怎样复用torch.compile缓存？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：文档建议分发torch.compile缓存以跳过其他机器上的编译步骤。

禁止误读：部署到其他机器必须无条件重新编译，缓存不能分发。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/references/torch_compile_cache.md

规范化行 4-4；SHA256 4b9088332c5e70eec69fa7f6203edfa3445a7ccdf46bc8b5fff43a7d2173e727

```text
If you want to deploy a model on many different machines, you can ship the torch.compile cache to these machines and skip the compilation steps.
```

## official-018-2 · holdout · conditional

SGLang v0.5.2：每台机器都必须重新做相同的compile调优吗？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：文档建议分发torch.compile缓存以跳过其他机器上的编译步骤。

禁止误读：部署到其他机器必须无条件重新编译，缓存不能分发。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/references/torch_compile_cache.md

规范化行 4-4；SHA256 4b9088332c5e70eec69fa7f6203edfa3445a7ccdf46bc8b5fff43a7d2173e727

```text
If you want to deploy a model on many different machines, you can ship the torch.compile cache to these machines and skip the compilation steps.
```

## official-018-3 · holdout · code_api

SGLang v0.5.2：编写多机模型部署脚本时，已有torch.compile缓存可怎样用于避免重复编译？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：文档建议分发torch.compile缓存以跳过其他机器上的编译步骤。

禁止误读：部署到其他机器必须无条件重新编译，缓存不能分发。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/references/torch_compile_cache.md

规范化行 4-4；SHA256 4b9088332c5e70eec69fa7f6203edfa3445a7ccdf46bc8b5fff43a7d2173e727

```text
If you want to deploy a model on many different machines, you can ship the torch.compile cache to these machines and skip the compilation steps.
```

## official-018-4 · holdout · unanswerable

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在torch_compile_cache场景下精确的P95延迟毫秒值吗？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

证据缺失理由：未提供私有部署的硬件、模型、输入长度、并发和实测延迟；冻结正文不能确定该部署精确P95。

须审查冻结语料，不能依据检索失败判定。

## official-019-1 · holdout · single_hop

SGLang v0.5.2：安装报CUDA_HOME未设置时，需要先指定什么目录？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：CUDA_HOME缺失时应指向本机CUDA安装根目录。

禁止误读：可以不检查安装目录就把CUDA_HOME设成任意路径。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/get_started/install.md

规范化行 19-19；SHA256 95e2deb4f3057612af0379b7a1ddeaa7a920234c595147301cf3fcd8e6982d41

```text
Please set it to your CUDA install root with either of the following solutions:
```

## official-019-2 · holdout · conditional

SGLang v0.5.2：能否直接把别人的CUDA路径照抄为本机CUDA_HOME？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：CUDA_HOME缺失时应指向本机CUDA安装根目录。

禁止误读：可以不检查安装目录就把CUDA_HOME设成任意路径。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/get_started/install.md

规范化行 19-19；SHA256 95e2deb4f3057612af0379b7a1ddeaa7a920234c595147301cf3fcd8e6982d41

```text
Please set it to your CUDA install root with either of the following solutions:
```

## official-019-3 · holdout · code_api

SGLang v0.5.2：针对CUDA_HOME未设置报错，环境变量应表达什么路径？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：CUDA_HOME缺失时应指向本机CUDA安装根目录。

禁止误读：可以不检查安装目录就把CUDA_HOME设成任意路径。

证据组（组内全部需要）：primary

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/get_started/install.md

规范化行 19-19；SHA256 95e2deb4f3057612af0379b7a1ddeaa7a920234c595147301cf3fcd8e6982d41

```text
Please set it to your CUDA install root with either of the following solutions:
```

## official-019-4 · holdout · unanswerable

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在install场景下精确的P95延迟毫秒值吗？

条件：{'project': 'sglang', 'release': 'v0.5.2', 'hardware': 'not specified; do not infer'}

参考要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

证据缺失理由：未提供私有部署的硬件、模型、输入长度、并发和实测延迟；冻结正文不能确定该部署精确P95。

须审查冻结语料，不能依据检索失败判定。

## official-021-1 · holdout · single_hop

CUDA 13.0.1：CUDA线程块需要满足什么调度独立性要求？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：线程块需独立执行，不能依赖块的固定调度顺序。

禁止误读：同一grid的块总会按索引顺序执行。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#thread-hierarchy

规范化行 64-64；SHA256 71764f72e7062cf2a1a2bbed31afb4c3b5fb572e3ce32e6c24b808fa96d6af22

```text
Thread blocks are required to execute independently. It must be possible to execute blocks in any order, in parallel or in series.
```

## official-021-2 · holdout · conditional

CUDA 13.0.1：一个块等待下一个索引块先运行，这种设计是否符合独立性要求？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：线程块需独立执行，不能依赖块的固定调度顺序。

禁止误读：同一grid的块总会按索引顺序执行。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#thread-hierarchy

规范化行 64-64；SHA256 71764f72e7062cf2a1a2bbed31afb4c3b5fb572e3ce32e6c24b808fa96d6af22

```text
Thread blocks are required to execute independently. It must be possible to execute blocks in any order, in parallel or in series.
```

## official-021-3 · holdout · code_api

CUDA 13.0.1：代码用线程块索引推断执行先后，这是否符合thread block独立执行要求？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：线程块需独立执行，不能依赖块的固定调度顺序。

禁止误读：同一grid的块总会按索引顺序执行。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#thread-hierarchy

规范化行 64-64；SHA256 71764f72e7062cf2a1a2bbed31afb4c3b5fb572e3ce32e6c24b808fa96d6af22

```text
Thread blocks are required to execute independently. It must be possible to execute blocks in any order, in parallel or in series.
```

## official-021-4 · holdout · unanswerable

CUDA 13.0.1：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在thread-hierarchy场景下精确的P95延迟毫秒值吗？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

证据缺失理由：未提供私有部署的硬件、模型、输入长度、并发和实测延迟；冻结正文不能确定该部署精确P95。

须审查冻结语料，不能依据检索失败判定。

## official-023-1 · holdout · single_hop

CUDA 13.0.1：设备线性内存的分配、释放和拷贝常用哪三个API？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：设备线性内存通常用cudaMalloc分配、cudaFree释放，主设备传输用cudaMemcpy。

禁止误读：cudaFree负责分配内存或cudaMalloc负责拷贝。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#device-memory

规范化行 39-39；SHA256 ed213e07968b4cc0abcb6a0af1e2d1859e9bd98bf3b7f1ae6d69ca26fda19d03

```text
Linear memory is typically allocated using cudaMalloc() and freed using cudaFree() and data transfer between host memory and device memory are typically done using cudaMemcpy().
```

## official-023-2 · holdout · conditional

CUDA 13.0.1：分配设备内存之后是否等于已经完成主机数据拷贝？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：设备线性内存通常用cudaMalloc分配、cudaFree释放，主设备传输用cudaMemcpy。

禁止误读：cudaFree负责分配内存或cudaMalloc负责拷贝。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#device-memory

规范化行 39-39；SHA256 ed213e07968b4cc0abcb6a0af1e2d1859e9bd98bf3b7f1ae6d69ca26fda19d03

```text
Linear memory is typically allocated using cudaMalloc() and freed using cudaFree() and data transfer between host memory and device memory are typically done using cudaMemcpy().
```

## official-023-3 · holdout · code_api

CUDA 13.0.1：将设备内存生命周期和传输分开，分别应使用什么API？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：设备线性内存通常用cudaMalloc分配、cudaFree释放，主设备传输用cudaMemcpy。

禁止误读：cudaFree负责分配内存或cudaMalloc负责拷贝。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#device-memory

规范化行 39-39；SHA256 ed213e07968b4cc0abcb6a0af1e2d1859e9bd98bf3b7f1ae6d69ca26fda19d03

```text
Linear memory is typically allocated using cudaMalloc() and freed using cudaFree() and data transfer between host memory and device memory are typically done using cudaMemcpy().
```

## official-023-4 · holdout · unanswerable

CUDA 13.0.1：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在device-memory场景下精确的P95延迟毫秒值吗？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

证据缺失理由：未提供私有部署的硬件、模型、输入长度、并发和实测延迟；冻结正文不能确定该部署精确P95。

须审查冻结语料，不能依据检索失败判定。

## official-025-1 · holdout · single_hop

CUDA 13.0.1：分配与释放锁页主机内存应使用哪两个API？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：cudaHostAlloc和cudaFreeHost用于分配释放锁页主机内存。

禁止误读：cudaHostAlloc分配的是普通设备global memory。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#page-locked-host-memory

规范化行 5-5；SHA256 baaa4d97e78598934924f7be4ffc492e5812db2420dfec7a9ba993b6a7676a61

```text
cudaHostAlloc() and cudaFreeHost() allocate and free page-locked host memory;
```

## official-025-2 · holdout · code_api

CUDA 13.0.1：代码中锁页主机缓冲区应怎样分配和释放？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：cudaHostAlloc和cudaFreeHost用于分配释放锁页主机内存。

禁止误读：cudaHostAlloc分配的是普通设备global memory。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#page-locked-host-memory

规范化行 5-5；SHA256 baaa4d97e78598934924f7be4ffc492e5812db2420dfec7a9ba993b6a7676a61

```text
cudaHostAlloc() and cudaFreeHost() allocate and free page-locked host memory;
```

## official-025-3 · holdout · debugging

CUDA 13.0.1：排查该主题时，有人声称“cudaHostAlloc分配的是普通设备global memory。”，根据文档这个说法哪里需要纠正？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：cudaHostAlloc和cudaFreeHost用于分配释放锁页主机内存。

禁止误读：cudaHostAlloc分配的是普通设备global memory。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#page-locked-host-memory

规范化行 5-5；SHA256 baaa4d97e78598934924f7be4ffc492e5812db2420dfec7a9ba993b6a7676a61

```text
cudaHostAlloc() and cudaFreeHost() allocate and free page-locked host memory;
```

## official-025-4 · holdout · debugging

CUDA 13.0.1：对page-locked-host-memory相关代码进行review时，为何不能接受“cudaHostAlloc分配的是普通设备global memory。”作为正确性依据？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：cudaHostAlloc和cudaFreeHost用于分配释放锁页主机内存。

禁止误读：cudaHostAlloc分配的是普通设备global memory。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#page-locked-host-memory

规范化行 5-5；SHA256 baaa4d97e78598934924f7be4ffc492e5812db2420dfec7a9ba993b6a7676a61

```text
cudaHostAlloc() and cudaFreeHost() allocate and free page-locked host memory;
```

## official-027-1 · holdout · single_hop

CUDA 13.0.1：不同stream之间是否存在固定顺序或并发保证？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：不同stream可能乱序或并发，不能依赖这种行为保证正确性。

禁止误读：不同stream总保证并发，且有固定相对执行顺序。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#streams

规范化行 3-3；SHA256 6fafa2f5f75fb089f1117c64b5688e08a72992b573f1a502bc1797918d2b516e

```text
Different streams, on the other hand, may execute their commands out of order with respect to one another or concurrently; this behavior is not guaranteed and should therefore not be relied upon for correctness
```

## official-027-2 · holdout · code_api

CUDA 13.0.1：多stream结果不稳定时，为什么不能假定天然的相对执行顺序？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：不同stream可能乱序或并发，不能依赖这种行为保证正确性。

禁止误读：不同stream总保证并发，且有固定相对执行顺序。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#streams

规范化行 3-3；SHA256 6fafa2f5f75fb089f1117c64b5688e08a72992b573f1a502bc1797918d2b516e

```text
Different streams, on the other hand, may execute their commands out of order with respect to one another or concurrently; this behavior is not guaranteed and should therefore not be relied upon for correctness
```

## official-027-3 · holdout · debugging

CUDA 13.0.1：排查该主题时，有人声称“不同stream总保证并发，且有固定相对执行顺序。”，根据文档这个说法哪里需要纠正？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：不同stream可能乱序或并发，不能依赖这种行为保证正确性。

禁止误读：不同stream总保证并发，且有固定相对执行顺序。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#streams

规范化行 3-3；SHA256 6fafa2f5f75fb089f1117c64b5688e08a72992b573f1a502bc1797918d2b516e

```text
Different streams, on the other hand, may execute their commands out of order with respect to one another or concurrently; this behavior is not guaranteed and should therefore not be relied upon for correctness
```

## official-027-4 · holdout · debugging

CUDA 13.0.1：对streams相关代码进行review时，为何不能接受“不同stream总保证并发，且有固定相对执行顺序。”作为正确性依据？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：不同stream可能乱序或并发，不能依赖这种行为保证正确性。

禁止误读：不同stream总保证并发，且有固定相对执行顺序。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#streams

规范化行 3-3；SHA256 6fafa2f5f75fb089f1117c64b5688e08a72992b573f1a502bc1797918d2b516e

```text
Different streams, on the other hand, may execute their commands out of order with respect to one another or concurrently; this behavior is not guaranteed and should therefore not be relied upon for correctness
```

## official-029-1 · holdout · single_hop

CUDA 13.0.1：统一内存的同一指针对CPU/GPU访问有什么意义？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：统一内存以同一指针为不同处理器提供访问方式。

禁止误读：同一指针可访问意味着所有环境都无数据迁移或同步需求。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#unified-memory-programming

规范化行 21-24；SHA256 360b2b02922954808049d9df6ff54db82db327e5aacfe9a44f80f5a4f2556946

```text
a single pointer value enables all processors in the system
(all CPUs, all GPUs, etc.)
to access this memory with all of their native memory operations
(pointer dereferences, atomics, etc.).
```

## official-029-2 · holdout · code_api

CUDA 13.0.1：CPU/GPU代码使用同一个统一内存指针，接口意义是什么，能否据此断言零迁移成本？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：统一内存以同一指针为不同处理器提供访问方式。

禁止误读：同一指针可访问意味着所有环境都无数据迁移或同步需求。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#unified-memory-programming

规范化行 21-24；SHA256 360b2b02922954808049d9df6ff54db82db327e5aacfe9a44f80f5a4f2556946

```text
a single pointer value enables all processors in the system
(all CPUs, all GPUs, etc.)
to access this memory with all of their native memory operations
(pointer dereferences, atomics, etc.).
```

## official-029-3 · holdout · debugging

CUDA 13.0.1：排查该主题时，有人声称“同一指针可访问意味着所有环境都无数据迁移或同步需求。”，根据文档这个说法哪里需要纠正？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：统一内存以同一指针为不同处理器提供访问方式。

禁止误读：同一指针可访问意味着所有环境都无数据迁移或同步需求。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#unified-memory-programming

规范化行 21-24；SHA256 360b2b02922954808049d9df6ff54db82db327e5aacfe9a44f80f5a4f2556946

```text
a single pointer value enables all processors in the system
(all CPUs, all GPUs, etc.)
to access this memory with all of their native memory operations
(pointer dereferences, atomics, etc.).
```

## official-029-4 · holdout · debugging

CUDA 13.0.1：对unified-memory-programming相关代码进行review时，为何不能接受“同一指针可访问意味着所有环境都无数据迁移或同步需求。”作为正确性依据？

条件：{'project': 'cuda', 'release': '13.0.1', 'hardware': 'not specified; do not infer'}

参考要点：统一内存以同一指针为不同处理器提供访问方式。

禁止误读：同一指针可访问意味着所有环境都无数据迁移或同步需求。

证据组（组内全部需要）：primary

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#unified-memory-programming

规范化行 21-24；SHA256 360b2b02922954808049d9df6ff54db82db327e5aacfe9a44f80f5a4f2556946

```text
a single pointer value enables all processors in the system
(all CPUs, all GPUs, etc.)
to access this memory with all of their native memory operations
(pointer dereferences, atomics, etc.).
```

