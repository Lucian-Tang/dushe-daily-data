#!/usr/bin/env python3
"""社会热点数据预处理 2026-05-17：多源交叉验证 + 情绪关键词提取"""

import json
import re
from collections import OrderedDict

INPUT_FILE = "/root/.openclaw/workspace/dushe-daily-data/raw_social_20260517.json"
OUTPUT_PROCESSED = "/root/.openclaw/workspace/dushe-daily-data/data/social_processed_20260517.json"
OUTPUT_EMOTION = "/root/.openclaw/workspace/dushe-daily-data/data/social_emotion_20260517.json"

EMOTION_KEYWORDS = {
    "positive": ["victory", "peace", "win", "hope", "success", "happy", "celebrate", "achievement",
                 "deal", "ceasefire", "agreement", "positive", "breakthrough", "approve", "launch",
                 "bail", "released", "resign", "good", "cool down", "commute"],
    "negative": ["war", "attack", "death", "died", "killed", "crisis", "conflict", "terror", "fear",
                 "threat", "danger", "sanction", "violate", "violation", "disaster", "emergency",
                 "fire", "explosion", "violence", "jail", "rape", "scandal", "fraud", "corrupt",
                 "murder", "decline", "lose", "loss", "fail", "recession", "inflation", "depression",
                 "crash", "collapse", "impeached", "quarantine", "laid off", "hantavirus",
                 "outbreak", "strike", "death toll", "mistrial", "indictment"],
    "positive_zh": ["胜利", "和平", "成功", "达成", "协议", "批准", "发布", "突破", "获奖",
                    "庆", "喜", "好", "发声", "回归", "守护", "新高", "和解"],
    "negative_zh": ["死亡", "战争", "攻击", "枪击", "爆炸", "火灾", "逮捕", "入狱", "腐败",
                    "丑闻", "暴跌", "倒闭", "失败", "抗议", "冲突", "威胁", "灾难", "嫖娼",
                    "伤害", "凶杀", "遇袭", "跌", "沦", "禁", "骗", "盲道", "疫情"],
}

def normalize_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\u4e00-\u9fff\s]', ' ', text)
    return text

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

def compute_trend_score(item):
    content = item.get("content", "")
    m = re.search(r'🔥\s*([0-9,]+)', content)
    if m:
        return int(m.group(1).replace(',', ''))
    return 0

def extract_heat_from_content(content):
    """Parse heat from enriched content fields"""
    if not content:
        return 0
    m = re.search(r'🔥\s*([0-9,]+)', content)
    if m:
        return int(m.group(1).replace(',', ''))
    return 0

# 话题聚类映射
def topic_key(item):
    title = item.get("title", "")
    content = item.get("content", "")
    whole = (title + " " + content).lower()
    
    maps = [
        # 中美元首会晤/特朗普访华
        (["中美元首会晤", "trump", "xi", "beijing", "china summit", "trump's learning curve",
          "trump leaves beijing", "trump and xi conclude", "secret garden",
          "trump's china", "trump's beijing", "trump goes to china",
          "nvidia's future in china", "trump and boeing"], "特朗普访华/中美元首会晤"),

        # 台湾问题
        (["taiwan", "台湾"], "特朗普警告台湾问题"),

        # 伊朗局势/霍尔木兹海峡
        (["iran", "strait of hormuz", "hormuz", "iran war", "iran ceasefire",
          "iran says it cannot trust", "no point in continuing iran",
          "iran announces strait", "oil prices rise as trump-xi",
          "executions surge in iran", "gas stations", "tank readers"], "伊朗局势/霍尔木兹海峡"),

        # 俄乌战争
        (["ukraine", "ukrainian", "russia invasion", "zelenskyy", "kyiv",
          "russian strike", "russian drones", "russia may use belarus",
          "prisoner swap goes ahead", "killer robots", "russia drones",
          "moscow bans", "zelenskyy russians preparing", "death toll in kyiv",
          "supply robots", "day 1541"], "俄乌战争"),

        # 黎巴嫩/以色列
        (["lebanon", "hezbollah", "israel strike"], "黎巴嫩/以色列冲突"),

        # 加沙/哈马斯
        (["gaza", "hamas", "al-haddad", "haddad", "netanyahu"], "加沙/哈马斯冲突"),

        # 古巴
        (["cuba", "raul castro", "castro indictment", "cia chief visits cuba"], "古巴危机"),

        # 埃博拉
        (["ebola", "congo outbreak"], "刚果埃博拉疫情"),

        # 马尔代夫潜水事故
        (["maldives", "scuba dive", "five italian", "cave scuba"], "马尔代夫潜水事故"),

        # 哈维·韦恩斯坦
        (["weinstein", "mistrial"], "韦恩斯坦性侵案"),

        # 德国总理默茨
        (["merz", "german leader", "german chancellor"], "德国总理默茨"),

        # 黑客攻击加油站
        (["hacker", "tank reader", "gas station", "fuel storage"], "伊朗黑客入侵美国加油站"),

        # Pentagon平民死亡
        (["pentagon", "civilian death"], "五角大楼平民保护项目"),

        # 最高法院堕胎药
        (["alito", "abortion pill", "dobbs"], "最高法院堕胎药裁决"),

        # 股市/油价/债市
        (["stock market", "dow", "s&p", "nasdaq", "oil prices", "inflation jitters",
          "global bonds", "30-year treasury", "bond"], "全球经济/通胀恐慌"),

        # 科罗拉多减刑
        (["colorado governor", "tina peters"], "科罗拉多州长减刑"),

        # 弗吉尼亚选区
        (["virginia", "voting map", "supreme court rejects"], "最高法院否决弗吉尼亚选区"),

        # Nvidia中国
        (["nvidia", "chip"], "英伟达中国市场"),

        # 墨西哥贩毒集团
        (["drug cartel", "sinaloa", "mexican"], "墨西哥贩毒集团"),

        # 刚果遣返移民
        (["congo", "deport", "congolese hotel"], "特朗普遣返移民到刚果"),

        # 巴勒斯坦阿巴斯
        (["abbas", "palestinian leader", "fatah"], "巴勒斯坦阿巴斯"),

        # 澳大利亚反犹太
        (["antisemitism", "bondi", "australian jews"], "澳大利亚反犹太调查"),

        # 死刑伊朗
        (["execution iran"], "伊朗死刑激增"),

        # Xbox改名
        (["xbox", "xbox"], "Xbox改名"),

        # 冰激凌召回
        (["ice cream", "recall", "metal contamination"], "FDA冰淇淋召回"),

        # 智慧产品
        (["smart product", "smart products"], "智能产品沦为智商税"),

        # 伊利雅特木乃伊
        (["iliad", "mummy", "egyptian mummy", "archaeologist"], "埃及木乃伊与荷马史诗"),

        # 反移民AI视频
        (["anti-immigration", "ai video", "overseas faker"], "反移民AI虚假视频"),

        # 俄罗斯治安会
        (["russian vigilante", "russkaya obschina", "brutal raid"], "俄罗斯治安会暴力行动"),

        # AI恋童癖钓鱼
        (["paedophile", "pedophile", "vigilante trap"], "AI钓鱼执法恋童癖"),

        # 欧洲歌唱大赛/爱尔兰
        (["eurovision", "ireland"], "爱尔兰抵制欧洲歌唱大赛"),

        # 世界杯酒店
        (["world cup", "hotel", "boom"], "美国世界杯酒店冷清"),

        # 纽约时报起诉
        (["new york times", "israel threatens to sue"], "以色列威胁起诉纽约时报"),

        # CIA对墨西哥
        (["terrorism law", "mexican official", "justice dept aims"], "美国用反恐法打击墨西哥官员"),

        # Kataib Hezbollah
        (["kataib hezbollah", "iraqi proxy"], "伊拉克真主党旅"),

        # Mengele
        (["mengele", "auschwitz", "angel of death"], "瑞士公开门格勒档案"),

        # 全球变暖
        (["record global temperature", "el niño", "global temperature"], "全球创纪录高温预警"),

        # NY非法摩托车
        (["motorbike", "new york city crime", "illegal motorbike"], "纽约市铲除非法摩托车"),

        # 法官去世
        (["cerdini", "nazi", "klaus barbie"], "纳粹审判法官去世"),

        # 特朗普金卡/IRS
        (["irs", "slush fund", "trump irs"], "IRS诉讼和解争议"),

        # 共和党议会
        (["capitol agenda", "gop", "ballroom"], "国会共和党预算"),

        # 盲道摆拍
        (["盲道", "摆拍", "盲道被撞", "薛之谦"], "女孩盲道被撞摆拍事件"),

        # 退礼服女孩
        (["退礼服", "礼服女孩", "合唱团已报案", "道歉"], "退礼服女孩事件"),

        # 江豚
        (["江豚"], "江豚回归"),

        # 金价/英伟达
        (["金价", "英伟达"], "金价/英伟达下跌"),

        # 奔跑吧
        (["奔跑吧"], "奔跑吧14收视创新高"),

        # 药店骗保
        (["药店", "骗保", "串药"], "多家药店骗保被约谈"),

        # 新娘回应
        (["新娘", "婚礼没敬酒", "敬酒宾客"], "新娘回应婚礼敬酒"),

        # 樊振东
        (["樊振东"], "樊振东训练"),

        # 白鹿
        (["白鹿"], "白鹿卢昱晓营业"),

        # 李冰冰
        (["李冰冰"], "李冰冰戛纳红毯"),

        # 罗永浩
        (["罗永浩"], "罗永浩怼保时捷"),

        # 美国记者豆汁
        (["豆汁", "美国记者"], "美国记者品北京豆汁"),

        # 小鹿九尾
        (["小鹿", "九尾"], "小鹿九尾"),

        # AI表情包
        (["包浆", "表情包", "ai救了"], "AI修复包浆表情包"),

        # 马刺森林狼
        (["马刺", "森林狼"], "马刺vs森林狼"),

        # 大车选色
        (["大车选紫色"], "大车选紫色"),

        # 蒋毅
        (["蒋毅", "赵樱子"], "蒋毅赵樱子热舞"),

        # 流量撑不起演员
        (["流量", "演员的底气"], "流量撑不起演员底气"),

        # 金鹰奖
        (["金鹰奖"], "金鹰奖提名预测"),

        # 丁程鑫
        (["丁程鑫", "泰国"], "丁程鑫泰国"),

        # 王濛
        (["王濛", "萧蔷", "孙怡"], "王濛孙怡综艺"),

        # 女子减重
        (["174斤", "减到95斤", "减重"], "女子减重174斤"),

        # 何宣林
        (["何宣林", "师姐帮唱"], "何宣林退出师姐帮唱"),
    ]

    for patterns, key in maps:
        if any(p in whole for p in patterns):
            return key
    return None


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw = json.load(f)

# 按话题聚类
topic_map = OrderedDict()

for item in raw:
    key = topic_key(item)
    if not key:  # fallback for unmatched items
        key = item["title"][:40]

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

    # 主来源优先
    source_priority = ["微博热搜", "Google News Top", "BBC News World", "NYT World", "Reddit WorldNews"]
    primary = next((s for s in source_priority if s in unique_sources), unique_sources[0])

    top_item = max(topic["items"], key=lambda x: compute_trend_score(x) if compute_trend_score(x) > 0 else len(x.get("content", "")))

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

# 排序：交叉源数高→低，热度高→低
processed.sort(key=lambda x: (-x["source_count"], -x["heat"]))
emotion_data.sort(key=lambda x: -x["heat"])

stats = {
    "date": "2026-05-17",
    "total_topics": len(processed),
    "🔥_topics": sum(1 for x in processed if x["emoji"] == "🔥"),
    "🟡_topics": sum(1 for x in processed if x["emoji"] == "🟡"),
    "total_items": len(emotion_data),
    "positive_items": sum(1 for x in emotion_data if x["sentiment"] == "positive"),
    "negative_items": sum(1 for x in emotion_data if x["sentiment"] == "negative"),
    "neutral_items": sum(1 for x in emotion_data if x["sentiment"] == "neutral"),
}

processed_output = {"stats": stats, "topics": processed}
emotion_output = {"stats": stats, "items": emotion_data}

with open(OUTPUT_PROCESSED, "w", encoding="utf-8") as f:
    json.dump(processed_output, f, ensure_ascii=False, indent=2)

with open(OUTPUT_EMOTION, "w", encoding="utf-8") as f:
    json.dump(emotion_output, f, ensure_ascii=False, indent=2)

print(f"✅ Processed: {OUTPUT_PROCESSED}")
print(f"✅ Emotion:   {OUTPUT_EMOTION}")
print(f"   Date:      2026-05-17")
print(f"   Topics:    {stats['total_topics']} (🔥 {stats['🔥_topics']}, 🟡 {stats['🟡_topics']})")
print(f"   Items:     {stats['total_items']} (😊{stats['positive_items']} 😠{stats['negative_items']} 😐{stats['neutral_items']})")