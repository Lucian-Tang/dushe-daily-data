# OpenClaw Skill 生态调研报告

> 产品视角 | 2026-05-07 | 调研人：Thomas

---

## 1. Skill 体系概述

### 什么是 Skill

Skill 是 OpenClaw 的能力扩展单元。本质上，它是一套结构化的**操作规范文档 + 可执行脚本 + 参考资料**的组合，使 AI Agent 在特定领域具备可复用、可共享的标准化操作能力。

Skill 独立于主程序维护，通过描述文件（SKILL.md）声明触发条件和使用方式，AI 在执行任务时自动匹配对应的 Skill。

### 目录结构

```
~/.openclaw/workspace/skills/<skill-name>/
├── SKILL.md          # 核心定义文件（必须）
├── _meta.json        # 元数据：slug、版本、发布者
├── scripts/          # 可执行脚本（如 fetch_trends.py）
├── references/       # 参考文档（API 文档、权限说明等）
└── assets/          # 静态资源（图片、配置模板等）
```

**SKILL.md** 是核心，包含：
- `description` — Skill 用途描述，也是 AI 触发匹配的关键词来源
- `metadata` — 依赖声明（所需命令、环境变量、npm 包等）
- 使用说明和工作流示例

---

## 2. 当前 Skill 生态（22 个已安装）

按功能分为四大类：

### 🛠 Web 工具（3 个）
| Skill | 功能 |
|---|---|
| `agent-browser-clawdbot` | 无头浏览器自动化，基于 accessibility tree 的确定性元素交互 |
| `openclaw-tavily-search` | Tavily AI 搜索 API，支持网页搜索和结构化摘要 |
| `web-tools-guide` | Web 工具策略指南（强制前置规则） |

### 📱 社交媒体 / 舆情（6 个）
| Skill | 功能 |
|---|---|
| `hot-news-aggregator` | 国内外科技/军事/社会新闻聚合，自动筛选要点 |
| `cn-trends-aggregator` | 百度/头条/V2EX/HN/GitHub 多平台热榜聚合 |
| `baidu-hot-monitor` | 百度热搜实时监控 |
| `douyin-hot` | 抖音热榜数据获取 |
| `twitter-collector` | 推特/X 指定用户推文采集（twscrape） |
| `web-hot` | 主流中文平台热搜榜单（微博/知乎/抖音等） |

### 📄 文档办公（4 个）
| Skill | 功能 |
|---|---|
| `feishu-doc-write` | 飞书文档写入规范（防子 agent 误报） |
| `tencent-docs` | 腾讯文档全套操作（创建/编辑/知识库/导入导出） |
| `feishu-doc` / `feishu-wiki` / `feishu-drive` / `feishu-perm` | 飞书各模块原生操作（内置 Tool 级别支持） |

### 🏗 运维 / 基础设施（4 个）
| Skill | 功能 |
|---|---|
| `github` | gh CLI 封装，操作 issues/PRs/CI runs |
| `tencentcloud-lighthouse-skill` | 腾讯轻量应用服务器管理 |
| `tencent-cos-skill` | 腾讯云对象存储 |
| `tencent-meeting-skill` | 腾讯会议 |

### 🧠 系统 / 记忆 / 管理（5 个）
| Skill | 功能 |
|---|---|
| `memory-manager` | 向量记忆管理（压缩检测/快照/语义搜索） |
| `memory-hygiene` | LanceDB 向量库清理维护 |
| `weather` | 天气查询（wttr.in + Open-Meteo，无需 API Key） |
| `automation-workflows` | 自动化工作流设计方法论 |
| `find-skills` / `skillhub-preference` | Skill 发现与安装引导 |

---

## 3. 热门 Skill 用法模式

通过分析现有 Skill，归纳出三种主流自动化模式：

### 模式 A：数据采集 → AI 分析 → 格式化输出

**代表 Skill：** `cn-trends-aggregator`、`hot-news-aggregator`、`baidu-hot-monitor`

```
[数据源 API/网页]
      ↓
[scripts/ 抓取脚本 → JSON/结构化数据]
      ↓
[AI 理解上下文，过滤噪音，提炼要点]
      ↓
[格式化输出：Markdown/表格/通知]
```

典型触发：用户说"给我今天的热榜"、"科技新闻有哪些"
输出形式：结构化 Markdown 摘要，带来源和时间戳

### 模式 B：定时监控 → 报警汇报

**代表 Skill：** 内置 Cron + `hot-news-aggregator` 组合

```
[Cron 定时触发]
      ↓
[数据源批量抓取]
      ↓
[AI 比对历史，识别异常/新增]
      ↓
[推送报告：飞书/微信/邮件]
```

典型场景：
- 每日早报（9:00 推送热榜汇总）
- 品牌舆情监控（关键词异动报警）
- 服务器告警（`tencentcloud-lighthouse-skill`）

### 模式 C：内容自动化创建

**代表 Skill：** `tencent-docs`、`feishu-doc-write`、`automation-workflows`

```
[用户意图输入]
      ↓
[AI 理解任务 → 调用文档 Skill 创建内容]
      ↓
[自动填充模板 / 格式化 / 写入目标平台]
```

典型场景：
- "帮我写一份产品周报，发送到飞书"
- "创建一个腾讯文档，格式是..."
- 自动生成日报/会议纪要/数据报告

---

## 4. Skill 分发渠道

### ClawHub（clawhub.com / clawhub.ai）

- **定位：** OpenClaw 官方 Skill 市场，全球化
- **规模：** 52.7k+ tools，180k+ 用户，12M+ 下载量
- **CLI：** `npm i -g clawhub`，支持 search/install/update/publish
- **特点：** 开源、Hash 版本校验、支持发布自己开发的 Skill

### SkillHub（中文优化）

- **定位：** 中文用户优先的 Skill 发现渠道，响应更快、合规性更好
- **策略：** 优先使用 `skillhub`，失败时 fallback 到 `clawhub`
- **工具：** 通过 `find-skills` / `skillhub-preference` Skill 封装调用

### 两者的区别

| 维度 | ClawHub | SkillHub |
|---|---|---|
| 目标用户 | 全球 | 中文用户为主 |
| 网络速度 | 一般（国际） | 更快（国内） |
| 内容合规 | 通用 | 本地化优化 |
| Skill 数量 | 非常丰富 | 相对有限 |
| 发布门槛 | 低 | 低 |

---

## 5. 产品视角的价值评估

### ✅ 高价值，值得推广的模式

**1. 数据聚合 + 智能摘要（模式 A）**
- 壁垒低、复用性极高，一个脚本可以服务多种场景
- 适合：舆情监控、竞品追踪、行业情报
- 建议：沉淀通用的 `fetch_*.py` 框架，新数据源快速接入

**2. 文档自动化（模式 C）**
- 与日常工作流深度绑定，用户感知价值明确
- 腾讯文档 + 飞书双平台覆盖，文档操作类 Skill 成熟度最高
- 建议：进一步封装"文档创建 → 内容填充 → 分享权限"的一键工作流

**3. 定时任务 + 推送（模式 B）**
- 真正实现"AI 不用提醒，自动值守"
- 典型价值场景：日报定时生成、会议提醒、舆情报警
- 建议：提供 Cron + Skill 的标准配置模板

### 🔧 适合自定义开发的场景

- **内部系统对接**：私有 API、定制化 CRM/ERP，没有通用 Skill
- **垂直行业数据源**：行业专属媒体、数据平台
- **特定审批流**：需要与内部流程深度绑定的文档操作
- **低代码平台集成**：公司内部的飞书审批/腾讯自建应用

> **原则：** 通用能力用现成 Skill，差异化能力自建。自建 Skill 时参考 `SKILL.md` 规范，便于沉淀和复用。

### ⚠️ 当前短板

1. **Skill 之间缺乏互操作机制**：Skill A 的输出无法直接触发 Skill B，需要 Agent 居中协调
2. **Cron 集成不够标准化**：定时触发 Skill 缺少统一配置界面
3. **Skill 版本管理**：多环境（开发/生产）下 Skill 版本一致性无法保障
4. **Skill 调试体验**：Skill 执行失败时，排查路径不清晰

---

## 6. 建议

### 团队如何高效利用 Skill 体系

#### 短期（1-2 周可落地）

1. **建立 Skill 资产清单**
   - 整理现有 22 个 Skill，按部门/场景打标签
   - 明确每个 Skill 的 Owner 和适用场景

2. **推广"热榜早报"自动化**
   - 用 `cn-trends-aggregator` + Cron，每天 9:00 推送热榜摘要到飞书群
   - 零开发投入，立即感知价值

3. **文档操作标准化**
   - 确定"日常文档用腾讯文档，协作文档用飞书"的分工策略
   - 封装通用 Prompt 模板，减少每次的描述成本

#### 中期（1-2 个月）

4. **自建垂直场景 Skill**
   - 优先选高频、规则化、有明确输入输出的场景
   - 参考 `cn-trends-aggregator` 的脚本 + SKILL.md 结构快速开发

5. **完善 Cron + 推送机制**
   - 建立"定时任务配置表"：任务名 / 触发时间 / Skill / 推送渠道
   - 推广关键场景：舆情监控、服务器告警、日报生成

6. **Skill 开发规范落地**
   - 新 Skill 必须包含：SKILL.md + `_meta.json` + 至少一个测试用例
   - 发布前在 `clawhub` 或 `skillhub` 试运行，收集反馈

#### 长期

7. **构建团队私有 Skill 库**
   - 将内部系统对接封装为私有 Skill，积累团队资产
   - 通过 `clawhub publish` 或内部镜像分发

8. **推动 Skill 互操作设计**
   - 设计 Skill 间的标准化输入/输出格式
   - 探索 Skill 组合 DSL，降低多 Skill 编排复杂度

---

## 附录

### 快速参考：常用 Skill 触发词

| 想做的事 | 对应 Skill | 触发词 |
|---|---|---|
| 查天气 | `weather` | 天气 |
| 看热搜 | `cn-trends-aggregator` | 热榜、热搜、趋势 |
| 抓新闻 | `hot-news-aggregator` | 新闻、科技新闻、军事新闻 |
| 管飞书文档 | `feishu-doc` | 飞书、文档 |
| 管腾讯文档 | `tencent-docs` | 腾讯文档、在线文档 |
| GitHub 操作 | `github` | github、issue、pr |
| 自动化工作流 | `automation-workflows` | 自动化、工作流 |
| 找新 Skill | `find-skills` | 找技能、安装 skill |

---

*报告完成 | 调研人：Thomas | 2026-05-07*
