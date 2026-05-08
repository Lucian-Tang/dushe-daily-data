# 团队执行规则

> 从每日复盘中提取，持续积累，不走回头路。
> 最后更新：2026-05-08

---

## 规则 1：发版前必走校验官

```
Stephen 改代码 → 校验官（MiniMax M2.7）审查
  → 通过 → Lucia 发版预览
  → 打回 → Stephen 修 → 重新送审
```

**触发：** 每次 `scripts/upload.js` 前

---

## 规则 2：产品方案先于代码

```
Boss 提需求 → Thomas 出轻量级产品方案（15min）
  → 讨论确认 →
  → Stephen 写代码
```

**禁止：** 需求直接跳代码

---

## 规则 3：CSS 精准修改原则

- 不写全量选择器（`view { ... }`）
- 修改最小范围，用 class 选择器
- 改完自己测 iPhone 模拟器
- 所有卡片/布局元素加 `box-sizing: border-box`

---

## 规则 4：Cron 错峰

```
3:10 industry-daily
3:15 dev-daily
3:20 startup-daily
3:25 ai-daily
3:30 design-daily
3:35 signals (hn, github, arxiv)
```

间隔 ≥5 分钟，避免并发 token 竞争

---

## 规则 5：归档追加不覆写

- 更新索引/归档文档：**用 `append`，不 `write` 全量替换**
- 保护历史数据，每日追加顶部

---

## 规则 6：双轨产出

```
所有重要产出：
1. 本地文件 → reports/ 或 agents/ 目录
2. 飞书文档 → folder: PaxYfSJpklspzudy9MqcYMbQnde
3. 只有本地 = 没做完
```

---

## 规则 7：Agent Mode Declaration

每次开始任务，先声明工作模式：
- 「模式：架构设计」
- 「模式：快速编码」
- 「模式：产品调研」

让 Boss 知道当前产出质量预期。

---

## 规则 8：文件锁协议

共享资源操作前在群内：`占用 → 完成 → 释放`
避免多个 agent 同时改同一文件。

---

## 执行检查

Lucia 每次心跳检查：
- 校验官是否在发版前跑过？
- cron 是否按错峰表运行？
- 归档是否完整（双轨）？

---

*本文件为执行层规则，与 agents/AGENTS.md（架构层）互补。*
*每日复盘新增的规则追加到本文档。*
