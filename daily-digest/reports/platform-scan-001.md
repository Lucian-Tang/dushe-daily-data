# 📋 平台采集现状盘点 — platform-scan-001

> 盘点时间：2026-05-02 | 盘点范围：HN / V2EX / 百度 / 推特 / GitHub Trending

---

## 一、现有工具清单

### 🔴 HN (Hacker News)
| 工具 | 路径 | 状态 | 说明 |
|------|------|------|------|
| `hn_scraper.py` | `agents/engineering/scripts/hn_scraper.py` | ⚠️ 可用但粗糙 | 搜索糗事类关键词，Algolia API，缺重试、缺真实Topstories抓取 |
| `fetch_trends.py` (cn-aggregator) | `skills/cn-trends-aggregator/scripts/fetch_trends.py` | ✅ 可用 | 通过 Firebase API 抓 Topstories，限10条，无过滤 |

**问题：** 两个工具各自为战，没有整合；Algolia搜索不够稳定

---

### 🟡 V2EX
| 工具 | 路径 | 状态 | 说明 |
|------|------|------|------|
| `fetch_trends.py` (cn-aggregator) | `skills/cn-trends-aggregator/scripts/fetch_trends.py` | ✅ 正常 | 调用 `/api/topics/hot.json`，返回10条，速度快 |
| 直接curl | - | ✅ 可用 | `curl https://www.v2ex.com/api/topics/hot.json` |

**问题：** 官方API已支持，无反爬问题；数据字段完整（title/node/author/replies）

---

### 🟡 百度热搜
| 工具 | 路径 | 状态 | 说明 |
|------|------|------|------|
| `baidu_hot.py` (BAIDU_HOT skill) | `skills/baidu-hot-monitor/scripts/baidu_hot.py` | ✅ 可用 | 调用真实API `top.baidu.com/api/board?platform=wise&tab=realtime`，返回30条 |
| `fetch_trends.py` (cn-aggregator) | `skills/cn-trends-aggregator/scripts/fetch_trends.py` | ⚠️ 备选 | curl HTML + 正则，速度慢但稳定 |

**问题：** `baidu_hot.py` API 有时返回空数据（需加兜底逻辑）；`cn-aggregator`版本用curl正则不稳定

---

### 🔴 推特/X
| 工具 | 路径 | 状态 | 说明 |
|------|------|------|------|
| 无 | - | ❌ 缺失 | 需要Cookie/Token，X.com 反爬极严，第三方库维护成本高 |

---

### 🟢 GitHub Trending
| 工具 | 路径 | 状态 | 说明 |
|------|------|------|------|
| `fetch_trends.py` (cn-aggregator) | `skills/cn-trends-aggregator/scripts/fetch_trends.py` | ✅ 正常 | GitHub Search API，按创建时间+stars排序，限10条 |
| `hn_scraper.py` | `agents/engineering/scripts/hn_scraper.py` | ❌ 不适用 | 这是HN糗事采集 |

---

## 二、缺失清单

| 平台 | 缺失项 | 优先级 |
|------|--------|--------|
| 推特/X | 完全缺失采集方案 | P0 |
| HN | 无稳定TopStories采集（当前用Algolia搜索兜底） | P1 |
| 百度 | 百度热点API有时失效，缺兜底HTML抓取 + 重试 | P1 |
| V2EX | 当前API正常，但无本地缓存/去重机制 | P2 |
| GitHub | 当前可用，但无法抓Trending每日榜（只抓new repos） | P2 |

---

## 三、整合建议

1. **统一入口**：`daily-digest/scripts/step1_collect.sh` 已整合cn-aggregator，但各collector分散
2. **推特方案**：建议使用 `nitter` 实例（开源推特镜像）或第三方付费API
3. **HN改进**：合并 `hn_scraper.py` + `cn-aggregator` 的HN部分，取TopStories而非搜索

---

*生成时间：2026-05-02*