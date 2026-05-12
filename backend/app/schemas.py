from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RagIngestRequest(BaseModel):
    documents_dir: str = Field(default="examples/docs")
    collection: Optional[str] = None


class RagQueryRequest(BaseModel):
    question: str
    top_k: int = 4
    collection: Optional[str] = None


class RagSource(BaseModel):
    doc_id: str
    score: float
    text: str
    metadata: Dict[str, Any] = {}


class RagQueryResponse(BaseModel):
    answer: str
    sources: List[RagSource]


class YoloInferRequest(BaseModel):
    image_path: str
    model_path: Optional[str] = None
    confidence: float = 0.25
    image_size: int = 640


class YoloInferResponse(BaseModel):
    ok: bool
    detections: List[Dict[str, Any]] = []
    message: str = ""
    latency_ms: Optional[float] = None


class GuiPlanRequest(BaseModel):
    task: str
    screenshot_path: Optional[str] = None
    dry_run: bool = True


class GuiPlanResponse(BaseModel):
    task: str
    plan: List[Dict[str, Any]]
    dry_run: bool
    notes: str
    trace: List[Dict[str, Any]] = []


class LlavaChatRequest(BaseModel):
    image_path: str
    prompt: str
    model: Optional[str] = None


class LlavaChatResponse(BaseModel):
    ok: bool
    answer: str
    model: str
    message: str = ""
