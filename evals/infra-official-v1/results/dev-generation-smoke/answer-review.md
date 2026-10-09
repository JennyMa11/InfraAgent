# 答案独立人工复核

填写 answer-review.json；事实字段留空表示尚未评分。
引用 ID 合法不代表陈述受到证据支持。

## official-002-1:oracle:oracle

vLLM v0.10.2：缓存块身份除了文本还需要哪些额外哈希？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "fbce25ef-23db-432d-a656-0c61160602fa",
  "answer": "当前检索到的资料不足以可靠回答这个问题。可以补充文档或把问题问得更具体。",
  "citations": [],
  "status": "no_evidence",
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
      "duration_ms": 5409.8,
      "provider": "ollama",
      "model": "qwen3:4b",
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

## official-002-1:hybrid:retrieved

vLLM v0.10.2：缓存块身份除了文本还需要哪些额外哈希？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "383a0980-e638-48f8-a92a-e61d1e731da6",
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
      "duration_ms": 2647.4,
      "provider": "ollama",
      "model": "qwen3:4b",
      "validated": true
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

## official-002-2:oracle:oracle

vLLM v0.10.2：两个适配器使用相同文本，是否可以只按文本共享缓存？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "1fc1c9f7-7326-4d0e-8a7a-478c12e954ed",
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
      "duration_ms": 1963.0,
      "provider": "ollama",
      "model": "qwen3:4b",
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

## official-002-2:hybrid:retrieved

vLLM v0.10.2：两个适配器使用相同文本，是否可以只按文本共享缓存？

必要要点：额外哈希包含LoRA ID、多模态输入哈希和租户隔离盐。

禁止误读：缓存键只需文本token，适配器和图像不影响身份。

```json
{
  "conversation_id": "563bb6ba-374c-4153-ac28-cb7ddcb948fd",
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
      "duration_ms": 7729.6,
      "provider": "ollama",
      "model": "qwen3:4b",
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

