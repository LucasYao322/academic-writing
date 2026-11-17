# 安装与发布

本仓库包含同一个 Skill 的 Codex 和 Claude Code 包装。选择一种安装方式即可，不要同时通过插件和独立 Skill 安装同名内容。插件无需 MCP 服务、API 密钥或运行时依赖。校验和打包脚本使用 Python 3.10 或更新版本的标准库。

## Codex

在仓库根目录运行下列命令，将当前目录作为本地 marketplace 注册，再安装插件。安装会由 Codex 正常更新当前用户的插件配置和缓存。

```sh
codex plugin marketplace add .
codex plugin add academic-writing@academic-writing-marketplace
```

重新开始会话后，通过技能选择器选择 academic-writing，或者在提示中写明使用 academic-writing 润色论文。可用 `codex plugin list --marketplace academic-writing-marketplace` 检查安装结果。较旧客户端缺少 `plugin` 子命令时，请先更新客户端，或使用下文的独立 Skill 方式。

从公开 GitHub 仓库安装。

```sh
codex plugin marketplace add LucasYao322/academic-writing
codex plugin add academic-writing@academic-writing-marketplace
```

## Claude Code

本地临时加载，不写入永久插件安装配置。

```sh
claude --plugin-dir /absolute/path/to/academic-writing
```

在 Claude Code 中调用 `/academic-writing:academic-writing`。如需永久安装，可在仓库根目录运行。

```sh
claude plugin marketplace add .
claude plugin install academic-writing@academic-writing-marketplace
```

从公开 GitHub 仓库安装。

```sh
claude plugin marketplace add LucasYao322/academic-writing
claude plugin install academic-writing@academic-writing-marketplace
```

Claude Code 提供额外的宿主校验命令，可在已安装客户端的机器运行。

```sh
claude plugin validate .
```

## 独立 Skill 与普通聊天

支持 Agent Skills 的客户端可以直接导入整个 `skills/academic-writing/` 目录。必须保留其中的 `references/`，不要只复制 SKILL.md。具体保存位置以客户端文档为准。

普通聊天可以复制 [精简提示词](../prompts/academic-writing.txt)，随后提供原文和写作要求。完整规则以 [SKILL.md](../skills/academic-writing/SKILL.md) 为准。

## 验证与打包

在仓库根目录运行。

```sh
python scripts/validate.py
python -m unittest discover -s scripts/tests -v
python scripts/build.py
```

输出位于 `dist/`。

- `academic-writing-1.0.0-source.zip` 包含一层 academic-writing 目录，适合解压为 GitHub 项目。
- `academic-writing-1.0.0-plugin.zip` 在 ZIP 根目录放置插件文件，适合需要插件 ZIP 的导入界面，也可解压后本地安装。
- `SHA256SUMS` 提供两个压缩包的 SHA256 校验值。

两种压缩包的文件内容相同，只有根目录布局不同。构建使用显式文件白名单，固定 ZIP 时间戳和权限，不包含 Git 历史、缓存、环境配置或未列入清单的稿件。新增需要发布的文件后，需更新 `scripts/validate.py` 中的 `DISTRIBUTION_FILES`。

静态校验会检查本项目使用的 manifest 字段、版本一致性、路径、Skill 元数据、本地 Markdown 链接和精简提示词的标点。它不是宿主完整 JSON Schema 的实现，也不证明语言模型遵守了全部写作规则。宿主实际安装和写作效果需分别验证。

## 开源发布

将仓库推送至你有权限的公开 GitHub 仓库即可提供 marketplace 安装。发布前确认 [来源说明](../NOTICE.md) 和两份上游许可随仓库保留，再将公开地址补入 README。GitHub 发布不会自动将插件上架到 OpenAI 或 Anthropic 的官方目录。官方目录提交是独立流程。

项目提供只读权限的 GitHub Actions 验证工作流。另有手动触发的 Package release 工作流，以 contents write 权限为既有 v1.0.0 Release 上传插件包和校验值，不创建仓库。后续版本需更新发布工作流中的版本引用。

## 规范依据

包装依据以下官方资料及当前 Codex CLI 的 `plugin --help`，核对日期为 2026 年 11 月 17 日。

- [OpenAI 插件包装与 marketplace 文档](https://developers.openai.com/plugins/build/plugins)。本版采用仍受支持的 `.codex-plugin/plugin.json` 兼容布局。
- [Claude Code 插件清单](https://code.claude.com/docs/en/plugins-reference)。Skill 使用标准 `skills/` 发现路径。
- [Claude Code marketplace 文档](https://code.claude.com/docs/en/plugin-marketplaces)。本地插件 source 相对于仓库根目录解析。

此项目没有依赖第三方仓库清单作为格式规范，也没有宣称已经通过平台上架审核。
