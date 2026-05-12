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

# ---- Step 3: 生成 index.json（完整版，包含所有板块 + 合并文件）----
log "[index] 生成完整 index.json..."
python3 -c "
import json, os, glob, hashlib

# 检测所有可用板块文件
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
today_files = {}  # 今天的日报文件，用于生成合并文件

for section, (raw_prefix, daily_prefix) in section_map.items():
    # 优先使用 daily 文件
    if daily_prefix:
        daily_files = sorted(glob.glob(daily_prefix + '_*.json'))
        if daily_files:
            latest[section] = daily_files[-1]
            # 收集今天的文件
            for f in daily_files:
                date_str = f.replace(daily_prefix + '_', '').replace('.json', '').replace('_', '')
                if date_str not in history:
                    history[date_str] = {}
                if section not in history[date_str]:
                    history[date_str][section] = []
                history[date_str][section].append(f)
            continue
    
    # fallback 到 raw 文件
    if raw_prefix:
        raw_files = sorted(glob.glob(raw_prefix + '_*.json'))
        if raw_files:
            latest[section] = raw_files[-1]

# 压缩 history 为简洁格式
compressed_history = {}
for date_str, sections in history.items():
    compressed_history[date_str] = sections

# 生成 checksums
for fname in glob.glob('*_daily_*.json') + glob.glob('raw_*.json'):
    with open(fname, 'rb') as f:
        checksums[fname] = hashlib.sha256(f.read()).hexdigest()

# 生成合并文件（combined_all_YYYYMMDD.json）
today = os.path.basename(__file__) if '__file__' in dir() else ''
today_str = os.environ.get('DATE_STR', '') or ''

index = {
    'schemaVersion': '2.0',
    'updated': __import__('datetime').datetime.now().isoformat(),
    **latest,
    'history': compressed_history,
    'checksums': checksums
}

# 尝试生成合并文件
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
        # 从文件名提取日期
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

# ---- Step 4: Git commit & push ----
log "[git] commit & push..."
git add -A
git commit -m "📊 $(date +%Y-%m-%d) 日报数据自动推送" || log "[git] 无变更，跳过 commit"
git push origin main 2>&1 | tail -1

log "[done] sync OK | $(date)"
