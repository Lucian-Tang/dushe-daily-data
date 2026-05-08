#!/usr/bin/env python3
"""记录每日token用量到文件"""
import json, datetime, glob

today = datetime.date.today().strftime('%Y-%m-%d')
log_file = f"/root/.openclaw/workspace/daily-digest/token-log.json"

# 读取现有日志
try:
    with open(log_file) as f:
        logs = json.load(f)
except:
    logs = []

# 遍历今日的session文件，计算用量
total_in = 0
total_out = 0
session_count = 0

session_files = glob.glob("/root/.openclaw/agents/main/sessions/*.jsonl")
for sf in session_files:
    try:
        with open(sf) as f:
            for line in f:
                try:
                    obj = json.loads(line.strip())
                    if obj.get('role') == 'assistant':
                        usage = obj.get('usage', {})
                        total_in += usage.get('input_tokens', 0)
                        total_out += usage.get('output_tokens', 0)
                        session_count += 1
                except:
                    pass
    except:
        pass

# 写入日志
entry = {
    "date": today,
    "input_tokens": total_in,
    "output_tokens": total_out,
    "total_tokens": total_in + total_out,
    "sessions": session_count,
    "timestamp": datetime.datetime.now().isoformat()
}

# 保留最近30天
logs = [e for e in logs if e['date'] >= (datetime.date.today() - datetime.timedelta(days=30)).isoformat()]
logs.append(entry)

with open(log_file, 'w') as f:
    json.dump(logs, f, ensure_ascii=False, indent=2)

print(f"{today} 用量: {total_in} in / {total_out} out = {total_in+total_out} total ({session_count} sessions)")