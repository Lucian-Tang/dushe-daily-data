#!/usr/bin/env python3
"""
fetch_wechat_exa.py - 微信公众号文章采集脚本 (Phase 1 POC)
依赖: Exa Search → mcporter MCP (免费, 无需 API Key)
原理: Exa 搜索引擎已索引微信公众号文章, 通过 includeDomains 过滤
输出: data/wechat_daily_YYYYMMDD.json

使用方式:
  python3 scripts/fetch_wechat_exa.py
  python3 scripts/fetch_wechat_exa.py --queries "AI agent,LLM,大模型" --count 10
  python3 scripts/fetch_wechat_exa.py --dry-run

⚠ 注意:
  - Exa 免费层有调用次数限制 (约 1000 次/月)
  - 公众号文章索引延迟 2-4 小时
  - 覆盖率未经大规模验证

输出格式:
[
  {
    "uid": "wechat_a1b2c3d4",
    "title": "公众号文章标题",
    "content": "文章摘要 (≤200字)",
    "quote": "毒舌点评 (15-30字)",
    "source": "微信公众号",
    "url": "https://mp.weixin.qq.com/s/xxxxx",
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

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# === 日志配置 ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# === 毒舌点评模板 (微信公众号专用, 15-30字) ===
WECHAT_QUOTES = [
    "公众号 AI 圈的标题党，从来不让人失望",
    "看完标题以为要宣布 AGI 了，读完全文发现是广告",
    "中国 AI 圈的公众号推文，精彩程度堪比连载小说",
    "这篇文章的标题已经把所有信息量都用完了",
    "公众号大佬今儿说了啥——我看完了，但我不说",
    "AI 公众号今日份：三成干货七成软文",
    "又一篇万字长文，读完后唯一的收获是标题",
    "中国 AI 自媒体的流量密码：标题里带'颠覆'",
    "公众号的评论区比正文有营养多了（如果开放的话）",
    "这篇文章如果是人写的，我给 10 分；如果是 AI 写的，我给 8 分",
    "标题写着'深度解读'，内容全是复制粘贴",
    "AI 圈公众号的终极课题：如何把老新闻写成新发现",
    "这篇文章的排版比内容用心十倍",
    "公众号推文的收藏/阅读比，永远是个谜",
    "今天的 AI 公众号推送，又是熟悉的配方",
    "科普文写得像悬疑小说——这就是微信 AI 圈的特色",
    "按微信公众号的节奏，这个消息已经「过时」三天了",
    "AI 自媒体的一句名言：先写上热搜，活到明天再说",
]

# === UID 生成 ===
def gen_uid(title: str, url: str = "") -> str:
    def normalize(s: str) -> str:
        return re.sub(r'[^\u0000-\uFFFF]', '', s)\
                 .replace('：', ':').replace('—', '-').replace('–', '-')\
                 .lower().strip()
    key = normalize(title) + '|' + normalize(url)
    return f"wechat_{hashlib.md5(key.encode()).hexdigest()[:8]}"


# === Exa MCP 调用 (通过 mcporter) ===
def call_exa_search(query: str, num_results: int = 10, days_old: int = 1) -> Optional[list]:
    """
    通过 mcporter 调用 Exa 搜索微信公众号文章
    返回: [{"title", "url", "text", "publishedDate", "author"}, ...]
    """
    # 构建 mcporter 命令
    # mcporter call 'exa.web_search_exa(query: "AI agent", numResults: 10, includeDomains: ["mp.weixin.qq.com"])'
    include_domains = 'includeDomains: ["mp.weixin.qq.com"]'
    cmd_parts = [
        "mcporter", "call",
        f'exa.web_search_exa(query: "{query}", numResults: {num_results}, {include_domains})'
    ]

    try:
        logger.info(f"🔍 Exa 搜索: '{query}' (n={num_results})...")
        # 注意: mcporter 可能需要交互式环境, 在 cron 中可能需要设置环境变量
        result = subprocess.run(
            cmd_parts,
            capture_output=True, text=True,
            timeout=120,
            env={**os.environ, "NO_COLOR": "1"}  # 禁止颜色输出
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if stderr:
            logger.debug(f"Exa stderr: {stderr[:300]}")

        if result.returncode != 0:
            logger.error(f"❌ Exa 搜索失败 (exit={result.returncode}): {stderr[:500]}")
            return None

        # 尝试解析 JSON 输出
        # mcporter 输出格式可能为纯 JSON 或带前缀的文本
        return parse_exa_output(stdout)

    except subprocess.TimeoutExpired:
        logger.error("❌ Exa 搜索超时")
        return None
    except FileNotFoundError:
        logger.error("❌ mcporter 未安装 (npm install -g mcporter)")
        return None
    except Exception as e:
        logger.error(f"❌ Exa 搜索异常: {e}")
        return None


def parse_exa_output(raw: str) -> Optional[list]:
    """解析 Exa 搜索结果"""
    # Exa 输出可能直接是 JSON, 也可能是带前缀的文本
    # 尝试: 1) 直接 JSON 解析  2) 提取 JSON 块

    # 尝试 1: 直接解析
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            results = data.get("results", data.get("data", []))
            if isinstance(results, list):
                return results
    except json.JSONDecodeError:
        pass

    # 尝试 2: 提取 JSON 块
    json_match = re.search(r'\[[\s\S]*\]', raw)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

        json_match = re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                if isinstance(data, list):
                    return data
                if isinstance(data, dict):
                    results = data.get("results", data.get("data", []))
                    if isinstance(results, list):
                        return results
            except json.JSONDecodeError:
                pass

    # 尝试 3: 行解析 (fallback)
    logger.warning("⚠ JSON 解析失败, 尝试行解析...")
    results = []
    for line in raw.split('\n'):
        line = line.strip()
        if line.startswith('{') and line.endswith('}'):
            try:
                obj = json.loads(line)
                if isinstance(obj, dict) and obj.get("url"):
                    results.append(obj)
            except json.JSONDecodeError:
                continue
    return results if results else None


# === 标准化输出格式 ===
def normalize_results(exa_results: list, date_str: str) -> list:
    """将 Exa 返回结果转换为有数Feed 标准格式"""
    items = []
    for r in exa_results:
        if not isinstance(r, dict):
            continue

        title = (r.get("title") or "").strip()
        url = (r.get("url") or "").strip()

        # 过滤: 确保是微信公众号文章
        if url and "mp.weixin.qq.com" not in url:
            logger.debug(f"⏭ 跳过非微信链接: {url[:60]}")
            continue

        content = (r.get("text") or r.get("snippet") or r.get("description") or "").strip()[:200]
        author = r.get("author", "")
        published_date = r.get("publishedDate", r.get("published_date", ""))

        # 优先用 Exa 返回的日期，fallback 到今天
        if published_date:
            published = published_date[:10]  # 取 YYYY-MM-DD
        else:
            published = date_str[:4] + "-" + date_str[4:6] + "-" + date_str[6:8]

        uid = gen_uid(title, url)

        items.append({
            "uid": uid,
            "title": title,
            "content": content,
            "quote": random.choice(WECHAT_QUOTES),
            "source": "微信公众号",
            "url": url,
            "published": published,
            "_meta": {
                "author": author,
                "exa_date": published_date,
            }
        })

    return items


# === 主采集逻辑 ===
def fetch_wechat(query: str, count: int = 10) -> list:
    """针对单个关键词采集微信公众号文章"""
    date_str = datetime.now().strftime("%Y%m%d")
    exa_results = call_exa_search(query, num_results=count)
    if not exa_results:
        logger.warning(f"⚠ Exa 搜索 '{query}' 无结果")
        return []
    return normalize_results(exa_results, date_str)


# === 主入口 ===
def main():
    import argparse
    parser = argparse.ArgumentParser(description="微信公众号 Exa 搜索采集脚本")
    parser.add_argument("--queries", type=str,
                        default="AI agent,LLM大模型,人工智能,DeepSeek",
                        help="搜索关键词,逗号分隔")
    parser.add_argument("--count", type=int, default=10,
                        help="每个关键词采集条数 (default: 10)")
    parser.add_argument("--dry-run", action="store_true",
                        help="空跑测试")
    args = parser.parse_args()

    date_str = datetime.now().strftime("%Y%m%d")
    published = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    # 检查 mcporter 是否安装
    try:
        subprocess.run(["mcporter", "--version"], capture_output=True, timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.error("❌ mcporter 未安装。请执行: npm install -g mcporter && mcporter config add exa https://mcp.exa.ai/mcp")
        sys.exit(1)

    # 检查 Exa MCP 配置
    config_check = subprocess.run(["mcporter", "list"], capture_output=True, text=True, timeout=10)
    if "exa" not in config_check.stdout.lower():
        logger.error("❌ Exa MCP 未配置。请执行: mcporter config add exa https://mcp.exa.ai/mcp")
        sys.exit(1)

    # 采集
    queries = [q.strip() for q in args.queries.split(",") if q.strip()]
    all_items = []

    for q in queries:
        logger.info(f"🔍 采集关键词: '{q}'")
        items = fetch_wechat(q, count=args.count)
        all_items.extend(items)
        logger.info(f"✅ '{q}': {len(items)} 条")

        # 请求间隔 (Exa 免费层建议≥120s)
        if len(queries) > 1:
            logger.info(f"⏳ 等待 2 秒 (POC 模式)...")
            time.sleep(2)  # POC: 2秒; 生产: 120秒

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
    out_path = DATA_DIR / f"wechat_daily_{date_str}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ 已保存 {len(unique)} 条 → {out_path}")

    # Fallback: 如果 Exa 无结果, 尝试 wechat-article-search 技能
    if len(unique) == 0:
        logger.warning("⚠ Exa 搜索无结果, 建议手动降级到 wechat-article-search 技能")


if __name__ == "__main__":
    main()
