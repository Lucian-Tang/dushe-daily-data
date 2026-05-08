> 📄 飞书文档: https://feishu.cn/docx/ZTw0dmL7ToAxj5xV0wec5wgbnTc
> 📅 同步时间: 2026-05-08T08:28:00+08:00

# feishu-sync — 飞书文档自动同步

## Overview
`feishu-sync` 负责检测团队产出内容，自动判断是否需要创建飞书文档，并按规范写入「Lucia 日报汇总」文件夹。每个新创建的飞书文档都会回写链接到本地文件系统和 Bitable，确保"本地有记录、云端可协作"。

**设计原则：** 一个产出 = 一个飞书文档（原子粒度），不合并不同类型的产出到同一个文档。

**目标文件夹：**
- 名称：`Lucia 日报汇总`
- Folder Token：`PaxYfSJpklspzudy9MqcYMbQnde`

## When to Use
- 任何 Agent 完成了有保存价值的产出（报告、skill 设计、分析、决策记录、SOP）
- 每日工作报告生成后，需要归档到飞书
- 本地 `reports/` 目录下有新文件但尚未同步到飞书
- `MEMORY.md` 或 `memory/YYYY-MM-DD.md` 有重要更新需要同步到云端
- 用户明确要求"把这个存到飞书"

**以下情况不应触发：**
- 纯代码文件（`.py`, `.js`, `.ts` 等）→ 属于 git 管理
- 临时调试日志 → 无长期价值
- 已在飞书上有相同内容且未修改的文档 → 避免重复
- 文件内容少于 100 字符 → 太短无归档价值

## Process

### Step 1: 检测产出（Trigger Detection）

触发条件（满足任一即触发）：
- `reports/` 目录下有新文件（对比 `agents/{role}/status.json` 中的 `last_output`）
- 任务完成时子 Agent 返回 `output.files` 非空
- `MEMORY.md` 的 mtime 发生变化且变化量 > 200 字符
- 用户显式指令

### Step 2: 是否该创建飞书文档？（Decision Matrix）

| 产出类型 | 创建飞书文档？ | 原因 |
|----------|:---:|------|
| Skill 设计（SKILL.md） | ✅ 是 | 团队共享知识资产 |
| 工作报告（日报/周报） | ✅ 是 | 归档到日报汇总文件夹 |
| 需求分析文档 | ✅ 是 | 需团队 review |
| 技术调研报告 | ✅ 是 | 知识库积累 |
| 决策记录 | ✅ 是 | 决策追溯 |
| SOP/流程文档 | ✅ 是 | 团队参考 |
| 代码片段 | ❌ 否 | 属于 git |
| 临时记录 | ❌ 否 | 无长期价值 |
| 个人笔记 | ❌ 否 | 私人性质 |
| 已同步且未变更 | ❌ 否 | 避免重复 |

### Step 3: 标题规范

**格式：** `[{类型标签}] {YYYY-MM-DD} {内容摘要}`

**类型标签：**
| 标签 | 适用场景 |
|------|----------|
| `[日报]` | 每日工作报告 |
| `[周报]` | 每周汇总报告 |
| `[Skill]` | Agent Skill 设计文档 |
| `[需求]` | 产品需求分析 |
| `[调研]` | 技术/市场调研 |
| `[决策]` | 重要决策记录 |
| `[SOP]` | 标准操作流程 |
| `[复盘]` | 项目复盘/教训 |

**示例：**
- `[日报] 2026-05-08 团队工作汇总`
- `[Skill] 2026-05-08 agent-handoff 多 Agent 任务交接协议`
- `[决策] 2026-05-08 飞书同步触发策略选择`
- `[调研] 2026-05-08 LanceDB 性能测试结果`

### Step 4: 写入飞书文档

1. 调用 `feishu_doc` action=create，传入：
   - `title`: 按规范生成
   - `folder_token`: `PaxYfSJpklspzudy9MqcYMbQnde`
   - `content`: 本地文件内容（markdown 格式）
   - `grant_to_requester`: true

2. 获取返回的 `doc_token` 和文档 URL

### Step 5: 回写链接

**必须回写到以下位置：**

1. **本地文件头部**（如果是 SKILL.md 或 .md 文件）：
   ```markdown
   > 📄 飞书文档: https://xxx.feishu.cn/docx/{doc_token}
   > 📅 同步时间: 2026-05-08T08:28:00+08:00
   ```

2. **Bitable「Lucia 日报汇总」表**（如果存在对应的 Bitable）：
   - 字段：`文档标题`、`飞书链接`、`类型`、`创建日期`、`本地路径`
   - 如果 Bitable 不存在，记录到 `agents/status.json` 的 `pending_bitable_sync` 字段

3. **agents/{role}/status.json**：
   ```json
   {
     "last_synced_doc": "https://xxx.feishu.cn/docx/{doc_token}",
     "last_synced_at": "ISO timestamp"
   }
   ```

### Step 6: 确认同步

同步完成后，本地记录同步状态到 `memory/feishu-sync-log.json`：
```json
{
  "local_path": "reports/skills/agent-handoff/SKILL.md",
  "feishu_url": "https://xxx.feishu.cn/docx/xxx",
  "doc_token": "xxx",
  "synced_at": "2026-05-08T08:28:00+08:00",
  "synced_by": "thomas"
}
```

## Rationalizations

| 常见借口 | 反驳 |
|----------|------|
| "这个文件不重要，不需要同步到飞书" | 判断标准不是"重要与否"，而是"是否有人需要协作/查阅"。只要 ≥2 个人可能需要看，就应该同步。 |
| "等所有文件都写完再一起同步" | 批量同步 = 一次性大量 API 调用 + 可能触发限流 + 同步失败时不知道哪个文件出问题。逐文件同步，原子操作。 |
| "标题随便起一个就行" | 标题是飞书搜索的唯一入口。不规范的标题 = 永远找不到这份文档。标题规范不是负担，是未来的救命稻草。 |
| "folder_token 我每次都手动查很麻烦" | folder_token `PaxYfSJpklspzudy9MqcYMbQnde` 是硬编码在 skill 里的常量，不需要每次查。直接用。 |
| "回写链接太麻烦，URL 我知道就行" | 你不是唯一的使用者。Lucia/Stephen 也需要知道文档在哪。本地文件头部写 URL 是最低成本的链接传播方式。 |
| "飞书 API 限流了，我下次再试" | 如果遇到 429，等 Retry-After 秒后重试一次。重试仍失败则写入 `pending_sync` 队列，下次 heartbeat 时补同步。不静默丢弃。 |
| "Bitable 还没建好，先不管" | 先把链接写入 `pending_bitable_sync` 字段。Bitable 建好后批量补齐。宁可有 pending 队列，不能丢失链接。 |

## Red Flags
- 飞书文档创建成功但 folder_token 不是 `PaxYfSJpklspzudy9MqcYMbQnde` → 写到错误文件夹，需移动
- `feishu-sync-log.json` 中同一个 `local_path` 出现多条记录 → 可能重复同步，检查是否需要去重
- 回写链接到本地文件失败（权限问题） → 记录 warning，不阻塞主流程
- 飞书 API 返回 403 → 权限不足，检查 app scopes
- `doc_token` 在创建后 5 分钟内无法读取 → 飞书可能有创建延迟，重试 3 次（间隔 5s）
- 本地文件内容与飞书文档内容不一致 → 以本地为准，重新同步

## Verification
1. 创建一份测试文档到目标文件夹，验证 `feishu_doc` action=create 成功
2. 检查本地文件头部是否正确写入了飞书链接
3. 检查 `memory/feishu-sync-log.json` 是否记录了本次同步
4. 检查 `agents/{role}/status.json` 的 `last_synced_doc` 字段是否更新
5. 用 folder_token `PaxYfSJpklspzudy9MqcYMbQnde` 检查目标文件夹，确认文件已出现
6. 模拟 API 限流场景，验证 pending 队列机制是否正常工作
