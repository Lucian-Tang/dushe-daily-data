#!/usr/bin/env python3
"""
Twitter collector for morning-news system.
Supports multiple backends: RSSHub, Nitter (if alive), or direct API.
"""
import argparse
import asyncio
import sys
from datetime import datetime
import urllib.request
import json

def fetch_via_rsshub(username: str, base_url: str = "http://localhost:1200") -> list:
    """Fetch tweets via local RSSHub instance."""
    url = f"{base_url}/twitter/user/{username}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            content = r.read().decode('utf-8')
        # Simple RSS parsing - extract titles from item entries
        tweets = []
        import re
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
        for item in items[:20]:
            title_match = re.search(r'<title>(.*?)</title>', item)
            link_match = re.search(r'<link>(.*?)</link>', item)
            if title_match:
                title = title_match.group(1).strip()
                link = link_match.group(1).strip() if link_match else ""
                tweets.append({"text": title, "url": link})
        return tweets
    except Exception as e:
        return []

def fetch_via_nitter(username: str) -> list:
    """Try Nitter instances as fallback."""
    nitter_instances = [
        "https://nitter.privacydev.net",
        "https://nitter.poast.org",
        "https://nitter.bus-hit.top",
    ]
    for instance in nitter_instances:
        try:
            url = f"{instance}/{username}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                content = r.read().decode('utf-8')
            # Parse Nitter RSS-like output
            tweets = []
            import re
            # Nitter returns individual tweet divs
            tweet_matches = re.findall(r'<span class="tweet-content"[^>]*>(.*?)</span>', content, re.DOTALL)
            link_matches = re.findall(r'<a href="/([^/]+)/status/\d+)"[^>]*class="timestamp"', content)
            for i, tm in enumerate(tweet_matches[:20]):
                clean = re.sub(r'<[^>]+>', '', tm).strip()
                tweets.append({"text": clean, "url": f"https://twitter.com/{username}/status/unknown"})
            return tweets
        except:
            continue
    return []

def fetch_via_twscrape(username: str, limit: int = 10) -> list:
    """Fetch using twscrape (requires Twitter account)."""
    try:
        from twscrape import API
    except ImportError:
        return []

    async def _fetch():
        api = API()
        tweets = []
        async for tweet in api.user_tweets_and_replies(username, limit=limit):
            tweets.append({
                "id": tweet.id,
                "text": tweet.rawContent,
                "created_at": str(tweet.createdAt),
                "likes": tweet.likeCount,
                "retweets": tweet.retweetCount,
                "url": f"https://twitter.com/{username}/status/{tweet.id}"
            })
        return tweets

    return asyncio.run(_fetch())

def main():
    parser = argparse.ArgumentParser(description="Twitter collector")
    parser.add_argument("--user", "-u", help="Twitter username")
    parser.add_argument("--users", "-U", nargs="+", help="Multiple usernames")
    parser.add_argument("--limit", "-l", type=int, default=10)
    parser.add_argument("--backend", "-b", choices=["rsshub", "nitter", "twscrape", "auto"], default="auto")
    parser.add_argument("--rsshub-url", default="http://localhost:1200")
    parser.add_argument("--output", "-o", choices=["text", "json", "markdown"], default="text")
    args = parser.parse_args()

    users = [args.user] if args.user else args.users
    if not users:
        print("Error: --user or --users required")
        sys.exit(1)

    all_results = {}
    for username in users:
        tweets = []
        if args.backend == "twscrape":
            tweets = fetch_via_twscrape(username, args.limit)
        elif args.backend == "auto":
            # Try in order: RSSHub -> twscrape -> Nitter
            tweets = fetch_via_rsshub(username, args.rsshub_url)
            if not tweets:
                tweets = fetch_via_twscrape(username, args.limit)
            if not tweets:
                tweets = fetch_via_nitter(username)

        all_results[username] = tweets
        print(f"\n=== @{username} ({len(tweets)} tweets) ===")
        for t in tweets[:args.limit]:
            print(f"  {t.get('text', t.get('text',''))[:120]}")

    if args.output == "json":
        print(json.dumps(all_results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()