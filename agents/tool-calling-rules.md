# Tool Calling Rules

> 适用：OpenClaw + DeepSeek V4 Pro / MiniMax M2.7
> 基于 DeepSeek V4 Pro 工具调用固定模式错误的 10 条规则，筛选优化后落地

---

## 背景

OpenClaw 对工具参数做 **JSON Schema 强制类型校验**，字段类型不符直接报错。这意味着部分通用规则在 OpenClaw 环境下要么多余（校验器替你挡了）、要么需要调整。

---

## 最终规则（合并优化版）

### 1. ✅ 保留（已实践）
**可选字段不传 null / 空字符串 / 空对象**

- `null` → 直接省略
- `""`（空字符串）→ 省略或有实际值再传
- `{}`（空对象）→ 省略或填实际字段

> OpenClaw 校验：`additionalProperties: false` + `required` 强制，非必填字段不传即可。空值仍然会导致类型错误（expected string got null）。

---

### 2. ✅ 保留（需强调）
**数组字段用 JSON 数组，单元素也带括号**

```json
// ✅ 正确
{ "members": ["ou_xxx"] }

// ❌ 错误
{ "members": "ou_xxx" }
```

> OpenClaw 校验：`type: array` 强制，单字符串会报类型错误。但 LLM 有时为了"省字符"会退化为标量，这条规则起到预防作用。

---

### 3. ⚠️ 部分适用
**字符串不加引号 / 代码块 / markdown**

```json
// ✅ 正确（工具调用时）
{ "path": "/root/workspace/README.md" }

// ❌ 错误（markdown 格式）
{ "path": "`/root/workspace/README.md`" }
```

> OpenClaw 校验会做 JSON parse，markdown 格式会导致 parse 失败。但这条规则对"说明性文字"（如 `prompt` 字段）约束力弱，可酌情放松。

---

### 4. ⚠️ OpenClaw 已强制
**数字和布尔不加引号**

```json
// ✅ 正确
{ "limit": 100, "silent": true }

// ❌ 错误
{ "limit": "100", "silent": "true" }
```

> OpenClaw 的 JSON Schema 对 `type: number` / `type: boolean` 强制校验，传字符串直接报错。但这条规则对 **参数构建阶段**（LLM 生成 JSON 字符串时）仍有约束价值，防止模型混淆类型。

---

### 5. ✅ 保留
**路径 / URL / ID 不格式化为 markdown 链接**

```json
// ✅ 正确
{ "url": "https://example.com/doc" }

// ❌ 错误
{ "url": "[文档链接](https://example.com/doc)" }
```

> OpenClaw 工具参数均为结构化字段，markdown 链接无法被解析。

---

### 6. ✅ 保留
**path 字段不加修饰**

```json
// ✅ 正确
{ "path": "/root/workspace/file.txt" }

// ❌ 错误
{ "path": "文件路径: /root/workspace/file.txt" }
```

---

### 7. ⚠️ 调整为"配对字段同进同出"
**成对参数（offset + limit 等）要么都传要么都不传**

```json
// ✅ 正确（两个都传）
{ "offset": 0, "limit": 20 }

// ✅ 正确（两个都不传，用默认值）
{}

// ❌ 错误（只传一个）
{ "offset": 0 }
```

> OpenClaw 校验：如果两个字段都是 optional，单独传一个通常不报错。但从业务语义上，分页参数应成对出现，否则逻辑不完整。这条规则更多是语义约束，不是校验约束。

---

### 8. ✅ 保留
**校验错误只修报错的部分，不改写整个调用**

```json
// 假设 limit 报错
// ✅ 只修 limit
{ "offset": 0, "limit": 20 }

// ❌ 不要重写整个调用（可能引入新错误）
{ "action": "list", "offset": 0, "limit": 20, "page": 1 }
```

> OpenClaw 返回的错误信息包含 `path` 和 `message`，精确定位到字段级别。全文重写反而容易扩散错误。

---

### 9. ✅ 保留（通用沟通规范）
**"Note:" 开头的是通知不是错误**

- `Error:` / `WARNING:` → 需要修复
- `Note:` / `INFO:` → 仅提示，不阻断

---

### 10. ✅ 保留（效能规范）
**用最精准的工具，不滥用 shell**

- 优先找特定工具（如 `read` / `write` / `browser`）
- `exec` / `shell` 是兜底，不是首选
- 调用 `exec` 前确认是否有更精准的工具可用

---

## 不适用于 OpenClaw 的规则

| 原规则 | 不适用的原因 |
|--------|-------------|
| 规则 1（null/空值） | OpenClaw JSON Schema 类型校验已部分覆盖，但省略 vs 传 null 的行为取决于 schema 设计，建议仍遵循"不传"原则 |
| 规则 3（字符串不加引号） | JSON parse 阶段会暴露 markdown 问题，但对 prompt 类自由文本约束较弱 |

---

## 总结

| 状态 | 规则数 |
|------|--------|
| ✅ 完整保留 | 6（1, 2, 5, 6, 8, 9, 10 → 7条） |
| ⚠️ 部分调整 | 2（3, 7） |
| 🔄 OpenClaw 已强制 | 1（4） |

**最终有效规则：8 条强制 + 1 条通用（规则 9 沟通规范）**

---

## SYSTEM_PROMPT_PATCH

```markdown
## Tool Calling 规范（强制）

1. **可选字段**：`null` / `""` / `{}` → 直接省略，不传
2. **数组字段**：单元素也用 JSON 数组 `["item"]`，不用标量 `"item"`
3. **字符串内容**：路径/URL/ID 直接写值，不加 markdown 链接或代码块包裹
4. **数字/布尔**：类型要正确，`100` 而非 `"100"`，`true` 而非 `"true"`
5. **path 字段**：只写路径本身，不加"路径为"等前缀文字
6. **成对参数**（如 offset + limit）：要么都传，要么都不传
7. **报错修复**：只改报错字段，不全文重写
8. **工具选择**：优先用最精准的专用工具，`exec` 是最后兜底
9. **Note vs Error**：`Note:` 是通知不阻断，`Error:` 才需修复
```