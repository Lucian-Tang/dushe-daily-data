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

# ===== 安全复制函数：防止用空数据覆盖有效数据 =====
safe_cp() {
    local src="$1"
    local dst="$2"
    
    # 如果源文件不存在，跳过
    if [ ! -f "$src" ]; then
        log "[safe-cp] 源文件不存在: $src (跳过)"
        return 1
    fi
    
    # 检查源文件是否为空数组（只有 [] 的 JSON 文件大小为 2 字节）
    local src_size=$(stat -c%s "$src" 2>/dev/null || stat -f%z "$src" 2>/dev/null)
    
    # 如果目标文件已存在且有数据（>2字节）
    if [ -f "$dst" ]; then
        local dst_size=$(stat -c%s "$dst" 2>/dev/null || stat -f%z "$dst" 2>/dev/null)
        
        # 源为空（size=2 即 []），目标有正常数据 → 跳过覆盖
        if [ "$src_size" -le 3 ] && [ "$dst_size" -gt 3 ]; then
            local fname=$(basename "$src")
            log "[safe-cp] 🔴 阻止空数据覆盖: $fname (src=${src_size}B, dst=${dst_size}B, 保留现有数据)"
            return 1
        fi
    fi
    
    cp "$src" "$dst"
    return 0
}

# ---- Step 1: 毒舌点评 enrichment ----
# 加 --skip-if-enriched：若 daily 产物已有毒舌点评则跳过（06:00 冗余 cron 防止重复 LLM 调用）
log "[enrich] 开始毒舌点评 enrichment..."
if python3 "$SCRIPT_DIR/enrich_quotes.py" --date "$DATE_STR" --skip-if-enriched >> "$LOG_DIR/enrich_quotes.log" 2>&1; then
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

# ---- Step 1.6: 采集 GitHub Trending ----
log "[github] 采集 GitHub Trending..."
if python3 "$SCRIPT_DIR/fetch_github.py" 2>&1 | tee -a "$LOG_DIR/sync-github.log"; then
    log "[github] ✅ GitHub Trending 采集完成"
else
    log "[github] ⚠️ 采集失败（不阻塞后续流程）"
fi

# ---- Step 2: 复制数据到 Git 仓库（使用 safe_cp 防止空数据覆盖）----
log "[copy] 复制数据文件..."
cd "$WORKSPACE"
for f in "$WORKSPACE/data/raw_articles_"*.json; do [ -f "$f" ] && safe_cp "$f" .; done
for f in "$WORKSPACE/data/raw_dev_"*.json; do [ -f "$f" ] && safe_cp "$f" .; done
for f in "$WORKSPACE/data/raw_design_"*.json; do [ -f "$f" ] && safe_cp "$f" .; done
for f in "$WORKSPACE/data/raw_startup_"*.json; do [ -f "$f" ] && safe_cp "$f" .; done
for f in "$WORKSPACE/data/raw_clawhub_"*.json; do [ -f "$f" ] && safe_cp "$f" .; done
for f in "$WORKSPACE/data/github_trending_"*.json; do [ -f "$f" ] && safe_cp "$f" .; done
for f in "$WORKSPACE/data/clawhub_trending_"*.json; do [ -f "$f" ] && safe_cp "$f" .; done
# raw_social 已停用
# for f in "$WORKSPACE/data/raw_social_"*.json; do [ -f "$f" ] && safe_cp "$f" .; done

# ---- Step 2.5: 从 MD 报告生成标准化 JSON 文件 ----
log "[daily-json] 运行 generate_daily_json.py 生成标准化 JSON..."
if python3 "$SCRIPT_DIR/generate_daily_json.py" --date "$DATE_STR" 2>&1 | tee -a "$LOG_DIR/sync-github.log"; then
    log "[daily-json] ✅ JSON 文件生成完成"
else
    log "[daily-json] ⚠️ JSON 生成失败（检查是否有 MD 报告文件）"
fi

# ---- Step 2.5b: 将刚生成的 daily JSON 复制到 data/ 目录（供 normalize 处理）----
# 🔴 P0 修复（2026-06-03）：normalize_daily_data.py 以 data/ 为权威数据源，
#    需在此先同步根目录→data/，确保 data/ 有最新生成的数据。
#    使用 safe_cp 阻止空文件（生成失败时的 []）覆盖 data/ 有效数据。
log "[pre-sync] 将生成文件同步到 data/（供 normalize 处理）..."
for f in "$WORKSPACE"/*_daily_*.json; do
    [ -f "$f" ] || continue
    basename_f="$(basename "$f")"
    # 仅同步今日文件（按文件名中的日期判断）
    if echo "$basename_f" | grep -q "$DATE_STR"; then
        safe_cp "$f" "$WORKSPACE/data/$basename_f" || log "[pre-sync] 🛡️ $(basename "$f") → data/ 受保护（跳过空数据覆盖）"
    fi
done
log "[pre-sync] ✅ 生成文件已同步到 data/"

# ---- Step 2.6: 数据规范化（修复URL/日期格式/过滤旧数据，仅处理今日文件）----
# 🔴 normalize 以 data/ 目录文件为权威源（data/ 优先，根目录 fallback）
log "[normalize] 开始数据规范化（仅今日，data/ 先行）..."
if python3 "$SCRIPT_DIR/normalize_daily_data.py" --date "$DATE_STR" 2>&1 | tee -a "$LOG_DIR/sync-github.log"; then
    log "[normalize] ✅ 数据规范化完成"
else
    log "[normalize] ⚠️ 规范化失败（不阻塞后续流程）"
fi

# ---- Step 2.7: AI模型分类与聚合 ----
log "[ai-models] AI模型分类..."
if python3 "$SCRIPT_DIR/classify_ai_models.py" --date "$DATE_STR" 2>&1 | tee -a "$LOG_DIR/sync-github.log"; then
    log "[ai-models] AI模型日聚合..."
    python3 "$SCRIPT_DIR/generate_ai_models_daily.py" --date "$DATE_STR" 2>&1 | tee -a "$LOG_DIR/sync-github.log"
    log "[ai-models] AI模型周报..."
    python3 "$SCRIPT_DIR/generate_ai_models_weekly.py" --date "$DATE_STR" 2>&1 | tee -a "$LOG_DIR/sync-github.log"
    log "[ai-models] ✅ AI模型分类与聚合完成"
else
    log "[ai-models] ⚠️ AI模型分类失败（不阻塞后续流程）"
fi

# ---- Step 2.8: GitHub 周报 ----
log "[weekly-github] 生成 GitHub 周报..."
python3 "$SCRIPT_DIR/generate_weekly_github.py" --date "$DATE_STR" 2>&1 | tee -a "$LOG_DIR/sync-github.log" || log "[weekly-github] ⚠️ GitHub 周报生成失败"

# ---- Step 2.9: ClawHub 周报 ----
log "[weekly-clawhub] 生成 ClawHub 周报..."
python3 "$SCRIPT_DIR/generate_weekly_clawhub.py" --date "$DATE_STR" 2>&1 | tee -a "$LOG_DIR/sync-github.log" || log "[weekly-clawhub] ⚠️ ClawHub 周报生成失败"

# ---- Step 3: 使用 gen-index.py 生成 index.json（统一入口）----
# 🔴 P0 修复（2026-06-03）：gen-index.py 扫描 data/ 子目录生成索引，
#    index.json 中的文件路径使用 "data/" 前缀，如 "data/industry_daily_20260603.json"
#    确保 CDN 直接从 data/ 读数据，砍掉根目录→data/ 的双路径依赖
log "[index] 使用 gen-index.py 生成 index.json（data/ 权威源）..."
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
    'github': (None, 'github_daily'),
    'clawhub': (None, 'clawhub_daily'),
    'ai_models': (None, 'ai_models_daily'),
    'weekly_github': (None, 'weekly_github'),
    'weekly_clawhub': (None, 'weekly_clawhub'),
    'ai_models_weekly': (None, 'ai_models_weekly'),
}

latest = {}
history = {}
checksums = {}

# 🔴 P0 fix: scan data/ subdirectory first (authoritative source), fallback to root
DATA_PREFIX = 'data/'
scan_dirs = [('./data/', DATA_PREFIX), ('./', '')] if os.path.isdir('./data') else [('./', '')]

for section, (raw_prefix, daily_prefix) in section_map.items():
    if daily_prefix:
        for scan_dir, prefix in scan_dirs:
            if not os.path.isdir(scan_dir):
                continue
            daily_files = sorted(glob.glob(scan_dir + daily_prefix + '_*.json'))
            if daily_files:
                latest[section] = prefix + os.path.basename(daily_files[-1]) if prefix else daily_files[-1]
                history[section] = []
                for f in daily_files:
                    fname = prefix + os.path.basename(f) if prefix else f
                    history[section].append(fname)
                break  # data/ found, skip root

    if section not in latest and raw_prefix:
        raw_files = sorted(glob.glob(raw_prefix + '_*.json'))
        if raw_files:
            latest[section] = raw_files[-1]

for fname in glob.glob('data/*_daily_*.json') + glob.glob('*_daily_*.json') + glob.glob('raw_*.json'):
    if os.path.isfile(fname):
        with open(fname, 'rb') as f:
            checksums[fname] = hashlib.sha256(f.read()).hexdigest()

index = {
    'schemaVersion': '2.0',
    'updated': __import__('datetime').datetime.now().isoformat(),
    **latest,
    'history': history,
    'checksums': checksums
}

with open('index.json', 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

# Also write data/index.json without data/ prefix (for mini program)
if os.path.isdir('./data'):
    data_index = dict(index)
    for k in list(data_index.keys()):
        if k in section_map and isinstance(data_index[k], str) and data_index[k].startswith(DATA_PREFIX):
            data_index[k] = data_index[k][len(DATA_PREFIX):]
    with open('./data/index.json', 'w', encoding='utf-8') as f:
        json.dump(data_index, f, ensure_ascii=False, indent=2)

print(f'[index] generated: {len(latest)} sections')
"
fi

# ---- Step 3.5: 反向同步 data/ → root（确保根目录镜像 data/ 权威数据）----
# 🔴 P0 修复（2026-06-03）：方向反转！旧逻辑 root→data/ 会覆盖 data/ 有效数据。
#    新逻辑 data/→root：data/ 是权威源，root 是镜像。safe_cp 阻止空数据覆盖。
log "[data-sync] 反向同步 data/ → root（权威源→镜像）..."
bash "$SCRIPT_DIR/sync_to_data.sh" 2>&1 | tee -a "$LOG_DIR/sync-github.log"

# ---- Step 4: 数据新鲜度检查 ----
# 🔴 检查 data/ 目录数据（权威源），而非根目录
log "[qa] 数据新鲜度检查（data/ 权威源）..."
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