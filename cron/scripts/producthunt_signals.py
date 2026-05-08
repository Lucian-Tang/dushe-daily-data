#!/usr/bin/env python3
"""ProductHunt daily top products via RSS feed (Scrapling fetcher + XPath)"""
import json, os, sys
from datetime import datetime

OUT_DIR = os.path.expanduser("~/.openclaw/workspace/data/opportunities/producthunt")
os.makedirs(OUT_DIR, exist_ok=True)

def main():
    from scrapling import Fetcher
    from scrapling.parser import Adaptor
    
    fetcher = Fetcher()
    resp = fetcher.get("https://www.producthunt.com/feed")
    page = Adaptor(resp.html_content)
    
    entries = page.xpath('//entry')
    products = []
    
    for entry in entries:
        try:
            titles = entry.xpath('.//title')
            name = titles[0].get_all_text().strip() if titles else ""
            if not name:
                continue
            
            contents = entry.xpath('.//content')
            desc = ""
            if contents:
                desc_raw = contents[0].get_all_text() or ""
                desc = desc_raw.split('</p>')[0].replace('<p>', '')[:200].strip()
            
            links = entry.xpath('.//link[@rel="alternate"]') or entry.xpath('.//link')
            link = links[0].attrib.get('href', '') if links else ""
            
            products.append({
                "name": name,
                "description": desc,
                "url": link,
                "source": "ProductHunt"
            })
        except Exception:
            continue
    
    today = datetime.now().strftime("%Y-%m-%d")
    out = {"date": today, "source": "producthunt", "count": len(products), "items": products}
    with open(f"{OUT_DIR}/{today}.json", 'w') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"✅ ProductHunt: {len(products)} products")
    for p in products[:3]:
        print(f"  - {p['name']}: {p['description'][:60]}")

if __name__ == "__main__":
    main()
