#!/usr/bin/env python3
"""
generate_combined_3days.py
生成 combined_3days_YYYYMMDD.json，包含最近3天的全量数据（去重）
"""
import json
import os
import sys
import re
from datetime import datetime, timezone, timedelta, date

SECTIONS = ['industry', 'dev', 'ai', 'startup', 'design']

# ===== 唯一标识符 uid =====
def gen_uid(section: str, title: str, url: str = "") -> str:
    """
    生成稳定的 uid：{section}_{8位hex哈希(title+url)}
    同一篇文章（相同标题+URL）跨天保持同一 uid
    用于收藏/已读/投票等持久化标识
    """
    import hashlib
    # 归一化：去掉 emoji（非BMP字符）、统一标点、小写
    key = (title or '') + '|' + (url or '')
    key = key.lower()
    key = re.sub(r'[^\u0000-\uFFFF]', '', key)  # 去掉大部分 emoji（非BMP平面）
    key = key.replace('：', ':').replace('—', '-').replace('–', '-').replace('—', '-')
    # 统一标点前后的空格：去掉冒号前的空格，确保冒号后有一个空格
    key = re.sub(r'\s*:\s*', ': ', key)
    key = re.sub(r'\s+', ' ', key).strip()
    # 短哈希（8位hex）
    h = hashlib.md5(key.encode('utf-8')).hexdigest()[:8]
    return f"{section}_{h}"


def get_recent_files(section, index_data, max_days=3):
    """从 index.json history 中获取最近 max_days 个文件路径（排除今日）"""
    history = index_data.get('history', {})
    section_history = history.get(section, [])
    
    # 排除今日文件（已在顶层 latest 中），取最近2天
    today_file = index_data.get(section)
    recent = []
    for fname in section_history:
        if fname != today_file:
            recent.append(fname)
        if len(recent) >= max_days - 1:
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
        # 可能是 dict 格式，取 items 字段
        if isinstance(data, dict) and 'items' in data:
            return data['items']
        return []
    except Exception as e:
        print(f"  [warn] 加载失败 {filepath}: {e}", file=sys.stderr)
        return []

def filter_recent(items, max_days_back=3, today_date=None):
    """
    过滤掉超过 max_days_back 天的 item
    只保留 published 日期在最近 max_days_back 天内的 item
    """
    if not today_date:
        today_date = datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')
    try:
        today = datetime.strptime(str(today_date)[:8], '%Y%m%d').date()
    except:
        return items  # 如果日期解析失败则不过滤
    
    result = []
    cutoff = today - timedelta(days=max_days_back)
    for item in items:
        pub = item.get('published', '')
        if not pub:
            continue  # 无日期的不展示
        try:
            # 统一为 YYYY-MM-DD 格式，去掉时间戳尾部
            pub_clean = pub[:10]
            item_date = datetime.strptime(pub_clean, '%Y-%m-%d').date()
            if item_date >= cutoff:
                # 统一 published 字段为日期格式，避免小程序显示 '2026-05-11T02:50:03...'
                item['published'] = pub_clean
                result.append(item)
        except:
            result.append(item)  # 无法解析的日期保持原样
    return result


def merge_and_deduplicate(items_by_day, section=""):
    """
    合并多日数据，按 URL 去重，保留最新日期的版本
    同时为每条注入 uid（若已存在则不覆盖）
    items_by_day: [(date_str, items_list), ...] 按日期从新到旧排列
    """
    url_to_item = {}
    date_priority = {}
    
    for i, (date_str, items) in enumerate(items_by_day):
        priority = len(items_by_day) - i
        for item in items:
            # 注入 uid（客户端持久化的主键，不覆盖已有 uid）
            if 'uid' not in item:
                uid_str = gen_uid(section, item.get('title', ''), item.get('url', ''))
                item['uid'] = uid_str
            url = item.get('url', '')
            if not url:
                continue
            if url not in url_to_item:
                url_to_item[url] = item
                date_priority[url] = priority
            elif date_priority.get(url, 0) < priority:
                url_to_item[url] = item
                date_priority[url] = priority
    
    return list(url_to_item.values())

def main():
    workdir = os.path.dirname(os.path.abspath(__file__))
    # 如果从 scripts/ 调用，workdir 是脚本目录；切换到 dushe-daily-data/
    if os.path.basename(workdir) == 'scripts':
        workdir = os.path.dirname(workdir)
    
    os.chdir(workdir)
    
    # 读取 index.json
    with open('index.json', 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    # 找到今日日期（从 latest 文件名中提取）
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
    
    combined = {}
    total_items = 0
    
    for section in SECTIONS:
        # 收集3天数据：今日 + 最近2天历史
        today_file = index_data.get(section, '')
        recent_files = get_recent_files(section, index_data, max_days=3)
        
        # 按日期从新到旧排列（今日优先）
        items_by_day = []
        if today_file and os.path.exists(today_file):
            items_by_day.append((today_date, load_items_from_file(today_file)))
        
        for fname in recent_files:
            if os.path.exists(fname):
                # 从文件名提取日期
                m = re.search(r'_(\d{8})\.json$', fname)
                date_str = m.group(1) if m else 'unknown'
                items_by_day.append((date_str, load_items_from_file(fname)))
        
        # 合并去重
        merged = merge_and_deduplicate(items_by_day, section=section)
        # 过滤掉超过3天的旧数据
        merged = filter_recent(merged, max_days_back=2, today_date=today_date)
        combined[section] = merged
        total_items += len(merged)
        print(f"  {section}: {len(merged)} 条（来源: {today_file}, {len(recent_files)} 天历史）")
    
    # 写入 combined_3days 文件
    out_fname = f'combined_3days_{today_date}.json'
    with open(out_fname, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    
    print(f"[combined_3days] ✅ 生成 {out_fname}，共 {total_items} 条数据")
    
    # 更新 index.json 添加 combined_3days 字段
    index_data['combined_3days'] = {today_date: out_fname}
    with open('index.json', 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"[combined_3days] ✅ index.json 已更新 combined_3days 字段")

if __name__ == '__main__':
    main()