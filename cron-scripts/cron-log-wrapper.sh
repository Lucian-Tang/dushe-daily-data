#!/bin/bash
# cron-log-wrapper.sh - 结构化执行日志包装器
# 用法: cron-log-wrapper.sh <cron_name> <stage1,stage2,...> <command>
# 例: cron-log-wrapper.sh dev-daily-report "fetch,summarize,format,push_feishu,push_github" "echo hello"

set -e

CRON_NAME="$1"
STAGES="$2"
shift 2 || shift 1
COMMAND="$@"

# 日志目录
LOG_DIR="/root/.openclaw/workspace/logs"
mkdir -p "$LOG_DIR"

# 日志文件（每日一个JSONL）
TODAY=$(date +%Y-%m-%d)
LOG_FILE="${LOG_DIR}/cron-exec-${TODAY}.jsonl"

# 解析 stages（支持逗号分隔或空格分隔）
IFS=',' read -ra STAGE_ARRAY <<< "$STAGES"
if [ ${#STAGE_ARRAY[@]} -eq 1 ] && [ -z "${STAGE_ARRAY[0]}" ]; then
  STAGE_ARRAY=("full")
fi

log_entry() {
  local stage="$1"
  local status="$2"
  local duration_ms="$3"
  local error="$4"
  local ts
  ts=$(date +%Y-%m-%dT%H:%M:%S.%3NZ)

  local json
  if [ "$status" = "failed" ] && [ -n "$error" ]; then
    json=$(printf '%s' "{\"timestamp\":\"$ts\",\"cron_name\":\"$CRON_NAME\",\"stage\":\"$stage\",\"status\":\"$status\",\"duration_ms\":$duration_ms,\"error\":\"$(echo "$error" | sed 's/"/\\"/g' | tr -d '\n')\"}")
  else
    json=$(printf '%s' "{\"timestamp\":\"$ts\",\"cron_name\":\"$CRON_NAME\",\"stage\":\"$stage\",\"status\":\"$status\",\"duration_ms\":$duration_ms}")
  fi

  echo "$json" >> "$LOG_FILE"
}

echo "[cron-log-wrapper] Starting cron=$CRON_NAME stages=${STAGES}" >&2

for stage in "${STAGE_ARRAY[@]}"; do
  stage=$(echo "$stage" | xargs)  # trim whitespace
  start_ns=$(date +%s%N)

  # 记录 started
  log_entry "$stage" "started" 0

  # 执行命令（如果是 full stage，执行全部命令）
  error_msg=""
  if [ "$stage" = "full" ]; then
    set +e
    eval "$COMMAND" 2>&1
    exit_code=$?
    set -e
    if [ $exit_code -ne 0 ]; then
      error_msg="exit_code=$exit_code"
    fi
  else
    # 分阶段：这里 stage 仅用于日志标记，实际执行由外部控制
    # 此模式供将来扩展用，当前 full 模式覆盖主要用法
    :
  fi

  end_ns=$(date +%s%N)
  duration_ms=$(( (end_ns - start_ns) / 1000000 ))

  if [ -n "$error_msg" ]; then
    log_entry "$stage" "failed" "$duration_ms" "$error_msg"
    echo "[cron-log-wrapper] FAILED cron=$CRON_NAME stage=$stage duration_ms=$duration_ms error=$error_msg" >&2
  else
    log_entry "$stage" "success" "$duration_ms"
    echo "[cron-log-wrapper] SUCCESS cron=$CRON_NAME stage=$stage duration_ms=$duration_ms" >&2
  fi
done

echo "[cron-log-wrapper] Done cron=$CRON_NAME" >&2
