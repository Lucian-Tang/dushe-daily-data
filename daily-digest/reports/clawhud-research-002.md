# 🐾 Clawhud 竞品调研 & 现有采集技能清单 — clawhud-research-002

> 调研时间：2026-05-02

---

## 一、Clawhud 平台定位

Clawhud（clawhub.com）是 OpenClaw 的官方技能市场，提供技能搜索/安装/发布功能。

---

## 二、已安装的采集相关技能

| 技能名 | 路径 | 功能 | 可直接用于早报 |
|--------|------|------|---------------|
| `cn-trends-aggregator` | `skills/cn-trends-aggregator/` | 聚合百度/头条/V2EX/HN/GitHub | ✅ 最核心 |
| `baidu-hot-monitor` | `skills/baidu-hot-monitor/` | 百度热搜API抓取 | ✅ 备用百度 |
| `douyin-hot` | `skills/douyin-hot/` | 抖音热榜采集 | ✅ 已有数据 |
| `hot-topics` | `skills/web-hot/` | 微博/知乎/抖音/头条等热搜 | ✅ 备用 |
| `hot-news-aggregator` | `skills/hot-news-aggregator/` | 社会/科技/军事新闻汇总 | ✅ 已有 |
| `baidu-hot-cn` | 包含在上述 | 百度热榜监控 | ✅ 已覆盖 |

---

## 三、竞品分析

| 竞品 | 数据源 | 覆盖范围 | 限制 |
|------|--------|---------|------|
| RSSHub | rss/github | 微博/知乎/B站/各类网站RSS | 需要自建，配置复杂 |
| 今日热榜 | hotrank.cn | 国内平台聚合 | 付费，需Cookie |
| 新榜 | newrank.cn | 抖音/快手/视频号 | 需申请API，付费 |
| Nitter | nitter.net | Twitter/X 镜像 | 实例不稳定 |
| GitHub API | api.github.com | GitHub Trending | 速率限制(60 req/hr未认证) |

---

## 四、缺失技能的 Clawhud 搜索建议

| 关键词 | 预期技能 | 优先级 |
|--------|---------|--------|
| `twitter scraper` | Twitter/X 采集 | P0 |
| `hn scraper` | Hacker News 采集增强 | P1 |
| `v2ex collector` | V2EX 深度采集 | P2 |

---

## 五、结论与建议

**已覆盖：** 百度/V2EX/GitHub/HN/抖音/头条/微博/知乎 —— 几乎全覆盖中文热榜生态

**缺失项：** 推特/X 是唯一空白，需单独解决（推荐 Nitter 实例或 RSSHub Twitter 源）

**建议：** 优先安装 `cn-trends-aggregator` + `baidu-hot-monitor` 的组合，早报数据源已完整

---

*生成时间：2026-05-02*