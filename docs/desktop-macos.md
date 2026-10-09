# macOS 悬浮问答助手 · Infra Lens

Infra Lens 是本地知识问答助手：一个约 64 像素、可拖动的置顶悬浮球。
点击小球或按 `⌃⌥Space` 展开或收起对话面板；位置会在重启后保留。
Dock 和菜单栏也能找到应用。输入问题后，它用混合检索从已导入文档中找证据，
调用本机 Ollama 生成中文回答，并显示可核对的来源。支持连续追问、查看引用、
导入文件或文件夹和新建对话；对话保存在本机索引目录下的 SQLite 数据库中。

## 本机运行

需要 macOS、Swift 命令行工具、Python 3.12+、`uv` 和本机 Ollama。
桌面版默认使用真实 BGE 检索模型、bge-reranker-base 重排和 Ollama 的
`qwen3:4b` 回答模型。
在仓库根目录执行：

```bash
ollama pull qwen3:4b
uv sync --all-extras
zsh desktop/macos/build.sh
open dist/InfraLens.app
```

运行前确保 Ollama 已启动。默认使用独立索引 `data/desktop-bge`。
首次使用时通过 **导入文件或文件夹** 建立自己的索引，或使用已准备好的 BGE 索引。
输入问题后回车或点击 **发送**。关闭面板后悬浮球仍在，点击它即可再次打开；
也可从菜单栏图标或 `⌃⌥Space` 打开。
窗口连接成功后会在后台预热 BGE 检索和 Ollama 回答模型，状态栏显示完成情况；
立即提问仍可能等待首次加载。Ollama 在最后一次问答后保留模型 10 分钟，以便继续追问。
从菜单栏选择退出时，本地 API 进程会一起停止。构建产物位于被 Git 忽略的 `dist/`。

若已有其他**单独的 BGE 索引**，可在构建时指定：

```bash
INFRA_DESKTOP_INDEX="$PWD/data/text-v2" zsh desktop/macos/build.sh
open dist/InfraLens.app
```

不要把 demo 索引目录用于 BGE 模式；索引指纹会拒绝不兼容配置。
可设置 `INFRA_DESKTOP_PORT` 改变本地服务端口，默认 `18774`。
如需对照实验，可在构建时设置 `INFRA_DESKTOP_RERANK=0` 关闭重排。重排通常提升
证据排序，但预热时需要加载额外模型，提问耗时也会增加。
服务只绑定 `127.0.0.1`；启动和异常信息写入 `data/desktop-backend.log`。
移动仓库或改变上述构建配置后，重新运行 `build.sh`。

## 实现和范围

界面采用 SwiftUI，AppKit `NSPanel` 实现透明悬浮球与按需展开的紧凑面板，
Carbon 注册全局快捷键。悬浮球的呼吸动画直接由 SwiftUI 绘制。
应用启动仓库现有 Python API，通过 `/health`、`/warmup`、`/ingest`、`/chat` 和
`/conversations/{id}` 交互；问答链路执行混合检索、有限历史上下文拼接、
本地生成、引用 ID 校验，并返回检索及生成耗时轨迹。找不到证据时会提示补充文档。
父进程退出时守护脚本关闭 API，避免留下占用端口的后台服务。

交互参考开源的 [PopChat](https://github.com/lec77/PopChat)（MIT）菜单栏悬浮面板设计。
本仓库的界面和对接代码是独立实现，没有复制其聊天、账号或模型调用代码。
当前构建依赖本机仓库与 `.venv`，适合开发和本机使用；尚未打包独立安装器、签名或公证。
导入大型语料仍由现有同步 API 处理，窗口会显示忙碌状态。
引用校验只保证 ID 来自本轮检索证据，不能证明回答的每项表述都被证据支持；
重要内容仍应打开来源核对。当前没有 Salvo 中的业务意图分类、工单转人工或自动评测闭环。
