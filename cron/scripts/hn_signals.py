#!/usr/bin/env python3
"""
hn_signals.py - Hacker News Top 10 Signals Collector
Fetches HN Top 10 stories via Firebase API, filters by keywords and score,
writes to local JSON + Feishu Bitable.
"""
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

# Config
APP_TOKEN = "S8mlbvHk6a4a6ss46klcw5CSnCY"
TABLE_ID = "tblIiWi9t04d0u5D"
DATA_DIR = "/root/.openclaw/workspace/data/opportunities/hn"
LOG_FILE = "/root/.openclaw/workspace/logs/cron-exec-{}.jsonl".format(
    datetime.now().strftime("%Y-%m-%d"))

# Keywords for filtering
FILTER_KEYWORDS = ["AI", "ML", "machine learning", "LLM", "AGI", "startup", 
                   "tool", "SaaS", "product", "launch", "open source", 
                   "developer", "API", "framework", "agent", "automation",
                   "GPT", "Claude", "gemini", "robot", "hardware"]
MIN_SCORE = 100

def log_jsonl(status, stage="full", duration_ms=0, error=""):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cron_name": "hn-signals",
        "stage": stage,
        "status": status,
        "duration_ms": duration_ms
    }
    if error:
        entry["error"] = error
    print(json.dumps(entry))

def fetch_hn_topstories():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        log_jsonl("failed", "fetch", 0, str(e))
        return []

def fetch_hn_item(item_id):
    url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return json.loads(r.read())
    except:
        return None

def score_item(item):
    """Simple 4-dim rough screening score (1-10)."""
    score = item.get("score", 0)
    title = item.get("title", "").lower()
    
    # Dim 1: Engagement (score normalized, max 4 points)
    dim1 = min(4, int(score / 100))
    
    # Dim 2: Comment activity (max 3 points)
    descendants = item.get("descendants", 0)
    dim2 = min(3, int(descendants / 50))
    
    # Dim 3: Keyword relevance (max 2 points)
    dim3 = 0
    for kw in FILTER_KEYWORDS:
        if kw.lower() in title:
            dim3 += 1
            if dim3 >= 2:
                break
    
    # Dim 4: URL credibility (has URL = 1 point)
    dim4 = 1 if item.get("url") else 0
    
    return dim1 + dim2 + dim3 + dim4

def should_include(item):
    if item.get("type") != "story":
        return False
    score = item.get("score", 0)
    if score < MIN_SCORE:
        return False
    title = item.get("title", "").lower()
    for kw in FILTER_KEYWORDS:
        if kw.lower() in title:
            return True
    return False

def infer_signal_type(title):
    title_lower = title.lower()
    if any(x in title_lower for x in ["launch", "release", "announce", "introduce", "new"]):
        return "产品发布"
    elif any(x in title_lower for x in ["raise", "funding", "seed", "series", "invest"]):
        return "融资"
    elif any(x in title_lower for x in ["model", "research", "paper", "study", "breakthrough"]):
        return "技术突破"
    elif any(x in title_lower for x in ["policy", "regulation", "government", "law"]):
        return "政策"
    elif any(x in title_lower for x in ["problem", "pain", "frustrat", "need", "want"]):
        return "痛点"
    return "技术突破"

def infer_tags(title, item):
    tags = []
    title_lower = title.lower()
    if any(x in title_lower for x in ["ai", "llm", "gpt", "claude", "gemini", "model"]):
        tags.append("AI")
    if any(x in title_lower for x in ["agent", "automat"]):
        tags.append("Agent")
    if any(x in title_lower for x in ["open source", "github", "framework"]):
        tags.append("开源")
    if any(x in title_lower for x in ["hardware", "device", "chip", "robot"]):
        tags.append("硬件")
    if any(x in title_lower for x in ["saas", "product", "tool"]):
        tags.append("工具")
    if any(x in title_lower for x in ["developer", "api", "code", "programming"]):
        tags.append("开发者工具")
    return tags if tags else ["AI"]

def main():
    log_jsonl("started", "full", 0)
    start = datetime.now()
    
    today = datetime.now().strftime("%Y-%m-%d")
    import os
    os.makedirs(DATA_DIR, exist_ok=True)
    
    top_ids = fetch_hn_topstories()[:10]
    
    signals = []
    for item_id in top_ids:
        item = fetch_hn_item(item_id)
        if not item:
            continue
        if should_include(item):
            title = item.get("title", "Untitled")
            raw_summary = f"HN Score:{item.get('score')} | Comments:{item.get('descendants',0)} | {title[:80]}"
            if len(raw_summary) > 150:
                raw_summary = raw_summary[:147] + "..."
            
            signal = {
                "title": title,
                "source": "HN",
                "signal_type": infer_signal_type(title),
                "url": item.get("url", f"https://news.ycombinator.com/item?id={item_id}"),
                "raw_summary": raw_summary,
                "rough_score": score_item(item),
                "status": "raw",
                "discovered_at": today,
                "tags": infer_tags(title, item)
            }
            signals.append(signal)
    
    total = len(top_ids)
    passed = len(signals)
    
    # Save local JSON
    month = datetime.now().strftime("%Y-%m")
    json_file = f"{DATA_DIR}/{month}.json"
    
    existing = []
    if os.path.exists(json_file):
        with open(json_file) as f:
            existing = json.load(f)
    
    # Append daily batch
    daily_batch = {
        "date": today,
        "source": "HN",
        "total_fetched": total,
        "passed_filter": passed,
        "signals": signals
    }
    existing.append(daily_batch)
    
    with open(json_file, "w") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    # Write to Feishu Bitable
    from subprocess import run, PIPE
    for sig in signals:
        tags = sig.pop("tags", [])
        fields = {
            "Opportunity Signals": sig["title"],
            "信源": sig["source"],
            "信号类型": sig["signal_type"],
            "原始链接": {"text": sig["title"], "link": sig["url"]},
            "原始摘要": sig["raw_summary"],
            "粗筛评分": sig["rough_score"],
            "状态": sig["status"],
            "发现时间": int(datetime.now().timestamp() * 1000),
            "标签": tags
        }
        cmd = [
            "python3", "-c",
            f"""import sys; sys.path.insert(0, '/root/.openclaw/workspace/cron/scripts');
from feishu_bitable_client import create_record;
print(create_record('{APP_TOKEN}', '{TABLE_ID}', {json.dumps(fields)}))"""
        ]
        run(cmd, capture_output=True)
    
    duration = int((datetime.now() - start).total_seconds() * 1000)
    log_jsonl("success", "full", duration)
    print(f"hn-signals: fetched={total}, passed={passed}")

if __name__ == "__main__":
    main()