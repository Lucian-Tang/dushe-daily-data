#!/usr/bin/env python3
"""
百度热搜采集器 — baidu-collector-005
参考 baidu-hot-monitor skill 的 baidu_hot.py
增加：兜底HTML抓取 + 重试机制 + 分类标签
"""

import json
import re
import subprocess
import random
import urllib.parse
from datetime import datetime

BAIDU_API_URL = "https://top.baidu.com/api/board?platform=wise&tab=realtime"
BAIDU_HTML_URL = "https://top.baidu.com/board?tab=realtime"

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

def curl_fetch(url, timeout=15):
    ua = random.choice(USER_AGENTS)
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-time", str(timeout),
             "-H", f"User-Agent: {ua}",
             "-H", "Accept: application/json, text/plain, */*",
             "-H", "Accept-Language: zh-CN,zh;q=0.9",
             "-H", "Referer: https://top.baidu.com/",
             url],
            capture_output=True, text=True, timeout=timeout + 5
        )
        return result.stdout.strip()
    except:
        return None

def fetch_api(limit=50):
    """方式1：百度实时API"""
    data = curl_fetch(BAIDU_API_URL)
    if not data:
        return []
    try:
        obj = json.loads(data)
        if not obj.get("success"):
            return []
        cards = obj.get("data", {}).get("cards", [])
        items = []
        for card in cards:
            for content in card.get("content", []):
                for item in content.get("content", []):
                    items.append(item)
        return items[:limit]
    except:
        return []

def fetch_html(limit=50):
    """方式2：HTML正则兜底"""
    html = curl_fetch(BAIDU_HTML_URL)
    if not html:
        return []
    items = []
    words = re.findall(r'"word"\s*:\s*"([^"]+)"', html)
    scores = re.findall(r'"hotScore"\s*:\s*"?(\d+)"?', html)
    labels = re.findall(r'"labelTag"\s*:\s*\{"day"\s*:\s*\{"text"\s*:\s*"([^"]+)"', html)
    tags = re.findall(r'"hotTag"\s*:\s*"(\d)"', html)
    
    for i, word in enumerate(words[:limit]):
        item = {
            "word": word,
            "hotScore": scores[i] if i < len(scores) else "0",
            "labelTag": labels[i] if i < len(labels) else "",
            "hotTag": tags[i] if i < len(tags) else "0",
            "index": i
        }
        items.append(item)
    return items

def format_item(item, rank):
    title = item.get("word", "")
    if not title:
        return None
    
    hot_tag_str = item.get("hotTag", "0")
    label_dict = item.get("labelTag", {})
    
    if isinstance(label_dict, dict):
        label = label_dict.get("day", {}).get("text", "") if isinstance(label_dict.get("day"), dict) else ""
    else:
        label = str(label_dict) if label_dict else ""
    
    if label:
        category = label
    elif hot_tag_str == "1":
        category = "新"
    elif hot_tag_str == "3":
        category = "热"
    else:
        category = "综合"
    
    return {
        "rank": rank,
        "title": title,
        "category": category,
        "hot_score": item.get("hotScore", "0"),
        "hot_tag": hot_tag_str,
        "label": label,
        "url": f"https://www.baidu.com/s?wd={urllib.parse.quote(title.encode('utf-8'))}",
        "platform": "百度",
    }

def save_json(data, filepath):
    output = {
        "timestamp": datetime.now().isoformat(),
        "source": "百度热搜 (API + HTML fallback)",
        "count": len(data),
        "data": data
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    return filepath

def main():
    print("=== 百度热搜采集器 ===")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("📡 尝试API方式...")
    items = fetch_api(limit=50)
    fetch_method = "api"
    
    if not items:
        print("   API失败，尝试HTML兜底...")
        items = fetch_html(limit=50)
        fetch_method = "html"
    
    if not items:
        print("❌ 所有方式均失败")
        return
    
    print(f"   {fetch_method}方式获取到 {len(items)} 条")
    
    formatted = []
    for i, item in enumerate(items):
        f = format_item(item, i + 1)
        if f:
            formatted.append(f)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"/root/.openclaw/workspace/daily-digest/collectors/baidu/baidu_hot_{timestamp}.json"
    save_json(formatted, out_path)
    
    print(f"\n✅ 输出: {out_path}")
    print(f"   共 {len(formatted)} 条 (方法: {fetch_method})\n")
    
    print("=== Top 15 ===")
    for item in formatted[:15]:
        cat = item["category"]
        print(f"  {item['rank']:2d}. [{cat}] {item['title'][:50]}")

if __name__ == "__main__":
    main()