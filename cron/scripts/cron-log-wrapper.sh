#!/bin/bash
# cron-log-wrapper.sh - Structured JSONL logger for cron jobs
# Usage: cron-log-wrapper.sh <cron_name> <stage> <command> [args...]
# Output: JSONL to /root/.openclaw/workspace/logs/cron-exec-YYYY-MM-DD.jsonl

set -euo pipefail

CRON_NAME="${1:-}"
STAGE="${2:-full}"
COMMAND="${3:-}"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)
LOG_DIR="/root/.openclaw/workspace/logs"
LOG_FILE="${LOG_DIR}/cron-exec-$(date +%Y-%m-%d).jsonl"

if [ -z "$CRON_NAME" ] || [ -z "$COMMAND" ]; then
  echo "Usage: cron-log-wrapper.sh <cron_name> <stage> <command> [args...]" >&2
  exit 1
fi

mkdir -p "$LOG_DIR"

log_event() {
  local status="$1"
  local duration_ms="${2:-0}"
  local error="${3:-}"
  local entry
  if [ -n "$error" ]; then
    entry=$(printf '{"timestamp":"%s","cron_name":"%s","stage":"%s","status":"%s","duration_ms":%s,"error":"%s"}' \
      "$TIMESTAMP" "$CRON_NAME" "$STAGE" "$status" "$duration_ms" "$error")
  else
    entry=$(printf '{"timestamp":"%s","cron_name":"%s","stage":"%s","status":"%s","duration_ms":%s}' \
      "$TIMESTAMP" "$CRON_NAME" "$STAGE" "$status" "$duration_ms")
  fi
  echo "$entry" >> "$LOG_FILE"
}

log_event "started" 0

START_TIME=$(date +%s%3N)
set +e
bash -c "$COMMAND ${4:-} ${5:-} ${6:-} ${7:-} ${8:-}" 2>&1
EXIT_CODE=$?
set -e
END_TIME=$(date +%s%3N)
DURATION=$((END_TIME - START_TIME))

if [ $EXIT_CODE -eq 0 ]; then
  log_event "success" "$DURATION"
  exit 0
else
  log_event "failed" "$DURATION" "exit_code:$EXIT_CODE"
  exit $EXIT_CODE
fi