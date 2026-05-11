# 信源健康报告 | 2026-05-11

## 一、行业日报 ✅ 已修复

- **industry_daily_20260511.json**: ✅ 生成完成，14条记录
- 解析自 `reports/industry-daily/2026-05-11.md`
- 信源覆盖: The Verge(5) · TechCrunch(4) · Hacker News(4) · 知乎(1)

### 行业信源扩增建议

| 信源 | 建议 | RSS/URL | 状态 |
|------|------|---------|------|
| 36氪 | 商业/科技/消费 | `https://36kr.com/feed` | ✅ 已验证可用 |
| 晚点LatePost | 深度商业报道 | 无公开RSS，需自建抓取 | ⚠️ 需开发 |
| The Verge | 全站科技 | `https://www.theverge.com/rss/index.xml` | ✅ 可用 |
| TechCrunch | 全站科技 | `https://techcrunch.com/feed/` | ✅ 可用 |

---

## 二、社会板块国内信源 ⚠️ 需替换

### 当前状态
- **腾讯新闻**: ❌ 403 Forbidden
- **澎湃新闻**: ❌ 403 Forbidden  
- **微博热搜**: ⚠️ 30条，但100%娱乐/体育内容（国乒、世乒赛等）

### 现有 raw_social 构成 (110条)
| 信源 | 条数 | 类型 |
|------|------|------|
| 微博热搜 | 30 | 娱乐/体育 |
| Google News Top | 20 | 国际新闻 |
| BBC News World | 20 | 国际新闻 |
| Reddit WorldNews | 20 | 国际新闻 |
| NYT World | 20 | 国际新闻 |
| **国内新闻** | **0** | **空缺** |

### 建议新增（已测试）

| 信源 | 类型 | RSS/API URL | 验证结果 |
|------|------|-------------|---------|
| 中国新闻网 | 国内综合 | `http://www.chinanews.com/rss` (HTML页) | ⚠️ 返回HTML需找真实feed |
| 网易新闻 | 国内综合 | `https://news.163.com/rss` | ❌ 403 |
| 搜狐新闻 | 国内综合 | `https://www.sohu.com/rss` | ❌ 403 |
| 观察者网 | 政经/国际 | `https://rsshub.app/guancha/index` | ❌ 403 (公版RSSHub) |
| RSSHub (自建) | 全站代理 | 自建实例 | ✅ 推荐方案 |

**推荐方案**: 自建 RSSHub 实例（docker 一键部署），可解锁所有国内媒体 RSS + Dribbble + 36氪等公版 RSSHub 无法访问的路由。公版 `rsshub.app` 目前对所有测试路由返回 403。

---

## 三、设计板块 Dribbble ❌ 损坏

### 测试结果

| 方案 | URL | 结果 | 说明 |
|------|-----|------|------|
| RSSHub 公版 | `rsshub.app/dribbble/popular` | ❌ 403 | Cloudflare 挑战 |
| Dribbble RSS | `dribbble.com/shots/popular.rss` | ❌ 202/0字节 | Cloudflare 挑战 |
| Dribbble 网站 | `dribbble.com` | ❌ 需JS渲染 | 空数据 |
| Behance RSS | `behance.net/rss` | ❌ 400 | 格式错误/需认证 |
| Designspiration | `designspiration.net/rss` | ❌ 404 | 路由不存在 |

### 推荐方案

**方案1 (推荐)**: 自建 RSSHub + Dribbble route
```bash
# RSSHub 支持 Dribbble 路由，需自建
docker run -d --name rsshub -p 1200:80 diygod/rsshub
# 访问 http://localhost:1200/dribbble/popular
```

**方案2**: 换用 Behance (Adobe系，RSS 可能需要修复)
```bash
# 尝试不同格式
https://www.behance.net/creators/feed
https://behance.net/featured/feed
```

**方案3**: 使用 CSS Winner / Awwwards 等替代设计榜单
- CSS Winner: `https://csswinner.com/rss/` (需验证)
- Awwwards: `https://www.awwwards.com/blog/feed/` (需验证)

---

## 四、提交记录

```
fix: industry daily JSON + source health report
- 修复 parser bug: 舆情小结 in part 导致 Part 14 被错误跳过 → 现在正确解析14条
- 生成 industry_daily_20260511.json (14条)
- 新增 SOURCE_HEALTH_20260511.md (信源健康报告)
```
