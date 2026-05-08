#!/usr/bin/env python3
"""
fetch_industry.py - 行业热点抓取脚本
并行抓取多个 RSS/API 信源，去重后输出 JSON
"""

import asyncio
import json
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import feedparser

# ===================== 配置 =====================
CONFIG_PATH = Path(__file__).parent.parent / "config" / "sources.yaml"
OUTPUT_DIR = Path(__file__).parent.parent / "data"
LOG_DIR = Path(__file__).parent.parent / "logs"

TIMEOUT_SEC = 15
MAX_CONCURRENT = 5  # 并发上限，避免对信源压力太大

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "fetch.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def load_sources() -> list[dict]:
    """从 YAML 加载信源列表（Future: 等 Thomas 出信源后启用）"""
    try:
        import yaml
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config.get("sources", [])
    except Exception as e:
        logger.warning(f"YAML 加载失败 ({e})，使用默认演示信源")
        # 演示用假信源（Thomas 出信源后替换）
        return _demo_sources()


def _demo_sources() -> list[dict]:
    """演示信源——Thomas 出信源后替换"""
    return [
        {"name": "车东西", "url": "https://www.chexun.com/feed", "type": "rss", "category": "auto"},
        {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss", "type": "rss", "category": "ai"},
        {"name": "机器人大讲堂", "url": "https://www.roboleague.com/rss", "type": "rss", "category": "robot"},
    ]


def normalize_article(entry: dict, source: dict) -> dict:
    """将 RSS entry 或 API 响应归一化为统一格式"""
    # 提取标题
    title = entry.get("title", "").strip()

    # 提取链接
    url = ""
    if "link" in entry:
        url = entry["link"]
    elif "url" in entry:
        url = entry["url"]

    # 提取正文（优先 description/.summary，其次 content）
    content = (
        entry.get("summary") or entry.get("description") or entry.get("content", "")
    )
    # 清理 HTML 标签（简单版）
    import re
    content = re.sub(r"<[^>]+>", "", content).strip()[:500]  # 截断到 500 字

    # 提取时间
    published = (
        entry.get("published") or entry.get("published_parsed") or datetime.now().isoformat()
    )
    if isinstance(published, tuple):  # feedparser 的时间戳元组
        published = datetime(*published[:6]).isoformat()

    return {
        "title": title,
        "url": url,
        "source": source["name"],
        "published": str(published),
        "content": content,
        "category": source["category"],
    }


async def fetch_rss(session: httpx.AsyncClient, source: dict) -> list[dict]:
    """抓取单个 RSS 信源"""
    try:
        resp = await session.get(source["url"], timeout=TIMEOUT_SEC)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        articles = [normalize_article(e, source) for e in feed.entries]
        logger.info(f"[{source['name']}] 抓取成功，共 {len(articles)} 条")
        return articles
    except Exception as e:
        logger.warning(f"[{source['name']}] 抓取失败: {e}")
        return []


async def fetch_api(session: httpx.AsyncClient, source: dict) -> list[dict]:
    """抓取单个 API 信源"""
    try:
        resp = await session.get(source["url"], timeout=TIMEOUT_SEC)
        resp.raise_for_status()
        data = resp.json()
        # 通用解析（假设返回 list 或 {"data": list}）
        items = data if isinstance(data, list) else data.get("data", data.get("articles", []))
        return [normalize_article(item, source) for item in items]
    except Exception as e:
        logger.warning(f"[{source['name']}] API 抓取失败: {e}")
        return []


async def fetch_source(session: httpx.AsyncClient, source: dict) -> list[dict]:
    """根据信源类型分发抓取"""
    if source.get("type") == "api":
        return await fetch_api(session, source)
    return await fetch_rss(session, source)


def deduplicate(articles: list[dict]) -> list[dict]:
    """按 title + source 做 MD5 去重"""
    seen = set()
    unique = []
    for art in articles:
        key = hashlib.md5(f"{art['title']}|{art['source']}".encode()).hexdigest()
        if key not in seen:
            seen.add(key)
            unique.append(art)
    return unique


async def fetch_all(sources: list[dict]) -> list[dict]:
    """并发抓取所有信源（限流 MAX_CONCURRENT）"""
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    async with httpx.AsyncClient(follow_redirects=True, headers={
        "User-Agent": "IndustryDailyBot/1.0"
    }) as session:
        async def bounded_fetch(src):
            async with semaphore:
                return await fetch_source(session, src)
        results = await asyncio.gather(*[bounded_fetch(s) for s in sources])
    # 扁平化
    articles = [a for sublist in results for a in sublist]
    return deduplicate(articles)


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    sources = load_sources()
    logger.info(f"开始抓取 {len(sources)} 个信源...")

    articles = await fetch_all(sources)
    logger.info(f"抓取完成，共 {len(articles)} 条去重后文章")

    date_str = datetime.now().strftime("%Y%m%d")
    output_path = OUTPUT_DIR / f"raw_articles_{date_str}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    logger.info(f"已保存到 {output_path}")
    return articles


if __name__ == "__main__":
    asyncio.run(main())