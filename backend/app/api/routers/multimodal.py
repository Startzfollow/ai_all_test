from fastapi import APIRouter

from backend.app.schemas import LlavaChatRequest, LlavaChatResponse
from backend.app.services.llava_service import LlavaService

router = APIRouter()
_service = LlavaService()

@router.post("/llava/chat", response_model=LlavaChatResponse)
def llava_chat(req: LlavaChatRequest):
    return _service.chat(image_path=req.image_path, prompt=req.prompt, model=req.model)
