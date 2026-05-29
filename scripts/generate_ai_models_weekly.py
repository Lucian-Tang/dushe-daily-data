#!/usr/bin/env python3
"""
generate_ai_models_weekly.py - AI模型周报
读取最近 7 天的 ai_models_classified_*.json，聚合为周报
输出 ai_models_weekly_YYYYMMDD.json（data/ + 根目录 双份）
"""

import json, logging, argparse, glob, re, os
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "data"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Vendor 元信息（与 classify_ai_models.py 保持一致）
VENDOR_META = {
    "anthropic": {"displayName": "Anthropic/Claude", "icon": "🧬"},
    "openai": {"displayName": "OpenAI/GPT", "icon": "🔬"},
    "google": {"displayName": "Google/Gemini", "icon": "🌐"},
    "alibaba": {"displayName": "阿里巴巴/Qwen", "icon": "☁️"},
    "deepseek": {"displayName": "DeepSeek", "icon": "🔍"},
    "meta": {"displayName": "Meta/LLaMA", "icon": "👁️"},
    "amazon": {"displayName": "Amazon/AWS", "icon": "📦"},
    "apple": {"displayName": "Apple", "icon": "🍎"},
    "mistral": {"displayName": "Mistral", "icon": "💨"},
    "xai": {"displayName": "xAI/Grok", "icon": "🚀"},
    "microsoft": {"displayName": "Microsoft", "icon": "🪟"},
    "other": {"displayName": "其他", "icon": "📰"},
}


def generate_summary(stats, timeline):
    """生成周报文字摘要"""
    parts = []
    vendor_counts = stats.get("by_vendor", {})

    # 找出最活跃的 3 个 vendor
    top_vendors = sorted(
        vendor_counts.items(), key=lambda x: -x[1]
    )[:3]

    if top_vendors:
        named = []
        for vk, count in top_vendors:
            meta = VENDOR_META.get(vk, {"displayName": vk})
            named.append(f"{meta['displayName']}（{count}条）")
        parts.append(f"本周最活跃：{'、'.join(named)}")

    # 方向分析
    directions = stats.get("by_direction", {})
    top_dir = max(directions, key=directions.get) if directions else ""
    if top_dir:
        parts.append(f"主要方向为{top_dir}（{directions[top_dir]}条）")

    # 总条目
    parts.insert(0, f"本周共收录AI领域动态 {stats.get('total_items', 0)} 条")

    return "。".join(parts) + "。"


def extract_date_from_file(filename):
    """从文件名中提取日期"""
    m = re.search(r'(\d{8})', filename)
    if m:
        return m.group(1)
    return None


def load_7_days(date_str):
    """加载最近 7 天的分类数据"""
    date_obj = datetime.strptime(date_str, "%Y%m%d")
    all_items = []
    timeline_dates = []

    for i in range(6, -1, -1):
        d = date_obj - timedelta(days=i)
        d_str = d.strftime("%Y%m%d")
        d_long = d.strftime("%Y-%m-%d")

        # 优先从 data/ 读
        fpath = DATA_DIR / f"ai_models_classified_{d_str}.json"
        if not fpath.exists():
            fpath = WORKSPACE / f"ai_models_classified_{d_str}.json"

        if fpath.exists():
            try:
                with open(fpath, encoding="utf-8") as f:
                    day_items = json.load(f)
                if isinstance(day_items, list) and day_items:
                    all_items.extend(day_items)
                    timeline_dates.append(d_long)
            except Exception as e:
                logger.warning(f"  跳过 {d_long}: {e}")

    return all_items, timeline_dates


def pick_highlights(items, n=5):
    """
    选择本周最重要的 n 条：
    优先级：模型发布 > 工具/平台 > 研究/论文，vendor 多样性
    """
    # 分类优先级打分
    priority = {
        "模型发布": 5,
        "工具/平台": 4,
        "研究/论文": 3,
        "应用/落地": 2,
        "政策/合规": 2,
        "行业动态": 1,
    }

    scored = []
    for item in items:
        dir_score = priority.get(item.get("direction", ""), 0)
        # 标题长度加分（长的通常更具体）
        title_len = min(len(item.get("title", "")), 100) / 100.0
        # quote 存在加分
        quote_bonus = 1 if item.get("quote", "").strip() else 0
        total = dir_score + title_len + quote_bonus
        scored.append((total, item))

    scored.sort(key=lambda x: -x[0])

    # 取前 n 条，确保 vendor 多样性（至少覆盖 3 个 vendor）
    highlights = []
    seen_vendors = set()

    # First pass: pick best one from each vendor
    for score, item in scored:
        v = item.get("vendor", "other")
        if v not in seen_vendors:
            highlights.append(item)
            seen_vendors.add(v)
        if len(highlights) >= n:
            break

    # Second pass: fill remaining slots
    if len(highlights) < n:
        for score, item in scored:
            if item not in highlights:
                highlights.append(item)
            if len(highlights) >= n:
                break

    return highlights[:n]


def main():
    ap = argparse.ArgumentParser(description="AI模型周报")
    ap.add_argument("--date", "-d", default=datetime.now().strftime("%Y%m%d"))
    args = ap.parse_args()

    date_str = args.date

    # 加载最近 7 天
    all_items, timeline_dates = load_7_days(date_str)

    if not all_items:
        logger.warning(f"⚠️ 未找到任何分类数据（最近7天无记录）")
        return

    logger.info(f"加载 {len(all_items)} 条 (覆盖 {len(timeline_dates)} 天)")

    # 统计
    by_vendor = {}
    by_direction = {}
    for item in all_items:
        v = item.get("vendor", "other")
        d = item.get("direction", "")
        by_vendor[v] = by_vendor.get(v, 0) + 1
        by_direction[d] = by_direction.get(d, 0) + 1

    # 按日期编排 timeline
    timeline = []
    for d_long in sorted(timeline_dates):
        day_items = [it for it in all_items if it.get("published", "") == d_long]
        if not day_items:
            continue

        # 按 vendor 分组当天的
        day_models = {}
        for item in day_items:
            v = item.get("vendor", "other")
            if v not in day_models:
                meta = VENDOR_META.get(v, {"displayName": v, "icon": "📰"})
                day_models[v] = {
                    "displayName": meta["displayName"],
                    "icon": meta["icon"],
                    "items": [],
                }
            day_models[v]["items"].append({
                "uid": item.get("uid", ""),
                "title": item.get("title", ""),
                "direction": item.get("direction", ""),
                "quote": item.get("quote", ""),
                "url": item.get("url", ""),
                "published": item.get("published", ""),
            })

        timeline.append({
            "date": d_long,
            "models": day_models,
        })

    # 本周亮点
    highlights = pick_highlights(all_items)

    # 构建周报
    date_obj = datetime.strptime(date_str, "%Y%m%d")
    week_start = (date_obj - timedelta(days=6)).strftime("%Y-%m-%d")
    week_end = date_obj.strftime("%Y-%m-%d")

    output = {
        "week_start": week_start,
        "week_end": week_end,
        "summary": generate_summary(
            {"total_items": len(all_items), "by_vendor": by_vendor, "by_direction": by_direction},
            timeline,
        ),
        "stats": {
            "total_items": len(all_items),
            "by_vendor": dict(sorted(by_vendor.items(), key=lambda x: -x[1])),
            "by_direction": dict(sorted(by_direction.items(), key=lambda x: -x[1])),
        },
        "timeline": timeline,
        "highlights": highlights,
    }

    # 双份输出
    out_path = DATA_DIR / f"ai_models_weekly_{date_str}.json"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    root_out = WORKSPACE / f"ai_models_weekly_{date_str}.json"
    with open(root_out, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ 周报完成: {out_path.name}")
    logger.info(f"   时间段: {week_start} ~ {week_end}")
    logger.info(f"   总条目: {len(all_items)}")

    top_vendors = sorted(by_vendor.items(), key=lambda x: -x[1])[:3]
    logger.info(f"   最活跃: {', '.join(f'{k}({v})' for k, v in top_vendors)}")


if __name__ == "__main__":
    main()
