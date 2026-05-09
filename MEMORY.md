# MEMORY.md — Lucia 的长期记忆

## Boss 信息
- **名字:** Lucian
- **时区:** Asia/Shanghai (GMT+8)
- **偏好:** 直接、不废话、要干货
- **所在地:** 广州（常往返上海）

## 当前团队
- **Lucia (我)** — 主控 Agent，负责分活、监控、汇报
- **Thomas** — 产品经理 Agent，负责需求分析、竞品调研、PRD
- **Stephen** — 研发工程师 Agent，负责架构、代码、技术选型

## 当前项目
- 热点早报采集器：HN/V2EX/知乎日报/GitHub Trending，端到端 39s，已推群
- Twitter 采集：所有方案均需账号凭证，待 Lucian 提供

## 技术栈
- Gateway: OpenClaw 2026.4.21
- 主模型: DeepSeek V4 Pro
- 降级: MiniMax M2.7 → MiniMax M2.7-highspeed
- 飞书 Bot: 4 个账号（lucia/product/engineering/default）
- 任务看板: 飞书多维表格 (app_token=RIYebA1R7aKZ02sCHBhc9Twxntf)

## 模型使用原则
- 主 Agent 对话: deepseek-v4-pro（品质优先）
- Subagent/Cron: minimax-m2.7（成本优先，包月不浪费）
- **Stephen（研发）：deepseek-v4-pro**（代码/架构需品质模型）
- Spawn subagent 时必须传 model 参数
- 复杂子任务（需深度推理）例外: 使用 `deepseek-v4-pro`

## 重要决策
- 2026-05-07: 删除冗余 secretary agent，合并进 Lucia
- 2026-05-07: 三个主 agent 统一用 DeepSeek V4 Pro，subagent 降级用 MiniMax
- 2026-05-07: 状态文件格式统一 (role/state/task/updated_at/blocker)
- 模型选择原则: 主 agent 用品质模型，subagent/cron 用便宜模型

## 行为规范
- 主动但不骚扰，每天 1-3 次随机搭话
- 群聊不抢话，有需要时再开口
- 不在 23:00-08:00 发消息
- 心跳时同步 Bitable 任务队列
