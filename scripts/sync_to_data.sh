#!/bin/bash
# sync_to_data.sh - 将 repo root 的输出文件同步到 data/ 目录（CDN 实际读取路径）
#
# 背景: 管线在 repo root 生成 _daily_*.json / index.json / combined_3days_*.json，
#       但小程序和 web app 从 data/ 子目录读取。此脚本确保 data/ 始终与 root 同步。
#
# 用法:
#   ./scripts/sync_to_data.sh              # 同步所有输出文件
#   ./scripts/sync_to_data.sh --date 0519  # 仅同步指定日期文件

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"

log() { echo "[$(date '+%H:%M:%S')] $1"; }

cd "$WORKSPACE"

sync_count=0
skip_count=0

# ── 辅助函数：仅当源文件更新或不同时才复制 ──
smart_copy() {
    local src="$1"
    local dst="$2"
    if [ ! -f "$src" ]; then
        return 1  # 源文件不存在
    fi
    if [ -f "$dst" ]; then
        if cmp -s "$src" "$dst"; then
            skip_count=$((skip_count + 1))
            return 0  # 已相同，跳过
        fi
    fi
    cp "$src" "$dst"
    sync_count=$((sync_count + 1))
    log "  📄 $(basename "$src") → data/"
    return 0
}

# ── 1. 同步 _daily_*.json ──
# 优先同步今日文件；如果传了 --date 参数则只同步指定日期
DATE_FILTER="${1:-}"

for f in *_daily_*.json; do
    [ -f "$f" ] || continue
    
    # 如果有日期过滤，只匹配指定日期
    if [ -n "$DATE_FILTER" ] && [ "$DATE_FILTER" != "--date" ]; then
        if ! echo "$f" | grep -q "$DATE_FILTER"; then
            continue
        fi
    fi
    
    smart_copy "$f" "data/$f" || true
done

# ── 2. 同步 index.json ──
smart_copy "index.json" "data/index.json" || true

# ── 3. 同步 combined_3days_*.json ──
for f in combined_3days_*.json; do
    [ -f "$f" ] || continue
    if [ -n "$DATE_FILTER" ] && [ "$DATE_FILTER" != "--date" ]; then
        if ! echo "$f" | grep -q "$DATE_FILTER"; then
            continue
        fi
    fi
    smart_copy "$f" "data/$f" || true
done

# ── 4. 同步 combined_all_*.json ──
for f in combined_all_*.json; do
    [ -f "$f" ] || continue
    if [ -n "$DATE_FILTER" ] && [ "$DATE_FILTER" != "--date" ]; then
        if ! echo "$f" | grep -q "$DATE_FILTER"; then
            continue
        fi
    fi
    smart_copy "$f" "data/$f" || true
done

# ── 5. 同步 hf_daily_*.json (如有) ──
for f in hf_daily_*.json; do
    [ -f "$f" ] || continue
    smart_copy "$f" "data/$f" || true
done

if [ "$sync_count" -gt 0 ]; then
    log "✅ data/ 同步完成: ${sync_count} 个文件更新, ${skip_count} 个跳过"
else
    log "✅ data/ 已是最新 (${skip_count} 个文件无变化)"
fi
