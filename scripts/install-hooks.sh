#!/bin/bash
# install-hooks.sh - 安装 Git hooks 到 .git/hooks/
#
# 用法:
#   bash scripts/install-hooks.sh              # 安装所有 hooks
#   bash scripts/install-hooks.sh --dry-run    # 预览（不实际写入）
#
# 安全措施:
#   - 安装前自动备份已有 hook（.git/hooks/<name>.bak.时间戳）
#   - 不会静默覆盖

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"
HOOKS_DIR="$WORKSPACE/.git/hooks"
DRY_RUN=false

[ "${1:-}" = "--dry-run" ] && DRY_RUN=true

if [ ! -d "$HOOKS_DIR" ]; then
    echo "❌ 未找到 .git/hooks 目录，请确认在 Git 仓库中执行"
    exit 1
fi

install_hook() {
    local source_name="$1"   # 源文件名（不含 .sh 后缀）
    local target_name="${2:-$1}"  # 目标 hook 名
    local source="$SCRIPT_DIR/${source_name}.sh"
    local target="$HOOKS_DIR/$target_name"

    if [ ! -f "$source" ]; then
        echo "⚠️  源文件不存在: $source，跳过"
        return
    fi

    echo ""
    echo "📋 安装 $target_name hook..."

    if $DRY_RUN; then
        if [ -f "$target" ]; then
            echo "   [dry-run] 将备份已有 $target_name → ${target_name}.bak.$(date +%Y%m%d-%H%M%S)"
        fi
        echo "   [dry-run] $source → $target"
        return
    fi

    # 备份已有 hook
    if [ -f "$target" ]; then
        local bak="${target}.bak.$(date +%Y%m%d-%H%M%S)"
        cp "$target" "$bak"
        echo "   📦 已备份已有 hook → .git/hooks/$(basename "$bak")"
    fi

    # 复制新的 hook
    cp "$source" "$target"
    chmod +x "$target"
    echo "   ✅ $target_name hook 安装完成"
}

# ── 安装 pre-push hook ──
install_hook "pre-push-hook" "pre-push"

echo ""
echo "✅ 所有 hooks 安装完成"
echo ""
echo "当前已安装的 hooks:"
ls -la "$HOOKS_DIR" | grep -v '\.sample' | grep -v '^total' | grep -v '\.bak\.' | awk '{print "   " $NF}'
