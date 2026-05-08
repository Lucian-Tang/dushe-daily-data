# 行业热点日报系统 - 技术方案
**日期:** 2026-05-07  
**状态:** 框架阶段（信源待 Thomas 注入）

---

## 系统架构图（文字版）

```
                    ┌──────────────────────────────────────┐
                    │         Cron 调度器                    │
                    │   每天 07:30 执行 daily_pipeline.sh    │
                    └──────────────┬───────────────────────┘
                                   │ /bin/bash
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     daily_pipeline.sh                             │
│  ① fetch_industry.py  →  data/raw_articles.json                  │
│  ② daily_report.py    →  reports/YYYY-MM-DD.md                   │
│  ③ push_to_feishu.py  →  飞书群消息                              │
└─────────────────────────────────────────────────────────────────┘
        │                           │                    │
        ▼                           ▼                    ▼
┌──────────────┐         ┌──────────────────┐   ┌─────────────────┐
│  RSS/API     │         │  OpenClaw LLM    │   │   飞书 Webhook   │
│  信源列表     │         │  minimax-m2.7    │   │   消息推送       │
│  (6-10个)    │         │  摘要+观点生成    │   │                 │
└──────────────┘         └──────────────────┘   └─────────────────┘
```

---

## 目录结构

```
workspace/
├── reports/
│   ├── industry-daily-pipeline-20260507.md   ← 本文档
│   ├── industry-daily-sources-20260507.md     ← Thomas 的信源文档（待生成）
│   └── 2026-05-07.md                         ← 生成的日报
├── scripts/
│   ├── fetch_industry.py                     ← 抓取脚本
│   ├── daily_report.py                       ← 日报生成脚本
│   ├── push_to_feishu.py                     ← 推送脚本
│   └── daily_pipeline.sh                     ← 调度入口
└── config/
    └── sources.yaml                          ← 信源配置（Thomas 出信源后填充）
```

---

## 抓取层 - fetch_industry.py

**技术选型:** `httpx`（异步并发）+ `feedparser`（RSS fallback）

**输入:** `config/sources.yaml` 中的信源列表（RSS / API）  
**输出:** `data/raw_articles_YYYYMMDD.json`

**核心逻辑:**
1. 读取 `config/sources.yaml`，解析信源列表（每个信源含 `name`, `url`, `type`, `category`）
2. 并发抓取（`asyncio` + `httpx.AsyncClient`，超时 15s）
3. RSS → `feedparser` 解析；API → `httpx` JSON 解析
4. 内容归一化：`{"title", "url", "source", "published", "content", "category"}`
5. **去重逻辑：** 按 `title` + `source` 做 MD5 哈希，放入 `seen` set 去重（24h 内相同标题视为重复）
6. 单源失败不影响其他源（`try/except` 包裹，超时 → 记录日志 → 继续）
7. 输出 JSON Lines 格式，便于后续追加

```python
# 关键函数签名（框架）
async def fetch_source(session: httpx.AsyncClient, source: dict) -> list[dict]:
    """抓取单个信源，返回归一化文章列表"""

async def deduplicate(articles: list[dict]) -> list[dict]:
    """按 title+source 去重"""

async def main() -> None:
    articles = await fetch_all_sources(config["sources"])
    articles = await deduplicate(articles)
    save_jsonlines(articles, output_path)
```

---

## 分析层 - daily_report.py

**技术选型:** 调用 OpenClaw 内置 LLM（`minimax-m2.7`），通过环境/内部接口

**输入:** `data/raw_articles_YYYYMMDD.json`  
**输出:** `reports/YYYY-MM-DD.md`（结构化日报）

**Prompt 设计（每条 < 50 字摘要 + < 30 字观点）:**

```
## SYSTEM PROMPT

你是一个科技产业分析师。请根据以下文章列表，生成行业热点日报。

要求：
- 每个赛道（自动驾驶、机器人、AI）各选 3-5 条最重要新闻
- 每条新闻格式：
  **【摘要】** <50字的摘要
  **【观点】** <30字的一句话分析
- 按赛道分组，格式见下方
- 只输出日报内容，不要其他说明

## 输出格式

### 🚗 自动驾驶
1. [标题](URL)
   【摘要】<50字>
   【观点】<30字>

### 🤖 机器人
...

### 🧠 AI 大模型
...

---
来源：共抓取 N 条，去重后 M 条，选取最重要的报道
生成时间：{timestamp}
```

**成本控制策略:**
- 先按 `category` 分组，每组最多取 5 条（减少 token 消耗）
- 不做全文 embedding，只用标题+摘要
- 预计输入 ~1500 tokens，输出 ~600 tokens，合计 < 3K tokens/天

**错误处理:**
- 如果 LLM 调用失败（如网络超时），脚本返回非零退出码，cron 通知
- 已抓取的文章保留，可手动重跑 `daily_report.py` 恢复

---

## 推送层 - push_to_feishu.py

**技术选型:** 飞书自定义机器人 Webhook（不需要 app token）

**输入:** `reports/YYYY-MM-DD.md`  
**输出:** 飞书群消息

**推送方式决策: 消息卡片（富文本）**

原因：
- 文档（Feishu Doc）需要 OAuth 授权链路较长
- 消息卡片支持标题+摘要+链接，手机端体验好
- 可选：同时创建飞书文档（二次确认后开启）

**消息卡片格式:**
```json
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": {"tag": "plain_text", "content": "📰 行业热点日报 | 2026-05-07"},
      "template": "blue"
    },
    "elements": [
      {"tag": "markdown", "content": "### 🚗 自动驾驶\n> [标题](url)\n> 摘要 | 观点"},
      ...
    ]
  }
}
```

**错误处理:**
- Webhook 请求超时 → 重试 2 次，间隔 5s
- 全部失败 → 写错误日志，退出码非零（cron 会收到告警）

---

## 调度层 - daily_pipeline.sh

```bash
#!/bin/bash
# daily_pipeline.sh - 行业热点日报调度入口

DATE=$(date +%Y-%m-%d)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/../logs"
mkdir -p "$LOG_DIR"

echo "[$(date)] 开始抓取行业热点..." >> "$LOG_DIR/daily.log"
python3 "${SCRIPT_DIR}/fetch_industry.py" >> "$LOG_DIR/fetch.log" 2>&1
EXIT_FETCH=$?

echo "[$(date)] 开始生成日报..." >> "$LOG_DIR/daily.log"
python3 "${SCRIPT_DIR}/daily_report.py" >> "$LOG_DIR/report.log" 2>&1
EXIT_REPORT=$?

if [ $EXIT_REPORT -eq 0 ]; then
  echo "[$(date)] 开始推送飞书..." >> "$LOG_DIR/daily.log"
  python3 "${SCRIPT_DIR}/push_to_feishu.py" >> "$LOG_DIR/push.log" 2>&1
fi

echo "[$(date)] 日报流程完成 (fetch=$EXIT_FETCH, report=$EXIT_REPORT)" >> "$LOG_DIR/daily.log"
```

**Cron 配置:**
```cron
# 每天早上 7:30 执行
30 7 * * * /root/.openclaw/workspace/scripts/daily_pipeline.sh >> /root/.openclaw/workspace/logs/crontab.log 2>&1
```

---

## 信源配置格式 - config/sources.yaml

（Thomas 出信源后填充）

```yaml
sources:
  - name: "36kr 自动驾驶"
    url: "https://36kr.cn/feed/autonomous-driving"  # 示例占位
    type: "rss"   # rss | api
    category: "auto"

  - name: "机器之心"
    url: "https://www.jiqizhixin.com/rss"
    type: "rss"
    category: "ai"

  # 更多信源...
```

---

## 错误处理策略汇总

| 场景 | 处理方式 |
|------|---------|
| 单个信源超时/失败 | 记录日志，继续其他信源，不中断 |
| LLM 调用失败 | 退出码非零，cron 告警，文章数据保留可重跑 |
| 飞书 Webhook 失败 | 重试 2 次，间隔 5s，仍失败则记录日志 |
| 抓取结果为空 | 跳过分析层，直接告警 |
| 重复文章（24h内） | MD5(title+source) 去重 |

---

## 成本预估

| 项目 | 数值 |
|------|------|
| 日均 Token 消耗 | ~2,500（输入 1500 + 输出 600 + buffer） |
| 模型 | minimax-m2.7 |
| 日均成本 | ~$0.0003 |
| 月成本 | ~$0.009 |