#!/usr/bin/env python3
"""Run the V4 production-pilot acceptance suite."""
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(name: str, cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {
        "name": name,
        "passed": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
    }


def main() -> int:
    py = sys.executable
    checks = [
        run("task_lifecycle", [py, "scripts/task_lifecycle_smoke_v4.py"]),
        run("object_store", [py, "scripts/object_store_smoke_v4.py"]),
        run("db_health", [py, "scripts/db_health_check_v4.py"]),
    ]

    dataset_script = ROOT / "scripts" / "run_business_dataset_acceptance.py"
    dataset_root = ROOT / "data" / "business_field_service_demo"
    if dataset_script.exists() and dataset_root.exists():
        checks.append(
            run(
                "business_dataset_acceptance",
                [
                    py,
                    "scripts/run_business_dataset_acceptance.py",
                    "--repo-root",
                    ".",
                    "--dataset-root",
                    "data/business_field_service_demo",
                    "--with-business-smoke",
                    "--with-quality-eval",
                ],
            )
        )

    # Generate customer report last. It is allowed to pass even when some optional source reports are absent.
    checks.append(run("customer_report", [py, "scripts/generate_customer_business_report_v4.py"]))

    score = round(sum(1 for c in checks if c["passed"]) / len(checks), 4)
    report = {
        "passed": all(c["passed"] for c in checks),
        "score": score,
        "release_level": "production_pilot_candidate" if score >= 0.9 else "pilot_candidate" if score >= 0.75 else "commercial_poc",
        "checks": checks,
    }
    out = ROOT / "outputs" / "production_pilot_v4"
    out.mkdir(parents=True, exist_ok=True)
    (out / "production_pilot_v4_acceptance.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "production_pilot_v4_acceptance.md").write_text(
        "# Production Pilot V4 Acceptance\n\n"
        f"- Passed: {report['passed']}\n"
        f"- Score: {report['score']}\n"
        f"- Release level: {report['release_level']}\n\n"
        + "\n".join(f"- [{'x' if c['passed'] else ' '}] {c['name']}" for c in checks)
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
