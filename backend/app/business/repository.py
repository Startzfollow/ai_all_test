from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional
from urllib.parse import urlparse


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def default_database_url() -> str:
    # Local demo default. For production-like use, set:
    # BUSINESS_DB_URL=postgresql://postgres:postgres@localhost:5432/ai_ops
    return os.getenv("BUSINESS_DB_URL", "sqlite:///outputs/business_ops.db")


def mask_url(url: str) -> str:
    if "@" not in url:
        return url
    scheme, rest = url.split("://", 1)
    return f"{scheme}://***:***@{rest.split('@', 1)[1]}"


class BusinessRepository:
    """Tiny repository layer.

    It supports SQLite for local smoke tests and PostgreSQL through psycopg for deployment.
    The schema intentionally uses TEXT JSON payloads to keep the first commercial PoC simple.
    """

    def __init__(self, database_url: Optional[str] = None) -> None:
        self.database_url = database_url or default_database_url()
        self.is_postgres = self.database_url.startswith("postgresql://") or self.database_url.startswith(
            "postgres://"
        )
        if not self.is_postgres:
            path = self.database_url.replace("sqlite:///", "")
            Path(path).parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self) -> Iterator[Any]:
        if self.is_postgres:
            try:
                import psycopg  # type: ignore
            except Exception as exc:  # pragma: no cover - optional dependency
                raise RuntimeError(
                    "PostgreSQL mode requires psycopg. Install with: pip install 'psycopg[binary]'"
                ) from exc
            conn = psycopg.connect(self.database_url)
        else:
            path = self.database_url.replace("sqlite:///", "")
            conn = sqlite3.connect(path)
            conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init_schema(self) -> None:
        ddl = [
            """
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                business_domain TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                name TEXT NOT NULL,
                object_uri TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                task_type TEXT NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                params_json TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS model_assets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                model_type TEXT NOT NULL,
                local_path TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS dataset_assets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                dataset_type TEXT NOT NULL,
                local_path TEXT NOT NULL,
                metadata_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS evaluations (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                task_id TEXT,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                release_level TEXT NOT NULL,
                details_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                task_id TEXT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """,
        ]
        with self.connect() as conn:
            cur = conn.cursor()
            for sql in ddl:
                cur.execute(sql)

    def _execute(self, sql: str, params: Iterable[Any] = ()) -> None:
        with self.connect() as conn:
            conn.cursor().execute(sql, tuple(params))

    def _fetchall(self, sql: str, params: Iterable[Any] = ()) -> List[Dict[str, Any]]:
        with self.connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
            return [dict(row) for row in rows]

    def create_project(self, name: str, business_domain: str, description: str) -> Dict[str, Any]:
        self.init_schema()
        item = {
            "id": new_id("proj"),
            "name": name,
            "business_domain": business_domain,
            "description": description,
            "created_at": now_iso(),
        }
        self._execute(
            "INSERT INTO projects(id, name, business_domain, description, created_at) VALUES (?, ?, ?, ?, ?)",
            item.values(),
        )
        return item

    def ensure_default_project(self) -> Dict[str, Any]:
        self.init_schema()
        projects = self.list_projects()
        if projects:
            return projects[0]
        return self.create_project(
            name="Default Field Service Workspace",
            business_domain="field_service",
            description="默认单用户工作台：用于设备巡检、售后知识库、图片问答、YOLO 检测和训练实验。",
        )

    def list_projects(self) -> List[Dict[str, Any]]:
        self.init_schema()
        return self._fetchall("SELECT * FROM projects ORDER BY created_at DESC")

    def create_asset(
        self, project_id: str, asset_type: str, name: str, object_uri: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        item = {
            "id": new_id("asset"),
            "project_id": project_id,
            "asset_type": asset_type,
            "name": name,
            "object_uri": object_uri,
            "metadata_json": json.dumps(metadata or {}, ensure_ascii=False),
            "created_at": now_iso(),
        }
        self._execute(
            """INSERT INTO assets(id, project_id, asset_type, name, object_uri, metadata_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            item.values(),
        )
        return self._asset_out(item)

    def list_assets(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if project_id:
            rows = self._fetchall("SELECT * FROM assets WHERE project_id = ? ORDER BY created_at DESC", [project_id])
        else:
            rows = self._fetchall("SELECT * FROM assets ORDER BY created_at DESC")
        return [self._asset_out(row) for row in rows]

    def create_task(self, project_id: str, task_type: str, title: str, params: Dict[str, Any]) -> Dict[str, Any]:
        ts = now_iso()
        item = {
            "id": new_id("task"),
            "project_id": project_id,
            "task_type": task_type,
            "title": title,
            "status": "pending",
            "params_json": json.dumps(params, ensure_ascii=False),
            "result_json": json.dumps({}, ensure_ascii=False),
            "created_at": ts,
            "updated_at": ts,
        }
        self._execute(
            """INSERT INTO tasks(id, project_id, task_type, title, status, params_json, result_json, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            item.values(),
        )
        return self._task_out(item)

    def list_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        if status:
            rows = self._fetchall("SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC", [status])
        else:
            rows = self._fetchall("SELECT * FROM tasks ORDER BY created_at DESC")
        return [self._task_out(row) for row in rows]

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        rows = self._fetchall("SELECT * FROM tasks WHERE id = ?", [task_id])
        return self._task_out(rows[0]) if rows else None

    def update_task(self, task_id: str, status: str, result: Optional[Dict[str, Any]] = None) -> None:
        self._execute(
            "UPDATE tasks SET status = ?, result_json = ?, updated_at = ? WHERE id = ?",
            [status, json.dumps(result or {}, ensure_ascii=False), now_iso(), task_id],
        )

    def create_evaluation(
        self,
        project_id: str,
        task_id: Optional[str],
        metric_name: str,
        metric_value: Optional[float],
        release_level: str,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:
        item = {
            "id": new_id("eval"),
            "project_id": project_id,
            "task_id": task_id,
            "metric_name": metric_name,
            "metric_value": metric_value,
            "release_level": release_level,
            "details_json": json.dumps(details, ensure_ascii=False),
            "created_at": now_iso(),
        }
        self._execute(
            """INSERT INTO evaluations(id, project_id, task_id, metric_name, metric_value, release_level, details_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            item.values(),
        )
        return self._evaluation_out(item)

    def list_evaluations(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if project_id:
            rows = self._fetchall("SELECT * FROM evaluations WHERE project_id = ? ORDER BY created_at DESC", [project_id])
        else:
            rows = self._fetchall("SELECT * FROM evaluations ORDER BY created_at DESC")
        return [self._evaluation_out(row) for row in rows]

    def log_event(
        self, level: str, message: str, payload: Optional[Dict[str, Any]] = None, project_id: Optional[str] = None, task_id: Optional[str] = None
    ) -> None:
        self._execute(
            """INSERT INTO events(id, project_id, task_id, level, message, payload_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [new_id("evt"), project_id, task_id, level, message, json.dumps(payload or {}, ensure_ascii=False), now_iso()],
        )

    def _asset_out(self, row: Dict[str, Any]) -> Dict[str, Any]:
        out = dict(row)
        out["metadata"] = json.loads(out.pop("metadata_json", "{}") or "{}")
        return out

    def _task_out(self, row: Dict[str, Any]) -> Dict[str, Any]:
        out = dict(row)
        out["params"] = json.loads(out.pop("params_json", "{}") or "{}")
        out["result"] = json.loads(out.pop("result_json", "{}") or "{}")
        return out

    def _evaluation_out(self, row: Dict[str, Any]) -> Dict[str, Any]:
        out = dict(row)
        out["details"] = json.loads(out.pop("details_json", "{}") or "{}")
        return out
