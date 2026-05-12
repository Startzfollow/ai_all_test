"""Database health and schema validation helpers for Production Pilot V4."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import os
import sqlite3


REQUIRED_TABLES = ["projects", "assets", "tasks", "evaluations", "events"]


@dataclass
class DBHealthResult:
    backend: str
    connected: bool
    required_tables: List[str]
    existing_tables: List[str]
    missing_tables: List[str]
    message: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "backend": self.backend,
            "connected": self.connected,
            "required_tables": self.required_tables,
            "existing_tables": self.existing_tables,
            "missing_tables": self.missing_tables,
            "message": self.message,
        }


def check_sqlite_health(path: str | Path = "outputs/business_v4.sqlite3") -> DBHealthResult:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        existing = sorted(row[0] for row in rows)
        missing = [t for t in REQUIRED_TABLES if t not in existing]
        return DBHealthResult("sqlite", True, REQUIRED_TABLES, existing, missing, "connected")
    finally:
        conn.close()


def check_database_health() -> DBHealthResult:
    url = os.getenv("BUSINESS_DB_URL", "").strip()
    if not url or url.startswith("sqlite"):
        sqlite_path = url.removeprefix("sqlite:///") if url.startswith("sqlite:///") else "outputs/business_v4.sqlite3"
        return check_sqlite_health(sqlite_path)

    if url.startswith("postgresql"):
        try:
            try:
                import psycopg  # type: ignore
                with psycopg.connect(url, connect_timeout=5) as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public'")
                        existing = sorted(row[0] for row in cur.fetchall())
            except ImportError:
                import psycopg2  # type: ignore
                conn = psycopg2.connect(url, connect_timeout=5)
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public'")
                    existing = sorted(row[0] for row in cur.fetchall())
                finally:
                    conn.close()
            missing = [t for t in REQUIRED_TABLES if t not in existing]
            return DBHealthResult("postgresql", True, REQUIRED_TABLES, existing, missing, "connected")
        except Exception as exc:  # noqa: BLE001
            return DBHealthResult("postgresql", False, REQUIRED_TABLES, [], REQUIRED_TABLES, str(exc))

    return DBHealthResult("unknown", False, REQUIRED_TABLES, [], REQUIRED_TABLES, f"unsupported BUSINESS_DB_URL: {url}")
