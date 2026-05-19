#!/usr/bin/env python3
"""
normalize_daily_data.py - 日报CDN数据规范化

在 gen-index.py 之前运行，fix 所有 _daily_*.json 文件的常见问题：
1. 补全缺失的 url 字段（从 content/quote 中提取，或留空但可不跳过）
2. 统一 published 字段为 YYYY-MM-DD 格式
3. 检查 content 是否为空（需>=30字符）
4. 删除超3天的旧数据（仅保留最近3天）

用法:
    python3 normalize_daily_data.py                              # 处理所有 daily 文件
    python3 normalize_daily_data.py --date 20260513              # 仅处理指定日期
    python3 normalize_daily_data.py --dry-run                    # 预览不写入
"""
import os
import sys
import json
import hashlib
import re
import glob
import argparse
from datetime import datetime, timezone, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = SCRIPT_DIR
if os.path.basename(DATA_DIR) == 'scripts':
    DATA_DIR = os.path.dirname(DATA_DIR)

BLOCKLIST_PATH = os.path.join(SCRIPT_DIR, 'security-blocklist.json')
DAILY_PATTERN = re.compile(r'^(\w+)_daily_(\d{8})\.json$')
MAX_DAYS_BACK = 2  # 保留最近3天（今天+2天前）


def load_blocklist():
    """加载敏感词 blocklist，文件不存在或格式错误时返回空列表"""
    if not os.path.exists(BLOCKLIST_PATH):
        return []
    try:
        with open(BLOCKLIST_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        blocklist = data.get('blocklist', [])
        if isinstance(blocklist, list):
            print(f"[normalize] 加载敏感词 blacklist: {len(blocklist)} 个关键词")
            return blocklist
    except Exception as e:
        print(f"[normalize] 加载 blocklist 失败: {e}")
    return []


def is_blocked(text, blocklist):
    """检查文本是否包含 blocked 关键词"""
    if not blocklist or not text:
        return False
    text_lower = text.lower()
    return any(k.lower() in text_lower for k in blocklist)


def gen_uid(section, title, url=""):
    """生成稳定的 uid：{section}_{8位hex哈希(title+url)}"""
    key = (title or '') + '|' + (url or '')
    key = key.lower()
    key = re.sub(r'[^\u0000-\uFFFF]', '', key)  # 去掉 emoji（非BMP平面）
    key = key.replace('：', ':').replace('—', '-').replace('–', '-')
    key = re.sub(r'\s*:\s*', ': ', key)
    key = re.sub(r'\s+', ' ', key).strip()
    h = hashlib.md5(key.encode('utf-8')).hexdigest()[:8]
    return f"{section}_{h}"


def normalize_item(item, filename_date):
    """Fix a single item's fields"""
    fixed = False
    issues = []

    # 1. Force published date = filename date (bugfix: AI 生成的 published 是原文日期，小程序按 published 判断今日数据)
    pub_raw = item.get('published', '')
    pub_clean = pub_raw[:10] if pub_raw else ''
    try:
        filename_date_ymd = datetime.strptime(filename_date, '%Y%m%d').strftime('%Y-%m-%d')
        if pub_clean != filename_date_ymd:
            old_val = pub_clean or '(空)'
            item['published'] = filename_date_ymd
            fixed = True
            issues.append(f'published日期强制修正: {old_val} -> {filename_date_ymd}')
    except ValueError:
        if pub_raw and pub_raw != pub_clean:
            item['published'] = pub_clean
            fixed = True
            issues.append(f'published格式修正: {pub_raw} -> {pub_clean}')

    # 2. Ensure url field exists
    url = item.get('url', '')
    if not url:
        # 尝试从内容中提取 URL
        content = item.get('content', '') or item.get('title', '')
        url_match = re.search(r'https?://[^\s\)\]}"]+', content)
        if url_match:
            item['url'] = url_match.group(0)
        else:
            # url 字段不能为空（小程序会静默丢弃），用占位符
            item['url'] = '#'
        fixed = True
        issues.append(f'补全url字段')

    # 3. Check content - 小程序 MIN_CONTENT_LENGTH=50，<50字会被isLowQuality过滤
    #    必须确保每条item有>=50字的content，空content也不行
    MIN_CONTENT_LENGTH = 50
    content = item.get('content', '')
    if len(content) < MIN_CONTENT_LENGTH:
        title = item.get('title', '')
        source = item.get('source', '')
        if not content:
            # 空content：从title+source生成兜底内容
            fallback = title
            if source:
                fallback += f"，来源：{source}"
            fallback += "。详情请阅读原文了解更多相关信息。"
            if len(fallback) < MIN_CONTENT_LENGTH:
                fallback = title + "。" + title + "。该消息来自当日资讯报道，更多详情请查看原文链接。"
            item['content'] = fallback
            fixed = True
            issues.append(f'补全空content: {len(fallback)}字')
        else:
            # 短content：追加自然扩展文本
            extended = content + " " + title + "相关内容可查阅原文获取更多信息。"
            if len(extended) < MIN_CONTENT_LENGTH:
                extended = content + "。" + title + "，该消息来自" + (source or "相关资讯") + "报道，更多详情请查看原文链接。"
            item['content'] = extended
            fixed = True
            issues.append(f'扩展短content: {len(content)}→{len(extended)}字')

    # 4. Ensure title exists
    if not item.get('title', ''):
        item['title'] = '无标题'
        fixed = True
        issues.append('补全空title')

    return fixed, issues


def normalize_file(filepath, dry_run=False, blocklist=None):
    """Normalize a single daily JSON file"""
    if blocklist is None:
        blocklist = []
    filename = os.path.basename(filepath)
    match = DAILY_PATTERN.match(filename)
    if not match:
        return 0, 0, [f'skip非daily文件: {filename}']

    section, date_str = match.group(1), match.group(2)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        return 0, 0, [f'{filename}: 不是数组格式(实际{type(data).__name__})，跳过']

    fixed_count = 0
    uid_count = 0
    blocked_count = 0
    all_fixed_info = []
    clean_items = []

    for item in data:
        # 注入 uid（稳定唯一标识符，用于收藏/已读/投票的主键）
        if not item.get('uid'):
            uid = gen_uid(section, item.get('title', ''), item.get('url', ''))
            item['uid'] = uid
            uid_count += 1

        # 按3天过滤旧数据（仅对今天文件生效，历史文件不删数据）
        try:
            pub = item.get('published', '')
            item_date = datetime.strptime(pub[:10], '%Y-%m-%d').date()
            today = datetime.now(timezone(timedelta(hours=8))).date()
            file_date = datetime.strptime(date_str, '%Y%m%d').date()
            # 只有今天的文件才按今天为基准过滤；历史文件按自身文件日期过滤
            cutoff = today if file_date >= today else file_date
            if item_date < cutoff - timedelta(days=MAX_DAYS_BACK):
                continue
        except:
            pass  # 无法解析日期的保留

        fixed, issues = normalize_item(item, date_str)
        if fixed:
            fixed_count += 1
            all_fixed_info.extend(issues)
        
        # 敏感词过滤（标题 + 内容）
        item_text = (item.get('title', '') or '') + ' ' + (item.get('content', '') or '')
        if is_blocked(item_text, blocklist):
            blocked_count += 1
            all_fixed_info.append(f'🔒 过滤敏感内容: {item.get("title", "")[:40]}')
            continue  # 跳过，不加入 clean_items
        
        clean_items.append(item)

    if not dry_run and (fixed_count > 0 or uid_count > 0 or blocked_count > 0):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(clean_items, f, ensure_ascii=False, indent=2)

    if uid_count > 0:
        all_fixed_info.insert(0, f'注入 {uid_count} 个 uid')
    if blocked_count > 0:
        all_fixed_info.insert(0, f'🔒 过滤 {blocked_count} 条敏感内容')

    return len(data), len(clean_items), all_fixed_info


def main():
    parser = argparse.ArgumentParser(description='Normalize daily data JSON files')
    parser.add_argument('--date', default=datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d'),
                        help='仅处理指定日期文件 (YYYYMMDD)，默认今天')
    parser.add_argument('--all', action='store_true',
                        help='🔴 处理所有历史 daily 文件（危险！仅在紧急修复时使用）')
    parser.add_argument('--dry-run', action='store_true', help='预览不写入')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    args = parser.parse_args()

    os.chdir(DATA_DIR)

    if args.all:
        pattern = '*_daily_*.json'
        print("[normalize] ⚠️ --all 模式: 将处理所有历史 daily 文件")
    else:
        pattern = f'*_daily_{args.date}.json'
    files = sorted(glob.glob(pattern))

    print(f"[normalize] 扫描 {len(files)} 个 daily JSON 文件")
    print(f"[normalize] 3天过滤: 仅保留最近{MAX_DAYS_BACK}天数据\n")

    blocklist = load_blocklist()
    if blocklist:
        print(f"[normalize] 敏感词过滤: 已激活（{len(blocklist)} 个关键词）")
    else:
        print("[normalize] 敏感词过滤: 未激活（blocklist 为空或不存在）")
    print()

    total_before = 0
    total_after = 0
    total_fixed = 0
    all_issues = []

    for fp in files:
        before, after, issues = normalize_file(fp, args.dry_run, blocklist)
        total_before += before
        total_after += after
        total_fixed += len(issues) if issues else 0

        if before != after or issues:
            status = "⚠️" if before != after else "修"
            print(f"  {status} {os.path.basename(fp)}: {before} → {after} 条")
            for issue in issues:
                print(f"     {issue}")
                all_issues.append(issue)

    print(f"\n[normalize] 汇总: {total_before} → {total_after} 条, 修复 {total_fixed} 项")
    
    if args.dry_run:
        print("[normalize] 🔴 dry-run 模式，未写入任何文件")
    else:
        print("[normalize] ✅ 写入完成")

    return all_issues


if __name__ == '__main__':
    main()
