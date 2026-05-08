#!/usr/bin/env python3
"""
push_to_feishu.py - 飞书推送脚本
读取生成的日报，推送到飞书群
"""

import logging
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
        logging.FileHandler(LOG_DIR / "push.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ===================== 配置 =====================
# 飞书自定义机器人 Webhook URL（从环境变量或配置文件读取）
FEISHU_WEBHOOK_URL = "FEISHU_WEBHOOK_URL"


def load_report(date_str: str = None) -> str:
    """读取日报文件内容"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    report_path = SCRIPT_DIR / "reports" / f"{date_str}.md"
    if not report_path.exists():
        raise FileNotFoundError(f"未找到日报: {report_path}")

    with open(report_path, "r", encoding="utf-8") as f:
        return f.read()


def build_card(report_content: str, date_str: str) -> dict:
    """构建飞书交互卡片"""
    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"📰 行业热点日报 | {date_str}",
                },
                "template": "blue",
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": report_content,
                },
                {
                    "tag": "hr",
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"由 IndustryDailyBot 自动生成 | {datetime.now().strftime('%H:%M:%S')}",
                        }
                    ],
                },
            ],
        },
    }


def send_feishu(webhook_url: str, payload: dict, retries: int = 2) -> bool:
    """发送飞书消息，重试机制"""
    import httpx

    for attempt in range(retries + 1):
        try:
            resp = httpx.post(webhook_url, json=payload, timeout=10)
            if resp.status_code == 200:
                result = resp.json()
                if result.get("code") == 0 or result.get("StatusCode") == 0:
                    logger.info("飞书消息发送成功")
                    return True
                logger.warning(f"飞书返回错误: {result}")
            else:
                logger.warning(f"HTTP {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"发送失败 (attempt {attempt + 1}/{retries + 1}): {e}")

        if attempt < retries:
            import time
            time.sleep(5)

    return False


def main():
    date_str = datetime.now().strftime("%Y-%m-%d")
    date_short = datetime.now().strftime("%Y%m%d")

    # 读取日报
    try:
        report_content = load_report(date_str)
        logger.info(f"读取日报成功，字数 {len(report_content)}")
    except FileNotFoundError as e:
        logger.error(f"无法读取日报: {e}")
        sys.exit(1)

    # 构建卡片
    card = build_card(report_content, date_str)

    # 获取 Webhook URL
    import os
    webhook_url = os.environ.get(FEISHU_WEBHOOK_URL, "")

    # 如果没配置环境变量，从配置文件读取（备用）
    if not webhook_url:
        config_path = SCRIPT_DIR / "config" / "feishu_webhook.txt"
        if config_path.exists():
            webhook_url = config_path.read_text().strip()
        else:
            # 开发/测试用的占位 URL
            webhook_url = os.environ.get(
                "FEISHU_WEBHOOK_URL",
                "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR-WEBHOOK-ID"
            )

    logger.info(f"开始推送飞书 (webhook: {webhook_url[:50]}...)")
    success = send_feishu(webhook_url, card)

    if success:
        print(f"✅ 飞书推送成功")
        logger.info("推送完成")
    else:
        print(f"❌ 飞书推送失败，请检查 logs/push.log")
        logger.error("推送失败")
        sys.exit(1)


if __name__ == "__main__":
    main()