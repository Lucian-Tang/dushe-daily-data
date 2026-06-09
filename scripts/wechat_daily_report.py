#!/usr/bin/env python3
"""
wechat_daily_report.py - 微信公众号每日热点报告
每天抓取指定关键词的公众号文章 → 生成飞书报告 → 归档NAS

数据源（双通道）：
  1. Exa MCP (mcporter) - 主通道
  2. Sogou 微信搜索 - 备选

用法:
  python3 scripts/wechat_daily_report.py --keywords "具身机器人,自动驾驶" --date 20260609
"""

import json
import logging
import subprocess
import sys
import hashlib
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent.parent
REPORTS_DIR = BASE_DIR / "reports" / "wechat_daily"
SEARCH_SCRIPT = BASE_DIR / "skills" / "wechat-article-search" / "scripts" / "search_wechat.js"

# ===== 关键词配置 =====
DEFAULT_KEYWORDS = [
    {"keyword": "具身机器人", "query": "site:mp.weixin.qq.com 具身机器人", "section": "具身机器人"},
    {"keyword": "自动驾驶", "query": "site:mp.weixin.qq.com 自动驾驶", "section": "自动驾驶"},
]

CST = timezone(timedelta(hours=8))

def now_cst() -> str:
    return datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S")

def today_compact() -> str:
    return datetime.now(CST).strftime("%Y%m%d")

def uid(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:8]

# ===== Exa 搜索通道 =====
def search_exa_wechat(query: str, count: int = 10) -> list:
    """通过 Exa MCP 搜索微信公众号文章"""
    import re
    search_query = f'site:mp.weixin.qq.com {query}' if "具身" in query or "自动" in query else f'site:mp.weixin.qq.com {query}'
    
    cmd = [
        "mcporter", "call",
        f'exa.web_search_exa(query: "{search_query}", numResults: {count})'
    ]
    
    logger.info(f"🔍 Exa 搜索: {query}")
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=30)
        if r.returncode != 0:
            logger.warning(f"⚠ Exa 搜索失败")
            return []
        
        # 尝试 UTF-8 解码
        try:
            output = r.stdout.decode("utf-8", errors="replace")
        except:
            output = r.stdout.decode("latin-1", errors="replace")
        
        # 解析结果
        lines = output.split("\n")
        articles = []
        current = {}
        for line in lines:
            if line.startswith("Title: "):
                if current.get("title"):
                    articles.append(current)
                current = {"title": line[7:].strip()}
            elif line.startswith("URL: ") and "url" not in current:
                current["url"] = line[5:].strip()
            elif line.startswith("Published: "):
                current["published"] = line[11:].strip()
            elif line.startswith("Author: "):
                current["author"] = line[8:].strip()
            elif line.startswith("Highlights:"):
                current["content"] = ""
            elif current.get("content") is not None:
                current["content"] += line.strip() + " "
        
        if current.get("title"):
            articles.append(current)
        
        # 过滤只保留 mp.weixin.qq.com 链接
        wechat_articles = [a for a in articles if "mp.weixin.qq.com" in a.get("url", "")]
        
        logger.info(f"  → Exa 获取 {len(articles)} 条, 微信来源 {len(wechat_articles)} 条")
        return wechat_articles
    except subprocess.TimeoutExpired:
        logger.warning(f"⚠ Exa 搜索超时")
        return []
    except Exception as e:
        logger.warning(f"⚠ Exa 搜索异常: {e}")
        return []

# ===== 搜狗微信搜索通道（备用）=====
def search_sogou_wechat(keyword: str, count: int = 10) -> list:
    """通过搜狗微信搜索（Node.js）"""
    cmd = ["node", str(SEARCH_SCRIPT), keyword, "-n", str(count)]
    logger.info(f"🔍 搜狗搜索: {keyword}")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            logger.warning(f"⚠ 搜狗搜索失败")
            return []
        text = r.stdout.strip()
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            return []
        data = json.loads(text[start:end+1])
        articles = data.get("articles", [])
        result = []
        for art in articles:
            result.append({
                "title": art.get("title", ""),
                "url": art.get("url", ""),
                "published": art.get("datetime", ""),
                "author": art.get("source", ""),
                "content": art.get("summary", ""),
            })
        logger.info(f"  → 搜狗获取 {len(result)} 条")
        return result
    except Exception as e:
        logger.warning(f"⚠ 搜狗搜索异常: {e}")
        return []

# ===== 报告生成 =====
def generate_markdown(date_str: str, sections: dict) -> str:
    """生成 Markdown 格式报告"""
    lines = [f"# 微信公众平台 · 每日热点报告 | {date_str}", ""]
    lines.append(f"> 生成时间: {now_cst()}")
    lines.append("")
    
    total = sum(len(items) for items in sections.values())
    lines.append(f"**关键词**: {', '.join(sections.keys())}  |  **总计**: {total} 篇文章")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    for keyword, items in sections.items():
        if not items:
            continue
        lines.append(f"## 📌 {keyword}")
        lines.append("")
        for i, item in enumerate(items, 1):
            title = item.get("title", "")
            url = item.get("url", "")
            author = item.get("author", "未知来源")
            published = item.get("published", "")[:10]
            content = item.get("content", "")[:150]
            
            lines.append(f"### {i}. {title}")
            if url:
                lines.append(f"🔗 {url}")
            lines.append(f"📰 {author}" + (f"  |  🕐 {published}" if published else ""))
            if content:
                content_clean = content.replace("...", "").strip()
                if content_clean:
                    lines.append(f"> {content_clean}")
            lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append(f"*报告由有数Feed 采集管线自动生成 | {now_cst()}*")
    lines.append("")
    
    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="微信公众号每日热点报告")
    parser.add_argument("--keywords", type=str, help="关键词逗号分隔")
    parser.add_argument("--count", type=int, default=10, help="每个关键词获取文章数")
    parser.add_argument("--date", type=str, help="日期 YYYYMMDD（默认今天）")
    parser.add_argument("--dry-run", action="store_true", help="仅打印报告内容")
    args = parser.parse_args()
    
    dt = args.date or today_compact()
    date_str = f"{dt[:4]}-{dt[4:6]}-{dt[6:]}"
    
    # 关键词列表
    if args.keywords:
        kw_list = [k.strip() for k in args.keywords.split(",")]
    else:
        kw_list = [d["keyword"] for d in DEFAULT_KEYWORDS]
    
    sections = {}
    for kw in kw_list:
        kw_config = next((d for d in DEFAULT_KEYWORDS if d["keyword"] == kw), None)
        items = []
        
        # 主通道：Exa
        exa_items = search_exa_wechat(kw, count=args.count)
        items.extend(exa_items)
        
        # 如果 Exa 返回不足，用搜狗补充
        if len(items) < 3:
            logger.info(f"Exa 结果不足，尝试搜狗搜索补充...")
            sogou_items = search_sogou_wechat(kw, count=args.count)
            # 去重
            seen_urls = {i.get("url") for i in items}
            for si in sogou_items:
                if si.get("url") not in seen_urls:
                    items.append(si)
                    seen_urls.add(si.get("url"))
        
        sections[kw] = items
        logger.info(f"  {kw}: 共 {len(items)} 篇文章")
    
    # 生成报告
    report = generate_markdown(date_str, sections)
    
    if args.dry_run:
        print(report)
        return
    
    # 保存本地
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    local_path = REPORTS_DIR / f"wechat_daily_report_{dt}.md"
    local_path.write_text(report)
    logger.info(f"✅ 本地报告: {local_path}")
    
    # 创建飞书文档（外部调用）
    doc_url_file = REPORTS_DIR / f"wechat_daily_report_{dt}.doc_url"
    doc_url_file.write_text("")
    logger.info(f"ℹ️ 请使用 feishu_doc create + write 将报告写入飞书")
    logger.info(f"ℹ️ 请使用 archive-to-kb.py 归档到 NAS")

if __name__ == "__main__":
    main()
