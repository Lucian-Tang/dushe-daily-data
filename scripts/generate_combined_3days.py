#!/usr/bin/env python3
"""
generate_combined_3days.py
生成 combined_3days_YYYYMMDD.json

三层架构：
  L2 (每日不可变) → L3 (直接拼接，不做跨天去重)

设计原则：
  - 前两天的数据不可变（直接从当日 L2 文件加载）
  - 不做跨天 URL 去重 — 同一篇文章在不同天出现就保留在不同天
  - 不做日期过滤 — L2 文件的 published 日期是原始数据，保留原样
  - 唯一做的事情是按 section 把三天数据首尾拼接
"""
import json
import os
import sys
import re
from datetime import datetime, timezone, timedelta, date

SECTIONS = ['industry', 'dev', 'ai', 'startup', 'design']

# ===== 敏感词过滤 =====
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLOCKLIST_PATH = os.path.join(SCRIPT_DIR, 'security-blocklist.json')


def load_blocklist():
    """加载敏感词 blocklist"""
    if not os.path.exists(BLOCKLIST_PATH):
        return [], {}
    try:
        with open(BLOCKLIST_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        blocklist = data.get('blocklist', [])
        if isinstance(blocklist, list):
            return blocklist, data
    except Exception as e:
        print(f"  [warn] 加载 blocklist 失败: {e}", file=sys.stderr)
    return [], {}


def is_blocked(text, blocklist):
    """检查文本是否包含 blocked 关键词"""
    if not blocklist or not text:
        return False
    text_lower = text.lower()
    return any(k.lower() in text_lower for k in blocklist)


def apply_blocklist_to_items(items, blocklist):
    """过滤 items 中包含敏感词的条目"""
    if not blocklist:
        return items, 0
    filtered = []
    blocked_count = 0
    for item in items:
        item_text = (item.get('title', '') or '') + ' ' + (item.get('content', '') or '')
        if is_blocked(item_text, blocklist):
            blocked_count += 1
        else:
            filtered.append(item)
    return filtered, blocked_count

# ===== 唯一标识符 uid =====
def gen_uid(section: str, title: str, url: str = "") -> str:
    """
    生成稳定的 uid:{section}_{8位hex哈希(title+url)}
    同一篇文章(相同title+URL)跨天保持同一 uid
    用于收藏/已读/投票等持久化标识
    """
    import hashlib
    # 归一化:去掉 emoji(非BMP字符)、统一标点、小写
    key = (title or '') + '|' + (url or '')
    key = key.lower()
    key = re.sub(r'[^\u0000-\uFFFF]', '', key)  # 去掉大部分 emoji(非BMP平面)
    key = key.replace('：', ':').replace('—', '-').replace('–', '-')
    # 统一标点前后的空格:去掉冒号前的空格,确保冒号后有一个空格
    key = re.sub(r'\s*:\s*', ': ', key)
    key = re.sub(r'\s+', ' ', key).strip()
    # 短哈希(8位hex)
    h = hashlib.md5(key.encode('utf-8')).hexdigest()[:8]
    return f"{section}_{h}"


def get_recent_files(section, index_data, max_days=2):
    """从 index.json history 中获取最近 max_days 个文件路径(排除今日)"""
    history = index_data.get('history', {})
    section_history = history.get(section, [])

    # 排除今日文件(已在顶层 latest 中),从最靠近今天的文件开始取
    today_file = index_data.get(section)
    recent = []
    for fname in section_history:
        if fname != today_file:
            recent.append(fname)
        if len(recent) >= max_days:
            break
    return recent

def load_items_from_file(filepath):
    """加载单个 JSON 文件的 items 列表"""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        # 可能是 dict 格式,取 items 字段
        if isinstance(data, dict) and 'items' in data:
            return data['items']
        return []
    except Exception as e:
        print(f"  [warn] 加载失败 {filepath}: {e}", file=sys.stderr)
        return []


def main():
    workdir = os.path.dirname(os.path.abspath(__file__))
    # 如果从 scripts/ 调用,workdir 是脚本目录;切换到 dushe-daily-data/
    if os.path.basename(workdir) == 'scripts':
        workdir = os.path.dirname(workdir)

    os.chdir(workdir)

    # 读取 index.json
    with open('index.json', 'r', encoding='utf-8') as f:
        index_data = json.load(f)

    # 找到今日日期(从 latest 文件名中提取)
    today_date = None
    for section in SECTIONS:
        fname = index_data.get(section, '')
        m = re.search(r'_(\d{8})\.json$', fname)
        if m:
            today_date = m.group(1)
            break

    if not today_date:
        today_date = datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')

    print(f"[combined_3days] 今日日期: {today_date}")

    blocklist, security_data = load_blocklist()
    if blocklist:
        print(f"[combined_3days] 敏感词过滤: 已激活({len(blocklist)} 个关键词)")
    else:
        print("[combined_3days] 敏感词过滤: 未激活(blocklist 为空或不存在)")

    combined = {}
    total_items = 0
    total_blocked = 0

    for section in SECTIONS:
        # 找到三天的文件：今日 + 昨天 + 前天
        today_file = index_data.get(section, '')
        recent_files = get_recent_files(section, index_data, max_days=2)

        # 按日期从新到旧的顺序加载文件
        file_list = []
        if today_file:
            file_list.append(today_file)
        file_list.extend(recent_files)

        # 只加载，不做跨天去重 — 前两天的数据不可变
        # 同一篇文章不同天出现就保留在不同天（根据 published 日期区分）
        merged = []
        for fname in file_list:
            items = load_items_from_file(fname)
            for item in items:
                # 注入 uid
                if not item.get('uid'):
                    uid_str = gen_uid(section, item.get('title', ''), item.get('url', ''))
                    item['uid'] = uid_str
                # 统一 published 格式
                published_val = normalize_published(item.get('published', ''))
                if published_val:
                    item['published'] = published_val
                merged.append(item)

        # 敏感词过滤
        merged, blocked = apply_blocklist_to_items(merged, blocklist)
        total_blocked += blocked

        combined[section] = merged
        total_items += len(merged)
        print(f"  {section}: {len(merged)} 条(来源: {today_file}, {len(recent_files)} 天历史){' 🔒 过滤 ' + str(blocked) + ' 条' if blocked > 0 else ''}")

    # 写入 combined_3days 文件
    out_fname = f'combined_3days_{today_date}.json'
    with open(out_fname, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"[combined_3days] ✅ 生成 {out_fname}，共 {total_items} 条数据{'，过滤 ' + str(total_blocked) + ' 条敏感内容' if total_blocked > 0 else ''}")

    # 更新 index.json 添加 combined_3days 和 security 字段
    index_data['combined_3days'] = {today_date: out_fname}
    index_data['security'] = security_data.get('version') is not None and security_data or {
        'blocklist': blocklist
    }
    with open('index.json', 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"[combined_3days] ✅ index.json 已更新 combined_3days + security 字段")


def normalize_published(pub_str):
    """统一 published 字段为 YYYY-MM-DD 格式"""
    if not pub_str:
        return None
    clean = pub_str[:10]
    try:
        datetime.strptime(clean, '%Y-%m-%d')
        return clean
    except:
        return None


if __name__ == '__main__':
    main()
