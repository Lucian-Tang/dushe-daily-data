# Cron 执行日志方案

**任务：** cron-exec-log-001  
**执行人：** Stephen  
**日期：** 2026-05-08

## 方案概述

创建了结构化日志包装脚本 `cron-scripts/cron-log-wrapper.sh`，为 dev-daily-report 和 industry-daily-report 两个 cron 提供可追溯的执行日志。

## 日志格式

JSONL（每行一个 JSON），写入 `/root/.openclaw/workspace/logs/cron-exec-YYYY-MM-DD.jsonl`

```json
{"timestamp":"2026-05-08T03:20:00.123Z","cron_name":"dev-daily-report","stage":"fetch","status":"started","duration_ms":0}
{"timestamp":"2026-05-08T03:20:05.456Z","cron_name":"dev-daily-report","stage":"fetch","status":"success","duration_ms":5333}
```

## 字段说明

| 字段 | 说明 |
|------|------|
| timestamp | UTC 时间戳 |
| cron_name | dev-daily-report / industry-daily-report / social-news-daily |
| stage | fetch / summarize / format / push_feishu / push_github / full |
| status | started / success / failed |
| duration_ms | 阶段耗时（毫秒） |
| error | 仅失败时包含 |

## 使用方式

```bash
# 全流程日志（所有阶段作为整体记录）
cron-scripts/cron-log-wrapper.sh dev-daily-report "full" "./run-cron.sh"

# 分阶段日志（扩展用，当前以 full 模式为主）
cron-scripts/cron-log-wrapper.sh dev-daily-report "fetch,summarize,format" "./run-cron.sh"
```

## 下一步

1. 将 wrapper 接入现有 cron 的 task prompt（在 cron 开头加 log wrapper 调用）
2. 后续可加日志分析脚本，自动检测超时/失败趋势
3. 可接入 Bitable 作为监控面板数据源
