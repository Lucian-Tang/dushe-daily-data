# 洞见 V0.4.0 QA 评审报告

**评审日期：** 2026-05-09
**评审人：** QA Gate
**版本：** V0.4.0
**文件列表：**
- `lib/praise.js`
- `pages/index/index.wxml`
- `pages/index/index.js`
- `pages/result/result.wxml`
- `pages/result/result.js`

---

## 一、功能完整性：引导页 → 主页 → 挑战 → 结果 全链路

### 链路总览

| 步骤 | 来源 | 目标 | 状态 |
|------|------|------|------|
| 引导页首次打开 | index onLoad | showOnboarding=true | ✅ |
| 跳过/完成引导 | startChallenge() | showOnboarding=false + setStorage | ✅ |
| 主页 → 今日挑战 | startDaily() | /challenge?mode=daily | ✅ |
| 主页 → 分类练习 | startCategory() | /challenge?mode=category | ✅ |
| 挑战 → 结果 | finishChallenge() | /result?score&correct&total | ✅ |
| 结果 → 再来一局 | challengeAgain() | /challenge?mode=daily | ⚠️ |
| 结果 → 返回首页 | goHome() | /index (switchTab) | ✅ |

### 1.1 引导页 → 主页

`index.js` `onLoad()` 检查 `dongjian_onboarded` 存储键，首次访问显示引导 swiper。`startChallenge()` 标记已完成并关闭引导，加载用户状态。

**行为正确** — 但语义有歧义：引导页第3页 CTA 文案写"开始挑战"，实际只关闭引导回到主页，并不立即进入挑战页。用户可能误以为点击后会直接开始答题。

### 1.2 主页 → 挑战

`startDaily()` 和 `startCategory()` 传参正确，challenge 页面正确解析 `mode` 和 `cat` 参数。

### 1.3 挑战 → 结果

`challenge.js` `finishChallenge()` 跳转时传参：`score`、`correct`、`total`、`rankName`、`rankIcon`。result 页面 `onLoad` 正确解析 `score/correct/total`，**但 `rankName` 和 `rankIcon` 参数被忽略**（result.js 用 `praise.getPraise(correctPercent)` 重新计算段位）。冗余参数不影响功能，但暴露了调用方与接收方之间的耦合。

### 1.4 结果 → 再来一局（⚠️ 逻辑缺失）

```js
// result.js
challengeAgain() {
  wx.redirectTo({ url: '/pages/challenge/challenge?mode=daily' });
}
```

结果页**丢失了原始 `mode` 参数**。如果用户从"AI鉴定师"分类入口进入挑战，完成后点"再来一局"会变成"今日挑战"（daily）而非分类练习。用户意图被覆盖。

---

## 二、代码质量：边界/空值/错误兜底

### 2.1 praise.js — ✅ 较好

```js
function getPraise(percent) {
  const p = Math.max(0, Math.min(100, percent)); // clamp ✅
  let tierIndex = 0;
  for (let i = 0; i < TIER_PERCENT.length; i++) {
    if (p <= TIER_PERCENT[i]) { tierIndex = i; break; } // ✅
  }
  ...
  const ratio = tierRange > 0 ? inTier / tierRange : 0.5; // 防止除零 ✅
```

边界覆盖：0% → `bronze.low`；100% → `king.high`；输入非法值自动 clamp。

### 2.2 index.js — 有问题

**问题 1（严重）：段位进度计算使用哨兵值，导致进度条 UI 异常**

```js
const tiers = [
  { min: 0 }, { min: 500 }, { min: 1500 }, { min: 3500 },
  { min: 7000 }, { min: 12000 }, { min: 99999 }  // ← 哨兵
];
const nextTier = tiers[currentTier + 1];
const nextScore = nextTier ? nextTier.min : score + 1000;
```

当用户段位达到最高档（`score ≥ 12000`）时，`nextScore = 99999`，进度条显示 `12000/99999`。这个数值对用户完全无意义，且 87999 的分差导致进度条几乎为 0。这是**设计泄漏**，不应该暴露给用户。

此外，这段 `tiers` 数组与 `store.js` 中 `getRank()` 的段位定义**各自独立维护**，存在日后不同步的风险。

**问题 2（中等）：`loadCategoryCounts` 无错误兜底**

```js
async loadCategoryCounts() {
  const questions = await dataLoader.fetchQuestions();
  const counts = { image: 0, text: 0, design: 0 };
  questions.forEach(q => { if (counts[q.category] !== undefined) counts[q.category]++; });
  const categories = this.data.categories.map(cat => ({ ...cat, count: counts[cat.id] || 0 }));
  this.setData({ categories });
}
```

网络完全失败时 `fetchQuestions` 会返回空数组（已在 loader 内部 catch），此时 UI 显示各分类 0 题。可接受，但不优雅。

### 2.3 result.js — 有问题

**问题 3（严重）：Canvas 分享图完全未实现**

```js
// result.js
shareResult() {
  this.setData({ showCanvas: true }); // 只设置了一个 flag，无任何绘制逻辑
}

// result.wxml
<canvas type="2d" id="shareCanvas" class="share-canvas" wx:if="{{showCanvas}}"></canvas>
```

`showCanvas` 为 true 时 Canvas 组件会渲染，但没有任何 JS 调用 `wx.createCanvasContext` 或执行绘制。点击"炫耀一下"按钮后，用户看到的只是一个空 Canvas。这是**功能性残留**，分享图能力完全缺失。

### 2.4 result.js — rank-tag 类名不匹配（⚠️ CSS bug）

```html
<!-- result.wxml -->
<text class="rank-tag {{praiseTag}}">...</text>
```

`praiseTag` 来自 `p.tag`，可取值为 `'夸'`、`'激将'`、`'鼓励'`、`'夸+激将'`。

WXSS 中定义的类：
```css
.rank-tag.夸 { background: rgba(0,212,170,0.12); color: #00D4AA; }
.rank-tag.激将 { background: rgba(232,93,117,0.12); color: #E85D75; }
.rank-tag.鼓励 { background: rgba(255,215,0,0.12); color: #FFD700; }
```

`'夸+激将'`（diamond.low 专属 tag）没有任何 CSS 规则匹配，背景色和文字色均不生效。标签降级为纯文本显示，视觉上一致性断裂。

**修复建议**：在 result.js 的 `setData` 前将 `'夸+激将'` normalize 为 `'激将'` 或 `'鼓励'`，或在 CSS 中增加 `.rank-tag.夸\+激将`（需转义）。

---

## 三、文案质量：冒犯风险 & 分享合规

### 3.1 彩虹屁冒犯风险评估

| 段位 | 档位 | 文案关键词 | 风险 |
|------|------|-----------|------|
| bronze | low/mid/high | "踩坑"、"没关系" | ✅ 无风险 |
| silver | low/mid/high | "雷达搜索信号没搜到" | ⚠️ 轻微 |
| gold | **low** | **"AI在笑你：就差一点，我就骗到你了"** | ⚠️⚠️ 具攻击性 |
| gold | mid/high | "超过50%参与者" | ✅ |
| platinum | all | — | ✅ |
| diamond | all | "AI碰到你算是踢到铁板了" | ✅ 游戏化可接受 |
| king | low | "AI在角落里瑟瑟发抖" | ⚠️ 略阴阳，但高段位可接受 |

**gold.low** 的文案将 AI 人格化为嘲笑者，结合"骗到你"的措辞，对在意成绩的用户可能产生不适或社交尴尬（想象在朋友圈被分享这条时的场景）。

### 3.2 分享文案合规

```js
// praise.js
function getShareText(percent) {
  return `我在洞见的段位是${tierNames[p.tierIndex]}「${p.name}」${p.emoji}\n${p.text}\n\n来测测你的AI审美段位？`;
}
```

- 无诱导分享奖励 ✅
- 无强制关注引导 ✅
- 无虚假承诺 ✅

**但存在的问题**：`p.text` 直接拼接在分享文本中。如果 `p.text` 本身是"激将"类文案（如 gold.low 的"AI在笑你"），接收方看到时没有游戏上下文，可能误解为嘲讽。**建议**：分享文本中 `p.text` 改为统一的简短 summary 或直接省略，只保留段位+emoji+邀请语。

---

## 四、性能：引导页存储 & 回调

### 4.1 引导页存储

```js
// index.js
const onboarded = wx.getStorageSync(ONBOARDING_KEY); // 同步读，单键 ✅
if (!onboarded) { this.setData({ showOnboarding: true }); }

// startChallenge()
wx.setStorageSync(ONBOARDING_KEY, true); // 同步写，单布尔值 ✅
this.setData({ showOnboarding: false });
```

存储操作是同步的，数据量极小（一个布尔值），在低端设备上也不会造成 UI 阻塞。✅

### 4.2 引导页 swiper 回调

```js
onSlideChange(e) {
  this.setData({ currentSlide: e.detail.current }); // 轻量 setData ✅
}
```

无防抖/节流，swiper 每帧切换触发，但 `setData` 数据量极小（一个数字），性能影响可忽略。✅

### 4.3 首页数据加载

`onShow` 在非引导状态下顺序执行 `loadUserState()`（同步）和 `loadCategoryCounts()`（异步 fire-and-forget）。`loadUserState` 的 `setData` 同步完成，UI 不会卡顿。✅

`loadCategoryCounts` 是 fire-and-forget，**不 await**，用户会先看到 count=0（来自 data init），异步返回后更新。这在网络较慢时用户体验稍差，但不会崩溃。

---

## 五、组件引用

### 5.1 页面注册

`app.json` 中所有页面均已注册，index 和 result 都在列表中。✅

### 5.2 组件注册

`index.json` 和 `result.json` 均为：

```json
{ "usingComponents": {} }
```

两页面均**不使用任何自定义组件**，全部使用微信原生组件（swiper、view、text、button、canvas）。✅

---

## 六、额外发现

### 6.1 挑战页与结果页参数不一致

`challenge.js` `finishChallenge()` 传递 `rankName` 和 `rankIcon`，但 `result.js` 完全不使用这两个参数（自己从 `correctPercent` 推算）。属死代码，但不影响运行。

### 6.2 引导页 CTA 语义歧义

引导第3页 swiper-item 内：
```html
<view class="ob-cta" bindtap="startChallenge">
  <text class="ob-cta-text">开始挑战</text>
</view>
```

函数名 `startChallenge` 与按钮文案"开始挑战"语义对齐，但实际行为是"完成引导→回到主页"，用户并未进入挑战流程。建议函数改名 `completeOnboarding` 或 `enterHome`，或按钮文案改为"进入洞见"。

---

## 七、问题汇总

| # | 严重度 | 文件 | 问题 |
|---|--------|------|------|
| 1 | 🔴 严重 | index.js | 进度条哨兵值 `min: 99999` 导致 UI 显示无意义数值（12000/99999） |
| 2 | 🔴 严重 | result.js | `shareResult()` 未实现 Canvas 绘制，分享图功能空壳 |
| 3 | 🔴 严重 | result.wxml / result.js | `'夸+激将'` tag 无对应 CSS 规则，样式丢失 |
| 4 | 🟡 中等 | result.js | "再来一局"丢失原始 mode（category → daily） |
| 5 | 🟡 中等 | praise.js | gold.low 文案"AI在笑你"具攻击性，社交分享场景可能引发不适 |
| 6 | 🟢 轻微 | index.js | `loadCategoryCounts` 无错误反馈，count 为0时用户无感知 |
| 7 | 🟢 轻微 | index.js | 引导页 `startChallenge` 命名与行为不对应 |
| 8 | 🟢 轻微 | praise.js | 分享文案直接暴露激将类彩虹屁，接收方无上下文 |

---

## 八、GATE 结论

**结论：条件通过（Conditional Pass）**

### 必须修复（阻塞合并）

- **[P0-1]** `index.js` `loadUserState()`：移除 `{min: 99999}` 哨兵值，或在 `nextScore === 99999` 时特殊处理（如 `nextRankScore: null`，UI 上隐藏进度条文字）
- **[P0-2]** `result.js` `shareResult()`：实现 Canvas 绘制逻辑（生成含分数/段位/emoji 的分享卡片图），或在确认功能暂不上线时将按钮文案改为"功能开发中"
- **[P0-3]** `result.js` / `result.wxml`：将 `praiseTag === '夸+激将'` 在 `setData` 前 normalize 为 `'激将'`，确保 CSS 类名匹配

### 建议修复（下一迭代）

- **[P1]** `result.js`：接收并透传 `mode` 参数，使"再来一局"能还原用户原始入口
- **[P1]** `praise.js` gold.low 文案润色，或分享时过滤激将类文案
- **[P2]** `index.js`：引导页 `startChallenge` → `completeOnboarding`，UI 文案改为"进入洞见"

---

*报告生成：2026-05-09 15:55 GMT+8*
