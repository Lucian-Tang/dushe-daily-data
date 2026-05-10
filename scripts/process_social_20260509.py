#!/usr/bin/env python3
"""社会热点数据预处理：多源交叉验证 + 情绪关键词提取"""

import json
import re
from collections import defaultdict
from datetime import datetime

INPUT_FILE = "/root/.openclaw/workspace/data/raw_social_20260509.json"
OUTPUT_PROCESSED = "/root/.openclaw/workspace/data/social_processed_20260509.json"
OUTPUT_EMOTION = "/root/.openclaw/workspace/data/social_emotion_20260509.json"

# 情绪关键词
EMOTION_KEYWORDS = {
    "positive": ["victory", "peace", "win", "hope", "success", "happy", "celebrate", "achievement", "deal", " ceasefire", "agreement", "positive", "breakthrough", "approve", "launch"],
    "negative": ["war", "attack", "death", "kill", "died", "killed", "crisis", "conflict", "terror", "fear", "threat", "danger", "sanction", "violate", "violation", "disaster", "emergency", "fire", "explosion", "violence", "jail", "rape", "scandal", "fraud", "corrupt", "murder", "decline", "lose", "loss", "fail", "recession", "inflation", "depression", "crash", "collapse"],
    "negative_zh": ["死亡", "战争", "攻击", "恐怖", "枪击", "爆炸", "火灾", "逮捕", "入狱", "腐败", "丑闻", "暴跌", "倒闭", "失败", "抗议", "冲突", "威胁", "灾难", "死亡"],
    "positive_zh": ["胜利", "和平", "成功", "达成", "协议", "批准", "发布", "突破", "获奖", "庆", "喜", "好"],
}

def normalize_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return text

def extract_keywords_from_title(title):
    """从标题提取关键词"""
    if not title:
        return []
    title_lower = normalize_text(title)
    words = [w for w in title_lower.split() if len(w) > 2]
    return words

def check_emotion(title, content=""):
    """检测情绪关键词"""
    text = (title + " " + content).lower()
    result = {"positive": [], "negative": []}
    
    for kw in EMOTION_KEYWORDS["positive"]:
        if kw in text:
            result["positive"].append(kw)
    for kw in EMOTION_KEYWORDS["negative"]:
        if kw in text:
            result["negative"].append(kw)
    for kw in EMOTION_KEYWORDS["positive_zh"]:
        if kw in text:
            result["positive"].append(kw)
    for kw in EMOTION_KEYWORDS["negative_zh"]:
        if kw in text:
            result["negative"].append(kw)
    
    return result

def extract_entities(title, content=""):
    """简单的实体提取"""
    entities = []
    text = (title + " " + content).lower()
    
    known_entities = {
        "US", "Iran", "China", "Russia", "Ukraine", "Trump", "Elon Musk", "Musk",
        "Taiwan", "Israel", "Palestine", "Hamas", "NATO", "EU", "UK", "Labour",
        "FDA", "Pentagon", "Virginia", "South Africa", "Japan", "Hungary", "Greece",
        "UFO", "Tesla", "Cybertruck", "Discord", "Moderna", "Samsung", "Hantavirus",
        "Mark Hamill", "Kamala Harris", "JD Vance", "Kristin Smart",
    }
    
    for entity in known_entities:
        if entity.lower() in text:
            entities.append(entity)
    
    return list(set(entities))

def find_topic_key(title):
    """从标题提取话题关键词"""
    title_lower = title.lower()
    
    # 提取关键实体/话题词
    topic_patterns = [
        "hantavirus", "cruise", "ship",
        "iran", "u.s.", "us", "america",
        "china", "chinese",
        "russia", "ukraine", "zelensky", "putin",
        "trump", "ceasefire", "tariff",
        "ufo", "pentagon", "defense department",
        "taiwan", "beijing",
        "samsung", "tesla", "cybertruck",
        "discord", "moderna", "vaccine",
        "uk election", "labour", "starmer", "reform",
        "north korea", "kim", "nuclear",
        "hong kong", "tianwen", "mars",
        "world cup", "fifa",
        "ai", "chatgpt",
    ]
    
    for pattern in topic_patterns:
        if pattern in title_lower:
            return pattern
    return None

def cluster_by_topic(items):
    """按话题聚类"""
    clusters = defaultdict(list)
    
    for item in items:
        title = item.get("title", "")
        key = find_topic_key(title)
        if key:
            clusters[key].append(item)
    
    return clusters

def main():
    # 加载原始数据
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    print(f"Loaded {len(raw_data)} items from raw_social_20260509.json")
    
    # 按标题关键词/实体聚类
    topic_map = defaultdict(list)
    
    for item in raw_data:
        title = item.get("title", "")
        content = item.get("content", "")
        
        # 提取话题关键词
        key = find_topic_key(title)
        if key:
            topic_map[key].append(item)
    
    # 转换为话题列表
    topics = []
    
    for key, items in topic_map.items():
        source_count = len(set(item.get("source", "") for item in items))
        badge = "🔥" if source_count >= 3 else "🟡" if source_count >= 2 else "⚪"
        
        # 提取情绪
        all_emotions = {"positive": [], "negative": []}
        all_entities = set()
        all_titles = [item.get("title", "") for item in items]
        
        for item in items:
            title = item.get("title", "")
            content = item.get("content", "")
            emos = check_emotion(title, content)
            all_emotions["positive"].extend(emos["positive"])
            all_emotions["negative"].extend(emos["negative"])
            all_entities.update(extract_entities(title, content))
        
        # 去重情绪关键词
        all_emotions["positive"] = list(set(all_emotions["positive"]))
        all_emotions["negative"] = list(set(all_emotions["negative"]))
        
        # 构建话题
        topic = {
            "key": [key],
            "badge": badge,
            "source_count": source_count,
            "sources": list(set(item.get("source", "") for item in items)),
            "titles": all_titles[:10],  # 最多10个标题
            "entities": list(all_entities),
            "keywords": extract_keywords_from_title(key),
            "emotions": [
                {"type": "positive", "keywords": all_emotions["positive"]} if all_emotions["positive"] else None,
                {"type": "negative", "keywords": all_emotions["negative"]} if all_emotions["negative"] else None,
            ],
            "items": items[:20],  # 最多20条原始数据
        }
        # 移除空的emotions
        topic["emotions"] = [e for e in topic["emotions"] if e]
        
        topics.append(topic)
    
    # 按source_count排序
    topics.sort(key=lambda x: -x["source_count"])
    
    # 分类
    hot_topics = [t for t in topics if t["badge"] == "🔥"]
    medium_topics = [t for t in topics if t["badge"] == "🟡"]
    
    # 构建输出
    processed = {
        "date": "20260509",
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_items": len(raw_data),
            "total_topics": len(topics),
            "hot_count": len(hot_topics),
            "medium_count": len(medium_topics),
            "sources": {}
        },
        "hot_topics": hot_topics + medium_topics
    }
    
    # 统计来源
    source_counts = defaultdict(int)
    for item in raw_data:
        source_counts[item.get("source", "unknown")] += 1
    processed["summary"]["sources"] = dict(source_counts)
    
    # 输出情绪摘要
    emotion_topics = {"positive": [], "negative": [], "neutral": []}
    
    for topic in topics:
        if not topic["emotions"]:
            continue
        emotion_data = {
            "titles": topic["titles"],
            "keywords": topic["emotions"][0]["keywords"] if topic["emotions"] else [],
            "badge": topic["badge"],
            "sources": topic["sources"],
            "entities": topic["entities"]
        }
        
        for emo in topic["emotions"]:
            if emo["type"] == "positive" and emotion_data not in emotion_topics["positive"]:
                emotion_topics["positive"].append(emotion_data)
            elif emo["type"] == "negative" and emotion_data not in emotion_topics["negative"]:
                emotion_topics["negative"].append(emotion_data)
    
    emotion_output = {
        "date": "20260509",
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_analyzed": len(raw_data),
            "emotion_positive": len(emotion_topics["positive"]),
            "emotion_negative": len(emotion_topics["negative"]),
            "emotion_neutral": len(emotion_topics["neutral"]),
            "topics_with_emotion": len([t for t in topics if t["emotions"]])
        },
        "emotion_topics": emotion_topics
    }
    
    # 写入文件
    with open(OUTPUT_PROCESSED, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)
    print(f"Written: {OUTPUT_PROCESSED}")
    
    with open(OUTPUT_EMOTION, "w", encoding="utf-8") as f:
        json.dump(emotion_output, f, ensure_ascii=False, indent=2)
    print(f"Written: {OUTPUT_EMOTION}")
    
    # 打印摘要
    print(f"\n=== 预处理完成 ===")
    print(f"总条目: {len(raw_data)}")
    print(f"总话题: {len(topics)}")
    print(f"🔥 热门话题: {len(hot_topics)}")
    print(f"🟡 中等话题: {len(medium_topics)}")
    
    return processed, emotion_output

if __name__ == "__main__":
    main()