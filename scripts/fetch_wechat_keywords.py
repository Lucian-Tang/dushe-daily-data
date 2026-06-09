#!/usr/bin/env python3
"""
fetch_wechat_keywords.py - 按关键词搜索微信公众号文章，输出标准格式
用于集成到有数Feed行业板块。

依赖: Node.js + cheerio (已安装)
搜索引擎: 搜狗微信搜索 (Sogou WeChat Search)
"""

import json
import hashlib
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 搜狗搜索脚本路径
SEARCH_SCRIPT = Path(__file__).parent.parent.parent / "skills" / "wechat-article-search" / "scripts" / "search_wechat.js"

# 预制关键词（每天自动抓）
DEFAULT_KEYWORDS = ["具身机器人", "自动驾驶", "具身智能"]

# 来源名称映射
KEYWORD_SOURCE = {
    "具身机器人": "公众号·具身机器人",
    "自动驾驶": "公众号·自动驾驶",
    "具身智能": "公众号·具身智能",
}

def uid(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:8]

def search_wechat(keyword: str, count: int = 10, resolve_url: bool = False) -> list:
    """调用 Node.js 搜狗微信搜索脚本"""
    cmd = ["node", str(SEARCH_SCRIPT), keyword, "-n", str(count)]
    if resolve_url:
        cmd.append("-r")
    
    logger.info(f"🔍 搜索微信: {keyword} (count={count}, resolve_url={resolve_url})")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            logger.warning(f"⚠ 搜索 '{keyword}' 失败: {r.stderr[:200]}")
            return []
        # 解析 JSON 输出（搜索 JSON 边界）
        text = r.stdout.strip()
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            logger.warning(f"⚠ 无法解析搜索结果: {r.stdout[:200]}")
            return []
        json_str = text[start:end+1]
        data = json.loads(json_str)
        articles = data.get("articles", [])
        logger.info(f"  → 获取 {len(articles)} 条")
        return articles
    except subprocess.TimeoutExpired:
        logger.warning(f"⚠ 搜索 '{keyword}' 超时")
        return []
    except Exception as e:
        logger.warning(f"⚠ 搜索 '{keyword}' 异常: {e}")
        return []

def to_standard_format(articles: list, keyword: str, date_str: str) -> list:
    """转换为有数Feed标准格式"""
    source_name = KEYWORD_SOURCE.get(keyword, f"公众号·{keyword}")
    items = []
    for art in articles:
        title = art.get("title", "")
        summary = art.get("summary", "")
        url = art.get("url", "")
        pub_time = art.get("datetime", "")
        
        item = {
            "uid": f"wx{uid(title + url)}",
            "title": title,
            "content": summary[:200],
            "quote": summary[:100],
            "url": url,
            "source": source_name,
            "published": pub_time or date_str,
        }
        items.append(item)
    return items

def main():
    import argparse
    parser = argparse.ArgumentParser(description="微信公众号关键词文章采集")
    parser.add_argument("--keywords", type=str, help="关键词逗号分隔，默认: 具身机器人,自动驾驶")
    parser.add_argument("--count", type=int, default=10, help="每个关键词获取文章数")
    parser.add_argument("--resolve", action="store_true", help="解析真实URL（较慢但可直链访问）")
    parser.add_argument("--output", type=str, help="输出文件路径")
    parser.add_argument("--dry-run", action="store_true", help="仅打印，不生成文件")
    args = parser.parse_args()
    
    keywords = [k.strip() for k in args.keywords.split(",")] if args.keywords else DEFAULT_KEYWORDS
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    compact_date = datetime.now().strftime("%Y%m%d")
    
    all_items = []
    for kw in keywords:
        articles = search_wechat(kw, count=args.count, resolve_url=args.resolve)
        items = to_standard_format(articles, kw, date_str)
        all_items.extend(items)
        logger.info(f"  {kw}: {len(items)} 条")
    
    # 去重（按title去重，跨关键词可能有重复）
    seen = set()
    unique_items = []
    for item in all_items:
        key = item["uid"]
        if key not in seen:
            seen.add(key)
            unique_items.append(item)
    
    logger.info(f"📊 总计 {len(all_items)} 条 → 去重后 {len(unique_items)} 条")
    
    output = {
        "section": "wechat_industry",
        "date": compact_date,
        "keywords": keywords,
        "count": len(unique_items),
        "items": unique_items,
    }
    
    if args.dry_run:
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return
    
    if args.output:
        out_path = Path(args.output)
    else:
        out_path = Path(__file__).parent.parent / "data" / f"wechat_industry_{compact_date}.json"
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    logger.info(f"✅ 已保存: {out_path}")

if __name__ == "__main__":
    main()
