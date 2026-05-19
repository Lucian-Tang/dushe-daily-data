#!/bin/bash
# verify-l2-immutable.sh - 每日 L2 文件写入后生成 sha256 快照校验和
#
# 用法:
#   bash scripts/verify-l2-immutable.sh                  # 为今日文件生成校验和
#   bash scripts/verify-l2-immutable.sh --date 20260519  # 指定日期
#
# 输出文件: data/.l2_checksums
# 格式:
#   # 2026-05-19
#   industry_daily_20260519.json   sha256:abc123...
#   dev_daily_20260519.json        sha256:def456...
#
# 每次 push 前 pre-push hook 会检查：
#   - 历史文件（日期 < 今天）不允许修改
#   - 今日文件如有改动，与 checksum 对比并警告

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"
CHECKSUM_FILE="$WORKSPACE/data/.l2_checksums"

DATE_ARG="${1:-}"
if [ "$DATE_ARG" = "--date" ]; then
    DATE_STR="${2:-$(date +%Y%m%d)}"
else
    DATE_STR="$(date +%Y%m%d)"
fi

cd "$WORKSPACE"

# 确保 data/ 目录存在
mkdir -p "$WORKSPACE/data"

# 写入日期头
echo "# $(date -d "${DATE_STR:0:4}-${DATE_STR:4:2}-${DATE_STR:6:2}" +%Y-%m-%d 2>/dev/null || echo "$DATE_STR")" >> "$CHECKSUM_FILE"

count=0
for f in *_daily_${DATE_STR}.json; do
    [ -f "$f" ] || continue
    sha=$(sha256sum "$f" | awk '{print $1}')
    printf "%-35s sha256:%s\n" "$(basename "$f")" "$sha" >> "$CHECKSUM_FILE"
    count=$((count + 1))
done

# 如果根目录有文件，也检查 data/ 下的同日期文件（确保 CDN 路径同步）
for f in data/*_daily_${DATE_STR}.json; do
    [ -f "$f" ] || continue
    sha=$(sha256sum "$f" | awk '{print $1}')
    printf "%-35s sha256:%s\n" "$(basename "$f")" "$sha" >> "$CHECKSUM_FILE"
    count=$((count + 1))
done

echo "" >> "$CHECKSUM_FILE"

if [ "$count" -gt 0 ]; then
    echo "[checksum] ✅ ${count} 个 L2 文件快照已追加到 data/.l2_checksums"
else
    echo "[checksum] ⚠️ 未找到日期 ${DATE_STR} 的 daily 文件，跳过"
fi
