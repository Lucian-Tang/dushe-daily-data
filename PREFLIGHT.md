# PREFLIGHT.md — Lucia 行为准则（强制执行版）

> ⚠️ 这不是建议，是硬约束。每次回复前必须过一遍。

## 发送前自检

### 飞书文档
- [ ] 单次写入不超过 5000 字符
- [ ] 多板块用 `append` 分批写，不一次 `create` 全量
- [ ] 写完后 `read` 验证 block_count > 100
- [ ] 6 个板块（行业/开发者/AI/社会/创投/设计）全部存在

### 日报内容
- [ ] 每条新闻都有 🔥 毒舌点评（不是纯信息搬运）
- [ ] 每条有来源链接（http 开头）
- [ ] 每个板块至少 3 条
- [ ] 格式统一：同板块内标题层级一致

### Subagent 管理
- [ ] Spawn 后立即记录到 agent status
- [ ] 设置 timeout >= 120s（300s 的 minimax 容易卡）
- [ ] 超时 80% 无输出 → kill + 降级处理
- [ ] Kill 后不静默，群通知

### Cron 监控
- [ ] 任何 error 立即通知，不等心跳
- [ ] Timeout 自动 +300s 重试一次
- [ ] 连续 3 次失败 → 群求助 Boss

### 数据发布
- [ ] GitHub push 后验证 index.json 有所有频道
- [ ] 小程序上传后确认版本号正确
- [ ] 飞书文档 URL 确保 Boss 有编辑权限

## 翻车时
1. 立即记录到 `failures/failure-log.json`
2. 提取为新的检查规则
3. 更新本文件（如果需要）

---

*Last updated: 2026-05-10 10:10 CST — after a morning of catching mistakes*
