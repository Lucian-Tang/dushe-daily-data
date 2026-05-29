#!/bin/bash
# sync_github_pages.sh - 每日同步数据到 GitHub Pages（mini program 数据源）
# 新流程: enrichment → copy → push
# Cron: 25 4 * * * (早间) 和 40 11 * * * (午间)

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$WORKSPACE/logs"
DATE_STR=$(date +%Y%m%d)

mkdir -p "$LOG_DIR"

log() { echo "[$(date '+%H:%M:%S')] $1"; }

# ---- Step 1: 毒舌点评 enrichment ----
log "[enrich] 开始毒舌点评 enrichment..."
if python3 "$SCRIPT_DIR/enrich_quotes.py" --date "$DATE_STR" >> "$LOG_DIR/enrich_quotes.log" 2>&1; then
    log "[enrich] enrichment 完成"
else
    log "[enrich] enrichment 失败（不阻塞后续流程）"
fi

# ---- Step 1.5: 采集 ClawHub 技能市场数据 ----
log "[clawhub] 采集 ClawHub 技能市场..."
if command -v clawhub &>/dev/null; then
    python3 "$SCRIPT_DIR/fetch_clawhub.py" 2>&1 | tee -a "$LOG_DIR/sync-github.log"
else
    log "[clawhub] clawhub CLI 不可用，跳过"
fi

# ---- Step 2: 复制数据到 Git 仓库 ----
log "[copy] 复制数据文件..."
cd "$WORKSPACE"
cp "$WORKSPACE/data/raw_articles_"*.json . 2>/dev/null || log "[copy] raw_articles 无新文件"
cp "$WORKSPACE/data/raw_dev_"*.json . 2>/dev/null || log "[copy] raw_dev 无新文件"
cp "$WORKSPACE/data/raw_social_"*.json . 2>/dev/null || log "[copy] raw_social 无新文件"
cp "$WORKSPACE/data/raw_design_"*.json . 2>/dev/null || log "[copy] raw_design 无新文件"
cp "$WORKSPACE/data/raw_startup_"*.json . 2>/dev/null || log "[copy] raw_startup 无新文件"
cp "$WORKSPACE/data/raw_clawhub_"*.json . 2>/dev/null || log "[copy] raw_clawhub 无新文件"

# ---- Step 2.5: 从 MD 报告生成标准化 JSON 文件 ----
log "[daily-json] 运行 generate_daily_json.py 生成标准化 JSON..."
if python3 "$SCRIPT_DIR/generate_daily_json.py" --date "$DATE_STR" 2>&1 | tee -a "$LOG_DIR/sync-github.log"; then
    log "[daily-json] ✅ JSON 文件生成完成"
else
    log "[daily-json] ⚠️ JSON 生成失败（检查是否有 MD 报告文件）"
fi

# ---- Step 2.6: 数据规范化（修复URL/日期格式/过滤旧数据，仅处理今日文件）----
log "[normalize] 开始数据规范化（仅今日）..."
if python3 "$SCRIPT_DIR/normalize_daily_data.py" --date "$DATE_STR" 2>&1 | tee -a "$LOG_DIR/sync-github.log"; then
    log "[normalize] ✅ 数据规范化完成"
else
    log "[normalize] ⚠️ 规范化失败（不阻塞后续流程）"
fi

# ---- Step 3: 使用 gen-index.py 生成 index.json（统一入口）----
log "[index] 使用 gen-index.py 生成 index.json..."
cd "$WORKSPACE"
GEN_INDEX="$(dirname "$WORKSPACE")/scripts/gen-index.py"
if python3 "$GEN_INDEX" --path . --quiet 2>&1; then
    log "[index] index.json 生成完成"
else
    log "[index] gen-index.py 失败，回退到内联生成..."
    python3 -c "
import json, os, glob, hashlib

section_map = {
    'industry': ('raw_articles', 'industry_daily'),
    'dev': ('raw_dev', 'dev_daily'),
    'social': ('raw_social', None),
    'ai': ('raw_ai', 'ai_daily'),
    'startup': ('raw_startup', 'startup_daily'),
    'design': ('raw_design', 'design_daily'),
    'hf_daily': (None, 'hf_daily'),
}

latest = {}
history = {}
checksums = {}

for section, (raw_prefix, daily_prefix) in section_map.items():
    if daily_prefix:
        daily_files = sorted(glob.glob(daily_prefix + '_*.json'))
        if daily_files:
            latest[section] = daily_files[-1]
            for f in daily_files:
                date_str = f.replace(daily_prefix + '_', '').replace('.json', '').replace('_', '')
                if date_str not in history:
                    history[date_str] = {}
                if section not in history[date_str]:
                    history[date_str][section] = []
                history[date_str][section].append(f)
            continue
    
    if raw_prefix:
        raw_files = sorted(glob.glob(raw_prefix + '_*.json'))
        if raw_files:
            latest[section] = raw_files[-1]

compressed_history = {}
for date_str, sections in history.items():
    compressed_history[date_str] = sections

for fname in glob.glob('*_daily_*.json') + glob.glob('raw_*.json'):
    with open(fname, 'rb') as f:
        checksums[fname] = hashlib.sha256(f.read()).hexdigest()

index = {
    'schemaVersion': '2.0',
    'updated': __import__('datetime').datetime.now().isoformat(),
    **latest,
    'history': compressed_history,
    'checksums': checksums
}

with open('index.json', 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

print(f'[index] generated: {len(latest)} sections')
"
fi

# ---- Step 3.5: 同步输出文件到 data/ 目录（CDN 实际读取路径）----
log "[data-sync] 同步输出文件到 data/ 目录..."
bash "$SCRIPT_DIR/sync_to_data.sh" 2>&1 | tee -a "$LOG_DIR/sync-github.log"

# ---- Step 4: 数据新鲜度检查 ----
log "[qa] 数据新鲜度检查..."
if python3 "$SCRIPT_DIR/check-freshness.py" --warn 2>&1 | tee -a "$LOG_DIR/sync-github.log"; then
    log "[qa] ✅ 数据新鲜度检查通过"
else
    log "[qa] ⚠️ 数据新鲜度检查未通过（不阻塞）"
fi

# ---- Step 4.5: L2 不可变快照（sha256 校验和）----
log "[checksum] 生成 L2 快照校验和..."
bash "$SCRIPT_DIR/verify-l2-immutable.sh" 2>&1 | tee -a "$LOG_DIR/sync-github.log"
log "[checksum] ✅ L2 快照已追加"

# ---- Step 5: Git commit & push to staging ----
log "[git] commit & push to staging..."
cd "$WORKSPACE"
# 切到 staging 分支（如已在 staging 则跳过）
git checkout staging 2>/dev/null || git checkout -b staging
git add -u --ignore-removal .
git add .
git commit -m "📊 $(date +%Y-%m-%d) 日报数据自动推送" || log "[git] 无变更，跳过 commit"
git push origin staging 2>&1
PUSH_EXIT=$?
if [ $PUSH_EXIT -ne 0 ]; then
    log "[git] 🔴 push 失败 (exit=$PUSH_EXIT)，pre-push hook 可能已拦截"
    exit $PUSH_EXIT
fi

# ---- Step 6: 自动 promote staging → main ----
log "[promote] 自动 promote staging → main..."
if bash "$SCRIPT_DIR/promote-staging.sh" 2>&1 | tee -a "$LOG_DIR/sync-github.log"; then
    log "[promote] ✅ promote 成功"
else
    log "[promote] ⚠️ promote 失败（不阻塞，staging 已更新）"
fi

log "[done] ✅ 数据已推送至 staging + promote 至 main"
log "[done] sync OK | $(date)"