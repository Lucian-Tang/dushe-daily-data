#!/bin/bash
# bitable-monitor.sh - 每15分钟检查飞书多维表格，发现pending/卡住任务自动分派

APP_ID="cli_a9663d0dd3785bc0"
APP_SECRET="GcNApeIkIowx5Y42UOHZ5c50TlEyOg0K"
APP_TOKEN="RIYebA1R7aKZ02sCHBhc9Twxntf"
TABLE_ID="tbl2LN4fBmsg0L4r"
BOT_NAME="Lucia"

# 获取 tenant_access_token
TOKEN_RESP=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}")

TOKEN=$(echo "$TOKEN_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tenant_access_token',''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "$(date): failed to get token"
  exit 1
fi

# 读取bitable pending任务
RECORDS=$(curl -s "https://open.feishu.cn/open-apis/bitable/v1/apps/${APP_TOKEN}/tables/${TABLE_ID}/records?page_size=100" \
  -H "Authorization: Bearer $TOKEN" \
  2>/dev/null)

echo "$(date): bitable scan run, got records" >> /root/.openclaw/workspace/memory/bitable-scan.log
echo "$RECORDS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"total: {d.get('data',{}).get('total',0)}\")" 2>/dev/null