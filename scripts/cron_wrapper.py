#!/usr/bin/env python3
"""
cron_wrapper.py - Cron 任务包装器，记录结构化执行日志
用法:
  python3 scripts/cron_wrapper.py <pipeline_name> <command...>

示例:
  python3 scripts/cron_wrapper.py fetch-dev python3 scripts/fetch_dev.py
  python3 scripts/cron_wrapper.py sync-github bash scripts/sync_github_pages.sh
"""

import json, os, subprocess, sys, time
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
LOG_DIR = WORKSPACE / "logs"
RUNLOG_DIR = LOG_DIR / "runs"
LOG_DIR.mkdir(exist_ok=True)
RUNLOG_DIR.mkdir(exist_ok=True)


def main():
    if len(sys.argv) < 3:
        print("用法: cron_wrapper.py <pipeline_name> <command...>", file=sys.stderr)
        sys.exit(1)

    pipeline_name = sys.argv[1]
    cmd = sys.argv[2:]
    date_str = datetime.now().strftime("%Y%m%d")
    t_start = time.time()
    start_ts = datetime.now().isoformat()

    print(f"[{start_ts}] 🚀 {pipeline_name} 开始: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        duration = round(time.time() - t_start, 2)
        ok = result.returncode == 0
        end_ts = datetime.now().isoformat()

        # 输出 stdout/stderr
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        status = "✅" if ok else "❌"
        print(f"[{end_ts}] {status} {pipeline_name} 完成 ({duration}s)")

        # 写入结构化日志
        runlog = {
            "pipeline": pipeline_name,
            "date": date_str,
            "start_ts": start_ts,
            "end_ts": end_ts,
            "duration_s": duration,
            "command": " ".join(cmd),
            "exit_code": result.returncode,
            "status": "ok" if ok else "failed",
            "stdout_lines": len(result.stdout.splitlines()) if result.stdout else 0,
            "stderr_lines": len(result.stderr.splitlines()) if result.stderr else 0,
        }

        # 写入 runlog
        runlog_path = RUNLOG_DIR / f"{pipeline_name}-{date_str}.json"
        with open(runlog_path, "w", encoding="utf-8") as f:
            json.dump(runlog, f, ensure_ascii=False, indent=2)

        # 追加到汇总日志
        summary_log = LOG_DIR / "cron-summary.log"
        with open(summary_log, "a", encoding="utf-8") as f:
            f.write(f"[{end_ts}] {status} {pipeline_name} "
                    f"({duration}s, exit={result.returncode})\n")
            if result.stderr:
                # 只记录最后 3 行错误
                err_lines = [l for l in result.stderr.strip().splitlines() if l][-3:]
                for line in err_lines:
                    f.write(f"  ⚠ {line[:200]}\n")

        sys.exit(result.returncode)

    except subprocess.TimeoutExpired:
        duration = round(time.time() - t_start, 2)
        print(f"[{datetime.now().isoformat()}] ❌ {pipeline_name} 超时 ({duration}s)")
        sys.exit(1)
    except Exception as e:
        duration = round(time.time() - t_start, 2)
        print(f"[{datetime.now().isoformat()}] ❌ {pipeline_name} 异常: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
