#!/usr/bin/env python3
"""fetch_design.py - 产品设计日报信源抓取 v2 (with retry + fallback)"""
import asyncio, json, hashlib, logging, re, sys, shutil
from datetime import datetime, timedelta
from pathlib import Path
import httpx, feedparser

WORKSPACE = Path(__file__).parent.parent
LOG_DIR = WORKSPACE / "logs"
DATA_DIR = WORKSPACE / "data"
ALERT_FILE = LOG_DIR / "fetch_alerts.log"
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SOURCES = [
    {"name": "Smashing Magazine", "url": "https://www.smashingmagazine.com/feed/", "type": "rss", "category": "ui-ux", "lang": "en"},
    {"name": "UX Collective", "url": "https://uxdesign.cc/feed", "type": "rss", "category": "ui-ux", "lang": "en"},
    {"name": "ProductHunt Tech", "url": "https://www.producthunt.com/feed?category=tech", "type": "rss", "category": "product", "lang": "en"},
    {"name": "ProductHunt Design Tools", "url": "https://www.producthunt.com/feed?topic=design-tools", "type": "rss", "category": "product", "lang": "en"},
    {"name": "Awwwards", "url": "https://www.awwwards.com/blog/feed", "type": "rss", "category": "inspiration", "lang": "en"},
    {"name": "Design-Milk", "url": "https://design-milk.com/feed/", "type": "rss", "category": "inspiration", "lang": "en"},
]

ALERT_PREFIX = "[fetch_design]"
RETRY_DELAY = 30  # seconds


def write_alert(level: str, message: str):
    """Write alert to both stdout and the shared alert file."""
    ts = datetime.now().isoformat()
    line = f"{ts} [{level}] {ALERT_PREFIX} {message}"
    # stderr — printed for cron/pipe capture
    print(line, file=sys.stderr, flush=True)
    # shared alert file — append
    with open(ALERT_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def fallback_to_yesterday(raw_prefix: str, today: str) -> bool:
    """
    Copy yesterday's raw JSON as today's.
    Returns True on success, False if yesterday's file is also missing.
    """
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    src = DATA_DIR / f"{raw_prefix}_{yesterday}.json"
    dst = DATA_DIR / f"{raw_prefix}_{today}.json"

    if src.exists():
        shutil.copy2(src, dst)
        logger.warning(f"⚠️ 回退：复制昨日数据 {src.name} → {dst.name}")
        write_alert("WARNING",
            f"所有信源获取失败，已回退至昨日数据 {src.name} → {dst.name}")
        return True
    else:
        logger.critical(f"❌ 回退失败：昨日数据 {src.name} 也不存在")
        write_alert("CRITICAL",
            f"所有信源获取失败，且昨日数据 {src.name} 不存在！{dst.name} 将为空文件")
        # Still write empty file so downstream doesn't crash on FileNotFound
        json.dump([], open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        return False


async def fetch_rss(session, src):
    try:
        resp = await session.get(src["url"], timeout=20, follow_redirects=True)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        articles = []
        for e in feed.entries:
            content = re.sub(r'<[^>]+>', '', e.get("summary", "") or e.get("description", "") or "").strip()[:200]
            articles.append({
                "title": e.get("title", "").strip(),
                "url": e.get("link", ""),
                "source": src["name"],
                "category": src["category"],
                "lang": src["lang"],
                "content": content,
                "published": str(e.get("published", "") or datetime.now().isoformat())
            })
        logger.info(f"  ✅ [{src['name']}] {len(articles)} 条")
        return (src, articles, True)
    except Exception as e:
        logger.warning(f"  ❌ [{src['name']}] 失败: {e}")
        return (src, [], False)


async def main():
    source_names = [s["name"] for s in SOURCES]
    logger.info(f"🚀 开始抓取 design 信源 ({len(SOURCES)} 个): {', '.join(source_names)}")

    # ── Round 1: fetch all sources in parallel ──
    async with httpx.AsyncClient(
        headers={"User-Agent": "DesignDailyBot/2.0"},
        follow_redirects=True,
        timeout=30
    ) as session:
        tasks = [fetch_rss(session, s) for s in SOURCES]
        results = await asyncio.gather(*tasks)

    # Collect per-source stats
    all_articles = []
    failed_sources = []
    for src, articles, ok in results:
        all_articles.extend(articles)
        if not ok:
            failed_sources.append(src)
        elif len(articles) == 0 and ok:
            # HTTP succeeded but feed had 0 entries — treat as soft failure
            logger.warning(f"  ⚠️  [{src['name']}] HTTP 成功但 0 条文章")
            failed_sources.append(src)

    total_before_retry = len(all_articles)

    # ── Round 2: retry failed sources after delay ──
    if failed_sources and total_before_retry == 0:
        logger.warning(f"⏳ 首轮 0 条，{RETRY_DELAY}s 后重试 {len(failed_sources)} 个失败信源...")
        await asyncio.sleep(RETRY_DELAY)

        async with httpx.AsyncClient(
            headers={"User-Agent": "DesignDailyBot/2.0 (retry)"},
            follow_redirects=True,
            timeout=30
        ) as session:
            retry_tasks = [fetch_rss(session, s) for s in failed_sources]
            retry_results = await asyncio.gather(*retry_tasks)

        retry_failed = []
        for src, articles, ok in retry_results:
            all_articles.extend(articles)
            if not ok or len(articles) == 0:
                retry_failed.append(src)
                logger.warning(f"  🔁 [{src['name']}] 重试仍失败" + (f": {len(articles)} 条" if ok else ""))
        failed_sources = retry_failed

    # ── Deduplicate ──
    seen = set()
    unique = []
    for a in all_articles:
        k = hashlib.md5(f"{a['title']}|{a['source']}".encode()).hexdigest()
        if k not in seen:
            seen.add(k)
            unique.append(a)

    date = datetime.now().strftime("%Y%m%d")
    path = DATA_DIR / f"raw_design_{date}.json"

    # ── Summary ──
    ok_count = len(SOURCES) - len(failed_sources)
    logger.info(
        f"📊 信源汇总: {ok_count}/{len(SOURCES)} 成功, "
        f"首轮 {total_before_retry} 条, 去重后 {len(unique)} 条"
    )
    if failed_sources:
        failed_names = [s["name"] for s in failed_sources]
        logger.warning(f"⚠️  失败信源: {', '.join(failed_names)}")

    # ── Fallback if all empty ──
    if len(unique) == 0:
        success = fallback_to_yesterday("raw_design", date)
        if not success:
            # yesterday also missing — write empty and raise exit code
            logger.critical("❌ CRITICAL: 无数据且无昨日备份，写入空文件")
            sys.exit(1)
        # fallback succeeded — file was already written by fallback_to_yesterday
    else:
        json.dump(unique, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        logger.info(f"✅ 完成 {len(unique)} 条 → {path}")

    # ── Final report ──
    if failed_sources:
        write_alert("WARNING",
            f"部分信源失败 ({len(failed_sources)}/{len(SOURCES)}): "
            + ", ".join(s["name"] for s in failed_sources))


if __name__ == "__main__":
    asyncio.run(main())
