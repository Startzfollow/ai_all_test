from fastapi import APIRouter

from backend.app.schemas import RagIngestRequest, RagQueryRequest, RagQueryResponse
from backend.app.services.rag_service import RagService

router = APIRouter()
_service = RagService()

@router.post("/ingest")
def ingest(req: RagIngestRequest):
    result = _service.ingest_dir(req.documents_dir, collection=req.collection)
    return result

@router.post("/query", response_model=RagQueryResponse)
def query(req: RagQueryRequest):
    return _service.query(req.question, top_k=req.top_k, collection=req.collection)
