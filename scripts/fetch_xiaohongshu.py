#!/usr/bin/env python3
"""
fetch_xiaohongshu.py - 小红书采集脚本 (Phase 1 POC)
依赖: xhs-cli (pipx install xhs-cli)
认证: Cookie (web_session, a1, webId) → /opt/cookies/xiaohongshu.json
输出: data/xiaohongshu_daily_YYYYMMDD.json

⚠ 高风险警告:
  - 小红书反爬机制极其严格，封号速度极快
  - 必须使用专用小号（不要用主号！）
  - 仅限低频查询（每天最多 1 次，建议隔天）
  - 搜索关键词限制 1-2 个，不超过 3 个
  - 请求间隔 ≥ 5 分钟
  - 建议手动触发而非 cron 自动化

使用方式:
  python3 scripts/fetch_xiaohongshu.py
  python3 scripts/fetch_xiaohongshu.py --query "AI工具推荐" --count 10
  python3 scripts/fetch_xiaohongshu.py --query "AI" --dry-run

输出格式:
[
  {
    "uid": "xhs_a1b2c3d4",
    "title": "小红书笔记标题",
    "content": "笔记摘要 (≤200字)",
    "quote": "毒舌点评 (15-30字)",
    "source": "小红书",
    "url": "https://www.xiaohongshu.com/explore/xxxxx",
    "published": "2026-06-09",
    "_meta": {"likes": 1200, "collects": 300, "author": "博主名"}
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
COOKIE_FILE = Path("/opt/cookies/xiaohongshu.json")

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# === 日志配置 ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# === 毒舌点评模板 (小红书专用, 15-30字) ===
XHS_QUOTES = [
    "小红书的 AI 种草笔记，连代码都能写出氛围感",
    "XHS 上面的 AI 工具推荐，至少七成是恰饭",
    "刷到一条 AI 工具推荐——点赞已破万，效果待考证",
    "小红书 AI 博主的必备技能：会截图，会调色",
    "这个工具推荐写得太好了，好到我怀疑是不是广告",
    "XHS 上的人工智能教程：手把手教你一键生成",
    "小红书的 AI 热帖，图片比干货多十倍",
    "这条笔记的封面图比整个 AI 行业都努力",
    "小红书 AI 赛道已卷到连调色都要用 AI 了",
    "今天 XHS 给我推的 AI 工具，昨天刚被曝翻车",
    "在 XHS 上，AI 工具先用滤镜，再用算法推荐给你",
    "小红书 AI 博主的商业化程度已达宇宙级",
    "这条笔记如果能动，一定是个漂亮的 PPT",
    "XHS 上对 AI 的理解：能帮我修图的就是好 AI",
    "小红书 AI 热帖三要素：好看、好用、链接在简介",
    "看完这条推荐我下载了——然后发现要付费",
    "XHS 的 AI 赛道，已经从工具推荐进化到卖课了",
    "这个笔记的数据这么好，要么真的有用要么真的有钱",
]

# === 安全: Cookie 日志过滤 ===
def sanitize_output(text: str) -> str:
    patterns = [
        (r'web_session[=:]\s*["\']?[a-zA-Z0-9_\-]+', 'web_session=***REDACTED***'),
        (r'a1[=:]\s*["\']?[a-zA-Z0-9_\-]+', 'a1=***REDACTED***'),
        (r'webId[=:]\s*["\']?[a-zA-Z0-9_\-]+', 'webId=***REDACTED***'),
        (r'set-cookie:\s*[^\n]+', '[set-cookie redacted]'),
    ]
    for pat, replacement in patterns:
        text = re.sub(pat, replacement, text, flags=re.IGNORECASE)
    return text


# === Cookie 加载 ===
def load_cookies() -> Optional[dict]:
    """加载小红书 Cookie (环境变量优先, 文件备选)"""
    web_session = os.environ.get("XHS_WEB_SESSION")
    a1 = os.environ.get("XHS_A1")
    web_id = os.environ.get("XHS_WEB_ID")
    if web_session and a1:
        logger.info("✅ Cookie 从环境变量加载")
        return {"web_session": web_session, "a1": a1, "webId": web_id or ""}

    if COOKIE_FILE.exists():
        try:
            with open(COOKIE_FILE, "r") as f:
                cookies = json.load(f)
            # 支持两种格式
            if isinstance(cookies, list):
                cookie_map = {c.get("name", ""): c.get("value", "") for c in cookies}
                return cookie_map
            return cookies
        except Exception as e:
            logger.error(f"❌ Cookie 文件解析失败: {e}")
            return None

    logger.error("❌ 未找到小红书 Cookie (设置 XHS_WEB_SESSION/XHS_A1 或创建 /opt/cookies/xiaohongshu.json)")
    return None


# === UID 生成 ===
def gen_uid(title: str, url: str = "") -> str:
    def normalize(s: str) -> str:
        return re.sub(r'[^\u0000-\uFFFF]', '', s)\
                 .replace('：', ':').replace('—', '-').replace('–', '-')\
                 .lower().strip()
    key = normalize(title) + '|' + normalize(url)
    return f"xhs_{hashlib.md5(key.encode()).hexdigest()[:8]}"


# === 请求间隔管理 (防封核心) ===
_last_request_time: float = 0
_MIN_INTERVAL = 300  # 最少 5 分钟间隔

def wait_if_needed(min_interval: int = None):
    """强制间隔等待，防止请求过快导致封号"""
    global _last_request_time
    if min_interval is None:
        min_interval = _MIN_INTERVAL
    elapsed = time.time() - _last_request_time
    if elapsed < min_interval:
        wait_time = min_interval - elapsed
        logger.info(f"⏳ 等待 {wait_time:.0f}s (防封间隔)...")
        time.sleep(wait_time)
    _last_request_time = time.time()


# === CLI 调用 (带退避重试) ===
def run_xhs_cli(args: list, timeout: int = 120, max_retries: int = 2) -> Optional[str]:
    """
    调用 xhs-cli，带退避重试
    args: 如 ["search", "AI工具", "--count", "10", "--json"]
    """
    wait_if_needed()

    backoff = 300  # 初始退避 5 分钟
    for attempt in range(max_retries + 1):
        try:
            result = subprocess.run(
                ["xhs"] + args,
                capture_output=True, text=True,
                timeout=timeout,
                env={**os.environ, "NO_COLOR": "1"}
            )

            stdout = sanitize_output(result.stdout)
            stderr = sanitize_output(result.stderr)

            if stderr:
                # 检测封号信号
                if any(kw in stderr.lower() for kw in ["block", "ban", "verify", "captcha", "login", "unauthorized"]):
                    logger.error(f"🚨 检测到封号风险信号: {stderr[:200]}")
                    return None

                logger.warning(f"⚠ stderr: {stderr[:200]}")

            if result.returncode != 0:
                logger.error(f"❌ xhs-cli 退出码 {result.returncode} (attempt {attempt+1}/{max_retries+1})")
                if attempt < max_retries:
                    logger.info(f"⏳ 退避 {backoff}s 后重试...")
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                return None

            return stdout

        except subprocess.TimeoutExpired:
            logger.error(f"❌ xhs-cli 超时 ({timeout}s) (attempt {attempt+1}/{max_retries+1})")
            if attempt < max_retries:
                time.sleep(backoff)
                backoff *= 2
        except FileNotFoundError:
            logger.error("❌ xhs-cli 未安装 (pipx install xhs-cli)")
            return None
        except Exception as e:
            logger.error(f"❌ xhs-cli 调用异常: {e}")
            if attempt < max_retries:
                time.sleep(backoff)
                backoff *= 2

    return None


# === 输出解析 ===
def parse_output(raw: str, date_str: str) -> list:
    """解析 xhs-cli search --json 输出"""
    items = []
    try:
        data = json.loads(raw)
        notes = data if isinstance(data, list) else data.get("notes", data.get("data", []))

        for note in notes:
            if not isinstance(note, dict):
                continue

            title = (note.get("title") or note.get("display_title") or "").strip()[:150]
            content = (note.get("desc") or note.get("description") or "").strip()[:200]
            note_id = note.get("id", note.get("note_id", ""))
            url = f"https://www.xiaohongshu.com/explore/{note_id}" if note_id else note.get("url", "")

            uid = gen_uid(title, url)
            published = date_str[:4] + "-" + date_str[4:6] + "-" + date_str[6:8]

            items.append({
                "uid": uid,
                "title": title,
                "content": content,
                "quote": random.choice(XHS_QUOTES),
                "source": "小红书",
                "url": url,
                "published": published,
                "_meta": {
                    "likes": note.get("likes", note.get("liked_count", 0)),
                    "collects": note.get("collects", note.get("collected_count", 0)),
                    "author": note.get("user", {}).get("nickname", "") if isinstance(note.get("user"), dict) else note.get("author", ""),
                    "type": note.get("type", "normal"),  # normal 或 video
                }
            })
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON 解析失败: {e}")
        # 非 JSON fallback: 行解析
        for line in raw.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # 简单 key:value 解析
            match = re.match(r'(.+?)\s*[:-]\s*(.+)', line)
            if match and len(match.group(1)) < 100:
                title = match.group(1).strip()[:150]
                items.append({
                    "uid": gen_uid(title, ""),
                    "title": title,
                    "content": match.group(2).strip()[:200],
                    "quote": random.choice(XHS_QUOTES),
                    "source": "小红书",
                    "url": "",
                    "published": date_str[:4] + "-" + date_str[4:6] + "-" + date_str[6:8],
                })

    return items


# === 封号检测 ===
def check_account_status() -> bool:
    """检查账号是否正常 (是否被封)"""
    raw = run_xhs_cli(["status", "--json"], timeout=30)
    if not raw:
        logger.warning("⚠ 无法获取账号状态 (可能被限流/封号)")
        return False
    try:
        status = json.loads(raw)
        logged_in = status.get("logged_in", status.get("ok", False))
        if not logged_in:
            logger.error("🚨 账号未登录或 Cookie 已过期")
            return False
        logger.info("✅ 小红书账号状态正常")
        return True
    except json.JSONDecodeError:
        logger.warning("⚠ 账号状态解析失败")
        return True  # 乐观假设


# === 主采集 ===
def fetch_search(query: str, count: int = 10) -> list:
    """搜索笔记"""
    logger.info(f"🔍 小红书搜索: '{query}' (count={count})...")
    raw = run_xhs_cli(["search", query, "--count", str(count), "--json"])
    if not raw:
        return []
    return parse_output(raw, datetime.now().strftime("%Y%m%d"))


# === 主入口 ===
def main():
    import argparse
    parser = argparse.ArgumentParser(description="小红书采集脚本 (⚠ 高风险, 低频使用)")
    parser.add_argument("--query", type=str, default="AI工具推荐",
                        help="搜索关键词 (默认: AI工具推荐)")
    parser.add_argument("--count", type=int, default=10,
                        help="采集条数 (default: 10, max: 15)")
    parser.add_argument("--dry-run", action="store_true",
                        help="空跑测试")
    parser.add_argument("--skip-status-check", action="store_true",
                        help="跳过账号状态检查 (节省请求)")
    args = parser.parse_args()

    # 硬限制: 最多 15 条
    count = min(args.count, 15)
    if args.count > 15:
        logger.warning(f"⚠ 采集数量限制为 15 (请求了 {args.count})")

    date_str = datetime.now().strftime("%Y%m%d")

    # 检查 Cookie
    cookies = load_cookies()
    if not cookies:
        logger.error("❌ 无 Cookie，无法采集")
        sys.exit(1)

    # 注入环境变量
    os.environ["XHS_WEB_SESSION"] = os.environ.get("XHS_WEB_SESSION", cookies.get("web_session", ""))
    os.environ["XHS_A1"] = os.environ.get("XHS_A1", cookies.get("a1", ""))
    os.environ["XHS_WEB_ID"] = os.environ.get("XHS_WEB_ID", cookies.get("webId", ""))

    # 检查账号状态
    if not args.skip_status_check:
        if not check_account_status():
            logger.error("🚨 账号状态异常，终止采集")
            sys.exit(1)

    # 采集 (单关键词)
    all_items = fetch_search(args.query, count=count)

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
            logger.info(f"  {item['title'][:60]}...")
        return

    # 写入 data/
    out_path = DATA_DIR / f"xiaohongshu_daily_{date_str}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ 已保存 {len(unique)} 条 → {out_path}")


if __name__ == "__main__":
    main()
