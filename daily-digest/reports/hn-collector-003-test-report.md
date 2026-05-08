# HN采集器测试报告 — hn-collector-003

> 测试时间：2026-05-02

---

## 测试结论

| 项目 | 结果 |
|------|------|
| 脚本路径 | `collectors/hn/hn_collector.py` |
| 数据源 | HN Firebase API (topstories) |
| 稳定性 | ✅ 通过 |
| 输出格式 | JSON |
| 单次耗时 | ~10秒 |

---

## 修复内容 (v2.0)

1. **数据源升级**：从 Algolia 搜索改为 Firebase TopStories API，获取真实Top30
2. **增加UA随机化**：避免被识别为爬虫
3. **增加重试机制**：失败自动重试，最多重试2次
4. **批量请求延迟**：防止请求过快被限流
5. **JSON结构化输出**：统一字段（rank/title/score/comments/author/url）

---

## 测试数据（2026-05-02）

| 排名 | 标题 | 分数 | 评论数 |
|------|------|------|--------|
| 1 | Show HN: WhatCable, a tiny menu bar app for inspecting USB-C | 481 | 88 |
| 2 | The gay jailbreak technique (2025) | 481 | 0 |
| 3 | Ti-84 Evo | 413 | 366 |
| 4 | City Learns Flock Accessed Cameras in Children's Gymnastics | 379 | 0 |
| 5 | New research suggests people can communicate... | 308 | 0 |
| 6 | Ask HN: Who is hiring? (May 2026) | 253 | 0 |
| 7 | Ask.com has closed | 200 | 101 |
| 8 | Artemis II Photo Timeline | 163 | 12 |
| 9 | The smelly baby problem | 159 | 0 |
| 10 | Apocalypse Early Warning System | 156 | 0 |

**获取总数：30条**

---

## 使用方法

```bash
cd /root/.openclaw/workspace/daily-digest/collectors/hn
python3 hn_collector.py
# 输出文件：hn_top_YYYYMMDD_HHMMSS.json
```

---

## 状态：✅ 可用