#!/bin/bash
# sync_github_pages.sh - 每日同步数据到 GitHub Pages（mini program 数据源）
# 新流程: enrichment → copy → push
# Cron: 30 3 * * * 和 40 11 * * *

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$WORKSPACE/logs"
DATE_STR=$(date +%Y%m%d)

mkdir -p "$LOG_DIR"

log() { echo "[$(date '+%H:%M:%S')] $1"; }

# ---- Step 1: 毒舌点评 enrichment ----
log "[enrich] 开始毒舌点评 enrichment..."
if python3 "$SCRIPT_DIR/enrich_quotes.py" --date "$DATE_STR" >> "$LOG_DIR/enrich_quotes.log" 2>&1; then
    log "[enrich] enrichment 完成"
else
    log "[enrich] enrichment 失败（不阻塞后续流程）"
fi

# ---- Step 2: 复制数据到 Git 仓库 ----
log "[copy] 复制数据文件..."
cd "$WORKSPACE/dushe-daily-data"
cp "$WORKSPACE/data/raw_articles_"*.json . 2>/dev/null || log "[copy] raw_articles 无新文件"
cp "$WORKSPACE/data/raw_dev_"*.json . 2>/dev/null || log "[copy] raw_dev 无新文件"
cp "$WORKSPACE/data/raw_social_"*.json . 2>/dev/null || log "[copy] raw_social 无新文件"

# ---- Step 3: 生成 index.json ----
log "[index] 生成 index.json..."
python3 -c "
import json, os, glob
latest = {}
for cat, prefix in [('industry','raw_articles'),('dev','raw_dev'),('social','raw_social')]:
    files = sorted(glob.glob(f'{prefix}_*.json'))
    if files: latest[cat] = files[-1]
json.dump(latest, open('index.json','w'), ensure_ascii=False, indent=2)
print('index:', latest)
"

# ---- Step 4: Git commit & push ----
log "[git] commit & push..."
git add -A
git commit -m "📊 $(date +%Y-%m-%d) 日报数据自动推送" || log "[git] 无变更，跳过 commit"
git push origin main 2>&1 | tail -1

log "[done] sync OK | $(date)"
