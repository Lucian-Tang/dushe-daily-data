#!/usr/bin/env python3
"""fetch_clawhub.py - 采集 ClawHub 技能市场的最新/热门技能
输出 data/raw_clawhub_YYYYMMDD.json（全量原始数据）
输出 data/clawhub_trending_YYYYMMDD.json（标准化 Top 10 板块数据）
"""

import subprocess, json, sys, hashlib, random
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "data"

# 毒舌点评模板（抓取自 generate_daily_json.py 复用）
CLAWHUB_QUOTES = [
    "又一个试图让 AI 干所有活的工具包",
    "听起来很美，装上了可能翻车翻得彻底",
    "名字取得不错，能不能用就另说了",
    "卷王的新玩具，普通人观望就好了",
    "开源精神值得表扬，稳定性打个问号",
    "技能市场的长尾产物，有用就算赚了",
    "社区贡献喜+1，实际价值等时间验证",
    "装完发现原来自己也能手写，何必呢",
    "给 Agent 加技能包，跟装浏览器插件一样",
    "又一个'让工作流自动化'的尝试，祝好运",
    "看起来花里胡哨，核心代码就几百行",
    "低代码梦还在继续，这次是 Agent 版",
    "宣称很好用，实际全看运气和网络",
    "技能生态的一块砖，搭起来才算数",
    "小众但确实有用，可惜多数人用不上",
    "工具链又胖了一圈，项目依赖+1",
    "先 star 收藏再说，反正不一定会用",
    "卷王的又一个新玩具，普通人观望就行",
]


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

    # Save raw
    path = DATA_DIR / f"raw_clawhub_{date}.json"
    json.dump(merged, open(path, "w"), ensure_ascii=False, indent=2)
    print(f"✅ saved raw to {path}")

    # ── 生成 clawhub_trending 板块文件（标准 6 字段 + 扩展字段）──
    def score(s):
        st = s.get("stats", {}) or {}
        return (st.get("downloads", 0) or 0) * 1 + (st.get("stars", 0) or 0) * 10

    sorted_skills = sorted(merged, key=score, reverse=True)
    take = min(10, len(sorted_skills))
    top10 = sorted_skills[:take]

    published = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
    trending_items = []
    for i, s in enumerate(top10):
        slug = s.get("slug", "")
        display_name = s.get("displayName", slug)
        summary = s.get("summary", "")
        tags = s.get("tags", {}) or {}
        version = tags.get("latest", "")
        stats = s.get("stats", {}) or {}
        downloads = stats.get("downloads", 0) or 0
        stars = stats.get("stars", 0) or 0

        title = display_name.strip() if display_name else slug.replace("-", " ").title()

        # 中文摘要
        content = f"ClawHub 技能市场收录的开源技能包「{display_name}」"
        if version:
            content += f"（v{version}）"
        content += "，可安装至 OpenClaw Agent 使用。"
        if summary:
            desc_short = summary[:120].strip()
            content += f"功能要点：{desc_short}。"
        if downloads or stars:
            content += f"已累计 {downloads} 次下载"
            if stars:
                content += f"、{stars} 个 Star"
            content += "。"
        content = content[:200]

        # 毒舌点评
        quote = random.choice(CLAWHUB_QUOTES)

        # uid
        key = f"{title}|ClawHub"
        uid = f"clawhub_{hashlib.md5(key.encode()).hexdigest()[:8]}"

        trending_items.append({
            "uid": uid,
            "title": title,
            "content": content,
            "quote": quote,
            "source": "ClawHub",
            "url": f"https://clawhub.ai/skills/{slug}",
            "published": published,
            "downloads": downloads,
            "stars_val": stars,
            "version": version,
            "rank": i + 1,
        })

    trending_path = DATA_DIR / f"clawhub_trending_{date}.json"
    json.dump(trending_items, open(trending_path, "w"), ensure_ascii=False, indent=2)
    print(f"✅ clawhub_trending Top {len(trending_items)} → {trending_path}")


if __name__ == "__main__":
    main()
