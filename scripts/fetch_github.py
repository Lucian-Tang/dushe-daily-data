#!/usr/bin/env python3
"""
fetch_github.py - 采集 GitHub Trending 今日热门项目 Top 20
Primary: GitHub Trending HTML 页面爬取（无需认证）
Fallback: GitHub REST API（需要 GITHUB_TOKEN 或 ~/.gh_token）
输出 data/github_trending_YYYYMMDD.json
"""

import os, sys, json, re, hashlib, logging
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "data"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 毒舌点评模板（GitHub Trending 专用，15-30字）
GITHUB_QUOTES = [
    "Star 数涨得比我余额宝利息还快",
    "又一个'改变世界'的仓库，先 star 为敬",
    "README 写得很唬人，代码就不知道了",
    "今天的顶流 repo，明天可能就尘封了",
    "开源界的今日爆款，保质期未知",
    "看起来厉害得不行，装着试试再说",
    "收藏癖的狂欢，生产环境的噩梦",
    "名字很有气势，星星来得也很有气势",
    "又双叒叕一个 AI 套壳工具上榜了",
    "程序员的新玩具，老板看不懂系列",
    "代码没几行，Star 先破千",
    "开源社区的热情，比这个 repo 的 README 还长",
    "点赞一时爽，落地火葬场",
    "又一个号称'All-in-One'的，光依赖就 200 个",
    "今天的 GitHub 热搜，明天的技术债",
    "新一代轮子制造机又上线了",
    "看似美好，clone 下来 2GB",
    "Star 破千只需一个好看的 README",
]


def get_token():
    """获取 GitHub API token"""
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        return token
    token_path = Path.home() / ".gh_token"
    if token_path.exists():
        return token_path.read_text().strip()
    return ""


def fetch_trending_html(date_str):
    """Method 1: 从 GitHub Trending HTML 页面爬取（无需认证）"""
    import urllib.request

    url = "https://github.com/trending?since=daily"
    try:
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "text/html",
                "User-Agent": "DevDailyBot/2.0",
            },
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        logger.warning(f"[html] 爬取失败: {e}")
        return None

    # 解析 Trending 页面：
    # 仓库链接: <a href="/owner/repo"> 在 <h2 class="h3 lh-condensed"> 内
    # 描述: <p class="col-9 ..."> 内的 text
    # 语言: <span itemprop="programmingLanguage">
    # 今日 stars: <span class="d-inline-block float-sm-right">
    # 总 stars: 页面在每个 article 的底部有 star 和 fork 计数

    # 使用 article.Box-row 分隔每个仓库
    articles = re.split(r'<article\s+class="Box-row"', html)[1:]

    items = []
    for art in articles[:20]:  # Top 20
        # 提取仓库名
        repo_m = re.search(r'<a[^>]*href="/([^/]+/[^/"]+)"', art)
        if not repo_m:
            continue
        repo = repo_m.group(1).strip()
        if repo.count("/") != 1:
            continue

        # 描述
        desc_m = re.search(r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>', art, re.DOTALL)
        desc = ""
        if desc_m:
            desc = re.sub(r'<[^>]+>', "", desc_m.group(1)).strip()[:200]

        # 编程语言
        lang_m = re.search(r'itemprop="programmingLanguage"[^>]*>([^<]*)<', art)
        language = lang_m.group(1).strip() if lang_m else ""

        # 今日 stars（格式: 1,234 stars today）
        stars_today_m = re.search(r'([\d,]+)\s+stars?\s+today', art)
        stars_today = 0
        if stars_today_m:
            stars_today = int(stars_today_m.group(1).replace(",", ""))

        # 总 stars
        stars_total_m = re.search(r'([\d,]+)\s+stars?\s*($|[^t])', art)
        stars = 0
        if stars_total_m:
            val = stars_total_m.group(1).replace(",", "")
            try:
                stars = int(val)
            except ValueError:
                stars = 0

        # forks
        forks_m = re.search(r'([\d,]+)\s+forks', art)
        forks = 0
        if forks_m:
            forks = int(forks_m.group(1).replace(",", ""))

        # 生成 uid
        key = f"{repo}|GitHub"
        uid = f"github_{hashlib.md5(key.encode()).hexdigest()[:8]}"

        # 随机毒舌点评
        import random
        quote = random.choice(GITHUB_QUOTES)

        published = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

        items.append({
            "uid": uid,
            "title": repo,
            "content": desc,
            "quote": quote,
            "source": "GitHub Trending",
            "url": f"https://github.com/{repo}",
            "language": language,
            "stars": stars,
            "stars_today": stars_today,
            "forks": forks,
            "published": published,
        })

    return items


def fetch_trending_api(date_str):
    """Method 2: 通过 GitHub REST API 搜索（fallback）"""
    token = get_token()
    if not token:
        logger.warning("[api] 无 GitHub token，无法使用 API")
        return None

    import urllib.request, urllib.parse

    # 搜索今天创建的热门项目
    yesterday_day = int(date_str[6:8]) - 1
    yesterday = f"{date_str[:4]}-{date_str[4:6]}-{str(yesterday_day).zfill(2)}"
    query = f"created:>{yesterday}&sort=stars&order=desc"
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&per_page=20"

    try:
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "User-Agent": "DevDailyBot/2.0",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.warning(f"[api] 请求失败: {e}")
        return None

    import random
    items = []
    for repo in data.get("items", [])[:20]:
        repo_full = repo.get("full_name", "")
        desc = (repo.get("description") or "")[:200]
        language = repo.get("language") or ""
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)

        key = f"{repo_full}|GitHub"
        uid = f"github_{hashlib.md5(key.encode()).hexdigest()[:8]}"

        published = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

        items.append({
            "uid": uid,
            "title": repo_full,
            "content": desc,
            "quote": random.choice(GITHUB_QUOTES),
            "source": "GitHub Trending",
            "url": repo.get("html_url", f"https://github.com/{repo_full}"),
            "language": language,
            "stars": stars,
            "stars_today": 0,  # API 不提供今日增量
            "forks": forks,
            "published": published,
        })

    return items


def main():
    date_str = datetime.now().strftime("%Y%m%d")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Method 1: HTML 爬取
    items = fetch_trending_html(date_str)

    # Method 2: API fallback
    if not items:
        logger.info("HTML 爬取失败，尝试 API fallback...")
        items = fetch_trending_api(date_str)

    if not items:
        logger.error("❌ 所有方法均失败，无法获取 GitHub Trending 数据")
        sys.exit(1)

    # 排序：按 stars 降序
    items.sort(key=lambda x: x.get("stars", 0), reverse=True)

    # 保存到 data/ 目录
    out_path = DATA_DIR / f"github_trending_{date_str}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ {len(items)} 条 → {out_path}")


if __name__ == "__main__":
    main()
