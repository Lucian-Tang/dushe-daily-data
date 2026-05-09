# 🔍 Vibe-Daily v2 代码 Review

**Reviewer:** Stephen（研发工程师）  
**Date:** 2026-05-09  
**Scope:** data-loader.js, pages/index/*, pages/detail/*, pages/share/*

---

## 1. data-loader.js

### 🐛 Bug

**B1. `isToday()` 时区问题**
```js
function isToday(dateStr) {
  if (!dateStr) return true;
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return true;
  const now = new Date();
  return d.getDate() === now.getDate() && ...
}
```
- 数据源的时间字符串带时区（如 `2026-05-08T09:48:14-04:00` 是 UTC-4），`new Date()` 会转为本地时间比较
- 对于跨时区数据（如美国时区的文章），凌晨抓取时可能被误判为"昨天"
- **Fix:** 统一使用 `toISOString().slice(0,10)` 字符串比较日期

**B2. `getRandomLuciaComment(type)` 兜底缺陷**
```js
const list = LUCHA_COMMENTS[type] || LUCHA_COMMENTS.social;
```
- `LUCHA_COMMENTS.social` 是空数组 `[]`
- 如果 type 不匹配且 social 为空，`list[Math.floor(Math.random() * 0)]` 返回 `undefined`
- **Fix:** 添加全局兜底数组

### ⚠️ 风险

**R1. `isForeignAI()` 同时过滤了中文内容**
```js
const foreignPattern = /...|马斯克|硅谷|旧金山|加州|美国|白宫|Congress|EU\b|欧洲|日本|韩国|Samsung|SoftBank/i;
```
- "马斯克"、"加州"等出现在中文语境中也全被过滤
- 导致 AI 频道可能漏掉重要中文报道中有海外背景的新闻
- **建议:** 只过滤纯外文来源的新闻，中文语境下的跨国内容保留

**R2. `calcHotScore()` 随机性太强**
```js
return Math.floor((str.length * 37 + Math.random() * 500));
```
- 每次调用产生不同热度值，同一篇文章在不同 tab 切换时分数波动
- **建议:** 基于内容 hash 或固定 seed

### 💡 优化

**O1.** `normalize()` 中 `fullContent` 和 `content` 字段职责不清 — 建议统一为一个 `content`（完整正文）+ `summary`（摘要）

**O2.** `formatTime()` 对无日期数据返回"未知" — 建议返回空字符串，交由 UI 层 hide

---

## 2. pages/index/*

### 🐛 Bug

**B3. `onScroll` 内存泄漏风险**
```js
onScroll(e) {
  const scrollTop = e.detail.scrollTop;
  if (scrollTop > 200 && !this.data.showFab) this.setData({ showFab: true });
  else if (scrollTop <= 200 && this.data.showFab) this.setData({ showFab: false });
}
```
- 每次滚动都调用 `setData`（当跨越 200 阈值时），高频滚动下性能开销大
- **Fix:** 加 throttle（如 200ms）

**B4. `toggleBookmark` 不更新 `todayCount`**
- 当前收藏切换后 `todayCount` 被设为 0（见 `goBookmarks()` 中 `todayCount: 0`）
- 从收藏页切回其他 tab 后数字丢失

### ⚠️ 风险

**R3. `wx.setStorageSync('detail_cache', item)` 只存单条**
- 快速点击两张卡片时，第二张覆盖第一张
- 详情页后退再点另一条时可能读到错误缓存
- **Fix:** 改为 Map 存储 `detail_cache_{id}`

**R4. `switchTab` 每次切换都重新拉取数据**
- 增加网络请求和渲染开销
- **建议:** 对已加载的 tab 数据做内存缓存

### 💡 优化

**O3.** `enrichData()` 中分割毒舌逻辑复杂（`showLuciaBreak`/`luciaBreakQuote`），建议抽离为独立 `utils/lucia-break.js`

**O4.** 卡片点击 `goDetail()` 缓存整条数据可能导致 `wx.storage` 超限（小程序限制 10MB）

---

## 3. pages/detail/*

### 🐛 Bug

**B5. 详情页数据回退为空时用户体验差**
```js
this.setData({
  article: article ? { ...article, bookmarked: !!bookmarks[id] } : null,
```
- `article` 为 null 时显示"文章飞走了"，但没有重试机制
- **Fix:** 添加"重新加载"按钮

### ⚠️ 风险

**R5. `openLink()` 只能复制链接，无法跳转**
- 小程序内嵌 web-view 需要配置业务域名
- **建议:** 至少在详情页注明需要浏览器打开的提示

---

## 4. pages/share/*

### ⚠️ 风险

**R6. Canvas 2D 绘制无超时保护**
```js
setTimeout(() => {
  wx.canvasToTempFilePath({...})
}, 150);
```
- 如果 canvas 初始化失败（低端机），150ms 后仍可能失败
- **Fix:** 添加绘制状态标记 + 失败重试

**R7. `savePoster()` 无权限预处理**
- iOS 首次调用 `wx.saveImageToPhotosAlbum` 需要授权
- 当前虽有 Modal 引导，但 `openSetting` 后不会自动重试
- **Fix:** 权限获取成功后自动调用 `savePoster()`

---

## 优先级排序

| 级别 | ID | 问题 | 影响 |
|------|-----|------|------|
| **P0** | B1 | isToday() 时区问题 | 今日计数不准确 |
| **P0** | B3 | onScroll 高频 setData | 低端机严重卡顿 |
| **P0** | R3 | detail_cache 覆盖 | 详情页数据错乱 |
| **P1** | B2 | getRandomLuciaComment 空数组 | 特殊场景 quote 缺失 |
| **P1** | R2 | calcHotScore 随机性 | 数据一致性差 |
| **P1** | R6 | Canvas 无超时保护 | 低端机海报生成失败 |
| **P2** | O1-O4 | 代码组织优化 | 可维护性提升 |
| **P2** | R1 | isForeignAI 过度过滤 | 少数新闻漏掉 |
