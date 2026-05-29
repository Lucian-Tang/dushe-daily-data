# 有数Feed 网页版新功能产品调研报告

> 🔥 调研时间：2026-05-29  
> 🧠 调研员：Thomas（产品 Agent）  
> 📋 调研目的：GitHub/ClawHub 排行榜 + AI模型动态看板，两个新板块的产品方案

---

## 一、先说结论（省时间）

**两个功能都值得做，但优先级差一个量级：**

| 功能 | 优先级 | 理由 |
|------|--------|------|
| GitHub Trending Top 10 | 🔴 高 | 数据现成，10分钟能接上，天然日更 |
| ClawHub 热门技能 Top 10 | 🟡 中 | 数据格式已有，接入成本低 |
| GitHub 周报 | 🟡 中 | 需跨期数据存储，有一定工程量 |
| AI 模型动态看板 | 🔴 高 | 数据已在手，差异化核心，竞品少 |

**建议 MVP 顺序：GitHub Top 10 → ClawHub Top 10 → AI模型动态看板 → GitHub 周报**

技术复杂度最高的是周报（需要历史数据存储），最低的是 GitHub Top 10（直接接 GitHub Trending HTML）。

---

## 二、需求1：GitHub/ClawHub 前十看板 + 周报

### 2.1 功能定义

#### GitHub Trending Top 10
- 每日抓取 GitHub Trending（当日最热）Top 10 项目
- 字段：项目名、作者、描述、语言、star数、今日新增star、fork数
- 可选：附带上榜原因一句话解读（为什么火）

#### ClawHub 热门技能 Top 10
- 展示 OpenClaw 技能市场（clawhub.com）热门技能 Top 10
- 字段：技能名、下载量、版本、简介、安装量趋势
- 定位：给 AI 爱好者/开发者的技能发现入口

#### GitHub 周报
- 汇总一周内 GitHub Trending Top 10 的跨期变化
- 对比上周 Top 10：哪些新上榜？哪些排名上升/下降？
- 形态：每周一份，类似「本周 GitHub 热榜风云榜」

### 2.2 目标用户

- **GitHub Top 10**：开发者、科技从业者，了解行业技术热点
- **ClawHub Top 10**：AI 爱好者、OpenClaw 用户，找新工具
- **GitHub 周报**：周度阅读需求的用户，形成习惯性查阅

### 2.3 使用场景

- 早上花3分钟扫一眼 GitHub Top 10，了解当天技术趋势
- 想找新工具时翻 ClawHub Top 10
- 周末看一篇周报，一周技术动态尽在掌握

### 2.4 数据源调研

#### GitHub Trending

| 数据源 | 可用性 | 稳定性 | 备注 |
|--------|--------|--------|------|
| `https://github.com/trending` | ✅ 可用 | 高 | 直接 HTML 解析，已验证可抓取 |
| GitHub REST API `/search/repositories` | ⚠️ 需 auth | 高 | 有 rate limit，免费版 10次/分 |
| GitHub GraphQL API | ⚠️ 需 token | 高 | 更灵活但需认证 |
| 第三方聚合（如 star-history） | ❌ 商业付费 | - | 不考虑 |

**结论：直接爬 `github.com/trending` HTML，最快最简单。**

今日实测可抓取，Top 10 项目示例：
```
1. MoneyPrinterTurbo — 66,277 stars，今日+4,698
2. ECC (agent harness优化) — 今日+2,234
3. Taste-Skill — 26,393 stars，今日+2,234
4. stop-slop — 6,405 stars，今日+761
5. twenty (开源Salesforce替代) — 47,844 stars，今日+493
```

#### ClawHub 热门技能

| 数据源 | 可用性 | 稳定性 | 备注 |
|--------|--------|--------|------|
| `https://clawhub.com/api/skills?sort=downloads` | ✅ JSON | 高 | 已有 raw_clawhub_*.json 数据 |
| ClawHub 网页 | ⚠️ 需 JS | 中 | 不考虑 |

**结论：直接用现有 ClawHub JSON 数据，现有管线已能采集。**

已有数据示例（raw_clawhub_20260529.json）：
```json
{
  "slug": "stealthy-auto-browse",
  "displayName": "stealthy-auto-browse",
  "stats": { "downloads": 3208, "installsAllTime": 6 },
  "tags": { "latest": "2.1.0" }
}
```

#### GitHub 周报（跨期数据）

**问题：现有管线只存当日数据，没有历史快照。**

方案：
1. 每日保存一份 trending snapshot 到 `raw_github_trending_YYYYMMDD.json`
2. 周报管线读取最近7份快照，对比排名变化
3. 工程量：需要新增 cron 任务 + 存储策略（保留7天/30天）

**复杂度评估：中等偏高。** 需要修改 cron 脚本，不只是接数据。

---

## 三、需求2：AI模型动态进展综述

### 3.1 功能定义

**一张图看清楚各家AI模型在干什么：**

- 追踪：OpenAI GPT系列、Anthropic Claude系列、Google Gemini、阿里Qwen、DeepSeek 等
- 每条记录包含：模型名称、版本、核心能力突破、专注场景、一句话评价
- 展示形态：**赛道对比矩阵 + 时间线**

### 3.2 目标用户

- AI 产品经理：快速了解竞品动态，做产品决策参考
- 科技投资人：追踪模型进展，判断投资方向
- 开发者：选型参考，了解各家模型能力边界

### 3.3 使用场景

- 每周打开一次，看各家 AI "最近在干嘛"
- 对比各家的发力方向（编码？Agent？长文本？多模态？）
- 快速了解哪家突然有突破

### 3.4 数据来源

**好消息：数据已经在手。**

现有 `ai_daily_*.json` 每日管线已经采集了：
- Anthropic / OpenAI / Google 等官方博客
- VentureBeat AI 报道
- 技术媒体 AI 相关内容

今日数据示例：
```
- Claude Opus 4.8：Effort Control + 动态工作流
- GPT-5.5：DeepSWE基准夺冠，32%判分错误率
- Qwen3.7-Max：35小时自主运行，不再开源
- Figma Make：自然语言生成应用
```

**数据丰富度足够，缺的是结构化重组。**

现有 AI 日报每条是独立的"新闻"，需要：
1. 从新闻中提炼出"模型"+"能力"+"方向"的结构化标签
2. 按模型聚合，生成"XX模型最近在搞什么"的综述视角

### 3.5 展示形式建议

#### 方案A：赛道 × 模型矩阵（推荐）

```
              编码      Agent     长文本    多模态    成本
GPT-5.5       ●●●●●    ●●●●○    ●●●●●    ●●●●○    ●●○
Claude 4.8    ●●●●●    ●●●●●    ●●●●○    ●●●●○    ●●●
Gemini 2.5    ●●●○○    ●●●○○    ●●●●●    ●●●●●    ●●●●
Qwen3.7-Max  ●●●○○    ●●●●●    ●●●●○    ●●●○○    ●●●●●
DeepSeek    ●●●●○    ●●●●○    ●●●●○    ●●●○○    ●●●●●
```

**优点：一目了然，5秒钟搞清楚各家定位**
**缺点：需要人工定期更新●的判定，或者写规则自动打标**

#### 方案B：时间线视图

按周展示各模型的版本发布/能力突破时间线，适合发现"这家最近突然发力了"类型的信号。

**建议：矩阵为主（扫一眼），时间线为辅（详情页）。**

#### 方案C：卡片式（最简单，MVP优先）

每家模型一张卡片，列出最近在推的核心能力 + 一个毒舌点评。

```
┌─────────────────────────────────────┐
│ 🤖 GPT-5.5                          │
│ 近期重点：编码称霸，SWE-Bench夺冠    │
│ 方向：Agent化 + 长任务自主执行        │
│ 毒舌：排行榜第一不代表实际好用       │
└─────────────────────────────────────┘
```

**卡片式跟现有日报格式一致，改动最小，适合 MVP。**

---

## 四、竞品参考

### 4.1 GitHub Trending 类产品

| 产品 | 特点 | 值得借鉴 |
|------|------|----------|
| GitHub Trending 官网 | 直接、朴素 | 数据源本身 |
| [gitlogs.com](https://gitlogs.com) | GitHub 动态邮件订阅 | 周报形式 |
| [gitpop3.com](https://gitpop3.com) | 分析star趋势，预测爆款 | 趋势预测思路 |
| [hackerlog.app](https://hackerlog.app) | HN + GitHub 结合 | 内容整合思路 |
| [theresanaiforthat.com](https://theresanaiforthat.com) | AI工具发现，每周更新 | 技能发现+周报形式 |

**借鉴点：gitlogs 的周报邮件形式值得直接抄。**

### 4.2 AI模型动态追踪类产品

| 产品 | 特点 | 值得借鉴 |
|------|------|----------|
| [maboroshi-ai.sh](https://maboroshi-ai.sh) | 每日AI新闻精选 | 内容整合思路 |
| [FUTUREPEND](https://futurepend.com) | AI/Startup动态追踪 | 赛道矩阵形式 |
| [Supertools by aishin](https://supertools.utm.utoronto.ca) | AI工具分类+动态 | 卡片式 |
| [There's An AI For That](https://theresanaiforthat.com) | AI工具库 | 分类+热度 |

**关键发现：赛道矩阵式（像 Figma 的 Feature Overview 那种）基本没有竞品在做。** 大多是工具罗列，没有"各家在什么赛道上竞争"的视角。这是差异化机会。

---

## 五、UX/UI 建议

### 5.1 现有网页版架构

```
index.html（单页） → data-loader.js → CDN JSON files
                              ↓
                      6个 tab（汇总/行业/开发/AI/创业/设计）
```

新增两个 tab：
- `github` → GitHub Trending Top 10 + 周报
- `models` → AI 模型动态看板

### 5.2 具体 UI 建议

#### GitHub Top 10 Tab

```
┌────────────────────────────────────────────────┐
│ 💻 GitHub · 今日 Top 10                [周报→] │
├────────────────────────────────────────────────┤
│ 1. [icon] MoneyPrinterTurbo          ⭐ 66k    │
│    AI一键生成短视频                          │
│    🔥 今日 +4,698 ★  周均 +12k              │
│                                                │
│ 2. [icon] ECC                         ⭐ --    │
│    Agent Harness性能优化系统                  │
│    🔥 今日 +2,234 ★                          │
│ ...                                              │
└────────────────────────────────────────────────┘
```

**设计要点：**
- 排名数字大且醒目（1st/2nd/3rd 用不同颜色）
- 今日新增 star 突出显示（🔥 图标）
- 与昨日/上周对比用箭头（↑↓）标注升降
- 点击跳转 GitHub 详情页

#### AI 模型动态 Tab

```
┌────────────────────────────────────────────────┐
│ 🤖 AI模型动态                          本周更新 │
├────────────────────────────────────────────────┤
│ 【编码】GPT-5.5: +4  Claude 4.8: +3  Gemini: +2 │
│ 【Agent】Qwen3.7-Max: +5  Claude 4.8: +4        │
│ 【多模态】Gemini 2.5: +4  GPT-5.5: +3          │
│                                                │
│ ┌──────────────────────────────────────────┐  │
│ │ 🏆 模型能力矩阵                    [详细] │  │
│ │        编码  Agent  长文本  多模态  成本   │  │
│ │ GPT-5.5  ●●●●● ●●●●○  ●●●●● ●●●●○  ●●○   │  │
│ │ Claude4.8●●●●● ●●●●●  ●●●●○ ●●●●○  ●●○   │  │
│ │ Gemini2.5●●●○○ ●●●○○  ●●●●● ●●●●●  ●●●○  │  │
│ │ Qwen3.7  ●●●○○ ●●●●●  ●●●●○ ●●●○○  ●●●●○ │  │
│ └──────────────────────────────────────────┘  │
└────────────────────────────────────────────────┘
```

**设计要点：**
- 顶部用快捷频道（编码/Agent/多模态/长文本）快速筛选
- 中部矩阵一眼看清赛道分布
- 底部各家模型的详细卡片（可折叠）
- 卡片内：模型名 + 版本 + 核心能力 + 一句话毒舌点评

### 5.3 导航位置建议

**方案A（推荐）：在现有6个tab基础上新增2个**
```
汇总 | 行业 | 开发 | AI | 创业 | 设计 | GitHub | 模型动向
```

**方案B（次选）：把 GitHub 和模型动向做成子 tab**
```
AI（主tab）
  ├── AI资讯（现有）
  ├── 模型动向（新增）
  └── GitHub（新增）
```

**选方案A**：两个新功能都是独立使用场景，不应该藏在 AI tab 下面。GitHub 跟开发有关但不是开发资讯，是排行榜；模型动向是独立视角，跟AI资讯并列。

---

## 六、MVP 建议（先做什么后做什么）

### Phase 1：GitHub Top 10（1-2天）

**目标：** 最快速度上线，产生用户价值

**需要做的事：**
1. 写一个 cron 脚本抓 GitHub Trending HTML → 解析 → 输出 `github_trending_YYYYMMDD.json`
2. 在 index.json 加入 `github` 字段
3. 在 web demo 的 tab nav 加入 GitHub tab
4. UI：排行榜卡片样式，参考现有 card 样式

**数据格式：**
```json
{
  "published": "2026-05-29",
  "items": [
    {
      "rank": 1,
      "name": "MoneyPrinterTurbo",
      "author": "harry0703",
      "description": "利用AI大模型，一键生成高清短视频",
      "stars": 66277,
      "stars_today": 4698,
      "forks": 9597,
      "language": "Python",
      "url": "https://github.com/harry0703/MoneyPrinterTurbo"
    }
  ]
}
```

**技术复杂度：🟢 低。** 爬虫5分钟能写完，主要是解析HTML，复用现有cron框架。

---

### Phase 2：ClawHub 热门技能 Top 10（1天）

**目标：** 补全"AI工具发现"场景

**需要做的事：**
1. 改造现有 clawhub 采集脚本，过滤出 Top 10 按下载量排序
2. 输出 `clawhub_trending_YYYYMMDD.json`
3. 新增 tab，UI 参考 GitHub Top 10

**数据格式：**
```json
{
  "published": "2026-05-29",
  "items": [
    {
      "rank": 1,
      "slug": "stealthy-auto-browse",
      "name": "stealthy-auto-browse",
      "downloads": 3208,
      "version": "2.1.0",
      "summary": "Headless-detection-resistant browser automation..."
    }
  ]
}
```

**已有数据，直接复用，复杂度🟢 低。**

---

### Phase 3：AI模型动态看板（2-3天）

**目标：** 把现有 AI 日报从"新闻视角"转化为"模型视角"

**需要做的事：**
1. 新增 `models_daily_YYYYMMDD.json` 生成管线
2. 从 AI 日报中提取涉及模型的条目，按模型聚合
3. 输出结构化数据：模型名 + 能力标签 + 近期动态 + 毒舌点评
4. UI：矩阵 + 卡片

**核心挑战：** 不是数据采集，是**数据重组**——从新闻变成模型档案。
需要写一个 `enrich_models.py` 脚本做这件事。

**数据格式：**
```json
{
  "published": "2026-05-29",
  "models": [
    {
      "id": "gpt-5.5",
      "name": "GPT-5.5",
      "vendor": "OpenAI",
      "capabilities": ["coding", "agent", "long-context"],
      "highlights": [
        {
          "title": "DeepSWE基准夺冠",
          "content": "70%胜率在编码任务上领先",
          "quote": "排行榜第一不代表实际好用"
        }
      ]
    }
  ]
}
```

**技术复杂度：🟡 中。** 数据采集不难，难的是标签化和聚合逻辑。需要人工定义"能力标签"体系。

---

### Phase 4：GitHub 周报（3-5天）

**目标：** 跨期对比，产生增量信息

**需要做的事：**
1. 每日保存 GitHub Trending snapshot（`raw_github_trending_YYYYMMDD.json`）
2. 周报 cron（每周一凌晨）读取最近7份快照
3. 计算：排名变化、新上榜项目、排名突变项目
4. 输出 `github_weekly_YYYYMMDD.json`
5. UI：周报视图（类似现有 日报 的折叠样式）

**技术复杂度：🔴 偏高。** 需要：
- 存储策略（保留多少天历史？）
- 周报 cron 独立调度
- 对比算法（如何判断"上升最多"？）

---

## 七、技术复杂度总评

| 功能 | 工程量 | 存储 | 爬虫 | UI | 备注 |
|------|--------|------|------|-----|------|
| GitHub Top 10 | 🟢 小 | 无 | 有 | 小 | 直接接 GitHub Trending |
| ClawHub Top 10 | 🟢 小 | 无 | 无 | 小 | 复用现有数据 |
| AI模型动态看板 | 🟡 中 | 可选 | 无 | 中 | 数据重组，非采集 |
| GitHub 周报 | 🔴 大 | 需要 | 已有 | 中 | 需历史存储+跨期计算 |

**老板最关心的：Phase 1 和 Phase 2 加起来不超过3天就能上线。**

---

## 八、一个毒舌总结

**为什么这两个功能值得做：**

GitHub Top 10 是"送分题"——数据现成，竞品成熟（gitlogs已经在做邮件周报），用户需求明确（开发者想知道今天什么项目火了），做出来就有价值。

AI模型动态看板是"差异化牌"——现在市面上没有一家把这个做好的。各个AI媒体都在发新闻，但没有"一张图看清楚各家在干嘛"的视角。有数Feed如果能每天出一张这样的图，就能占据"AI竞品追踪"这个细分类目。

**为什么有风险：**

AI模型动态看板的数据重组需要人工事先定义"能力标签"体系——这玩意儿没有标准答案，做着做着可能变成"我们认为GPT在编码方面强"这种主观判断。需要老板想清楚：是做成客观数据展示，还是带观点的分析报告？

如果是要客观，就用新闻来源打分；如果要观点，就直接上毒舌点评。这个定位必须在开发前确定。

**ClawHub 和 GitHub 周报可以并行做，Phase 3 和 Phase 4 建议串行——Phase 3 做顺手了，Phase 4 的数据结构就清楚了。**

---

*报告完毕。🔚*