#!/bin/bash
# bitable-monitor-system.sh - 每30分钟检查bitable，发现in_progress超过45分钟的任务
# 彻底旁路 agent 层，避免 OpenClaw cron 超时波动

set -e

APP_ID="cli_a9663d0dd3785bc0"
APP_SECRET="GcNApeIkIowx5Y42UOHZ5c50TlEyOg0K"
APP_TOKEN="RIYebA1R7aKZ02sCHBhc9Twxntf"
TABLE_ID="tbl2LN4fBmsg0L4r"
LOG_FILE="/root/.openclaw/workspace/memory/bitable-scan-system.log"
ALERT_LOG="/root/.openclaw/workspace/memory/bitable-alert.log"
FEISHU_GROUP="oc_b020039d18d36b0d02eb3c021df8af9e"

get_token() {
    curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
        -H "Content-Type: application/json" \
        -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" \
        | python3 -c "import sys,json; print(json.load(sys.stdin).get('tenant_access_token',''))"
}

fetch_records() {
    local token=$1
    curl -s "https://open.feishu.cn/open-apis/bitable/v1/apps/${APP_TOKEN}/tables/${TABLE_ID}/records?page_size=500" \
        -H "Authorization: Bearer $token"
}

send_feishu() {
    local token=$1
    local msg=$2
    curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "{\"receive_id\":\"$FEISHU_GROUP\",\"msg_type\":\"text\",\"content\":{\"text\":\"$msg\"}}" > /dev/null
}

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"
}

log "=== Bitable scan started ==="

TOKEN=$(get_token)
if [ -z "$TOKEN" ]; then
    log "ERROR: failed to get token"
    exit 1
fi

RECORDS=$(fetch_records "$TOKEN")

if ! echo "$RECORDS" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
    log "ERROR: failed to fetch records"
    exit 1
fi

STUCK=$(echo "$RECORDS" | python3 -c "
import sys, json
from datetime import datetime

d = json.load(sys.stdin)
now_ms = int(datetime.now().timestamp() * 1000)
stuck = []

for r in d.get('data', {}).get('items', []):
    fields = r.get('fields', {})
    status = fields.get('状态', '')
    created = fields.get('创建时间', 0)
    task_id = fields.get('task_id', 'unknown')

    if status == 'in_progress' and created and created > 1000000000000:
        age_min = (now_ms - created) / 60000
        if age_min > 45:
            rid = r.get('id', '')
            stuck.append(f'{task_id} ({int(age_min)}min)')

if stuck:
    print('\n'.join(stuck))
else:
    print('OK')
")

if [ "$STUCK" = "OK" ]; then
    log "No stuck tasks"
    send_feishu "$TOKEN" "✅ BitableMonitor: 无卡住任务"
else
    MSG="⚠️ BitableMonitor 发现卡住任务:
$STUCK"
    echo "$MSG" >> "$ALERT_LOG"
    send_feishu "$TOKEN" "$MSG"
    log "Found stuck tasks: $STUCK"
fi