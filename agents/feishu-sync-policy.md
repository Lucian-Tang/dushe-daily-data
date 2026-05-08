# 飞书文档同步问题根治方案

## 根因
Subagent 在执行任务时无法可靠调用 `feishu_doc write`。它们会 `feishu_doc create` 建空壳，但从不写入内容。从 2026-05-08 早到晚反复出现：社会日报、Cron 方案、重构方案、家庭管家架构——每次都是空文档。

## 永久规则
**Subagent 只产出本地文件。飞书文档由 Lucia 统一负责。**

### Subagent 任务规范
- Task prompt 中删除所有"创建飞书文档"、"feishu_doc create"等指令
- Task prompt 只要求：本地 Markdown 文件 + agents/{role}/status.json 更新
- 输出路径统一在 `reports/` 或 `agents/{role}/`

### Lucia 同步流程
每个 subagent 完成后：
1. 读本地报告文件
2. `feishu_doc create` → 立即 `feishu_doc write` 写入内容
3. 更新 Bitable 记录（产出链接字段）

### 验收标准
- ✅ 本地 Markdown 文件存在且内容完整
- ✅ 飞书文档 content 不为空（revision_id > 1）
- ❌ 空文档 = 退回 Lucia 重同步
