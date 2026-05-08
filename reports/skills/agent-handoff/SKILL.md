> 📄 飞书文档: https://feishu.cn/docx/ITjCdDF4QoG0uSxsbtYcRCQOnmc
> 📅 同步时间: 2026-05-08T08:28:00+08:00

# agent-handoff — 多 Agent 任务交接协议

## Overview
`agent-handoff` 定义了团队内 Agent 之间（Lucia ↔ Thomas ↔ Stephen）的任务下发、结果回传、上下文传递和冲突仲裁的标准协议。确保每次交接都是无损的，不丢失 context、不产生歧义、不重复执行。

**核心角色：**
| Role | Name | 职责 |
|------|------|------|
| Orchestrator | Lucia | 任务分发、最终汇总、对外输出 |
| Product Manager | Thomas | 产品设计、需求分析、skill 设计、文档 |
| Engineer | Stephen | 工程实现、代码、调试、技术调研 |

## When to Use
- Lucia 需要把子任务委托给 Thomas 或 Stephen 时
- Thomas/Stephen 完成任务后需要回传结果给 Lucia 时
- 多个 Agent 对同一资源（文件、飞书文档、Bitable）存在并发修改风险时
- 任务遇到 blocker 需要升级/转交时
- 需要跨 session 保持任务状态追踪时

## Process

### 1. Lucia → Thomas/Stephen 任务下发 (Dispatch)

使用 `subagent` 机制下发任务，消息体必须包含以下结构化字段：

```
task_id: {unique-id}          # 全局唯一任务 ID，格式：{domain}-{type}-{seq}
role: {thomas|stephen}        # 目标角色
title: {一句话任务描述}
context:                      # 完整上下文
  - background: {为什么需要做这件事}
  - related_files: [{路径}]   # 相关文件列表
  - references: [{URL/路径}]  # 参考资料
output:                       # 产出规格
  - path: {本地输出路径}       # 必填，如 reports/xxx/ 或 agents/{role}/
  - format: {markdown|json|code|mixed}
  - deliverable: {具体产出物列表}
constraints:                  # 约束条件
  - deadline: {ISO timestamp 或 "EOD" 或 "ASAP"}
  - notify_on_complete: true|false
  - depends_on: [{task_id}]  # 依赖的前置任务
```

**最小示例（Lucia → Thomas）：**
```
task_id: product-skill-design-001
role: thomas
title: 设计 agent-handoff skill
context:
  background: 团队缺少标准化任务交接协议，导致返工和 context 丢失
  related_files: [agents/product/status.json]
  references: [addyosmani/agent-skills 模板]
output:
  path: reports/skills/agent-handoff/
  format: markdown
  deliverable: [SKILL.md]
constraints:
  deadline: 2026-05-08T18:00:00+08:00
  notify_on_complete: true
```

### 2. Thomas/Stephen → Lucia 结果回传 (Return)

任务完成后，子 Agent 必须在最终回复中包含以下结构：

```
task_id: {与下发一致的 task_id}
status: done|blocked|partial
output:
  files: [{本地路径}]         # 产出文件列表
  feishu_doc: {URL}|null      # 如果创建了飞书文档
  feishu_bitable: {URL}|null  # 如果更新了 Bitable
summary: {三句话以内的完成摘要}
blocker: {阻塞原因}|null      # 如果 status != done
next_steps: [{建议的后续步骤}]  # 可选
```

### 3. 上下文传递规范

每个 task 的上下文通过以下方式持久化，确保跨 session 可恢复：

| 字段 | 存储位置 | 格式 |
|------|----------|------|
| `task_id` | agents/{role}/status.json → task 字段 | string |
| `blocker` | agents/{role}/status.json → blocker 字段 | string\|null |
| `output_path` | agents/{role}/status.json → last_output 字段 | string |
| 完整的 task 定义 | memory/YYYY-MM-DD.md | 自然语言摘要 + task_id |
| 关键决策 | MEMORY.md（长期记忆） | 结构化条目 |

**status.json 规范：**
```json
{
  "role": "Thomas",
  "state": "idle|working|blocked",
  "task": "task_id or null",
  "updated_at": "ISO timestamp",
  "blocker": "blocker description or null",
  "last_output": "/path/to/output or null",
  "last_completed": "task_id or null"
}
```

### 4. 冲突仲裁规则

当多个 Agent 可能并发修改同一资源时：

| 场景 | 规则 | 理由 |
|------|------|------|
| 同一文件并发写入 | **Lucia 裁定**，Thomas/Stephen 写入前先检查 agents/status.json，若 Lucia state=working 则先挂起 | Lucia 是唯一编排者 |
| Bitable 同一行并发更新 | **后写者负责合并**，必须读-改-写，不能盲写 | 飞书 API 无事务 |
| 同一飞书文档并发编辑 | **按 role 分段**：Lucia 写头部，Thomas 写产品段，Stephen 写技术段 | 段落级隔离 |
| 任务依赖未满足 | **等待 + 在 status.json 标注 depends_on**，不擅自跳过 | 防止不可靠输出 |
| Blocker 升级冲突 | **升级到 Lucia**，由 Lucia 决定是等待、转交还是降级 | Lucia 有全局视野 |

**仲裁优先级：** Lucia > Thomas = Stephen（当 Thomas 和 Stephen 冲突时，Lucia 仲裁）

## Rationalizations

| 常见借口 | 反驳 |
|----------|------|
| "任务很简单，口头说一下就行，不用填结构" | 最简单的任务最容易被忘记。结构化交接的成本是 2 分钟，找回丢失 context 的成本可能是 2 小时。 |
| "我直接写到文件里了，不需要回传" | 不回传 = Lucia 不知道你完成了。系统不会自动发现文件变更，必须显式通知。 |
| "这个 blocker 我可以自己解决，不用升级" | 22 分钟原则：如果 22 分钟内无法自行解决，必须升级。自己死磕会拖慢整个 task graph。 |
| "status.json 更新太麻烦，我最后一起更新" | status.json 是团队唯一的任务状态信源。不更新 = 其他人看不到你的状态 = 无效等待。 |
| "冲突仲裁太复杂，我先改了再说" | 先改后说的代价是合并冲突 + 数据丢失风险。原子操作：先检查 → 再修改 → 再通知。 |
| "我不需要填 deadline" | 没有 deadline 的任务 = 永远不会被排期的任务。至少填 ASAP / EOD / NBD。 |
| "task_id 随便写一个就行" | task_id 是全局唯一索引，用于跨文件追踪。格式不规范会导致找不到关联信息。 |

## Red Flags
- 子 Agent 在未收到显式 task_id 的情况下被调用 → 可能是非正式请求，需确认
- status.json 超过 4 小时未更新且 state=working → 可能卡死，需要 heartcheck
- 同一个 task_id 出现在两个 Agent 的 status.json 中 → 重复派发，需要 Lucia 确认
- output_path 指向不存在的目录 → 子 Agent 可能创建失败，需要检查
- blocker 字段写了但 state 不是 blocked → 状态不一致，需要修复
- 子 Agent 返回时 task_id 与下发不一致 → 可能是串任务，需要验证

## Verification
1. 检查 `agents/{role}/status.json` 是否随任务状态变化及时更新
2. 用 `task_id` 全文搜索 `memory/` 目录，确认可以找到完整的任务链路
3. 模拟一次完整交接：Lucia dispatch → 子 Agent 执行 → 子 Agent return → 检查所有字段是否完整
4. 故意制造一个冲突场景（两方同时尝试写同一 Bitable），验证仲裁规则是否正确触发
5. 抽查最近 5 个 task_id 的 output_path，确认文件确实存在且内容符合预期
