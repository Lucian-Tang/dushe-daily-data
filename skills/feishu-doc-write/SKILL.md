# Feishu 文档写入规范（SKILL.md）

> 正确的文档写入流程，防止子 agent 谎报完成

## 核心问题

`feishu_doc action: "create"` 只创建空白文档，标题是唯一的初始内容。
**不会自动写内容进去。**

## 正确流程（必须分两步）

### Step 1：创建文档

```json
{
  "action": "create",
  "title": "文档标题",
  "owner_open_id": "ou_229a693d4119ce6c9459b27e38fb254c"
}
```

返回：`doc_token`，用于后续写入。

**关键：创建后必须立即用 `append` 写入内容，不能创建完就结束。**

### Step 2：追加内容（创建后立即执行）

```json
{
  "action": "append",
  "doc_token": "返回的doc_token",
  "content": "## 标题\n\n内容..."
}
```

`append` 会把内容追加到文档末尾，支持 Markdown 格式。

## 写入内容验证

写入后必须验证文档有内容：

```json
{ "action": "list_blocks", "doc_token": "xxx" }
```

检查返回的 `blocks` 数组：
- 如果只有1个 block（Page标题），说明写入失败
- 如果有多个 block，说明写入成功

## 错误示例（子 agent 常犯）

```json
// ❌ 错误：创建后不写入内容
{ "action": "create", "title": "xxx" }
// → 谎报完成，实际文档是空的

// ✅ 正确：创建后立即 append
{ "action": "create", "title": "xxx" }
// → 获取 doc_token
{ "action": "append", "doc_token": "刚返回的token", "content": "..." }
// → 验证 list_blocks 确认有内容
```

## 写入模式选择

| action | 适用场景 | 说明 |
|--------|---------|------|
| `write` | 替换整个文档 | 会删除原有内容，用 `create`+`append` 代替 |
| `append` | 追加内容 | 添加到文档末尾，不会删除原有内容 |
| `create` | 新建文档 | 单独使用无效，必须配合 `append` |

## 完整示例流程

```
1. 创建文档 → 获取 doc_token
2. 立即 append 内容
3. list_blocks 验证有内容
4. 确认完成，才算真正完成
```

## 常见失败原因

1. 子 agent 只调用 create 不调用 append
2. 子 agent 报完成时文档还是空的
3. 没有验证步骤就确认完成

## 验证命令

创建文档后必须执行：

```json
{ "action": "list_blocks", "doc_token": "xxx" }
```

只有当返回的 blocks 数量 > 1 时，才算写入成功。