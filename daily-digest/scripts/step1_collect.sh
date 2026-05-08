#!/usr/bin/env python3
"""热点采集 Step1: 多平台数据聚合写入raw文件"""
import json, re, datetime, subprocess, sys

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {e}"

# 1. 采集CN热榜
print("采集中...")
cn_output = run_cmd("cd /root/.openclaw/workspace/skills/cn-trends-aggregator && python3 scripts/fetch_trends.py --sources baidu,toutiao,v2ex,hn,github --limit 10 --format json 2>/dev/null")
try:
    cn_data = json.loads(cn_output)
except:
    cn_data = {}

# 2. 采集抖音（JSON 模式）
douyin_output = run_cmd("cd /root/.openclaw/workspace/skills/douyin-hot && timeout 15 node scripts/douyin.js json 10 2>/dev/null")

# 3. 解析抖音数据
douyin_items = []
try:
    douyin_data = json.loads(douyin_output)
    for item in douyin_data:
        douyin_items.append({
            'rank': item.get('rank'),
            'title': item.get('title'),
            'url': item.get('link', '')
        })
except json.JSONDecodeError:
    douyin_items = []

# 4. 合并数据
combined = {
    'date': datetime.date.today().strftime('%Y-%m-%d'),
    'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
    'baidu': cn_data.get('百度热榜', []),
    'douyin': douyin_items,
    'toutiao': cn_data.get('今日头条', []),
    'v2ex': cn_data.get('V2EX', []),
    'hn': cn_data.get('Hacker News', []),
    'github': cn_data.get('GitHub 热门新项目', [])
}

# 5. 写入文件
out_path = f"/root/.openclaw/workspace/daily-digest/raw/hot-raw-{datetime.date.today().strftime('%Y-%m-%d')}.json"
with open(out_path, 'w') as f:
    json.dump(combined, f, ensure_ascii=False, indent=2)

total = sum(len(v) for v in combined.values() if isinstance(v, list))
print(f"采集完成，共 {total} 条数据")
print(f"百度: {len(combined['baidu'])} 抖音: {len(combined['douyin'])} 头条: {len(combined['toutiao'])} V2EX: {len(combined['v2ex'])} HN: {len(combined['hn'])} GitHub: {len(combined['github'])}")
print(f"文件: {out_path}")
