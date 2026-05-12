#!/usr/bin/env python3
"""社会热点数据预处理 2026-05-12：多源交叉验证 + 情绪关键词提取"""

import json
import re
from collections import defaultdict
from datetime import datetime

INPUT_FILE = "/root/.openclaw/workspace/dushe-daily-data/raw_social_20260512.json"
OUTPUT_PROCESSED = "/root/.openclaw/workspace/dushe-daily-data/data/social_processed_20260512.json"
OUTPUT_EMOTION = "/root/.openclaw/workspace/dushe-daily-data/data/social_emotion_20260512.json"

# 情绪关键词
EMOTION_KEYWORDS = {
    "positive": ["victory", "peace", "win", "hope", "success", "happy", "celebrate", "achievement",
                 "deal", "ceasefire", "agreement", "positive", "breakthrough", "approve", "launch",
                 "bail", "released", "resign"],
    "negative": ["war", "attack", "death", "died", "killed", "crisis", "conflict", "terror", "fear",
                 "threat", "danger", "sanction", "violate", "violation", "disaster", "emergency",
                 "fire", "explosion", "violence", "jail", "rape", "scandal", "fraud", "corrupt",
                 "murder", "decline", "lose", "loss", "fail", "recession", "inflation", "depression",
                 "crash", "collapse", "impeached", "quarantine", "laid off", "hantavirus"],
    "negative_zh": ["死亡", "战争", "攻击", "枪击", "爆炸", "火灾", "逮捕", "入狱", "腐败",
                    "丑闻", "暴跌", "倒闭", "失败", "抗议", "冲突", "威胁", "灾难", "嫖娼",
                    "伤害", "凶杀"],
    "positive_zh": ["胜利", "和平", "成功", "达成", "协议", "批准", "发布", "突破", "获奖",
                    "庆", "喜", "好", "发声", "随"],
}

def normalize_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return text

def extract_keywords(title):
    if not title:
        return []
    text = normalize_text(title)
    return [w for w in text.split() if len(w) > 2]

def check_emotion(title, content=""):
    text = (title + " " + content).lower()
    pos, neg = [], []
    for kw in EMOTION_KEYWORDS["positive"]:
        if kw in text:
            pos.append(kw)
    for kw in EMOTION_KEYWORDS["negative"]:
        if kw in text:
            neg.append(kw)
    for kw in EMOTION_KEYWORDS["positive_zh"]:
        if kw in text:
            pos.append(kw)
    for kw in EMOTION_KEYWORDS["negative_zh"]:
        if kw in text:
            neg.append(kw)
    return {"positive": list(set(pos)), "negative": list(set(neg))}

def topic_key(title):
    t = title.lower()
    maps = [
        ("iran ceasefire", "伊朗停火协议"),
        ("iran war", "伊朗战争"),
        ("trump china", "特朗普访华"),
        ("elon musk cook trump china", "马斯克库克随特朗普访华"),
        ("hantavirus cruise", "汉坦病毒游轮"),
        ("starmer labour uk", "英国工党斯塔默"),
        ("zelen", "乌克兰泽连斯基"),
        ("yermak corruption", "乌克兰反腐"),
        ("arcadia mayor chinese foreign agent", "阿凯迪亚市长中国间谍"),
        ("netanyahu phase out military aid", "内塔尼亚胡美国军援"),
        ("trump iran ceasefire", "特朗普伊朗停火"),
        ("gas tax", "美国天然气税"),
        ("palantir nhs data", "英国NHS数据"),
        ("europe microsoft amazon google ban", "欧洲禁止科技巨头"),
        ("hungary new pm", "匈牙利新总理"),
        ("north korea gdp russia war", "朝鲜援俄"),
        ("spain eu army", "西班牙欧盟军队"),
        ("canada military recruitment", "加拿大军事招募"),
        ("supreme court abortion pill", "最高法院药物流产"),
        ("supreme court alabama house map", "最高法院阿拉巴马选区"),
        ("laredo train boxcar deaths", "拉雷多火车闷死"),
        ("california mayor chinese foreign agent", "加州阿凯迪亚市长"),
        ("google zero day hack ai", "谷歌AI零日漏洞"),
        ("gm layoffs ai", "通用汽车AI裁员"),
        ("end to end encryption android iphone", "安卓苹果加密"),
        ("buzzfeed byron allen", "BuzzFeed收购"),
        ("trump venezuela oil", "特朗普委内瑞拉"),
        ("uae iran attacks", "阿联酋伊朗袭击"),
        ("汶川地震", "汶川地震18周年"),
        ("演出完退礼服", "退礼服女孩发声"),
        ("廖智生四胎", "廖智生四胎"),
        ("双胞胎姐妹入室", "双胞胎姐妹入室伤害"),
        ("特朗普金卡", "特朗普金卡"),
        ("微信状态浏览", "微信状态浏览"),
        ("湖人vs雷霆", "湖人雷霆"),
        ("活塞vs骑士", "活塞骑士"),
        ("天坛公园", "天坛公园暂停开放"),
    ]
    for pattern, key in maps:
        if pattern in t:
            return key
    return None

def compute_trend_score(item):
    """从content字段解析热度"""
    content = item.get("content", "")
    m = re.search(r'🔥\s*([0-9,]+)', content)
    if m:
        return int(m.group(1).replace(',', ''))
    return 0

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw = json.load(f)

# 按话题聚类
from collections import OrderedDict
topic_map = OrderedDict()

for item in raw:
    key = topic_key(item["title"])
    if not key:
        continue
    if key not in topic_map:
        topic_map[key] = {"title": key, "sources": [], "items": [], "heat": 0}
    topic_map[key]["sources"].append(item["source"])
    topic_map[key]["items"].append(item)
    heat = compute_trend_score(item)
    if heat > topic_map[key]["heat"]:
        topic_map[key]["heat"] = heat

# 交叉验证
processed = []
emotion_data = []

for key, topic in topic_map.items():
    unique_sources = list(set(topic["sources"]))
    src_count = len(unique_sources)
    emoji = "🔥" if src_count >= 3 else "🟡"
    
    # 主来源
    source_priority = ["微博热搜", "Google News Top", "BBC News World", "NYT World", "Reddit WorldNews"]
    primary = next((s for s in source_priority if s in unique_sources), unique_sources[0])
    
    top_item = max(topic["items"], key=lambda x: compute_trend_score(x))
    
    emotions = check_emotion(top_item["title"], top_item.get("content", ""))
    sentiment = "negative" if len(emotions["negative"]) > len(emotions["positive"]) else \
               "positive" if len(emotions["positive"]) > len(emotions["negative"]) else "neutral"
    
    processed.append({
        "topic": key,
        "emoji": emoji,
        "source_count": src_count,
        "sources": unique_sources,
        "primary_source": primary,
        "title": top_item["title"],
        "url": top_item["url"],
        "heat": topic["heat"],
        "category": top_item.get("category", ""),
        "region": top_item.get("region", ""),
        "lang": top_item.get("lang", ""),
        "published": top_item.get("published", ""),
        "sentiment": sentiment,
        "emotion_positive": emotions["positive"],
        "emotion_negative": emotions["negative"],
    })
    
    for item in topic["items"]:
        e = check_emotion(item["title"], item.get("content", ""))
        sentiment_item = "negative" if len(e["negative"]) > len(e["positive"]) else \
                        "positive" if len(e["positive"]) > len(e["negative"]) else "neutral"
        emotion_data.append({
            "title": item["title"],
            "source": item["source"],
            "region": item.get("region", ""),
            "category": item.get("category", ""),
            "sentiment": sentiment_item,
            "positive_keywords": e["positive"],
            "negative_keywords": e["negative"],
            "heat": compute_trend_score(item),
            "url": item["url"],
        })

# 按source_count和heat排序
processed.sort(key=lambda x: (-x["source_count"], -x["heat"]))
emotion_data.sort(key=lambda x: -x["heat"])

# 统计
stats = {
    "date": "2026-05-12",
    "total_topics": len(processed),
    "🔥_topics": sum(1 for x in processed if x["emoji"] == "🔥"),
    "🟡_topics": sum(1 for x in processed if x["emoji"] == "🟡"),
    "total_items": len(emotion_data),
    "positive_items": sum(1 for x in emotion_data if x["sentiment"] == "positive"),
    "negative_items": sum(1 for x in emotion_data if x["sentiment"] == "negative"),
    "neutral_items": sum(1 for x in emotion_data if x["sentiment"] == "neutral"),
}

with open(OUTPUT_PROCESSED, "w", encoding="utf-8") as f:
    json.dump({"stats": stats, "topics": processed}, f, ensure_ascii=False, indent=2)

with open(OUTPUT_EMOTION, "w", encoding="utf-8") as f:
    json.dump({"stats": stats, "items": emotion_data}, f, ensure_ascii=False, indent=2)

print(f"✅ 处理完成: {stats['total_topics']} 个话题, {stats['🔥_topics']} 🔥 / {stats['🟡_topics']} 🟡")
print(f"✅ 情绪条目: {stats['total_items']} 条 (正{stats['positive_items']} 负{stats['negative_items']} 中{stats['neutral_items']})")
print(f"✅ 输出: {OUTPUT_PROCESSED}")
print(f"✅ 输出: {OUTPUT_EMOTION}")