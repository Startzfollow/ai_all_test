from fastapi import APIRouter

from backend.app.schemas import YoloInferRequest, YoloInferResponse
from backend.app.services.yolo_service import YoloService

router = APIRouter()
_service = YoloService()

@router.post("/yolo/infer", response_model=YoloInferResponse)
def yolo_infer(req: YoloInferRequest):
    return _service.infer(
        image_path=req.image_path,
        model_path=req.model_path,
        confidence=req.confidence,
        image_size=req.image_size,
    )
