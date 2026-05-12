#!/usr/bin/env python3
"""
check-freshness.py — 日报数据新鲜度检查
检查所有板块的 daily JSON 文件是否有今日数据。
作为管线准出检查，在 sync_github_pages.sh 中调用。

用法：
  python3 scripts/check-freshness.py           # 完整检查（硬失败）
  python3 scripts/check-freshness.py --warn    # 仅警告，不退出
  python3 scripts/check-freshness.py --summary # 汇总模式，JSON输出
"""

import json, glob, os, sys
from datetime import datetime, timezone, timedelta

TZ = timezone(timedelta(hours=8))
TODAY = datetime.now(TZ).strftime('%Y-%m-%d')

SECTIONS = [
    ('行业', 'industry_daily'),
    ('开发者', 'dev_daily'),
    ('AI', 'ai_daily'),
    ('创投', 'startup_daily'),
    ('设计', 'design_daily'),
]

def check_all(root_dir: str) -> list[dict]:
    """检查所有板块，返回结果列表"""
    results = []
    for label, prefix in SECTIONS:
        latest = None
        for f in sorted(glob.glob(os.path.join(root_dir, f'{prefix}_*.json')), reverse=True):
            latest = f; break

        if not latest:
            results.append({
                'section': label,
                'total': 0,
                'today': 0,
                'ok': False,
                'reason': '无数据文件',
                'latest_date': None
            })
            continue

        with open(latest) as fh:
            items = json.load(fh)

        today_items = [it for it in items if str(it.get('published', '')).startswith(TODAY)]
        latest_date = items[0].get('published', '?') if items else '?'

        results.append({
            'section': label,
            'total': len(items),
            'today': len(today_items),
            'ok': len(today_items) > 0,
            'latest_date': latest_date,
        })
    return results


def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mode = 'fail'
    if '--warn' in sys.argv: mode = 'warn'
    if '--summary' in sys.argv: mode = 'summary'

    results = check_all(root_dir)
    all_ok = all(r['ok'] for r in results)

    if mode == 'summary':
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    print(f'📅 数据新鲜度检查 | 日期: {TODAY}')
    print('-' * 50)
    for r in results:
        icon = '✅' if r['ok'] else '❌'
        detail = f'{r["total"]}条，{r["today"]}条今日'
        if not r['ok']:
            detail += f' (最新: {r["latest_date"]})'
        print(f'  {icon} {r["section"]}: {detail}')

    print('-' * 50)
    if all_ok:
        print('✅ 全部通过！')
    else:
        stale = [r['section'] for r in results if not r['ok']]
        msg = f'⚠️  {len(stale)} 个板块无今日数据: {", ".join(stale)}'
        if mode == 'fail':
            print(f'❌ {msg}')
            sys.exit(1)
        else:
            print(f'{msg}')


if __name__ == '__main__':
    main()
