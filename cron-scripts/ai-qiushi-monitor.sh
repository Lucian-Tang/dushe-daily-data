#!/bin/bash
# AI糗事项目进度监控
# 每5分钟检查Thomas和Stephen在群里的进展，有重要更新才汇报

SESSION_FILE="/root/.openclaw/agents/main/sessions/1738d716-aa9f-4286-b57e-4208429f401a.jsonl"
LAST_MARKER="/root/.openclaw/workspace/cron-scripts/.qiushi-monitor.last"
REPORT_FILE="/root/.openclaw/workspace/cron-scripts/.qiushi-monitor.report"

# 获取最后处理的消息行数
LAST_LINE=$(cat "$LAST_MARKER" 2>/dev/null || echo "0")

# 检查群session文件是否有新消息（来自Thomas或Stephen）
if [ ! -f "$SESSION_FILE" ]; then
  exit 0
fi

TOTAL_LINES=$(wc -l < "$SESSION_FILE")

if [ "$TOTAL_LINES" -le "$LAST_LINE" ]; then
  exit 0
fi

# 读取新增的消息内容
NEW_CONTENT=$(sed -n "$((LAST_LINE + 1)),${TOTAL_LINES}p" "$SESSION_FILE")

# 检查是否有Thomas或Stephen的新消息
THOMAS_MSGS=$(echo "$NEW_CONTENT" | grep -c "ou_a008f43038a95e29f811ef091080b2dc\|Thomas" 2>/dev/null || true)
STEPHEN_MSGS=$(echo "$NEW_CONTENT" | grep -c "ou_8c7e4af2f2e4f98fc849e6320a7afc4f\|Stephen" 2>/dev/null || true)

# 只要有任一方的新消息就记录
if [ "$THOMAS_MSGS" -gt 0 ] || [ "$STEPHEN_MSGS" -gt 0 ]; then
  echo "Thomas: $THOMAS_MSGS条新消息, Stephen: $STEPHEN_MSGS条新消息" > "$REPORT_FILE"
fi

# 更新marker
echo "$TOTAL_LINES" > "$LAST_MARKER"

exit 0