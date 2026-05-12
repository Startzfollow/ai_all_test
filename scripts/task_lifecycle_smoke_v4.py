#!/usr/bin/env python3
"""Smoke test for Production Pilot V4 task lifecycle."""
from __future__ import annotations

from pathlib import Path
import json
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.business.task_lifecycle_v4 import JsonTaskStore, TaskLifecycleRunner, TaskStatus, demo_handlers  # noqa: E402


def check(condition: bool, message: str) -> dict:
    return {"name": message, "passed": bool(condition)}


def main() -> int:
    out = ROOT / "outputs" / "task_lifecycle_v4_smoke"
    if out.exists():
        shutil.rmtree(out)
    store = JsonTaskStore(out / "store")
    runner = TaskLifecycleRunner(store=store, result_root=out / "results")
    handlers = demo_handlers()

    checks = []

    rag = runner.create_task("rag_build", {"documents": ["manual.md", "faq.md"]})
    checks.append(check(rag.status == TaskStatus.PENDING, "created task is pending"))

    completed = runner.run_task(rag.task_id, handlers)
    checks.append(check(completed.status == TaskStatus.SUCCEEDED, "task succeeds"))
    checks.append(check(completed.progress == 1.0, "task reaches 100% progress"))
    checks.append(check(completed.result_uri is not None, "task has result URI"))
    checks.append(check(len(runner.logs.read(rag.task_id)) >= 3, "task logs are written"))
    checks.append(check(len(store.events(rag.task_id)) >= 3, "task events are written"))

    failing = runner.create_task("unknown_task", {})
    failed = runner.run_task(failing.task_id, handlers)
    checks.append(check(failed.status == TaskStatus.FAILED, "unknown task fails safely"))
    checks.append(check(bool(failed.error_message), "failed task has error message"))

    cancellable = runner.create_task("report_generate", {})
    cancelled = runner.cancel(cancellable.task_id, "smoke cancellation")
    checks.append(check(cancelled.status == TaskStatus.CANCELLED, "pending task can be cancelled"))

    report = {
        "passed": all(item["passed"] for item in checks),
        "score": round(sum(1 for item in checks if item["passed"]) / len(checks), 4),
        "checks": checks,
        "output_dir": str(out),
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "task_lifecycle_smoke_v4.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "task_lifecycle_smoke_v4.md").write_text(
        "# Task Lifecycle V4 Smoke\n\n"
        f"- Passed: {report['passed']}\n"
        f"- Score: {report['score']}\n\n"
        + "\n".join(f"- [{'x' if c['passed'] else ' '}] {c['name']}" for c in checks)
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
