# OpenClaw 内核分析 & 隐藏能力挖掘

> Stephen（超时后 Lucia 代补） | 2026-05-08

---

## 一、我们当前用到的 OpenClaw 能力

| 能力 | 用途 | 深度 |
|------|------|------|
| `cron` | 13 个定时任务 | 重度 |
| `gateway` | WebSocket 服务 | 默认配置 |
| `message send` | 飞书消息推送 | 频繁 |
| `sessions_spawn` | Subagent 分发 | 重度 |
| `feishu_doc` | 飞书文档读写 | 频繁 |
| `feishu_bitable` | 任务看板 CRUD | 轻度 |
| `memory_search/memory_get` | 记忆检索 | 中度 |
| `skills` | 外部 Skill 引入 | 轻度（仅 feishu-sync） |

---

## 二、我们没用到但很有价值的隐藏能力

### 🔴 立即可用（P0）

**1. `openclaw tasks` — TaskFlow 持久任务系统**
- OpenClaw 内置了 TaskFlow，支持 durable background task state
- 当前我们用 Bitable + 手动 JSON 同步，TaskFlow 可以原生管理
- 支持：create/list/update/complete/fail，有检查点和重启机制
- **替代价值：** 省掉手动 Bitable 同步的心跳开销

**2. `openclaw hooks` — Agent 生命周期钩子**
- 支持 pre/post hooks，在 agent 处理前后执行
- **应用场景：** pre-upload 自动跑校验官 → 通过才允许上传
- 可以写在 `hooks/pre-upload.js` 里面

**3. `openclaw memory` — 记忆管理 CLI**
- 直接搜索、检查、重建索引
- **当前问题：** 我们只用 memory_search API，没做索引维护
- 定期 `openclaw memory reindex` 可以提升检索质量

### 🟡 2-4 周可探索（P1）

**4. `openclaw agents` — 独立 Agent 管理**
- 官方支持的 agent workspace 隔离、认证、路由
- **当前做法：** 我们用 `agents/{product,engineering,qa}/` 手动建目录
- 可能有标准化的 agent 配置 schema 我们没发现

**5. `openclaw mcp` — MCP 协议支持**
- Model Context Protocol（Anthropic 标准）
- 可以把我们的 cron scripts 封装成 MCP tools
- 对外暴露标准化的 tool 接口

**6. Build-in Skills 生态**
- OpenClaw 自带 45+ 内置 skills（1password, github, weather, etc.）
- 我们只用了 skills 目录下手动安装的，内置的没探索
- 例如 `session-logs`, `model-usage`, `blogwatcher` 可能有用

### 🟢 远期（P2）

**7. `openclaw sandbox` — 容器隔离**
- Podman/Docker 容器化 agent 执行环境
- 安全隔离，防止 agent 误操作宿主机

**8. `openclaw plugins` — 插件扩展**
- 官方插件机制，可以开发定制扩展
- 当前用 scripts 目录 + cron 调用，不如原生插件优雅

**9. `openclaw backup` — 状态备份**
- 自动备份本地 state 到归档
- 当前没做备份，数据在内存和磁盘中，有丢失风险

---

## 三、优化建议

### 立即执行
1. **拿 TaskFlow 替代 Bitable 手动同步** → 减少心跳复杂度
2. **加 pre-upload hook** → 自动跑校验官，不用手动 spawn
3. **跑一次 `openclaw memory reindex`** → 提升检索准确度

### 本周探索
4. 研究 `openclaw agents` 的标准化配置，跟我们的 agents/ 目录结构合并
5. 试用 `session-logs` 内置 skill，分析 agent 调用模式

---

## 四、架构对比

| 层级 | 当前做法 | OpenClaw 原生方案 | 差距 |
|------|---------|-------------------|------|
| 任务管理 | Bitable + JSON 手动同步 | TaskFlow | 自动化 |
| Agent 隔离 | 手动创建目录 + status.json | `openclaw agents` | 标准化 |
| 发版审查 | 手动 spawn 校验官 | `openclaw hooks` pre-upload | 自动化 |
| Cron 调度 | `openclaw cron` | ✅ 已最佳实践 | - |
| 消息投递 | `message send` | ✅ 已最佳实践 | - |
| 文档管理 | `feishu_doc` | ✅ 已最佳实践 | - |

---

*本报告基于 OpenClaw 2026.4.21 CLI 命令列表 + 源码目录结构分析。*
