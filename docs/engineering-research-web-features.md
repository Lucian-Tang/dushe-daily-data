# 有数Feed 网页版新功能 — 工程调研报告

> 日期: 2026-05-29  
> 调研人: Stephen (Engineering Agent)  
> 仓库: dushe-daily-data  
> 版本: v1.2

---

## 1. 现有架构分析

### 1.1 Web Demo (`web-demo/index.html`)

| 维度 | 现状 |
|------|------|
| 框架 | 纯 vanilla HTML/CSS/JS，无框架依赖，单文件 27KB |
| 数据加载 | 先请求 `index.json` 获取各板块最新文件路径，再并行加载各板块的 per-day JSON |
| 路由 | 无路由，纯 tab 切换，前端 state |
| 板块 | 5 个: industry / dev / ai / startup / design |
| 展示 | 今日汇总 + 单板块列表（按日期分组折叠），支持暗色模式 |
| 历史数据 | 每个板块加载今日 + 最近 2 天历史数据 |
| 部署 | GitHub Pages 静态托管 |

**关键发现**：
- 整个 demo 是**纯静态单文件**，没有构建工具、没有框架、没有后端
- 加载 6 个 JSON 文件（1 index + 5 sections），总数据量约 50-200KB
- 加载流程是串行 index → 并行 sections，简洁高效
- 新增板块只需：添加数据文件 + 在 index.html 加 tab 和渲染逻辑

### 1.2 数据管线架构

```
Cron (03:15 - 04:30 每日)
    │
    ├── fetch_industry.py → raw_articles_YYYYMMDD.json
    ├── fetch_dev.py      → raw_dev_YYYYMMDD.json      (含 GitHub Trending HTML 爬虫)
    ├── fetch_startup.py  → raw_startup_YYYYMMDD.json
    ├── fetch_design.py   → raw_design_YYYYMMDD.json
    ├── fetch_social_news.py → raw_social_YYYYMMDD.json
    ├── fetch_clawhub.py  → raw_clawhub_YYYYMMDD.json  (via clawhub CLI)
    │
    ▼  MD 报告生成 (AI agent 每日生成)
    │
    ├── generate_daily_json.py   → {section}_daily_YYYYMMDD.json
    │   (解析 MD 报告 + raw JSON → 标准化 6 字段格式)
    │
    ├── normalize_daily_data.py  → 数据规范化
    ├── gen-index.py             → index.json
    │
    ▼  Git push to staging → promote to main → GitHub Pages 自动部署
```

**数据格式（标准 6 字段）**：
```json
{
  "title": "文章标题",
  "content": "摘要/正文 (200字内)",
  "quote": "毒舌点评 (15-30字)",
  "source": "来源名称",
  "url": "原文链接",
  "published": "2026-05-29",
  "uid": "section_hash8"   // 8位MD5哈希，跨天去重用
}
```

### 1.3 关键脚本速查

| 脚本 | 作用 | 关键发现 |
|------|------|---------|
| `fetch_dev.py` | 抓取 8 个 RSS + GitHub Trending HTML 爬虫 | GitHub Trending 已部分实现（HTML 解析，非 API） |
| `fetch_clawhub.py` | 调用 `clawhub explore` CLI 采集技能市场数据 | 已完全实现，数据注入 dev 板块 |
| `generate_daily_json.py` | 解析 MD 报告 + raw JSON → 标准化 JSON | 支持 5 板块，ClawHub 作为 dev 板块补充 |
| `generate_combined_3days.py` | 聚合 3 天数据 | 已有去重/uid/敏感词过滤逻辑 |
| `sync_github_pages.sh` | 每日同步主流程 | 完整链路：fetch → enrich → gen → normalize → index → git push → promote |

---

## 2. 需求 1: GitHub/ClawHub 看板 + 周报

### 2.1 现状分析

**GitHub Trending**：
- `fetch_dev.py` 已用 HTML 爬虫抓取 `github.com/trending?since=daily`
- 获取到 repo 名和描述，但**缺少 stars 数、语言、topics、daily stars 增量**
- 当前作为 dev 板块原始数据的一部分，没有独立展示
- GitHub API 已认证，5000 req/hr，完全够用

**ClawHub 技能市场**：
- `fetch_clawhub.py` 完全实现：newest 25 + trending 25 → 去重 → raw JSON
- `generate_daily_json.py` 有 `parse_clawhub()` 函数：排序、取 5-8 条精华、生成中文摘要 + 毒舌点评
- 当前混入 dev 板块，没有独立板块

### 2.2 数据获取方案

| 数据源 | 方案 | API 成本 | 实现难度 |
|--------|------|---------|---------|
| GitHub Trending | GitHub REST API `/search/repositories?q=created:>YYYY-MM-DD&sort=stars` | 30 req/min，5000 req/h，每天约 5 次请求 | ⭐ 低（已有认证） |
| GitHub Trending | 现有 HTML 爬虫增强 | 无限制（HTTP） | ⭐⭐ 中（HTML 解析脆弱） |
| ClawHub | 已有 `fetch_clawhub.py` + `clawhub explore` CLI | 无限制（本地 CLI） | ⭐ 低（已完成） |

**推荐**: 用 GitHub REST API 替代 HTML 爬虫，可以获取 stars/language/description/topics 等结构化数据。同时保留 HTML 爬虫作为降级方案。

### 2.3 数据格式新增

新增 `github_daily_YYYYMMDD.json`：
```json
[
  {
    "uid": "github_abc12345",
    "title": "repo/name",
    "content": "项目描述",
    "quote": "毒舌点评", 
    "source": "GitHub Trending",
    "url": "https://github.com/repo/name",
    "language": "TypeScript",
    "stars": 1234,
    "stars_today": 56,
    "topics": ["ai", "agent"],
    "published": "2026-05-29"
  }
]
```

新增 `clawhub_daily_YYYYMMDD.json`（从 dev 板块拆出）：
```json
[
  {
    "uid": "clawhub_abc12345",
    "title": "skill-display-name",
    "content": "中文描述",
    "quote": "毒舌点评",
    "source": "ClawHub",
    "url": "https://clawhub.ai/skills/slug",
    "published": "2026-05-29"
  }
]
```

**周报数据** `weekly_github_YYYYMMDD.json` / `weekly_clawhub_YYYYMMDD.json`：
- 由管线脚本预计算生成（可选，也可以前端聚合）
- 包含：7 天新增项目数、周星标最多 top 10、本周新上榜、趋势变化

### 2.4 架构方案: 纯静态 ✅

**结论：纯静态完全满足，不需要后端。**

理由：
1. 数据量小：每日 GitHub top 10-20 个项目 + ClawHub top 5-8 个技能 = ~10-15KB
2. 周报可预计算：管线里新增一个脚本跑聚合，生成 `weekly_*.json`
3. 已认证 GitHub API：5000 req/h 足够，只需每天 5 次请求
4. GitHub Pages 免费，无服务端成本

**不选后端的理由**：
- 当前无服务器/容器基础设施
- 数据不需要实时性（日/周更新即可）
- 纯静态 CDN 部署已有成熟链路
- 新增后端会增加运维负担（部署、监控、安全）

### 2.5 管线集成位置

```
现有管线
  ├── ...
  ├── sync_github_pages.sh
  │     ├── fetch_clawhub.py      ← 已有，需改为输出独立板块文件
  │     ├── generate_daily_json.py ← 已有，需加 --section github + --section clawhub
  │     ├── [NEW] fetch_github.py  ← 新增：GitHub API 采集
  │     ├── [NEW] generate_weekly.py ← 新增：周报聚合
  │     ├── gen-index.py
  │     └── git push ...
```

最小侵入性：在 `sync_github_pages.sh` 的 Step 1.5 和 Step 2.5 之间插入新步骤。

---

## 3. 需求 2: AI 模型动态进展综述

### 3.1 现状分析

- `ai_daily_YYYYMMDD.json` 每日约 10-20 条 AI 新闻
- 内容丰富：Anthropic/OpenAI/Google/Meta/DeepSeek/Qwen/Amazon 等均有覆盖
- **当前问题**：
  - 数据是扁平列表，没有按模型/公司维度聚合
  - 没有方向标签（如 "模型发布"、"工具/平台"、"研究/论文"、"应用/落地"、"政策/合规"）
  - 跨天数据没有关联（同一模型的多天动态无法串联）

### 3.2 数据获取方案

**不需要新增采集**，完全基于现有 AI 日报数据做后处理。

处理管线：
```
ai_daily_YYYYMMDD.json (现有)
    │
    ▼  NLP 分类/打标
    │
    ├── 模型归属: rule-based keyword matching
    │   (Anthropic/Claude → anthropic, OpenAI/GPT → openai, ...)
    │
    ├── 方向标签: rule-based + LLM classification
    │   (模型发布, 工具/平台, 研究/论文, 应用/落地, 政策/合规, 行业动态)
    │
    ▼  聚合输出
    │
    ├── ai_models_daily_YYYYMMDD.json  (每日模型动态)
    └── ai_models_weekly_YYYYMMDD.json (周度综述)
```

**方向标签分类规则（Rule-based 优先）**：

| 标签 | 关键词匹配 |
|------|----------|
| 模型发布 | 发布、上线、推出、release、launch、upgrade、升级 |
| 工具/平台 | SDK、API、plugin、agent、workflow、tool、coding、IDE |
| 研究/论文 | 论文、paper、benchmark、research、训练、training、架构 |
| 应用/落地 | 合作、deploy、应用、企业、医疗、金融、教育、integration |
| 政策/合规 | 监管、policy、合规、法律、copyright、开源、open source |
| 行业动态 | 融资、收购、hire、裁员、partnership、trend |

### 3.3 数据格式设计

`ai_models_daily_YYYYMMDD.json`：
```json
{
  "date": "2026-05-29",
  "models": {
    "anthropic": {
      "displayName": "Anthropic/Claude",
      "icon": "🧬",
      "items": [
        {
          "uid": "ai_0bc762db",
          "title": "Claude Opus 4.8 发布",
          "direction": "模型发布",
          "quote": "毒舌点评",
          "url": "...",
          "published": "2026-05-29"
        }
      ]
    },
    "openai": { ... },
    "google": { ... }
  },
  "summary": "本周 AI 圈... (综述文字)"
}
```

`ai_models_weekly_YYYYMMDD.json`：
```json
{
  "week_start": "2026-05-23",
  "week_end": "2026-05-29",
  "summary": "本周 Anthropic 密集发布 Opus 4.8 + Claude Code 动态工作流...",
  "stats": {
    "total_items": 87,
    "by_model": { "anthropic": 12, "openai": 9, ... },
    "by_direction": { "模型发布": 15, "工具/平台": 23, ... }
  },
  "timeline": [
    { "date": "2026-05-23", "models": { "anthropic": [...], ... } },
    ...
  ],
  "highlights": [ ... ]  // 本周最重要的 5 条
}
```

### 3.4 前端展示方案

新增页面/tab: **🤖 AI 大模型动态**

两种展示模式：
1. **按公司/模型分组**：卡片式布局，每个模型一个卡片，显示最近动态
2. **时间线模式**：水平时间轴，7 天按日期排列

推荐**卡片式 + 折叠**：每个模型一个可折叠卡片，默认展开最新 3 条。

---

## 4. 实施路径

### Phase 1: GitHub/ClawHub 独立板块 (1-2 天)

```
目标：在 web-demo 新增 "开源" 和 "技能" 两个 tab

任务：
1.1 新增 fetch_github.py         — GitHub API 采集团队 (0.5天, ~200行)
1.2 修改 fetch_clawhub.py        — 输出独立板块文件 (0.2天, ~20行改动)
1.3 修改 generate_daily_json.py  — 加 --section github/clawhub (0.3天, ~100行)
1.4 修改 sync_github_pages.sh    — 插入新步骤 (0.1天, ~15行)
1.5 修改 gen-index.py            — 注册新板块 (0.1天, ~5行)
1.6 修改 web-demo/index.html     — 加 tab + 渲染 + 加载逻辑 (0.5天, ~150行)

里程碑：网页版出现 GitHub 和 ClawHub 两个新 tab
```

### Phase 2: AI 模型动态综述 (2-3 天)

```
目标：新增 "AI 模型动态" tab，按公司/模型聚合 AI 日报

任务：
2.1 新增 classify_ai_models.py   — 分类+打标脚本 (0.5天, ~200行)
2.2 新增 generate_ai_models_daily.py — 每日模型聚合 (0.5天, ~150行)
2.3 新增 generate_ai_models_weekly.py — 周度综述生成 (0.5天, ~200行)
2.4 修改 sync_github_pages.sh    — 插入新步骤 (0.1天, ~10行)
2.5 修改 gen-index.py            — 注册新板块 (0.1天, ~5行)
2.6 修改 web-demo/index.html     — 加 tab + 卡片布局 + 折叠交互 (1天, ~300行)

里程碑：AI 大模型动态综述上线，可按模型/公司查看进展
```

### Phase 3: 周报聚合 (1-2 天)

```
目标：为 GitHub、ClawHub、AI 模型分别提供周报视图

任务：
3.1 新增 generate_weekly_github.py    — GitHub 7 天聚合 (0.3天, ~150行)
3.2 新增 generate_weekly_clawhub.py   — ClawHub 7 天聚合 (0.2天, ~100行)
3.3 修改 generate_ai_models_weekly.py — 扩增周报内容 (0.3天, ~150行)
3.4 修改 sync_github_pages.sh         — 增加周报生成步骤 (0.1天, ~10行)
3.5 修改 web-demo/index.html          — 加周报视图切换 (0.5天, ~200行)

里程碑：每个板块支持日/周视图切换
```

---

## 5. 工作量估算

| 产物 | 数量 | 代码量 | 难度 |
|------|------|--------|------|
| 新 Python 脚本 | 5 个 | ~1000 行 | ⭐⭐ |
| 修改现有脚本 | 4 个 | ~150 行改动 | ⭐ |
| web-demo 改动 | 1 文件 | ~650 行新增 | ⭐⭐ |
| 管线配置 | shell 脚本 | ~50 行新增 | ⭐ |
| **总计** | **10 文件** | **~1850 行** | — |

**时间估算**：4-7 个工作日（单人）

**API 接入难度**：
- GitHub REST API: ⭐ 极低（已认证，文档完善，Python SDK 可用）
- ClawHub CLI: ⭐ 极低（已完成）
- AI 模型分类: ⭐⭐ 低（rule-based 为主，LLM 降级增强）

---

## 6. 技术风险点

### 风险 1: GitHub API 频率限制
- **风险等级**: 🟡 低
- **说明**: 无认证 60 req/h，已认证 5000 req/h
- **配置项**: 每日约 5 次请求（1 search + 4 repo details），远低于限制
- **降级**: 保留现有 HTML 爬虫作为 fallback

### 风险 2: GitHub Trending HTML 爬虫脆弱
- **风险等级**: 🟡 低
- **说明**: GitHub 改 HTML 结构会导致爬虫失效
- **缓解**: 用 API 替代 HTML 爬虫作为主方案，爬虫仅作降级

### 风险 3: AI 模型分类准确率
- **风险等级**: 🟡 中低
- **说明**: 纯 rule-based 分类可能误分类边缘内容
- **缓解**: 多层规则（title+content+source 联合判定）+ LLM double-check 可疑条目

### 风险 4: web-demo 文件膨胀
- **风险等级**: 🟢 极低
- **说明**: 当前 27KB，新增 ~650 行后约 45KB
- **缓解**: 合理组织代码，保持单文件但用注释分区

### 风险 5: 周报数据量
- **风险等级**: 🟢 极低
- **说明**: 7 天聚合数据约 30-50KB，远低于 GitHub Pages 限制 (1GB repo / 100GB 带宽)

### 风险 6: clawhub CLI 依赖
- **风险等级**: 🟡 低
- **说明**: `sync_github_pages.sh` 已有降级处理（`command -v clawhub` 检查失败则跳过）
- **缓解**: 保持降级逻辑，ClawHub 板块无数据时显示占位

---

## 7. 推荐方案总结

| 决策 | 推荐 | 原因 |
|------|------|------|
| 架构 | **纯静态** | 数据量小、无实时要求、0 运维成本 |
| GitHub 数据源 | **REST API 为主 + HTML 爬虫降级** | API 结构化、爬虫免费无边限 |
| ClawHub 数据源 | **已有方案不变** | 完全可用，只需拆出独立板块 |
| AI 模型分类 | **Rule-based + LLM fallback** | 成本低、可离线、准确性可接受 |
| 周报方案 | **管线预计算** | 减少前端请求数、加速首屏 |
| 前端实现 | **纯 JS 增量修改** | 保持架构一致性，不加框架 |
| 部署 | **现有 GitHub Pages** | 无需变更 |

---

## 附录: 现有管线的数据流全景图

```
┌─────────────────────────────────────────────────────────────┐
│                    CRON 每日调度                              │
│                     03:15-04:30                              │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  fetch_      │  MD 报告     │  generate_   │  sync_github_  │
│  *.py        │  (AI agent)  │  daily_json  │  pages.sh      │
│              │              │              │                │
│  行业/开发/  │  dev-daily/  │  解析MD+raw  │  1. enrich     │
│  AI/创投/    │  ai-daily/   │  → 标准JSON  │  2. clawhub    │
│  设计/Claw   │  design/     │  6字段+uid   │  3. copy raw   │
│  Hub         │  startup/    │              │  4. gen daily  │
│  ↓           │  industry/   │  输出:        │  5. normalize  │
│  raw_*.json  │  ↓           │  *_daily_    │  6. gen index  │
│  → data/     │  reports/    │  YYYYMMDD    │  7. QA check   │
│              │  {sec}-      │  .json       │  8. git push   │
│              │  daily/      │              │     staging    │
│              │  YYYY-MM-    │              │  9. promote    │
│              │  DD.md       │              │     → main     │
└──────────────┴──────────────┴──────────────┴────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │    GitHub Pages (CDN)      │
                    │  dushe-daily-data/         │
                    │  ├── index.json            │
                    │  ├── ai_daily_*.json       │
                    │  ├── dev_daily_*.json      │
                    │  ├── industry_daily_*.json │
                    │  ├── startup_daily_*.json   │
                    │  ├── design_daily_*.json   │
                    │  └── web-demo/index.html   │
                    └───────────────┬───────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │  web-demo/index.html       │
                    │  (纯静态 SPA)              │
                    │                            │
                    │  加载 index.json           │
                    │  → 并行请求板块 JSON      │
                    │  → Tab 渲染               │
                    └───────────────────────────┘
```
