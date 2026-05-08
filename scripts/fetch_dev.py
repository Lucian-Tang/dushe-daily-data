#!/usr/bin/env python3
"""fetch_dev.py - 开发者日报信源抓取 v2"""
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
    # === P0 必选 ===
    {"name":"HN Show HN","url":"https://hnrss.org/newest?q=Show+HN","type":"rss","category":"showcase","lang":"en"},
    {"name":"HN Front Page","url":"https://hnrss.org/frontpage","type":"rss","category":"discussion","lang":"en"},
    {"name":"开源中国 OSChina","url":"https://www.oschina.net/project/rss","type":"rss","category":"showcase","lang":"zh"},
    # lobste.rs 被墙，已移除。保持 8 源（需代理可恢复）
    # {"name":"lobste.rs","url":"https://lobste.rs/t/programming.rss","type":"rss","category":"discussion","lang":"en"},
    # === P1 推荐 ===
    {"name":"V2EX Tech","url":"https://www.v2ex.com/feed/tech.xml","type":"rss","category":"discussion","lang":"zh"},
    {"name":"V2EX Share","url":"https://www.v2ex.com/feed/create.xml","type":"rss","category":"showcase","lang":"zh"},
    {"name":"Dev.to","url":"https://dev.to/feed","type":"rss","category":"blog","lang":"en"},
    {"name":"博客园 Cnblogs","url":"https://www.cnblogs.com/rss","type":"rss","category":"blog","lang":"zh"},
    # === P2 增强 ===
    {"name":"GitHub Trending Daily","url":"https://github.com/trending?since=daily","type":"github","category":"github","lang":"en"},
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

async def fetch_github_trending(session, src):
    """GitHub Trending HTML 爬虫（无 RSS）"""
    try:
        resp = await session.get(src["url"], timeout=20, follow_redirects=True,
            headers={"Accept":"text/html","User-Agent":"DevDailyBot/1.0"})
        resp.raise_for_status()
        html = resp.text
        # 从 HTML 中提取 <h2 class="h3 lh-condensed"> 内的仓库名
        repos = re.findall(r'<h2[^>]*class="[^"]*h3[^"]*lh-condensed[^"]*"[^>]*>.*?<a[^>]*href="/([^"]+)"', html, re.DOTALL)
        articles = []
        for i, repo in enumerate(repos[:10]):
            desc_match = re.search(f'{re.escape(repo)}[^<]*</a>.*?</h2>.*?<p[^>]*class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>', html, re.DOTALL)
            desc = desc_match.group(1).strip() if desc_match else ""
            desc = re.sub(r'<[^>]+>', '', desc)[:200]
            articles.append({
                "title": repo, "url": f"https://github.com/{repo}",
                "source": src["name"], "category": src["category"],
                "lang": src["lang"], "content": desc,
                "published": str(datetime.now().isoformat())
            })
        logger.info(f"[{src['name']}] {len(articles)} 条")
        return articles
    except Exception as e:
        logger.warning(f"[{src['name']}] 失败: {e}")
        return []

async def main():
    async with httpx.AsyncClient(headers={"User-Agent":"DevDailyBot/1.0"}, follow_redirects=True, timeout=30) as session:
        tasks = []
        for s in SOURCES:
            if s["type"] == "github":
                tasks.append(fetch_github_trending(session, s))
            else:
                tasks.append(fetch_rss(session, s))
        results = await asyncio.gather(*tasks)

    all_articles = [a for sub in results for a in sub]
    seen = set(); unique = []
    for a in all_articles:
        k = hashlib.md5(f"{a['title']}|{a['source']}".encode()).hexdigest()
        if k not in seen: seen.add(k); unique.append(a)

    date = datetime.now().strftime("%Y%m%d")
    path = DATA_DIR / f"raw_dev_{date}.json"
    json.dump(unique, open(path,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    logger.info(f"完成 {len(unique)} 条 → {path}")

if __name__ == "__main__":
    asyncio.run(main())