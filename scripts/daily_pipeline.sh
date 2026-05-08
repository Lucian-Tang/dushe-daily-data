#!/bin/bash
# daily_pipeline.sh - 行业热点日报调度入口
# Cron: 30 7 * * * /root/.openclaw/workspace/scripts/daily_pipeline.sh >> /root/.openclaw/workspace/logs/crontab.log 2>&1

set -e  # 任何命令失败则退出

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="${WORKSPACE_DIR}/logs"
DATE=$(date +%Y-%m-%d)
DATE_SHORT=$(date +%Y%m%d)

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/daily.log"
}

log "========== 日报流程开始 =========="
log "日期: $DATE"

# Step 1: 抓取
log "[Step 1/3] 开始抓取信源..."
if python3 "${SCRIPT_DIR}/fetch_industry.py" >> "$LOG_DIR/fetch.log" 2>&1; then
    log "抓取完成"
else
    log "抓取失败（继续尝试生成日报）"
fi

# Step 2: 生成日报
log "[Step 2/3] 开始生成日报..."
if python3 "${SCRIPT_DIR}/daily_report.py" >> "$LOG_DIR/report.log" 2>&1; then
    log "日报生成完成"
else
    log "日报生成失败，退出"
    exit 1
fi

# Step 3: 推送飞书
log "[Step 3/3] 开始推送飞书..."
if python3 "${SCRIPT_DIR}/push_to_feishu.py" >> "$LOG_DIR/push.log" 2>&1; then
    log "飞书推送成功"
else
    log "飞书推送失败（详见 push.log）"
    exit 1
fi

log "========== 日报流程完成 =========="