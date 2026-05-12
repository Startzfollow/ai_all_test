from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from backend.app.business.repository import BusinessRepository


class BusinessTaskRunner:
    """Small synchronous runner for a DB-backed asynchronous-task design.

    API calls create tasks as pending. A worker can execute them one by one. For local smoke tests,
    /api/business/tasks/{id}/run executes one task synchronously and persists the result.
    """

    def __init__(self, repo: Optional[BusinessRepository] = None, repo_root: str = ".") -> None:
        self.repo = repo or BusinessRepository()
        self.repo_root = Path(repo_root)

    def run_task(self, task_id: str) -> Dict[str, Any]:
        task = self.repo.get_task(task_id)
        if not task:
            raise KeyError(f"Task not found: {task_id}")
        self.repo.update_task(task_id, "running", {"started": True})
        try:
            if task["task_type"] == "rag_build":
                result = self._run_rag_build(task)
            elif task["task_type"] == "yolo_benchmark":
                result = self._run_yolo_benchmark(task)
            elif task["task_type"] == "llava_train":
                result = self._run_llava_train(task)
            elif task["task_type"] == "report_generate":
                result = self._run_report_generate(task)
            else:
                result = {"ok": False, "error": f"Unsupported task_type: {task['task_type']}"}
            status = "succeeded" if result.get("ok") else "failed"
            self.repo.update_task(task_id, status, result)
            self.repo.log_event(status, f"Task {task_id} {status}", result, task.get("project_id"), task_id)
            self._write_evaluation(task, result)
            return self.repo.get_task(task_id) or task
        except Exception as exc:
            result = {"ok": False, "error": str(exc)}
            self.repo.update_task(task_id, "failed", result)
            self.repo.log_event("error", f"Task {task_id} failed", result, task.get("project_id"), task_id)
            return self.repo.get_task(task_id) or task

    def run_next(self) -> Optional[Dict[str, Any]]:
        pending = self.repo.list_tasks(status="pending")
        if not pending:
            return None
        return self.run_task(pending[-1]["id"])

    def _run_rag_build(self, task: Dict[str, Any]) -> Dict[str, Any]:
        script = self.repo_root / "scripts" / "eval_rag.py"
        if not script.exists():
            return {"ok": True, "mode": "simulated", "message": "RAG eval script not found; task recorded."}
        cmd = [sys.executable, str(script), "--documents-dir", task["params"].get("documents_dir", "examples/docs"), "--top-k", str(task["params"].get("top_k", 4))]
        proc = subprocess.run(cmd, cwd=self.repo_root, capture_output=True, text=True, timeout=int(task["params"].get("timeout", 120)))
        return {
            "ok": proc.returncode == 0,
            "command": cmd,
            "stdout_tail": proc.stdout[-4000:],
            "stderr_tail": proc.stderr[-4000:],
        }

    def _run_yolo_benchmark(self, task: Dict[str, Any]) -> Dict[str, Any]:
        script = self.repo_root / "scripts" / "benchmark_yolo.py"
        model = task["params"].get("model", os.getenv("YOLO_MODEL_PATH", "weights/yolov8n.pt"))
        image = task["params"].get("image", os.getenv("YOLO_IMAGE_PATH", "examples/images/demo.png"))
        if not script.exists():
            return {"ok": False, "error": "scripts/benchmark_yolo.py not found"}
        if not (self.repo_root / model).exists():
            return {"ok": False, "error": f"YOLO model missing: {model}"}
        if not (self.repo_root / image).exists():
            return {"ok": False, "error": f"YOLO image missing: {image}"}
        cmd = [sys.executable, str(script), "--model", model, "--image", image, "--runs", str(task["params"].get("runs", 10))]
        proc = subprocess.run(cmd, cwd=self.repo_root, capture_output=True, text=True, timeout=int(task["params"].get("timeout", 180)))
        return {
            "ok": proc.returncode == 0,
            "command": cmd,
            "stdout_tail": proc.stdout[-4000:],
            "stderr_tail": proc.stderr[-4000:],
            "business_metric": "field_image_detection_latency",
        }

    def _run_llava_train(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Long training must not be started accidentally from a web UI.
        if not task["params"].get("allow_long_run", False):
            return {
                "ok": True,
                "mode": "planned",
                "message": "LLaVA training task recorded. Set allow_long_run=true for worker execution.",
                "recommended_command": "bash experiments/llava_lora_docvqa/train.sh",
            }
        cmd = ["bash", task["params"].get("train_script", "experiments/llava_lora_docvqa/train.sh")]
        proc = subprocess.run(cmd, cwd=self.repo_root, capture_output=True, text=True, timeout=int(task["params"].get("timeout", 3600)))
        return {"ok": proc.returncode == 0, "command": cmd, "stdout_tail": proc.stdout[-4000:], "stderr_tail": proc.stderr[-4000:]}

    def _run_report_generate(self, task: Dict[str, Any]) -> Dict[str, Any]:
        output = self.repo_root / "outputs" / "business" / "field_service_summary.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        summary = {
            "ok": True,
            "project_id": task["project_id"],
            "business_value": "现场工程师可通过一个工作台完成手册知识库问答、设备图片识别、YOLO 检测评估和训练任务管理。",
            "tasks": self.repo.list_tasks(),
            "evaluations": self.repo.list_evaluations(task["project_id"]),
        }
        output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "report_path": str(output)}

    def _write_evaluation(self, task: Dict[str, Any], result: Dict[str, Any]) -> None:
        score = 1.0 if result.get("ok") else 0.0
        release_level = "commercial_poc" if score >= 1.0 else "demo"
        self.repo.create_evaluation(
            project_id=task["project_id"],
            task_id=task["id"],
            metric_name=f"task_success/{task['task_type']}",
            metric_value=score,
            release_level=release_level,
            details=result,
        )
