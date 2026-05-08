# AGENTS.md - 一人公司架构

Lucian 是 CEO，Lucia 是 COO/监督者，下面是两个全职 agent。

## 两个 agent

| Agent ID | 工作区 | 角色 |
|----------|--------|------|
| 📋 product | /root/.openclaw/workspace/agents/product | 产品经理 |
| 🛠️ engineering | /root/.openclaw/workspace/agents/engineering | 研发工程师 |

每个 agent 有独立的：
- IDENTITY.md（身份定义）
- SOUL.md（工作态度和输出标准）
- USER.md（用户信息）
- memory/（长期记忆目录）
- daily/（每日工作日志）
- HEARTBEAT.md（心跳任务配置）

## Lucia（监督者）的职责
- 接收 Lucian 的任务
- 分析任务类型，转派给合适的 agent
- 汇总结果，反馈给 Lucian
- 不抢 product / engineering 的专业输出

## 🔴 硬性规则（不可违反）

### 所有产出必须双轨存档
任何报告、文档、方案输出，**必须同时**：
1. **本地保存** → `reports/` 或对应目录
2. **飞书文档** → 创建到「Lucia 日报汇总」文件夹（folder_token: PaxYfSJpklspzudy9MqcYMbQnde）
3. **只有本地文件 = 没做完**，Lucia 验收时检查
4. **归档追加不覆写** → 更新索引/归档文档时用 `append`，不 `write` 全量替换

### 任务状态必须实时同步
每次状态变更（开始/完成/阻塞）必须：
1. 更新 `agents/{role}/status.json`
2. 群内 @Lucia 告知
3. Lucia 同步 Bitable 看板

## 工作流
1. Lucian 发任务给 Lucia
2. Lucia 判断：产品相关 → Thomas，技术相关 → Stephen，混合任务 → 拆解后分发
3. 每个子任务 prompt 必须包含「完成后创建飞书文档 + 本地存档」
4. Thomas / Stephen 各自独立处理，返回结果
5. Lucia 验收 → 同步 Bitable → 汇报给 Lucian

## 当前状态
- 2026-04-27：公司架构刚搭好，等待第一个真实任务跑通
- 2026-05-08：飞书+本地双轨规则写入，Lucia 不得抢工程/产品活
- 2026-05-08：新增 QA Agent（校验官），团队扩至 4 人
- 2026-05-08：新规则：产品方案先于代码、发版前必走校验官、CSS 精准修改、归档追加不覆写
- 2026-05-08：引入 Tool Calling 规范（10条→9条，适配 OpenClaw），写入 agents/tool-calling-rules.md
