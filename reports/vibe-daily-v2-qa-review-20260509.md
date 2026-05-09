# 「今天毒什么」V2.0 可信度评分功能 — QA守门人评审报告

**评审日期**: 2026-05-09  
**评审范围**: 可信度评分引擎、卡片UI改造、数据注入链路、浮层组件  
**评审结论**: 🟡 **条件通过**（1个必须修 + 3个建议修后可通过）

---

## 一、功能完整性 ⭐⭐⭐☆☆ (3/5)

### ✅ 已实现
| 功能点 | 状态 | 说明 |
|--------|------|------|
| 四维评分引擎 (信源/完整度/时效/独立) | ✅ | `credibility.evaluate()` 含完整启发式规则 |
| 卡片星级+标签展示 | ✅ | WXML 内联 `[1,2,3,4,5]` 渲染，带 `cred-warn` 状态 |
| 浮层详细分解 | ✅ | `credibility-detail` 组件含因子条、备注、颜色编码 |
| 浮层AIGC标注 | ✅ | 底部文本"内容由AI生成" |
| 数据注入链路 | ✅ | `index.js:enrichData()` → `credibility.evaluate(item)` |
| 信源分级 (官媒/知名媒体/自媒体) | ✅ | `SOURCE_TIERS` + `KNOWN_DOMAINS` 覆盖约60+信源 |

### 🔴 关键缺陷

#### 🔴 B-1: 卡片模板缺少credibility空值防护
**位置**: `pages/index/index.wxml:40-43`
```xml
<text class="cred-star-mini {{index < item.credibility.stars ? 'active' : ''}}">
```
**问题**: 若 `item.credibility` 为 `undefined`（预加载数据在 enrichData 之前渲染、或缓存读取路径不一致），访问 `.stars` 会抛出 `TypeError`，导致整张卡片渲染崩溃。

**影响**: 阻断性 — 微信小程序会白屏。

**修复建议**:
```xml
<!-- 方案A: WXML三元保护 -->
wx:if="{{item.credibility}}"
<!-- 方案B: enrichData确保注入（推荐） -->
```

---

### ⚠️ 隐患

#### Y-1: `injectBatch` 批量注入+缓存完全未使用
**位置**: `utils/credibility.js:184-196`  
`injectCredibility()` 和 `injectBatch()` 是两个 exported API，但 `index.js:enrichData()` 直接调用 `credibility.evaluate(item)`，完全绕过了缓存层。`_batchCache` 是死代码。

**影响**: 功能无碍，但暴露设计不一致 — `enrichData` 应该用 `injectCredibility` 还是 `evaluate`？当前混用可能导致后续维护者困惑。

**建议**: 要么删除 `injectBatch`，要么统一调用 `injectCredibility`。

#### Y-2: 评分引擎的API扩展点是空壳
**位置**: `utils/credibility.js:68`
```js
function evaluate(item) {
  // 预留 API 扩展点（未来可替换为真实评分接口）
  return evaluate_heuristic(item);
}
```
这是合理的设计预留，但当前无任何真实 API 对接或降级策略。目前不算 bug，仅注记。

---

## 二、代码质量 ⭐⭐⭐⭐☆ (3.5/5)

### ✅ 优点
- 评分维度拆分清晰，每个维度独立函数 + 返回值带 `note` 说明
- `normalize()` 上游已有 `isLowQuality()` 过滤广告/低质内容
- 浮层组件与页面完全解耦，通过 `properties` + `triggerEvent` 通信
- `calcSourceScore` 有三级 fallback：信源名匹配 → 域名匹配 → 未知兜底
- `index.json` 正确注册了 `credibility-detail` 组件

### 🔴 代码问题

#### B-2: `calcTimeliness` 仅匹配中文时间格式
**位置**: `utils/credibility.js:135-147`
```js
const hourMatch = pubTime.match(/(\d+)\s*小时前/);
const dayMatch = pubTime.match(/(\d+)\s*天前/);
```
**问题**: 若数据源返回 ISO 时间戳、"2 hours ago"、绝对日期等非中文格式，一律落入 `{ value: 1, note: '时效不确定' }`。该分支覆盖了"完全无法判断时效"的情况却给了1分（满分为2），可能造成误评。

**建议**: 
- 尝试 `new Date(pubTime)` 解析绝对时间，计算距今小时数
- 无法解析时给 `{ value: 0, note: '无法判断时效' }`

#### Y-3: `showCredibility` 变量命名混淆
**位置**: `pages/index/index.js:101-113`
```js
const stars = item.credibility ? [
  item.credibility.stars,
  {1:'#E85D75',...}[item.credibility.stars] || '#888'
] : [3, '#888'];
this.setData({
  credDetail: {
    stars: stars[0],     // ← 这个 stars[0] 是数字
    ...
```
**问题**: 变量 `stars` 先代表一个两元素数组 `[number, color]`，然后 `stars[0]` 取数字。同名变量承担不同含义，容易误读。

**建议**: 重命名为 `starInfo` 或 `[stars, color]` 解构。

#### Y-4: 详情页无credibility数据
**检查结果**: `pages/detail/` 下没有任何 `credibility` 引用。用户从卡片点击进入详情页后，看不到可信度信息。这是功能不完整 — 评分只存在于列表页。

---

## 三、UI/UX ⭐⭐⭐☆☆ (3/5)

### ✅ 已做好
- 暗色主题一致（`#1A1A2E` 浮层背景，暗色卡片）
- 红色警告态 `cred-warn` 对低可信度内容有视觉区分
- `catchtap` 正确隔离了评分标签和卡片点击事件
- 浮层点击遮罩可关闭，符合微信小程序交互习惯
- 星级颜色编码：1-2星红 `#E85D75`，3星金 `#FFD700`，4星绿 `#8BC34A`，5星青 `#00D4AA`

### 🟡 UX问题

#### U-1: 卡片上的可信度标签无点击反馈
**位置**: `pages/index/index.wxml:40`
```xml
<text class="card-credibility {{item.credibility.warning ? 'cred-warn' : ''}}" catchtap="showCredibility">
```
**问题**: 没有 `:active` 或 `hover-class` 样式。用户无法从视觉上感知这是一个可点击的交互元素。

**建议**: 添加 `hover-class="cred-hover"` 并定义按压态样式（如背景加深、缩放）。

#### U-2: 热门度🔥与可信度★的视觉权重失衡
**位置**: `pages/index/index.wxml:42-43`
```
★可信度标签 (内联, 小字10px, 灰色)  |  🔥热力值 (大号, 醒目)
```
可信度是V2.0核心功能，但视觉上比热力值弱很多。用户注意力会被🔥热度吸引而忽略★评分。

**建议**: 调整字号比例，至少让可信度标签体量与热力值持平。

#### U-3: 浮层星际颜色与卡片不一致的风险
**卡片侧**: 星级颜色固定 `#FFD700`（金色），Labels 动态颜色  
**浮层侧**: 星级颜色固定 `#FFD700`，Label 用 `labelColor` 动态色  
两处一致，但浮层内的因子进度条全部是 `#FFD700` 金色，未按分数高低做颜色区分。考虑让进度条颜色与得分级别匹配（红/金/绿/青）。

---

## 四、性能 ⭐⭐⭐⭐⭐ (5/5)

### 评测结果：无性能问题

| 检查项 | 结果 |
|--------|------|
| 评分计算复杂度 | O(n×m)，n=条目数，m=tiers数组长度(~20)，每项 < 0.1ms |
| 是否异步阻塞渲染 | 否，`evaluate()` 全同步字符串操作，无I/O |
| 首屏评分计算量 | 典型首页 ~20条，总耗时 < 2ms |
| setData调用量 | 每项注入1次（在 `enrichData` 中批量完成），无额外 setData |
| 浮层渲染 | 按需渲染（`wx:if="{{visible}}"`），关闭时销毁DOM |
| 缓存 | 预加载机制在 `data-loader.js` 中已实现10分钟TTL，前端无重复请求 |

**结论**: 评分计算完全不增加可感知卡顿。

---

## 五、合规 ⭐⭐☆☆☆ (2/5)

### 🔴 合规缺口

#### C-1: AIGC标注不完整（高风险）
**当前状态**:
| 位置 | AIGC标注 | 合规? |
|------|----------|-------|
| 浮层底部 | ✅ "内容由AI生成" | ✅ |
| 卡片主视图 | ❌ 无任何AIGC标识 | 🔴 缺失 |
| 首页免责声明 | ❌ 仅"内容源自公开信源" | 🔴 不完整 |

**法规依据**: 《互联网信息服务深度合成管理规定》第17条 — 深度合成服务提供者应当对使用其服务生成或者编辑的信息内容，采取技术措施添加不影响用户使用的标识。

**问题**: 用户看到卡片时完全不知道这是AI生成/加工的内容。AIGC标识藏在需要二次点击才能看到的浮层中，不符合"显著标识"要求。

**修复建议**:
1. 在卡片底部或标题旁添加一行 `🤖 AI辅助生成` 小字标识
2. 在首页免责声明中增加 "内容由AI筛选与点评，仅供参考"
3. 建议在每张卡片的毒舌点评区 `😈 毒舌` 旁标注 `（AI生成）`

#### C-2: 免责声明无法律效力
**当前**: `"内容源自公开信源，仅供参考。如有版权问题请联系删除。"`  
**缺失**: 无联系渠道、无主体信息、无ICP备案号、无投诉路径

---

## 六、Gate结论

### 🟡 条件通过

**必须修复（1项）**:
- 🔴 **B-1**: 卡片模板添加 `credibility` 空值防护，防止undefined崩溃

**强烈建议修复（3项）**:
- 🔴 **C-1**: AIGC标注扩展到卡片主视图（法规风险）
- 🟡 **B-2**: `calcTimeliness` 支持非中文时间格式
- 🟡 **Y-1**: 统一数据注入路径（用 `injectCredibility` 替代裸调 `evaluate`）

**可后续迭代**:
- U-1（点击反馈）、U-2（视觉权重）、Y-3（变量命名）、Y-4（详情页credibility）、C-2（免责声明完善）

---

## 附录：文件变更清单

| 文件 | 行数 | 评审结果 |
|------|------|----------|
| `utils/credibility.js` | 201行 | 引擎逻辑正确，2个待修项 |
| `pages/index/index.wxml` | ~100行 | 模板缺少空值防护 🔴 |
| `pages/index/index.js` | ~155行 | 注入链路正确，命名混淆 ⚠️ |
| `pages/index/index.json` | 5行 | 组件注册正确 ✅ |
| `pages/index/index.wxss` | ~140行 | 样式一致，缺少hover态 ⚠️ |
| `components/credibility-detail/*` | ~80行 | 组件结构清晰 ✅ |

---

*评审人: QA Gate Subagent (Lucia)*  
*审核模型: deepseek-v4-pro*
