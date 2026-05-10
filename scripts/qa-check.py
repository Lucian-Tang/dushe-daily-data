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

def check_deploy(version: str, files: list[str]) -> list[str]:
    """检查部署完整性"""
    issues = []
    
    if not version or version == "1.5":
        issues.append(f"版本号异常: {version}")
    
    if "utils/credibility.js" not in str(files) and "V2" in str(version):
        issues.append("V2.0 关键文件 credibility.js 缺失")
    
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
