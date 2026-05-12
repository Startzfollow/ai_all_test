from fastapi import APIRouter

from backend.app.schemas import GuiPlanRequest, GuiPlanResponse
from backend.app.services.gui_agent import GuiAgent

router = APIRouter()
_service = GuiAgent()

@router.post("/gui/plan", response_model=GuiPlanResponse)
def gui_plan(req: GuiPlanRequest):
    return _service.plan(task=req.task, screenshot_path=req.screenshot_path, dry_run=req.dry_run)
