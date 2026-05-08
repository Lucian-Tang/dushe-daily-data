#!/usr/bin/env python3
"""Reddit r/startups + r/entrepreneur via RSS (old.reddit.com with Scrapling anti-bot)"""
import json, os, sys
from datetime import datetime
from scrapling import Fetcher

OUT_DIR = os.path.expanduser("~/.openclaw/workspace/data/opportunities/reddit")
os.makedirs(OUT_DIR, exist_ok=True)

def fetch_rss(fetcher, sub):
    """Fetch subreddit RSS feed"""
    url = f"https://www.reddit.com/r/{sub}/top/.rss?t=week&limit=10"
    try:
        resp = fetcher.get(url)
        return resp.text
    except Exception as e:
        print(f"  {sub}: {e}", file=sys.stderr)
        return None

def parse_rss(xml_text, sub):
    """Parse Reddit RSS XML"""
    from scrapling.parser import Adaptor
    page = Adaptor(xml_text)
    posts = []
    for entry in page.css('entry'):
        try:
            title_el = entry.css('title')
            title = title_el[0].text.strip() if title_el else ""
            
            link_el = entry.css('link')
            link = link_el[0].get('href', '') if link_el else ""
            
            if title and link:
                posts.append({
                    "title": title,
                    "url": link,
                    "subreddit": sub
                })
        except Exception:
            continue
    return posts

def main():
    fetcher = Fetcher()
    all_posts = []
    
    for sub in ['startups', 'Entrepreneur']:
        print(f"  Fetching r/{sub}...")
        xml_data = fetch_rss(fetcher, sub)
        if xml_data and len(xml_data) > 100:
            posts = parse_rss(xml_data, sub)
            all_posts.extend(posts)
            print(f"    {len(posts)} posts")
        else:
            print(f"    ❌ Blocked (datacenter IP)")

    today = datetime.now().strftime("%Y-%m-%d")
    out = {"date": today, "source": "reddit", "count": len(all_posts), "items": all_posts}
    with open(f"{OUT_DIR}/{today}.json", 'w') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"✅ Reddit: {len(all_posts)} posts total")

if __name__ == "__main__":
    main()
