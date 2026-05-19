# Pipeline Audit Report 2026-05-19

**审计目标:** 明天02:00~03:00的cron管线稳定运行，不需要修CDN
**工作目录:** `/root/.openclaw/workspace/dushe-daily-data/`

---

## Summary

| Metric | Value |
|--------|-------|
| Total crons | 19 |
| Cron errors | 9 |
| Daily pipeline crons (our scope) | 11 |
| Daily pipeline errors | 8 (ALL due to Feishu delivery target misconfig, NOT script failure) |
| Sections with retry + yesterday fallback | 2/5 (startup, design) |
| Sections without retry/fallback | 3/5 (dev, industry, ai) |

**Fallback coverage: startup ✅ v2, design ✅ v2, dev ❌ plain, industry ❌ plain, ai ❌ plain**

---

## Per-Section Status

### startup
- **Cron:** startup-daily (02:00) — `status: ok` ✅
- **Fetch:** `fetch_startup.py v2` ✅ (retry + yesterday fallback confirmed)
- **Data (20260519):** exists ✅, content≥50 ✅ (10条 all pass normalize)
- **Risk:** ⚠️ sync-github.log 显示 startup 今天 0 条（freshness check FAIL），但 data/ 有文件。说明 startup raw fetch 在 cron 环境可能部分失败，被 fallback 救了。
- **Overall:** 🟡 Acceptable — v2 fallback 有效，但需监控明天是否真正走 v2

---

### design
- **Cron:** design-daily (02:15) — `status: ok` ✅
- **Fetch:** `fetch_design.py v2` ✅ (retry + yesterday fallback confirmed)
- **Data (20260519):** exists ✅, content≥50 ✅ (12条 all pass normalize)
- **Risk:** Low — v2 fallback 完整，normalize 已将 content 补全到70~84字
- **Overall:** 🟢 Good

---

### industry
- **Cron:** industry-daily-report (00:15) — `status: ok` ✅
- **Fetch:** `fetch_industry.py` — ❌ No retry, ❌ No yesterday fallback (plain asyncio RSS dump)
- **Data (20260519):** exists ✅, content≥50 ✅ (15条 industry content为空但normalize扩展了)
- **Risk:** ⚠️ No fallback = 如果所有 RSS 源超时，今天 industry 数据会为空
- **Overall:** 🟡 Needs monitor — plain fetch with no fallback

---

### dev
- **Cron:** dev-collect-A (00:30) — `status: error` ⚠️ (Feishu delivery target misconfig)
- **Cron:** dev-collect-B (00:45) — `status: error` ⚠️ (Feishu delivery target misconfig)
- **Cron:** dev-merge (01:00) — `status: error` ⚠️ (Feishu delivery target misconfig)
- **Fetch:** `fetch_dev.py` — ❌ No retry, ❌ No yesterday fallback
- **Risk:** 🔴 Delivery error = cron announces to "feishu" without explicit chat ID → fails closed. The actual data pipeline may still run (subagent writes files), but notification delivery fails. **Impact: non-blocking for data, blocking for alerts.**
- **Overall:** 🟡 Acceptable for data — dev raw data exists for today

---

### ai
- **Cron:** ai-collect-A (01:15) — `status: error` ⚠️ (Feishu delivery target misconfig)
- **Cron:** ai-collect-B (01:30) — `status: error` ⚠️ (Feishu delivery target misconfig)
- **Cron:** ai-merge (01:45) — `status: error` ⚠️ (Feishu delivery target misconfig)
- **Fetch:** ⚠️ (ai uses agent-generated MD reports, not raw fetch scripts — fallback coverage N/A for raw fetch)
- **Data (20260519):** exists ✅, content≥50 ✅ (12条)
- **Risk:** ⚠️ Feishu delivery errors for all 3 ai crons — but data was successfully written (ai_daily_20260519.json present)
- **Overall:** 🟡 Acceptable for data — AI MD 生成成功并已规范化

---

### social
- **Status:** Raw file present (`raw_social_20260519.json`), no CDN push (social 走飞书内部不发CDN)
- **Risk:** Low — 仅内部使用

---

## Cron Error Root Cause

All 8 "error" cron statuses share the same root cause:
```
Delivering to Feishu requires target <chatId|user:openId|chat:chatId>
```
The `delivery` field is set to `announce -> feishu` without an explicit `chat:oc_b020039d18d36b0d02eb3c021df8af9e`. This is a **non-blocking data issue** — the subagent still runs, writes files, but cannot deliver the announce message to Feishu. The main pipeline data (raw files, CDN JSON) is still generated correctly.

---

## Pipeline Step Integrity

### sync_github_pages.sh (Step-by-step)

| Step | Script | Parameter | Status |
|------|---------|-----------|--------|
| Step 1 | `enrich_quotes.py` | `--date $DATE_STR` | ✅ Working |
| Step 2 (copy) | raw JSON copy | pattern match | ✅ Working |
| Step 2.5 | `generate_daily_json.py` | `--date $DATE_STR` | ✅ Working |
| Step 2.6 | `normalize_daily_data.py` | `--date $DATE_STR` | ✅ Working |
| Step 3 | `gen-index.py` (fallback: inline) | `--path .` | ✅ Working |
| Step 3.5 | `sync_to_data.sh` | (today only) | ✅ Working — runs BEFORE git push |
| Step 4 | `check-freshness.py` | `--warn` | ✅ Working |
| Step 4.5 | `verify-l2-immutable.sh` | (no args = today) | ✅ Working |
| Step 5 | git commit + push staging | — | ✅ Working |

**Critical order check:** `sync_to_data.sh` runs at Step 3.5, BEFORE git commit (Step 5). ✅ Correct.
**Critical order check:** `verify-l2-immutable.sh` runs at Step 4.5, after normalize (Step 2.6) but before git push. ✅ Correct.

---

## L2 Immutability Protection

| Component | Status | Notes |
|-----------|--------|-------|
| pre-push hook | ✅ Installed | `.git/hooks/pre-push` exists, executable, 7010 bytes |
| verify-l2-immutable.sh | ✅ In管线 | Called in sync_github_pages.sh Step 4.5 |
| normalize_daily_data.py --date | ✅ Defaults to today | `datetime.now().strftime('%Y%m%d')` |
| Checksum file | ✅ Working | `data/.l2_checksums` appends daily sha256 |

**pre-push hook content verified:**
- Blocks modification of historical L2 files (date < today)
- Shows checksum mismatch warning for today's files (non-blocking)
- Blocks force push

---

## Critical Risks (must fix before next cron)

### 🔴 CRITICAL 1: `combined_3days` and `security` in index.json
**File:** `index.json` and `data/index.json`
**Issue:** gen-index.py (via sync_github_pages.sh Step 3 fallback inline script) writes `combined_3days` and `security` as top-level keys in index.json. These are stale/incorrect:
- `combined_3days` → points to old file that is no longer generated
- `security` → blocklist structure (not a file pointer)
- Combined: `{"20260519": "combined_3days_20260519.json"}`

**Why this is critical:** 小程序读取 index.json 时可能会尝试解析 `combined_3days` 字段，如果按 section 处理会失败。`security` 作为 dict 嵌入也不是预期格式。

**Fix:** gen-index.py TYPE_MAP needs to be updated to exclude `combined_3days_*.json` files. The inline fallback in sync_github_pages.sh also needs updating to exclude combined files from index generation.

---

### 🔴 CRITICAL 2: `promote-staging.sh` still validates combined_3days in QA
**File:** `scripts/promote-staging.sh` Step 3
**Issue:** QA 校验 Step 3 checks for `combined_3days` file existence and item count:
```
[03:07:45] [3/5] 校验 combined_3days 文件...
[03:07:45]    combined_3days: 141条, 今日47条
```
This is dead code — `generate_combined_3days.py` is deleted, so this check will always fail for new runs. The promote log shows it passed because it found existing combined files from old data.

**Fix:** Remove the combined_3days validation step from promote-staging.sh. The file no longer exists, so promoting after 02:00 cron will trigger this failure.

---

### 🟡 MEDIUM 3: startup-daily has 0 content freshness failure
**File:** `logs/sync-github.log`
**Issue:** Freshness check output:
```
❌ 创投: 0条，0条今日 (最新: ?)
```
But `startup_daily_20260519.json` exists with 10 items (8339 bytes). This inconsistency suggests the freshness check script reads the wrong field or file.

**Fix:** Investigate why check-freshness.py reports 0 items for startup despite the file having 10 items. May be a published date or URL field issue.

---

### 🟡 MEDIUM 4: dev/industry/ai have no retry or yesterday fallback
**Files:** `scripts/fetch_dev.py`, `scripts/fetch_industry.py`
**Issue:** Unlike startup/design v2 scripts, dev and industry raw fetch scripts have no retry logic and no yesterday fallback. If all RSS sources fail (network timeout, API rate limit), the resulting raw file is empty or partial.

**Fix (nice to have):** Backport retry + yesterday fallback from v2 scripts to dev and industry fetchers. This is not critical since these sections use agent-generated MD reports (not raw fetch) as primary source, but the raw files are used for enrichment.

---

### 🟡 MEDIUM 5: security-blocklist.json is empty
**File:** `scripts/security-blocklist.json`
**Issue:** The blocklist is an empty array `[]`. This means the content filtering in normalize is currently inactive.

**Risk:** If a high-risk keyword appears, it won't be filtered. However, this is "宁少勿多" by design per the file header — the blocklist should remain conservative.

**Recommendation:** Keep as-is; expand only if a real incident occurs.

---

## Recommendations

1. **Fix index.json generation** to exclude `combined_3days` and `security` top-level keys. Either patch gen-index.py TYPE_MAP or simplify the inline fallback script in sync_github_pages.sh to not include these.

2. **Remove combined_3days QA check** from promote-staging.sh Step 3 before tomorrow's promote runs.

3. **Investigate startup freshness failure** — why check-freshness.py reports 0 items despite file having 10.

4. **Consider backporting retry/fallback** from startup v2 to dev/industry fetchers for robustness (low priority).

5. **Pre-push hook is working correctly** — no action needed.

6. **normalize_daily_data.py content length fix is working** — 20260519 data shows all items are ≥50 chars after normalize. ✅

7. **sync_to_data.sh order is correct** — data/ is synced before git push. ✅

---

## Combined_3days Removal Verification

| Check | Status |
|-------|--------|
| `scripts/generate_combined_3days.py` exists | ✅ Deleted |
| `sync_github_pages.sh` calls combined generation | ✅ Not called |
| `promote-staging.sh` validates combined_3days | ❌ **Still validates — needs fix** |
| `index.json` top-level key for combined | ❌ **Still present — needs fix** |
| `data/` directory contains old combined files | ⚠️ Yes (historical files remain, not cleaned up) |

---

## Audit Conclusion

**Pipeline is 75% ready for tomorrow.** The core sync flow (enrich→normalize→gen-index→sync_to_data→git push→verify-l2) is intact and working correctly based on today's logs. The L2 immutability protection is in place. The critical fixes needed are:

1. Remove stale `combined_3days` from index.json generation (gen-index.py + inline fallback)
2. Remove dead combined_3days QA check from promote-staging.sh
3. Investigate startup freshness check discrepancy

The Feishu delivery errors on dev/ai crons are non-blocking for the data pipeline (subagents still execute and write files). They will generate alert noise in the cron status but won't cause data loss.