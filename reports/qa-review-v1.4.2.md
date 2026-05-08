# QA 校验报告：今天毒什么 V1.4.2

**校验人：** Lucia (QA Agent)
**日期：** 2026-05-08
**版本：** V1.4.2

---

## 校验结果：**修改后重审**

发现 **4 个问题**（含 1 个隐患）：

---

### 1. [CSS/隐患] `.tabs` 规则重复定义 —— 低优先级，建议修

**位置：** `index.wxss`

```wxss
/* 第一处 */
.tabs { display: flex; justify-content: space-around; padding: 10rpx 16rpx 16rpx; border-bottom: 1px solid rgba(124, 58, 237, 0.2); position: sticky; top: 0; z-index: 10; background: #0F0F1A; width: 100vw; overflow-x: hidden; flex-wrap: nowrap; }

/* 第二处（完全独立的另一条）*/
.tabs { width: 100%; overflow-x: auto; white-space: nowrap; }
```

**问题：** 同样的选择器写了两遍，第二条覆盖第一条。当前行为正确（`overflow-x: auto` 让频道栏可横向滚动，`white-space: nowrap` 让 Tab 不折行）。但后续维护风险极高——如果有人在第一条加新属性，很容易忘记第二条会覆盖它。

**建议：** 合并为一条规则：
```wxss
.tabs {
  display: flex;
  justify-content: space-around;
  width: 100%;
  overflow-x: auto;
  white-space: nowrap;
  padding: 10rpx 16rpx 16rpx;
  border-bottom: 1px solid rgba(124, 58, 237, 0.2);
  position: sticky;
  top: 0;
  z-index: 10;
  background: #0F0F1A;
}
```

---

### 2. [CSS/隐患] `.card-list` 规则缺失 `box-sizing: border-box`

**位置：** `index.wxss`

```wxss
.card-list {
  width: 100%;
  box-sizing: border-box;  /* ← 缺失 */
  padding: 12px 16px;
}
```

**问题：** 页面级有 `view { box-sizing: border-box; }`，理论上全局生效。但当 `.card-list` 同时设置 `width: 100%` + `padding` 时，`box-sizing` 的缺失在层级嵌套场景下可能产生微妙宽度计算问题（`scroll-view` > `scroll-wrapper` > `card-list` > `card` 多层嵌套，`100%` 基准以谁为准取决于 box-sizing 是否显式声明）。

**建议：** 显式声明 `box-sizing: border-box`：
```wxss
.card-list {
  width: 100%;
  box-sizing: border-box;
  padding: 12px 16px;
}
```

---

### 3. [JS/逻辑/竞态] `voteAction` 读-写非原子，有并发覆盖风险

**位置：** `index.js` 第 108-127 行

```js
voteAction(e) {
  // ...计算新的 likes/disses/userVote...
  this.setData({ listData: list });  // ← 先更新 UI

  // 持久化
  try {
    const votes = {};
    list.forEach(item => {           // ← 基于当前 list 计算
      votes[item.id] = { likes, disses, userVote };
    });
    wx.setStorageSync('card_votes', votes);  // ← 再写存储
  } catch(e) {}
}
```

**问题：** `setData` 是同步的，但后续 `wx.setStorageSync` 如果因系统 I/O 延迟（低性能设备或存储快满时），此时若用户快速连续操作（如反复点按），`enrichData` 会在下次 `fetchData` 时用旧存储值覆盖 UI 显示值，导致点赞/踩数字与用户实际选择不一致。

**建议：** 改为先读存储、合并数据再写的原子操作：
```js
try {
  const votes = wx.getStorageSync('card_votes') || {};
  votes[id] = { likes: item.likes, disses: item.disses, userVote: item.userVote };
  wx.setStorageSync('card_votes', votes);
} catch(e) {}
```

---

### 4. [交互/功能] FAB `scrollToTop` 在部分场景可能失效

**位置：** `index.js` 第 130-132 行

```js
scrollToTop() {
  this.setData({ scrollTop: 0 });
}
```

**问题：** WeChat Mini Program 中 `scroll-top` 设为 `0` 有时不会被正确触发（尤其是 `scroll-with-animation` 开启时），表现是点击 FAB 后无反应或滚动位置不归零。这是已知的微信小程序兼容性问题。

**建议：** 改为递增 `1` 触发重渲染：
```js
scrollToTop() {
  const top = this.data.scrollTop === 0 ? 1 : 0;
  this.setData({ scrollTop: top }, () => {
    this.setData({ scrollTop: 0 });
  });
}
```

---

## 已知问题排查结果

| # | 已知问题 | 状态 | 说明 |
|---|----------|------|------|
| 1 | 主页横向滚动卡片右侧被裁 | ❌ **未确认修复** | `.card { width: 100% }` + 父级 `padding: 12px 16px` 在 `box-sizing: border-box` 全局生效下理论上安全，但缺少 `.card-list` 显式 `box-sizing` 声明（见问题 #2），存在隐患 |
| 2 | 点赞按钮点不到 | ✅ **已修复** | `catchtap="voteAction"` 正确阻止冒泡，不会触发 `openModal` |
| 3 | 先点赞再点 diss 数目无限叠加 | ✅ **已修复** | `voteAction` 逻辑完整覆盖所有状态切换场景，未见叠加问题 |

---

## ✅ 通过项

- **点赞按钮交互：** `catchtap` 正确使用，不会误触卡片 `openModal`
- **FAB 可见性逻辑：** `onScroll` 正确控制 `showFab` 布尔值，`wx:if` 正确条件渲染
- **Tabs 横向滚动行为：** 最终生效规则为 `overflow-x: auto; white-space: nowrap`，Tab 可横向滑动 ✓
- **卡片宽度约束：** `.card { width: 100%; box-sizing: border-box; }` 理论上不会溢出父容器
- **Modal 事件隔离：** `catchtap=""` 在 `.modal-content` 上阻止冒泡，`.modal-mask` 的 `bindtap="closeModal"` 正常工作

---

## 总结

V1.4.2 在交互逻辑（点赞/踩切换、按钮阻止冒泡）上已无明显 bug，FAB 和 Modal 逻辑健全。

**核心遗留风险：** CSS 规则重复定义（`.tabs`）和 `voteAction` 持久化非原子操作在高频操作下可能导致视觉/数据不一致，建议在下一版本修复后重新验收。
