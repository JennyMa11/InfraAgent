"""Append operation reasons, outcomes and problems to the project journal."""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]


def record_operation(operation, reason, result, problem="无"):
    timestamp = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")
    with (ROOT / "日志.log").open("a", encoding="utf-8") as journal:
        journal.write(
            f"[{timestamp}]\n操作：{operation}\n原因：{reason}\n结果：{result}\n问题：{problem}\n\n"
        )
