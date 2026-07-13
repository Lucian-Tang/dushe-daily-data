#!/usr/bin/env python3
"""
wechat_daily_report.py - 微信公众号每日热点报告
每天抓取指定关键词的公众号文章 → 生成飞书报告 → 归档NAS

数据源（双通道）：
  1. Sogou 微信搜索 - 主通道（专搜公众号，内容新鲜）
  2. Exa MCP (mcporter) - 备选（仅 Sogou 结果不足时）

用法:
  python3 scripts/wechat_daily_report.py --keywords "具身机器人,自动驾驶" --date 20260609
"""

import json
import logging
import subprocess
import sys
import hashlib
import os
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent.parent
REPORTS_DIR = BASE_DIR / "reports" / "wechat_daily"
SEARCH_SCRIPT = BASE_DIR / "skills" / "wechat-article-search" / "scripts" / "search_wechat.js"

# ===== 质量过滤（黑白名单）=====
# config/wechat_sources.py 必须存在，否则报错提示创建
try:
    sys.path.insert(0, str(BASE_DIR))
    from config.wechat_sources import (
        SOURCE_BLACKLIST,
        SOURCE_WHITELIST,
        TITLE_BLACKLIST_KEYWORDS,
        is_source_blacklisted,
        is_source_whitelisted,
        has_blacklisted_title_keyword,
    )
    QUALITY_GATE_ENABLED = True
    logger.info("✅ 质量门禁已加载: config/wechat_sources.py")
except ImportError as e:
    logger.warning(f"⚠️ 质量门禁未加载 (config/wechat_sources.py 不存在): {e}")
    logger.warning("  → 请先创建 BASE_DIR/config/wechat_sources.py 配置黑白名单")
    QUALITY_GATE_ENABLED = False

    # 空桩函数，确保脚本不报错
    def is_source_blacklisted(source): return False
    def is_source_whitelisted(source): return False
    def has_blacklisted_title_keyword(title): return False
    SOURCE_BLACKLIST = set()
    SOURCE_WHITELIST = set()

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

# ===== 时间过滤 =====
MAX_AGE_DAYS = 7  # 文章最大时效（天）
MAX_AGE_HOT = 3   # 热点优选时效（天）

def parse_datetime(dt_str: str):
    """尝试解析日期字符串为 datetime，失败返回 None"""
    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"]:
        try:
            return datetime.strptime(dt_str[:19].strip(), fmt).replace(tzinfo=CST)
        except (ValueError, IndexError):
            continue
    return None

def filter_by_recency(items: list, days: int = MAX_AGE_DAYS) -> list:
    """过滤掉超过 days 天的文章，并返回按时间降序排列的结果"""
    now = datetime.now(CST)
    cutoff = now - timedelta(days=days)
    filtered = []
    for item in items:
        published = item.get("published", "")
        dt = parse_datetime(published)
        if dt and dt >= cutoff:
            item["_parsed_dt"] = dt
            filtered.append(item)
        elif not dt:
            # 无时间信息的保留（但排到后面）
            item["_parsed_dt"] = datetime.min.replace(tzinfo=CST)
            filtered.append(item)
    # 按时间降序（最新在前）
    filtered.sort(key=lambda x: x["_parsed_dt"], reverse=True)
    # 清理辅助字段
    for item in filtered:
        item.pop("_parsed_dt", None)
    return filtered

def friendly_age(dt_str: str) -> str:
    """将日期转为人类可读的相对时间"""
    dt = parse_datetime(dt_str)
    if not dt:
        return dt_str[:10] if dt_str else ""
    now = datetime.now(CST)
    diff = now - dt
    if diff.total_seconds() < 0:
        return dt_str[:10]
    minutes = int(diff.total_seconds() / 60)
    if minutes < 60:
        return f"{minutes}分钟前"
    hours = int(minutes / 60)
    if hours < 24:
        return f"{hours}小时前"
    days = int(hours / 24)
    if days < 30:
        return f"{days}天前"
    return dt_str[:10]

# ===== Exa 搜索通道（备用）=====
def search_exa_wechat(query: str, count: int = 10) -> list:
    """通过 Exa MCP 搜索微信公众号文章（备用通道）"""
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

# ===== 搜狗微信搜索通道（主通道）=====
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
def generate_markdown(date_str: str, sections: dict, whitelist_stats: dict = None) -> str:
    """生成 Markdown 格式报告"""
    lines = [f"# 微信公众平台 · 每日热点报告 | {date_str}", ""]
    lines.append(f"> 生成时间: {now_cst()}")
    lines.append("")
    
    total = sum(len(items) for items in sections.values())
    lines.append(f"**关键词**: {', '.join(sections.keys())}  |  **总计**: {total} 篇文章")
    if whitelist_stats and QUALITY_GATE_ENABLED:
        top_sources = sorted(whitelist_stats.items(), key=lambda x: -x[1])[:5]
        if top_sources:
            sources_str = ", ".join(f"{s}({c}篇)" for s, c in top_sources)
            lines.append(f"🏅 优质来源: {sources_str}")
        lines.append("")
    # 过滤说明
    blacklist_hit = sum(
        1 for items in sections.values()
        for item in items
        if item.get("author", "") in SOURCE_BLACKLIST
    )
    if blacklist_hit > 0 and QUALITY_GATE_ENABLED:
        lines.append(f"🔍 质量门禁已生效: 今日过滤 {blacklist_hit} 篇低质来源")
        lines.append("")

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
            published_raw = item.get("published", "")
            age = friendly_age(published_raw)
            content = item.get("content", "")[:150]
            
            lines.append(f"### {i}. {title}")
            if url:
                lines.append(f"🔗 {url}")
            time_tag = age if age != published_raw[:10] else published_raw
            lines.append(f"📰 {author}  |  🕐 {time_tag}" if author else f"🕐 {time_tag}")
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


# ===== 质量过滤 =====
def filter_by_quality(items: list, section: str = "") -> list:
    """
    质量门禁：按来源黑名单 + 标题黑名单关键词过滤
    策略：先用严格模式过滤，如果结果不足 3 条则回退到仅过滤来源黑名单
    """
    if not QUALITY_GATE_ENABLED:
        return items

    blacklisted_sources = []
    blacklisted_titles = []
    passed = []

    for item in items:
        source = item.get("author", "")
        title = item.get("title", "")

        # 来源黑名单过滤
        if is_source_blacklisted(source):
            blacklisted_sources.append(source)
            continue

        # 标题黑名单关键词过滤（白名单来源跳过，不误杀优质号）
        if not is_source_whitelisted(source) and has_blacklisted_title_keyword(title):
            blacklisted_titles.append(title[:60])
            continue

        passed.append(item)

    filtered_out = len(items) - len(passed)
    if filtered_out > 0:
        logger.info(f"  [{section}] 质量过滤: 滤除 {filtered_out} 篇")
        logger.info(f"    - 来源黑名单 {len(blacklisted_sources)} 篇: {', '.join(set(blacklisted_sources))[:120]}")
        if blacklisted_titles:
            logger.info(f"    - 标题黑名单 {len(blacklisted_titles)} 篇")

    # 若严格过滤后不足 3 条，放宽到只滤来源黑名单（不滤标题关键词）
    if len(passed) < 3 and blacklisted_titles:
        logger.info(f"  [{section}] 严格过滤后仅 {len(passed)} 条，放宽：标题关键词降级为警告")
        relaxed = []
        for item in items:
            source = item.get("author", "")
            if not is_source_blacklisted(source):
                relaxed.append(item)
        logger.info(f"    → 放宽后 {len(relaxed)} 条")
        return relaxed

    return passed


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
        items = []
        seen_urls = set()
        
        # 主通道：搜狗微信搜索（专搜公众号，内容新鲜）
        sogou_items = search_sogou_wechat(kw, count=args.count)
        for si in sogou_items:
            url = si.get("url", "")
            if url not in seen_urls:
                items.append(si)
                seen_urls.add(url)
        
        # 如果搜狗结果不足，用 Exa 补充
        if len(items) < 3:
            logger.info(f"搜狗结果不足({len(items)}条)，尝试 Exa 补充...")
            exa_items = search_exa_wechat(kw, count=args.count)
            for ei in exa_items:
                url = ei.get("url", "")
                if url not in seen_urls:
                    items.append(ei)
                    seen_urls.add(url)

        # 时间过滤：先按热点时效过滤，不足则放宽到最大时效
        filtered = filter_by_recency(items, days=MAX_AGE_HOT)
        if len(filtered) < 3 and len(items) > len(filtered):
            logger.info(f"  {kw}: 热点时效({MAX_AGE_HOT}天)仅{len(filtered)}条，放宽到{MAX_AGE_DAYS}天")
            filtered = filter_by_recency(items, days=MAX_AGE_DAYS)
        filtered = filtered if filtered else filter_by_recency(items, days=MAX_AGE_DAYS)

        # 质量过滤（黑白名单）
        if QUALITY_GATE_ENABLED and filtered:
            filtered = filter_by_quality(filtered, section=kw)

        sections[kw] = filtered
        logger.info(f"  {kw}: 原始{len(items)}条 → 质量过滤后{len(sections[kw])}条")

    # 最终检查：如果所有板块都为空，发个警告
    total_filtered = sum(len(v) for v in sections.values())
    if total_filtered == 0:
        logger.warning("⚠️ 所有板块过滤后均为空！尝试不限制时间重新生成...")
        sections = {}
        for kw in kw_list:
            sogou_items = search_sogou_wechat(kw, count=args.count)
            sections[kw] = sogou_items
            logger.info(f"  {kw}: 不限时间共 {len(sogou_items)} 条")

    # 质量过滤报告（汇总）
    if QUALITY_GATE_ENABLED:
        for kw in list(sections.keys()):
            if not sections[kw]:
                logger.warning(f"⚠️ {kw}: 质量过滤后为空！考虑放宽黑名单或扩展搜索关键词")
                # 尝试不质量过滤重新跑一次
                logger.info(f"  → 尝试不限制黑白名单重新搜索 {kw}...")
                fallback_items = search_sogou_wechat(kw, count=args.count)
                sections[kw] = filter_by_recency(fallback_items, days=MAX_AGE_DAYS)
                logger.info(f"  → 回退后 {len(sections[kw])} 条")

    # 标记白名单来源（用于报告头部补充说明）
    whitelist_stats = {}
    for kw, items in sections.items():
        for item in items:
            author = item.get("author", "")
            if author and is_source_whitelisted(author):
                whitelist_stats[author] = whitelist_stats.get(author, 0) + 1
    
    # 生成报告
    report = generate_markdown(date_str, sections, whitelist_stats=whitelist_stats)
    
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
