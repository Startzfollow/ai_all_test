from pathlib import Path

from fastapi import APIRouter

from backend.app.core.config import get_settings

router = APIRouter()


@router.get("/health")
def health():
    return {"ok": True, "service": "ai-fullstack-mm"}


@router.get("/status")
def status():
    """Operational status for the frontend dashboard."""

    s = get_settings()
    yolo_path = Path(s.vision.get("yolo_model_path", "weights/yolov8n.pt"))
    rag_cfg = s.rag
    return {
        "ok": True,
        "backend": "fastapi",
        "rag_store": rag_cfg.get("vector_backend", "local"),
        "rag_local_store": rag_cfg.get("local_store_path", "vector_db/local_rag_store.json"),
        "qdrant": "optional",
        "vlm": "mock_or_local_endpoint",
        "yolo": "ready" if yolo_path.exists() else "weights_missing",
        "yolo_model_path": str(yolo_path),
        "docs": "/docs",
    }


@router.get("/config")
def config_summary():
    s = get_settings()
    return {
        "app": s.app_name,
        "paths": s.paths,
        "rag": s.rag,
        "vision": s.vision,
        "gui_agent": s.gui_agent,
    }
