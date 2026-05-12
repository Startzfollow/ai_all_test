"""Run a tiny offline demo of the project.

This script does not need Qdrant, LLaVA weights, YOLO weights, or an external LLM.
It proves the backend wiring works and demonstrates:
1) RAG document ingestion + retrieval
2) GUI Agent dry-run planning
3) VLM/LLaVA-compatible interface placeholder
4) YOLO endpoint health/fallback behavior

Run from repository root:
    python scripts/run_mini_demo.py
"""
from __future__ import annotations

import base64
import json
from pathlib import Path
import os

from fastapi.testclient import TestClient
import sys

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
# Keep the mini demo deterministic across repeated runs.
store_path = ROOT / "vector_db" / "local_rag_store.json"
if store_path.exists():
    store_path.unlink()

from backend.app.main import app


SAMPLE_IMAGE = ROOT / "examples" / "images" / "demo.png"


def ensure_sample_image() -> Path:
    SAMPLE_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    if not SAMPLE_IMAGE.exists():
        # 1x1 transparent PNG; enough for interface smoke testing.
        png_b64 = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
        )
        SAMPLE_IMAGE.write_bytes(base64.b64decode(png_b64))
    return SAMPLE_IMAGE


def print_block(title: str, payload) -> None:
    print(f"\n===== {title} =====")
    if isinstance(payload, (dict, list)):
        print(json.dumps(payload, ensure_ascii=False, indent=2)[:2500])
    else:
        print(str(payload)[:2500])


def main() -> None:
    client = TestClient(app)
    image_path = ensure_sample_image()

    print_block("1. API Root", client.get("/").json())
    print_block("2. Health", client.get("/api/system/health").json())

    ingest_payload = {"documents_dir": "examples/docs"}
    print_block("3. RAG Ingest", client.post("/api/rag/ingest", json=ingest_payload).json())

    rag_payload = {"question": "这个项目覆盖哪些技术栈？", "top_k": 3}
    rag_result = client.post("/api/rag/query", json=rag_payload).json()
    print_block(
        "4. RAG Query",
        {
            "answer_preview": rag_result.get("answer", "")[:800],
            "sources": [
                {
                    "score": round(s.get("score", 0), 4),
                    "source": s.get("metadata", {}).get("source"),
                    "text_preview": s.get("text", "")[:120].replace("\n", " "),
                }
                for s in rag_result.get("sources", [])
            ],
        },
    )

    agent_payload = {"task": "打开浏览器搜索 LLaVA 多模态微调", "dry_run": True}
    print_block("5. GUI Agent Dry-run Plan", client.post("/api/agent/gui/plan", json=agent_payload).json())

    vlm_payload = {"image_path": str(image_path.relative_to(ROOT)), "prompt": "请描述这张图片"}
    print_block("6. LLaVA-compatible VLM Endpoint", client.post("/api/multimodal/llava/chat", json=vlm_payload).json())

    yolo_payload = {"image_path": str(image_path.relative_to(ROOT)), "model_path": "weights/yolov8n.pt"}
    print_block("7. YOLO Endpoint", client.post("/api/vision/yolo/infer", json=yolo_payload).json())

    print("\nMini demo finished. For real YOLO inference, put a .pt/.engine file under weights/ and rerun /api/vision/yolo/infer.")


if __name__ == "__main__":
    main()
