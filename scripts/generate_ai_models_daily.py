#!/usr/bin/env python3
"""
generate_ai_models_daily.py - AI模型日聚合
读取 ai_models_classified_YYYYMMDD.json，按 vendor 聚合
输出 ai_models_daily_YYYYMMDD.json（data/ + 根目录 双份）
"""

import json, logging, argparse
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "data"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Vendor 元信息（与 classify_ai_models.py 保持一致）
VENDOR_META = {
    "anthropic": {"displayName": "Anthropic/Claude", "icon": "\U0001f9ec"},
    "openai": {"displayName": "OpenAI/GPT", "icon": "\U0001f52c"},
    "google": {"displayName": "Google/Gemini", "icon": "\U0001f310"},
    "alibaba": {"displayName": "阿里巴巴/Qwen", "icon": "\u2601\ufe0f"},
    "deepseek": {"displayName": "DeepSeek", "icon": "\U0001f50d"},
    "meta": {"displayName": "Meta/LLaMA", "icon": "\U0001f441\ufe0f"},
    "amazon": {"displayName": "Amazon/AWS", "icon": "\U0001f4e6"},
    "apple": {"displayName": "Apple", "icon": "\U0001f34e"},
    "mistral": {"displayName": "Mistral", "icon": "\U0001f4a8"},
    "xai": {"displayName": "xAI/Grok", "icon": "\U0001f680"},
    "microsoft": {"displayName": "Microsoft", "icon": "\U0001fa9f"},
    "other": {"displayName": "其他", "icon": "\U0001f4f0"},
}


def main():
    ap = argparse.ArgumentParser(description="AI模型日聚合")
    ap.add_argument("--date", "-d", default=datetime.now().strftime("%Y%m%d"))
    args = ap.parse_args()

    date_str = args.date
    d_long = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    input_path = DATA_DIR / f"ai_models_classified_{date_str}.json"

    if not input_path.exists():
        logger.warning(f"WARN: 输入文件不存在: {input_path}")
        return

    with open(input_path, encoding="utf-8") as f:
        items = json.load(f)

    if not isinstance(items, list):
        logger.error(f"ERR: 数据格式错误")
        return

    logger.info(f"读取 {len(items)} 条分类数据")

    # 按 vendor 分组
    models = {}
    for item in items:
        vendor = item.get("vendor", "other")
        if vendor not in models:
            meta = VENDOR_META.get(vendor, VENDOR_META["other"])
            models[vendor] = {
                "displayName": meta["displayName"],
                "icon": meta["icon"],
                "items": [],
            }

        models[vendor]["items"].append({
            "uid": item.get("uid", ""),
            "title": item.get("title", ""),
            "content": item.get("content", ""),
            "quote": item.get("quote", ""),
            "source": item.get("source", ""),
            "url": item.get("url", ""),
            "published": item.get("published", d_long),
            "direction": item.get("direction", ""),
        })

    # 排序 vendor：按条目数降序，other 放最后
    vendor_order = sorted(
        models.keys(),
        key=lambda v: (v == "other", -len(models[v]["items"])),
    )

    ordered_models = {v: models[v] for v in vendor_order}

    output = {
        "date": d_long,
        "total": len(items),
        "vendors": list(ordered_models.keys()),
        "models": ordered_models,
    }

    # 双份输出
    out_path = DATA_DIR / f"ai_models_daily_{date_str}.json"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    root_out = WORKSPACE / f"ai_models_daily_{date_str}.json"
    with open(root_out, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Build summary string
    vendor_summary = []
    for v in vendor_order:
        vendor_summary.append(f"{v}({len(models[v]['items'])})")
    logger.info(f"OK 日聚合完成: {out_path.name} ({', '.join(vendor_summary)})")


if __name__ == "__main__":
    main()
