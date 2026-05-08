# 📱 iOS OpenClaw UI 调研报告

> **任务 ID**: ios-openclaw-ui-research-001  
> **作者**: Thomas（产品经理）  
> **日期**: 2026-05-08  
> **背景**: Boss 想了解是否值得为 OpenClaw 打造一个 iOS 原生 UI 应用，能够在移动端直接看到 agent 状态、进度监控，而非聊天界面。

---

## 一、现有方案梳理

### 方案 1：OpenClaw Web UI（浏览器访问 Control UI）

**产品形态**：通过 `http://<host>:18789/` 访问的 Vite + Lit 单页应用。

**支持能力**：
- 实时会话列表（sessions.list）
- Agent 聊天、模型切换
- Cron 任务管理
- Channels/节点状态监控
- Config 配置读写
- 日志实时 tail
- 支持 PWA 安装（可添加到主屏幕）
- 支持中文在内的 18 种语言本地化

**优点**：
- 功能最全面，Gateway 原生自带
- PWA 模式可在 iOS Safari "添加到主屏幕"后获得类 App 体验
- 通过 Tailscale Serve 可远程访问

**缺点**：
- 桌面优先设计，移动端体验差（表格太窄、按钮过小）
- 不算真正的原生 App，无法推送通知、后台刷新
- 需要保持 Safari 标签页存活，耗电
- 没有专属的状态监控 Dashboard 视图

**结论**：基本可用，但不符合"移动端仪表盘监控"的定位。

---

### 方案 2：OpenClaw iOS 官方 App（Node 模式）

**产品形态**：OpenClaw 官方出品的 iOS 应用（内部预览阶段，未公开分发）。

**定位**：**Node 终端**，不是监控 Dashboard。

**支持能力**：
- 与 Gateway 建立 WebSocket 连接（LAN 或 Tailnet）
- 暴露 Node 能力：Canvas、ScreenSnapshot、Camera、Location、Talk mode、Voice wake
- 接收 `node.invoke` 命令
- Relay-backed APNs 推送（官方构建版）

**优点**：
- 官方亲儿子，有 APNs 推送支持
- Voice wake + Talk mode 是差异化能力

**缺点**：
- **不是监控/仪表盘应用**，是"被 agent 控制的 iOS 设备节点"
- 无任何状态监控、进度查看能力
- 仅内部预览，未公开发布
- 需要 Gateway 运行在其他设备上

**结论**：和 Boss 需求完全不同，不适用。

---

### 方案 3：OpenClaw macOS Companion App（菜单栏模式）

**产品形态**：macOS 菜单栏应用，管理本地 Gateway。

**支持能力**：
- 菜单栏状态图标
- Gateway 本地/远程模式切换
- TCC 权限管理（Notifications、Accessibility、Screen Recording 等）
- 节点能力暴露（Canvas、Camera、Screen）
- SSH Tunnel 远程连接模式

**优点**：
- 状态指示直观（菜单栏图标）
- 可管理多个 Gateway

**缺点**：
- macOS 独占，iOS 用户无法使用
- 本质是桌面工具，非移动监控 Dashboard

**结论**：不适用于 iOS 移动场景。

---

### 方案 4：Coze（字节跳动）AI Agent 平台

**产品形态**：一站式 AI Bot 构建平台（coze.cn），提供 Bot Studio + 实时监控 + 工作流编排。

**核心 UI 设计亮点**（值得借鉴）：

| 设计维度 | Coze 的做法 |
|---|---|
| **Bot 创建** | 可视化卡片编辑器，零代码/low-code 定义 bot 行为 |
| **工作流编排** | 节点式流程图，拖拽连线，实时预览 |
| **实时监控** | 运行日志实时展示，每步节点状态清晰标注（成功/失败/运行中） |
| **调试体验** | 单步执行、参数修改即时生效，无需重新部署 |
| **发布渠道** | 一键发布到多个平台（飞书、微信、Discord 等） |
| **数据分析** | Bot 对话量、用户反馈、留存等数据面板 |

**优点**：
- 工作流可视化做得非常成熟，用户知道"Bot 在哪一步"
- 实时日志面板完美解决"进度可见性"问题
- 有移动端 H5 版本，通过浏览器即可访问

**缺点**：
- 是 Bot 创建平台，不是 OpenClaw 类的 personal assistant
- 不开源，无法定制
- 国内访问有时不稳定

**借鉴意义**：Coze 的"节点式日志 + 实时状态"设计理念，直接回答了 Boss "Agent 在干什么、进度如何"的监控需求。

---

### 方案 5：ChatGPT App / Claude App 参考

**ChatGPT iOS App**：
- 主界面：对话列表 + 新建对话，简洁
- GPT-4o 语音模式有实时视觉感知状态指示
- 没有 agent 状态监控，主要是对话交互

**Claude App（Anthropic）**：
- 主打"Projects"概念，有侧边栏会话管理
- Artifacts 实时渲染有进度提示
- 移动端体验接近桌面版，功能完整度高

**借鉴点**：两者都是对话优先，但移动端完成度高。OpenClaw 若做 iOS App，可以借鉴 Claude 的 Projects 侧边栏布局 + 实时状态指示器设计。

---

## 二、Boss 核心诉求分析

| 诉求 | 对应设计方向 |
|---|---|
| iOS 上直接看到 agent 状态 | **Dashboard 首页** — 卡片式 agent 状态总览 |
| 不是聊天界面，是仪表盘 | **监控视图** — 非对话的平行面板展示 |
| 谁在干什么、进度如何 | **实时日志/任务流** — Coze 式的节点状态面板 |
| 移动端随时查看 | **Native iOS App**（或高质量 PWA） |

---

## 三、自建 vs 不建 综合评估

### 不建的理由

| 因素 | 说明 |
|---|---|
| **OpenClaw Web UI 已可用** | 通过 Safari PWA 基本覆盖移动端需求 |
| **iOS Node App 已在做** | 官方已有 iOS 应用规划，重复建设浪费 |
| **开发成本高** | 原生 iOS App 需要 Swift 开发，涉及 WebSocket、推送、Gateway API 对接 |
| **Gateway Protocol 变化风险** | OpenClaw 仍在活跃开发中，API 不稳定 |
| **Coze 等外部方案** | 如果核心需求是"Bot 监控"，Coze 等平台已做得很好 |

### 建的理由

| 因素 | 说明 |
|---|---|
| **差异化体验** | Web UI 移动端体验差，PWA 不支持推送通知和后台刷新 |
| **满足老板核心需求** | 仪表盘式监控是真实需求，Web UI 无法满足 |
| **可商业化** | 如果开源，可能吸引其他 OpenClaw 用户 |
| **护城河** | 竞品普遍没有做得好的 OpenClaw 移动端监控方案 |

### 替代方案（低成本）

1. **优化现有 Web UI 移动端体验**（响应式改造）
   - 成本：低（纯前端 CSS 调整）
   - 效果：有限，无法获得原生 App 能力

2. **PWA + 推送通知**
   - 成本：低（利用现有 Control UI PWA 能力）
   - 效果：中等，可获得通知但无后台刷新

3. **基于现有 iOS Node App 扩展 Dashboard Tab**
   - 成本：中（官方已在做，可参与共建）
   - 效果：高，但需与 OpenClaw 核心团队协作

---

## 四、自建决策：综合建议

### 🟡 建议：暂不自建独立 App，但推进 MVP 版

**理由**：
1. OpenClaw 本身还在快速迭代（v2026.4.21），API 不够稳定
2. Web UI PWA 可作为过渡方案
3. iOS Node App 官方已在做，可考虑在官方路线图中贡献 Dashboard 能力

**如果决定开建，推荐做一个「OpenClaw Monitor」类应用**，不是替代聊天，而是专注监控。

### MVP 功能建议（最小可用版本）

```
优先级    功能                          说明
--------  ----------------------------  -----------------------------------
P0        Agent 状态卡片总览             展示所有 agent 状态、最后活跃时间
P0        实时会话进度                   当前运行的 task/agent，状态指示
P0        Gateway 连接状态               在线/离线，连接方式（LAN/Tailnet）
P1        Cron 任务状态面板              最近执行结果、成功/失败指示
P1        节点列表（Node status）        各 node 在线状态、最后 ping 时间
P2        推送通知（Critical 更新）       Gateway 离线、重要任务失败等
P2        快捷操作                      终止会话、触发 cron 立即执行
P3        日志流实时 tail                从 App 内查看 gateway logs
P3        多 Gateway 切换               如果运营多个 OpenClaw 实例
```

**技术实现路径**：
- iOS App 通过 WebSocket 直连 Gateway（与现有 Control UI 相同协议）
- 不需要单独 Server，直接读 Gateway 的 RPC 接口
- Swift + SwiftUI，参考 OpenClaw Control UI 的 WebSocket 协议文档
- 推送可复用现有 iOS Node App 的 APNs relay 基础设施

**预计工时**：
- MVP（P0+P1）：**约 6-8 周**（单人 iOS 开发）
- 完整版（含 P2+P3）：**约 12-16 周**

---

## 五、结论

| 问题 | 答案 |
|---|---|
| OpenClaw 有官方移动端 UI 吗？ | ❌ 没有正式发布的。Web UI 可用，iOS Node App 内部预览中 |
| 第三方客户端？ | ❌ 未发现 |
| Coze UI 值得借鉴吗？ | ✅ **非常值得**。节点式实时日志 + 状态追踪是核心借鉴点 |
| 有没有必要自建？ | 🟡 **中等必要**。Web UI 勉强能用，但监控体验差距大；独立 App 成本高，建议先做 MVP |
| 推荐路径 | 先用 PWA 过渡 + 向官方 iOS App 贡献 Dashboard 能力，条件成熟再做独立 App |

---

*Thomas @ 2026-05-08*
