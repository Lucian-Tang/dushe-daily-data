> 📄 飞书文档: https://feishu.cn/docx/OGrCdMyo6ot7b3xVFy0c2Nlgngb
> 📅 同步时间: 2026-05-08T08:28:00+08:00

# daily-report — 每日工作报告生成

## Overview
`daily-report` 负责在每个工作日结束时（或按需）从各 Agent 的 `status.json` 收集当日完成项，生成按角色分组的结构化工作报告，通过群聊消息和飞书文档双通道输出，确保团队所有人对当日进度可见。

**报告三要素：**
- ✅ 已完成 — 当日实际交付的任务
- 🔄 进行中 — 已启动但未完成的任务
- 🚫 阻塞项 — 因外部依赖或问题无法推进的任务

**输出双通道：**
1. **群聊消息** — 即时可见，适合快速扫读（精简版）
2. **飞书文档** — 归档到 `Lucia 日报汇总` 文件夹（完整版）

## When to Use
- **定时触发：** 每个工作日 18:00（北京时间）自动生成
- **按需触发：** 用户通过 Lucia 发送指令如"今日工作总结"、"日报"
- **事件触发：** 当天有 ≥3 个任务完成时，可主动提醒是否需要生成日报
- **异常触发：** 当天有 blocker 持续 >4 小时未解决时，日报优先标注

**以下情况不应触发：**
- 周末/节假日（除非 on-call 或用户特别要求）
- 当天没有任何 Agent 的 status.json 发生变化 → 无更新可报
- 距离上次报告 < 2 小时 → 避免刷屏

## Process

### Step 1: 数据收集

读取以下数据源：
1. `agents/lucia/status.json` → Lucia 的状态
2. `agents/product/status.json` → Thomas 的状态
3. `agents/engineering/status.json` → Stephen 的状态
4. `agents/status.json` → 全局状态汇总（如果存在）
5. `memory/YYYY-MM-DD.md` → 当日的原始日志

**提取字段：**
```
role, state, task, updated_at, blocker, last_completed, last_output
```

### Step 2: 按角色分组汇总

对每个角色，从 `memory/YYYY-MM-DD.md` 中解析当日完成的 task_id，匹配到对应的产出：

```
Lucia:
  ✅ 已完成: [task_id_1, task_id_2, ...]
  🔄 进行中: [task_id_3]
  🚫 阻塞项: [blocker_description]

Thomas:
  ✅ 已完成: [task_id_4]
  🔄 进行中: [task_id_5]
  🚫 阻塞项: null

Stephen:
  ✅ 已完成: []
  🔄 进行中: [task_id_6]
  🚫 阻塞项: [external_api_dependency]
```

### Step 3: 生成群聊消息（精简版）

**格式规范：** Discord/飞书群聊不支持 markdown 表格，使用列表格式。

```markdown
📊 **日报 | 2026年5月8日（周四）**

**Lucia** 🔥
✅ 完成 agent-handoff skill review
✅ 处理飞书同步触发策略
🔄 进行中 custom-skills-build-001 编排
🆗 无阻塞

**Thomas** 📋
✅ 完成 agent-handoff SKILL.md 设计
✅ 完成 feishu-sync SKILL.md 设计
🔄 进行中 daily-report 和 knowledge-base-update 设计
🆗 无阻塞

**Stephen** 🔧
🔄 进行中 LanceDB memory-hygiene skill 优化
🚫 等待飞书 API scope 审批 (blocked → 已升级给 Lucia)

---
📄 完整报告: <https://xxx.feishu.cn/docx/xxx>
📊 任务看板: <Bitable URL>
```

**关键规则：**
- 每个角色 3-5 条，不超过 6 条。超过则选最重要的列，其余写"等 N 项"
- blocker 必须单独一行，用 🚫 emoji 突出
- 如果某角色当天无任何更新，写"🆗 今日无更新"
- 必须附带飞书完整报告链接

### Step 4: 生成飞书文档（完整版）

飞书文档包含更详细的内容：

```markdown
# 日报 | 2026年5月8日（周四）

## 全局概览
- 总任务: 8 | ✅ 已完成: 5 | 🔄 进行中: 2 | 🚫 阻塞: 1
- 阻塞项: Stephen → 飞书 API scope 审批

## Lucia
### ✅ 已完成
- **agent-handoff-skill-review-001**: 完成 agent-handoff skill 审查
  - 产出: reports/skills/agent-handoff/SKILL.md (已 review)
  - 关联: https://xxx.feishu.cn/docx/xxx

### 🔄 进行中
- **custom-skills-build-001**: 编排 4 个 skill 的设计和创建

## Thomas
### ✅ 已完成
- **agent-handoff-skill-design-001**: 完成 agent-handoff SKILL.md 设计
  - 产出: reports/skills/agent-handoff/SKILL.md
- **feishu-sync-skill-design-001**: 完成 feishu-sync SKILL.md 设计
  - 产出: reports/skills/feishu-sync/SKILL.md

### 🔄 进行中
- **daily-report-skill-design-001**: 设计 daily-report SKILL.md
- **knowledge-base-skill-design-001**: 设计 knowledge-base-update SKILL.md

## Stephen
### 🔄 进行中
- **memory-hygiene-optimize-001**: LanceDB memory-hygiene skill 优化

### 🚫 阻塞项
- **飞书 API scope 审批**: 需要 admin 审批 drive:docx:create 权限
  - 阻塞时间: 2026-05-08 12:00 → 至今 (4h+)
  - 已升级给: Lucia

## 明日计划
- Thomas: 完成 4 个 skill 的飞书同步
- Stephen: memory-hygiene 优化（如 scope 通过）
- Lucia: skill 最终 review + 发布
```

### Step 5: 回写与归档

1. 创建飞书文档后，调用 `feishu-sync` 的 Step 5 回写链接
2. 更新 `agents/status.json`（全局）的 `last_daily_report` 字段
3. 在 `memory/YYYY-MM-DD.md` 末尾追加报告摘要

## Rationalizations

| 常见借口 | 反驳 |
|----------|------|
| "今天没干什么，不用写日报" | 日报不是表彰大会，是状态同步。"今天调研了 X 方向，暂无结论"也是有效信息，它告诉团队这个方向有人在看。 |
| "群聊消息就够了，不用飞书文档" | 群聊消息会滚动消失。下周你想找"上周三 Thomas 到底做了哪个 skill"，群聊搜索靠不住。飞书文档是可检索的永久记录。 |
| "统计数据不准确，随便写写" | 不准确的日报比没有日报更危险——它制造错误认知。数据来自 status.json 和 memory/，这些是客观记录，不需要"估计"。 |
| "Stephen 没更新 status.json，日报里跳过他就行" | 不更新 status.json 本身就是信息——说明 Stephen 的状态同步有问题。日报应标注"N/A（状态未更新）"而不是假装无事发生。 |
| "日报太长没人看" | 精简版 3-5 条/人，扫读只需 15 秒。完整版是给需要深入了解的人看的。长短各有用途。 |
| "周末不用发日报" | 正确。但如果有 on-call 或异常 blocker（如安全事故），日报是必须的。规则是平常不发，异常必发。 |
| "每天 18:00 自动发太死板" | 18:00 是默认，不是强制。如果当天任务 14:00 就全部完成了，可以提前发并标注"提前日报"。灵活优于死板。 |
| "飞书文档排版不重要" | 排版体现专业度。乱排版的文档 = 没人会认真看 = 等同于没写。花 2 分钟排版是值得的。 |

## Red Flags
- 某个角色的 status.json 超过 8 小时未更新 → 可能离线或卡死，日报需标注"状态异常"
- 当天有至少一个 blocker 但日报未体现 → 信息遗漏，需要补上
- 飞书文档创建失败但群聊消息已发送 → 需要补同步，不能只发一半
- 统计数字与 memory/ 日志不符 → 可能存在"做了但没记录"或"记录了但没做"的不一致
- 日报中某个角色的条目数为 0 但 status.json 显示 state=working → 进度丢失，需要排查
- 连续 3 天日报中同一 blocker 未解决 → 需要升级处理

## Verification
1. 检查 `agents/status.json` 的 `last_daily_report` 字段是否在每次日报后更新
2. 对比 `memory/YYYY-MM-DD.md` 中记录的 task_id 与日报中的任务列表，确认无遗漏
3. 检查飞书文档是否成功创建在 `Lucia 日报汇总` 文件夹（folder_token: `PaxYfSJpklspzudy9MqcYMbQnde`）
4. 确认群聊消息包含了飞书文档链接
5. 模拟"某角色无 status.json 更新"场景，验证日报标注逻辑
6. 验证 blocker 行是否在群聊消息和飞书文档中都被正确呈现
