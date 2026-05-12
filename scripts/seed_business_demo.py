#!/usr/bin/env python3
from backend.app.business.repository import BusinessRepository
from backend.app.business.storage import ObjectStore

repo = BusinessRepository()
repo.init_schema()
project = repo.ensure_default_project()
store = ObjectStore()

manual_uri = store.put_text(
    "business-assets",
    f"{project['id']}/demo_device_manual.txt",
    "设备巡检手册：现场工程师需要识别设备照片、检索维修文档、运行 YOLO 检测并生成售后报告。",
)
repo.create_asset(project["id"], "manual", "demo_device_manual", manual_uri, {"language": "zh", "source": "seed"})
repo.create_task(project["id"], "rag_build", "Build device manual knowledge base", {"documents_dir": "examples/docs", "top_k": 4})
repo.create_task(project["id"], "yolo_benchmark", "Benchmark field image detection", {"model": "weights/yolov8n.pt", "image": "examples/images/demo.png", "runs": 10})
repo.create_task(project["id"], "llava_train", "Plan LLaVA field-image LoRA training", {"allow_long_run": False})
repo.create_task(project["id"], "report_generate", "Generate field service AI report", {})
print(f"Seeded project: {project['id']}")
