from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routers import rag, vision, agent, multimodal, system, business_ops
from backend.app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="AI Fullstack Multimodal Agent Suite",
    description="RAG + GUI Agent + LLaVA + YOLO acceleration API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
app.include_router(vision.router, prefix="/api/vision", tags=["vision"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(multimodal.router, prefix="/api/multimodal", tags=["multimodal"])
app.include_router(business_ops.router, prefix="/api/business", tags=["business-ops"])

@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "modules": [
            "RAG",
            "GUI Agent",
            "LLaVA/VLM",
            "YOLO acceleration",
            "Business Ops Platform",
        ],
        "docs": "/docs",
    }
