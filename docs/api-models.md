# 本地与 API 回答模型切换

保留原来的Ollama `qwen3:4b`，通过配置切换回答模型。BGE、ChromaDB、BM25、重排、
证据预算、系统提示词及引用校验流程保持不变。无需修改用户的`~/.claude/settings.json`。

## 配置

当前配置为项目根目录 `.env.llm`，恢复官方 DeepSeek；`.env.deepseek` 保留为独立历史配置。
两者均被 Git 忽略，权限为 0600；密钥只保存在本地文件或环境变量中。
模板见[deepseek.env.example](../examples/deepseek.env.example)。原AgentRouter文件独立保留。

```dotenv
# 官方API模式；切回本地：provider改为ollama，查询翻译改为none，重启服务
INFRA_RAG_LLM_PROVIDER=anthropic
# INFRA_RAG_LLM_PROVIDER=ollama
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
ANTHROPIC_MODEL=deepseek-flash
ANTHROPIC_API_KEY=YOUR_API_KEY
```

默认按`.env.llm`、`.env.aliyun`、`.env.agentrouter.openai`、`.env.aihubmix`、`.env.deepseek`、`.env.agentrouter`顺序选择第一个存在的文件。
环境变量优先于文件；使用`INFRA_RAG_LLM_ENV_FILE`选择其他配置文件。模型名是用户指定的
路由名，是否可用必须由账号权限与真实响应验证。`ANTHROPIC_deepseek_MODEL`不会自动选择模型，
使用标准`ANTHROPIC_MODEL`字段。切换后重新启动项目API；`/health`会显示实际选择的provider/model。

本客户端按[DeepSeek官方兼容文档](https://api-docs.deepseek.com/guides/anthropic_api/)
使用`x-api-key`，请求`https://api.deepseek.com/anthropic/v1/messages`。
系统提示词位于顶层system；对话历史位于messages。官方入口显式关闭thinking，协议冻结该选项。
原AgentRouter使用Bearer鉴权；根URL与末尾`/v1`均支持。不自动替换模型或入口。
API预热是最多8输出token的连通性请求，可能产生调用费用。

## 独立评测

成功连通后使用审核后的题集建立新协议与新结果目录，不覆盖本地基线：

```bash
uv run python scripts/benchmark_official.py freeze \
  --dataset evals/infra-official-v1-reviewed --provider anthropic \
  --answer-model deepseek-flash --env-file .env.deepseek \
  --output evals/infra-official-v1-reviewed/results/protocol-deepseek-api
uv run python scripts/benchmark_official.py run \
  --protocol evals/infra-official-v1-reviewed/results/protocol-deepseek-api/protocol.json \
  --env-file .env.deepseek --split dev \
  --output evals/infra-official-v1-reviewed/results/dev-deepseek-api
```

正式dev包含60题×Oracle与四种检索配置，共300条。协议只保存公开地址、路由名、选项与
预热响应元数据；不包含Key或配置文件内容。逐次生成保存返回的model、usage、stop_reason和
请求ID，便于查看路由、token消耗与截断。没有固定API权重摘要，服务端模型可能更新。

API输出上限650token、temperature0；原始系统提示词和两次格式/引用校验沿用原流程。
API没有Ollama的`format=json`约束或本地8192上下文配置，因此不能声称两端解码条件完全相同；
API仅通过同一系统提示词请求JSON，记录其实际格式遵循情况。token消耗不等同于费用，需结合账号价格。

## 连通性记录

2026-10-01，DeepSeek官方入口已验证成功，实际返回`deepseek-flash`、`end_turn`，
预热用量为8输入token、1输出token。该轮配置选择了官方API；本地模式保留为配置注释。当前默认已恢复为 DeepSeek，使用 `.env.llm`。

此前AgentRouter的Bearer与原生`x-api-key`检查均返回401，错误类型为
`unauthorized_client_error`。此结果仅属于原入口，不代表官方DeepSeek接口不可用。

完整300条dev已采集，见[DeepSeek对照报告](../evals/infra-official-v1-reviewed/results/deepseek-comparison.md)。
API169条作答、131条拒答、0条调用错误；294次实际请求，均返回end_turn。
待审核事实指标仍为空，holdout未运行。

## 历史：AIHubMix hy3-free

独立配置文件为`.env.aihubmix`，Git忽略且仅文件所有者可读写（0600）。
模板：[aihubmix.env.example](../examples/aihubmix.env.example)。

```dotenv
INFRA_RAG_LLM_PROVIDER=openai
# INFRA_RAG_LLM_PROVIDER=ollama
AIHUBMIX_BASE_URL=https://aihubmix.com/v1
AIHUBMIX_MODEL=hy3-free
AIHUBMIX_MAX_TOKENS=1024
AIHUBMIX_API_KEY=YOUR_API_KEY
```

按[AIHubMix官方入口说明](https://aihubmix.com/developers)使用Chat Completions与Bearer鉴权，
请求`https://aihubmix.com/v1/chat/completions`。传输采用项目已有标准库HTTP客户端，
无需安装OpenAI SDK；与示例使用相同API格式。保留system/user/assistant历史，非流式调用，
max_tokens为1024、temperature为0。仅提取message.content，记录模型、usage、finish_reason，
继续使用原有RAG提示词、JSON与引用ID校验。没有添加未经验证的思考或结构化输出扩展参数。

重新启动服务后生效。切回本地可将provider改为ollama；切回DeepSeek可指定文件：

```bash
INFRA_RAG_LLM_ENV_FILE=.env.deepseek uv run infra-rag serve
```

2026-10-01真实检查：项目预热及用户原始示例参数均返回HTTP400，错误码
`no_available_channel`，服务端提示`hy3-free`当前无法提供服务。这不证明Key无效，
也尚未确认该模型的实际返回身份和RAG质量。保持指定路由，没有自动替换模型。
没有产生hy3-free评测成绩，原DeepSeek和本地评测保留。

当服务端恢复后，可以用新独立协议评测（先freeze连通检查成功才创建协议）：

```bash
uv run python scripts/benchmark_official.py freeze \
  --dataset evals/infra-official-v1-reviewed --provider openai \
  --answer-model hy3-free --env-file .env.aihubmix \
  --output evals/infra-official-v1-reviewed/results/protocol-hy3-free
uv run python scripts/benchmark_official.py run \
  --protocol evals/infra-official-v1-reviewed/results/protocol-hy3-free/protocol.json \
  --env-file .env.aihubmix --split dev \
  --output evals/infra-official-v1-reviewed/results/dev-hy3-free
```

此前DeepSeek协议冻结650输出token，本配置按用户示例使用1024。
未来两轮对照须披露这个生成参数差异，检索输入与证据预算依然沿用冻结设置。

## 历史：AIHubMix coding-glm-4.6-free

2026-10-01，按用户要求将`.env.aihubmix`中的模型改为`coding-glm-4.6-free`，
API Key保持原值，base_url仍为`https://aihubmix.com/v1`，max_tokens仍为1024，非流式。
当前模板也已更新。重启服务后生效。

真实Hello请求成功，RAG独立冒烟的JSON结构和引用ID校验通过。
两次实际响应的model字段均为`glm-5.3-flash`，与请求路由`coding-glm-4.6-free`不同；
这仅记录服务端声明，不能据此验证底层权重。响应usage包含reasoning_tokens，
本客户端未强制关闭该路由思考模式。未替换请求模型名，未跑300条完整评测，
不能将此前DeepSeek成绩视为本模型成绩。

## AIHubMix dev执行结果

300条执行记录已采集，但仅前两条为真实模型回答。之后159次响应在completion正文中提示：
未充值账号只能试用10次；79条被原框架当作非JSON格式重试后记为拒答，另1条重试调用失败。
共213条连接或JSON响应错误、6条无证据直接拒答。原始记录保留，附加报告独立标注额度限制。
没有形成有效的完整模型质量/速度评测，未写dev-completed、未执行holdout。
见[执行记录及额度诊断](../evals/infra-official-v1-reviewed/results/aihubmix-comparison.md)。

## 历史：AgentRouter OpenAI兼容入口

用户指定`https://agentrouter.org/v1`，模型确认使用`deepseek-v4-flash`。
该地址属于AgentRouter，名称与OpenRouter服务不同。
使用此前已保存的AgentRouter密钥，不将AIHubMix密钥发送到此入口。

独立文件`.env.agentrouter.openai`已Git忽略、0600，原`.env.agentrouter`和其他服务配置保留。
模板：[agentrouter-openai.env.example](../examples/agentrouter-openai.env.example)。

```dotenv
INFRA_RAG_LLM_PROVIDER=openai
# INFRA_RAG_LLM_PROVIDER=ollama
OPENAI_BASE_URL=https://agentrouter.org/v1
OPENAI_MODEL=deepseek-v4-flash
OPENAI_MAX_TOKENS=1024
OPENAI_API_KEY=YOUR_AGENTROUTER_API_KEY
```

OpenAI兼容配置支持通用OPENAI字段，兼容旧AIHUBMIX字段。
请求`/v1/chat/completions`，Bearer鉴权，非流式，temperature=0。
历史配置；当前默认读取 `.env.llm`；环境变量或INFRA_RAG_LLM_ENV_FILE可覆盖选择。重启项目服务后生效。

2026-10-01，GET模型列表、项目Chat Completions预热和不含temperature的最小请求均HTTP401，
上游提示`unauthorized client detected`。仅改变协议入口没有解决此前客户端访问限制。
无法据此证明密钥无效；需服务端允许项目客户端调用后才能继续评测。没有伪装客户端或自动换模型。

## 阿里云百炼 OpenAI兼容入口

独立配置`.env.aliyun`，0600且Git忽略；使用用户新提供的阿里云密钥，其他服务密钥保留。
模板：[aliyun.env.example](../examples/aliyun.env.example)。
入口为用户指定的北京业务空间专属域名，路径为`/compatible-mode/v1`。
沿用此前用户选定的模型`deepseek-v4-flash`，已在该入口模型列表中确认；max_tokens=1024。
请求路径遵循[阿里云官方Chat接口文档](https://help.aliyun.com/zh/model-studio/qwen-api-via-openai-chat-completions)，
仅追加`/chat/completions`，不丢失compatible-mode前缀。

2026-10-01，真实模型列表请求成功；独立合成证据RAG冒烟JSON与引用ID校验通过。
实际返回模型名`deepseek-v4-flash`、finish_reason=stop，usage包含reasoning_tokens。
未显式关闭思考；不能与关闭thinking且650输出token的此前官方DeepSeek实验视为严格相同解码条件。

当前默认选择 `.env.llm`，本文件独立保留。配置切回本地可改provider为ollama；选择其他服务可以使用
INFRA_RAG_LLM_ENV_FILE指定旧配置文件，修改后重启服务。

## 历史尝试：qwen3.7-flash-2026-07-15

用户指定模型已写入`.env.aliyun`，原阿里云密钥、业务空间入口和max_tokens1024不变。
此前阿里云DeepSeek运行已按用户模型变更停止，46条完成记录保存于
`dev-aliyun-deepseek-20261001/rows.jsonl`，中断说明为`interrupted.json`。
该部分实验没有完整summary或dev-completed标记，不用于完整模型比较。

新Qwen模型真实RAG冒烟与最小Hello请求均返回HTTP403，错误码为
`AccessDenied.Unpurchased`，服务端提示`Access to model denied`。
尚未取得该模型真实输出，未启动300条正式采集，没有Qwen评测成绩。
配置已选定指定模型，没有自动降级或替换；需要该账号/业务空间允许访问此模型后才能继续。

## 官方配置核对与SDK复测

已核对用户指定的[百炼Chat文档](https://docs.bailian.console.aliyun.com/zh/model-studio/qwen-api-via-openai-chat-completions)
及[阿里云帮助中心同名文档](https://help.aliyun.com/zh/model-studio/qwen-api-via-openai-chat-completions)。
实际Workspace ID为`ws-2iwr7zmws5o8bpiw`，请求路径保留`/compatible-mode/v1/chat/completions`。
`.env.aliyun`密钥字段已改为`DASHSCOPE_API_KEY`，密钥值不变。
客户端只对阿里云域名采用该字段，其他服务继续使用各自的密钥。

用官方OpenAI SDK重测，去掉项目系统提示词与temperature参数仍返回403。
按文档使用`max_completion_tokens=32`与`extra_body={"enable_thinking": false}`：

| 入口 | HTTP | 错误码 |
|---|---:|---|
| 用户提供的业务空间专属域名 | 403 | AccessDenied.Unpurchased |
| 官方北京旧域名dashscope.aliyuncs.com | 400 | Arrearage |

[官方错误说明](https://help.aliyun.com/zh/model-studio/error-code)将Arrearage解释为账号欠费导致访问拒绝。
因此先核对密钥所属账号的账单、欠费或余额状态；恢复正常后还需验证指定业务空间和模型授权。
当前证据不能保证解决计费后403一定消失。未自动开通或付费，仍保留用户指定模型和专属入口。

复现脚本使用官方SDK，安全读取本地配置，无需在命令中粘贴密钥：

```bash
uv run --with openai python scripts/verify_aliyun_api.py
uv run --with openai python scripts/verify_aliyun_api.py --legacy
```

脚本只输出无密钥的响应诊断，失败返回非零退出码，SDK不自动重试。
这是独立配置检查，脚本的32-token参数不修改项目1024-token生成配置。
项目会读取`.env.aliyun`；如果单独运行仅含`os.getenv`的官方示例，需要自行加载环境变量，
Python和OpenAI SDK不会自动读取该文件。

[SDK实测与配置审计](../evals/infra-official-v1-reviewed/results/aliyun-config-audit-20261001.json)
单独保存；未启动新的Qwen正式评测，既有300条DeepSeek基线与46条部分实验未覆盖。
