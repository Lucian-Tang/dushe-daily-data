# 毒舌日报小程序 — 6 需求技术可行性评估报告

> 评估人：Stephen（工程师视角）
> 日期：2026-05-09
> 版本：v1.0
> 代码基准：v1.4.4（2026-05-08）

---

## 0. 现有架构摘要

### 0.1 页面结构

| 页面 | 文件路径 | 功能 |
|------|----------|------|
| 首页 | `pages/index/` | 列表 + tab 切换 + 模态详情 + 投票 |
| 详情页 | `pages/detail/` | 独立文章页（navigateTo 跳转） |
| 分享页 | `pages/share/` | Canvas 2D 生成海报并保存 |

### 0.2 现有组件

| 组件 | 状态 | 说明 |
|------|------|------|
| `news-card/` | **存在但未使用** | index 页面完全内联卡片 HTML，未引用此组件 |
| — | — | 组件内含 title/summary/quote/source/hotScore 显示 |

### 0.3 数据层

- **GitHub Pages 基础 URL**：`https://lucian-tang.github.io/dushe-daily-data/`
- **索引文件**：`index.json` → 各分类 JSON（按日期命名）
- **加载策略**：`data-loader.js` 模块加载时预加载所有频道，10 分钟缓存
- **字段规范化**：`normalize()` 函数统一转换为 `{id, type, title, content, summary, quote, hotScore, pubTime, source, url}`

### 0.4 现有交互能力

- 投票（like/diss）：本地 `wx.setStorageSync` 持久化 ✅
- 下拉刷新：`enablePullDownRefresh: true` ✅
- 回到顶部 FAB：`wx.pageScrollTo` ✅
- 分享海报：Canvas 2D 绘制 + `wx.canvasToTempFilePath` + `wx.saveImageToPhotosAlbum` ✅
- AI 毒舌点评兜底库：`LUCHA_COMMENTS` 按频道随机选取 ✅

---

## 1. 需求一：数据格式统一

### 1.1 现状：各频道字段差异分析

通过抓取 GitHub Pages 各频道 JSON 实测，字段差异如下：

| 字段 | industry | dev | ai | startup | design | hf-daily |
|------|----------|-----|----|---------|--------|-----------|
| `title` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `content` | ✅ 英文原文 | ✅ 英文原文 | ✅ 中文摘要 | ✅ 中文摘要 | ✅ 中文摘要 | ✅ 中文摘要 |
| `quote` | ❌ **缺失** | ❌ **缺失** | ✅ | ✅ | ✅ | ✅ |
| `url` | ✅ | ✅ | ❌ **空字符串** | ✅ | ❌ **缺失** | ✅ |
| `source` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `published` | ✅ ISO 8601 | ✅ RFC 5322 | ❌ **缺失** | ✅ | ✅ | ✅ `published` |
| `summary` | ❌ 由 content 截断生成 | 同左 | 同左 | 同左 | 同左 | 同左 |
| `pubTime` | ❌ 由 `formatTime()` 生成 | 同左 | 同左 | 同左 | 同左 | 同左 |

**根本原因**：
- `industry` 和 `dev` 的原始数据来自爬虫/翻译管道，**没有 quote 字段**
- `ai/startup/design` 的数据来自不同采集脚本，带 quote 和 content
- `design` 频道文件名用日期格式（`2026-05-08.json`）而非 `design_YYYYMMDD.json`，且 **url 字段完全缺失**
- `ai` 频道 `url` 字段为空字符串（AI 论文类内容通常以 `source` 作为来源标识）
- `pubTime` 是运行时由 `formatTime()` 计算的展示值，非原始数据字段

### 1.2 统一目标格式

```json
{
  "id": "string",
  "type": "industry|dev|ai|startup|design|hf-daily",
  "title": "string（必填）",
  "summary": "string（必填，最多 200 字）",
  "quote": "string（必填，毒舌点评）",
  "url": "string（必填，原文链接，不可为空）",
  "pubTime": "string（必填，展示用，如 '2小时前'）",
  "source": "string（必填，来源媒体）",
  "content": "string（可选，正文全文，详情页用）",
  "hotScore": "number（可选）",
  "raw": "object（可选，保留原始数据）"
}
```

### 1.3 技术方案

**步骤 1：数据采集端修复（数据源侧）**
- `industry` / `dev` 的采集脚本（不在小程序仓库内，需同步修改采集脚本仓库）需新增 `quote` 字段
- `design` 采集脚本需补充 `url` 字段（从原文页面提取）
- `ai` 频道：若 `url` 为空则回退到 `source` 字段的 URL

**步骤 2：`data-loader.js` 的 `normalize()` 函数加强**

```javascript
function normalize(raw, type) {
  // url 处理：禁止空字符串
  let url = raw.url || '';
  if (!url || url === '') {
    // ai 类：尝试从 source 推导；其他：报错并过滤
    url = deriveFallbackUrl(raw, type);
  }

  // quote 处理：禁止空，兜底库兜底
  let quote = raw.quote || '';
  if (!quote) {
    quote = getRandomLuciaComment(type); // 复用现有兜底库
  }

  // summary 处理：content 截断，但保留原始 content 全文
  const summary = (raw.content || raw.title || '')
    .replace(/<[^>]+>/g, '').substring(0, 200);

  return {
    ...,
    url,
    quote,
    summary,
    content: raw.content || raw.title || '',  // 保留全文（详情页用）
  };
}
```

**步骤 3：统一 content 字段（正文内容）**

目前 `normalize()` 中 `content` 字段有值，但被 `summary`（截断版）替代展示，正文全文丢失。修复：始终保留原始 `content` 作为 `content`，同时生成截断 `summary` 供列表展示。

### 1.4 风险

| 风险 | 等级 | 应对 |
|------|------|------|
| industry/dev 采集端修改需要同时维护两个仓库 | 高 | 与采集脚本仓库协同 PR，统一发版 |
| design 的 url 来源有时不可得（Product Hunt 链接需解析） | 中 | 允许 `source` 字段补充作为链接备选，或标记"来源平台查看" |
| 统一后旧数据缓存（10 分钟 TTL）导致短暂不一致 | 低 | 调用 `refresh()` 强制刷新 |

### 1.5 改动范围

| 文件 | 改动量 |
|------|--------|
| 采集脚本（外部仓库） | 需确认，估算中等 |
| `utils/data-loader.js`（`normalize()`、`fetchDataByType()`） | 中等，约 30 行 |
| `utils/api.js`（无需改动） | 无 |

---

## 2. 需求二：卡片 UI

### 2.1 现状

index 页面已实现**内联卡片**，包含：
- `card-header`（来源 + 热度）
- `card-title`
- `card-summary`
- `card-viewpoint`（Lucia 观点，用 🤖 标记）
- `card-roast`（毒舌，用 😈 标记）
- 投票区（👍👎）
- `lucia-divider`（每 5 条插入毒舌分隔）

独立组件 `components/news-card/` 存在且结构良好，但 **index 页面完全未引用它**，两套卡片实现并存。

### 2.2 技术方案

**选项 A（推荐）：复用现有 news-card 组件，扩展字段**

`components/news-card/` 已包含 title/summary/quote（通过 `item.quote`），无需新建组件。只需：

1. `index/index.wxml`：将内联卡片 HTML 替换为 `<news-card>` 组件调用
2. `components/news-card/news-card.js`：新增 `properties` 验证，支持新增字段（见统一格式）
3. 统一卡片的 viewpoint/roast 展示逻辑（与 index 当前逻辑对齐）

优点：复用已有组件，减少维护成本；UI 一致性由组件保证
缺点：需仔细对齐样式，确保与现有 index 卡片视觉一致

**选项 B：重构 index 页面内联卡片**

将 index 卡片封装为独立 `components/article-card/` 组件（传递 props：title/summary/quote/viewpoint/roast/likes/disses/userVote），完整重构。

优点：设计自由度更高，可按新设计稿完全重绘
缺点：工作量大，需同步修改 index 的 `enrichData()` 和 `voteAction()`

### 2.3 卡片 UI 增强建议（可同步做）

| 增强 | 实现方式 | 预估增量 |
|------|----------|---------|
| 卡片入场动画 | CSS `@keyframes fadeInUp` + `animation-delay` 交错 | +3KB CSS |
| 悬浮发光边框 | `:hover` → `box-shadow: 0 0 20px rgba(124,58,237,0.5)` | +1KB |
| 热度条动画 | CSS `transition: width 0.6s ease` | +1KB |
| 卡片内小图标/标签 | `category` 字段映射图标 | +1KB |

### 2.4 风险

| 风险 | 等级 | 应对 |
|------|------|------|
| 替换卡片后样式不一致 | 低 | 先在不提交模式测试，对比截图 |
| news-card 组件内 typeName 映射不完整 | 中 | 扩展 `typeMap` 支持 `startup`、`design`、`hf-daily` |

### 2.5 改动范围

| 文件 | 改动量 |
|------|--------|
| `pages/index/index.wxml`（内联卡片 → 组件调用） | 小 |
| `pages/index/index.js`（`enrichData` 字段对齐） | 小 |
| `components/news-card/news-card.js`（扩展 properties） | 小 |
| `components/news-card/news-card.wxss`（动画增强） | 小 |
| `components/news-card/news-card.wxml`（按需调整） | 小 |

---

## 3. 需求三：详情页（跳转式 + 正文内容）

### 3.1 现状

详情页**已存在**（`pages/detail/`），但：
- 首页点击卡片是**模态弹窗**（`modal-mask`），不是页面跳转
- `detail` 页面当前从 `api.fetchDetail(id)` 获取数据，依赖 `data-loader` 的内存缓存
- `detail` 页的 `article.quote` 是**模拟数据**（`bubble-sub` 标注"以上为样例，正式版将接入 AI 实时生成"），非真实毒舌点评
- `content` 字段从 GitHub Pages 读取后被截断为 `summary`，**正文全文不可得**

### 3.2 技术方案

**问题 1：将首页模态改为页面跳转**

```javascript
// index/index.js openModal 改为 navigateTo
openModal(e) {
  const id = e.currentTarget.dataset.id; // 从 dataset.id 获取（需在 wxml 中补充）
  wx.navigateTo({
    url: `/pages/detail/detail?id=${id}`
  });
}
```

当前 openModal 传递的是 `data-index`（列表下标），需改为 `data-id`（文章唯一标识）。`enrichData()` 返回的数据已包含 `item.id`，可直接使用。

**问题 2：详情页显示正文内容**

当前 `normalize()` 中 `content` 字段保留原始全文（如果 `raw.content` 有值）。但展示层面：
- industry/dev 的 `content` 是英文原文（爬虫直接抓取，无翻译）
- `detail/detail.wxml` 的 `.article-summary` 只展示 `summary`（截断版）

方案：增加 `article.content` 展示区域（或区分"摘要"和"正文"两个展示块）：

```xml
<!-- detail/detail.wxml 新增 -->
<view class="article-content" wx:if="{{article.content && article.content !== article.summary}}">
  <text class="content-label">📄 详细内容</text>
  <text class="content-text">{{article.content}}</text>
</view>
```

**问题 3：detail 页数据依赖预加载缓存**

`api.fetchDetail(id)` 依赖 `_preloaded` 内存数据。如果用户直接通过分享链接打开详情页（冷启动），`_preloaded` 可能为空。需确保详情页在 `_preloaded` 未就绪时发起网络请求：

```javascript
// detail/detail.js
async loadArticle(id) {
  // 先尝试从缓存读
  const article = api.fetchDetail(id); // 同步从 loader 内存取
  if (article) {
    this.setData({ article });
  }
  // 若缓存为空，发起远程刷新
  if (!article || !article.content) {
    await api.refreshData();
    const refreshed = api.fetchDetail(id);
    this.setData({ article: refreshed });
  }
}
```

### 3.3 风险

| 风险 | 等级 | 应对 |
|------|------|------|
| industry/dev 的 `content` 是英文原文 | 高 | 采集端增加翻译步骤，或在 UI 标注"英文原文，点击查看" |
| 直接分享详情页链接（冷启动）数据为空 | 中 | 详情页增加数据加载状态（骨架屏），并做容错 |
| 首页"查看原文"是复制链接而非跳转 | 低 | detail 页底部增加"浏览器打开"按钮 |

### 3.4 改动范围

| 文件 | 改动量 |
|------|--------|
| `pages/index/index.wxml`（卡片点击传 id 而非 index） | 小 |
| `pages/index/index.js`（openModal 改为 navigateTo） | 小 |
| `pages/detail/detail.wxml`（增加 content 展示区） | 小 |
| `pages/detail/detail.js`（冷启动容错逻辑） | 小 |
| `utils/data-loader.js`（normalize 保留完整 content） | 中 |

---

## 4. 需求四：Scroll Bug（详情页滑动影响主页列表）

### 4.1 问题分析

**根本原因：scroll-view 在 WebView 中的共享上下文问题**

微信小程序的 `scroll-view` 组件在 WebView 层共享渲染上下文。当使用 `wx.navigateTo` 从首页跳转到详情页时：

```
[ WebView 上下文 ]
  └─ index 页 scroll-view（保持原 scrollTop 位置，惯性继续）
  └─ detail 页 scroll-view
```

首页的 `scroll-view` 并未被销毁或隐藏，其滚动位置和惯性状态被保留。当用户在详情页上下滑动时，**首页 scroll-view 的惯性滚动仍在继续**，表现为"主页列表跟着滑动"。

### 4.2 关键代码位置

index 页面：
```xml
<scroll-view scroll-y class="card-list" id="cardScroll" scroll-with-animation bindscroll="onScroll">
```

当前 `scrollToTop()` 使用了 `wx.pageScrollTo({ scrollTop: 0 })`，但这是**页面级滚动 API**，与 `scroll-view` 内部滚动**是两套机制**。`wx.pageScrollTo` 无法重置 `scroll-view` 的内部 scrollTop。

### 4.3 技术方案

**方案 A（推荐）：在 onHide 生命周期重置 scroll-view 滚动位置**

```javascript
// pages/index/index.js
onHide() {
  // 离开首页时重置 scroll-view 到顶部，防止跳转详情后底层列表"透传"滚动
  this.resetScroll && this.resetScroll();
},

onUnload() {
  this.setData({ listData: [] }); // 释放大数据
},
```

但 `scroll-view` 没有直接的"重置 scrollTop"API，需通过 WXS 或 Canvas node API。

**方案 B（推荐）：detail 页面使用 `page-meta` 控制背景，并 navgivate 前重置 index scroll**

在 `navigateTo` 详情页前，强制将首页 scroll-view 滚动到 0：

```javascript
// index/index.js
openModal(e) {
  const id = e.currentTarget.dataset.id;
  // 关键：在跳转前重置 scroll-view
  const query = wx.createSelectorQuery().in(this);
  query.select('#cardScroll').boundingClientRect();
  query.selectViewport().scrollOffset();
  query.exec(() => {
    // 通过 WXS 或手动计算设置 scroll-top
    this.setData({ scrollTop: 0 }); // 需配合 wxml scroll-top 属性
    wx.navigateTo({ url: `/pages/detail/detail?id=${id}` });
  });
}
```

需在 index 的 `scroll-view` 上增加 `scroll-top="{{scrollTop}}"` 属性。

**方案 C（彻底方案）：detail 改为 modal 形式，或使用 `scroll-view` 的 `scroll-into-view`**

如果详情页改回 modal 全屏覆盖（类似当前首页的 `modal-mask`），则不存在页面跳转问题。详情页模态的 `scroll-view` 与首页列表是独立的组件树，不共享上下文。

**推荐方案**：方案 B + 方案 C 结合——将首页卡片点击改为 `wx.navigateTo` 跳 detail，detail 使用自身 `scroll-view`（已实现），同时在 `onHide` 时将首页 `scroll-view` 重置到顶部。

### 4.4 风险

| 风险 | 等级 | 应对 |
|------|------|------|
| iOS/Android 微信版本差异导致 scroll-view 行为不一致 | 中 | 在两种系统上分别测试 |
| `wx.pageScrollTo` 与 `scroll-view` 混用的边界情况 | 低 | 优先使用 WXS 版本的 scroll-into-view |

### 4.5 改动范围

| 文件 | 改动量 |
|------|--------|
| `pages/index/index.wxml`（scroll-view 增加 scroll-top 绑定） | 小 |
| `pages/index/index.js`（onHide/onUnload 重置滚动，openModal 跳转前重置） | 小 |
| `pages/detail/detail.js`（确保 onLoad 时自身 scroll-view 正常） | 小 |

---

## 5. 需求五：首页显示今日更新数目

### 5.1 现状

index 页面 header 区域有 Lucia IP 头像和状态文字，tabs 区域显示频道标签，但**无今日更新数目显示**。

当前 `data-loader.js` 的 `loadAll()` 返回所有历史数据（经过过滤后），没有"今日"的概念。

### 5.2 技术方案

**核心逻辑**：统计 `pubTime` 字段包含"刚刚"/"N分钟前"/"N小时前"（当天内）的条目数量，或直接比对 `published` 日期。

```javascript
// 在 enrichData 中增加今日统计
function getTodayCount(listData) {
  const today = new Date();
  const todayStr = today.toISOString().slice(0, 10); // '2026-05-09'
  return listData.filter(item => {
    const pubDate = item.raw?.published;
    if (!pubDate) return false;
    // pubDate 格式：'2026-05-08T09:48:14-04:00' 或 'Fri, 08 May 2026'
    return pubDate.includes(todayStr);
  }).length;
}
```

但注意：`pubTime` 是"刚刚"、"2小时前"这类展示字符串，无法直接用于日期比对。需要使用 `raw.published` 原始日期字段（normalize 后存在 `item.raw.published`）。

**UI 展示位置**：在 tabs 区域或 header 区域增加徽章：

```xml
<!-- index/index.wxml -->
<view class="today-count" wx:if="{{todayCount > 0}}">
  <text class="count-badge">今日更新 {{todayCount}} 条</text>
</view>
```

### 5.3 风险

| 风险 | 等级 | 应对 |
|------|------|------|
| 今日统计在首次加载时（预加载未完成）为空 | 低 | 异步加载完成后更新，或在刷新后重新计算 |
| 数据跨天时（UTC vs 北京时间）统计偏差 | 中 | 统一用北京时间比对（东八区） |

### 5.4 改动范围

| 文件 | 改动量 |
|------|--------|
| `pages/index/index.js`（fetchData/enrichData 中计算 todayCount） | 小 |
| `pages/index/index.wxml`（新增今日更新徽章 HTML） | 小 |
| `pages/index/index.wxss`（徽章样式） | 小 |

---

## 6. 需求六：互动增强（收藏 + 小红书风格分享卡片）

### 6.1 现状

- **投票**：已实现（`card_votes` 存储在 `wx.setStorageSync`）
- **分享海报**：已存在 `pages/share/`，Canvas 2D 绘制渐变风格海报，400 行代码，逻辑完整
- **收藏**：**未实现**

### 6.2 收藏功能

**数据结构设计（纯本地存储）**：

```javascript
// wx.setStorageSync('favorites', [...ids])
```

```javascript
// utils/favorites.js
function toggleFavorite(id) {
  const favs = wx.getStorageSync('favorites') || [];
  const idx = favs.indexOf(id);
  if (idx > -1) {
    favs.splice(idx, 1);
  } else {
    favs.unshift(id); // 最新收藏在前
  }
  wx.setStorageSync('favorites', favs);
  return favs;
}

function isFavorite(id) {
  return (wx.getStorageSync('favorites') || []).includes(id);
}

module.exports = { toggleFavorite, isFavorite };
```

**UI 方案**：
- 卡片右上角增加 ❤️ 收藏图标（已 vote 区域旁）
- 详情页底部增加"收藏"按钮
- 收藏后：弹出 toast "已收藏" / 取消后 "已取消收藏"
- 可选：新增"我的收藏"页面（`pages/favorites/`）

**微信限制**：小程序没有真正的"收藏到微信"API，只能本地收藏记录。

### 6.3 小红书风格分享卡片

**现有 share 页面分析**：

`pages/share/share.js` 已实现完整 Canvas 2D 海报：
- 尺寸：600×900（3:4.5 竖版，接近小红书 3:4 比例）
- 渐变暗黑紫底 + 装饰线 + Lucia 金句 + 新闻标题 + 底部小程序码占位
- `wx.canvasToTempFilePath` + `wx.saveImageToPhotosAlbum`

**小红书风格增强建议**：

| 维度 | 现有风格 | 小红书偏好 |
|------|----------|-----------|
| 背景 | 暗黑紫（#1A1035） | 更亮、更清新，或高饱和撞色 |
| 字体大小 | quote 36px 偏小 | quote 48-56px，大字报风格 |
| 比例 | 2:3（600:900） | 接近 3:4（小红书标准） |
| 小程序码 | 灰色占位文字 | 需要真实二维码（可用微信 Canvas 绘制） |
| 品牌标识 | "🔥 毒舌日报" | 强化 Lucia IP（Lucia 头像/emoji 更突出） |
| 底部文案 | "今天的毒舌，明天的谈资" | 可定制或留空给用户填 |

**技术实现**：

1. **多种海报模板**：定义 `TEMPLATES` 配置对象，支持 `dark`（现有）、`xiaohongshu`（新）、`minimal` 等
2. **Canvas 2D 重构**：将现有 drawPoster 函数拆分为模板函数 + 渲染函数，便于新增模板
3. **真实小程序码**：微信 `wxacode.get` 系列 API（需后端支持，需申请）

```javascript
// 模板配置示例
const TEMPLATES = {
  xiaohongshu: {
    bgGradient: ['#FFF5F5', '#FFE4E6'],  // 浅粉白
    accentColor: '#FF6B6B',               // 珊瑚红
    quoteFontSize: 52,
    layout: 'centered'                     // 大字居中
  }
};
```

**小程序码限制**：微信小程序的「小程序码」需要后端调用 `wxacode.getUnlimited` 或 `wxacode.get` 接口生成，前端 Canvas 无法直接绘制真实小程序码（除非服务器返回图片）。

**可选方案（无需后端）**：
- 使用 `web-preview` 链接分享（非海报，但可直接跳转）
- 在 Canvas 中留出小程序码占位区（灰色框 + 引导文字"用小程序打开查看"）

### 6.4 风险

| 风险 | 等级 | 应对 |
|------|------|------|
| 收藏数据仅本地，换机丢失 | 低 | 可接受（v1 阶段），后续迁移到云开发 |
| Canvas 海报在低端机性能问题 | 低 | 控制 Canvas 操作复杂度，避免逐像素绘制 |
| 小红书平台对外部图片有压缩，影响海报质量 | 中 | 导出时使用 `quality: 1.0` 最高质量 |
| 多模板导致 share.js 复杂度上升 | 中 | 模板抽取为独立配置文件 |

### 6.5 改动范围

| 文件 | 改动量 |
|------|--------|
| `utils/favorites.js`（新建收藏工具模块） | 小 |
| `pages/index/index.wxml`（卡片增加收藏图标） | 小 |
| `pages/index/index.js`（收藏逻辑） | 小 |
| `pages/detail/detail.wxml`（底部收藏按钮） | 小 |
| `pages/detail/detail.js`（收藏逻辑） | 小 |
| `pages/share/share.js`（模板化重构 + 小红书模板） | 中 |
| `pages/share/share.wxml`（模板选择器） | 小 |

---

## 7. 推荐实现顺序

### 7.1 顺序及理由

```
优先级排序：
1. 需求四（Scroll Bug）       → 用户体验直接影响所有页面，修复风险低
2. 需求一（数据格式统一）      → 基础设施，所有功能依赖正确数据
3. 需求三（详情页 + 正文）      → 数据就绪后直接受益
4. 需求五（今日更新数目）      → 纯 UI 小改动，可快速上线
5. 需求二（卡片 UI）          → 视觉优化，依赖需求一数据就绪
6. 需求六（收藏 + 小红书分享）  → 新功能，增量价值
```

**理由**：
- **Scroll Bug 排第一**：这是明确的 bug，修复代价极低（~10 行代码），不应带着 bug 做新功能
- **数据格式统一第二**：这是其他所有需求的地基。card UI、detail 页、今日计数都依赖统一的数据字段
- **详情页第三**：依赖数据统一后可立即接通正文内容
- **今日计数第四**：纯展示逻辑，与数据格式改动可同步进行
- **卡片 UI 第五**：确认数据格式后再渲染，避免返工
- **收藏 + 小红书第六**：新增功能，可从容开发

### 7.2 实施分组

**Group 0（Bug Fix，不用等）：**
- Scroll Bug 修复（需求四）

**Group 1（数据层，一次性搞定）：**
- 数据格式统一（需求一）

**Group 2（页面层，依赖 Group 1）：**
- 详情页正文内容（需求三）
- 今日更新数目（需求五）
- 卡片 UI 优化（需求二）

**Group 3（互动功能，单独迭代）：**
- 收藏功能
- 小红书风格分享卡

---

## 8. 数据流全景图（修复后）

```
GitHub Pages (lucian-tang.github.io/dushe-daily-data)
    │
    ▼
data-loader.js fetchIndex() → 获取 index.json
    │
    ▼
fetchDataByType(type) → 按 type 取对应 JSON 文件
    │
    ▼
normalize(raw, type) → 统一格式
  ├── title      ✅ 取自 raw.title
  ├── summary    ✅ 取自 raw.content 截断（保留原始 content）
  ├── quote      ✅ raw.quote || 兜底库
  ├── url        ✅ raw.url || 推导备选
  ├── pubTime    ✅ formatTime(raw.published)
  ├── source     ✅ raw.source
  ├── content    ✅ 保留完整正文（detail 页用）
  └── hotScore   ✅ calcHotScore(raw)
    │
    ▼
api.fetchDailyList(type) → 页面使用
    │
    ├─→ index 页 ─→ news-card 组件渲染
    │       ├─ todayCount 统计
    │       ├─ 投票（storage 持久化）
    │       ├─ 收藏（storage 持久化）
    │       └─ 跳转 detail 页（navigateTo）
    │
    ├─→ detail 页 ─→ 展示 title/summary/content/quote/url
    │       └─ 生成分享海报（navigateTo share）
    │
    └─→ share 页 ─→ Canvas 2D 渲染多模板海报
            ├─ dark 模板（现有）
            ├─ xiaohongshu 模板（新增）
            └─ saveImageToPhotosAlbum
```

---

## 9. 关键注意事项

1. **不破坏现有数据管道**：所有修改以不破坏现有 GitHub Pages 数据消费为前提
2. **向后兼容**：normalize 函数在 `quote/url` 缺失时使用兜底策略，不因此过滤掉任何内容
3. **包体积**：当前总包 < 600KB（不含基础库），所有需求完成后预估 < 800KB，远低于 2MB 限制
4. **微信审核**：分享功能使用 `onShareAppMessage`（微信原生），无额外审核风险；Canvas 生图无审核问题
5. **GitHub Pages 跨域**：小程序 `wx.request` 可直接请求 GitHub Pages（无 CORS 限制），无需配置

---

## 10. 改动清单汇总

| 需求 | 文件 | 预估改动量 | 风险 |
|------|------|-----------|------|
| 四（Scroll Bug） | `pages/index/index.{js,wxml}` | ~15 行 | 低 |
| 一（数据统一） | 采集脚本 + `utils/data-loader.js` | ~50 行 | 中 |
| 三（详情页） | `pages/detail/{js,wxml}`, `pages/index/index.{js,wxml}` | ~30 行 | 低 |
| 五（今日计数） | `pages/index/index.{js,wxml,wxss}` | ~20 行 | 低 |
| 二（卡片 UI） | `components/news-card/*`, `pages/index/index.{wxml,js}` | ~40 行 | 低 |
| 六（收藏） | `utils/favorites.js`（新），index/detail 页面 | ~40 行 | 低 |
| 六（小红书分享） | `pages/share/share.{js,wxml}` | ~80 行 | 中 |

**总代码改动量**：约 275 行（含新文件），分散在 8 个文件中，分 3 个迭代可完成。

---

*Boss，技术上 6 个需求全部可行，无根本性障碍。核心建议：先把 Scroll Bug 和数据格式修了，这两件事代价低、收益大，是后面所有改进的地基。*
