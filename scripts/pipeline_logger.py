#!/usr/bin/env python3
"""
pipeline_logger.py - 流水线结构化日志
所有 cron 脚本统一通过此模块记录执行过程，生成 JSON 日志供人工排查和监控消费。

用法:
  from pipeline_logger import PipelineLogger

  plog = PipelineLogger("dev-daily")
  plog.stage_start("fetch")
  try:
      articles = fetch_all()
      plog.stage_end("fetch", ok=True, meta={"count": len(articles)})
  except Exception as e:
      plog.stage_end("fetch", ok=False, error=str(e))
  plog.summary()
"""

import json, os, sys, time, traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

WORKSPACE = Path(__file__).parent.parent
LOG_DIR = WORKSPACE / "logs"
RUNLOG_DIR = LOG_DIR / "runs"
LOG_DIR.mkdir(exist_ok=True)
RUNLOG_DIR.mkdir(exist_ok=True)


class PipelineLogger:
    """流水线执行日志器"""

    def __init__(self, pipeline_name: str, date_str: Optional[str] = None):
        self.pipeline_name = pipeline_name
        self.t_start = time.time()
        self.start_ts = datetime.now().isoformat()
        self.date_str = date_str or datetime.now().strftime("%Y%m%d")
        self.stages: list[dict] = []
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def stage_start(self, stage: str) -> float:
        """记录 stage 开始，返回 start_time"""
        t = time.time()
        self.stages.append({
            "stage": stage,
            "status": "started",
            "start_ts": datetime.now().isoformat(),
            "start_t": t,
        })
        return t

    def stage_end(self, stage: str, ok: bool, meta: dict = None, error: str = None):
        """记录 stage 结束"""
        t = time.time()
        for s in self.stages:
            if s["stage"] == stage and s["status"] == "started":
                s["status"] = "ok" if ok else "failed"
                s["end_ts"] = datetime.now().isoformat()
                s["duration_s"] = round(t - s["start_t"], 2)
                if meta:
                    s["meta"] = meta
                if error:
                    s["error"] = error[:500]
                    self.errors.append(f"[{stage}] {error[:200]}")
                break
        else:
            self.warnings.append(f"stage_end called for unknown stage: {stage}")

    def warn(self, msg: str):
        self.warnings.append(msg)

    def error(self, msg: str):
        self.errors.append(msg)

    def summary(self) -> dict:
        """输出执行摘要"""
        total_duration = round(time.time() - self.t_start, 2)
        ok_stages = sum(1 for s in self.stages if s["status"] == "ok")
        total_stages = len(self.stages)
        failed = sum(1 for s in self.stages if s["status"] == "failed")

        summary_data = {
            "pipeline": self.pipeline_name,
            "date": self.date_str,
            "start_ts": self.start_ts,
            "end_ts": datetime.now().isoformat(),
            "duration_s": total_duration,
            "stages_total": total_stages,
            "stages_ok": ok_stages,
            "stages_failed": failed,
            "overall": "failed" if failed > 0 else "ok",
            "stages": self.stages,
            "errors": self.errors,
            "warnings": self.warnings,
        }

        # 写入运行时日志文件
        runlog_path = RUNLOG_DIR / f"{self.pipeline_name}-{self.date_str}.json"
        with open(runlog_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)

        # 同时追加到汇总日志
        summary_log = LOG_DIR / "pipeline-summary.log"
        icon = "✅" if failed == 0 else "❌"
        stages_str = " → ".join(
            f"{s['stage']}({'✓' if s['status']=='ok' else '✗' if s['status']=='failed' else '…'})"
            for s in self.stages
        )
        with open(summary_log, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {icon} {self.pipeline_name} "
                    f"({total_duration}s) {stages_str}\n")
            if self.errors:
                for e in self.errors:
                    f.write(f"  ❌ {e}\n")

        return summary_data

    def print_summary(self):
        """打印可读摘要到 stdout"""
        s = self.summary()
        icon = "✅" if s["overall"] == "ok" else "❌"
        print(f"\n{'='*60}")
        print(f"  {icon} {self.pipeline_name} | {self.date_str} | {s['duration_s']}s")
        print(f"{'='*60}")
        for st in s["stages"]:
            status = "✓" if st["status"] == "ok" else "✗" if st["status"] == "failed" else "…"
            dur = f" ({st.get('duration_s', '?')}s)" if "duration_s" in st else ""
            print(f"  {status} {st['stage']}{dur}")
            if st.get("meta"):
                meta_str = ", ".join(f"{k}={v}" for k, v in st["meta"].items())
                print(f"    └─ {meta_str}")
            if st.get("error"):
                print(f"    └─ ⚠ {st['error']}")
        if s["errors"]:
            print(f"\n  错误明细:")
            for e in s["errors"]:
                print(f"    ❌ {e}")
        print(f"{'='*60}\n")


# CLI 入口：可直接作为独立脚本运行测试
if __name__ == "__main__":
    plog = PipelineLogger("test-pipeline")
    plog.stage_start("fetch")
    time.sleep(0.1)
    plog.stage_end("fetch", ok=True, meta={"sources": 8, "articles": 42})
    plog.stage_start("generate")
    time.sleep(0.2)
    plog.stage_end("generate", ok=True, meta={"tokens": 1200})
    plog.stage_start("push")
    plog.stage_end("push", ok=False, error="Connection timeout to feishu API")
    plog.print_summary()
    print(f"日志已写入: {RUNLOG_DIR}/test-pipeline-{datetime.now().strftime('%Y%m%d')}.json")
