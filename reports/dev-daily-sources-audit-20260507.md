# 开发者日报信源调研报告

**负责人：** Thomas（产品经理）
**日期：** 2026-05-07
**目标：** 补全现有 5 个信源，目标是最终覆盖 8-12 个高质量信源

---

## 一、现有信源评估

### 1.1 现状总览

| # | 信源 | 状态 | 问题 |
|---|------|------|------|
| 1 | HN Show HN | ⚠️ 需确认 | HN 域名结构已变，需验证实际 URL |
| 2 | HN Front Page | ✅ 正常 | 持续可用 |
| 3 | V2EX Tech | ✅ 正常 | 有 RSS |
| 4 | V2EX Share/创造 | ✅ 正常 | 有 RSS |
| 5 | ClawHub Hot | ❌ API 404 | **待修**，见下节 |

### 1.2 ClawHub API 404 问题分析

**原因：** ClawHub 公开 API 尚不稳定，频繁变更端点或 Token 认证失效。

**替代方案：**

| 替代方案 | URL | 可用性 | 备注 |
|----------|-----|--------|------|
| ClawHub 官网手动抓取 | https://clawhub.com | 需 browser | 每日一次可接受 |
| SkillHub（优先国内源） | https://skillhub.hk | ✅ 可用 | 国内团队优先推荐 |
| NPM Registry 监控 | https://registry.npmjs.org | ✅ API | 监控 `openclaw` 关键词包更新 |

**建议：** 短期用 SkillHub + NPM 监控组合；长期等 ClawHub API 稳定后接回。

### 1.3 V2EX / HN 是否够用？

**结论：不够。** 两者合计覆盖：
- HN → 英文技术社区主流声音，但缺乏系统性项目发现
- V2EX → 国内开发者社区，但体量偏小、节奏慢

缺少的维度：
- **新项目爆发发现**（GitHub Trending、ProductHunt）
- **中文专业内容平台**（掘金、SegmentFault）
- **小众但高质量的技术讨论**（lobste.rs）
- **框架/工具更新主动通知**（GitHub Releases、Changelog）

---

## 二、候选信源调研（15 个候选 → 精选 10 个）

### 2.1 新项目 / 工具发现

#### ★ GitHub Trending
- **URL：** https://github.com/trending
- **RSS：** `https://github.com/trending?since=daily.rss`（非标准，需构造）
- **类型：** 趋势榜单 / 英文
- **更新频率：** 每日多次
- **抓取方式：** HTML 爬虫（页面结构稳定）
- **可靠度：** **A**
- **价值：** 全球开源项目爆发地，涵盖所有语言，是新工具发现的第一入口。推荐同时抓 Python、Go、Rust、JS 四榜。
- **建议优先级：** 🔥 P0

#### ★ ProductHunt
- **URL：** https://www.producthunt.com
- **RSS：** `https://feeds.feedburner.com/ProductHunt`（Atom，✅ 已验证 200）
- **类型：** 新产品发布 / 英文
- **更新频率：** 每日
- **抓取方式：** RSS（稳定）
- **可靠度：** **A**
- **价值：** 覆盖 SaaS、工具、API 类新产品发布，偏产品视角，与 GitHub 互为补充。
- **注意：** FeedBurner 被墙，需配置代理或 relay。

#### ★ lobste.rs
- **URL：** https://lobste.rs
- **RSS：** `https://lobste.rs/t/programming.rss`（✅ 已验证 200）
- **类型：** 技术讨论 / 英文
- **更新频率：** 实时
- **抓取方式：** RSS（稳定）
- **可靠度：** **A**
- **价值：** 高质量小众技术社区，讨论深度优于 HN，审核制确保内容质量。对后端/系统/语言话题覆盖深。
- **建议优先级：** 🔥 P1

---

### 2.2 技能 / 框架生态

#### ★ GitHub Releases（监控特定组织）
- **URL：** https://github.com/{org}/{repo}/releases
- **RSS：** `https://github.com/{org}/{repo}/releases.atom`
- **类型：** 版本发布 / 多语言
- **更新频率：** 按需
- **抓取方式：** Atom RSS（稳定）
- **可靠度：** **A**
- **价值：** 监控我们依赖的核心框架更新（如 OpenClaw 自身、t3 stack、vercel 等）。可与我们技术栈强关联。
- **建议优先级：** P1

#### NPM Registry（openclaw 生态）
- **URL：** https://registry.npmjs.org/-/v1/search
- **API：** `?text=openclaw&size=10`（✅ 可用）
- **类型：** NPM 包更新 / 英文
- **更新频率：** 按需
- **抓取方式：** REST API（稳定）
- **可靠度：** **A**
- **价值：** 监控 OpenClaw 相关插件/Skill 包更新。
- **建议优先级：** P2

#### ★ Lobster Skills Changelog
- **URL：** https://lobster.tools/changelog
- **RSS：** 待验证（页面有更新日志）
- **类型：** 技能更新 / 英文
- **更新频率：** 按版本
- **抓取方式：** HTML 爬虫
- **可靠度：** **B+**
- **价值：** Lobster 是 OpenClaw 的重要技能来源，其 changelog 直接反映能力演进。
- **建议优先级：** P2（有条件接入）

---

### 2.3 技术深度讨论

#### Dev.to（替代 HN 的英文深度讨论）
- **URL：** https://dev.to
- **RSS：** `https://dev.to/feed`（✅ 常见 Atom/RSS）
- **类型：** 技术博客 / 英文
- **更新频率：** 实时
- **抓取方式：** RSS
- **可靠度：** **A**
- **价值：** 覆盖前端、云原生、AI 工程化等话题，作者群体活跃，文章质量较高且持续。
- **建议优先级：** P2

#### ★ 技术视野聚合（Hacker News Digest）
- **URL：** https://hnrss.org/frontpage
- **RSS：** `https://hnrss.org/frontpage`（✅ 可用）
- **类型：** 聚合榜单 / 英文
- **更新频率：** 实时
- **抓取方式：** RSS（hnrss.org 提供结构化 RSS）
- **可靠度：** **A**
- **价值：** 替代直接爬 HN，用 hnrss.org 提供稳定结构化输出，比 HTML 解析可靠。
- **建议优先级：** P1

---

### 2.4 中文开发者生态

#### 掘金（Juejin）
- **URL：** https://juejin.cn
- **RSS：** `https://juejin.cn/rss`（待实测，疑似非标准）
- **类型：** 技术博客 / 中文
- **更新频率：** 实时
- **抓取方式：** HTML 爬虫（推荐）/ 非标准 RSS
- **可靠度：** **B+**
- **价值：** 前端/Android/AI 内容丰富，是国内最有质量的技术内容平台之一。
- **建议优先级：** 🔥 P1（前端团队必选）
- **注意：** RSS 可能需代理访问，建议用爬虫替代。

#### 开源中国（OSChina）
- **URL：** https://www.oschina.net
- **RSS：** `https://www.oschina.net/feed`（✅ 已验证可用）
- **类型：** 综合技术 / 中文
- **更新频率：** 实时
- **抓取方式：** RSS（稳定）
- **可靠度：** **A**
- **价值：** 开源项目报道在国内最全面，覆盖 GitHub 热门项目的中文解读，是 HN+GitHub 的中文镜像。
- **建议优先级：** 🔥 P1

#### SegmentFault
- **URL：** https://segmentfault.com
- **RSS：** ❌ 付费墙内，**无公开 RSS**
- **类型：** 技术问答 / 中文
- **抓取方式：** 无法 RSS，只能手动或 browser
- **可靠度：** N/A
- **价值：** 技术问答质量高，但无 RSS 直接限制自动化采集。
- **建议优先级：** P3（考虑 browser 方案或放弃）

#### ★ CSDN 博客（技术资讯）
- **URL：** https://blog.csdn.net
- **RSS：** 有部分分类 RSS（如 `https://blog.csdn.net/rss.html`）
- **类型：** 技术博客 / 中文
- **更新频率：** 实时
- **抓取方式：** HTML 爬虫
- **可靠度：** **B-**（广告偏多，内容筛选成本高）
- **价值：** 流量最大，但内容质量参差不齐。可作舆情/热门话题参考，不建议作为核心信源。
- **建议优先级：** P3（降权使用）

#### 博客园（Cnblogs）
- **URL：** https://www.cnblogs.com
- **RSS：** `https://www.cnblogs.com/rss`（✅ 有）
- **类型：** 技术博客 / 中文
- **更新频率：** 实时
- **抓取方式：** RSS（稳定）
- **可靠度：** **B+**
- **价值：** 老牌技术博客平台，后端/架构内容丰富，文章质量高于 CSDN 平均。
- **建议优先级：** P2

---

### 2.5 工具类数据源

#### GitHub Trending Daily（结构化版本）
- **URL：** https://gitmostwanted.com/trending/daily/（待验证）
- **类型：** 趋势榜单 / 英文
- **替代：** 直接爬 GitHub Trending HTML
- **可靠度：** **B**
- **价值：** 提供更结构化的 trending 数据，减少解析成本。
- **建议优先级：** P2

#### 日、韩技术社区（可选）
- **Zenn（日本）：** https://zenn.dev/feed （✅ 有 RSS）
- **Note.com（韩国）：** https://note.com/（部分有 RSS）
- **价值：** 亚太技术趋势补充，非必需。
- **建议优先级：** P3（有国际化需求时升级）

---

## 三、信源综合评级表

| # | 信源 | 类型 | 语言 | 更新频率 | RSS/API | 可靠度 | 优先级 |
|---|------|------|------|----------|---------|--------|--------|
| 1 | GitHub Trending | 新项目 | 英文 | 日更+ | HTML爬虫 | A | **P0** |
| 2 | 开源中国 OSChina | 综合技术 | 中文 | 实时 | RSS ✅ | A | **P0** |
| 3 | 掘金 Juejin | 技术博客 | 中文 | 实时 | HTML爬虫 | B+ | **P1** |
| 4 | lobste.rs | 技术讨论 | 英文 | 实时 | RSS ✅ | A | **P1** |
| 5 | HN Front Page（hnrss 代理） | 技术讨论 | 英文 | 实时 | RSS ✅ | A | **P1** |
| 6 | ProductHunt | 新产品 | 英文 | 日更 | RSS ✅ | A | **P1** |
| 7 | GitHub Releases（关键框架） | 版本发布 | 多语言 | 按需 | Atom ✅ | A | **P1** |
| 8 | 博客园 Cnblogs | 技术博客 | 中文 | 实时 | RSS ✅ | B+ | P2 |
| 9 | Dev.to | 技术博客 | 英文 | 实时 | RSS ✅ | A | P2 |
| 10 | Lobster Changelog | 技能更新 | 英文 | 按版本 | HTML爬虫 | B+ | P2 |
| 11 | NPM Registry（openclaw） | 包更新 | 英文 | 按需 | API ✅ | A | P2 |
| 12 | CSDN | 技术博客 | 中文 | 实时 | HTML爬虫 | B- | P3 |

---

## 四、最终推荐信源组合（精选 10 个）

### 核心层（P0 — 必选，4 个）

1. **GitHub Trending** — 新项目发现第一入口（Python/Go/Rust/JS 多榜）
2. **开源中国 OSChina** — 中文开源生态覆盖最全，RSS 稳定
3. **掘金 Juejin** — 中文技术博客质量最高，前端/AI 内容丰富
4. **lobste.rs** — 高质量小众技术讨论，深度优于 HN

### 重要层（P1 — 推荐，4 个）

5. **ProductHunt** — 海外新工具/SaaS 产品发布
6. **HN Front Page（via hnrss.org）** — 技术热点聚合，RSS 稳定
7. **GitHub Releases（监控关键框架）** — 依赖框架版本更新主动通知
8. **V2EX Tech + Share/创造**（保留现有）— 国内开发者社区晴雨表

### 增强层（P2 — 有条件接入，2 个）

9. **Dev.to** — 英文技术博客补充，覆盖前端/云原生/AI
10. **博客园 Cnblogs** — 中文老牌技术博客，可与掘金互补

---

## 五、执行建议

### 立即可上线（本次接入）
- ✅ GitHub Trending（HTML 爬虫）
- ✅ 开源中国 OSChina（RSS）
- ✅ lobste.rs（RSS）
- ✅ hnrss.org（RSS，替代 HN 直接爬）
- ✅ ProductHunt（RSS）

### 待技术方案确认后接入
- ⏳ 掘金（需解决 RSS/代理问题，建议 HTML 爬虫）
- ⏳ GitHub Releases（需确认监控哪些框架的 org list）
- ⏳ Lobster Changelog（需确认更新频率和爬虫可行性）

### 暂不接入
- ❌ SegmentFault（无公开 RSS）
- ❌ CSDN（内容质量差，维护成本高）

---

## 六、风险与注意事项

| 风险 | 说明 | 缓解方案 |
|------|------|----------|
| RSS 被墙 | ProductHunt feedburner/部分中文 RSS 需代理 | 统一走代理 or relay 中转服务 |
| ClawHub API 持续 404 | 当前状态，影响技能生态覆盖 | 切换到 SkillHub + NPM 监控 |
| 掘金 RSS 不稳定 | 疑似非标准 RSS | 改用 HTML 爬虫方案 |
| 信源重复 | OSChina 与 V2EX、掘金内容可能重叠 | 接入后做去重过滤 |
| 更新频率过高 | 多个实时 RSS 可能产生噪声 | 设置每日合并阈值或定时汇总 |

---

**报告完成时间：** 2026-05-07
**下一步：** 请技术侧确认 HTML 爬虫实现成本，以及代理/relay 配置可行性。
