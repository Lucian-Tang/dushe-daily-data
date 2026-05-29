#!/usr/bin/env python3
"""
classify_ai_models.py - AI模型动态分类器
读取 ai_daily_YYYYMMDD.json，对每条数据进行：
1. 模型归属分类（vendor）：基于关键词匹配，识别所属公司/模型系列
2. 方向标签分类（direction）：6类（模型发布/工具平台/研究论文/应用落地/政策合规/行业动态）
输出 data/ai_models_classified_YYYYMMDD.json
"""

import json, re, logging, argparse
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / "data"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── 模型归属分类规则（vendor classification）──
# 格式: { vendor_key: { "displayName": "...", "icon": "...", "keywords": ["keyword", ...] } }
VENDOR_RULES = [
    {
        "key": "anthropic",
        "displayName": "Anthropic/Claude",
        "icon": "🧬",
        "keywords": ["claude", "anthropic", "claude code", "opus", "sonnet", "haiku"],
    },
    {
        "key": "openai",
        "displayName": "OpenAI/GPT",
        "icon": "🔬",
        "keywords": ["openai", "gpt", "chatgpt", "o1", "o3", "o4", "dall-e", "sora"],
    },
    {
        "key": "google",
        "displayName": "Google/Gemini",
        "icon": "🌐",
        "keywords": ["gemini", "google", "bard", "deepmind", "alphafold", "veo"],
    },
    {
        "key": "alibaba",
        "displayName": "阿里巴巴/Qwen",
        "icon": "☁️",
        "keywords": ["qwen", "通义", "阿里", "alibaba"],
    },
    {
        "key": "deepseek",
        "displayName": "DeepSeek",
        "icon": "🔍",
        "keywords": ["deepseek"],
    },
    {
        "key": "meta",
        "displayName": "Meta/LLaMA",
        "icon": "👁️",
        "keywords": ["meta", "llama", "facebook ai"],
    },
    {
        "key": "amazon",
        "displayName": "Amazon/AWS",
        "icon": "📦",
        "keywords": ["amazon", "aws", "nova", "prime"],
    },
    {
        "key": "apple",
        "displayName": "Apple",
        "icon": "🍎",
        "keywords": ["apple", "ios", "macos", "siri"],
    },
    {
        "key": "mistral",
        "displayName": "Mistral",
        "icon": "💨",
        "keywords": ["mistral"],
    },
    {
        "key": "xai",
        "displayName": "xAI/Grok",
        "icon": "🚀",
        "keywords": ["xai", "grok", "elon"],
    },
    {
        "key": "microsoft",
        "displayName": "Microsoft",
        "icon": "🪟",
        "keywords": ["microsoft", "azure", "copilot"],
    },
    {
        "key": "other",
        "displayName": "其他",
        "icon": "📰",
        "keywords": [],  # catch-all
    },
]

# ── 方向标签分类规则（direction classification）──
DIRECTION_RULES = [
    {
        "key": "model_release",
        "label": "模型发布",
        "keywords": [
            "发布", "上线", "推出", "release", "launch", "upgrade", "升级",
            "开源", "发布新", "推出新", "亮相", "发布大模型", "开箱",
        ],
    },
    {
        "key": "tool_platform",
        "label": "工具/平台",
        "keywords": [
            "sdk", "api", "plugin", "agent", "workflow", "tool", "coding",
            "ide", "编辑器", "工具", "平台", "产品", "功能", "更新",
            "app", "应用推出", "cli", "figma", "notion", "cursor",
            "框架", "extension", "扩展", "插件",
        ],
    },
    {
        "key": "research",
        "label": "研究/论文",
        "keywords": [
            "paper", "research", "benchmark", "训练", "training",
            "研究", "论文", "实验", "评测", "推理", "reasoning",
            "性能", "曲线", "突破", "创新",
        ],
    },
    {
        "key": "application",
        "label": "应用/落地",
        "keywords": [
            "deploy", "应用", "企业", "合作", "医疗", "金融", "教育",
            "落地", "生产", "上线案例", "客户", "解决方案",
            "制药", "药物", "游戏", "动画", "娱乐",
            "视频制作", "创意", "短片", "音乐", "艺术",
        ],
    },
    {
        "key": "policy",
        "label": "政策/合规",
        "keywords": [
            "监管", "policy", "合规", "版权", "法律", "法规",
            "法案", "诉讼", "立法", "商标", "专利",
            "审查", "censor", "禁令", "禁止",
        ],
    },
    {
        "key": "industry",
        "label": "行业动态",
        "keywords": [
            "融资", "收购", "hire", "裁员", "partnership",
            "市值", "股价", "财报", "ipo", "投资",
            "竞争", "行业", "生态", "趋势", "格局",
            "内卷", "变现", "商业化", "营收",
        ],
    },
]


def classify_vendor(title, content):
    """基于标题和内容的关键词匹配，判断模型归属"""
    text = f"{title} {content}".lower()

    # 先检查特定规则（避免误匹配）
    # Anthropic 优先检测（避免 Claude Code 里面的 'code' 干扰）
    for rule in VENDOR_RULES:
        if rule["key"] == "other":
            continue
        for kw in rule["keywords"]:
            if kw.lower() in text:
                return rule["key"]

    return "other"


def classify_direction(title, content):
    """基于标题和内容的关键词匹配，判断方向标签"""
    text = f"{title} {content}".lower()

    # 对每个方向评分（匹配关键词数）
    scores = {}
    for rule in DIRECTION_RULES:
        score = 0
        for kw in rule["keywords"]:
            if kw.lower() in text:
                score += 1
        scores[rule["key"]] = score

    # 取最高分的方向
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "行业动态"  # 默认归类为行业动态

    # 返回 label
    for rule in DIRECTION_RULES:
        if rule["key"] == best:
            return rule["label"]

    return "行业动态"


def get_vendor_info(vendor_key):
    """获取 vendor 的 displayName 和 icon"""
    for rule in VENDOR_RULES:
        if rule["key"] == vendor_key:
            return rule["displayName"], rule["icon"]
    return "其他", "📰"


def main():
    ap = argparse.ArgumentParser(description="AI模型动态分类器")
    ap.add_argument("--date", "-d", default=datetime.now().strftime("%Y%m%d"))
    args = ap.parse_args()

    date_str = args.date
    input_path = WORKSPACE / f"ai_daily_{date_str}.json"

    if not input_path.exists():
        logger.error(f"❌ 输入文件不存在: {input_path}")
        # 不退出，允许管线继续
        return

    with open(input_path, encoding="utf-8") as f:
        items = json.load(f)

    if not isinstance(items, list):
        logger.error(f"❌ 输入数据格式错误: {type(items)}")
        return

    logger.info(f"读取 {len(items)} 条 AI 数据")

    classified = []
    vendor_stats = {}
    direction_stats = {}

    for item in items:
        title = item.get("title", "")
        content = item.get("content", "")
        vendor_key = classify_vendor(title, content)
        direction = classify_direction(title, content)

        classified_item = {
            "uid": item.get("uid", ""),
            "title": title,
            "content": content,
            "quote": item.get("quote", ""),
            "source": item.get("source", ""),
            "url": item.get("url", ""),
            "published": item.get("published", ""),
            "vendor": vendor_key,
            "direction": direction,
        }
        classified.append(classified_item)

        # 统计
        vendor_stats[vendor_key] = vendor_stats.get(vendor_key, 0) + 1
        direction_stats[direction] = direction_stats.get(direction, 0) + 1

    # 保存
    out_path = DATA_DIR / f"ai_models_classified_{date_str}.json"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(classified, f, ensure_ascii=False, indent=2)

    # 同时存一份到根目录
    root_out = WORKSPACE / f"ai_models_classified_{date_str}.json"
    with open(root_out, "w", encoding="utf-8") as f:
        json.dump(classified, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ 分类完成: {len(classified)} 条 → {out_path.name}")
    logger.info(f"   Vendor 分布: {json.dumps(vendor_stats, ensure_ascii=False)}")
    logger.info(f"   Direction 分布: {json.dumps(direction_stats, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
