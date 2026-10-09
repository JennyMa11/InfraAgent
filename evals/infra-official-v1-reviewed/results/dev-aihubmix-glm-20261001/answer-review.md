# 答案独立人工复核

填写 answer-review.json；事实字段留空表示尚未评分。
引用 ID 合法不代表陈述受到证据支持。

## official-002-1:oracle:oracle

vLLM v0.10.2：缓存块身份除了文本还需要哪些额外哈希？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "1cfaee3e-36cd-4f97-91cd-40c3a9f1a2ad",
  "answer": "除文本外，缓存块身份还需要额外哈希（Extra hashes）来保证块唯一性，包括：LoRA ID、多模态输入的哈希（multi-modality input hashes），以及用于在多租户环境中隔离缓存的 cache salts [E1ea8fd1c1607655904749488]。",
  "citations": [
    {
      "citation_id": "E1ea8fd1c1607655904749488",
      "content": "Extra hashes: Other values required to make this block unique, such as LoRA IDs, multi-modality input hashes (see the example below), and cache salts to isolate caches in multi-tenant environments.",
      "source": "/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md",
      "locator": "https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/design/prefix_caching.md",
      "document_id": "vllm-prefix_caching"
    }
  ],
  "status": "answered",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：缓存块身份除了文本还需要哪些额外哈希？",
      "hits": 0,
      "evidence": 1
    },
    {
      "step": "generate",
      "duration_ms": 6299.1,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": true
    }
  ]
}
```

实际输入证据：

### E1ea8fd1c1607655904749488

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/design/prefix_caching.md

```text
Extra hashes: Other values required to make this block unique, such as LoRA IDs, multi-modality input hashes (see the example below), and cache salts to isolate caches in multi-tenant environments.
```

## official-002-1:bm25:retrieved

vLLM v0.10.2：缓存块身份除了文本还需要哪些额外哈希？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "e6d5e0db-544f-4a24-8763-1b3bf4c51d2f",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：缓存块身份除了文本还需要哪些额外哈希？",
      "hits": 0,
      "evidence": 9
    },
    {
      "step": "generate",
      "duration_ms": 12067.5,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": true
    }
  ]
}
```

实际输入证据：

### E01cd7f8528e50b0d7013c1be

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L14-L20

```text
## Speculating with a draft model

The following code configures vLLM in an offline mode to use speculative decoding with a draft model, speculating 5 tokens at a time.

!!! warning
    In vllm v0.10.0, speculative decoding with a draft model is not supported.
    If you use the following code, you will get a `NotImplementedError`.
```

### E53a04ce20e63602ad4637565

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L33-L33

```text
3. Evaluating accuracy in vLLM
```

### Ecf2dd228b34ec7b53985eff4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L288-L293

```text
## Resources for vLLM contributors
- [A Hacker's Guide to Speculative Decoding in vLLM](https://www.youtube.com/watch?
```

### E9a5dde88f838a11ba9dccd64

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
## Use vLLM's Official Docker Image
vLLM offers an official Docker image for deployment.
The image can be used to run OpenAI compatible server and is available on Docker Hub as [vllm/vllm-openai](https://hub.docker.com/r/vllm/vllm-openai/tags).
```

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### E16b83f578a404c7f80c61a32

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L288-L293

```text
v=9wNAgpX6z_4)
- [What is Lookahead Scheduling in vLLM?
](https://docs.google.com/document/d/1Z9TvqzzBPnh5WHcRwjvK2UEeFeq5zMZb5mFE8jR0HCs/edit#heading=h.1fjfb0donq5a)
- [Information on batch expansion](https://docs.google.com/document/d/1T-JaS2T1NRfdP51qzqpyakoCXxSXTtORppiwaj5asxA/edit#heading=h.kk7dq05lc6q8)
- [Dynamic speculative decoding](gh-issue:4565)
```

### E129c5629e0e269f5141eaa20

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model Qwen/Qwen3-0.6B
```
This image can also be used with other container engines such as [Podman](https://podman.io/).
```

### E76dca9b42c02be4cdcff9c3e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
podman run --device nvidia.com/gpu=all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
  -p 8000:8000 \
  --ipc=host \
  docker.io/vllm/vllm-openai:latest \
  --model Qwen/Qwen3-0.6B
```
You can add any other [engine-args](../configuration/engine_args.md) you need after the image tag (`vllm/vllm-openai:latest`).
```

### Ec94bd3c0efd3b0755001340f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
!!
! note
You can either use the `ipc=host` flag or `--shm-size` flag to allow the
container to access the host's shared memory.
vLLM uses PyTorch, which uses shared
memory to share data between processes under the hood, particularly for tensor parallel inference.
```

## official-002-1:dense:retrieved

vLLM v0.10.2：缓存块身份除了文本还需要哪些额外哈希？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "c02b0c6f-f103-4ad0-99b3-8d2fde1e5882",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：缓存块身份除了文本还需要哪些额外哈希？",
      "hits": 0,
      "evidence": 9
    },
    {
      "step": "generate",
      "duration_ms": 1754.7,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Eb1696b36d266157a207a2b9d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L159-L184

```text
```yaml
...
spec:
  containers:
    - name: vllm
      image: vllm/vllm-openai
      securityContext:
        capabilities:
          add: ["IPC_LOCK"]
      volumeMounts:
        - mountPath: /dev/shm
          name: dshm
      resources:
        limits:
          nvidia.com/gpu: 8
        requests:
          nvidia.com/gpu: 8
  volumes:
    - name: dshm
      emptyDir:
        medium: Memory
...
```
```

### Eb66faf21718bf2708ca32373

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L43-L67

```text
quant_config) # load model

model.quantize(calibration_dataset, batch_size=2) # quantize
model.save(quant_path) # save model
```
```

### E36b43e89ddc1aefb338ba4e4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
full. Retract requests.` occasionally but not frequently, it is okay.

### Tune `--mem-fraction-static` to increase KV cache pool capacity
SGLang allocates memory as follows:

Total memory usage = model weights + KV cache pool + CUDA graph buffers + activations

The `--mem-fraction-static` parameter determines how much memory is allocated to the first two components:

mem_fraction_static = (model weights + KV cache pool) / GPU memory capacity

To
```

### E0ecab1b338db115dc6966ad9

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-conserving_memory.md#L1-L3

```text
# Conserving Memory

Large models might cause your machine to run out of memory (OOM). Here are some options that help alleviate this problem.
```

### E11e8b54ee3c815c0740ca87e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-pr-21611.md#L30-L194

```text
storage path length after llm generate: 2**
Adding requests: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  6.16it/s]
Processed prompts:   0%|                                                                                                                    | 0/1 [00:00<?, ?it/s, est. speed input: 0.00 toks/
```

### E5b09769c743f5aeb7b751318

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L159-L184

```text
!!
! tip "Confirm GPUDirect RDMA operation"
To confirm your InfiniBand card is using GPUDirect RDMA, run vLLM with detailed NCCL logs: `NCCL_DEBUG=TRACE vllm serve ...`.
```

### Ed113d222c40bd67cd5603407

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L43-L67

```text
```py
from datasets import load_dataset
from gptqmodel import GPTQModel, QuantizeConfig

model_id = "meta-llama/Llama-3.2-1B-Instruct"
quant_path = "Llama-3.2-1B-Instruct-gptqmodel-4bit"

calibration_dataset = load_dataset(
    "allenai/c4", data_files="en/c4-train.00001-of-01024.json.gz",
    split="train"
  ).select(range(1024))["text"]

quant_config = QuantizeConfig(bits=4, group_size=128) # quantization config
model = GPTQModel.load(model_id,
```

### E09bb5036d01e98073ac1f344

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L43-L67

```text
#### Using [GPTQModel](https://github.com/ModelCloud/GPTQModel)
```bash
# install
pip install gptqmodel --no-build-isolation -v
```
```

### E44817ba471505d1b42c1b7c6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
server being too conservative can happen when users send many requests with a large `max_new_tokens` but the requests stop very early due to EOS or stop strings.

On the other hand, if you see `token usage` very high and you frequently see warnings like
`KV cache pool is full.
```

## official-002-1:hybrid:retrieved

vLLM v0.10.2：缓存块身份除了文本还需要哪些额外哈希？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "264c15ed-95c0-4ced-a259-be909d6fdf5a",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：缓存块身份除了文本还需要哪些额外哈希？",
      "hits": 0,
      "evidence": 9
    },
    {
      "step": "generate",
      "duration_ms": 1312.7,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Eadfaab7e8dc33ac661f2f94c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L165-L168

```text
You can either install existing plugins or implement your own.
By default, vLLM comes with a [resolver plugin to load LoRA adapters from a local directory.](https://github.com/vllm-project/vllm/tree/main/vllm/plugins/lora_resolvers)
To enable this resolver, set `VLLM_ALLOW_RUNTIME_LORA_UPDATING` to True, set `VLLM_PLUGINS` to include `lora_filesystem_resolver`, and then set `VLLM_LORA_RESOLVER_CACHE_DIR` to a local directory.
```

### E0049cea289627054ed67f5d7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

```text
The argument `vllm/vllm-openai` specifies the image to run, and should be replaced with the name of the custom-built image (the `-t` tag from the build command).
```

### E01cd7f8528e50b0d7013c1be

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L14-L20

```text
## Speculating with a draft model

The following code configures vLLM in an offline mode to use speculative decoding with a draft model, speculating 5 tokens at a time.

!!! warning
    In vllm v0.10.0, speculative decoding with a draft model is not supported.
    If you use the following code, you will get a `NotImplementedError`.
```

### Eb1696b36d266157a207a2b9d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L159-L184

```text
```yaml
...
spec:
  containers:
    - name: vllm
      image: vllm/vllm-openai
      securityContext:
        capabilities:
          add: ["IPC_LOCK"]
      volumeMounts:
        - mountPath: /dev/shm
          name: dshm
      resources:
        limits:
          nvidia.com/gpu: 8
        requests:
          nvidia.com/gpu: 8
  volumes:
    - name: dshm
      emptyDir:
        medium: Memory
...
```
```

### E53a04ce20e63602ad4637565

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L33-L33

```text
3. Evaluating accuracy in vLLM
```

### E062010e52f86dd5d0e443c52

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L165-L168

```text
When vLLM receives a request using a LoRA adapter `foobar`,
it will first look in the local directory for a directory `foobar`, and attempt to load the contents of that directory as a LoRA adapter.
If successful, the request will complete as normal and
that adapter will then be available for normal use on the server.
```

### E744227b8a6f815899ea7e35a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

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

### Ed297b4db013cea35b4dec16a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

```text
!!
! note
**For version 0.4.1 and 0.4.2 only** - the vLLM docker images under these versions are supposed to be run under the root user since a library under the root user's home directory, i.e.
`/root/.config/vllm/nccl/cu12/libnccl.so.2.18.1` is required to be loaded during runtime.
```

### E5b09769c743f5aeb7b751318

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L159-L184

```text
!!
! tip "Confirm GPUDirect RDMA operation"
To confirm your InfiniBand card is using GPUDirect RDMA, run vLLM with detailed NCCL logs: `NCCL_DEBUG=TRACE vllm serve ...`.
```

## official-002-1:hybrid_rerank:retrieved

vLLM v0.10.2：缓存块身份除了文本还需要哪些额外哈希？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "ee66d2a7-6c3f-4a2e-a06f-51b329fb4359",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：缓存块身份除了文本还需要哪些额外哈希？",
      "hits": 0,
      "evidence": 10
    },
    {
      "step": "generate",
      "duration_ms": 2022.6,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E854176531e0cf52e426febb2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L21-L24

```text
- Increase `gpu_memory_utilization`.
vLLM pre-allocates GPU cache using this percentage of memory.
By increasing utilization, you can provide more KV cache space.
- Decrease `max_num_seqs` or `max_num_batched_tokens`.
This reduces the number of concurrent requests in a batch, thereby requiring less KV cache space.
- Increase `tensor_parallel_size`.
```

### Ed6d39e475341f4ab01dc6509

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L50-L51

```text
### To reproduce:
vllm version: v0.9.2
```

### Eb1696b36d266157a207a2b9d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L159-L184

```text
```yaml
...
spec:
  containers:
    - name: vllm
      image: vllm/vllm-openai
      securityContext:
        capabilities:
          add: ["IPC_LOCK"]
      volumeMounts:
        - mountPath: /dev/shm
          name: dshm
      resources:
        limits:
          nvidia.com/gpu: 8
        requests:
          nvidia.com/gpu: 8
  volumes:
    - name: dshm
      emptyDir:
        medium: Memory
...
```
```

### Ede81f51af23dabfaa0a634ce

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L42-L51

```text
    If you need to use those dependencies (having accepted the license terms),
    create a custom Dockerfile on top of the base image with an extra layer that installs them:

    ```Dockerfile
    FROM vllm/vllm-openai:v0.9.0

    # e.g. install the `audio` optional dependencies
    # NOTE: Make sure the version of vLLM matches the base image!
    RUN uv pip install --system vllm[audio]==0.9.0
    ```
```

### Ec94bd3c0efd3b0755001340f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
!!
! note
You can either use the `ipc=host` flag or `--shm-size` flag to allow the
container to access the host's shared memory.
vLLM uses PyTorch, which uses shared
memory to share data between processes under the hood, particularly for tensor parallel inference.
```

### Ea9ce84adf4242fba791cc864

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L21-L24

```text
This shards model weights across GPUs, allowing each GPU to have more memory available for KV cache.
However, increasing this value may cause excessive synchronization overhead.
- Increase `pipeline_parallel_size`.
```

### Edb1580edf1a94751e80875de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L21-L24

```text
This distributes model layers across GPUs, reducing the memory needed for model weights on each GPU, indirectly leaving more memory available for KV cache.
However, increasing this value may cause latency penalties.
```

### E5b09769c743f5aeb7b751318

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L159-L184

```text
!!
! tip "Confirm GPUDirect RDMA operation"
To confirm your InfiniBand card is using GPUDirect RDMA, run vLLM with detailed NCCL logs: `NCCL_DEBUG=TRACE vllm serve ...`.
```

### E76dca9b42c02be4cdcff9c3e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
podman run --device nvidia.com/gpu=all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
  -p 8000:8000 \
  --ipc=host \
  docker.io/vllm/vllm-openai:latest \
  --model Qwen/Qwen3-0.6B
```
You can add any other [engine-args](../configuration/engine_args.md) you need after the image tag (`vllm/vllm-openai:latest`).
```

### E9a5dde88f838a11ba9dccd64

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
## Use vLLM's Official Docker Image
vLLM offers an official Docker image for deployment.
```

## official-002-2:oracle:oracle

vLLM v0.10.2：两个适配器使用相同文本，是否可以只按文本共享缓存？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "285bbff7-d00a-4fc7-b77d-3c825dc099e8",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：两个适配器使用相同文本，是否可以只按文本共享缓存？",
      "hits": 0,
      "evidence": 1
    },
    {
      "step": "generate",
      "duration_ms": 1319.2,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E1ea8fd1c1607655904749488

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/design/prefix_caching.md

```text
Extra hashes: Other values required to make this block unique, such as LoRA IDs, multi-modality input hashes (see the example below), and cache salts to isolate caches in multi-tenant environments.
```

## official-002-2:bm25:retrieved

vLLM v0.10.2：两个适配器使用相同文本，是否可以只按文本共享缓存？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "8110bb0a-34f1-4561-9edb-ed9bfce6e372",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：两个适配器使用相同文本，是否可以只按文本共享缓存？",
      "hits": 0,
      "evidence": 9
    },
    {
      "step": "generate",
      "duration_ms": 1325.3,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E01cd7f8528e50b0d7013c1be

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L14-L20

```text
## Speculating with a draft model

The following code configures vLLM in an offline mode to use speculative decoding with a draft model, speculating 5 tokens at a time.

!!! warning
    In vllm v0.10.0, speculative decoding with a draft model is not supported.
    If you use the following code, you will get a `NotImplementedError`.
```

### E53a04ce20e63602ad4637565

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L33-L33

```text
3. Evaluating accuracy in vLLM
```

### Ecf2dd228b34ec7b53985eff4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L288-L293

```text
## Resources for vLLM contributors
- [A Hacker's Guide to Speculative Decoding in vLLM](https://www.youtube.com/watch?
```

### E9a5dde88f838a11ba9dccd64

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
## Use vLLM's Official Docker Image
vLLM offers an official Docker image for deployment.
The image can be used to run OpenAI compatible server and is available on Docker Hub as [vllm/vllm-openai](https://hub.docker.com/r/vllm/vllm-openai/tags).
```

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### E16b83f578a404c7f80c61a32

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L288-L293

```text
v=9wNAgpX6z_4)
- [What is Lookahead Scheduling in vLLM?
](https://docs.google.com/document/d/1Z9TvqzzBPnh5WHcRwjvK2UEeFeq5zMZb5mFE8jR0HCs/edit#heading=h.1fjfb0donq5a)
- [Information on batch expansion](https://docs.google.com/document/d/1T-JaS2T1NRfdP51qzqpyakoCXxSXTtORppiwaj5asxA/edit#heading=h.kk7dq05lc6q8)
- [Dynamic speculative decoding](gh-issue:4565)
```

### E129c5629e0e269f5141eaa20

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model Qwen/Qwen3-0.6B
```
This image can also be used with other container engines such as [Podman](https://podman.io/).
```

### E76dca9b42c02be4cdcff9c3e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
podman run --device nvidia.com/gpu=all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
  -p 8000:8000 \
  --ipc=host \
  docker.io/vllm/vllm-openai:latest \
  --model Qwen/Qwen3-0.6B
```
You can add any other [engine-args](../configuration/engine_args.md) you need after the image tag (`vllm/vllm-openai:latest`).
```

### Ec94bd3c0efd3b0755001340f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
!!
! note
You can either use the `ipc=host` flag or `--shm-size` flag to allow the
container to access the host's shared memory.
vLLM uses PyTorch, which uses shared
memory to share data between processes under the hood, particularly for tensor parallel inference.
```

## official-002-2:dense:retrieved

vLLM v0.10.2：两个适配器使用相同文本，是否可以只按文本共享缓存？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "fc70bda6-e2d1-4965-89d7-dcf5ddf1c0c5",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：两个适配器使用相同文本，是否可以只按文本共享缓存？",
      "hits": 0,
      "evidence": 7
    },
    {
      "step": "generate",
      "duration_ms": 1596.2,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ec94bd3c0efd3b0755001340f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
!!
! note
You can either use the `ipc=host` flag or `--shm-size` flag to allow the
container to access the host's shared memory.
vLLM uses PyTorch, which uses shared
memory to share data between processes under the hood, particularly for tensor parallel inference.
```

### Ed297b4db013cea35b4dec16a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

```text
!!
! note
**For version 0.4.1 and 0.4.2 only** - the vLLM docker images under these versions are supposed to be run under the root user since a library under the root user's home directory, i.e.
`/root/.config/vllm/nccl/cu12/libnccl.so.2.18.1` is required to be loaded during runtime.
```

### Ede81f51af23dabfaa0a634ce

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L42-L51

```text
    If you need to use those dependencies (having accepted the license terms),
    create a custom Dockerfile on top of the base image with an extra layer that installs them:

    ```Dockerfile
    FROM vllm/vllm-openai:v0.9.0

    # e.g. install the `audio` optional dependencies
    # NOTE: Make sure the version of vLLM matches the base image!
    RUN uv pip install --system vllm[audio]==0.9.0
    ```
```

### Eadfaab7e8dc33ac661f2f94c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L165-L168

```text
You can either install existing plugins or implement your own.
By default, vLLM comes with a [resolver plugin to load LoRA adapters from a local directory.](https://github.com/vllm-project/vllm/tree/main/vllm/plugins/lora_resolvers)
To enable this resolver, set `VLLM_ALLOW_RUNTIME_LORA_UPDATING` to True, set `VLLM_PLUGINS` to include `lora_filesystem_resolver`, and then set `VLLM_LORA_RESOLVER_CACHE_DIR` to a local directory.
```

### E744227b8a6f815899ea7e35a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

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

### E76dca9b42c02be4cdcff9c3e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
podman run --device nvidia.com/gpu=all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
  -p 8000:8000 \
  --ipc=host \
  docker.io/vllm/vllm-openai:latest \
  --model Qwen/Qwen3-0.6B
```
You can add any other [engine-args](../configuration/engine_args.md) you need after the image tag (`vllm/vllm-openai:latest`).
```

### E129c5629e0e269f5141eaa20

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model Qwen/Qwen3-0.6B
```
This image can also be used with other container engines such as [Podman](https://podman.io/).
```

## official-002-2:hybrid:retrieved

vLLM v0.10.2：两个适配器使用相同文本，是否可以只按文本共享缓存？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "e74afced-5037-4942-98b6-014d3e833efd",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：两个适配器使用相同文本，是否可以只按文本共享缓存？",
      "hits": 0,
      "evidence": 9
    },
    {
      "step": "generate",
      "duration_ms": 1732.9,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E744227b8a6f815899ea7e35a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

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

### Eadfaab7e8dc33ac661f2f94c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L165-L168

```text
You can either install existing plugins or implement your own.
By default, vLLM comes with a [resolver plugin to load LoRA adapters from a local directory.](https://github.com/vllm-project/vllm/tree/main/vllm/plugins/lora_resolvers)
To enable this resolver, set `VLLM_ALLOW_RUNTIME_LORA_UPDATING` to True, set `VLLM_PLUGINS` to include `lora_filesystem_resolver`, and then set `VLLM_LORA_RESOLVER_CACHE_DIR` to a local directory.
```

### Ede81f51af23dabfaa0a634ce

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L42-L51

```text
    If you need to use those dependencies (having accepted the license terms),
    create a custom Dockerfile on top of the base image with an extra layer that installs them:

    ```Dockerfile
    FROM vllm/vllm-openai:v0.9.0

    # e.g. install the `audio` optional dependencies
    # NOTE: Make sure the version of vLLM matches the base image!
    RUN uv pip install --system vllm[audio]==0.9.0
    ```
```

### E9a5dde88f838a11ba9dccd64

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
## Use vLLM's Official Docker Image
vLLM offers an official Docker image for deployment.
The image can be used to run OpenAI compatible server and is available on Docker Hub as [vllm/vllm-openai](https://hub.docker.com/r/vllm/vllm-openai/tags).
```

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### E0049cea289627054ed67f5d7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

```text
The argument `vllm/vllm-openai` specifies the image to run, and should be replaced with the name of the custom-built image (the `-t` tag from the build command).
```

### Ed297b4db013cea35b4dec16a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

```text
!!
! note
**For version 0.4.1 and 0.4.2 only** - the vLLM docker images under these versions are supposed to be run under the root user since a library under the root user's home directory, i.e.
`/root/.config/vllm/nccl/cu12/libnccl.so.2.18.1` is required to be loaded during runtime.
```

### Eb2a0f8bf7ceabe619bc48d27

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

```text
If you are running the container under a different user, you may need to first change the permissions of the library (and all the parent directories) to allow the user to access it, then run vLLM with environment variable `VLLM_NCCL_SO_PATH=/root/.config/vllm/nccl/cu12/libnccl.so.2.18.1` .
```

### E062010e52f86dd5d0e443c52

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L165-L168

```text
When vLLM receives a request using a LoRA adapter `foobar`,
it will first look in the local directory for a directory `foobar`, and attempt to load the contents of that directory as a LoRA adapter.
```

## official-002-2:hybrid_rerank:retrieved

vLLM v0.10.2：两个适配器使用相同文本，是否可以只按文本共享缓存？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "8b7025ec-a5df-47de-ba91-a73e56c320ff",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：两个适配器使用相同文本，是否可以只按文本共享缓存？",
      "hits": 0,
      "evidence": 9
    },
    {
      "step": "generate",
      "duration_ms": 2110.1,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ec94bd3c0efd3b0755001340f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
!!
! note
You can either use the `ipc=host` flag or `--shm-size` flag to allow the
container to access the host's shared memory.
vLLM uses PyTorch, which uses shared
memory to share data between processes under the hood, particularly for tensor parallel inference.
```

### Eb2a0f8bf7ceabe619bc48d27

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

```text
If you are running the container under a different user, you may need to first change the permissions of the library (and all the parent directories) to allow the user to access it, then run vLLM with environment variable `VLLM_NCCL_SO_PATH=/root/.config/vllm/nccl/cu12/libnccl.so.2.18.1` .
```

### Ed6d39e475341f4ab01dc6509

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L50-L51

```text
### To reproduce:
vllm version: v0.9.2
```

### Eb16da0423a909f74b851d03a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L147-L155

```text
If you use Docker, set up the container as follows:

```bash
docker run --gpus all \
    --ipc=host \
    --shm-size=16G \
    -v /dev/shm:/dev/shm \
    vllm/vllm-openai
```
```

### Ecfe9bd24625d0f9f4e165871

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-pr-21611.md#L30-L194

```text
===============
***info: Identical pure text input as a case-control***
**Expected storage path length after llm generate: 5**
Adding requests: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 1199.40it/s]
INFO 07-30 02:52:29 [shared_storage_connector.py:257] External Cache Hit!
Processed prompts:   0%|          
```

### E76dca9b42c02be4cdcff9c3e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
podman run --device nvidia.com/gpu=all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
  -p 8000:8000 \
  --ipc=host \
  docker.io/vllm/vllm-openai:latest \
  --model Qwen/Qwen3-0.6B
```
You can add any other [engine-args](../configuration/engine_args.md) you need after the image tag (`vllm/vllm-openai:latest`).
```

### E129c5629e0e269f5141eaa20

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model Qwen/Qwen3-0.6B
```
This image can also be used with other container engines such as [Podman](https://podman.io/).
```

### E9a5dde88f838a11ba9dccd64

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
## Use vLLM's Official Docker Image
vLLM offers an official Docker image for deployment.
The image can be used to run OpenAI compatible server and is available on Docker Hub as [vllm/vllm-openai](https://hub.docker.com/r/vllm/vllm-openai/tags).
```

### Ed297b4db013cea35b4dec16a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

```text
!!
! note
**For version 0.4.1 and 0.4.2 only** - the vLLM docker images under these versions are supposed to be run under the root user since a library under the root user's home directory, i.e.
`/root/.config/vllm/nccl/cu12/libnccl.so.2.18.1` is required to be loaded during runtime.
```

## official-002-3:oracle:oracle

vLLM v0.10.2：多租户前缀相同但需要隔离，应检查缓存键中的什么信息？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "d8f8ed25-d237-497d-b2e1-a4fabae144e9",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：多租户前缀相同但需要隔离，应检查缓存键中的什么信息？",
      "hits": 0,
      "evidence": 1
    },
    {
      "step": "generate",
      "duration_ms": 1866.3,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E1ea8fd1c1607655904749488

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/design/prefix_caching.md

```text
Extra hashes: Other values required to make this block unique, such as LoRA IDs, multi-modality input hashes (see the example below), and cache salts to isolate caches in multi-tenant environments.
```

## official-002-3:bm25:retrieved

vLLM v0.10.2：多租户前缀相同但需要隔离，应检查缓存键中的什么信息？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "0c633f70-0127-4c56-a258-390485c9ecfd",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：多租户前缀相同但需要隔离，应检查缓存键中的什么信息？",
      "hits": 0,
      "evidence": 9
    },
    {
      "step": "generate",
      "duration_ms": 1574.1,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E01cd7f8528e50b0d7013c1be

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L14-L20

```text
## Speculating with a draft model

The following code configures vLLM in an offline mode to use speculative decoding with a draft model, speculating 5 tokens at a time.

!!! warning
    In vllm v0.10.0, speculative decoding with a draft model is not supported.
    If you use the following code, you will get a `NotImplementedError`.
```

### E53a04ce20e63602ad4637565

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L33-L33

```text
3. Evaluating accuracy in vLLM
```

### Ecf2dd228b34ec7b53985eff4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L288-L293

```text
## Resources for vLLM contributors
- [A Hacker's Guide to Speculative Decoding in vLLM](https://www.youtube.com/watch?
```

### E9a5dde88f838a11ba9dccd64

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
## Use vLLM's Official Docker Image
vLLM offers an official Docker image for deployment.
The image can be used to run OpenAI compatible server and is available on Docker Hub as [vllm/vllm-openai](https://hub.docker.com/r/vllm/vllm-openai/tags).
```

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### E16b83f578a404c7f80c61a32

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L288-L293

```text
v=9wNAgpX6z_4)
- [What is Lookahead Scheduling in vLLM?
](https://docs.google.com/document/d/1Z9TvqzzBPnh5WHcRwjvK2UEeFeq5zMZb5mFE8jR0HCs/edit#heading=h.1fjfb0donq5a)
- [Information on batch expansion](https://docs.google.com/document/d/1T-JaS2T1NRfdP51qzqpyakoCXxSXTtORppiwaj5asxA/edit#heading=h.kk7dq05lc6q8)
- [Dynamic speculative decoding](gh-issue:4565)
```

### E129c5629e0e269f5141eaa20

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model Qwen/Qwen3-0.6B
```
This image can also be used with other container engines such as [Podman](https://podman.io/).
```

### E76dca9b42c02be4cdcff9c3e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
podman run --device nvidia.com/gpu=all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
  -p 8000:8000 \
  --ipc=host \
  docker.io/vllm/vllm-openai:latest \
  --model Qwen/Qwen3-0.6B
```
You can add any other [engine-args](../configuration/engine_args.md) you need after the image tag (`vllm/vllm-openai:latest`).
```

### Ec94bd3c0efd3b0755001340f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
!!
! note
You can either use the `ipc=host` flag or `--shm-size` flag to allow the
container to access the host's shared memory.
vLLM uses PyTorch, which uses shared
memory to share data between processes under the hood, particularly for tensor parallel inference.
```

## official-002-3:dense:retrieved

vLLM v0.10.2：多租户前缀相同但需要隔离，应检查缓存键中的什么信息？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "db13c260-5157-4110-b151-2ca9b5ca2c6d",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：多租户前缀相同但需要隔离，应检查缓存键中的什么信息？",
      "hits": 0,
      "evidence": 12
    },
    {
      "step": "generate",
      "duration_ms": 1315.2,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ec6fca19f47e344a23b08f552

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L144-L145

```text
- `IPC_LOCK` security context: add the `IPC_LOCK` capability to the container's security context to lock memory pages and prevent swapping to disk.
- Shared memory with `/dev/shm`: mount `/dev/shm` in the pod spec to provide shared memory for interprocess communication (IPC).
```

### E727fbf7338b5fce226be101c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L26-L26

```text
You can monitor the number of preemption requests through Prometheus metrics exposed by vLLM. Additionally, you can log the cumulative number of preemption requests by setting `disable_log_stats=False`.
```

### E1463499a732287269ea92129

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
To improve privacy in shared environments, vLLM supports isolating prefix cache reuse through optional per-request salting.
By including a `cache_salt` in the request, this value is injected into the hash of the first block, ensuring that only requests with the same salt can reuse cached KV blocks.
This prevents timing-based attacks where an adversary could infer cached content by observing latency differences.
```

### E51f5a53fb4763709cb17044a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L196-L196

```text
**Note**: When using cache-aware routing, removed workers are cleanly evicted from the routing tree and request queues.
```

### E1fbbdb1804f22185246d4a23

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L362-L392

```text
</figure>
<figure markdown="span">
!
[](../assets/design/paged_attention/logits_vec.png){ align="center" alt="logits_vec" width="50%" }
```

### E5dda40ed0c5092aadb08696f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
In the rest of this document, we first introduce the data structure used for prefix caching in vLLM v1, followed by the prefix caching workflow of major KV cache operators (e.g., allocate, append, free, eviction).
Finally, we use an example to illustrate the end to end prefix caching workflow.
**Cache Isolation for Security**
```

### Ea78a5260abf923558a637c53

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
This offers protection without compromising performance.
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Here is a document with details about the world series: ..."},
    {"role": "user", "content": "Who won the world series in 2020?"}
  ],
  "cache_salt": "your-cache-salt"
}
```
```

### E5d8fe7ed6ec122403b10c915

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
With this setup, cache sharing is limited to users or requests that explicitly agree on a common salt, enabling cache reuse within a trust group while isolating others.
```

### E9179e0166553b73ef2a10c4b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
!!
! note
Cache isolation is not supported in engine V0.
```

### Ef3ccfce03c1e69b997b949ce

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L362-L392

```text
## Value
<figure markdown="span">
!
[](../assets/design/paged_attention/value.png){ align="center" alt="value" width="70%" }
```

### E156d702ea1147eece0be7bd8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L362-L392

```text
</figure>
<figure markdown="span">
!
[](../assets/design/paged_attention/v_vec.png){ align="center" alt="v_vec" width="70%" }
```

### E726e5e269d86e6536952b5b8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L362-L392

```text
</figure>
Now we need to retrieve the value data and perform dot multiplication
with `logits`.
Unlike query and key, there is no thread group
concept for value data.
As shown in diagram, different from key token
```

## official-002-3:hybrid:retrieved

vLLM v0.10.2：多租户前缀相同但需要隔离，应检查缓存键中的什么信息？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "df91ec00-c7cb-4ab4-946a-21a620debcd8",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：多租户前缀相同但需要隔离，应检查缓存键中的什么信息？",
      "hits": 0,
      "evidence": 10
    },
    {
      "step": "generate",
      "duration_ms": 1547.2,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E9334c8ebd5003f269a8dbfa0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
3.
**vLLM Logprob Stability**
\- vLLM does not currently guarantee stable token log probabilities (logprobs).
This can result in different outputs for the
```

### Eb2a0f8bf7ceabe619bc48d27

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

```text
If you are running the container under a different user, you may need to first change the permissions of the library (and all the parent directories) to allow the user to access it, then run vLLM with environment variable `VLLM_NCCL_SO_PATH=/root/.config/vllm/nccl/cu12/libnccl.so.2.18.1` .
```

### Eadfaab7e8dc33ac661f2f94c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L165-L168

```text
You can either install existing plugins or implement your own.
By default, vLLM comes with a [resolver plugin to load LoRA adapters from a local directory.](https://github.com/vllm-project/vllm/tree/main/vllm/plugins/lora_resolvers)
To enable this resolver, set `VLLM_ALLOW_RUNTIME_LORA_UPDATING` to True, set `VLLM_PLUGINS` to include `lora_filesystem_resolver`, and then set `VLLM_LORA_RESOLVER_CACHE_DIR` to a local directory.
```

### Ec6fca19f47e344a23b08f552

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L144-L145

```text
- `IPC_LOCK` security context: add the `IPC_LOCK` capability to the container's security context to lock memory pages and prevent swapping to disk.
- Shared memory with `/dev/shm`: mount `/dev/shm` in the pod spec to provide shared memory for interprocess communication (IPC).
```

### E01cd7f8528e50b0d7013c1be

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L14-L20

```text
## Speculating with a draft model

The following code configures vLLM in an offline mode to use speculative decoding with a draft model, speculating 5 tokens at a time.

!!! warning
    In vllm v0.10.0, speculative decoding with a draft model is not supported.
    If you use the following code, you will get a `NotImplementedError`.
```

### E817b770fdd612fe5c92ce442

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
same request across runs.
For more details, see the FAQ section
titled *Can the output of a prompt vary across runs in vLLM?
```

### E806a86f3d7c94ddceb889b00

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
* in the [FAQs](../usage/faq.md).
While vLLM strives to ensure losslessness in speculative decoding, variations in generated outputs with and without speculative decoding
can occur due to following factors:
- **Floating-Point Precision**: Differences in hardware numerical precision may lead to slight discrepancies in the output distribution.
```

### E1f8f4afd3342de899d5b77f5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
- **Batch Size and Numerical Stability**: Changes in batch size may cause variations in logprobs and output probabilities, potentially
due to non-deterministic behavior in batched operations or numerical instability.
```

### E5a09222d3c9ddb741403611b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
For mitigation strategies, please refer to the FAQ entry *Can the output of a prompt vary across runs in vLLM?
* in the [FAQs](../usage/faq.md).
```

### Ed297b4db013cea35b4dec16a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

```text
!!
! note
```

## official-002-3:hybrid_rerank:retrieved

vLLM v0.10.2：多租户前缀相同但需要隔离，应检查缓存键中的什么信息？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "82ce82f2-ab91-46a8-b1e1-97522a518e95",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：多租户前缀相同但需要隔离，应检查缓存键中的什么信息？",
      "hits": 0,
      "evidence": 11
    },
    {
      "step": "generate",
      "duration_ms": 2288.5,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E1463499a732287269ea92129

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
To improve privacy in shared environments, vLLM supports isolating prefix cache reuse through optional per-request salting.
By including a `cache_salt` in the request, this value is injected into the hash of the first block, ensuring that only requests with the same salt can reuse cached KV blocks.
This prevents timing-based attacks where an adversary could infer cached content by observing latency differences.
```

### Eb2a0f8bf7ceabe619bc48d27

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

```text
If you are running the container under a different user, you may need to first change the permissions of the library (and all the parent directories) to allow the user to access it, then run vLLM with environment variable `VLLM_NCCL_SO_PATH=/root/.config/vllm/nccl/cu12/libnccl.so.2.18.1` .
```

### E53a04ce20e63602ad4637565

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L33-L33

```text
3. Evaluating accuracy in vLLM
```

### E744227b8a6f815899ea7e35a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

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

### E08bb8c7f5e64fc23a316108f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L142-L174

```text
int* ptr = (int*)malloc(sizeof(int));
write_value<<<1, 1>>>(ptr, 1);
// Synchronize required
// (before, cudaMemcpy was synchronizing)
cudaDeviceSynchronize();
```

### E5dda40ed0c5092aadb08696f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
In the rest of this document, we first introduce the data structure used for prefix caching in vLLM v1, followed by the prefix caching workflow of major KV cache operators (e.g., allocate, append, free, eviction).
Finally, we use an example to illustrate the end to end prefix caching workflow.
**Cache Isolation for Security**
```

### Ea78a5260abf923558a637c53

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
This offers protection without compromising performance.
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Here is a document with details about the world series: ..."},
    {"role": "user", "content": "Who won the world series in 2020?"}
  ],
  "cache_salt": "your-cache-salt"
}
```
```

### E5d8fe7ed6ec122403b10c915

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
With this setup, cache sharing is limited to users or requests that explicitly agree on a common salt, enabling cache reuse within a trust group while isolating others.
```

### E9179e0166553b73ef2a10c4b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
!!
! note
Cache isolation is not supported in engine V0.
```

### E0049cea289627054ed67f5d7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

```text
The argument `vllm/vllm-openai` specifies the image to run, and should be replaced with the name of the custom-built image (the `-t` tag from the build command).
```

### Ed297b4db013cea35b4dec16a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

```text
!!
! note
**For version 0.4.1 and 0.4.2 only** - the vLLM docker images under these versions are supposed to be run under the root user since a library under the root user's home directory, i.e.
```

## official-002-4:oracle:oracle

vLLM v0.10.2：先确认服务模型支持LoRA，再考虑两个LoRA请求文本相同，为什么缓存键仍需额外区分身份？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。；服务模型须支持LoRA；切换适配器时缓存键还需要适配器身份。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "5d35361a-3674-416c-8e6f-16049dc2be54",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：先确认服务模型支持LoRA，再考虑两个LoRA请求文本相同，为什么缓存键仍需额外区分身份？",
      "hits": 0,
      "evidence": 2
    },
    {
      "step": "generate",
      "duration_ms": 1743.8,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E1ea8fd1c1607655904749488

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/design/prefix_caching.md

```text
Extra hashes: Other values required to make this block unique, such as LoRA IDs, multi-modality input hashes (see the example below), and cache salts to isolate caches in multi-tenant environments.
```

### E626a0a41fb1d95a0092ba36d

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/lora.md

```text
LoRA adapters can be used with any vLLM model that implements
```

## official-002-4:bm25:retrieved

vLLM v0.10.2：先确认服务模型支持LoRA，再考虑两个LoRA请求文本相同，为什么缓存键仍需额外区分身份？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。；服务模型须支持LoRA；切换适配器时缓存键还需要适配器身份。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "1b7a5e0a-6d7e-477f-8b50-2d5da27dcf2b",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：先确认服务模型支持LoRA，再考虑两个LoRA请求文本相同，为什么缓存键仍需额外区分身份？",
      "hits": 0,
      "evidence": 7
    },
    {
      "step": "generate",
      "duration_ms": 1448.8,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E18b40967bf69bdff910d3cff

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L52-L61

```text
## Serving LoRA Adapters

LoRA adapted models can also be served with the Open-AI compatible vLLM server. To do so, we use
`--lora-modules {name}={path} {name}={path}` to specify each LoRA module when we kick off the server:

```bash
vllm serve meta-llama/Llama-2-7b-hf \
    --enable-lora \
    --lora-modules sql-lora=$HOME/.cache/huggingface/hub/models--yard1--llama-2-7b-sql-lora-test/snapshots/0dfa347e8877a4d4ed19ee56c140fa518470028c/
```
```

### E6d8cc64a2f6933e5ab8b6091

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L357-L372

```text
For example, if your LoRA adapters have ranks [16, 32, 64], use `--max-lora-rank 64` rather than 256
```bash
# Good: matches actual maximum rank
vllm serve model --enable-lora --max-lora-rank 64

# Bad: unnecessarily high, wastes memory
vllm serve model --enable-lora --max-lora-rank 256
```
```

### Eadfaab7e8dc33ac661f2f94c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L165-L168

```text
You can either install existing plugins or implement your own.
By default, vLLM comes with a [resolver plugin to load LoRA adapters from a local directory.](https://github.com/vllm-project/vllm/tree/main/vllm/plugins/lora_resolvers)
To enable this resolver, set `VLLM_ALLOW_RUNTIME_LORA_UPDATING` to True, set `VLLM_PLUGINS` to include `lora_filesystem_resolver`, and then set `VLLM_LORA_RESOLVER_CACHE_DIR` to a local directory.
```

### E855452e936e497bf2e51ce80

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L114-L119

```text
To enable dynamic LoRA configuration, ensure that the environment variable `VLLM_ALLOW_RUNTIME_LORA_UPDATING`
is set to `True`.

```bash
export VLLM_ALLOW_RUNTIME_LORA_UPDATING=True
```
```

### E73367775116b0ea04ade603e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L1-L27

```text
# LoRA Adapters
This document shows you how to use [LoRA adapters](https://arxiv.org/abs/2106.09685) with vLLM on top of a base model.
LoRA adapters can be used with any vLLM model that implements [SupportsLoRA][vllm.model_executor.models.interfaces.SupportsLoRA].
Adapters can be efficiently served on a per request basis with minimal overhead.
First we download the adapter(s) and save
them locally with
```

### E3ce9529770c0dd4b62db0b21

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L357-L372

```text
### Configuring `max_lora_rank`
The `--max-lora-rank` parameter controls the maximum rank allowed for LoRA adapters.
This setting affects memory allocation and performance:
- **Set it to the maximum rank** among all LoRA adapters you plan to use
- **Avoid setting it too high** - using a value much larger than needed wastes memory and can cause performance issues
```

### E062010e52f86dd5d0e443c52

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L165-L168

```text
When vLLM receives a request using a LoRA adapter `foobar`,
it will first look in the local directory for a directory `foobar`, and attempt to load the contents of that directory as a LoRA adapter.
If successful, the request will complete as normal and
that adapter will then be available for normal use on the server.
```

## official-002-4:dense:retrieved

vLLM v0.10.2：先确认服务模型支持LoRA，再考虑两个LoRA请求文本相同，为什么缓存键仍需额外区分身份？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。；服务模型须支持LoRA；切换适配器时缓存键还需要适配器身份。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "5b427a5d-3c26-453e-bc43-75c6ea4c2188",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：先确认服务模型支持LoRA，再考虑两个LoRA请求文本相同，为什么缓存键仍需额外区分身份？",
      "hits": 0,
      "evidence": 9
    },
    {
      "step": "generate",
      "duration_ms": 1337.9,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ebd417708ca6c39c6b97c74fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L172-L203

```text
lora_request = LoRARequest(
                    lora_name=lora_name,
                    lora_path=local_path,
                    lora_int_id=abs(hash(lora_name))
                )
                return lora_request
        ```
```

### E85b2e3d3e5be6edc336efae6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L216-L231

```text
```bash
--lora-modules '{"name": "sql-lora", "path": "/path/to/lora", "base_model_name": "meta-llama/Llama-2-7b"}'
```
To provide the backward compatibility support, you can still use the old key-value format (name=path), but the `base_model_name` will remain unspecified in that case.
```

### E4577c1b7f2ba3f1166805e89

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L216-L231

```text
## New format for `--lora-modules`
In the previous version, users would provide LoRA modules via the following format, either as a key-value pair or in JSON format.
For example:
```

### Ea046f275b4b86291bc9fdffa

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L343-L343

```text
You can also pass a json dictionary of `--default-mm-loras` mapping modalities to LoRA model IDs. For example, when starting the server:
```

### Eadfaab7e8dc33ac661f2f94c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L165-L168

```text
You can either install existing plugins or implement your own.
By default, vLLM comes with a [resolver plugin to load LoRA adapters from a local directory.](https://github.com/vllm-project/vllm/tree/main/vllm/plugins/lora_resolvers)
To enable this resolver, set `VLLM_ALLOW_RUNTIME_LORA_UPDATING` to True, set `VLLM_PLUGINS` to include `lora_filesystem_resolver`, and then set `VLLM_LORA_RESOLVER_CACHE_DIR` to a local directory.
```

### E10300437bc40da2237f14ed8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L172-L203

```text
(self, base_model_name, lora_name):
                s3_path = self.s3_path_format.format(base_model_name=base_model_name, lora_name=lora_name)
                local_path = self.local_path_format.format(base_model_name=base_model_name, lora_name=lora_name)

                # Download the LoRA from S3 to the local path
                await self.s3._get(
                    s3_path, local_path, recursive=True, maxdepth=1
                )

        
```

### Ebf812ffaa039ef650f8eb40e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L172-L203

```text
```python
        import os
        import s3fs
        from vllm.lora.request import LoRARequest
        from vllm.lora.resolver import LoRAResolver

        class S3LoRAResolver(LoRAResolver):
            def __init__(self):
                self.s3 = s3fs.S3FileSystem()
                self.s3_path_format = os.getenv("S3_PATH_TEMPLATE")
                self.local_path_format = os.getenv("LOCAL_PATH_TEMPLATE")

            async def resolve_lora
```

### E06c1e79fda42049fdc268fee

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L172-L203

```text
1.
Implement the LoRAResolver interface.
?
??
code "Example of a simple S3 LoRAResolver implementation"
```

### E062010e52f86dd5d0e443c52

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L165-L168

```text
When vLLM receives a request using a LoRA adapter `foobar`,
it will first look in the local directory for a directory `foobar`, and attempt to load the contents of that directory as a LoRA adapter.
If successful, the request will complete as normal and
that adapter will then be available for normal use on the server.
```

## official-002-4:hybrid:retrieved

vLLM v0.10.2：先确认服务模型支持LoRA，再考虑两个LoRA请求文本相同，为什么缓存键仍需额外区分身份？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。；服务模型须支持LoRA；切换适配器时缓存键还需要适配器身份。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "156063db-8072-4840-98ba-94a977ae1c10",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：先确认服务模型支持LoRA，再考虑两个LoRA请求文本相同，为什么缓存键仍需额外区分身份？",
      "hits": 0,
      "evidence": 8
    },
    {
      "step": "generate",
      "duration_ms": 1463.5,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E18b40967bf69bdff910d3cff

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L52-L61

```text
## Serving LoRA Adapters

LoRA adapted models can also be served with the Open-AI compatible vLLM server. To do so, we use
`--lora-modules {name}={path} {name}={path}` to specify each LoRA module when we kick off the server:

```bash
vllm serve meta-llama/Llama-2-7b-hf \
    --enable-lora \
    --lora-modules sql-lora=$HOME/.cache/huggingface/hub/models--yard1--llama-2-7b-sql-lora-test/snapshots/0dfa347e8877a4d4ed19ee56c140fa518470028c/
```
```

### Eadfaab7e8dc33ac661f2f94c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L165-L168

```text
You can either install existing plugins or implement your own.
By default, vLLM comes with a [resolver plugin to load LoRA adapters from a local directory.](https://github.com/vllm-project/vllm/tree/main/vllm/plugins/lora_resolvers)
To enable this resolver, set `VLLM_ALLOW_RUNTIME_LORA_UPDATING` to True, set `VLLM_PLUGINS` to include `lora_filesystem_resolver`, and then set `VLLM_LORA_RESOLVER_CACHE_DIR` to a local directory.
```

### Ebd417708ca6c39c6b97c74fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L172-L203

```text
lora_request = LoRARequest(
                    lora_name=lora_name,
                    lora_path=local_path,
                    lora_int_id=abs(hash(lora_name))
                )
                return lora_request
        ```
```

### Efc55291935303ead3eaceed3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L108-L110

```text
## Dynamically serving LoRA Adapters

In addition to serving LoRA adapters at server startup, the vLLM server supports dynamically configuring LoRA adapters at runtime through dedicated API endpoints and plugins. This feature can be particularly useful when the flexibility to change models on-the-fly is needed.
```

### E855452e936e497bf2e51ce80

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L114-L119

```text
To enable dynamic LoRA configuration, ensure that the environment variable `VLLM_ALLOW_RUNTIME_LORA_UPDATING`
is set to `True`.

```bash
export VLLM_ALLOW_RUNTIME_LORA_UPDATING=True
```
```

### E062010e52f86dd5d0e443c52

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L165-L168

```text
When vLLM receives a request using a LoRA adapter `foobar`,
it will first look in the local directory for a directory `foobar`, and attempt to load the contents of that directory as a LoRA adapter.
If successful, the request will complete as normal and
that adapter will then be available for normal use on the server.
```

### E10300437bc40da2237f14ed8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L172-L203

```text
(self, base_model_name, lora_name):
                s3_path = self.s3_path_format.format(base_model_name=base_model_name, lora_name=lora_name)
                local_path = self.local_path_format.format(base_model_name=base_model_name, lora_name=lora_name)

                # Download the LoRA from S3 to the local path
                await self.s3._get(
                    s3_path, local_path, recursive=True, maxdepth=1
                )

        
```

### E06c1e79fda42049fdc268fee

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L172-L203

```text
1.
Implement the LoRAResolver interface.
?
??
code "Example of a simple S3 LoRAResolver implementation"
```

## official-002-4:hybrid_rerank:retrieved

vLLM v0.10.2：先确认服务模型支持LoRA，再考虑两个LoRA请求文本相同，为什么缓存键仍需额外区分身份？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。；服务模型须支持LoRA；切换适配器时缓存键还需要适配器身份。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "060de4c6-84e2-4189-b6ed-db0f40ecdb3a",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：先确认服务模型支持LoRA，再考虑两个LoRA请求文本相同，为什么缓存键仍需额外区分身份？",
      "hits": 0,
      "evidence": 8
    },
    {
      "step": "generate",
      "duration_ms": 1410.3,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ebd417708ca6c39c6b97c74fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L172-L203

```text
lora_request = LoRARequest(
                    lora_name=lora_name,
                    lora_path=local_path,
                    lora_int_id=abs(hash(lora_name))
                )
                return lora_request
        ```
```

### E3a528fe3c6c257dc764bbd5c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L345-L351

```text
```bash
vllm serve ibm-granite/granite-speech-3.3-2b \
    --max-model-len 2048 \
    --enable-lora \
    --default-mm-loras '{"audio":"ibm-granite/granite-speech-3.3-2b"}' \
    --max-lora-rank 64
```
```

### E18b40967bf69bdff910d3cff

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L52-L61

```text
## Serving LoRA Adapters

LoRA adapted models can also be served with the Open-AI compatible vLLM server. To do so, we use
`--lora-modules {name}={path} {name}={path}` to specify each LoRA module when we kick off the server:

```bash
vllm serve meta-llama/Llama-2-7b-hf \
    --enable-lora \
    --lora-modules sql-lora=$HOME/.cache/huggingface/hub/models--yard1--llama-2-7b-sql-lora-test/snapshots/0dfa347e8877a4d4ed19ee56c140fa518470028c/
```
```

### E85b2e3d3e5be6edc336efae6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L216-L231

```text
```bash
--lora-modules '{"name": "sql-lora", "path": "/path/to/lora", "base_model_name": "meta-llama/Llama-2-7b"}'
```
To provide the backward compatibility support, you can still use the old key-value format (name=path), but the `base_model_name` will remain unspecified in that case.
```

### E6639307c506adfc92f30cc73

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L242-L276

```text
{
                .....
                }
            ]
            },
            {
            "id": "sql-lora",
            "object": "model",
            "created": 1715644056,
            "owned_by": "vllm",
            "root": "~/.cache/huggingface/hub/models--yard1--llama-2-7b-sql-lora-test/snapshots/0dfa347e8877a4d4ed19ee56c140fa518470028c/",
            "parent": meta-llama/Llama-2-7b-hf,
            "permission": [
                {
   
```

### E10300437bc40da2237f14ed8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L172-L203

```text
(self, base_model_name, lora_name):
                s3_path = self.s3_path_format.format(base_model_name=base_model_name, lora_name=lora_name)
                local_path = self.local_path_format.format(base_model_name=base_model_name, lora_name=lora_name)

                # Download the LoRA from S3 to the local path
                await self.s3._get(
                    s3_path, local_path, recursive=True, maxdepth=1
                )

        
```

### Ebf812ffaa039ef650f8eb40e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L172-L203

```text
```python
        import os
        import s3fs
        from vllm.lora.request import LoRARequest
        from vllm.lora.resolver import LoRAResolver

        class S3LoRAResolver(LoRAResolver):
            def __init__(self):
                self.s3 = s3fs.S3FileSystem()
                self.s3_path_format = os.getenv("S3_PATH_TEMPLATE")
                self.local_path_format = os.getenv("LOCAL_PATH_TEMPLATE")

            async def resolve_lora
```

### E06c1e79fda42049fdc268fee

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L172-L203

```text
1.
Implement the LoRAResolver interface.
?
??
```

## official-004-1:oracle:oracle

vLLM v0.10.2：Ampere在此版本支持的FP8配置与kernel是什么？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "b275f280-aa50-4e6e-a5e1-b9b5000bdda1",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：Ampere在此版本支持的FP8配置与kernel是什么？",
      "hits": 0,
      "evidence": 1
    },
    {
      "step": "generate",
      "duration_ms": 1364.6,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ef799598e9c44e1e80614ed21

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/quantization/fp8.md

```text
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

## official-004-1:bm25:retrieved

vLLM v0.10.2：Ampere在此版本支持的FP8配置与kernel是什么？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "288d2be3-dc52-4886-bba5-a79084e85aca",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：Ampere在此版本支持的FP8配置与kernel是什么？",
      "hits": 0,
      "evidence": 9
    },
    {
      "step": "generate",
      "duration_ms": 1558.8,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E707fd541c52eb73c2ed6c6d8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

### E304d729ae809670c7310aad7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L15-L17

```text
!!! note
    FP8 computation is supported on NVIDIA GPUs with compute capability > 8.9 (Ada Lovelace, Hopper).
    FP8 models will run on compute capability > 8.0 (Ampere) as weight-only W8A16, utilizing FP8 Marlin.
```

### E400a2325c86135a091062b95

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L8-L8

```text
Please visit the HF collection of [quantized FP8 checkpoints of popular LLMs ready to use with vLLM](https://huggingface.co/collections/neuralmagic/fp8-llms-for-vllm-666742ed2b78b7ac8df13127).
```

### E16f7d126776da84bba5a8652

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
| `SGLANG_FORCE_FP8_MARLIN` | Force using FP8 MARLIN kernels even if other FP8 kernels are available | `false` |
| `SGLANG_ENABLE_FLASHINFER_GEMM` | Use flashinfer kernels when running blockwise fp8 GEMM on Blackwell GPUs | `false` |
| `SGLANG_SUPPORT_CUTLASS_BLOCK_FP8` | Use Cutlass kernels when running blockwise fp8 GEMM on Hopper or Blackwell GPUs | `false` |
| `SGLANG_CUTLASS_MOE` | Use Cutlass FP8 MoE kernel on Blackwell GPUs | `false` |
```

### Ef875130d2ac8c37dc2ed476c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L12-L19

```text
- [ ] batch mm for FP8 optimization on rocm
- [x] composable kernel block gemm https://github.com/sgl-project/sglang/pull/4075
```

### Ef54934c2952f9f0e01ac3b8e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
Quantization of models with FP8 allows for a 2x reduction in model memory requirements and up to a 1.6x improvement in throughput with minimal impact on accuracy.
```

### E112b956fffe3fc7785a2dec1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
## Model-Specific Options
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_USE_AITER` | Use AITER optimize implementation | `false` |
| `SGLANG_INT4_WEIGHT` | Enable INT4 weight quantization | `false` |
| `SGLANG_MOE_PADDING` | Enable MoE padding (sets padding size to 128 if value is `1`, often set to `1` in Docker builds) | `0` |
```

### E4e1044238dc894ec734a0d3c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L12-L19

```text
### TODO
- [x] amd base image testing https://github.com/sgl-project/sglang/pull/2692
- [x] sgl-kernel add amd backend https://github.com/sgl-project/sglang/pull/3287
- [x] DeepseekV3 triton MOE config optimization https://github.com/sgl-project/sglang/pull/3146
```

### Eca92fdaba7b018d8ee335a73

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L12-L19

```text
- [x] ep moe
<!
-- Describe the changes made in this PR.
-->
```

## official-004-1:dense:retrieved

vLLM v0.10.2：Ampere在此版本支持的FP8配置与kernel是什么？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "3841690f-1621-4820-9125-958eb60c19f2",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：Ampere在此版本支持的FP8配置与kernel是什么？",
      "hits": 0,
      "evidence": 7
    },
    {
      "step": "generate",
      "duration_ms": 1252.3,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E707fd541c52eb73c2ed6c6d8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

### Ef0bcfaaeb4a524e28e862f7a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L148-L148

```text
kernel_D<<< ..., stream1 >>>(...);
```

### E1ca51f7844ccfd2fad082f24

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L27-L27

```text
AMD MI300, NVIDIA Hopper or later) support native hardware conversion between FP8 and other formats (fp32, fp16, bf16), this benefit is not yet fully realized.
```

### E988ae850271d6537ff6da7a7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L135-L135

```text
kernel_A<<< ..., stream1 >>>(...);
```

### Ed6d39e475341f4ab01dc6509

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L50-L51

```text
### To reproduce:
vllm version: v0.9.2
```

### Ef54934c2952f9f0e01ac3b8e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
Quantization of models with FP8 allows for a 2x reduction in model memory requirements and up to a 1.6x improvement in throughput with minimal impact on accuracy.
```

### Eae834ae549878a8e7655820e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L27-L27

```text
However, there are currently no latency improvements as the implementation does not yet include fused dequantization and attention operations.
Future releases will support quantized attention with hardware acceleration, which should provide additional performance benefits.
While the most recent silicon offerings (e.g.
```

## official-004-1:hybrid:retrieved

vLLM v0.10.2：Ampere在此版本支持的FP8配置与kernel是什么？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "b34d568b-f9b0-48bb-9266-4c7ea9501ba8",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：Ampere在此版本支持的FP8配置与kernel是什么？",
      "hits": 0,
      "evidence": 8
    },
    {
      "step": "generate",
      "duration_ms": 1344.1,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E707fd541c52eb73c2ed6c6d8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

### E304d729ae809670c7310aad7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L15-L17

```text
!!! note
    FP8 computation is supported on NVIDIA GPUs with compute capability > 8.9 (Ada Lovelace, Hopper).
    FP8 models will run on compute capability > 8.0 (Ampere) as weight-only W8A16, utilizing FP8 Marlin.
```

### E7a06027150976a90d15667d4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L19-L21

```text
## Installation

To produce performant FP8 quantized models with vLLM, you'll need to install the [llm-compressor](https://github.com/vllm-project/llm-compressor/) library:
```

### E8c0a6d8da59e340ff546c81b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L10-L10

```text
The FP8 types typically supported in hardware have two distinct representations, each useful in different scenarios:
```

### E904c381bf1f5f1779dedef72

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
This action will ignore the Hugging Face config's quantization settings.
For instance, with `neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic`, if you execute with `--quantization w8a8_fp8`, the system will use the `W8A8Fp8Config` from SGLang to invoke the sgl-kernel, rather than the `CompressedTensorsConfig` for vLLM kernels.
```

### Ef54934c2952f9f0e01ac3b8e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
Quantization of models with FP8 allows for a 2x reduction in model memory requirements and up to a 1.6x improvement in throughput with minimal impact on accuracy.
```

### E74b994b5ce8fbeb1f2a0b11e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4 \
    --port 30000 --host 0.0.0.0
```
Take note, if your model is **per-channel quantized (INT8 or FP8) with per-token dynamic quantization activation**, you can opt to include `--quantization w8a8_int8` or `--quantization w8a8_fp8` to invoke the corresponding CUTLASS int8_kernel or fp8_kernel in sgl-kernel.
```

### Ef6c630563d458d3c5beb00ac

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic \
    --quantization w8a8_fp8 \
    --port 30000 --host 0.0.0.0
```
```

## official-004-1:hybrid_rerank:retrieved

vLLM v0.10.2：Ampere在此版本支持的FP8配置与kernel是什么？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "6da26823-2bcd-46c4-8108-966fbad73978",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：Ampere在此版本支持的FP8配置与kernel是什么？",
      "hits": 0,
      "evidence": 9
    },
    {
      "step": "generate",
      "duration_ms": 2364.7,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E707fd541c52eb73c2ed6c6d8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

### Ea69ba78298695847964cf47f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L54-L56

```text
- `"auto"`: Uses the model's default "unquantized" data type
- `"fp8"` or `"fp8_e4m3"`: Supported on CUDA 11.8+ and ROCm (AMD GPU)
- `"fp8_e5m2"`: Supported on CUDA 11.8+
```

### E304d729ae809670c7310aad7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L15-L17

```text
!!! note
    FP8 computation is supported on NVIDIA GPUs with compute capability > 8.9 (Ada Lovelace, Hopper).
    FP8 models will run on compute capability > 8.0 (Ampere) as weight-only W8A16, utilizing FP8 Marlin.
```

### E904c381bf1f5f1779dedef72

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
This action will ignore the Hugging Face config's quantization settings.
For instance, with `neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic`, if you execute with `--quantization w8a8_fp8`, the system will use the `W8A8Fp8Config` from SGLang to invoke the sgl-kernel, rather than the `CompressedTensorsConfig` for vLLM kernels.
```

### Ea6bcaebd8167730f80fdf7fa

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L121-L137

```text
## Online Dynamic Quantization
Dynamic quantization of an original precision BF16/FP16 model to FP8 can be achieved with vLLM without any calibration data required.
You can enable the feature by specifying `--quantization="fp8"` in the command line or setting `quantization="fp8"` in the LLM constructor.
```

### Ef54934c2952f9f0e01ac3b8e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
Quantization of models with FP8 allows for a 2x reduction in model memory requirements and up to a 1.6x improvement in throughput with minimal impact on accuracy.
```

### E74b994b5ce8fbeb1f2a0b11e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4 \
    --port 30000 --host 0.0.0.0
```
Take note, if your model is **per-channel quantized (INT8 or FP8) with per-token dynamic quantization activation**, you can opt to include `--quantization w8a8_int8` or `--quantization w8a8_fp8` to invoke the corresponding CUTLASS int8_kernel or fp8_kernel in sgl-kernel.
```

### Ef6c630563d458d3c5beb00ac

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic \
    --quantization w8a8_fp8 \
    --port 30000 --host 0.0.0.0
```
```

### E89847cad528bee0939cb2a61

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L121-L137

```text
In this mode, all Linear modules (except for the final `lm_head`) have their weights quantized down to FP8_E4M3 precision with a per-tensor scale.
```

## official-004-2:oracle:oracle

vLLM v0.10.2：能否把Ampere的W8A16支持解释为W8A8？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "17cb0087-13f6-4cca-9866-76ca7977c4a9",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：能否把Ampere的W8A16支持解释为W8A8？",
      "hits": 0,
      "evidence": 1
    },
    {
      "step": "generate",
      "duration_ms": 1280.7,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ef799598e9c44e1e80614ed21

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/quantization/fp8.md

```text
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

## official-004-2:bm25:retrieved

vLLM v0.10.2：能否把Ampere的W8A16支持解释为W8A8？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "08a92e1d-598a-4544-91db-0a8c0acf253d",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：能否把Ampere的W8A16支持解释为W8A8？",
      "hits": 0,
      "evidence": 6
    },
    {
      "step": "generate",
      "duration_ms": 1268.1,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E707fd541c52eb73c2ed6c6d8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

### E304d729ae809670c7310aad7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L15-L17

```text
!!! note
    FP8 computation is supported on NVIDIA GPUs with compute capability > 8.9 (Ada Lovelace, Hopper).
    FP8 models will run on compute capability > 8.0 (Ampere) as weight-only W8A16, utilizing FP8 Marlin.
```

### E400a2325c86135a091062b95

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L8-L8

```text
Please visit the HF collection of [quantized FP8 checkpoints of popular LLMs ready to use with vLLM](https://huggingface.co/collections/neuralmagic/fp8-llms-for-vllm-666742ed2b78b7ac8df13127).
```

### E01cd7f8528e50b0d7013c1be

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L14-L20

```text
## Speculating with a draft model

The following code configures vLLM in an offline mode to use speculative decoding with a draft model, speculating 5 tokens at a time.

!!! warning
    In vllm v0.10.0, speculative decoding with a draft model is not supported.
    If you use the following code, you will get a `NotImplementedError`.
```

### E8c0a6d8da59e340ff546c81b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L10-L10

```text
The FP8 types typically supported in hardware have two distinct representations, each useful in different scenarios:
```

### Ef54934c2952f9f0e01ac3b8e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
Quantization of models with FP8 allows for a 2x reduction in model memory requirements and up to a 1.6x improvement in throughput with minimal impact on accuracy.
```

## official-004-2:dense:retrieved

vLLM v0.10.2：能否把Ampere的W8A16支持解释为W8A8？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "2fa5721b-69ab-4c95-a0c1-bba8acf13485",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：能否把Ampere的W8A16支持解释为W8A8？",
      "hits": 0,
      "evidence": 6
    },
    {
      "step": "generate",
      "duration_ms": 1221.0,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E707fd541c52eb73c2ed6c6d8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

### E0e84432891126a30a6e4410c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L26-L29

```text
```python
from vllm import LLM
llm = LLM("Qwen/Qwen3-0.6B", enable_sleep_mode=True)
```
```

### Ed6d39e475341f4ab01dc6509

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L50-L51

```text
### To reproduce:
vllm version: v0.9.2
```

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### E8c0a6d8da59e340ff546c81b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L10-L10

```text
The FP8 types typically supported in hardware have two distinct representations, each useful in different scenarios:
```

### Ef54934c2952f9f0e01ac3b8e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
Quantization of models with FP8 allows for a 2x reduction in model memory requirements and up to a 1.6x improvement in throughput with minimal impact on accuracy.
```

## official-004-2:hybrid:retrieved

vLLM v0.10.2：能否把Ampere的W8A16支持解释为W8A8？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "b8537450-9b7f-4a2a-acad-c07cee964559",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：能否把Ampere的W8A16支持解释为W8A8？",
      "hits": 0,
      "evidence": 8
    },
    {
      "step": "generate",
      "duration_ms": 1328.6,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E707fd541c52eb73c2ed6c6d8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

### E8c0a6d8da59e340ff546c81b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L10-L10

```text
The FP8 types typically supported in hardware have two distinct representations, each useful in different scenarios:
```

### E304d729ae809670c7310aad7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L15-L17

```text
!!! note
    FP8 computation is supported on NVIDIA GPUs with compute capability > 8.9 (Ada Lovelace, Hopper).
    FP8 models will run on compute capability > 8.0 (Ampere) as weight-only W8A16, utilizing FP8 Marlin.
```

### E904c381bf1f5f1779dedef72

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
This action will ignore the Hugging Face config's quantization settings.
For instance, with `neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic`, if you execute with `--quantization w8a8_fp8`, the system will use the `W8A8Fp8Config` from SGLang to invoke the sgl-kernel, rather than the `CompressedTensorsConfig` for vLLM kernels.
```

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### Ef54934c2952f9f0e01ac3b8e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
Quantization of models with FP8 allows for a 2x reduction in model memory requirements and up to a 1.6x improvement in throughput with minimal impact on accuracy.
```

### E74b994b5ce8fbeb1f2a0b11e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4 \
    --port 30000 --host 0.0.0.0
```
Take note, if your model is **per-channel quantized (INT8 or FP8) with per-token dynamic quantization activation**, you can opt to include `--quantization w8a8_int8` or `--quantization w8a8_fp8` to invoke the corresponding CUTLASS int8_kernel or fp8_kernel in sgl-kernel.
```

### Ef6c630563d458d3c5beb00ac

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic \
    --quantization w8a8_fp8 \
    --port 30000 --host 0.0.0.0
```
```

## official-004-2:hybrid_rerank:retrieved

vLLM v0.10.2：能否把Ampere的W8A16支持解释为W8A8？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "afbbcbb0-4284-4dda-bf7e-db4f480f0885",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：能否把Ampere的W8A16支持解释为W8A8？",
      "hits": 0,
      "evidence": 6
    },
    {
      "step": "generate",
      "duration_ms": 1380.3,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E707fd541c52eb73c2ed6c6d8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

### E304d729ae809670c7310aad7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L15-L17

```text
!!! note
    FP8 computation is supported on NVIDIA GPUs with compute capability > 8.9 (Ada Lovelace, Hopper).
    FP8 models will run on compute capability > 8.0 (Ampere) as weight-only W8A16, utilizing FP8 Marlin.
```

### E904c381bf1f5f1779dedef72

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
This action will ignore the Hugging Face config's quantization settings.
For instance, with `neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic`, if you execute with `--quantization w8a8_fp8`, the system will use the `W8A8Fp8Config` from SGLang to invoke the sgl-kernel, rather than the `CompressedTensorsConfig` for vLLM kernels.
```

### E74b994b5ce8fbeb1f2a0b11e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4 \
    --port 30000 --host 0.0.0.0
```
Take note, if your model is **per-channel quantized (INT8 or FP8) with per-token dynamic quantization activation**, you can opt to include `--quantization w8a8_int8` or `--quantization w8a8_fp8` to invoke the corresponding CUTLASS int8_kernel or fp8_kernel in sgl-kernel.
```

### Ef6c630563d458d3c5beb00ac

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic \
    --quantization w8a8_fp8 \
    --port 30000 --host 0.0.0.0
```
```

### Ef54934c2952f9f0e01ac3b8e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
Quantization of models with FP8 allows for a 2x reduction in model memory requirements and up to a 1.6x improvement in throughput with minimal impact on accuracy.
```

## official-004-3:oracle:oracle

vLLM v0.10.2：在Ampere部署FP8模型时把激活也按8bit支持处理，应先核对哪个限制？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "a89c4077-1633-4e6f-9f61-886d152ca7ba",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：在Ampere部署FP8模型时把激活也按8bit支持处理，应先核对哪个限制？",
      "hits": 0,
      "evidence": 1
    },
    {
      "step": "generate",
      "duration_ms": 1533.7,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ef799598e9c44e1e80614ed21

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/quantization/fp8.md

```text
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

## official-004-3:bm25:retrieved

vLLM v0.10.2：在Ampere部署FP8模型时把激活也按8bit支持处理，应先核对哪个限制？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "f2ecc0fe-1543-4e9e-b3d0-ce61048660fe",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：在Ampere部署FP8模型时把激活也按8bit支持处理，应先核对哪个限制？",
      "hits": 0,
      "evidence": 9
    },
    {
      "step": "generate",
      "duration_ms": 1339.4,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E707fd541c52eb73c2ed6c6d8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

### E304d729ae809670c7310aad7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L15-L17

```text
!!! note
    FP8 computation is supported on NVIDIA GPUs with compute capability > 8.9 (Ada Lovelace, Hopper).
    FP8 models will run on compute capability > 8.0 (Ampere) as weight-only W8A16, utilizing FP8 Marlin.
```

### E400a2325c86135a091062b95

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L8-L8

```text
Please visit the HF collection of [quantized FP8 checkpoints of popular LLMs ready to use with vLLM](https://huggingface.co/collections/neuralmagic/fp8-llms-for-vllm-666742ed2b78b7ac8df13127).
```

### E7a06027150976a90d15667d4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L19-L21

```text
## Installation

To produce performant FP8 quantized models with vLLM, you'll need to install the [llm-compressor](https://github.com/vllm-project/llm-compressor/) library:
```

### Ea6bcaebd8167730f80fdf7fa

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L121-L137

```text
## Online Dynamic Quantization
Dynamic quantization of an original precision BF16/FP16 model to FP8 can be achieved with vLLM without any calibration data required.
You can enable the feature by specifying `--quantization="fp8"` in the command line or setting `quantization="fp8"` in the LLM constructor.
```

### Ef54934c2952f9f0e01ac3b8e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
Quantization of models with FP8 allows for a 2x reduction in model memory requirements and up to a 1.6x improvement in throughput with minimal impact on accuracy.
```

### E89847cad528bee0939cb2a61

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L121-L137

```text
In this mode, all Linear modules (except for the final `lm_head`) have their weights quantized down to FP8_E4M3 precision with a per-tensor scale.
Activations have their minimum and maximum values calculated during each forward pass to provide a dynamic per-tensor scale for high accuracy.
As a result, latency improvements are limited in this mode.
```

### E234e1c6204abd1316e61d229

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L121-L137

```text
```python
from vllm import LLM

llm = LLM("facebook/opt-125m", quantization="fp8")
# INFO 06-10 17:55:42 model_runner.py:157] Loading model weights took 0.1550 GB
result = llm.generate("Hello, my name is")
print(result[0].outputs[0].text)
```
```

### Efed7071e79f74c856c3435e5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L121-L137

```text
!!
! warning
Currently, we load the model at original precision before quantizing down to 8-bits, so you need enough memory to load the whole model.
```

## official-004-3:dense:retrieved

vLLM v0.10.2：在Ampere部署FP8模型时把激活也按8bit支持处理，应先核对哪个限制？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "3ca1a24c-ed60-4229-bd9d-539dcf3111a1",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：在Ampere部署FP8模型时把激活也按8bit支持处理，应先核对哪个限制？",
      "hits": 0,
      "evidence": 11
    },
    {
      "step": "generate",
      "duration_ms": 1381.6,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E9179e0166553b73ef2a10c4b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
!!
! note
Cache isolation is not supported in engine V0.
```

### E707fd541c52eb73c2ed6c6d8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

### E2a987935049ba4a72d481f15

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L1-L3

```text
# Sleep Mode

vLLM's Sleep Mode allows you to temporarily release most GPU memory used by a model, including model weights and KV cache, without stopping the server or unloading the Docker container. This is especially useful for RLHF, training, or cost-saving scenarios where GPU resources need to be freed between inference workloads.
```

### E8c0a6d8da59e340ff546c81b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L10-L10

```text
The FP8 types typically supported in hardware have two distinct representations, each useful in different scenarios:
```

### Eb09a14de4b65a8718d6c9f01

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L589-L603

```text
// execute on CPU
cudaMemLocation location = {.type = cudaMemLocationTypeDevice, .id = myGpuId};
cudaMemPrefetchAsync(data, N, location, s, 0 /* flags */);
// prefetch to GPU
```

### E5d8fe7ed6ec122403b10c915

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
With this setup, cache sharing is limited to users or requests that explicitly agree on a common salt, enabling cache reuse within a trust group while isolating others.
```

### Ea78a5260abf923558a637c53

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
This offers protection without compromising performance.
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Here is a document with details about the world series: ..."},
    {"role": "user", "content": "Who won the world series in 2020?"}
  ],
  "cache_salt": "your-cache-salt"
}
```
```

### E1463499a732287269ea92129

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
To improve privacy in shared environments, vLLM supports isolating prefix cache reuse through optional per-request salting.
By including a `cache_salt` in the request, this value is injected into the hash of the first block, ensuring that only requests with the same salt can reuse cached KV blocks.
This prevents timing-based attacks where an adversary could infer cached content by observing latency differences.
```

### E5dda40ed0c5092aadb08696f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
In the rest of this document, we first introduce the data structure used for prefix caching in vLLM v1, followed by the prefix caching workflow of major KV cache operators (e.g., allocate, append, free, eviction).
Finally, we use an example to illustrate the end to end prefix caching workflow.
**Cache Isolation for Security**
```

### Ef54934c2952f9f0e01ac3b8e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
Quantization of models with FP8 allows for a 2x reduction in model memory requirements and up to a 1.6x improvement in throughput with minimal impact on accuracy.
```

### E52ec56a9d4444256a742d13a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L589-L603

```text
Managed
void test_prefetch_managed(cudaStream_t s) {
char *data;
cudaMallocManaged(&data, N);
init_data(data, N);
```

## official-004-3:hybrid:retrieved

vLLM v0.10.2：在Ampere部署FP8模型时把激活也按8bit支持处理，应先核对哪个限制？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "350a55cb-baad-46c2-a265-a86516d3f330",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：在Ampere部署FP8模型时把激活也按8bit支持处理，应先核对哪个限制？",
      "hits": 0,
      "evidence": 6
    },
    {
      "step": "generate",
      "duration_ms": 1528.9,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E707fd541c52eb73c2ed6c6d8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

### E7a06027150976a90d15667d4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L19-L21

```text
## Installation

To produce performant FP8 quantized models with vLLM, you'll need to install the [llm-compressor](https://github.com/vllm-project/llm-compressor/) library:
```

### E8c0a6d8da59e340ff546c81b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L10-L10

```text
The FP8 types typically supported in hardware have two distinct representations, each useful in different scenarios:
```

### E304d729ae809670c7310aad7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L15-L17

```text
!!! note
    FP8 computation is supported on NVIDIA GPUs with compute capability > 8.9 (Ada Lovelace, Hopper).
    FP8 models will run on compute capability > 8.0 (Ampere) as weight-only W8A16, utilizing FP8 Marlin.
```

### Ea69ba78298695847964cf47f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L54-L56

```text
- `"auto"`: Uses the model's default "unquantized" data type
- `"fp8"` or `"fp8_e4m3"`: Supported on CUDA 11.8+ and ROCm (AMD GPU)
- `"fp8_e5m2"`: Supported on CUDA 11.8+
```

### Ef54934c2952f9f0e01ac3b8e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
Quantization of models with FP8 allows for a 2x reduction in model memory requirements and up to a 1.6x improvement in throughput with minimal impact on accuracy.
```

## official-004-3:hybrid_rerank:retrieved

vLLM v0.10.2：在Ampere部署FP8模型时把激活也按8bit支持处理，应先核对哪个限制？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "97d3fc12-36ab-48a8-9f82-1365a93cd771",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：在Ampere部署FP8模型时把激活也按8bit支持处理，应先核对哪个限制？",
      "hits": 0,
      "evidence": 8
    },
    {
      "step": "generate",
      "duration_ms": 1490.4,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ea69ba78298695847964cf47f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L54-L56

```text
- `"auto"`: Uses the model's default "unquantized" data type
- `"fp8"` or `"fp8_e4m3"`: Supported on CUDA 11.8+ and ROCm (AMD GPU)
- `"fp8_e5m2"`: Supported on CUDA 11.8+
```

### Ee4f4fbccc9548d5e3f51da06

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L140-L150

```text
When running the model you must specify `kv_cache_dtype="fp8"` in order to enable the kv cache quantization and use the scales.

```python
from vllm import LLM, SamplingParams

sampling_params = SamplingParams(temperature=0.7, top_p=0.8)
llm = LLM(model="Llama-3.1-8B-Instruct-FP8-KV", kv_cache_dtype="fp8")
prompt = "London is the capital of"
out = llm.generate(prompt, sampling_params)[0].outputs[0].text
print(out)
```
```

### E707fd541c52eb73c2ed6c6d8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

### Eb1696b36d266157a207a2b9d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L159-L184

```text
```yaml
...
spec:
  containers:
    - name: vllm
      image: vllm/vllm-openai
      securityContext:
        capabilities:
          add: ["IPC_LOCK"]
      volumeMounts:
        - mountPath: /dev/shm
          name: dshm
      resources:
        limits:
          nvidia.com/gpu: 8
        requests:
          nvidia.com/gpu: 8
  volumes:
    - name: dshm
      emptyDir:
        medium: Memory
...
```
```

### E5858c0b6aa2464dc1072738e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
It supports other [quantization strategies (INT8/FP8)](https://github.com/sgl-project/sglang/blob/v0.3.6/python/sglang/srt/server_args.py#L671) as well.
- To enable fp8 weight quantization, add `--quantization fp8` on a fp16 checkpoint or directly load a fp8 checkpoint without specifying any arguments.
- To enable fp8 kv cache quantization, add `--kv-cache-dtype fp8_e5m2`.
```

### Ef54934c2952f9f0e01ac3b8e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
Quantization of models with FP8 allows for a 2x reduction in model memory requirements and up to a 1.6x improvement in throughput with minimal impact on accuracy.
```

### E5b09769c743f5aeb7b751318

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L159-L184

```text
!!
! tip "Confirm GPUDirect RDMA operation"
To confirm your InfiniBand card is using GPUDirect RDMA, run vLLM with detailed NCCL logs: `NCCL_DEBUG=TRACE vllm serve ...`.
```

### E0378d6a07be801542c20d2ae

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
For more details, please refer to [PyTorch official documentation](https://pytorch.org/tutorials/recipes/torch_compile_caching_tutorial.html) and [Enabling cache for torch.compile](https://docs.sglang.ai/backend/hyperparameter_tuning.html#enabling-cache-for-torch-compile).
- To enable torchao quantization, add `--torchao-config int4wo-128`.
```

## official-004-4:oracle:oracle

vLLM v0.10.2：先界定vLLM Ampere FP8支持的精度组合，再判断能否把它照搬到SGLang AMD DeepSeekV3，应核对PR中的哪种FP8格式？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。；Ampere的W8A16不是通用W8A8保证；AMD DeepSeekV3修复另涉及e4m3fnuz，需按硬件和模型核验。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "e3fd11f8-acd3-47f9-8389-a8144f5f1864",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：先界定vLLM Ampere FP8支持的精度组合，再判断能否把它照搬到SGLang AMD DeepSeekV3，应核对PR中的哪种FP8格式？",
      "hits": 0,
      "evidence": 2
    },
    {
      "step": "generate",
      "duration_ms": 1307.9,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ef799598e9c44e1e80614ed21

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/quantization/fp8.md

```text
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

### Ebcf2b7523b37b4477e9b7927

https://github.com/sgl-project/sglang/pull/2601

```text
Add proper fix for AMD FP8 ```e4m3fnuz``` to support DeepseekV3 FP8 model
```

## official-004-4:bm25:retrieved

vLLM v0.10.2：先界定vLLM Ampere FP8支持的精度组合，再判断能否把它照搬到SGLang AMD DeepSeekV3，应核对PR中的哪种FP8格式？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。；Ampere的W8A16不是通用W8A8保证；AMD DeepSeekV3修复另涉及e4m3fnuz，需按硬件和模型核验。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "09045372-241d-4539-8252-b81babfaa75a",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：先界定vLLM Ampere FP8支持的精度组合，再判断能否把它照搬到SGLang AMD DeepSeekV3，应核对PR中的哪种FP8格式？",
      "hits": 0,
      "evidence": 8
    },
    {
      "step": "generate",
      "duration_ms": 1317.1,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ec195863d548a6b5e424b535a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L5-L7

```text
## Motivation
- Support DeepseekV3 on AMD Instinct MI300X GPU
<!-- Explain the purpose of this PR and the goals it aims to achieve. -->
```

### E870326793d056a107a5a1672

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L8-L11

```text
## Modifications
- Add proper fix for AMD FP8 ```e4m3fnuz``` to support DeepseekV3 FP8 model
- Bypass ```FlashInfer backend bmm_fp8``` to cast FP8 to BF16 in MLA
- Add AMD ```triton stages``` config
```

### E707fd541c52eb73c2ed6c6d8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

### E4e1044238dc894ec734a0d3c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L12-L19

```text
### TODO
- [x] amd base image testing https://github.com/sgl-project/sglang/pull/2692
- [x] sgl-kernel add amd backend https://github.com/sgl-project/sglang/pull/3287
- [x] DeepseekV3 triton MOE config optimization https://github.com/sgl-project/sglang/pull/3146
```

### E304d729ae809670c7310aad7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L15-L17

```text
!!! note
    FP8 computation is supported on NVIDIA GPUs with compute capability > 8.9 (Ada Lovelace, Hopper).
    FP8 models will run on compute capability > 8.0 (Ampere) as weight-only W8A16, utilizing FP8 Marlin.
```

### Ef54934c2952f9f0e01ac3b8e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
Quantization of models with FP8 allows for a 2x reduction in model memory requirements and up to a 1.6x improvement in throughput with minimal impact on accuracy.
```

### Ef875130d2ac8c37dc2ed476c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L12-L19

```text
- [ ] batch mm for FP8 optimization on rocm
- [x] composable kernel block gemm https://github.com/sgl-project/sglang/pull/4075
```

### Eca92fdaba7b018d8ee335a73

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L12-L19

```text
- [x] ep moe
<!
-- Describe the changes made in this PR.
-->
```

## official-004-4:dense:retrieved

vLLM v0.10.2：先界定vLLM Ampere FP8支持的精度组合，再判断能否把它照搬到SGLang AMD DeepSeekV3，应核对PR中的哪种FP8格式？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。；Ampere的W8A16不是通用W8A8保证；AMD DeepSeekV3修复另涉及e4m3fnuz，需按硬件和模型核验。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "3a1ba79b-163b-4e20-bd77-06262fb85099",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：先界定vLLM Ampere FP8支持的精度组合，再判断能否把它照搬到SGLang AMD DeepSeekV3，应核对PR中的哪种FP8格式？",
      "hits": 0,
      "evidence": 10
    },
    {
      "step": "generate",
      "duration_ms": 1332.8,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ef875130d2ac8c37dc2ed476c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L12-L19

```text
- [ ] batch mm for FP8 optimization on rocm
- [x] composable kernel block gemm https://github.com/sgl-project/sglang/pull/4075
```

### E870326793d056a107a5a1672

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L8-L11

```text
## Modifications
- Add proper fix for AMD FP8 ```e4m3fnuz``` to support DeepseekV3 FP8 model
- Bypass ```FlashInfer backend bmm_fp8``` to cast FP8 to BF16 in MLA
- Add AMD ```triton stages``` config
```

### Ea69ba78298695847964cf47f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L54-L56

```text
- `"auto"`: Uses the model's default "unquantized" data type
- `"fp8"` or `"fp8_e4m3"`: Supported on CUDA 11.8+ and ROCm (AMD GPU)
- `"fp8_e5m2"`: Supported on CUDA 11.8+
```

### E684706db09e2eda820aef950

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L283-L322

```text
```cpp
for (int mask = WARP_SIZE / 2; mask >= THREAD_GROUP_SIZE; mask /= 2) {
    qk_max = fmaxf(qk_max, VLLM_SHFL_XOR_SYNC(qk_max, mask));
}

if (lane == 0) {
    red_smem[warp_idx] = qk_max;
}
```
Then we need to get the reduced `qk_max` across each warp.
```

### E707fd541c52eb73c2ed6c6d8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

### E4e1044238dc894ec734a0d3c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L12-L19

```text
### TODO
- [x] amd base image testing https://github.com/sgl-project/sglang/pull/2692
- [x] sgl-kernel add amd backend https://github.com/sgl-project/sglang/pull/3287
- [x] DeepseekV3 triton MOE config optimization https://github.com/sgl-project/sglang/pull/3146
```

### Eca92fdaba7b018d8ee335a73

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L12-L19

```text
- [x] ep moe
<!
-- Describe the changes made in this PR.
-->
```

### Eaeb654651008cc2aed64d739

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L283-L322

```text
thread group.
```cpp
if (thread_group_offset == 0) {
    const bool mask = token_idx >= context_len;
    logits[token_idx - start_token_idx] = mask ? 0.f : qk;
    qk_max = mask ? qk_max : fmaxf(qk_max, qk);
}
```
Please note that the `logits` here is on shared memory, so each
thread group will set the fields for its own assigned context tokens.
Overall, the size of logits should be number of context tokens.
```

### Ea75b4f110082beadf7adb12e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L283-L322

```text
The main
idea is to make threads in warp to communicate with each other and
get the final max `qk` .
```cpp
for (int mask = NUM_WARPS / 2; mask >= 1; mask /= 2) {
    qk_max = fmaxf(qk_max, VLLM_SHFL_XOR_SYNC(qk_max, mask));
}
qk_max = VLLM_SHFL_SYNC(qk_max, 0);
```
```

### Ed654f471b8473eb9e647bc78

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L283-L322

```text
store the normalized softmax result).
Also we can compare and collect
the `qk_max` for all `qk`s that are calculated by current
```

## official-004-4:hybrid:retrieved

vLLM v0.10.2：先界定vLLM Ampere FP8支持的精度组合，再判断能否把它照搬到SGLang AMD DeepSeekV3，应核对PR中的哪种FP8格式？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。；Ampere的W8A16不是通用W8A8保证；AMD DeepSeekV3修复另涉及e4m3fnuz，需按硬件和模型核验。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "1c947635-505d-4de7-9bf1-d88dd760e921",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：先界定vLLM Ampere FP8支持的精度组合，再判断能否把它照搬到SGLang AMD DeepSeekV3，应核对PR中的哪种FP8格式？",
      "hits": 0,
      "evidence": 8
    },
    {
      "step": "generate",
      "duration_ms": 1316.8,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E870326793d056a107a5a1672

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L8-L11

```text
## Modifications
- Add proper fix for AMD FP8 ```e4m3fnuz``` to support DeepseekV3 FP8 model
- Bypass ```FlashInfer backend bmm_fp8``` to cast FP8 to BF16 in MLA
- Add AMD ```triton stages``` config
```

### E707fd541c52eb73c2ed6c6d8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
# FP8 W8A8
vLLM supports FP8 (8-bit floating point) weight and activation quantization using hardware acceleration on GPUs such as Nvidia H100 and AMD MI300x.
Currently, only Hopper and Ada Lovelace GPUs are officially supported for W8A8.
Ampere GPUs are supported for W8A16 (weight-only FP8) utilizing Marlin kernels.
```

### Ea69ba78298695847964cf47f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L54-L56

```text
- `"auto"`: Uses the model's default "unquantized" data type
- `"fp8"` or `"fp8_e4m3"`: Supported on CUDA 11.8+ and ROCm (AMD GPU)
- `"fp8_e5m2"`: Supported on CUDA 11.8+
```

### Ef875130d2ac8c37dc2ed476c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L12-L19

```text
- [ ] batch mm for FP8 optimization on rocm
- [x] composable kernel block gemm https://github.com/sgl-project/sglang/pull/4075
```

### E304d729ae809670c7310aad7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L15-L17

```text
!!! note
    FP8 computation is supported on NVIDIA GPUs with compute capability > 8.9 (Ada Lovelace, Hopper).
    FP8 models will run on compute capability > 8.0 (Ampere) as weight-only W8A16, utilizing FP8 Marlin.
```

### Ef54934c2952f9f0e01ac3b8e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L1-L6

```text
Quantization of models with FP8 allows for a 2x reduction in model memory requirements and up to a 1.6x improvement in throughput with minimal impact on accuracy.
```

### E4e1044238dc894ec734a0d3c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L12-L19

```text
### TODO
- [x] amd base image testing https://github.com/sgl-project/sglang/pull/2692
- [x] sgl-kernel add amd backend https://github.com/sgl-project/sglang/pull/3287
- [x] DeepseekV3 triton MOE config optimization https://github.com/sgl-project/sglang/pull/3146
```

### Eca92fdaba7b018d8ee335a73

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L12-L19

```text
- [x] ep moe
<!
-- Describe the changes made in this PR.
-->
```

## official-004-4:hybrid_rerank:retrieved

vLLM v0.10.2：先界定vLLM Ampere FP8支持的精度组合，再判断能否把它照搬到SGLang AMD DeepSeekV3，应核对PR中的哪种FP8格式？

必要要点：Ampere的该支持是使用Marlin的W8A16权重量化。；Ampere的W8A16不是通用W8A8保证；AMD DeepSeekV3修复另涉及e4m3fnuz，需按硬件和模型核验。

禁止误读：Ampere文档中的该支持等同于W8A8。

```json
{
  "conversation_id": "c1ecbb44-f95e-4541-b03f-b19d2b6b297e",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：先界定vLLM Ampere FP8支持的精度组合，再判断能否把它照搬到SGLang AMD DeepSeekV3，应核对PR中的哪种FP8格式？",
      "hits": 0,
      "evidence": 7
    },
    {
      "step": "generate",
      "duration_ms": 1666.9,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ea69ba78298695847964cf47f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L54-L56

```text
- `"auto"`: Uses the model's default "unquantized" data type
- `"fp8"` or `"fp8_e4m3"`: Supported on CUDA 11.8+ and ROCm (AMD GPU)
- `"fp8_e5m2"`: Supported on CUDA 11.8+
```

### E904c381bf1f5f1779dedef72

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
This action will ignore the Hugging Face config's quantization settings.
For instance, with `neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic`, if you execute with `--quantization w8a8_fp8`, the system will use the `W8A8Fp8Config` from SGLang to invoke the sgl-kernel, rather than the `CompressedTensorsConfig` for vLLM kernels.
```

### E870326793d056a107a5a1672

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L8-L11

```text
## Modifications
- Add proper fix for AMD FP8 ```e4m3fnuz``` to support DeepseekV3 FP8 model
- Bypass ```FlashInfer backend bmm_fp8``` to cast FP8 to BF16 in MLA
- Add AMD ```triton stages``` config
```

### Ee4f4fbccc9548d5e3f51da06

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L140-L150

```text
When running the model you must specify `kv_cache_dtype="fp8"` in order to enable the kv cache quantization and use the scales.

```python
from vllm import LLM, SamplingParams

sampling_params = SamplingParams(temperature=0.7, top_p=0.8)
llm = LLM(model="Llama-3.1-8B-Instruct-FP8-KV", kv_cache_dtype="fp8")
prompt = "London is the capital of"
out = llm.generate(prompt, sampling_params)[0].outputs[0].text
print(out)
```
```

### Ec4fa51a2f0c2ad3e9e166b09

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L116-L129

```text
Alternatively, you can set `tensor_parallel_size` to the total number of GPUs in the cluster:
```bash
vllm serve /path/to/the/model/in/the/container \
     --tensor-parallel-size 16
```
```

### E74b994b5ce8fbeb1f2a0b11e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4 \
    --port 30000 --host 0.0.0.0
```
Take note, if your model is **per-channel quantized (INT8 or FP8) with per-token dynamic quantization activation**, you can opt to include `--quantization w8a8_int8` or `--quantization w8a8_fp8` to invoke the corresponding CUTLASS int8_kernel or fp8_kernel in sgl-kernel.
```

### Ef6c630563d458d3c5beb00ac

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic \
    --quantization w8a8_fp8 \
    --port 30000 --host 0.0.0.0
```
```

## official-005-1:oracle:oracle

vLLM v0.10.2：KV空间不足导致抢占后，请求如何恢复执行？

必要要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "c706eeb5-a1c8-4289-9311-cf4a71e3b136",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：KV空间不足导致抢占后，请求如何恢复执行？",
      "hits": 0,
      "evidence": 1
    },
    {
      "step": "generate",
      "duration_ms": 1314.0,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ef7dce1912d553a4fa7f91978

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/configuration/optimization.md

```text
Preempted requests are recomputed when sufficient KV cache space becomes
available again.
```

## official-005-1:bm25:retrieved

vLLM v0.10.2：KV空间不足导致抢占后，请求如何恢复执行？

必要要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "1a10bf60-a244-4850-97d6-752ea1a717d9",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：KV空间不足导致抢占后，请求如何恢复执行？",
      "hits": 0,
      "evidence": 10
    },
    {
      "step": "generate",
      "duration_ms": 1315.3,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E01cd7f8528e50b0d7013c1be

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L14-L20

```text
## Speculating with a draft model

The following code configures vLLM in an offline mode to use speculative decoding with a draft model, speculating 5 tokens at a time.

!!! warning
    In vllm v0.10.0, speculative decoding with a draft model is not supported.
    If you use the following code, you will get a `NotImplementedError`.
```

### E05fa3ecae9f31c8965f45edd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
\
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_connector":"SharedStorageConnector","kv_role":"kv_producer","kv_rank":0,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}' &

# decoding instance, which is the KV consumer
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_NAME \
    --port 7204 \
    --gpu-memory-utilization 0.8 \
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_co
```

### E19f9888ee3de3dd559ce25a2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L8-L19

```text
## Preemption
Due to the auto-regressive nature of transformer architecture, there are times when KV cache space is insufficient to handle all batched requests.
In such cases, vLLM can preempt requests to free up KV cache space for other requests.
Preempted requests are recomputed when sufficient KV cache space becomes
```

### E0a0f6849d62f7169de1c0b5b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-pr-21611.md#L9-L10

```text
Support V1 PD multimodal input without wrongly reusing kv (issue 21175)
https://github.com/vllm-project/vllm/issues/21175
```

### E20853351d30eab09ebf69f4e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L100-L117

```text
## Data Structure
The prefix caching in vLLM v1 is implemented in the KV cache manager.
The basic building block is the “Block” data class (simplified):
```

### E76386a2d669e1a99e5aa70cf

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
```python
MODEL_NAME=models/Qwen2.5-VL-3B-Instruct/   # model path here

# a function that waits vLLM server to start
wait_for_server() {
  local port=$1
  timeout 12000 bash -c "
    until curl -s localhost:${port}/v1/chat/completions > /dev/null; do
      sleep 1
    done" && return 0 || return 1
}

# prefilling instance, which is the KV producer
CUDA_VISIBLE_DEVICES=0 vllm serve $MODEL_NAME \
    --port 7104 \
    --gpu-memory-utilization 0.8 
```

### Ed1e1300af58c1464e44b128e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
nnector":"SharedStorageConnector","kv_role":"kv_consumer","kv_rank":1,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}'  &

# wait until prefill and decode instances are ready
wait_for_server 7104
wait_for_server 7204

# launch the proxy server
python3 examples/online_serving/disaggregated_serving/disagg_proxy_demo.py  \
    --model $MODEL_NAME  \
    --prefill localhost:7104   \
    --decode localh
```

### Eca7787c4400bc8f084b7feb4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
To start the PD instances:
```

### Ef9dcf75b0d93b6dcd5172b33

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
ost:7204   \
    --port 9774
```
```

### E9582c677de8671c062989a9b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L100-L117

```text
ock"] = None
```
```

## official-005-1:dense:retrieved

vLLM v0.10.2：KV空间不足导致抢占后，请求如何恢复执行？

必要要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "bce5e786-acbf-4e40-ac48-998fab5c9868",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：KV空间不足导致抢占后，请求如何恢复执行？",
      "hits": 0,
      "evidence": 8
    },
    {
      "step": "generate",
      "duration_ms": 1515.2,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E20853351d30eab09ebf69f4e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L100-L117

```text
## Data Structure
The prefix caching in vLLM v1 is implemented in the KV cache manager.
The basic building block is the “Block” data class (simplified):
```

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### Ef433a588f6abcfc5b1bd9c20

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-conserving_memory.md#L85-L90

```text
## Adjust cache size

If you run out of CPU RAM, try the following options:

- (Multi-modal models only) you can set the size of multi-modal cache by setting `mm_processor_cache_gb` engine argument (default 4 GiB).
- (CPU backend only) you can set the size of KV cache using `VLLM_CPU_KVCACHE_SPACE` environment variable (default 4 GiB).
```

### E5b3677f3140911d7ff3124ab

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L126-L126

```text
As a result, we will have the following components when the KV cache manager is initialized:
```

### E2dc8648e7eb8fb1cf6957293

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-distributed_troubleshooting.md#L9-L11

```text
Ensure that vLLM and Ray use the same IP address by setting `VLLM_HOST_IP` in <gh-file:examples/online_serving/run_cluster.sh> (with a different value on each node).
Use `ray status` and `ray list nodes` to verify the chosen IP address.
For more information, see <gh-issue:7815>.
```

### E4292c5e89c78d6dd6b526c4d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L100-L117

```text
```python
class KVCacheBlock:
    # The block ID (immutable)
    block_id: int
    # The block hash (will be assigned when the block is full,
    # and will be reset when the block is evicted).
    block_hash: BlockHash
    # The number of requests using this block now.
    ref_cnt: int

    # The pointers to form a doubly linked list for the free queue.
    prev_free_block: Optional["KVCacheBlock"] = None
    next_free_block: Optional["KVCacheBl
```

### E9582c677de8671c062989a9b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L100-L117

```text
ock"] = None
```
```

### E2c2fa52d577e24ef01b362a6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-distributed_troubleshooting.md#L9-L11

```text
## No available node types can fulfill resource request
The error message `Error: No available node types can fulfill resource request` can appear even when the cluster has enough GPUs.
The issue often occurs when nodes have multiple IP addresses and vLLM can't select the correct one.
```

## official-005-1:hybrid:retrieved

vLLM v0.10.2：KV空间不足导致抢占后，请求如何恢复执行？

必要要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "9b3fdd8d-cae1-4c6a-b60b-9cd923d72f9e",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：KV空间不足导致抢占后，请求如何恢复执行？",
      "hits": 0,
      "evidence": 11
    },
    {
      "step": "generate",
      "duration_ms": 2137.3,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E20853351d30eab09ebf69f4e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L100-L117

```text
## Data Structure
The prefix caching in vLLM v1 is implemented in the KV cache manager.
The basic building block is the “Block” data class (simplified):
```

### E19f9888ee3de3dd559ce25a2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L8-L19

```text
## Preemption
Due to the auto-regressive nature of transformer architecture, there are times when KV cache space is insufficient to handle all batched requests.
In such cases, vLLM can preempt requests to free up KV cache space for other requests.
Preempted requests are recomputed when sufficient KV cache space becomes
```

### E01cd7f8528e50b0d7013c1be

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L14-L20

```text
## Speculating with a draft model

The following code configures vLLM in an offline mode to use speculative decoding with a draft model, speculating 5 tokens at a time.

!!! warning
    In vllm v0.10.0, speculative decoding with a draft model is not supported.
    If you use the following code, you will get a `NotImplementedError`.
```

### E1463499a732287269ea92129

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
To improve privacy in shared environments, vLLM supports isolating prefix cache reuse through optional per-request salting.
By including a `cache_salt` in the request, this value is injected into the hash of the first block, ensuring that only requests with the same salt can reuse cached KV blocks.
This prevents timing-based attacks where an adversary could infer cached content by observing latency differences.
```

### E9b447f23a80b6e3cfb4e96a0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L20-L22

```text
### Performance Impact

The current FP8 KV cache implementation primarily benefits throughput by allowing approximately double the amount of space for KV cache allocation. This enables either:
```

### E4292c5e89c78d6dd6b526c4d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L100-L117

```text
```python
class KVCacheBlock:
    # The block ID (immutable)
    block_id: int
    # The block hash (will be assigned when the block is full,
    # and will be reset when the block is evicted).
    block_hash: BlockHash
    # The number of requests using this block now.
    ref_cnt: int

    # The pointers to form a doubly linked list for the free queue.
    prev_free_block: Optional["KVCacheBlock"] = None
    next_free_block: Optional["KVCacheBl
```

### E9582c677de8671c062989a9b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L100-L117

```text
ock"] = None
```
```

### Ea2f195be08e9d1cc2daec84a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L8-L19

```text
available again.
When this occurs, you may see the following warning:
```text
WARNING 05-09 00:49:33 scheduler.py:1057 Sequence group 0 is preempted by PreemptionMode.RECOMPUTE mode because there is not enough KV cache space. This can affect the end-to-end performance. Increase gpu_memory_utilization or tensor_parallel_size to provide more KV cache memory. total_cumulative_preemption_cnt=1
```
```

### Ef90577f9a3333a77be2b88d1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L8-L19

```text
While this mechanism ensures system robustness, preemption and recomputation can adversely affect end-to-end latency.
If you frequently encounter preemptions, consider the following actions:
```

### E5dda40ed0c5092aadb08696f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
In the rest of this document, we first introduce the data structure used for prefix caching in vLLM v1, followed by the prefix caching workflow of major KV cache operators (e.g., allocate, append, free, eviction).
Finally, we use an example to illustrate the end to end prefix caching workflow.
**Cache Isolation for Security**
```

### E9179e0166553b73ef2a10c4b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
!!
! note
```

## official-005-1:hybrid_rerank:retrieved

vLLM v0.10.2：KV空间不足导致抢占后，请求如何恢复执行？

必要要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "a9c78404-744e-4c90-8ce3-967ad96eba9a",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：KV空间不足导致抢占后，请求如何恢复执行？",
      "hits": 0,
      "evidence": 8
    },
    {
      "step": "generate",
      "duration_ms": 1521.4,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E19f9888ee3de3dd559ce25a2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L8-L19

```text
## Preemption
Due to the auto-regressive nature of transformer architecture, there are times when KV cache space is insufficient to handle all batched requests.
In such cases, vLLM can preempt requests to free up KV cache space for other requests.
Preempted requests are recomputed when sufficient KV cache space becomes
```

### E1463499a732287269ea92129

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
To improve privacy in shared environments, vLLM supports isolating prefix cache reuse through optional per-request salting.
By including a `cache_salt` in the request, this value is injected into the hash of the first block, ensuring that only requests with the same salt can reuse cached KV blocks.
This prevents timing-based attacks where an adversary could infer cached content by observing latency differences.
```

### E854176531e0cf52e426febb2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L21-L24

```text
- Increase `gpu_memory_utilization`.
vLLM pre-allocates GPU cache using this percentage of memory.
By increasing utilization, you can provide more KV cache space.
- Decrease `max_num_seqs` or `max_num_batched_tokens`.
This reduces the number of concurrent requests in a batch, thereby requiring less KV cache space.
- Increase `tensor_parallel_size`.
```

### Ebf13eeb5c9f8d5c8b8e51b4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
```bash
  --kv-transfer-config '{"kv_connector":"MultiConnector","kv_role":"kv_both","kv_connector_extra_config":{"connectors":[{"kv_connector":"NixlConnector","kv_role":"kv_both"},{"kv_connector":"SharedStorageConnector","kv_role":"kv_both","kv_connector_extra_config":{"shared_storage_path":"local_storage"}}]}}'
  ```
```

### Ee4f4fbccc9548d5e3f51da06

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L140-L150

```text
When running the model you must specify `kv_cache_dtype="fp8"` in order to enable the kv cache quantization and use the scales.

```python
from vllm import LLM, SamplingParams

sampling_params = SamplingParams(temperature=0.7, top_p=0.8)
llm = LLM(model="Llama-3.1-8B-Instruct-FP8-KV", kv_cache_dtype="fp8")
prompt = "London is the capital of"
out = llm.generate(prompt, sampling_params)[0].outputs[0].text
print(out)
```
```

### Ea2f195be08e9d1cc2daec84a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L8-L19

```text
available again.
When this occurs, you may see the following warning:
```text
WARNING 05-09 00:49:33 scheduler.py:1057 Sequence group 0 is preempted by PreemptionMode.RECOMPUTE mode because there is not enough KV cache space. This can affect the end-to-end performance. Increase gpu_memory_utilization or tensor_parallel_size to provide more KV cache memory. total_cumulative_preemption_cnt=1
```
```

### Ef90577f9a3333a77be2b88d1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L8-L19

```text
While this mechanism ensures system robustness, preemption and recomputation can adversely affect end-to-end latency.
If you frequently encounter preemptions, consider the following actions:
```

### E9179e0166553b73ef2a10c4b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
!!
! note
Cache isolation is not supported in engine V0.
```

## official-005-2:oracle:oracle

vLLM v0.10.2：抢占是否意味着后续恢复完全不需要重算？

必要要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "231d47d5-8fda-4086-a700-102c03c58575",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：抢占是否意味着后续恢复完全不需要重算？",
      "hits": 0,
      "evidence": 1
    },
    {
      "step": "generate",
      "duration_ms": 1388.4,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ef7dce1912d553a4fa7f91978

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/configuration/optimization.md

```text
Preempted requests are recomputed when sufficient KV cache space becomes
available again.
```

## official-005-2:bm25:retrieved

vLLM v0.10.2：抢占是否意味着后续恢复完全不需要重算？

必要要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "ad1944f8-beb3-4f17-a766-c10e874c6fab",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：抢占是否意味着后续恢复完全不需要重算？",
      "hits": 0,
      "evidence": 9
    },
    {
      "step": "generate",
      "duration_ms": 1300.1,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E01cd7f8528e50b0d7013c1be

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L14-L20

```text
## Speculating with a draft model

The following code configures vLLM in an offline mode to use speculative decoding with a draft model, speculating 5 tokens at a time.

!!! warning
    In vllm v0.10.0, speculative decoding with a draft model is not supported.
    If you use the following code, you will get a `NotImplementedError`.
```

### E53a04ce20e63602ad4637565

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L33-L33

```text
3. Evaluating accuracy in vLLM
```

### Ecf2dd228b34ec7b53985eff4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L288-L293

```text
## Resources for vLLM contributors
- [A Hacker's Guide to Speculative Decoding in vLLM](https://www.youtube.com/watch?
```

### E9a5dde88f838a11ba9dccd64

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
## Use vLLM's Official Docker Image
vLLM offers an official Docker image for deployment.
The image can be used to run OpenAI compatible server and is available on Docker Hub as [vllm/vllm-openai](https://hub.docker.com/r/vllm/vllm-openai/tags).
```

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### E16b83f578a404c7f80c61a32

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L288-L293

```text
v=9wNAgpX6z_4)
- [What is Lookahead Scheduling in vLLM?
](https://docs.google.com/document/d/1Z9TvqzzBPnh5WHcRwjvK2UEeFeq5zMZb5mFE8jR0HCs/edit#heading=h.1fjfb0donq5a)
- [Information on batch expansion](https://docs.google.com/document/d/1T-JaS2T1NRfdP51qzqpyakoCXxSXTtORppiwaj5asxA/edit#heading=h.kk7dq05lc6q8)
- [Dynamic speculative decoding](gh-issue:4565)
```

### E129c5629e0e269f5141eaa20

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model Qwen/Qwen3-0.6B
```
This image can also be used with other container engines such as [Podman](https://podman.io/).
```

### E76dca9b42c02be4cdcff9c3e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
podman run --device nvidia.com/gpu=all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
  -p 8000:8000 \
  --ipc=host \
  docker.io/vllm/vllm-openai:latest \
  --model Qwen/Qwen3-0.6B
```
You can add any other [engine-args](../configuration/engine_args.md) you need after the image tag (`vllm/vllm-openai:latest`).
```

### Ec94bd3c0efd3b0755001340f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
!!
! note
You can either use the `ipc=host` flag or `--shm-size` flag to allow the
container to access the host's shared memory.
vLLM uses PyTorch, which uses shared
memory to share data between processes under the hood, particularly for tensor parallel inference.
```

## official-005-2:dense:retrieved

vLLM v0.10.2：抢占是否意味着后续恢复完全不需要重算？

必要要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "b9fb980d-dd44-485e-adde-bad63fdb15c5",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：抢占是否意味着后续恢复完全不需要重算？",
      "hits": 0,
      "evidence": 11
    },
    {
      "step": "generate",
      "duration_ms": 1315.2,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ef4b53048d437c20a01dd2210

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L63-L63

```text
Now every process in vLLM will have a corresponding connector. Specifically, we have:
```

### E20853351d30eab09ebf69f4e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L100-L117

```text
## Data Structure
The prefix caching in vLLM v1 is implemented in the KV cache manager.
The basic building block is the “Block” data class (simplified):
```

### Ed6d39e475341f4ab01dc6509

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L50-L51

```text
### To reproduce:
vllm version: v0.9.2
```

### E817b770fdd612fe5c92ce442

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
same request across runs.
For more details, see the FAQ section
titled *Can the output of a prompt vary across runs in vLLM?
```

### Ea538466a6d9a83baf54eb455

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L178-L192

```text
In v0, when detecting block 3 is duplicated, we free block 3 and let Request 2 use block 1 instead, so its block table becomes `[0, 1]` in Time 1.
However, the block table in vLLM v1 is append-only, meaning that changing the block table from `[0, 3]` to `[0, 1]` is not allowed.
As a result, we will have duplicated blocks for the hash key E-H.
This duplication will be eliminated when the request is freed.
```

### E4292c5e89c78d6dd6b526c4d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L100-L117

```text
```python
class KVCacheBlock:
    # The block ID (immutable)
    block_id: int
    # The block hash (will be assigned when the block is full,
    # and will be reset when the block is evicted).
    block_hash: BlockHash
    # The number of requests using this block now.
    ref_cnt: int

    # The pointers to form a doubly linked list for the free queue.
    prev_free_block: Optional["KVCacheBlock"] = None
    next_free_block: Optional["KVCacheBl
```

### E9582c677de8671c062989a9b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L100-L117

```text
ock"] = None
```
```

### E9334c8ebd5003f269a8dbfa0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
3.
**vLLM Logprob Stability**
\- vLLM does not currently guarantee stable token log probabilities (logprobs).
This can result in different outputs for the
```

### E806a86f3d7c94ddceb889b00

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
* in the [FAQs](../usage/faq.md).
While vLLM strives to ensure losslessness in speculative decoding, variations in generated outputs with and without speculative decoding
can occur due to following factors:
- **Floating-Point Precision**: Differences in hardware numerical precision may lead to slight discrepancies in the output distribution.
```

### E1f8f4afd3342de899d5b77f5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
- **Batch Size and Numerical Stability**: Changes in batch size may cause variations in logprobs and output probabilities, potentially
due to non-deterministic behavior in batched operations or numerical instability.
```

### E5a09222d3c9ddb741403611b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
For mitigation strategies, please refer to the FAQ entry *Can the output of a prompt vary across runs in vLLM?
* in the [FAQs](../usage/faq.md).
```

## official-005-2:hybrid:retrieved

vLLM v0.10.2：抢占是否意味着后续恢复完全不需要重算？

必要要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "51d6bffc-1877-4c21-88d5-6d724bf56652",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：抢占是否意味着后续恢复完全不需要重算？",
      "hits": 0,
      "evidence": 11
    },
    {
      "step": "generate",
      "duration_ms": 1393.3,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### E817b770fdd612fe5c92ce442

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
same request across runs.
For more details, see the FAQ section
titled *Can the output of a prompt vary across runs in vLLM?
```

### Ed6d39e475341f4ab01dc6509

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L50-L51

```text
### To reproduce:
vllm version: v0.9.2
```

### Eadfaab7e8dc33ac661f2f94c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L165-L168

```text
You can either install existing plugins or implement your own.
By default, vLLM comes with a [resolver plugin to load LoRA adapters from a local directory.](https://github.com/vllm-project/vllm/tree/main/vllm/plugins/lora_resolvers)
To enable this resolver, set `VLLM_ALLOW_RUNTIME_LORA_UPDATING` to True, set `VLLM_PLUGINS` to include `lora_filesystem_resolver`, and then set `VLLM_LORA_RESOLVER_CACHE_DIR` to a local directory.
```

### Eb2a0f8bf7ceabe619bc48d27

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

```text
If you are running the container under a different user, you may need to first change the permissions of the library (and all the parent directories) to allow the user to access it, then run vLLM with environment variable `VLLM_NCCL_SO_PATH=/root/.config/vllm/nccl/cu12/libnccl.so.2.18.1` .
```

### E9334c8ebd5003f269a8dbfa0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
3.
**vLLM Logprob Stability**
\- vLLM does not currently guarantee stable token log probabilities (logprobs).
This can result in different outputs for the
```

### E806a86f3d7c94ddceb889b00

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
* in the [FAQs](../usage/faq.md).
While vLLM strives to ensure losslessness in speculative decoding, variations in generated outputs with and without speculative decoding
can occur due to following factors:
- **Floating-Point Precision**: Differences in hardware numerical precision may lead to slight discrepancies in the output distribution.
```

### E1f8f4afd3342de899d5b77f5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
- **Batch Size and Numerical Stability**: Changes in batch size may cause variations in logprobs and output probabilities, potentially
due to non-deterministic behavior in batched operations or numerical instability.
```

### E5a09222d3c9ddb741403611b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
For mitigation strategies, please refer to the FAQ entry *Can the output of a prompt vary across runs in vLLM?
* in the [FAQs](../usage/faq.md).
```

### E062010e52f86dd5d0e443c52

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L165-L168

```text
When vLLM receives a request using a LoRA adapter `foobar`,
it will first look in the local directory for a directory `foobar`, and attempt to load the contents of that directory as a LoRA adapter.
If successful, the request will complete as normal and
that adapter will then be available for normal use on the server.
```

### Ed297b4db013cea35b4dec16a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L123-L138

```text
!!
! note
```

## official-005-2:hybrid_rerank:retrieved

vLLM v0.10.2：抢占是否意味着后续恢复完全不需要重算？

必要要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "ccd3e8e0-35c3-446c-baae-90008f1cd5ed",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：抢占是否意味着后续恢复完全不需要重算？",
      "hits": 0,
      "evidence": 9
    },
    {
      "step": "generate",
      "duration_ms": 1473.3,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Eb81c406e8ea7ecad47e04367

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L28-L28

```text
In vLLM V1, the default preemption mode is `RECOMPUTE` rather than `SWAP`, as recomputation has lower overhead in the V1 architecture.
```

### Ed6d39e475341f4ab01dc6509

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L50-L51

```text
### To reproduce:
vllm version: v0.9.2
```

### E53a04ce20e63602ad4637565

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L33-L33

```text
3. Evaluating accuracy in vLLM
```

### E6d4d021c4614a53e07a1e696

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L109-L114

```text
All resources across the Ray cluster are visible to vLLM, so a single `vllm` command on a single node is sufficient.
```

### Ef8453fe21f4f381e4c4ca3fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L264-L272

```text
>   without it.
This verifies that vLLM's speculative decoding framework, when integrated with the vLLM forward pass and the vLLM rejection sampler,
>   provides a lossless guarantee.
Almost all of the tests in <gh-dir:tests/spec_decode/e2e>.
>   verify this property using [this assertion implementation](https://github.com/vllm-project/vllm/blob/b67ae00cdbbe1a58ffc8ff170f0c8d79044a684a/tests/spec_decode/e2e/conftest.py#L291)
```

### E64ba0faeed4527c66a3fa427

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L109-L114

```text
### Running vLLM on a Ray cluster
!
!!
tip
If Ray is running inside containers, run the commands in the remainder of this guide *inside the containers*, not on the host.
To open a shell inside a container, connect to a node and use `docker exec -it <container_name> /bin/bash`.
Once a Ray cluster is running, use vLLM as you would in a single-node setting.
```

### E147d26ecc078186f69049c06

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L264-L272

```text
[View Test Code](https://github.com/vllm-project/vllm/blob/47b65a550866c7ffbd076ecb74106714838ce7da/tests/samplers/test_rejection_sampler.py#L252)
> - **Greedy Sampling Equality**: Confirms that greedy sampling with speculative decoding matches greedy sampling
```

### E98d943a3f7e2ccaa47dc0926

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L264-L272

```text
> - **Rejection Sampler Convergence**: Ensures that samples from vLLM’s rejection sampler align with the target
>   distribution.
```

### E5859034c0e3b12d2ba362629

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L264-L272

```text
2.
**Algorithmic Losslessness**
\- vLLM’s implementation of speculative decoding is algorithmically validated to be lossless.
Key validation tests include:
```

## official-005-3:oracle:oracle

vLLM v0.10.2：并发过高出现preemption警告，应如何解释恢复阶段的额外计算？

必要要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "85a2f732-c59f-4bf2-a1b4-85af08b5b5f6",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：并发过高出现preemption警告，应如何解释恢复阶段的额外计算？",
      "hits": 0,
      "evidence": 1
    },
    {
      "step": "generate",
      "duration_ms": 1366.9,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ef7dce1912d553a4fa7f91978

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/configuration/optimization.md

```text
Preempted requests are recomputed when sufficient KV cache space becomes
available again.
```

## official-005-3:bm25:retrieved

vLLM v0.10.2：并发过高出现preemption警告，应如何解释恢复阶段的额外计算？

必要要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "f36a83d7-cd7c-41b3-a142-9516c67ad47e",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：并发过高出现preemption警告，应如何解释恢复阶段的额外计算？",
      "hits": 0,
      "evidence": 6
    },
    {
      "step": "generate",
      "duration_ms": 1282.3,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E727fbf7338b5fce226be101c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L26-L26

```text
You can monitor the number of preemption requests through Prometheus metrics exposed by vLLM. Additionally, you can log the cumulative number of preemption requests by setting `disable_log_stats=False`.
```

### Eb81c406e8ea7ecad47e04367

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L28-L28

```text
In vLLM V1, the default preemption mode is `RECOMPUTE` rather than `SWAP`, as recomputation has lower overhead in the V1 architecture.
```

### E19f9888ee3de3dd559ce25a2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L8-L19

```text
## Preemption
Due to the auto-regressive nature of transformer architecture, there are times when KV cache space is insufficient to handle all batched requests.
In such cases, vLLM can preempt requests to free up KV cache space for other requests.
Preempted requests are recomputed when sufficient KV cache space becomes
```

### E05e3e1be201a1552358a6c20

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L30-L30

```text
[](){ #chunked-prefill }
```

### Ef90577f9a3333a77be2b88d1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L8-L19

```text
While this mechanism ensures system robustness, preemption and recomputation can adversely affect end-to-end latency.
If you frequently encounter preemptions, consider the following actions:
```

### Ea2f195be08e9d1cc2daec84a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L8-L19

```text
available again.
When this occurs, you may see the following warning:
```text
WARNING 05-09 00:49:33 scheduler.py:1057 Sequence group 0 is preempted by PreemptionMode.RECOMPUTE mode because there is not enough KV cache space. This can affect the end-to-end performance. Increase gpu_memory_utilization or tensor_parallel_size to provide more KV cache memory. total_cumulative_preemption_cnt=1
```
```

## official-005-3:dense:retrieved

vLLM v0.10.2：并发过高出现preemption警告，应如何解释恢复阶段的额外计算？

必要要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "d7e11e1f-9bdf-41ac-9c95-f418be8a814c",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：并发过高出现preemption警告，应如何解释恢复阶段的额外计算？",
      "hits": 0,
      "evidence": 9
    },
    {
      "step": "generate",
      "duration_ms": 1363.0,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E727fbf7338b5fce226be101c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L26-L26

```text
You can monitor the number of preemption requests through Prometheus metrics exposed by vLLM. Additionally, you can log the cumulative number of preemption requests by setting `disable_log_stats=False`.
```

### E817b770fdd612fe5c92ce442

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
same request across runs.
For more details, see the FAQ section
titled *Can the output of a prompt vary across runs in vLLM?
```

### Eb81c406e8ea7ecad47e04367

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L28-L28

```text
In vLLM V1, the default preemption mode is `RECOMPUTE` rather than `SWAP`, as recomputation has lower overhead in the V1 architecture.
```

### Ed6d39e475341f4ab01dc6509

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L50-L51

```text
### To reproduce:
vllm version: v0.9.2
```

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### E9334c8ebd5003f269a8dbfa0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
3.
**vLLM Logprob Stability**
\- vLLM does not currently guarantee stable token log probabilities (logprobs).
This can result in different outputs for the
```

### E806a86f3d7c94ddceb889b00

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
* in the [FAQs](../usage/faq.md).
While vLLM strives to ensure losslessness in speculative decoding, variations in generated outputs with and without speculative decoding
can occur due to following factors:
- **Floating-Point Precision**: Differences in hardware numerical precision may lead to slight discrepancies in the output distribution.
```

### E1f8f4afd3342de899d5b77f5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
- **Batch Size and Numerical Stability**: Changes in batch size may cause variations in logprobs and output probabilities, potentially
due to non-deterministic behavior in batched operations or numerical instability.
```

### E5a09222d3c9ddb741403611b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
For mitigation strategies, please refer to the FAQ entry *Can the output of a prompt vary across runs in vLLM?
* in the [FAQs](../usage/faq.md).
```

## official-005-3:hybrid:retrieved

vLLM v0.10.2：并发过高出现preemption警告，应如何解释恢复阶段的额外计算？

必要要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "7e7925b9-50f8-4979-9b9a-a77ae27d11ef",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：并发过高出现preemption警告，应如何解释恢复阶段的额外计算？",
      "hits": 0,
      "evidence": 11
    },
    {
      "step": "generate",
      "duration_ms": 1600.5,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E727fbf7338b5fce226be101c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L26-L26

```text
You can monitor the number of preemption requests through Prometheus metrics exposed by vLLM. Additionally, you can log the cumulative number of preemption requests by setting `disable_log_stats=False`.
```

### Eb81c406e8ea7ecad47e04367

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L28-L28

```text
In vLLM V1, the default preemption mode is `RECOMPUTE` rather than `SWAP`, as recomputation has lower overhead in the V1 architecture.
```

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### Ef90577f9a3333a77be2b88d1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L8-L19

```text
While this mechanism ensures system robustness, preemption and recomputation can adversely affect end-to-end latency.
If you frequently encounter preemptions, consider the following actions:
```

### E817b770fdd612fe5c92ce442

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
same request across runs.
For more details, see the FAQ section
titled *Can the output of a prompt vary across runs in vLLM?
```

### Ea2f195be08e9d1cc2daec84a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L8-L19

```text
available again.
When this occurs, you may see the following warning:
```text
WARNING 05-09 00:49:33 scheduler.py:1057 Sequence group 0 is preempted by PreemptionMode.RECOMPUTE mode because there is not enough KV cache space. This can affect the end-to-end performance. Increase gpu_memory_utilization or tensor_parallel_size to provide more KV cache memory. total_cumulative_preemption_cnt=1
```
```

### E19f9888ee3de3dd559ce25a2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L8-L19

```text
## Preemption
Due to the auto-regressive nature of transformer architecture, there are times when KV cache space is insufficient to handle all batched requests.
In such cases, vLLM can preempt requests to free up KV cache space for other requests.
Preempted requests are recomputed when sufficient KV cache space becomes
```

### E9334c8ebd5003f269a8dbfa0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
3.
**vLLM Logprob Stability**
\- vLLM does not currently guarantee stable token log probabilities (logprobs).
This can result in different outputs for the
```

### E806a86f3d7c94ddceb889b00

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
* in the [FAQs](../usage/faq.md).
While vLLM strives to ensure losslessness in speculative decoding, variations in generated outputs with and without speculative decoding
can occur due to following factors:
- **Floating-Point Precision**: Differences in hardware numerical precision may lead to slight discrepancies in the output distribution.
```

### E1f8f4afd3342de899d5b77f5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
- **Batch Size and Numerical Stability**: Changes in batch size may cause variations in logprobs and output probabilities, potentially
due to non-deterministic behavior in batched operations or numerical instability.
```

### E5a09222d3c9ddb741403611b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
For mitigation strategies, please refer to the FAQ entry *Can the output of a prompt vary across runs in vLLM?
* in the [FAQs](../usage/faq.md).
```

## official-005-3:hybrid_rerank:retrieved

vLLM v0.10.2：并发过高出现preemption警告，应如何解释恢复阶段的额外计算？

必要要点：被抢占请求会在KV空间足够时重新计算。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "c3de28cd-3590-4dd5-a361-74b5e30b7822",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：并发过高出现preemption警告，应如何解释恢复阶段的额外计算？",
      "hits": 0,
      "evidence": 7
    },
    {
      "step": "generate",
      "duration_ms": 1368.0,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Eb81c406e8ea7ecad47e04367

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L28-L28

```text
In vLLM V1, the default preemption mode is `RECOMPUTE` rather than `SWAP`, as recomputation has lower overhead in the V1 architecture.
```

### Ea2f195be08e9d1cc2daec84a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L8-L19

```text
available again.
When this occurs, you may see the following warning:
```text
WARNING 05-09 00:49:33 scheduler.py:1057 Sequence group 0 is preempted by PreemptionMode.RECOMPUTE mode because there is not enough KV cache space. This can affect the end-to-end performance. Increase gpu_memory_utilization or tensor_parallel_size to provide more KV cache memory. total_cumulative_preemption_cnt=1
```
```

### E19f9888ee3de3dd559ce25a2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L8-L19

```text
## Preemption
Due to the auto-regressive nature of transformer architecture, there are times when KV cache space is insufficient to handle all batched requests.
In such cases, vLLM can preempt requests to free up KV cache space for other requests.
Preempted requests are recomputed when sufficient KV cache space becomes
```

### Ed6d39e475341f4ab01dc6509

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L50-L51

```text
### To reproduce:
vllm version: v0.9.2
```

### E9041556c305b4ab5a90588d1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L1-L12

```text
# Speculative Decoding
!
!!
warning
Please note that speculative decoding in vLLM is not yet optimized and does
not usually yield inter-token latency reductions for all prompt datasets or sampling parameters.
The work to optimize it is ongoing and can be followed here: <gh-issue:4630>
```

### Ef90577f9a3333a77be2b88d1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L8-L19

```text
While this mechanism ensures system robustness, preemption and recomputation can adversely affect end-to-end latency.
If you frequently encounter preemptions, consider the following actions:
```

### E12fd27572c9ae4f65a11fcfe

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L1-L12

```text
!
!!
warning
Currently, speculative decoding in vLLM is not compatible with pipeline parallelism.
This document shows how to use [Speculative Decoding](https://x.com/karpathy/status/1697318534555336961) with vLLM.
Speculative decoding is a technique which improves inter-token latency in memory-bound LLM inference.
```

## official-005-4:oracle:oracle

vLLM v0.10.2：先解释KV空间不足时抢占请求的恢复成本，再从内存优化指南找出将模型跨GPU拆分的参数。

必要要点：被抢占请求会在KV空间足够时重新计算。；KV抢占恢复需要重算；内存优化文档提供tensor_parallel_size将模型分布到多GPU的选项。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "de5a1209-aa8d-44c6-beb9-33804de3265c",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：先解释KV空间不足时抢占请求的恢复成本，再从内存优化指南找出将模型跨GPU拆分的参数。",
      "hits": 0,
      "evidence": 2
    },
    {
      "step": "generate",
      "duration_ms": 1427.2,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ef7dce1912d553a4fa7f91978

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/configuration/optimization.md

```text
Preempted requests are recomputed when sufficient KV cache space becomes
available again.
```

### E93f569b7fe486b9818d731c8

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/configuration/conserving_memory.md

```text
Tensor parallelism (`tensor_parallel_size` option) can be used to split the model across multiple GPUs.
```

## official-005-4:bm25:retrieved

vLLM v0.10.2：先解释KV空间不足时抢占请求的恢复成本，再从内存优化指南找出将模型跨GPU拆分的参数。

必要要点：被抢占请求会在KV空间足够时重新计算。；KV抢占恢复需要重算；内存优化文档提供tensor_parallel_size将模型分布到多GPU的选项。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "917db568-aa6b-4738-a11a-4842e36b9ec2",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：先解释KV空间不足时抢占请求的恢复成本，再从内存优化指南找出将模型跨GPU拆分的参数。",
      "hits": 0,
      "evidence": 8
    },
    {
      "step": "generate",
      "duration_ms": 1641.1,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E854176531e0cf52e426febb2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L21-L24

```text
- Increase `gpu_memory_utilization`.
vLLM pre-allocates GPU cache using this percentage of memory.
By increasing utilization, you can provide more KV cache space.
- Decrease `max_num_seqs` or `max_num_batched_tokens`.
This reduces the number of concurrent requests in a batch, thereby requiring less KV cache space.
- Increase `tensor_parallel_size`.
```

### E05fa3ecae9f31c8965f45edd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
\
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_connector":"SharedStorageConnector","kv_role":"kv_producer","kv_rank":0,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}' &

# decoding instance, which is the KV consumer
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_NAME \
    --port 7204 \
    --gpu-memory-utilization 0.8 \
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_co
```

### E2a987935049ba4a72d481f15

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L1-L3

```text
# Sleep Mode

vLLM's Sleep Mode allows you to temporarily release most GPU memory used by a model, including model weights and KV cache, without stopping the server or unloading the Docker container. This is especially useful for RLHF, training, or cost-saving scenarios where GPU resources need to be freed between inference workloads.
```

### Eb26664e6ed144816adcec24f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L15-L23

```text
```text
INFO 07-23 13:56:04 [kv_cache_utils.py:775] GPU KV cache size: 643,232 tokens
INFO 07-23 13:56:04 [kv_cache_utils.py:779] Maximum concurrency for 40,960 tokens per request: 15.70x
```
The `GPU KV cache size` line reports the total number of tokens that can be stored in the GPU KV cache at once.
```

### E01cd7f8528e50b0d7013c1be

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L14-L20

```text
## Speculating with a draft model

The following code configures vLLM in an offline mode to use speculative decoding with a draft model, speculating 5 tokens at a time.

!!! warning
    In vllm v0.10.0, speculative decoding with a draft model is not supported.
    If you use the following code, you will get a `NotImplementedError`.
```

### Ea9ce84adf4242fba791cc864

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L21-L24

```text
This shards model weights across GPUs, allowing each GPU to have more memory available for KV cache.
However, increasing this value may cause excessive synchronization overhead.
- Increase `pipeline_parallel_size`.
```

### Edb1580edf1a94751e80875de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L21-L24

```text
This distributes model layers across GPUs, reducing the memory needed for model weights on each GPU, indirectly leaving more memory available for KV cache.
However, increasing this value may cause latency penalties.
```

### Ed1e1300af58c1464e44b128e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
nnector":"SharedStorageConnector","kv_role":"kv_consumer","kv_rank":1,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}'  &

# wait until prefill and decode instances are ready
wait_for_server 7104
wait_for_server 7204

# launch the proxy server
```

## official-005-4:dense:retrieved

vLLM v0.10.2：先解释KV空间不足时抢占请求的恢复成本，再从内存优化指南找出将模型跨GPU拆分的参数。

必要要点：被抢占请求会在KV空间足够时重新计算。；KV抢占恢复需要重算；内存优化文档提供tensor_parallel_size将模型分布到多GPU的选项。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "5e0ba480-ff6d-4d5d-ae24-9e358d41d35e",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：先解释KV空间不足时抢占请求的恢复成本，再从内存优化指南找出将模型跨GPU拆分的参数。",
      "hits": 0,
      "evidence": 8
    },
    {
      "step": "generate",
      "duration_ms": 1514.9,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ea9ce84adf4242fba791cc864

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L21-L24

```text
This shards model weights across GPUs, allowing each GPU to have more memory available for KV cache.
However, increasing this value may cause excessive synchronization overhead.
- Increase `pipeline_parallel_size`.
```

### E854176531e0cf52e426febb2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L21-L24

```text
- Increase `gpu_memory_utilization`.
vLLM pre-allocates GPU cache using this percentage of memory.
By increasing utilization, you can provide more KV cache space.
- Decrease `max_num_seqs` or `max_num_batched_tokens`.
This reduces the number of concurrent requests in a batch, thereby requiring less KV cache space.
- Increase `tensor_parallel_size`.
```

### Ef433a588f6abcfc5b1bd9c20

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-conserving_memory.md#L85-L90

```text
## Adjust cache size

If you run out of CPU RAM, try the following options:

- (Multi-modal models only) you can set the size of multi-modal cache by setting `mm_processor_cache_gb` engine argument (default 4 GiB).
- (CPU backend only) you can set the size of KV cache using `VLLM_CPU_KVCACHE_SPACE` environment variable (default 4 GiB).
```

### Eccc3c69aae8e6b44c211083f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L73-L74

```text
- When the model is too large to fit on a single GPU
- When you need to reduce memory pressure per GPU to allow more KV cache space for higher throughput
```

### E6fcff5765635f30b24c2d96c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L67-L85

```text
!!
! note
By default vLLM will build for all GPU types for widest distribution.
If you are just building for the
current GPU type the machine is running on, you can add the argument `--build-arg torch_cuda_arch_list=""`
for vLLM to find the current GPU type and build for that.
If you are using Podman instead of Docker, you might need to disable SELinux labeling by
```

### Edb1580edf1a94751e80875de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L21-L24

```text
This distributes model layers across GPUs, reducing the memory needed for model weights on each GPU, indirectly leaving more memory available for KV cache.
However, increasing this value may cause latency penalties.
```

### E341615f9c49887ba248e3699

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L67-L85

```text
## Building vLLM's Docker Image from Source
You can build and run vLLM from source via the provided <gh-file:docker/Dockerfile>.
To build vLLM:
```bash
# optionally specifies: --build-arg max_jobs=8 --build-arg nvcc_threads=2
DOCKER_BUILDKIT=1 docker build . \
    --target vllm-openai \
    --tag vllm/vllm-openai \
    --file docker/Dockerfile
```
```

### Eb4f7cd8c5ff4c4cbf177370a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L67-L85

```text
adding `--security-opt label=disable` when running `podman build` command to avoid certain [existing issues](https://github.com/containers/buildah/discussions/4184).
```

## official-005-4:hybrid:retrieved

vLLM v0.10.2：先解释KV空间不足时抢占请求的恢复成本，再从内存优化指南找出将模型跨GPU拆分的参数。

必要要点：被抢占请求会在KV空间足够时重新计算。；KV抢占恢复需要重算；内存优化文档提供tensor_parallel_size将模型分布到多GPU的选项。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "cd751005-2967-4403-a581-172ebcfd4e15",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：先解释KV空间不足时抢占请求的恢复成本，再从内存优化指南找出将模型跨GPU拆分的参数。",
      "hits": 0,
      "evidence": 8
    },
    {
      "step": "generate",
      "duration_ms": 2144.2,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E854176531e0cf52e426febb2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L21-L24

```text
- Increase `gpu_memory_utilization`.
vLLM pre-allocates GPU cache using this percentage of memory.
By increasing utilization, you can provide more KV cache space.
- Decrease `max_num_seqs` or `max_num_batched_tokens`.
This reduces the number of concurrent requests in a batch, thereby requiring less KV cache space.
- Increase `tensor_parallel_size`.
```

### Eccc3c69aae8e6b44c211083f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L73-L74

```text
- When the model is too large to fit on a single GPU
- When you need to reduce memory pressure per GPU to allow more KV cache space for higher throughput
```

### Ea9ce84adf4242fba791cc864

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L21-L24

```text
This shards model weights across GPUs, allowing each GPU to have more memory available for KV cache.
However, increasing this value may cause excessive synchronization overhead.
- Increase `pipeline_parallel_size`.
```

### E6fcff5765635f30b24c2d96c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L67-L85

```text
!!
! note
By default vLLM will build for all GPU types for widest distribution.
If you are just building for the
current GPU type the machine is running on, you can add the argument `--build-arg torch_cuda_arch_list=""`
for vLLM to find the current GPU type and build for that.
If you are using Podman instead of Docker, you might need to disable SELinux labeling by
```

### E2a987935049ba4a72d481f15

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L1-L3

```text
# Sleep Mode

vLLM's Sleep Mode allows you to temporarily release most GPU memory used by a model, including model weights and KV cache, without stopping the server or unloading the Docker container. This is especially useful for RLHF, training, or cost-saving scenarios where GPU resources need to be freed between inference workloads.
```

### Edb1580edf1a94751e80875de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L21-L24

```text
This distributes model layers across GPUs, reducing the memory needed for model weights on each GPU, indirectly leaving more memory available for KV cache.
However, increasing this value may cause latency penalties.
```

### E341615f9c49887ba248e3699

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L67-L85

```text
## Building vLLM's Docker Image from Source
You can build and run vLLM from source via the provided <gh-file:docker/Dockerfile>.
To build vLLM:
```bash
# optionally specifies: --build-arg max_jobs=8 --build-arg nvcc_threads=2
DOCKER_BUILDKIT=1 docker build . \
    --target vllm-openai \
    --tag vllm/vllm-openai \
    --file docker/Dockerfile
```
```

### Eb4f7cd8c5ff4c4cbf177370a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L67-L85

```text
adding `--security-opt label=disable` when running `podman build` command to avoid certain [existing issues](https://github.com/containers/buildah/discussions/4184).
```

## official-005-4:hybrid_rerank:retrieved

vLLM v0.10.2：先解释KV空间不足时抢占请求的恢复成本，再从内存优化指南找出将模型跨GPU拆分的参数。

必要要点：被抢占请求会在KV空间足够时重新计算。；KV抢占恢复需要重算；内存优化文档提供tensor_parallel_size将模型分布到多GPU的选项。

禁止误读：抢占后请求必然丢弃或无需重新计算。

```json
{
  "conversation_id": "ae4c32c3-b692-44e3-8206-2c4a366fcca9",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：先解释KV空间不足时抢占请求的恢复成本，再从内存优化指南找出将模型跨GPU拆分的参数。",
      "hits": 0,
      "evidence": 7
    },
    {
      "step": "generate",
      "duration_ms": 1743.1,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E7eb06a8bf569c4754c22e656

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L76-L83

```text
```python
from vllm import LLM

# Split model across 4 GPUs
llm = LLM(model="meta-llama/Llama-3.3-70B-Instruct", tensor_parallel_size=4)
```

For models that are too large to fit on a single GPU (like 70B parameter models), tensor parallelism is essential.
```

### Ee4f4fbccc9548d5e3f51da06

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L140-L150

```text
When running the model you must specify `kv_cache_dtype="fp8"` in order to enable the kv cache quantization and use the scales.

```python
from vllm import LLM, SamplingParams

sampling_params = SamplingParams(temperature=0.7, top_p=0.8)
llm = LLM(model="Llama-3.1-8B-Instruct-FP8-KV", kv_cache_dtype="fp8")
prompt = "London is the capital of"
out = llm.generate(prompt, sampling_params)[0].outputs[0].text
print(out)
```
```

### E05fa3ecae9f31c8965f45edd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
\
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_connector":"SharedStorageConnector","kv_role":"kv_producer","kv_rank":0,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}' &

# decoding instance, which is the KV consumer
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_NAME \
    --port 7204 \
    --gpu-memory-utilization 0.8 \
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_co
```

### E50c474b99d138b120edc0d74

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L574-L587

```text
System Allocator
void test_prefetch_sam(cudaStream_t s) {
char *data = (char*)malloc(N);
init_data(data, N);
// execute on CPU
cudaMemLocation location = {.type = cudaMemLocationTypeDevice, .id = myGpuId};
cudaMemPrefetchAsync(data, N, location, s, 0 /* flags */);
// prefetch to GPU
```

### E76386a2d669e1a99e5aa70cf

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
```python
MODEL_NAME=models/Qwen2.5-VL-3B-Instruct/   # model path here

# a function that waits vLLM server to start
wait_for_server() {
  local port=$1
  timeout 12000 bash -c "
    until curl -s localhost:${port}/v1/chat/completions > /dev/null; do
      sleep 1
    done" && return 0 || return 1
}

# prefilling instance, which is the KV producer
CUDA_VISIBLE_DEVICES=0 vllm serve $MODEL_NAME \
    --port 7104 \
    --gpu-memory-utilization 0.8 
```

### Eca7787c4400bc8f084b7feb4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
To start the PD instances:
```

### Ed1e1300af58c1464e44b128e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
nnector":"SharedStorageConnector","kv_role":"kv_consumer","kv_rank":1,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}'  &

# wait until prefill and decode instances are ready
wait_for_server 7104
wait_for_server 7204

# launch the proxy server
python3 examples/online_serving/disaggregated_serving/disagg_proxy_demo.py  \
    --model $MODEL_NAME  \
```

## official-008-1:oracle:oracle

vLLM v0.10.2：文档对解耦prefill的吞吐收益作出什么限制？

必要要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "72d1e8cf-673e-438b-b4ba-6ceac983d029",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：文档对解耦prefill的吞吐收益作出什么限制？",
      "hits": 0,
      "evidence": 1
    },
    {
      "step": "generate",
      "duration_ms": 1347.8,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ecbae1b327e3ec1a52271d283

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/disagg_prefill.md

```text
Disaggregated prefill DOES NOT improve throughput.
```

## official-008-1:bm25:retrieved

vLLM v0.10.2：文档对解耦prefill的吞吐收益作出什么限制？

必要要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "8d714e7f-4690-498d-801d-2f4fcf1550e1",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：文档对解耦prefill的吞吐收益作出什么限制？",
      "hits": 0,
      "evidence": 7
    },
    {
      "step": "generate",
      "duration_ms": 1687.1,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E29490795e239155a8c7d9d21

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
## Chunked Prefill
Chunked prefill allows vLLM to process large prefills in smaller chunks and batch them together with decode requests.
This feature helps improve both throughput and latency by better balancing compute-bound (prefill) and memory-bound (decode) operations.
In vLLM V1, **chunked prefill is always enabled by default**.
This is different from vLLM V0, where it was conditionally enabled based on model characteristics.
```

### Ec0b2de7c0399262bb841227b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L38-L40

```text
## Development

We implement disaggregated prefilling by running 2 vLLM instances. One for prefill (we call it prefill instance) and one for decode (we call it decode instance), and then use a connector to transfer the prefill KV caches and results from prefill instance to decode instance.
```

### E01cd7f8528e50b0d7013c1be

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L14-L20

```text
## Speculating with a draft model

The following code configures vLLM in an offline mode to use speculative decoding with a draft model, speculating 5 tokens at a time.

!!! warning
    In vllm v0.10.0, speculative decoding with a draft model is not supported.
    If you use the following code, you will get a `NotImplementedError`.
```

### E6bdad69da7615cd693b983b2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L12-L13

```text
Without disaggregated prefilling, vLLM may insert some prefill jobs during the decoding of one request.
This results in higher tail latency.
Disaggregated prefilling helps you solve this issue and control tail ITL.
Chunked prefill with a proper chunk size also can achieve the same goal, but in practice it's hard to figure out the correct chunk size value.
So disaggregated prefilling is a much more reliable way to control tail ITL.
```

### E83613a6596bd80aa1e9a366b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L131-L136

```text
#### Understanding --prefill Arguments

The `--prefill` flag accepts URLs with optional bootstrap ports:
- `--prefill http://server:8000` - No bootstrap port
- `--prefill http://server:8000 9000` - Bootstrap port 9000
- `--prefill http://server:8000 none` - Explicitly no bootstrap port
```

### E1503adc8ce2e41e0596ea20d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
With chunked prefill enabled, the scheduling policy prioritizes decode requests.
It batches all pending decode requests before scheduling any prefill operations.
When there are available tokens in the `max_num_batched_tokens` budget, it schedules pending prefills.
If a pending prefill request cannot fit into `max_num_batched_tokens`, it automatically chunks it.
```

### Ec7ec068690e4d510990f420d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L12-L13

```text
- **Tuning time-to-first-token (TTFT) and inter-token-latency (ITL) separately**.
Disaggregated prefilling put prefill and decode phase of LLM inference inside different vLLM instances.
This gives you the flexibility to assign different parallel strategies (e.g.
`tp` and `pp`) to tune TTFT without affecting ITL, or to tune ITL without affecting TTFT.
- **Controlling tail ITL**.
```

## official-008-1:dense:retrieved

vLLM v0.10.2：文档对解耦prefill的吞吐收益作出什么限制？

必要要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "1076d5c1-1968-4d7b-837c-af5c968acbd9",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：文档对解耦prefill的吞吐收益作出什么限制？",
      "hits": 0,
      "evidence": 8
    },
    {
      "step": "generate",
      "duration_ms": 1509.7,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Efa726d7b2694135c695667f4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L227-L238

```text
3.
When using EAGLE-based speculators with vLLM, the observed speedup is lower than what is
reported in the reference implementation [here](https://github.com/SafeAILab/EAGLE).
This issue is under
investigation and tracked here: <gh-issue:9565>.
```

### E29490795e239155a8c7d9d21

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
## Chunked Prefill
Chunked prefill allows vLLM to process large prefills in smaller chunks and batch them together with decode requests.
This feature helps improve both throughput and latency by better balancing compute-bound (prefill) and memory-bound (decode) operations.
In vLLM V1, **chunked prefill is always enabled by default**.
This is different from vLLM V0, where it was conditionally enabled based on model characteristics.
```

### Ec0b2de7c0399262bb841227b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L38-L40

```text
## Development

We implement disaggregated prefilling by running 2 vLLM instances. One for prefill (we call it prefill instance) and one for decode (we call it decode instance), and then use a connector to transfer the prefill KV caches and results from prefill instance to decode instance.
```

### E83613a6596bd80aa1e9a366b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L131-L136

```text
#### Understanding --prefill Arguments

The `--prefill` flag accepts URLs with optional bootstrap ports:
- `--prefill http://server:8000` - No bootstrap port
- `--prefill http://server:8000 9000` - Bootstrap port 9000
- `--prefill http://server:8000 none` - Explicitly no bootstrap port
```

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### Ed9e3abcfeaef15d4450568be

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L227-L238

```text
2.
The EAGLE based draft models need to be run without tensor parallelism
(i.e.
draft_tensor_parallel_size is set to 1 in `speculative_config`), although
it is possible to run the main model using tensor parallelism (see example above).
```

### E08e8134cea75f600e7efb7c2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L227-L238

```text
4.
When using EAGLE-3 based draft model, option "method" must be set to "eagle3".
That is, to specify `"method": "eagle3"` in `speculative_config`.
A variety of EAGLE draft models are available on the Hugging Face hub:
```

### E1503adc8ce2e41e0596ea20d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
With chunked prefill enabled, the scheduling policy prioritizes decode requests.
It batches all pending decode requests before scheduling any prefill operations.
When there are available tokens in the `max_num_batched_tokens` budget, it schedules pending prefills.
If a pending prefill request cannot fit into `max_num_batched_tokens`, it automatically chunks it.
```

## official-008-1:hybrid:retrieved

vLLM v0.10.2：文档对解耦prefill的吞吐收益作出什么限制？

必要要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "81d234eb-6ee8-480f-9066-b45fe795cfda",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：文档对解耦prefill的吞吐收益作出什么限制？",
      "hits": 0,
      "evidence": 8
    },
    {
      "step": "generate",
      "duration_ms": 1597.7,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E29490795e239155a8c7d9d21

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
## Chunked Prefill
Chunked prefill allows vLLM to process large prefills in smaller chunks and batch them together with decode requests.
This feature helps improve both throughput and latency by better balancing compute-bound (prefill) and memory-bound (decode) operations.
In vLLM V1, **chunked prefill is always enabled by default**.
This is different from vLLM V0, where it was conditionally enabled based on model characteristics.
```

### Ec0b2de7c0399262bb841227b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L38-L40

```text
## Development

We implement disaggregated prefilling by running 2 vLLM instances. One for prefill (we call it prefill instance) and one for decode (we call it decode instance), and then use a connector to transfer the prefill KV caches and results from prefill instance to decode instance.
```

### E83613a6596bd80aa1e9a366b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L131-L136

```text
#### Understanding --prefill Arguments

The `--prefill` flag accepts URLs with optional bootstrap ports:
- `--prefill http://server:8000` - No bootstrap port
- `--prefill http://server:8000 9000` - Bootstrap port 9000
- `--prefill http://server:8000 none` - Explicitly no bootstrap port
```

### E6bdad69da7615cd693b983b2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L12-L13

```text
Without disaggregated prefilling, vLLM may insert some prefill jobs during the decoding of one request.
This results in higher tail latency.
Disaggregated prefilling helps you solve this issue and control tail ITL.
Chunked prefill with a proper chunk size also can achieve the same goal, but in practice it's hard to figure out the correct chunk size value.
So disaggregated prefilling is a much more reliable way to control tail ITL.
```

### Efa726d7b2694135c695667f4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L227-L238

```text
3.
When using EAGLE-based speculators with vLLM, the observed speedup is lower than what is
reported in the reference implementation [here](https://github.com/SafeAILab/EAGLE).
This issue is under
investigation and tracked here: <gh-issue:9565>.
```

### E1503adc8ce2e41e0596ea20d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
With chunked prefill enabled, the scheduling policy prioritizes decode requests.
It batches all pending decode requests before scheduling any prefill operations.
When there are available tokens in the `max_num_batched_tokens` budget, it schedules pending prefills.
If a pending prefill request cannot fit into `max_num_batched_tokens`, it automatically chunks it.
```

### Ec7ec068690e4d510990f420d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L12-L13

```text
- **Tuning time-to-first-token (TTFT) and inter-token-latency (ITL) separately**.
Disaggregated prefilling put prefill and decode phase of LLM inference inside different vLLM instances.
This gives you the flexibility to assign different parallel strategies (e.g.
`tp` and `pp`) to tune TTFT without affecting ITL, or to tune ITL without affecting TTFT.
- **Controlling tail ITL**.
```

### Ed9e3abcfeaef15d4450568be

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L227-L238

```text
2.
The EAGLE based draft models need to be run without tensor parallelism
(i.e.
```

## official-008-1:hybrid_rerank:retrieved

vLLM v0.10.2：文档对解耦prefill的吞吐收益作出什么限制？

必要要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "efe25792-05ce-4a5a-8e50-bc88e248db51",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：文档对解耦prefill的吞吐收益作出什么限制？",
      "hits": 0,
      "evidence": 7
    },
    {
      "step": "generate",
      "duration_ms": 1447.9,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E3935f79de724759010e2e8fb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L42-L44

```text
All disaggregated prefilling implementation is under `vllm/distributed/kv_transfer`.

Key abstractions for disaggregated prefilling:
```

### Eb81c406e8ea7ecad47e04367

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L28-L28

```text
In vLLM V1, the default preemption mode is `RECOMPUTE` rather than `SWAP`, as recomputation has lower overhead in the V1 architecture.
```

### E29490795e239155a8c7d9d21

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
## Chunked Prefill
Chunked prefill allows vLLM to process large prefills in smaller chunks and batch them together with decode requests.
This feature helps improve both throughput and latency by better balancing compute-bound (prefill) and memory-bound (decode) operations.
In vLLM V1, **chunked prefill is always enabled by default**.
This is different from vLLM V0, where it was conditionally enabled based on model characteristics.
```

### Ed6d39e475341f4ab01dc6509

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L50-L51

```text
### To reproduce:
vllm version: v0.9.2
```

### E6bdad69da7615cd693b983b2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L12-L13

```text
Without disaggregated prefilling, vLLM may insert some prefill jobs during the decoding of one request.
This results in higher tail latency.
Disaggregated prefilling helps you solve this issue and control tail ITL.
Chunked prefill with a proper chunk size also can achieve the same goal, but in practice it's hard to figure out the correct chunk size value.
So disaggregated prefilling is a much more reliable way to control tail ITL.
```

### E1503adc8ce2e41e0596ea20d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
With chunked prefill enabled, the scheduling policy prioritizes decode requests.
It batches all pending decode requests before scheduling any prefill operations.
When there are available tokens in the `max_num_batched_tokens` budget, it schedules pending prefills.
If a pending prefill request cannot fit into `max_num_batched_tokens`, it automatically chunks it.
```

### Ec7ec068690e4d510990f420d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L12-L13

```text
- **Tuning time-to-first-token (TTFT) and inter-token-latency (ITL) separately**.
Disaggregated prefilling put prefill and decode phase of LLM inference inside different vLLM instances.
This gives you the flexibility to assign different parallel strategies (e.g.
`tp` and `pp`) to tune TTFT without affecting ITL, or to tune ITL without affecting TTFT.
- **Controlling tail ITL**.
```

## official-008-2:oracle:oracle

vLLM v0.10.2：能否仅凭启用prefill/decode解耦就宣称吞吐提升？

必要要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "9aa7be75-8730-4b2b-a0cd-772aecfeb835",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：能否仅凭启用prefill/decode解耦就宣称吞吐提升？",
      "hits": 0,
      "evidence": 1
    },
    {
      "step": "generate",
      "duration_ms": 1445.1,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ecbae1b327e3ec1a52271d283

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/disagg_prefill.md

```text
Disaggregated prefill DOES NOT improve throughput.
```

## official-008-2:bm25:retrieved

vLLM v0.10.2：能否仅凭启用prefill/decode解耦就宣称吞吐提升？

必要要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "62911ae6-47fb-4af3-8ff4-a78c5cb916b2",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：能否仅凭启用prefill/decode解耦就宣称吞吐提升？",
      "hits": 0,
      "evidence": 9
    },
    {
      "step": "generate",
      "duration_ms": 1347.9,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ec0b2de7c0399262bb841227b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L38-L40

```text
## Development

We implement disaggregated prefilling by running 2 vLLM instances. One for prefill (we call it prefill instance) and one for decode (we call it decode instance), and then use a connector to transfer the prefill KV caches and results from prefill instance to decode instance.
```

### E29490795e239155a8c7d9d21

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
## Chunked Prefill
Chunked prefill allows vLLM to process large prefills in smaller chunks and batch them together with decode requests.
This feature helps improve both throughput and latency by better balancing compute-bound (prefill) and memory-bound (decode) operations.
In vLLM V1, **chunked prefill is always enabled by default**.
This is different from vLLM V0, where it was conditionally enabled based on model characteristics.
```

### E14004c472a06f97c258a0b18

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
1.
**Only `--policy` specified**: Both prefill and decode nodes use this policy
2.
**`--policy` and `--prefill-policy` specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--policy`
```

### Efdad1bd26f7ed89a954d75dc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L116-L118

```text
### Mode 3: Prefill-Decode Disaggregation

This advanced mode separates prefill and decode operations for optimized performance:
```

### Ebb8dd13c7d22423cb013a280

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L334-L344

```text
| --------------------------------- | ---- | ------- | ----------------------------------------------------- |
| `--pd-disaggregation`             | flag | False   | Enable PD disaggregated mode                          |
| `--prefill`                       | list | []      | Prefill server URLs with optional bootstrap ports     |
| `--decode`                        | list | []      | Decode server URLs                                    |
```

### E1503adc8ce2e41e0596ea20d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
With chunked prefill enabled, the scheduling policy prioritizes decode requests.
It batches all pending decode requests before scheduling any prefill operations.
When there are available tokens in the `max_num_batched_tokens` budget, it schedules pending prefills.
If a pending prefill request cannot fit into `max_num_batched_tokens`, it automatically chunks it.
```

### E52424825f1fdd2370ae03999

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
3.
**`--policy` and `--decode-policy` specified**: Prefill nodes use `--policy`, decode nodes use `--decode-policy`
```

### E1c7a85f00f61773ead210bcb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
4.
**All three specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--decode-policy` (main `--policy` is ignored)
```

### E7ccfd56fb63e6b824e888000

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L334-L344

```text
### Prefill-Decode Disaggregation Parameters
| Parameter                         | Type | Default | Description                                           |
```

## official-008-2:dense:retrieved

vLLM v0.10.2：能否仅凭启用prefill/decode解耦就宣称吞吐提升？

必要要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "d52c1921-a3ed-4be0-8971-2903dc5575c1",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：能否仅凭启用prefill/decode解耦就宣称吞吐提升？",
      "hits": 0,
      "evidence": 6
    },
    {
      "step": "generate",
      "duration_ms": 1602.7,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ec0b2de7c0399262bb841227b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L38-L40

```text
## Development

We implement disaggregated prefilling by running 2 vLLM instances. One for prefill (we call it prefill instance) and one for decode (we call it decode instance), and then use a connector to transfer the prefill KV caches and results from prefill instance to decode instance.
```

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### Ed6d39e475341f4ab01dc6509

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L50-L51

```text
### To reproduce:
vllm version: v0.9.2
```

### E29490795e239155a8c7d9d21

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
## Chunked Prefill
Chunked prefill allows vLLM to process large prefills in smaller chunks and batch them together with decode requests.
This feature helps improve both throughput and latency by better balancing compute-bound (prefill) and memory-bound (decode) operations.
In vLLM V1, **chunked prefill is always enabled by default**.
This is different from vLLM V0, where it was conditionally enabled based on model characteristics.
```

### Ede81f51af23dabfaa0a634ce

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L42-L51

```text
    If you need to use those dependencies (having accepted the license terms),
    create a custom Dockerfile on top of the base image with an extra layer that installs them:

    ```Dockerfile
    FROM vllm/vllm-openai:v0.9.0

    # e.g. install the `audio` optional dependencies
    # NOTE: Make sure the version of vLLM matches the base image!
    RUN uv pip install --system vllm[audio]==0.9.0
    ```
```

### E1503adc8ce2e41e0596ea20d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
With chunked prefill enabled, the scheduling policy prioritizes decode requests.
It batches all pending decode requests before scheduling any prefill operations.
When there are available tokens in the `max_num_batched_tokens` budget, it schedules pending prefills.
If a pending prefill request cannot fit into `max_num_batched_tokens`, it automatically chunks it.
```

## official-008-2:hybrid:retrieved

vLLM v0.10.2：能否仅凭启用prefill/decode解耦就宣称吞吐提升？

必要要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "ab09500c-3842-4c66-80ba-54b04f1ae75f",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：能否仅凭启用prefill/decode解耦就宣称吞吐提升？",
      "hits": 0,
      "evidence": 9
    },
    {
      "step": "generate",
      "duration_ms": 1983.1,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ec0b2de7c0399262bb841227b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L38-L40

```text
## Development

We implement disaggregated prefilling by running 2 vLLM instances. One for prefill (we call it prefill instance) and one for decode (we call it decode instance), and then use a connector to transfer the prefill KV caches and results from prefill instance to decode instance.
```

### E29490795e239155a8c7d9d21

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
## Chunked Prefill
Chunked prefill allows vLLM to process large prefills in smaller chunks and batch them together with decode requests.
This feature helps improve both throughput and latency by better balancing compute-bound (prefill) and memory-bound (decode) operations.
In vLLM V1, **chunked prefill is always enabled by default**.
This is different from vLLM V0, where it was conditionally enabled based on model characteristics.
```

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### Ed6d39e475341f4ab01dc6509

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L50-L51

```text
### To reproduce:
vllm version: v0.9.2
```

### E14004c472a06f97c258a0b18

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
1.
**Only `--policy` specified**: Both prefill and decode nodes use this policy
2.
**`--policy` and `--prefill-policy` specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--policy`
```

### E1503adc8ce2e41e0596ea20d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
With chunked prefill enabled, the scheduling policy prioritizes decode requests.
It batches all pending decode requests before scheduling any prefill operations.
When there are available tokens in the `max_num_batched_tokens` budget, it schedules pending prefills.
If a pending prefill request cannot fit into `max_num_batched_tokens`, it automatically chunks it.
```

### E52424825f1fdd2370ae03999

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
3.
**`--policy` and `--decode-policy` specified**: Prefill nodes use `--policy`, decode nodes use `--decode-policy`
```

### E1c7a85f00f61773ead210bcb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
4.
**All three specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--decode-policy` (main `--policy` is ignored)
```

### Eb21de41bd9abccda7860e337

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
Example with mixed policies:
```bash
python -m sglang_router.launch_router \
    --pd-disaggregation \
    --prefill http://prefill1:8000
    --prefill http://prefill2:8000 \
    --decode http://decode1:8001
    --decode http://decode2:8001 \
    --policy round_robin \
    --prefill-policy cache_aware  # Prefill uses cache_aware and decode uses round_robin from --policy
```
```

## official-008-2:hybrid_rerank:retrieved

vLLM v0.10.2：能否仅凭启用prefill/decode解耦就宣称吞吐提升？

必要要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "22bafd30-32ed-4ec6-9999-57392eba401e",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：能否仅凭启用prefill/decode解耦就宣称吞吐提升？",
      "hits": 0,
      "evidence": 9
    },
    {
      "step": "generate",
      "duration_ms": 1516.3,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E29490795e239155a8c7d9d21

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
## Chunked Prefill
Chunked prefill allows vLLM to process large prefills in smaller chunks and batch them together with decode requests.
This feature helps improve both throughput and latency by better balancing compute-bound (prefill) and memory-bound (decode) operations.
In vLLM V1, **chunked prefill is always enabled by default**.
This is different from vLLM V0, where it was conditionally enabled based on model characteristics.
```

### Ed6d39e475341f4ab01dc6509

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L50-L51

```text
### To reproduce:
vllm version: v0.9.2
```

### E87da218a58471d09aa9c455b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L120-L129

```text
```bash
python -m sglang_router.launch_router \
    --pd-disaggregation \
    --prefill http://prefill1:8000 9000 \
    --prefill http://prefill2:8001 9001 \
    --decode http://decode1:8002 \
    --decode http://decode2:8003 \
    --prefill-policy cache_aware \
    --decode-policy round_robin
```
```

### Eb21de41bd9abccda7860e337

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
Example with mixed policies:
```bash
python -m sglang_router.launch_router \
    --pd-disaggregation \
    --prefill http://prefill1:8000
    --prefill http://prefill2:8000 \
    --decode http://decode1:8001
    --decode http://decode2:8001 \
    --policy round_robin \
    --prefill-policy cache_aware  # Prefill uses cache_aware and decode uses round_robin from --policy
```
```

### Ec0b2de7c0399262bb841227b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L38-L40

```text
## Development

We implement disaggregated prefilling by running 2 vLLM instances. One for prefill (we call it prefill instance) and one for decode (we call it decode instance), and then use a connector to transfer the prefill KV caches and results from prefill instance to decode instance.
```

### E1503adc8ce2e41e0596ea20d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
With chunked prefill enabled, the scheduling policy prioritizes decode requests.
It batches all pending decode requests before scheduling any prefill operations.
When there are available tokens in the `max_num_batched_tokens` budget, it schedules pending prefills.
If a pending prefill request cannot fit into `max_num_batched_tokens`, it automatically chunks it.
```

### E1c7a85f00f61773ead210bcb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
4.
**All three specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--decode-policy` (main `--policy` is ignored)
```

### E52424825f1fdd2370ae03999

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
3.
**`--policy` and `--decode-policy` specified**: Prefill nodes use `--policy`, decode nodes use `--decode-policy`
```

### E14004c472a06f97c258a0b18

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
1.
**Only `--policy` specified**: Both prefill and decode nodes use this policy
2.
**`--policy` and `--prefill-policy` specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--policy`
```

## official-008-3:oracle:oracle

vLLM v0.10.2：切换解耦prefill后吞吐没有提升，是否违背文档承诺？

必要要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "65cd12da-e530-4bd2-807a-66c159fa3516",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：切换解耦prefill后吞吐没有提升，是否违背文档承诺？",
      "hits": 0,
      "evidence": 1
    },
    {
      "step": "generate",
      "duration_ms": 1632.1,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ecbae1b327e3ec1a52271d283

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/disagg_prefill.md

```text
Disaggregated prefill DOES NOT improve throughput.
```

## official-008-3:bm25:retrieved

vLLM v0.10.2：切换解耦prefill后吞吐没有提升，是否违背文档承诺？

必要要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "82061450-b75d-4fe5-bd36-d70368504e55",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：切换解耦prefill后吞吐没有提升，是否违背文档承诺？",
      "hits": 0,
      "evidence": 7
    },
    {
      "step": "generate",
      "duration_ms": 1339.4,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E29490795e239155a8c7d9d21

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
## Chunked Prefill
Chunked prefill allows vLLM to process large prefills in smaller chunks and batch them together with decode requests.
This feature helps improve both throughput and latency by better balancing compute-bound (prefill) and memory-bound (decode) operations.
In vLLM V1, **chunked prefill is always enabled by default**.
This is different from vLLM V0, where it was conditionally enabled based on model characteristics.
```

### Ec0b2de7c0399262bb841227b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L38-L40

```text
## Development

We implement disaggregated prefilling by running 2 vLLM instances. One for prefill (we call it prefill instance) and one for decode (we call it decode instance), and then use a connector to transfer the prefill KV caches and results from prefill instance to decode instance.
```

### E01cd7f8528e50b0d7013c1be

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L14-L20

```text
## Speculating with a draft model

The following code configures vLLM in an offline mode to use speculative decoding with a draft model, speculating 5 tokens at a time.

!!! warning
    In vllm v0.10.0, speculative decoding with a draft model is not supported.
    If you use the following code, you will get a `NotImplementedError`.
```

### E6bdad69da7615cd693b983b2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L12-L13

```text
Without disaggregated prefilling, vLLM may insert some prefill jobs during the decoding of one request.
This results in higher tail latency.
Disaggregated prefilling helps you solve this issue and control tail ITL.
Chunked prefill with a proper chunk size also can achieve the same goal, but in practice it's hard to figure out the correct chunk size value.
So disaggregated prefilling is a much more reliable way to control tail ITL.
```

### E83613a6596bd80aa1e9a366b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L131-L136

```text
#### Understanding --prefill Arguments

The `--prefill` flag accepts URLs with optional bootstrap ports:
- `--prefill http://server:8000` - No bootstrap port
- `--prefill http://server:8000 9000` - Bootstrap port 9000
- `--prefill http://server:8000 none` - Explicitly no bootstrap port
```

### E1503adc8ce2e41e0596ea20d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
With chunked prefill enabled, the scheduling policy prioritizes decode requests.
It batches all pending decode requests before scheduling any prefill operations.
When there are available tokens in the `max_num_batched_tokens` budget, it schedules pending prefills.
If a pending prefill request cannot fit into `max_num_batched_tokens`, it automatically chunks it.
```

### Ec7ec068690e4d510990f420d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L12-L13

```text
- **Tuning time-to-first-token (TTFT) and inter-token-latency (ITL) separately**.
Disaggregated prefilling put prefill and decode phase of LLM inference inside different vLLM instances.
This gives you the flexibility to assign different parallel strategies (e.g.
`tp` and `pp`) to tune TTFT without affecting ITL, or to tune ITL without affecting TTFT.
- **Controlling tail ITL**.
```

## official-008-3:dense:retrieved

vLLM v0.10.2：切换解耦prefill后吞吐没有提升，是否违背文档承诺？

必要要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "24082369-76a0-47dd-a923-96b828ed7721",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：切换解耦prefill后吞吐没有提升，是否违背文档承诺？",
      "hits": 0,
      "evidence": 11
    },
    {
      "step": "generate",
      "duration_ms": 1293.3,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ef6da67af73e0e081f183d79f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L219-L225

```text
and specify `"model": "path/to/modified/eagle/model"` in `speculative_config`.
If weight-loading problems still occur when using the latest version of vLLM, please leave a comment or raise an issue.
```

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### Eceb2cd5603a911fb514b54d7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L1-L23

```text
vLLM multi-head query attention kernel.
After going through this
document, users will likely have a better understanding and feel easier
to follow the actual implementation.
```

### E20853351d30eab09ebf69f4e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L100-L117

```text
## Data Structure
The prefix caching in vLLM v1 is implemented in the KV cache manager.
The basic building block is the “Block” data class (simplified):
```

### Ec0b2de7c0399262bb841227b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L38-L40

```text
## Development

We implement disaggregated prefilling by running 2 vLLM instances. One for prefill (we call it prefill instance) and one for decode (we call it decode instance), and then use a connector to transfer the prefill KV caches and results from prefill instance to decode instance.
```

### Eef19054a92bfeead1e0277a8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L219-L225

```text
A few important things to consider when using the EAGLE based draft models:
1.
The EAGLE draft models available in the [HF repository for EAGLE models](https://huggingface.co/yuhuili) should
be able to be loaded and used directly by vLLM after <gh-pr:12304>.
If you are using vllm version before <gh-pr:12304>, please use the
[script](https://gist.github.com/abhigoyal1997/1e7a4109ccb7704fbc67f625e86b2d6d) to convert the speculative model,
```

### E651e88ca0914058c22080722

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L1-L23

```text
The purpose of this
document is to provide a high-level explanation of the kernel
implementation step by step, aiding those who wish to learn about the
```

### E73ed6b033e408055ba67ce0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L1-L23

```text
attention block as "block", while refer to GPU thread block as
"thread block").
To achieve high performance, this kernel relies on a specially
designed memory layout and access method, specifically when threads
read data from global memory to shared memory.
```

### E5b439317d584c2241b07f36a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L1-L23

```text
separate blocks (note that this block concept differs from the GPU
thread block.
So in a later document, I will refer to vLLM paged
```

### E0ba72e65234add842fa94e1f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L1-L23

```text
# Paged Attention
!
!!
warning
This is a historical document based on the [original paper for vLLM](https://arxiv.org/abs/2309.06180).
It no longer describes the code used in vLLM today.
Currently, vLLM utilizes its own implementation of a multi-head query
attention kernel (`csrc/attention/attention_kernels.cu`).
This kernel is designed to be compatible with
vLLM's paged KV caches, where the key and value cache are stored in
```

### E9582c677de8671c062989a9b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L100-L117

```text
ock"] = None
```
```

## official-008-3:hybrid:retrieved

vLLM v0.10.2：切换解耦prefill后吞吐没有提升，是否违背文档承诺？

必要要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "3d9cff51-40b8-4d4a-9540-de7c9f7f747f",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：切换解耦prefill后吞吐没有提升，是否违背文档承诺？",
      "hits": 0,
      "evidence": 6
    },
    {
      "step": "generate",
      "duration_ms": 1363.3,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ec0b2de7c0399262bb841227b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L38-L40

```text
## Development

We implement disaggregated prefilling by running 2 vLLM instances. One for prefill (we call it prefill instance) and one for decode (we call it decode instance), and then use a connector to transfer the prefill KV caches and results from prefill instance to decode instance.
```

### E29490795e239155a8c7d9d21

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
## Chunked Prefill
Chunked prefill allows vLLM to process large prefills in smaller chunks and batch them together with decode requests.
This feature helps improve both throughput and latency by better balancing compute-bound (prefill) and memory-bound (decode) operations.
In vLLM V1, **chunked prefill is always enabled by default**.
This is different from vLLM V0, where it was conditionally enabled based on model characteristics.
```

### E1503adc8ce2e41e0596ea20d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
With chunked prefill enabled, the scheduling policy prioritizes decode requests.
It batches all pending decode requests before scheduling any prefill operations.
When there are available tokens in the `max_num_batched_tokens` budget, it schedules pending prefills.
If a pending prefill request cannot fit into `max_num_batched_tokens`, it automatically chunks it.
```

### Ef6da67af73e0e081f183d79f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L219-L225

```text
and specify `"model": "path/to/modified/eagle/model"` in `speculative_config`.
If weight-loading problems still occur when using the latest version of vLLM, please leave a comment or raise an issue.
```

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### Eef19054a92bfeead1e0277a8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L219-L225

```text
A few important things to consider when using the EAGLE based draft models:
1.
The EAGLE draft models available in the [HF repository for EAGLE models](https://huggingface.co/yuhuili) should
be able to be loaded and used directly by vLLM after <gh-pr:12304>.
If you are using vllm version before <gh-pr:12304>, please use the
[script](https://gist.github.com/abhigoyal1997/1e7a4109ccb7704fbc67f625e86b2d6d) to convert the speculative model,
```

## official-008-3:hybrid_rerank:retrieved

vLLM v0.10.2：切换解耦prefill后吞吐没有提升，是否违背文档承诺？

必要要点：文档明确不应把解耦prefill描述成吞吐提升。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "8f7f7053-502f-486c-bfdb-d36660742a80",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：切换解耦prefill后吞吐没有提升，是否违背文档承诺？",
      "hits": 0,
      "evidence": 10
    },
    {
      "step": "generate",
      "duration_ms": 1370.2,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Eb81c406e8ea7ecad47e04367

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L28-L28

```text
In vLLM V1, the default preemption mode is `RECOMPUTE` rather than `SWAP`, as recomputation has lower overhead in the V1 architecture.
```

### Ed6d39e475341f4ab01dc6509

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L50-L51

```text
### To reproduce:
vllm version: v0.9.2
```

### E6bdad69da7615cd693b983b2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L12-L13

```text
Without disaggregated prefilling, vLLM may insert some prefill jobs during the decoding of one request.
This results in higher tail latency.
Disaggregated prefilling helps you solve this issue and control tail ITL.
Chunked prefill with a proper chunk size also can achieve the same goal, but in practice it's hard to figure out the correct chunk size value.
So disaggregated prefilling is a much more reliable way to control tail ITL.
```

### E9334c8ebd5003f269a8dbfa0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
3.
**vLLM Logprob Stability**
\- vLLM does not currently guarantee stable token log probabilities (logprobs).
This can result in different outputs for the
```

### E29490795e239155a8c7d9d21

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
## Chunked Prefill
Chunked prefill allows vLLM to process large prefills in smaller chunks and batch them together with decode requests.
This feature helps improve both throughput and latency by better balancing compute-bound (prefill) and memory-bound (decode) operations.
In vLLM V1, **chunked prefill is always enabled by default**.
This is different from vLLM V0, where it was conditionally enabled based on model characteristics.
```

### Ec7ec068690e4d510990f420d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L12-L13

```text
- **Tuning time-to-first-token (TTFT) and inter-token-latency (ITL) separately**.
Disaggregated prefilling put prefill and decode phase of LLM inference inside different vLLM instances.
This gives you the flexibility to assign different parallel strategies (e.g.
`tp` and `pp`) to tune TTFT without affecting ITL, or to tune ITL without affecting TTFT.
- **Controlling tail ITL**.
```

### E817b770fdd612fe5c92ce442

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
same request across runs.
For more details, see the FAQ section
titled *Can the output of a prompt vary across runs in vLLM?
```

### E806a86f3d7c94ddceb889b00

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
* in the [FAQs](../usage/faq.md).
While vLLM strives to ensure losslessness in speculative decoding, variations in generated outputs with and without speculative decoding
can occur due to following factors:
- **Floating-Point Precision**: Differences in hardware numerical precision may lead to slight discrepancies in the output distribution.
```

### E1f8f4afd3342de899d5b77f5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
- **Batch Size and Numerical Stability**: Changes in batch size may cause variations in logprobs and output probabilities, potentially
due to non-deterministic behavior in batched operations or numerical instability.
```

### E5a09222d3c9ddb741403611b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
For mitigation strategies, please refer to the FAQ entry *Can the output of a prompt vary across runs in vLLM?
* in the [FAQs](../usage/faq.md).
```

## official-008-4:oracle:oracle

vLLM v0.10.2：根据SGLang说明先识别分离阶段的作用，再依据vLLM限制判断能否把解耦直接当作吞吐提升保证。

必要要点：文档明确不应把解耦prefill描述成吞吐提升。；先识别prefill/decode阶段干扰，再解释分离阶段用于针对性优化，不能据此宣称vLLM该版本吞吐必涨。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "80362a1d-f621-48a7-ba7f-58beb858dd54",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：根据SGLang说明先识别分离阶段的作用，再依据vLLM限制判断能否把解耦直接当作吞吐提升保证。",
      "hits": 0,
      "evidence": 2
    },
    {
      "step": "generate",
      "duration_ms": 1319.8,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### Ecbae1b327e3ec1a52271d283

https://github.com/vllm-project/vllm/blob/01efc7ef781391e744ed08c3292817a773d654e6/docs/features/disagg_prefill.md

```text
Disaggregated prefill DOES NOT improve throughput.
```

### E0530f63d40ea8581ccc70dcd

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/pd_disaggregation.md

```text
PD Disaggregation resolves these by separating the two stages, enabling tailored optimizations for each.
```

## official-008-4:bm25:retrieved

vLLM v0.10.2：根据SGLang说明先识别分离阶段的作用，再依据vLLM限制判断能否把解耦直接当作吞吐提升保证。

必要要点：文档明确不应把解耦prefill描述成吞吐提升。；先识别prefill/decode阶段干扰，再解释分离阶段用于针对性优化，不能据此宣称vLLM该版本吞吐必涨。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "232f81c8-5454-43f7-bc68-b7fd6dfb5c18",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：根据SGLang说明先识别分离阶段的作用，再依据vLLM限制判断能否把解耦直接当作吞吐提升保证。",
      "hits": 0,
      "evidence": 7
    },
    {
      "step": "generate",
      "duration_ms": 1479.5,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E01cd7f8528e50b0d7013c1be

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L14-L20

```text
## Speculating with a draft model

The following code configures vLLM in an offline mode to use speculative decoding with a draft model, speculating 5 tokens at a time.

!!! warning
    In vllm v0.10.0, speculative decoding with a draft model is not supported.
    If you use the following code, you will get a `NotImplementedError`.
```

### E4a99edc287be8e7e99295b08

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L105-L105

```text
Then, you can directly use the quantized model with `SGLang`, by using the following command:
```

### E904c381bf1f5f1779dedef72

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
This action will ignore the Hugging Face config's quantization settings.
For instance, with `neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic`, if you execute with `--quantization w8a8_fp8`, the system will use the `W8A8Fp8Config` from SGLang to invoke the sgl-kernel, rather than the `CompressedTensorsConfig` for vLLM kernels.
```

### E6e735407436bdd0db25147db

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L107-L111

```text
```bash
python3 -m sglang.launch_server \
    --model-path $PWD/Meta-Llama-3-8B-Instruct-FP8-Dynamic \
    --port 30000 --host 0.0.0.0
```
```

### E8651ea1f0391d57e95cc940c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L1-L3

```text
# Install SGLang

You can install SGLang using one of the methods below.
```

### E74b994b5ce8fbeb1f2a0b11e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4 \
    --port 30000 --host 0.0.0.0
```
Take note, if your model is **per-channel quantized (INT8 or FP8) with per-token dynamic quantization activation**, you can opt to include `--quantization w8a8_int8` or `--quantization w8a8_fp8` to invoke the corresponding CUTLASS int8_kernel or fp8_kernel in sgl-kernel.
```

### Ef6c630563d458d3c5beb00ac

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic \
    --quantization w8a8_fp8 \
    --port 30000 --host 0.0.0.0
```
```

## official-008-4:dense:retrieved

vLLM v0.10.2：根据SGLang说明先识别分离阶段的作用，再依据vLLM限制判断能否把解耦直接当作吞吐提升保证。

必要要点：文档明确不应把解耦prefill描述成吞吐提升。；先识别prefill/decode阶段干扰，再解释分离阶段用于针对性优化，不能据此宣称vLLM该版本吞吐必涨。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "38e8e56e-2092-45fd-af52-784e35613672",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：根据SGLang说明先识别分离阶段的作用，再依据vLLM限制判断能否把解耦直接当作吞吐提升保证。",
      "hits": 0,
      "evidence": 7
    },
    {
      "step": "generate",
      "duration_ms": 1506.8,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### Ec0b2de7c0399262bb841227b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L38-L40

```text
## Development

We implement disaggregated prefilling by running 2 vLLM instances. One for prefill (we call it prefill instance) and one for decode (we call it decode instance), and then use a connector to transfer the prefill KV caches and results from prefill instance to decode instance.
```

### E29490795e239155a8c7d9d21

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
## Chunked Prefill
Chunked prefill allows vLLM to process large prefills in smaller chunks and batch them together with decode requests.
This feature helps improve both throughput and latency by better balancing compute-bound (prefill) and memory-bound (decode) operations.
In vLLM V1, **chunked prefill is always enabled by default**.
This is different from vLLM V0, where it was conditionally enabled based on model characteristics.
```

### Ef6da67af73e0e081f183d79f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L219-L225

```text
and specify `"model": "path/to/modified/eagle/model"` in `speculative_config`.
If weight-loading problems still occur when using the latest version of vLLM, please leave a comment or raise an issue.
```

### Efbb576120d973191dc3e7b42

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L1-L4

```text
# Sampling Parameters

This doc describes the sampling parameters of the SGLang Runtime. It is the low-level endpoint of the runtime.
If you want a high-level endpoint that can automatically handle chat templates, consider using the [OpenAI Compatible API](openai_api_completions.ipynb).
```

### E1503adc8ce2e41e0596ea20d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L32-L38

```text
With chunked prefill enabled, the scheduling policy prioritizes decode requests.
It batches all pending decode requests before scheduling any prefill operations.
When there are available tokens in the `max_num_batched_tokens` budget, it schedules pending prefills.
If a pending prefill request cannot fit into `max_num_batched_tokens`, it automatically chunks it.
```

### Eef19054a92bfeead1e0277a8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L219-L225

```text
A few important things to consider when using the EAGLE based draft models:
1.
The EAGLE draft models available in the [HF repository for EAGLE models](https://huggingface.co/yuhuili) should
be able to be loaded and used directly by vLLM after <gh-pr:12304>.
If you are using vllm version before <gh-pr:12304>, please use the
[script](https://gist.github.com/abhigoyal1997/1e7a4109ccb7704fbc67f625e86b2d6d) to convert the speculative model,
```

## official-008-4:hybrid:retrieved

vLLM v0.10.2：根据SGLang说明先识别分离阶段的作用，再依据vLLM限制判断能否把解耦直接当作吞吐提升保证。

必要要点：文档明确不应把解耦prefill描述成吞吐提升。；先识别prefill/decode阶段干扰，再解释分离阶段用于针对性优化，不能据此宣称vLLM该版本吞吐必涨。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "8f9c2e37-9c64-40a2-acd5-cdfffa0f9300",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：根据SGLang说明先识别分离阶段的作用，再依据vLLM限制判断能否把解耦直接当作吞吐提升保证。",
      "hits": 0,
      "evidence": 12
    },
    {
      "step": "generate",
      "duration_ms": 1758.7,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### E8dc2fb2a5fca69b5d1a146b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L1-L3

```text
# SGLang Router

The SGLang Router is a high-performance request distribution system that routes inference requests across multiple SGLang runtime instances. It features cache-aware load balancing, fault tolerance, and support for advanced deployment patterns including data parallelism and prefill-decode disaggregation.
```

### E01cd7f8528e50b0d7013c1be

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L14-L20

```text
## Speculating with a draft model

The following code configures vLLM in an offline mode to use speculative decoding with a draft model, speculating 5 tokens at a time.

!!! warning
    In vllm v0.10.0, speculative decoding with a draft model is not supported.
    If you use the following code, you will get a `NotImplementedError`.
```

### E9334c8ebd5003f269a8dbfa0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
3.
**vLLM Logprob Stability**
\- vLLM does not currently guarantee stable token log probabilities (logprobs).
This can result in different outputs for the
```

### E2f7560e9ddf1ed421bd0d6f5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| None |
| `--model-impl` | Which implementation of the model to use.
'auto' will try to use the SGLang implementation if it exists and fall back to the Transformers implementation if no SGLang implementation is available.
'sglang' will use the SGLang model implementation.
'transformers' will use the Transformers model implementation.
```

### E817b770fdd612fe5c92ce442

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
same request across runs.
For more details, see the FAQ section
titled *Can the output of a prompt vary across runs in vLLM?
```

### E806a86f3d7c94ddceb889b00

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
* in the [FAQs](../usage/faq.md).
While vLLM strives to ensure losslessness in speculative decoding, variations in generated outputs with and without speculative decoding
can occur due to following factors:
- **Floating-Point Precision**: Differences in hardware numerical precision may lead to slight discrepancies in the output distribution.
```

### E1f8f4afd3342de899d5b77f5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
- **Batch Size and Numerical Stability**: Changes in batch size may cause variations in logprobs and output probabilities, potentially
due to non-deterministic behavior in batched operations or numerical instability.
```

### E5a09222d3c9ddb741403611b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L274-L286

```text
For mitigation strategies, please refer to the FAQ entry *Can the output of a prompt vary across runs in vLLM?
* in the [FAQs](../usage/faq.md).
```

### E6804fdf269f9381d4466550f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| None |
| `--revision` | The specific model version to use.
It can be a branch name, a tag name, or a commit id.
If unspecified, will use the default version.
```

### Ee8a88173212a4442d4ce3c0a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| auto |
```

### Ee2d15087b506eeeac7be0e83

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| None |
| `--is-embedding` | Whether to use a CausalLM as an embedding model.
| False |
```

## official-008-4:hybrid_rerank:retrieved

vLLM v0.10.2：根据SGLang说明先识别分离阶段的作用，再依据vLLM限制判断能否把解耦直接当作吞吐提升保证。

必要要点：文档明确不应把解耦prefill描述成吞吐提升。；先识别prefill/decode阶段干扰，再解释分离阶段用于针对性优化，不能据此宣称vLLM该版本吞吐必涨。

禁止误读：该版本解耦prefill必然提高吞吐。

```json
{
  "conversation_id": "4d2eef67-f689-43e7-8454-3bda1ad8dbc0",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "vLLM v0.10.2：根据SGLang说明先识别分离阶段的作用，再依据vLLM限制判断能否把解耦直接当作吞吐提升保证。",
      "hits": 0,
      "evidence": 8
    },
    {
      "step": "generate",
      "duration_ms": 1991.0,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E4a99edc287be8e7e99295b08

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L105-L105

```text
Then, you can directly use the quantized model with `SGLang`, by using the following command:
```

### E53a04ce20e63602ad4637565

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L33-L33

```text
3. Evaluating accuracy in vLLM
```

### E6e735407436bdd0db25147db

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L107-L111

```text
```bash
python3 -m sglang.launch_server \
    --model-path $PWD/Meta-Llama-3-8B-Instruct-FP8-Dynamic \
    --port 30000 --host 0.0.0.0
```
```

### E904c381bf1f5f1779dedef72

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
This action will ignore the Hugging Face config's quantization settings.
For instance, with `neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic`, if you execute with `--quantization w8a8_fp8`, the system will use the `W8A8Fp8Config` from SGLang to invoke the sgl-kernel, rather than the `CompressedTensorsConfig` for vLLM kernels.
```

### E12fd27572c9ae4f65a11fcfe

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L1-L12

```text
!
!!
warning
Currently, speculative decoding in vLLM is not compatible with pipeline parallelism.
This document shows how to use [Speculative Decoding](https://x.com/karpathy/status/1697318534555336961) with vLLM.
Speculative decoding is a technique which improves inter-token latency in memory-bound LLM inference.
```

### E74b994b5ce8fbeb1f2a0b11e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4 \
    --port 30000 --host 0.0.0.0
```
Take note, if your model is **per-channel quantized (INT8 or FP8) with per-token dynamic quantization activation**, you can opt to include `--quantization w8a8_int8` or `--quantization w8a8_fp8` to invoke the corresponding CUTLASS int8_kernel or fp8_kernel in sgl-kernel.
```

### Ef6c630563d458d3c5beb00ac

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic \
    --quantization w8a8_fp8 \
    --port 30000 --host 0.0.0.0
```
```

### E9041556c305b4ab5a90588d1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L1-L12

```text
# Speculative Decoding
!
!!
warning
Please note that speculative decoding in vLLM is not yet optimized and does
not usually yield inter-token latency reductions for all prompt datasets or sampling parameters.
The work to optimize it is ongoing and can be followed here: <gh-issue:4630>
```

## official-010-1:oracle:oracle

历史修复 PR21611：PR21611怎样让connector区分不同多模态输入的KV？

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
{
  "conversation_id": "ef1757e0-bd19-477e-9a64-06a8919dcb85",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "历史修复 PR21611：PR21611怎样让connector区分不同多模态输入的KV？",
      "hits": 0,
      "evidence": 1
    },
    {
      "step": "generate",
      "duration_ms": 2345.4,
      "provider": "openai-compatible",
      "model": "coding-glm-4.6-free",
      "validated": false
    }
  ]
}
```

实际输入证据：

### E18e46086d71bc6f871bfc38e

https://github.com/vllm-project/vllm/pull/21611

```text
It brings in the mm_hashes from the Request to the connector to form a proper key; that can help distinguish kv for different mm input.
```

## official-010-1:bm25:retrieved

历史修复 PR21611：PR21611怎样让connector区分不同多模态输入的KV？

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### Ebf13eeb5c9f8d5c8b8e51b4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
```bash
  --kv-transfer-config '{"kv_connector":"MultiConnector","kv_role":"kv_both","kv_connector_extra_config":{"connectors":[{"kv_connector":"NixlConnector","kv_role":"kv_both"},{"kv_connector":"SharedStorageConnector","kv_role":"kv_both","kv_connector_extra_config":{"shared_storage_path":"local_storage"}}]}}'
  ```
```

### E5a272eae0c90bf1956be01fb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L65-L66

```text
- Scheduler connector: the connector that locates in the same process as the scheduler process. It schedules the KV cache transfer ops.
- Worker connectors: the connectors that locate in the worker processes. They execute KV cache transfer ops.
```

### E4d858f31046eaf432dd1fbe6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L46-L48

```text
- **Connector**: Connector allows **kv consumer** to retrieve the KV caches of a batch of request from **kv producer**.
- **LookupBuffer**: LookupBuffer provides two API: `insert` KV cache and `drop_select` KV cache.
The semantics of `insert` and `drop_select` are similar to SQL, where `insert` inserts a KV cache into the buffer, and `drop_select` returns the KV cache that matches the given condition and drop it from the buffer.
```

### E05fa3ecae9f31c8965f45edd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
\
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_connector":"SharedStorageConnector","kv_role":"kv_producer","kv_rank":0,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}' &

# decoding instance, which is the KV consumer
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_NAME \
    --port 7204 \
    --gpu-memory-utilization 0.8 \
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_co
```

### Eac6bedf57178bddecc14fb84

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L72-L72

```text
The figure below shows how the worker connector works with the attention module to achieve layer-by-layer KV cache store and load:
```

### E91e2197a5b7264c744e6c9a3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **MultiConnector**: take advantage of the kv_connector_extra_config: dict[str, Any] already present in KVTransferConfig to stash all the connectors we want in an ordered list of kwargs.such as:
```

### Ef712143253f8f2b7db98d45a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **NixlConnector**: refer to <gh-file:tests/v1/kv_connector/nixl_integration/run_accuracy_test.sh> for the example usage of NixlConnector disaggregated prefilling which support fully async send/recv.
- **P2pNcclConnector**: refer to <gh-file:examples/online_serving/disaggregated_serving_p2p_nccl_xpyd/disagg_example_p2p_nccl_xpyd.sh> for the example usage of P2pNcclConnector disaggregated prefilling.
```

### E10e99aa4ba4e834098ffd9df

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L46-L48

```text
- **Pipe**: A single-direction FIFO pipe for tensor transmission.
It supports `send_tensor` and `recv_tensor`.
```

## official-010-1:dense:retrieved

历史修复 PR21611：PR21611怎样让connector区分不同多模态输入的KV？

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### E05fa3ecae9f31c8965f45edd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
\
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_connector":"SharedStorageConnector","kv_role":"kv_producer","kv_rank":0,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}' &

# decoding instance, which is the KV consumer
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_NAME \
    --port 7204 \
    --gpu-memory-utilization 0.8 \
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_co
```

### Ebf13eeb5c9f8d5c8b8e51b4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
```bash
  --kv-transfer-config '{"kv_connector":"MultiConnector","kv_role":"kv_both","kv_connector_extra_config":{"connectors":[{"kv_connector":"NixlConnector","kv_role":"kv_both"},{"kv_connector":"SharedStorageConnector","kv_role":"kv_both","kv_connector_extra_config":{"shared_storage_path":"local_storage"}}]}}'
  ```
```

### E91e2197a5b7264c744e6c9a3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **MultiConnector**: take advantage of the kv_connector_extra_config: dict[str, Any] already present in KVTransferConfig to stash all the connectors we want in an ordered list of kwargs.such as:
```

### E5a272eae0c90bf1956be01fb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L65-L66

```text
- Scheduler connector: the connector that locates in the same process as the scheduler process. It schedules the KV cache transfer ops.
- Worker connectors: the connectors that locate in the worker processes. They execute KV cache transfer ops.
```

### Ea406129230cc382d53a8775f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L68-L100

```text
pletion = client.completions.create(
        model=model,
        prompt="The future of AI is",
        echo=False,
        n=1,
        stream=stream,
    )

    print("Completion results:")
    if stream:
        for c in completion:
            print(c)
    else:
        print(completion)
    ```
```

### E76386a2d669e1a99e5aa70cf

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
```python
MODEL_NAME=models/Qwen2.5-VL-3B-Instruct/   # model path here

# a function that waits vLLM server to start
wait_for_server() {
  local port=$1
  timeout 12000 bash -c "
    until curl -s localhost:${port}/v1/chat/completions > /dev/null; do
      sleep 1
    done" && return 0 || return 1
}

# prefilling instance, which is the KV producer
CUDA_VISIBLE_DEVICES=0 vllm serve $MODEL_NAME \
    --port 7104 \
    --gpu-memory-utilization 0.8 
```

### Ed1e1300af58c1464e44b128e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
nnector":"SharedStorageConnector","kv_role":"kv_consumer","kv_rank":1,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}'  &

# wait until prefill and decode instances are ready
wait_for_server 7104
wait_for_server 7204

# launch the proxy server
python3 examples/online_serving/disaggregated_serving/disagg_proxy_demo.py  \
    --model $MODEL_NAME  \
    --prefill localhost:7104   \
    --decode localh
```

## official-010-1:hybrid:retrieved

历史修复 PR21611：PR21611怎样让connector区分不同多模态输入的KV？

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### Ebf13eeb5c9f8d5c8b8e51b4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
```bash
  --kv-transfer-config '{"kv_connector":"MultiConnector","kv_role":"kv_both","kv_connector_extra_config":{"connectors":[{"kv_connector":"NixlConnector","kv_role":"kv_both"},{"kv_connector":"SharedStorageConnector","kv_role":"kv_both","kv_connector_extra_config":{"shared_storage_path":"local_storage"}}]}}'
  ```
```

### E05fa3ecae9f31c8965f45edd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
\
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_connector":"SharedStorageConnector","kv_role":"kv_producer","kv_rank":0,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}' &

# decoding instance, which is the KV consumer
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_NAME \
    --port 7204 \
    --gpu-memory-utilization 0.8 \
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_co
```

### E5a272eae0c90bf1956be01fb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L65-L66

```text
- Scheduler connector: the connector that locates in the same process as the scheduler process. It schedules the KV cache transfer ops.
- Worker connectors: the connectors that locate in the worker processes. They execute KV cache transfer ops.
```

### E4d858f31046eaf432dd1fbe6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L46-L48

```text
- **Connector**: Connector allows **kv consumer** to retrieve the KV caches of a batch of request from **kv producer**.
- **LookupBuffer**: LookupBuffer provides two API: `insert` KV cache and `drop_select` KV cache.
The semantics of `insert` and `drop_select` are similar to SQL, where `insert` inserts a KV cache into the buffer, and `drop_select` returns the KV cache that matches the given condition and drop it from the buffer.
```

### E91e2197a5b7264c744e6c9a3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **MultiConnector**: take advantage of the kv_connector_extra_config: dict[str, Any] already present in KVTransferConfig to stash all the connectors we want in an ordered list of kwargs.such as:
```

### Ef712143253f8f2b7db98d45a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **NixlConnector**: refer to <gh-file:tests/v1/kv_connector/nixl_integration/run_accuracy_test.sh> for the example usage of NixlConnector disaggregated prefilling which support fully async send/recv.
- **P2pNcclConnector**: refer to <gh-file:examples/online_serving/disaggregated_serving_p2p_nccl_xpyd/disagg_example_p2p_nccl_xpyd.sh> for the example usage of P2pNcclConnector disaggregated prefilling.
```

### E1f35621552a76b0afad7719a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **SharedStorageConnector**: refer to <gh-file:examples/offline_inference/disaggregated-prefill-v1/run.sh> for the example usage of SharedStorageConnector disaggregated prefilling.
```

### Eca7787c4400bc8f084b7feb4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
To start the PD instances:
```

## official-010-1:hybrid_rerank:retrieved

历史修复 PR21611：PR21611怎样让connector区分不同多模态输入的KV？

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### E4a4301f57840469930f6dc45

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-pr-21611.md#L16-L18

```text
## Purpose
It brings in the mm_hashes from the Request to the connector to form a proper key; that can help distinguish kv for different mm input. It fix the problems about wrongly reusing the kv mentioned in the issue.
Support multiple multimodal inputs as well.
```

### Ebf13eeb5c9f8d5c8b8e51b4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
```bash
  --kv-transfer-config '{"kv_connector":"MultiConnector","kv_role":"kv_both","kv_connector_extra_config":{"connectors":[{"kv_connector":"NixlConnector","kv_role":"kv_both"},{"kv_connector":"SharedStorageConnector","kv_role":"kv_both","kv_connector_extra_config":{"shared_storage_path":"local_storage"}}]}}'
  ```
```

### E05fa3ecae9f31c8965f45edd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
\
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_connector":"SharedStorageConnector","kv_role":"kv_producer","kv_rank":0,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}' &

# decoding instance, which is the KV consumer
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_NAME \
    --port 7204 \
    --gpu-memory-utilization 0.8 \
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_co
```

### E4d858f31046eaf432dd1fbe6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L46-L48

```text
- **Connector**: Connector allows **kv consumer** to retrieve the KV caches of a batch of request from **kv producer**.
- **LookupBuffer**: LookupBuffer provides two API: `insert` KV cache and `drop_select` KV cache.
The semantics of `insert` and `drop_select` are similar to SQL, where `insert` inserts a KV cache into the buffer, and `drop_select` returns the KV cache that matches the given condition and drop it from the buffer.
```

### E91e2197a5b7264c744e6c9a3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **MultiConnector**: take advantage of the kv_connector_extra_config: dict[str, Any] already present in KVTransferConfig to stash all the connectors we want in an ordered list of kwargs.such as:
```

### Ef712143253f8f2b7db98d45a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **NixlConnector**: refer to <gh-file:tests/v1/kv_connector/nixl_integration/run_accuracy_test.sh> for the example usage of NixlConnector disaggregated prefilling which support fully async send/recv.
- **P2pNcclConnector**: refer to <gh-file:examples/online_serving/disaggregated_serving_p2p_nccl_xpyd/disagg_example_p2p_nccl_xpyd.sh> for the example usage of P2pNcclConnector disaggregated prefilling.
```

### E1f35621552a76b0afad7719a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **SharedStorageConnector**: refer to <gh-file:examples/offline_inference/disaggregated-prefill-v1/run.sh> for the example usage of SharedStorageConnector disaggregated prefilling.
```

### Eca7787c4400bc8f084b7feb4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
To start the PD instances:
```

## official-010-2:oracle:oracle

历史修复 PR21611：相同文本和相同图像尺寸是否足以安全复用多模态KV？

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### E18e46086d71bc6f871bfc38e

https://github.com/vllm-project/vllm/pull/21611

```text
It brings in the mm_hashes from the Request to the connector to form a proper key; that can help distinguish kv for different mm input.
```

## official-010-2:bm25:retrieved

历史修复 PR21611：相同文本和相同图像尺寸是否足以安全复用多模态KV？

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### Ebf13eeb5c9f8d5c8b8e51b4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
```bash
  --kv-transfer-config '{"kv_connector":"MultiConnector","kv_role":"kv_both","kv_connector_extra_config":{"connectors":[{"kv_connector":"NixlConnector","kv_role":"kv_both"},{"kv_connector":"SharedStorageConnector","kv_role":"kv_both","kv_connector_extra_config":{"shared_storage_path":"local_storage"}}]}}'
  ```
```

### Ebdbca0e91344eb6949640f00

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L1-L1

```text
# Quantized KV Cache
```

### E05fa3ecae9f31c8965f45edd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
\
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_connector":"SharedStorageConnector","kv_role":"kv_producer","kv_rank":0,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}' &

# decoding instance, which is the KV consumer
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_NAME \
    --port 7204 \
    --gpu-memory-utilization 0.8 \
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_co
```

### E4d858f31046eaf432dd1fbe6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L46-L48

```text
- **Connector**: Connector allows **kv consumer** to retrieve the KV caches of a batch of request from **kv producer**.
- **LookupBuffer**: LookupBuffer provides two API: `insert` KV cache and `drop_select` KV cache.
The semantics of `insert` and `drop_select` are similar to SQL, where `insert` inserts a KV cache into the buffer, and `drop_select` returns the KV cache that matches the given condition and drop it from the buffer.
```

### E3880baf52cf3de41e8738304

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L3-L5

```text
## FP8 KV Cache

Quantizing the KV cache to FP8 reduces its memory footprint. This increases the number of tokens that can be stored in the cache, improving throughput.
```

### E91e2197a5b7264c744e6c9a3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **MultiConnector**: take advantage of the kv_connector_extra_config: dict[str, Any] already present in KVTransferConfig to stash all the connectors we want in an ordered list of kwargs.such as:
```

### Ef712143253f8f2b7db98d45a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **NixlConnector**: refer to <gh-file:tests/v1/kv_connector/nixl_integration/run_accuracy_test.sh> for the example usage of NixlConnector disaggregated prefilling which support fully async send/recv.
- **P2pNcclConnector**: refer to <gh-file:examples/online_serving/disaggregated_serving_p2p_nccl_xpyd/disagg_example_p2p_nccl_xpyd.sh> for the example usage of P2pNcclConnector disaggregated prefilling.
```

### E1f35621552a76b0afad7719a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **SharedStorageConnector**: refer to <gh-file:examples/offline_inference/disaggregated-prefill-v1/run.sh> for the example usage of SharedStorageConnector disaggregated prefilling.
```

### Eca7787c4400bc8f084b7feb4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
To start the PD instances:
```

## official-010-2:dense:retrieved

历史修复 PR21611：相同文本和相同图像尺寸是否足以安全复用多模态KV？

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### E8713fd87b381389222fcfab8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L8-L22

```text
### 🐛 Describe the bug
**I use the model Qwen2.5-VL-3B-Instruct for V1 PD disaggregation with 1 image input;
Everything is fine until I sent 2 different requests, with identical text prompt, but different input images in same image size.
It wrongly reuses KV for the later request, which cause it wrongly returning an identical output with the previous request.**
```

### Eaa5eccb906fb3493a09ec874

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L76-L136

```text
struct-FP8-KV
    SAVE_DIR = MODEL_ID.split("/")[1] + "-FP8-KV"
    model.save_pretrained(SAVE_DIR, save_compressed=True)
    tokenizer.save_pretrained(SAVE_DIR)
    ```
```

### E2c3ff3a79fd187d92d82bca6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1196-L1217

```text
printf("Atom value: %d\n", *ptr);
```

### Ef875130d2ac8c37dc2ed476c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L12-L19

```text
- [ ] batch mm for FP8 optimization on rocm
- [x] composable kernel block gemm https://github.com/sgl-project/sglang/pull/4075
```

### E244cf1481157d5ae32dc6ea7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L177-L182

```text
- GLM-4.5V GLM-4.1V (<gh-pr:23168>)
- Kimi-VL (<gh-pr:23817>)
- Llama4 (<gh-pr:18368>)
- MiniCPM-V-2.5 or above (<gh-pr:23327>, <gh-pr:23948>)
- Qwen2.5-VL (<gh-pr:22742>)
- Step3 (<gh-pr:22697>)
```

### Eae0ae5713c85163e541b9944

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L8-L22

```text
**I use the `SharedStorageConnector` to faciliate the v1 PD disagg;
but I guess there is no design/implementation for this issue yet for other connector as well?
```

### E80b3f3e5e667bb50735373d9

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L8-L22

```text
**
I tried these requests in a single instance (PD mix) case, and a 1P1D disaggregation case in V1.
The outputs in PD disagg are similar/identical to the outputs from PD mix;
Prefiller encode the mm_input, then prefill, then Decoder can successfully load KV stored from Prefiller and give decent results.
I think we can assume that V1 PD disagg with mm input works fine in general, _except for below bug situation:
```

### Eb199d09bc0d6303b9c2c05e5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L8-L22

```text
```python
# prompt:
#  {"type": "text", "text": "Repeat all below: What is following the sequence 1 3 5 7 9 11 13 15 17 19 21 23 25 27 29 31 33 35 37 39 41 43 45 47 49 51 53 55 57 59 61 63 65 67 69 71? Repeat the whole sequence; What is in the image? Write in around 100 words; Lastly, End your answer with the word `BYE`"},
```
I use the exact same text prompt for every following request.
```

### E12e6d4cab91fc461d1986f51

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L76-L136

```text
v_cache_scheme:
                    num_bits: 8
                    type: float
                    strategy: tensor
                    dynamic: false
                    symmetric: true
    """

    # Apply quantization
    oneshot(
        model=model,
        dataset=ds,
        recipe=recipe,
        max_seq_length=MAX_SEQUENCE_LENGTH,
        num_calibration_samples=NUM_CALIBRATION_SAMPLES,
    )

    # Save quantized model: Llama-3.1-8B-In
```

### Efba151b46e3fa3c2f60f2cc5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L76-L136

```text
(example["messages"], tokenize=False)
        return tokenizer(
            text,
            padding=False,
            max_length=MAX_SEQUENCE_LENGTH,
            truncation=True,
```

## official-010-2:hybrid:retrieved

历史修复 PR21611：相同文本和相同图像尺寸是否足以安全复用多模态KV？

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### Ea8fa7763be809659577e2faa

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L1-L1

```text
# [Bug]: Wrongly reuse KV, for V1 PD disaggregation with multimodal input
```

### E05fa3ecae9f31c8965f45edd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
\
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_connector":"SharedStorageConnector","kv_role":"kv_producer","kv_rank":0,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}' &

# decoding instance, which is the KV consumer
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_NAME \
    --port 7204 \
    --gpu-memory-utilization 0.8 \
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_co
```

### E92661bb4894e8ef80693d008

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L77-L84

```text
| `SGLANG_CI_SMALL_KV_SIZE` | Use small KV cache size in CI | Not set |
```

### Eaa5eccb906fb3493a09ec874

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L76-L136

```text
struct-FP8-KV
    SAVE_DIR = MODEL_ID.split("/")[1] + "-FP8-KV"
    model.save_pretrained(SAVE_DIR, save_compressed=True)
    tokenizer.save_pretrained(SAVE_DIR)
    ```
```

### E16ef5342b23dd9999061414a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L37-L52

```text
nt(out)
    ```
The `kv_cache_dtype` argument specifies the data type for KV cache storage:
```

### E76386a2d669e1a99e5aa70cf

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
```python
MODEL_NAME=models/Qwen2.5-VL-3B-Instruct/   # model path here

# a function that waits vLLM server to start
wait_for_server() {
  local port=$1
  timeout 12000 bash -c "
    until curl -s localhost:${port}/v1/chat/completions > /dev/null; do
      sleep 1
    done" && return 0 || return 1
}

# prefilling instance, which is the KV producer
CUDA_VISIBLE_DEVICES=0 vllm serve $MODEL_NAME \
    --port 7104 \
    --gpu-memory-utilization 0.8 
```

### Ed1e1300af58c1464e44b128e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
nnector":"SharedStorageConnector","kv_role":"kv_consumer","kv_rank":1,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}'  &

# wait until prefill and decode instances are ready
wait_for_server 7104
wait_for_server 7204

# launch the proxy server
python3 examples/online_serving/disaggregated_serving/disagg_proxy_demo.py  \
    --model $MODEL_NAME  \
    --prefill localhost:7104   \
    --decode localh
```

### Eca7787c4400bc8f084b7feb4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
To start the PD instances:
```

### Ef9dcf75b0d93b6dcd5172b33

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
ost:7204   \
    --port 9774
```
```

### E695ba05057649c70fdf10c01

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L77-L84

```text
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_IS_IN_CI` | Indicates if running in CI environment | `false` |
| `SGLANG_AMD_CI` | Indicates running in AMD CI environment | `0` |
| `SGLANG_TEST_RETRACT` | Enable retract decode testing | `false` |
```

## official-010-2:hybrid_rerank:retrieved

历史修复 PR21611：相同文本和相同图像尺寸是否足以安全复用多模态KV？

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### E8a66c157f288954c72338e6d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L41-L46

```text
<img width="1841" height="851" alt="Image4" src="https://github.com/user-attachments/assets/da9eb806-f328-46c0-9901-42bd9eed93b9" />
**This is likely due to the fact that, the key for KV transfer only depends on prompt_token_ids;
Where number of placeholder tokens in it would be the same for different images with the same image size.
I think this issue happen not only in SharedStorageConnector, but in V1 PD disagg in general?
```

### E8713fd87b381389222fcfab8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L8-L22

```text
### 🐛 Describe the bug
**I use the model Qwen2.5-VL-3B-Instruct for V1 PD disaggregation with 1 image input;
Everything is fine until I sent 2 different requests, with identical text prompt, but different input images in same image size.
It wrongly reuses KV for the later request, which cause it wrongly returning an identical output with the previous request.**
```

### Ebf13eeb5c9f8d5c8b8e51b4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
```bash
  --kv-transfer-config '{"kv_connector":"MultiConnector","kv_role":"kv_both","kv_connector_extra_config":{"connectors":[{"kv_connector":"NixlConnector","kv_role":"kv_both"},{"kv_connector":"SharedStorageConnector","kv_role":"kv_both","kv_connector_extra_config":{"shared_storage_path":"local_storage"}}]}}'
  ```
```

### Eaa5eccb906fb3493a09ec874

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L76-L136

```text
struct-FP8-KV
    SAVE_DIR = MODEL_ID.split("/")[1] + "-FP8-KV"
    model.save_pretrained(SAVE_DIR, save_compressed=True)
    tokenizer.save_pretrained(SAVE_DIR)
    ```
```

### E05fa3ecae9f31c8965f45edd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
\
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_connector":"SharedStorageConnector","kv_role":"kv_producer","kv_rank":0,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}' &

# decoding instance, which is the KV consumer
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_NAME \
    --port 7204 \
    --gpu-memory-utilization 0.8 \
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_co
```

### E470bac3892e3d98145e4a3eb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L41-L46

```text
### **Request 4 with Image C, after emptying shared_storage_path (Abnormal):**
**This one is even weird;
even I emptied the shared_storage_path and send request with Image C again.
However, the output is still identical with Image B**
**I need to restart the PD instances and emptied the shared_storage_path to give proper output for Image C**
```

### Eff94daff240a59597904ac88

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L41-L46

```text
Since I didn't find any design specifically for multimodal V1 PD disagg?
**
```

## official-010-3:oracle:oracle

历史修复 PR21611：SharedStorageConnector因图片变化返回旧答案，应核对修复中的哪项缓存键信息？

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### E18e46086d71bc6f871bfc38e

https://github.com/vllm-project/vllm/pull/21611

```text
It brings in the mm_hashes from the Request to the connector to form a proper key; that can help distinguish kv for different mm input.
```

## official-010-3:bm25:retrieved

历史修复 PR21611：SharedStorageConnector因图片变化返回旧答案，应核对修复中的哪项缓存键信息？

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### E1f35621552a76b0afad7719a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **SharedStorageConnector**: refer to <gh-file:examples/offline_inference/disaggregated-prefill-v1/run.sh> for the example usage of SharedStorageConnector disaggregated prefilling.
- **LMCacheConnectorV1**: refer to <gh-file:examples/others/lmcache/disagg_prefill_lmcache_v1/disagg_example_nixl.sh> for the example usage of LMCacheConnectorV1 disaggregated prefilling which uses NIXL as the underlying KV transmission.
```

### Eae0ae5713c85163e541b9944

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L8-L22

```text
**I use the `SharedStorageConnector` to faciliate the v1 PD disagg;
but I guess there is no design/implementation for this issue yet for other connector as well?
```

### Ebf13eeb5c9f8d5c8b8e51b4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
```bash
  --kv-transfer-config '{"kv_connector":"MultiConnector","kv_role":"kv_both","kv_connector_extra_config":{"connectors":[{"kv_connector":"NixlConnector","kv_role":"kv_both"},{"kv_connector":"SharedStorageConnector","kv_role":"kv_both","kv_connector_extra_config":{"shared_storage_path":"local_storage"}}]}}'
  ```
```

### E05fa3ecae9f31c8965f45edd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
\
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_connector":"SharedStorageConnector","kv_role":"kv_producer","kv_rank":0,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}' &

# decoding instance, which is the KV consumer
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_NAME \
    --port 7204 \
    --gpu-memory-utilization 0.8 \
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_co
```

### Ed1e1300af58c1464e44b128e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
nnector":"SharedStorageConnector","kv_role":"kv_consumer","kv_rank":1,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}'  &

# wait until prefill and decode instances are ready
wait_for_server 7104
wait_for_server 7204

# launch the proxy server
python3 examples/online_serving/disaggregated_serving/disagg_proxy_demo.py  \
    --model $MODEL_NAME  \
    --prefill localhost:7104   \
    --decode localh
```

### Ef712143253f8f2b7db98d45a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **NixlConnector**: refer to <gh-file:tests/v1/kv_connector/nixl_integration/run_accuracy_test.sh> for the example usage of NixlConnector disaggregated prefilling which support fully async send/recv.
- **P2pNcclConnector**: refer to <gh-file:examples/online_serving/disaggregated_serving_p2p_nccl_xpyd/disagg_example_p2p_nccl_xpyd.sh> for the example usage of P2pNcclConnector disaggregated prefilling.
```

## official-010-3:dense:retrieved

历史修复 PR21611：SharedStorageConnector因图片变化返回旧答案，应核对修复中的哪项缓存键信息？

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### E3ca4e8b5f33ffaaddf0826f7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L294-L294

```text
Managed Memory: data allocation changed to use cudaMallocManaged(), which returns a pointer valid from both host and device code.
```

### E92c63cbaa6990f7f40ed7953

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| 1 |
| `--delete-ckpt-after-loading` | Delete the model checkpoint after loading the model.
| False |
| `--enable-memory-saver` | Allow saving memory using release_memory_occupation and resume_memory_occupation.
```

### Ea2ded2b31f2140aea4caf06f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L213-L246

```text
// Requires CUDA Managed Memory support
cudaMallocManaged(&ptr, sizeof(int));
write_value<<<1, 1>>>(ptr, 1);
// Synchronize required
// (before, cudaMemcpy was synchronizing)
cudaDeviceSynchronize();
```

### E30f4f1588b2e0b8f4ba6a9db

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L964-L985

```text
Physical pages: this represents a fixed-size contiguous chunk of memory
the processor’s main Memory Management Unit (MMU) supports and into which
a virtual page can be mapped.
```

### E1a44efd926011e7236e78106

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L71-L93

```text
Here, secondary_kernel is launched after primary_kernel finishes its execution.
Serialized execution is usually necessary because secondary_kernel depends on result data
produced by primary_kernel.
If secondary_kernel has no dependency on primary_kernel,
```

### E0b415413bd6cda0c4959831f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| `--num-continuous-decode-steps` | Run multiple continuous decoding steps to reduce scheduling overhead.
This can potentially increase throughput but may also increase time-to-first-token latency.
The default value is 1, meaning only run one decoding step at a time.
```

### E6e6e1b0004adff9f846354e3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--allow-auto-truncate` | Allow automatically truncating requests that exceed the maximum input length instead of returning an error.
| False |
```

### E422366a405dddf04e1878382

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--triton-attention-num-kv-splits` | The number of KV splits in flash decoding Triton kernel.
Larger value is better in longer context scenarios.
The default value is 8.
| 8 |
```

### E18803b0fbb8c02fa4753e15a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| `--enable-custom-logit-processor` | Enable users to pass custom logit processors to the server (disabled by default for security).
```

### Ed8ee3a2fb4894a8108afd577

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--triton-attention-reduce-in-fp32` | Cast the intermediate attention results to fp32 to avoid possible crashes related to fp16.
This only affects Triton attention kernels.
```

### Eb5dc70af3f60d71d432802e9

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--flashinfer-mla-disable-ragged` | Disable ragged processing in Flashinfer MLA.
| False |
| `--disable-shared-experts-fusion` | Disable shared experts fusion.
| False |
| `--disable-chunked-prefix-cache` | Disable chunked prefix cache.
| False |
```

### E181758bd5f56316845fe0b0b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--enable-p2p-check` | Enable P2P check for GPU access, otherwise the p2p access is allowed by default.
```

## official-010-3:hybrid:retrieved

历史修复 PR21611：SharedStorageConnector因图片变化返回旧答案，应核对修复中的哪项缓存键信息？

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### E1f35621552a76b0afad7719a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **SharedStorageConnector**: refer to <gh-file:examples/offline_inference/disaggregated-prefill-v1/run.sh> for the example usage of SharedStorageConnector disaggregated prefilling.
- **LMCacheConnectorV1**: refer to <gh-file:examples/others/lmcache/disagg_prefill_lmcache_v1/disagg_example_nixl.sh> for the example usage of LMCacheConnectorV1 disaggregated prefilling which uses NIXL as the underlying KV transmission.
```

### E3ca4e8b5f33ffaaddf0826f7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L294-L294

```text
Managed Memory: data allocation changed to use cudaMallocManaged(), which returns a pointer valid from both host and device code.
```

### E92c63cbaa6990f7f40ed7953

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| 1 |
| `--delete-ckpt-after-loading` | Delete the model checkpoint after loading the model.
| False |
| `--enable-memory-saver` | Allow saving memory using release_memory_occupation and resume_memory_occupation.
```

### Eae0ae5713c85163e541b9944

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L8-L22

```text
**I use the `SharedStorageConnector` to faciliate the v1 PD disagg;
but I guess there is no design/implementation for this issue yet for other connector as well?
```

### Ebf13eeb5c9f8d5c8b8e51b4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
```bash
  --kv-transfer-config '{"kv_connector":"MultiConnector","kv_role":"kv_both","kv_connector_extra_config":{"connectors":[{"kv_connector":"NixlConnector","kv_role":"kv_both"},{"kv_connector":"SharedStorageConnector","kv_role":"kv_both","kv_connector_extra_config":{"shared_storage_path":"local_storage"}}]}}'
  ```
```

### Ef712143253f8f2b7db98d45a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **NixlConnector**: refer to <gh-file:tests/v1/kv_connector/nixl_integration/run_accuracy_test.sh> for the example usage of NixlConnector disaggregated prefilling which support fully async send/recv.
- **P2pNcclConnector**: refer to <gh-file:examples/online_serving/disaggregated_serving_p2p_nccl_xpyd/disagg_example_p2p_nccl_xpyd.sh> for the example usage of P2pNcclConnector disaggregated prefilling.
```

### E91e2197a5b7264c744e6c9a3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **MultiConnector**: take advantage of the kv_connector_extra_config: dict[str, Any] already present in KVTransferConfig to stash all the connectors we want in an ordered list of kwargs.such as:
```

### E0b415413bd6cda0c4959831f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| `--num-continuous-decode-steps` | Run multiple continuous decoding steps to reduce scheduling overhead.
This can potentially increase throughput but may also increase time-to-first-token latency.
The default value is 1, meaning only run one decoding step at a time.
```

### E6e6e1b0004adff9f846354e3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--allow-auto-truncate` | Allow automatically truncating requests that exceed the maximum input length instead of returning an error.
| False |
```

## official-010-3:hybrid_rerank:retrieved

历史修复 PR21611：SharedStorageConnector因图片变化返回旧答案，应核对修复中的哪项缓存键信息？

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### Ebf13eeb5c9f8d5c8b8e51b4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
```bash
  --kv-transfer-config '{"kv_connector":"MultiConnector","kv_role":"kv_both","kv_connector_extra_config":{"connectors":[{"kv_connector":"NixlConnector","kv_role":"kv_both"},{"kv_connector":"SharedStorageConnector","kv_role":"kv_both","kv_connector_extra_config":{"shared_storage_path":"local_storage"}}]}}'
  ```
```

### E8a66c157f288954c72338e6d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L41-L46

```text
<img width="1841" height="851" alt="Image4" src="https://github.com/user-attachments/assets/da9eb806-f328-46c0-9901-42bd9eed93b9" />
**This is likely due to the fact that, the key for KV transfer only depends on prompt_token_ids;
Where number of placeholder tokens in it would be the same for different images with the same image size.
I think this issue happen not only in SharedStorageConnector, but in V1 PD disagg in general?
```

### E05fa3ecae9f31c8965f45edd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
\
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_connector":"SharedStorageConnector","kv_role":"kv_producer","kv_rank":0,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}' &

# decoding instance, which is the KV consumer
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_NAME \
    --port 7204 \
    --gpu-memory-utilization 0.8 \
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_co
```

### Ed1e1300af58c1464e44b128e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
nnector":"SharedStorageConnector","kv_role":"kv_consumer","kv_rank":1,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}'  &

# wait until prefill and decode instances are ready
wait_for_server 7104
wait_for_server 7204

# launch the proxy server
python3 examples/online_serving/disaggregated_serving/disagg_proxy_demo.py  \
    --model $MODEL_NAME  \
    --prefill localhost:7104   \
    --decode localh
```

### Ed4f06f541c224ddec79dc11c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L213-L223

```text
Next, we need to read the key token data from `k_ptr` and store
them on register memory as `k_vecs`.
We use register memory for
`k_vecs` because it will only be accessed by one thread once,
whereas `q_vecs` will be accessed by multiple threads multiple
```

### E91e2197a5b7264c744e6c9a3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **MultiConnector**: take advantage of the kv_connector_extra_config: dict[str, Any] already present in KVTransferConfig to stash all the connectors we want in an ordered list of kwargs.such as:
```

### E470bac3892e3d98145e4a3eb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L41-L46

```text
### **Request 4 with Image C, after emptying shared_storage_path (Abnormal):**
**This one is even weird;
```

## official-010-4:oracle:oracle

历史修复 PR21611：先从Issue21175辨认错误输出与KV复用的关系，再说明PR21611在哪个输入身份信息上修复了connector缓存键。

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。；Issue描述不同图像请求误复用KV；对应PR通过请求mm_hashes修正connector键。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### E18e46086d71bc6f871bfc38e

https://github.com/vllm-project/vllm/pull/21611

```text
It brings in the mm_hashes from the Request to the connector to form a proper key; that can help distinguish kv for different mm input.
```

### E93cdc8547a8299b08b7dc5aa

https://github.com/vllm-project/vllm/issues/21175

```text
It wrongly reuses KV for the later request, which cause it wrongly returning an identical output with the previous request.
```

## official-010-4:bm25:retrieved

历史修复 PR21611：先从Issue21175辨认错误输出与KV复用的关系，再说明PR21611在哪个输入身份信息上修复了connector缓存键。

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。；Issue描述不同图像请求误复用KV；对应PR通过请求mm_hashes修正connector键。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### Ebf13eeb5c9f8d5c8b8e51b4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
```bash
  --kv-transfer-config '{"kv_connector":"MultiConnector","kv_role":"kv_both","kv_connector_extra_config":{"connectors":[{"kv_connector":"NixlConnector","kv_role":"kv_both"},{"kv_connector":"SharedStorageConnector","kv_role":"kv_both","kv_connector_extra_config":{"shared_storage_path":"local_storage"}}]}}'
  ```
```

### E5a272eae0c90bf1956be01fb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L65-L66

```text
- Scheduler connector: the connector that locates in the same process as the scheduler process. It schedules the KV cache transfer ops.
- Worker connectors: the connectors that locate in the worker processes. They execute KV cache transfer ops.
```

### E4d858f31046eaf432dd1fbe6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L46-L48

```text
- **Connector**: Connector allows **kv consumer** to retrieve the KV caches of a batch of request from **kv producer**.
- **LookupBuffer**: LookupBuffer provides two API: `insert` KV cache and `drop_select` KV cache.
The semantics of `insert` and `drop_select` are similar to SQL, where `insert` inserts a KV cache into the buffer, and `drop_select` returns the KV cache that matches the given condition and drop it from the buffer.
```

### E05fa3ecae9f31c8965f45edd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
\
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_connector":"SharedStorageConnector","kv_role":"kv_producer","kv_rank":0,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}' &

# decoding instance, which is the KV consumer
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_NAME \
    --port 7204 \
    --gpu-memory-utilization 0.8 \
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_co
```

### Eac6bedf57178bddecc14fb84

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L72-L72

```text
The figure below shows how the worker connector works with the attention module to achieve layer-by-layer KV cache store and load:
```

### E91e2197a5b7264c744e6c9a3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **MultiConnector**: take advantage of the kv_connector_extra_config: dict[str, Any] already present in KVTransferConfig to stash all the connectors we want in an ordered list of kwargs.such as:
```

### Ef712143253f8f2b7db98d45a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **NixlConnector**: refer to <gh-file:tests/v1/kv_connector/nixl_integration/run_accuracy_test.sh> for the example usage of NixlConnector disaggregated prefilling which support fully async send/recv.
- **P2pNcclConnector**: refer to <gh-file:examples/online_serving/disaggregated_serving_p2p_nccl_xpyd/disagg_example_p2p_nccl_xpyd.sh> for the example usage of P2pNcclConnector disaggregated prefilling.
```

### E10e99aa4ba4e834098ffd9df

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L46-L48

```text
- **Pipe**: A single-direction FIFO pipe for tensor transmission.
It supports `send_tensor` and `recv_tensor`.
```

## official-010-4:dense:retrieved

历史修复 PR21611：先从Issue21175辨认错误输出与KV复用的关系，再说明PR21611在哪个输入身份信息上修复了connector缓存键。

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。；Issue描述不同图像请求误复用KV；对应PR通过请求mm_hashes修正connector键。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### E5a272eae0c90bf1956be01fb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L65-L66

```text
- Scheduler connector: the connector that locates in the same process as the scheduler process. It schedules the KV cache transfer ops.
- Worker connectors: the connectors that locate in the worker processes. They execute KV cache transfer ops.
```

### E2fdb4e0f1129e35b4342448b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-page-locked-host-memory.md#L17-L21

```text
Note

Page-locked host memory is not cached on non I/O coherent Tegra devices. Also, cudaHostRegister() is not supported on non I/O coherent Tegra devices.

The simple zero-copy CUDA sample comes with a detailed document on the page-locked memory APIs.
```

### E91e2197a5b7264c744e6c9a3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **MultiConnector**: take advantage of the kv_connector_extra_config: dict[str, Any] already present in KVTransferConfig to stash all the connectors we want in an ordered list of kwargs.such as:
```

### E05fa3ecae9f31c8965f45edd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
\
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_connector":"SharedStorageConnector","kv_role":"kv_producer","kv_rank":0,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}' &

# decoding instance, which is the KV consumer
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_NAME \
    --port 7204 \
    --gpu-memory-utilization 0.8 \
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_co
```

### Ebf13eeb5c9f8d5c8b8e51b4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
```bash
  --kv-transfer-config '{"kv_connector":"MultiConnector","kv_role":"kv_both","kv_connector_extra_config":{"connectors":[{"kv_connector":"NixlConnector","kv_role":"kv_both"},{"kv_connector":"SharedStorageConnector","kv_role":"kv_both","kv_connector_extra_config":{"shared_storage_path":"local_storage"}}]}}'
  ```
```

### Ef712143253f8f2b7db98d45a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **NixlConnector**: refer to <gh-file:tests/v1/kv_connector/nixl_integration/run_accuracy_test.sh> for the example usage of NixlConnector disaggregated prefilling which support fully async send/recv.
- **P2pNcclConnector**: refer to <gh-file:examples/online_serving/disaggregated_serving_p2p_nccl_xpyd/disagg_example_p2p_nccl_xpyd.sh> for the example usage of P2pNcclConnector disaggregated prefilling.
```

### E1f35621552a76b0afad7719a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **SharedStorageConnector**: refer to <gh-file:examples/offline_inference/disaggregated-prefill-v1/run.sh> for the example usage of SharedStorageConnector disaggregated prefilling.
- **LMCacheConnectorV1**: refer to <gh-file:examples/others/lmcache/disagg_prefill_lmcache_v1/disagg_example_nixl.sh> for the example usage of LMCacheConnectorV1 disaggregated prefilling which uses NIXL as the underlying KV transmission.
```

## official-010-4:hybrid:retrieved

历史修复 PR21611：先从Issue21175辨认错误输出与KV复用的关系，再说明PR21611在哪个输入身份信息上修复了connector缓存键。

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。；Issue描述不同图像请求误复用KV；对应PR通过请求mm_hashes修正connector键。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### E5a272eae0c90bf1956be01fb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L65-L66

```text
- Scheduler connector: the connector that locates in the same process as the scheduler process. It schedules the KV cache transfer ops.
- Worker connectors: the connectors that locate in the worker processes. They execute KV cache transfer ops.
```

### Ebf13eeb5c9f8d5c8b8e51b4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
```bash
  --kv-transfer-config '{"kv_connector":"MultiConnector","kv_role":"kv_both","kv_connector_extra_config":{"connectors":[{"kv_connector":"NixlConnector","kv_role":"kv_both"},{"kv_connector":"SharedStorageConnector","kv_role":"kv_both","kv_connector_extra_config":{"shared_storage_path":"local_storage"}}]}}'
  ```
```

### E05fa3ecae9f31c8965f45edd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
\
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_connector":"SharedStorageConnector","kv_role":"kv_producer","kv_rank":0,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}' &

# decoding instance, which is the KV consumer
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_NAME \
    --port 7204 \
    --gpu-memory-utilization 0.8 \
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_co
```

### E4d858f31046eaf432dd1fbe6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L46-L48

```text
- **Connector**: Connector allows **kv consumer** to retrieve the KV caches of a batch of request from **kv producer**.
- **LookupBuffer**: LookupBuffer provides two API: `insert` KV cache and `drop_select` KV cache.
The semantics of `insert` and `drop_select` are similar to SQL, where `insert` inserts a KV cache into the buffer, and `drop_select` returns the KV cache that matches the given condition and drop it from the buffer.
```

### E91e2197a5b7264c744e6c9a3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **MultiConnector**: take advantage of the kv_connector_extra_config: dict[str, Any] already present in KVTransferConfig to stash all the connectors we want in an ordered list of kwargs.such as:
```

### Ef712143253f8f2b7db98d45a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **NixlConnector**: refer to <gh-file:tests/v1/kv_connector/nixl_integration/run_accuracy_test.sh> for the example usage of NixlConnector disaggregated prefilling which support fully async send/recv.
- **P2pNcclConnector**: refer to <gh-file:examples/online_serving/disaggregated_serving_p2p_nccl_xpyd/disagg_example_p2p_nccl_xpyd.sh> for the example usage of P2pNcclConnector disaggregated prefilling.
```

### E1f35621552a76b0afad7719a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **SharedStorageConnector**: refer to <gh-file:examples/offline_inference/disaggregated-prefill-v1/run.sh> for the example usage of SharedStorageConnector disaggregated prefilling.
```

### Eca7787c4400bc8f084b7feb4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
To start the PD instances:
```

## official-010-4:hybrid_rerank:retrieved

历史修复 PR21611：先从Issue21175辨认错误输出与KV复用的关系，再说明PR21611在哪个输入身份信息上修复了connector缓存键。

必要要点：修复把请求的mm_hashes带入connector缓存键，区分不同多模态输入。；Issue描述不同图像请求误复用KV；对应PR通过请求mm_hashes修正connector键。

禁止误读：图像只需尺寸一致便能安全共用KV。

```json
null
```

实际输入证据：

### Ebf13eeb5c9f8d5c8b8e51b4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
```bash
  --kv-transfer-config '{"kv_connector":"MultiConnector","kv_role":"kv_both","kv_connector_extra_config":{"connectors":[{"kv_connector":"NixlConnector","kv_role":"kv_both"},{"kv_connector":"SharedStorageConnector","kv_role":"kv_both","kv_connector_extra_config":{"shared_storage_path":"local_storage"}}]}}'
  ```
```

### E4d858f31046eaf432dd1fbe6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L46-L48

```text
- **Connector**: Connector allows **kv consumer** to retrieve the KV caches of a batch of request from **kv producer**.
- **LookupBuffer**: LookupBuffer provides two API: `insert` KV cache and `drop_select` KV cache.
The semantics of `insert` and `drop_select` are similar to SQL, where `insert` inserts a KV cache into the buffer, and `drop_select` returns the KV cache that matches the given condition and drop it from the buffer.
```

### E05fa3ecae9f31c8965f45edd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
\
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_connector":"SharedStorageConnector","kv_role":"kv_producer","kv_rank":0,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}' &

# decoding instance, which is the KV consumer
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_NAME \
    --port 7204 \
    --gpu-memory-utilization 0.8 \
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_co
```

### E4a4301f57840469930f6dc45

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-pr-21611.md#L16-L18

```text
## Purpose
It brings in the mm_hashes from the Request to the connector to form a proper key; that can help distinguish kv for different mm input. It fix the problems about wrongly reusing the kv mentioned in the issue.
Support multiple multimodal inputs as well.
```

### Ef5713c7016ca2f5b08be9e52

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-pr-21611.md#L30-L194

```text
| 0/1 [00:00<?, ?it/s, est. speed input: 0.00 toks/s, output: 0.00 toks/s]WARNING 07-30 02:52:29 [shared_storage_connector.py:152] In connector.start_load_kv, but the attn_metadata is None
Processed prompts: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  3.21it/s, est. speed input: 131.84 toks/s, output: 128.62 toks/s]
----------------------------------------------
```

### E91e2197a5b7264c744e6c9a3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **MultiConnector**: take advantage of the kv_connector_extra_config: dict[str, Any] already present in KVTransferConfig to stash all the connectors we want in an ordered list of kwargs.such as:
```

### Ef712143253f8f2b7db98d45a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **NixlConnector**: refer to <gh-file:tests/v1/kv_connector/nixl_integration/run_accuracy_test.sh> for the example usage of NixlConnector disaggregated prefilling which support fully async send/recv.
```

### Ecab0c87413552287f8b5d591

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-pr-21611.md#L30-L194

```text
========
```

## official-012-1:oracle:oracle

SGLang v0.5.2：频繁出现queue-req为零提示什么供给问题？

必要要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### Ea9500a277e9c122d80741822

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/hyperparameter_tuning.md

```text
If you frequently see `#queue-req: 0`, it suggests that your client code is submitting requests too slowly.
```

## official-012-1:bm25:retrieved

SGLang v0.5.2：频繁出现queue-req为零提示什么供给问题？

必要要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### E63c1f7fb51b02d051c9fafca

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
```Decode batch. #running-req: 233, #token: 370959, token usage: 0.82, cuda graph: True, gen throughput (token/s): 4594.01, #queue-req: 317```

### Adjust the request submission speed to control `#queue-req`

`#queue-req` indicates the number of requests in the queue.
If you frequently see `#queue-req: 0`, it suggests that your client code is submitting requests too slowly.
A healthy range for `#queue-req` is `100 - 2000`.
However, avoid making `
```

### Ed0e655fecbc0130e94eda744

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
#queue-req` too large, as this will increase the scheduling overhead on the server.

### Achieve a high `token usage`

`token usage` indicates the KV cache memory utilization of the server. `token usage > 0.9` means good utilization.

If you frequently see `token usage < 0.9` and `#queue-req > 0`, it means the server is too conservative about taking in new requests. You can decrease `--schedule-conservativeness` to a value like 0.3.
The case of a
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### Ec6ce229e909fa8499eeb7ef0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L194-L198

```text
![Free queue after a request us freed](../assets/design/prefix_caching/free.png)
```

### E44817ba471505d1b42c1b7c6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
server being too conservative can happen when users send many requests with a large `max_new_tokens` but the requests stop very early due to EOS or stop strings.

On the other hand, if you see `token usage` very high and you frequently see warnings like
`KV cache pool is full. Retract requests. #retracted_reqs: 1, #new_token_ratio: 0.9998 -> 1.0000`, you can increase `--schedule-conservativeness` to a value like 1.3.
If you see `KV cache pool is 
```

### E36b43e89ddc1aefb338ba4e4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
full. Retract requests.` occasionally but not frequently, it is okay.

### Tune `--mem-fraction-static` to increase KV cache pool capacity
SGLang allocates memory as follows:

Total memory usage = model weights + KV cache pool + CUDA graph buffers + activations

The `--mem-fraction-static` parameter determines how much memory is allocated to the first two components:
```

## official-012-1:dense:retrieved

SGLang v0.5.2：频繁出现queue-req为零提示什么供给问题？

必要要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### Ee19acae85ef1e4928d1f3ffd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L332-L359

```text
// If the graph fails to update, errorNode will be set to the
// node causing the failure and updateResult will be set to a
// reason code.
cudaGraphExecUpdate(graphExec, graph, &errorNode, &updateResult);
```

### E0980d4a98ece9c6b02c1f27e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L113-L135

```text
SGLang supports the following quantization methods based on torchao `["int8dq", "int8wo", "fp8wo", "fp8dq-per_tensor", "fp8dq-per_row", "int4wo-32", "int4wo-64", "int4wo-128", "int4wo-256"]`.
```

### E140ba685af5b7d8bee1b3fe0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L137-L145

```text
Note: According to [this issue](https://github.com/sgl-project/sglang/issues/2219#issuecomment-2561890230), `"int8dq"` method currently has some bugs when using together with cuda graph capture.
So we suggest to disable cuda graph capture when using `"int8dq"` method.
```

### E8713fd87b381389222fcfab8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L8-L22

```text
### 🐛 Describe the bug
**I use the model Qwen2.5-VL-3B-Instruct for V1 PD disaggregation with 1 image input;
Everything is fine until I sent 2 different requests, with identical text prompt, but different input images in same image size.
It wrongly reuses KV for the later request, which cause it wrongly returning an identical output with the previous request.**
```

### E63c1f7fb51b02d051c9fafca

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
```Decode batch. #running-req: 233, #token: 370959, token usage: 0.82, cuda graph: True, gen throughput (token/s): 4594.01, #queue-req: 317```

### Adjust the request submission speed to control `#queue-req`

`#queue-req` indicates the number of requests in the queue.
If you frequently see `#queue-req: 0`, it suggests that your client code is submitting requests too slowly.
A healthy range for `#queue-req` is `100 - 2000`.
However, avoid making `
```

### Ee396e1ce5cf25468ff4a6a78

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L332-L359

```text
// If we've already instantiated the graph, try to update it directly
// and avoid the instantiation overhead
if (graphExec !
= NULL) {
```

### Eecb060d2ff28c292d752deb5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L332-L359

```text
}
// Instantiate during the first iteration or whenever the update
// fails for any reason
if (graphExec == NULL || updateResult !
= cudaGraphExecUpdateSuccess) {
```

### E99e6f9817e0d05486615a1df

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L332-L359

```text
cudaGraphExec_t graphExec = NULL;
for (int i = 0;
i < 10;
i++) {
cudaGraph_t graph;
cudaGraphExecUpdateResult updateResult;
cudaGraphNode_t errorNode;
// In this example we use stream capture to create the graph.
// You can also use the Graph API to produce a graph.
cudaStreamBeginCapture(stream, cudaStreamCaptureModeGlobal);
// Call a user-defined, stream based workload, for example
do_cuda_work(stream);
cudaStreamEndCapture(stream, &graph);
```

### E80b3f3e5e667bb50735373d9

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L8-L22

```text
**
```

## official-012-1:hybrid:retrieved

SGLang v0.5.2：频繁出现queue-req为零提示什么供给问题？

必要要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### E63c1f7fb51b02d051c9fafca

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
```Decode batch. #running-req: 233, #token: 370959, token usage: 0.82, cuda graph: True, gen throughput (token/s): 4594.01, #queue-req: 317```

### Adjust the request submission speed to control `#queue-req`

`#queue-req` indicates the number of requests in the queue.
If you frequently see `#queue-req: 0`, it suggests that your client code is submitting requests too slowly.
A healthy range for `#queue-req` is `100 - 2000`.
However, avoid making `
```

### Ed0e655fecbc0130e94eda744

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
#queue-req` too large, as this will increase the scheduling overhead on the server.

### Achieve a high `token usage`

`token usage` indicates the KV cache memory utilization of the server. `token usage > 0.9` means good utilization.

If you frequently see `token usage < 0.9` and `#queue-req > 0`, it means the server is too conservative about taking in new requests. You can decrease `--schedule-conservativeness` to a value like 0.3.
The case of a
```

### E2529bb21ff333e194f7b349c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L58-L66

```text
| **`SGLANG_DISAGGREGATION_QUEUE_SIZE`** | Sets the number of parallel transfer queues.
KVCache transfer requests from multiple decode instances will be sharded into these queues so that they can share the threads and the transfer bandwidth at the same time.
If it is set to `1`, then we transfer requests one by one according to fcfs strategy | `4` |
```

### E8d5d5a418248458ed0da3d26

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L232-L232

```text
**Time 7: Request 2 comes in with the 29 prompt tokens, where the first 12 tokens are the same as request 0\.** Note that even the block order in the free queue was `7 - 8 - 9 - 4 - 3 - 2 - 6 - 5 - 1 - 0`, the cache hit blocks (i.e., 0, 1, 2) are touched and removed from the queue before allocation, so the free queue becomes `7 - 8 - 9 - 4 - 3 - 6 - 5`.
```

### E8dc2fb2a5fca69b5d1a146b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L1-L3

```text
# SGLang Router

The SGLang Router is a high-performance request distribution system that routes inference requests across multiple SGLang runtime instances. It features cache-aware load balancing, fault tolerance, and support for advanced deployment patterns including data parallelism and prefill-decode disaggregation.
```

### E44817ba471505d1b42c1b7c6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
server being too conservative can happen when users send many requests with a large `max_new_tokens` but the requests stop very early due to EOS or stop strings.

On the other hand, if you see `token usage` very high and you frequently see warnings like
`KV cache pool is full. Retract requests. #retracted_reqs: 1, #new_token_ratio: 0.9998 -> 1.0000`, you can increase `--schedule-conservativeness` to a value like 1.3.
If you see `KV cache pool is 
```

### E36b43e89ddc1aefb338ba4e4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
full. Retract requests.` occasionally but not frequently, it is okay.

### Tune `--mem-fraction-static` to increase KV cache pool capacity
SGLang allocates memory as follows:
```

## official-012-1:hybrid_rerank:retrieved

SGLang v0.5.2：频繁出现queue-req为零提示什么供给问题？

必要要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### E63c1f7fb51b02d051c9fafca

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
```Decode batch. #running-req: 233, #token: 370959, token usage: 0.82, cuda graph: True, gen throughput (token/s): 4594.01, #queue-req: 317```

### Adjust the request submission speed to control `#queue-req`

`#queue-req` indicates the number of requests in the queue.
If you frequently see `#queue-req: 0`, it suggests that your client code is submitting requests too slowly.
A healthy range for `#queue-req` is `100 - 2000`.
However, avoid making `
```

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### Ed0e655fecbc0130e94eda744

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
#queue-req` too large, as this will increase the scheduling overhead on the server.

### Achieve a high `token usage`

`token usage` indicates the KV cache memory utilization of the server. `token usage > 0.9` means good utilization.

If you frequently see `token usage < 0.9` and `#queue-req > 0`, it means the server is too conservative about taking in new requests. You can decrease `--schedule-conservativeness` to a value like 0.3.
The case of a
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ebcc291b3c6bc07b25f46a8f6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L17-L17

```text
Below are a few key settings to confirm or enable for SGLang:
```

### E44817ba471505d1b42c1b7c6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
server being too conservative can happen when users send many requests with a large `max_new_tokens` but the requests stop very early due to EOS or stop strings.

On the other hand, if you see `token usage` very high and you frequently see warnings like
`KV cache pool is full. Retract requests. #retracted_reqs: 1, #new_token_ratio: 0.9998 -> 1.0000`, you can increase `--schedule-conservativeness` to a value like 1.3.
If you see `KV cache pool is 
```

### E36b43e89ddc1aefb338ba4e4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
full. Retract requests.` occasionally but not frequently, it is okay.

### Tune `--mem-fraction-static` to increase KV cache pool capacity
SGLang allocates memory as follows:

Total memory usage = model weights + KV cache pool + CUDA graph buffers + activations

The `--mem-fraction-static` parameter determines how much memory is allocated to the first two components:
```

## official-012-2:oracle:oracle

SGLang v0.5.2：能否仅凭queue-req为零就判定GPU太慢？

必要要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### Ea9500a277e9c122d80741822

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/hyperparameter_tuning.md

```text
If you frequently see `#queue-req: 0`, it suggests that your client code is submitting requests too slowly.
```

## official-012-2:bm25:retrieved

SGLang v0.5.2：能否仅凭queue-req为零就判定GPU太慢？

必要要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### E63c1f7fb51b02d051c9fafca

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
```Decode batch. #running-req: 233, #token: 370959, token usage: 0.82, cuda graph: True, gen throughput (token/s): 4594.01, #queue-req: 317```

### Adjust the request submission speed to control `#queue-req`

`#queue-req` indicates the number of requests in the queue.
If you frequently see `#queue-req: 0`, it suggests that your client code is submitting requests too slowly.
A healthy range for `#queue-req` is `100 - 2000`.
However, avoid making `
```

### Ed0e655fecbc0130e94eda744

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
#queue-req` too large, as this will increase the scheduling overhead on the server.

### Achieve a high `token usage`

`token usage` indicates the KV cache memory utilization of the server. `token usage > 0.9` means good utilization.

If you frequently see `token usage < 0.9` and `#queue-req > 0`, it means the server is too conservative about taking in new requests. You can decrease `--schedule-conservativeness` to a value like 0.3.
The case of a
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E836c7d1b89a88031ebc19bb7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
You can install the frontend locally without needing a GPU, while the backend can be set up on a GPU-enabled machine.
To install the frontend, run `pip install sglang`, and for the backend, use `pip install sglang[srt]`.
`srt` is the abbreviation of SGLang runtime.
```

### E44817ba471505d1b42c1b7c6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
server being too conservative can happen when users send many requests with a large `max_new_tokens` but the requests stop very early due to EOS or stop strings.

On the other hand, if you see `token usage` very high and you frequently see warnings like
`KV cache pool is full. Retract requests. #retracted_reqs: 1, #new_token_ratio: 0.9998 -> 1.0000`, you can increase `--schedule-conservativeness` to a value like 1.3.
If you see `KV cache pool is 
```

### E36b43e89ddc1aefb338ba4e4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
full. Retract requests.` occasionally but not frequently, it is okay.

### Tune `--mem-fraction-static` to increase KV cache pool capacity
SGLang allocates memory as follows:
```

### Ed40ac9f26230255755dbb880

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
## Common Notes
```

## official-012-2:dense:retrieved

SGLang v0.5.2：能否仅凭queue-req为零就判定GPU太慢？

必要要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### Eac21656670164d7db38d4f80

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L1-L3

```text
# AMD GPUs

This document describes how run SGLang on AMD GPUs. If you encounter issues or have questions, please [open an issue](https://github.com/sgl-project/sglang/issues).
```

### E6afafdfed2155ebcdad03682

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1291-L1303

```text
x = 10;
}
int main() {
kernel<<< 1, 1 >>>();
y = 20;
// Error on GPUs not supporting concurrent access
```

### Ec0e109a6d70f396afd71fe32

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L103-L120

```text
| 0 |
| `--gpu-id-step` | The delta between consecutive GPU IDs that are used.
For example, setting it to 2 will use GPU 0,2,4,....
```

### Ee5403a25cedd554bda9e4410

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L9-L27

```text
It can also be used together with tensor parallelism.
The following command uses 4 GPUs in total.
We recommend [SGLang Router](../advanced_features/router.md) for data parallelism.
```bash
  python -m sglang_router.launch_server --model-path meta-llama/Meta-Llama-3-8B-Instruct --dp 2 --tp 2
  ```
```

### E7eb06a8bf569c4754c22e656

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L76-L83

```text
```python
from vllm import LLM

# Split model across 4 GPUs
llm = LLM(model="meta-llama/Llama-3.3-70B-Instruct", tensor_parallel_size=4)
```

For models that are too large to fit on a single GPU (like 70B parameter models), tensor parallelism is essential.
```

### E8d9788e2fec987ac9991ed00

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1291-L1303

```text
It is not permitted for the CPU to access any managed allocations or variables while the GPU is active for devices with concurrentManagedAccess property set to 0.
On these systems concurrent CPU/GPU accesses, even to different managed memory allocations, will cause a segmentation fault because the page is considered inaccessible to the CPU.
__device__ __managed__ int x, y=2;
__global__  void  kernel() {
```

### Eba2c124f5b8f8a483119e75d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1291-L1303

```text
When managed data is used with cudaMemcpy*() or cudaMemset*(), the system may choose to access the source or destination from the host or the device, which will put constraints on concurrent CPU access to that data while the cudaMemcpy*() or cudaMemset*() is executing.
See Memcpy()/Memset() Behavior With Unified Memory for further details.
```

### Ef947a90e798b789bc19b08f5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1291-L1303

```text
24.3.2.4.1.
GPU Exclusive Access To Managed Memory
To ensure coherency on pre-6.x GPU architectures, the Unified Memory programming model puts constraints on data accesses while both the CPU and GPU are executing concurrently.
In effect, the GPU has exclusive access to all managed data while any kernel operation is executing, regardless of whether the specific kernel is actively using the data.
```

### E175b282840cfad46b8e903d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L103-L120

```text
| None |
| `--base-gpu-id` | The base GPU ID to start allocating GPUs from.
Useful when running multiple instances on the same machine.
```

### E3b5e85b6565ab8ef9ef531b3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L103-L120

```text
| 1 |
| `--sleep-on-idle` | Reduce CPU usage when sglang is idle.
| False |
```

## official-012-2:hybrid:retrieved

SGLang v0.5.2：能否仅凭queue-req为零就判定GPU太慢？

必要要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### E836c7d1b89a88031ebc19bb7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
You can install the frontend locally without needing a GPU, while the backend can be set up on a GPU-enabled machine.
To install the frontend, run `pip install sglang`, and for the backend, use `pip install sglang[srt]`.
`srt` is the abbreviation of SGLang runtime.
```

### Eac21656670164d7db38d4f80

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L1-L3

```text
# AMD GPUs

This document describes how run SGLang on AMD GPUs. If you encounter issues or have questions, please [open an issue](https://github.com/sgl-project/sglang/issues).
```

### E63c1f7fb51b02d051c9fafca

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
```Decode batch. #running-req: 233, #token: 370959, token usage: 0.82, cuda graph: True, gen throughput (token/s): 4594.01, #queue-req: 317```

### Adjust the request submission speed to control `#queue-req`

`#queue-req` indicates the number of requests in the queue.
If you frequently see `#queue-req: 0`, it suggests that your client code is submitting requests too slowly.
A healthy range for `#queue-req` is `100 - 2000`.
However, avoid making `
```

### E6afafdfed2155ebcdad03682

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1291-L1303

```text
x = 10;
}
int main() {
kernel<<< 1, 1 >>>();
y = 20;
// Error on GPUs not supporting concurrent access
```

### Ed0e655fecbc0130e94eda744

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
#queue-req` too large, as this will increase the scheduling overhead on the server.

### Achieve a high `token usage`

`token usage` indicates the KV cache memory utilization of the server. `token usage > 0.9` means good utilization.

If you frequently see `token usage < 0.9` and `#queue-req > 0`, it means the server is too conservative about taking in new requests. You can decrease `--schedule-conservativeness` to a value like 0.3.
The case of a
```

### E60efa2876c564037d25230c7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
- To reinstall flashinfer locally, use the following command: `pip3 install --upgrade flashinfer-python --force-reinstall --no-deps` and then delete the cache with `rm -rf ~/.cache/flashinfer`.
- If you only need to use OpenAI API models with the frontend language, you can avoid installing other dependencies by using `pip install "sglang[openai]"`.
- The language frontend operates independently of the backend runtime.
```

### Eb87769bfc3e391ac8b6ece77

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
It only supports sm75 and above.
If you encounter any FlashInfer-related issues on sm75+ devices (e.g., T4, A10, A100, L4, L40S, H100), please switch to other kernels by adding `--attention-backend triton --sampling-backend pytorch` and open an issue on GitHub.
```

### Ed40ac9f26230255755dbb880

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
## Common Notes
- [FlashInfer](https://github.com/flashinfer-ai/flashinfer) is the default attention kernel backend.
```

### E44817ba471505d1b42c1b7c6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
server being too conservative can happen when users send many requests with a large `max_new_tokens` but the requests stop very early due to EOS or stop strings.

On the other hand, if you see `token usage` very high and you frequently see warnings like
`KV cache pool is full. Retract requests.
```

## official-012-2:hybrid_rerank:retrieved

SGLang v0.5.2：能否仅凭queue-req为零就判定GPU太慢？

必要要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E3f1061b966c2797da48780ab

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L135-L141

```text
```bash
$ python -m sglang.launch_server --model-path meta-llama/Llama-3.1-8B-Instruct --disaggregation-mode prefill --disaggregation-transfer-backend ascend
$ python -m sglang.launch_server --model-path meta-llama/Llama-3.1-8B-Instruct --disaggregation-mode decode --port 30001 --base-gpu-id 1 --disaggregation-transfer-backend ascend
$ python -m sglang_router.launch_router --pd-disaggregation --prefill http://127.0.0.1:30000 --decode http://127.0
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### E836c7d1b89a88031ebc19bb7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
You can install the frontend locally without needing a GPU, while the backend can be set up on a GPU-enabled machine.
To install the frontend, run `pip install sglang`, and for the backend, use `pip install sglang[srt]`.
`srt` is the abbreviation of SGLang runtime.
```

### E2e0224661ab7fc43f42f6b78

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
### Tune `--dp-size` and `--tp-size`
Data parallelism is better for throughput.
When there is enough GPU memory, always favor data parallelism for throughput.
Refer to [sglang router](../advanced_features/router.md) for a better data parallelism rather than using `dp_size` parameter.
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

### Ebceb65a7a0b9e639d13e6c61

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L135-L141

```text
### Llama Single Node
```

### E4d234ddedc7cd56f48081503

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L135-L141

```text
.0.1:30001 --host 0.0.0.0 --port 8000
```
```

### E60efa2876c564037d25230c7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
- To reinstall flashinfer locally, use the following command: `pip3 install --upgrade flashinfer-python --force-reinstall --no-deps` and then delete the cache with `rm -rf ~/.cache/flashinfer`.
- If you only need to use OpenAI API models with the frontend language, you can avoid installing other dependencies by using `pip install "sglang[openai]"`.
- The language frontend operates independently of the backend runtime.
```

### Eb87769bfc3e391ac8b6ece77

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
It only supports sm75 and above.
```

### Ed40ac9f26230255755dbb880

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
## Common Notes
- [FlashInfer](https://github.com/flashinfer-ai/flashinfer) is the default attention kernel backend.
```

## official-012-3:oracle:oracle

SGLang v0.5.2：离线吞吐低且队列经常为空，应先检查请求提交的哪一环？

必要要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### Ea9500a277e9c122d80741822

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/hyperparameter_tuning.md

```text
If you frequently see `#queue-req: 0`, it suggests that your client code is submitting requests too slowly.
```

## official-012-3:bm25:retrieved

SGLang v0.5.2：离线吞吐低且队列经常为空，应先检查请求提交的哪一环？

必要要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E8651ea1f0391d57e95cc940c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L1-L3

```text
# Install SGLang

You can install SGLang using one of the methods below.
```

### E1ff39d43ec8ef2cc491f4d4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L39-L41

```text
## Install SGLang

You can install SGLang using one of the methods below.
```

### E8dc2fb2a5fca69b5d1a146b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L1-L3

```text
# SGLang Router

The SGLang Router is a high-performance request distribution system that routes inference requests across multiple SGLang runtime instances. It features cache-aware load balancing, fault tolerance, and support for advanced deployment patterns including data parallelism and prefill-decode disaggregation.
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

## official-012-3:dense:retrieved

SGLang v0.5.2：离线吞吐低且队列经常为空，应先检查请求提交的哪一环？

必要要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### E10678bf2f844017fcf791376

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L68-L73

```text
| **`SGLANG_DISAGGREGATION_WAITING_TIMEOUT`** | Timeout (seconds) for receiving KV Cache after request initialization | `300` |
```

### E92661bb4894e8ef80693d008

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L77-L84

```text
| `SGLANG_CI_SMALL_KV_SIZE` | Use small KV cache size in CI | Not set |
```

### E3974950a05db59fcd2cd1715

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L58-L66

```text
| **`SGLANG_DISAGGREGATION_BOOTSTRAP_TIMEOUT`** | Timeout (seconds) for receiving destination KV indices during request initialization | `300` |
If a greater mean TTFT is acceptable, you can `export SGLANG_DISAGGREGATION_BOOTSTRAP_TIMEOUT=600` (10 minutes) to relax the timeout condition.
```

### Ec047ac1b84d7d208150dd28b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L43-L50

```text
| `SGL_DISABLE_TP_MEMORY_INBALANCE_CHECK` | Disable checks for memory imbalance across Tensor Parallel ranks | Not set (defaults to enabled check) |
```

### E8dc2fb2a5fca69b5d1a146b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L1-L3

```text
# SGLang Router

The SGLang Router is a high-performance request distribution system that routes inference requests across multiple SGLang runtime instances. It features cache-aware load balancing, fault tolerance, and support for advanced deployment patterns including data parallelism and prefill-decode disaggregation.
```

### E088b076a6d681481616767d5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L68-L73

```text
#### Decode Server Configuration
| Variable | Description | Default |
|:--------:|:-----------:|:--------:
| **`SGLANG_DISAGGREGATION_HEARTBEAT_INTERVAL`** | Interval (seconds) between health checks to prefill bootstrap servers | `5.0` |
| **`SGLANG_DISAGGREGATION_HEARTBEAT_MAX_FAILURE`** | Consecutive heartbeat failures before marking prefill server offline | `2` |
```

### E695ba05057649c70fdf10c01

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L77-L84

```text
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_IS_IN_CI` | Indicates if running in CI environment | `false` |
| `SGLANG_AMD_CI` | Indicates running in AMD CI environment | `0` |
| `SGLANG_TEST_RETRACT` | Enable retract decode testing | `false` |
| `SGLANG_RECORD_STEP_TIME` | Record step time for profiling | `false` |
| `SGLANG_TEST_REQUEST_TIME_STATS` | Test request time statistics | `false` |
```

### E2529bb21ff333e194f7b349c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L58-L66

```text
| **`SGLANG_DISAGGREGATION_QUEUE_SIZE`** | Sets the number of parallel transfer queues.
KVCache transfer requests from multiple decode instances will be sharded into these queues so that they can share the threads and the transfer bandwidth at the same time.
If it is set to `1`, then we transfer requests one by one according to fcfs strategy | `4` |
```

### Ec703ef76078527f6fe777012

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L58-L66

```text
Please be aware that this setting will cause prefill instances to take a longer time to clean up the affected memory resources when a running decode node loses connection.
```

### E57df5f9102a1da2e155a7609

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L58-L66

```text
#### Prefill Server Configuration
| Variable | Description | Default |
|:--------:|:-----------:|:--------:
```

## official-012-3:hybrid:retrieved

SGLang v0.5.2：离线吞吐低且队列经常为空，应先检查请求提交的哪一环？

必要要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### E8dc2fb2a5fca69b5d1a146b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L1-L3

```text
# SGLang Router

The SGLang Router is a high-performance request distribution system that routes inference requests across multiple SGLang runtime instances. It features cache-aware load balancing, fault tolerance, and support for advanced deployment patterns including data parallelism and prefill-decode disaggregation.
```

### E836c7d1b89a88031ebc19bb7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
You can install the frontend locally without needing a GPU, while the backend can be set up on a GPU-enabled machine.
To install the frontend, run `pip install sglang`, and for the backend, use `pip install sglang[srt]`.
`srt` is the abbreviation of SGLang runtime.
```

### Ed05566d3e7ac4a78756bcd14

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L115-L124

```text
3.
To further scale up your deployment with autoscaling and failure recovery, check out the [SkyServe + SGLang guide](https://github.com/skypilot-org/skypilot/tree/master/llm/sglang#serving-llama-2-with-sglang-for-more-traffic-using-skyserve).
```

### E3b5e85b6565ab8ef9ef531b3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L103-L120

```text
| 1 |
| `--sleep-on-idle` | Reduce CPU usage when sglang is idle.
| False |
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### E60efa2876c564037d25230c7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
- To reinstall flashinfer locally, use the following command: `pip3 install --upgrade flashinfer-python --force-reinstall --no-deps` and then delete the cache with `rm -rf ~/.cache/flashinfer`.
- If you only need to use OpenAI API models with the frontend language, you can avoid installing other dependencies by using `pip install "sglang[openai]"`.
- The language frontend operates independently of the backend runtime.
```

### Eb87769bfc3e391ac8b6ece77

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
It only supports sm75 and above.
If you encounter any FlashInfer-related issues on sm75+ devices (e.g., T4, A10, A100, L4, L40S, H100), please switch to other kernels by adding `--attention-backend triton --sampling-backend pytorch` and open an issue on GitHub.
```

### Ed40ac9f26230255755dbb880

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
## Common Notes
- [FlashInfer](https://github.com/flashinfer-ai/flashinfer) is the default attention kernel backend.
```

### E7c8946eeb476097a2e4b6b07

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L115-L124

```text
```bash
# Deploy on any cloud or Kubernetes cluster. Use --cloud <cloud> to select a specific cloud provider.
HF_TOKEN=<secret> sky launch -c sglang --env HF_TOKEN sglang.yaml

# Get the HTTP API endpoint
sky status --endpoint 30000 sglang
```
```

### E828f1a4e40173d58251bca51

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L115-L124

```text
</details>
```

### Ec0e109a6d70f396afd71fe32

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L103-L120

```text
| 0 |
| `--gpu-id-step` | The delta between consecutive GPU IDs that are used.
For example, setting it to 2 will use GPU 0,2,4,....
```

### E175b282840cfad46b8e903d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L103-L120

```text
| None |
```

## official-012-3:hybrid_rerank:retrieved

SGLang v0.5.2：离线吞吐低且队列经常为空，应先检查请求提交的哪一环？

必要要点：频繁队列为空提示客户端提交速度可能太慢。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ebcc291b3c6bc07b25f46a8f6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L17-L17

```text
Below are a few key settings to confirm or enable for SGLang:
```

### E8dc2fb2a5fca69b5d1a146b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L1-L3

```text
# SGLang Router

The SGLang Router is a high-performance request distribution system that routes inference requests across multiple SGLang runtime instances. It features cache-aware load balancing, fault tolerance, and support for advanced deployment patterns including data parallelism and prefill-decode disaggregation.
```

### E3974950a05db59fcd2cd1715

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L58-L66

```text
| **`SGLANG_DISAGGREGATION_BOOTSTRAP_TIMEOUT`** | Timeout (seconds) for receiving destination KV indices during request initialization | `300` |
If a greater mean TTFT is acceptable, you can `export SGLANG_DISAGGREGATION_BOOTSTRAP_TIMEOUT=600` (10 minutes) to relax the timeout condition.
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

### E2529bb21ff333e194f7b349c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L58-L66

```text
| **`SGLANG_DISAGGREGATION_QUEUE_SIZE`** | Sets the number of parallel transfer queues.
KVCache transfer requests from multiple decode instances will be sharded into these queues so that they can share the threads and the transfer bandwidth at the same time.
If it is set to `1`, then we transfer requests one by one according to fcfs strategy | `4` |
```

### Ec703ef76078527f6fe777012

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L58-L66

```text
Please be aware that this setting will cause prefill instances to take a longer time to clean up the affected memory resources when a running decode node loses connection.
```

### E57df5f9102a1da2e155a7609

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L58-L66

```text
#### Prefill Server Configuration
| Variable | Description | Default |
|:--------:|:-----------:|:--------:
| **`SGLANG_DISAGGREGATION_THREAD_POOL_SIZE`** | Controls the total number of worker threads for KVCache transfer operations per TP rank | A dynamic value calculated by `int(0.75 * os.cpu_count()) // 8)`, which is limited to be larger than 4 and less than 12 to ensure efficiency and prevent thread race conditions |
```

## official-012-4:oracle:oracle

SGLang v0.5.2：先根据queue-req诊断客户端供给，再查服务器内存参数默认值，为什么不能把默认0.9当作队列为空的直接根因？

必要要点：频繁队列为空提示客户端提交速度可能太慢。；先检查队列供给而非直接加大内存；mem-fraction-static默认0.9不是所有低吞吐现象的解决办法。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### Ea9500a277e9c122d80741822

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/hyperparameter_tuning.md

```text
If you frequently see `#queue-req: 0`, it suggests that your client code is submitting requests too slowly.
```

### E4dce99978561336895057e92

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/server_arguments.md

```text
The default value is `0.9`.
```

## official-012-4:bm25:retrieved

SGLang v0.5.2：先根据queue-req诊断客户端供给，再查服务器内存参数默认值，为什么不能把默认0.9当作队列为空的直接根因？

必要要点：频繁队列为空提示客户端提交速度可能太慢。；先检查队列供给而非直接加大内存；mem-fraction-static默认0.9不是所有低吞吐现象的解决办法。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### E63c1f7fb51b02d051c9fafca

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
```Decode batch. #running-req: 233, #token: 370959, token usage: 0.82, cuda graph: True, gen throughput (token/s): 4594.01, #queue-req: 317```

### Adjust the request submission speed to control `#queue-req`

`#queue-req` indicates the number of requests in the queue.
If you frequently see `#queue-req: 0`, it suggests that your client code is submitting requests too slowly.
A healthy range for `#queue-req` is `100 - 2000`.
However, avoid making `
```

### Ed0e655fecbc0130e94eda744

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
#queue-req` too large, as this will increase the scheduling overhead on the server.

### Achieve a high `token usage`

`token usage` indicates the KV cache memory utilization of the server. `token usage > 0.9` means good utilization.

If you frequently see `token usage < 0.9` and `#queue-req > 0`, it means the server is too conservative about taking in new requests. You can decrease `--schedule-conservativeness` to a value like 0.3.
The case of a
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E0f4f4d685998aef8e888d8b9

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L9-L27

```text
- If you see out-of-memory errors during serving, try to reduce the memory usage of the KV cache pool by setting a smaller value of `--mem-fraction-static`.
The default value is `0.9`.
```

### E44817ba471505d1b42c1b7c6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
server being too conservative can happen when users send many requests with a large `max_new_tokens` but the requests stop very early due to EOS or stop strings.

On the other hand, if you see `token usage` very high and you frequently see warnings like
`KV cache pool is full. Retract requests. #retracted_reqs: 1, #new_token_ratio: 0.9998 -> 1.0000`, you can increase `--schedule-conservativeness` to a value like 1.3.
If you see `KV cache pool is 
```

### E36b43e89ddc1aefb338ba4e4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
full. Retract requests.` occasionally but not frequently, it is okay.

### Tune `--mem-fraction-static` to increase KV cache pool capacity
SGLang allocates memory as follows:

Total memory usage = model weights + KV cache pool + CUDA graph buffers + activations
```

## official-012-4:dense:retrieved

SGLang v0.5.2：先根据queue-req诊断客户端供给，再查服务器内存参数默认值，为什么不能把默认0.9当作队列为空的直接根因？

必要要点：频繁队列为空提示客户端提交速度可能太慢。；先检查队列供给而非直接加大内存；mem-fraction-static默认0.9不是所有低吞吐现象的解决办法。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### Eeff17fd2ef9b5329fccfd502

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L574-L587

```text
mykernel<<<(N + TPB - 1) / TPB, TPB, 0, s>>>(data, N);
// execute on GPU
location = {.type = cudaMemLocationTypeHost};
cudaMemPrefetchAsync(data, N, location, s, 0 /* flags */);
// prefetch to CPU
```

### E0bda9d8005b12499e7a4d11a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L589-L603

```text
mykernel<<<(N + TPB - 1) / TPB, TPB, 0, s>>>(data, N);
// execute on GPU
location = {.type = cudaMemLocationTypeHost};
cudaMemPrefetchAsync(data, N, location, s, 0 /* flags */);
// prefetch to CPU
```

### Ed95ac8dc82b8bb9f1719f401

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-streams.md#L100-L119

```text
}
...
for (size_t i = 0;
i < 2;
++i) {
cudaMemcpyAsync(devPtrIn[i], hostPtr[i], size, cudaMemcpyHostToDevice, stream[i]);
MyKernel<<<100, 512, 0, stream[i]>>>(devPtrOut[i], devPtrIn[i], size);
cudaMemcpyAsync(hostPtr[i], devPtrOut[i], size, cudaMemcpyDeviceToHost, stream[i]);
cudaLaunchHostFunc(stream[i], MyCallback, (void*)i);
```

### E7ea1bf8edde07ab763204e6f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-streams.md#L84-L98

```text
MyKernel<<<100, 512, 0, stream[i]>>>
(outputDevPtr + i * size, inputDevPtr + i * size, size);
for (int i = 0;
i < 2;
++i)
cudaMemcpyAsync(hostPtr + i * size, outputDevPtr + i * size,
size, cudaMemcpyDeviceToHost, stream[i]);
then the memory copy from host to device issued to stream[1] overlaps with the kernel launch issued to stream[0].
```

### E6ce7d333d624340905d309c3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L656-L677

```text
Passing in a value of cudaMemLocationTypeHost for location.type sets the preferred location as CPU memory.
Other hints, like cudaMemPrefetchAsync, may override this hint,
leading the memory to be migrated away from its preferred location.
```

### E50c474b99d138b120edc0d74

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L574-L587

```text
System Allocator
void test_prefetch_sam(cudaStream_t s) {
char *data = (char*)malloc(N);
init_data(data, N);
// execute on CPU
cudaMemLocation location = {.type = cudaMemLocationTypeDevice, .id = myGpuId};
cudaMemPrefetchAsync(data, N, location, s, 0 /* flags */);
// prefetch to GPU
```

### Eee466a28f2038b6ac124e645

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L574-L587

```text
cudaStreamSynchronize(s);
use_data(data, N);
free(data);
}
```

### Eb09a14de4b65a8718d6c9f01

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L589-L603

```text
// execute on CPU
cudaMemLocation location = {.type = cudaMemLocationTypeDevice, .id = myGpuId};
cudaMemPrefetchAsync(data, N, location, s, 0 /* flags */);
// prefetch to GPU
```

### E13b18885cb8495677d9f6495

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L589-L603

```text
cudaStreamSynchronize(s);
use_data(data, N);
cudaFree(data);
}
```

### E52ec56a9d4444256a742d13a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L589-L603

```text
Managed
void test_prefetch_managed(cudaStream_t s) {
char *data;
cudaMallocManaged(&data, N);
init_data(data, N);
```

### E87a7b2de97d41a2f3b2e49c4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-streams.md#L100-L119

```text
}
```

## official-012-4:hybrid:retrieved

SGLang v0.5.2：先根据queue-req诊断客户端供给，再查服务器内存参数默认值，为什么不能把默认0.9当作队列为空的直接根因？

必要要点：频繁队列为空提示客户端提交速度可能太慢。；先检查队列供给而非直接加大内存；mem-fraction-static默认0.9不是所有低吞吐现象的解决办法。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### E3c3a3dc7ba007d74b5c8b0ce

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L7-L16

```text
## General Configuration
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_USE_MODELSCOPE` | Enable using models from ModelScope | `false` |
| `SGLANG_HOST_IP` | Host IP address for the server | `0.0.0.0` |
| `SGLANG_PORT` | Port for the server | auto-detected |
| `SGLANG_LOGGING_CONFIG_PATH` | Custom logging configuration path | Not set |
| `SGLANG_DISABLE_REQUEST_LOGGING` | Disable request logging | `false` |
```

### Eeff17fd2ef9b5329fccfd502

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L574-L587

```text
mykernel<<<(N + TPB - 1) / TPB, TPB, 0, s>>>(data, N);
// execute on GPU
location = {.type = cudaMemLocationTypeHost};
cudaMemPrefetchAsync(data, N, location, s, 0 /* flags */);
// prefetch to CPU
```

### E63c1f7fb51b02d051c9fafca

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
```Decode batch. #running-req: 233, #token: 370959, token usage: 0.82, cuda graph: True, gen throughput (token/s): 4594.01, #queue-req: 317```

### Adjust the request submission speed to control `#queue-req`

`#queue-req` indicates the number of requests in the queue.
If you frequently see `#queue-req: 0`, it suggests that your client code is submitting requests too slowly.
A healthy range for `#queue-req` is `100 - 2000`.
However, avoid making `
```

### E0bda9d8005b12499e7a4d11a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L589-L603

```text
mykernel<<<(N + TPB - 1) / TPB, TPB, 0, s>>>(data, N);
// execute on GPU
location = {.type = cudaMemLocationTypeHost};
cudaMemPrefetchAsync(data, N, location, s, 0 /* flags */);
// prefetch to CPU
```

### Ed0e655fecbc0130e94eda744

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
#queue-req` too large, as this will increase the scheduling overhead on the server.

### Achieve a high `token usage`

`token usage` indicates the KV cache memory utilization of the server. `token usage > 0.9` means good utilization.

If you frequently see `token usage < 0.9` and `#queue-req > 0`, it means the server is too conservative about taking in new requests. You can decrease `--schedule-conservativeness` to a value like 0.3.
The case of a
```

### E31d76b4ee496eaa10e0edd9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L7-L16

```text
| `SGLANG_HEALTH_CHECK_TIMEOUT` | Timeout for health check in seconds | `20` |
```

### E50c474b99d138b120edc0d74

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L574-L587

```text
System Allocator
void test_prefetch_sam(cudaStream_t s) {
char *data = (char*)malloc(N);
init_data(data, N);
// execute on CPU
cudaMemLocation location = {.type = cudaMemLocationTypeDevice, .id = myGpuId};
cudaMemPrefetchAsync(data, N, location, s, 0 /* flags */);
// prefetch to GPU
```

### Eee466a28f2038b6ac124e645

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L574-L587

```text
cudaStreamSynchronize(s);
use_data(data, N);
free(data);
}
```

### E44817ba471505d1b42c1b7c6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
server being too conservative can happen when users send many requests with a large `max_new_tokens` but the requests stop very early due to EOS or stop strings.
```

## official-012-4:hybrid_rerank:retrieved

SGLang v0.5.2：先根据queue-req诊断客户端供给，再查服务器内存参数默认值，为什么不能把默认0.9当作队列为空的直接根因？

必要要点：频繁队列为空提示客户端提交速度可能太慢。；先检查队列供给而非直接加大内存；mem-fraction-static默认0.9不是所有低吞吐现象的解决办法。

禁止误读：队列为空必然说明GPU算力不足。

```json
null
```

实际输入证据：

### E0f4f4d685998aef8e888d8b9

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L9-L27

```text
- If you see out-of-memory errors during serving, try to reduce the memory usage of the KV cache pool by setting a smaller value of `--mem-fraction-static`.
The default value is `0.9`.
```

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### Ed0e655fecbc0130e94eda744

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
#queue-req` too large, as this will increase the scheduling overhead on the server.

### Achieve a high `token usage`

`token usage` indicates the KV cache memory utilization of the server. `token usage > 0.9` means good utilization.

If you frequently see `token usage < 0.9` and `#queue-req > 0`, it means the server is too conservative about taking in new requests. You can decrease `--schedule-conservativeness` to a value like 0.3.
The case of a
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### E3c3a3dc7ba007d74b5c8b0ce

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L7-L16

```text
## General Configuration
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_USE_MODELSCOPE` | Enable using models from ModelScope | `false` |
| `SGLANG_HOST_IP` | Host IP address for the server | `0.0.0.0` |
| `SGLANG_PORT` | Port for the server | auto-detected |
| `SGLANG_LOGGING_CONFIG_PATH` | Custom logging configuration path | Not set |
| `SGLANG_DISABLE_REQUEST_LOGGING` | Disable request logging | `false` |
```

### Ee5403a25cedd554bda9e4410

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L9-L27

```text
It can also be used together with tensor parallelism.
The following command uses 4 GPUs in total.
We recommend [SGLang Router](../advanced_features/router.md) for data parallelism.
```bash
  python -m sglang_router.launch_server --model-path meta-llama/Meta-Llama-3-8B-Instruct --dp 2 --tp 2
  ```
```

### Ebe8fb23b46c130fcafe23fa5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L9-L27

```text
```bash
  python -m sglang.launch_server --model-path meta-llama/Meta-Llama-3-8B-Instruct --mem-fraction-static 0.7
  ```
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

### E44817ba471505d1b42c1b7c6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
server being too conservative can happen when users send many requests with a large `max_new_tokens` but the requests stop very early due to EOS or stop strings.
```

## official-014-1:oracle:oracle

SGLang v0.5.2：加载预量化模型时应避免哪个重复量化动作？

必要要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

```json
null
```

实际输入证据：

### E2c2eeda1e6ae347665aeb1c9

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/quantization.md

```text
If you use a pre-quantized model, do not add `--quantization` to enable online quantization at the same time.
```

## official-014-1:bm25:retrieved

SGLang v0.5.2：加载预量化模型时应避免哪个重复量化动作？

必要要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

```json
null
```

实际输入证据：

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E8651ea1f0391d57e95cc940c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L1-L3

```text
# Install SGLang

You can install SGLang using one of the methods below.
```

### E1ff39d43ec8ef2cc491f4d4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L39-L41

```text
## Install SGLang

You can install SGLang using one of the methods below.
```

### E8dc2fb2a5fca69b5d1a146b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L1-L3

```text
# SGLang Router

The SGLang Router is a high-performance request distribution system that routes inference requests across multiple SGLang runtime instances. It features cache-aware load balancing, fault tolerance, and support for advanced deployment patterns including data parallelism and prefill-decode disaggregation.
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

## official-014-1:dense:retrieved

SGLang v0.5.2：加载预量化模型时应避免哪个重复量化动作？

必要要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

```json
null
```

实际输入证据：

### E0d564c3bb80088a446830783

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L20-L24

```text
## Offline Quantization

To load already quantized models, simply load the model weights and config. **Again, if the model has been quantized offline,
there's no need to add `--quantization` argument when starting the engine. The quantization method will be parsed from the
downloaded Hugging Face config. For example, DeepSeek V3/R1 models are already in FP8, so do not add redundant parameters.**
```

### Eed21f2e683edee6636155939

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L7-L11

```text
- **Fine-grained control**: Optionally wake up only model weights or KV cache to avoid OOM during weight updates.
```

### E34f381f18411ae2b1c63f9f3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L41-L56

```text
#### RLHF weight updates
During RLHF training, vLLM allows you to selectively wake up only the model weights or the KV cache using the tags argument in wake_up().
This fine-grained control is especially useful when updating model weights: by waking up just the weights (e.g., llm.wake_up(tags=["weights"])), you avoid allocating memory for the KV cache until after the weight update is complete.
```

### Ed9e3abcfeaef15d4450568be

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L227-L238

```text
2.
The EAGLE based draft models need to be run without tensor parallelism
(i.e.
draft_tensor_parallel_size is set to 1 in `speculative_config`), although
it is possible to run the main model using tensor parallelism (see example above).
```

### E112b956fffe3fc7785a2dec1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
## Model-Specific Options
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_USE_AITER` | Use AITER optimize implementation | `false` |
| `SGLANG_INT4_WEIGHT` | Enable INT4 weight quantization | `false` |
| `SGLANG_MOE_PADDING` | Enable MoE padding (sets padding size to 128 if value is `1`, often set to `1` in Docker builds) | `0` |
```

### Ea0310db075832529f15be1a7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L7-L11

```text
- **Frees GPU memory**: Offloads model weights to CPU RAM and discards KV cache, releasing up to 90%+ of GPU memory for other tasks.
- **Fast resume**: Quickly wake up the engine and resume inference without full model reload.
- **API endpoints**: Control sleep/wake_up state via HTTP endpoints or Python API.
- **Supports distributed workloads**: Works with tensor parallelism, pipeline parallelism, etc.
```

### Ee8e0d6e9b706922315bad75e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L41-L56

```text
This approach helps prevent GPU out-of-memory (OOM) errors, particularly with large models, by minimizing peak memory usage during weight synchronization and update operations.
Use `tags=["weights"]` or `tags=["kv_cache"]` to control which resources are restored, useful for RLHF and weight updates.
**Note** that `is_sleeping` will report `true` until all components are awake.
```

### E7410c5b87345f76dbd57a76c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L41-L56

```text
```python
# Put engine to deep sleep (level=2)
llm.sleep(level=2)
# ... Get the new weights
# Wake up only weights to avoid OOM
llm.wake_up(tags=["weights"])
# ... Update the weights
# wake up KV cache after weights are updated
llm.wake_up(tags=["kv_cache"])
```
```

## official-014-1:hybrid:retrieved

SGLang v0.5.2：加载预量化模型时应避免哪个重复量化动作？

必要要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

```json
null
```

实际输入证据：

### E2f7560e9ddf1ed421bd0d6f5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| None |
| `--model-impl` | Which implementation of the model to use.
'auto' will try to use the SGLang implementation if it exists and fall back to the Transformers implementation if no SGLang implementation is available.
'sglang' will use the SGLang model implementation.
'transformers' will use the Transformers model implementation.
```

### E836c7d1b89a88031ebc19bb7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
You can install the frontend locally without needing a GPU, while the backend can be set up on a GPU-enabled machine.
To install the frontend, run `pip install sglang`, and for the backend, use `pip install sglang[srt]`.
`srt` is the abbreviation of SGLang runtime.
```

### E8dc2fb2a5fca69b5d1a146b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L1-L3

```text
# SGLang Router

The SGLang Router is a high-performance request distribution system that routes inference requests across multiple SGLang runtime instances. It features cache-aware load balancing, fault tolerance, and support for advanced deployment patterns including data parallelism and prefill-decode disaggregation.
```

### Ec845f797c6676f4ac475e4e4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L1-L5

```text
# Environment Variables

SGLang supports various environment variables that can be used to configure its runtime behavior. This document provides a comprehensive list and aims to stay updated over time.

*Note: SGLang uses two prefixes for environment variables: `SGL_` and `SGLANG_`. This is likely due to historical reasons. While both are currently supported for different settings, future versions might consolidate them.*
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### E6804fdf269f9381d4466550f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| None |
| `--revision` | The specific model version to use.
It can be a branch name, a tag name, or a commit id.
If unspecified, will use the default version.
```

### Ee8a88173212a4442d4ce3c0a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| auto |
```

### Ee2d15087b506eeeac7be0e83

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| None |
| `--is-embedding` | Whether to use a CausalLM as an embedding model.
| False |
| `--enable-multimodal` | Enable the multimodal functionality for the served model.
If the model being served is not multimodal, nothing will happen.
```

### E3d540e49b4fde19c311617c6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| False |
| `--context-length` | The model's maximum context length.
Defaults to None (will use the value from the model's config.json instead).
```

### E80b206d968ecffa49eff982d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| auto |
| `--trust-remote-code` | Whether or not to allow for custom models defined on the Hub in their own modeling files.
```

### E36143cd5baf39cf8e41afcfa

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
'npcache' will load the weights in pytorch format and store a numpy cache to speed up the loading.
'dummy' will initialize the weights with random values, which is mainly for profiling.
'gguf' will load the weights in the gguf format.
```

### Ed00680afdd0197fff3520cee

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| None |
```

## official-014-1:hybrid_rerank:retrieved

SGLang v0.5.2：加载预量化模型时应避免哪个重复量化动作？

必要要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

```json
null
```

实际输入证据：

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### Eed21f2e683edee6636155939

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L7-L11

```text
- **Fine-grained control**: Optionally wake up only model weights or KV cache to avoid OOM during weight updates.
```

### E2f7560e9ddf1ed421bd0d6f5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| None |
| `--model-impl` | Which implementation of the model to use.
'auto' will try to use the SGLang implementation if it exists and fall back to the Transformers implementation if no SGLang implementation is available.
'sglang' will use the SGLang model implementation.
'transformers' will use the Transformers model implementation.
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ebcc291b3c6bc07b25f46a8f6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L17-L17

```text
Below are a few key settings to confirm or enable for SGLang:
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

### Ea0310db075832529f15be1a7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L7-L11

```text
- **Frees GPU memory**: Offloads model weights to CPU RAM and discards KV cache, releasing up to 90%+ of GPU memory for other tasks.
- **Fast resume**: Quickly wake up the engine and resume inference without full model reload.
- **API endpoints**: Control sleep/wake_up state via HTTP endpoints or Python API.
- **Supports distributed workloads**: Works with tensor parallelism, pipeline parallelism, etc.
```

### E6804fdf269f9381d4466550f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| None |
| `--revision` | The specific model version to use.
It can be a branch name, a tag name, or a commit id.
If unspecified, will use the default version.
```

### Ee8a88173212a4442d4ce3c0a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| auto |
```

### Ee2d15087b506eeeac7be0e83

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| None |
| `--is-embedding` | Whether to use a CausalLM as an embedding model.
| False |
| `--enable-multimodal` | Enable the multimodal functionality for the served model.
If the model being served is not multimodal, nothing will happen.
```

### E3d540e49b4fde19c311617c6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| False |
| `--context-length` | The model's maximum context length.
Defaults to None (will use the value from the model's config.json instead).
```

### E80b206d968ecffa49eff982d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| auto |
| `--trust-remote-code` | Whether or not to allow for custom models defined on the Hub in their own modeling files.
```

### Ed00680afdd0197fff3520cee

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L54-L68

```text
| None |
```

## official-014-2:oracle:oracle

SGLang v0.5.2：模型已经离线量化，是否总应再传quantization启用在线量化？

必要要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

```json
null
```

实际输入证据：

### E2c2eeda1e6ae347665aeb1c9

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/quantization.md

```text
If you use a pre-quantized model, do not add `--quantization` to enable online quantization at the same time.
```

## official-014-2:bm25:retrieved

SGLang v0.5.2：模型已经离线量化，是否总应再传quantization启用在线量化？

必要要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

```json
null
```

实际输入证据：

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E9e27ac051ce62af8450419a8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
# Quantization
SGLang supports various quantization methods, including offline quantization and online dynamic quantization.
Offline quantization loads pre-quantized model weights directly during inference.
This is required for quantization methods
such as GPTQ and AWQ, which collect and pre-compute various statistics from the original weights using the calibration dataset.
```

### E0980d4a98ece9c6b02c1f27e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L113-L135

```text
SGLang supports the following quantization methods based on torchao `["int8dq", "int8wo", "fp8wo", "fp8dq-per_tensor", "fp8dq-per_row", "int4wo-32", "int4wo-64", "int4wo-128", "int4wo-256"]`.
```

### Effe6cbd5d4289a524020e9a5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L113-L135

```text
Our team is working on supporting more online quantization methods.
SGLang will soon support methods including but not limited to `["awq", "gptq", "marlin", "gptq_marlin", "awq_marlin", "bitsandbytes", "gguf"]`.
SGLang also supports quantization methods based on [torchao](https://github.com/pytorch/ao).
You can simply specify `--torchao-config` in the command line to support this feature.
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

### Ecdc32b4e8bd9acdbd7d27b9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
Online quantization dynamically computes scaling parameters—such as the maximum/minimum values of model weights—during runtime.
Like NVIDIA FP8 training's [delayed scaling](https://docs.nvidia.com/deeplearning/transformer-engine/user-guide/examples/fp8_primer.html#Mixed-precision-training-with-FP8) mechanism, online quantization calculates the appropriate scaling factors
on-the-fly to convert high-precision weights into a lower-precision format.
```

### E72b0308bd3dc8dd15e8e2d6c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
**Note: For better performance, usability and convenience, offline quantization is recommended over online quantization.**
```

## official-014-2:dense:retrieved

SGLang v0.5.2：模型已经离线量化，是否总应再传quantization启用在线量化？

必要要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

```json
null
```

实际输入证据：

### E4a99edc287be8e7e99295b08

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L105-L105

```text
Then, you can directly use the quantized model with `SGLang`, by using the following command:
```

### E77e65b506114816eb41e9099

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-conserving_memory.md#L33-L36

```text
Statically quantized models can be downloaded from HF Hub (some popular ones are available at [Red Hat AI](https://huggingface.co/RedHatAI))
and used directly without extra configuration.

Dynamic quantization is also supported via the `quantization` option -- see [here](../features/quantization/README.md) for more details.
```

### Eb66faf21718bf2708ca32373

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L43-L67

```text
quant_config) # load model

model.quantize(calibration_dataset, batch_size=2) # quantize
model.save(quant_path) # save model
```
```

### E0d564c3bb80088a446830783

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L20-L24

```text
## Offline Quantization

To load already quantized models, simply load the model weights and config. **Again, if the model has been quantized offline,
there's no need to add `--quantization` argument when starting the engine. The quantization method will be parsed from the
downloaded Hugging Face config. For example, DeepSeek V3/R1 models are already in FP8, so do not add redundant parameters.**
```

### E8d558c88c0c1fce78b350fc8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L41-L41

```text
### Examples of Offline Model Quantization
```

### Ed113d222c40bd67cd5603407

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L43-L67

```text
```py
from datasets import load_dataset
from gptqmodel import GPTQModel, QuantizeConfig

model_id = "meta-llama/Llama-3.2-1B-Instruct"
quant_path = "Llama-3.2-1B-Instruct-gptqmodel-4bit"

calibration_dataset = load_dataset(
    "allenai/c4", data_files="en/c4-train.00001-of-01024.json.gz",
    split="train"
  ).select(range(1024))["text"]

quant_config = QuantizeConfig(bits=4, group_size=128) # quantization config
model = GPTQModel.load(model_id,
```

### E09bb5036d01e98073ac1f344

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L43-L67

```text
#### Using [GPTQModel](https://github.com/ModelCloud/GPTQModel)
```bash
# install
pip install gptqmodel --no-build-isolation -v
```
```

## official-014-2:hybrid:retrieved

SGLang v0.5.2：模型已经离线量化，是否总应再传quantization启用在线量化？

必要要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

```json
null
```

实际输入证据：

### E112b956fffe3fc7785a2dec1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
## Model-Specific Options
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_USE_AITER` | Use AITER optimize implementation | `false` |
| `SGLANG_INT4_WEIGHT` | Enable INT4 weight quantization | `false` |
| `SGLANG_MOE_PADDING` | Enable MoE padding (sets padding size to 128 if value is `1`, often set to `1` in Docker builds) | `0` |
```

### E8d558c88c0c1fce78b350fc8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L41-L41

```text
### Examples of Offline Model Quantization
```

### E77e65b506114816eb41e9099

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-conserving_memory.md#L33-L36

```text
Statically quantized models can be downloaded from HF Hub (some popular ones are available at [Red Hat AI](https://huggingface.co/RedHatAI))
and used directly without extra configuration.

Dynamic quantization is also supported via the `quantization` option -- see [here](../features/quantization/README.md) for more details.
```

### E9e27ac051ce62af8450419a8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
# Quantization
SGLang supports various quantization methods, including offline quantization and online dynamic quantization.
Offline quantization loads pre-quantized model weights directly during inference.
This is required for quantization methods
such as GPTQ and AWQ, which collect and pre-compute various statistics from the original weights using the calibration dataset.
```

### E54fe6490f3a729888b8673da

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L113-L135

```text
## Online Quantization
To enable online quantization, you can simply specify `--quantization` in the command line.
For example, you can launch the server with the following command to enable `FP8` quantization for model `meta-llama/Meta-Llama-3.1-8B-Instruct`:
```bash
python3 -m sglang.launch_server \
    --model-path meta-llama/Meta-Llama-3.1-8B-Instruct \
    --quantization fp8 \
    --port 30000 --host 0.0.0.0
```
```

### E16f7d126776da84bba5a8652

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
| `SGLANG_FORCE_FP8_MARLIN` | Force using FP8 MARLIN kernels even if other FP8 kernels are available | `false` |
| `SGLANG_ENABLE_FLASHINFER_GEMM` | Use flashinfer kernels when running blockwise fp8 GEMM on Blackwell GPUs | `false` |
| `SGLANG_SUPPORT_CUTLASS_BLOCK_FP8` | Use Cutlass kernels when running blockwise fp8 GEMM on Hopper or Blackwell GPUs | `false` |
| `SGLANG_CUTLASS_MOE` | Use Cutlass FP8 MoE kernel on Blackwell GPUs | `false` |
```

### Ecdc32b4e8bd9acdbd7d27b9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
Online quantization dynamically computes scaling parameters—such as the maximum/minimum values of model weights—during runtime.
Like NVIDIA FP8 training's [delayed scaling](https://docs.nvidia.com/deeplearning/transformer-engine/user-guide/examples/fp8_primer.html#Mixed-precision-training-with-FP8) mechanism, online quantization calculates the appropriate scaling factors
on-the-fly to convert high-precision weights into a lower-precision format.
```

### E72b0308bd3dc8dd15e8e2d6c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
**Note: For better performance, usability and convenience, offline quantization is recommended over online quantization.**
```

## official-014-2:hybrid_rerank:retrieved

SGLang v0.5.2：模型已经离线量化，是否总应再传quantization启用在线量化？

必要要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

```json
null
```

实际输入证据：

### E72b0308bd3dc8dd15e8e2d6c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
**Note: For better performance, usability and convenience, offline quantization is recommended over online quantization.**
```

### E9e27ac051ce62af8450419a8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
# Quantization
SGLang supports various quantization methods, including offline quantization and online dynamic quantization.
Offline quantization loads pre-quantized model weights directly during inference.
This is required for quantization methods
such as GPTQ and AWQ, which collect and pre-compute various statistics from the original weights using the calibration dataset.
```

### E54fe6490f3a729888b8673da

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L113-L135

```text
## Online Quantization
To enable online quantization, you can simply specify `--quantization` in the command line.
For example, you can launch the server with the following command to enable `FP8` quantization for model `meta-llama/Meta-Llama-3.1-8B-Instruct`:
```bash
python3 -m sglang.launch_server \
    --model-path meta-llama/Meta-Llama-3.1-8B-Instruct \
    --quantization fp8 \
    --port 30000 --host 0.0.0.0
```
```

### Effe6cbd5d4289a524020e9a5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L113-L135

```text
Our team is working on supporting more online quantization methods.
SGLang will soon support methods including but not limited to `["awq", "gptq", "marlin", "gptq_marlin", "awq_marlin", "bitsandbytes", "gguf"]`.
SGLang also supports quantization methods based on [torchao](https://github.com/pytorch/ao).
You can simply specify `--torchao-config` in the command line to support this feature.
```

### E7a70794e3abe0baba0df156e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L14-L18

```text
If you use a pre-quantized model, do not add `--quantization` to enable online quantization at the same time.
For popular pre-quantized models, please visit [ModelCloud](https://huggingface.co/collections/ModelCloud/vortex-673743382af0a52b2a8b9fe2)
or [NeuralMagic](https://huggingface.co/collections/neuralmagic) collections on HF for some
popular quality validated quantized models.
```

### Ecdc32b4e8bd9acdbd7d27b9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
Online quantization dynamically computes scaling parameters—such as the maximum/minimum values of model weights—during runtime.
Like NVIDIA FP8 training's [delayed scaling](https://docs.nvidia.com/deeplearning/transformer-engine/user-guide/examples/fp8_primer.html#Mixed-precision-training-with-FP8) mechanism, online quantization calculates the appropriate scaling factors
on-the-fly to convert high-precision weights into a lower-precision format.
```

### E521219ad7bd79291e77923c3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L113-L135

```text
For example, if you want to enable `int4wo-128` for model `meta-llama/Meta-Llama-3.1-8B-Instruct`, you can launch the server with the following command:
```bash
python3 -m sglang.launch_server \
    --model-path meta-llama/Meta-Llama-3.1-8B-Instruct \
    --torchao-config int4wo-128 \
    --port 30000 --host 0.0.0.0
```
```

### Eddfea029d340e1d84866aa66

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L14-L18

```text
Quantized models must be validated via benchmarks post-quantization
```

## official-014-3:oracle:oracle

SGLang v0.5.2：启动预量化模型时应如何处理用于在线量化的quantization参数？

必要要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

```json
null
```

实际输入证据：

### E2c2eeda1e6ae347665aeb1c9

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/quantization.md

```text
If you use a pre-quantized model, do not add `--quantization` to enable online quantization at the same time.
```

## official-014-3:bm25:retrieved

SGLang v0.5.2：启动预量化模型时应如何处理用于在线量化的quantization参数？

必要要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

```json
null
```

实际输入证据：

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E9e27ac051ce62af8450419a8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
# Quantization
SGLang supports various quantization methods, including offline quantization and online dynamic quantization.
Offline quantization loads pre-quantized model weights directly during inference.
This is required for quantization methods
such as GPTQ and AWQ, which collect and pre-compute various statistics from the original weights using the calibration dataset.
```

### E0980d4a98ece9c6b02c1f27e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L113-L135

```text
SGLang supports the following quantization methods based on torchao `["int8dq", "int8wo", "fp8wo", "fp8dq-per_tensor", "fp8dq-per_row", "int4wo-32", "int4wo-64", "int4wo-128", "int4wo-256"]`.
```

### Effe6cbd5d4289a524020e9a5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L113-L135

```text
Our team is working on supporting more online quantization methods.
SGLang will soon support methods including but not limited to `["awq", "gptq", "marlin", "gptq_marlin", "awq_marlin", "bitsandbytes", "gguf"]`.
SGLang also supports quantization methods based on [torchao](https://github.com/pytorch/ao).
You can simply specify `--torchao-config` in the command line to support this feature.
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

### Ecdc32b4e8bd9acdbd7d27b9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
Online quantization dynamically computes scaling parameters—such as the maximum/minimum values of model weights—during runtime.
Like NVIDIA FP8 training's [delayed scaling](https://docs.nvidia.com/deeplearning/transformer-engine/user-guide/examples/fp8_primer.html#Mixed-precision-training-with-FP8) mechanism, online quantization calculates the appropriate scaling factors
on-the-fly to convert high-precision weights into a lower-precision format.
```

### E72b0308bd3dc8dd15e8e2d6c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
**Note: For better performance, usability and convenience, offline quantization is recommended over online quantization.**
```

## official-014-3:dense:retrieved

SGLang v0.5.2：启动预量化模型时应如何处理用于在线量化的quantization参数？

必要要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

```json
null
```

实际输入证据：

### Eb66faf21718bf2708ca32373

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L43-L67

```text
quant_config) # load model

model.quantize(calibration_dataset, batch_size=2) # quantize
model.save(quant_path) # save model
```
```

### E112b956fffe3fc7785a2dec1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
## Model-Specific Options
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_USE_AITER` | Use AITER optimize implementation | `false` |
| `SGLANG_INT4_WEIGHT` | Enable INT4 weight quantization | `false` |
| `SGLANG_MOE_PADDING` | Enable MoE padding (sets padding size to 128 if value is `1`, often set to `1` in Docker builds) | `0` |
```

### E4a99edc287be8e7e99295b08

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L105-L105

```text
Then, you can directly use the quantized model with `SGLang`, by using the following command:
```

### E77e65b506114816eb41e9099

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-conserving_memory.md#L33-L36

```text
Statically quantized models can be downloaded from HF Hub (some popular ones are available at [Red Hat AI](https://huggingface.co/RedHatAI))
and used directly without extra configuration.

Dynamic quantization is also supported via the `quantization` option -- see [here](../features/quantization/README.md) for more details.
```

### E7eb06a8bf569c4754c22e656

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L76-L83

```text
```python
from vllm import LLM

# Split model across 4 GPUs
llm = LLM(model="meta-llama/Llama-3.3-70B-Instruct", tensor_parallel_size=4)
```

For models that are too large to fit on a single GPU (like 70B parameter models), tensor parallelism is essential.
```

### Ed113d222c40bd67cd5603407

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L43-L67

```text
```py
from datasets import load_dataset
from gptqmodel import GPTQModel, QuantizeConfig

model_id = "meta-llama/Llama-3.2-1B-Instruct"
quant_path = "Llama-3.2-1B-Instruct-gptqmodel-4bit"

calibration_dataset = load_dataset(
    "allenai/c4", data_files="en/c4-train.00001-of-01024.json.gz",
    split="train"
  ).select(range(1024))["text"]

quant_config = QuantizeConfig(bits=4, group_size=128) # quantization config
model = GPTQModel.load(model_id,
```

### E09bb5036d01e98073ac1f344

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L43-L67

```text
#### Using [GPTQModel](https://github.com/ModelCloud/GPTQModel)
```bash
# install
pip install gptqmodel --no-build-isolation -v
```
```

### E16f7d126776da84bba5a8652

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
| `SGLANG_FORCE_FP8_MARLIN` | Force using FP8 MARLIN kernels even if other FP8 kernels are available | `false` |
| `SGLANG_ENABLE_FLASHINFER_GEMM` | Use flashinfer kernels when running blockwise fp8 GEMM on Blackwell GPUs | `false` |
| `SGLANG_SUPPORT_CUTLASS_BLOCK_FP8` | Use Cutlass kernels when running blockwise fp8 GEMM on Hopper or Blackwell GPUs | `false` |
| `SGLANG_CUTLASS_MOE` | Use Cutlass FP8 MoE kernel on Blackwell GPUs | `false` |
```

## official-014-3:hybrid:retrieved

SGLang v0.5.2：启动预量化模型时应如何处理用于在线量化的quantization参数？

必要要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

```json
null
```

实际输入证据：

### E112b956fffe3fc7785a2dec1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
## Model-Specific Options
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_USE_AITER` | Use AITER optimize implementation | `false` |
| `SGLANG_INT4_WEIGHT` | Enable INT4 weight quantization | `false` |
| `SGLANG_MOE_PADDING` | Enable MoE padding (sets padding size to 128 if value is `1`, often set to `1` in Docker builds) | `0` |
```

### E9e27ac051ce62af8450419a8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
# Quantization
SGLang supports various quantization methods, including offline quantization and online dynamic quantization.
Offline quantization loads pre-quantized model weights directly during inference.
This is required for quantization methods
such as GPTQ and AWQ, which collect and pre-compute various statistics from the original weights using the calibration dataset.
```

### E54fe6490f3a729888b8673da

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L113-L135

```text
## Online Quantization
To enable online quantization, you can simply specify `--quantization` in the command line.
For example, you can launch the server with the following command to enable `FP8` quantization for model `meta-llama/Meta-Llama-3.1-8B-Instruct`:
```bash
python3 -m sglang.launch_server \
    --model-path meta-llama/Meta-Llama-3.1-8B-Instruct \
    --quantization fp8 \
    --port 30000 --host 0.0.0.0
```
```

### E77e65b506114816eb41e9099

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-conserving_memory.md#L33-L36

```text
Statically quantized models can be downloaded from HF Hub (some popular ones are available at [Red Hat AI](https://huggingface.co/RedHatAI))
and used directly without extra configuration.

Dynamic quantization is also supported via the `quantization` option -- see [here](../features/quantization/README.md) for more details.
```

### E8d558c88c0c1fce78b350fc8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L41-L41

```text
### Examples of Offline Model Quantization
```

### E16f7d126776da84bba5a8652

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
| `SGLANG_FORCE_FP8_MARLIN` | Force using FP8 MARLIN kernels even if other FP8 kernels are available | `false` |
| `SGLANG_ENABLE_FLASHINFER_GEMM` | Use flashinfer kernels when running blockwise fp8 GEMM on Blackwell GPUs | `false` |
| `SGLANG_SUPPORT_CUTLASS_BLOCK_FP8` | Use Cutlass kernels when running blockwise fp8 GEMM on Hopper or Blackwell GPUs | `false` |
| `SGLANG_CUTLASS_MOE` | Use Cutlass FP8 MoE kernel on Blackwell GPUs | `false` |
```

### Ecdc32b4e8bd9acdbd7d27b9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
Online quantization dynamically computes scaling parameters—such as the maximum/minimum values of model weights—during runtime.
Like NVIDIA FP8 training's [delayed scaling](https://docs.nvidia.com/deeplearning/transformer-engine/user-guide/examples/fp8_primer.html#Mixed-precision-training-with-FP8) mechanism, online quantization calculates the appropriate scaling factors
on-the-fly to convert high-precision weights into a lower-precision format.
```

### E72b0308bd3dc8dd15e8e2d6c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
**Note: For better performance, usability and convenience, offline quantization is recommended over online quantization.**
```

## official-014-3:hybrid_rerank:retrieved

SGLang v0.5.2：启动预量化模型时应如何处理用于在线量化的quantization参数？

必要要点：预量化模型不应同时通过quantization参数启用在线量化。

禁止误读：预量化模型总要再执行一次在线量化。

```json
null
```

实际输入证据：

### E9e27ac051ce62af8450419a8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
# Quantization
SGLang supports various quantization methods, including offline quantization and online dynamic quantization.
Offline quantization loads pre-quantized model weights directly during inference.
This is required for quantization methods
such as GPTQ and AWQ, which collect and pre-compute various statistics from the original weights using the calibration dataset.
```

### E54fe6490f3a729888b8673da

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L113-L135

```text
## Online Quantization
To enable online quantization, you can simply specify `--quantization` in the command line.
For example, you can launch the server with the following command to enable `FP8` quantization for model `meta-llama/Meta-Llama-3.1-8B-Instruct`:
```bash
python3 -m sglang.launch_server \
    --model-path meta-llama/Meta-Llama-3.1-8B-Instruct \
    --quantization fp8 \
    --port 30000 --host 0.0.0.0
```
```

### Effe6cbd5d4289a524020e9a5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L113-L135

```text
Our team is working on supporting more online quantization methods.
SGLang will soon support methods including but not limited to `["awq", "gptq", "marlin", "gptq_marlin", "awq_marlin", "bitsandbytes", "gguf"]`.
SGLang also supports quantization methods based on [torchao](https://github.com/pytorch/ao).
You can simply specify `--torchao-config` in the command line to support this feature.
```

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### Ef6c630563d458d3c5beb00ac

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic \
    --quantization w8a8_fp8 \
    --port 30000 --host 0.0.0.0
```
```

### Ecdc32b4e8bd9acdbd7d27b9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
Online quantization dynamically computes scaling parameters—such as the maximum/minimum values of model weights—during runtime.
Like NVIDIA FP8 training's [delayed scaling](https://docs.nvidia.com/deeplearning/transformer-engine/user-guide/examples/fp8_primer.html#Mixed-precision-training-with-FP8) mechanism, online quantization calculates the appropriate scaling factors
on-the-fly to convert high-precision weights into a lower-precision format.
```

### E72b0308bd3dc8dd15e8e2d6c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
**Note: For better performance, usability and convenience, offline quantization is recommended over online quantization.**
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

## official-014-4:oracle:oracle

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在quantization场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
{
  "conversation_id": "d198b01c-2b3a-41a3-a117-78ce1bc5889c",
  "answer": "资料库中没有找到可以支持这个问题的证据。请换个问法或先导入相关文档。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在quantization场景下精确的P95延迟毫秒值吗？",
      "hits": 0,
      "evidence": 0
    }
  ]
}
```

实际输入证据：

## official-014-4:bm25:retrieved

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在quantization场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E9e27ac051ce62af8450419a8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
# Quantization
SGLang supports various quantization methods, including offline quantization and online dynamic quantization.
Offline quantization loads pre-quantized model weights directly during inference.
This is required for quantization methods
such as GPTQ and AWQ, which collect and pre-compute various statistics from the original weights using the calibration dataset.
```

### E0980d4a98ece9c6b02c1f27e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L113-L135

```text
SGLang supports the following quantization methods based on torchao `["int8dq", "int8wo", "fp8wo", "fp8dq-per_tensor", "fp8dq-per_row", "int4wo-32", "int4wo-64", "int4wo-128", "int4wo-256"]`.
```

### Effe6cbd5d4289a524020e9a5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L113-L135

```text
Our team is working on supporting more online quantization methods.
SGLang will soon support methods including but not limited to `["awq", "gptq", "marlin", "gptq_marlin", "awq_marlin", "bitsandbytes", "gguf"]`.
SGLang also supports quantization methods based on [torchao](https://github.com/pytorch/ao).
You can simply specify `--torchao-config` in the command line to support this feature.
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

### Ecdc32b4e8bd9acdbd7d27b9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
Online quantization dynamically computes scaling parameters—such as the maximum/minimum values of model weights—during runtime.
Like NVIDIA FP8 training's [delayed scaling](https://docs.nvidia.com/deeplearning/transformer-engine/user-guide/examples/fp8_primer.html#Mixed-precision-training-with-FP8) mechanism, online quantization calculates the appropriate scaling factors
on-the-fly to convert high-precision weights into a lower-precision format.
```

### E72b0308bd3dc8dd15e8e2d6c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L1-L12

```text
**Note: For better performance, usability and convenience, offline quantization is recommended over online quantization.**
```

## official-014-4:dense:retrieved

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在quantization场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### Eac21656670164d7db38d4f80

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L1-L3

```text
# AMD GPUs

This document describes how run SGLang on AMD GPUs. If you encounter issues or have questions, please [open an issue](https://github.com/sgl-project/sglang/issues).
```

### E10678bf2f844017fcf791376

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L68-L73

```text
| **`SGLANG_DISAGGREGATION_WAITING_TIMEOUT`** | Timeout (seconds) for receiving KV Cache after request initialization | `300` |
```

### E904c381bf1f5f1779dedef72

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
This action will ignore the Hugging Face config's quantization settings.
For instance, with `neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic`, if you execute with `--quantization w8a8_fp8`, the system will use the `W8A8Fp8Config` from SGLang to invoke the sgl-kernel, rather than the `CompressedTensorsConfig` for vLLM kernels.
```

### E0d564c3bb80088a446830783

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L20-L24

```text
## Offline Quantization

To load already quantized models, simply load the model weights and config. **Again, if the model has been quantized offline,
there's no need to add `--quantization` argument when starting the engine. The quantization method will be parsed from the
downloaded Hugging Face config. For example, DeepSeek V3/R1 models are already in FP8, so do not add redundant parameters.**
```

### E129c5629e0e269f5141eaa20

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model Qwen/Qwen3-0.6B
```
This image can also be used with other container engines such as [Podman](https://podman.io/).
```

### E088b076a6d681481616767d5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L68-L73

```text
#### Decode Server Configuration
| Variable | Description | Default |
|:--------:|:-----------:|:--------:
| **`SGLANG_DISAGGREGATION_HEARTBEAT_INTERVAL`** | Interval (seconds) between health checks to prefill bootstrap servers | `5.0` |
| **`SGLANG_DISAGGREGATION_HEARTBEAT_MAX_FAILURE`** | Consecutive heartbeat failures before marking prefill server offline | `2` |
```

### E74b994b5ce8fbeb1f2a0b11e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4 \
    --port 30000 --host 0.0.0.0
```
Take note, if your model is **per-channel quantized (INT8 or FP8) with per-token dynamic quantization activation**, you can opt to include `--quantization w8a8_int8` or `--quantization w8a8_fp8` to invoke the corresponding CUTLASS int8_kernel or fp8_kernel in sgl-kernel.
```

### Ef6c630563d458d3c5beb00ac

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic \
    --quantization w8a8_fp8 \
    --port 30000 --host 0.0.0.0
```
```

## official-014-4:hybrid:retrieved

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在quantization场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### E904c381bf1f5f1779dedef72

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
This action will ignore the Hugging Face config's quantization settings.
For instance, with `neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic`, if you execute with `--quantization w8a8_fp8`, the system will use the `W8A8Fp8Config` from SGLang to invoke the sgl-kernel, rather than the `CompressedTensorsConfig` for vLLM kernels.
```

### E140ba685af5b7d8bee1b3fe0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L137-L145

```text
Note: According to [this issue](https://github.com/sgl-project/sglang/issues/2219#issuecomment-2561890230), `"int8dq"` method currently has some bugs when using together with cuda graph capture.
So we suggest to disable cuda graph capture when using `"int8dq"` method.
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Eac21656670164d7db38d4f80

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L1-L3

```text
# AMD GPUs

This document describes how run SGLang on AMD GPUs. If you encounter issues or have questions, please [open an issue](https://github.com/sgl-project/sglang/issues).
```

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E74b994b5ce8fbeb1f2a0b11e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4 \
    --port 30000 --host 0.0.0.0
```
Take note, if your model is **per-channel quantized (INT8 or FP8) with per-token dynamic quantization activation**, you can opt to include `--quantization w8a8_int8` or `--quantization w8a8_fp8` to invoke the corresponding CUTLASS int8_kernel or fp8_kernel in sgl-kernel.
```

### Ef6c630563d458d3c5beb00ac

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic \
    --quantization w8a8_fp8 \
    --port 30000 --host 0.0.0.0
```
```

### Ef9ab049a56e12ed7f8ff61d4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L137-L145

```text
Namely, please use the following command:
```bash
python3 -m sglang.launch_server \
    --model-path meta-llama/Meta-Llama-3.1-8B-Instruct \
    --torchao-config int8dq \
    --disable-cuda-graph \
    --port 30000 --host 0.0.0.0
```
```

## official-014-4:hybrid_rerank:retrieved

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在quantization场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### Ef6c630563d458d3c5beb00ac

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic \
    --quantization w8a8_fp8 \
    --port 30000 --host 0.0.0.0
```
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### E74b994b5ce8fbeb1f2a0b11e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
```bash
python3 -m sglang.launch_server \
    --model-path hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4 \
    --port 30000 --host 0.0.0.0
```
Take note, if your model is **per-channel quantized (INT8 or FP8) with per-token dynamic quantization activation**, you can opt to include `--quantization w8a8_int8` or `--quantization w8a8_fp8` to invoke the corresponding CUTLASS int8_kernel or fp8_kernel in sgl-kernel.
```

### Ef9ab049a56e12ed7f8ff61d4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L137-L145

```text
Namely, please use the following command:
```bash
python3 -m sglang.launch_server \
    --model-path meta-llama/Meta-Llama-3.1-8B-Instruct \
    --torchao-config int8dq \
    --disable-cuda-graph \
    --port 30000 --host 0.0.0.0
```
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

### E904c381bf1f5f1779dedef72

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L26-L39

```text
This action will ignore the Hugging Face config's quantization settings.
For instance, with `neuralmagic/Meta-Llama-3.1-8B-Instruct-FP8-dynamic`, if you execute with `--quantization w8a8_fp8`, the system will use the `W8A8Fp8Config` from SGLang to invoke the sgl-kernel, rather than the `CompressedTensorsConfig` for vLLM kernels.
```

### E140ba685af5b7d8bee1b3fe0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-quantization.md#L137-L145

```text
Note: According to [this issue](https://github.com/sgl-project/sglang/issues/2219#issuecomment-2561890230), `"int8dq"` method currently has some bugs when using together with cuda graph capture.
So we suggest to disable cuda graph capture when using `"int8dq"` method.
```

## official-016-1:oracle:oracle

SGLang v0.5.2：该路由器有哪些policy选项？

必要要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

```json
null
```

实际输入证据：

### E9faefa1cb17387473074f5b3

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/router.md

```text
--policy cache_aware  # or random, round_robin, power_of_two
```

## official-016-1:bm25:retrieved

SGLang v0.5.2：该路由器有哪些policy选项？

必要要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

```json
null
```

实际输入证据：

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### Eb21de41bd9abccda7860e337

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
Example with mixed policies:
```bash
python -m sglang_router.launch_router \
    --pd-disaggregation \
    --prefill http://prefill1:8000
    --prefill http://prefill2:8000 \
    --decode http://decode1:8001
    --decode http://decode2:8001 \
    --policy round_robin \
    --prefill-policy cache_aware  # Prefill uses cache_aware and decode uses round_robin from --policy
```
```

### E14004c472a06f97c258a0b18

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
1.
**Only `--policy` specified**: Both prefill and decode nodes use this policy
2.
**`--policy` and `--prefill-policy` specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--policy`
```

### E52424825f1fdd2370ae03999

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
3.
**`--policy` and `--decode-policy` specified**: Prefill nodes use `--policy`, decode nodes use `--decode-policy`
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

### E1c7a85f00f61773ead210bcb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
4.
**All three specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--decode-policy` (main `--policy` is ignored)
```

## official-016-1:dense:retrieved

SGLang v0.5.2：该路由器有哪些policy选项？

必要要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

```json
null
```

实际输入证据：

### E52424825f1fdd2370ae03999

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
3.
**`--policy` and `--decode-policy` specified**: Prefill nodes use `--policy`, decode nodes use `--decode-policy`
```

### Ebe845369079ff2afb5daf5cb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L138-L140

```text
#### Policy Inheritance in PD Mode

The router intelligently handles policy configuration for prefill and decode nodes:
```

### E1c7a85f00f61773ead210bcb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
4.
**All three specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--decode-policy` (main `--policy` is ignored)
```

### E14004c472a06f97c258a0b18

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
1.
**Only `--policy` specified**: Both prefill and decode nodes use this policy
2.
**`--policy` and `--prefill-policy` specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--policy`
```

### Ee31ab8f47f6fe827bdb4226b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L22-L22

```text
Now supports 5 types of connectors:
```

### Eb21de41bd9abccda7860e337

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
Example with mixed policies:
```bash
python -m sglang_router.launch_router \
    --pd-disaggregation \
    --prefill http://prefill1:8000
    --prefill http://prefill2:8000 \
    --decode http://decode1:8001
    --decode http://decode2:8001 \
    --policy round_robin \
    --prefill-policy cache_aware  # Prefill uses cache_aware and decode uses round_robin from --policy
```
```

## official-016-1:hybrid:retrieved

SGLang v0.5.2：该路由器有哪些policy选项？

必要要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

```json
null
```

实际输入证据：

### E52424825f1fdd2370ae03999

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
3.
**`--policy` and `--decode-policy` specified**: Prefill nodes use `--policy`, decode nodes use `--decode-policy`
```

### E14004c472a06f97c258a0b18

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
1.
**Only `--policy` specified**: Both prefill and decode nodes use this policy
2.
**`--policy` and `--prefill-policy` specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--policy`
```

### Ebe845369079ff2afb5daf5cb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L138-L140

```text
#### Policy Inheritance in PD Mode

The router intelligently handles policy configuration for prefill and decode nodes:
```

### E1c7a85f00f61773ead210bcb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
4.
**All three specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--decode-policy` (main `--policy` is ignored)
```

### E8dc2fb2a5fca69b5d1a146b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L1-L3

```text
# SGLang Router

The SGLang Router is a high-performance request distribution system that routes inference requests across multiple SGLang runtime instances. It features cache-aware load balancing, fault tolerance, and support for advanced deployment patterns including data parallelism and prefill-decode disaggregation.
```

### Eb21de41bd9abccda7860e337

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
Example with mixed policies:
```bash
python -m sglang_router.launch_router \
    --pd-disaggregation \
    --prefill http://prefill1:8000
    --prefill http://prefill2:8000 \
    --decode http://decode1:8001
    --decode http://decode2:8001 \
    --policy round_robin \
    --prefill-policy cache_aware  # Prefill uses cache_aware and decode uses round_robin from --policy
```
```

## official-016-1:hybrid_rerank:retrieved

SGLang v0.5.2：该路由器有哪些policy选项？

必要要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

```json
null
```

实际输入证据：

### E8dc2fb2a5fca69b5d1a146b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L1-L3

```text
# SGLang Router

The SGLang Router is a high-performance request distribution system that routes inference requests across multiple SGLang runtime instances. It features cache-aware load balancing, fault tolerance, and support for advanced deployment patterns including data parallelism and prefill-decode disaggregation.
```

### Eb21de41bd9abccda7860e337

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
Example with mixed policies:
```bash
python -m sglang_router.launch_router \
    --pd-disaggregation \
    --prefill http://prefill1:8000
    --prefill http://prefill2:8000 \
    --decode http://decode1:8001
    --decode http://decode2:8001 \
    --policy round_robin \
    --prefill-policy cache_aware  # Prefill uses cache_aware and decode uses round_robin from --policy
```
```

### Eea415b931dfc094b40574c41

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L239-L241

```text
```bash
--policy random
```
```

### E87da218a58471d09aa9c455b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L120-L129

```text
```bash
python -m sglang_router.launch_router \
    --pd-disaggregation \
    --prefill http://prefill1:8000 9000 \
    --prefill http://prefill2:8001 9001 \
    --decode http://decode1:8002 \
    --decode http://decode2:8003 \
    --prefill-policy cache_aware \
    --decode-policy round_robin
```
```

### Ee9d9f152784db7b4347bb660

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L108-L114

```text
```bash
python -m sglang_router.launch_router \
    --worker-urls http://worker1:8000 http://worker2:8001 \
    --host 0.0.0.0 \
    --port 30000 \
    --policy cache_aware  # or random, round_robin, power_of_two
```
```

### E1c7a85f00f61773ead210bcb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
4.
**All three specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--decode-policy` (main `--policy` is ignored)
```

### E52424825f1fdd2370ae03999

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
3.
**`--policy` and `--decode-policy` specified**: Prefill nodes use `--policy`, decode nodes use `--decode-policy`
```

### E14004c472a06f97c258a0b18

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
1.
**Only `--policy` specified**: Both prefill and decode nodes use this policy
2.
**`--policy` and `--prefill-policy` specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--policy`
```

## official-016-2:oracle:oracle

SGLang v0.5.2：cache_aware是否是路由器唯一可用策略？

必要要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

```json
null
```

实际输入证据：

### E9faefa1cb17387473074f5b3

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/router.md

```text
--policy cache_aware  # or random, round_robin, power_of_two
```

## official-016-2:bm25:retrieved

SGLang v0.5.2：cache_aware是否是路由器唯一可用策略？

必要要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

```json
null
```

实际输入证据：

### E5d703c7b97b67f658450e964

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L261-L266

```text
```bash
--policy cache_aware \
--cache-threshold 0.5 \
--balance-abs-threshold 32 \
--balance-rel-threshold 1.0001
```
```

### E2c2225f19a9a13d0006676fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L296-L306

```text
| `--policy`                  | str  | cache_aware | Routing policy (random, round_robin, cache_aware, power_of_two) |
| `--max-concurrent-requests` | int  | 64          | Maximum concurrent requests (rate limiting)                     |
| `--request-timeout-secs`    | int  | 600         | Request timeout in seconds                                      |
```

### Eb21de41bd9abccda7860e337

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
Example with mixed policies:
```bash
python -m sglang_router.launch_router \
    --pd-disaggregation \
    --prefill http://prefill1:8000
    --prefill http://prefill2:8000 \
    --decode http://decode1:8001
    --decode http://decode2:8001 \
    --policy round_robin \
    --prefill-policy cache_aware  # Prefill uses cache_aware and decode uses round_robin from --policy
```
```

### Ee9d9f152784db7b4347bb660

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L108-L114

```text
```bash
python -m sglang_router.launch_router \
    --worker-urls http://worker1:8000 http://worker2:8001 \
    --host 0.0.0.0 \
    --port 30000 \
    --policy cache_aware  # or random, round_robin, power_of_two
```
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### E2e73c3353337880584e7673e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L296-L306

```text
| `--host`                    | str  | 127.0.0.1   | Router server host address                                      |
| `--port`                    | int  | 30000       | Router server port                                              |
| `--worker-urls`             | list | []          | Worker URLs for separate launch mode                            |
```

### E5fc3dae10d7529bd6f262275

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L296-L306

```text
| `--max-payload-size`        | int  | 256MB       | Maximum request payload size                                    |
```

### E3d6bec2ae40916623c04b831

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L296-L306

```text
| --------------------------- | ---- | ----------- | --------------------------------------------------------------- |
```

### E3f9299218da47b74abf84de0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L296-L306

```text
### Core Settings
| Parameter                   | Type | Default     | Description                                                     |
```

### E1c7a85f00f61773ead210bcb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
4.
**All three specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--decode-policy` (main `--policy` is ignored)
```

### E52424825f1fdd2370ae03999

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
3.
**`--policy` and `--decode-policy` specified**: Prefill nodes use `--policy`, decode nodes use `--decode-policy`
```

## official-016-2:dense:retrieved

SGLang v0.5.2：cache_aware是否是路由器唯一可用策略？

必要要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

```json
null
```

实际输入证据：

### E175abfb72289c61f79345465

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L257-L259

```text
### 4. Cache-Aware Load Balancing (Default)

The most sophisticated policy that combines cache optimization with load balancing:
```

### E0d9ace42e104957291c84cdc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L138-L142

```text
## Enabling GPUDirect RDMA

GPUDirect RDMA (Remote Direct Memory Access) is an NVIDIA technology that allows network adapters to directly access GPU memory, bypassing the CPU and system memory. This direct access reduces latency and CPU overhead, which is beneficial for large data transfers between GPUs across nodes.

To enable GPUDirect RDMA with vLLM, configure the following settings:
```

### E2a987935049ba4a72d481f15

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L1-L3

```text
# Sleep Mode

vLLM's Sleep Mode allows you to temporarily release most GPU memory used by a model, including model weights and KV cache, without stopping the server or unloading the Docker container. This is especially useful for RLHF, training, or cost-saving scenarios where GPU resources need to be freed between inference workloads.
```

### E9179e0166553b73ef2a10c4b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
!!
! note
Cache isolation is not supported in engine V0.
```

### E9b57a84b4c35fdd281e418e5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L9-L27

```text
## Common launch commands
- To enable multi-GPU tensor parallelism, add `--tp 2`.
If it reports the error "peer access is not supported between these two devices", add `--enable-p2p-check` to the server launch command.
```bash
  python -m sglang.launch_server --model-path meta-llama/Meta-Llama-3-8B-Instruct --tp 2
  ```
- To enable multi-GPU data parallelism, add `--dp 2`.
Data parallelism is better for throughput if there is enough memory.
```

### E5d8fe7ed6ec122403b10c915

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
With this setup, cache sharing is limited to users or requests that explicitly agree on a common salt, enabling cache reuse within a trust group while isolating others.
```

### Ea78a5260abf923558a637c53

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
This offers protection without compromising performance.
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Here is a document with details about the world series: ..."},
    {"role": "user", "content": "Who won the world series in 2020?"}
  ],
  "cache_salt": "your-cache-salt"
}
```
```

### E1463499a732287269ea92129

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
To improve privacy in shared environments, vLLM supports isolating prefix cache reuse through optional per-request salting.
By including a `cache_salt` in the request, this value is injected into the hash of the first block, ensuring that only requests with the same salt can reuse cached KV blocks.
This prevents timing-based attacks where an adversary could infer cached content by observing latency differences.
```

### E5dda40ed0c5092aadb08696f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-prefix_caching.md#L79-L98

```text
In the rest of this document, we first introduce the data structure used for prefix caching in vLLM v1, followed by the prefix caching workflow of major KV cache operators (e.g., allocate, append, free, eviction).
Finally, we use an example to illustrate the end to end prefix caching workflow.
**Cache Isolation for Security**
```

### E0f4f4d685998aef8e888d8b9

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L9-L27

```text
- If you see out-of-memory errors during serving, try to reduce the memory usage of the KV cache pool by setting a smaller value of `--mem-fraction-static`.
```

## official-016-2:hybrid:retrieved

SGLang v0.5.2：cache_aware是否是路由器唯一可用策略？

必要要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

```json
null
```

实际输入证据：

### E175abfb72289c61f79345465

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L257-L259

```text
### 4. Cache-Aware Load Balancing (Default)

The most sophisticated policy that combines cache optimization with load balancing:
```

### Ef42660deb26899b1da5aa8cf

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L308-L316

```text
### Cache-Aware Routing Parameters
| Parameter                  | Type  | Default  | Description                                            |
```

### E8dc2fb2a5fca69b5d1a146b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L1-L3

```text
# SGLang Router

The SGLang Router is a high-performance request distribution system that routes inference requests across multiple SGLang runtime instances. It features cache-aware load balancing, fault tolerance, and support for advanced deployment patterns including data parallelism and prefill-decode disaggregation.
```

### E6532df59fd0dd55e6db3b9fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-torch_compile_cache.md#L1-L4

```text
# Enabling cache for torch.compile

SGLang uses `max-autotune-no-cudagraphs` mode of torch.compile. The auto-tuning can be slow.
If you want to deploy a model on many different machines, you can ship the torch.compile cache to these machines and skip the compilation steps.
```

### E5d703c7b97b67f658450e964

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L261-L266

```text
```bash
--policy cache_aware \
--cache-threshold 0.5 \
--balance-abs-threshold 32 \
--balance-rel-threshold 1.0001
```
```

### Ef123440b32d9632e875ed7a5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L308-L316

```text
| -------------------------- | ----- | -------- | ------------------------------------------------------ |
| `--cache-threshold`        | float | 0.5      | Minimum prefix match ratio for cache routing (0.0-1.0) |
| `--balance-abs-threshold`  | int   | 32       | Absolute load difference threshold                     |
| `--balance-rel-threshold`  | float | 1.0001   | Relative load ratio threshold                          |
```

### E76f55f75c37c32fbeb669498

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L308-L316

```text
| `--eviction-interval-secs` | int   | 60       | Seconds between cache eviction cycles                  |
| `--max-tree-size`          | int   | 16777216 | Maximum nodes in routing tree                          |
```

## official-016-2:hybrid_rerank:retrieved

SGLang v0.5.2：cache_aware是否是路由器唯一可用策略？

必要要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

```json
null
```

实际输入证据：

### E8dc2fb2a5fca69b5d1a146b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L1-L3

```text
# SGLang Router

The SGLang Router is a high-performance request distribution system that routes inference requests across multiple SGLang runtime instances. It features cache-aware load balancing, fault tolerance, and support for advanced deployment patterns including data parallelism and prefill-decode disaggregation.
```

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### Eb21de41bd9abccda7860e337

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
Example with mixed policies:
```bash
python -m sglang_router.launch_router \
    --pd-disaggregation \
    --prefill http://prefill1:8000
    --prefill http://prefill2:8000 \
    --decode http://decode1:8001
    --decode http://decode2:8001 \
    --policy round_robin \
    --prefill-policy cache_aware  # Prefill uses cache_aware and decode uses round_robin from --policy
```
```

### Ee9d9f152784db7b4347bb660

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L108-L114

```text
```bash
python -m sglang_router.launch_router \
    --worker-urls http://worker1:8000 http://worker2:8001 \
    --host 0.0.0.0 \
    --port 30000 \
    --policy cache_aware  # or random, round_robin, power_of_two
```
```

### E87da218a58471d09aa9c455b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L120-L129

```text
```bash
python -m sglang_router.launch_router \
    --pd-disaggregation \
    --prefill http://prefill1:8000 9000 \
    --prefill http://prefill2:8001 9001 \
    --decode http://decode1:8002 \
    --decode http://decode2:8003 \
    --prefill-policy cache_aware \
    --decode-policy round_robin
```
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

### E1c7a85f00f61773ead210bcb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
4.
**All three specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--decode-policy` (main `--policy` is ignored)
```

### E52424825f1fdd2370ae03999

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
3.
**`--policy` and `--decode-policy` specified**: Prefill nodes use `--policy`, decode nodes use `--decode-policy`
```

### E14004c472a06f97c258a0b18

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
1.
**Only `--policy` specified**: Both prefill and decode nodes use this policy
2.
**`--policy` and `--prefill-policy` specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--policy`
```

## official-016-3:oracle:oracle

SGLang v0.5.2：启动路由器时希望选择缓存感知策略，policy参数应填什么？

必要要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

```json
null
```

实际输入证据：

### E9faefa1cb17387473074f5b3

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/router.md

```text
--policy cache_aware  # or random, round_robin, power_of_two
```

## official-016-3:bm25:retrieved

SGLang v0.5.2：启动路由器时希望选择缓存感知策略，policy参数应填什么？

必要要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

```json
null
```

实际输入证据：

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### Eb21de41bd9abccda7860e337

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
Example with mixed policies:
```bash
python -m sglang_router.launch_router \
    --pd-disaggregation \
    --prefill http://prefill1:8000
    --prefill http://prefill2:8000 \
    --decode http://decode1:8001
    --decode http://decode2:8001 \
    --policy round_robin \
    --prefill-policy cache_aware  # Prefill uses cache_aware and decode uses round_robin from --policy
```
```

### E14004c472a06f97c258a0b18

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
1.
**Only `--policy` specified**: Both prefill and decode nodes use this policy
2.
**`--policy` and `--prefill-policy` specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--policy`
```

### E52424825f1fdd2370ae03999

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
3.
**`--policy` and `--decode-policy` specified**: Prefill nodes use `--policy`, decode nodes use `--decode-policy`
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

### E1c7a85f00f61773ead210bcb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
4.
**All three specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--decode-policy` (main `--policy` is ignored)
```

## official-016-3:dense:retrieved

SGLang v0.5.2：启动路由器时希望选择缓存感知策略，policy参数应填什么？

必要要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

```json
null
```

实际输入证据：

### E836c7d1b89a88031ebc19bb7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
You can install the frontend locally without needing a GPU, while the backend can be set up on a GPU-enabled machine.
To install the frontend, run `pip install sglang`, and for the backend, use `pip install sglang[srt]`.
`srt` is the abbreviation of SGLang runtime.
```

### Efc55291935303ead3eaceed3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L108-L110

```text
## Dynamically serving LoRA Adapters

In addition to serving LoRA adapters at server startup, the vLLM server supports dynamically configuring LoRA adapters at runtime through dedicated API endpoints and plugins. This feature can be particularly useful when the flexibility to change models on-the-fly is needed.
```

### E2a987935049ba4a72d481f15

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L1-L3

```text
# Sleep Mode

vLLM's Sleep Mode allows you to temporarily release most GPU memory used by a model, including model weights and KV cache, without stopping the server or unloading the Docker container. This is especially useful for RLHF, training, or cost-saving scenarios where GPU resources need to be freed between inference workloads.
```

### Eb4f7cd8c5ff4c4cbf177370a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L67-L85

```text
adding `--security-opt label=disable` when running `podman build` command to avoid certain [existing issues](https://github.com/containers/buildah/discussions/4184).
```

### Ee0929569d29fcc572d15931d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L62-L71

```text
#### Server in development mode

When using the flag `VLLM_SERVER_DEV_MODE=1` you enable development endpoints, and these endpoints should not be exposed to users.

```bash
VLLM_SERVER_DEV_MODE=1 python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen3-0.6B \
  --enable-sleep-mode \
  --port 8000
```
```

### E60efa2876c564037d25230c7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
- To reinstall flashinfer locally, use the following command: `pip3 install --upgrade flashinfer-python --force-reinstall --no-deps` and then delete the cache with `rm -rf ~/.cache/flashinfer`.
- If you only need to use OpenAI API models with the frontend language, you can avoid installing other dependencies by using `pip install "sglang[openai]"`.
- The language frontend operates independently of the backend runtime.
```

### Eb87769bfc3e391ac8b6ece77

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
It only supports sm75 and above.
If you encounter any FlashInfer-related issues on sm75+ devices (e.g., T4, A10, A100, L4, L40S, H100), please switch to other kernels by adding `--attention-backend triton --sampling-backend pytorch` and open an issue on GitHub.
```

### Ed40ac9f26230255755dbb880

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
## Common Notes
- [FlashInfer](https://github.com/flashinfer-ai/flashinfer) is the default attention kernel backend.
```

### E6fcff5765635f30b24c2d96c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L67-L85

```text
!!
! note
By default vLLM will build for all GPU types for widest distribution.
If you are just building for the
current GPU type the machine is running on, you can add the argument `--build-arg torch_cuda_arch_list=""`
for vLLM to find the current GPU type and build for that.
If you are using Podman instead of Docker, you might need to disable SELinux labeling by
```

## official-016-3:hybrid:retrieved

SGLang v0.5.2：启动路由器时希望选择缓存感知策略，policy参数应填什么？

必要要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

```json
null
```

实际输入证据：

### E52424825f1fdd2370ae03999

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
3.
**`--policy` and `--decode-policy` specified**: Prefill nodes use `--policy`, decode nodes use `--decode-policy`
```

### E14004c472a06f97c258a0b18

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
1.
**Only `--policy` specified**: Both prefill and decode nodes use this policy
2.
**`--policy` and `--prefill-policy` specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--policy`
```

### E836c7d1b89a88031ebc19bb7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
You can install the frontend locally without needing a GPU, while the backend can be set up on a GPU-enabled machine.
To install the frontend, run `pip install sglang`, and for the backend, use `pip install sglang[srt]`.
`srt` is the abbreviation of SGLang runtime.
```

### E8dc2fb2a5fca69b5d1a146b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L1-L3

```text
# SGLang Router

The SGLang Router is a high-performance request distribution system that routes inference requests across multiple SGLang runtime instances. It features cache-aware load balancing, fault tolerance, and support for advanced deployment patterns including data parallelism and prefill-decode disaggregation.
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### E1c7a85f00f61773ead210bcb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
4.
**All three specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--decode-policy` (main `--policy` is ignored)
```

### Eb21de41bd9abccda7860e337

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
Example with mixed policies:
```bash
python -m sglang_router.launch_router \
    --pd-disaggregation \
    --prefill http://prefill1:8000
    --prefill http://prefill2:8000 \
    --decode http://decode1:8001
    --decode http://decode2:8001 \
    --policy round_robin \
    --prefill-policy cache_aware  # Prefill uses cache_aware and decode uses round_robin from --policy
```
```

### E60efa2876c564037d25230c7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
- To reinstall flashinfer locally, use the following command: `pip3 install --upgrade flashinfer-python --force-reinstall --no-deps` and then delete the cache with `rm -rf ~/.cache/flashinfer`.
- If you only need to use OpenAI API models with the frontend language, you can avoid installing other dependencies by using `pip install "sglang[openai]"`.
- The language frontend operates independently of the backend runtime.
```

### Eb87769bfc3e391ac8b6ece77

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
It only supports sm75 and above.
If you encounter any FlashInfer-related issues on sm75+ devices (e.g., T4, A10, A100, L4, L40S, H100), please switch to other kernels by adding `--attention-backend triton --sampling-backend pytorch` and open an issue on GitHub.
```

## official-016-3:hybrid_rerank:retrieved

SGLang v0.5.2：启动路由器时希望选择缓存感知策略，policy参数应填什么？

必要要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

```json
null
```

实际输入证据：

### E87da218a58471d09aa9c455b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L120-L129

```text
```bash
python -m sglang_router.launch_router \
    --pd-disaggregation \
    --prefill http://prefill1:8000 9000 \
    --prefill http://prefill2:8001 9001 \
    --decode http://decode1:8002 \
    --decode http://decode2:8003 \
    --prefill-policy cache_aware \
    --decode-policy round_robin
```
```

### Ee9d9f152784db7b4347bb660

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L108-L114

```text
```bash
python -m sglang_router.launch_router \
    --worker-urls http://worker1:8000 http://worker2:8001 \
    --host 0.0.0.0 \
    --port 30000 \
    --policy cache_aware  # or random, round_robin, power_of_two
```
```

### Eb21de41bd9abccda7860e337

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
Example with mixed policies:
```bash
python -m sglang_router.launch_router \
    --pd-disaggregation \
    --prefill http://prefill1:8000
    --prefill http://prefill2:8000 \
    --decode http://decode1:8001
    --decode http://decode2:8001 \
    --policy round_robin \
    --prefill-policy cache_aware  # Prefill uses cache_aware and decode uses round_robin from --policy
```
```

### Eea415b931dfc094b40574c41

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L239-L241

```text
```bash
--policy random
```
```

### E5a9b6d765b51f2fa0439df1a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L246-L248

```text
```bash
--policy round_robin
```
```

### E1c7a85f00f61773ead210bcb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
4.
**All three specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--decode-policy` (main `--policy` is ignored)
```

### E52424825f1fdd2370ae03999

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
3.
**`--policy` and `--decode-policy` specified**: Prefill nodes use `--policy`, decode nodes use `--decode-policy`
```

### E14004c472a06f97c258a0b18

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L142-L157

```text
1.
**Only `--policy` specified**: Both prefill and decode nodes use this policy
2.
**`--policy` and `--prefill-policy` specified**: Prefill nodes use `--prefill-policy`, decode nodes use `--policy`
```

## official-016-4:oracle:oracle

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在router场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
{
  "conversation_id": "aa97c7b2-901a-4433-825b-7990b544a8c1",
  "answer": "资料库中没有找到可以支持这个问题的证据。请换个问法或先导入相关文档。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在router场景下精确的P95延迟毫秒值吗？",
      "hits": 0,
      "evidence": 0
    }
  ]
}
```

实际输入证据：

## official-016-4:bm25:retrieved

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在router场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E8dc2fb2a5fca69b5d1a146b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L1-L3

```text
# SGLang Router

The SGLang Router is a high-performance request distribution system that routes inference requests across multiple SGLang runtime instances. It features cache-aware load balancing, fault tolerance, and support for advanced deployment patterns including data parallelism and prefill-decode disaggregation.
```

### E6235a8f1dcc8d2e14b1c10da

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L25-L28

```text
```bash
python -m sglang_router.launch_server --help  # Co-launch router and workers
python -m sglang_router.launch_router --help  # Launch router only
```
```

### Edfac3d789064dcde7b3d9b5c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L20-L22

```text
## Router Integration

For deploying PD disaggregation at scale with load balancing and fault tolerance, SGLang provides a router. The router can distribute requests between prefill and decode instances using various routing policies. For detailed information on setting up routing with PD disaggregation, including configuration options and deployment patterns, see the [SGLang Router documentation](router.md#mode-3-prefill-decode-disaggregation).
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

## official-016-4:dense:retrieved

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在router场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### E8dc2fb2a5fca69b5d1a146b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L1-L3

```text
# SGLang Router

The SGLang Router is a high-performance request distribution system that routes inference requests across multiple SGLang runtime instances. It features cache-aware load balancing, fault tolerance, and support for advanced deployment patterns including data parallelism and prefill-decode disaggregation.
```

### Eac21656670164d7db38d4f80

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L1-L3

```text
# AMD GPUs

This document describes how run SGLang on AMD GPUs. If you encounter issues or have questions, please [open an issue](https://github.com/sgl-project/sglang/issues).
```

### E129c5629e0e269f5141eaa20

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model Qwen/Qwen3-0.6B
```
This image can also be used with other container engines such as [Podman](https://podman.io/).
```

### E76dca9b42c02be4cdcff9c3e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
podman run --device nvidia.com/gpu=all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
  -p 8000:8000 \
  --ipc=host \
  docker.io/vllm/vllm-openai:latest \
  --model Qwen/Qwen3-0.6B
```
You can add any other [engine-args](../configuration/engine_args.md) you need after the image tag (`vllm/vllm-openai:latest`).
```

### E10678bf2f844017fcf791376

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L68-L73

```text
| **`SGLANG_DISAGGREGATION_WAITING_TIMEOUT`** | Timeout (seconds) for receiving KV Cache after request initialization | `300` |
```

### E9a5dde88f838a11ba9dccd64

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
## Use vLLM's Official Docker Image
vLLM offers an official Docker image for deployment.
The image can be used to run OpenAI compatible server and is available on Docker Hub as [vllm/vllm-openai](https://hub.docker.com/r/vllm/vllm-openai/tags).
```

### Ec94bd3c0efd3b0755001340f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
!!
! note
You can either use the `ipc=host` flag or `--shm-size` flag to allow the
container to access the host's shared memory.
vLLM uses PyTorch, which uses shared
memory to share data between processes under the hood, particularly for tensor parallel inference.
```

### E088b076a6d681481616767d5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L68-L73

```text
#### Decode Server Configuration
| Variable | Description | Default |
|:--------:|:-----------:|:--------:
| **`SGLANG_DISAGGREGATION_HEARTBEAT_INTERVAL`** | Interval (seconds) between health checks to prefill bootstrap servers | `5.0` |
| **`SGLANG_DISAGGREGATION_HEARTBEAT_MAX_FAILURE`** | Consecutive heartbeat failures before marking prefill server offline | `2` |
```

## official-016-4:hybrid:retrieved

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在router场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### E8dc2fb2a5fca69b5d1a146b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L1-L3

```text
# SGLang Router

The SGLang Router is a high-performance request distribution system that routes inference requests across multiple SGLang runtime instances. It features cache-aware load balancing, fault tolerance, and support for advanced deployment patterns including data parallelism and prefill-decode disaggregation.
```

### E52674bc1670073378803c76c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L440-L445

```text
```bash
python -m sglang_router.launch_router \
    --worker-urls http://worker1:8000 http://worker2:8001 \
    --log-level debug \
    --log-dir ./router_logs
```
```

### E0d967a55fa6ea9bae371dca8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L38-L49

```text
### Mode 1: Co-launch Router and Workers

This mode launches both the router and multiple worker instances in a single command. It's the simplest deployment option and replaces the `--dp-size` argument of SGLang Runtime.

```bash
# Launch router with 4 workers
python -m sglang_router.launch_server \
    --model-path meta-llama/Meta-Llama-3.1-8B-Instruct \
    --dp-size 4 \
    --host 0.0.0.0 \
    --port 30000
```
```

### E6235a8f1dcc8d2e14b1c10da

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L25-L28

```text
```bash
python -m sglang_router.launch_server --help  # Co-launch router and workers
python -m sglang_router.launch_router --help  # Launch router only
```
```

### E10ea964300ddbadd312eaa83

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L380-L387

```text
#### Standard Mode
```bash
python -m sglang_router.launch_router \
    --service-discovery \
    --selector app=sglang-worker env=prod \
    --service-discovery-namespace production \
    --service-discovery-port 8000
```
```

## official-016-4:hybrid_rerank:retrieved

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在router场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E92464a6e04740566b364e30d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L218-L225

```text
```bash
python -m sglang_router.launch_router \
    --worker-urls http://worker1:8000 http://worker2:8001 \
    --cb-failure-threshold 5 \
    --cb-success-threshold 2 \
    --cb-timeout-duration-secs 30 \
    --cb-window-duration-secs 60
```
```

### Ee0d5736fabcf39cd3f5a98fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L405-L410

```text
```bash
python -m sglang_router.launch_router \
    --worker-urls http://worker1:8000 http://worker2:8001 \
    --prometheus-port 29000 \
    --prometheus-host 0.0.0.0
```
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ef33f7f4b318e1421cc59177a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L418-L422

```text
```bash
python -m sglang_router.launch_router \
    --worker-urls http://worker1:8000 http://worker2:8001 \
    --request-id-headers x-request-id x-trace-id
```
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

## official-017-1:oracle:oracle

SGLang v0.5.2：temperature为零与提高温度分别改变什么采样行为？

必要要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

```json
null
```

实际输入证据：

### E0793ae080d2f9fd4247b79d7

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/basic_usage/sampling_params.md

```text
`temperature = 0` corresponds to greedy sampling, a higher temperature leads to more diversity.
```

## official-017-1:bm25:retrieved

SGLang v0.5.2：temperature为零与提高温度分别改变什么采样行为？

必要要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

```json
null
```

实际输入证据：

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### Ee40e6126002381f7a0a9facf

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-faq.md#L31-L35

```text
- The per-request random seed is tracked at [https://github.com/sgl-project/sglang/issues/1335](https://github.com/sgl-project/sglang/issues/1335).
```

### E0b7351620a7cf7cf68539eef

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| temperature     | `float = 1.0`                                | [Temperature](https://platform.openai.com/docs/api-reference/chat/create#chat-create-temperature) when sampling the next token.
`temperature = 0` corresponds to greedy sampling, a higher temperature leads to more diversity.
```

### E80f829d65ca2f40a360f16a0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-faq.md#L23-L29

```text
### The results are not deterministic, even with a temperature of 0
You may notice that when you send the same request twice, the results from the engine will be slightly different, even when the temperature is set to 0.
From our initial investigation, this indeterminism arises from two factors: dynamic batching and prefix caching.
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

### E865577520769d14721757180

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-faq.md#L31-L35

```text
We are still investigating the root causes and potential solutions.
In the short term, we may introduce a "deterministic mode" that uses more padding to address the variance caused by dynamic batching.
This mode will be more deterministic but slower.
We have two issues to track our progress:
- The deterministic mode is tracked at [https://github.com/sgl-project/sglang/issues/1729](https://github.com/sgl-project/sglang/issues/1729).
```

### E072897bed238401e262b8f8f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| stop_token_ids  | `Optional[List[int]] = None`                 | Provide stop words in the form of token IDs.
Generation will stop if one of these token IDs is sampled.
```

### Ec625ad9c7b102ae144bf90ea

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| top_p           | `float = 1.0`                                | [Top-p](https://platform.openai.com/docs/api-reference/chat/create#chat-create-top_p) selects tokens from the smallest sorted set whose cumulative probability exceeds `top_p`.
When `top_p = 1`, this reduces to unrestricted sampling from all tokens.
```

## official-017-1:dense:retrieved

SGLang v0.5.2：temperature为零与提高温度分别改变什么采样行为？

必要要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

```json
null
```

实际输入证据：

### E05078378961a85c6c87feedd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L8-L16

```text
## Method 1: With pip or uv

It is recommended to use uv for faster installation:

```bash
pip install --upgrade pip
pip install uv
uv pip install "sglang[all]>=0.5.2"
```
```

### E187a08bf77ca5464493728f7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L15-L19

```text
## Installation

```bash
pip install sglang-router
```
```

### E112b956fffe3fc7785a2dec1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
## Model-Specific Options
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_USE_AITER` | Use AITER optimize implementation | `false` |
| `SGLANG_INT4_WEIGHT` | Enable INT4 weight quantization | `false` |
| `SGLANG_MOE_PADDING` | Enable MoE padding (sets padding size to 128 if value is `1`, often set to `1` in Docker builds) | `0` |
```

### E1ff39d43ec8ef2cc491f4d4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L39-L41

```text
## Install SGLang

You can install SGLang using one of the methods below.
```

### E8651ea1f0391d57e95cc940c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L1-L3

```text
# Install SGLang

You can install SGLang using one of the methods below.
```

### E16f7d126776da84bba5a8652

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
| `SGLANG_FORCE_FP8_MARLIN` | Force using FP8 MARLIN kernels even if other FP8 kernels are available | `false` |
| `SGLANG_ENABLE_FLASHINFER_GEMM` | Use flashinfer kernels when running blockwise fp8 GEMM on Blackwell GPUs | `false` |
| `SGLANG_SUPPORT_CUTLASS_BLOCK_FP8` | Use Cutlass kernels when running blockwise fp8 GEMM on Hopper or Blackwell GPUs | `false` |
| `SGLANG_CUTLASS_MOE` | Use Cutlass FP8 MoE kernel on Blackwell GPUs | `false` |
```

## official-017-1:hybrid:retrieved

SGLang v0.5.2：temperature为零与提高温度分别改变什么采样行为？

必要要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

```json
null
```

实际输入证据：

### Ef91c9ea7ae5e874a8e4ae11d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L286-L341

```text
erate(
        inputs,
        sampling_params=SamplingParams(
            temperature=0.2,
            max_tokens=64,
        ),
    )
    ```
```

### E1ff39d43ec8ef2cc491f4d4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L39-L41

```text
## Install SGLang

You can install SGLang using one of the methods below.
```

### E8651ea1f0391d57e95cc940c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L1-L3

```text
# Install SGLang

You can install SGLang using one of the methods below.
```

### E8dc2fb2a5fca69b5d1a146b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md#L1-L3

```text
# SGLang Router

The SGLang Router is a high-performance request distribution system that routes inference requests across multiple SGLang runtime instances. It features cache-aware load balancing, fault tolerance, and support for advanced deployment patterns including data parallelism and prefill-decode disaggregation.
```

### E6aab8b2e68120715a59cd786

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L24-L46

```text
```python
    from vllm import LLM, SamplingParams

    prompts = [
        "The future of AI is",
    ]
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

    llm = LLM(
        model="facebook/opt-6.7b",
        tensor_parallel_size=1,
        speculative_config={
            "model": "facebook/opt-125m",
            "num_speculative_tokens": 5,
        },
    )
    outputs = llm.generate(prompts, sampling_params)

    for outpu
```

### E85ec22c5c2f684fff91254ec

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L286-L341

```text
default_mm_loras = {"audio": model_id},
        enforce_eager=True,
    )

    question = "can you transcribe the speech into a written format?"
    prompt_with_audio = get_prompt(
        question=question,
        has_audio=True,
    )
    audio = AudioAsset("mary_had_lamb").audio_and_sample_rate

    inputs = {
        "prompt": prompt_with_audio,
        "multi_modal_data": {
            "audio": audio,
        }
    }


    outputs = llm.gen
```

### E6cd3244c6b47a95ad98986d3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L286-L341

```text
{
                "role": "user",
                "content": question
            }
        ]
        return tokenizer.apply_chat_template(chat, tokenize=False)


    llm = LLM(
        model=model_id,
        enable_lora=True,
        max_lora_rank=64,
        max_model_len=2048,
        limit_mm_per_prompt={"audio": 1},
        # Will always pass a `LoRARequest` with the `model_id`
        # whenever audio is contained in the request data.
    
```

### Ea9a611d797ab099cb48a2a56

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L286-L341

```text
```python
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.assets.audio import AudioAsset

    model_id = "ibm-granite/granite-speech-3.3-2b"
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    def get_prompt(question: str, has_audio: bool):
        """Build the input prompt to send to vLLM."""
        if has_audio:
            question = f"<|audio|>{question}"
        chat = [
           
```

### E5587222ef0e01aa3e2559919

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L24-L46

```text
t in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
    ```
```

## official-017-1:hybrid_rerank:retrieved

SGLang v0.5.2：temperature为零与提高温度分别改变什么采样行为？

必要要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

```json
null
```

实际输入证据：

### E0b7351620a7cf7cf68539eef

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| temperature     | `float = 1.0`                                | [Temperature](https://platform.openai.com/docs/api-reference/chat/create#chat-create-temperature) when sampling the next token.
`temperature = 0` corresponds to greedy sampling, a higher temperature leads to more diversity.
```

### E80f829d65ca2f40a360f16a0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-faq.md#L23-L29

```text
### The results are not deterministic, even with a temperature of 0
You may notice that when you send the same request twice, the results from the engine will be slightly different, even when the temperature is set to 0.
From our initial investigation, this indeterminism arises from two factors: dynamic batching and prefix caching.
```

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E554668bafa992f15b3a8eb5a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L91-L106

```text
```bash
curl http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "sql-lora",
        "prompt": "San Francisco is a",
        "max_tokens": 7,
        "temperature": 0
    }' | jq
```
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### E072897bed238401e262b8f8f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| stop_token_ids  | `Optional[List[int]] = None`                 | Provide stop words in the form of token IDs.
Generation will stop if one of these token IDs is sampled.
```

### Ec625ad9c7b102ae144bf90ea

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| top_p           | `float = 1.0`                                | [Top-p](https://platform.openai.com/docs/api-reference/chat/create#chat-create-top_p) selects tokens from the smallest sorted set whose cumulative probability exceeds `top_p`.
When `top_p = 1`, this reduces to unrestricted sampling from all tokens.
```

### Ed0e4f52b2cf5f13eb65a6e78

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
| stop            | `Optional[Union[str, List[str]]] = None`     | One or multiple [stop words](https://platform.openai.com/docs/api-reference/chat/create#chat-create-stop).
Generation will stop if one of these words is sampled.
```

### E1bb1ec74e27f3ecd7797b21c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| top_k           | `int = -1`                                   | [Top-k](https://developer.nvidia.com/blog/how-to-get-better-outputs-from-your-large-language-model/#predictability_vs_creativity) randomly selects from the `k` highest-probability tokens.
```

### E48c43b6868dd620551b7f85a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
```

## official-017-2:oracle:oracle

SGLang v0.5.2：temperature为零是否意味着均匀随机选择下一token？

必要要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

```json
null
```

实际输入证据：

### E0793ae080d2f9fd4247b79d7

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/basic_usage/sampling_params.md

```text
`temperature = 0` corresponds to greedy sampling, a higher temperature leads to more diversity.
```

## official-017-2:bm25:retrieved

SGLang v0.5.2：temperature为零是否意味着均匀随机选择下一token？

必要要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

```json
null
```

实际输入证据：

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### E0b7351620a7cf7cf68539eef

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| temperature     | `float = 1.0`                                | [Temperature](https://platform.openai.com/docs/api-reference/chat/create#chat-create-temperature) when sampling the next token.
`temperature = 0` corresponds to greedy sampling, a higher temperature leads to more diversity.
```

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### Ee40e6126002381f7a0a9facf

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-faq.md#L31-L35

```text
- The per-request random seed is tracked at [https://github.com/sgl-project/sglang/issues/1335](https://github.com/sgl-project/sglang/issues/1335).
```

### E38bb0550ceb8b3da28d9bab3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L198-L252

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

### E072897bed238401e262b8f8f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| stop_token_ids  | `Optional[List[int]] = None`                 | Provide stop words in the form of token IDs.
Generation will stop if one of these token IDs is sampled.
```

### Ec625ad9c7b102ae144bf90ea

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| top_p           | `float = 1.0`                                | [Top-p](https://platform.openai.com/docs/api-reference/chat/create#chat-create-top_p) selects tokens from the smallest sorted set whose cumulative probability exceeds `top_p`.
When `top_p = 1`, this reduces to unrestricted sampling from all tokens.
```

### Ed0e4f52b2cf5f13eb65a6e78

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
| stop            | `Optional[Union[str, List[str]]] = None`     | One or multiple [stop words](https://platform.openai.com/docs/api-reference/chat/create#chat-create-stop).
Generation will stop if one of these words is sampled.
```

### E1bb1ec74e27f3ecd7797b21c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
```

### E5aa33ae1202374846aadafb2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
| max_new_tokens  | `int = 128`                                  | The maximum output length measured in tokens.
|
```

### E48c43b6868dd620551b7f85a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
```

## official-017-2:dense:retrieved

SGLang v0.5.2：temperature为零是否意味着均匀随机选择下一token？

必要要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

```json
null
```

实际输入证据：

### E0b7351620a7cf7cf68539eef

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| temperature     | `float = 1.0`                                | [Temperature](https://platform.openai.com/docs/api-reference/chat/create#chat-create-temperature) when sampling the next token.
`temperature = 0` corresponds to greedy sampling, a higher temperature leads to more diversity.
```

### E98647595cf74b7a11cdefd6b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L45-L51

```text
|
| min_new_tokens     | `int = 0`              | Forces the model to generate at least `min_new_tokens` until a stop word or EOS token is sampled.
Note that this might lead to unintended behavior, for example, if the distribution is highly skewed towards these tokens.
```

### Ea58fa50c2376987be3807e24

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L49-L59

```text
- Smaller values (e.g., 2048) achieve better inter-token latency (ITL) because there are fewer prefills slowing down decodes.
- Higher values achieve better time to first token (TTFT) as you can process more prefill tokens in a batch.
- For optimal throughput, we recommend setting `max_num_batched_tokens > 8192` especially for smaller models on large GPUs.
```

### Ef91c9ea7ae5e874a8e4ae11d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L286-L341

```text
erate(
        inputs,
        sampling_params=SamplingParams(
            temperature=0.2,
            max_tokens=64,
        ),
    )
    ```
```

### E04696c878c012a58247592d4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L200-L212

```text
| `--speculative-eagle-topk` | The number of tokens sampled from the draft model in eagle2 each step.
| None |
| `--speculative-num-draft-tokens` | The number of tokens sampled from the draft model in Speculative Decoding.
```

### E072897bed238401e262b8f8f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| stop_token_ids  | `Optional[List[int]] = None`                 | Provide stop words in the form of token IDs.
Generation will stop if one of these token IDs is sampled.
```

### Ec625ad9c7b102ae144bf90ea

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| top_p           | `float = 1.0`                                | [Top-p](https://platform.openai.com/docs/api-reference/chat/create#chat-create-top_p) selects tokens from the smallest sorted set whose cumulative probability exceeds `top_p`.
When `top_p = 1`, this reduces to unrestricted sampling from all tokens.
```

### Ed0e4f52b2cf5f13eb65a6e78

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
| stop            | `Optional[Union[str, List[str]]] = None`     | One or multiple [stop words](https://platform.openai.com/docs/api-reference/chat/create#chat-create-stop).
Generation will stop if one of these words is sampled.
```

### E1bb1ec74e27f3ecd7797b21c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| top_k           | `int = -1`                                   | [Top-k](https://developer.nvidia.com/blog/how-to-get-better-outputs-from-your-large-language-model/#predictability_vs_creativity) randomly selects from the `k` highest-probability tokens.
```

### E5aa33ae1202374846aadafb2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
| max_new_tokens  | `int = 128`                                  | The maximum output length measured in tokens.
|
```

### E48c43b6868dd620551b7f85a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
```

### E9910165b86d7c62fdcccec82

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
```

### E55800a19b070afca4d89cfb2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
### Core parameters
| Argument        | Type/Default                                 | Description                                                                                                                                    |
```

## official-017-2:hybrid:retrieved

SGLang v0.5.2：temperature为零是否意味着均匀随机选择下一token？

必要要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

```json
null
```

实际输入证据：

### E0b7351620a7cf7cf68539eef

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| temperature     | `float = 1.0`                                | [Temperature](https://platform.openai.com/docs/api-reference/chat/create#chat-create-temperature) when sampling the next token.
`temperature = 0` corresponds to greedy sampling, a higher temperature leads to more diversity.
```

### Ef91c9ea7ae5e874a8e4ae11d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L286-L341

```text
erate(
        inputs,
        sampling_params=SamplingParams(
            temperature=0.2,
            max_tokens=64,
        ),
    )
    ```
```

### E80f829d65ca2f40a360f16a0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-faq.md#L23-L29

```text
### The results are not deterministic, even with a temperature of 0
You may notice that when you send the same request twice, the results from the engine will be slightly different, even when the temperature is set to 0.
From our initial investigation, this indeterminism arises from two factors: dynamic batching and prefix caching.
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### E98647595cf74b7a11cdefd6b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L45-L51

```text
|
| min_new_tokens     | `int = 0`              | Forces the model to generate at least `min_new_tokens` until a stop word or EOS token is sampled.
Note that this might lead to unintended behavior, for example, if the distribution is highly skewed towards these tokens.
```

### E072897bed238401e262b8f8f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| stop_token_ids  | `Optional[List[int]] = None`                 | Provide stop words in the form of token IDs.
Generation will stop if one of these token IDs is sampled.
```

### Ec625ad9c7b102ae144bf90ea

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| top_p           | `float = 1.0`                                | [Top-p](https://platform.openai.com/docs/api-reference/chat/create#chat-create-top_p) selects tokens from the smallest sorted set whose cumulative probability exceeds `top_p`.
When `top_p = 1`, this reduces to unrestricted sampling from all tokens.
```

### Ed0e4f52b2cf5f13eb65a6e78

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
| stop            | `Optional[Union[str, List[str]]] = None`     | One or multiple [stop words](https://platform.openai.com/docs/api-reference/chat/create#chat-create-stop).
Generation will stop if one of these words is sampled.
```

### E1bb1ec74e27f3ecd7797b21c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| top_k           | `int = -1`                                   | [Top-k](https://developer.nvidia.com/blog/how-to-get-better-outputs-from-your-large-language-model/#predictability_vs_creativity) randomly selects from the `k` highest-probability tokens.
```

### E5aa33ae1202374846aadafb2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
| max_new_tokens  | `int = 128`                                  | The maximum output length measured in tokens.
|
```

### E48c43b6868dd620551b7f85a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
```

### E9910165b86d7c62fdcccec82

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
```

### E55800a19b070afca4d89cfb2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
### Core parameters
```

## official-017-2:hybrid_rerank:retrieved

SGLang v0.5.2：temperature为零是否意味着均匀随机选择下一token？

必要要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

```json
null
```

实际输入证据：

### E0b7351620a7cf7cf68539eef

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| temperature     | `float = 1.0`                                | [Temperature](https://platform.openai.com/docs/api-reference/chat/create#chat-create-temperature) when sampling the next token.
`temperature = 0` corresponds to greedy sampling, a higher temperature leads to more diversity.
```

### E80f829d65ca2f40a360f16a0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-faq.md#L23-L29

```text
### The results are not deterministic, even with a temperature of 0
You may notice that when you send the same request twice, the results from the engine will be slightly different, even when the temperature is set to 0.
From our initial investigation, this indeterminism arises from two factors: dynamic batching and prefix caching.
```

### E38bb0550ceb8b3da28d9bab3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L198-L252

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

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### Ef91c9ea7ae5e874a8e4ae11d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L286-L341

```text
erate(
        inputs,
        sampling_params=SamplingParams(
            temperature=0.2,
            max_tokens=64,
        ),
    )
    ```
```

### E072897bed238401e262b8f8f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| stop_token_ids  | `Optional[List[int]] = None`                 | Provide stop words in the form of token IDs.
Generation will stop if one of these token IDs is sampled.
```

### Ec625ad9c7b102ae144bf90ea

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| top_p           | `float = 1.0`                                | [Top-p](https://platform.openai.com/docs/api-reference/chat/create#chat-create-top_p) selects tokens from the smallest sorted set whose cumulative probability exceeds `top_p`.
When `top_p = 1`, this reduces to unrestricted sampling from all tokens.
```

### Ed0e4f52b2cf5f13eb65a6e78

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
| stop            | `Optional[Union[str, List[str]]] = None`     | One or multiple [stop words](https://platform.openai.com/docs/api-reference/chat/create#chat-create-stop).
Generation will stop if one of these words is sampled.
```

### E1bb1ec74e27f3ecd7797b21c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L33-L43

```text
|
| top_k           | `int = -1`                                   | [Top-k](https://developer.nvidia.com/blog/how-to-get-better-outputs-from-your-large-language-model/#predictability_vs_creativity) randomly selects from the `k` highest-probability tokens.
```

## official-017-3:oracle:oracle

SGLang v0.5.2：请求JSON中想启用贪心采样，temperature应设置成多少？

必要要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

```json
null
```

实际输入证据：

### E0793ae080d2f9fd4247b79d7

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/basic_usage/sampling_params.md

```text
`temperature = 0` corresponds to greedy sampling, a higher temperature leads to more diversity.
```

## official-017-3:bm25:retrieved

SGLang v0.5.2：请求JSON中想启用贪心采样，temperature应设置成多少？

必要要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

```json
null
```

实际输入证据：

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### E38bb0550ceb8b3da28d9bab3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L198-L252

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

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E0b525850024c3f46a96ae5e8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L87-L101

```text
```python
import requests

response = requests.post(
    "http://localhost:30000/generate",
    json={
        "text": "The capital of France is",
        "sampling_params": {
            "temperature": 0,
            "max_new_tokens": 32,
        },
    },
)
print(response.json())
```
```

### E0e326ce3d6eced7732b39168

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L198-L252

```text
s": 64,
            "regex": "(France|England)",
        },
    },
)
print(response.json())

# EBNF (XGrammar backend only)
response = requests.post(
    "http://localhost:30000/generate",
    json={
        "text": "Write a greeting.",
        "sampling_params": {
            "temperature": 0,
            "max_new_tokens": 64,
            "ebnf": 'root ::= "Hello" | "Hi" | "Hey"',
        },
    },
)
print(response.json())
```
```

### Ede65dacdbfb3608885adc702

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L198-L252

```text
```python
import json
import requests

json_schema = json.dumps({
    "type": "object",
    "properties": {
        "name": {"type": "string", "pattern": "^[\\w]+$"},
        "population": {"type": "integer"},
    },
    "required": ["name", "population"],
})

# JSON (works with both Outlines and XGrammar)
response = requests.post(
    "http://localhost:30000/generate",
    json={
        "text": "Here is the information of the capital of France 
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

## official-017-3:dense:retrieved

SGLang v0.5.2：请求JSON中想启用贪心采样，temperature应设置成多少？

必要要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

```json
null
```

实际输入证据：

### E03955c38a5e61c3c67f1cecf

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L71-L77

```text
**Solved with**
```python/sglang/srt/layers/attention/triton_ops/decode_attention.py +410```
- If you get an error like `ImportError: cannot import name 'build_regex_from_schema' from 'outlines.fsm.json_schema'`, same with https://github.com/sgl-project/sglang/issues/2530
**Solved with** ```
```

### E848f2fc3e6cdaf0e40c6e4f7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L29-L43

```text
```python
from vllm import LLM
llm = LLM("facebook/opt-13b", tensor_parallel_size=4)
output = llm.generate("San Francisco is a")
```
For multi-GPU serving, include `--tensor-parallel-size` when starting the server.
For example, to run the API server on 4 GPUs:
```

### E88c0d498f39a5afd01c0d0fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L87-L114

```text
4.
To verify the utility, you can run a benchmark in another terminal or refer to [other docs](https://docs.sglang.ai/backend/openai_api_completions.html) to send requests to the engine.
```bash
   drun sglang_image \
       python3 -m sglang.bench_serving \
       --backend sglang \
       --dataset-name random \
       --num-prompts 4000 \
       --random-input 128 \
       --random-output 128
   ```
```

### E8713fd87b381389222fcfab8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L8-L22

```text
### 🐛 Describe the bug
**I use the model Qwen2.5-VL-3B-Instruct for V1 PD disaggregation with 1 image input;
Everything is fine until I sent 2 different requests, with identical text prompt, but different input images in same image size.
It wrongly reuses KV for the later request, which cause it wrongly returning an identical output with the previous request.**
```

### Ecab0c87413552287f8b5d591

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-pr-21611.md#L30-L194

```text
========
***info: Pure text input test as a case-control***
**Expected storage path length after llm generate: 5**
Adding requests: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 948.94it/s]
Processed prompts:   0%|                                                                                                
```

### Ec0b1bd88b1cd27c667f8e004

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L71-L77

```text
## Issues
- If you get the error like `raise OutOfResources(self.metadata.shared, max_shared, "shared memory")`, same with https://github.com/sgl-project/sglang/issues/2384
```

### E867be2c7ab1891cef1ab0ed0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L71-L77

```text
downgrade vllm
```
- If you get an error like `RuntimeError: [enforce fail at /app/pytorch/third_party/gloo/gloo/transport/tcp/device.cc:83] ifa != nullptr. Unable to find address for: eth0' 
**Solved with** ifconfig check your eth number and  ```
export GLOO_SOCKET_IFNAME=your eth```
```

### E897194ad2f791358ff557c8f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L29-L43

```text
You can override the defaults by setting `distributed_executor_backend` in the `LLM` class or `--distributed-executor-backend` in the API server.
Use `mp` for `multiprocessing` or `ray` for Ray.
For multi-GPU inference, set `tensor_parallel_size` in the `LLM` class to the desired GPU count.
For example, to run inference on 4 GPUs:
```

### E13de57b4b78ec4f9f38ce564

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L29-L43

```text
## Single-node deployment
vLLM supports distributed tensor-parallel and pipeline-parallel inference and serving.
```

## official-017-3:hybrid:retrieved

SGLang v0.5.2：请求JSON中想启用贪心采样，temperature应设置成多少？

必要要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

```json
null
```

实际输入证据：

### E03955c38a5e61c3c67f1cecf

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L71-L77

```text
**Solved with**
```python/sglang/srt/layers/attention/triton_ops/decode_attention.py +410```
- If you get an error like `ImportError: cannot import name 'build_regex_from_schema' from 'outlines.fsm.json_schema'`, same with https://github.com/sgl-project/sglang/issues/2530
**Solved with** ```
```

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E554668bafa992f15b3a8eb5a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L91-L106

```text
```bash
curl http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "sql-lora",
        "prompt": "San Francisco is a",
        "max_tokens": 7,
        "temperature": 0
    }' | jq
```
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### E38bb0550ceb8b3da28d9bab3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L198-L252

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

### Ec0b1bd88b1cd27c667f8e004

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L71-L77

```text
## Issues
- If you get the error like `raise OutOfResources(self.metadata.shared, max_shared, "shared memory")`, same with https://github.com/sgl-project/sglang/issues/2384
```

### E867be2c7ab1891cef1ab0ed0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L71-L77

```text
downgrade vllm
```
- If you get an error like `RuntimeError: [enforce fail at /app/pytorch/third_party/gloo/gloo/transport/tcp/device.cc:83] ifa != nullptr. Unable to find address for: eth0' 
**Solved with** ifconfig check your eth number and  ```
export GLOO_SOCKET_IFNAME=your eth```
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

### E5088cfa0e13fb1052694966d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L91-L106

```text
Requests can specify the LoRA adapter as if it were any other model via the `model` request parameter.
The requests will be
processed according to the server-wide LoRA configuration (i.e.
in parallel with base model requests, and potentially other
LoRA adapter requests if they were provided and `max_loras` is set high enough).
```

## official-017-3:hybrid_rerank:retrieved

SGLang v0.5.2：请求JSON中想启用贪心采样，temperature应设置成多少？

必要要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

```json
null
```

实际输入证据：

### E0e326ce3d6eced7732b39168

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L198-L252

```text
s": 64,
            "regex": "(France|England)",
        },
    },
)
print(response.json())

# EBNF (XGrammar backend only)
response = requests.post(
    "http://localhost:30000/generate",
    json={
        "text": "Write a greeting.",
        "sampling_params": {
            "temperature": 0,
            "max_new_tokens": 64,
            "ebnf": 'root ::= "Hello" | "Hi" | "Hey"',
        },
    },
)
print(response.json())
```
```

### E52907137367087cb5eb17c93

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L156-L175

```text
```python
import requests

response = requests.post(
    "http://localhost:30000/generate",
    json={
        "text": "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n"
                "<|im_start|>user\n<image>\nDescribe this image in a very short sentence.<|im_end|>\n"
                "<|im_start|>assistant\n",
        "image_data": "example_image.png",
        "sampling_params": {
            "temperature": 0,
            "max_new
```

### E38bb0550ceb8b3da28d9bab3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L198-L252

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

### E0b525850024c3f46a96ae5e8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L87-L101

```text
```python
import requests

response = requests.post(
    "http://localhost:30000/generate",
    json={
        "text": "The capital of France is",
        "sampling_params": {
            "temperature": 0,
            "max_new_tokens": 32,
        },
    },
)
print(response.json())
```
```

### Ee68648cbf9e99a5be90f5951

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L105-L136

```text
```python
import requests, json

response = requests.post(
    "http://localhost:30000/generate",
    json={
        "text": "The capital of France is",
        "sampling_params": {
            "temperature": 0,
            "max_new_tokens": 32,
        },
        "stream": True,
    },
    stream=True,
)

prev = 0
for chunk in response.iter_lines(decode_unicode=False):
    chunk = chunk.decode("utf-8")
    if chunk and chunk.startswith("data:"):
```

### Ede65dacdbfb3608885adc702

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L198-L252

```text
```python
import json
import requests

json_schema = json.dumps({
    "type": "object",
    "properties": {
        "name": {"type": "string", "pattern": "^[\\w]+$"},
        "population": {"type": "integer"},
    },
    "required": ["name", "population"],
})

# JSON (works with both Outlines and XGrammar)
response = requests.post(
    "http://localhost:30000/generate",
    json={
        "text": "Here is the information of the capital of France 
```

### E03593c294f9f0f5cdc6af31f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L156-L175

```text
_tokens": 32,
        },
    },
)
print(response.json())
```
The `image_data` can be a file name, a URL, or a base64 encoded string.
See also `python/sglang/srt/utils.py:load_image`.
```

## official-017-4:oracle:oracle

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在sampling_params场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
{
  "conversation_id": "8f5359de-0faa-49a6-b0ab-5326323747cf",
  "answer": "资料库中没有找到可以支持这个问题的证据。请换个问法或先导入相关文档。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在sampling_params场景下精确的P95延迟毫秒值吗？",
      "hits": 0,
      "evidence": 0
    }
  ]
}
```

实际输入证据：

## official-017-4:bm25:retrieved

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在sampling_params场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### E7fa3e055872741cbe43b9b44

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-structured_outputs.md#L310-L325

```text
```python
    from vllm import LLM, SamplingParams
    from vllm.sampling_params import GuidedDecodingParams

    llm = LLM(model="HuggingFaceTB/SmolLM2-1.7B-Instruct")

    guided_decoding_params = GuidedDecodingParams(choice=["Positive", "Negative"])
    sampling_params = SamplingParams(guided_decoding=guided_decoding_params)
    outputs = llm.generate(
        prompts="Classify this sentiment: vLLM is wonderful!",
        sampling_params=sampl
```

### E606715c679b8e98189e2fb63

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L10-L27

```text
|
| sampling_params            | `Optional[Union[List[Dict], Dict]] = None`                                   | The sampling parameters as described in the sections below.
```

### Ef91c9ea7ae5e874a8e4ae11d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L286-L341

```text
erate(
        inputs,
        sampling_params=SamplingParams(
            temperature=0.2,
            max_tokens=64,
        ),
    )
    ```
```

### E38bb0550ceb8b3da28d9bab3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L198-L252

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

### E6aab8b2e68120715a59cd786

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L24-L46

```text
```python
    from vllm import LLM, SamplingParams

    prompts = [
        "The future of AI is",
    ]
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

    llm = LLM(
        model="facebook/opt-6.7b",
        tensor_parallel_size=1,
        speculative_config={
            "model": "facebook/opt-125m",
            "num_speculative_tokens": 5,
        },
    )
    outputs = llm.generate(prompts, sampling_params)

    for outpu
```

### Ec62598327ec6483fefcea2d0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-structured_outputs.md#L310-L325

```text
ing_params,
    )
    print(outputs[0].outputs[0].text)
    ```
See also: [full example](../examples/online_serving/structured_outputs.md)
```

### E134405b69996d3a60a33018a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L10-L27

```text
|
| audio_data                 | `Optional[Union[List[AudioDataItem], AudioDataItem]] = None`                 | The audio input.
Can be a file name, URL, or base64 encoded string.
```

### E587e7b16e26ed768d6ec71f6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L10-L27

```text
|
| rid                        | `Optional[Union[List[str], str]] = None`                                     | The request ID.
```

### Eaefb75e949c7987383e03791

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L10-L27

```text
|
| image_data                 | `Optional[Union[List[List[ImageDataItem]], List[ImageDataItem], ImageDataItem]] = None` | The image input.
Can be an image instance, file name, URL, or base64 encoded string.
Can be a single image, list of images, or list of lists of images.
```

### E26bca0ce6fa2833b4872e9d4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L10-L27

```text
|
| return_logprob             | `Optional[Union[List[bool], bool]] = None`                                   | Whether to return log probabilities for tokens.
```

### E0013475991edddd9eb716fed

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L10-L27

```text
|
```

## official-017-4:dense:retrieved

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在sampling_params场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### Eac21656670164d7db38d4f80

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L1-L3

```text
# AMD GPUs

This document describes how run SGLang on AMD GPUs. If you encounter issues or have questions, please [open an issue](https://github.com/sgl-project/sglang/issues).
```

### E8651ea1f0391d57e95cc940c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L1-L3

```text
# Install SGLang

You can install SGLang using one of the methods below.
```

### E10678bf2f844017fcf791376

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L68-L73

```text
| **`SGLANG_DISAGGREGATION_WAITING_TIMEOUT`** | Timeout (seconds) for receiving KV Cache after request initialization | `300` |
```

### E1ff39d43ec8ef2cc491f4d4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L39-L41

```text
## Install SGLang

You can install SGLang using one of the methods below.
```

### E2a987935049ba4a72d481f15

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L1-L3

```text
# Sleep Mode

vLLM's Sleep Mode allows you to temporarily release most GPU memory used by a model, including model weights and KV cache, without stopping the server or unloading the Docker container. This is especially useful for RLHF, training, or cost-saving scenarios where GPU resources need to be freed between inference workloads.
```

### E088b076a6d681481616767d5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pd_disaggregation.md#L68-L73

```text
#### Decode Server Configuration
| Variable | Description | Default |
|:--------:|:-----------:|:--------:
| **`SGLANG_DISAGGREGATION_HEARTBEAT_INTERVAL`** | Interval (seconds) between health checks to prefill bootstrap servers | `5.0` |
| **`SGLANG_DISAGGREGATION_HEARTBEAT_MAX_FAILURE`** | Consecutive heartbeat failures before marking prefill server offline | `2` |
```

## official-017-4:hybrid:retrieved

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在sampling_params场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### E6aab8b2e68120715a59cd786

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L24-L46

```text
```python
    from vllm import LLM, SamplingParams

    prompts = [
        "The future of AI is",
    ]
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

    llm = LLM(
        model="facebook/opt-6.7b",
        tensor_parallel_size=1,
        speculative_config={
            "model": "facebook/opt-125m",
            "num_speculative_tokens": 5,
        },
    )
    outputs = llm.generate(prompts, sampling_params)

    for outpu
```

### Efbb576120d973191dc3e7b42

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L1-L4

```text
# Sampling Parameters

This doc describes the sampling parameters of the SGLang Runtime. It is the low-level endpoint of the runtime.
If you want a high-level endpoint that can automatically handle chat templates, consider using the [OpenAI Compatible API](openai_api_completions.ipynb).
```

### E2e29604285dfb58946048719

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md#L29-L31

```text
## Sampling parameters

The object is defined at `sampling_params.py::SamplingParams`. You can also read the source code to find more arguments and docs.
```

### E31510e3f4ebb16a987042d94

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L109-L132

```text
```python
    from vllm import LLM, SamplingParams

    prompts = [
        "The future of AI is",
    ]
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

    llm = LLM(
        model="facebook/opt-6.7b",
        tensor_parallel_size=1,
        speculative_config={
            "method": "ngram",
            "num_speculative_tokens": 5,
            "prompt_lookup_max": 4,
        },
    )
    outputs = llm.generate(prompts, sampli
```

### Eac21656670164d7db38d4f80

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L1-L3

```text
# AMD GPUs

This document describes how run SGLang on AMD GPUs. If you encounter issues or have questions, please [open an issue](https://github.com/sgl-project/sglang/issues).
```

### E5587222ef0e01aa3e2559919

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L24-L46

```text
t in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
    ```
```

### E76332a0d51bc20bac67bb891

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L109-L132

```text
ng_params)

    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
    ```
```

## official-017-4:hybrid_rerank:retrieved

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在sampling_params场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### E31510e3f4ebb16a987042d94

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L109-L132

```text
```python
    from vllm import LLM, SamplingParams

    prompts = [
        "The future of AI is",
    ]
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

    llm = LLM(
        model="facebook/opt-6.7b",
        tensor_parallel_size=1,
        speculative_config={
            "method": "ngram",
            "num_speculative_tokens": 5,
            "prompt_lookup_max": 4,
        },
    )
    outputs = llm.generate(prompts, sampli
```

### E6aab8b2e68120715a59cd786

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L24-L46

```text
```python
    from vllm import LLM, SamplingParams

    prompts = [
        "The future of AI is",
    ]
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95)

    llm = LLM(
        model="facebook/opt-6.7b",
        tensor_parallel_size=1,
        speculative_config={
            "model": "facebook/opt-125m",
            "num_speculative_tokens": 5,
        },
    )
    outputs = llm.generate(prompts, sampling_params)

    for outpu
```

### E836c7d1b89a88031ebc19bb7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
You can install the frontend locally without needing a GPU, while the backend can be set up on a GPU-enabled machine.
To install the frontend, run `pip install sglang`, and for the backend, use `pip install sglang[srt]`.
`srt` is the abbreviation of SGLang runtime.
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

### E76332a0d51bc20bac67bb891

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L109-L132

```text
ng_params)

    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
    ```
```

### E5587222ef0e01aa3e2559919

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-spec_decode.md#L24-L46

```text
t in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
    ```
```

### E60efa2876c564037d25230c7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
- To reinstall flashinfer locally, use the following command: `pip3 install --upgrade flashinfer-python --force-reinstall --no-deps` and then delete the cache with `rm -rf ~/.cache/flashinfer`.
```

## official-020-1:oracle:oracle

SGLang v0.5.2：哪个环境变量控制torch.compile，默认值是什么？

必要要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

```json
null
```

实际输入证据：

### E24ec3bd0aec6fd7f17e6e464

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/references/environment_variables.md

```text
`SGLANG_ENABLE_TORCH_COMPILE` | Enable torch.compile | `true`
```

## official-020-1:bm25:retrieved

SGLang v0.5.2：哪个环境变量控制torch.compile，默认值是什么？

必要要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

```json
null
```

实际输入证据：

### E6532df59fd0dd55e6db3b9fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-torch_compile_cache.md#L1-L4

```text
# Enabling cache for torch.compile

SGLang uses `max-autotune-no-cudagraphs` mode of torch.compile. The auto-tuning can be slow.
If you want to deploy a model on many different machines, you can ship the torch.compile cache to these machines and skip the compilation steps.
```

### E04c0aeade9a0982b561c79d3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
## Performance Tuning
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_ENABLE_TORCH_INFERENCE_MODE` | Control whether to use torch.inference_mode | `false` |
| `SGLANG_ENABLE_TORCH_COMPILE` | Enable torch.compile | `true` |
| `SGLANG_SET_CPU_AFFINITY` | Enable CPU affinity setting (often set to `1` in Docker builds) | `0` |
```

### E2d78cbc882954c36a96fb374

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-torch_compile_cache.md#L6-L6

```text
This is based on https://pytorch.org/tutorials/recipes/torch_compile_caching_tutorial.html
```

### E0378d6a07be801542c20d2ae

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
For more details, please refer to [PyTorch official documentation](https://pytorch.org/tutorials/recipes/torch_compile_caching_tutorial.html) and [Enabling cache for torch.compile](https://docs.sglang.ai/backend/hyperparameter_tuning.html#enabling-cache-for-torch-compile).
- To enable torchao quantization, add `--torchao-config int4wo-128`.
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ea05186af02bae47f9a2d81f2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
| `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN` | Allows the scheduler to overwrite longer context length requests (often set to `1` in Docker builds) | `0` |
| `SGLANG_IS_FLASHINFER_AVAILABLE` | Control FlashInfer availability check | `true` |
| `SGLANG_SKIP_P2P_CHECK` | Skip P2P (peer-to-peer) access check | `false` |
| `SGL_CHUNKED_PREFIX_CACHE_THRESHOLD` | Sets the threshold for enabling chunked prefix caching | `8192` |
```

### E70c5727f50f834f5685f298f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
| `SGLANG_FUSED_MLA_ENABLE_ROPE_FUSION` | Enable RoPE fusion in Fused Multi-Layer Attention | `1` |
```

### Ec4678a8fc21dd044a00d2f47

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
- To enable `torch.compile` acceleration, add `--enable-torch-compile`.
It accelerates small models on small batch sizes.
By default, the cache path is located at `/tmp/torchinductor_root`, you can customize it using environment variable `TORCHINDUCTOR_CACHE_DIR`.
```

### E5858c0b6aa2464dc1072738e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
It supports other [quantization strategies (INT8/FP8)](https://github.com/sgl-project/sglang/blob/v0.3.6/python/sglang/srt/server_args.py#L671) as well.
```

## official-020-1:dense:retrieved

SGLang v0.5.2：哪个环境变量控制torch.compile，默认值是什么？

必要要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

```json
null
```

实际输入证据：

### E112b956fffe3fc7785a2dec1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
## Model-Specific Options
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_USE_AITER` | Use AITER optimize implementation | `false` |
| `SGLANG_INT4_WEIGHT` | Enable INT4 weight quantization | `false` |
| `SGLANG_MOE_PADDING` | Enable MoE padding (sets padding size to 128 if value is `1`, often set to `1` in Docker builds) | `0` |
```

### E04c0aeade9a0982b561c79d3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
## Performance Tuning
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_ENABLE_TORCH_INFERENCE_MODE` | Control whether to use torch.inference_mode | `false` |
| `SGLANG_ENABLE_TORCH_COMPILE` | Enable torch.compile | `true` |
| `SGLANG_SET_CPU_AFFINITY` | Enable CPU affinity setting (often set to `1` in Docker builds) | `0` |
```

### E1a039fd3e6e7f242e5aab544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-automatic_prefix_caching.md#L10-L12

```text
## Enabling APC in vLLM

Set `enable_prefix_caching=True` in vLLM engine to enable APC. Here is an example:
```

### E0e84432891126a30a6e4410c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L26-L29

```text
```python
from vllm import LLM
llm = LLM("Qwen/Qwen3-0.6B", enable_sleep_mode=True)
```
```

### E1f32f5cd845fdb312ed52d0d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L151-L165

```text
```python
from vllm import LLM

llm = LLM(
    model="Qwen/Qwen2.5-VL-72B-Instruct",
    tensor_parallel_size=4,
    # When mm_encoder_tp_mode="data",
    # the vision encoder uses TP=4 (not DP=1) to shard the input data,
    # so the TP size becomes the effective DP size.
    # Note that this is independent of the DP size for language decoder which is used in expert parallel setting.
    mm_encoder_tp_mode="data",
    # The language decoder uses
```

### E16f7d126776da84bba5a8652

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
| `SGLANG_FORCE_FP8_MARLIN` | Force using FP8 MARLIN kernels even if other FP8 kernels are available | `false` |
| `SGLANG_ENABLE_FLASHINFER_GEMM` | Use flashinfer kernels when running blockwise fp8 GEMM on Blackwell GPUs | `false` |
| `SGLANG_SUPPORT_CUTLASS_BLOCK_FP8` | Use Cutlass kernels when running blockwise fp8 GEMM on Hopper or Blackwell GPUs | `false` |
| `SGLANG_CUTLASS_MOE` | Use Cutlass FP8 MoE kernel on Blackwell GPUs | `false` |
```

### Ea05186af02bae47f9a2d81f2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
| `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN` | Allows the scheduler to overwrite longer context length requests (often set to `1` in Docker builds) | `0` |
| `SGLANG_IS_FLASHINFER_AVAILABLE` | Control FlashInfer availability check | `true` |
| `SGLANG_SKIP_P2P_CHECK` | Skip P2P (peer-to-peer) access check | `false` |
| `SGL_CHUNKED_PREFIX_CACHE_THRESHOLD` | Sets the threshold for enabling chunked prefix caching | `8192` |
```

### E70c5727f50f834f5685f298f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
| `SGLANG_FUSED_MLA_ENABLE_ROPE_FUSION` | Enable RoPE fusion in Fused Multi-Layer Attention | `1` |
```

## official-020-1:hybrid:retrieved

SGLang v0.5.2：哪个环境变量控制torch.compile，默认值是什么？

必要要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

```json
null
```

实际输入证据：

### E04c0aeade9a0982b561c79d3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
## Performance Tuning
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_ENABLE_TORCH_INFERENCE_MODE` | Control whether to use torch.inference_mode | `false` |
| `SGLANG_ENABLE_TORCH_COMPILE` | Enable torch.compile | `true` |
| `SGLANG_SET_CPU_AFFINITY` | Enable CPU affinity setting (often set to `1` in Docker builds) | `0` |
```

### E8e644a8686c6a13daccba2fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L86-L91

```text
## Profiling & Benchmarking

| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_TORCH_PROFILER_DIR` | Directory for PyTorch profiler output | `/tmp` |
| `SGLANG_PROFILE_WITH_STACK` | Set `with_stack` option (bool) for PyTorch profiler (capture stack trace) | `true` |
```

### E4bed9a447d315197d41b2c64

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-fp8.md#L39-L47

```text
```python
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, device_map="auto", torch_dtype="auto",
)
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
```
```

### E112b956fffe3fc7785a2dec1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
## Model-Specific Options
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_USE_AITER` | Use AITER optimize implementation | `false` |
| `SGLANG_INT4_WEIGHT` | Enable INT4 weight quantization | `false` |
| `SGLANG_MOE_PADDING` | Enable MoE padding (sets padding size to 128 if value is `1`, often set to `1` in Docker builds) | `0` |
```

### E6532df59fd0dd55e6db3b9fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-torch_compile_cache.md#L1-L4

```text
# Enabling cache for torch.compile

SGLang uses `max-autotune-no-cudagraphs` mode of torch.compile. The auto-tuning can be slow.
If you want to deploy a model on many different machines, you can ship the torch.compile cache to these machines and skip the compilation steps.
```

### Ea05186af02bae47f9a2d81f2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
| `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN` | Allows the scheduler to overwrite longer context length requests (often set to `1` in Docker builds) | `0` |
| `SGLANG_IS_FLASHINFER_AVAILABLE` | Control FlashInfer availability check | `true` |
| `SGLANG_SKIP_P2P_CHECK` | Skip P2P (peer-to-peer) access check | `false` |
| `SGL_CHUNKED_PREFIX_CACHE_THRESHOLD` | Sets the threshold for enabling chunked prefix caching | `8192` |
```

### E70c5727f50f834f5685f298f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
| `SGLANG_FUSED_MLA_ENABLE_ROPE_FUSION` | Enable RoPE fusion in Fused Multi-Layer Attention | `1` |
```

### E16f7d126776da84bba5a8652

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
| `SGLANG_FORCE_FP8_MARLIN` | Force using FP8 MARLIN kernels even if other FP8 kernels are available | `false` |
| `SGLANG_ENABLE_FLASHINFER_GEMM` | Use flashinfer kernels when running blockwise fp8 GEMM on Blackwell GPUs | `false` |
```

## official-020-1:hybrid_rerank:retrieved

SGLang v0.5.2：哪个环境变量控制torch.compile，默认值是什么？

必要要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

```json
null
```

实际输入证据：

### Ec4678a8fc21dd044a00d2f47

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
- To enable `torch.compile` acceleration, add `--enable-torch-compile`.
It accelerates small models on small batch sizes.
By default, the cache path is located at `/tmp/torchinductor_root`, you can customize it using environment variable `TORCHINDUCTOR_CACHE_DIR`.
```

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E6532df59fd0dd55e6db3b9fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-torch_compile_cache.md#L1-L4

```text
# Enabling cache for torch.compile

SGLang uses `max-autotune-no-cudagraphs` mode of torch.compile. The auto-tuning can be slow.
If you want to deploy a model on many different machines, you can ship the torch.compile cache to these machines and skip the compilation steps.
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### E04c0aeade9a0982b561c79d3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
## Performance Tuning
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_ENABLE_TORCH_INFERENCE_MODE` | Control whether to use torch.inference_mode | `false` |
| `SGLANG_ENABLE_TORCH_COMPILE` | Enable torch.compile | `true` |
| `SGLANG_SET_CPU_AFFINITY` | Enable CPU affinity setting (often set to `1` in Docker builds) | `0` |
```

### E0378d6a07be801542c20d2ae

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
For more details, please refer to [PyTorch official documentation](https://pytorch.org/tutorials/recipes/torch_compile_caching_tutorial.html) and [Enabling cache for torch.compile](https://docs.sglang.ai/backend/hyperparameter_tuning.html#enabling-cache-for-torch-compile).
- To enable torchao quantization, add `--torchao-config int4wo-128`.
```

### E5858c0b6aa2464dc1072738e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
It supports other [quantization strategies (INT8/FP8)](https://github.com/sgl-project/sglang/blob/v0.3.6/python/sglang/srt/server_args.py#L671) as well.
- To enable fp8 weight quantization, add `--quantization fp8` on a fp16 checkpoint or directly load a fp8 checkpoint without specifying any arguments.
- To enable fp8 kv cache quantization, add `--kv-cache-dtype fp8_e5m2`.
```

### E55a42b362f0ccb7c56dd9aca

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
If you meet deadlock, please try to add `--disable-cuda-graph`
```

## official-020-2:oracle:oracle

SGLang v0.5.2：能否假定SGLANG_ENABLE_TORCH_COMPILE默认关闭？

必要要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

```json
null
```

实际输入证据：

### E24ec3bd0aec6fd7f17e6e464

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/references/environment_variables.md

```text
`SGLANG_ENABLE_TORCH_COMPILE` | Enable torch.compile | `true`
```

## official-020-2:bm25:retrieved

SGLang v0.5.2：能否假定SGLANG_ENABLE_TORCH_COMPILE默认关闭？

必要要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

```json
null
```

实际输入证据：

### E04c0aeade9a0982b561c79d3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
## Performance Tuning
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_ENABLE_TORCH_INFERENCE_MODE` | Control whether to use torch.inference_mode | `false` |
| `SGLANG_ENABLE_TORCH_COMPILE` | Enable torch.compile | `true` |
| `SGLANG_SET_CPU_AFFINITY` | Enable CPU affinity setting (often set to `1` in Docker builds) | `0` |
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### E0378d6a07be801542c20d2ae

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
For more details, please refer to [PyTorch official documentation](https://pytorch.org/tutorials/recipes/torch_compile_caching_tutorial.html) and [Enabling cache for torch.compile](https://docs.sglang.ai/backend/hyperparameter_tuning.html#enabling-cache-for-torch-compile).
- To enable torchao quantization, add `--torchao-config int4wo-128`.
```

### E6532df59fd0dd55e6db3b9fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-torch_compile_cache.md#L1-L4

```text
# Enabling cache for torch.compile

SGLang uses `max-autotune-no-cudagraphs` mode of torch.compile. The auto-tuning can be slow.
If you want to deploy a model on many different machines, you can ship the torch.compile cache to these machines and skip the compilation steps.
```

### Eae6183a3ed453e4929d9ddee

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
### Try other options
- `torch.compile` accelerates small models on small batch sizes.
You can enable it with `--enable-torch-compile`.
- Try other quantization (e.g.
FP8 quantization with `--quantization fp8`)
```

### Ea05186af02bae47f9a2d81f2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
| `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN` | Allows the scheduler to overwrite longer context length requests (often set to `1` in Docker builds) | `0` |
| `SGLANG_IS_FLASHINFER_AVAILABLE` | Control FlashInfer availability check | `true` |
| `SGLANG_SKIP_P2P_CHECK` | Skip P2P (peer-to-peer) access check | `false` |
| `SGL_CHUNKED_PREFIX_CACHE_THRESHOLD` | Sets the threshold for enabling chunked prefix caching | `8192` |
```

### E70c5727f50f834f5685f298f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
| `SGLANG_FUSED_MLA_ENABLE_ROPE_FUSION` | Enable RoPE fusion in Fused Multi-Layer Attention | `1` |
```

### Ec4678a8fc21dd044a00d2f47

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
- To enable `torch.compile` acceleration, add `--enable-torch-compile`.
It accelerates small models on small batch sizes.
By default, the cache path is located at `/tmp/torchinductor_root`, you can customize it using environment variable `TORCHINDUCTOR_CACHE_DIR`.
```

### E55a42b362f0ccb7c56dd9aca

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
If you meet deadlock, please try to add `--disable-cuda-graph`
```

## official-020-2:dense:retrieved

SGLang v0.5.2：能否假定SGLANG_ENABLE_TORCH_COMPILE默认关闭？

必要要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

```json
null
```

实际输入证据：

### E1ff39d43ec8ef2cc491f4d4c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L39-L41

```text
## Install SGLang

You can install SGLang using one of the methods below.
```

### E8651ea1f0391d57e95cc940c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L1-L3

```text
# Install SGLang

You can install SGLang using one of the methods below.
```

### E03955c38a5e61c3c67f1cecf

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L71-L77

```text
**Solved with**
```python/sglang/srt/layers/attention/triton_ops/decode_attention.py +410```
- If you get an error like `ImportError: cannot import name 'build_regex_from_schema' from 'outlines.fsm.json_schema'`, same with https://github.com/sgl-project/sglang/issues/2530
**Solved with** ```
```

### E9369c16d9538eeb85b2202d5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-attention_backend.md#L1-L4

```text
# Attention Backend

SGLang supports multiple attention backends. Each of them has different pros and cons.
You can test them according to your needs.
```

### Ec845f797c6676f4ac475e4e4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L1-L5

```text
# Environment Variables

SGLang supports various environment variables that can be used to configure its runtime behavior. This document provides a comprehensive list and aims to stay updated over time.

*Note: SGLang uses two prefixes for environment variables: `SGL_` and `SGLANG_`. This is likely due to historical reasons. While both are currently supported for different settings, future versions might consolidate them.*
```

### Ec0b1bd88b1cd27c667f8e004

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L71-L77

```text
## Issues
- If you get the error like `raise OutOfResources(self.metadata.shared, max_shared, "shared memory")`, same with https://github.com/sgl-project/sglang/issues/2384
```

### E867be2c7ab1891cef1ab0ed0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L71-L77

```text
downgrade vllm
```
- If you get an error like `RuntimeError: [enforce fail at /app/pytorch/third_party/gloo/gloo/transport/tcp/device.cc:83] ifa != nullptr. Unable to find address for: eth0' 
**Solved with** ifconfig check your eth number and  ```
export GLOO_SOCKET_IFNAME=your eth```
```

## official-020-2:hybrid:retrieved

SGLang v0.5.2：能否假定SGLANG_ENABLE_TORCH_COMPILE默认关闭？

必要要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

```json
null
```

实际输入证据：

### E04c0aeade9a0982b561c79d3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
## Performance Tuning
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_ENABLE_TORCH_INFERENCE_MODE` | Control whether to use torch.inference_mode | `false` |
| `SGLANG_ENABLE_TORCH_COMPILE` | Enable torch.compile | `true` |
| `SGLANG_SET_CPU_AFFINITY` | Enable CPU affinity setting (often set to `1` in Docker builds) | `0` |
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E3c3a3dc7ba007d74b5c8b0ce

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L7-L16

```text
## General Configuration
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_USE_MODELSCOPE` | Enable using models from ModelScope | `false` |
| `SGLANG_HOST_IP` | Host IP address for the server | `0.0.0.0` |
| `SGLANG_PORT` | Port for the server | auto-detected |
| `SGLANG_LOGGING_CONFIG_PATH` | Custom logging configuration path | Not set |
| `SGLANG_DISABLE_REQUEST_LOGGING` | Disable request logging | `false` |
```

### Ebcc291b3c6bc07b25f46a8f6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L17-L17

```text
Below are a few key settings to confirm or enable for SGLang:
```

### Ea05186af02bae47f9a2d81f2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
| `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN` | Allows the scheduler to overwrite longer context length requests (often set to `1` in Docker builds) | `0` |
| `SGLANG_IS_FLASHINFER_AVAILABLE` | Control FlashInfer availability check | `true` |
| `SGLANG_SKIP_P2P_CHECK` | Skip P2P (peer-to-peer) access check | `false` |
| `SGL_CHUNKED_PREFIX_CACHE_THRESHOLD` | Sets the threshold for enabling chunked prefix caching | `8192` |
```

### E70c5727f50f834f5685f298f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
| `SGLANG_FUSED_MLA_ENABLE_ROPE_FUSION` | Enable RoPE fusion in Fused Multi-Layer Attention | `1` |
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

### E31d76b4ee496eaa10e0edd9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L7-L16

```text
| `SGLANG_HEALTH_CHECK_TIMEOUT` | Timeout for health check in seconds | `20` |
```

## official-020-2:hybrid_rerank:retrieved

SGLang v0.5.2：能否假定SGLANG_ENABLE_TORCH_COMPILE默认关闭？

必要要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

```json
null
```

实际输入证据：

### E6532df59fd0dd55e6db3b9fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-torch_compile_cache.md#L1-L4

```text
# Enabling cache for torch.compile

SGLang uses `max-autotune-no-cudagraphs` mode of torch.compile. The auto-tuning can be slow.
If you want to deploy a model on many different machines, you can ship the torch.compile cache to these machines and skip the compilation steps.
```

### Ebcc291b3c6bc07b25f46a8f6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L17-L17

```text
Below are a few key settings to confirm or enable for SGLang:
```

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E2c33408cdce01cebc96efef3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-torch_compile_cache.md#L9-L13

```text
1. Generate the cache by setting TORCHINDUCTOR_CACHE_DIR and running the model once.
```
TORCHINDUCTOR_CACHE_DIR=/root/inductor_root_cache python3 -m sglang.launch_server --model meta-llama/Llama-3.1-8B-Instruct --enable-torch-compile
```
2. Copy the cache folder to other machines and launch the server with `TORCHINDUCTOR_CACHE_DIR`.
```

### E04c0aeade9a0982b561c79d3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
## Performance Tuning
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_ENABLE_TORCH_INFERENCE_MODE` | Control whether to use torch.inference_mode | `false` |
| `SGLANG_ENABLE_TORCH_COMPILE` | Enable torch.compile | `true` |
| `SGLANG_SET_CPU_AFFINITY` | Enable CPU affinity setting (often set to `1` in Docker builds) | `0` |
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

### Ea05186af02bae47f9a2d81f2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
| `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN` | Allows the scheduler to overwrite longer context length requests (often set to `1` in Docker builds) | `0` |
| `SGLANG_IS_FLASHINFER_AVAILABLE` | Control FlashInfer availability check | `true` |
| `SGLANG_SKIP_P2P_CHECK` | Skip P2P (peer-to-peer) access check | `false` |
| `SGL_CHUNKED_PREFIX_CACHE_THRESHOLD` | Sets the threshold for enabling chunked prefix caching | `8192` |
```

### E70c5727f50f834f5685f298f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
| `SGLANG_FUSED_MLA_ENABLE_ROPE_FUSION` | Enable RoPE fusion in Fused Multi-Layer Attention | `1` |
```

## official-020-3:oracle:oracle

SGLang v0.5.2：排查编译开关时，环境变量SGLANG_ENABLE_TORCH_COMPILE的意义和默认值是什么？

必要要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

```json
null
```

实际输入证据：

### E24ec3bd0aec6fd7f17e6e464

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/references/environment_variables.md

```text
`SGLANG_ENABLE_TORCH_COMPILE` | Enable torch.compile | `true`
```

## official-020-3:bm25:retrieved

SGLang v0.5.2：排查编译开关时，环境变量SGLANG_ENABLE_TORCH_COMPILE的意义和默认值是什么？

必要要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

```json
null
```

实际输入证据：

### E04c0aeade9a0982b561c79d3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
## Performance Tuning
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_ENABLE_TORCH_INFERENCE_MODE` | Control whether to use torch.inference_mode | `false` |
| `SGLANG_ENABLE_TORCH_COMPILE` | Enable torch.compile | `true` |
| `SGLANG_SET_CPU_AFFINITY` | Enable CPU affinity setting (often set to `1` in Docker builds) | `0` |
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### E0378d6a07be801542c20d2ae

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
For more details, please refer to [PyTorch official documentation](https://pytorch.org/tutorials/recipes/torch_compile_caching_tutorial.html) and [Enabling cache for torch.compile](https://docs.sglang.ai/backend/hyperparameter_tuning.html#enabling-cache-for-torch-compile).
- To enable torchao quantization, add `--torchao-config int4wo-128`.
```

### E6532df59fd0dd55e6db3b9fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-torch_compile_cache.md#L1-L4

```text
# Enabling cache for torch.compile

SGLang uses `max-autotune-no-cudagraphs` mode of torch.compile. The auto-tuning can be slow.
If you want to deploy a model on many different machines, you can ship the torch.compile cache to these machines and skip the compilation steps.
```

### Eae6183a3ed453e4929d9ddee

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-hyperparameter_tuning.md#L8-L77

```text
### Try other options
- `torch.compile` accelerates small models on small batch sizes.
You can enable it with `--enable-torch-compile`.
- Try other quantization (e.g.
FP8 quantization with `--quantization fp8`)
```

### Ea05186af02bae47f9a2d81f2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
| `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN` | Allows the scheduler to overwrite longer context length requests (often set to `1` in Docker builds) | `0` |
| `SGLANG_IS_FLASHINFER_AVAILABLE` | Control FlashInfer availability check | `true` |
| `SGLANG_SKIP_P2P_CHECK` | Skip P2P (peer-to-peer) access check | `false` |
| `SGL_CHUNKED_PREFIX_CACHE_THRESHOLD` | Sets the threshold for enabling chunked prefix caching | `8192` |
```

### E70c5727f50f834f5685f298f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
| `SGLANG_FUSED_MLA_ENABLE_ROPE_FUSION` | Enable RoPE fusion in Fused Multi-Layer Attention | `1` |
```

### Ec4678a8fc21dd044a00d2f47

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
- To enable `torch.compile` acceleration, add `--enable-torch-compile`.
It accelerates small models on small batch sizes.
By default, the cache path is located at `/tmp/torchinductor_root`, you can customize it using environment variable `TORCHINDUCTOR_CACHE_DIR`.
```

### E55a42b362f0ccb7c56dd9aca

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
If you meet deadlock, please try to add `--disable-cuda-graph`
```

## official-020-3:dense:retrieved

SGLang v0.5.2：排查编译开关时，环境变量SGLANG_ENABLE_TORCH_COMPILE的意义和默认值是什么？

必要要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

```json
null
```

实际输入证据：

### E112b956fffe3fc7785a2dec1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
## Model-Specific Options
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_USE_AITER` | Use AITER optimize implementation | `false` |
| `SGLANG_INT4_WEIGHT` | Enable INT4 weight quantization | `false` |
| `SGLANG_MOE_PADDING` | Enable MoE padding (sets padding size to 128 if value is `1`, often set to `1` in Docker builds) | `0` |
```

### E8e644a8686c6a13daccba2fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L86-L91

```text
## Profiling & Benchmarking

| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_TORCH_PROFILER_DIR` | Directory for PyTorch profiler output | `/tmp` |
| `SGLANG_PROFILE_WITH_STACK` | Set `with_stack` option (bool) for PyTorch profiler (capture stack trace) | `true` |
```

### E04c0aeade9a0982b561c79d3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
## Performance Tuning
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_ENABLE_TORCH_INFERENCE_MODE` | Control whether to use torch.inference_mode | `false` |
| `SGLANG_ENABLE_TORCH_COMPILE` | Enable torch.compile | `true` |
| `SGLANG_SET_CPU_AFFINITY` | Enable CPU affinity setting (often set to `1` in Docker builds) | `0` |
```

### E03955c38a5e61c3c67f1cecf

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L71-L77

```text
**Solved with**
```python/sglang/srt/layers/attention/triton_ops/decode_attention.py +410```
- If you get an error like `ImportError: cannot import name 'build_regex_from_schema' from 'outlines.fsm.json_schema'`, same with https://github.com/sgl-project/sglang/issues/2530
**Solved with** ```
```

### E3c3a3dc7ba007d74b5c8b0ce

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L7-L16

```text
## General Configuration
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_USE_MODELSCOPE` | Enable using models from ModelScope | `false` |
| `SGLANG_HOST_IP` | Host IP address for the server | `0.0.0.0` |
| `SGLANG_PORT` | Port for the server | auto-detected |
| `SGLANG_LOGGING_CONFIG_PATH` | Custom logging configuration path | Not set |
| `SGLANG_DISABLE_REQUEST_LOGGING` | Disable request logging | `false` |
```

### E16f7d126776da84bba5a8652

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
| `SGLANG_FORCE_FP8_MARLIN` | Force using FP8 MARLIN kernels even if other FP8 kernels are available | `false` |
| `SGLANG_ENABLE_FLASHINFER_GEMM` | Use flashinfer kernels when running blockwise fp8 GEMM on Blackwell GPUs | `false` |
| `SGLANG_SUPPORT_CUTLASS_BLOCK_FP8` | Use Cutlass kernels when running blockwise fp8 GEMM on Hopper or Blackwell GPUs | `false` |
| `SGLANG_CUTLASS_MOE` | Use Cutlass FP8 MoE kernel on Blackwell GPUs | `false` |
```

### Ea05186af02bae47f9a2d81f2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
| `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN` | Allows the scheduler to overwrite longer context length requests (often set to `1` in Docker builds) | `0` |
| `SGLANG_IS_FLASHINFER_AVAILABLE` | Control FlashInfer availability check | `true` |
```

## official-020-3:hybrid:retrieved

SGLang v0.5.2：排查编译开关时，环境变量SGLANG_ENABLE_TORCH_COMPILE的意义和默认值是什么？

必要要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

```json
null
```

实际输入证据：

### E04c0aeade9a0982b561c79d3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
## Performance Tuning
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_ENABLE_TORCH_INFERENCE_MODE` | Control whether to use torch.inference_mode | `false` |
| `SGLANG_ENABLE_TORCH_COMPILE` | Enable torch.compile | `true` |
| `SGLANG_SET_CPU_AFFINITY` | Enable CPU affinity setting (often set to `1` in Docker builds) | `0` |
```

### E112b956fffe3fc7785a2dec1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
## Model-Specific Options
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_USE_AITER` | Use AITER optimize implementation | `false` |
| `SGLANG_INT4_WEIGHT` | Enable INT4 weight quantization | `false` |
| `SGLANG_MOE_PADDING` | Enable MoE padding (sets padding size to 128 if value is `1`, often set to `1` in Docker builds) | `0` |
```

### E8e644a8686c6a13daccba2fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L86-L91

```text
## Profiling & Benchmarking

| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_TORCH_PROFILER_DIR` | Directory for PyTorch profiler output | `/tmp` |
| `SGLANG_PROFILE_WITH_STACK` | Set `with_stack` option (bool) for PyTorch profiler (capture stack trace) | `true` |
```

### E3c3a3dc7ba007d74b5c8b0ce

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L7-L16

```text
## General Configuration
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_USE_MODELSCOPE` | Enable using models from ModelScope | `false` |
| `SGLANG_HOST_IP` | Host IP address for the server | `0.0.0.0` |
| `SGLANG_PORT` | Port for the server | auto-detected |
| `SGLANG_LOGGING_CONFIG_PATH` | Custom logging configuration path | Not set |
| `SGLANG_DISABLE_REQUEST_LOGGING` | Disable request logging | `false` |
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ea05186af02bae47f9a2d81f2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
| `SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN` | Allows the scheduler to overwrite longer context length requests (often set to `1` in Docker builds) | `0` |
| `SGLANG_IS_FLASHINFER_AVAILABLE` | Control FlashInfer availability check | `true` |
| `SGLANG_SKIP_P2P_CHECK` | Skip P2P (peer-to-peer) access check | `false` |
| `SGL_CHUNKED_PREFIX_CACHE_THRESHOLD` | Sets the threshold for enabling chunked prefix caching | `8192` |
```

### E70c5727f50f834f5685f298f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L18-L29

```text
| `SGLANG_FUSED_MLA_ENABLE_ROPE_FUSION` | Enable RoPE fusion in Fused Multi-Layer Attention | `1` |
```

### E16f7d126776da84bba5a8652

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L52-L62

```text
| `SGLANG_FORCE_FP8_MARLIN` | Force using FP8 MARLIN kernels even if other FP8 kernels are available | `false` |
```

## official-020-3:hybrid_rerank:retrieved

SGLang v0.5.2：排查编译开关时，环境变量SGLANG_ENABLE_TORCH_COMPILE的意义和默认值是什么？

必要要点：SGLANG_ENABLE_TORCH_COMPILE控制torch.compile，文档默认true。

禁止误读：该环境变量默认禁用torch.compile。

```json
null
```

实际输入证据：

### E695ba05057649c70fdf10c01

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L77-L84

```text
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_IS_IN_CI` | Indicates if running in CI environment | `false` |
| `SGLANG_AMD_CI` | Indicates running in AMD CI environment | `0` |
| `SGLANG_TEST_RETRACT` | Enable retract decode testing | `false` |
| `SGLANG_RECORD_STEP_TIME` | Record step time for profiling | `false` |
| `SGLANG_TEST_REQUEST_TIME_STATS` | Test request time statistics | `false` |
```

### E6532df59fd0dd55e6db3b9fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-torch_compile_cache.md#L1-L4

```text
# Enabling cache for torch.compile

SGLang uses `max-autotune-no-cudagraphs` mode of torch.compile. The auto-tuning can be slow.
If you want to deploy a model on many different machines, you can ship the torch.compile cache to these machines and skip the compilation steps.
```

### Ec845f797c6676f4ac475e4e4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L1-L5

```text
# Environment Variables

SGLang supports various environment variables that can be used to configure its runtime behavior. This document provides a comprehensive list and aims to stay updated over time.

*Note: SGLang uses two prefixes for environment variables: `SGL_` and `SGLANG_`. This is likely due to historical reasons. While both are currently supported for different settings, future versions might consolidate them.*
```

### Ec4678a8fc21dd044a00d2f47

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
- To enable `torch.compile` acceleration, add `--enable-torch-compile`.
It accelerates small models on small batch sizes.
By default, the cache path is located at `/tmp/torchinductor_root`, you can customize it using environment variable `TORCHINDUCTOR_CACHE_DIR`.
```

### Ed5bb7f1eaddc28afe2bf92c7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-attention_backend.md#L28-L57

```text
- Torch Native
```bash
python3 -m sglang.launch_server --model meta-llama/Meta-Llama-3.1-8B-Instruct --attention-backend torch_native
```
```

### E92661bb4894e8ef80693d008

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L77-L84

```text
| `SGLANG_CI_SMALL_KV_SIZE` | Use small KV cache size in CI | Not set |
```

### E0378d6a07be801542c20d2ae

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
For more details, please refer to [PyTorch official documentation](https://pytorch.org/tutorials/recipes/torch_compile_caching_tutorial.html) and [Enabling cache for torch.compile](https://docs.sglang.ai/backend/hyperparameter_tuning.html#enabling-cache-for-torch-compile).
- To enable torchao quantization, add `--torchao-config int4wo-128`.
```

### E5858c0b6aa2464dc1072738e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L37-L42

```text
It supports other [quantization strategies (INT8/FP8)](https://github.com/sgl-project/sglang/blob/v0.3.6/python/sglang/srt/server_args.py#L671) as well.
- To enable fp8 weight quantization, add `--quantization fp8` on a fp16 checkpoint or directly load a fp8 checkpoint without specifying any arguments.
- To enable fp8 kv cache quantization, add `--kv-cache-dtype fp8_e5m2`.
```

## official-020-4:oracle:oracle

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在amd_gpu场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
{
  "conversation_id": "23c8b1b0-7856-4be9-90d2-8e4ffc0d2040",
  "answer": "资料库中没有找到可以支持这个问题的证据。请换个问法或先导入相关文档。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在amd_gpu场景下精确的P95延迟毫秒值吗？",
      "hits": 0,
      "evidence": 0
    }
  ]
}
```

实际输入证据：

## official-020-4:bm25:retrieved

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在amd_gpu场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### Ed59dc37ef0b0397387266086

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L5-L6

```text
This page primarily applies to common NVIDIA GPU platforms.
For other or newer platforms, please refer to the dedicated pages for [NVIDIA Blackwell GPUs](../platforms/blackwell_gpu.md), [AMD GPUs](../platforms/amd_gpu.md), [Intel Xeon CPUs](../platforms/cpu_server.md), [NVIDIA Jetson](../platforms/nvidia_jetson.md), [Ascend NPUs](../platforms/ascend_npu.md).
```

### Eac21656670164d7db38d4f80

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L1-L3

```text
# AMD GPUs

This document describes how run SGLang on AMD GPUs. If you encounter issues or have questions, please [open an issue](https://github.com/sgl-project/sglang/issues).
```

### Ec38170f0e0078fe99cbbc37b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L87-L114

```text
With your AMD system properly configured and SGLang installed, you can now fully leverage AMD hardware to power SGLang’s machine learning capabilities.
```

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E88c0d498f39a5afd01c0d0fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L87-L114

```text
4.
To verify the utility, you can run a benchmark in another terminal or refer to [other docs](https://docs.sglang.ai/backend/openai_api_completions.html) to send requests to the engine.
```bash
   drun sglang_image \
       python3 -m sglang.bench_serving \
       --backend sglang \
       --dataset-name random \
       --num-prompts 4000 \
       --random-input 128 \
       --random-output 128
   ```
```

### E6dcab46e61ae3d96fcdbdc18

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L87-L114

```text
3.
Launch the server.
**NOTE:** Replace `<secret>` below with your [huggingface hub token](https://huggingface.co/docs/hub/en/security-tokens).
```bash
   drun -p 30000:30000 \
       -v ~/.cache/huggingface:/root/.cache/huggingface \
       --env "HF_TOKEN=<secret>" \
       sglang_image \
       python3 -m sglang.launch_server \
       --model-path NousResearch/Meta-Llama-3.1-8B \
       --host 0.0.0.0 \
       --port 30000
   ```
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

## official-020-4:dense:retrieved

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在amd_gpu场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### Eac21656670164d7db38d4f80

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L1-L3

```text
# AMD GPUs

This document describes how run SGLang on AMD GPUs. If you encounter issues or have questions, please [open an issue](https://github.com/sgl-project/sglang/issues).
```

### Ec195863d548a6b5e424b535a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L5-L7

```text
## Motivation
- Support DeepseekV3 on AMD Instinct MI300X GPU
<!-- Explain the purpose of this PR and the goals it aims to achieve. -->
```

### E129c5629e0e269f5141eaa20

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
    -p 8000:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    --model Qwen/Qwen3-0.6B
```
This image can also be used with other container engines such as [Podman](https://podman.io/).
```

### E76dca9b42c02be4cdcff9c3e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
```bash
podman run --device nvidia.com/gpu=all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HUGGING_FACE_HUB_TOKEN=$HF_TOKEN" \
  -p 8000:8000 \
  --ipc=host \
  docker.io/vllm/vllm-openai:latest \
  --model Qwen/Qwen3-0.6B
```
You can add any other [engine-args](../configuration/engine_args.md) you need after the image tag (`vllm/vllm-openai:latest`).
```

### Ec38170f0e0078fe99cbbc37b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L87-L114

```text
With your AMD system properly configured and SGLang installed, you can now fully leverage AMD hardware to power SGLang’s machine learning capabilities.
```

### E9a5dde88f838a11ba9dccd64

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
## Use vLLM's Official Docker Image
vLLM offers an official Docker image for deployment.
The image can be used to run OpenAI compatible server and is available on Docker Hub as [vllm/vllm-openai](https://hub.docker.com/r/vllm/vllm-openai/tags).
```

### Ec94bd3c0efd3b0755001340f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L5-L37

```text
!!
! note
You can either use the `ipc=host` flag or `--shm-size` flag to allow the
container to access the host's shared memory.
vLLM uses PyTorch, which uses shared
memory to share data between processes under the hood, particularly for tensor parallel inference.
```

### E88c0d498f39a5afd01c0d0fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L87-L114

```text
4.
To verify the utility, you can run a benchmark in another terminal or refer to [other docs](https://docs.sglang.ai/backend/openai_api_completions.html) to send requests to the engine.
```bash
   drun sglang_image \
       python3 -m sglang.bench_serving \
       --backend sglang \
       --dataset-name random \
       --num-prompts 4000 \
       --random-input 128 \
       --random-output 128
   ```
```

## official-020-4:hybrid:retrieved

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在amd_gpu场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### Eac21656670164d7db38d4f80

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L1-L3

```text
# AMD GPUs

This document describes how run SGLang on AMD GPUs. If you encounter issues or have questions, please [open an issue](https://github.com/sgl-project/sglang/issues).
```

### Ec38170f0e0078fe99cbbc37b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L87-L114

```text
With your AMD system properly configured and SGLang installed, you can now fully leverage AMD hardware to power SGLang’s machine learning capabilities.
```

### Ec195863d548a6b5e424b535a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L5-L7

```text
## Motivation
- Support DeepseekV3 on AMD Instinct MI300X GPU
<!-- Explain the purpose of this PR and the goals it aims to achieve. -->
```

### E4e1044238dc894ec734a0d3c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L12-L19

```text
### TODO
- [x] amd base image testing https://github.com/sgl-project/sglang/pull/2692
- [x] sgl-kernel add amd backend https://github.com/sgl-project/sglang/pull/3287
- [x] DeepseekV3 triton MOE config optimization https://github.com/sgl-project/sglang/pull/3146
```

### E7d31667c9ca749ba09ace7a1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L5-L13

```text
## System Configuration
When using AMD GPUs (such as MI300X), certain system-level optimizations help ensure stable performance.
Here we take MI300X as an example.
AMD provides official documentation for MI300X optimization and system tuning:
- [AMD MI300X Tuning Guides](https://rocm.docs.amd.com/en/latest/how-to/tuning-guides/mi300x/index.html)
```

### E88c0d498f39a5afd01c0d0fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L87-L114

```text
4.
To verify the utility, you can run a benchmark in another terminal or refer to [other docs](https://docs.sglang.ai/backend/openai_api_completions.html) to send requests to the engine.
```bash
   drun sglang_image \
       python3 -m sglang.bench_serving \
       --backend sglang \
       --dataset-name random \
       --num-prompts 4000 \
       --random-input 128 \
       --random-output 128
   ```
```

### E6dcab46e61ae3d96fcdbdc18

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L87-L114

```text
3.
Launch the server.
**NOTE:** Replace `<secret>` below with your [huggingface hub token](https://huggingface.co/docs/hub/en/security-tokens).
```bash
   drun -p 30000:30000 \
       -v ~/.cache/huggingface:/root/.cache/huggingface \
       --env "HF_TOKEN=<secret>" \
       sglang_image \
       python3 -m sglang.launch_server \
       --model-path NousResearch/Meta-Llama-3.1-8B \
       --host 0.0.0.0 \
       --port 30000
   ```
```

### Ef875130d2ac8c37dc2ed476c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L12-L19

```text
- [ ] batch mm for FP8 optimization on rocm
- [x] composable kernel block gemm https://github.com/sgl-project/sglang/pull/4075
```

### Eca92fdaba7b018d8ee335a73

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-pr-2601.md#L12-L19

```text
- [x] ep moe
<!
-- Describe the changes made in this PR.
-->
```

### E9aa3bb3ce364b986f85ab77d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L5-L13

```text
- [LLM inference performance validation on AMD Instinct MI300X](https://rocm.docs.amd.com/en/latest/how-to/rocm-for-ai/inference/vllm-benchmark.html)
- [AMD Instinct MI300X System Optimization](https://rocm.docs.amd.com/en/latest/how-to/system-optimization/mi300x.html)
```

## official-020-4:hybrid_rerank:retrieved

SGLang v0.5.2：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在amd_gpu场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### Ec42bb7b2ccabdad49a03155f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
## Method 2: From source
```bash
# Use the last release branch
git clone -b v0.5.2 https://github.com/sgl-project/sglang.git
cd sglang

# Install the python packages
pip install --upgrade pip
pip install -e "python[all]"
```
**Quick fixes to common problems**
- If you want to develop SGLang, it is recommended to use docker.
Please refer to [setup docker container](../developer_guide/development_guide_using_docker.md#setup-docker-container).
```

### E2155f15de5afe18bf9c36f0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-amd_gpu.md#L43-L58

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

### E836c7d1b89a88031ebc19bb7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
You can install the frontend locally without needing a GPU, while the backend can be set up on a GPU-enabled machine.
To install the frontend, run `pip install sglang`, and for the backend, use `pip install sglang[srt]`.
`srt` is the abbreviation of SGLang runtime.
```

### Edf940734964cbe02dabf42e7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L38-L52

```text
```bash
docker run --gpus all \
    --shm-size 32g \
    -p 30000:30000 \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    --env "HF_TOKEN=<secret>" \
    --ipc=host \
    lmsysorg/sglang:latest \
    python3 -m sglang.launch_server --model-path meta-llama/Llama-3.1-8B-Instruct --host 0.0.0.0 --port 30000
```
```

### E695ba05057649c70fdf10c01

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-environment_variables.md#L77-L84

```text
| Environment Variable | Description | Default Value |
| --- | --- | --- |
| `SGLANG_IS_IN_CI` | Indicates if running in CI environment | `false` |
| `SGLANG_AMD_CI` | Indicates running in AMD CI environment | `0` |
| `SGLANG_TEST_RETRACT` | Enable retract decode testing | `false` |
| `SGLANG_RECORD_STEP_TIME` | Record step time for profiling | `false` |
| `SGLANG_TEST_REQUEST_TIME_STATS` | Test request time statistics | `false` |
```

### Eb4f523faf06b93c9716166d6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L23-L36

```text
The docker image is `lmsysorg/sglang:dev`.
```

### E60efa2876c564037d25230c7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
- To reinstall flashinfer locally, use the following command: `pip3 install --upgrade flashinfer-python --force-reinstall --no-deps` and then delete the cache with `rm -rf ~/.cache/flashinfer`.
- If you only need to use OpenAI API models with the frontend language, you can avoid installing other dependencies by using `pip install "sglang[openai]"`.
- The language frontend operates independently of the backend runtime.
```

### Eb87769bfc3e391ac8b6ece77

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
It only supports sm75 and above.
If you encounter any FlashInfer-related issues on sm75+ devices (e.g., T4, A10, A100, L4, L40S, H100), please switch to other kernels by adding `--attention-backend triton --sampling-backend pytorch` and open an issue on GitHub.
```

### Ed40ac9f26230255755dbb880

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L126-L131

```text
## Common Notes
- [FlashInfer](https://github.com/flashinfer-ai/flashinfer) is the default attention kernel backend.
```

## official-022-1:oracle:oracle

CUDA 13.0.1：local与shared memory的作用域和生命周期有何区别？

必要要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

```json
null
```

实际输入证据：

### E2998a9d5088e49e507e777cd

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#memory-hierarchy

```text
Each thread has private local memory. Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
```

## official-022-1:bm25:retrieved

CUDA 13.0.1：local与shared memory的作用域和生命周期有何区别？

必要要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

```json
null
```

实际输入证据：

### Edb4fe65bec83c651e06dfe24

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
5.3.
Memory Hierarchy
CUDA threads may access data from multiple memory spaces during their execution as illustrated by Figure 6.
Each thread has private local memory.
Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
Thread blocks in a thread block cluster can perform read, write, and atomics operations on each other’s shared memory.
All threads have access to the same global memory.
```

### E26f4250aa57456c8a93978de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

### E886d8ee4d345e68795a91fc2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
does not support Managed Memory: handles to this type of memory may not be shared through
any of the mechanisms discussed in this section.
On systems with full CUDA Unified Memory support,
System-Allocated Memory is Inter-Process Communication (IPC) capable.
Once access to System-Allocated Memory has been shared with other processes,
```

### Edf9df952793566dbe1cf0940

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
24.2.2.4.
Atomic accesses & synchronization primitives
CUDA Unified Memory supports all atomic operations available to host and device threads,
enabling all threads to cooperate by concurrently accessing the same shared memory location.
The CUDA C++ standard library
```

### E1cec5f1657fa6e7dc4b6eac9

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L476-L479

```text
## Output

Now we can write all of calculated result from local register memory
to final output global memory.
```

### E3cde33937aaf59d90c01188e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
There are also two additional read-only memory spaces accessible by all threads: the constant and texture memory spaces.
The global, constant, and texture memory spaces are optimized for different memory usages (see Device Memory Accesses).
Texture memory also offers different addressing modes, as well as data filtering, for some specific data formats (see Texture and Surface Memory).
```

### E5f547b764d41ee021d6de85d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
The global, constant, and texture memory spaces are persistent across kernel launches by the same application.
```

### Ec62b71f33327c96106baa4e7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
The following code sample is a straightforward implementation of matrix multiplication that does not take advantage of shared memory.
Each thread reads one row of A and one column of B and computes the corresponding element of C as illustrated in Figure 8.
A is therefore read B.width times from global memory and B is read A.height times.
```

### E5ee5e8b68e1ef766abe3ad17

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
Note
As of now, using IPC with Unified Memory can have significant performance implications.
Many applications prefer to manage one GPU per process, but still need to use Unified Memory,
for example for over-subscription, and access it from multiple GPUs.
CUDA IPC (see Interprocess Communication)
```

### E42814340a07b80e201e6e128

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
the same Programming Model applies,
similar to File-backed Unified Memory.
See the following references for more information on various ways of creating
```

### Ef435059a27602151178349e6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
IPC-capable System-Allocated Memory under Linux:
```

## official-022-1:dense:retrieved

CUDA 13.0.1：local与shared memory的作用域和生命周期有何区别？

必要要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

```json
null
```

实际输入证据：

### E181ac7ad650994d7f0c7cd40

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L72-L72

```text
Full CUDA Unified Memory: all memory has full support. This includes System-Allocated and CUDA Managed Memory.
```

### E886d8ee4d345e68795a91fc2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
does not support Managed Memory: handles to this type of memory may not be shared through
any of the mechanisms discussed in this section.
On systems with full CUDA Unified Memory support,
System-Allocated Memory is Inter-Process Communication (IPC) capable.
Once access to System-Allocated Memory has been shared with other processes,
```

### Ee0cbe7a9d751458c84c906b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L80-L80

```text
By blocking the computation this way, we take advantage of fast shared memory and save a lot of global memory bandwidth since A is only read (B.width / block_size) times from global memory and B is read (A.height / block_size) times.
```

### E0a73c6fa9de0d1f1e502224d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L335-L337

```text
24.1.2.2. Allocation API for CUDA Managed Memory: cudaMallocManaged()

On systems with CUDA Managed Memory support, unified memory may be allocated using:
```

### Eb555b6140eca7526e6331d8a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L35-L37

```text
The total amount of shared memory required for a block is equal to the sum of the amount of statically allocated shared memory and the amount of dynamically allocated shared memory.
```

### E5ee5e8b68e1ef766abe3ad17

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
Note
As of now, using IPC with Unified Memory can have significant performance implications.
Many applications prefer to manage one GPU per process, but still need to use Unified Memory,
for example for over-subscription, and access it from multiple GPUs.
CUDA IPC (see Interprocess Communication)
```

### E42814340a07b80e201e6e128

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
the same Programming Model applies,
similar to File-backed Unified Memory.
See the following references for more information on various ways of creating
```

### Ef435059a27602151178349e6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
IPC-capable System-Allocated Memory under Linux:
```

### Ede50619bb283b920ece63c65

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L35-L37

```text
The number of blocks and warps residing on each multiprocessor for a given kernel call depends on the execution configuration of the call (Execution Configuration), the memory resources of the multiprocessor, and the resource requirements of the kernel as described in Hardware Multithreading.
Register and shared memory usage are reported by the compiler when compiling with the --ptxas-options=-v option.
```

## official-022-1:hybrid:retrieved

CUDA 13.0.1：local与shared memory的作用域和生命周期有何区别？

必要要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

```json
null
```

实际输入证据：

### E886d8ee4d345e68795a91fc2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
does not support Managed Memory: handles to this type of memory may not be shared through
any of the mechanisms discussed in this section.
On systems with full CUDA Unified Memory support,
System-Allocated Memory is Inter-Process Communication (IPC) capable.
Once access to System-Allocated Memory has been shared with other processes,
```

### Edb4fe65bec83c651e06dfe24

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
5.3.
Memory Hierarchy
CUDA threads may access data from multiple memory spaces during their execution as illustrated by Figure 6.
Each thread has private local memory.
Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
Thread blocks in a thread block cluster can perform read, write, and atomics operations on each other’s shared memory.
All threads have access to the same global memory.
```

### Eb555b6140eca7526e6331d8a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L35-L37

```text
The total amount of shared memory required for a block is equal to the sum of the amount of statically allocated shared memory and the amount of dynamically allocated shared memory.
```

### E26f4250aa57456c8a93978de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

### E181ac7ad650994d7f0c7cd40

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L72-L72

```text
Full CUDA Unified Memory: all memory has full support. This includes System-Allocated and CUDA Managed Memory.
```

### E5ee5e8b68e1ef766abe3ad17

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
Note
As of now, using IPC with Unified Memory can have significant performance implications.
Many applications prefer to manage one GPU per process, but still need to use Unified Memory,
for example for over-subscription, and access it from multiple GPUs.
CUDA IPC (see Interprocess Communication)
```

### E42814340a07b80e201e6e128

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
the same Programming Model applies,
similar to File-backed Unified Memory.
See the following references for more information on various ways of creating
```

### Ef435059a27602151178349e6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
IPC-capable System-Allocated Memory under Linux:
```

### E3cde33937aaf59d90c01188e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
There are also two additional read-only memory spaces accessible by all threads: the constant and texture memory spaces.
The global, constant, and texture memory spaces are optimized for different memory usages (see Device Memory Accesses).
Texture memory also offers different addressing modes, as well as data filtering, for some specific data formats (see Texture and Surface Memory).
```

### E5f547b764d41ee021d6de85d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
The global, constant, and texture memory spaces are persistent across kernel launches by the same application.
```

### Ede50619bb283b920ece63c65

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L35-L37

```text
The number of blocks and warps residing on each multiprocessor for a given kernel call depends on the execution configuration of the call (Execution Configuration), the memory resources of the multiprocessor, and the resource requirements of the kernel as described in Hardware Multithreading.
Register and shared memory usage are reported by the compiler when compiling with the --ptxas-options=-v option.
```

## official-022-1:hybrid_rerank:retrieved

CUDA 13.0.1：local与shared memory的作用域和生命周期有何区别？

必要要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

```json
null
```

实际输入证据：

### Edb4fe65bec83c651e06dfe24

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
5.3.
Memory Hierarchy
CUDA threads may access data from multiple memory spaces during their execution as illustrated by Figure 6.
Each thread has private local memory.
Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
Thread blocks in a thread block cluster can perform read, write, and atomics operations on each other’s shared memory.
All threads have access to the same global memory.
```

### E26f4250aa57456c8a93978de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

### Ed5b7174e4b1fb72a7ce2f862

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
// Get sub-matrix Asub of A
Matrix Asub = GetSubMatrix(A, blockRow, m);
// Get sub-matrix Bsub of B
Matrix Bsub = GetSubMatrix(B, m, blockCol);
// Shared memory used to store Asub and Bsub respectively
__shared__ float As[BLOCK_SIZE][BLOCK_SIZE];
__shared__ float Bs[BLOCK_SIZE][BLOCK_SIZE];
// Load Asub and Bsub from device memory to shared memory
// Each thread loads one element of each sub-matrix
```

### Ee0cbe7a9d751458c84c906b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L80-L80

```text
By blocking the computation this way, we take advantage of fast shared memory and save a lot of global memory bandwidth since A is only read (B.width / block_size) times from global memory and B is read (A.height / block_size) times.
```

### Edf9df952793566dbe1cf0940

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
24.2.2.4.
Atomic accesses & synchronization primitives
CUDA Unified Memory supports all atomic operations available to host and device threads,
enabling all threads to cooperate by concurrently accessing the same shared memory location.
The CUDA C++ standard library
```

### E3cde33937aaf59d90c01188e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
There are also two additional read-only memory spaces accessible by all threads: the constant and texture memory spaces.
The global, constant, and texture memory spaces are optimized for different memory usages (see Device Memory Accesses).
Texture memory also offers different addressing modes, as well as data filtering, for some specific data formats (see Texture and Surface Memory).
```

### E5f547b764d41ee021d6de85d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
The global, constant, and texture memory spaces are persistent across kernel launches by the same application.
```

### Ec62b71f33327c96106baa4e7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
The following code sample is a straightforward implementation of matrix multiplication that does not take advantage of shared memory.
Each thread reads one row of A and one column of B and computes the corresponding element of C as illustrated in Figure 8.
A is therefore read B.width times from global memory and B is read A.height times.
```

### Efc3c51f8f613f4d080c9f09c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
// required to compute Csub
// Multiply each pair of sub-matrices together
// and accumulate the results
for (int m = 0;
m < (A.width / BLOCK_SIZE);
++m) {
```

### Eae2611959395f1f39148cb16

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
// before starting the computation
```

## official-022-2:oracle:oracle

CUDA 13.0.1：能否把一个普通线程块的shared memory当全grid共享空间？

必要要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

```json
null
```

实际输入证据：

### E2998a9d5088e49e507e777cd

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#memory-hierarchy

```text
Each thread has private local memory. Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
```

## official-022-2:bm25:retrieved

CUDA 13.0.1：能否把一个普通线程块的shared memory当全grid共享空间？

必要要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

```json
null
```

实际输入证据：

### E26f4250aa57456c8a93978de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

### E886d8ee4d345e68795a91fc2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
does not support Managed Memory: handles to this type of memory may not be shared through
any of the mechanisms discussed in this section.
On systems with full CUDA Unified Memory support,
System-Allocated Memory is Inter-Process Communication (IPC) capable.
Once access to System-Allocated Memory has been shared with other processes,
```

### Edf9df952793566dbe1cf0940

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
24.2.2.4.
Atomic accesses & synchronization primitives
CUDA Unified Memory supports all atomic operations available to host and device threads,
enabling all threads to cooperate by concurrently accessing the same shared memory location.
The CUDA C++ standard library
```

### Edb4fe65bec83c651e06dfe24

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
5.3.
Memory Hierarchy
CUDA threads may access data from multiple memory spaces during their execution as illustrated by Figure 6.
Each thread has private local memory.
Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
Thread blocks in a thread block cluster can perform read, write, and atomics operations on each other’s shared memory.
All threads have access to the same global memory.
```

### E058aff20cdaceda83a69c4c5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L200-L200

```text
Figure 9 Matrix Multiplication with Shared Memory
```

### Ec62b71f33327c96106baa4e7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
The following code sample is a straightforward implementation of matrix multiplication that does not take advantage of shared memory.
Each thread reads one row of A and one column of B and computes the corresponding element of C as illustrated in Figure 8.
A is therefore read B.width times from global memory and B is read A.height times.
```

### E5ee5e8b68e1ef766abe3ad17

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
Note
As of now, using IPC with Unified Memory can have significant performance implications.
Many applications prefer to manage one GPU per process, but still need to use Unified Memory,
for example for over-subscription, and access it from multiple GPUs.
CUDA IPC (see Interprocess Communication)
```

### E42814340a07b80e201e6e128

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
the same Programming Model applies,
similar to File-backed Unified Memory.
See the following references for more information on various ways of creating
```

### Ef435059a27602151178349e6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
IPC-capable System-Allocated Memory under Linux:
```

### Ec5e671a6a30fd10316381a19

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
provides many heterogeneous synchronization primitives tuned for concurrent use between host and device threads,
including cuda::atomic, cuda::atomic_ref, cuda::barrier, cuda::semaphore, among many others.
On systems without CPU and GPU page tables: hardware coherency vs.
software coherency,
atomic accesses from the device to file-backed host memory are not supported.
```

### E1e6e9b8c1adb15ad22b95aa6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
The following example code is valid on systems with CPU and GPU page tables: hardware coherency vs.
software coherency
```

## official-022-2:dense:retrieved

CUDA 13.0.1：能否把一个普通线程块的shared memory当全grid共享空间？

必要要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

```json
null
```

实际输入证据：

### Edb4fe65bec83c651e06dfe24

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
5.3.
Memory Hierarchy
CUDA threads may access data from multiple memory spaces during their execution as illustrated by Figure 6.
Each thread has private local memory.
Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
Thread blocks in a thread block cluster can perform read, write, and atomics operations on each other’s shared memory.
All threads have access to the same global memory.
```

### E65e628476282c93a5e23d8ed

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L104-L123

```text
all threads may access System-Allocated Memory and CUDA Managed Memory.
These systems include NVIDIA Grace Hopper, IBM Power9 + Volta, and modern Linux systems with HMM enabled (see next bullet), among others.
Linux HMM requires Linux kernel version 6.1.24+, 6.2.11+ or 6.3+,
devices with compute capability 7.5 or higher and
a CUDA driver version 535+ installed with
Open Kernel Modules.
```

### E743f50645474beacb25db53c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-thread-hierarchy.md#L68-L68

```text
For efficient cooperation, shared memory is expected to be a low-latency memory near each processor core (much like an L1 cache) and __syncthreads() is expected to be lightweight.
```

### E0a73c6fa9de0d1f1e502224d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L335-L337

```text
24.1.2.2. Allocation API for CUDA Managed Memory: cudaMallocManaged()

On systems with CUDA Managed Memory support, unified memory may be allocated using:
```

### Eaf67f52334bd8cad1bd2f95b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-thread-hierarchy.md#L9-L32

```text
...
}
There is a limit to the number of threads per block, since all threads of a block are expected to reside on the same streaming multiprocessor core and must share the limited memory resources of that core.
On current GPUs, a thread block may contain up to 1024 threads.
```

### E3cde33937aaf59d90c01188e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
There are also two additional read-only memory spaces accessible by all threads: the constant and texture memory spaces.
The global, constant, and texture memory spaces are optimized for different memory usages (see Device Memory Accesses).
Texture memory also offers different addressing modes, as well as data filtering, for some specific data formats (see Texture and Surface Memory).
```

### E5f547b764d41ee021d6de85d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
The global, constant, and texture memory spaces are persistent across kernel launches by the same application.
```

### Edaa9604125c42b15c4514a36

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L104-L123

```text
The behavior of an application that attempts to use Unified Memory on a system that does not support it is undefined.
The following properties enable CUDA applications to check the level of system support for Unified Memory, and
to be portable between systems with different levels of support:
pageableMemoryAccess: This property is set to 1 on systems with CUDA Unified Memory support where
```

### E8b7ebdb27cf3dd43e3f41148

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L104-L123

```text
concurrentManagedAccess: This property is set to 1 on systems with full CUDA Managed Memory support.
When this property is set to 0, there is only partial support for Unified Memory in CUDA Managed Memory.
For Tegra support of Unified Memory, see
CUDA for Tegra Memory Management.
A program may query the level of GPU support for CUDA Unified Memory, by querying the attributes in
Table 31 using  cudaGetDeviceProperties().
```

### E1f42588fd1ceeafd19cf262d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-thread-hierarchy.md#L9-L32

```text
int main()
{
...
// Kernel invocation with one block of N * N * 1 threads
int numBlocks = 1;
dim3 threadsPerBlock(N, N);
```

## official-022-2:hybrid:retrieved

CUDA 13.0.1：能否把一个普通线程块的shared memory当全grid共享空间？

必要要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

```json
null
```

实际输入证据：

### Edb4fe65bec83c651e06dfe24

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
5.3.
Memory Hierarchy
CUDA threads may access data from multiple memory spaces during their execution as illustrated by Figure 6.
Each thread has private local memory.
Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
Thread blocks in a thread block cluster can perform read, write, and atomics operations on each other’s shared memory.
All threads have access to the same global memory.
```

### E886d8ee4d345e68795a91fc2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
does not support Managed Memory: handles to this type of memory may not be shared through
any of the mechanisms discussed in this section.
On systems with full CUDA Unified Memory support,
System-Allocated Memory is Inter-Process Communication (IPC) capable.
Once access to System-Allocated Memory has been shared with other processes,
```

### E76c6e5d44e1ea9d25a3292e3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-thread-hierarchy.md#L114-L139

```text
{
cudaLaunchConfig_t config = {0};
// The grid dimension is not affected by cluster launch, and is still enumerated
// using number of blocks.
// The grid dimension should be a multiple of cluster size.
config.gridDim = numBlocks;
config.blockDim = threadsPerBlock;
```

### Edf9df952793566dbe1cf0940

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
24.2.2.4.
Atomic accesses & synchronization primitives
CUDA Unified Memory supports all atomic operations available to host and device threads,
enabling all threads to cooperate by concurrently accessing the same shared memory location.
The CUDA C++ standard library
```

### E26f4250aa57456c8a93978de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

### E3cde33937aaf59d90c01188e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
There are also two additional read-only memory spaces accessible by all threads: the constant and texture memory spaces.
The global, constant, and texture memory spaces are optimized for different memory usages (see Device Memory Accesses).
Texture memory also offers different addressing modes, as well as data filtering, for some specific data formats (see Texture and Surface Memory).
```

### E5f547b764d41ee021d6de85d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
The global, constant, and texture memory spaces are persistent across kernel launches by the same application.
```

### E5ee5e8b68e1ef766abe3ad17

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
Note
As of now, using IPC with Unified Memory can have significant performance implications.
Many applications prefer to manage one GPU per process, but still need to use Unified Memory,
for example for over-subscription, and access it from multiple GPUs.
CUDA IPC (see Interprocess Communication)
```

### E42814340a07b80e201e6e128

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
the same Programming Model applies,
similar to File-backed Unified Memory.
See the following references for more information on various ways of creating
```

### Ef435059a27602151178349e6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
IPC-capable System-Allocated Memory under Linux:
```

### E9ed5c1ac4e7e5ae5f4bb1026

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-thread-hierarchy.md#L114-L139

```text
int main()
{
float *input, *output;
dim3 threadsPerBlock(16, 16);
dim3 numBlocks(N / threadsPerBlock.x, N / threadsPerBlock.y);
// Kernel invocation with runtime cluster size
```

## official-022-2:hybrid_rerank:retrieved

CUDA 13.0.1：能否把一个普通线程块的shared memory当全grid共享空间？

必要要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

```json
null
```

实际输入证据：

### E26f4250aa57456c8a93978de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

### Edb4fe65bec83c651e06dfe24

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
5.3.
Memory Hierarchy
CUDA threads may access data from multiple memory spaces during their execution as illustrated by Figure 6.
Each thread has private local memory.
Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
Thread blocks in a thread block cluster can perform read, write, and atomics operations on each other’s shared memory.
All threads have access to the same global memory.
```

### E94476e2701ba39db8e9f4a47

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L155-L166

```text
```cpp
__shared__ Q_vec q_vecs[THREAD_GROUP_SIZE][NUM_VECS_PER_THREAD];
```
Next, we need to read the global memory data pointed to by `q_ptr`
into shared memory as `q_vecs`.
It is important to note that each
vecs is assigned to a different row.
For example, if the
`THREAD_GROUP_SIZE` is 2, thread 0 will handle the 0th row vecs,
while thread 1 handles the 1st row vecs.
```

### E94db25a2ecb0b60ff0dc81ed

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-thread-hierarchy.md#L62-L66

```text
More precisely, one can specify synchronization points in the kernel by calling the __syncthreads() intrinsic function;
__syncthreads() acts as a barrier at which all threads in the block must wait before any is allowed to proceed.
Shared Memory gives an example of using shared memory.
In addition to __syncthreads(), the Cooperative Groups API provides a rich set of thread-synchronization primitives.
```

### E0de848d132cf0d7db2bb2524

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L126-L145

```text
primary_kernel<<<grid_dim, block_dim, 0, stream>>>();
cudaLaunchKernelEx(&configSecondary, secondary_kernel);
When the secondary kernel is launched using the cudaLaunchAttributeProgrammaticStreamSerialization attribute,
the CUDA driver is safe to launch the secondary kernel early and not wait on the
completion and memory flush of the primary before launching the secondary.
```

### Ec62b71f33327c96106baa4e7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
The following code sample is a straightforward implementation of matrix multiplication that does not take advantage of shared memory.
Each thread reads one row of A and one column of B and computes the corresponding element of C as illustrated in Figure 8.
A is therefore read B.width times from global memory and B is read A.height times.
```

### E3cde33937aaf59d90c01188e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
There are also two additional read-only memory spaces accessible by all threads: the constant and texture memory spaces.
The global, constant, and texture memory spaces are optimized for different memory usages (see Device Memory Accesses).
Texture memory also offers different addressing modes, as well as data filtering, for some specific data formats (see Texture and Surface Memory).
```

### E5f547b764d41ee021d6de85d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
The global, constant, and texture memory spaces are persistent across kernel launches by the same application.
```

### Ef5c702ed2cceacf43421981d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L155-L166

```text
By reading the query data in
```

## official-022-3:oracle:oracle

CUDA 13.0.1：代码中的普通线程块shared memory，其可见范围和生命周期应怎样理解？

必要要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

```json
null
```

实际输入证据：

### E2998a9d5088e49e507e777cd

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#memory-hierarchy

```text
Each thread has private local memory. Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
```

## official-022-3:bm25:retrieved

CUDA 13.0.1：代码中的普通线程块shared memory，其可见范围和生命周期应怎样理解？

必要要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

```json
null
```

实际输入证据：

### E26f4250aa57456c8a93978de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

### E886d8ee4d345e68795a91fc2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
does not support Managed Memory: handles to this type of memory may not be shared through
any of the mechanisms discussed in this section.
On systems with full CUDA Unified Memory support,
System-Allocated Memory is Inter-Process Communication (IPC) capable.
Once access to System-Allocated Memory has been shared with other processes,
```

### Edf9df952793566dbe1cf0940

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
24.2.2.4.
Atomic accesses & synchronization primitives
CUDA Unified Memory supports all atomic operations available to host and device threads,
enabling all threads to cooperate by concurrently accessing the same shared memory location.
The CUDA C++ standard library
```

### Edb4fe65bec83c651e06dfe24

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
5.3.
Memory Hierarchy
CUDA threads may access data from multiple memory spaces during their execution as illustrated by Figure 6.
Each thread has private local memory.
Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
Thread blocks in a thread block cluster can perform read, write, and atomics operations on each other’s shared memory.
All threads have access to the same global memory.
```

### E058aff20cdaceda83a69c4c5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L200-L200

```text
Figure 9 Matrix Multiplication with Shared Memory
```

### Ec62b71f33327c96106baa4e7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
The following code sample is a straightforward implementation of matrix multiplication that does not take advantage of shared memory.
Each thread reads one row of A and one column of B and computes the corresponding element of C as illustrated in Figure 8.
A is therefore read B.width times from global memory and B is read A.height times.
```

### E5ee5e8b68e1ef766abe3ad17

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
Note
As of now, using IPC with Unified Memory can have significant performance implications.
Many applications prefer to manage one GPU per process, but still need to use Unified Memory,
for example for over-subscription, and access it from multiple GPUs.
CUDA IPC (see Interprocess Communication)
```

### E42814340a07b80e201e6e128

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
the same Programming Model applies,
similar to File-backed Unified Memory.
See the following references for more information on various ways of creating
```

### Ef435059a27602151178349e6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
IPC-capable System-Allocated Memory under Linux:
```

### Ec5e671a6a30fd10316381a19

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
provides many heterogeneous synchronization primitives tuned for concurrent use between host and device threads,
including cuda::atomic, cuda::atomic_ref, cuda::barrier, cuda::semaphore, among many others.
On systems without CPU and GPU page tables: hardware coherency vs.
software coherency,
atomic accesses from the device to file-backed host memory are not supported.
```

### E1e6e9b8c1adb15ad22b95aa6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
The following example code is valid on systems with CPU and GPU page tables: hardware coherency vs.
software coherency
```

## official-022-3:dense:retrieved

CUDA 13.0.1：代码中的普通线程块shared memory，其可见范围和生命周期应怎样理解？

必要要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

```json
null
```

实际输入证据：

### E0a73c6fa9de0d1f1e502224d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L335-L337

```text
24.1.2.2. Allocation API for CUDA Managed Memory: cudaMallocManaged()

On systems with CUDA Managed Memory support, unified memory may be allocated using:
```

### E8a4e6d2e2c4f737e04c354d3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L35-L69

```text
Linear memory is typically allocated using cudaMalloc() and freed using cudaFree() and data transfer between host memory and device memory are typically done using cudaMemcpy().
In the vector addition code sample of Kernels, the vectors need to be copied from host memory to device memory:
// Device code
```

### Edb4fe65bec83c651e06dfe24

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
5.3.
Memory Hierarchy
CUDA threads may access data from multiple memory spaces during their execution as illustrated by Figure 6.
Each thread has private local memory.
Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
Thread blocks in a thread block cluster can perform read, write, and atomics operations on each other’s shared memory.
All threads have access to the same global memory.
```

### E181ac7ad650994d7f0c7cd40

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L72-L72

```text
Full CUDA Unified Memory: all memory has full support. This includes System-Allocated and CUDA Managed Memory.
```

### E603944b00ee8332ec2e05581

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L81-L102

```text
cudaFree(d_A);
cudaFree(d_B);
cudaFree(d_C);
// Free host memory
...
}
Linear memory can also be allocated through cudaMallocPitch() and cudaMalloc3D().
```

### E1429d2fa5fca06134f3a1182

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L35-L69

```text
Note
On devices of compute capability 5.3 (Maxwell) and earlier, the CUDA driver creates an uncommitted 40bit virtual address reservation to ensure that memory allocations (pointers) fall into the supported range.
This reservation appears as reserved virtual memory, but does not occupy any physical memory until the program actually allocates memory.
```

### E578028cd0135b3801c788597

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L35-L69

```text
__global__ void VecAdd(float* A, float* B, float* C, int N)
{
int i = blockDim.x * blockIdx.x + threadIdx.x;
if (i < N)
C[i] = A[i] + B[i];
}
```

### E84d2356367c5f3c0e58ebb27

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L35-L69

```text
// Host code
int main()
{
int N = ...;
size_t size = N * sizeof(float);
// Allocate input vectors h_A and h_B in host memory
float* h_A = (float*)malloc(size);
float* h_B = (float*)malloc(size);
float* h_C = (float*)malloc(size);
```

### Ecedcd94bb962d4daca342aaa

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L35-L69

```text
// Initialize input vectors
...
// Allocate vectors in device memory
float* d_A;
cudaMalloc(&d_A, size);
float* d_B;
cudaMalloc(&d_B, size);
float* d_C;
cudaMalloc(&d_C, size);
```

### E3cde33937aaf59d90c01188e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
There are also two additional read-only memory spaces accessible by all threads: the constant and texture memory spaces.
The global, constant, and texture memory spaces are optimized for different memory usages (see Device Memory Accesses).
Texture memory also offers different addressing modes, as well as data filtering, for some specific data formats (see Texture and Surface Memory).
```

### E5f547b764d41ee021d6de85d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
The global, constant, and texture memory spaces are persistent across kernel launches by the same application.
```

## official-022-3:hybrid:retrieved

CUDA 13.0.1：代码中的普通线程块shared memory，其可见范围和生命周期应怎样理解？

必要要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

```json
null
```

实际输入证据：

### Edb4fe65bec83c651e06dfe24

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
5.3.
Memory Hierarchy
CUDA threads may access data from multiple memory spaces during their execution as illustrated by Figure 6.
Each thread has private local memory.
Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
Thread blocks in a thread block cluster can perform read, write, and atomics operations on each other’s shared memory.
All threads have access to the same global memory.
```

### E886d8ee4d345e68795a91fc2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
does not support Managed Memory: handles to this type of memory may not be shared through
any of the mechanisms discussed in this section.
On systems with full CUDA Unified Memory support,
System-Allocated Memory is Inter-Process Communication (IPC) capable.
Once access to System-Allocated Memory has been shared with other processes,
```

### E0a73c6fa9de0d1f1e502224d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L335-L337

```text
24.1.2.2. Allocation API for CUDA Managed Memory: cudaMallocManaged()

On systems with CUDA Managed Memory support, unified memory may be allocated using:
```

### Eb555b6140eca7526e6331d8a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L35-L37

```text
The total amount of shared memory required for a block is equal to the sum of the amount of statically allocated shared memory and the amount of dynamically allocated shared memory.
```

### Ecb74db96bd116ef76697e61f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-thread-hierarchy.md#L141-L143

```text
Thread blocks in a cluster have the ability to read, write, and perform atomics to any address in the distributed shared memory.
Distributed Shared Memory gives an example of performing histograms in distributed shared memory.
```

### E3cde33937aaf59d90c01188e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
There are also two additional read-only memory spaces accessible by all threads: the constant and texture memory spaces.
The global, constant, and texture memory spaces are optimized for different memory usages (see Device Memory Accesses).
Texture memory also offers different addressing modes, as well as data filtering, for some specific data formats (see Texture and Surface Memory).
```

### E5f547b764d41ee021d6de85d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
The global, constant, and texture memory spaces are persistent across kernel launches by the same application.
```

### E5ee5e8b68e1ef766abe3ad17

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
Note
As of now, using IPC with Unified Memory can have significant performance implications.
Many applications prefer to manage one GPU per process, but still need to use Unified Memory,
for example for over-subscription, and access it from multiple GPUs.
CUDA IPC (see Interprocess Communication)
```

### E42814340a07b80e201e6e128

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
the same Programming Model applies,
similar to File-backed Unified Memory.
See the following references for more information on various ways of creating
```

### Ef435059a27602151178349e6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
IPC-capable System-Allocated Memory under Linux:
```

### Ede50619bb283b920ece63c65

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L35-L37

```text
The number of blocks and warps residing on each multiprocessor for a given kernel call depends on the execution configuration of the call (Execution Configuration), the memory resources of the multiprocessor, and the resource requirements of the kernel as described in Hardware Multithreading.
Register and shared memory usage are reported by the compiler when compiling with the --ptxas-options=-v option.
```

## official-022-3:hybrid_rerank:retrieved

CUDA 13.0.1：代码中的普通线程块shared memory，其可见范围和生命周期应怎样理解？

必要要点：local memory属于线程，shared memory可见范围和生命周期属于线程块。

禁止误读：普通shared memory天然对所有grid线程共享。

```json
null
```

实际输入证据：

### Edb4fe65bec83c651e06dfe24

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
5.3.
Memory Hierarchy
CUDA threads may access data from multiple memory spaces during their execution as illustrated by Figure 6.
Each thread has private local memory.
Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
Thread blocks in a thread block cluster can perform read, write, and atomics operations on each other’s shared memory.
All threads have access to the same global memory.
```

### Eb555b6140eca7526e6331d8a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L35-L37

```text
The total amount of shared memory required for a block is equal to the sum of the amount of statically allocated shared memory and the amount of dynamically allocated shared memory.
```

### Ed5b7174e4b1fb72a7ce2f862

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
// Get sub-matrix Asub of A
Matrix Asub = GetSubMatrix(A, blockRow, m);
// Get sub-matrix Bsub of B
Matrix Bsub = GetSubMatrix(B, m, blockCol);
// Shared memory used to store Asub and Bsub respectively
__shared__ float As[BLOCK_SIZE][BLOCK_SIZE];
__shared__ float Bs[BLOCK_SIZE][BLOCK_SIZE];
// Load Asub and Bsub from device memory to shared memory
// Each thread loads one element of each sub-matrix
```

### E26f4250aa57456c8a93978de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

### E94db25a2ecb0b60ff0dc81ed

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-thread-hierarchy.md#L62-L66

```text
More precisely, one can specify synchronization points in the kernel by calling the __syncthreads() intrinsic function;
__syncthreads() acts as a barrier at which all threads in the block must wait before any is allowed to proceed.
Shared Memory gives an example of using shared memory.
In addition to __syncthreads(), the Cooperative Groups API provides a rich set of thread-synchronization primitives.
```

### E3cde33937aaf59d90c01188e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
There are also two additional read-only memory spaces accessible by all threads: the constant and texture memory spaces.
The global, constant, and texture memory spaces are optimized for different memory usages (see Device Memory Accesses).
Texture memory also offers different addressing modes, as well as data filtering, for some specific data formats (see Texture and Surface Memory).
```

### E5f547b764d41ee021d6de85d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
The global, constant, and texture memory spaces are persistent across kernel launches by the same application.
```

### Ede50619bb283b920ece63c65

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L35-L37

```text
The number of blocks and warps residing on each multiprocessor for a given kernel call depends on the execution configuration of the call (Execution Configuration), the memory resources of the multiprocessor, and the resource requirements of the kernel as described in Hardware Multithreading.
Register and shared memory usage are reported by the compiler when compiling with the --ptxas-options=-v option.
```

### Efc3c51f8f613f4d080c9f09c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
// required to compute Csub
// Multiply each pair of sub-matrices together
// and accumulate the results
```

## official-022-4:oracle:oracle

CUDA 13.0.1：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在memory-hierarchy场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
{
  "conversation_id": "05419f7c-5410-4bd5-b39b-14a5355e586f",
  "answer": "资料库中没有找到可以支持这个问题的证据。请换个问法或先导入相关文档。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "CUDA 13.0.1：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在memory-hierarchy场景下精确的P95延迟毫秒值吗？",
      "hits": 0,
      "evidence": 0
    }
  ]
}
```

实际输入证据：

## official-022-4:bm25:retrieved

CUDA 13.0.1：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在memory-hierarchy场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### E6de2556ed5d7cae93203d1dc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L9-L9

```text
Figure 6 Memory Hierarchy
```

### Edb4fe65bec83c651e06dfe24

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
5.3.
Memory Hierarchy
CUDA threads may access data from multiple memory spaces during their execution as illustrated by Figure 6.
Each thread has private local memory.
Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
Thread blocks in a thread block cluster can perform read, write, and atomics operations on each other’s shared memory.
All threads have access to the same global memory.
```

### E26f4250aa57456c8a93978de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

### E5f547b764d41ee021d6de85d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
The global, constant, and texture memory spaces are persistent across kernel launches by the same application.
```

### E743f50645474beacb25db53c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-thread-hierarchy.md#L68-L68

```text
For efficient cooperation, shared memory is expected to be a low-latency memory near each processor core (much like an L1 cache) and __syncthreads() is expected to be lightweight.
```

### E3cde33937aaf59d90c01188e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
There are also two additional read-only memory spaces accessible by all threads: the constant and texture memory spaces.
The global, constant, and texture memory spaces are optimized for different memory usages (see Device Memory Accesses).
Texture memory also offers different addressing modes, as well as data filtering, for some specific data formats (see Texture and Surface Memory).
```

### Ec62b71f33327c96106baa4e7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
The following code sample is a straightforward implementation of matrix multiplication that does not take advantage of shared memory.
Each thread reads one row of A and one column of B and computes the corresponding element of C as illustrated in Figure 8.
A is therefore read B.width times from global memory and B is read A.height times.
```

## official-022-4:dense:retrieved

CUDA 13.0.1：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在memory-hierarchy场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### E10d4c1a966d1b318e13ff8ba

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-conserving_memory.md#L51-L56

```text
## Reduce CUDA Graphs

By default, we optimize model inference using CUDA graphs which take up extra memory in the GPU.

!!! warning
    CUDA graph capture takes up more memory in V1 than in V0.
```

### Eccc3c69aae8e6b44c211083f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L73-L74

```text
- When the model is too large to fit on a single GPU
- When you need to reduce memory pressure per GPU to allow more KV cache space for higher throughput
```

### E885ebf52beeb93b690a2dc22

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
cudaMemRangeAttributePreferredLocation:
the result returned will be a GPU device id or cudaCpuDeviceId if the entire
memory range has the corresponding processor as preferred location,
```

### E2a987935049ba4a72d481f15

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-sleep_mode.md#L1-L3

```text
# Sleep Mode

vLLM's Sleep Mode allows you to temporarily release most GPU memory used by a model, including model weights and KV cache, without stopping the server or unloading the Docker container. This is especially useful for RLHF, training, or cost-saving scenarios where GPU resources need to be freed between inference workloads.
```

### Ec8badce76b9e3fd7d3fbe392

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-page-locked-host-memory.md#L53-L61

```text
Also note that CUDA runtime requires that 1-byte, 2-byte, 4-byte, 8-byte, and 16-byte naturally aligned
loads and stores to host memory initiated from the device are preserved as single accesses
from the point of view of the host and other devices.
On some platforms, atomics to memory may be broken by the hardware into separate
```

### E6389c5d5cad82e7e87c6bd6c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
otherwise cudaInvalidDeviceId will be returned.
An application can use this query API to make decision about staging data through
CPU or GPU depending on the preferred location attribute of the managed pointer.
Note that the actual location of the memory range at the time
of the query may be different from the preferred location.
cudaMemRangeAttributeAccessedBy:
```

### E8527e24f7def8dbf37934928

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
will return the list of devices that have that advise set for that memory range.
cudaMemRangeAttributeLastPrefetchLocation:
will return the last location to which the memory range was prefetched
explicitly using cudaMemPrefetchAsync.
Note that this simply returns the last location that the application requested to prefetch the memory range to.
```

### E36e2d92db8de1d6211448d94

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
It gives no indication as to whether the prefetch operation to that location has completed or even begun.
cudaMemRangeAttributePreferredLocationType:
```

### E6cdf3e87eb776614e116411e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-page-locked-host-memory.md#L53-L61

```text
load and store operations.
These component load and store operations have the same requirements on preservation of naturally aligned accesses.
```

### E0bf105ee520f57f38bb42e8f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-page-locked-host-memory.md#L53-L61

```text
The CUDA runtime does not support a PCI Express bus topology where a PCI Express bridge splits
8-byte naturally aligned operations and NVIDIA is not aware of any topology that splits
16-byte naturally aligned operations.
```

## official-022-4:hybrid:retrieved

CUDA 13.0.1：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在memory-hierarchy场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### E126a10689ab080a486fe6685

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L78-L80

```text
Unified Memory on devices with full CUDA Unified Memory support

Only CUDA Managed Memory has full support.
```

### E10d4c1a966d1b318e13ff8ba

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-conserving_memory.md#L51-L56

```text
## Reduce CUDA Graphs

By default, we optimize model inference using CUDA graphs which take up extra memory in the GPU.

!!! warning
    CUDA graph capture takes up more memory in V1 than in V0.
```

### E743f50645474beacb25db53c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-thread-hierarchy.md#L68-L68

```text
For efficient cooperation, shared memory is expected to be a low-latency memory near each processor core (much like an L1 cache) and __syncthreads() is expected to be lightweight.
```

### E3b01b0318ab093fe54e56e1c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L102-L102

```text
CUDA for Tegra Memory Management
```

### Eda86ef0d3db21dcb5942cc0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L747-L747

```text
24.2. Unified memory on devices with full CUDA Unified Memory support
```

## official-022-4:hybrid_rerank:retrieved

CUDA 13.0.1：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在memory-hierarchy场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### E885ebf52beeb93b690a2dc22

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
cudaMemRangeAttributePreferredLocation:
the result returned will be a GPU device id or cudaCpuDeviceId if the entire
memory range has the corresponding processor as preferred location,
```

### Ec9120c82efd9aae0d03c9801

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L132-L149

```text
there will be a minor increase in memory consumption and may cause OOM if you can barely fit the model already.
You can enable batch-level DP by setting `mm_encoder_tp_mode="data"`, for example:
```

### Ec5335ba9c597a43e6a9c547e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L454-L479

```text
char const* kind(cudaPointerAttributes a, bool pma, bool cma) {
switch(a.type) {
case cudaMemoryTypeHost: return pma?
"Unified: CUDA Host or Registered Memory" :
"Not Unified: CUDA Host or Registered Memory";
case cudaMemoryTypeDevice: return "Not Unified: CUDA Device Memory";
case cudaMemoryTypeManaged: return cma?
"Unified: CUDA Managed Memory" : "Not Unified: CUDA Managed Memory";
```

### Eb99b65b612b7dd3a604e3b1e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1102-L1125

```text
// pages populated in GPU memory
cudaDeviceSynchronize();
for(int i = 0;
i < 1000;
i++)
printf("%d: A+B = %d\n", i, ret[i]);
```

### E3b01b0318ab093fe54e56e1c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L102-L102

```text
CUDA for Tegra Memory Management
```

### E6389c5d5cad82e7e87c6bd6c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
otherwise cudaInvalidDeviceId will be returned.
An application can use this query API to make decision about staging data through
CPU or GPU depending on the preferred location attribute of the managed pointer.
Note that the actual location of the memory range at the time
of the query may be different from the preferred location.
cudaMemRangeAttributeAccessedBy:
```

### E8527e24f7def8dbf37934928

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
will return the list of devices that have that advise set for that memory range.
cudaMemRangeAttributeLastPrefetchLocation:
will return the last location to which the memory range was prefetched
explicitly using cudaMemPrefetchAsync.
Note that this simply returns the last location that the application requested to prefetch the memory range to.
```

### E36e2d92db8de1d6211448d94

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
It gives no indication as to whether the prefetch operation to that location has completed or even begun.
cudaMemRangeAttributePreferredLocationType:
```

### E72131fb0344f92e172ea9d6c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L132-L149

```text
This has been shown to improve the throughput by around 10% for
`tensor_parallel_size=8`.
For vision encoders that use hardware-unoptimized Conv3D operations,
batch-level DP can provide another 40% increase to throughput compared to regular TP.
Nevertheless, since the weights of the multi-modal encoder are replicated across each TP rank,
```

### Ee72c1289e96a14e54dc9e690

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L132-L149

```text
overhead because of all-reduce being performed after every layer.
Given this, it may be advantageous to instead shard the batched input data using TP, essentially
performing batch-level DP.
```

## official-024-1:oracle:oracle

CUDA 13.0.1：矩阵乘示例里shared memory作为缓存主要减少哪种访问？

必要要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

```json
null
```

实际输入证据：

### Ec1869158904bd6ac2f36d793

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#shared-memory

```text
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

## official-024-1:bm25:retrieved

CUDA 13.0.1：矩阵乘示例里shared memory作为缓存主要减少哪种访问？

必要要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

```json
null
```

实际输入证据：

### E26f4250aa57456c8a93978de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

### E886d8ee4d345e68795a91fc2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
does not support Managed Memory: handles to this type of memory may not be shared through
any of the mechanisms discussed in this section.
On systems with full CUDA Unified Memory support,
System-Allocated Memory is Inter-Process Communication (IPC) capable.
Once access to System-Allocated Memory has been shared with other processes,
```

### Edf9df952793566dbe1cf0940

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
24.2.2.4.
Atomic accesses & synchronization primitives
CUDA Unified Memory supports all atomic operations available to host and device threads,
enabling all threads to cooperate by concurrently accessing the same shared memory location.
The CUDA C++ standard library
```

### Edb4fe65bec83c651e06dfe24

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
5.3.
Memory Hierarchy
CUDA threads may access data from multiple memory spaces during their execution as illustrated by Figure 6.
Each thread has private local memory.
Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
Thread blocks in a thread block cluster can perform read, write, and atomics operations on each other’s shared memory.
All threads have access to the same global memory.
```

### E058aff20cdaceda83a69c4c5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L200-L200

```text
Figure 9 Matrix Multiplication with Shared Memory
```

### Ec62b71f33327c96106baa4e7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
The following code sample is a straightforward implementation of matrix multiplication that does not take advantage of shared memory.
Each thread reads one row of A and one column of B and computes the corresponding element of C as illustrated in Figure 8.
A is therefore read B.width times from global memory and B is read A.height times.
```

### E5ee5e8b68e1ef766abe3ad17

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
Note
As of now, using IPC with Unified Memory can have significant performance implications.
Many applications prefer to manage one GPU per process, but still need to use Unified Memory,
for example for over-subscription, and access it from multiple GPUs.
CUDA IPC (see Interprocess Communication)
```

### E42814340a07b80e201e6e128

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
the same Programming Model applies,
similar to File-backed Unified Memory.
See the following references for more information on various ways of creating
```

### Ef435059a27602151178349e6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
IPC-capable System-Allocated Memory under Linux:
```

### Ec5e671a6a30fd10316381a19

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
provides many heterogeneous synchronization primitives tuned for concurrent use between host and device threads,
including cuda::atomic, cuda::atomic_ref, cuda::barrier, cuda::semaphore, among many others.
On systems without CPU and GPU page tables: hardware coherency vs.
software coherency,
atomic accesses from the device to file-backed host memory are not supported.
```

### E1e6e9b8c1adb15ad22b95aa6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
The following example code is valid on systems with CPU and GPU page tables: hardware coherency vs.
software coherency
```

## official-024-1:dense:retrieved

CUDA 13.0.1：矩阵乘示例里shared memory作为缓存主要减少哪种访问？

必要要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

```json
null
```

实际输入证据：

### E8a4e6d2e2c4f737e04c354d3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L35-L69

```text
Linear memory is typically allocated using cudaMalloc() and freed using cudaFree() and data transfer between host memory and device memory are typically done using cudaMemcpy().
In the vector addition code sample of Kernels, the vectors need to be copied from host memory to device memory:
// Device code
```

### E603944b00ee8332ec2e05581

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L81-L102

```text
cudaFree(d_A);
cudaFree(d_B);
cudaFree(d_C);
// Free host memory
...
}
Linear memory can also be allocated through cudaMallocPitch() and cudaMalloc3D().
```

### E743f50645474beacb25db53c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-thread-hierarchy.md#L68-L68

```text
For efficient cooperation, shared memory is expected to be a low-latency memory near each processor core (much like an L1 cache) and __syncthreads() is expected to be lightweight.
```

### E8c3de479cf7c745dd6d0518e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L339-L350

```text
__host__ cudaError_t cudaMallocManaged(void **devPtr, size_t size);
This API is syntactically identical to cudaMalloc(): it allocates size bytes of managed memory and
sets devPtr to refer to the allocation.
CUDA Managed Memory is also deallocated with cudaFree().
On systems with full CUDA Managed Memory support, managed memory allocations
may be accessed concurrently by all CPUs and GPUs in the system.
```

### E0a73c6fa9de0d1f1e502224d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L335-L337

```text
24.1.2.2. Allocation API for CUDA Managed Memory: cudaMallocManaged()

On systems with CUDA Managed Memory support, unified memory may be allocated using:
```

### E1429d2fa5fca06134f3a1182

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L35-L69

```text
Note
On devices of compute capability 5.3 (Maxwell) and earlier, the CUDA driver creates an uncommitted 40bit virtual address reservation to ensure that memory allocations (pointers) fall into the supported range.
This reservation appears as reserved virtual memory, but does not occupy any physical memory until the program actually allocates memory.
```

### E578028cd0135b3801c788597

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L35-L69

```text
__global__ void VecAdd(float* A, float* B, float* C, int N)
{
int i = blockDim.x * blockIdx.x + threadIdx.x;
if (i < N)
C[i] = A[i] + B[i];
}
```

### E84d2356367c5f3c0e58ebb27

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L35-L69

```text
// Host code
int main()
{
int N = ...;
size_t size = N * sizeof(float);
// Allocate input vectors h_A and h_B in host memory
float* h_A = (float*)malloc(size);
float* h_B = (float*)malloc(size);
float* h_C = (float*)malloc(size);
```

### Ecedcd94bb962d4daca342aaa

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L35-L69

```text
// Initialize input vectors
...
// Allocate vectors in device memory
float* d_A;
cudaMalloc(&d_A, size);
float* d_B;
cudaMalloc(&d_B, size);
float* d_C;
cudaMalloc(&d_C, size);
```

### E66c691e9b38da97e514477fb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L81-L102

```text
// Copy result from device memory to host memory
// h_C contains the result in host memory
cudaMemcpy(h_C, d_C, size, cudaMemcpyDeviceToHost);
// Free device memory
```

### E35cda14a1e5af2fe8958dc58

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L81-L102

```text
The returned pitch (or stride) must be used to access array elements.
```

## official-024-1:hybrid:retrieved

CUDA 13.0.1：矩阵乘示例里shared memory作为缓存主要减少哪种访问？

必要要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

```json
null
```

实际输入证据：

### E886d8ee4d345e68795a91fc2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
does not support Managed Memory: handles to this type of memory may not be shared through
any of the mechanisms discussed in this section.
On systems with full CUDA Unified Memory support,
System-Allocated Memory is Inter-Process Communication (IPC) capable.
Once access to System-Allocated Memory has been shared with other processes,
```

### E0a73c6fa9de0d1f1e502224d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L335-L337

```text
24.1.2.2. Allocation API for CUDA Managed Memory: cudaMallocManaged()

On systems with CUDA Managed Memory support, unified memory may be allocated using:
```

### Eb003b386333ecd750d765cb1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
// Read C from device memory
cudaMemcpy(C.elements, d_C.elements, size,
cudaMemcpyDeviceToHost);
// Free device memory
```

### E181ac7ad650994d7f0c7cd40

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L72-L72

```text
Full CUDA Unified Memory: all memory has full support. This includes System-Allocated and CUDA Managed Memory.
```

### Ea1e8b857028387b3ecaf2d04

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L20-L54

```text
// Read C from device memory
cudaMemcpy(C.elements, d_C.elements, size,
cudaMemcpyDeviceToHost);
```

### E5ee5e8b68e1ef766abe3ad17

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
Note
As of now, using IPC with Unified Memory can have significant performance implications.
Many applications prefer to manage one GPU per process, but still need to use Unified Memory,
for example for over-subscription, and access it from multiple GPUs.
CUDA IPC (see Interprocess Communication)
```

### E42814340a07b80e201e6e128

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
the same Programming Model applies,
similar to File-backed Unified Memory.
See the following references for more information on various ways of creating
```

### Ef435059a27602151178349e6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
IPC-capable System-Allocated Memory under Linux:
```

### E8b1ca3d9aca9893108397dfb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
// Invoke kernel
dim3 dimBlock(BLOCK_SIZE, BLOCK_SIZE);
dim3 dimGrid(B.width / dimBlock.x, A.height / dimBlock.y);
MatMulKernel<<<dimGrid, dimBlock>>>(d_A, d_B, d_C);
```

### Eeedf06e379969bee14ee8915

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
cudaFree(d_A.elements);
cudaFree(d_B.elements);
cudaFree(d_C.elements);
}
// Matrix multiplication kernel called by MatMul()
__global__ void MatMulKernel(Matrix A, Matrix B, Matrix C)
```

### E40fbf8011f402b16085eb7fe

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
Matrix d_B;
d_B.width = d_B.stride = B.width;
d_B.height = B.height;
size = B.width * B.height * sizeof(float);
cudaMalloc(&d_B.elements, size);
cudaMemcpy(d_B.elements, B.elements, size,
cudaMemcpyHostToDevice);
// Allocate C in device memory
Matrix d_C;
d_C.width = d_C.stride = C.width;
d_C.height = C.height;
size = C.width * C.height * sizeof(float);
cudaMalloc(&d_C.elements, size);
```

### E8ca8102ef19a84fe429c7d91

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
{
// Block row and column
int blockRow = blockIdx.y;
int blockCol = blockIdx.x;
// Each thread block computes one sub-matrix Csub of C
Matrix Csub = GetSubMatrix(C, blockRow, blockCol);
```

## official-024-1:hybrid_rerank:retrieved

CUDA 13.0.1：矩阵乘示例里shared memory作为缓存主要减少哪种访问？

必要要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

```json
null
```

实际输入证据：

### E26f4250aa57456c8a93978de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

### E058aff20cdaceda83a69c4c5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L200-L200

```text
Figure 9 Matrix Multiplication with Shared Memory
```

### Ed5b7174e4b1fb72a7ce2f862

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
// Get sub-matrix Asub of A
Matrix Asub = GetSubMatrix(A, blockRow, m);
// Get sub-matrix Bsub of B
Matrix Bsub = GetSubMatrix(B, m, blockCol);
// Shared memory used to store Asub and Bsub respectively
__shared__ float As[BLOCK_SIZE][BLOCK_SIZE];
__shared__ float Bs[BLOCK_SIZE][BLOCK_SIZE];
// Load Asub and Bsub from device memory to shared memory
// Each thread loads one element of each sub-matrix
```

### Ef17178a96c4ba4390bd108ce

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L76-L76

```text
Figure 8 Matrix Multiplication without Shared Memory
```

### E743f50645474beacb25db53c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-thread-hierarchy.md#L68-L68

```text
For efficient cooperation, shared memory is expected to be a low-latency memory near each processor core (much like an L1 cache) and __syncthreads() is expected to be lightweight.
```

### Ec62b71f33327c96106baa4e7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
The following code sample is a straightforward implementation of matrix multiplication that does not take advantage of shared memory.
Each thread reads one row of A and one column of B and computes the corresponding element of C as illustrated in Figure 8.
A is therefore read B.width times from global memory and B is read A.height times.
```

### Efc3c51f8f613f4d080c9f09c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
// required to compute Csub
// Multiply each pair of sub-matrices together
// and accumulate the results
for (int m = 0;
m < (A.width / BLOCK_SIZE);
++m) {
```

### E14ff9c392c7b724999a0628d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
As[row][col] = GetElement(Asub, row, col);
Bs[row][col] = GetElement(Bsub, row, col);
// Synchronize to make sure the sub-matrices are loaded
```

### Ec33e4b3787066ac0842880cc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
// Thread row and column within Csub
int row = threadIdx.y;
int col = threadIdx.x;
// Loop over all the sub-matrices of A and B that are
```

### Eae2611959395f1f39148cb16

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
// before starting the computation
__syncthreads();
// Multiply Asub and Bsub together
for (int e = 0;
e < BLOCK_SIZE;
++e)
Cvalue += As[row][e] * Bs[e][col];
```

### E8ca8102ef19a84fe429c7d91

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
{
// Block row and column
int blockRow = blockIdx.y;
int blockCol = blockIdx.x;
// Each thread block computes one sub-matrix Csub of C
Matrix Csub = GetSubMatrix(C, blockRow, blockCol);
// Each thread computes one element of Csub
// by accumulating results into Cvalue
float Cvalue = 0;
```

## official-024-2:oracle:oracle

CUDA 13.0.1：shared memory优化是否意味着矩阵乘法运算不再执行？

必要要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

```json
null
```

实际输入证据：

### Ec1869158904bd6ac2f36d793

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#shared-memory

```text
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

## official-024-2:bm25:retrieved

CUDA 13.0.1：shared memory优化是否意味着矩阵乘法运算不再执行？

必要要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

```json
null
```

实际输入证据：

### E26f4250aa57456c8a93978de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

### E886d8ee4d345e68795a91fc2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
does not support Managed Memory: handles to this type of memory may not be shared through
any of the mechanisms discussed in this section.
On systems with full CUDA Unified Memory support,
System-Allocated Memory is Inter-Process Communication (IPC) capable.
Once access to System-Allocated Memory has been shared with other processes,
```

### Edf9df952793566dbe1cf0940

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
24.2.2.4.
Atomic accesses & synchronization primitives
CUDA Unified Memory supports all atomic operations available to host and device threads,
enabling all threads to cooperate by concurrently accessing the same shared memory location.
The CUDA C++ standard library
```

### Edb4fe65bec83c651e06dfe24

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
5.3.
Memory Hierarchy
CUDA threads may access data from multiple memory spaces during their execution as illustrated by Figure 6.
Each thread has private local memory.
Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
Thread blocks in a thread block cluster can perform read, write, and atomics operations on each other’s shared memory.
All threads have access to the same global memory.
```

### E058aff20cdaceda83a69c4c5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L200-L200

```text
Figure 9 Matrix Multiplication with Shared Memory
```

### Ec62b71f33327c96106baa4e7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
The following code sample is a straightforward implementation of matrix multiplication that does not take advantage of shared memory.
Each thread reads one row of A and one column of B and computes the corresponding element of C as illustrated in Figure 8.
A is therefore read B.width times from global memory and B is read A.height times.
```

### E5ee5e8b68e1ef766abe3ad17

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
Note
As of now, using IPC with Unified Memory can have significant performance implications.
Many applications prefer to manage one GPU per process, but still need to use Unified Memory,
for example for over-subscription, and access it from multiple GPUs.
CUDA IPC (see Interprocess Communication)
```

### E42814340a07b80e201e6e128

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
the same Programming Model applies,
similar to File-backed Unified Memory.
See the following references for more information on various ways of creating
```

### Ef435059a27602151178349e6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
IPC-capable System-Allocated Memory under Linux:
```

### Ec5e671a6a30fd10316381a19

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
provides many heterogeneous synchronization primitives tuned for concurrent use between host and device threads,
including cuda::atomic, cuda::atomic_ref, cuda::barrier, cuda::semaphore, among many others.
On systems without CPU and GPU page tables: hardware coherency vs.
software coherency,
atomic accesses from the device to file-backed host memory are not supported.
```

### E1e6e9b8c1adb15ad22b95aa6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
The following example code is valid on systems with CPU and GPU page tables: hardware coherency vs.
software coherency
```

## official-024-2:dense:retrieved

CUDA 13.0.1：shared memory优化是否意味着矩阵乘法运算不再执行？

必要要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

```json
null
```

实际输入证据：

### E8a4e6d2e2c4f737e04c354d3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L35-L69

```text
Linear memory is typically allocated using cudaMalloc() and freed using cudaFree() and data transfer between host memory and device memory are typically done using cudaMemcpy().
In the vector addition code sample of Kernels, the vectors need to be copied from host memory to device memory:
// Device code
```

### E885ebf52beeb93b690a2dc22

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
cudaMemRangeAttributePreferredLocation:
the result returned will be a GPU device id or cudaCpuDeviceId if the entire
memory range has the corresponding processor as preferred location,
```

### E181ac7ad650994d7f0c7cd40

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L72-L72

```text
Full CUDA Unified Memory: all memory has full support. This includes System-Allocated and CUDA Managed Memory.
```

### E40ee535161aeb7c019a0247e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L39-L56

```text
Total system memory usage may be reduced by avoiding duplicating memory on both CPUs and GPUs.
Functionality: It enables GPU programs to work on data that exceeds the GPU memory’s capacity.
With CUDA Unified Memory, data movement still takes place, and hints may improve performance.
These hints are not required for correctness or functionality, that is, programmers may focus on parallelizing
```

### E3ca4e8b5f33ffaaddf0826f7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L294-L294

```text
Managed Memory: data allocation changed to use cudaMallocManaged(), which returns a pointer valid from both host and device code.
```

### E1429d2fa5fca06134f3a1182

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L35-L69

```text
Note
On devices of compute capability 5.3 (Maxwell) and earlier, the CUDA driver creates an uncommitted 40bit virtual address reservation to ensure that memory allocations (pointers) fall into the supported range.
This reservation appears as reserved virtual memory, but does not occupy any physical memory until the program actually allocates memory.
```

### E578028cd0135b3801c788597

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L35-L69

```text
__global__ void VecAdd(float* A, float* B, float* C, int N)
{
int i = blockDim.x * blockIdx.x + threadIdx.x;
if (i < N)
C[i] = A[i] + B[i];
}
```

### E84d2356367c5f3c0e58ebb27

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L35-L69

```text
// Host code
int main()
{
int N = ...;
size_t size = N * sizeof(float);
// Allocate input vectors h_A and h_B in host memory
float* h_A = (float*)malloc(size);
float* h_B = (float*)malloc(size);
float* h_C = (float*)malloc(size);
```

### Ecedcd94bb962d4daca342aaa

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L35-L69

```text
// Initialize input vectors
...
// Allocate vectors in device memory
float* d_A;
cudaMalloc(&d_A, size);
float* d_B;
cudaMalloc(&d_B, size);
float* d_C;
cudaMalloc(&d_C, size);
```

### E6389c5d5cad82e7e87c6bd6c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
otherwise cudaInvalidDeviceId will be returned.
An application can use this query API to make decision about staging data through
CPU or GPU depending on the preferred location attribute of the managed pointer.
Note that the actual location of the memory range at the time
of the query may be different from the preferred location.
cudaMemRangeAttributeAccessedBy:
```

### E7f511bc019505c0801404a20

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L39-L56

```text
System-Allocated Memory: memory allocated on the host with system APIs:
```

## official-024-2:hybrid:retrieved

CUDA 13.0.1：shared memory优化是否意味着矩阵乘法运算不再执行？

必要要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

```json
null
```

实际输入证据：

### E886d8ee4d345e68795a91fc2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
does not support Managed Memory: handles to this type of memory may not be shared through
any of the mechanisms discussed in this section.
On systems with full CUDA Unified Memory support,
System-Allocated Memory is Inter-Process Communication (IPC) capable.
Once access to System-Allocated Memory has been shared with other processes,
```

### E181ac7ad650994d7f0c7cd40

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L72-L72

```text
Full CUDA Unified Memory: all memory has full support. This includes System-Allocated and CUDA Managed Memory.
```

### E0a73c6fa9de0d1f1e502224d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L335-L337

```text
24.1.2.2. Allocation API for CUDA Managed Memory: cudaMallocManaged()

On systems with CUDA Managed Memory support, unified memory may be allocated using:
```

### E3b01b0318ab093fe54e56e1c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L102-L102

```text
CUDA for Tegra Memory Management
```

### E8b7ebdb27cf3dd43e3f41148

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L104-L123

```text
concurrentManagedAccess: This property is set to 1 on systems with full CUDA Managed Memory support.
When this property is set to 0, there is only partial support for Unified Memory in CUDA Managed Memory.
For Tegra support of Unified Memory, see
CUDA for Tegra Memory Management.
A program may query the level of GPU support for CUDA Unified Memory, by querying the attributes in
Table 31 using  cudaGetDeviceProperties().
```

### E5ee5e8b68e1ef766abe3ad17

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
Note
As of now, using IPC with Unified Memory can have significant performance implications.
Many applications prefer to manage one GPU per process, but still need to use Unified Memory,
for example for over-subscription, and access it from multiple GPUs.
CUDA IPC (see Interprocess Communication)
```

### E42814340a07b80e201e6e128

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
the same Programming Model applies,
similar to File-backed Unified Memory.
See the following references for more information on various ways of creating
```

### Ef435059a27602151178349e6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
IPC-capable System-Allocated Memory under Linux:
```

### E65e628476282c93a5e23d8ed

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L104-L123

```text
all threads may access System-Allocated Memory and CUDA Managed Memory.
These systems include NVIDIA Grace Hopper, IBM Power9 + Volta, and modern Linux systems with HMM enabled (see next bullet), among others.
Linux HMM requires Linux kernel version 6.1.24+, 6.2.11+ or 6.3+,
devices with compute capability 7.5 or higher and
a CUDA driver version 535+ installed with
Open Kernel Modules.
```

### Edaa9604125c42b15c4514a36

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L104-L123

```text
The behavior of an application that attempts to use Unified Memory on a system that does not support it is undefined.
The following properties enable CUDA applications to check the level of system support for Unified Memory, and
to be portable between systems with different levels of support:
pageableMemoryAccess: This property is set to 1 on systems with CUDA Unified Memory support where
```

## official-024-2:hybrid_rerank:retrieved

CUDA 13.0.1：shared memory优化是否意味着矩阵乘法运算不再执行？

必要要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

```json
null
```

实际输入证据：

### Ef17178a96c4ba4390bd108ce

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L76-L76

```text
Figure 8 Matrix Multiplication without Shared Memory
```

### E26f4250aa57456c8a93978de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

### E058aff20cdaceda83a69c4c5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L200-L200

```text
Figure 9 Matrix Multiplication with Shared Memory
```

### E40ee535161aeb7c019a0247e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L39-L56

```text
Total system memory usage may be reduced by avoiding duplicating memory on both CPUs and GPUs.
Functionality: It enables GPU programs to work on data that exceeds the GPU memory’s capacity.
With CUDA Unified Memory, data movement still takes place, and hints may improve performance.
These hints are not required for correctness or functionality, that is, programmers may focus on parallelizing
```

### Eb555b6140eca7526e6331d8a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L35-L37

```text
The total amount of shared memory required for a block is equal to the sum of the amount of statically allocated shared memory and the amount of dynamically allocated shared memory.
```

### Ec62b71f33327c96106baa4e7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
The following code sample is a straightforward implementation of matrix multiplication that does not take advantage of shared memory.
Each thread reads one row of A and one column of B and computes the corresponding element of C as illustrated in Figure 8.
A is therefore read B.width times from global memory and B is read A.height times.
```

### E09331132a5468f7ea5b35227

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L39-L56

```text
their applications across GPUs and CPUs first, and worry about data-movement later in the development cycle as a performance optimization.
Note that the physical location of data is invisible to a program and may be changed at any time,
but accesses to the data’s virtual address will remain valid and coherent from any processor regardless of locality.
There are two main ways to obtain CUDA Unified Memory:
```

### E7f511bc019505c0801404a20

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L39-L56

```text
System-Allocated Memory: memory allocated on the host with system APIs:
stack variables, global-/file-scope variables, malloc() / mmap()
(see System-Allocated Memory: in-depth examples for in-depth examples), thread locals, etc.
CUDA APIs that explicitly allocate Unified Memory: memory allocated with, for example, cudaMallocManaged(),
are available on more systems and may perform better than System-Allocated Memory.
```

### Ede50619bb283b920ece63c65

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L35-L37

```text
The number of blocks and warps residing on each multiprocessor for a given kernel call depends on the execution configuration of the call (Execution Configuration), the memory resources of the multiprocessor, and the resource requirements of the kernel as described in Hardware Multithreading.
Register and shared memory usage are reported by the compiler when compiling with the --ptxas-options=-v option.
```

## official-024-3:oracle:oracle

CUDA 13.0.1：__shared__缓冲区为何可以作为减少global访问的暂存空间？

必要要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

```json
null
```

实际输入证据：

### Ec1869158904bd6ac2f36d793

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#shared-memory

```text
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

## official-024-3:bm25:retrieved

CUDA 13.0.1：__shared__缓冲区为何可以作为减少global访问的暂存空间？

必要要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

```json
null
```

实际输入证据：

### E26f4250aa57456c8a93978de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

### Ed5b7174e4b1fb72a7ce2f862

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
// Get sub-matrix Asub of A
Matrix Asub = GetSubMatrix(A, blockRow, m);
// Get sub-matrix Bsub of B
Matrix Bsub = GetSubMatrix(B, m, blockCol);
// Shared memory used to store Asub and Bsub respectively
__shared__ float As[BLOCK_SIZE][BLOCK_SIZE];
__shared__ float Bs[BLOCK_SIZE][BLOCK_SIZE];
// Load Asub and Bsub from device memory to shared memory
// Each thread loads one element of each sub-matrix
```

### E94476e2701ba39db8e9f4a47

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-paged_attention.md#L155-L166

```text
```cpp
__shared__ Q_vec q_vecs[THREAD_GROUP_SIZE][NUM_VECS_PER_THREAD];
```
Next, we need to read the global memory data pointed to by `q_ptr`
into shared memory as `q_vecs`.
It is important to note that each
vecs is assigned to a different row.
For example, if the
`THREAD_GROUP_SIZE` is 2, thread 0 will handle the 0th row vecs,
while thread 1 handles the 1st row vecs.
```

### Ef2581112ae6045dac45bddc4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L380-L390

```text
24.1.2.3.
Global-Scope Managed Variables Using __managed__
CUDA __managed__ variables behave as if they were allocated via cudaMallocManaged()
(see Allocation API for CUDA Managed Memory: cudaMallocManaged()).
They simplify programs with global variables, making it particularly easy to exchange data between host and device
without manual allocations or copying.
On systems with full CUDA Unified Memory support,
```

### Ef286f489cb64da93a11a5f26

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L409-L438

```text
Managed
__global__ void write_value(int* ptr, int v) {
*ptr = v;
}
// Requires CUDA Managed Memory support
__managed__ int value;
int main() {
```

### Ec62b71f33327c96106baa4e7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
The following code sample is a straightforward implementation of matrix multiplication that does not take advantage of shared memory.
Each thread reads one row of A and one column of B and computes the corresponding element of C as illustrated in Figure 8.
A is therefore read B.width times from global memory and B is read A.height times.
```

### Efc3c51f8f613f4d080c9f09c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
// required to compute Csub
// Multiply each pair of sub-matrices together
// and accumulate the results
for (int m = 0;
m < (A.width / BLOCK_SIZE);
++m) {
```

### E14ff9c392c7b724999a0628d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
As[row][col] = GetElement(Asub, row, col);
Bs[row][col] = GetElement(Bsub, row, col);
// Synchronize to make sure the sub-matrices are loaded
```

### Ec33e4b3787066ac0842880cc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L84-L198

```text
// Thread row and column within Csub
int row = threadIdx.y;
int col = threadIdx.x;
```

## official-024-3:dense:retrieved

CUDA 13.0.1：__shared__缓冲区为何可以作为减少global访问的暂存空间？

必要要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

```json
null
```

实际输入证据：

### Ef0fd0ba42967546506d4e56a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1196-L1217

```text
__global__ void kernel(int* ptr) {
cuda::atomic_ref{*ptr}.store(2);
}
int main() {
// this will be closed/deleted by default on exit
```

### E79e8fef2d91811e6f4a92e47

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L847-L873

```text
}
// On systems with pageableMemoryAccess set to 1, we can access the address
// of a global variable.
The below kernel takes that address as an argument
__global__ void kernel(int* global_variable_addr) {
printf("%d\n", *global_variable_addr);
```

### E2f9bc6ecd218ac9ebf804bc4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L142-L174

```text
cudaFree(d_ptr);
return 0;
}
__global__ void write_value(int* ptr, int v) {
*ptr = v;
}
int main() {
// Requires System-Allocated Memory support
```

### E0e6c4c08207d54b3ecb14dd3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L178-L209

```text
cudaFree(d_ptr);
return 0;
}
__global__ void write_value(int* ptr, int v) {
*ptr = v;
}
int main() {
// Requires System-Allocated Memory support
```

### Ea490cdafe130189f88c5bca3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L250-L290

```text
cudaFree(d_ptr);
return 0;
}
__global__ void write_value(int* ptr, int v) {
*ptr = v;
}
// Requires CUDA Managed Memory support
__managed__ int value;
int main() {
```

### Ec5d6a18fc3c0778fb3d966ee

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1196-L1217

```text
FILE* tmp_file = tmpfile64();
// need to allcate space in the file, we do this with posix_fallocate here
int status = posix_fallocate(fileno(tmp_file), 0, 4096);
if (status !
= 0) ERR("Failed to allocate space in temp file\n");
int* ptr = (int*)mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_PRIVATE, fileno(tmp_file), 0);
if (ptr == MAP_FAILED) ERR("Failed to map temp file\n");
// initialize the value in our file-backed memory
```

### E018556aff23465e6eec6b981

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1196-L1217

```text
*ptr = 1;
printf("Atom value: %d\n", *ptr);
// device and host thread access ptr concurrently, using cuda::atomic_ref
kernel<<<1, 1>>>(ptr);
while (cuda::atomic_ref{*ptr}.load() !
= 2);
// this will always be 2
```

### E2c3ff3a79fd187d92d82bca6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1196-L1217

```text
printf("Atom value: %d\n", *ptr);
```

### E6e3ffb4150cbbf39d5f96104

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L847-L873

```text
However, consider the following example with a global-scope integer:
// this variable is declared at global scope
int global_variable;
__global__ void kernel_uncompilable() {
// this causes a compilation error: global (__host__) variables must not
// be accessed from __device__ / __global__ code
printf("%d\n", global_variable);
```

### E4622c4bde49da749ee0111ad

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L847-L873

```text
}
int main() {
kernel<<<1, 1>>>(&global_variable);
...
return 0;
}
```

### E954dc13d21494aaf6ef2211f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L847-L873

```text
Note that for the extern variable, it could be declared and its memory
```

## official-024-3:hybrid:retrieved

CUDA 13.0.1：__shared__缓冲区为何可以作为减少global访问的暂存空间？

必要要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

```json
null
```

实际输入证据：

### Ef2581112ae6045dac45bddc4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L380-L390

```text
24.1.2.3.
Global-Scope Managed Variables Using __managed__
CUDA __managed__ variables behave as if they were allocated via cudaMallocManaged()
(see Allocation API for CUDA Managed Memory: cudaMallocManaged()).
They simplify programs with global variables, making it particularly easy to exchange data between host and device
without manual allocations or copying.
On systems with full CUDA Unified Memory support,
```

### Ef0fd0ba42967546506d4e56a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1196-L1217

```text
__global__ void kernel(int* ptr) {
cuda::atomic_ref{*ptr}.store(2);
}
int main() {
// this will be closed/deleted by default on exit
```

### Ea490cdafe130189f88c5bca3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L250-L290

```text
cudaFree(d_ptr);
return 0;
}
__global__ void write_value(int* ptr, int v) {
*ptr = v;
}
// Requires CUDA Managed Memory support
__managed__ int value;
int main() {
```

### E79e8fef2d91811e6f4a92e47

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L847-L873

```text
}
// On systems with pageableMemoryAccess set to 1, we can access the address
// of a global variable.
The below kernel takes that address as an argument
__global__ void kernel(int* global_variable_addr) {
printf("%d\n", *global_variable_addr);
```

### E6e3ffb4150cbbf39d5f96104

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L847-L873

```text
However, consider the following example with a global-scope integer:
// this variable is declared at global scope
int global_variable;
__global__ void kernel_uncompilable() {
// this causes a compilation error: global (__host__) variables must not
// be accessed from __device__ / __global__ code
printf("%d\n", global_variable);
```

### E8fa68d39ef8a346e9192a7b8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L380-L390

```text
file-scope or global-scope variables cannot be directly accessed by device code.
But a pointer to these variables may be passed to the kernel as an argument,
see System-Allocated Memory: in-depth examples for examples.
```

### Ec5d6a18fc3c0778fb3d966ee

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1196-L1217

```text
FILE* tmp_file = tmpfile64();
// need to allcate space in the file, we do this with posix_fallocate here
int status = posix_fallocate(fileno(tmp_file), 0, 4096);
if (status !
= 0) ERR("Failed to allocate space in temp file\n");
int* ptr = (int*)mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_PRIVATE, fileno(tmp_file), 0);
if (ptr == MAP_FAILED) ERR("Failed to map temp file\n");
// initialize the value in our file-backed memory
```

### E018556aff23465e6eec6b981

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1196-L1217

```text
*ptr = 1;
printf("Atom value: %d\n", *ptr);
// device and host thread access ptr concurrently, using cuda::atomic_ref
kernel<<<1, 1>>>(ptr);
while (cuda::atomic_ref{*ptr}.load() !
= 2);
// this will always be 2
```

### E051fdfa73be8bbcee440a454

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L250-L290

```text
cudaMalloc(&d_ptr, sizeof(int));
```

## official-024-3:hybrid_rerank:retrieved

CUDA 13.0.1：__shared__缓冲区为何可以作为减少global访问的暂存空间？

必要要点：shared memory可作为软件管理缓存来减少线程块的global memory访问。

禁止误读：使用shared memory意味着取消矩阵乘所需计算。

```json
null
```

实际输入证据：

### E26f4250aa57456c8a93978de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

### Ee0cbe7a9d751458c84c906b7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L80-L80

```text
By blocking the computation this way, we take advantage of fast shared memory and save a lot of global memory bandwidth since A is only read (B.width / block_size) times from global memory and B is read (A.height / block_size) times.
```

### Ef0fd0ba42967546506d4e56a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1196-L1217

```text
__global__ void kernel(int* ptr) {
cuda::atomic_ref{*ptr}.store(2);
}
int main() {
// this will be closed/deleted by default on exit
```

### E873eb11c3e2c3ffbd66b3822

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L166-L166

```text
cudaGetSymbolAddress() is used to retrieve the address pointing to the memory allocated for a variable declared in global memory space. The size of the allocated memory is obtained through cudaGetSymbolSize().
```

### Ec527e1bd27e82478a9d210e6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L829-L840

```text
/** This may be a non-CUDA file */
char* ext_data;
static const char global_string[] = "Hello World";

void __attribute__ ((constructor)) setup(void) {
  ext_data = (char*)malloc(sizeof(global_string));
  strncpy(ext_data, global_string, sizeof(global_string));
}

void __attribute__ ((destructor)) tear_down(void) {
  free(ext_data);
}
```

### Ec62b71f33327c96106baa4e7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
The following code sample is a straightforward implementation of matrix multiplication that does not take advantage of shared memory.
Each thread reads one row of A and one column of B and computes the corresponding element of C as illustrated in Figure 8.
A is therefore read B.width times from global memory and B is read A.height times.
```

### Ec5d6a18fc3c0778fb3d966ee

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1196-L1217

```text
FILE* tmp_file = tmpfile64();
// need to allcate space in the file, we do this with posix_fallocate here
int status = posix_fallocate(fileno(tmp_file), 0, 4096);
if (status !
= 0) ERR("Failed to allocate space in temp file\n");
int* ptr = (int*)mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_PRIVATE, fileno(tmp_file), 0);
if (ptr == MAP_FAILED) ERR("Failed to map temp file\n");
// initialize the value in our file-backed memory
```

### E018556aff23465e6eec6b981

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1196-L1217

```text
*ptr = 1;
printf("Atom value: %d\n", *ptr);
// device and host thread access ptr concurrently, using cuda::atomic_ref
kernel<<<1, 1>>>(ptr);
while (cuda::atomic_ref{*ptr}.load() !
= 2);
// this will always be 2
```

### E2c3ff3a79fd187d92d82bca6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1196-L1217

```text
printf("Atom value: %d\n", *ptr);
```

## official-024-4:oracle:oracle

CUDA 13.0.1：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在shared-memory场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
{
  "conversation_id": "2178dd0b-4292-4af1-927b-1b8e6ccb18b7",
  "answer": "资料库中没有找到可以支持这个问题的证据。请换个问法或先导入相关文档。",
  "citations": [],
  "status": "no_evidence",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "CUDA 13.0.1：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在shared-memory场景下精确的P95延迟毫秒值吗？",
      "hits": 0,
      "evidence": 0
    }
  ]
}
```

实际输入证据：

## official-024-4:bm25:retrieved

CUDA 13.0.1：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在shared-memory场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### E26f4250aa57456c8a93978de

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
6.2.4.
Shared Memory
As detailed in Variable Memory Space Specifiers shared memory is allocated using the __shared__ memory space specifier.
Shared memory is expected to be much faster than global memory as mentioned in Thread Hierarchy and detailed in Shared Memory.
It can be used as scratchpad memory (or software managed cache) to minimize global memory accesses from a CUDA block as illustrated by the following matrix multiplication example.
```

### E886d8ee4d345e68795a91fc2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
does not support Managed Memory: handles to this type of memory may not be shared through
any of the mechanisms discussed in this section.
On systems with full CUDA Unified Memory support,
System-Allocated Memory is Inter-Process Communication (IPC) capable.
Once access to System-Allocated Memory has been shared with other processes,
```

### Edf9df952793566dbe1cf0940

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
24.2.2.4.
Atomic accesses & synchronization primitives
CUDA Unified Memory supports all atomic operations available to host and device threads,
enabling all threads to cooperate by concurrently accessing the same shared memory location.
The CUDA C++ standard library
```

### Edb4fe65bec83c651e06dfe24

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-memory-hierarchy.md#L1-L7

```text
5.3.
Memory Hierarchy
CUDA threads may access data from multiple memory spaces during their execution as illustrated by Figure 6.
Each thread has private local memory.
Each thread block has shared memory visible to all threads of the block and with the same lifetime as the block.
Thread blocks in a thread block cluster can perform read, write, and atomics operations on each other’s shared memory.
All threads have access to the same global memory.
```

### E058aff20cdaceda83a69c4c5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L200-L200

```text
Figure 9 Matrix Multiplication with Shared Memory
```

### Ec62b71f33327c96106baa4e7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-shared-memory.md#L1-L7

```text
The following code sample is a straightforward implementation of matrix multiplication that does not take advantage of shared memory.
Each thread reads one row of A and one column of B and computes the corresponding element of C as illustrated in Figure 8.
A is therefore read B.width times from global memory and B is read A.height times.
```

### E5ee5e8b68e1ef766abe3ad17

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
Note
As of now, using IPC with Unified Memory can have significant performance implications.
Many applications prefer to manage one GPU per process, but still need to use Unified Memory,
for example for over-subscription, and access it from multiple GPUs.
CUDA IPC (see Interprocess Communication)
```

### E42814340a07b80e201e6e128

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
the same Programming Model applies,
similar to File-backed Unified Memory.
See the following references for more information on various ways of creating
```

### Ef435059a27602151178349e6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L921-L938

```text
IPC-capable System-Allocated Memory under Linux:
```

### Ec5e671a6a30fd10316381a19

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
provides many heterogeneous synchronization primitives tuned for concurrent use between host and device threads,
including cuda::atomic, cuda::atomic_ref, cuda::barrier, cuda::semaphore, among many others.
On systems without CPU and GPU page tables: hardware coherency vs.
software coherency,
atomic accesses from the device to file-backed host memory are not supported.
```

### E1e6e9b8c1adb15ad22b95aa6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
The following example code is valid on systems with CPU and GPU page tables: hardware coherency vs.
software coherency
```

## official-024-4:dense:retrieved

CUDA 13.0.1：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在shared-memory场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### Eccc3c69aae8e6b44c211083f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L73-L74

```text
- When the model is too large to fit on a single GPU
- When you need to reduce memory pressure per GPU to allow more KV cache space for higher throughput
```

### E743f50645474beacb25db53c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-thread-hierarchy.md#L68-L68

```text
For efficient cooperation, shared memory is expected to be a low-latency memory near each processor core (much like an L1 cache) and __syncthreads() is expected to be lightweight.
```

### E10d4c1a966d1b318e13ff8ba

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-conserving_memory.md#L51-L56

```text
## Reduce CUDA Graphs

By default, we optimize model inference using CUDA graphs which take up extra memory in the GPU.

!!! warning
    CUDA graph capture takes up more memory in V1 than in V0.
```

### E126a10689ab080a486fe6685

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L78-L80

```text
Unified Memory on devices with full CUDA Unified Memory support

Only CUDA Managed Memory has full support.
```

### E885ebf52beeb93b690a2dc22

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
cudaMemRangeAttributePreferredLocation:
the result returned will be a GPU device id or cudaCpuDeviceId if the entire
memory range has the corresponding processor as preferred location,
```

### E6389c5d5cad82e7e87c6bd6c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
otherwise cudaInvalidDeviceId will be returned.
An application can use this query API to make decision about staging data through
CPU or GPU depending on the preferred location attribute of the managed pointer.
Note that the actual location of the memory range at the time
of the query may be different from the preferred location.
cudaMemRangeAttributeAccessedBy:
```

### E8527e24f7def8dbf37934928

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
will return the list of devices that have that advise set for that memory range.
cudaMemRangeAttributeLastPrefetchLocation:
will return the last location to which the memory range was prefetched
explicitly using cudaMemPrefetchAsync.
Note that this simply returns the last location that the application requested to prefetch the memory range to.
```

### E36e2d92db8de1d6211448d94

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
It gives no indication as to whether the prefetch operation to that location has completed or even begun.
cudaMemRangeAttributePreferredLocationType:
```

## official-024-4:hybrid:retrieved

CUDA 13.0.1：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在shared-memory场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### E126a10689ab080a486fe6685

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L78-L80

```text
Unified Memory on devices with full CUDA Unified Memory support

Only CUDA Managed Memory has full support.
```

### E181ac7ad650994d7f0c7cd40

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L72-L72

```text
Full CUDA Unified Memory: all memory has full support. This includes System-Allocated and CUDA Managed Memory.
```

### E10d4c1a966d1b318e13ff8ba

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-conserving_memory.md#L51-L56

```text
## Reduce CUDA Graphs

By default, we optimize model inference using CUDA graphs which take up extra memory in the GPU.

!!! warning
    CUDA graph capture takes up more memory in V1 than in V0.
```

### E3b01b0318ab093fe54e56e1c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L102-L102

```text
CUDA for Tegra Memory Management
```

### E1c19eb5b4cf97a8ca049ce26

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1249-L1249

```text
24.3. Unified memory on devices without full CUDA Unified Memory support
```

## official-024-4:hybrid_rerank:retrieved

CUDA 13.0.1：仅凭当前官方资料，能给出我未提供硬件、模型和日志的私有部署在shared-memory场景下精确的P95延迟毫秒值吗？

必要要点：明确说明缺少所需测量或环境信息，不能推断精确答案。

禁止误读：编造未提供的配置、测量值或运行日志。

```json
null
```

实际输入证据：

### E885ebf52beeb93b690a2dc22

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
cudaMemRangeAttributePreferredLocation:
the result returned will be a GPU device id or cudaCpuDeviceId if the entire
memory range has the corresponding processor as preferred location,
```

### E3b01b0318ab093fe54e56e1c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L102-L102

```text
CUDA for Tegra Memory Management
```

### Ea2ded2b31f2140aea4caf06f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L213-L246

```text
// Requires CUDA Managed Memory support
cudaMallocManaged(&ptr, sizeof(int));
write_value<<<1, 1>>>(ptr, 1);
// Synchronize required
// (before, cudaMemcpy was synchronizing)
cudaDeviceSynchronize();
```

### E2dd44275fb79a73fc5d29f98

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L370-L378

```text
Note

For systems that support CUDA Managed Memory allocations, but do not provide full support,
see Coherency and Concurrency.
Implementation details (may change any time):

Devices of compute capability 5.x allocate CUDA Managed Memory on the GPU.

Devices of compute capability 6.x and greater populate the memory on first touch, just like System-Allocated Memory APIs.
```

### E1c19eb5b4cf97a8ca049ce26

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1249-L1249

```text
24.3. Unified memory on devices without full CUDA Unified Memory support
```

### E6389c5d5cad82e7e87c6bd6c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
otherwise cudaInvalidDeviceId will be returned.
An application can use this query API to make decision about staging data through
CPU or GPU depending on the preferred location attribute of the managed pointer.
Note that the actual location of the memory range at the time
of the query may be different from the preferred location.
cudaMemRangeAttributeAccessedBy:
```

### E8527e24f7def8dbf37934928

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
will return the list of devices that have that advise set for that memory range.
cudaMemRangeAttributeLastPrefetchLocation:
will return the last location to which the memory range was prefetched
explicitly using cudaMemPrefetchAsync.
Note that this simply returns the last location that the application requested to prefetch the memory range to.
```

### E36e2d92db8de1d6211448d94

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
It gives no indication as to whether the prefetch operation to that location has completed or even begun.
cudaMemRangeAttributePreferredLocationType:
```

### Ed8dd56b8cc7859a224dde2f1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L213-L246

```text
cudaFree(d_ptr);
return 0;
}
__global__ void write_value(int* ptr, int v) {
*ptr = v;
}
int main() {
int* ptr = nullptr;
```

### E2567f675cadc8fde9750eabf

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L213-L246

```text
printf("value = %d\n", *ptr);
cudaFree(ptr);
return 0;
}
```

### Ef825f563984abf708d99cc6e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L213-L246

```text
cudaMalloc(&d_ptr, sizeof(int));
write_value<<<1, 1>>>(d_ptr, 1);
int h_value;
// Copy memory back to the host and synchronize
cudaMemcpy(&h_value, d_ptr, sizeof(int),
cudaMemcpyDefault);
printf("value = %d\n", h_value);
```

### Ec11933778268b0ed0f6cd3dc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L213-L246

```text
__global__ void write_value(int* ptr, int v) {
*ptr = v;
}
```

## official-026-1:oracle:oracle

CUDA 13.0.1：Async内存拷贝何时仍可能同步？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### Ed6cb6db9ada95f18e2c062f6

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#asynchronous-concurrent-execution

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

## official-026-1:bm25:retrieved

CUDA 13.0.1：Async内存拷贝何时仍可能同步？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### E2ebc08fd5ff6b619d38e64df

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// Will retain a
// new reference
cudaGraphDestroy(graph);
// graphExec still owns a reference
cudaGraphLaunch(graphExec, 0);
// Async launch has access to the user objects
```

### E76166ab4dfae9b45ee1e6e9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L33-L35

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

### E57a99437853406f7a0202cc5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L31-L50

```text
Check out <gh-file:examples/offline_inference/multilora_inference.py> for an example of how to use LoRA adapters with the async engine and how to use more advanced configuration options.
```

### Ec5b93f855e95a5da9d7c5a60

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L25-L31

```text
Memory copies within a single device’s memory;

Memory copies from host to device of a memory block of 64 KB or less;

Memory copies performed by functions that are suffixed with Async;

Memory set function calls.
```

### Ebf812ffaa039ef650f8eb40e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L172-L203

```text
```python
        import os
        import s3fs
        from vllm.lora.request import LoRARequest
        from vllm.lora.resolver import LoRAResolver

        class S3LoRAResolver(LoRAResolver):
            def __init__(self):
                self.s3 = s3fs.S3FileSystem()
                self.s3_path_format = os.getenv("S3_PATH_TEMPLATE")
                self.local_path_format = os.getenv("LOCAL_PATH_TEMPLATE")

            async def resolve_lora
```

### Efc24074d12a2fb9e19281f26

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
);
// No more references owned by this thread;
no need to call release API
cudaGraphExec_t graphExec;
cudaGraphInstantiate(&graphExec, graph, nullptr, nullptr, 0);
```

### E1f8f9760ee1945ed9c68dd30

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaGraphExecDestroy(graphExec);
// Launch is not synchronized;
the release
// will be deferred if needed
cudaStreamSynchronize(0);
// After the launch is synchronized, the remaining
// reference is released and the destructor will
```

### E21b180de346261e28a6ec32c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaUserObjectNoDestructorSync  // Acknowledge that the callback cannot be
// waited on via CUDA
);
cudaGraphRetainUserObject(
graph,
cuObject,
1,  // Number of references
cudaGraphUserObjectMove  // Transfer a reference owned by the caller (do
// not modify the total reference count)
```

### Ef99e328d65c3f0c790c882d5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// execute.
Note this happens asynchronously.
// If the destructor callback had signaled a synchronization object, it would
// be safe to wait on it at this point.
```

### E2f5db7779a2f507b05cb56aa

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
Object *object = new Object;
// C++ object with possibly nontrivial destructor
cudaUserObject_t cuObject;
cudaUserObjectCreate(
&cuObject,
object,  // Here we use a CUDA-provided template wrapper for this API,
// which supplies a callback to delete the C++ object pointer
1,  // Initial refcount
```

### E06c1e79fda42049fdc268fee

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L172-L203

```text
1.
```

## official-026-1:dense:retrieved

CUDA 13.0.1：Async内存拷贝何时仍可能同步？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### E1f8f9760ee1945ed9c68dd30

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaGraphExecDestroy(graphExec);
// Launch is not synchronized;
the release
// will be deferred if needed
cudaStreamSynchronize(0);
// After the launch is synchronized, the remaining
// reference is released and the destructor will
```

### Ea2ded2b31f2140aea4caf06f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L213-L246

```text
// Requires CUDA Managed Memory support
cudaMallocManaged(&ptr, sizeof(int));
write_value<<<1, 1>>>(ptr, 1);
// Synchronize required
// (before, cudaMemcpy was synchronizing)
cudaDeviceSynchronize();
```

### E0bf105ee520f57f38bb42e8f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-page-locked-host-memory.md#L53-L61

```text
The CUDA runtime does not support a PCI Express bus topology where a PCI Express bridge splits
8-byte naturally aligned operations and NVIDIA is not aware of any topology that splits
16-byte naturally aligned operations.
```

### E45fcf8ab878d9077a6622413

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1477-L1483

```text
If cudaMemcpyDeviceTo* is specified and the source data is unified memory, then it will be accessed from the device.
The source must be coherently accessible from the device in the copy stream (2);
otherwise, an error is returned.
Similar rules apply to the destination when cudaMemcpy*ToDevice is specified and the destination is unified memory.
```

### E7f15fc933bca7e85735c0583

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1485-L1493

```text
If cudaMemcpyDefault is specified, then unified memory will be accessed from the host either if it cannot be coherently accessed from the device in the copy stream (2) or if the preferred location for the data is cudaCpuDeviceId and it can be coherently accessed from the host in the copy stream (1);
otherwise, it will be accessed from the device.
```

### E2ebc08fd5ff6b619d38e64df

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// Will retain a
// new reference
cudaGraphDestroy(graph);
// graphExec still owns a reference
cudaGraphLaunch(graphExec, 0);
// Async launch has access to the user objects
```

### Ef99e328d65c3f0c790c882d5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// execute.
Note this happens asynchronously.
// If the destructor callback had signaled a synchronization object, it would
// be safe to wait on it at this point.
```

### Efc24074d12a2fb9e19281f26

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
);
// No more references owned by this thread;
no need to call release API
cudaGraphExec_t graphExec;
cudaGraphInstantiate(&graphExec, graph, nullptr, nullptr, 0);
```

### E21b180de346261e28a6ec32c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaUserObjectNoDestructorSync  // Acknowledge that the callback cannot be
// waited on via CUDA
);
cudaGraphRetainUserObject(
graph,
cuObject,
1,  // Number of references
cudaGraphUserObjectMove  // Transfer a reference owned by the caller (do
// not modify the total reference count)
```

### E2f5db7779a2f507b05cb56aa

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
Object *object = new Object;
// C++ object with possibly nontrivial destructor
cudaUserObject_t cuObject;
cudaUserObjectCreate(
&cuObject,
```

## official-026-1:hybrid:retrieved

CUDA 13.0.1：Async内存拷贝何时仍可能同步？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### E76166ab4dfae9b45ee1e6e9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L33-L35

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

### E0a73c6fa9de0d1f1e502224d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L335-L337

```text
24.1.2.2. Allocation API for CUDA Managed Memory: cudaMallocManaged()

On systems with CUDA Managed Memory support, unified memory may be allocated using:
```

### E181ac7ad650994d7f0c7cd40

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L72-L72

```text
Full CUDA Unified Memory: all memory has full support. This includes System-Allocated and CUDA Managed Memory.
```

### Eda86ef0d3db21dcb5942cc0f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L747-L747

```text
24.2. Unified memory on devices with full CUDA Unified Memory support
```

### E2ebc08fd5ff6b619d38e64df

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// Will retain a
// new reference
cudaGraphDestroy(graph);
// graphExec still owns a reference
cudaGraphLaunch(graphExec, 0);
// Async launch has access to the user objects
```

### Ef21de5916d0902d7b7aef21d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L33-L35

```text
Programmers can globally disable asynchronicity of kernel launches for all CUDA applications running on a system by setting the CUDA_LAUNCH_BLOCKING environment variable to 1.
This feature is provided for debugging purposes only and should not be used as a way to make production software run reliably.
Kernel launches are synchronous if hardware counters are collected via a profiler (Nsight Compute) unless concurrent kernel profiling is enabled.
```

### Efc24074d12a2fb9e19281f26

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
);
// No more references owned by this thread;
no need to call release API
cudaGraphExec_t graphExec;
cudaGraphInstantiate(&graphExec, graph, nullptr, nullptr, 0);
```

### E1f8f9760ee1945ed9c68dd30

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaGraphExecDestroy(graphExec);
// Launch is not synchronized;
the release
// will be deferred if needed
cudaStreamSynchronize(0);
// After the launch is synchronized, the remaining
// reference is released and the destructor will
```

### E21b180de346261e28a6ec32c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaUserObjectNoDestructorSync  // Acknowledge that the callback cannot be
// waited on via CUDA
);
cudaGraphRetainUserObject(
graph,
cuObject,
1,  // Number of references
cudaGraphUserObjectMove  // Transfer a reference owned by the caller (do
// not modify the total reference count)
```

### Ef99e328d65c3f0c790c882d5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// execute.
Note this happens asynchronously.
// If the destructor callback had signaled a synchronization object, it would
// be safe to wait on it at this point.
```

### E2f5db7779a2f507b05cb56aa

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
Object *object = new Object;
// C++ object with possibly nontrivial destructor
cudaUserObject_t cuObject;
cudaUserObjectCreate(
&cuObject,
object,  // Here we use a CUDA-provided template wrapper for this API,
// which supplies a callback to delete the C++ object pointer
1,  // Initial refcount
```

## official-026-1:hybrid_rerank:retrieved

CUDA 13.0.1：Async内存拷贝何时仍可能同步？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### E76166ab4dfae9b45ee1e6e9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L33-L35

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

### E1f8f9760ee1945ed9c68dd30

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaGraphExecDestroy(graphExec);
// Launch is not synchronized;
the release
// will be deferred if needed
cudaStreamSynchronize(0);
// After the launch is synchronized, the remaining
// reference is released and the destructor will
```

### Ef0fd0ba42967546506d4e56a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1196-L1217

```text
__global__ void kernel(int* ptr) {
cuda::atomic_ref{*ptr}.store(2);
}
int main() {
// this will be closed/deleted by default on exit
```

### Ec5b93f855e95a5da9d7c5a60

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L25-L31

```text
Memory copies within a single device’s memory;

Memory copies from host to device of a memory block of 64 KB or less;

Memory copies performed by functions that are suffixed with Async;

Memory set function calls.
```

### E477a91043c3505de28aeea79

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
// has been associated with no stream.
return  0;
}
Here we explicitly associate y with host accessibility, thus enabling access at all times from the CPU.
(As before, note the absence of cudaDeviceSynchronize() before the access.) Accesses to y by the GPU running kernel will now produce undefined results.
Note that associating a variable with a stream does not change the associating of any other variable.
```

### Ef21de5916d0902d7b7aef21d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L33-L35

```text
Programmers can globally disable asynchronicity of kernel launches for all CUDA applications running on a system by setting the CUDA_LAUNCH_BLOCKING environment variable to 1.
This feature is provided for debugging purposes only and should not be used as a way to make production software run reliably.
Kernel launches are synchronous if hardware counters are collected via a profiler (Nsight Compute) unless concurrent kernel profiling is enabled.
```

### E2ebc08fd5ff6b619d38e64df

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// Will retain a
// new reference
cudaGraphDestroy(graph);
// graphExec still owns a reference
cudaGraphLaunch(graphExec, 0);
// Async launch has access to the user objects
```

### Ef99e328d65c3f0c790c882d5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// execute.
Note this happens asynchronously.
// If the destructor callback had signaled a synchronization object, it would
// be safe to wait on it at this point.
```

### Efc24074d12a2fb9e19281f26

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
);
// No more references owned by this thread;
no need to call release API
cudaGraphExec_t graphExec;
cudaGraphInstantiate(&graphExec, graph, nullptr, nullptr, 0);
```

### E21b180de346261e28a6ec32c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaUserObjectNoDestructorSync  // Acknowledge that the callback cannot be
// waited on via CUDA
);
cudaGraphRetainUserObject(
graph,
cuObject,
1,  // Number of references
cudaGraphUserObjectMove  // Transfer a reference owned by the caller (do
// not modify the total reference count)
```

## official-026-2:oracle:oracle

CUDA 13.0.1：调用Async传输却未得到预期重叠，应先检查主机缓冲区的什么属性？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### Ed6cb6db9ada95f18e2c062f6

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#asynchronous-concurrent-execution

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

## official-026-2:bm25:retrieved

CUDA 13.0.1：调用Async传输却未得到预期重叠，应先检查主机缓冲区的什么属性？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### E2ebc08fd5ff6b619d38e64df

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// Will retain a
// new reference
cudaGraphDestroy(graph);
// graphExec still owns a reference
cudaGraphLaunch(graphExec, 0);
// Async launch has access to the user objects
```

### E76166ab4dfae9b45ee1e6e9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L33-L35

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

### E57a99437853406f7a0202cc5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L31-L50

```text
Check out <gh-file:examples/offline_inference/multilora_inference.py> for an example of how to use LoRA adapters with the async engine and how to use more advanced configuration options.
```

### Ec5b93f855e95a5da9d7c5a60

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L25-L31

```text
Memory copies within a single device’s memory;

Memory copies from host to device of a memory block of 64 KB or less;

Memory copies performed by functions that are suffixed with Async;

Memory set function calls.
```

### Ebf812ffaa039ef650f8eb40e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L172-L203

```text
```python
        import os
        import s3fs
        from vllm.lora.request import LoRARequest
        from vllm.lora.resolver import LoRAResolver

        class S3LoRAResolver(LoRAResolver):
            def __init__(self):
                self.s3 = s3fs.S3FileSystem()
                self.s3_path_format = os.getenv("S3_PATH_TEMPLATE")
                self.local_path_format = os.getenv("LOCAL_PATH_TEMPLATE")

            async def resolve_lora
```

### Efc24074d12a2fb9e19281f26

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
);
// No more references owned by this thread;
no need to call release API
cudaGraphExec_t graphExec;
cudaGraphInstantiate(&graphExec, graph, nullptr, nullptr, 0);
```

### E1f8f9760ee1945ed9c68dd30

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaGraphExecDestroy(graphExec);
// Launch is not synchronized;
the release
// will be deferred if needed
cudaStreamSynchronize(0);
// After the launch is synchronized, the remaining
// reference is released and the destructor will
```

### E21b180de346261e28a6ec32c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaUserObjectNoDestructorSync  // Acknowledge that the callback cannot be
// waited on via CUDA
);
cudaGraphRetainUserObject(
graph,
cuObject,
1,  // Number of references
cudaGraphUserObjectMove  // Transfer a reference owned by the caller (do
// not modify the total reference count)
```

### Ef99e328d65c3f0c790c882d5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// execute.
Note this happens asynchronously.
// If the destructor callback had signaled a synchronization object, it would
// be safe to wait on it at this point.
```

### E2f5db7779a2f507b05cb56aa

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
Object *object = new Object;
// C++ object with possibly nontrivial destructor
cudaUserObject_t cuObject;
cudaUserObjectCreate(
&cuObject,
object,  // Here we use a CUDA-provided template wrapper for this API,
// which supplies a callback to delete the C++ object pointer
1,  // Initial refcount
```

### E06c1e79fda42049fdc268fee

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L172-L203

```text
1.
```

## official-026-2:dense:retrieved

CUDA 13.0.1：调用Async传输却未得到预期重叠，应先检查主机缓冲区的什么属性？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### E0bf105ee520f57f38bb42e8f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-page-locked-host-memory.md#L53-L61

```text
The CUDA runtime does not support a PCI Express bus topology where a PCI Express bridge splits
8-byte naturally aligned operations and NVIDIA is not aware of any topology that splits
16-byte naturally aligned operations.
```

### E1f8f9760ee1945ed9c68dd30

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaGraphExecDestroy(graphExec);
// Launch is not synchronized;
the release
// will be deferred if needed
cudaStreamSynchronize(0);
// After the launch is synchronized, the remaining
// reference is released and the destructor will
```

### Ea2ded2b31f2140aea4caf06f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L213-L246

```text
// Requires CUDA Managed Memory support
cudaMallocManaged(&ptr, sizeof(int));
write_value<<<1, 1>>>(ptr, 1);
// Synchronize required
// (before, cudaMemcpy was synchronizing)
cudaDeviceSynchronize();
```

### E477a91043c3505de28aeea79

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
// has been associated with no stream.
return  0;
}
Here we explicitly associate y with host accessibility, thus enabling access at all times from the CPU.
(As before, note the absence of cudaDeviceSynchronize() before the access.) Accesses to y by the GPU running kernel will now produce undefined results.
Note that associating a variable with a stream does not change the associating of any other variable.
```

### Eda4d68c63f9e12abd50788a9

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-install.md#L18-L21

```text
**Quick fixes to common problems**
- If you encounter `OSError: CUDA_HOME environment variable is not set`.
Please set it to your CUDA install root with either of the following solutions:
```

### E6cdf3e87eb776614e116411e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-page-locked-host-memory.md#L53-L61

```text
load and store operations.
These component load and store operations have the same requirements on preservation of naturally aligned accesses.
```

### Ec8badce76b9e3fd7d3fbe392

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-page-locked-host-memory.md#L53-L61

```text
Also note that CUDA runtime requires that 1-byte, 2-byte, 4-byte, 8-byte, and 16-byte naturally aligned
loads and stores to host memory initiated from the device are preserved as single accesses
from the point of view of the host and other devices.
On some platforms, atomics to memory may be broken by the hardware into separate
```

### E2ebc08fd5ff6b619d38e64df

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// Will retain a
// new reference
cudaGraphDestroy(graph);
// graphExec still owns a reference
cudaGraphLaunch(graphExec, 0);
// Async launch has access to the user objects
```

### Ef99e328d65c3f0c790c882d5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// execute.
Note this happens asynchronously.
// If the destructor callback had signaled a synchronization object, it would
// be safe to wait on it at this point.
```

### Efc24074d12a2fb9e19281f26

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
);
// No more references owned by this thread;
no need to call release API
cudaGraphExec_t graphExec;
cudaGraphInstantiate(&graphExec, graph, nullptr, nullptr, 0);
```

### E21b180de346261e28a6ec32c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaUserObjectNoDestructorSync  // Acknowledge that the callback cannot be
// waited on via CUDA
);
cudaGraphRetainUserObject(
graph,
cuObject,
1,  // Number of references
```

## official-026-2:hybrid:retrieved

CUDA 13.0.1：调用Async传输却未得到预期重叠，应先检查主机缓冲区的什么属性？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### E0bf105ee520f57f38bb42e8f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-page-locked-host-memory.md#L53-L61

```text
The CUDA runtime does not support a PCI Express bus topology where a PCI Express bridge splits
8-byte naturally aligned operations and NVIDIA is not aware of any topology that splits
16-byte naturally aligned operations.
```

### E2ebc08fd5ff6b619d38e64df

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// Will retain a
// new reference
cudaGraphDestroy(graph);
// graphExec still owns a reference
cudaGraphLaunch(graphExec, 0);
// Async launch has access to the user objects
```

### E76166ab4dfae9b45ee1e6e9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L33-L35

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

### E1f8f9760ee1945ed9c68dd30

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaGraphExecDestroy(graphExec);
// Launch is not synchronized;
the release
// will be deferred if needed
cudaStreamSynchronize(0);
// After the launch is synchronized, the remaining
// reference is released and the destructor will
```

### E57a99437853406f7a0202cc5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L31-L50

```text
Check out <gh-file:examples/offline_inference/multilora_inference.py> for an example of how to use LoRA adapters with the async engine and how to use more advanced configuration options.
```

### E6cdf3e87eb776614e116411e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-page-locked-host-memory.md#L53-L61

```text
load and store operations.
These component load and store operations have the same requirements on preservation of naturally aligned accesses.
```

### Ec8badce76b9e3fd7d3fbe392

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-page-locked-host-memory.md#L53-L61

```text
Also note that CUDA runtime requires that 1-byte, 2-byte, 4-byte, 8-byte, and 16-byte naturally aligned
loads and stores to host memory initiated from the device are preserved as single accesses
from the point of view of the host and other devices.
On some platforms, atomics to memory may be broken by the hardware into separate
```

### Efc24074d12a2fb9e19281f26

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
);
// No more references owned by this thread;
no need to call release API
cudaGraphExec_t graphExec;
cudaGraphInstantiate(&graphExec, graph, nullptr, nullptr, 0);
```

### Ef99e328d65c3f0c790c882d5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// execute.
Note this happens asynchronously.
// If the destructor callback had signaled a synchronization object, it would
// be safe to wait on it at this point.
```

### E21b180de346261e28a6ec32c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaUserObjectNoDestructorSync  // Acknowledge that the callback cannot be
// waited on via CUDA
);
cudaGraphRetainUserObject(
graph,
cuObject,
1,  // Number of references
cudaGraphUserObjectMove  // Transfer a reference owned by the caller (do
// not modify the total reference count)
```

### E2f5db7779a2f507b05cb56aa

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
Object *object = new Object;
// C++ object with possibly nontrivial destructor
cudaUserObject_t cuObject;
cudaUserObjectCreate(
&cuObject,
object,  // Here we use a CUDA-provided template wrapper for this API,
// which supplies a callback to delete the C++ object pointer
1,  // Initial refcount
```

## official-026-2:hybrid_rerank:retrieved

CUDA 13.0.1：调用Async传输却未得到预期重叠，应先检查主机缓冲区的什么属性？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### Ea86cf3fb222a080e065d780a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-streams.md#L5-L24

```text
cudaMemcpyAsync(hostPtr + i * size, outputDevPtr + i * size,
size, cudaMemcpyDeviceToHost, stream[i]);
}
```

### Eb09a14de4b65a8718d6c9f01

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L589-L603

```text
// execute on CPU
cudaMemLocation location = {.type = cudaMemLocationTypeDevice, .id = myGpuId};
cudaMemPrefetchAsync(data, N, location, s, 0 /* flags */);
// prefetch to GPU
```

### E76166ab4dfae9b45ee1e6e9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L33-L35

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

### E1f8f9760ee1945ed9c68dd30

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaGraphExecDestroy(graphExec);
// Launch is not synchronized;
the release
// will be deferred if needed
cudaStreamSynchronize(0);
// After the launch is synchronized, the remaining
// reference is released and the destructor will
```

### Ea2ded2b31f2140aea4caf06f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L213-L246

```text
// Requires CUDA Managed Memory support
cudaMallocManaged(&ptr, sizeof(int));
write_value<<<1, 1>>>(ptr, 1);
// Synchronize required
// (before, cudaMemcpy was synchronizing)
cudaDeviceSynchronize();
```

### E92434999fd9d594aed1241ad

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-streams.md#L5-L24

```text
Each of these streams is defined by the following code sample as a sequence of one memory copy from host to device, one kernel launch, and one memory copy from device to host:
for (int i = 0;
i < 2;
++i) {
cudaMemcpyAsync(inputDevPtr + i * size, hostPtr + i * size,
size, cudaMemcpyHostToDevice, stream[i]);
MyKernel <<<100, 512, 0, stream[i]>>>
(outputDevPtr + i * size, inputDevPtr + i * size, size);
```

### Ea8cb526686963d597e8845b8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-streams.md#L5-L24

```text
6.2.8.5.1.
Creation and Destruction of Streams
A stream is defined by creating a stream object and specifying it as the stream parameter to a sequence of kernel launches and host <-> device memory copies.
The following code sample creates two streams and allocates an array hostPtr of float in page-locked memory.
cudaStream_t stream[2];
for (int i = 0;
i < 2;
++i)
cudaStreamCreate(&stream[i]);
float* hostPtr;
cudaMallocHost(&hostPtr, 2 * size);
```

### E52ec56a9d4444256a742d13a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L589-L603

```text
Managed
void test_prefetch_managed(cudaStream_t s) {
char *data;
cudaMallocManaged(&data, N);
init_data(data, N);
```

### E0bda9d8005b12499e7a4d11a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L589-L603

```text
mykernel<<<(N + TPB - 1) / TPB, TPB, 0, s>>>(data, N);
// execute on GPU
location = {.type = cudaMemLocationTypeHost};
cudaMemPrefetchAsync(data, N, location, s, 0 /* flags */);
// prefetch to CPU
```

### E13b18885cb8495677d9f6495

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L589-L603

```text
cudaStreamSynchronize(s);
use_data(data, N);
cudaFree(data);
}
```

### Efc24074d12a2fb9e19281f26

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
);
```

## official-026-3:oracle:oracle

CUDA 13.0.1：排查该主题时，有人声称“所有带Async后缀的调用都无条件异步。”，根据文档这个说法哪里需要纠正？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### Ed6cb6db9ada95f18e2c062f6

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#asynchronous-concurrent-execution

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

## official-026-3:bm25:retrieved

CUDA 13.0.1：排查该主题时，有人声称“所有带Async后缀的调用都无条件异步。”，根据文档这个说法哪里需要纠正？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### E2ebc08fd5ff6b619d38e64df

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// Will retain a
// new reference
cudaGraphDestroy(graph);
// graphExec still owns a reference
cudaGraphLaunch(graphExec, 0);
// Async launch has access to the user objects
```

### E76166ab4dfae9b45ee1e6e9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L33-L35

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

### E57a99437853406f7a0202cc5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L31-L50

```text
Check out <gh-file:examples/offline_inference/multilora_inference.py> for an example of how to use LoRA adapters with the async engine and how to use more advanced configuration options.
```

### Ec5b93f855e95a5da9d7c5a60

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L25-L31

```text
Memory copies within a single device’s memory;

Memory copies from host to device of a memory block of 64 KB or less;

Memory copies performed by functions that are suffixed with Async;

Memory set function calls.
```

### Ebf812ffaa039ef650f8eb40e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L172-L203

```text
```python
        import os
        import s3fs
        from vllm.lora.request import LoRARequest
        from vllm.lora.resolver import LoRAResolver

        class S3LoRAResolver(LoRAResolver):
            def __init__(self):
                self.s3 = s3fs.S3FileSystem()
                self.s3_path_format = os.getenv("S3_PATH_TEMPLATE")
                self.local_path_format = os.getenv("LOCAL_PATH_TEMPLATE")

            async def resolve_lora
```

### Efc24074d12a2fb9e19281f26

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
);
// No more references owned by this thread;
no need to call release API
cudaGraphExec_t graphExec;
cudaGraphInstantiate(&graphExec, graph, nullptr, nullptr, 0);
```

### E1f8f9760ee1945ed9c68dd30

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaGraphExecDestroy(graphExec);
// Launch is not synchronized;
the release
// will be deferred if needed
cudaStreamSynchronize(0);
// After the launch is synchronized, the remaining
// reference is released and the destructor will
```

### E21b180de346261e28a6ec32c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaUserObjectNoDestructorSync  // Acknowledge that the callback cannot be
// waited on via CUDA
);
cudaGraphRetainUserObject(
graph,
cuObject,
1,  // Number of references
cudaGraphUserObjectMove  // Transfer a reference owned by the caller (do
// not modify the total reference count)
```

### Ef99e328d65c3f0c790c882d5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// execute.
Note this happens asynchronously.
// If the destructor callback had signaled a synchronization object, it would
// be safe to wait on it at this point.
```

### E2f5db7779a2f507b05cb56aa

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
Object *object = new Object;
// C++ object with possibly nontrivial destructor
cudaUserObject_t cuObject;
cudaUserObjectCreate(
&cuObject,
object,  // Here we use a CUDA-provided template wrapper for this API,
// which supplies a callback to delete the C++ object pointer
1,  // Initial refcount
```

### E06c1e79fda42049fdc268fee

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L172-L203

```text
1.
```

## official-026-3:dense:retrieved

CUDA 13.0.1：排查该主题时，有人声称“所有带Async后缀的调用都无条件异步。”，根据文档这个说法哪里需要纠正？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### Ec6c6044cb73387a74449ccb2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L278-L278

```text
A node whose function originally did not use CUDA dynamic parallelism cannot be updated to a function which uses CUDA dynamic parallelism.
```

### E9f9fc511bfd84bbd49821eff

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
For example, associating x with stream1 does not ensure that only x is accessed by kernels launched in stream1, thus an error is caused by this code:
```

### E477a91043c3505de28aeea79

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
// has been associated with no stream.
return  0;
}
Here we explicitly associate y with host accessibility, thus enabling access at all times from the CPU.
(As before, note the absence of cudaDeviceSynchronize() before the access.) Accesses to y by the GPU running kernel will now produce undefined results.
Note that associating a variable with a stream does not change the associating of any other variable.
```

### E33fb01fcc939e6e96fbce789

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L286-L292

```text
Only 1D cudaMemset/cudaMemcpy nodes can be changed.

Additional memcpy node restrictions:

Changing either the source or destination memory type (i.e., cudaPitchedPtr, cudaArray_t, etc.), or the type of transfer (i.e., cudaMemcpyKind) is not supported.

External semaphore wait nodes and record nodes:
```

### E0be60d2e48c2378da5b289c2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L250-L254

```text
In either case, if previous launches are not synchronized, any references which would be released are held until the launches have finished executing.
There is not currently a mechanism to wait on user object destructors via a CUDA API.
Users may signal a synchronization object manually from the destructor code.
In addition, it is not legal to call CUDA APIs from the destructor, similar to the restriction on cudaLaunchHostFunc.
```

### E75dedcf490c9d8c7f1d5d439

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
kernel<<< 1, 1, 0, stream1 >>>();
// Note: Launches into stream1.
y = 20;
// Success – a kernel is running but “y”
```

### E6cff26435664c9ec90900fe3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
__device__ __managed__ int x, y=2;
__global__  void  kernel() {
x = 10;
}
int main() {
cudaStream_t stream1;
cudaStreamCreate(&stream1);
cudaStreamAttachMemAsync(stream1, &y, 0, cudaMemAttachHost);
cudaDeviceSynchronize();
// Wait for Host attachment to occur.
```

### E8c2ba59623fd635499a2c2c4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
24.3.2.4.4.
Stream Association Examples
Associating data with a stream allows fine-grained control over CPU + GPU concurrency, but what data is visible to which streams must be kept in mind when using devices of compute capability lower than 6.0.
Looking at the earlier synchronization example:
```

### E0d8a2bd0465510e0c8bd3d9d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L250-L254

```text
References owned by graphs in child graph nodes are associated to the child graphs, not the parents.
If a child graph is updated or deleted, the references change accordingly.
```

## official-026-3:hybrid:retrieved

CUDA 13.0.1：排查该主题时，有人声称“所有带Async后缀的调用都无条件异步。”，根据文档这个说法哪里需要纠正？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### Ec6c6044cb73387a74449ccb2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L278-L278

```text
A node whose function originally did not use CUDA dynamic parallelism cannot be updated to a function which uses CUDA dynamic parallelism.
```

### E2ebc08fd5ff6b619d38e64df

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// Will retain a
// new reference
cudaGraphDestroy(graph);
// graphExec still owns a reference
cudaGraphLaunch(graphExec, 0);
// Async launch has access to the user objects
```

### E76166ab4dfae9b45ee1e6e9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L33-L35

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

### E9f9fc511bfd84bbd49821eff

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
For example, associating x with stream1 does not ensure that only x is accessed by kernels launched in stream1, thus an error is caused by this code:
```

### E477a91043c3505de28aeea79

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
// has been associated with no stream.
return  0;
}
Here we explicitly associate y with host accessibility, thus enabling access at all times from the CPU.
(As before, note the absence of cudaDeviceSynchronize() before the access.) Accesses to y by the GPU running kernel will now produce undefined results.
Note that associating a variable with a stream does not change the associating of any other variable.
```

### Efc24074d12a2fb9e19281f26

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
);
// No more references owned by this thread;
no need to call release API
cudaGraphExec_t graphExec;
cudaGraphInstantiate(&graphExec, graph, nullptr, nullptr, 0);
```

### E1f8f9760ee1945ed9c68dd30

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaGraphExecDestroy(graphExec);
// Launch is not synchronized;
the release
// will be deferred if needed
cudaStreamSynchronize(0);
// After the launch is synchronized, the remaining
// reference is released and the destructor will
```

### E21b180de346261e28a6ec32c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaUserObjectNoDestructorSync  // Acknowledge that the callback cannot be
// waited on via CUDA
);
cudaGraphRetainUserObject(
graph,
cuObject,
1,  // Number of references
cudaGraphUserObjectMove  // Transfer a reference owned by the caller (do
// not modify the total reference count)
```

### Ef99e328d65c3f0c790c882d5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// execute.
Note this happens asynchronously.
// If the destructor callback had signaled a synchronization object, it would
// be safe to wait on it at this point.
```

### E2f5db7779a2f507b05cb56aa

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
Object *object = new Object;
// C++ object with possibly nontrivial destructor
cudaUserObject_t cuObject;
cudaUserObjectCreate(
&cuObject,
object,  // Here we use a CUDA-provided template wrapper for this API,
// which supplies a callback to delete the C++ object pointer
1,  // Initial refcount
```

### E75dedcf490c9d8c7f1d5d439

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
kernel<<< 1, 1, 0, stream1 >>>();
// Note: Launches into stream1.
y = 20;
```

## official-026-3:hybrid_rerank:retrieved

CUDA 13.0.1：排查该主题时，有人声称“所有带Async后缀的调用都无条件异步。”，根据文档这个说法哪里需要纠正？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### E76166ab4dfae9b45ee1e6e9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L33-L35

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

### E2ebc08fd5ff6b619d38e64df

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// Will retain a
// new reference
cudaGraphDestroy(graph);
// graphExec still owns a reference
cudaGraphLaunch(graphExec, 0);
// Async launch has access to the user objects
```

### Ec5335ba9c597a43e6a9c547e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L454-L479

```text
char const* kind(cudaPointerAttributes a, bool pma, bool cma) {
switch(a.type) {
case cudaMemoryTypeHost: return pma?
"Unified: CUDA Host or Registered Memory" :
"Not Unified: CUDA Host or Registered Memory";
case cudaMemoryTypeDevice: return "Not Unified: CUDA Device Memory";
case cudaMemoryTypeManaged: return cma?
"Unified: CUDA Managed Memory" : "Not Unified: CUDA Managed Memory";
```

### Ef712143253f8f2b7db98d45a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-disagg_prefill.md#L24-L32

```text
- **NixlConnector**: refer to <gh-file:tests/v1/kv_connector/nixl_integration/run_accuracy_test.sh> for the example usage of NixlConnector disaggregated prefilling which support fully async send/recv.
- **P2pNcclConnector**: refer to <gh-file:examples/online_serving/disaggregated_serving_p2p_nccl_xpyd/disagg_example_p2p_nccl_xpyd.sh> for the example usage of P2pNcclConnector disaggregated prefilling.
```

### E57a99437853406f7a0202cc5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-lora.md#L31-L50

```text
Check out <gh-file:examples/offline_inference/multilora_inference.py> for an example of how to use LoRA adapters with the async engine and how to use more advanced configuration options.
```

### Ef21de5916d0902d7b7aef21d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L33-L35

```text
Programmers can globally disable asynchronicity of kernel launches for all CUDA applications running on a system by setting the CUDA_LAUNCH_BLOCKING environment variable to 1.
This feature is provided for debugging purposes only and should not be used as a way to make production software run reliably.
Kernel launches are synchronous if hardware counters are collected via a profiler (Nsight Compute) unless concurrent kernel profiling is enabled.
```

### Efc24074d12a2fb9e19281f26

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
);
// No more references owned by this thread;
no need to call release API
cudaGraphExec_t graphExec;
cudaGraphInstantiate(&graphExec, graph, nullptr, nullptr, 0);
```

### E1f8f9760ee1945ed9c68dd30

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaGraphExecDestroy(graphExec);
// Launch is not synchronized;
the release
// will be deferred if needed
cudaStreamSynchronize(0);
// After the launch is synchronized, the remaining
// reference is released and the destructor will
```

### E21b180de346261e28a6ec32c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaUserObjectNoDestructorSync  // Acknowledge that the callback cannot be
// waited on via CUDA
);
cudaGraphRetainUserObject(
graph,
cuObject,
1,  // Number of references
cudaGraphUserObjectMove  // Transfer a reference owned by the caller (do
```

## official-026-4:oracle:oracle

CUDA 13.0.1：对asynchronous-concurrent-execution相关代码进行review时，为何不能接受“所有带Async后缀的调用都无条件异步。”作为正确性依据？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### Ed6cb6db9ada95f18e2c062f6

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#asynchronous-concurrent-execution

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

## official-026-4:bm25:retrieved

CUDA 13.0.1：对asynchronous-concurrent-execution相关代码进行review时，为何不能接受“所有带Async后缀的调用都无条件异步。”作为正确性依据？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### E9032a6c3f451b8df8c7d1f60

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L1-L3

```text
6.2.8. Asynchronous Concurrent Execution

CUDA exposes the following operations as independent tasks that can operate concurrently with one another:
```

### E5159d0d7b65c4d9cfd92c171

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L19-L21

```text
6.2.8.1.
Concurrent Execution between Host and Device
Concurrent host execution is facilitated through asynchronous library functions that return control to the host thread before the device completes the requested task.
Using asynchronous calls, many device operations can be queued up together to be executed by the CUDA driver when appropriate device resources are available.
```

### E76166ab4dfae9b45ee1e6e9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L33-L35

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

### Efac75510f85dcc3f0516bb3d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L17-L17

```text
The level of concurrency achieved between these operations will depend on the feature set and compute capability of the device as described below.
```

### Ec5b93f855e95a5da9d7c5a60

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L25-L31

```text
Memory copies within a single device’s memory;

Memory copies from host to device of a memory block of 64 KB or less;

Memory copies performed by functions that are suffixed with Async;

Memory set function calls.
```

### E012e636b7371e57a74efe4a5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L19-L21

```text
This relieves the host thread of much of the responsibility to manage the device, leaving it free for other tasks.
The following device operations are asynchronous with respect to the host:
```

### Ef21de5916d0902d7b7aef21d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L33-L35

```text
Programmers can globally disable asynchronicity of kernel launches for all CUDA applications running on a system by setting the CUDA_LAUNCH_BLOCKING environment variable to 1.
This feature is provided for debugging purposes only and should not be used as a way to make production software run reliably.
Kernel launches are synchronous if hardware counters are collected via a profiler (Nsight Compute) unless concurrent kernel profiling is enabled.
```

## official-026-4:dense:retrieved

CUDA 13.0.1：对asynchronous-concurrent-execution相关代码进行review时，为何不能接受“所有带Async后缀的调用都无条件异步。”作为正确性依据？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### E9032a6c3f451b8df8c7d1f60

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L1-L3

```text
6.2.8. Asynchronous Concurrent Execution

CUDA exposes the following operations as independent tasks that can operate concurrently with one another:
```

### E0be60d2e48c2378da5b289c2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L250-L254

```text
In either case, if previous launches are not synchronized, any references which would be released are held until the launches have finished executing.
There is not currently a mechanism to wait on user object destructors via a CUDA API.
Users may signal a synchronization object manually from the destructor code.
In addition, it is not legal to call CUDA APIs from the destructor, similar to the restriction on cudaLaunchHostFunc.
```

### E83e7405f8a45f0c79c37aade

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1326-L1332

```text
cudaStreamSynchronize() and cudaStreamQuery() (provided it returns cudaSuccess and not cudaErrorNotReady) where the specified stream is the only stream still executing on the GPU;
cudaEventSynchronize() and cudaEventQuery() in cases where the specified event is not followed by any device work;
as well as uses of cudaMemcpy() and cudaMemset() that are documented as being fully synchronous with respect to the host.
```

### Ec6c6044cb73387a74449ccb2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L278-L278

```text
A node whose function originally did not use CUDA dynamic parallelism cannot be updated to a function which uses CUDA dynamic parallelism.
```

### Ee0cfed13f71c6bc53141e3fa

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L161-L167

```text
It is therefore also invalid to call synchronous APIs in this case.
Synchronous APIs, such as cudaMemcpy(), enqueue work to the legacy stream and synchronize it before returning.
```

### E0d8a2bd0465510e0c8bd3d9d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L250-L254

```text
References owned by graphs in child graph nodes are associated to the child graphs, not the parents.
If a child graph is updated or deleted, the references change accordingly.
If an executable graph or child graph is updated with cudaGraphExecUpdate or cudaGraphExecChildGraphNodeSetParams, the references in the new source graph are cloned and replace the references in the target graph.
```

### E0d8550669f2f21e571687c61

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L250-L254

```text
This is to avoid blocking a CUDA internal shared thread and preventing forward progress.
It is legal to signal another thread to perform an API call, if the dependency is one way and the thread doing the call cannot block forward progress of CUDA work.
User objects are created with cudaUserObjectCreate, which is a good starting point to browse related APIs.
```

### Eb3d67347a293eb773fb9af27

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1326-L1332

```text
This aligns with the CUDA programming model, which specifies that a kernel can run at any time following a launch and is not guaranteed to have finished until the host issues a synchronization call.
Any function call that logically guarantees the GPU completes its work is valid.
This includes cudaDeviceSynchronize();
```

### Ebc81bb294818402ec2154b33

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1326-L1332

```text
24.3.2.4.2.
Explicit Synchronization and Logical GPU Activity
```

## official-026-4:hybrid:retrieved

CUDA 13.0.1：对asynchronous-concurrent-execution相关代码进行review时，为何不能接受“所有带Async后缀的调用都无条件异步。”作为正确性依据？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### E9032a6c3f451b8df8c7d1f60

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L1-L3

```text
6.2.8. Asynchronous Concurrent Execution

CUDA exposes the following operations as independent tasks that can operate concurrently with one another:
```

### E5159d0d7b65c4d9cfd92c171

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L19-L21

```text
6.2.8.1.
Concurrent Execution between Host and Device
Concurrent host execution is facilitated through asynchronous library functions that return control to the host thread before the device completes the requested task.
Using asynchronous calls, many device operations can be queued up together to be executed by the CUDA driver when appropriate device resources are available.
```

### Ec8a524a3eb303e197f102d50

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L11-L15

```text
8.2.2. Device Level

At a lower level, the application should maximize parallel execution between the multiprocessors of a device.

Multiple kernels can execute concurrently on a device, so maximum utilization can also be achieved by using streams to enable enough kernels to execute concurrently as described in Asynchronous Concurrent Execution.
```

### E0be60d2e48c2378da5b289c2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L250-L254

```text
In either case, if previous launches are not synchronized, any references which would be released are held until the launches have finished executing.
There is not currently a mechanism to wait on user object destructors via a CUDA API.
Users may signal a synchronization object manually from the destructor code.
In addition, it is not legal to call CUDA APIs from the destructor, similar to the restriction on cudaLaunchHostFunc.
```

### E83e7405f8a45f0c79c37aade

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1326-L1332

```text
cudaStreamSynchronize() and cudaStreamQuery() (provided it returns cudaSuccess and not cudaErrorNotReady) where the specified stream is the only stream still executing on the GPU;
cudaEventSynchronize() and cudaEventQuery() in cases where the specified event is not followed by any device work;
as well as uses of cudaMemcpy() and cudaMemset() that are documented as being fully synchronous with respect to the host.
```

### E012e636b7371e57a74efe4a5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L19-L21

```text
This relieves the host thread of much of the responsibility to manage the device, leaving it free for other tasks.
The following device operations are asynchronous with respect to the host:
```

### E0d8a2bd0465510e0c8bd3d9d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L250-L254

```text
References owned by graphs in child graph nodes are associated to the child graphs, not the parents.
If a child graph is updated or deleted, the references change accordingly.
If an executable graph or child graph is updated with cudaGraphExecUpdate or cudaGraphExecChildGraphNodeSetParams, the references in the new source graph are cloned and replace the references in the target graph.
```

### E0d8550669f2f21e571687c61

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L250-L254

```text
This is to avoid blocking a CUDA internal shared thread and preventing forward progress.
It is legal to signal another thread to perform an API call, if the dependency is one way and the thread doing the call cannot block forward progress of CUDA work.
```

## official-026-4:hybrid_rerank:retrieved

CUDA 13.0.1：对asynchronous-concurrent-execution相关代码进行review时，为何不能接受“所有带Async后缀的调用都无条件异步。”作为正确性依据？

必要要点：涉及未锁页主机内存时，Async拷贝也可能同步。

禁止误读：所有带Async后缀的调用都无条件异步。

```json
null
```

实际输入证据：

### E76166ab4dfae9b45ee1e6e9f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L33-L35

```text
Async memory copies might also be synchronous if they involve host memory that is not page-locked.
```

### E7df00d40381261b9b7ecab9c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-page-locked-host-memory.md#L45-L51

```text
Since mapped page-locked memory is shared between host and device however, the application must synchronize memory accesses using streams or events (see Asynchronous Concurrent Execution) to avoid any potential read-after-write, write-after-read, or write-after-write hazards.
```

### E5159d0d7b65c4d9cfd92c171

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L19-L21

```text
6.2.8.1.
Concurrent Execution between Host and Device
Concurrent host execution is facilitated through asynchronous library functions that return control to the host thread before the device completes the requested task.
Using asynchronous calls, many device operations can be queued up together to be executed by the CUDA driver when appropriate device resources are available.
```

### E052676d9f8d3c0d69999e8fb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-streams.md#L73-L82

```text
If the
code is rewritten the following way (and assuming the device supports overlap of data transfer and kernel execution)
```

### Ec6c6044cb73387a74449ccb2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L278-L278

```text
A node whose function originally did not use CUDA dynamic parallelism cannot be updated to a function which uses CUDA dynamic parallelism.
```

### Ef21de5916d0902d7b7aef21d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L33-L35

```text
Programmers can globally disable asynchronicity of kernel launches for all CUDA applications running on a system by setting the CUDA_LAUNCH_BLOCKING environment variable to 1.
This feature is provided for debugging purposes only and should not be used as a way to make production software run reliably.
Kernel launches are synchronous if hardware counters are collected via a profiler (Nsight Compute) unless concurrent kernel profiling is enabled.
```

### E3bbd8261329b9e1953356637

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-page-locked-host-memory.md#L45-L51

```text
To be able to retrieve the device pointer to any mapped page-locked memory, page-locked memory mapping must be enabled by calling cudaSetDeviceFlags() with the cudaDeviceMapHost flag before any other CUDA call is performed.
Otherwise, cudaHostGetDevicePointer() will return an error.
cudaHostGetDevicePointer() also returns an error if the device does not support mapped page-locked host memory.
```

### Ebfe9b4c1fb7ff38fbee7a1c1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-page-locked-host-memory.md#L45-L51

```text
Applications may query this capability by checking the canMapHostMemory device property (see Device Enumeration), which is equal to 1 for devices that support mapped page-locked host memory.
Note that atomic functions (see Atomic Functions) operating on mapped page-locked memory are not atomic from the point of view of the host or other devices.
```

### E012e636b7371e57a74efe4a5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L19-L21

```text
This relieves the host thread of much of the responsibility to manage the device, leaving it free for other tasks.
The following device operations are asynchronous with respect to the host:
```

### Ee245d3ef5649db4ae109ddb6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-streams.md#L73-L82

```text
For example, on devices that do not support concurrent data transfers, the two streams of the code sample of Creation and Destruction of Streams
```

## official-028-1:oracle:oracle

CUDA 13.0.1：CUDA Graph如何表达操作关系以及定义与执行？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### E0731fb9d096f154a155fd3e1

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#cuda-graphs

```text
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
```

## official-028-1:bm25:retrieved

CUDA 13.0.1：CUDA Graph如何表达操作关系以及定义与执行？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### E79b875211cebcae361a00b29

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| None |
| `--cuda-graph-bs` | Set the list of batch sizes for cuda graph.
| None |
| `--disable-cuda-graph` | Disable cuda graph.
```

### Ee22117982614a85e52e421a8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--disable-cuda-graph-padding` | Disable cuda graph when padding is needed.
Still uses cuda graph when padding is not needed.
```

### E8df193b2059c7c54dbf85565

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L217-L217

```text
cudaGraph_t graph;  // Preexisting graph
```

### E4f9bd39164386af01795ac05

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--cuda-graph-max-bs` | Set the maximum batch size for cuda graph.
It will extend the cuda graph capture batch size to this value.
```

### E7f8cbf6083add496e80e0296

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-attention_backend.md#L84-L104

```text
2.
Run with cuda graph.
It has two phases (capture and replay) and you need to implement three functions
- init_cuda_graph_state
```

### E28be820d1fc3d377411a70ab

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
## Optimization/debug options
| Arguments | Description | Defaults |
|-----------|-------------|----------|
| `--disable-radix-cache` | Disable RadixAttention for prefix caching.
```

### Edbb36dd8137ded494920093d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--enable-profile-cuda-graph` | Enable profiling of cuda graph capture.
| False |
| `--enable-nccl-nvls` | Enable NCCL NVLS for prefill heavy requests when available.
```

### E50ac24f52595a5b43e045c1e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--enable-symm-mem` | Enable NCCL symmetric memory for fast collectives.
| False |
| `--enable-tokenizer-batch-encode` | Enable batch tokenization for improved performance when processing multiple text inputs.
Do not use with image inputs, pre-tokenized input_ids, or input_embeds.
```

### Ea2c77c0f4f7a9f01496e6171

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--disable-outlines-disk-cache` | Disable disk cache of outlines to avoid possible crashes related to file system or high concurrency.
```

### E95cbf95289d6c0e07c82e949

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--disable-custom-all-reduce` | Disable the custom all-reduce kernel and fall back to NCCL.
| False |
```

### E469acb5f6e1af2778f7f85d0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| `--enable-mscclpp` | Enable using mscclpp for small messages for all-reduce kernel and fall back to NCCL.
| False |
```

### E178b5bb8b20bc415926ae0dd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| `--disable-overlap-schedule` | Disable the overlap scheduler, which overlaps the CPU scheduler with GPU model worker.
```

### Ecce4eff7400ceef59be19594

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--enable-mixed-chunk` | Enabling mixing prefill and decode in a batch when using chunked prefill.
| False |
```

### E44c880aca90a2a66371253ed

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
Currently DeepSeek-V2 and Qwen 2/3 MoE models are supported.
| False |
```

## official-028-1:dense:retrieved

CUDA 13.0.1：CUDA Graph如何表达操作关系以及定义与执行？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### Ebc459d1dffa94905abd1e4d2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
6.2.8.7.
CUDA Graphs
CUDA Graphs present a new model for work submission in CUDA.
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
This allows a graph to be defined once and then launched repeatedly.
```

### Ed3ecc8a3b383e51f314ee343

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L781-L811

```text
Starting in CUDA 12.8, IF nodes can also have an optional second body graph which is executed once when the node is executed if the condition value is zero.
void graphSetup() {
cudaGraph_t graph;
cudaGraphExec_t graphExec;
cudaGraphNode_t node;
void *kernelArgs[1];
int value = 1;
```

### E7f8cbf6083add496e80e0296

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-attention_backend.md#L84-L104

```text
2.
Run with cuda graph.
It has two phases (capture and replay) and you need to implement three functions
- init_cuda_graph_state
```

### E3e3b76169249c4aa5028d43d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L306-L306

```text
It is not possible to update a cudaGraphExec_t with a cudaGraph_t if the cudaGraph_t is currently instantiated as a different cudaGraphExec_t.
```

### Ee22117982614a85e52e421a8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--disable-cuda-graph-padding` | Disable cuda graph when padding is needed.
Still uses cuda graph when padding is not needed.
```

### Ebde76133f3b80c0292f8021e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
Separating out the definition of a graph from its execution enables a number of optimizations: first, CPU launch costs are reduced compared to streams, because much of the setup is done in advance;
second, presenting the whole workflow to CUDA enables optimizations which might not be possible with the piecewise work submission mechanism of streams.
```

### E85a652bc6dcffe9619cdbc33

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
To see the optimizations possible with graphs, consider what happens in a stream: when you place a kernel into a stream, the host driver performs a sequence of operations in preparation for the execution of the kernel on the GPU.
These operations, necessary for setting up and launching the kernel, are an overhead cost which must be paid for each kernel that is issued.
```

### Eb842a9a30ddb7416d9660673

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
For a GPU kernel with a short execution time, this overhead cost can be a significant fraction of the overall end-to-end execution time.
Work submission using graphs is separated into three distinct stages: definition, instantiation, and execution.
```

### E69abe81548aa911cf96dc62c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L781-L811

```text
cudaGraphCreate(&graph, 0);
cudaGraphConditionalHandle handle;
cudaGraphConditionalHandleCreate(&handle, graph);
// Use a kernel upstream of the conditional to set the handle value
cudaGraphNodeParams params = { cudaGraphNodeTypeKernel };
params.kernel.func = (void *)setHandle;
params.kernel.gridDim.x = params.kernel.gridDim.y = params.kernel.gridDim.z = 1;
```

### E79b875211cebcae361a00b29

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| None |
```

## official-028-1:hybrid:retrieved

CUDA 13.0.1：CUDA Graph如何表达操作关系以及定义与执行？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### Ee22117982614a85e52e421a8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--disable-cuda-graph-padding` | Disable cuda graph when padding is needed.
Still uses cuda graph when padding is not needed.
```

### E7f8cbf6083add496e80e0296

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-attention_backend.md#L84-L104

```text
2.
Run with cuda graph.
It has two phases (capture and replay) and you need to implement three functions
- init_cuda_graph_state
```

### Ebc459d1dffa94905abd1e4d2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
6.2.8.7.
CUDA Graphs
CUDA Graphs present a new model for work submission in CUDA.
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
This allows a graph to be defined once and then launched repeatedly.
```

### E79b875211cebcae361a00b29

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| None |
| `--cuda-graph-bs` | Set the list of batch sizes for cuda graph.
| None |
| `--disable-cuda-graph` | Disable cuda graph.
```

### E8df193b2059c7c54dbf85565

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L217-L217

```text
cudaGraph_t graph;  // Preexisting graph
```

### E4f9bd39164386af01795ac05

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--cuda-graph-max-bs` | Set the maximum batch size for cuda graph.
It will extend the cuda graph capture batch size to this value.
```

### Edbb36dd8137ded494920093d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--enable-profile-cuda-graph` | Enable profiling of cuda graph capture.
| False |
| `--enable-nccl-nvls` | Enable NCCL NVLS for prefill heavy requests when available.
```

### E28be820d1fc3d377411a70ab

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
## Optimization/debug options
| Arguments | Description | Defaults |
|-----------|-------------|----------|
| `--disable-radix-cache` | Disable RadixAttention for prefix caching.
```

### E50ac24f52595a5b43e045c1e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--enable-symm-mem` | Enable NCCL symmetric memory for fast collectives.
| False |
| `--enable-tokenizer-batch-encode` | Enable batch tokenization for improved performance when processing multiple text inputs.
Do not use with image inputs, pre-tokenized input_ids, or input_embeds.
```

### Ea2c77c0f4f7a9f01496e6171

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--disable-outlines-disk-cache` | Disable disk cache of outlines to avoid possible crashes related to file system or high concurrency.
```

### E95cbf95289d6c0e07c82e949

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--disable-custom-all-reduce` | Disable the custom all-reduce kernel and fall back to NCCL.
| False |
```

### E469acb5f6e1af2778f7f85d0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| `--enable-mscclpp` | Enable using mscclpp for small messages for all-reduce kernel and fall back to NCCL.
| False |
```

### Ecce4eff7400ceef59be19594

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
```

### E78bf4aac5f54fc12b20b4c4f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
```

## official-028-1:hybrid_rerank:retrieved

CUDA 13.0.1：CUDA Graph如何表达操作关系以及定义与执行？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### Ebc459d1dffa94905abd1e4d2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
6.2.8.7.
CUDA Graphs
CUDA Graphs present a new model for work submission in CUDA.
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
This allows a graph to be defined once and then launched repeatedly.
```

### Ed4375469fcf99592187cbc41

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-attention_backend.md#L84-L104

```text
- It will be called once during life time
- Create all common shared buffers
- init_forward_metadata_capture_cuda_graph
- It will be called before capturing a cuda graph
- It is similar to init_forward_metadata but write the medatada to some pre-defined buffers
- init_forward_metadata_replay_cuda_graph
- It will be called before replaying a cuda graph
- This function is in the critical path and needs to be fast
```

### E2aac9fb4423f0d9c4fe62f91

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L213-L213

```text
When a reference is associated to a CUDA graph, CUDA will manage the graph operations automatically. A cloned cudaGraph_t retains a copy of every reference owned by the source cudaGraph_t, with the same multiplicity. An instantiated cudaGraphExec_t retains a copy of every reference in the source cudaGraph_t. When a cudaGraphExec_t is destroyed without being synchronized, the references are retained until the execution is completed.
```

### E307e023a919e38e0828ab73e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L693-L701

```text
If cudaGraphCondAssignDefault is specified when the handle is created, the condition value will be initialized to the specified default at the beginning of each graph execution.
If this flag is not provided, the condition value is undefined at the start of each graph execution and code should not assume that the condition value persists across executions.
```

### Ed3ecc8a3b383e51f314ee343

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L781-L811

```text
Starting in CUDA 12.8, IF nodes can also have an optional second body graph which is executed once when the node is executed if the condition value is zero.
void graphSetup() {
cudaGraph_t graph;
cudaGraphExec_t graphExec;
cudaGraphNode_t node;
void *kernelArgs[1];
int value = 1;
```

### Ebde76133f3b80c0292f8021e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
Separating out the definition of a graph from its execution enables a number of optimizations: first, CPU launch costs are reduced compared to streams, because much of the setup is done in advance;
second, presenting the whole workflow to CUDA enables optimizations which might not be possible with the piecewise work submission mechanism of streams.
```

### E85a652bc6dcffe9619cdbc33

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
To see the optimizations possible with graphs, consider what happens in a stream: when you place a kernel into a stream, the host driver performs a sequence of operations in preparation for the execution of the kernel on the GPU.
These operations, necessary for setting up and launching the kernel, are an overhead cost which must be paid for each kernel that is issued.
```

### Eb842a9a30ddb7416d9660673

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
For a GPU kernel with a short execution time, this overhead cost can be a significant fraction of the overall end-to-end execution time.
```

## official-028-2:oracle:oracle

CUDA 13.0.1：审核Graph节点依赖代码时，应怎样区分图定义与实际执行？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### E0731fb9d096f154a155fd3e1

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#cuda-graphs

```text
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
```

## official-028-2:bm25:retrieved

CUDA 13.0.1：审核Graph节点依赖代码时，应怎样区分图定义与实际执行？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### E79b875211cebcae361a00b29

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| None |
| `--cuda-graph-bs` | Set the list of batch sizes for cuda graph.
| None |
| `--disable-cuda-graph` | Disable cuda graph.
```

### Ee22117982614a85e52e421a8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--disable-cuda-graph-padding` | Disable cuda graph when padding is needed.
Still uses cuda graph when padding is not needed.
```

### E8df193b2059c7c54dbf85565

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L217-L217

```text
cudaGraph_t graph;  // Preexisting graph
```

### E4f9bd39164386af01795ac05

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--cuda-graph-max-bs` | Set the maximum batch size for cuda graph.
It will extend the cuda graph capture batch size to this value.
```

### E7f8cbf6083add496e80e0296

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-attention_backend.md#L84-L104

```text
2.
Run with cuda graph.
It has two phases (capture and replay) and you need to implement three functions
- init_cuda_graph_state
```

### E28be820d1fc3d377411a70ab

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
## Optimization/debug options
| Arguments | Description | Defaults |
|-----------|-------------|----------|
| `--disable-radix-cache` | Disable RadixAttention for prefix caching.
```

### Edbb36dd8137ded494920093d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--enable-profile-cuda-graph` | Enable profiling of cuda graph capture.
| False |
| `--enable-nccl-nvls` | Enable NCCL NVLS for prefill heavy requests when available.
```

### E50ac24f52595a5b43e045c1e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--enable-symm-mem` | Enable NCCL symmetric memory for fast collectives.
| False |
| `--enable-tokenizer-batch-encode` | Enable batch tokenization for improved performance when processing multiple text inputs.
Do not use with image inputs, pre-tokenized input_ids, or input_embeds.
```

### Ea2c77c0f4f7a9f01496e6171

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--disable-outlines-disk-cache` | Disable disk cache of outlines to avoid possible crashes related to file system or high concurrency.
```

### E95cbf95289d6c0e07c82e949

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--disable-custom-all-reduce` | Disable the custom all-reduce kernel and fall back to NCCL.
| False |
```

### E469acb5f6e1af2778f7f85d0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| `--enable-mscclpp` | Enable using mscclpp for small messages for all-reduce kernel and fall back to NCCL.
| False |
```

### E178b5bb8b20bc415926ae0dd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| `--disable-overlap-schedule` | Disable the overlap scheduler, which overlaps the CPU scheduler with GPU model worker.
```

### Ecce4eff7400ceef59be19594

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--enable-mixed-chunk` | Enabling mixing prefill and decode in a batch when using chunked prefill.
| False |
```

### E44c880aca90a2a66371253ed

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
Currently DeepSeek-V2 and Qwen 2/3 MoE models are supported.
| False |
```

## official-028-2:dense:retrieved

CUDA 13.0.1：审核Graph节点依赖代码时，应怎样区分图定义与实际执行？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### Ed3ecc8a3b383e51f314ee343

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L781-L811

```text
Starting in CUDA 12.8, IF nodes can also have an optional second body graph which is executed once when the node is executed if the condition value is zero.
void graphSetup() {
cudaGraph_t graph;
cudaGraphExec_t graphExec;
cudaGraphNode_t node;
void *kernelArgs[1];
int value = 1;
```

### E603944b00ee8332ec2e05581

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L81-L102

```text
cudaFree(d_A);
cudaFree(d_B);
cudaFree(d_C);
// Free host memory
...
}
Linear memory can also be allocated through cudaMallocPitch() and cudaMalloc3D().
```

### Ecd863ff040dcc19aaeab6d42

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L422-L430

```text
6.2.8.7.6.
Using Graph APIs
cudaGraph_t objects are not thread-safe.
It is the responsibility of the user to ensure that multiple threads do not concurrently access the same cudaGraph_t.
A cudaGraphExec_t cannot run concurrently with itself.
A launch of a cudaGraphExec_t will be ordered after previous launches of the same executable graph.
Graph execution is done in streams for ordering with other asynchronous work.
```

### E1f8f9760ee1945ed9c68dd30

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaGraphExecDestroy(graphExec);
// Launch is not synchronized;
the release
// will be deferred if needed
cudaStreamSynchronize(0);
// After the launch is synchronized, the remaining
// reference is released and the destructor will
```

### Eb532c7ce2c59483f5b05d544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L827-L849

```text
{
static int count = 10;
cudaGraphSetConditional(handle, --count ?
1 : 0);
}
void graphSetup() {
cudaGraph_t graph;
cudaGraphExec_t graphExec;
cudaGraphNode_t node;
void *kernelArgs[1];
```

### E69abe81548aa911cf96dc62c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L781-L811

```text
cudaGraphCreate(&graph, 0);
cudaGraphConditionalHandle handle;
cudaGraphConditionalHandleCreate(&handle, graph);
// Use a kernel upstream of the conditional to set the handle value
cudaGraphNodeParams params = { cudaGraphNodeTypeKernel };
params.kernel.func = (void *)setHandle;
params.kernel.gridDim.x = params.kernel.gridDim.y = params.kernel.gridDim.z = 1;
params.kernel.blockDim.x = params.kernel.blockDim.y = params.kernel.blockDim.z = 1;
```

### E817f413c9f4cf515a61a1abb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L781-L811

```text
params.kernel.kernelParams = kernelArgs;
kernelArgs[0] = &handle;
cudaGraphAddNode(&node, graph, NULL, NULL, 0, &params);
cudaGraphNodeParams cParams = { cudaGraphNodeTypeConditional };
cParams.conditional.handle = handle;
cParams.conditional.type   = cudaGraphCondTypeIf;
cParams.conditional.size   = 2;
// Note that size is now set to '2'
```

### Eb7a7863d0f600c92979d79b0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L781-L811

```text
cudaGraphAddNode(&node, graph, &node, NULL, 1, &cParams);
cudaGraph_t ifBodyGraph = cParams.conditional.phGraph_out[0];
cudaGraph_t elseBodyGraph = cParams.conditional.phGraph_out[1];
```

## official-028-2:hybrid:retrieved

CUDA 13.0.1：审核Graph节点依赖代码时，应怎样区分图定义与实际执行？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### Ee22117982614a85e52e421a8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--disable-cuda-graph-padding` | Disable cuda graph when padding is needed.
Still uses cuda graph when padding is not needed.
```

### E4f9bd39164386af01795ac05

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--cuda-graph-max-bs` | Set the maximum batch size for cuda graph.
It will extend the cuda graph capture batch size to this value.
```

### E79b875211cebcae361a00b29

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| None |
| `--cuda-graph-bs` | Set the list of batch sizes for cuda graph.
| None |
| `--disable-cuda-graph` | Disable cuda graph.
```

### E2ebc08fd5ff6b619d38e64df

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
// Will retain a
// new reference
cudaGraphDestroy(graph);
// graphExec still owns a reference
cudaGraphLaunch(graphExec, 0);
// Async launch has access to the user objects
```

### E770f1c8ef4ab527b07666d9a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-attention_backend.md#L84-L104

```text
1.
Run without cuda graph.
Support the two forward functions
- forward_extend
- Will be used for prefill, prefill with KV cache, and target verification
- It will be called once per layer
- forward_decode
- Will be used for normal decode, and draft decode
- It will be called once per layer
```

### E28be820d1fc3d377411a70ab

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
## Optimization/debug options
| Arguments | Description | Defaults |
|-----------|-------------|----------|
| `--disable-radix-cache` | Disable RadixAttention for prefix caching.
```

### Edbb36dd8137ded494920093d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--enable-profile-cuda-graph` | Enable profiling of cuda graph capture.
| False |
| `--enable-nccl-nvls` | Enable NCCL NVLS for prefill heavy requests when available.
```

### E50ac24f52595a5b43e045c1e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--enable-symm-mem` | Enable NCCL symmetric memory for fast collectives.
| False |
| `--enable-tokenizer-batch-encode` | Enable batch tokenization for improved performance when processing multiple text inputs.
Do not use with image inputs, pre-tokenized input_ids, or input_embeds.
```

### Ea2c77c0f4f7a9f01496e6171

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--disable-outlines-disk-cache` | Disable disk cache of outlines to avoid possible crashes related to file system or high concurrency.
```

### E95cbf95289d6c0e07c82e949

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--disable-custom-all-reduce` | Disable the custom all-reduce kernel and fall back to NCCL.
| False |
```

### E469acb5f6e1af2778f7f85d0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| `--enable-mscclpp` | Enable using mscclpp for small messages for all-reduce kernel and fall back to NCCL.
| False |
```

### E178b5bb8b20bc415926ae0dd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| `--disable-overlap-schedule` | Disable the overlap scheduler, which overlaps the CPU scheduler with GPU model worker.
```

### Ecce4eff7400ceef59be19594

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
```

## official-028-2:hybrid_rerank:retrieved

CUDA 13.0.1：审核Graph节点依赖代码时，应怎样区分图定义与实际执行？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### Ebc459d1dffa94905abd1e4d2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
6.2.8.7.
CUDA Graphs
CUDA Graphs present a new model for work submission in CUDA.
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
This allows a graph to be defined once and then launched repeatedly.
```

### Eb532c7ce2c59483f5b05d544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L827-L849

```text
{
static int count = 10;
cudaGraphSetConditional(handle, --count ?
1 : 0);
}
void graphSetup() {
cudaGraph_t graph;
cudaGraphExec_t graphExec;
cudaGraphNode_t node;
void *kernelArgs[1];
```

### E307e023a919e38e0828ab73e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L693-L701

```text
If cudaGraphCondAssignDefault is specified when the handle is created, the condition value will be initialized to the specified default at the beginning of each graph execution.
If this flag is not provided, the condition value is undefined at the start of each graph execution and code should not assume that the condition value persists across executions.
```

### E4c17d0251633bbb1515b5d53

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L851-L878

```text
cudaGraphLaunch(graphExec, 0);
cudaDeviceSynchronize();
cudaGraphExecDestroy(graphExec);
cudaGraphDestroy(graph);
```

### E1f8f9760ee1945ed9c68dd30

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
cudaGraphExecDestroy(graphExec);
// Launch is not synchronized;
the release
// will be deferred if needed
cudaStreamSynchronize(0);
// After the launch is synchronized, the remaining
// reference is released and the destructor will
```

### Ebde76133f3b80c0292f8021e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
Separating out the definition of a graph from its execution enables a number of optimizations: first, CPU launch costs are reduced compared to streams, because much of the setup is done in advance;
second, presenting the whole workflow to CUDA enables optimizations which might not be possible with the piecewise work submission mechanism of streams.
```

### E85a652bc6dcffe9619cdbc33

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
To see the optimizations possible with graphs, consider what happens in a stream: when you place a kernel into a stream, the host driver performs a sequence of operations in preparation for the execution of the kernel on the GPU.
These operations, necessary for setting up and launching the kernel, are an overhead cost which must be paid for each kernel that is issued.
```

### Eb842a9a30ddb7416d9660673

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
For a GPU kernel with a short execution time, this overhead cost can be a significant fraction of the overall end-to-end execution time.
Work submission using graphs is separated into three distinct stages: definition, instantiation, and execution.
```

### E6b29543582e526856e3d1fcb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L827-L849

```text
The handle
is created using cudaGraphCondAssignDefault to avoid the need for an upstream kernel.
The body of the
conditional is populated using the graph API.
__global__ void loopKernel(cudaGraphConditionalHandle handle)
```

### Efc24074d12a2fb9e19281f26

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L219-L248

```text
);
```

## official-028-3:oracle:oracle

CUDA 13.0.1：排查该主题时，有人声称“CUDA Graph只是把相互依赖的kernel无条件同时启动。”，根据文档这个说法哪里需要纠正？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### E0731fb9d096f154a155fd3e1

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#cuda-graphs

```text
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
```

## official-028-3:bm25:retrieved

CUDA 13.0.1：排查该主题时，有人声称“CUDA Graph只是把相互依赖的kernel无条件同时启动。”，根据文档这个说法哪里需要纠正？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### Eaa57126c7d84fb84fbf9dcd5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L450-L456

```text
The graph’s nodes must all reside on a single device.

The graph can only contain kernel nodes, memcpy nodes, memset nodes, and child graph nodes.

Kernel nodes:

Use of CUDA Dynamic Parallelism by kernels in the graph is not permitted.
```

### Ebc459d1dffa94905abd1e4d2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
6.2.8.7.
CUDA Graphs
CUDA Graphs present a new model for work submission in CUDA.
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
This allows a graph to be defined once and then launched repeatedly.
```

### Ebb2a333d6adf1670fd881766

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L147-L155

```text
6.2.8.6.3.
Use in CUDA Graphs
Programmatic Dependent Launch can be used in CUDA Graphs via stream capture or
directly via edge data.
To program this feature in a CUDA Graph with edge data, use a cudaGraphDependencyType
value of cudaGraphDependencyTypeProgrammatic on an edge connecting two kernel nodes.
This edge type makes the upstream kernel
visible to a cudaGridDependencySynchronize() in the downstream kernel.
```

### E01cf2b5da014c07af055ed1b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L703-L715

```text
6.2.8.7.8.2. Condtional Node Body Graph Requirements

General requirements:

The graph’s nodes must all reside on a single device.

The graph can only contain kernel nodes, empty nodes, memcpy nodes, memset nodes, child graph nodes, and conditional nodes.

Kernel nodes:

Use of CUDA Dynamic Parallelism or Device Graph Launch by kernels in the graph is not permitted.

Cooperative launches are permitted so long as MPS is not in use.
```

### E79b875211cebcae361a00b29

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| None |
| `--cuda-graph-bs` | Set the list of batch sizes for cuda graph.
| None |
| `--disable-cuda-graph` | Disable cuda graph.
```

### Ebde76133f3b80c0292f8021e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
Separating out the definition of a graph from its execution enables a number of optimizations: first, CPU launch costs are reduced compared to streams, because much of the setup is done in advance;
second, presenting the whole workflow to CUDA enables optimizations which might not be possible with the piecewise work submission mechanism of streams.
```

### E85a652bc6dcffe9619cdbc33

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
To see the optimizations possible with graphs, consider what happens in a stream: when you place a kernel into a stream, the host driver performs a sequence of operations in preparation for the execution of the kernel on the GPU.
These operations, necessary for setting up and launching the kernel, are an overhead cost which must be paid for each kernel that is issued.
```

### Eb842a9a30ddb7416d9660673

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
For a GPU kernel with a short execution time, this overhead cost can be a significant fraction of the overall end-to-end execution time.
Work submission using graphs is separated into three distinct stages: definition, instantiation, and execution.
```

### E4f9bd39164386af01795ac05

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
```

## official-028-3:dense:retrieved

CUDA 13.0.1：排查该主题时，有人声称“CUDA Graph只是把相互依赖的kernel无条件同时启动。”，根据文档这个说法哪里需要纠正？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### Ed3ecc8a3b383e51f314ee343

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L781-L811

```text
Starting in CUDA 12.8, IF nodes can also have an optional second body graph which is executed once when the node is executed if the condition value is zero.
void graphSetup() {
cudaGraph_t graph;
cudaGraphExec_t graphExec;
cudaGraphNode_t node;
void *kernelArgs[1];
int value = 1;
```

### Ea798b961e633d1b58b818923

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L37-L45

```text
A kernel from one CUDA context cannot execute concurrently with a kernel from another CUDA context.
The GPU may time slice to provide forward progress to each context.
If a user wants to run kernels from multiple process simultaneously on the SM, one must enable MPS.
Kernels that use many textures or a large amount of local memory are less likely to execute concurrently with other kernels.
```

### Ed75d83f7528659779b8ad8a4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L126-L145

```text
The CUDA driver can launch the secondary kernel when all primary thread blocks have launched and executed
cudaTriggerProgrammaticLaunchCompletion.
If the primary kernel doesn’t execute the trigger, it implicitly occurs after
all thread blocks in the primary kernel exit.
In either case, the secondary thread blocks might launch
before data written by the primary kernel is visible.
```

### Ee22117982614a85e52e421a8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--disable-cuda-graph-padding` | Disable cuda graph when padding is needed.
Still uses cuda graph when padding is not needed.
```

### Eb3d67347a293eb773fb9af27

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1326-L1332

```text
This aligns with the CUDA programming model, which specifies that a kernel can run at any time following a launch and is not guaranteed to have finished until the host issues a synchronization call.
Any function call that logically guarantees the GPU completes its work is valid.
This includes cudaDeviceSynchronize();
```

### E69abe81548aa911cf96dc62c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L781-L811

```text
cudaGraphCreate(&graph, 0);
cudaGraphConditionalHandle handle;
cudaGraphConditionalHandleCreate(&handle, graph);
// Use a kernel upstream of the conditional to set the handle value
cudaGraphNodeParams params = { cudaGraphNodeTypeKernel };
params.kernel.func = (void *)setHandle;
params.kernel.gridDim.x = params.kernel.gridDim.y = params.kernel.gridDim.z = 1;
params.kernel.blockDim.x = params.kernel.blockDim.y = params.kernel.blockDim.z = 1;
```

### E817f413c9f4cf515a61a1abb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L781-L811

```text
params.kernel.kernelParams = kernelArgs;
kernelArgs[0] = &handle;
cudaGraphAddNode(&node, graph, NULL, NULL, 0, &params);
cudaGraphNodeParams cParams = { cudaGraphNodeTypeConditional };
cParams.conditional.handle = handle;
cParams.conditional.type   = cudaGraphCondTypeIf;
cParams.conditional.size   = 2;
// Note that size is now set to '2'
```

### Eb7a7863d0f600c92979d79b0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L781-L811

```text
cudaGraphAddNode(&node, graph, &node, NULL, 1, &cParams);
```

## official-028-3:hybrid:retrieved

CUDA 13.0.1：排查该主题时，有人声称“CUDA Graph只是把相互依赖的kernel无条件同时启动。”，根据文档这个说法哪里需要纠正？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### Eaa57126c7d84fb84fbf9dcd5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L450-L456

```text
The graph’s nodes must all reside on a single device.

The graph can only contain kernel nodes, memcpy nodes, memset nodes, and child graph nodes.

Kernel nodes:

Use of CUDA Dynamic Parallelism by kernels in the graph is not permitted.
```

### Ee22117982614a85e52e421a8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--disable-cuda-graph-padding` | Disable cuda graph when padding is needed.
Still uses cuda graph when padding is not needed.
```

### Ebc459d1dffa94905abd1e4d2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
6.2.8.7.
CUDA Graphs
CUDA Graphs present a new model for work submission in CUDA.
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
This allows a graph to be defined once and then launched repeatedly.
```

### Ebb2a333d6adf1670fd881766

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L147-L155

```text
6.2.8.6.3.
Use in CUDA Graphs
Programmatic Dependent Launch can be used in CUDA Graphs via stream capture or
directly via edge data.
To program this feature in a CUDA Graph with edge data, use a cudaGraphDependencyType
value of cudaGraphDependencyTypeProgrammatic on an edge connecting two kernel nodes.
This edge type makes the upstream kernel
visible to a cudaGridDependencySynchronize() in the downstream kernel.
```

### E7f07b71aee892c9c2ee5c293

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L733-L771

```text
cudaGraphCreate(&graph, 0);
cudaGraphConditionalHandle handle;
cudaGraphConditionalHandleCreate(&handle, graph);
// Use a kernel upstream of the conditional to set the handle value
cudaGraphNodeParams params = { cudaGraphNodeTypeKernel };
params.kernel.func = (void *)setHandle;
params.kernel.gridDim.x = params.kernel.gridDim.y = params.kernel.gridDim.z = 1;
params.kernel.blockDim.x = params.kernel.blockDim.y = params.kernel.blockDim.z = 1;
```

### E79b875211cebcae361a00b29

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| None |
| `--cuda-graph-bs` | Set the list of batch sizes for cuda graph.
| None |
| `--disable-cuda-graph` | Disable cuda graph.
```

### Edbb36dd8137ded494920093d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--enable-profile-cuda-graph` | Enable profiling of cuda graph capture.
| False |
| `--enable-nccl-nvls` | Enable NCCL NVLS for prefill heavy requests when available.
```

### E4f9bd39164386af01795ac05

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--cuda-graph-max-bs` | Set the maximum batch size for cuda graph.
It will extend the cuda graph capture batch size to this value.
```

### E50ac24f52595a5b43e045c1e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-server_arguments.md#L246-L284

```text
| False |
| `--enable-symm-mem` | Enable NCCL symmetric memory for fast collectives.
| False |
| `--enable-tokenizer-batch-encode` | Enable batch tokenization for improved performance when processing multiple text inputs.
Do not use with image inputs, pre-tokenized input_ids, or input_embeds.
```

## official-028-3:hybrid_rerank:retrieved

CUDA 13.0.1：排查该主题时，有人声称“CUDA Graph只是把相互依赖的kernel无条件同时启动。”，根据文档这个说法哪里需要纠正？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### Eb532c7ce2c59483f5b05d544

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L827-L849

```text
{
static int count = 10;
cudaGraphSetConditional(handle, --count ?
1 : 0);
}
void graphSetup() {
cudaGraph_t graph;
cudaGraphExec_t graphExec;
cudaGraphNode_t node;
void *kernelArgs[1];
```

### Ed773a6f7e4fddc79ed43e9fd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L126-L145

```text
As such, when the secondary kernel is configured with Programmatic Dependent Launch,
it must always use cudaGridDependencySynchronize
or other means to verify that the result data from the primary is available.
Please note that these methods provide the opportunity for the primary and secondary kernels to execute concurrently, however
this behavior is opportunistic and not guaranteed to lead to concurrent kernel execution.
```

### Ea798b961e633d1b58b818923

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L37-L45

```text
A kernel from one CUDA context cannot execute concurrently with a kernel from another CUDA context.
The GPU may time slice to provide forward progress to each context.
If a user wants to run kernels from multiple process simultaneously on the SM, one must enable MPS.
Kernels that use many textures or a large amount of local memory are less likely to execute concurrently with other kernels.
```

### Ebc459d1dffa94905abd1e4d2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
6.2.8.7.
CUDA Graphs
CUDA Graphs present a new model for work submission in CUDA.
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
This allows a graph to be defined once and then launched repeatedly.
```

### Ec3bad866abf38be06fa06f76

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L823-L827

```text
void test_extern() {
  kernel<<<1, 1>>>("extern", ext_data);
  ASSERT(cudaDeviceSynchronize() == cudaSuccess,
    "CUDA failed with '%s'", cudaGetErrorString(cudaGetLastError()));
}
```

### E6b29543582e526856e3d1fcb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L827-L849

```text
The handle
is created using cudaGraphCondAssignDefault to avoid the need for an upstream kernel.
The body of the
conditional is populated using the graph API.
__global__ void loopKernel(cudaGraphConditionalHandle handle)
```

### E03956c3897dd126a10abdebf

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L827-L849

```text
6.2.8.7.8.4.
Conditional WHILE Nodes
The body graph of a WHILE node will be executed as long as the condition is non-zero.
The condition will be
evaluated when the node is executed and after completion of the body graph.
The following diagram depicts
a 3 node graph where the middle node, B, is a conditional node:
Figure 24 Conditional WHILE Node
The following code illustrates the creation of a graph containing a WHILE conditional node.
```

### Ed75d83f7528659779b8ad8a4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L126-L145

```text
The CUDA driver can launch the secondary kernel when all primary thread blocks have launched and executed
cudaTriggerProgrammaticLaunchCompletion.
If the primary kernel doesn’t execute the trigger, it implicitly occurs after
all thread blocks in the primary kernel exit.
In either case, the secondary thread blocks might launch
before data written by the primary kernel is visible.
```

## official-028-4:oracle:oracle

CUDA 13.0.1：对cuda-graphs相关代码进行review时，为何不能接受“CUDA Graph只是把相互依赖的kernel无条件同时启动。”作为正确性依据？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### E0731fb9d096f154a155fd3e1

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#cuda-graphs

```text
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
```

## official-028-4:bm25:retrieved

CUDA 13.0.1：对cuda-graphs相关代码进行review时，为何不能接受“CUDA Graph只是把相互依赖的kernel无条件同时启动。”作为正确性依据？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### Ebc459d1dffa94905abd1e4d2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
6.2.8.7.
CUDA Graphs
CUDA Graphs present a new model for work submission in CUDA.
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
This allows a graph to be defined once and then launched repeatedly.
```

### Ebb2a333d6adf1670fd881766

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L147-L155

```text
6.2.8.6.3.
Use in CUDA Graphs
Programmatic Dependent Launch can be used in CUDA Graphs via stream capture or
directly via edge data.
To program this feature in a CUDA Graph with edge data, use a cudaGraphDependencyType
value of cudaGraphDependencyTypeProgrammatic on an edge connecting two kernel nodes.
This edge type makes the upstream kernel
visible to a cudaGridDependencySynchronize() in the downstream kernel.
```

### E5b213af7cdbdf96ffd8f03d1

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L159-L159

```text
Resulting graph edge
```

### E10d4c1a966d1b318e13ff8ba

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-conserving_memory.md#L51-L56

```text
## Reduce CUDA Graphs

By default, we optimize model inference using CUDA graphs which take up extra memory in the GPU.

!!! warning
    CUDA graph capture takes up more memory in V1 than in V0.
```

### E12256b78e20642c8d347e1e6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-conserving_memory.md#L76-L76

```text
You can disable graph capturing completely via the `enforce_eager` flag:
```

### Ebde76133f3b80c0292f8021e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
Separating out the definition of a graph from its execution enables a number of optimizations: first, CPU launch costs are reduced compared to streams, because much of the setup is done in advance;
second, presenting the whole workflow to CUDA enables optimizations which might not be possible with the piecewise work submission mechanism of streams.
```

### E85a652bc6dcffe9619cdbc33

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
To see the optimizations possible with graphs, consider what happens in a stream: when you place a kernel into a stream, the host driver performs a sequence of operations in preparation for the execution of the kernel on the GPU.
These operations, necessary for setting up and launching the kernel, are an overhead cost which must be paid for each kernel that is issued.
```

### Eb842a9a30ddb7416d9660673

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
For a GPU kernel with a short execution time, this overhead cost can be a significant fraction of the overall end-to-end execution time.
Work submission using graphs is separated into three distinct stages: definition, instantiation, and execution.
```

### Ef0405adf195e658c83b8dccf

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L147-L155

```text
This type must be used with an outgoing port of
either cudaGraphKernelNodePortLaunchCompletion or cudaGraphKernelNodePortProgrammatic.
The resulting graph equivalents for stream capture are as follows:
```

## official-028-4:dense:retrieved

CUDA 13.0.1：对cuda-graphs相关代码进行review时，为何不能接受“CUDA Graph只是把相互依赖的kernel无条件同时启动。”作为正确性依据？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### Ed3ecc8a3b383e51f314ee343

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L781-L811

```text
Starting in CUDA 12.8, IF nodes can also have an optional second body graph which is executed once when the node is executed if the condition value is zero.
void graphSetup() {
cudaGraph_t graph;
cudaGraphExec_t graphExec;
cudaGraphNode_t node;
void *kernelArgs[1];
int value = 1;
```

### Ef60380f1cc526a0aaf82f002

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-faq.md#L15-L18

```text
### CUDA Error: Illegal Memory Access Encountered
This error may result from kernel errors or out-of-memory issues:
- If it is a kernel error, resolving it may be challenging. Please file an issue on GitHub.
- If it is an out-of-memory issue, it may sometimes be reported as this error instead of "Out of Memory." Refer to the section above for guidance on avoiding OOM issues.
```

### E3e3b76169249c4aa5028d43d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L306-L306

```text
It is not possible to update a cudaGraphExec_t with a cudaGraph_t if the cudaGraph_t is currently instantiated as a different cudaGraphExec_t.
```

### E2740e3d00e632f4577074c30

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L95-L115

```text
// Initial work that should finish before starting secondary kernel
// Trigger the secondary kernel
cudaTriggerProgrammaticLaunchCompletion();
// Work that can coincide with the secondary kernel
```

### Ed773a6f7e4fddc79ed43e9fd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L126-L145

```text
As such, when the secondary kernel is configured with Programmatic Dependent Launch,
it must always use cudaGridDependencySynchronize
or other means to verify that the result data from the primary is available.
Please note that these methods provide the opportunity for the primary and secondary kernels to execute concurrently, however
this behavior is opportunistic and not guaranteed to lead to concurrent kernel execution.
```

### E69abe81548aa911cf96dc62c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L781-L811

```text
cudaGraphCreate(&graph, 0);
cudaGraphConditionalHandle handle;
cudaGraphConditionalHandleCreate(&handle, graph);
// Use a kernel upstream of the conditional to set the handle value
cudaGraphNodeParams params = { cudaGraphNodeTypeKernel };
params.kernel.func = (void *)setHandle;
params.kernel.gridDim.x = params.kernel.gridDim.y = params.kernel.gridDim.z = 1;
params.kernel.blockDim.x = params.kernel.blockDim.y = params.kernel.blockDim.z = 1;
```

### E817f413c9f4cf515a61a1abb

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L781-L811

```text
params.kernel.kernelParams = kernelArgs;
kernelArgs[0] = &handle;
cudaGraphAddNode(&node, graph, NULL, NULL, 0, &params);
cudaGraphNodeParams cParams = { cudaGraphNodeTypeConditional };
cParams.conditional.handle = handle;
cParams.conditional.type   = cudaGraphCondTypeIf;
cParams.conditional.size   = 2;
// Note that size is now set to '2'
```

### Eb7a7863d0f600c92979d79b0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L781-L811

```text
cudaGraphAddNode(&node, graph, &node, NULL, 1, &cParams);
cudaGraph_t ifBodyGraph = cParams.conditional.phGraph_out[0];
```

## official-028-4:hybrid:retrieved

CUDA 13.0.1：对cuda-graphs相关代码进行review时，为何不能接受“CUDA Graph只是把相互依赖的kernel无条件同时启动。”作为正确性依据？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### Eaa57126c7d84fb84fbf9dcd5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L450-L456

```text
The graph’s nodes must all reside on a single device.

The graph can only contain kernel nodes, memcpy nodes, memset nodes, and child graph nodes.

Kernel nodes:

Use of CUDA Dynamic Parallelism by kernels in the graph is not permitted.
```

### Ebb2a333d6adf1670fd881766

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L147-L155

```text
6.2.8.6.3.
Use in CUDA Graphs
Programmatic Dependent Launch can be used in CUDA Graphs via stream capture or
directly via edge data.
To program this feature in a CUDA Graph with edge data, use a cudaGraphDependencyType
value of cudaGraphDependencyTypeProgrammatic on an edge connecting two kernel nodes.
This edge type makes the upstream kernel
visible to a cudaGridDependencySynchronize() in the downstream kernel.
```

### Ebc459d1dffa94905abd1e4d2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
6.2.8.7.
CUDA Graphs
CUDA Graphs present a new model for work submission in CUDA.
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
This allows a graph to be defined once and then launched repeatedly.
```

### Ed3ecc8a3b383e51f314ee343

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L781-L811

```text
Starting in CUDA 12.8, IF nodes can also have an optional second body graph which is executed once when the node is executed if the condition value is zero.
void graphSetup() {
cudaGraph_t graph;
cudaGraphExec_t graphExec;
cudaGraphNode_t node;
void *kernelArgs[1];
int value = 1;
```

### Ef60380f1cc526a0aaf82f002

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-faq.md#L15-L18

```text
### CUDA Error: Illegal Memory Access Encountered
This error may result from kernel errors or out-of-memory issues:
- If it is a kernel error, resolving it may be challenging. Please file an issue on GitHub.
- If it is an out-of-memory issue, it may sometimes be reported as this error instead of "Out of Memory." Refer to the section above for guidance on avoiding OOM issues.
```

### Ef0405adf195e658c83b8dccf

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L147-L155

```text
This type must be used with an outgoing port of
either cudaGraphKernelNodePortLaunchCompletion or cudaGraphKernelNodePortProgrammatic.
The resulting graph equivalents for stream capture are as follows:
```

### Ebde76133f3b80c0292f8021e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
Separating out the definition of a graph from its execution enables a number of optimizations: first, CPU launch costs are reduced compared to streams, because much of the setup is done in advance;
second, presenting the whole workflow to CUDA enables optimizations which might not be possible with the piecewise work submission mechanism of streams.
```

### E85a652bc6dcffe9619cdbc33

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
To see the optimizations possible with graphs, consider what happens in a stream: when you place a kernel into a stream, the host driver performs a sequence of operations in preparation for the execution of the kernel on the GPU.
These operations, necessary for setting up and launching the kernel, are an overhead cost which must be paid for each kernel that is issued.
```

## official-028-4:hybrid_rerank:retrieved

CUDA 13.0.1：对cuda-graphs相关代码进行review时，为何不能接受“CUDA Graph只是把相互依赖的kernel无条件同时启动。”作为正确性依据？

必要要点：CUDA Graph用依赖连接操作，并将定义和执行分开。

禁止误读：CUDA Graph只是把相互依赖的kernel无条件同时启动。

```json
null
```

实际输入证据：

### Eaa57126c7d84fb84fbf9dcd5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L450-L456

```text
The graph’s nodes must all reside on a single device.

The graph can only contain kernel nodes, memcpy nodes, memset nodes, and child graph nodes.

Kernel nodes:

Use of CUDA Dynamic Parallelism by kernels in the graph is not permitted.
```

### Ea798b961e633d1b58b818923

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L37-L45

```text
A kernel from one CUDA context cannot execute concurrently with a kernel from another CUDA context.
The GPU may time slice to provide forward progress to each context.
If a user wants to run kernels from multiple process simultaneously on the SM, one must enable MPS.
Kernels that use many textures or a large amount of local memory are less likely to execute concurrently with other kernels.
```

### Ed773a6f7e4fddc79ed43e9fd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L126-L145

```text
As such, when the secondary kernel is configured with Programmatic Dependent Launch,
it must always use cudaGridDependencySynchronize
or other means to verify that the result data from the primary is available.
Please note that these methods provide the opportunity for the primary and secondary kernels to execute concurrently, however
this behavior is opportunistic and not guaranteed to lead to concurrent kernel execution.
```

### E3e3b76169249c4aa5028d43d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L306-L306

```text
It is not possible to update a cudaGraphExec_t with a cudaGraph_t if the cudaGraph_t is currently instantiated as a different cudaGraphExec_t.
```

### Ebc459d1dffa94905abd1e4d2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
6.2.8.7.
CUDA Graphs
CUDA Graphs present a new model for work submission in CUDA.
A graph is a series of operations, such as kernel launches, connected by dependencies, which is defined separately from its execution.
This allows a graph to be defined once and then launched repeatedly.
```

### E0b5dcb4fe1e929c2d6c9927c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L37-L45

```text
6.2.8.2.
Concurrent Kernel Execution
Some devices of compute capability 2.x and higher can execute multiple kernels concurrently.
Applications may query this capability by checking the concurrentKernels device property (see Device Enumeration), which is equal to 1 for devices that support it.
The maximum number of kernel launches that a device can execute concurrently depends on its compute capability and is listed in Table 27.
```

### Ed75d83f7528659779b8ad8a4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L126-L145

```text
The CUDA driver can launch the secondary kernel when all primary thread blocks have launched and executed
cudaTriggerProgrammaticLaunchCompletion.
If the primary kernel doesn’t execute the trigger, it implicitly occurs after
all thread blocks in the primary kernel exit.
In either case, the secondary thread blocks might launch
before data written by the primary kernel is visible.
```

### E93eabc3ba816ed7ba9abdb44

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L126-L145

```text
Reliance on concurrent execution in this manner is unsafe and can lead to deadlock.
```

### E0de848d132cf0d7db2bb2524

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L126-L145

```text
primary_kernel<<<grid_dim, block_dim, 0, stream>>>();
cudaLaunchKernelEx(&configSecondary, secondary_kernel);
```

## official-030-1:oracle:oracle

CUDA 13.0.1：CUDA利用率指南建议怎样划分host与device工作？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### E863f2de4411304d26b192855

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#maximize-utilization

```text
It should assign to each processor the type of work it does best: serial workloads to the host; parallel workloads to the devices.
```

## official-030-1:bm25:retrieved

CUDA 13.0.1：CUDA利用率指南建议怎样划分host与device工作？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### Ec5e671a6a30fd10316381a19

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
provides many heterogeneous synchronization primitives tuned for concurrent use between host and device threads,
including cuda::atomic, cuda::atomic_ref, cuda::barrier, cuda::semaphore, among many others.
On systems without CPU and GPU page tables: hardware coherency vs.
software coherency,
atomic accesses from the device to file-backed host memory are not supported.
```

### E5159d0d7b65c4d9cfd92c171

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L19-L21

```text
6.2.8.1.
Concurrent Execution between Host and Device
Concurrent host execution is facilitated through asynchronous library functions that return control to the host thread before the device completes the requested task.
Using asynchronous calls, many device operations can be queued up together to be executed by the CUDA driver when appropriate device resources are available.
```

### E8d70928b125eb4221afb66dd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L1-L11

```text
6.2.2.
Device Memory
As mentioned in Heterogeneous Programming, the CUDA programming model assumes a system composed of a host and a device, each with their own separate memory.
Kernels operate out of device memory, so the runtime provides functions to allocate, deallocate, and copy device memory, as well as transfer data between host memory and device memory.
Device memory can be allocated either as linear memory or as CUDA arrays.
```

### Ec5335ba9c597a43e6a9c547e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L454-L479

```text
char const* kind(cudaPointerAttributes a, bool pma, bool cma) {
switch(a.type) {
case cudaMemoryTypeHost: return pma?
"Unified: CUDA Host or Registered Memory" :
"Not Unified: CUDA Host or Registered Memory";
case cudaMemoryTypeDevice: return "Not Unified: CUDA Device Memory";
case cudaMemoryTypeManaged: return cma?
"Unified: CUDA Managed Memory" : "Not Unified: CUDA Managed Memory";
```

### E1503f01a2c1a270c0509a6c7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L502-L506

```text
6.2.8.7.7.2.1. Device Launch Modes

Unlike host launch, device graphs cannot be launched into regular CUDA streams, and can only be launched into distinct named streams, which each denote a specific launch mode:

Table 5 Device-only Graph Launch Streams
```

### Edf9df952793566dbe1cf0940

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
24.2.2.4.
Atomic accesses & synchronization primitives
CUDA Unified Memory supports all atomic operations available to host and device threads,
enabling all threads to cooperate by concurrently accessing the same shared memory location.
The CUDA C++ standard library
```

### E1e6e9b8c1adb15ad22b95aa6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
The following example code is valid on systems with CPU and GPU page tables: hardware coherency vs.
software coherency
```

### Ef2289768237477e5e2bdae3e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
but exhibits undefined behavior on other systems:
#include <cuda/atomic>
```

### E012e636b7371e57a74efe4a5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L19-L21

```text
This relieves the host thread of much of the responsibility to manage the device, leaving it free for other tasks.
```

## official-030-1:dense:retrieved

CUDA 13.0.1：CUDA利用率指南建议怎样划分host与device工作？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### Ed1b2ffbb9a2a3ea752954a2d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L623-L654

```text
cudaMemLocation location;
location.type = cudaMemLocationTypeDevice;
for (int device = 0;
device < maxDevices;
device++) {
location.id = device;
cudaMemPrefetchAsync(dataPtr, dataSize, location, 0 /* flags */, stream);
```

### E6aabf7fb801a61c913579d11

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L339-L350

```text
Replacing host calls to cudaMalloc() with cudaMallocManaged() does not impact program semantics on these systems;
device code is not able to call cudaMallocManaged().
The following example shows the use of cudaMallocManaged():
```

### E7f15fc933bca7e85735c0583

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1485-L1493

```text
If cudaMemcpyDefault is specified, then unified memory will be accessed from the host either if it cannot be coherently accessed from the device in the copy stream (2) or if the preferred location for the data is cudaCpuDeviceId and it can be coherently accessed from the host in the copy stream (1);
otherwise, it will be accessed from the device.
```

### Eb1e58d428b446869185686ca

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L611-L614

```text
cudaError_t cudaMemAdvise(const void *devPtr,
                          size_t count,
                          enum cudaMemoryAdvise advice,
                          struct cudaMemLocation location);
```

### E8c3de479cf7c745dd6d0518e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L339-L350

```text
__host__ cudaError_t cudaMallocManaged(void **devPtr, size_t size);
This API is syntactically identical to cudaMalloc(): it allocates size bytes of managed memory and
sets devPtr to refer to the allocation.
CUDA Managed Memory is also deallocated with cudaFree().
On systems with full CUDA Managed Memory support, managed memory allocations
may be accessed concurrently by all CPUs and GPUs in the system.
```

### E0acbcf49a65e1be277efdc0d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L623-L654

```text
int outerLoopIter = 0;
while (outerLoopIter < maxOuterLoopIter) {
// The data is written to in the outer loop on the CPU
init_data(dataPtr, dataSize);
// The data is made available to all GPUs by prefetching.
// Prefetching here causes read duplication of data instead
// of data migration
```

### E2b98242553d07636f6079837

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L623-L654

```text
}
// The kernel only reads this data in the inner loop
int innerLoopIter = 0;
while (innerLoopIter < maxInnerLoopIter) {
```

### E76f0727c232b1f73f93f7700

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L623-L654

```text
// Set the advice on the memory region
cudaMemLocation loc = {.type = cudaMemLocationTypeDevice, .id = myGpuId};
cudaMemAdvise(dataPtr, dataSize, cudaMemAdviseSetReadMostly, loc);
```

### E1c10ab42186724cb44922ff3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L623-L654

```text
mykernel<<<32, TPB, 0, stream>>>((const char *)dataPtr, dataSize);
innerLoopIter++;
}
outerLoopIter++;
}
cudaFree(dataPtr);
```

### E7644e4c3a6beb5e428806187

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L623-L654

```text
void test_advise_managed(cudaStream_t stream) {
char *dataPtr;
```

## official-030-1:hybrid:retrieved

CUDA 13.0.1：CUDA利用率指南建议怎样划分host与device工作？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### E6aabf7fb801a61c913579d11

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L339-L350

```text
Replacing host calls to cudaMalloc() with cudaMallocManaged() does not impact program semantics on these systems;
device code is not able to call cudaMallocManaged().
The following example shows the use of cudaMallocManaged():
```

### Eef144e5ebf1f62b693ff98d2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L356-L368

```text
int main() {
  // Allocate 100 bytes of memory, accessible to both Host and Device code
  char *s;
  cudaMallocManaged(&s, 100);
  // Note direct Host-code use of "s"
  strncpy(s, "Hello Unified Memory\n", 99);
  // Here we pass "s" to a kernel without explicitly copying
  printme<<< 1, 1 >>>(s);
  cudaDeviceSynchronize();
  // Free as for normal CUDA allocations
  cudaFree(s);
  return  0;
}
```

### E1e8f441320985b14ab0d09ec

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L125-L138

```text
24.1.2.
Programming Model
With CUDA Unified Memory, separate allocations between host and device, and explicit memory transfers between them, are no longer required.
Programs may allocate Unified Memory in the following ways:
System-Allocation APIs: on systems with full CUDA Unified Memory support via
any system allocation of the host process (C’s malloc(), C++’s new operator, POSIX’s mmap and so on).
```

### E9a4d47ca212aea1c3557b9e4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L322-L333

```text
int main() {
  // Allocate 100 bytes of memory, accessible to both Host and Device code
  char *s = (char*)malloc(100);
  // Physical allocation placed in CPU memory because host accesses "s" first
  strncpy(s, "Hello Unified Memory\n", 99);
  // Here we pass "s" to a kernel without explicitly copying
  printme<<< 1, 1 >>>(s);
  cudaDeviceSynchronize();
  // Free as for normal CUDA allocations
  cudaFree(s);
  return  0;
}
```

### Ec8badce76b9e3fd7d3fbe392

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-page-locked-host-memory.md#L53-L61

```text
Also note that CUDA runtime requires that 1-byte, 2-byte, 4-byte, 8-byte, and 16-byte naturally aligned
loads and stores to host memory initiated from the device are preserved as single accesses
from the point of view of the host and other devices.
On some platforms, atomics to memory may be broken by the hardware into separate
```

### E8c3de479cf7c745dd6d0518e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L339-L350

```text
__host__ cudaError_t cudaMallocManaged(void **devPtr, size_t size);
This API is syntactically identical to cudaMalloc(): it allocates size bytes of managed memory and
sets devPtr to refer to the allocation.
CUDA Managed Memory is also deallocated with cudaFree().
On systems with full CUDA Managed Memory support, managed memory allocations
may be accessed concurrently by all CPUs and GPUs in the system.
```

### E4e812ee811211d1e32c12e4b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L125-L138

```text
CUDA Managed Memory Allocation APIs: via the cudaMallocManaged() API which is syntactically similar to cudaMalloc().
CUDA Managed Variables: variables declared with __managed__, which are semantically similar to a __device__ variable.
Most examples in this chapter provide at least two versions, one using CUDA Managed Memory and one using System-Allocated Memory.
```

## official-030-1:hybrid_rerank:retrieved

CUDA 13.0.1：CUDA利用率指南建议怎样划分host与device工作？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### E6cff26435664c9ec90900fe3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
__device__ __managed__ int x, y=2;
__global__  void  kernel() {
x = 10;
}
int main() {
cudaStream_t stream1;
cudaStreamCreate(&stream1);
cudaStreamAttachMemAsync(stream1, &y, 0, cudaMemAttachHost);
cudaDeviceSynchronize();
// Wait for Host attachment to occur.
```

### E76f0727c232b1f73f93f7700

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L623-L654

```text
// Set the advice on the memory region
cudaMemLocation loc = {.type = cudaMemLocationTypeDevice, .id = myGpuId};
cudaMemAdvise(dataPtr, dataSize, cudaMemAdviseSetReadMostly, loc);
```

### E9a4d47ca212aea1c3557b9e4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L322-L333

```text
int main() {
  // Allocate 100 bytes of memory, accessible to both Host and Device code
  char *s = (char*)malloc(100);
  // Physical allocation placed in CPU memory because host accesses "s" first
  strncpy(s, "Hello Unified Memory\n", 99);
  // Here we pass "s" to a kernel without explicitly copying
  printme<<< 1, 1 >>>(s);
  cudaDeviceSynchronize();
  // Free as for normal CUDA allocations
  cudaFree(s);
  return  0;
}
```

### Ec5e671a6a30fd10316381a19

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
provides many heterogeneous synchronization primitives tuned for concurrent use between host and device threads,
including cuda::atomic, cuda::atomic_ref, cuda::barrier, cuda::semaphore, among many others.
On systems without CPU and GPU page tables: hardware coherency vs.
software coherency,
atomic accesses from the device to file-backed host memory are not supported.
```

### Ea86cf3fb222a080e065d780a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-streams.md#L5-L24

```text
cudaMemcpyAsync(hostPtr + i * size, outputDevPtr + i * size,
size, cudaMemcpyDeviceToHost, stream[i]);
}
```

### E8c2ba59623fd635499a2c2c4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
24.3.2.4.4.
Stream Association Examples
Associating data with a stream allows fine-grained control over CPU + GPU concurrency, but what data is visible to which streams must be kept in mind when using devices of compute capability lower than 6.0.
Looking at the earlier synchronization example:
```

### E75dedcf490c9d8c7f1d5d439

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
kernel<<< 1, 1, 0, stream1 >>>();
// Note: Launches into stream1.
y = 20;
// Success – a kernel is running but “y”
```

### E477a91043c3505de28aeea79

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
// has been associated with no stream.
return  0;
}
Here we explicitly associate y with host accessibility, thus enabling access at all times from the CPU.
(As before, note the absence of cudaDeviceSynchronize() before the access.) Accesses to y by the GPU running kernel will now produce undefined results.
Note that associating a variable with a stream does not change the associating of any other variable.
```

### E7644e4c3a6beb5e428806187

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L623-L654

```text
void test_advise_managed(cudaStream_t stream) {
char *dataPtr;
size_t dataSize = 64 * TPB;
```

## official-030-2:oracle:oracle

CUDA 13.0.1：异构代码中的串行控制循环与数据并行运算，按指南应分别放在host还是device？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### E863f2de4411304d26b192855

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#maximize-utilization

```text
It should assign to each processor the type of work it does best: serial workloads to the host; parallel workloads to the devices.
```

## official-030-2:bm25:retrieved

CUDA 13.0.1：异构代码中的串行控制循环与数据并行运算，按指南应分别放在host还是device？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### Ec5e671a6a30fd10316381a19

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
provides many heterogeneous synchronization primitives tuned for concurrent use between host and device threads,
including cuda::atomic, cuda::atomic_ref, cuda::barrier, cuda::semaphore, among many others.
On systems without CPU and GPU page tables: hardware coherency vs.
software coherency,
atomic accesses from the device to file-backed host memory are not supported.
```

### E5159d0d7b65c4d9cfd92c171

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L19-L21

```text
6.2.8.1.
Concurrent Execution between Host and Device
Concurrent host execution is facilitated through asynchronous library functions that return control to the host thread before the device completes the requested task.
Using asynchronous calls, many device operations can be queued up together to be executed by the CUDA driver when appropriate device resources are available.
```

### E8d70928b125eb4221afb66dd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-device-memory.md#L1-L11

```text
6.2.2.
Device Memory
As mentioned in Heterogeneous Programming, the CUDA programming model assumes a system composed of a host and a device, each with their own separate memory.
Kernels operate out of device memory, so the runtime provides functions to allocate, deallocate, and copy device memory, as well as transfer data between host memory and device memory.
Device memory can be allocated either as linear memory or as CUDA arrays.
```

### Ec5335ba9c597a43e6a9c547e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L454-L479

```text
char const* kind(cudaPointerAttributes a, bool pma, bool cma) {
switch(a.type) {
case cudaMemoryTypeHost: return pma?
"Unified: CUDA Host or Registered Memory" :
"Not Unified: CUDA Host or Registered Memory";
case cudaMemoryTypeDevice: return "Not Unified: CUDA Device Memory";
case cudaMemoryTypeManaged: return cma?
"Unified: CUDA Managed Memory" : "Not Unified: CUDA Managed Memory";
```

### E1503f01a2c1a270c0509a6c7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L502-L506

```text
6.2.8.7.7.2.1. Device Launch Modes

Unlike host launch, device graphs cannot be launched into regular CUDA streams, and can only be launched into distinct named streams, which each denote a specific launch mode:

Table 5 Device-only Graph Launch Streams
```

### Edf9df952793566dbe1cf0940

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
24.2.2.4.
Atomic accesses & synchronization primitives
CUDA Unified Memory supports all atomic operations available to host and device threads,
enabling all threads to cooperate by concurrently accessing the same shared memory location.
The CUDA C++ standard library
```

### E1e6e9b8c1adb15ad22b95aa6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
The following example code is valid on systems with CPU and GPU page tables: hardware coherency vs.
software coherency
```

### Ef2289768237477e5e2bdae3e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
but exhibits undefined behavior on other systems:
#include <cuda/atomic>
```

### E012e636b7371e57a74efe4a5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L19-L21

```text
This relieves the host thread of much of the responsibility to manage the device, leaving it free for other tasks.
```

## official-030-2:dense:retrieved

CUDA 13.0.1：异构代码中的串行控制循环与数据并行运算，按指南应分别放在host还是device？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### E7f15fc933bca7e85735c0583

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1485-L1493

```text
If cudaMemcpyDefault is specified, then unified memory will be accessed from the host either if it cannot be coherently accessed from the device in the copy stream (2) or if the preferred location for the data is cudaCpuDeviceId and it can be coherently accessed from the host in the copy stream (1);
otherwise, it will be accessed from the device.
```

### E6cff26435664c9ec90900fe3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
__device__ __managed__ int x, y=2;
__global__  void  kernel() {
x = 10;
}
int main() {
cudaStream_t stream1;
cudaStreamCreate(&stream1);
cudaStreamAttachMemAsync(stream1, &y, 0, cudaMemAttachHost);
cudaDeviceSynchronize();
// Wait for Host attachment to occur.
```

### E1b8c4f8440dc582e185467fc

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-streams.md#L35-L39

```text
For code that is compiled using the --default-stream per-thread compilation flag (or that defines the CUDA_API_PER_THREAD_DEFAULT_STREAM macro before including CUDA headers (cuda.h and cuda_runtime.h)), the default stream is a regular stream and each host thread has its own default stream.
```

### E45fcf8ab878d9077a6622413

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1477-L1483

```text
If cudaMemcpyDeviceTo* is specified and the source data is unified memory, then it will be accessed from the device.
The source must be coherently accessible from the device in the copy stream (2);
otherwise, an error is returned.
Similar rules apply to the destination when cudaMemcpy*ToDevice is specified and the destination is unified memory.
```

### Ebb19fae3fae339e01ba32d7d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1415-L1430

```text
__device__ __managed__ int x, y=2;
__global__  void  kernel() {
x = 10;
}
int main() {
cudaStream_t stream1;
cudaStreamCreate(&stream1);
cudaStreamAttachMemAsync(stream1, &x);
// Associate “x” with stream1.
cudaDeviceSynchronize();
// Wait for “x” attachment to occur.
```

### Ef836072a14b4a1331e7ee557

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1485-L1493

```text
When using cudaMemset*() with unified memory, the data must be coherently accessible from the device in the stream being used for the cudaMemset() operation (2);
otherwise, an error is returned.
When data is accessed from the device either by cudaMemcpy* or cudaMemset*, the stream of operation is considered to be active on the GPU.
```

### Efcd4f004fe269c7712c894f3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1485-L1493

```text
During this time, any CPU access of data that is associated with that stream or data that has global visibility, will result in a segmentation fault if the GPU has a zero value for the device attribute concurrentManagedAccess.
The program must synchronize appropriately to ensure the operation has completed before accessing any associated data from the CPU.
```

### E8c2ba59623fd635499a2c2c4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
24.3.2.4.4.
Stream Association Examples
```

## official-030-2:hybrid:retrieved

CUDA 13.0.1：异构代码中的串行控制循环与数据并行运算，按指南应分别放在host还是device？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### E5159d0d7b65c4d9cfd92c171

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L19-L21

```text
6.2.8.1.
Concurrent Execution between Host and Device
Concurrent host execution is facilitated through asynchronous library functions that return control to the host thread before the device completes the requested task.
Using asynchronous calls, many device operations can be queued up together to be executed by the CUDA driver when appropriate device resources are available.
```

### Eef144e5ebf1f62b693ff98d2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L356-L368

```text
int main() {
  // Allocate 100 bytes of memory, accessible to both Host and Device code
  char *s;
  cudaMallocManaged(&s, 100);
  // Note direct Host-code use of "s"
  strncpy(s, "Hello Unified Memory\n", 99);
  // Here we pass "s" to a kernel without explicitly copying
  printme<<< 1, 1 >>>(s);
  cudaDeviceSynchronize();
  // Free as for normal CUDA allocations
  cudaFree(s);
  return  0;
}
```

### E1e8f441320985b14ab0d09ec

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L125-L138

```text
24.1.2.
Programming Model
With CUDA Unified Memory, separate allocations between host and device, and explicit memory transfers between them, are no longer required.
Programs may allocate Unified Memory in the following ways:
System-Allocation APIs: on systems with full CUDA Unified Memory support via
any system allocation of the host process (C’s malloc(), C++’s new operator, POSIX’s mmap and so on).
```

### E6aabf7fb801a61c913579d11

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L339-L350

```text
Replacing host calls to cudaMalloc() with cudaMallocManaged() does not impact program semantics on these systems;
device code is not able to call cudaMallocManaged().
The following example shows the use of cudaMallocManaged():
```

### Ee38f6b125a227aa153dc4b02

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L220-L222

```text
6.2.8.9. Synchronous Calls

When a synchronous function is called, control is not returned to the host thread before the device has completed the requested task. Whether the host thread will then yield, block, or spin can be specified by calling cudaSetDeviceFlags()with some specific flags (see reference manual for details) before any other CUDA call is performed by the host thread.
```

### E012e636b7371e57a74efe4a5

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L19-L21

```text
This relieves the host thread of much of the responsibility to manage the device, leaving it free for other tasks.
The following device operations are asynchronous with respect to the host:
```

### E4e812ee811211d1e32c12e4b

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L125-L138

```text
CUDA Managed Memory Allocation APIs: via the cudaMallocManaged() API which is syntactically similar to cudaMalloc().
CUDA Managed Variables: variables declared with __managed__, which are semantically similar to a __device__ variable.
Most examples in this chapter provide at least two versions, one using CUDA Managed Memory and one using System-Allocated Memory.
Tabs allow you to choose between them.
```

### Ece48aaf0f05759cf5063bd10

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L125-L138

```text
The following samples illustrate how Unified Memory simplifies CUDA programs:
```

## official-030-2:hybrid_rerank:retrieved

CUDA 13.0.1：异构代码中的串行控制循环与数据并行运算，按指南应分别放在host还是device？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### Ea86cf3fb222a080e065d780a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-streams.md#L5-L24

```text
cudaMemcpyAsync(hostPtr + i * size, outputDevPtr + i * size,
size, cudaMemcpyDeviceToHost, stream[i]);
}
```

### E6cff26435664c9ec90900fe3

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
__device__ __managed__ int x, y=2;
__global__  void  kernel() {
x = 10;
}
int main() {
cudaStream_t stream1;
cudaStreamCreate(&stream1);
cudaStreamAttachMemAsync(stream1, &y, 0, cudaMemAttachHost);
cudaDeviceSynchronize();
// Wait for Host attachment to occur.
```

### Ec5335ba9c597a43e6a9c547e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L454-L479

```text
char const* kind(cudaPointerAttributes a, bool pma, bool cma) {
switch(a.type) {
case cudaMemoryTypeHost: return pma?
"Unified: CUDA Host or Registered Memory" :
"Not Unified: CUDA Host or Registered Memory";
case cudaMemoryTypeDevice: return "Not Unified: CUDA Device Memory";
case cudaMemoryTypeManaged: return cma?
"Unified: CUDA Managed Memory" : "Not Unified: CUDA Managed Memory";
```

### E76f0727c232b1f73f93f7700

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L623-L654

```text
// Set the advice on the memory region
cudaMemLocation loc = {.type = cudaMemLocationTypeDevice, .id = myGpuId};
cudaMemAdvise(dataPtr, dataSize, cudaMemAdviseSetReadMostly, loc);
```

### E7f15fc933bca7e85735c0583

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1485-L1493

```text
If cudaMemcpyDefault is specified, then unified memory will be accessed from the host either if it cannot be coherently accessed from the device in the copy stream (2) or if the preferred location for the data is cudaCpuDeviceId and it can be coherently accessed from the host in the copy stream (1);
otherwise, it will be accessed from the device.
```

### E92434999fd9d594aed1241ad

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-streams.md#L5-L24

```text
Each of these streams is defined by the following code sample as a sequence of one memory copy from host to device, one kernel launch, and one memory copy from device to host:
for (int i = 0;
i < 2;
++i) {
cudaMemcpyAsync(inputDevPtr + i * size, hostPtr + i * size,
size, cudaMemcpyHostToDevice, stream[i]);
MyKernel <<<100, 512, 0, stream[i]>>>
(outputDevPtr + i * size, inputDevPtr + i * size, size);
```

### Ea8cb526686963d597e8845b8

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-streams.md#L5-L24

```text
6.2.8.5.1.
Creation and Destruction of Streams
A stream is defined by creating a stream object and specifying it as the stream parameter to a sequence of kernel launches and host <-> device memory copies.
The following code sample creates two streams and allocates an array hostPtr of float in page-locked memory.
cudaStream_t stream[2];
for (int i = 0;
i < 2;
++i)
cudaStreamCreate(&stream[i]);
float* hostPtr;
cudaMallocHost(&hostPtr, 2 * size);
```

### E8c2ba59623fd635499a2c2c4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1392-L1413

```text
24.3.2.4.4.
Stream Association Examples
```

## official-030-3:oracle:oracle

CUDA 13.0.1：排查该主题时，有人声称“所有串行工作都应无条件搬到GPU。”，根据文档这个说法哪里需要纠正？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### E863f2de4411304d26b192855

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#maximize-utilization

```text
It should assign to each processor the type of work it does best: serial workloads to the host; parallel workloads to the devices.
```

## official-030-3:bm25:retrieved

CUDA 13.0.1：排查该主题时，有人声称“所有串行工作都应无条件搬到GPU。”，根据文档这个说法哪里需要纠正？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### E9e2550c0efacaae5da26ba32

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L64-L69

```text
6.2.8.6.1. Background

A CUDA application utilizes the GPU by launching and executing multiple kernels on it.
A typical GPU activity timeline is shown in Figure 10.

Figure 10 GPU activity timeline
```

### E10d4c1a966d1b318e13ff8ba

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-conserving_memory.md#L51-L56

```text
## Reduce CUDA Graphs

By default, we optimize model inference using CUDA graphs which take up extra memory in the GPU.

!!! warning
    CUDA graph capture takes up more memory in V1 than in V0.
```

### Ea69ba78298695847964cf47f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-quantized_kvcache.md#L54-L56

```text
- `"auto"`: Uses the model's default "unquantized" data type
- `"fp8"` or `"fp8_e4m3"`: Supported on CUDA 11.8+ and ROCm (AMD GPU)
- `"fp8_e5m2"`: Supported on CUDA 11.8+
```

### E56b53609cc3fa0d190917108

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L440-L445

```text
Note

For devices with CUDA Managed Memory without full support,
visibility of __managed__ variables for asynchronous operations executing in CUDA streams
is discussed in the section on
Managing Data Visibility and Concurrent CPU + GPU Access with Streams.
```

### Ec5e671a6a30fd10316381a19

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
provides many heterogeneous synchronization primitives tuned for concurrent use between host and device threads,
including cuda::atomic, cuda::atomic_ref, cuda::barrier, cuda::semaphore, among many others.
On systems without CPU and GPU page tables: hardware coherency vs.
software coherency,
atomic accesses from the device to file-backed host memory are not supported.
```

### Edf9df952793566dbe1cf0940

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
24.2.2.4.
Atomic accesses & synchronization primitives
CUDA Unified Memory supports all atomic operations available to host and device threads,
enabling all threads to cooperate by concurrently accessing the same shared memory location.
The CUDA C++ standard library
```

### E1e6e9b8c1adb15ad22b95aa6

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
The following example code is valid on systems with CPU and GPU page tables: hardware coherency vs.
software coherency
```

### Ef2289768237477e5e2bdae3e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
but exhibits undefined behavior on other systems:
#include <cuda/atomic>
```

## official-030-3:dense:retrieved

CUDA 13.0.1：排查该主题时，有人声称“所有串行工作都应无条件搬到GPU。”，根据文档这个说法哪里需要纠正？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### E885ebf52beeb93b690a2dc22

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
cudaMemRangeAttributePreferredLocation:
the result returned will be a GPU device id or cudaCpuDeviceId if the entire
memory range has the corresponding processor as preferred location,
```

### Ed75d83f7528659779b8ad8a4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L126-L145

```text
The CUDA driver can launch the secondary kernel when all primary thread blocks have launched and executed
cudaTriggerProgrammaticLaunchCompletion.
If the primary kernel doesn’t execute the trigger, it implicitly occurs after
all thread blocks in the primary kernel exit.
In either case, the secondary thread blocks might launch
before data written by the primary kernel is visible.
```

### Ed609720e94694b9b838bd6da

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L16-L32

```text
Productivity: GPU programs may access Unified Memory from GPU and CPU threads
concurrently without needing to create separate allocations (cudaMalloc()) and
copy memory manually back and forth (cudaMemcpy*()).
```

### E897194ad2f791358ff557c8f

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-parallelism_scaling.md#L29-L43

```text
You can override the defaults by setting `distributed_executor_backend` in the `LLM` class or `--distributed-executor-backend` in the API server.
Use `mp` for `multiprocessing` or `ray` for Ray.
For multi-GPU inference, set `tensor_parallel_size` in the `LLM` class to the desired GPU count.
For example, to run inference on 4 GPUs:
```

### Eb3d67347a293eb773fb9af27

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1326-L1332

```text
This aligns with the CUDA programming model, which specifies that a kernel can run at any time following a launch and is not guaranteed to have finished until the host issues a synchronization call.
Any function call that logically guarantees the GPU completes its work is valid.
This includes cudaDeviceSynchronize();
```

### E6389c5d5cad82e7e87c6bd6c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
otherwise cudaInvalidDeviceId will be returned.
An application can use this query API to make decision about staging data through
CPU or GPU depending on the preferred location attribute of the managed pointer.
Note that the actual location of the memory range at the time
of the query may be different from the preferred location.
cudaMemRangeAttributeAccessedBy:
```

### E8527e24f7def8dbf37934928

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
will return the list of devices that have that advise set for that memory range.
cudaMemRangeAttributeLastPrefetchLocation:
will return the last location to which the memory range was prefetched
explicitly using cudaMemPrefetchAsync.
Note that this simply returns the last location that the application requested to prefetch the memory range to.
```

### E36e2d92db8de1d6211448d94

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
It gives no indication as to whether the prefetch operation to that location has completed or even begun.
cudaMemRangeAttributePreferredLocationType:
```

### E0de848d132cf0d7db2bb2524

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L126-L145

```text
primary_kernel<<<grid_dim, block_dim, 0, stream>>>();
cudaLaunchKernelEx(&configSecondary, secondary_kernel);
When the secondary kernel is launched using the cudaLaunchAttributeProgrammaticStreamSerialization attribute,
```

## official-030-3:hybrid:retrieved

CUDA 13.0.1：排查该主题时，有人声称“所有串行工作都应无条件搬到GPU。”，根据文档这个说法哪里需要纠正？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### Eb3d67347a293eb773fb9af27

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1326-L1332

```text
This aligns with the CUDA programming model, which specifies that a kernel can run at any time following a launch and is not guaranteed to have finished until the host issues a synchronization call.
Any function call that logically guarantees the GPU completes its work is valid.
This includes cudaDeviceSynchronize();
```

### E10d4c1a966d1b318e13ff8ba

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-conserving_memory.md#L51-L56

```text
## Reduce CUDA Graphs

By default, we optimize model inference using CUDA graphs which take up extra memory in the GPU.

!!! warning
    CUDA graph capture takes up more memory in V1 than in V0.
```

### Ea798b961e633d1b58b818923

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L37-L45

```text
A kernel from one CUDA context cannot execute concurrently with a kernel from another CUDA context.
The GPU may time slice to provide forward progress to each context.
If a user wants to run kernels from multiple process simultaneously on the SM, one must enable MPS.
Kernels that use many textures or a large amount of local memory are less likely to execute concurrently with other kernels.
```

### E6fcff5765635f30b24c2d96c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-docker.md#L67-L85

```text
!!
! note
By default vLLM will build for all GPU types for widest distribution.
If you are just building for the
current GPU type the machine is running on, you can add the argument `--build-arg torch_cuda_arch_list=""`
for vLLM to find the current GPU type and build for that.
If you are using Podman instead of Docker, you might need to disable SELinux labeling by
```

### E9e2550c0efacaae5da26ba32

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L64-L69

```text
6.2.8.6.1. Background

A CUDA application utilizes the GPU by launching and executing multiple kernels on it.
A typical GPU activity timeline is shown in Figure 10.

Figure 10 GPU activity timeline
```

### Ebc81bb294818402ec2154b33

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1326-L1332

```text
24.3.2.4.2.
Explicit Synchronization and Logical GPU Activity
Note that explicit synchronization is required even if kernel runs quickly and finishes before the CPU touches y in the above example.
Unified Memory uses logical activity to determine whether the GPU is idle.
```

### E83e7405f8a45f0c79c37aade

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1326-L1332

```text
cudaStreamSynchronize() and cudaStreamQuery() (provided it returns cudaSuccess and not cudaErrorNotReady) where the specified stream is the only stream still executing on the GPU;
cudaEventSynchronize() and cudaEventQuery() in cases where the specified event is not followed by any device work;
as well as uses of cudaMemcpy() and cudaMemset() that are documented as being fully synchronous with respect to the host.
```

### E3f42fb36b6c1fde2ea55265a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1326-L1332

```text
Dependencies created between streams will be followed to infer completion of other streams by synchronizing on a stream or event.
Dependencies can be created via cudaStreamWaitEvent() or implicitly when using the default (NULL) stream.
```

### E0b5dcb4fe1e929c2d6c9927c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L37-L45

```text
6.2.8.2.
Concurrent Kernel Execution
```

## official-030-3:hybrid_rerank:retrieved

CUDA 13.0.1：排查该主题时，有人声称“所有串行工作都应无条件搬到GPU。”，根据文档这个说法哪里需要纠正？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### Eb09a14de4b65a8718d6c9f01

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L589-L603

```text
// execute on CPU
cudaMemLocation location = {.type = cudaMemLocationTypeDevice, .id = myGpuId};
cudaMemPrefetchAsync(data, N, location, s, 0 /* flags */);
// prefetch to GPU
```

### E04edc863965458fe494f3921

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1348-L1371

```text
cudaMallocManaged(&managed, 4);
cudaMallocManaged(&also_managed, 4);
// Point 1: CPU can access non-managed data.
kernel<<< 1, 1, 0, stream1 >>>(managed);
*non_managed = 1;
// Point 2: CPU cannot access any managed data while GPU is busy,
//          unless concurrentManagedAccess = 1
```

### E9cac37b06f07246d79a9fd4d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1309-L1322

```text
x = 10;
}
int main() {
kernel<<< 1, 1 >>>();
cudaDeviceSynchronize();
y = 20;
//  Success on GPUs not supporing concurrent access
```

### E7ef2488b4330c96a93a1ca80

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1269-L1271

```text
Combined with the system-wide virtual address space, page faulting provides several benefits.
First, page faulting means that the CUDA system software doesn’t need to synchronize all managed memory allocations to the GPU before each kernel launch.
If a kernel running on the GPU accesses a page that is not resident in its memory, it faults, allowing the page to be automatically migrated to the GPU memory on-demand.
```

### Ec5e671a6a30fd10316381a19

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
provides many heterogeneous synchronization primitives tuned for concurrent use between host and device threads,
including cuda::atomic, cuda::atomic_ref, cuda::barrier, cuda::semaphore, among many others.
On systems without CPU and GPU page tables: hardware coherency vs.
software coherency,
atomic accesses from the device to file-backed host memory are not supported.
```

### E52ec56a9d4444256a742d13a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L589-L603

```text
Managed
void test_prefetch_managed(cudaStream_t s) {
char *data;
cudaMallocManaged(&data, N);
init_data(data, N);
```

### E0bda9d8005b12499e7a4d11a

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L589-L603

```text
mykernel<<<(N + TPB - 1) / TPB, TPB, 0, s>>>(data, N);
// execute on GPU
location = {.type = cudaMemLocationTypeHost};
cudaMemPrefetchAsync(data, N, location, s, 0 /* flags */);
// prefetch to CPU
```

### E13b18885cb8495677d9f6495

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L589-L603

```text
cudaStreamSynchronize(s);
use_data(data, N);
cudaFree(data);
}
```

### E526c1cbf5ff9019b6075de92

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1348-L1371

```text
int main() {
cudaStream_t stream1, stream2;
cudaStreamCreate(&stream1);
cudaStreamCreate(&stream2);
int *non_managed, *managed, *also_managed;
cudaMallocHost(&non_managed, 4);
// Non-managed, CPU-accessible memory
```

### E51eb2796a17fb08818aa3113

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1348-L1371

```text
// Note we have not yet synchronized, so "kernel" is still active.
*also_managed = 2;
// Will issue segmentation fault
```

## official-030-4:oracle:oracle

CUDA 13.0.1：对maximize-utilization相关代码进行review时，为何不能接受“所有串行工作都应无条件搬到GPU。”作为正确性依据？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### E863f2de4411304d26b192855

https://docs.nvidia.com/cuda/archive/13.0.1/cuda-c-programming-guide/index.html#maximize-utilization

```text
It should assign to each processor the type of work it does best: serial workloads to the host; parallel workloads to the devices.
```

## official-030-4:bm25:retrieved

CUDA 13.0.1：对maximize-utilization相关代码进行review时，为何不能接受“所有串行工作都应无条件搬到GPU。”作为正确性依据？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### E3996a52a46b8aa95b13c74bd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L1-L3

```text
8.2. Maximize Utilization

To maximize utilization the application should be structured in a way that it exposes as much parallelism as possible and efficiently maps this parallelism to the various components of the system to keep them busy most of the time.
```

### Ec145e4456c40268a681ccc19

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L21-L21

```text
As described in Hardware Multithreading, a GPU multiprocessor primarily relies on thread-level parallelism to maximize utilization of its functional units.
Utilization is therefore directly linked to the number of resident warps.
At every instruction issue time, a warp scheduler selects an instruction that is ready to execute.
```

### Ec8a524a3eb303e197f102d50

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L11-L15

```text
8.2.2. Device Level

At a lower level, the application should maximize parallel execution between the multiprocessors of a device.

Multiple kernels can execute concurrently on a device, so maximum utilization can also be achieved by using streams to enable enough kernels to execute concurrently as described in Asynchronous Concurrent Execution.
```

### E854176531e0cf52e426febb2

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L21-L24

```text
- Increase `gpu_memory_utilization`.
vLLM pre-allocates GPU cache using this percentage of memory.
By increasing utilization, you can provide more KV cache space.
- Decrease `max_num_seqs` or `max_num_batched_tokens`.
This reduces the number of concurrent requests in a batch, thereby requiring less KV cache space.
- Increase `tensor_parallel_size`.
```

### E33f8a0095892ffa429fbb160

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L42-L43

```text
- It improves ITL and generation decode because decode requests are prioritized.
- It helps achieve better GPU utilization by locating compute-bound (prefill) and memory-bound (decode) requests to the same batch.
```

### E19c32c15fb91d2a801d0041d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L21-L21

```text
This instruction can be another independent instruction of the same warp, exploiting instruction-level parallelism, or more commonly an instruction of another warp, exploiting thread-level parallelism.
If a ready to execute instruction is selected it is issued to the active threads of the warp.
```

### E12cb0c340dce62bc1d0e20c0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L21-L21

```text
The number of clock cycles it takes for a warp to be ready to execute its next instruction is called the latency, and full utilization is achieved when all warp schedulers always have some instruction to issue for some warp at every clock cycle during that latency period, or in other words, when latency is completely “hidden”.
```

### E65d19572768d214ce253c5e7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L21-L21

```text
The number of instructions required to hide a latency of L clock cycles depends on the respective throughputs of these instructions (see the CUDA C++ Best Practices Guide for the throughputs of various arithmetic instructions).
If we assume instructions with maximum throughput, it is equal to:
```

### Ea9ce84adf4242fba791cc864

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-optimization.md#L21-L24

```text
This shards model weights across GPUs, allowing each GPU to have more memory available for KV cache.
However, increasing this value may cause excessive synchronization overhead.
- Increase `pipeline_parallel_size`.
```

## official-030-4:dense:retrieved

CUDA 13.0.1：对maximize-utilization相关代码进行review时，为何不能接受“所有串行工作都应无条件搬到GPU。”作为正确性依据？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### E885ebf52beeb93b690a2dc22

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
cudaMemRangeAttributePreferredLocation:
the result returned will be a GPU device id or cudaCpuDeviceId if the entire
memory range has the corresponding processor as preferred location,
```

### Ef60380f1cc526a0aaf82f002

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-faq.md#L15-L18

```text
### CUDA Error: Illegal Memory Access Encountered
This error may result from kernel errors or out-of-memory issues:
- If it is a kernel error, resolving it may be challenging. Please file an issue on GitHub.
- If it is an out-of-memory issue, it may sometimes be reported as this error instead of "Out of Memory." Refer to the section above for guidance on avoiding OOM issues.
```

### Ed75d83f7528659779b8ad8a4

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L126-L145

```text
The CUDA driver can launch the secondary kernel when all primary thread blocks have launched and executed
cudaTriggerProgrammaticLaunchCompletion.
If the primary kernel doesn’t execute the trigger, it implicitly occurs after
all thread blocks in the primary kernel exit.
In either case, the secondary thread blocks might launch
before data written by the primary kernel is visible.
```

### Eb3d67347a293eb773fb9af27

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1326-L1332

```text
This aligns with the CUDA programming model, which specifies that a kernel can run at any time following a launch and is not guaranteed to have finished until the host issues a synchronization call.
Any function call that logically guarantees the GPU completes its work is valid.
This includes cudaDeviceSynchronize();
```

### Ed609720e94694b9b838bd6da

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L16-L32

```text
Productivity: GPU programs may access Unified Memory from GPU and CPU threads
concurrently without needing to create separate allocations (cudaMalloc()) and
copy memory manually back and forth (cudaMemcpy*()).
```

### E6389c5d5cad82e7e87c6bd6c

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
otherwise cudaInvalidDeviceId will be returned.
An application can use this query API to make decision about staging data through
CPU or GPU depending on the preferred location attribute of the managed pointer.
Note that the actual location of the memory range at the time
of the query may be different from the preferred location.
cudaMemRangeAttributeAccessedBy:
```

### E8527e24f7def8dbf37934928

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
will return the list of devices that have that advise set for that memory range.
cudaMemRangeAttributeLastPrefetchLocation:
will return the last location to which the memory range was prefetched
explicitly using cudaMemPrefetchAsync.
Note that this simply returns the last location that the application requested to prefetch the memory range to.
```

### E36e2d92db8de1d6211448d94

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
It gives no indication as to whether the prefetch operation to that location has completed or even begun.
cudaMemRangeAttributePreferredLocationType:
```

### E0de848d132cf0d7db2bb2524

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L126-L145

```text
primary_kernel<<<grid_dim, block_dim, 0, stream>>>();
cudaLaunchKernelEx(&configSecondary, secondary_kernel);
```

## official-030-4:hybrid:retrieved

CUDA 13.0.1：对maximize-utilization相关代码进行review时，为何不能接受“所有串行工作都应无条件搬到GPU。”作为正确性依据？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### Ec145e4456c40268a681ccc19

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L21-L21

```text
As described in Hardware Multithreading, a GPU multiprocessor primarily relies on thread-level parallelism to maximize utilization of its functional units.
Utilization is therefore directly linked to the number of resident warps.
At every instruction issue time, a warp scheduler selects an instruction that is ready to execute.
```

### Eb3d67347a293eb773fb9af27

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1326-L1332

```text
This aligns with the CUDA programming model, which specifies that a kernel can run at any time following a launch and is not guaranteed to have finished until the host issues a synchronization call.
Any function call that logically guarantees the GPU completes its work is valid.
This includes cudaDeviceSynchronize();
```

### Ea798b961e633d1b58b818923

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-asynchronous-concurrent-execution.md#L37-L45

```text
A kernel from one CUDA context cannot execute concurrently with a kernel from another CUDA context.
The GPU may time slice to provide forward progress to each context.
If a user wants to run kernels from multiple process simultaneously on the SM, one must enable MPS.
Kernels that use many textures or a large amount of local memory are less likely to execute concurrently with other kernels.
```

### Eb842a9a30ddb7416d9660673

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-cuda-graphs.md#L1-L7

```text
For a GPU kernel with a short execution time, this overhead cost can be a significant fraction of the overall end-to-end execution time.
Work submission using graphs is separated into three distinct stages: definition, instantiation, and execution.
```

### E885ebf52beeb93b690a2dc22

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
cudaMemRangeAttributePreferredLocation:
the result returned will be a GPU device id or cudaCpuDeviceId if the entire
memory range has the corresponding processor as preferred location,
```

### E19c32c15fb91d2a801d0041d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L21-L21

```text
This instruction can be another independent instruction of the same warp, exploiting instruction-level parallelism, or more commonly an instruction of another warp, exploiting thread-level parallelism.
If a ready to execute instruction is selected it is issued to the active threads of the warp.
```

### E12cb0c340dce62bc1d0e20c0

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L21-L21

```text
The number of clock cycles it takes for a warp to be ready to execute its next instruction is called the latency, and full utilization is achieved when all warp schedulers always have some instruction to issue for some warp at every clock cycle during that latency period, or in other words, when latency is completely “hidden”.
```

### E65d19572768d214ce253c5e7

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-maximize-utilization.md#L21-L21

```text
The number of instructions required to hide a latency of L clock cycles depends on the respective throughputs of these instructions (see the CUDA C++ Best Practices Guide for the throughputs of various arithmetic instructions).
If we assume instructions with maximum throughput, it is equal to:
```

### Ebc81bb294818402ec2154b33

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1326-L1332

```text
24.3.2.4.2.
Explicit Synchronization and Logical GPU Activity
Note that explicit synchronization is required even if kernel runs quickly and finishes before the CPU touches y in the above example.
```

## official-030-4:hybrid_rerank:retrieved

CUDA 13.0.1：对maximize-utilization相关代码进行review时，为何不能接受“所有串行工作都应无条件搬到GPU。”作为正确性依据？

必要要点：串行工作适合host，并行工作适合device。

禁止误读：所有串行工作都应无条件搬到GPU。

```json
null
```

实际输入证据：

### E04edc863965458fe494f3921

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1348-L1371

```text
cudaMallocManaged(&managed, 4);
cudaMallocManaged(&also_managed, 4);
// Point 1: CPU can access non-managed data.
kernel<<< 1, 1, 0, stream1 >>>(managed);
*non_managed = 1;
// Point 2: CPU cannot access any managed data while GPU is busy,
//          unless concurrentManagedAccess = 1
```

### Ec5e671a6a30fd10316381a19

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1175-L1188

```text
provides many heterogeneous synchronization primitives tuned for concurrent use between host and device threads,
including cuda::atomic, cuda::atomic_ref, cuda::barrier, cuda::semaphore, among many others.
On systems without CPU and GPU page tables: hardware coherency vs.
software coherency,
atomic accesses from the device to file-backed host memory are not supported.
```

### E05fa3ecae9f31c8965f45edd

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/vllm-issue-21175.md#L53-L92

```text
\
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_connector":"SharedStorageConnector","kv_role":"kv_producer","kv_rank":0,"kv_parallel_size":2,"kv_connector_extra_config": {"shared_storage_path": "/workspace/test/kv"}}' &

# decoding instance, which is the KV consumer
CUDA_VISIBLE_DEVICES=1 vllm serve $MODEL_NAME \
    --port 7204 \
    --gpu-memory-utilization 0.8 \
    --trust-remote-code \
    --kv-transfer-config \
    '{"kv_co
```

### E9cac37b06f07246d79a9fd4d

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1309-L1322

```text
x = 10;
}
int main() {
kernel<<< 1, 1 >>>();
cudaDeviceSynchronize();
y = 20;
//  Success on GPUs not supporing concurrent access
```

### E885ebf52beeb93b690a2dc22

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L697-L715

```text
cudaMemRangeAttributePreferredLocation:
the result returned will be a GPU device id or cudaCpuDeviceId if the entire
memory range has the corresponding processor as preferred location,
```

### E526c1cbf5ff9019b6075de92

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1348-L1371

```text
int main() {
cudaStream_t stream1, stream2;
cudaStreamCreate(&stream1);
cudaStreamCreate(&stream2);
int *non_managed, *managed, *also_managed;
cudaMallocHost(&non_managed, 4);
// Non-managed, CPU-accessible memory
```

### E51eb2796a17fb08818aa3113

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1348-L1371

```text
// Note we have not yet synchronized, so "kernel" is still active.
*also_managed = 2;
// Will issue segmentation fault
```

### Ee24c11c6621e9027391edd18

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1348-L1371

```text
// Point 3: Concurrent GPU kernels can access the same data.
kernel<<< 1, 1, 0, stream2 >>>(managed);
// Point 4: Multi-GPU concurrent access is also permitted.
cudaSetDevice(1);
kernel<<< 1, 1 >>>(managed);
```

### Ed47792082fa50119e5a3028e

/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/cuda-unified-memory-programming.md#L1348-L1371

```text
return  0;
}
```

