#!/usr/bin/env python3
"""
enrich_quotes.py - 毒舌点评 enrichment
在 raw_*.json 数据生成后、sync_github_pages 前运行，
用 DeepSeek 给每条新闻生成一条毒舌点评（quote 字段）。

用法:
  python3 scripts/enrich_quotes.py                          # 处理今天所有数据
  python3 scripts/enrich_quotes.py --date 20260508           # 指定日期
  python3 scripts/enrich_quotes.py --type dev                # 只处理开发者日报
  python3 scripts/enrich_quotes.py --dry-run                 # 预览不写入

LLM 调用:
  通过 `openclaw infer model run` CLI 调用，使用系统配置的模型。
  无需额外 API key。
"""

import json, os, subprocess, sys, time, logging
from datetime import datetime
from pathlib import Path
from typing import Optional

# ---- 路径 ----
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "data"
LOG_DIR = WORKSPACE / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_DIR / "enrich_quotes.log")],
)
logger = logging.getLogger(__name__)

# ---- 配置 ----
LLM_MODEL = os.environ.get("ENRICH_MODEL", "deepseek/deepseek-v4-pro")  # 通过 openclaw CLI 调用

# 每批处理条数（控制 API 调用次数）
BATCH_SIZE = 20  # 减少 CLI 启动次数

# 每条毒舌点评的 prompt
QUOTE_PROMPT_TEMPLATE = """你是"毒舌点评师"，专门用黑色幽默给新闻写一句短评。

规则：
- 长度：15-25 字
- 风格：犀利、幽默、一针见血，像脱口秀开场白
- 不要重复标题里的词
- 不要用"这""那""很"等口水词
- 给每条新闻单独输出一行，格式：序号. 点评

新闻列表：
{articles}

直接输出点评，一行一条："""


def load_articles(date_str: str, article_type: str) -> tuple[list[dict], Path]:
    """加载指定类型和日期的文章"""
    type_map = {
        "industry": f"raw_articles_{date_str}.json",
        "dev": f"raw_dev_{date_str}.json",
        "social": f"raw_social_{date_str}.json",
    }
    filename = type_map.get(article_type)
    if not filename:
        raise ValueError(f"未知类型: {article_type}, 可选: {list(type_map.keys())}")

    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"数据文件不存在: {path}")

    with open(path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    return articles, path


def needs_quote(article: dict) -> bool:
    """判断文章是否缺少毒舌点评"""
    return not article.get("quote") or article.get("quote", "").strip() == ""


def build_batch_prompt(batch: list[dict]) -> str:
    """为一批文章构建 prompt"""
    lines = []
    for i, art in enumerate(batch, 1):
        title = art.get("title", "无标题")[:60]
        content = art.get("content", "")[:80]
        lines.append(f"{i}. 标题：{title}\n   摘要：{content}")
    return QUOTE_PROMPT_TEMPLATE.format(articles="\n".join(lines))


def call_llm(prompt: str, retries: int = 2) -> str:
    """通过 openclaw CLI 调用 LLM 生成毒舌点评"""
    system_prompt = "你是毒舌点评师，输出简洁有力，格式严格按要求。"
    full_prompt = f"{system_prompt}\n\n{prompt}"

    for attempt in range(retries + 1):
        try:
            result = subprocess.run(
                [
                    "openclaw", "infer", "model", "run",
                    "--model", LLM_MODEL,
                    "--prompt", full_prompt,
                    "--json",
                    "--local",  # 绕过 agent 模型限制
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode != 0:
                raise RuntimeError(f"CLI 返回非零: {result.returncode}, stderr: {result.stderr[:200]}")

            # 解析 JSON 输出: { ok, outputs: [{ text }] }
            data = json.loads(result.stdout)
            content = ""
            if isinstance(data, dict):
                outputs = data.get("outputs", [])
                if outputs and isinstance(outputs, list):
                    content = outputs[0].get("text", "")
                if not content:
                    content = data.get("content") or data.get("text", "")
            elif isinstance(data, str):
                content = data
            return content.strip()

        except Exception as e:
            logger.warning(f"LLM 调用失败 (尝试 {attempt+1}/{retries+1}): {e}")
            if attempt < retries:
                time.sleep(2 ** attempt)
            else:
                raise

    return ""  # unreachable


def parse_quotes(raw_output: str, expected_count: int) -> list[str]:
    """解析 DeepSeek 输出为毒舌点评列表"""
    quotes = []
    for line in raw_output.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # 去掉编号前缀 "1. " "1、" "1)" 等
        for sep in [". ", ".", "、", ") ", ")"]:
            if line[0].isdigit() and sep in line[:4]:
                line = line.split(sep, 1)[-1].strip()
                break
        # 去掉引号
        line = line.strip('"\'""''「」')
        if line and len(line) >= 5:
            quotes.append(line)

    # 如果解析数量不对，补充空串
    while len(quotes) < expected_count:
        quotes.append("")
    return quotes[:expected_count]


def enrich_file(
    date_str: str, article_type: str, dry_run: bool = False
) -> dict:
    """对单个数据文件执行 enrichment"""
    articles, path = load_articles(date_str, article_type)
    logger.info(f"加载 {article_type}: {len(articles)} 条")

    # 筛选需要 enrichment 的文章
    to_enrich = [(i, art) for i, art in enumerate(articles) if needs_quote(art)]
    total = len(to_enrich)

    if total == 0:
        logger.info(f"{article_type}: 所有文章已有毒舌点评，跳过")
        return {"total": len(articles), "enriched": 0, "skipped": len(articles)}

    logger.info(f"{article_type}: {total}/{len(articles)} 条需要生成毒舌点评")

    # 分批调用 API
    enriched = 0
    for batch_start in range(0, total, BATCH_SIZE):
        batch = to_enrich[batch_start : batch_start + BATCH_SIZE]
        batch_articles = [art for _, art in batch]

        try:
            prompt = build_batch_prompt(batch_articles)
            raw = call_llm(prompt)
            quotes = parse_quotes(raw, len(batch))

            for (idx, _), quote in zip(batch, quotes):
                if quote:
                    articles[idx]["quote"] = quote
                    enriched += 1

            logger.info(
                f"  batch {batch_start//BATCH_SIZE+1}: "
                f"生成 {len(quotes)} 条, 有效 {sum(1 for q in quotes if q)} 条"
            )
        except Exception as e:
            logger.error(f"  batch {batch_start//BATCH_SIZE+1} 失败: {e}")
            continue

        # API 限流保护
        if batch_start + BATCH_SIZE < total:
            time.sleep(1)

    if not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        logger.info(f"{article_type}: 已写入 {path} ({enriched} 条新增毒舌点评)")
    else:
        logger.info(f"{article_type}: [dry-run] 将写入 {enriched} 条毒舌点评")

    return {
        "total": len(articles),
        "enriched": enriched,
        "skipped": len(articles) - enriched,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="毒舌点评 enrichment")
    parser.add_argument("--date", default=datetime.now().strftime("%Y%m%d"), help="日期 YYYYMMDD")
    parser.add_argument("--type", choices=["industry", "dev", "social"], help="只处理指定类型")
    parser.add_argument("--dry-run", action="store_true", help="预览不写入")
    args = parser.parse_args()

    types = [args.type] if args.type else ["industry", "dev", "social"]
    results = {}
    all_ok = True

    for t in types:
        try:
            results[t] = enrich_file(args.date, t, dry_run=args.dry_run)
        except FileNotFoundError as e:
            logger.warning(f"跳过 {t}: {e}")
            results[t] = {"error": str(e)}
        except Exception as e:
            logger.error(f"{t} 处理失败: {e}")
            results[t] = {"error": str(e)}
            all_ok = False

    # 汇总
    total_enriched = sum(r.get("enriched", 0) for r in results.values())
    total_skipped = sum(r.get("skipped", 0) for r in results.values())
    logger.info(
        f"汇总: {total_enriched} 条新增毒舌点评, {total_skipped} 条已有/跳过"
    )

    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
