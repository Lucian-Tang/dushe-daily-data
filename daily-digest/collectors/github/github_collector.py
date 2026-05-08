#!/usr/bin/env python3
"""
GitHub Trending 采集器 — github-collector-007
使用 GitHub Search API (稳定) + Trending HTML 页面(需要登录)
"""

import json
import subprocess
from datetime import datetime, timedelta

GITHUB_API_SEARCH = "https://api.github.com/search/repositories"
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

def curl_fetch(url, timeout=15, accept="application/json"):
    ua = USER_AGENTS[0]
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-time", str(timeout),
             "-H", f"User-Agent: {ua}",
             "-H", f"Accept: {accept}",
             url],
            capture_output=True, text=True, timeout=timeout + 5
        )
        return result.stdout.strip()
    except:
        return None

def fetch_trending_by_api(limit=20):
    """通过 GitHub Search API 获取近期热门仓库（按 stars 排序）"""
    date_7d_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    url = f"{GITHUB_API_SEARCH}?q=created:>{date_7d_ago}&sort=stars&order=desc&per_page={limit}"
    
    data = curl_fetch(url)
    if not data:
        return []
    
    try:
        obj = json.loads(data)
        repos = []
        for i, repo in enumerate(obj.get("items", [])[:limit]):
            repos.append({
                "rank": i + 1,
                "name": repo.get("full_name", ""),
                "description": (repo.get("description") or "")[:200],
                "language": repo.get("language") or "N/A",
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "url": repo.get("html_url", ""),
                "created_at": repo.get("created_at", ""),
            })
        return repos
    except:
        return []

def save_json(data, filepath):
    output = {
        "timestamp": datetime.now().isoformat(),
        "source": "GitHub Search API (new repos, 7d, sorted by stars)",
        "count": len(data),
        "data": data
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    return filepath

def main():
    print("=== GitHub Trending 采集器 ===")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("📡 获取 GitHub 热门新项目（7天内，按星标排序）...")
    repos = fetch_trending_by_api(limit=25)
    
    if not repos:
        print("❌ API 获取失败")
        return
    
    print(f"   获取到 {len(repos)} 条")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = f"/root/.openclaw/workspace/daily-digest/collectors/github/github_trending_{timestamp}.json"
    save_json(repos, out_path)
    
    print(f"\n✅ 输出: {out_path}")
    print(f"   共 {len(repos)} 条\n")
    
    print("=== Top 15 ===")
    for r in repos[:15]:
        lang = r.get("language", "N/A")
        desc = r.get("description", "")[:60]
        print(f"  {r['rank']:2d}. [★{r['stars']:5d}] {r['name']}")
        print(f"       📌 {desc}")

if __name__ == "__main__":
    main()