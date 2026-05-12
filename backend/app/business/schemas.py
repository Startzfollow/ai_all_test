from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(default="Default Field Service Workspace")
    business_domain: str = Field(default="field_service")
    description: str = Field(
        default="多模态设备巡检与售后知识助手：面向现场工程师，整合设备图片、PDF 手册、RAG、YOLO、VLM 和训练任务。"
    )


class ProjectOut(BaseModel):
    id: str
    name: str
    business_domain: str
    description: str
    created_at: str


class AssetCreate(BaseModel):
    project_id: str
    asset_type: str = Field(description="image | pdf | manual | model | report | dataset | checkpoint")
    name: str
    content_text: Optional[str] = None
    source_uri: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AssetOut(BaseModel):
    id: str
    project_id: str
    asset_type: str
    name: str
    object_uri: str
    metadata: Dict[str, Any]
    created_at: str


class TaskCreate(BaseModel):
    project_id: str
    task_type: str = Field(description="rag_build | yolo_benchmark | llava_train | report_generate")
    title: str
    params: Dict[str, Any] = Field(default_factory=dict)


class TaskOut(BaseModel):
    id: str
    project_id: str
    task_type: str
    title: str
    status: str
    params: Dict[str, Any]
    result: Dict[str, Any]
    created_at: str
    updated_at: str


class EvaluationOut(BaseModel):
    id: str
    project_id: str
    task_id: Optional[str]
    metric_name: str
    metric_value: Optional[float]
    release_level: str
    details: Dict[str, Any]
    created_at: str


class StatusOut(BaseModel):
    business: str
    release_stage: str
    default_workspace: str
    database_url_masked: str
    object_store_root: str
    enabled_task_types: List[str]
    gpu_available: bool
    notes: List[str]
