# Phase 1 总结报告 — 创业机会发现系统

**执行人：** Stephen  
**完成时间：** 2026-05-08 17:30 GMT+8  
**任务：** opportunity-pipeline-phase1

---

## 1. 飞书多维表格结构

### 新建 App：「Opportunity Signals」

- **App Token：** `S8mlbvHk6a4a6ss46klcw5CSnCY`
- **Table ID：** `tblIiWi9t04d0u5D`
- **URL：** https://my.feishu.cn/base/S8mlbvHk6a4a6ss46klcw5CSnCY

### 字段设计（8个字段）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| Opportunity Signals（主字段） | 文本 | 信号标题，如 "[GitHub] repo-name (500⭐)" |
| 信源 | 单选 | HN / GitHub / arXiv / ProductHunt / Reddit / V2EX |
| 信号类型 | 单选 | 融资 / 产品发布 / 技术突破 / 政策 / 痛点 |
| 原始链接 | URL | 原始页面链接 |
| 原始摘要 | 文本 | 100字以内的原始内容摘要 |
| 粗筛评分 | 数字 | 1-10，4维粗筛得分 |
| 状态 | 单选 | raw / screening / deep_eval / opportunity_card / archived |
| 发现时间 | 日期 | 自动（auto_fill=true） |
| 标签 | 多选 | AI / 硬件 / 消费 / SaaS / 工具 / LLM / Agent / 开发者工具 / 开源 |

---

## 2. Cron Job 配置

### jobs.json 路径：`cron/jobs.json`

| Job Name | Schedule | Timeout | Script | 信源 | 频率 |
|----------|----------|---------|--------|------|------|
| hn-signals | `00 03 * * *` | 300s | `cron/scripts/hn_signals.py` | Hacker News Top 10 | 日更 03:00 |
| github-trending-signals | `10 03 * * *` | 300s | `cron/scripts/github_trending_signals.py` | GitHub Trending | 日更 03:10 |
| arxiv-signals | `20 03 * * *` | 300s | `cron/scripts/arxiv_signals.py` | arXiv cs.AI/cs.LG/cs.CL | 日更 03:20 |
| producthunt-signals | `30 03 * * *` | 300s | `cron/scripts/producthunt_signals.py` | Product Hunt | 日更 03:30 |
| reddit-signals | `00 03 * * 1` | 300s | `cron/scripts/reddit_signals.py` | r/startups + r/entrepreneur + r/SideProject + r/smallbusiness | 周更 周一03:00 |

---

## 3. 采集脚本实现

### 脚本列表（`cron/scripts/`）

| 脚本 | 功能 | 粗筛条件 |
|------|------|----------|
| `hn_signals.py` | Firebase API 获取 HN Top 10 | 分数>100 + 含AI/ML/Startup/Tool等关键词 |
| `github_trending_signals.py` | 爬取 GitHub Trending 页面 | Star>200 + Python/JS/Go/Rust + 描述含AI/ML/LLM/Agent |
| `arxiv_signals.py` | arXiv API 查询 cs.AI/cs.LG/cs.CL | 摘要含 LLM/Agent/Multimodal/Vision+Language 等 |
| `producthunt_signals.py` | 爬取 Product Hunt 首页 | 投票>200 + 分类为AI/Tools/Developer Tools |
| `reddit_signals.py` | Reddit JSON API 获取热帖 | Score>200 + 标题含 pain point/frustrated/looking for 等 |

### 通用设计
- **本地数据落地：** `data/opportunities/{source}/{YYYY-MM}.json`，每条信号按月 append
- **输出格式：** `{"date": "YYYY-MM-DD", "source": "...", "total_fetched": N, "passed_filter": M, "signals": [...]}`
- **JSONL 日志：** 每条记录写入 `logs/cron-exec-YYYY-MM-DD.jsonl`
- **4维粗筛评分：** engagement + activity + keyword relevance + credibility，1-10 分

---

## 4. 当前数据

- 飞书多维表格已创建，字段已配置完毕（不含数据，待 cron 首次触发）
- 本地 data/opportunities/{hn,github,arxiv,producthunt,reddit} 目录已初始化

---

## 5. 下一步建议（Phase 2）

1. **信源扩展：** 加入 V2EX、36kr 融资、Crunchbase API（Thomas 流程设计中的信源）
2. **去重层：** 实现 MinHash 去重，避免同一信号重复写入
3. **NLP 分类：** 从关键词规则升级为零样本 NLP 分类（bge-large-zh-v1.5）
4. **飞书写入认证：** 当前 feishu_bitable_client.py 依赖 `FEISHU_ACCESS_TOKEN` 环境变量，需确认 token 配置
5. **定时触发：** 将 jobs.json 接入实际 cron 系统（当前仅配置文件存在）

---

*文档版本：v1.0 | Stephen | 2026-05-08*