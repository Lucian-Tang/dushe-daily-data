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
    QA_REPORT=$(python3 "$SCRIPT_DIR/../../scripts/morning-pipeline-check.py" --date "$(date +%Y-%m-%d)" 2>&1)
    echo "$QA_REPORT" | tee -a "$LOG_FILE"
    
    if echo "$QA_REPORT" | grep -q "整体状态: ✅ OK"; then
        log "✅ QA 校验通过"
    else
        if echo "$QA_REPORT" | grep -q "整体状态: ⚠️"; then
            log "⚠️ QA 有警告（自动继续）"
        else
            log "❌ QA 校验失败！请检查 staging 数据后再试"
            log "   或使用 --force 跳过校验"
            exit 1
        fi
    fi
    
    # ── Phase 2: 深度 QA — CDN 文件 published 日期校验 ──
    # 🔴 P0 fix（2026-06-03）：检查 data/ 目录文件（CDN 权威数据源）
    log "[2b/5] CDN 文件 published 日期深度校验（data/ 权威源）..."
    TODAY_DASH=$(date +%Y-%m-%d)
    CDN_SECTIONS=("industry" "dev" "ai" "startup" "design")
    CDN_ERRORS=()
    for SEC in "${CDN_SECTIONS[@]}"; do
        CDN_FILE="$WORKSPACE/data/${SEC}_daily_$(date +%Y%m%d).json"
        if [ ! -f "$CDN_FILE" ]; then
            # Fallback: check root
            CDN_FILE="$WORKSPACE/${SEC}_daily_$(date +%Y%m%d).json"
            if [ ! -f "$CDN_FILE" ]; then
                CDN_ERRORS+=("❌ ${SEC}: CDN 文件缺失（data/ 和 root 均无）")
                continue
            fi
        fi
        # 检查所有 item 的 published 是否匹配文件名日期
        MISMATCH_COUNT=$(python3 -c "
import json
with open('$CDN_FILE') as f:
    data = json.load(f)
if not isinstance(data, list):
    print(-1)
    exit()
today = '$TODAY_DASH'
total = len(data)
if total == 0:
    print(0)
    exit()
mismatch = sum(1 for i in data if i.get('published','')[:10] != today)
print(mismatch)
")
        if [ "$MISMATCH_COUNT" = "-1" ]; then
            CDN_ERRORS+=("❌ ${SEC}: CDN 文件格式异常（非数组）")
        else
            ITEM_COUNT=$(python3 -c "import json;print(len(json.load(open('$CDN_FILE'))))")
            if [ "$ITEM_COUNT" -gt "0" ] && [ "$MISMATCH_COUNT" = "$ITEM_COUNT" ]; then
                CDN_ERRORS+=("❌ ${SEC}: ${MISMATCH_COUNT}/${ITEM_COUNT} 条 published 日期全不匹配 ${TODAY_DASH}")
            elif [ "$ITEM_COUNT" = "0" ]; then
                CDN_ERRORS+=("⚠️ ${SEC}: CDN 文件为空 (0条数据)")
            elif [ "$MISMATCH_COUNT" -gt "0" ]; then
                log "   ⚠️ ${SEC}: ${MISMATCH_COUNT}/${ITEM_COUNT} 条日期不匹配（部分错误，继续）"
            else
                log "   ✅ ${SEC}: ${ITEM_COUNT} 条，日期全部匹配"
            fi
        fi
    done
    
    if [ ${#CDN_ERRORS[@]} -gt 0 ]; then
        for err in "${CDN_ERRORS[@]}"; do
            log "   $err"
        done
        log "❌ CDN 深度 QA 失败 (${#CDN_ERRORS[@]} 项错误)，终止 promote"
        log "   修复步骤: 检查 normalize_daily_data.py 是否正确执行"
        exit 1
    fi
    log "✅ CDN 深度 QA 全部通过"
fi

# Step 3: 同步数据到 data/ 目录（安全网：确保 CDN 路径数据最新）
log "[3/5] 同步 data/ 目录..."
bash "$SCRIPT_DIR/sync_to_data.sh" 2>&1 | tee -a "$LOG_FILE" || log "⚠️ data/ 同步失败（不阻塞，继续 promote）"

# Step 4: Merge staging → main
log "[4/5] 合并 staging → main..."
# 确保本地 staging 是最新的
git checkout staging
git pull origin staging

# 切到 main，合并 staging
git checkout main
git pull origin main
git merge staging --no-edit || {
    log "⚠️ 合并冲突！自动兜底：以 staging 为准覆盖..."
    # 兜底策略：遇到冲突时，以 staging 的内容为准（staging 是上游数据源）
    git merge --abort 2>/dev/null
    
    # 方案1: -X theirs 自动选择 staging 版本
    if git merge -X theirs staging --no-edit 2>&1; then
        log "✅ 自动合并成功（-X theirs）"
    else
        # 方案2: 强制从 staging 拉取所有文件覆盖
        log "⚠️ -X theirs 失败，强制覆盖..."
        git merge --abort 2>/dev/null
        git checkout staging -- .
        git commit -m "auto-sync: force staging into main at $(date +%Y%m%d-%H%M%S)" --no-edit 2>/dev/null || {
            log "❌ 所有合并尝试均失败，请手动处理"
            git checkout staging
            exit 1
        }
        log "✅ 强制覆盖成功（staging → main）"
    fi
}

# ── index.json 校验（防止旧版覆盖）──
log "[4b/5] 校验 index.json..."
TODAY_SHORT=$(date +%Y%m%d)
python3 -c "
import json
with open('index.json') as f:
    d = json.load(f)
sections = ['industry','dev','ai','startup','design']
bad = [s for s in sections if '$TODAY_SHORT' not in str(d.get(s,''))]
assert not bad, f'index.json 仍指向旧文件: {bad}'
print(f'index.json ✅ 所有 {len(sections)} 板块指向今日文件')
" || {
    log "❌ index.json 校验失败！可能被旧版覆盖"
    log "   当前 index.json 内容:"
    python3 -c "import json;print(json.dumps(json.load(open('index.json')),indent=2,ensure_ascii=False))" 2>/dev/null | head -20
    git merge --abort 2>/dev/null || true
    git checkout staging
    log "   已回退合并，请检查 staging 上的 index.json 并手动修复"
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
