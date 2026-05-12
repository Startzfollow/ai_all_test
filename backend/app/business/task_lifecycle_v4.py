"""Production Pilot V4 task lifecycle primitives.

This module intentionally avoids hard dependencies on the existing repository
internals so it can be used as a stable upgrade layer. It models the lifecycle
that a business AI platform needs before moving from PoC to pilot:

pending -> running -> succeeded / failed / cancelled / timeout

The implementation is lightweight but production-oriented:
- structured JSONL events
- per-task log files
- progress tracking
- retry metadata
- result URI and log URI
- cancellation and failure handling
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional
import json
import os
import traceback
import uuid


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


TERMINAL_STATUSES = {
    TaskStatus.SUCCEEDED,
    TaskStatus.FAILED,
    TaskStatus.CANCELLED,
    TaskStatus.TIMEOUT,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class TaskEvent:
    task_id: str
    event_type: str
    message: str
    timestamp: str = field(default_factory=utc_now)
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskRecord:
    task_type: str
    payload: Dict[str, Any]
    project_id: str = "default"
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    priority: int = 100
    max_retries: int = 2
    retry_count: int = 0
    created_at: str = field(default_factory=utc_now)
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    error_message: Optional[str] = None
    result_uri: Optional[str] = None
    log_uri: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskRecord":
        copied = dict(data)
        copied["status"] = TaskStatus(copied.get("status", "pending"))
        return cls(**copied)


class TaskLogWriter:
    def __init__(self, log_root: str | Path = "outputs/task_logs_v4") -> None:
        self.log_root = Path(log_root)
        self.log_root.mkdir(parents=True, exist_ok=True)

    def log_path(self, task_id: str) -> Path:
        return self.log_root / f"{task_id}.log"

    def write(self, task_id: str, message: str, payload: Optional[Dict[str, Any]] = None) -> str:
        payload = payload or {}
        line = json.dumps({"ts": utc_now(), "message": message, "payload": payload}, ensure_ascii=False)
        path = self.log_path(task_id)
        with path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        return f"local://{path.as_posix()}"

    def read(self, task_id: str) -> List[Dict[str, Any]]:
        path = self.log_path(task_id)
        if not path.exists():
            return []
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rows.append(json.loads(line))
        return rows


class JsonTaskStore:
    """Small durable task store for local smoke tests and pilot demos.

    Production deployments can replace this with PostgreSQL-backed repository
    methods while keeping the same lifecycle semantics.
    """

    def __init__(self, root: str | Path = "outputs/task_store_v4") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.tasks_file = self.root / "tasks.json"
        self.events_file = self.root / "events.jsonl"
        if not self.tasks_file.exists():
            self.tasks_file.write_text("{}", encoding="utf-8")

    def _load_all(self) -> Dict[str, Dict[str, Any]]:
        return json.loads(self.tasks_file.read_text(encoding="utf-8") or "{}")

    def _save_all(self, data: Dict[str, Dict[str, Any]]) -> None:
        tmp = self.tasks_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, self.tasks_file)

    def create(self, task: TaskRecord) -> TaskRecord:
        data = self._load_all()
        data[task.task_id] = task.to_dict()
        self._save_all(data)
        self.add_event(TaskEvent(task.task_id, "task_created", f"Created {task.task_type}"))
        return task

    def get(self, task_id: str) -> TaskRecord:
        data = self._load_all()
        if task_id not in data:
            raise KeyError(f"task not found: {task_id}")
        return TaskRecord.from_dict(data[task_id])

    def update(self, task: TaskRecord) -> TaskRecord:
        data = self._load_all()
        if task.task_id not in data:
            raise KeyError(f"task not found: {task.task_id}")
        data[task.task_id] = task.to_dict()
        self._save_all(data)
        return task

    def list(self, status: Optional[TaskStatus] = None) -> List[TaskRecord]:
        tasks = [TaskRecord.from_dict(row) for row in self._load_all().values()]
        if status is not None:
            tasks = [task for task in tasks if task.status == status]
        return sorted(tasks, key=lambda t: (t.priority, t.created_at))

    def next_pending(self) -> Optional[TaskRecord]:
        pending = self.list(TaskStatus.PENDING)
        return pending[0] if pending else None

    def add_event(self, event: TaskEvent) -> None:
        with self.events_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")

    def events(self, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.events_file.exists():
            return []
        events = []
        for line in self.events_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            if task_id is None or item.get("task_id") == task_id:
                events.append(item)
        return events


class TaskLifecycleRunner:
    def __init__(
        self,
        store: Optional[JsonTaskStore] = None,
        log_writer: Optional[TaskLogWriter] = None,
        result_root: str | Path = "outputs/task_results_v4",
    ) -> None:
        self.store = store or JsonTaskStore()
        self.logs = log_writer or TaskLogWriter()
        self.result_root = Path(result_root)
        self.result_root.mkdir(parents=True, exist_ok=True)

    def create_task(self, task_type: str, payload: Dict[str, Any], project_id: str = "default") -> TaskRecord:
        task = TaskRecord(task_type=task_type, payload=payload, project_id=project_id)
        task.log_uri = self.logs.write(task.task_id, "Task created", {"task_type": task_type})
        return self.store.create(task)

    def cancel(self, task_id: str, reason: str = "cancelled by user") -> TaskRecord:
        task = self.store.get(task_id)
        if task.status in TERMINAL_STATUSES:
            raise ValueError(f"cannot cancel terminal task: {task.status.value}")
        task.status = TaskStatus.CANCELLED
        task.finished_at = utc_now()
        task.error_message = reason
        self.logs.write(task_id, "Task cancelled", {"reason": reason})
        self.store.add_event(TaskEvent(task_id, "task_cancelled", reason))
        return self.store.update(task)

    def run_task(self, task_id: str, handlers: Dict[str, Callable[[TaskRecord, TaskLogWriter], Dict[str, Any]]]) -> TaskRecord:
        task = self.store.get(task_id)
        if task.status != TaskStatus.PENDING:
            raise ValueError(f"task must be pending, got {task.status.value}")
        handler = handlers.get(task.task_type)
        if handler is None:
            task.status = TaskStatus.FAILED
            task.finished_at = utc_now()
            task.error_message = f"no handler registered for {task.task_type}"
            self.logs.write(task.task_id, "Task failed", {"error": task.error_message})
            self.store.add_event(TaskEvent(task.task_id, "task_failed", task.error_message))
            return self.store.update(task)

        task.status = TaskStatus.RUNNING
        task.started_at = utc_now()
        task.progress = 0.05
        self.store.update(task)
        self.logs.write(task.task_id, "Task started", {"task_type": task.task_type})
        self.store.add_event(TaskEvent(task.task_id, "task_started", f"Started {task.task_type}"))

        try:
            result = handler(task, self.logs)
            result_path = self.result_root / f"{task.task_id}.json"
            result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            task.status = TaskStatus.SUCCEEDED
            task.progress = 1.0
            task.finished_at = utc_now()
            task.result_uri = f"local://{result_path.as_posix()}"
            task.error_message = None
            self.logs.write(task.task_id, "Task succeeded", {"result_uri": task.result_uri})
            self.store.add_event(TaskEvent(task.task_id, "task_succeeded", "Task completed", {"result_uri": task.result_uri}))
            return self.store.update(task)
        except Exception as exc:  # noqa: BLE001 - smoke framework should catch all task errors
            task.status = TaskStatus.FAILED
            task.finished_at = utc_now()
            task.error_message = str(exc)
            self.logs.write(task.task_id, "Task failed", {"error": str(exc), "traceback": traceback.format_exc()})
            self.store.add_event(TaskEvent(task.task_id, "task_failed", str(exc)))
            return self.store.update(task)

    def run_next(self, handlers: Dict[str, Callable[[TaskRecord, TaskLogWriter], Dict[str, Any]]]) -> Optional[TaskRecord]:
        task = self.store.next_pending()
        if task is None:
            return None
        return self.run_task(task.task_id, handlers)


def demo_handlers() -> Dict[str, Callable[[TaskRecord, TaskLogWriter], Dict[str, Any]]]:
    def rag_build(task: TaskRecord, logs: TaskLogWriter) -> Dict[str, Any]:
        logs.write(task.task_id, "Indexing field-service documents")
        docs = task.payload.get("documents", [])
        return {"module": "rag", "indexed_documents": len(docs), "status": "ready"}

    def yolo_benchmark(task: TaskRecord, logs: TaskLogWriter) -> Dict[str, Any]:
        logs.write(task.task_id, "Running YOLO benchmark placeholder")
        return {"module": "yolo", "fps": task.payload.get("fps", 119.58), "latency_ms": task.payload.get("latency_ms", 8.36)}

    def report_generate(task: TaskRecord, logs: TaskLogWriter) -> Dict[str, Any]:
        logs.write(task.task_id, "Generating customer report")
        return {"module": "report", "report_title": "Field Service AI Ops Pilot Report", "sections": 6}

    def llava_train_plan(task: TaskRecord, logs: TaskLogWriter) -> Dict[str, Any]:
        logs.write(task.task_id, "Creating LLaVA training plan")
        return {"module": "llava", "mode": "plan", "dataset": task.payload.get("dataset", "LLaVA-CoT-100k")}

    return {
        "rag_build": rag_build,
        "yolo_benchmark": yolo_benchmark,
        "report_generate": report_generate,
        "llava_train": llava_train_plan,
    }
