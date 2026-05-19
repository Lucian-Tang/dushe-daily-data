#!/usr/bin/env python3
"""
QA 检查脚本 — 事件触发型，不再用 cron
在以下时机被调用：
  1. 日报 subagent 完成后 → 验证报告质量
  2. 飞书文档写入后 → 检查板块完整性
  3. 小程序上传后 → 验证版本和数据
"""

import json, sys, os, re
from datetime import datetime

FAILURE_LOG = os.path.join(os.path.dirname(__file__), "..", "failures", "failure-log.json")
EXPECTED_SECTIONS = ["行业", "开发者", "AI", "社会", "创投", "设计"]

def load_rules():
    with open(FAILURE_LOG) as f:
        data = json.load(f)
    return data.get("rules_active", []), data.get("failures", [])

def check_report(content: str, report_type: str) -> list[str]:
    """检查单份日报内容"""
    issues = []
    
    # 1. 检查是否有毒舌点评
    if "🔥" not in content and "毒舌" not in content:
        issues.append(f"[{report_type}] 缺少毒舌点评")
    
    # 2. 检查条目数量
    item_count = len(re.findall(r'^###?\s+\d+\.', content, re.MULTILINE))
    if item_count < 3:
        issues.append(f"[{report_type}] 仅 {item_count} 条，低于最低 3 条")
    
    # 3. 检查是否有链接
    if "http" not in content:
        issues.append(f"[{report_type}] 缺少来源链接")
    
    return issues

def check_feishu_doc(block_count: int, sections_found: list[str]) -> list[str]:
    """检查飞书文档完整性"""
    issues = []
    
    if block_count < 100:
        issues.append(f"飞书文档仅 {block_count} blocks，可能被截断")
    
    missing = [s for s in EXPECTED_SECTIONS if s not in str(sections_found)]
    if missing:
        issues.append(f"飞书文档缺少板块: {', '.join(missing)}")
    
    return issues

def check_daily_json(filepath: str) -> list[str]:
    """Check a _daily_*.json file for content quality issues.
    Returns list of issue descriptions; empty list means OK."""
    issues = []
    if not os.path.exists(filepath):
        return [f"文件不存在: {filepath}"]
    with open(filepath, 'r', encoding='utf-8') as f:
        items = json.load(f)
    if not isinstance(items, list):
        return [f"{filepath}: 非数组格式"]
    for i, item in enumerate(items):
        title = item.get('title', f'item-{i}')[:40]
        # Quote must not be empty
        quote = (item.get('quote', '') or '').strip()
        if not quote:
            issues.append(f"[{i}] quote 为空: {title}")
        # Content must not start with "Article URL" (raw scraped text leaked)
        content = (item.get('content', '') or '').strip()
        if content.startswith('Article URL'):
            issues.append(f"[{i}] content 以 'Article URL' 开头（抓取原文泄露）: {title}")
        # Content length check
        if len(content) < 50:
            issues.append(f"[{i}] content 过短 ({len(content)}字): {title}")
    return issues

def check_deploy(version: str, changes: str) -> list[str]:
    """检查小程序发版完整性"""
    issues = []
    
    # 版本号检查：末位数字递增，如 2.1.3
    if not version or not re.match(r'^\d+\.\d+\.\d+$', version):
        issues.append(f"版本号格式异常: {version}，应为 X.Y.Z")
    
    # 关于页版本号必须一致
    if "globalData.version" in changes or "app.js" in changes:
        pass  # 这个交给人工确认
    
    # 检查是否有 git diff（确保有改动）
    if not changes.strip():
        issues.append("无代码变更却要发版？")
    
    return issues

def log_failure(failure_type: str, cause: str, symptom: str, fix: str):
    """记录失败到 failure-log.json"""
    with open(FAILURE_LOG) as f:
        data = json.load(f)
    
    data["failures"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M"),
        "type": failure_type,
        "cause": cause,
        "symptom": symptom,
        "fix": fix,
    })
    
    with open(FAILURE_LOG, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    if len(sys.argv) < 2:
        cmd = "check_report"
    else:
        cmd = sys.argv[1]
    
    if cmd == "check_report":
        content = sys.stdin.read() if not sys.stdin.isatty() else ""
        report_type = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        issues = check_report(content, report_type)
    
    elif cmd == "check_doc":
        block_count = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        sections = sys.argv[3:] if len(sys.argv) > 3 else []
        issues = check_feishu_doc(block_count, sections)
    
    elif cmd == "check_daily_json":
        filepath = sys.argv[2] if len(sys.argv) > 2 else ""
        if not filepath:
            print("用法: qa-check.py check_daily_json <filepath>")
            sys.exit(1)
        issues = check_daily_json(filepath)

    elif cmd == "check_deploy":
        version = sys.argv[2] if len(sys.argv) > 2 else ""
        files = sys.argv[3:] if len(sys.argv) > 3 else []
        issues = check_deploy(version, files)
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
    
    if issues:
        print("\n".join(issues))
        sys.exit(1)
    else:
        print("✅ QA 通过")
        sys.exit(0)

if __name__ == "__main__":
    main()
