#!/bin/bash
# promote-staging.sh - 将 staging 分支的数据审核并提升到 main（生产环境）
#
# 用法:
#   ./scripts/promote-staging.sh              # 标准提升（含QA校验）
#   ./scripts/promote-staging.sh --force      # 跳过QA校验强制提升
#   ./scripts/promote-staging.sh --status     # 查看 staging vs main 差异
#   ./scripts/promote-staging.sh --rollback   # 回滚上一次 promote

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$WORKSPACE/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/promote-$(date +%Y%m%d-%H%M).log"

log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG_FILE"; }

cd "$WORKSPACE"

if [ "${1:-}" = "--status" ]; then
    log "=== staging vs main 差异 ==="
    git fetch origin staging main 2>&1 || true
    echo ""
    echo "📊 待 promote 的 commit:"
    git log origin/main..origin/staging --oneline --no-decorate 2>/dev/null || echo "  （无差异）"
    echo ""
    echo "📁 变更文件列表:"
    git diff origin/main..origin/staging --name-only 2>/dev/null || echo "  （无变更）"
    echo ""
    echo "📋 数据汇总（staging）:"
    python3 "$SCRIPT_DIR/../scripts/morning-pipeline-check.py" --date "$(date +%Y-%m-%d)" 2>/dev/null | head -25
    exit 0
fi

if [ "${1:-}" = "--rollback" ]; then
    log "=== 回滚 main 分支 ==="
    git checkout main
    git pull origin main
    echo ""
    log "当前 main 最近 5 个 commit:"
    git log --oneline -5
    echo ""
    read -p "输入要回滚到的 commit hash（留空回滚 1 步）: " TARGET
    if [ -z "$TARGET" ]; then
        git revert HEAD --no-edit
        log "✅ 已回滚 1 步"
    else
        git revert "$TARGET..HEAD" --no-edit
        log "✅ 已回滚到 $TARGET"
    fi
    git push origin main
    log "✅ main 已推送（CDN 将在 ~10min 后刷新）"
    git checkout staging
    exit 0
fi

log "=== Promote: staging → main ==="
log "日期: $(date +%Y-%m-%d %H:%M)"

# Step 1: Fetch latest
log "[1/5] 拉取最新代码..."
git fetch origin staging main

# Step 2: QA 校验（除非 --force）
if [ "${1:-}" = "--force" ]; then
    log "[2/5] ⚠️ 跳过 QA 校验（--force）"
else
    log "[2/5] 运行 QA 校验..."
    QA_REPORT=$(python3 "$SCRIPT_DIR/../scripts/morning-pipeline-check.py" --date "$(date +%Y-%m-%d)" 2>&1)
    echo "$QA_REPORT" | tee -a "$LOG_FILE"
    
    if echo "$QA_REPORT" | grep -q "整体状态: ✅ OK"; then
        log "✅ QA 校验通过"
    else
        if echo "$QA_REPORT" | grep -q "整体状态: ⚠️"; then
            log "⚠️ QA 有警告，是否需要继续? (y/N)"
            read -r CONTINUE
            if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
                log "❌ 取消 promote"
                exit 1
            fi
        else
            log "❌ QA 校验失败！请检查 staging 数据后再试"
            log "   或使用 --force 跳过校验"
            exit 1
        fi
    fi
fi

# Step 3: 检查 combined_3days 文件
log "[3/5] 检查 combined_3days 文件..."
DATE_COMPACT=$(date +%Y%m%d)
COMBINED_FILE="$WORKSPACE/combined_3days_${DATE_COMPACT}.json"
if [ -f "$COMBINED_FILE" ]; then
    ITEMS=$(python3 -c "import json;d=json.load(open('$COMBINED_FILE'));print(sum(len(v) for v in d.values()))")
    TODAY_ITEMS=$(python3 -c "
import json
d=json.load(open('$COMBINED_FILE'))
today='$(date +%Y-%m-%d)'
total=0
for k in ['industry','dev','ai','startup','design']:
    total+=len([i for i in d.get(k,[]) if i.get('published','')[:10]==today])
print(total)
")
    log "   combined_3days: ${ITEMS}条, 今日${TODAY_ITEMS}条"
else
    log "⚠️  combined_3days 文件不存在，将重生成..."
    python3 "$SCRIPT_DIR/generate_combined_3days.py" 2>&1 | tee -a "$LOG_FILE"
fi

# Step 4: Merge staging → main
log "[4/5] 合并 staging → main..."
# 确保本地 staging 是最新的
git checkout staging
git pull origin staging

# 切到 main，合并 staging
git checkout main
git pull origin main
git merge staging --no-edit || {
    log "❌ 合并冲突！请手动解决"
    git merge --abort
    git checkout staging
    exit 1
}

# Step 5: Push to main
log "[5/5] 推送到 main..."
git push origin main
echo ""
log "✅ Promote 完成！CDN 将在 ~10min 后刷新"
log "   回滚命令: ./scripts/promote-staging.sh --rollback"

# 切回 staging 以备下次使用
git checkout staging

log "=== Promote 结束 ==="
