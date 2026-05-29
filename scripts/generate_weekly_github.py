#!/usr/bin/env python3
"""
generate_weekly_github.py - GitHub 周报
读取最近 7 天的 github_daily_*.json，聚合周报：
- 本周新上榜项目
- 排名变化分析
输出 data/weekly_github_YYYYMMDD.json（data/ + 根目录 双份）
"""

import json, logging, argparse, re, os
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "data"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


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
                }
            else:
                repo = all_repos[title]
                repo["last_seen"] = date_key
                repo["appearances"] += 1
                if item.get("stars", 0) > repo["peak_stars"]:
                    repo["peak_stars"] = item.get("stars", 0)
                # Update to latest stats
                repo["stars"] = item.get("stars", repo["stars"])

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

    # 生成摘要
    summary_parts = [
        f"本周GitHub Trending共收录 {len(all_repos)} 个热门项目",
    ]
    if new_entries:
        summary_parts.append(f"新上榜 {len(new_entries)} 个")
    if persistent:
        summary_parts.append(f"持续热门 {len(persistent)} 个")
    summary = "，".join(summary_parts) + "。"

    # 语言分布
    langs = {}
    for repo in all_repos.values():
        lang = repo.get("language", "").strip()
        if lang:
            langs[lang] = langs.get(lang, 0) + 1

    output = {
        "week_start": week_start,
        "week_end": week_end,
        "summary": summary,
        "stats": {
            "total_repos": len(all_repos),
            "new_entries": len(new_entries),
            "persistent": len(persistent),
            "languages": dict(sorted(langs.items(), key=lambda x: -x[1])),
        },
        "top_10": [
            {
                "title": title,
                "url": repo["url"],
                "language": repo.get("language", ""),
                "stars": repo["stars"],
                "forks": repo.get("forks", 0),
                "first_seen": repo["first_seen"],
                "appearances": repo["appearances"],
                "content": repo.get("content", ""),
            }
            for title, repo in ranked[:10]
        ],
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


if __name__ == "__main__":
    main()
