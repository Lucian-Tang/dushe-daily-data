# Vibe Coding 调研报告 — 早报摘要生成器 Demo

项目：早报摘要生成器 Demo | 周期：2 周
团队：Thomas（产品）、Stephen（研发）| 协调：Lucia
创建时间：2026-05-07

## 1. 调研背景

- Vibe Coding（Karpathy 2025 年提出，Collins 年度词汇）
- 核心思路：自然语言描述需求 → AI 实现 → 人负责判断和审美
- 调研目的：用真实项目验证 vibe coding 在团队协作中的可行性、效率和坑点
- 工具链待选：Cursor、Claude Code、GitHub Copilot 等

## 2. 团队构成与分工

| 角色 | 负责人 | 职责 |
|------|--------|------|
| 产品 | Thomas | 需求定义、PRD 编写、验收标准、产品评估 |
| 研发 | Stephen | 技术选型、AI 协作编码、工程化落地 |
| 协调 | Lucia | 文档推进、流程跟踪、报告汇总 |

## 3. PRD：早报摘要生成器 v0.1

### 产品定位
每天自动采集指定信息源的更新内容，AI 生成摘要，推送到飞书群。

### 功能清单
- P0：RSS 源采集（3-5 个源：HN / 知乎日报 / V2EX）、内容去重、AI 摘要（每篇 <50 字中文）、早报格式化（Markdown）、飞书消息推送
- P1：cron 定时触发
- P2：自定义关键词配置

### 验收标准
1. 输入 3 个 RSS 源 → 输出格式化早报
2. 早报含：日期 + 链接 + AI 摘要 + 来源
3. 飞书格式清晰可读
4. 无重复文章
5. 端到端跑通

### 非功能需求
- 单次运行 < 60 秒
- 单源失败不影响其他源
- 输出含执行时间标记

### 工具选型建议
- IDE: Claude Code / Cursor
- 语言: Python / Node.js
- 采集: Feedparser（RSS 优先）
- AI 摘要: OpenClaw LLM 复用
- 输出: 飞书消息

## 4. 工具选型

待填写

## 5. 流程设计

待填写

## 6. 实践记录

Day 1：
Day 2：
Day 3：

## 7. 技术与产品评估

### 技术侧（Stephen）
待填写

### 产品侧（Thomas）
待填写

## 8. 结论与建议

待填写

## 附录

- 参考链接：https://feishu.cn/docx/L020d3qaqotk5kxgIKicCAB2nLf
- 参考资料：vibevibe.cn、GitHub vibe coding repos
