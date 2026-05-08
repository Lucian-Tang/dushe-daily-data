#!/usr/bin/env python3
"""
daily_report.py - 日报生成脚本
调用 OpenClaw LLM，将原始文章生成为结构化日报
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# ===================== 日志 =====================
SCRIPT_DIR = Path(__file__).parent.parent
LOG_DIR = SCRIPT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "report.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ===================== LLM 调用 =====================
# 通过 OpenClaw 环境变量或内部接口调用 minimax-m2.7
# 注意：实际调用方式取决于 OpenClaw 的 agent 调用机制
# 这里用 subprocess + openclaw CLI 作为框架示例

MINIMAX_MODEL = "minimax-m2.7"


def build_prompt(articles: list[dict]) -> str:
    """构建发给 LLM 的 prompt"""

    # 按 category 分组
    categories = {}
    for art in articles:
        cat = art.get("category", "other")
        categories.setdefault(cat, []).append(art)

    # 构造文章列表摘要（每条取 title + content 前100字）
    articles_text = []
    for cat, arts in categories.items():
        articles_text.append(f"\n## {cat.upper()}")
        for i, art in enumerate(arts[:5], 1):  # 每类最多5条
            content_brief = art.get("content", "")[:100]
            articles_text.append(
                f"{i}. {art['title']}\n   来源: {art['source']} | {art.get('published','')}\n   内容: {content_brief}..."
            )

    articles_section = "\n".join(articles_text)

    prompt = f"""## SYSTEM PROMPT

你是科技产业分析师。请根据以下今日抓取的新闻文章，生成行业热点日报。

规则：
- 每个赛道选 3 条最重要新闻（不足则全部选）
- 每条新闻格式：
  **【摘要】** 不超过50字的摘要
  **【观点】** 不超过30字的一句话分析
- 按赛道分组，用 emoji 区分（🚗 自动驾驶 🤖 机器人 🧠 AI）
- 只输出日报内容，不要其他说明
- 不要重复文章标题中的字

## 今日文章

{articles_section}

## 输出格式

### 🚗 自动驾驶
1. [标题](URL)
   【摘要】<50字>
   【观点】<30字>

### 🤖 机器人
...

### 🧠 AI 大模型
...

---
来源：共抓取 {len(articles)} 条，选取最重要的报道
生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    return prompt


def call_llm(prompt: str) -> str:
    """通过 OpenClaw CLI 调用 LLM（框架实现）"""
    # 注意：这里的调用方式需要根据实际 OpenClaw 接口调整
    # 框架阶段使用环境变量 OPENCLAW_API_KEY 或类似机制

    # 方案A：使用 openclaw 的 chat 接口（如果支持 CLI）
    # 方案B：直接用 httpx 调用 minimax API（需要 API key）
    # 这里用方案A的框架代码，实际运行时根据环境配置

    import subprocess

    # 框架占位——实际实现需要确定如何从脚本内调用 OpenClaw LLM
    # 假设 OpenClaw 提供 `openclaw chat --model minimax-m2.7 --prompt` 接口
    try:
        result = subprocess.run(
            ["openclaw", "chat", "--model", MINIMAX_MODEL, "--prompt", prompt],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return result.stdout
        else:
            logger.error(f"LLM 调用失败: {result.stderr}")
            raise RuntimeError(f"LLM 调用失败: {result.stderr}")
    except FileNotFoundError:
        logger.warning("openclaw CLI 未找到，尝试通过 HTTP 接口调用...")
        return call_llm_http(prompt)


def call_llm_http(prompt: str) -> str:
    """通过 HTTP API 调用 minimax（框架占位）"""
    import httpx

    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if not api_key:
        logger.error("未设置 MINIMAX_API_KEY 环境变量")
        raise RuntimeError("LLM API key 未配置")

    # minimax API 调用框架（实际 endpoint 需确认）
    try:
        resp = httpx.post(
            "https://api.minimax.chat/v1/text/chatcompletion_pro",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "MINIMAX-M2.7",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 800,
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"HTTP LLM 调用失败: {e}")
        raise


def generate_report(articles: list[dict], output_path: Path) -> str:
    """生成日报并保存"""
    prompt = build_prompt(articles)
    logger.info("开始调用 LLM 生成日报...")

    content = call_llm(prompt)
    logger.info("LLM 生成完成")

    # 写入文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"日报已保存到 {output_path}")
    return content


def load_articles(date_str: str = None) -> list[dict]:
    """从 data/ 目录加载今天的文章"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y%m%d")

    data_dir = SCRIPT_DIR / "data"
    article_path = data_dir / f"raw_articles_{date_str}.json"

    if not article_path.exists():
        logger.error(f"文章文件不存在: {article_path}")
        raise FileNotFoundError(f"未找到文章数据: {article_path}")

    with open(article_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    date_str = datetime.now().strftime("%Y%m%d")
    date_display = datetime.now().strftime("%Y-%m-%d")

    try:
        articles = load_articles(date_str)
        logger.info(f"加载了 {len(articles)} 条文章")
    except FileNotFoundError as e:
        logger.error(f"无法加载文章数据: {e}")
        sys.exit(1)

    if not articles:
        logger.warning("文章列表为空，跳过生成")
        sys.exit(0)

    # 生成日报
    reports_dir = SCRIPT_DIR / "reports"
    reports_dir.mkdir(exist_ok=True)
    output_path = reports_dir / f"{date_display}.md"

    try:
        report = generate_report(articles, output_path)
        print(f"\n===== 生成的日报 =====\n{report}")
    except Exception as e:
        logger.error(f"日报生成失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()