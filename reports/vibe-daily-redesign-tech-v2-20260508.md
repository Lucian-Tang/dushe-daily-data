# 小程序重构 — 技术评估 v2

> 作者：Lucia（Stephen subagent 超时后代笔）
> 日期：2026-05-08
> 对应产品方案：reports/vibe-daily-redesign-v2-20260508.md

---

## 缺陷根因分析

### 缺陷 1：情绪雷达图没用

**根因：** Canvas 2D 绘制（index.js drawRadar），数据写死在 data-loader.js 的 EMOTION_DATA：
```js
anger: 65, entertainment: 82, discussion: 71, anxiety: 58, positive: 74
```
这些数字是硬编码的，跟实际内容无关。不管今天是 AI 炸了还是创投崩了，雷达图永远长一样。

**技术方案：** 删掉 Canvas 2D 代码块（~80 行），替换为 `scroll-view horizontal` 标签流。
- 前端：删除 canvas 节点 + 添加 flex-wrap 布局
- 数据：标签来源 → 从 raw JSON 中提取高频关键词（top 10 by frequency）
- 工作量：0.5h

---

### 缺陷 2：长列表没跳转

**根因：** 列表渲染用的是 `wx:for` 直接展开全部数据（index.wxml），没有 `scroll-view` 的 `scroll-into-view` 属性，也没有 FAB 按钮。

**技术方案：**
| 组件 | 实现方式 | 工时 |
|------|---------|------|
| 回到顶部 FAB | `wx:if scrollTop>500`, 点击 `scrollTo(0)` | 0.5h |
| 分类锚点 Tab | Sticky 位置，点击 `scroll-into-view="anchor_ai"` | 1h |
| 性能优化 | 虚拟列表暂不需要（当前 <200 条，recycle-view 反而有 bug） | - |

---

### 缺陷 3：只有标题没正文

**根因：** data-loader.js 的 `normalize()` 函数：
```js
summary: raw.content.replace(/<[^>]+>/g, '').substring(0, 120) + '...'
```
sumary 存在但页面上没用。index.wxml 只渲染了 `item.title`，没有渲染 `item.summary`。

**技术方案：**
- WXML：卡片式布局，每条渲染 `title + summary + source + hotScore`
- WXSS：卡片样式（圆角、阴影、边距）
- 保留点击事件，可跳详情（等缺陷 5 修好）
- 工时：2h（WXML + WXSS 重构）

---

### 缺陷 4：混了广告和评论

**根因：** raw JSON 数据（raw_articles_20260508.json）有 817 条行业文章，很多来自 RSS 抓取，包含 promotion、sponsored、广告、评论等内容。

**技术方案：三层过滤**

**第 1 层：采集时过滤（cron 脚本）**
- 关键词黑名单：`['sponsored', 'advertisement', 'promoted', 'PR Newswire', 'Business Wire', 'click here', 'buy now']`
- 标题匹配黑名单，匹配的直接丢弃

**第 2 层：data-loader 端过滤**
```js
const AD_KEYWORDS = ['广告', '推广', 'sponsored', 'ad', 'promoted'];
const MIN_CONTENT_LENGTH = 50;
function isLowQuality(item) {
  if (item.content && item.content.length < MIN_CONTENT_LENGTH) return true;
  if (AD_KEYWORDS.some(k => item.title.includes(k) || item.content.includes(k))) return true;
  return false;
}
```

**第 3 层：GitHub 数据后处理**
- 等 cron 下次推送时，在 push 脚本里加过滤
- 过渡方案：在 data-loader 的 normalize 中返回 null → `.filter(Boolean)` 自动丢弃

工时：1.5h（改 data-loader + 改 cron 数据脚本）

---

### 缺陷 5：详情页无内容

**根因：** detail 页面尝试从 data-loader 查 item，但 normalize 函数：
```js
id: genId(type, Math.random().toString(36).substr(2, 6)),
```
id 是随机生成的，detail 页面无法用 id 查回原始 item。

**技术方案（选最简单的）：**
删掉详情页跳转，改为卡片内展开（accordion）。
- WXML：`wx:if="{{item.expanded}}"` 控制展开
- tap 事件切换 `expanded` 状态
- 展开时显示完整 content + 来源链接
- 删除 `pages/detail/detail.*` 引用

工时：1h

---

### 缺陷 6：毒舌太尬

**根因：** data-loader.js 的 LUCHA_COMMENTS 是硬编码的 5 句：
```js
'大厂又在内卷了，卷到最后发现用户在刷另一个App。'
'PPT融资时代过去了，现在流行的是——PPT裁员。'
...
```

**技术方案：**
- 不再用前端硬编码，改为 cron 生成毒舌点评时写入 raw JSON 的 `quote` 字段
- cron prompt 优化：给具体的人设指令
- 前端 data-loader 已支持 `raw.quote`（normalize 函数：`quote: raw.quote || getRandomLuciaComment(type)`）

**新毒舌 prompt 模板：**
```
你是 Lucia，一个嘴贱但懂行的AI产品评论员。给下面的新闻写一条毒舌点评：
- 长度：15-25字
- 语气：冷幽默，带点讽刺但不刻薄
- 风格：说人话，不拽术语
- 例子：不是"该产品通过创新技术实现了用户体验优化"
       而是"又一个花3000万做出来的App，日活比我家楼下便利店还少"
```

工时：0.5h（改 cron prompt）

---

## 总工时 + 优先级

| 优先级 | 缺陷 | 方案 | 工时 |
|--------|------|------|------|
| 🔴 P0 | #4 脏数据 | 三层过滤 | 1.5h |
| 🔴 P0 | #3 内容展示 | 卡片式 WXML/WXSS | 2h |
| 🔴 P0 | #2 长列表 | FAB + 锚点 | 1.5h |
| 🟡 P1 | #5 详情无内容 | 卡片内展开 | 1h |
| 🟡 P1 | #1 雷达图 | 删 → 标签流 | 0.5h |
| 🟡 P1 | #6 毒舌 | cron prompt 优化 | 0.5h |
| **合计** | | | **7h** |

---

## 实施建议

**今晚立即可做（0.5h）：**
- 改 cron prompt 修毒舌
- 改 data-loader 加过滤黑名单

**明天（完整重构）：**
- 全部 7h 工作量，Stephen 一个下午跑完
- 用 `miniprogram-ci` 上传 v20260509

---

*完整产品方案：reports/vibe-daily-redesign-v2-20260508.md*
