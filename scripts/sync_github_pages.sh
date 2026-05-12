#!/bin/bash
# sync_github_pages.sh - 每日同步数据到 GitHub Pages（mini program 数据源）
# 新流程: enrichment → copy → push
# Cron: 30 3 * * * 和 40 11 * * *

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

# ---- Step 2: 复制数据到 Git 仓库 ----
log "[copy] 复制数据文件..."
cd "$WORKSPACE/dushe-daily-data"
cp "$WORKSPACE/data/raw_articles_"*.json . 2>/dev/null || log "[copy] raw_articles 无新文件"
cp "$WORKSPACE/data/raw_dev_"*.json . 2>/dev/null || log "[copy] raw_dev 无新文件"
cp "$WORKSPACE/data/raw_social_"*.json . 2>/dev/null || log "[copy] raw_social 无新文件"
cp "$WORKSPACE/data/raw_design_"*.json . 2>/dev/null || log "[copy] raw_design 无新文件"
cp "$WORKSPACE/data/raw_startup_"*.json . 2>/dev/null || log "[copy] raw_startup 无新文件"

# ---- Step 3: 使用 gen-index.py 生成 index.json（统一入口）----
log "[index] 使用 gen-index.py 生成 index.json..."
cd "$WORKSPACE/dushe-daily-data"
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

# 生成合并文件
try:
    combined = {}
    for section in ['industry', 'dev', 'ai', 'startup', 'design']:
        fname = latest.get(section, '')
        if fname and os.path.exists(fname):
            with open(fname) as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    combined[section] = data
    
    if combined:
        import re
        date_match = None
        for fname in latest.values():
            m = re.search(r'_(\d{8})\.json$', str(fname))
            if m:
                date_match = m.group(1)
                break
        
        if date_match:
            combined_fname = f'combined_all_{date_match}.json'
            with open(combined_fname, 'w', encoding='utf-8') as f:
                json.dump(combined, f, ensure_ascii=False, indent=2)
            index['combined'] = {date_match: combined_fname}
            print(f'[combined] created {combined_fname} with {sum(len(v) for v in combined.values())} items')
except Exception as e:
    print(f'[combined] generation failed: {e}')

with open('index.json', 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

print(f'[index] generated: {len(latest)} sections, {len(combined)} combined')
"
fi

# ---- Step 4: Git commit & push ----
# ---- Step 3.5: 数据新鲜度检查 ----
log "[qa] 数据新鲜度检查..."
python3 "$SCRIPT_DIR/check-freshness.py" --warn 2>&1 | tee -a "$LOG_DIR/sync-github.log"
log "[qa] 数据新鲜度检查完成（仅警告，不阻塞）"
log "[git] commit & push..."
git add -A
git commit -m "📊 $(date +%Y-%m-%d) 日报数据自动推送" || log "[git] 无变更，跳过 commit"
git push origin main 2>&1 | tail -1

log "[done] sync OK | $(date)"

# ---- Step 2.5: 数据新鲜度检查 ----
log "[qa] 数据新鲜度检查..."
python3 -c "
import json, os, sys, glob, re
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
TODAY = datetime.now(TZ).strftime('%Y-%m-%d')

os.chdir('$WORKSPACE/dushe-daily-data')
errors = []
for section, fname in [('industry','industry_daily'), ('dev','dev_daily'), ('ai','ai_daily'),
                        ('startup','startup_daily'), ('design','design_daily')]:
    latest = None
    for f in sorted(glob.glob(f'{fname}_*.json'), reverse=True):
        latest = f; break
    if not latest:
        errors.append(f'[STALE] {section}: 无可用文件')
        continue
    with open(latest) as fh:
        items = json.load(fh)
    today_items = [it for it in items if it.get('published','').startswith(TODAY)]
    if not today_items:
        errors.append(f'[NO_TODAY] {section}: {len(items)}条，0条今日（最新: {items[0].get(\"published\",\"?\") if items else \"空\"}）')
    else:
        print(f'  ✅ {section}: {len(today_items)}/{len(items)} 条是今天的')

if errors:
    print('[QA FAILED]')
    for e in errors: print(f'  ❌ {e}')
    sys.exit(1)
else:
    print('[QA PASS] 所有板块都有今日数据')
" 2>&1 | tee -a "$LOG_DIR/sync-github.log"

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    log "[qa] ❌ 数据新鲜度检查不通过，但继续执行（不阻塞）"
else
    log "[qa] ✅ 数据新鲜度检查通过"
fi
