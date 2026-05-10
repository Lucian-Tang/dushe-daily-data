# Luxmind 模型分配策略

制定：Lucia | 更新：2026-05-09

---

## 可用模型

| 别名 | 完整名 | 类型 | 月成本 | 窗口 | 特点 |
|------|--------|------|--------|------|------|
| **deepseek-v4-pro** | deepseek/deepseek-v4-pro | API | 按量 | 200K | 品质最优，对话/推理 |
| deepseek-v4-flash | deepseek/deepseek-v4-flash | API | 按量 | 200K | 更快，轻量任务 |
| **minimax-m2.7** | minimax-portal/MiniMax-M2.7 | API | 包月 | 204K | 性价比，批量任务主力 |
| minimax-m2.7-highspeed | minimax-portal/MiniMax-M2.7-highspeed | API | 包月 | 204K | 降级备用 |
| gpt-5.4 | codex/gpt-5.4 | API | 未计费 | 272K | ACP harness 用 |

---

## 分配矩阵

```
┌─────────────────────┬──────────────────────┬──────────────┐
│ 场景                 │ 模型                  │ 原因          │
├─────────────────────┼──────────────────────┼──────────────┤
│ Lucia 主对话         │ deepseek-v4-pro      │ 品质优先      │
│ → 降级链             │ m2.7 → m2.7-hs       │ 主模型挂了才切 │
│                      │                      │              │
│ Cron 定时任务（全部）  │ minimax-m2.7         │ 包月不心疼     │
│                      │                      │              │
│ Subagent spawn       │ minimax-m2.7         │ DeepSeek子代理 │
│                      │                      │ 超时率100%     │
│ 复杂子任务（例外）     │ deepseek-v4-pro      │ 需深度推理     │
│                      │                      │              │
│ Stephen 代码/架构     │ deepseek-v4-pro      │ 代码品质要求高  │
│ Thomas 产品设计       │ minimax-m2.7         │ 够用即可       │
│ Researcher 调研       │ minimax-m2.7         │ web搜索为主    │
│                      │                      │              │
│ ACP harness 编码     │ gpt-5.4              │ Codex 原生支持  │
└─────────────────────┴──────────────────────┴──────────────┘
```

---

## Cron 超时配置

| Cron | 时间 | 超时 | 模型 |
|------|------|------|------|
| hn-signals | 00:00 | 300s | minimax-m2.7 |
| github-trending-signals | 02:02 | 300s | minimax-m2.7 |
| arxiv-signals | 02:04 | 300s | minimax-m2.7 |
| producthunt-signals | 02:06 | 300s | minimax-m2.7 |
| dev-daily-report | 03:20 | 600s | minimax-m2.7 |
| ai-daily | 03:25 | 600s | minimax-m2.7 |
| startup-daily | 03:30 | 600s | minimax-m2.7 |
| design-daily | 03:35 | 600s | minimax-m2.7 |
| daily-doc-sync | 03:40 | 300s | minimax-m2.7 |
| hf-papers-daily | 09:00 | 600s | minimax-m2.7 |
| social-news-preprocess | 11:20 | 300s | minimax-m2.7 |
| social-news-daily | 11:30 | 600s | minimax-m2.7 |
| reddit-signals | 周一 02:08 | 300s | minimax-m2.7 |

---

## 成本估算（月）

| 模型 | 用途 | 预估调用 | 月成本 |
|------|------|----------|--------|
| MiniMax M2.7 | Cron + Subagent | ~300次/天 | ¥300（包月） |
| DeepSeek V4 | 主对话 | ~50次/天 | ¥200-500 |
| **合计** | | | **¥500-800** |

---

## 核心原则

1. **包月先跑** — MiniMax 包月，cron/subagent 无脑用
2. **品质不降级** — 主对话用 DeepSeek，不因成本降模型
3. **子代理不用 DS** — 超时率 100%，已证实不可用
4. **代码走 DS** — Stephen 代码任务始终 deepseek-v4-pro
5. **降级链 3 层** — DS Pro → MiniMax M2.7 → MiniMax M2.7 HS
