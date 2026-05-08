#!/usr/bin/env python3
"""
V2EX 采集器 — v2ex-collector-004
功能：抓取V2EX热门话题，解决反爬，输出结构化JSON
状态：✅ API正常 (https://www.v2ex.com/api/topics/hot.json)
"""

import json
import subprocess
import random
from datetime import datetime

V2EX_API = "https://www.v2ex.com/api/topics/hot.json"
V2EX_BOARD = "https://www.v2ex.com/api/topics/latest.json"

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

def curl_fetch(url, timeout=10):
    """curl获取URL"""
    ua = random.choice(USER_AGENTS)
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-time", str(timeout),
             "-H", f"User-Agent: {ua}",
             "-H", "Accept: application/json",
             "-H", "Referer: https://www.v2ex.com/",
             url],
            capture_output=True, text=True, timeout=timeout + 5
        )
        return result.stdout.strip()
    except Exception as e:
        return None

def fetch_hot():
    """获取V2EX热门主题"""
    data = curl_fetch(V2EX_API)
    if not data:
        return []
    try:
        topics = json.loads(data)
        return topics
    except json.JSONDecodeError:
        return []

def format_topic(topic, rank):
    """格式化主题"""
    return {
        "rank": rank,
        "title": topic.get("title", ""),
        "node": topic.get("node", {}).get("title", "") if isinstance(topic.get("node"), dict) else "",
        "node_name": topic.get("node", {}).get("name", "") if isinstance(topic.get("node"), dict) else "",
        "author": topic.get("member", {}).get("username", "") if isinstance(topic.get("member"), dict) else "",
        "replies": topic.get("replies", 0),
        "url": f"https://www.v2ex.com/t/{topic.get('id', '')}",
        "topic_id": topic.get("id"),
        "created": topic.get("created", 0),
        "platform": "V2EX",
    }

def save_json(data, filepath):
    output = {
        "timestamp": datetime.now().isoformat(),
        "source": "V2EX API (hot.json)",
        "count": len(data),
        "data": data
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    return filepath

def main():
    print("=== V2EX采集器 ===")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    topics = fetch_hot()
    print(f"获取到 {len(topics)} 条热门主题")
    
    if not topics:
        print("❌ API返回为空，尝试备用方案...")
        # 备用：直接curl测试
        test = curl_fetch("https://www.v2ex.com/")
        print(f"   V2EX主页响应: {len(test) if test else '无响应'}")
    
    formatted = [format_topic(t, i+1) for i, t in enumerate(topics)]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"/root/.openclaw/workspace/daily-digest/collectors/v2ex/v2ex_hot_{timestamp}.json"
    save_json(formatted, out_path)
    
    print(f"\n✅ 输出: {out_path}")
    print(f"   共 {len(formatted)} 条\n")
    
    print("=== Top 10 ===")
    for item in formatted[:10]:
        print(f"  {item['rank']:2d}. [{item['replies']:3d}回复] {item['title'][:55]}")
        print(f"        [{item['node']}] @{item['author']}")

if __name__ == "__main__":
    main()