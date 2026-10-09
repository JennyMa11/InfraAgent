# 答案独立人工复核

填写 answer-review.json；事实字段留空表示尚未评分。
引用 ID 合法不代表陈述受到证据支持。

## official-016-3:oracle:oracle

SGLang v0.5.2：启动路由器时希望选择缓存感知策略，policy参数应填什么？

必要要点：policy可选cache_aware、random、round_robin、power_of_two。

禁止误读：路由策略只有轮询一种。

```json
{
  "conversation_id": "b8031419-093f-43df-8481-596726a3c264",
  "answer": "policy参数应填cache_aware\n\n依据：[E9faefa1cb17387473074f5b3]",
  "citations": [
    {
      "citation_id": "E9faefa1cb17387473074f5b3",
      "content": "--policy cache_aware  # or random, round_robin, power_of_two",
      "source": "/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-router.md",
      "locator": "https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/router.md",
      "document_id": "sglang-router"
    }
  ],
  "status": "answered",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "SGLang v0.5.2：启动路由器时希望选择缓存感知策略，policy参数应填什么？",
      "hits": 0,
      "evidence": 1
    },
    {
      "step": "generate",
      "duration_ms": 2536.5,
      "provider": "ollama",
      "model": "qwen3:4b",
      "validated": true
    }
  ]
}
```

实际输入证据：

### E9faefa1cb17387473074f5b3

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/advanced_features/router.md

```text
--policy cache_aware  # or random, round_robin, power_of_two
```

## official-017-3:oracle:oracle

SGLang v0.5.2：请求JSON中想启用贪心采样，temperature应设置成多少？

必要要点：温度零对应贪心采样，较高温度增加多样性。

禁止误读：温度零等于均匀随机采样。

```json
{
  "conversation_id": "ba6d5d52-633d-424e-8286-23c3a05564eb",
  "answer": "温度应设置为 0\n\n依据：[E0793ae080d2f9fd4247b79d7]",
  "citations": [
    {
      "citation_id": "E0793ae080d2f9fd4247b79d7",
      "content": "`temperature = 0` corresponds to greedy sampling, a higher temperature leads to more diversity.",
      "source": "/Users/jennyma/Projects/InfraAgent/data/official-evals/infra-official-v1/corpus/sglang-sampling_params.md",
      "locator": "https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/basic_usage/sampling_params.md",
      "document_id": "sglang-sampling_params"
    }
  ],
  "status": "answered",
  "trace": [
    {
      "step": "retrieve",
      "duration_ms": 0.0,
      "query": "SGLang v0.5.2：请求JSON中想启用贪心采样，temperature应设置成多少？",
      "hits": 0,
      "evidence": 1
    },
    {
      "step": "generate",
      "duration_ms": 2787.9,
      "provider": "ollama",
      "model": "qwen3:4b",
      "validated": true
    }
  ]
}
```

实际输入证据：

### E0793ae080d2f9fd4247b79d7

https://github.com/sgl-project/sglang/blob/b0d25e72c401f37b55d689ddbf05b8c583afe854/docs/basic_usage/sampling_params.md

```text
`temperature = 0` corresponds to greedy sampling, a higher temperature leads to more diversity.
```

