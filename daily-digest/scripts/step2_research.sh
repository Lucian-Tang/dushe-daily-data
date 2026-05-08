#!/usr/bin/env python3
"""热点研究 Step2: 基于raw数据分析，识别超级热点和情绪"""
import json, datetime

with open(f"/root/.openclaw/workspace/daily-digest/raw/hot-raw-{datetime.date.today().strftime('%Y-%m-%d')}.json") as f:
    raw = json.load(f)

def extract_keywords(title):
    """提取4字以上关键词"""
    words = []
    for i in range(len(title)-3):
        word = title[i:i+4]
        if len(word) >= 4 and not any(c in '。！？，、' for c in word):
            words.append(word)
    return words

# 关键词跨平台统计
keyword_map = {}
platforms = ['baidu', 'douyin', 'toutiao', 'v2ex', 'hn', 'github']
for platform in platforms:
    for item in raw.get(platform, []):
        title = item.get('title', '')
        for kw in extract_keywords(title):
            if kw not in keyword_map:
                keyword_map[kw] = set()
            keyword_map[kw].add(platform)

# 找出3+平台共现的词
cross_platform = {kw: list(plats) for kw, plats in keyword_map.items() if len(plats) >= 3}
top_keywords = sorted(cross_platform.items(), key=lambda x: -len(x[1]))[:8]

# 提取超级热点：每个平台TOP3
super_topics = []
for platform in ['baidu', 'douyin', 'toutiao']:
    rank_key = 'rank' if 'rank' in raw[platform][0] else 'rank'
    for item in raw.get(platform, [])[:3]:
        super_topics.append({
            'title': item.get('title', ''),
            'platform': platform,
            'rank': item.get('rank', ''),
            'heat': item.get('heat', item.get('hot', ''))
        })

# 跨平台扩散话题：从baidu/toutiao/douyin各取TOP5中的重叠
titles_by_platform = {}
for platform in ['baidu', 'douyin', 'toutiao']:
    titles_by_platform[platform] = [item.get('title','') for item in raw.get(platform, [])[:5]]

# 找出在多个平台TOP5都出现的标题
topic_cross = {}
for platform1 in ['baidu', 'douyin', 'toutiao']:
    for title in titles_by_platform[platform1]:
        if title not in topic_cross:
            topic_cross[title] = []
        topic_cross[title].append(platform1)

spread_topics = [{'title': t, 'platforms': p} for t, p in topic_cross.items() if len(p) >= 2]

# 输出分析
research = {
    'date': datetime.date.today().strftime('%Y-%m-%d'),
    'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
    'total_raw_items': sum(len(raw.get(p, [])) for p in platforms),
    'super_topics': super_topics,
    'cross_platform_keywords': [{'keyword': kw, 'platforms': plats} for kw, plats in top_keywords],
    'spread_topics': spread_topics[:5],
    'platform_summary': {
        p: {
            'count': len(raw.get(p, [])),
            'top3': [item.get('title', '') for item in raw.get(p, [])[:3]]
        } for p in platforms
    }
}

out_path = f"/root/.openclaw/workspace/daily-digest/research/hot-research-{datetime.date.today().strftime('%Y-%m-%d')}.json"
with open(out_path, 'w') as f:
    json.dump(research, f, ensure_ascii=False, indent=2)

print(f"研究完成")
print(f"- 超级热点: {len(super_topics)} 个")
print(f"- 跨平台关键词: {len(cross_platform)} 个")
print(f"- 扩散话题: {len(spread_topics)} 个")
print(f"- 输出: {out_path}")