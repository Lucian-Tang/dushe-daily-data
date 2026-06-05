#!/bin/bash
# sync_rankings_only.sh - 轻量版榜单同步（不碰板块日报和毒舌 enrich）
# 只刷新 GitHub Trending / ClawHub / AI Models 榜单
# Cron: 06:00 / 12:00 / 18:00
#
# 与 sync_github_pages.sh 的区别：
#   ❌ 不跑 enrich_quotes.py（毒舌点评）
#   ❌ 不跑 generate_daily_json.py（6板块日报 JSON）
#   ❌ 不跑 normalize_daily_data.py（数据规范化）
#   ❌ 不跑 check-freshness.py（新鲜度检查）
#   ❌ 不跑 verify-l2-immutable.sh（L2 快照）
#   ✅ 只跑榜单采集 + 分类 + 聚合 + 周报 + index.json + git push

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$WORKSPACE/logs"
DATE_STR=$(date +%Y%m%d)

mkdir -p "$LOG_DIR"

log() { echo "[$(date '+%H:%M:%S')] $1"; }

# ===== 安全复制函数：防止用空数据覆盖有效数据 =====
safe_cp() {
    local src="$1"
    local dst="$2"
    
    if [ ! -f "$src" ]; then
        log "[safe-cp] 源文件不存在: $src (跳过)"
        return 1
    fi
    
    local src_size
    src_size=$(stat -c%s "$src" 2>/dev/null || stat -f%z "$src" 2>/dev/null)
    
    if [ -f "$dst" ]; then
        local dst_size
        dst_size=$(stat -c%s "$dst" 2>/dev/null || stat -f%z "$dst" 2>/dev/null)
        
        # 源为空（size<=3），目标有正常数据 → 跳过覆盖
        if [ "$src_size" -le 3 ] && [ "$dst_size" -gt 3 ]; then
            local fname
            fname=$(basename "$src")
            log "[safe-cp] 🔴 阻止空数据覆盖: $fname (src=${src_size}B, dst=${dst_size}B, 保留现有数据)"
            return 1
        fi
    fi
    
    cp "$src" "$dst"
    return 0
}

# ====================================================================
# Step 1: 采集 GitHub Trending
# ====================================================================
log "[github] 采集 GitHub Trending..."
if python3 "$SCRIPT_DIR/fetch_github.py" 2>&1 | tee -a "$LOG_DIR/sync-rankings.log"; then
    log "[github] ✅ GitHub Trending 采集完成"
else
    log "[github] ⚠️ 采集失败（不阻塞后续流程）"
fi

# ====================================================================
# Step 2: 采集 ClawHub 技能
# ====================================================================
log "[clawhub] 采集 ClawHub 技能市场..."
if python3 "$SCRIPT_DIR/fetch_clawhub.py" 2>&1 | tee -a "$LOG_DIR/sync-rankings.log"; then
    log "[clawhub] ✅ ClawHub 采集完成"
else
    log "[clawhub] ⚠️ 采集失败（不阻塞后续流程）"
fi

# ====================================================================
# Step 3: AI 模型分类
# ====================================================================
log "[ai-models] AI模型分类..."
if python3 "$SCRIPT_DIR/classify_ai_models.py" --date "$DATE_STR" 2>&1 | tee -a "$LOG_DIR/sync-rankings.log"; then
    log "[ai-models] ✅ AI模型分类完成"
else
    log "[ai-models] ⚠️ 分类失败（不阻塞后续流程）"
fi

# ====================================================================
# Step 4: AI 模型日聚合
# ====================================================================
log "[ai-models-daily] AI模型日聚合..."
if python3 "$SCRIPT_DIR/generate_ai_models_daily.py" --date "$DATE_STR" 2>&1 | tee -a "$LOG_DIR/sync-rankings.log"; then
    log "[ai-models-daily] ✅ 日聚合完成"
else
    log "[ai-models-daily] ⚠️ 日聚合失败（不阻塞后续流程）"
fi

# ====================================================================
# Step 5: AI 模型周报
# ====================================================================
log "[ai-models-weekly] AI模型周报..."
python3 "$SCRIPT_DIR/generate_ai_models_weekly.py" --date "$DATE_STR" 2>&1 | tee -a "$LOG_DIR/sync-rankings.log" || \
    log "[ai-models-weekly] ⚠️ 周报生成失败（不阻塞）"

# ====================================================================
# Step 6: GitHub 周报
# ====================================================================
log "[weekly-github] 生成 GitHub 周报..."
python3 "$SCRIPT_DIR/generate_weekly_github.py" --date "$DATE_STR" 2>&1 | tee -a "$LOG_DIR/sync-rankings.log" || \
    log "[weekly-github] ⚠️ GitHub 周报生成失败（不阻塞）"

# ====================================================================
# Step 7: ClawHub 周报
# ====================================================================
log "[weekly-clawhub] 生成 ClawHub 周报..."
python3 "$SCRIPT_DIR/generate_weekly_clawhub.py" --date "$DATE_STR" 2>&1 | tee -a "$LOG_DIR/sync-rankings.log" || \
    log "[weekly-clawhub] ⚠️ ClawHub 周报生成失败（不阻塞）"

# ====================================================================
# Step 8: 把 data/ 目录中的排名 JSON 复制到根目录
# ====================================================================
log "[copy] 复制榜单数据 data/ → root（safe_cp 保护）..."
cd "$WORKSPACE"
for prefix in github_trending_ clawhub_trending_ ai_models_classified_ ai_models_daily_ ai_models_weekly_ weekly_github_ weekly_clawhub_; do
    for f in "$WORKSPACE/data/${prefix}"*.json; do
        [ -f "$f" ] || continue
        safe_cp "$f" "$(basename "$f")" || true
    done
done
log "[copy] ✅ 榜单数据已同步到根目录"

# ====================================================================
# Step 9a: 从 trending 文件生成 github_daily / clawhub_daily（passthrough 复制）
# 注：generate_daily_json.py 的 passthrough 逻辑直接读 trending 文件写 daily 文件
# 此处用同样的方式确保 index.json 的 key 能指向正确的文件
# ====================================================================
log "[passthrough] 生成 github_daily / clawhub_daily..."
cd "$WORKSPACE"
python3 -c "
import json
import glob
import sys

DATE_STR = '$DATE_STR'

# 从 trending 文件生成 daily 文件（passthrough 复制）
passthrough_map = {
    'github': ('github_trending_', 'github_daily_'),
    'clawhub': ('clawhub_trending_', 'clawhub_daily_'),
}

for section, (src_prefix, dst_prefix) in passthrough_map.items():
    src_path = f'data/{src_prefix}{DATE_STR}.json'
    if not __import__('os').path.exists(src_path):
        # fallback to root
        src_path = f'{src_prefix}{DATE_STR}.json'
    
    if __import__('os').path.exists(src_path):
        with open(src_path) as f:
            data = json.load(f)
        dst_path = f'{dst_prefix}{DATE_STR}.json'
        with open(dst_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f'[passthrough] {section}: {src_path} \u2192 {dst_path} ({len(data)} items)')
    else:
        print(f'[passthrough] {section}: \u274c source not found ({src_prefix}{DATE_STR}.json), skip')
"
log "[passthrough] \u2705 daily 文件生成完成"

# ====================================================================
# Step 9b: 更新 index.json（只更新榜单 key，保留主板块不变）
# ====================================================================
log "[index] 更新 index.json（仅榜单 key）..."
cd "$WORKSPACE"
python3 -c "
import json, os, glob, hashlib
from datetime import datetime

# 读取现有 index.json
index = {}
if os.path.exists('index.json'):
    with open('index.json', encoding='utf-8') as f:
        try:
            index = json.load(f)
        except Exception:
            index = {}

# 保留已有的 schemaVersion
if 'schemaVersion' not in index:
    index['schemaVersion'] = '2.0'

# 扫描并只更新榜单相关的 key（保留 industry/dev/ai/startup/design 等主板块 key 不变）
RANKING_KEYS = {
    'github': 'github_daily',
    'clawhub': 'clawhub_daily',
    'ai_models': 'ai_models_daily',
    'weekly_github': 'weekly_github',
    'weekly_clawhub': 'weekly_clawhub',
    'ai_models_weekly': 'ai_models_weekly',
}

for key, prefix in RANKING_KEYS.items():
    # 扫描根目录
    files = sorted(glob.glob(f'{prefix}_*.json'))
    if files:
        index[key] = files[-1]
        log_msg = f'[index] {key} → {files[-1]}'
    else:
        log_msg = f'[index] {key} → (未找到文件，保留旧值)'
    print(log_msg)

# 更新 timestamp
index['updated'] = datetime.now().isoformat()

# 更新榜单文件的 checksums（不影响其他 checksum）
if 'checksums' not in index:
    index['checksums'] = {}
for fname in glob.glob('github_daily_*.json') + glob.glob('clawhub_daily_*.json') + \
                 glob.glob('ai_models_daily_*.json') + glob.glob('weekly_github_*.json') + \
                 glob.glob('weekly_clawhub_*.json') + glob.glob('ai_models_weekly_*.json'):
    if os.path.isfile(fname):
        with open(fname, 'rb') as f:
            index['checksums'][fname] = hashlib.sha256(f.read()).hexdigest()

# 写回 index.json
with open('index.json', 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

# 同时生成 data/index.json（无 data/ 前缀版，供小程序使用）
if os.path.isdir('./data'):
    data_index = dict(index)
    for k in list(data_index.keys()):
        if isinstance(data_index[k], str) and data_index[k].startswith('data/'):
            data_index[k] = data_index[k][len('data/'):]
    if 'checksums' in data_index:
        data_index['checksums'] = {
            k[len('data/'):] if k.startswith('data/') else k: v
            for k, v in data_index['checksums'].items()
        }
    with open('./data/index.json', 'w', encoding='utf-8') as f:
        json.dump(data_index, f, ensure_ascii=False, indent=2)
    print('[index] data/index.json 已更新（无前缀版）')

print(f'[index] ✅ index.json 已更新 ({len(RANKING_KEYS)} 个榜单 key)')
"

# ====================================================================
# Step 10: 同步榜单数据到 data/ 目录
# ====================================================================
log "[sync-data] 同步榜单文件到 data/..."
cd "$WORKSPACE"
for prefix in github_daily_ clawhub_daily_ ai_models_daily_ ai_models_weekly_ weekly_github_ weekly_clawhub_; do
    for f in ${prefix}*.json; do
        [ -f "$f" ] || continue
        safe_cp "$f" "data/$f" || true
    done
done
log "[sync-data] ✅ 榜单文件已同步到 data/"

# ====================================================================
# Step 11: Git commit & push to staging + promote
# ====================================================================
log "[git] commit & push to staging..."
cd "$WORKSPACE"

# 切到 staging 分支
git checkout staging 2>/dev/null || git checkout -b staging
git add -u --ignore-removal .
git add .
git commit -m "🏷️ $(date +%Y-%m-%d) 榜单数据自动刷新（轻量版）" || log "[git] 无变更，跳过 commit"
git push origin staging 2>&1
PUSH_EXIT=$?
if [ $PUSH_EXIT -ne 0 ]; then
    log "[git] 🔴 push 失败 (exit=$PUSH_EXIT)，pre-push hook 可能已拦截"
    exit $PUSH_EXIT
fi

log "[promote] 自动 promote staging → main..."
if bash "$SCRIPT_DIR/promote-staging.sh" 2>&1 | tee -a "$LOG_DIR/sync-rankings.log"; then
    log "[promote] ✅ promote 成功"
else
    log "[promote] ⚠️ promote 失败（不阻塞，staging 已更新）"
fi

log "[done] ✅ 榜单刷新完成 | $(date)"
