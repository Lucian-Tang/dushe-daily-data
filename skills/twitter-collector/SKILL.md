---
name: twitter-collector
description: "推特/X 采集器 | 使用 twscrape 采集指定用户最新推文。触发词：推特、推文采集、twitter、tweet。"
metadata:
  openclaw:
    emoji: "🐦"
    category: "social-media"
    tags: ["twitter", "x", "social", "scraper"]
    requires:
      bins: ["python3", "curl"]
---

# Twitter Collector

使用 twscrape 采集推特/X 用户最新推文，不依赖 RSSHub。

## 环境准备

```bash
pip install twscrape --break-system-packages
```

## 使用方式

### 采集用户最新推文

```bash
python3 scripts/twitter_fetch.py --user <username> --limit 10
```

### 采集多个用户

```bash
python3 scripts/twitter_fetch.py --users user1 user2 user3 --limit 10
```

## twscrape CLI

twscrape 也提供命令行工具：

```bash
# 添加账号（需要 cookies/auth token）
twscrape add_accounts <cookie_string>

# 查看推文
twscrape user_tweets <username> --limit 10

# 搜索
twscrape search "关键词" --limit 10
```

## 注意

- 公开抓取有频率限制
- 建议配置多个账号提升配额
- 高频率请求可能导致账号被限制
