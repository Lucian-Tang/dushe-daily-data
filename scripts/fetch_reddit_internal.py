#!/usr/bin/env python3
"""
fetch_reddit_internal.py - Reddit 内部 API 采集脚本 (Phase 1 POC)
依赖: rdt-cli (git clone /opt/rdt-cli)
认证: Cookie (reddit_session + token) → /opt/cookies/reddit.json
输出: data/reddit_internal_daily_YYYYMMDD.json

⚠ 注意: 管线已有 Reddit RSS 采集 (fetch_dev.py), rdt-cli 作为增强信源
         提供内部 JSON API 的额外数据（评论数、热度分、作者信息等）

使用方式:
  python3 scripts/fetch_reddit_internal.py
  python3 scripts/fetch_reddit_internal.py --subreddits MachineLearning,artificial --count 15
  python3 scripts/fetch_reddit_internal.py --dry-run

输出格式:
[
  {
    "uid": "reddit_a1b2c3d4",
    "title": "帖子标题",
    "content": "帖子正文 (≤200字)",
    "quote": "毒舌点评 (15-30字)",
    "source": "Reddit 内部",
    "url": "https://reddit.com/r/...",
    "published": "2026-06-09",
    "_meta": {"subreddit": "MachineLearning", "score": 420, "comments": 88}
  }
]
"""

import os
import sys
import json
import re
import hashlib
import random
import subprocess
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# === 路径配置 ===
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "data"
LOG_DIR = WORKSPACE / "logs"
RDT_CLI_DIR = Path("/opt/rdt-cli")
COOKIE_FILE = Path("/opt/cookies/reddit.json")

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# === 日志配置 ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# === 毒舌点评模板 (Reddit 专用, 15-30字) ===
REDDIT_QUOTES = [
    "Reddit AI 板块今天又在上头讨论什么",
    "海外 AI 圈的热帖，一半是炼丹一半是吵架",
    "r/MachineLearning 的日常：论文挂一下就跑",
    "Reddit 热帖，评论区的辩论比正文精彩十倍",
    "又是一个'我复现了 SOTA'的帖子，点开结果是 Colab",
    "Reddit AI 老哥的年经话题又来了",
    "评论区比论文本身还有信息量——Reddit 老传统",
    "海外程序员的群聊记录又流出了",
    "r/artificial 今天的悲观指数又创新高",
    "Reddit 上的 AI 伦理争论，可能比论文都多",
    "又一个宣称'超越 GPT'的项目，楼下已开始打脸",
    "Reddit 老哥的复现实验，成功率不超过 10%",
    "这个帖子下面全是学术界和工业界在互怼",
    "海外 AI 社区的情报站，信噪比自行判断",
    "Reddit 热帖从来不是标题党的对手",
    "r/singularity 的 hype 浓度已超安全阈值",
    "Reddit 的收藏功能比浏览器的还好用",
    "这个帖子火得莫名其妙，大概是标题里有个'AI'",
]

# === 安全: Cookie 日志过滤 ===
def sanitize_output(text: str) -> str:
    patterns = [
        (r'reddit_session[=:]\s*["\']?[a-zA-Z0-9_\-]+', 'reddit_session=***REDACTED***'),
        (r'token[=:]\s*["\']?[a-zA-Z0-9_\-]+', 'token=***REDACTED***'),
        (r'set-cookie:\s*[^\n]+', '[set-cookie redacted]'),
    ]
    for pat, replacement in patterns:
        text = re.sub(pat, replacement, text, flags=re.IGNORECASE)
    return text


# === Cookie 加载 ===
def load_cookies() -> Optional[dict]:
    """加载 Reddit Cookie (环境变量优先, 文件备选)"""
    reddit_session = os.environ.get("REDDIT_SESSION")
    token = os.environ.get("REDDIT_TOKEN")
    if reddit_session and token:
        logger.info("✅ Cookie 从环境变量加载")
        return {"reddit_session": reddit_session, "token": token}

    if COOKIE_FILE.exists():
        try:
            with open(COOKIE_FILE, "r") as f:
                cookies = json.load(f)
            return cookies
        except Exception as e:
            logger.error(f"❌ Cookie 文件解析失败: {e}")
            return None

    logger.error("❌ 未找到 Reddit Cookie")
    return None


# === UID 生成 ===
def gen_uid(title: str, url: str = "") -> str:
    def normalize(s: str) -> str:
        return re.sub(r'[^\u0000-\uFFFF]', '', s)\
                 .replace('：', ':').replace('—', '-').replace('–', '-')\
                 .lower().strip()
    key = normalize(title) + '|' + normalize(url)
    return f"reddit_{hashlib.md5(key.encode()).hexdigest()[:8]}"


# === CLI 调用 ===
def run_rdt_cli(args: list, timeout: int = 60) -> Optional[str]:
    """调用 rdt-cli"""
    try:
        result = subprocess.run(
            ["rdt"] + args,
            capture_output=True, text=True,
            timeout=timeout,
            cwd=str(RDT_CLI_DIR) if RDT_CLI_DIR.exists() else None,
            env={**os.environ}
        )
        if result.stderr:
            logger.warning(f"⚠ stderr: {sanitize_output(result.stderr[:200])}")
        if result.returncode != 0:
            logger.error(f"❌ rdt-cli 退出码 {result.returncode}")
            return None
        return result.stdout
    except FileNotFoundError:
        logger.error(f"❌ rdt-cli 未安装 ({RDT_CLI_DIR})")
        return None
    except Exception as e:
        logger.error(f"❌ rdt-cli 调用异常: {e}")
        return None


# === 输出解析 ===
def parse_output(raw: str, date_str: str, subreddit: str = "") -> list:
    """解析 rdt-cli --json 输出"""
    items = []
    try:
        data = json.loads(raw)
        posts = data if isinstance(data, list) else data.get("posts", data.get("data", []))

        for post in posts:
            if not isinstance(post, dict):
                continue

            title = (post.get("title") or "").strip()[:150]
            content = (post.get("selftext") or post.get("body") or "").strip()[:200]
            permalink = post.get("permalink", "")
            url = f"https://reddit.com{permalink}" if permalink else post.get("url", "")
            sub = subreddit or post.get("subreddit", "")

            uid = gen_uid(title, url)
            published = date_str[:4] + "-" + date_str[4:6] + "-" + date_str[6:8]

            items.append({
                "uid": uid,
                "title": title,
                "content": content,
                "quote": random.choice(REDDIT_QUOTES),
                "source": "Reddit 内部",
                "url": url,
                "published": published,
                "_meta": {
                    "subreddit": sub,
                    "score": post.get("score", 0),
                    "comments": post.get("num_comments", post.get("comments", 0)),
                    "author": post.get("author", ""),
                    "upvote_ratio": post.get("upvote_ratio", 0),
                }
            })
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON 解析失败: {e}")

    return items


# === 主采集逻辑 ===
def fetch_subreddit(sub_name: str, sort: str = "hot", count: int = 20) -> list:
    """采集指定子版块"""
    logger.info(f"🔄 采集 r/{sub_name} (sort={sort}, count={count})...")
    raw = run_rdt_cli(["subreddit", sub_name, "--sort", sort, "--limit", str(count), "--json"])
    if not raw:
        logger.warning(f"⚠ r/{sub_name} 采集失败")
        return []
    return parse_output(raw, datetime.now().strftime("%Y%m%d"), sub_name)


def fetch_frontpage(count: int = 20) -> list:
    logger.info(f"🔄 采集 Reddit 首页 (count={count})...")
    raw = run_rdt_cli(["frontpage", "--json", "--limit", str(count)])
    if not raw:
        return []
    return parse_output(raw, datetime.now().strftime("%Y%m%d"))


# === 主入口 ===
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Reddit 内部 API 采集脚本")
    parser.add_argument("--subreddits", type=str,
                        default="MachineLearning,artificial,singularity,LocalLLaMA,OpenAI",
                        help="子版块列表,逗号分隔 (default: AI 相关板块)")
    parser.add_argument("--count", type=int, default=15,
                        help="每个子版块采集条数 (default: 15)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    date_str = datetime.now().strftime("%Y%m%d")
    published = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    # 检查 Cookie
    cookies = load_cookies()
    if not cookies:
        logger.error("❌ 无 Cookie，无法采集")
        sys.exit(1)

    # 注入环境变量
    os.environ["REDDIT_SESSION"] = os.environ.get("REDDIT_SESSION", cookies.get("reddit_session", ""))
    os.environ["REDDIT_TOKEN"] = os.environ.get("REDDIT_TOKEN", cookies.get("token", ""))

    # 采集
    all_items = []
    subreddits = [s.strip() for s in args.subreddits.split(",") if s.strip()]

    for sub in subreddits:
        items = fetch_subreddit(sub, sort="hot", count=args.count)
        all_items.extend(items)
        logger.info(f"✅ r/{sub}: {len(items)} 条")
        time.sleep(1)  # 请求间隔 (生产环境应≥30s)

    # 去重
    seen = set()
    unique = []
    for item in all_items:
        if item["uid"] not in seen:
            seen.add(item["uid"])
            unique.append(item)

    logger.info(f"📊 总计: {len(all_items)} 条 → 去重后 {len(unique)} 条")

    if args.dry_run:
        logger.info("🔍 空跑模式")
        for item in unique[:5]:
            logger.info(f"  [{item['_meta']['subreddit']}] {item['title'][:60]}...")
        return

    # 写入 data/
    out_path = DATA_DIR / f"reddit_internal_daily_{date_str}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ 已保存 {len(unique)} 条 → {out_path}")


if __name__ == "__main__":
    main()
