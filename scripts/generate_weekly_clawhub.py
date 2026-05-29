#!/usr/bin/env python3
"""
generate_weekly_clawhub.py - ClawHub 周报
读取最近 7 天的 clawhub_daily_*.json，聚合周报：
- 本周新上榜技能
- 下载量变化趋势
输出 data/weekly_clawhub_YYYYMMDD.json（data/ + 根目录 双份）
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
    # clawhub 数据可能包含在 content 中：
    # "已累计 1234 次下载、56 个 Star"
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
                    "history": [(date_key, downloads, stars)],
                }
            else:
                skill = all_skills[title]
                skill["last_seen"] = date_key
                skill["appearances"] += 1
                if downloads > skill["downloads"]:
                    skill["downloads"] = downloads
                if stars > skill["stars"]:
                    skill["stars"] = stars
                skill["history"].append((date_key, downloads, stars))

    # 新上榜
    new_entries = {k: v for k, v in all_skills.items() if v["first_seen"] >= week_start}

    # 增长最快（通过 history 计算下载量增量）
    growth_list = []
    for title, skill in all_skills.items():
        if len(skill["history"]) >= 2:
            _, first_dl, _ = skill["history"][0]
            _, last_dl, _ = skill["history"][-1]
            growth = last_dl - first_dl
            if growth > 0:
                growth_list.append((title, growth, skill))

    growth_list.sort(key=lambda x: -x[1])

    # 排序（按 downloads + stars 加权）
    ranked = sorted(
        all_skills.items(),
        key=lambda x: -(x[1]["downloads"] * 1 + x[1]["stars"] * 10),
    )
    new_ranked = sorted(
        new_entries.items(),
        key=lambda x: -(x[1]["downloads"] * 1 + x[1]["stars"] * 10),
    )

    # 摘要
    summary_parts = [f"本周ClawHub共收录 {len(all_skills)} 个技能"]
    if new_entries:
        summary_parts.append(f"新上榜 {len(new_entries)} 个")
    if growth_list:
        summary_parts.append(f"增长最快: {growth_list[0][0]}")
    summary = "，".join(summary_parts) + "。"

    output = {
        "week_start": week_start,
        "week_end": week_end,
        "summary": summary,
        "stats": {
            "total_skills": len(all_skills),
            "new_entries": len(new_entries),
            "total_downloads": sum(s["downloads"] for s in all_skills.values()),
            "total_stars": sum(s["stars"] for s in all_skills.values()),
        },
        "top_10": [
            {
                "title": title,
                "url": skill["url"],
                "downloads": skill["downloads"],
                "stars": skill["stars"],
                "first_seen": skill["first_seen"],
                "appearances": skill["appearances"],
                "content": skill.get("content", ""),
            }
            for title, skill in ranked[:10]
        ],
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
        "fastest_growing": [
            {
                "title": title,
                "growth": growth,
                "total": skill["downloads"],
                "url": skill["url"],
            }
            for title, growth, skill in growth_list[:5]
        ],
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
    logger.info(f"   总技能: {len(all_skills)}, 新上榜: {len(new_entries)}, 增长最快: {len(growth_list)}")


if __name__ == "__main__":
    main()
