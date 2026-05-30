#!/usr/bin/env python3
"""
generate_weekly_github.py - GitHub 周报（增强版）
读取最近 7 天的 github_daily_*.json，聚合周报：
- 对本项目自动分类（AI工具/开发工具/框架/学习资源等）
- 识别本周主题趋势与语言分布
- 精选 highlights（3-5 条最值得关注的项目 + 原因）
- 生成有洞察的分析摘要
输出 data/weekly_github_YYYYMMDD.json（data/ + 根目录 双份）
"""

import json, logging, argparse, re, os
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "data"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ====== 分类关键词库（纯代码逻辑，不依赖 LLM）======
CATEGORY_KEYWORDS = {
    "AI工具/LLM应用": [
        "AI", "LLM", "GPT", "Claude", "大模型", "生成", "knowledge graph",
        "knowledge base", "RAG", "chatbot", "prompt", "agent",
        "transformer", "embedding", "neural", "deep learning", "machine learning",
        "vision", "NLP", "AI Video", "video generation", "short videos",
        "AI-powered", "intelligence", "smart",
    ],
    "开发工具/CLI": [
        "CLI", "tool", "convert", "format", "transpile", "linter",
        "debugger", "profiler", "dev tool", "workflow", "pipeline",
        "IDE", "editor", "terminal", "shell", "plugin", "extension",
    ],
    "框架与库": [
        "framework", "library", "SDK", "API", "runtime", "engine",
        "component", "module", "package", "middleware",
    ],
    "学习资源/教程": [
        "guide", "tutorial", "learn", "tips", "Master programming",
        "从头", "入门", "教程", "学习", "book", "course", "cheat sheet",
        "reference", "documentation",
    ],
    "数据科学/可视化": [
        "data", "analytics", "visualization", "dashboard", "chart",
        "statistics", "dataset", "database", "SQL", "pandas",
        "notebook", "science", "analysis",
    ],
    "Agent/自动化": [
        "agent", "automation", "autonomous", "workflow", "orchestrator",
        "harness", "skill", "instinct", "memory",
    ],
    "安全/DevOps": [
        "security", "devops", "deploy", "docker", "kubernetes",
        "k8s", "infrastructure", "monitoring", "testing", "CI/CD",
    ],
    "内容/文档": [
        "Markdown", "document", "writing", "blog", "publishing",
        "content", "text", "translation",
    ],
    "其他": [],
}

# 分类排序权重（用于 highlight 评分时倾斜展示重点方向）
CATEGORY_PRIORITY = {
    "AI工具/LLM应用": 5,
    "Agent/自动化": 4,
    "开发工具/CLI": 4,
    "框架与库": 3,
    "数据科学/可视化": 3,
    "学习资源/教程": 2,
    "安全/DevOps": 2,
    "内容/文档": 1,
    "其他": 0,
}


def classify_project(content, title, language):
    """根据 content 和 title 对项目进行分类"""
    text = f"{title} {content} {language}".lower()

    # 精确匹配 - 某些项目有明确的方向
    if "money" in title.lower() and ("printer" in title.lower() or "video" in title.lower()):
        return "AI工具/LLM应用"

    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
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

        # Try data/ first, then root
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


def analyze_category_trends(all_repos):
    """分析分类趋势，返回描述文字和分类分布"""
    category_dist = {}
    lang_dist = {}

    for repo in all_repos.values():
        cat = repo.get("category", "其他")
        category_dist[cat] = category_dist.get(cat, 0) + 1

        lang = repo.get("language", "").strip()
        if lang:
            lang_dist[lang] = lang_dist.get(lang, 0) + 1

    # 排序
    category_dist = dict(sorted(category_dist.items(), key=lambda x: -x[1]))
    lang_dist = dict(sorted(lang_dist.items(), key=lambda x: -x[1]))

    return category_dist, lang_dist


def generate_summary(all_repos, new_entries, persistent, category_dist, langs, top_10):
    """生成有洞察的分析摘要"""
    parts = []

    # 基础统计
    parts.append(f"本周GitHub Trending共收录 {len(all_repos)} 个热门项目")

    # 新项目动态
    if new_entries:
        parts.append(f"新上榜 {len(new_entries)} 个")

    if persistent:
        parts.append(f"持续在榜 {len(persistent)} 个")

    # 语言主导
    if langs:
        top_lang = list(langs.items())[0] if langs else None
        if top_lang:
            lang_name, lang_count = top_lang
            parts.append(f"以{lang_name}项目为主（{lang_count}个）")

    # 分类趋势
    if category_dist:
        top_cats = list(category_dist.items())[:2]
        cat_names = [f"{cat}（{count}个）" for cat, count in top_cats]
        parts.append(f"主要集中在{'、'.join(cat_names)}方向")

    # 明星项目点评
    if top_10:
        first = top_10[0]
        title_short = first["title"].split("/")[-1] if "/" in first["title"] else first["title"]
        stars = first.get("stars", 0)
        cat_name = first.get("category", "")
        reason = ""
        # 从 highlights 拿原因，或者从分类推断
        if cat_name:
            reason = f"作为本周{cat_name}方向的明星项目"
        else:
            if "AI" in title_short or "AI" in first.get("content", ""):
                reason = "凭借AI相关能力"
            else:
                reason = "凭借高关注度"
        parts.append(f"榜首{title_short}{reason}登顶（{stars} stars）")

    # 总结视角
    if category_dist:
        top_cat = list(category_dist.items())[0][0]
        if "AI" in top_cat or "Agent" in top_cat:
            parts.append("反映出开发者对AI工具和智能体的持续旺盛需求")
        elif "学习" in top_cat:
            parts.append("反映出开发者持续高涨的学习热情")
        elif "开发" in top_cat:
            parts.append("反映开发者在提升开发效率方面的持续追求")

    return "，".join(parts) + "。"


def pick_highlights(all_repos, top_ranked, n=5):
    """
    精选本周最值得关注的 3-5 个项目
    评分维度: stars、连续在榜天数、内容信息量、分类多样性
    """
    scored = []
    for title, repo in all_repos.items():
        score = 0

        # Stars 得分（对数归一化）
        stars = repo.get("stars", 0)
        score += min(stars / 500, 10)  # 500 stars = 1分，5000 stars = 10分

        # 连续在榜加分
        appearances = repo.get("appearances", 1)
        score += min(appearances, 7) * 0.3

        # 内容信息量（越具体的描述分数越高）
        content = repo.get("content", "")
        if len(content) > 150:
            score += 2
        elif len(content) > 80:
            score += 1

        # 新上榜加分（freshness）
        first_seen = repo.get("first_seen", "")
        last_seen = repo.get("last_seen", "")
        if first_seen == last_seen:
            score += 0.5

        # 分类优先级
        cat = repo.get("category", "其他")
        score += CATEGORY_PRIORITY.get(cat, 0) * 0.5

        # 标题可读性加分（避免太长的无意义标题）
        title_clean = title.replace("/", " ").strip()
        if len(title_clean) > 3 and len(title_clean) < 50:
            score += 0.5

        scored.append((score, title, repo))

    scored.sort(key=lambda x: -x[0])

    # 确保分类多样性：最多选 2 个同分类的项目
    highlights = []
    seen_categories = {}
    for score, title, repo in scored:
        cat = repo.get("category", "其他")
        if seen_categories.get(cat, 0) >= 2:
            continue
        highlights.append({
            "title": title,
            "url": repo.get("url", ""),
            "stars": repo.get("stars", 0),
            "language": repo.get("language", ""),
            "category": cat,
            "appearances": repo.get("appearances", 1),
            "content": repo.get("content", "")[:120],
            "reason": _highlight_reason(repo, score),
        })
        seen_categories[cat] = seen_categories.get(cat, 0) + 1
        if len(highlights) >= n:
            break

    return highlights


def _highlight_reason(repo, score):
    """为精选项目生成原因说明"""
    reasons = []
    stars = repo.get("stars", 0)
    appearances = repo.get("appearances", 1)
    lang = repo.get("language", "")
    content = repo.get("content", "")

    if stars >= 3000:
        reasons.append(f"⭐ 超高人气（{stars} stars）")
    elif stars >= 1000:
        reasons.append(f"🌟 高关注度（{stars} stars）")
    elif stars >= 500:
        reasons.append(f"📈 人气上升（{stars} stars）")

    if appearances >= 5:
        reasons.append(f"🔥 连续 {appearances} 天在榜")
    elif appearances >= 3:
        reasons.append(f"📆 在榜 {appearances} 天")

    if lang:
        reasons.append(f"🛠 {lang} 技术栈")

    # 从 content 找亮点
    if "AI" in content or "LLM" in content or "大模型" in content:
        reasons.append("🤖 AI/LLM 方向")
    if "agent" in content.lower() or "Agent" in content:
        reasons.append("🧠 Agent 智能体")
    if "video" in content.lower() or "short video" in content.lower() or "短视频" in content:
        reasons.append("🎬 视频生成")
    if "knowledge" in content.lower() or "知识" in content:
        reasons.append("📚 知识管理")
    if "learn" in content.lower() or "教程" in content or "guide" in content.lower():
        reasons.append("📖 学习资源")

    # 取前 3 个原因
    selected = reasons[:3]
    if not selected:
        if stars > 0:
            selected.append(f"⭐ {stars} stars 关注")
        else:
            selected.append("📌 本周新上榜")

    return "、".join(selected)


def main():
    ap = argparse.ArgumentParser(description="GitHub 周报")
    ap.add_argument("--date", "-d", default=datetime.now().strftime("%Y%m%d"))
    args = ap.parse_args()

    date_str = args.date
    date_obj = datetime.strptime(date_str, "%Y%m%d")
    week_start = (date_obj - timedelta(days=6)).strftime("%Y-%m-%d")
    week_end = date_obj.strftime("%Y-%m-%d")

    # 加载 github_daily 数据（如果不存在则尝试 github_trending）
    all_days = load_7_days(date_str, "github_daily")

    if not all_days:
        # Fallback: try github_trending
        all_days = load_7_days(date_str, "github_trending")

    if not all_days:
        logger.warning(f"⚠️ 未找到任何 GitHub 数据（最近7天无记录）")
        return

    logger.info(f"加载 {sum(len(v) for v in all_days.values())} 条 (覆盖 {len(all_days)} 天)")

    # 统计所有项目（按 repo name 去重，保留最新信息）
    all_repos = {}
    for date_key, items in sorted(all_days.items()):
        for item in items:
            title = item.get("title", "")
            if not title:
                continue
            if title not in all_repos:
                all_repos[title] = {
                    "title": title,
                    "url": item.get("url", ""),
                    "language": item.get("language", ""),
                    "content": item.get("content", ""),
                    "stars": item.get("stars", 0),
                    "stars_today": item.get("stars_today", 0),
                    "forks": item.get("forks", 0),
                    "first_seen": date_key,
                    "last_seen": date_key,
                    "appearances": 1,
                    "peak_stars": item.get("stars", 0),
                    "dates": [date_key],
                }
            else:
                repo = all_repos[title]
                repo["last_seen"] = date_key
                repo["appearances"] += 1
                if item.get("stars", 0) > repo["peak_stars"]:
                    repo["peak_stars"] = item.get("stars", 0)
                # Update to latest stats
                repo["stars"] = item.get("stars", repo["stars"])
                repo["dates"].append(date_key)
                # Update content if newer item has more detail
                new_content = item.get("content", "")
                if len(new_content) > len(repo.get("content", "")):
                    repo["content"] = new_content

    # 对每个项目进行分类
    for repo in all_repos.values():
        repo["category"] = classify_project(
            repo.get("content", ""),
            repo.get("title", ""),
            repo.get("language", ""),
        )

    # 新上榜（本周首次出现）
    new_entries = {k: v for k, v in all_repos.items() if v["first_seen"] >= week_start}

    # 连续在榜（本周出现 >= 3 天）
    persistent = {
        k: v for k, v in all_repos.items()
        if v["appearances"] >= 3 and v["first_seen"] < week_start
    }

    # 按 stars 排序
    ranked = sorted(all_repos.items(), key=lambda x: -x[1]["stars"])
    new_ranked = sorted(new_entries.items(), key=lambda x: -x[1]["stars"])
    persistent_ranked = sorted(persistent.items(), key=lambda x: -x[1]["stars"])

    # 分类分布
    category_dist, lang_dist = analyze_category_trends(all_repos)

    # 生成洞察摘要
    top_10_list = [
        {
            "title": title,
            "url": repo["url"],
            "language": repo.get("language", ""),
            "stars": repo["stars"],
            "forks": repo.get("forks", 0),
            "first_seen": repo["first_seen"],
            "appearances": repo["appearances"],
            "content": repo.get("content", ""),
            "category": repo.get("category", "其他"),
        }
        for title, repo in ranked[:10]
    ]

    summary = generate_summary(
        all_repos, new_entries, persistent,
        category_dist, lang_dist, top_10_list,
    )

    # 精选 highlights
    highlights = pick_highlights(all_repos, ranked, n=5)

    output = {
        "week_start": week_start,
        "week_end": week_end,
        "summary": summary,
        "stats": {
            "total_repos": len(all_repos),
            "new_entries": len(new_entries),
            "persistent": len(persistent),
            "languages": lang_dist,
            "categories": category_dist,
        },
        "top_10": top_10_list,
        "new_entries": [
            {
                "title": title,
                "url": repo["url"],
                "language": repo.get("language", ""),
                "stars": repo["stars"],
                "first_seen": repo["first_seen"],
                "content": repo.get("content", ""),
            }
            for title, repo in new_ranked[:10]
        ],
        "persistent": [
            {
                "title": title,
                "url": repo["url"],
                "language": repo.get("language", ""),
                "stars": repo["stars"],
                "appearances": repo["appearances"],
            }
            for title, repo in persistent_ranked[:10]
        ],
        "highlights": highlights,
    }

    # 双份输出
    out_path = DATA_DIR / f"weekly_github_{date_str}.json"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    root_out = WORKSPACE / f"weekly_github_{date_str}.json"
    with open(root_out, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ 周报完成: {out_path.name}")
    logger.info(f"   总项目: {len(all_repos)}, 新上榜: {len(new_entries)}, 持续: {len(persistent)}")
    logger.info(f"   分类分布: {category_dist}")
    logger.info(f"   精选 {len(highlights)} 条 highlights")


if __name__ == "__main__":
    main()
