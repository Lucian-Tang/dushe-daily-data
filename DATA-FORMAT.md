# DATA-FORMAT.md — 日报数据格式规范

> 执行概要：所有日报 cron 和 subagent 必须遵循的数据质量标准

## 日报 JSON 格式

每条日报数据为 JSON 数组，每项包含以下字段：

```json
{
  "title": "新闻/产品标题（原文，不翻译）",
  "content": "80-150字中文详细描述，说明：什么事/什么技术、为什么重要、影响谁/目标用户",
  "quote": "15-30字中文毒舌点评 🔥",
  "source": "信源名称（如 Product Hunt、Hacker News）",
  "url": "原文链接",
  "published": "2026-05-10"
}
```

## 内容质量要求

- ✅ content 必须是 80-150 字中文详细描述，不能是一句话 tagline
- ✅ 描述结构：什么事 → 为什么重要 → 影响谁
- ✅ quote（毒舌）每条必带，15-30 字，不许用固定吐槽池
- ✅ source 标注信源，不是 "GitHub Pages"
- ✅ title 保留原标题
- ✅ published 统一 YYYY-MM-DD 格式

## 频道数据文件

| 频道 | 文件 | 数据源 |
|------|------|--------|
| 行业 | industry_daily_{date}.json | HN/The Verge |
| 开发者 | dev_daily_{date}.json | GitHub Trending/Dev.to |
| AI | ai_daily_{date}.json | arXiv/HN/各大AI博客 |
| 社会 | raw_social_{date}.json | 微博/知乎热榜 |
| 创投 | startup_daily_{date}.json | 36氪/TC/IT桔子 |
| 设计 | design_daily_{date}.json | Product Hunt |

## 小程序数据链路

```
GitHub Pages JSON → index.json → data-loader.js normalize() → WXML 渲染
                                              ↓
                                    summary: content前150字（卡片用）
                                    fullContent: 完整content（详情页用）
```

## 发版流程

1. 代码改动 → commit
2. 跑 QA：`python3 scripts/qa-check.py check_deploy {version} "$(git diff HEAD)"`
3. QA 通过 → 上传
4. 版本号：小修 2.1.x，大功能 2.x.0
