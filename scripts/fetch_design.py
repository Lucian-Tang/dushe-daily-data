#!/usr/bin/env python3
"""fetch_design.py - 产品设计日报信源抓取 v1"""
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
    {"name":"Smashing Magazine","url":"https://www.smashingmagazine.com/feed/","type":"rss","category":"ui-ux","lang":"en"},
    {"name":"UX Collective","url":"https://uxdesign.cc/feed","type":"rss","category":"ui-ux","lang":"en"},
    {"name":"ProductHunt Tech","url":"https://www.producthunt.com/feed?category=tech","type":"rss","category":"product","lang":"en"},
    {"name":"ProductHunt Design Tools","url":"https://www.producthunt.com/feed?topic=design-tools","type":"rss","category":"product","lang":"en"},
    {"name":"Awwwards","url":"https://www.awwwards.com/blog/feed","type":"rss","category":"inspiration","lang":"en"},
    {"name":"Design-Milk","url":"https://design-milk.com/feed/","type":"rss","category":"inspiration","lang":"en"},
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
    async with httpx.AsyncClient(headers={"User-Agent":"DesignDailyBot/1.0"}, follow_redirects=True, timeout=30) as session:
        tasks = [fetch_rss(session, s) for s in SOURCES]
        results = await asyncio.gather(*tasks)

    all_articles = [a for sub in results for a in sub]
    seen = set(); unique = []
    for a in all_articles:
        k = hashlib.md5(f"{a['title']}|{a['source']}".encode()).hexdigest()
        if k not in seen: seen.add(k); unique.append(a)

    date = datetime.now().strftime("%Y%m%d")
    path = DATA_DIR / f"raw_design_{date}.json"
    json.dump(unique, open(path,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    logger.info(f"完成 {len(unique)} 条 → {path}")

if __name__ == "__main__":
    asyncio.run(main())
