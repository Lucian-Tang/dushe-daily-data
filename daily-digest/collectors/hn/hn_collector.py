#!/usr/bin/env python3
"""
HN采集器 v2.0 — hn-collector-003
修复问题：
- 使用 Firebase TopStories API（而非Algolia搜索）获取真实Top20
- 增加重试机制
- 增加User-Agent随机化
- 输出结构化JSON
"""

import json
import time
import random
import subprocess
from datetime import datetime

HN_FIREBASE_TOP = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_FIREBASE_ITEM = "https://hacker-news.firebaseio.com/v0/item/{}.json"
HN_FIREBASE_USER = "https://hacker-news.firebaseio.com/v0/user/{}.json"

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

def curl_fetch(url, timeout=10, retries=2):
    """使用curl获取URL，增加重试和随机UA"""
    ua = random.choice(USER_AGENTS)
    for attempt in range(retries):
        try:
            result = subprocess.run(
                ["curl", "-s", "-L", "--max-time", str(timeout),
                 "-H", f"User-Agent: {ua}",
                 "-H", "Accept: application/json",
                 url],
                capture_output=True, text=True, timeout=timeout + 5
            )
            if result.stdout.strip():
                return result.stdout.strip()
            time.sleep(0.5 * (attempt + 1))
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
            else:
                return None
    return None

def fetch_top_story_ids(limit=30):
    """获取Top Stories ID列表"""
    data = curl_fetch(HN_FIREBASE_TOP)
    if not data:
        return []
    try:
        ids = json.loads(data)
        return ids[:limit]
    except:
        return []

def fetch_story(story_id):
    """获取单条故事详情"""
    url = HN_FIREBASE_ITEM.format(story_id)
    data = curl_fetch(url, timeout=8)
    if not data:
        return None
    try:
        item = json.loads(data)
        if item.get("deleted") or item.get("dead"):
            return None
        return item
    except:
        return None

def fetch_stories(story_ids, delay=0.3):
    """批量获取故事，带延迟"""
    stories = []
    for i, sid in enumerate(story_ids):
        story = fetch_story(sid)
        if story:
            stories.append(story)
        if (i + 1) % 5 == 0:
            time.sleep(delay)
        else:
            time.sleep(delay * 0.5)
    return stories

def format_story(story):
    """格式化故事输出"""
    return {
        "rank": 0,  # 将在排序后填充
        "title": story.get("title", ""),
        "url": story.get("url") or f"https://news.ycombinator.com/item?id={story.get('id')}",
        "score": story.get("score", 0),
        "comments": story.get("descendants", 0),
        "author": story.get("by", ""),
        "platform": "HN",
        "story_id": story.get("id"),
        "type": story.get("type", "story"),
        "created_at": datetime.fromtimestamp(story.get("time", 0)).isoformat() if story.get("time") else "",
    }

def save_json(data, filepath):
    """保存JSON文件"""
    output = {
        "timestamp": datetime.now().isoformat(),
        "source": "HN Firebase API",
        "count": len(data),
        "data": data
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    return filepath

def main():
    print("=== HN采集器 v2.0 ===")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 获取Top Stories IDs
    print("📡 获取HN Top Stories列表...")
    ids = fetch_top_story_ids(limit=30)
    print(f"   获取到 {len(ids)} 个Story ID")
    
    if not ids:
        print("❌ 无法获取Story ID列表")
        return
    
    # 2. 批量获取故事详情
    print("📥 批量获取故事详情...")
    stories = fetch_stories(ids, delay=0.4)
    print(f"   成功获取 {len(stories)} 条故事")
    
    if not stories:
        print("❌ 无法获取故事详情")
        return
    
    # 3. 格式化并按热度排序
    formatted = [format_story(s) for s in stories]
    formatted.sort(key=lambda x: x["score"], reverse=True)
    for i, item in enumerate(formatted):
        item["rank"] = i + 1
    
    # 4. 输出
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"/root/.openclaw/workspace/daily-digest/collectors/hn/hn_top_{timestamp}.json"
    save_json(formatted, out_path)
    
    print(f"\n✅ 输出: {out_path}")
    print(f"   共 {len(formatted)} 条\n")
    
    # 打印前10条
    print("=== Top 10 ===")
    for item in formatted[:10]:
        print(f"  {item['rank']:2d}. [{item['score']:4d}pts] {item['title'][:60]}")

if __name__ == "__main__":
    main()