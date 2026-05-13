#!/bin/bash
# rollback.sh - 回滚 main 分支（CDN数据）
# 用法:
#   ./scripts/rollback.sh              # 回滚1步
#   ./scripts/rollback.sh --list       # 显示最近5个版本
#   ./scripts/rollback.sh <hash>       # 回滚到指定版本

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$WORKSPACE"

if [ "${1:-}" = "--list" ]; then
    echo "📋 main 分支最近 10 个 commit:"
    git log origin/main --oneline -10
    exit 0
fi

TARGET="${1:-HEAD}"

git fetch origin main
git checkout main
git pull origin main

if [ "$TARGET" = "HEAD" ]; then
    echo "🔄 回滚 1 步..."
    git revert HEAD --no-edit
else
    echo "🔄 回滚到 $TARGET..."
    git revert "$TARGET..HEAD" --no-edit
fi

git push origin main
echo "✅ 回滚完成！CDN 将在 ~10min 后刷新"
echo "   当前状态:"
git log --oneline -3

git checkout staging 2>/dev/null || true
