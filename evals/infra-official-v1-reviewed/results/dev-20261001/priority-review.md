# 优先人工核验案例

以下分类是机械诊断，不是事实错误或误拒答金标。完整298条正常输出及2条失败行均在answer-review.md中；服务失败不能审批为答案。

## official-002-1:oracle:oracle · 输出校验失败

vLLM v0.10.2：缓存块身份除了文本还需要哪些额外哈希？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

最终回答：当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

最后一次原始生成：
```json
{
  "supported": true,
  "answer": "缓存块身份除了文本外，还需要 LoRA IDs、多模态输入哈希和缓存盐（用于多租户环境隔离）[E1ea8fd1c16076559047494888]",
  "citations": ["E1ea8fd1c16076559047494888"]
}
```

实际交付证据（摘录；全文见rows.jsonl）：

E1ea8fd1c1607655904749488 · https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/design/prefix_caching.md

```text
Extra hashes: Other values required to make this block unique, such as LoRA IDs, multi-modality input hashes (see the example below), and cache salts to isolate caches in multi-tenant environments.
```

## official-002-2:oracle:oracle · 交付完整标注证据但模型声明不足

vLLM v0.10.2：两个适配器使用相同文本，是否可以只按文本共享缓存？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

最终回答：当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

最后一次原始生成：
```json
{
  "supported": false,
  "answer": "证据中未明确说明两个适配器使用相同文本时是否可以只按文本共享缓存。该证据仅涉及前缀缓存设计的额外哈希值要求，未提供关于适配器共享缓存的具体规则。",
  "citations": []
}
```

实际交付证据（摘录；全文见rows.jsonl）：

E1ea8fd1c1607655904749488 · https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/design/prefix_caching.md

```text
Extra hashes: Other values required to make this block unique, such as LoRA IDs, multi-modality input hashes (see the example below), and cache salts to isolate caches in multi-tenant environments.
```

## official-004-2:oracle:oracle · 交付完整标注证据但模型声明不足

vLLM v0.10.2：能否把Ampere的W8A16支持解释为W8A8？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

最终回答：当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

最后一次原始生成：
```json
{
  "supported": false,
  "answer": "证据表明Ampere GPU支持W8A1:6（weight-only FP8），但未提及W8A8（weight-only FP8）的兼容性。因此，不能将Ampere的W8A16支持解释为W8A8。",
  "citations": ["Ef799598e9c44e1e80614ed21"]
}
```

实际交付证据（摘录；全文见rows.jsonl）：

Ef799598e9c44e1e80614ed21 · https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/quantization/fp8.md

```text
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

## official-004-2:bm25:retrieved · 交付完整标注证据但模型声明不足

vLLM v0.10.2：能否把Ampere的W8A16支持解释为W8A8？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

最终回答：当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

最后一次原始生成：
```json
{"supported": false, "answer": "证据中明确指出Ampere GPU仅支持W8A16（权重仅FP8），而W8A8需要Hopper或Ada Lovelace GPU。因此，不能将Ampere的W8A16支持解释为W8A8。", "citations": ["E707fd541c52eb73c2ed6c6d8"] }
```

实际交付证据（摘录；全文见rows.jsonl）：

E707fd541c52eb73c2ed6c6d8 · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

E304d729ae809670c7310aad7 · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L15-L17

```text
!!! note
    FP8 computation is supported on NVIDIA GPUs with compute capability > 8.9 (Ada Lovelace, Hopper).
    FP8 models will run on compute capability > 8.0 (Ampere) as weight-only W8A16, utilizing FP8 Marlin.
```

## official-012-2:bm25:retrieved · 交付完整标注证据但模型声明不足

SGLang v0.5.2：能否仅凭queue-req为零就判定GPU太慢？

必要要点：频繁队列为空提示客户端提交速度可能太慢。

最终回答：当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

最后一次原始生成：
```json
{
  "supported": false,
  "answer": "证据中没有直接说明仅凭queue-req为零就能判定GPU太慢的情况。证据提到当#queue-req为0时，表示客户端提交请求过慢，但未说明此时GPU是否太慢。需要更多证据来确认GPU性能问题。",
  "citations": []
}
```

实际交付证据（摘录；全文见rows.jsonl）：

E63c1f7fb51b02d051c9fafca · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
```Decode batch. #running-req: 233, #token: 370959, token usage: 0.82, cuda graph: True, gen throughput (token/s): 4594.01, #queue-req: 317```

### Adjust the request submission speed to control `#queue-req`

`#queue-req` indicates the number of requests in the queue.
If you frequently see `#queue-req: 0`, it suggests that your client code is submitting requests too slowly.
A healthy range for `#queue-req` is `100 - 2000`.
However, avoid making `
```

Ed0e655fecbc0130e94eda744 · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
#queue-req` too large, as this will increase the scheduling overhead on the server.

### Achieve a high `token usage`

`token usage` indicates the KV cache memory utilization of the server. `token usage > 0.9` means good utilization.

If you frequently see `token usage < 0.9` and `#queue-req > 0`, it means the server is too conservative about taking in new requests. You can decrease `--schedule-conservativeness` to a value like 0.3.
The case of a
```

## official-017-3:bm25:retrieved · 输出校验失败

SGLang v0.5.2：请求JSON中想启用贪心采样，temperature应设置成多少？

必要要点：温度零对应贪心采样，较高温度增加多样性。

最终回答：当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

最后一次原始生成：
```json
{
  "current_query": "SGLang v0.5.2：请求JSON中想启用贪心采样，temperature应设置成多少？",
  "evidence": [
    {
      "id": "E2155f15de5afe18bf9c36f0f",
      "content": "### Install from Source\n\n```bash\n# Use the last release branch\ngit clone -b v0.5.2 https://github.com/sgl-project/sglang.git\ncd sglang\n\n# Compile sgl-kernel\npip install --upgrade pip\ncd sgl-kernel\ncd sgl-kernel\npython setup_rocm.py install\n\n# Install sglang python package\ncd ..\npip install -e \"python[all_hip]\"\n```\n"
    },
    {
      "id": "E38bb0550ceb8b3da28d9bab3",
      "content": "in the JSON format.\n\",\n        \"sampling_params\": {\n            \"temperature\": 0,\n            \"max_new_token"
    },
    {
      "id": "Ec42bb7b2ccabdad49a03155f",
      "content": "## Method 2: From source\n\n```bash\n# Use the last release branch\ngit clone -b v0.5.2 https://github.com/sgl-project/sglang.git\ncd sglang\n\n# Install the python packages\npip install --upgrade pip\npip install -e \"python[all]\"\n```\n**Quick fixes to common problems**\n- If you want to develop SGLang, it is recommended to use docker.\nPlease refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container)."
    },
    {
      "id": "E0b525850024c3f46a96ae5e8",
      "content": "```python\nimport requests\n\nresponse = requests.post(\n    \"http://localhost:30000/generate\",\n    json={\n        \"text\": \"The capital of France is\",\n        \"sampling_params\": {\n            \"temper"
    },
    {
      "id": "E0e326ce3d6eced7732b39168",
      "content": "s\": 64,\n            \"regex\": \"(France|England)\",\n        },\n    },\n)\nprint(response.json())\n\n# EBNF (XGrammar backend only)\nresponse = requests.post(\n    \"http://localhost:30000/generate\",\n    json={\n        \"text\": \"Write a greeting.\",\n        \"sampling_params\": {\n            \"temperature\": 0,\n            \"max_new_tokens\": 64
```

实际交付证据（摘录；全文见rows.jsonl）：

E2155f15de5afe18bf9c36f0f · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

```text
### Install from Source

```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Compile sgl-kernel
pip install --upgrade pip
cd sgl-kernel
python setup_rocm.py install

# Install sglang python package
cd ..
pip install -e "python[all_hip]"
```
```

E38bb0550ceb8b3da28d9bab3 · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L198-L252

```text
in the JSON format.\n",
        "sampling_params": {
            "temperature": 0,
            "max_new_tokens": 64,
            "json_schema": json_schema,
        },
    },
)
print(response.json())

# Regular expression (Outlines backend only)
response = requests.post(
    "http://localhost:30000/generate",
    json={
        "text": "Paris is the capital of",
        "sampling_params": {
            "temperature": 0,
            "max_new_token
```

## official-004-2:dense:retrieved · 交付完整标注证据但模型声明不足

vLLM v0.10.2：能否把Ampere的W8A16支持解释为W8A8？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

最终回答：当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

最后一次原始生成：
```json
{
  "supported": false,
  "answer": "根据证据，Ampere GPU 仅支持 W8A16（权重仅 FP8），而 W8A8 需要 Hopper 或 Ada Lovelace GPU，因此不能将 Ampere 的 W8A16 支持解释为 W8A8。",
  "citations": ["E707fd541c52eb73c2ed6c6d8"]
}
```

实际交付证据（摘录；全文见rows.jsonl）：

E707fd541c52eb73c2ed6c6d8 · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

E0e84432891126a30a6e4410c · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L26-L29

```text
```python
from vllm import LLM
llm = LLM("Qwen/Qwen3-0.6B", enable_sleep_mode=True)
```
```

## official-004-3:dense:retrieved · 交付完整标注证据但模型声明不足

vLLM v0.10.2：在Ampere部署FP8模型时把激活也按8bit支持处理，应先核对哪个限制？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

最终回答：当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

最后一次原始生成：
```json
{"supported": false, "answer": "证据中未明确指出在Ampere部署FP8模型时应先核对哪个限制，但根据证据[E707fd541c52eb73c2ed6c6d8]可知，Ampere GPU仅支持W8A16（权重仅FP8）而非W8A8（权重和激活均FP8）", "citations": ["E707fd541c52eb73c2ed6c6d8"] }
```

实际交付证据（摘录；全文见rows.jsonl）：

E9179e0166553b73ef2a10c4b · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
!!
! note
Cache isolation is not supported in engine V0.
```

E707fd541c52eb73c2ed6c6d8 · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

## official-002-2:hybrid:retrieved · 输出校验失败

vLLM v0.10.2：两个适配器使用相同文本，是否可以只按文本共享缓存？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

最终回答：当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

最后一次原始生成：
```json
{
  "supported": false,
  "answer": "证据中没有直接说明vLLM v0.10.2中两个适配器使用相同文本时是否可以只按文本共享缓存的信息。vLLM的文档中提到了LoRA适配器的加载方式（如[E062010e52f86dd5d0e443c52]），但未涉及多适配器共享缓存的具体机制或v0.10.2版本的特性。",
  "citations": []
}
```

实际交付证据（摘录；全文见rows.jsonl）：

E744227b8a6f815899ea7e35a · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

```text
## Use the custom-built vLLM Docker image
To run vLLM with the custom-built Docker image:
```bash
docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -p 8000:8000 \
    --env "HUGGING_FACE_HUB_TOKEN=<secret>" \
    vllm/vllm-openai <args...>
```
```

Eadfaab7e8dc33ac661f2f94c · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L165-L168

```text
You can either install existing plugins or implement your own.
By default, vLLM comes with a [resolver plugin to load LoRA adapters from a local directory.](https://github.com/vllm-project/vllm/tree/main/vllm/plugins/lora_resolvers)
To enable this resolver, set `VLLM_ALLOW_RUNTIME_LORA_UPDATING` to True, set `VLLM_PLUGINS` to include `lora_filesystem_resolver`, and then set `VLLM_LORA_RESOLVER_CACHE_DIR` to a local directory.
```

## official-004-2:hybrid:retrieved · 交付完整标注证据但模型声明不足

vLLM v0.10.2：能否把Ampere的W8A16支持解释为W8A8？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

最终回答：当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

最后一次原始生成：
```json
{
  "supported": false,
  "answer": "vLLM v0.10.2 不支持将 Ampere 的 W8A16 解释为 W8A8。Ampere GPU 仅支持 W8A16（权重仅 FP8），而 W8A8 需要 Hopper 或 Ada Lovelace GPU（计算能力 >8.9）。",
  "citations": ["E707fd541c52eb73c2ed6c6d8", "E304d729ae809670c7310aad7"]
}
```

实际交付证据（摘录；全文见rows.jsonl）：

E707fd541c52eb73c2ed6c6d8 · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

E8c0a6d8da59e340ff546c81b · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L10-L10

```text
The FP8 types typically supported in hardware have two distinct representations, each useful in different scenarios:
```

## official-012-2:hybrid:retrieved · 交付完整标注证据但模型声明不足

SGLang v0.5.2：能否仅凭queue-req为零就判定GPU太慢？

必要要点：频繁队列为空提示客户端提交速度可能太慢。

最终回答：当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

最后一次原始生成：
```json
{
  "supported": false,
  "answer": "证据中没有直接说明仅凭queue-req为零就判定GPU太慢的信息。根据证据[E63c1f7fb51b02d051c9fafca]，当#queue-req为0时，可能表示客户端提交请求过慢，而非GPU性能问题。但证据未明确指出queue-req为零是否能直接判定GPU太慢。",
  "citations": ["E63c1f7fb51b02d051c9fafca"]
}
```

实际交付证据（摘录；全文见rows.jsonl）：

E836c7d1b89a88031ebc19bb7 · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
You can install the frontend locally without needing a GPU, while the backend can be set up on a GPU-enabled machine.
To install the frontend, run `pip install sglang`, and for the backend, use `pip install sglang[srt]`.
`srt` is the abbreviation of SGLang runtime.
```

Eac21656670164d7db38d4f80 · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L1-L3

```text
# AMD GPUs

This document describes how run SGLang on AMD GPUs. If you encounter issues or have questions, please [open an issue](https://github.com/sgl-project/sglang/issues).
```

## official-014-2:hybrid_rerank:retrieved · 输出校验失败

SGLang v0.5.2：模型已经离线量化，是否总应再传quantization启用在线量化？

必要要点：预量化模型不应同时通过quantization参数启用在线量化。

最终回答：当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

最后一次原始生成：
```json
{
  "supported": true,
  "answer": "SGLang v0.5.2 已经离线量化，不需要再传quantization启用在线量化。因为如果使用预量化模型，不应同时添加`--quantization`参数以启用在线量化 [E7a70794e3abe0baba0df156e]。离线量化模型已预先计算好量化参数，无需运行时动态计算 [E9e27ac051ce62af8450419a8]。",
  "citations": ["E7a70794e3abe0baba0df156e"]
}
```

实际交付证据（摘录；全文见rows.jsonl）：

E72b0308bd3dc8dd15e8e2d6c · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
**Note: For better performance, usability and convenience, offline quantization is recommended over online quantization.**
```

E9e27ac051ce62af8450419a8 · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
# Quantization
SGLang supports various quantization methods, including offline quantization and online dynamic quantization.
Offline quantization loads pre-quantized model weights directly during inference.
This is required for quantization methods
such as GPTQ and AWQ, which collect and pre-compute various statistics from the original weights using the calibration dataset.
```

## official-022-2:hybrid_rerank:retrieved · 交付完整标注证据但模型声明不足

CUDA 13.0.1：能否把一个普通线程块的shared memory当全grid共享空间？

必要要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

最终回答：当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

最后一次原始生成：
```json
{
  "supported": false,
  "answer": "证据中没有明确说明CUDA 13.0.1中普通线程块的shared memory能否作为全grid共享空间。根据提供的证据，shared memory是每个线程块内部可见的，且线程块之间不能直接共享（证据[Edb4fe65bec83c651e06dfe24]提到'Each thread block has shared memory visible to all threads of the block'，但未提及跨线程块共享）。",
  "citations": ["Edb4fe65bec83c651e06dfe24"]
}
```

实际交付证据（摘录；全文见rows.jsonl）：

E26f4250aa57456c8a93978de · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

Edb4fe65bec83c651e06dfe24 · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
5.3.
Memory Hierarchy
CUDA threads may access data from multiple memory spaces during their execution as illustrated by Figure 6.
Each thread has private local memory.
Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
Thread blocks in a thread block cluster can perform read, write, and atomics operations on each other’s shared memory.
All threads have access to the same global memory.
```

## official-024-2:hybrid_rerank:retrieved · 交付完整标注证据但模型声明不足

CUDA 13.0.1：shared memory优化是否意味着矩阵乘法运算不再执行？

必要要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

最终回答：当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。

最后一次原始生成：
```json
{
  "supported": false,
  "answer": "证据中未明确说明CUDA 13.0.1的shared memory优化是否会导致矩阵乘法运算不再执行。证据中提到共享内存用于优化矩阵乘法（如图8和图9所示），但未涉及CUDA 13.0.1版本的具体优化效果或矩阵乘法是否被取消执行。",
  "citations": []
}
```

实际交付证据（摘录；全文见rows.jsonl）：

Ef17178a96c4ba4390bd108ce · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L76-L76

```text
Figure 8 Matrix Multiplication without Shared Memory
```

E26f4250aa57456c8a93978de · /Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```
