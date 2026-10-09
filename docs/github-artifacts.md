# GitHub 中的大型实验记录

2026-10-09 同步包含项目源码、测试、桌面端、分析报告、实验协议、审核模板和实验记录。
超过 10MiB 的 25 个冻结评测文件以无损 gzip 副本存放在
`artifacts/github-large-evals/`，避免单文件超过 GitHub 普通 Git 限制。
本机原文件保留且未改写，历史实验清单及其 SHA256 也未修改。

归档清单为 [manifest.json](../artifacts/github-large-evals/manifest.json)，逐文件记录
原路径、原始字节数及 SHA256，以及压缩文件路径、字节数及 SHA256。
压缩副本保留原目录层级并增加 `.gz` 后缀。

## 克隆后的还原

在仓库根目录运行，仅使用 Python 标准库：

```bash
python3 scripts/restore_github_artifacts.py
```

脚本验证压缩文件和解压内容的大小与 SHA256，恢复到原始路径。
已存在的原文件只校验，不覆盖；内容不匹配即失败，避免改写冻结结果。
还原文件被 `.gitignore` 精确列出，后续提交仍使用压缩副本。
先还原文件，再执行引用原始路径的实验审计或重放命令。

仅检查全部压缩副本，以及本地已存在的原文件：

```bash
python3 scripts/restore_github_artifacts.py --verify-only
```

## 保留在本地的文件

凭据 `.env`、`data/` 语料与索引、模型缓存、虚拟环境、构建产物及
`.workbuddy-ai/` 内部笔记不上传。示例环境配置保留占位符。
独立人工审核仍为 pending；同步代码和实验记录不代表实验配置已通过采用门槛，
也不改变当前问答链路或默认配置。
