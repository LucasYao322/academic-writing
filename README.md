# Academic Writing

把研究问题、证据和结论写清楚的中文学术写作插件。整合学术表达、反防御性写作和自然行文规则，支持润色、重写、压缩与审校。

v1.1.0 采用三个顺序阶段。Anti-Defensive Writing 指导论证，Humanizer 执行润色，最后对照原文复核事实。两个上游项目的规则已蒸馏进本插件，不需要额外安装，也不自动调用第二个模型。

同一份 [Skill](skills/academic-writing/SKILL.md) 供 Codex、Claude Code 和支持 Agent Skills 的工具使用。插件本身只有指令和参考材料，无运行时依赖、MCP 服务或账号要求。

## 默认行为

- 正文只用逗号和句号，删除装饰符号，将括号等符号承载的信息融入完整句子。
- 因果解释先交代原因或机制，再说明结果。全文围绕研究问题展开，结论回应开头。
- 用概念承接、信息递进和完整推理建立 coherence，连接词按需要使用。
- 明确贡献和证据，删除空泛的自我贬低，同时保留关键负面结果与必要限定。
- 减少模板化句式和空洞评价，保持学术语体、术语一致及可追溯的来源归属。
- 改写后核对数字、单位、比较方向、适用范围和结论强度。

技术符号优先无损转写。公式、引文或标识符无法无损转写时，按 Skill 的冲突处理流程保留信息并明确说明，不把损坏的数据交付为合格正文。用户也可以明确要求保留原有技术格式。

## 使用

安装后直接提出任务，并提供待处理文本和必要证据。

```text
使用 academic-writing 润色下面的摘要。保持原意，正文只用逗号和句号，只输出修改后的正文。

在这里粘贴摘要。
```

```text
使用 academic-writing 审校这段讨论。先列出推理跳跃和来源不明之处，再给出修改稿。

在这里粘贴讨论。
```

```text
使用 academic-writing 压缩这段结果。保留公式、引文和统计符号的原格式，其余正文只用逗号和句号。

在这里粘贴结果。
```

这些是自然语言请求，不是程序参数。没有安装插件时，可以直接复制 [精简提示词](prompts/academic-writing.txt)。

## 安装

见 [安装说明](docs/installation.md)，包括本地加载、公开 GitHub 仓库安装和通用 Skill 安装。公开仓库为 https://github.com/LucasYao322/academic-writing 。

项目包含 Codex 与 Claude Code 插件清单。它不代表已进入任一官方插件目录。清单和打包可以在本地校验，模型改写质量仍需结合目标模型与实际稿件审阅。

## 示例

以下为虚构教学材料，不代表真实实验。

原文。

> 虽然本方法仅在两个数据集上取得了提升，但这一突破性成果充分彰显了模型的巨大潜力，为未来研究开启了全新的篇章。

修改后。

> 本方法在两个数据集上取得了提升。现有结果支持其在这两个数据集上的有效性，其他数据集上的表现尚未验证。

更多例子见 [改写示例](skills/academic-writing/references/examples.md)。

## 项目结构

```text
skills/academic-writing/       核心 Skill 和按需读取的参考材料
prompts/academic-writing.txt   可直接粘贴的精简提示词
.codex-plugin/                Codex 插件清单
.claude-plugin/               Claude Code 插件与 marketplace 清单
.agents/plugins/              Codex marketplace 清单
scripts/                      静态校验与可复现打包
docs/                         安装和规则设计说明
licenses/                     参考项目的原始许可证
```

## 开发与验证

开发脚本使用 Python 3.10 或更新版本的标准库。

```bash
python scripts/validate.py
python scripts/build.py
```

构建产物位于 `dist/`。具体打包范围和验证边界见脚本输出与 [安装说明](docs/installation.md)。自动检查验证项目结构与包装，不判断研究结论是否真实。

## 来源与许可

本项目根据需求重新组织规则，参考 [Anti-Defensive Writing](https://github.com/Adkid-Zephyr/anti-defensive-writing-Skill) 和 [Humanizer](https://github.com/blader/humanizer)。采用贡献聚焦、自然表达与事实核对等原则，并针对学术场景调整规则。选择性省略关键不利证据、根据结果随意更换比较口径等做法不属于本项目的写作规则。

项目使用 [MIT 许可证](LICENSE)。来源版本、设计取舍与第三方许可见 [NOTICE](NOTICE.md)、[规则设计](docs/design.md) 和 [贡献说明](CONTRIBUTING.md)。
