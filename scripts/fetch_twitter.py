#!/usr/bin/env python3
"""
fetch_twitter.py - Twitter/X 采集脚本 (Phase 1 POC)
依赖: twitter-cli (git clone /opt/twitter-cli)
认证: Cookie (auth_token + ct0) → /opt/cookies/twitter.json
输出: data/twitter_daily_YYYYMMDD.json

使用方式:
  python3 scripts/fetch_twitter.py
  python3 scripts/fetch_twitter.py --source all          # 综合: 推荐时间线 + AI 领域搜索
  python3 scripts/fetch_twitter.py --source timeline     # 仅推荐时间线
  python3 scripts/fetch_twitter.py --source search       # 仅搜索
  python3 scripts/fetch_twitter.py --count 15            # 采集数量
  python3 scripts/fetch_twitter.py --dry-run             # 空跑测试

输出格式 (与有数Feed 管线兼容):
[
  {
    "uid": "twitter_a1b2c3d4",
    "title": "@user: 推文标题",
    "content": "推文摘要 (≤200字)",
    "quote": "毒舌点评 (15-30字)",
    "source": "Twitter/X",
    "url": "https://x.com/user/status/123456",
    "published": "2026-06-09"
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
TWITTER_CLI_DIR = Path("/opt/twitter-cli")
COOKIE_FILE = Path("/opt/cookies/twitter.json")

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# === 日志配置 ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# === 毒舌点评模板 (Twitter 专用, 15-30字) ===
TWITTER_QUOTES = [
    "推特 AI 圈又在吵什么，点开一看果然又是画饼",
    "X 上的 AI bro 们永远能给你惊喜——或者惊吓",
    "140 字的豪言壮语，读完发现说了个寂寞",
    "X 上的 AI 热帖，一半是炒作一半是吐槽",
    "今天的推特 AI 共识：VC 又该掏钱了",
    "X 热搜上的 AI 话题，懂的都懂不懂的看个乐",
    "海外 AI 圈今天又发明了几个新 buzzword",
    "推特上的 AI 大 V 们，今天又在给哪家带货",
    "刷完 X 时间线，感觉 AI 明天就能统治世界",
    "X 上的 AI 战争比 Netflix 剧集还精彩",
    "今天推上又在争论哪个 LLM 更强——答案永远是下一个",
    "AI 圈内幕八卦，X 上永远第一时间更新",
    "刷 X 发现又有人融资了，看金额我沉默了",
    "X 上的 AI 创业者配方：一个 PPT + 一句愿景",
    "推特的 AI 吐槽大赛，每天都有新选手",
    "X 的热度像烟花一样，放完就没了",
    "海外 AI 圈三大法宝：发推、融资、换方向",
    "X 上的长文串总让你觉得学到了什么——其实没有",
]

# === 安全: Cookie 日志过滤 ===
def sanitize_output(text: str) -> str:
    """过滤输出中的 Cookie/Token 等敏感字段"""
    patterns = [
        (r'auth_token[=:]\s*["\']?[a-zA-Z0-9_\-%]+', 'auth_token=***REDACTED***'),
        (r'ct0[=:]\s*["\']?[a-zA-Z0-9_\-]+', 'ct0=***REDACTED***'),
        (r'bearer[=:]\s*["\']?[a-zA-Z0-9_\-%.]+', 'bearer=***REDACTED***'),
        (r'set-cookie:\s*[^\n]+', '[set-cookie redacted]'),
    ]
    for pat, replacement in patterns:
        text = re.sub(pat, replacement, text, flags=re.IGNORECASE)
    return text


# === Cookie 加载 ===
def load_cookies() -> Optional[dict]:
    """加载 Twitter Cookie (环境变量优先, 文件备选)"""
    # 环境变量优先
    auth_token = os.environ.get("TWITTER_AUTH_TOKEN")
    ct0 = os.environ.get("TWITTER_CT0")
    if auth_token and ct0:
        logger.info("✅ Cookie 从环境变量加载")
        return {"auth_token": auth_token, "ct0": ct0}

    # 文件备选
    if COOKIE_FILE.exists():
        try:
            with open(COOKIE_FILE, "r") as f:
                cookies = json.load(f)
            # 支持两种格式: {"auth_token":"xxx","ct0":"xxx"} 或 [{"name":"auth_token","value":"xxx"},...]
            if isinstance(cookies, list):
                cookie_map = {c.get("name", ""): c.get("value", "") for c in cookies}
                auth_token = cookie_map.get("auth_token", "")
                ct0 = cookie_map.get("ct0", "")
            else:
                auth_token = cookies.get("auth_token", "")
                ct0 = cookies.get("ct0", "")
            if auth_token and ct0:
                logger.info(f"✅ Cookie 从文件加载: {COOKIE_FILE}")
                return {"auth_token": auth_token, "ct0": ct0}
            else:
                logger.error(f"❌ Cookie 文件缺少 auth_token 或 ct0")
                return None
        except Exception as e:
            logger.error(f"❌ Cookie 文件解析失败: {e}")
            return None

    logger.error("❌ 未找到 Twitter Cookie (设置 TWITTER_AUTH_TOKEN/TWITTER_CT0 或创建 /opt/cookies/twitter.json)")
    return None


# === UID 生成 (与管线规范兼容) ===
def gen_uid(title: str, url: str = "") -> str:
    """生成 uid: twitter_{md5(normalize_title + '|' + normalize_url)[:8]}"""
    def normalize(s: str) -> str:
        return re.sub(r'[^\u0000-\uFFFF]', '', s)\
                 .replace('：', ':').replace('—', '-').replace('–', '-')\
                 .lower().strip()
    key = normalize(title) + '|' + normalize(url)
    return f"twitter_{hashlib.md5(key.encode()).hexdigest()[:8]}"


# === CLI 调用 ===
def run_twitter_cli(args: list, timeout: int = 60) -> Optional[str]:
    """调用 twitter-cli，返回 sanitized stdout"""
    try:
        result = subprocess.run(
            ["python3", "-m", "twitter_cli"] + args,
            capture_output=True, text=True,
            timeout=timeout,
            cwd=str(TWITTER_CLI_DIR) if TWITTER_CLI_DIR.exists() else None,
            env={**os.environ}  # 继承环境变量 (cookie 注入)
        )
        stdout = result.stdout
        stderr = result.stderr

        if stderr:
            logger.warning(f"⚠ stderr: {sanitize_output(stderr[:200])}")

        if result.returncode != 0:
            logger.error(f"❌ twitter-cli 退出码 {result.returncode}: {sanitize_output(stderr[:500])}")
            return None

        return stdout

    except subprocess.TimeoutExpired:
        logger.error(f"❌ twitter-cli 超时 ({timeout}s)")
        return None
    except FileNotFoundError:
        logger.error(f"❌ twitter-cli 未安装 ({TWITTER_CLI_DIR})")
        return None
    except Exception as e:
        logger.error(f"❌ twitter-cli 调用异常: {e}")
        return None


# === 解析 twitter-cli 输出 ===
def parse_timeline_output(raw: str, date_str: str) -> list:
    """解析 twitter timeline --json 输出为标准格式"""
    items = []
    try:
        data = json.loads(raw)
        # twitter-cli 输出格式可能为 {"tweets": [...]} 或直接是列表
        tweets = data if isinstance(data, list) else data.get("tweets", data.get("data", []))
        if not tweets:
            tweets = []

        for tweet in tweets:
            if not isinstance(tweet, dict):
                continue

            # 提取字段 (字段名可能因 twitter-cli 版本而异)
            tweet_id = tweet.get("id", tweet.get("id_str", ""))
            user = tweet.get("user", {})
            if isinstance(user, dict):
                username = user.get("screen_name", user.get("username", "unknown"))
            else:
                username = "unknown"

            text = (tweet.get("full_text") or tweet.get("text") or "").strip()
            # 处理短 URL 展开
            # tw_url = tweet.get("url", f"https://x.com/{username}/status/{tweet_id}")

            title_text = text[:80].replace('\n', ' ')
            title = f"@{username}: {title_text}"
            content = text[:200]
            url = f"https://x.com/{username}/status/{tweet_id}" if tweet_id else ""

            uid = gen_uid(title, url)
            published = date_str[:4] + "-" + date_str[4:6] + "-" + date_str[6:8]

            items.append({
                "uid": uid,
                "title": title,
                "content": content,
                "quote": random.choice(TWITTER_QUOTES),
                "source": "Twitter/X",
                "url": url,
                "published": published,
                "_meta": {
                    "username": username,
                    "likes": tweet.get("favorite_count", tweet.get("likes", 0)),
                    "retweets": tweet.get("retweet_count", tweet.get("retweets", 0)),
                }
            })
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON 解析失败: {e}")
        # 非 JSON 输出: 尝试行解析 (fallback)
        for line in raw.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            # fallback 简单格式: @user: text
            match = re.match(r'@(\w+):\s*(.+)', line)
            if match:
                username, text = match.groups()
                title = f"@{username}: {text[:80]}"
                items.append({
                    "uid": gen_uid(title, ""),
                    "title": title,
                    "content": text[:200],
                    "quote": random.choice(TWITTER_QUOTES),
                    "source": "Twitter/X",
                    "url": "",
                    "published": date_str[:4] + "-" + date_str[4:6] + "-" + date_str[6:8],
                })

    return items


def parse_search_output(raw: str, date_str: str) -> list:
    """解析 twitter search --json 输出"""
    # 搜索输出格式与时间线类似
    return parse_timeline_output(raw, date_str)


# === 主采集逻辑 ===
def fetch_timeline(count: int = 20) -> list:
    """获取推荐时间线"""
    logger.info(f"🔄 获取 Twitter 推荐时间线 (count={count})...")
    raw = run_twitter_cli(["timeline", "--json", "--count", str(count)])
    if not raw:
        logger.warning("⚠ 时间线采集失败")
        return []
    return parse_timeline_output(raw, datetime.now().strftime("%Y%m%d"))


def fetch_search(query: str, count: int = 15) -> list:
    """搜索关键词"""
    logger.info(f"🔍 Twitter 搜索: '{query}' (count={count})...")
    raw = run_twitter_cli(["search", query, "--json", "--count", str(count)])
    if not raw:
        logger.warning(f"⚠ 搜索 '{query}' 失败")
        return []
    return parse_search_output(raw, datetime.now().strftime("%Y%m%d"))


# === 主入口 ===
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Twitter/X 采集脚本")
    parser.add_argument("--source", choices=["all", "timeline", "search"], default="all",
                        help="采集来源 (default: all)")
    parser.add_argument("--count", type=int, default=20,
                        help="每个来源采集条数 (default: 20)")
    parser.add_argument("--dry-run", action="store_true",
                        help="空跑测试，不写入文件")
    args = parser.parse_args()

    date_str = datetime.now().strftime("%Y%m%d")
    published = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    # 检查 Cookie
    cookies = load_cookies()
    if not cookies:
        logger.error("❌ 无 Cookie，无法采集")
        sys.exit(1)

    # 设置环境变量 (如果 twitter-cli 需要)
    if not os.environ.get("TWITTER_AUTH_TOKEN"):
        os.environ["TWITTER_AUTH_TOKEN"] = cookies["auth_token"]
    if not os.environ.get("TWITTER_CT0"):
        os.environ["TWITTER_CT0"] = cookies.get("ct0", "")

    # 采集
    all_items = []

    if args.source in ("all", "timeline"):
        time.sleep(1)  # 请求间隔 (实际生产环境应≥60s)
        items = fetch_timeline(count=args.count)
        all_items.extend(items)
        logger.info(f"✅ 时间线: {len(items)} 条")

    if args.source in ("all", "search"):
        time.sleep(1)  # 请求间隔
        # 收集特定 AI 领域推文
        queries = [
            "AI agent 2026",
            "LLM model release OR update",
        ]
        for q in queries[:1]:  # POC 阶段只搜一个，降低请求量
            items = fetch_search(q, count=min(args.count, 10))
            all_items.extend(items)
            logger.info(f"✅ 搜索 '{q}': {len(items)} 条")
            if len(queries) > 1:
                time.sleep(1)

    # 去重
    seen = set()
    unique = []
    for item in all_items:
        if item["uid"] not in seen:
            seen.add(item["uid"])
            unique.append(item)

    logger.info(f"📊 总计: {len(all_items)} 条 → 去重后 {len(unique)} 条")

    if args.dry_run:
        logger.info("🔍 空跑模式，不写入文件")
        for item in unique[:5]:
            logger.info(f"  {item['title'][:60]}...")
        return

    # 写入 data/ 目录
    out_path = DATA_DIR / f"twitter_daily_{date_str}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ 已保存 {len(unique)} 条 → {out_path}")

    # 同时生成信号格式 (简化版) 到 reports/signals/
    signals_dir = WORKSPACE.parent / "reports" / "signals"
    signals_dir.mkdir(parents=True, exist_ok=True)
    signal_items = [
        {
            "name": item["title"],
            "description": item["content"][:150],
            "url": item["url"],
            "source": item["source"],
        }
        for item in unique
    ]
    signal_out = {
        "date": published,
        "source": "twitter",
        "count": len(signal_items),
        "items": signal_items,
    }
    signal_path = signals_dir / f"twitter_signals_{published}.json"
    with open(signal_path, "w", encoding="utf-8") as f:
        json.dump(signal_out, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ 信号格式已保存 → {signal_path}")


if __name__ == "__main__":
    main()
