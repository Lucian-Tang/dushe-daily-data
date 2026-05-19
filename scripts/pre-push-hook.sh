#!/bin/bash
# ============================================================
# Git pre-push hook for dushe-daily-data
# ============================================================
# 🔴 两道安全锁：
#   1. L2 数据不可变 — 禁止修改历史 daily JSON 文件
#   2. 禁止 force push — 通过检测 ref updates 判断
#
# 工作原理：
#   pre-push hook 从 stdin 接收每行: <local-ref> <local-sha> <remote-ref> <remote-sha>
#   - 如果 remote-sha != 全零 & local-sha 不是 remote-sha 的后代 → force push
#   - 如果被修改的 daily JSON 文件日期 < 今天 → L2 不可变冲突
# ============================================================

remote="$1"
remote_url="$2"

TODAY=$(date +%Y%m%d)
WORKSPACE=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
CHECKSUM_FILE="$WORKSPACE/data/.l2_checksums"

# ---- 保存 stdin（两个检查都需要读取） ----
STDIN_TMP=$(mktemp /tmp/pre-push-stdin.XXXXXX)
trap "rm -f $STDIN_TMP" EXIT
cat > "$STDIN_TMP"

# ---- Check 1: L2 数据不可变 ----
block_l2=false
violations=""

while read local_ref local_sha remote_ref remote_sha; do
    [ -z "$local_ref" ] && continue

    # 获取与 remote 的差异文件
    if [ "$remote_sha" = "0000000000000000000000000000000000000000" ]; then
        # 新分支：检查该 commit 的所有文件
        changed_files=$(git diff-tree --no-commit-id --name-only -r "$local_sha" 2>/dev/null)
    else
        # 增量的文件变更
        changed_files=$(git diff --name-only "$remote_sha" "$local_sha" 2>/dev/null)
    fi

    for f in $changed_files; do
        fname=$(basename "$f")
        # 匹配 {section}_daily_{YYYYMMDD}.json（根目录 + data/ 子目录）
        if [[ "$fname" =~ ^[a-z]+_daily_([0-9]{8})\.json$ ]]; then
            file_date="${BASH_REMATCH[1]}"
            if [ "$file_date" -lt "$TODAY" ]; then
                violations+="  $fname  (日期: $file_date, 路径: $f)"$'\n'
                block_l2=true
            fi

            # 对今天文件：检查 checksum（如果 checksum 文件存在）
            if [ "$file_date" -eq "$TODAY" ] && [ -f "$CHECKSUM_FILE" ]; then
                stored_sum=$(grep "^$fname " "$CHECKSUM_FILE" 2>/dev/null | tail -1 | awk '{print $2}' | sed 's/sha256://')
                if [ -n "$stored_sum" ]; then
                    current_sum=$(sha256sum "$WORKSPACE/$f" 2>/dev/null | awk '{print $1}')
                    if [ "$current_sum" != "$stored_sum" ]; then
                        echo ""
                        echo "╔══════════════════════════════════════════════╗"
                        echo "║  ⚠️  今日 L2 文件校验和不匹配: $fname"
                        echo "║     已记录 sha256: ${stored_sum:0:16}..."
                        echo "║     当前   sha256: ${current_sum:0:16}..."
                        echo "║     （可能是正常更新，继续推送）"
                        echo "╚══════════════════════════════════════════════╝"
                        echo ""
                    fi
                fi
            fi
        fi
    done
done < "$STDIN_TMP"

if [ "$block_l2" = true ]; then
    echo ""
    echo "╔══════════════════════════════════════════════╗"
    echo "║  🔴 修改了历史 L2 数据！                     ║"
    echo "║                                              ║"
    echo "║  L2 数据一旦当日采集完成并校核通过，         ║"
    echo "║  就再也不允许任何脚本修改。                   ║"
    echo "║                                              ║"
    echo "║  违规文件:                                    ║"
    echo -n "$violations"
    echo "║                                              ║"
    echo "║  如果必须修改，请联系 Lucian。               ║"
    echo "╚══════════════════════════════════════════════╝"
    echo ""
    exit 1
fi

# ---- Check 2: 禁止 Force Push ----
block_force_push=false
refs_checked=0

while read local_ref local_sha remote_ref remote_sha; do
    [ -z "$local_ref" ] && continue

    refs_checked=$((refs_checked + 1))

    # remote_sha 为全零 → 新分支，不阻止
    if [ "$remote_sha" = "0000000000000000000000000000000000000000" ]; then
        continue
    fi

    # 检查是否为 fast-forward：local_sha 必须是 remote_sha 的后代
    # 使用 merge-base 判断：remote_sha 是 local_sha 的祖先 = fast-forward
    merge_base=$(git merge-base "$local_sha" "$remote_sha" 2>/dev/null)
    if [ "$merge_base" != "$remote_sha" ]; then
        block_force_push=true
        echo ""
        echo "╔══════════════════════════════════════════════╗"
        echo "║  🔴 FORCE PUSH 被阻止                        ║"
        echo "║  dushe-daily-data 仓库禁止 force push         ║"
        echo "║                                              ║"
        echo "║  Ref: $remote_ref"
        echo "║  当前远程: ${remote_sha:0:8}"
        echo "║  你的本地: ${local_sha:0:8}"
        echo "║                                              ║"
        echo "║  修复步骤：                                   ║"
        echo "║    git pull --rebase                         ║"
        echo "║    git push                                  ║"
        echo "╚══════════════════════════════════════════════╝"
        echo ""
        break
    fi
done < "$STDIN_TMP"

if [ "$block_force_push" = true ]; then
    exit 1
fi

# 可选：推送前自动校验（非阻断，仅警告）
VALIDATE_SCRIPT="$WORKSPACE/scripts/check-freshness.py"
if [ -f "$VALIDATE_SCRIPT" ]; then
    echo ""
    echo "🔍 推送前数据校验中..."
    python3 "$VALIDATE_SCRIPT" --warn 2>/dev/null
    if [ $? -ne 0 ]; then
        echo ""
        echo "╔══════════════════════════════════════════════╗"
        echo "║  ⚠️  警告：数据校验未通过                     ║"
        echo "║  建议先修复后再推送。                         ║"
        echo "║  继续推送？按 Ctrl+C 取消，或等待 5 秒…       ║"
        echo "╚══════════════════════════════════════════════╝"
        echo ""
        sleep 5
    else
        echo "✅ 数据校验通过"
    fi
fi

exit 0
