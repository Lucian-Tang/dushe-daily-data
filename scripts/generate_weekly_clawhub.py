#!/usr/bin/env python3
"""
generate_weekly_clawhub.py - ClawHub 周报（增强版）
读取最近 7 天的 clawhub_daily_*.json，聚合周报：
- 对技能自动分类（开发工具/API集成/自动化/内容管理/数据等）
- 标记增长最快的技能并分析原因
- 精选 highlights（3-5 条最值得关注的技能 + 原因说明）
- 统计中增加 category 分布
- 生成有洞察的分析摘要
输出 data/weekly_clawhub_YYYYMMDD.json（data/ + 根目录 双份）
"""

import json, logging, argparse, re, os
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "data"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ====== 技能分类关键词库 ======
SKILL_CATEGORY_KEYWORDS = {
    "开发工具/代码管理": [
        "Git", "GitHub", "CLI", "code", "gh ", "gh.", "issue", "PR",
        "git", "dev", "programming", "debug",
    ],
    "API集成/云服务": [
        "API", "Gmail", "Calendar", "Drive", "Contacts", "Sheets",
        "Docs", "Google", "Notion", "integration", "workspace",
        "cloud", "service",
    ],
    "内容管理/笔记": [
        "Obsidian", "notes", "Markdown", "vault", "Notion",
        "knowledge", "wiki", "content", "document",
    ],
    "自动化/工作流": [
        "automate", "workflow", "pipeline", "orchestrator",
        "automation", "scheduler", "task",
    ],
    "媒体/娱乐/IoT": [
        "Sonos", "speaker", "audio", "music", "play", "volume",
        "IoT", "smart home", "media",
    ],
    "图像生成/处理": [
        "image", "Image", "picture", "photo", "generate", "edit",
        "vision", "banana", "pro",
    ],
    "语音/AI": [
        "Whisper", "speech", "voice", "text-to-speech", "STT",
        "transcribe", "translation",
    ],
    "数据/工具": [
        "weather", "forecast", "data", "fetch", "scrape",
        "download", "convert", "format",
    ],
    "文档/PDF": [
        "PDF", "document", "pdf", "doc", "file",
    ],
    "技能创建/模板": [
        "Skill", "creator", "template", "guide", "creating",
        "effective",
    ],
    "信息/搜索": [
        "search", "query", "find", "lookup", "info",
    ],
    "其他": [],
}

CATEGORY_PRIORITY = {
    "开发工具/代码管理": 4,
    "API集成/云服务": 5,
    "内容管理/笔记": 3,
    "自动化/工作流": 4,
    "媒体/娱乐/IoT": 2,
    "图像生成/处理": 3,
    "语音/AI": 5,
    "数据/工具": 3,
    "文档/PDF": 3,
    "技能创建/模板": 2,
    "信息/搜索": 2,
    "其他": 0,
}


def classify_skill(content, title):
    """根据 content 和 title 对技能进行分类"""
    text = f"{title} {content}".lower()

    scores = {}
    for category, keywords in SKILL_CATEGORY_KEYWORDS.items():
        if not keywords:
            continue
        score = sum(1 for kw in keywords if kw.lower() in text)
        if score > 0:
            scores[category] = score

    if not scores:
        return "其他"

    # 返回得分最高的分类
    return max(scores, key=scores.get)


def load_7_days(date_str, prefix):
    """加载最近 7 天的数据"""
    date_obj = datetime.strptime(date_str, "%Y%m%d")
    all_days = {}

    for i in range(6, -1, -1):
        d = date_obj - timedelta(days=i)
        d_str = d.strftime("%Y%m%d")
        d_long = d.strftime("%Y-%m-%d")

        fpath = DATA_DIR / f"{prefix}_{d_str}.json"
        if not fpath.exists():
            fpath = WORKSPACE / f"{prefix}_{d_str}.json"

        if fpath.exists():
            try:
                with open(fpath, encoding="utf-8") as f:
                    items = json.load(f)
                if isinstance(items, list) and items:
                    all_days[d_long] = items
            except Exception as e:
                logger.warning(f"  跳过 {d_long}: {e}")

    return all_days


def extract_stats_from_item(item):
    """从 item 中提取统计信息（downloads/stars/version）"""
    content = item.get("content", "")
    downloads = 0
    stars = 0

    m = re.search(r'(\d+)\s*次下载', content)
    if m:
        downloads = int(m.group(1))
    m = re.search(r'(\d+)\s*个\s*Star', content)
    if m:
        stars = int(m.group(1))

    return downloads, stars


def analyze_growth(all_skills):
    """分析技能增长趋势，返回增长列表和义务说明"""
    growth_list = []
    for title, skill in all_skills.items():
        if len(skill["history"]) >= 2:
            _, first_dl, _ = skill["history"][0]
            _, last_dl, _ = skill["history"][-1]
            growth = last_dl - first_dl
            if growth > 0:
                growth_list.append((title, growth, skill))
            elif len(skill["history"]) >= 2 and skill["downloads"] > 0:
                # Even without recorded growth, track popular ones
                growth_list.append((title, 0, skill))

    growth_list.sort(key=lambda x: -x[1])
    return growth_list


def analyze_growth_reason(title, skill, growth):
    """为增长最快的技能生成原因说明"""
    reasons = []
    content = skill.get("content", "")
    downloads = skill.get("downloads", 0)
    stars = skill.get("stars", 0)
    appearances = skill.get("appearances", 1)

    if growth > 1000:
        reasons.append(f"📈 爆发式增长（+{growth} 下载）")
    elif growth > 100:
        reasons.append(f"📈 显著增长（+{growth} 下载）")
    elif growth > 0:
        reasons.append(f"📈 持续增长（+{growth} 下载）")

    if downloads > 100000:
        reasons.append(f"🔥 总下载突破 {downloads // 10000} 万")
    if stars > 500:
        reasons.append(f"⭐ 高收藏量（{stars} Star）")

    # 从 content 提取功能关键词
    if "Google" in content or "Gmail" in content or "Calendar" in content or "Drive" in content:
        reasons.append("🔗 Google 生态整合")
    if "GitHub" in content or "git" in content or "gh " in content:
        reasons.append("🛠 开发者必备工具")
    if "weather" in content.lower():
        reasons.append("🌤 高频实用场景")
    if "PDF" in content or "pdf" in content:
        reasons.append("📄 文档处理")
    if "Notion" in content or "Obsidian" in content:
        reasons.append("📝 知识管理")
    if "Whisper" in content or "speech" in content.lower():
        reasons.append("🎤 语音处理")

    # 出现天数加分
    if appearances >= 5:
        reasons.append(f"📆 连续 {appearances} 天在榜")

    selected = reasons[:3]
    if not selected:
        if downloads > 0:
            selected.append(f"📥 {downloads} 下载量")
        else:
            selected.append("🆕 新晋热门技能")

    return "、".join(selected)


def generate_summary(all_skills, new_entries, growth_list, category_dist, top_10):
    """生成有洞察的分析摘要"""
    parts = []

    # 基础统计
    parts.append(f"本周ClawHub共收录 {len(all_skills)} 个技能")

    if new_entries:
        parts.append(f"新上榜 {len(new_entries)} 个")

    # 分类分布
    if category_dist:
        top_cats = list(category_dist.items())[:2]
        cat_desc = "、".join([f"{cat}（{count}个）" for cat, count in top_cats])
        parts.append(f"主要集中在{cat_desc}方向")

    # 增长最快
    if growth_list:
        top_grow = growth_list[0]
        title_short = top_grow[0]
        growth = top_grow[1]
        if growth > 0:
            parts.append(f"增长最快「{title_short}」（+{growth}）")
        else:
            parts.append(f"最热门「{title_short}」")

    # 总结视角
    if category_dist:
        top_cat = list(category_dist.items())[0][0]
        if "API" in top_cat or "集成" in top_cat:
            parts.append("开发者对第三方服务集成需求旺盛")
        elif "开发" in top_cat:
            parts.append("开发者工具仍是核心需求")
        elif "内容" in top_cat or "笔记" in top_cat:
            parts.append("知识管理和内容组织持续受到关注")
        elif "语音" in top_cat or "AI" in top_cat:
            parts.append("AI语音能力正在成为Agent标配")
        elif "自动化" in top_cat:
            parts.append("自动化工作流是Agent生态的主要场景")

    return "，".join(parts) + "。"


def pick_highlights(all_skills, growth_list, ranked, n=5):
    """
    精选本周最值得关注的技能
    评分维度: 下载量、增长速率、连续在榜天、收藏量、分类多样性
    """
    scored = []

    # 建立 title -> growth 映射
    growth_map = {title: growth for title, growth, _ in growth_list}

    for title, skill in all_skills.items():
        score = 0

        # 下载量（对数归一化）
        downloads = skill.get("downloads", 0)
        score += min(downloads / 20000, 10)  # 2万=1分，20万=10分

        # 增长加分
        growth = growth_map.get(title, 0)
        score += min(growth / 1000, 5)  # 1000=1分，5000=5分

        # 收藏加分
        stars = skill.get("stars", 0)
        score += min(stars / 100, 5)  # 100=1分，500=5分

        # 连续在榜加分
        appearances = skill.get("appearances", 1)
        score += min(appearances, 7) * 0.5

        # 内容信息量
        content = skill.get("content", "")
        if len(content) > 120:
            score += 1

        # 分类优先级
        cat = skill.get("category", "其他")
        score += CATEGORY_PRIORITY.get(cat, 0) * 0.5

        scored.append((score, title, skill))

    scored.sort(key=lambda x: -x[0])

    # 确保分类多样性
    highlights = []
    seen_categories = {}
    for score, title, skill in scored:
        cat = skill.get("category", "其他")
        if seen_categories.get(cat, 0) >= 2:
            continue
        highlights.append({
            "title": title,
            "url": skill.get("url", ""),
            "downloads": skill.get("downloads", 0),
            "stars": skill.get("stars", 0),
            "category": cat,
            "appearances": skill.get("appearances", 1),
            "content": skill.get("content", "")[:120],
            "growth": growth_map.get(title, 0),
            "reason": _highlight_reason(skill, growth_map.get(title, 0)),
        })
        seen_categories[cat] = seen_categories.get(cat, 0) + 1
        if len(highlights) >= n:
            break

    return highlights


def _highlight_reason(skill, growth):
    """为精选技能生成原因说明"""
    reasons = []
    downloads = skill.get("downloads", 0)
    stars = skill.get("stars", 0)
    appearances = skill.get("appearances", 1)
    content = skill.get("content", "")

    if downloads >= 150000:
        reasons.append(f"🔥 超级热门（{downloads // 10000}万+下载）")
    elif downloads >= 100000:
        reasons.append(f"🔥 热门技能（10万+下载）")
    elif downloads >= 50000:
        reasons.append(f"📊 高下载量（{downloads}次）")

    if stars >= 500:
        reasons.append(f"⭐ 高收藏（{stars} Star）")
    elif stars >= 200:
        reasons.append(f"⭐ 受欢迎（{stars} Star）")

    if growth > 500:
        reasons.append(f"📈 周增长 {growth}")
    elif growth > 100:
        reasons.append(f"📈 显著增长（+{growth}）")

    if appearances >= 5:
        reasons.append(f"📆 连续 {appearances} 天热门")

    # 功能亮点
    if "Google" in content or "Gmail" in content:
        reasons.append("🔗 Google 办公效率")
    if "GitHub" in content or "gh " in content:
        reasons.append("🛠 开发者必备")
    if "Notion" in content or "Obsidian" in content:
        reasons.append("📝 知识管理标配")
    if "weather" in content.lower():
        reasons.append("🌤 高频实用")

    selected = reasons[:3]
    if not selected:
        if downloads > 0:
            selected.append(f"📥 {downloads} 次下载")
        else:
            selected.append("🆕 新晋技能")

    return "、".join(selected)


def main():
    ap = argparse.ArgumentParser(description="ClawHub 周报")
    ap.add_argument("--date", "-d", default=datetime.now().strftime("%Y%m%d"))
    args = ap.parse_args()

    date_str = args.date
    date_obj = datetime.strptime(date_str, "%Y%m%d")
    week_start = (date_obj - timedelta(days=6)).strftime("%Y-%m-%d")
    week_end = date_obj.strftime("%Y-%m-%d")

    # 加载 clawhub_daily 数据
    all_days = load_7_days(date_str, "clawhub_daily")

    if not all_days:
        logger.warning(f"⚠️ 未找到任何 ClawHub 数据（最近7天无记录）")
        return

    logger.info(f"加载 {sum(len(v) for v in all_days.values())} 条 (覆盖 {len(all_days)} 天)")

    # 统计所有技能
    all_skills = {}
    for date_key, items in sorted(all_days.items()):
        for item in items:
            title = item.get("title", "")
            if not title:
                continue
            downloads, stars = extract_stats_from_item(item)

            if title not in all_skills:
                all_skills[title] = {
                    "title": title,
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "downloads": downloads,
                    "stars": stars,
                    "first_seen": date_key,
                    "last_seen": date_key,
                    "appearances": 1,
                    "dates": [date_key],
                    "history": [(date_key, downloads, stars)],
                }
            else:
                skill = all_skills[title]
                skill["last_seen"] = date_key
                skill["appearances"] += 1
                skill["dates"].append(date_key)
                if downloads > skill["downloads"]:
                    skill["downloads"] = downloads
                if stars > skill["stars"]:
                    skill["stars"] = stars
                skill["history"].append((date_key, downloads, stars))

                # Update content if newer has more info
                new_content = item.get("content", "")
                if len(new_content) > len(skill.get("content", "")):
                    skill["content"] = new_content

    # 对每个技能进行分类
    for skill in all_skills.values():
        skill["category"] = classify_skill(
            skill.get("content", ""),
            skill.get("title", ""),
        )

    # 新上榜
    new_entries = {k: v for k, v in all_skills.items() if v["first_seen"] >= week_start}

    # 增长分析
    growth_list = analyze_growth(all_skills)

    # 排序（按 downloads + stars 加权）
    ranked = sorted(
        all_skills.items(),
        key=lambda x: -(x[1]["downloads"] * 1 + x[1]["stars"] * 10),
    )
    new_ranked = sorted(
        new_entries.items(),
        key=lambda x: -(x[1]["downloads"] * 1 + x[1]["stars"] * 10),
    )

    # 分类分布
    category_dist = {}
    for skill in all_skills.values():
        cat = skill.get("category", "其他")
        category_dist[cat] = category_dist.get(cat, 0) + 1
    category_dist = dict(sorted(category_dist.items(), key=lambda x: -x[1]))

    # 生成摘要
    top_10_list = [
        {
            "title": title,
            "url": skill["url"],
            "downloads": skill["downloads"],
            "stars": skill["stars"],
            "first_seen": skill["first_seen"],
            "appearances": skill["appearances"],
            "content": skill.get("content", ""),
            "category": skill.get("category", "其他"),
        }
        for title, skill in ranked[:10]
    ]

    summary = generate_summary(
        all_skills, new_entries, growth_list, category_dist, top_10_list,
    )

    # 精选 highlights
    highlights = pick_highlights(all_skills, growth_list, ranked, n=5)

    # 增长最快列表（增强版：增加原因）
    enriched_growth = []
    for title, growth, skill in growth_list[:5]:
        enriched_growth.append({
            "title": title,
            "growth": growth,
            "total": skill["downloads"],
            "url": skill["url"],
            "stars": skill.get("stars", 0),
            "reason": analyze_growth_reason(title, skill, growth),
        })

    output = {
        "week_start": week_start,
        "week_end": week_end,
        "summary": summary,
        "stats": {
            "total_skills": len(all_skills),
            "new_entries": len(new_entries),
            "total_downloads": sum(s["downloads"] for s in all_skills.values()),
            "total_stars": sum(s["stars"] for s in all_skills.values()),
            "categories": category_dist,
        },
        "top_10": top_10_list,
        "new_entries": [
            {
                "title": title,
                "url": skill["url"],
                "downloads": skill["downloads"],
                "stars": skill["stars"],
                "first_seen": skill["first_seen"],
                "content": skill.get("content", ""),
            }
            for title, skill in new_ranked[:10]
        ],
        "fastest_growing": enriched_growth,
        "highlights": highlights,
    }

    # 双份输出
    out_path = DATA_DIR / f"weekly_clawhub_{date_str}.json"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    root_out = WORKSPACE / f"weekly_clawhub_{date_str}.json"
    with open(root_out, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ 周报完成: {out_path.name}")
    logger.info(f"   总技能: {len(all_skills)}, 新上榜: {len(new_entries)}")
    logger.info(f"   分类分布: {category_dist}")
    logger.info(f"   精选 {len(highlights)} 条 highlights")


if __name__ == "__main__":
    main()
