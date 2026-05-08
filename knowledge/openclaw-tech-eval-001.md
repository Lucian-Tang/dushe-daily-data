# OpenClaw 升级技术评估 — openclaw-tech-eval-001

> 调研时间：2026-05-04 | 任务编号：openclaw-tech-eval-001
> 当前版本：2026.4.21 | 目标版本：2026.5.2 | 负责人：Stephen

---

## 一、版本概况

| 项目 | 值 |
|------|-----|
| 当前运行版本 | OpenClaw 2026.4.21 (pnpm global) / 2026.4.27 (node_modules) |
| 目标版本 | OpenClaw 2026.5.2 |
| 最新稳定版本 | 2026.5.2（2026-05-02 发布） |
| Node 要求 | >=22.14.0（当前：v22.22.2 ✅） |

---

## 二、2026.5.2 主要变更

### 2.1 核心亮点

- **插件系统重构**：外部插件（Feishu、Discord、WhatsApp等）全面转向 npm-first，ClawHub 作为补充源
- **Gateway 性能优化**：启动时跳过插件auth-profile预计算，显著减少就绪延迟；新增 `gateway restart --force` 和 `--wait <duration>`
- **Control UI / WebChat 改进**：Sessions、Cron、长连接WebSocket、消息宽度、iOS PWA等方面的稳定性增强
- **xAI Grok 4.3**：已加入默认模型目录并成为默认 xAI 聊天模型

### 2.2 重要变化

| 类别 | 变化 | 影响 |
|------|------|------|
| 插件安装 | 外部插件优先从 npm 安装，ClawHub 作为 fallback | 需确保 npm 源可用 |
| 插件更新 | beta 频道下插件同时尝试 @beta 和 latest/latest | 可能引入不稳定插件 |
| threadBindings | 用 `threadBindings.spawnSessions` 替代旧的 split toggle | 需运行 `doctor --fix` 迁移 |
| doctor | `doctor --fix` 现在会自动提交安全的 legacy 配置迁移 | 可能自动修改配置 |
| 依赖版本 | TypeBox 1.1.37, AWS SDK 3.1041.0, OpenAI 6.35.0, Pi 0.71.1, Codex 0.128.0, Zod 4.4.1 等 | 依赖层面的更新 |

### 2.3 已知修复的问题

- GPT-5 API-key sessions 默认回退到 SSE Responses 传输（修复 WebSocket 无响应问题）
- Sessions 不会在完成后仍显示为 running（修复状态粘滞）
- 大型运行时配置不再阻塞启动（避免连接超时）
- 外部插件安装/更新时的依赖问题修复

---

## 三、兼容性评估

### 3.1 现有环境

**已安装 Skills（19个）：**
```
agent-browser-clawdbot, automation-workflows, baidu-hot-monitor, cn-trends-aggregator,
douyin-hot, feishu-doc-write, find-skills, github, hot-news-aggregator, memory-hygiene,
openclaw-tavily-search, skillhub-preference, tencentcloud-lighthouse-skill, tencent-cos-skill,
tencent-docs, tencent-meeting-skill, twitter-collector, weather, web-hot, web-tools-guide
```

**系统 Cron 任务：**
```
*/5 * * * *  qcloud/stargate lock
* * * * *    secu-tcs-agent monitor
0 3 * * *    session-cleanup.sh
*/30 * * * * bitable-monitor-system.sh
```

**Channel 配置：** Feishu（飞书）

### 3.2 兼容性结论

| 组件 | 兼容性 | 说明 |
|------|--------|------|
| agents (PI runtime) | ✅ 兼容 | 无 breaking changes |
| skills | ✅ 兼容 | skill 由 OpenClaw 加载机制不变 |
| cron scripts | ✅ 兼容 | bash 脚本独立于 OpenClaw 版本 |
| bitable-monitor-system.sh | ✅ 兼容 | 纯 bash/curl，不依赖 OpenClaw API |
| Feishu 插件 | ✅ 捆绑 | 仍为核心包的一部分 |
| node v22.22.2 | ✅ 满足 | 要求 >=22.14.0 |

---

## 四、升级步骤

### 4.1 标准升级命令

```bash
# 推荐：使用 openclaw update（自动检测安装方式、执行doctor、restart）
openclaw update

# 预览模式（不实际执行）
openclaw update --dry-run

# 预览 + JSON 格式输出
openclaw update --dry-run --json
openclaw update status --json
```

**pnpm 手动升级（当前安装方式）：**
```bash
pnpm add -g openclaw@latest
```

**npm 备选：**
```bash
npm i -g openclaw@latest
```

### 4.2 升级后验证

```bash
# 1. 确认版本
openclaw --version

# 2. 运行诊断
openclaw doctor

# 3. 检查 gateway 状态
openclaw gateway status

# 4. 检查 channel 连接（飞书）
openclaw status

# 5. 验证 cron 任务（bitable-monitor）
tail -n 50 /root/.openclaw/workspace/memory/bitable-cron-system.log
```

### 4.3 配置迁移

```bash
# 自动迁移旧的 threadBindings 配置
openclaw doctor --fix
```

---

## 五、回滚方案

### 5.1 方案A：npm/pnpm 降级

```bash
# 降级到 2026.4.21
pnpm add -g openclaw@2026.4.21

# 或指定具体版本
npm i -g openclaw@2026.4.21
```

### 5.2 方案B：从头重装

```bash
# 如果 update 失败后无法恢复，运行 installer
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method npm

# 指定版本
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method npm --version 2026.4.21
```

### 5.3 关键文件备份（升级前建议）

```bash
# 备份配置
cp -r ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak.$(date +%Y%m%d)

# 备份 workspace
cp -r ~/.openclaw/workspace ~/.openclaw/workspace.bak.$(date +%Y%m%d)

# 备份 crontab
crontab -l > ~/crontab.bak.$(date +%Y%m%d)
```

---

## 六、已知问题和风险

### 6.1 主要风险

| 风险 | 级别 | 缓解措施 |
|------|------|---------|
| 插件外部化导致npm依赖增多 | 低 | 使用 `openclaw doctor` 检查 |
| beta 频道插件版本不稳定 | 低 | 保持 stable 频道 |
| doctor --fix 自动修改配置 | 低 | 升级前先备份配置 |
| 升级后 gateway 无响应 | 中 | 准备好 SSH 访问和回滚命令 |

### 6.2 无 Breaking Changes

根据 release notes，2026.5.2 **未发现破坏性变更**：
- 配置字段全部向后兼容
- agent 运行时行为无重大变化
- 插件 SDK 保持兼容

### 6.3 升级失败应急处理

```bash
# 1. 检查 gateway 日志
tail -n 100 ~/.openclaw/logs/gateway.log

# 2. 查看进程状态
ps aux | grep openclaw

# 3. 强制重启 gateway
openclaw gateway restart --force

# 4. 若完全无法启动，降级
pnpm add -g openclaw@2026.4.21
openclaw gateway restart
```

---

## 七、建议

### 7.1 是否升级？

**建议：升级 ✅**

理由：
1. 无 breaking changes，风险低
2. 有重要的稳定性和性能修复
3. 解决了 GPT-5 WebSocket 无响应问题
4. 减少了 gateway 启动延迟

### 7.2 升级时机

建议在**业务低峰期**执行升级（如凌晨），因为：
- gateway 会在更新后重启
- 正在进行的 agent 会话会被中断
- 需要留出 10-15 分钟验证时间

### 7.3 升级后检查清单

- [ ] `openclaw --version` 显示 2026.5.2
- [ ] `openclaw doctor` 无红色错误
- [ ] 飞书消息正常收发
- [ ] cron 任务（bitable-monitor）正常执行
- [ ] 飞书群消息正常推送
- [ ] 无新出现的长等待/超时问题

---

## 八、参考链接

- 官方升级文档：https://docs.openclaw.ai/install/updating
- GitHub Release：https://github.com/openclaw/openclaw/releases/tag/v2026.5.2
- OpenClaw 官网：https://openclaw.ai

---

*生成时间：2026-05-04 | Stephen*