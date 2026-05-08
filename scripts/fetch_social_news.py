#!/usr/bin/env python3
"""fetch_social_news.py v2 — 三层混合抓取(技能+API+RSS)"""
import asyncio, json, hashlib, logging, re, subprocess, os
from datetime import datetime
from pathlib import Path
import httpx, feedparser

WORKSPACE = Path(__file__).parent.parent
LOG_DIR = WORKSPACE / "logs"; DATA_DIR = WORKSPACE / "data"
LOG_DIR.mkdir(exist_ok=True); DATA_DIR.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def run_opencli(cmd, timeout=45):
    """调用 opencli 技能 (baidu/weibo/zhihu)"""
    try:
        r = subprocess.run(["opencli"] + cmd, capture_output=True, text=True, timeout=timeout, cwd=str(WORKSPACE))
        if r.returncode != 0:
            logger.warning(f"opencli {' '.join(cmd)} 失败: {r.stderr[:200]}")
            return []
        return json.loads(r.stdout) if r.stdout.strip().startswith("[") else []
    except Exception as e:
        logger.warning(f"opencli {' '.join(cmd)} 异常: {e}")
        return []

# ===== RSS 信源 (已验证可用的) =====
RSS_SOURCES = [
    {"name":"Google News Top","url":"https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en","type":"rss","category":"hotspot","lang":"en","region":"intl"},
    {"name":"BBC News World","url":"https://feeds.bbci.co.uk/news/world/rss.xml","type":"rss","category":"media","lang":"en","region":"intl"},
    {"name":"Reddit WorldNews","url":"https://www.reddit.com/r/worldnews/hot/.rss","type":"rss","category":"social","lang":"en","region":"intl"},
    {"name":"NYT World","url":"https://rss.nytimes.com/services/xml/rss/nyt/World.xml","type":"rss","category":"media","lang":"en","region":"intl"},
    {"name":"Google News China","url":"https://news.google.com/rss/search?q=China&hl=en-US&gl=US&ceid=US:en","type":"rss","category":"hotspot","lang":"en","region":"intl"},
    {"name":"Reddit China","url":"https://www.reddit.com/r/China_News/.rss","type":"rss","category":"social","lang":"en","region":"intl"},
]

# ===== 微博热搜 API (已验证) =====
async def fetch_weibo(session):
    try:
        resp = await session.get("https://weibo.com/ajax/side/hotSearch", timeout=20,
            headers={"User-Agent":"Mozilla/5.0","Referer":"https://weibo.com/"})
        resp.raise_for_status()
        items = resp.json().get("data",{}).get("realtime",[])
        articles = []
        for item in items[:30]:
            word = item.get("word","") or item.get("note","")
            hot = item.get("num","") or item.get("raw_hot","")
            # 提取热搜中的用户情绪标签
            label = item.get("label_name","") or item.get("fun_word","")
            articles.append({
                "title": word.strip(), "url": f"https://s.weibo.com/weibo?q={word}",
                "source":"微博热搜", "category":"trending", "lang":"zh", "region":"cn",
                "content": f"🔥{hot} {label}", "published": str(datetime.now().isoformat())
            })
        logger.info(f"[微博热搜] {len(articles)} 条")
        return articles
    except Exception as e:
        logger.warning(f"[微博热搜] 失败: {e}")
        return []

async def fetch_rss(session, src):
    try:
        resp = await session.get(src["url"], timeout=25, follow_redirects=True)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        articles = []
        for e in feed.entries[:20]:
            content = re.sub(r'<[^>]+>', '', e.get("summary","") or e.get("description","") or "").strip()[:150]
            articles.append({
                "title": e.get("title","").strip(), "url": e.get("link",""),
                "source": src["name"], "category": src["category"],
                "lang": src["lang"], "region": src["region"],
                "content": content,
                "published": str(e.get("published","") or datetime.now().isoformat())
            })
        logger.info(f"[{src['name']}] {len(articles)} 条")
        return articles
    except Exception as e:
        logger.warning(f"[{src['name']}] 失败: {e}")
        return []

async def main():
    # 1. 抓 opencli 技能结果（百度热榜、知乎热榜）
    logger.info("=== 技能层抓取 ===")
    baidu_items = run_opencli(["baidu-hot","--raw"])
    zhihu_items = run_opencli(["zhihu-hot","--raw"])
    for item in baidu_items:
        item["source"]="百度热榜"; item["category"]="trending"; item["lang"]="zh"; item["region"]="cn"
    for item in zhihu_items:
        item["source"]="知乎热榜"; item["category"]="trending"; item["lang"]="zh"; item["region"]="cn"
    logger.info(f"[百度热榜] {len(baidu_items)} 条 | [知乎热榜] {len(zhihu_items)} 条")

    # 2. 异步抓 RSS + API
    logger.info("=== API+RSS 层抓取 ===")
    async with httpx.AsyncClient(headers={"User-Agent":"SocialNewsBot/1.0"}, follow_redirects=True, timeout=30) as session:
        wb_task = fetch_weibo(session)
        rss_tasks = [fetch_rss(session, s) for s in RSS_SOURCES]
        results = await asyncio.gather(wb_task, *rss_tasks)

    all_articles = baidu_items + zhihu_items + [a for sub in results for a in sub]

    # 去重
    seen = set(); unique = []
    for a in all_articles:
        k = hashlib.md5(f"{a['title'][:30]}|{a['source']}".encode()).hexdigest()
        if k not in seen: seen.add(k); unique.append(a)

    date = datetime.now().strftime("%Y%m%d")
    path = DATA_DIR / f"raw_social_{date}.json"
    json.dump(unique, open(path,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    logger.info(f"完成 {len(unique)} 条 → {path} | 信源: opencli×2 + API + RSS×6 = 9")
    print(f"TOTAL:{len(unique)}")

if __name__ == "__main__":
    asyncio.run(main())