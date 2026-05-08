# Multica 评估报告

**评估人：** Stephen（研发工程师）
**日期：** 2026-05-09
**目标：** 评估 Multica 智能体看板能否替代当前飞书 Bitable 任务管理

---

## 1. 系统概况

### 1.1 Multica 是什么

Multica（[github.com/mvanhorn/multica](https://github.com/mvanhorn/multica)）是开源的托管智能体平台，定位是"把 AI coding agents 变成真正的团队成员"。

核心特性：
- **Issue = 任务**：在 Web 看板创建 Issue，分配给 Agent 自动领取执行
- **多 runtime 支持**：OpenClaw、Claude Code、Codex、OpenCode、Hermes
- **实时进度流**：通过 WebSocket 实时推送 agent 执行状态
- **技能复用**：解决方案可沉淀为团队级可复用技能
- **多 Workspace 隔离**

### 1.2 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 16 (App Router) |
| 后端 | Go (Chi + gorilla/websocket) |
| 数据库 | PostgreSQL 17 + pgvector |
| Agent Runtime | 本地 Daemon（CLI） |

---

## 2. 部署复杂度评估

### 2.1 自部署（推荐方案）

**一行命令部署：**
```bash
curl -fsSL https://raw.githubusercontent.com/multica-ai/multica/main/scripts/install.sh | bash -s -- --with-server
```

实际做三件事：
1. 克隆仓库
2. 启动 Docker Compose（PostgreSQL + Go Backend + Next.js Frontend）
3. 安装 multica CLI

**门槛：**
- 需要 **Docker + Docker Compose**
- 需要每台运行 agent 的机器安装 multica CLI
- 每台机器需要预装 OpenClaw/Claude Code/Codex 等 CLI

**初始登录：** 访问 http://localhost:3000，任意邮箱 + 验证码 `888888`（非生产环境）

### 2.2 Multica Cloud（无需自部署）

直接使用 multica.ai/app，CLI 配置连接云端，省去运维。

### 2.3 与 OpenClaw 集成方式

Multica 的 OpenClaw 集成是 **local daemon 检测 PATH 上的 openclaw CLI**，然后通过 Multica server 统一管理任务分发。

也就是说：
- OpenClaw agent 运行在本地机器上
- Multica 作为任务队列 + 看板，驱动 OpenClaw 去执行
- 人在 Multica 看板上分配任务，OpenClaw agent 自动领取

---

## 3. 当前飞书 Bitable 方案分析

**表名：** Lucia 任务看板 V2
**总任务数：** 113 条
**团队规模：** 4 人

**现有字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| 状态 | SingleSelect | pending / assigned / in_progress / completed / failed |
| 负责人 | User（多人） | 有 |
| 产出链接 | URL | 有 |
| 创建时间 | DateTime | 有 |
| 背景描述 | Text | 有 |
| task_id | Text | 有 |
| 卡滞时间 | DateTime | 有 |
| 类别 | SingleSelect | 调研/开发/报告/运维/其他 |
| 模型 | SingleSelect | deepseek-v4-pro / minimax-m2.7 等 |
| 截止时间 | DateTime | 有 |
| 归档 | Checkbox | 有 |
| 优先级 | SingleSelect | P0 紧急 / P1 重要 / P2 普通 |

**现状：**
- 所有任务都是**手动录入**（非 AI 自动同步）
- 4 人团队通过飞书内嵌表格协作
- 有归档习惯（已完成任务打归档标记）
- 任务有优先级、分类、模型归属等定制字段

---

## 4. 对比分析

### 4.1 优势对比

**Multica 优势：**

| 优势 | 说明 |
|------|------|
| AI agent 自动领取任务 | 任务分配给 agent 后自动执行，无需手动同步状态 |
| 实时进度流 | WebSocket 实时看到 agent 在做什么 |
| 多 agent 统一管理 | 一个看板同时管 OpenClaw/Claude Code/Codex 等 |
| 技能复用 | 解决方案可沉淀，团队能力可叠加 |
| 无缝衔接 OpenClaw | openclaw 在 PATH 上即可被 Multica 感知 |

**Bitable 优势：**

| 优势 | 说明 |
|------|------|
| 无需任何部署 | 飞书原生，直接用 |
| 天然支持团队协作 | 飞书权限体系、评论、@ 成员 |
| 字段灵活 | 优先级、模型、类别等业务字段完全自定义 |
| 移动端体验好 | 飞书 App 随时查看 |
| 已有数据积累 | 113 条任务，完整的项目历史 |
| 中文友好 | 全中文界面，飞书通知 |
|Webhook/自动化| 可通过 Bitable API 做自动化| |

### 4.2 Multica 劣势（对当前团队）

| 劣势 | 说明 |
|------|------|
| **没有移动端看板** | 只有 Web，团队成员不一定能随时打开 |
| **不支持人工任务分配** | 本质是给 AI agent 用的，人工任务没有原生支持 |
| **迁移成本高** | 113 条历史任务、14 个字段需要迁移 |
| **仍是手动维护** | 如果只用 Multica 的看板功能（不连接 agent），和 Bitable 差不多 |
| **需要额外维护** | Docker 服务、数据库、CLI 安装 |
| **团队使用习惯** | 4 人团队已在飞书生态中，切换有摩擦 |
| **优先级/分类字段** | 需要自定义字段映射，pgvector 等高级功能不一定用得上 |

### 4.3 核心判断：你的团队真正需要什么？

分析 Bitable 历史任务：
- 所有 113 条任务几乎都是 **AI agent 自己完成的**（唐柳生、Stephen 等是 AI agent 的名字，不是真人）
- 任务包括：调研、报告、开发、复盘文档等
- 当前 Bitable 实际上是 **Lucia（主 agent）在管理 AI sub-agents 的任务记录**

**关键洞察：**

> Multica 的核心价值是让**没有 CI/CD 能力的 AI agent**（Claude Code/OpenClaw）像团队成员一样在看板上出现、领取任务、报告进度。而你们当前已经在用 OpenClaw 的 sub-agent 机制手动管理任务状态。

如果目标是**让 AI agent 自动同步状态到看板，无需手动维护**：

- Multica 能做到（通过 Daemon 自动同步 agent 状态）
- 但你们需要**把任务分配链路从 sessions_send 改成 Multica issue 分配**

如果目标只是**让团队成员（真人）看到任务列表**：

- Bitable 更轻，Bitable 已经能工作

---

## 5. 迁移成本估算

| 成本项 | 估算 |
|--------|------|
| 数据迁移 | 113 条记录 × 14 字段需手动或脚本迁移 |
| 字段映射 | Multica Issue 字段 vs Bitable 字段需手动对齐 |
| 团队再学习 | 4 人习惯飞书，切换有 1-2 周适应期 |
| 部署维护 | Docker 服务需要有人维护（虽然简单） |
| AI agent 集成 | 需要改造现有 agent 调用链路，走 Multica issue |
| 通知体系 | 飞书原生通知 vs Multica 内置通知 |

**总体迁移成本：中等偏高（预计 1-2 人天）**

---

## 6. 建议

### 建议：**观望（2-3 个月后再评估）**

**理由：**

1. **当前 Bitable 工作正常**：113 条任务，4 人团队（实际是 agent 协作），没有痛点
2. **Multica 太新**：从 GitHub 看还是早期项目（star 数量和社区规模未知），生产环境风险不明
3. **集成收益有限**：如果只是用看板功能，飞书 Bitable 够用；如果要用 agent 自动同步，需要改造现有架构，改造成本不小
4. **Multica Cloud 未稳定**：自部署虽然简单但需要维护，Cloud 版还年轻
5. **不是替换关系，更像补充**：Multica 适合管理 **AI agent 执行层**，Bitable 适合 **人工协作管理层**。你们目前 AI agent 任务占大多数，Bitable 已经承担了管理职责

**如果非要迁移，最值钱的场景：**
- 如果未来团队引入更多 AI agent（不只是 OpenClaw），Multica 作为统一管理层有价值
- 如果想要 agent **自动更新任务状态**（无需人工同步），值得投入

**立即可行的优化（不动系统）：**
- 给 Bitable 配一个简单的脚本，定时将 OpenClaw sub-agent 的 session 状态同步到 Bitable（减少手动维护）

---

## 7. 总结

| 维度 | Bitable | Multica |
|------|---------|---------|
| 部署难度 | ⭐ 无（云服务） | ⭐⭐⭐ Docker 一键但需维护 |
| OpenClaw 集成 | 需手动/API | 原生（Daemon 自动检测） |
| 实时进度 | ❌ 无 | ✅ WebSocket 实时 |
| 多 agent 支持 | 需二次开发 | ✅ 原生 |
| 移动端 | ✅ 飞书 App | ❌ Web only |
| 团队协作 | ✅ 完善 | ⚠️ 基础 |
| 数据迁移成本 | — | 高（113 条） |
| 生产稳定性 | ✅ 成熟 | ⚠️ 早期 |

**最终建议：不换，继续用 Bitable，关注 Multica 社区发展，等 v1.0 再评估。**