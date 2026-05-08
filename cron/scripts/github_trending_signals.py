#!/usr/bin/env python3
"""GitHub Trending Signals Collector"""
import json
import urllib.request
import re
from datetime import datetime

OUTPUT_DIR = "/root/.openclaw/workspace/data/opportunities/github"

KEYWORDS_AI = ["AI", "ML", "LLM", "agent", "LLM", "GPT", "Claude", "RAG", "vector", "embedding", "whisper", "stable-diffusion", "vision", "multimodal"]
LANG_KEYWORDS = ["Python", "JavaScript", "TypeScript", "Go", "Rust", "Swift"]

def fetch_github_trending():
    try:
        req = urllib.request.Request(
            "https://github.com/trending?since=daily",
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36", "Accept": "text/html"}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8")

        # Parse article elements
        articles = re.findall(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
        projects = []
        for art in articles:
            # Get h2 which contains repo link
            h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', art, re.DOTALL)
            if not h2_match:
                continue
            h2html = h2_match.group(1)

            # Get href from the <a> tag inside h2
            href_match = re.search(r'href="(/[^"]+)"', h2html)
            if not href_match:
                continue
            href = href_match.group(1)

            # Get display name by stripping tags
            name = re.sub(r'<[^>]+>', ' ', h2html)
            name = re.sub(r'\s+', ' ', name).strip()

            # Description
            desc_match = re.search(r'<p[^>]*>([^<]+)</p>', art)
            desc = desc_match.group(1).strip() if desc_match else ""

            # Stars
            stars_match = re.search(r'(\d[\d,.]+)\s*stars?', art)
            stars_str = stars_match.group(1) if stars_match else "0"
            try:
                stars = int(stars_str.replace(",", ""))
            except:
                stars = 0

            # Language
            lang_match = re.search(r'programmingLanguage[^>]*>([^<]+)</span>', art)
            lang = lang_match.group(1) if lang_match else ""

            projects.append({
                "name": name,
                "href": f"https://github.com{href}",
                "description": desc,
                "stars": stars,
                "language": lang
            })
        return projects
    except Exception as e:
        print(f"Error: {e}")
        return []

def filter_signals(projects):
    signals = []
    for p in projects:
        name = p["name"].lower()
        desc = p["description"].lower()
        lang = p["language"]
        stars = p["stars"]

        if stars < 200:
            continue
        if lang not in LANG_KEYWORDS:
            continue

        text = name + " " + desc
        if not any(k.lower() in text for k in KEYWORDS_AI):
            continue

        signals.append({
            "signal_title": f"{p['name']}: {p['description'][:80]}",
            "url": p["href"],
            "score": stars,
            "source": "GitHub",
            "signal_type": "tech_breakthrough",
            "raw_summary": p["description"][:150],
            "screening_score": min(10, stars // 100),
            "status": "raw",
            "discovered_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "tags": ["GitHub", "AI", "open_source"]
        })
    return signals

def main():
    print("Fetching GitHub Trending...")
    projects = fetch_github_trending()
    print(f"Fetched {len(projects)} projects")

    signals = filter_signals(projects)
    print(f"Filtered to {len(signals)} signals")

    today = datetime.now().strftime("%Y-%m-%d")
    out = f"{OUTPUT_DIR}/{today}.json"
    with open(out, "w") as f:
        json.dump({"date": today, "source": "GitHub", "total_fetched": len(projects), "passed_filter": len(signals), "signals": signals}, f, ensure_ascii=False, indent=2)

    import os
    shared = "/root/.openclaw/workspace/shared/opportunities/github_{}".format(today)
    os.makedirs("/root/.openclaw/workspace/shared/opportunities", exist_ok=True)
    with open(shared, "w") as f:
        json.dump({"source": "GitHub", "count": len(signals), "signals": signals}, f, ensure_ascii=False)

    print(f"Saved {len(signals)} signals")

if __name__ == "__main__":
    main()
