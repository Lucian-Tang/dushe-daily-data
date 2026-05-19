#!/usr/bin/env python3
"""fetch_clawhub.py - 采集 ClawHub 技能市场的最新/热门技能"""

import subprocess, json, sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "data"


def main():
    date = datetime.now().strftime("%Y%m%d")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Fetch newest
    result = subprocess.run(
        ["clawhub", "explore", "--sort", "newest", "--limit", "25", "--json"],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        print(f"❌ clawhub explore failed: {result.stderr}")
        sys.exit(1)

    data = json.loads(result.stdout)
    skills = data if isinstance(data, list) else data.get("items", [])
    print(f"✅ clawhub newest: {len(skills)} skills")

    # Also fetch trending for more variety
    result2 = subprocess.run(
        ["clawhub", "explore", "--sort", "trending", "--limit", "25", "--json"],
        capture_output=True, text=True, timeout=30,
    )
    trending = []
    if result2.returncode == 0:
        data2 = json.loads(result2.stdout)
        trending = data2 if isinstance(data2, list) else data2.get("items", [])
        print(f"✅ clawhub trending: {len(trending)} skills")

    # Merge: newest first, then trending (dedup by slug)
    seen = set()
    merged = []
    for s in skills + trending:
        slug = s.get("slug", "")
        if slug and slug not in seen:
            seen.add(slug)
            merged.append(s)
    print(f"✅ clawhub merged (deduped): {len(merged)} skills")

    # Save
    path = DATA_DIR / f"raw_clawhub_{date}.json"
    json.dump(merged, open(path, "w"), ensure_ascii=False, indent=2)
    print(f"✅ saved to {path}")


if __name__ == "__main__":
    main()
