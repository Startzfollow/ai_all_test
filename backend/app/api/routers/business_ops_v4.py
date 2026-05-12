"""Optional V4 business operations router.

Wire it into backend/app/main.py when you want API-level access:

    from backend.app.api.routers import business_ops_v4
    app.include_router(business_ops_v4.router, prefix="/api/business/v4")
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.business.task_lifecycle_v4 import JsonTaskStore, TaskLifecycleRunner, demo_handlers


router = APIRouter(tags=["business-v4"])
_store = JsonTaskStore("outputs/task_store_v4_api")
_runner = TaskLifecycleRunner(_store)


class CreateTaskRequest(BaseModel):
    task_type: str
    project_id: str = "default"
    payload: dict = {}


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "module": "business_ops_v4"}


@router.post("/tasks")
def create_task(req: CreateTaskRequest) -> dict:
    task = _runner.create_task(req.task_type, req.payload, req.project_id)
    return task.to_dict()


@router.get("/tasks")
def list_tasks() -> dict:
    return {"items": [task.to_dict() for task in _store.list()]}


@router.get("/tasks/{task_id}")
def get_task(task_id: str) -> dict:
    try:
        return _store.get(task_id).to_dict()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/tasks/{task_id}/run")
def run_task(task_id: str) -> dict:
    return _runner.run_task(task_id, demo_handlers()).to_dict()


@router.post("/tasks/{task_id}/cancel")
def cancel_task(task_id: str) -> dict:
    return _runner.cancel(task_id).to_dict()


@router.get("/tasks/{task_id}/logs")
def task_logs(task_id: str) -> dict:
    return {"task_id": task_id, "logs": _runner.logs.read(task_id)}


@router.get("/tasks/{task_id}/events")
def task_events(task_id: str) -> dict:
    return {"task_id": task_id, "events": _store.events(task_id)}
