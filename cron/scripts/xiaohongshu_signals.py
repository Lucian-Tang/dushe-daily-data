#!/usr/bin/env python3
"""
xiaohongshu_signals.py - 小红书信号采集器 (XHS Signals Collector)
通过 xiaohongshu-cli (jackwener/xiaohongshu-cli) 采集只读信号。

功能：
  - 搜索热门笔记（关键词：AI/创业/工具/开源）
  - 分类热门（美食/穿搭/旅行/科技）
  - 推荐 Feed

Cookie 管理：
  - 从 ~/.xiaohongshu-cli/cookies.json 读取
  - TTL 7 天，需人工刷新
  - 使用环境变量 XHS_BINARY 指定 xhs CLI 路径

用法：
  python3 xiaohongshu_signals.py [--keywords "AI,LLM,创业"] [--limit 20]
"""

import json
import os
import subprocess
import sys
import re
from datetime import datetime, timezone
from pathlib import Path

# ============ Config ============
APP_TOKEN = "S8mlbvHk6a4a6ss46klcw5CSnCY"
TABLE_ID = "tblIiWi9t04d0u5D"
DATA_DIR = Path("/root/.openclaw/workspace/data/opportunities/xiaohongshu")
LOG_FILE = Path(f"/root/.openclaw/workspace/logs/cron-exec-{datetime.now().strftime('%Y-%m-%d')}.jsonl")

# xhs CLI binary
XHS_BINARY = os.environ.get("XHS_BINARY", "/root/.openclaw/workspace/venv-xhs/bin/xhs")

# 搜索关键词
DEFAULT_KEYWORDS = [
    "AI", "LLM", "大模型", "GPT", "创业", "工具", "开源",
    "科技", "产品", "效率", "自动化", "Agent", "SaaS"
]

# 热门分类
HOT_CATEGORIES = ["food", "fashion", "travel", "digital"]  # 排除敏感分类


# ============ Logging ============
def log_jsonl(status, stage="full", duration_ms=0, error=""):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cron_name": "xiaohongshu-signals",
        "stage": stage,
        "status": status,
        "duration_ms": duration_ms
    }
    if error:
        entry["error"] = error
    print(json.dumps(entry))


# ============ Cookie Check ============
def check_cookie_valid():
    """检查 Cookie 是否存在且未过期（7天 TTL）。"""
    cookie_path = Path.home() / ".xiaohongshu-cli" / "cookies.json"
    if not cookie_path.exists():
        return False, "cookies.json not found"
    try:
        data = json.loads(cookie_path.read_text())
        if "a1" not in data:
            return False, "No a1 cookie"
        saved_at = data.get("saved_at", 0)
        import time
        age_days = (time.time() - saved_at) / 86400
        if age_days > 7:
            return False, f"Cookie expired ({age_days:.1f} days old)"
        return True, f"Cookie valid ({age_days:.1f} days old)"
    except Exception as e:
        return False, f"Cookie read error: {e}"


# ============ XHS CLI Wrappers ============
def run_xhs(args, timeout=60):
    """运行 xhs CLI，返回 YAML/JSON 输出。"""
    cmd = [XHS_BINARY] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "OUTPUT": "yaml"}
        )
        if result.returncode != 0:
            return None, f"xhs exit {result.returncode}: {result.stderr[:200]}"
        return result.stdout, None
    except subprocess.TimeoutExpired:
        return None, "xhs timeout"
    except Exception as e:
        return None, str(e)


def parse_xhs_output(stdout):
    """解析 xhs 的 YAML/JSON 输出，提取 notes 列表。"""
    try:
        # Try YAML first (default non-TTY output)
        import yaml
        data = yaml.safe_load(stdout)
    except Exception:
        try:
            # Fallback to JSON
            data = json.loads(stdout)
        except Exception:
            return None, f"Failed to parse output: {stdout[:200]}"

    if isinstance(data, dict):
        if not data.get("ok", False):
            return None, f"xhs returned ok=false: {data.get('error', {})}"
        # Unwrap envelope
        data = data.get("data", data)
    elif not isinstance(data, list):
        return None, f"Unexpected data structure: {type(data)}"

    return data, None


# ============ Fetch Functions ============
def fetch_keyword_search(keyword, limit=10, sort="popular"):
    """搜索关键词热门笔记。"""
    stdout, err = run_xhs(["search", keyword, "--sort", sort, "--page", "1", "--json"])
    if err:
        return [], err
    data, parse_err = parse_xhs_output(stdout)
    if parse_err:
        return [], parse_err

    notes = data if isinstance(data, list) else data.get("items", data.get("notes", []))
    return notes[:limit], None


def fetch_hot_notes(category="food", limit=10):
    """获取分类热门笔记。"""
    stdout, err = run_xhs(["hot", "-c", category, "--json"])
    if err:
        return [], err
    data, parse_err = parse_xhs_output(stdout)
    if parse_err:
        return [], parse_err
    notes = data if isinstance(data, list) else data.get("items", data.get("notes", []))
    return notes[:limit], None


def fetch_feed(limit=10):
    """获取推荐 Feed。"""
    stdout, err = run_xhs(["feed", "--json"])
    if err:
        return [], err
    data, parse_err = parse_xhs_output(stdout)
    if parse_err:
        return [], parse_err
    notes = data if isinstance(data, list) else data.get("items", data.get("notes", []))
    return notes[:limit], None


# ============ Signal Processing ============
SIGNAL_TYPES = [
    "技术突破", "产品发布", "创业投资", "开源动态", "工具推荐", "AI前沿"
]

def infer_signal_type(note):
    """根据笔记内容推断信号类型。"""
    title = note.get("display_title", "") or note.get("title", "")
    tags = note.get("tag_list", []) or note.get("tags", [])
    text = title.lower()
    tags_text = " ".join(tags).lower() if tags else ""

    if any(x in text for x in ["开源", "github", "code", "release"]):
        return "开源动态"
    elif any(x in text for x in ["launch", "发布", "新品", "产品"]):
        return "产品发布"
    elif any(x in text for x in ["投资", "融资", " funding", "raise"]):
        return "创业投资"
    elif any(x in text for x in ["AI", "LLM", "GPT", "model", "agent", "模型"]):
        return "AI前沿"
    elif any(x in text for x in ["工具", "tool", "app", "软件"]):
        return "工具推荐"
    return "AI前沿"


def infer_tags(note):
    """从笔记的 tag 列表中提取标签。"""
    tags = note.get("tag_list", []) or note.get("tags", []) or []
    return list(tags)[:5] if tags else []


def score_note(note):
    """计算笔记的分值 (1-10)。"""
    score = 0

    # Engagement score (liked_count, max 4 points)
    liked = note.get("interact_info", {}).get("liked_count", 0) or 0
    try:
        liked = int(liked)
    except (ValueError, TypeError):
        liked = 0

    if liked >= 10000:
        score += 4
    elif liked >= 5000:
        score += 3
    elif liked >= 1000:
        score += 2
    elif liked >= 100:
        score += 1

    # Title keyword match (max 3 points)
    title = (note.get("display_title", "") or note.get("title", "")).lower()
    quality_keywords = ["AI", "LLM", "GPT", "开源", "工具", "创业", "产品", "launch", "release", "agent"]
    matches = sum(1 for kw in quality_keywords if kw.lower() in title)
    score += min(3, matches)

    # Has image (max 1 point)
    images = note.get("image_list", [])
    if images:
        score += 1

    return min(10, max(1, score))


def convert_to_signal(note, source="search"):
    """将 xhs note 对象转换为统一信号格式。"""
    images = note.get("image_list", []) or []
    cover_url = images[0].get("url_default", "") or images[0].get("origin_url", "") if images else ""

    liked = note.get("interact_info", {}).get("liked_count", 0) or 0

    return {
        "title": (note.get("display_title", "") or note.get("title", ""))[:200],
        "source": "小红书",
        "signal_type": infer_signal_type(note),
        "url": note.get("share_url", "") or note.get("url", "") or f"https://www.xiaohongshu.com/explore/{note.get('note_id', '')}",
        "raw_summary": f"点赞:{liked} | 作者:{note.get('user', {}).get('nickname', 'N/A')} | 标签:{','.join(infer_tags(note))}",
        "rough_score": score_note(note),
        "status": "raw",
        "discovered_at": datetime.now().strftime("%Y-%m-%d"),
        "tags": infer_tags(note),
        "note_id": note.get("note_id", ""),
        "author": note.get("user", {}).get("nickname", ""),
        "liked_count": liked,
        "image_url": cover_url,
    }


# ============ Feishu Bitable Writer ============
def write_to_feishu(signals):
    """写入 Feishu Bitable。"""
    if not signals:
        return 0
    try:
        from feishu_bitable_client import create_record
    except ImportError:
        print("feishu_bitable_client not found, skipping Feishu write")
        return 0

    written = 0
    for sig in signals:
        tags = sig.pop("tags", [])
        note_id = sig.pop("note_id", "")
        author = sig.pop("author", "")
        liked_count = sig.pop("liked_count", 0)
        image_url = sig.pop("image_url", "")

        fields = {
            "Opportunity Signals": sig["title"],
            "信源": sig["source"],
            "信号类型": sig["signal_type"],
            "原始链接": {"text": sig["title"], "link": sig["url"]},
            "原始摘要": sig["raw_summary"],
            "粗筛评分": sig["rough_score"],
            "状态": sig["status"],
            "发现时间": int(datetime.now().timestamp() * 1000),
        }
        # Optional fields
        if tags:
            fields["标签"] = tags

        try:
            create_record(APP_TOKEN, TABLE_ID, fields)
            written += 1
        except Exception as e:
            print(f"  Feishu write failed for '{sig['title'][:30]}...': {e}")

    return written


# ============ Main ============
def main():
    log_jsonl("started", "full", 0)
    start = datetime.now()

    # Check cookie
    valid, cookie_msg = check_cookie_valid()
    if not valid:
        log_jsonl("failed", "check_cookie", 0, cookie_msg)
        print(f"[xiaohongshu] Cookie invalid: {cookie_msg}")
        print("[xiaohongshu] 需要手动配置 Cookie：")
        print("  1. 在有浏览器的机器上运行: xhs login")
        print("  2. 将 ~/.xiaohongshu-cli/cookies.json 上传到 VPS")
        print("  3. 确认后重新运行")
        sys.exit(1)

    print(f"[xiaohongshu] Cookie: {cookie_msg}")

    # Prepare output dir
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    all_signals = []

    # 1. Keyword searches
    keywords = os.environ.get("XHS_KEYWORDS", ",".join(DEFAULT_KEYWORDS)).split(",")
    for kw in keywords:
        kw = kw.strip()
        if not kw:
            continue
        print(f"[xiaohongshu] Searching: {kw}")
        notes, err = fetch_keyword_search(kw, limit=8, sort="popular")
        if err:
            print(f"  Error: {err}")
            log_jsonl("failed", f"search:{kw}", 0, err)
        else:
            print(f"  Got {len(notes)} notes")
            for note in notes:
                sig = convert_to_signal(note, source=f"search:{kw}")
                all_signals.append(sig)

    # 2. Hot notes by category
    for cat in HOT_CATEGORIES:
        print(f"[xiaohongshu] Hot category: {cat}")
        notes, err = fetch_hot_notes(cat, limit=5)
        if err:
            print(f"  Error: {err}")
        else:
            print(f"  Got {len(notes)} notes")
            for note in notes:
                sig = convert_to_signal(note, source=f"hot:{cat}")
                all_signals.append(sig)

    # 3. Feed (limited, high noise)
    # Skipping feed as it has high noise and is more for social discovery
    # rather than signal collection

    # Deduplicate by note_id
    seen = set()
    deduped = []
    for sig in all_signals:
        nid = sig.get("note_id", "")
        if nid and nid not in seen:
            seen.add(nid)
            deduped.append(sig)

    print(f"[xiaohongshu] Total signals (deduped): {len(deduped)}")

    # Write to local JSON
    month = datetime.now().strftime("%Y-%m")
    json_file = DATA_DIR / f"{month}.json"
    existing = []
    if json_file.exists():
        try:
            existing = json.loads(json_file.read_text())
        except Exception:
            existing = []

    existing.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "source": "小红书",
        "total_collected": len(deduped),
        "signals": deduped
    })
    json_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
    print(f"[xiaohongshu] Written to {json_file}")

    # Write to Feishu
    written = write_to_feishu(deduped)
    print(f"[xiaohongshu] Feishu written: {written}/{len(deduped)}")

    duration = int((datetime.now() - start).total_seconds() * 1000)
    log_jsonl("success", "full", duration)
    print(f"[xiaohongshu] Done in {duration}ms, signals={len(deduped)}, feishu={written}")


if __name__ == "__main__":
    main()