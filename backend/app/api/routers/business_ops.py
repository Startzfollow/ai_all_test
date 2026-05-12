from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.business.monitoring import gpu_snapshot, platform_health
from backend.app.business.repository import BusinessRepository, default_database_url, mask_url
from backend.app.business.schemas import AssetCreate, ProjectCreate, StatusOut, TaskCreate
from backend.app.business.storage import ObjectStore, default_object_store_root
from backend.app.business.task_queue import BusinessTaskRunner

router = APIRouter()


def repo() -> BusinessRepository:
    instance = BusinessRepository()
    instance.init_schema()
    return instance


@router.get("/status", response_model=StatusOut)
def status() -> StatusOut:
    repository = repo()
    default_project = repository.ensure_default_project()
    gpu = gpu_snapshot()
    return StatusOut(
        business="field_service_multimodal_ops",
        release_stage="commercial_poc_candidate",
        default_workspace=default_project["id"],
        database_url_masked=mask_url(default_database_url()),
        object_store_root=str(default_object_store_root()),
        enabled_task_types=["rag_build", "yolo_benchmark", "llava_train", "report_generate"],
        gpu_available=bool(gpu.get("available")),
        notes=[
            "Default UI is single-workspace; no user system is required for this version.",
            "Use PostgreSQL by setting BUSINESS_DB_URL=postgresql://...",
            "Object storage uses local:// by default and can be replaced by S3/MinIO later.",
        ],
    )


@router.post("/projects")
def create_project(payload: ProjectCreate):
    return repo().create_project(payload.name, payload.business_domain, payload.description)


@router.get("/projects")
def list_projects():
    return repo().list_projects()


@router.post("/assets/text")
def create_text_asset(payload: AssetCreate):
    repository = repo()
    content = payload.content_text or ""
    if not content:
        raise HTTPException(status_code=400, detail="content_text is required for /assets/text")
    uri = ObjectStore().put_text("business-assets", f"{payload.project_id}/{payload.name}.txt", content)
    return repository.create_asset(payload.project_id, payload.asset_type, payload.name, uri, payload.metadata)


@router.get("/assets")
def list_assets(project_id: str | None = None):
    return repo().list_assets(project_id)


@router.post("/tasks")
def create_task(payload: TaskCreate):
    return repo().create_task(payload.project_id, payload.task_type, payload.title, payload.params)


@router.get("/tasks")
def list_tasks(status: str | None = None):
    return repo().list_tasks(status)


@router.post("/tasks/{task_id}/run")
def run_task(task_id: str):
    try:
        return BusinessTaskRunner(repo()).run_task(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/worker/run-next")
def run_next_task():
    result = BusinessTaskRunner(repo()).run_next()
    return result or {"ok": True, "message": "no pending task"}


@router.get("/evaluations")
def list_evaluations(project_id: str | None = None):
    return repo().list_evaluations(project_id)


@router.get("/monitoring/gpu")
def get_gpu_snapshot():
    return gpu_snapshot()


@router.get("/monitoring/health")
def get_platform_health():
    return platform_health()
