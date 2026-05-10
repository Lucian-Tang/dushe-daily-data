---
name: gzh-prohibited-word
description: 基于官方违禁词库实时同步，覆盖广告法、医疗美容、金融风险等10+类目，支持文本、文件、图片多形式检测，10秒内输出违禁词标红+替换建议+优化文案，帮你避开封号限流风险。

version: 1.0.0
tags:
  - wechat-official-account
  - compliance
  - content-moderation
  - python-script
dependency:
  python:
    - python-docx==1.1.0
    - beautifulsoup4==4.12.3
    - playwright==1.58.0
  system:
    - playwright install chromium
---

# 公众号违禁词检测

执行完整检测、分批询问、结果版式与文件交付前，**必须先读取并严格遵循**同目录 [references/core_workflow.md](references/core_workflow.md)（输出模板、输出铁律、示例与注意事项全文在该文件中）。

## 简介

面向需要在**微信公众号**场景下预审文案合规的作者与运营：一键识别违禁词、给出可替换说法，并生成仅替换违禁词后的优化稿。

通过本 Skill，你可以：

- 🔍 **合规透视**：对原文中标出的违禁词做红字标注（HTML），并汇总类型与数量（平台固定为公众号）。
- 💡 **可执行改写**：逐词给出替换建议与理由；优化文案仅替换违禁词，允许为通顺微调连接成分并用蓝色标出。
- 📄 **可下载交付**：在检出违禁词时，将无 HTML 的纯文本优化稿写入 `./公众号_优化文案_{随机6位数字}.txt` 并以卡片发送（细则见核心文档）。

适用于公众号运营、新媒体编辑、品牌内容审核等需要在发文前自查违禁表述的场景。运行依赖见 frontmatter `dependency`；在项目**根目录**执行下文命令。**首次部署**须配置违禁词检测 API 接入点：设置 `GZH_SENSITIVE_WORD_API_HOST`，或使用 `GZH_SENSITIVE_WORD_API_CONFIG` / `scripts/gzh_sensitive_word_api.json`（示例见 `scripts/gzh_sensitive_word_api.example.json`）；详见 [references/core_workflow.md](references/core_workflow.md)「前置准备」。

## 功能特性

### 核心能力

- **多输入源**：直接粘贴文本；或 TXT / DOC / DOCX 等文本类文件（脚本提取）；或网页 URL（Playwright 渲染，失败时脚本回退静态抓取）；图片需由模型先 **read_image** 仅提取文字再以文本检测。
- **一站脚本**：`scripts/check_sensitive_words.py`；`--content` / `--file` / `--url` **三者互斥**，单次只传其一；`--extract-only` 仅返回 `content` 与 `length`，用于长文分支判断。
- **字数规则（须可被模型识别）**：接口单次 **3000** 字符；全稿建议上限 **10000** 字符——超过 10000 **不检测**并提示用户手动分批；3001～10000 **必须先问用户**选「只测前 3000」「按 3000 分批全测」「取消」，**禁止未答复继续**。
- **固定交付形态**：有违禁词时按核心文档的三板块输出；无违禁词（`word_count=0`）仅输出检测结果板块且不写文件（见核心文档）。

### 特色亮点

- **分批切割**：用户选择分批时，在**自然断句**处切批，每批 ≤3000 字符；多批完成后须**按原文顺序汇总**一份完整优化 txt，不得漏批。
- **脚本侧容错**：网络 5xx / 超时等由脚本自动重试（最多 2 次）；英文单词内子串误命中由脚本过滤，模型无需再判。

## 使用指南

### 基础使用（5 步）

#### 第 1 步：加载核心流程

打开 [references/core_workflow.md](references/core_workflow.md)，对照其中的「操作步骤」「输出模板」「输出格式铁律」「注意事项」执行，不得删减板块或跳过写文件 / 发卡片（检出违禁词时）。

#### 第 2 步：识别输入类型并提取（如需）

| 用户给出 | 先做                                                                   |
| -------- | ---------------------------------------------------------------------- |
| 纯文案   | 统计字符数，按 3000 / 10000 规则分支                                   |
| 文本文件 | `python scripts/check_sensitive_words.py --file=<路径> --extract-only` |
| 网页     | `python scripts/check_sensitive_words.py --url=<URL> --extract-only`   |
| 图片     | read_image 仅取文字，再按文本流程                                      |

未明确是文件还是 URL 时：**追问**或依据附件类型判断；勿臆造路径。

#### 第 3 步：按字数分支调用检测

- ≤3000：直接 `python scripts/check_sensitive_words.py --content="..."`（或用文件/Web 提取后的全文若 ≤3000）。
- 3001～10000：先发核心文档规定的 **1 / 2 / 3** 选项提问，**等待回复**后再调用脚本。
- \>10000：仅提示用户手动分批，**不执行**脚本检测。

分批检测时每批使用 `--content="该批正文"`；禁止单次混传 `--content` 与 `--file`/`--url`。

#### 第 4 步：解析 JSON 并按模板输出

严格使用核心文档中的三板块标题与顺序；**禁止**直接打印原始 JSON。`word_count=0` 时仅输出第一板块合规提示（见核心文档）。

#### 第 5 步：写入优化文案文件（有条件）

检出违禁词后：生成 `./公众号_优化文案_{随机6位数字}.txt`（内容与「建议优化文案」一致但去除全部 HTML），**实际落盘**并以**文件卡片**发给用户；分批时汇总全文后再写一份。

**对话示例**

> **用户**：帮我看下这篇公众号草稿有没有违禁词。（粘贴 800 字）
> **助手**：已按公众号规则检测；随后输出三板块；若有违禁词则写入 `公众号_优化文案_xxxxxx.txt` 并发送下载卡片。

> **用户**：这个 docx 帮我过一遍。（上传文件）
> **助手**：先用 `--file=... --extract-only` 取全文与 length，再按 3000/10000 规则决定是否追问 1/2/3，再检测。

### 常用命令速查

| 命令示例                                                                           | 作用                            |
| ---------------------------------------------------------------------------------- | ------------------------------- |
| `python scripts/check_sensitive_words.py --content="正文"`                         | 直接检测 ≤3000 字片段或某批正文 |
| `python scripts/check_sensitive_words.py --file=/path/to/a.docx --extract-only`    | 仅提取文本与 length             |
| `python scripts/check_sensitive_words.py --file=/path/to/a.txt`                    | 文件路径检测（短文本）          |
| `python scripts/check_sensitive_words.py --url=https://example.com --extract-only` | 仅抓取网页正文与 length         |
| `python scripts/check_sensitive_words.py --url=https://example.com`                | URL 短正文直接检测              |

说明：`--content`、`--file`、`--url` **每次只用其一**；检测平台在脚本内固定为**公众号**，不可切换。

## 使用场景

| 场景         | 角色        | 需求描述                   | 使用方式                                             |
| ------------ | ----------- | -------------------------- | ---------------------------------------------------- |
| 发文前自检   | 公众号运营  | 避免推文因违禁词被拦或删改 | 粘贴正文或上传 DOCX；按输出调整替换；下载优化 txt    |
| 落地页抽查   | 市场 / 增长 | 检查活动页文案是否踩线     | 提供 URL；`--extract-only` 后按字数规则检测          |
| 批量物料预审 | 新媒体编辑  | 多篇短文或单篇长文分段合规 | 长文触发 1/2/3 询问；选 2 则按 3000 字分批并汇总 txt |
| 图片海报字稿 | 设计师协作  | 图上文字需可达规           | read_image 提取字幕后按 `--content` 流程             |

## 注意事项与边界

- **必读**：输出样式、铁律、零命中时的输出范围、文件命名与卡片发送等**完整规则**以 [references/core_workflow.md](references/core_workflow.md) 为准；本页参数摘要不能替代该文档。
- **API 配置**：检测请求发往由部署方配置的 HTTPS 端点（环境变量或 `scripts/gzh_sensitive_word_api.json`），公开 Skill 包内不含第三方域名；未配置时脚本拒绝调用并返回说明，避免误连未知服务。
- **数据与诚实**：结果来自脚本调用的检测接口；不得伪造 `word_count`、违禁词列表或 JSON 字段。
- **字数阈值**：**3000**（单次调用上限 / 分批粒度）、**10000**（自动流程上限，超出中止）；**3001～10000 必须先用户选择**，不得默认替用户选。
- **文件类型**：支持常见文本与 Word；**不支持 PDF**；图片不走 `--file` 文字提取路径，须 OCR 后走 `--content`。
- **执行环境**：仅在**主 Agent**执行；子 Agent / 子任务中不要启用本 Skill。
- **后续对话**：检测完成后用户若追问替换词、复测或规则解释，可正常应答（见核心文档「注意事项」末条）。
