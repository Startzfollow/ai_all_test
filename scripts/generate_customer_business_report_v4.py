#!/usr/bin/env python3
"""Generate a customer-facing pilot report for the field-service AI platform."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    output_dir = ROOT / "outputs" / "reports_v4"
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset_result = load_json(ROOT / "docs" / "results" / "business_dataset_acceptance.json")
    quality_result = load_json(ROOT / "outputs" / "quality" / "product_quality_report.json")
    task_smoke = load_json(ROOT / "outputs" / "task_lifecycle_v4_smoke" / "task_lifecycle_smoke_v4.json")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "title": "Field Service Multimodal AI Ops Pilot Report",
        "business_goal": "Assist field-service engineers with maintenance knowledge retrieval, visual inspection, task execution, and pilot acceptance reporting.",
        "dataset_acceptance": dataset_result,
        "quality_evaluation": quality_result,
        "task_lifecycle": task_smoke,
        "release_recommendation": "pilot_candidate" if dataset_result.get("passed") else "needs_remediation",
    }

    md = [
        "# Field Service Multimodal AI Ops Pilot Report",
        "",
        f"Generated at: {report['generated_at']}",
        "",
        "## Business Goal",
        report["business_goal"],
        "",
        "## Acceptance Summary",
        f"- Dataset acceptance passed: {dataset_result.get('passed')}",
        f"- Dataset release level: {dataset_result.get('release_level')}",
        f"- Quality release level: {quality_result.get('release_level', quality_result.get('overall', {}).get('release_level'))}",
        f"- Task lifecycle smoke passed: {task_smoke.get('passed')}",
        "",
        "## Recommendation",
        report["release_recommendation"],
        "",
        "## Next Actions",
        "1. Run PostgreSQL + MinIO validation in a prod-lite environment.",
        "2. Add real customer documents and field images.",
        "3. Replace placeholder quality metrics with measured RAG / YOLO / VQA metrics.",
        "4. Add task detail UI and task log streaming.",
        "",
    ]

    (output_dir / "field_service_customer_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "field_service_customer_report.md").write_text("\n".join(md), encoding="utf-8")
    print(output_dir / "field_service_customer_report.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
