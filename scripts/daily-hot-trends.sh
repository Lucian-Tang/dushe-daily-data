#!/bin/bash
# 每日热榜推送脚本 — 推到飞书群
# 使用方式: bash daily-hot-trends.sh

SKILL_DIR="$HOME/.openclaw/workspace/skills/cn-trends-aggregator"
WORK_DIR="$HOME/.openclaw/workspace/shared/trends"
CHAT_ID="oc_b020039d18d36b0d02eb3c021df8af9e"

mkdir -p "$WORK_DIR"

# 抓数据
TRENDS=$(cd "$SKILL_DIR" && python3 scripts/fetch_trends.py \
  --sources baidu,toutiao,v2ex,hn,github \
  --format markdown \
  --limit 8 \
  2>/dev/null)

# 拼接日期
DATE_STR=$(date "+%Y年%m月%d日 %H:%M")

MESSAGE="🔥 每日热榜 — $DATE_STR

$TRENDS"

# 发飞书
openclaw message send \
  --channel feishu \
  --target "$CHAT_ID" \
  --message "$MESSAGE" 2>&1

echo "TRENDS_SENT_AT=$(date)" >> "$WORK_DIR/last_sent.log"
