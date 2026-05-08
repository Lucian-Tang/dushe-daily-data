# 项目上下文

## 活跃项目

### 热点早报采集器
- **状态:** 运行中 ✅
- **负责人:** Stephen（技术实现）、Thomas（产品评估）
- **描述:** 每 30 分钟采集 HN/V2EX/知乎日报/GitHub Trending，AI 摘要后推飞书群
- **当前里程碑:** M3 端到端验收
- **关键指标:** 端到端 <60s, 4 源全通, 无重复

### Twitter 采集
- **状态:** 阻塞中 🚫
- **阻塞原因:** 所有方案（Nitter/RSSHub/twscrape）均需 Twitter 账号凭证
- **下一步:** 等 Lucian 提供凭证或确认替代方案

## 技术选型记录
- AI 摘要直连 DeepSeek V4 Pro API
- 采集用 OpenClaw agent（不用 Cursor/Claude Code）
- 发布格式化 Markdown，按来源分组

## 待决策事项
- Twitter 采集：提供凭证 vs 替换平台（如 Reddit/Product Hunt）
- 早报推送频率：30min vs 60min
