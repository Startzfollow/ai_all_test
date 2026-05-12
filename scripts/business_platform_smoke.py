#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path

# Keep smoke test isolated and dependency-light.
os.environ.setdefault("BUSINESS_DB_URL", "sqlite:///outputs/smoke/business_ops_smoke.db")
os.environ.setdefault("BUSINESS_OBJECT_STORE_ROOT", "outputs/smoke/object_store")

from fastapi.testclient import TestClient  # noqa: E402
from backend.app.main import app  # noqa: E402

client = TestClient(app)

out_dir = Path("outputs/smoke")
out_dir.mkdir(parents=True, exist_ok=True)

checks = []

def record(name: str, ok: bool, details=None):
    checks.append({"name": name, "ok": ok, "details": details or {}})

status = client.get("/api/business/status")
record("business_status", status.status_code == 200, status.json())
project = client.post("/api/business/projects", json={"name": "Smoke Field Service Workspace"}).json()
record("create_project", bool(project.get("id")), project)
asset = client.post(
    "/api/business/assets/text",
    json={
        "project_id": project["id"],
        "asset_type": "manual",
        "name": "smoke_manual",
        "content_text": "现场设备故障处理：先查询知识库，再用图片模型辅助判断。",
    },
).json()
record("create_text_asset", bool(asset.get("object_uri")), asset)
for task_type, title, params in [
    ("rag_build", "Smoke RAG build", {"documents_dir": "examples/docs", "top_k": 4, "timeout": 60}),
    ("yolo_benchmark", "Smoke YOLO benchmark", {"model": "weights/yolov8n.pt", "image": "examples/images/demo.png", "runs": 3, "timeout": 120}),
    ("llava_train", "Smoke LLaVA train plan", {"allow_long_run": False}),
    ("report_generate", "Smoke business report", {}),
]:
    created = client.post("/api/business/tasks", json={"project_id": project["id"], "task_type": task_type, "title": title, "params": params}).json()
    ran = client.post(f"/api/business/tasks/{created['id']}/run").json()
    record(f"task_{task_type}", ran.get("status") == "succeeded", ran)

evals = client.get("/api/business/evaluations", params={"project_id": project["id"]}).json()
record("evaluations_persisted", len(evals) >= 3, {"count": len(evals)})
health = client.get("/api/business/monitoring/health").json()
record("monitoring_health", "gpu" in health, health)

score = sum(1 for c in checks if c["ok"]) / len(checks)
report = {"overall_score": round(score, 3), "passed": score >= 0.75, "checks": checks}
(out_dir / "business_platform_smoke_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
md = ["# Business Platform Smoke Report", "", f"Overall score: **{score:.3f}**", ""]
for c in checks:
    md.append(f"- {'✅' if c['ok'] else '❌'} {c['name']}")
(out_dir / "business_platform_smoke_report.md").write_text("\n".join(md), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if report["passed"] else 1)
