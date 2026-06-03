#!/bin/bash
# sync_to_data.sh - 将 data/ 目录反向同步到 repo root（防双路径腐烂）
#
# 🔴 2026-06-03 P0 修复：统一 CDN 数据源到 data/ 目录，砍掉双路径
#   - 旧逻辑：root → data/（root 是源，data/ 是镜像）→ 根目录空文件会覆盖 data/ 有效数据
#   - 新逻辑：data/ → root（data/ 是权威源，root 是镜像）→ 永远以 data/ 为准
#   - 搭配 gen-index.py：index.json 使用 "data/" 前缀，Web 端直接请求 data/ 文件
#   - 安全保护：safe_cp 阻止空数据（size≤3 bytes）覆盖有效数据
#
# 用法:
#   ./scripts/sync_to_data.sh              # 仅将今日 data/ 文件同步到 root
#   ./scripts/sync_to_data.sh --all        # 🔴 同步所有文件（危险！）
#   ./scripts/sync_to_data.sh --date 0519  # 仅同步指定日期文件

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"

log() { echo "[$(date '+%H:%M:%S')] $1"; }

cd "$WORKSPACE"

sync_count=0
skip_count=0
protected_count=0

# ── 安全复制函数：防止空数据覆盖有效数据 ──
safe_cp() {
    local src="$1"
    local dst="$2"

    if [ ! -f "$src" ]; then
        return 1  # 源文件不存在
    fi

    # 获取文件大小
    local src_size
    src_size=$(stat -c%s "$src" 2>/dev/null || stat -f%z "$src" 2>/dev/null || echo 0)

    # 如果目标文件已存在且有数据
    if [ -f "$dst" ]; then
        local dst_size
        dst_size=$(stat -c%s "$dst" 2>/dev/null || stat -f%z "$dst" 2>/dev/null || echo 0)

        # 源为空（size≤3 即 "[]" 或 "{}"），目标有正常数据 → 保护！跳过覆盖
        if [ "$src_size" -le 3 ] && [ "$dst_size" -gt 3 ]; then
            local fname
            fname=$(basename "$src")
            log "  🛡️  阻止空数据覆盖: $fname (src=${src_size}B空, dst=${dst_size}B有效, 已保护)"
            protected_count=$((protected_count + 1))
            return 1
        fi
    fi

    # 内容已相同则跳过
    if [ -f "$dst" ] && cmp -s "$src" "$dst"; then
        skip_count=$((skip_count + 1))
        return 0
    fi

    cp "$src" "$dst"
    sync_count=$((sync_count + 1))
    log "  📄 $(basename "$src") → root (data/ 权威源)"
    return 0
}

# ── 1. data/ → root: 将 data/ 的 daily JSON 反向同步到根目录 ──
# 默认只同步今日文件，保护历史 L2 数据不可变
SYNC_ALL=false
DATE_FILTER=""

if [ "${1:-}" = "--all" ]; then
    SYNC_ALL=true
elif [ "${1:-}" = "--date" ]; then
    DATE_FILTER="${2:-$(date +%Y%m%d)}"
fi

TODAY_FILTER=$(date +%Y%m%d)

for f in data/*_daily_*.json; do
    [ -f "$f" ] || continue
    basename_f="$(basename "$f")"

    if $SYNC_ALL; then
        true  # 同步所有
    elif [ -n "$DATE_FILTER" ]; then
        if ! echo "$basename_f" | grep -q "$DATE_FILTER"; then
            continue
        fi
    else
        # 默认：仅同步今日文件
        if ! echo "$basename_f" | grep -q "$TODAY_FILTER"; then
            continue
        fi
    fi

    # 🔴 data/ → root 反向同步（data/ 是权威源）
    safe_cp "$f" "$basename_f" || true
done

# ── 2. 同步 index.json（仍从 root 写，gen-index.py 已生成权威版本）──
# index.json 在 root 已由 gen-index.py 生成（带 data/ 前缀），
# data/index.json 也已由 gen-index.py 写入（不带前缀，供小程序加载）
# 此处确保 root 和 data/ 的 index.json 都存在且根版本最新
if [ -f "index.json" ]; then
    safe_cp "index.json" "data/index.json" || log "  ⚠️ index.json → data/index.json 跳过（保护）"
fi

# ── 3. 同步 weekly_*.json / ai_models_*.json / hf_daily (如有) ──
for prefix in hf_daily ai_models_daily ai_models_weekly weekly_github weekly_clawhub; do
    for f in ${prefix}_*.json; do
        [ -f "$f" ] || continue
        safe_cp "$f" "data/$f" || true
    done
done

if [ "$sync_count" -gt 0 ] || [ "$protected_count" -gt 0 ]; then
    log "✅ data/ → root 同步完成: ${sync_count} 更新, ${skip_count} 跳过, 🛡️ ${protected_count} 保护"
else
    log "✅ data/ → root 已是最新 (${skip_count} 个文件无变化)"
fi
