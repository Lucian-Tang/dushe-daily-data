#!/usr/bin/env python3
"""fetch_startup.py - 科技创业日报信源抓取 v1"""
import asyncio, json, hashlib, logging, re, sys
from datetime import datetime
from pathlib import Path
import httpx, feedparser

WORKSPACE = Path(__file__).parent.parent
LOG_DIR = WORKSPACE / "logs"; DATA_DIR = WORKSPACE / "data"
LOG_DIR.mkdir(exist_ok=True); DATA_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SOURCES = [
    {"name":"TechCrunch","url":"https://techcrunch.com/feed/","type":"rss","category":"startup","lang":"en"},
    {"name":"ProductHunt","url":"https://www.producthunt.com/feed","type":"rss","category":"product","lang":"en"},
    {"name":"ProductHunt Startup","url":"https://www.producthunt.com/feed?topic=tech","type":"rss","category":"startup","lang":"en"},
    {"name":"YC Hacker News","url":"https://hnrss.org/frontpage","type":"rss","category":"startup","lang":"en"},
]

async def fetch_rss(session, src):
    try:
        resp = await session.get(src["url"], timeout=20, follow_redirects=True)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        articles = []
        for e in feed.entries:
            content = re.sub(r'<[^>]+>', '', e.get("summary","") or e.get("description","") or "").strip()[:200]
            articles.append({
                "title": e.get("title","").strip(),
                "url": e.get("link",""),
                "source": src["name"], "category": src["category"],
                "lang": src["lang"], "content": content,
                "published": str(e.get("published","") or datetime.now().isoformat())
            })
        logger.info(f"[{src['name']}] {len(articles)} 条")
        return articles
    except Exception as e:
        logger.warning(f"[{src['name']}] 失败: {e}")
        return []

async def main():
    async with httpx.AsyncClient(headers={"User-Agent":"StartupDailyBot/1.0"}, follow_redirects=True, timeout=30) as session:
        tasks = [fetch_rss(session, s) for s in SOURCES]
        results = await asyncio.gather(*tasks)

    all_articles = [a for sub in results for a in sub]
    seen = set(); unique = []
    for a in all_articles:
        k = hashlib.md5(f"{a['title']}|{a['source']}".encode()).hexdigest()
        if k not in seen: seen.add(k); unique.append(a)

    date = datetime.now().strftime("%Y%m%d")
    path = DATA_DIR / f"raw_startup_{date}.json"
    json.dump(unique, open(path,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    logger.info(f"完成 {len(unique)} 条 → {path}")

if __name__ == "__main__":
    asyncio.run(main())
