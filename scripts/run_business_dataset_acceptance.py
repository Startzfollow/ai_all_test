#!/usr/bin/env python3
"""Run dataset-driven acceptance checks for Business Platform V3.

This is a quality layer between smoke tests and real customer pilots. It checks
whether a dataset is structurally ready for RAG, YOLO, VQA, Agent tasks, and the
business workflow.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def run_cmd(cmd: list[str], cwd: Path, timeout: int = 120) -> dict[str, Any]:
    try:
        result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=timeout)
        return {
            "command": " ".join(cmd),
            "returncode": result.returncode,
            "stdout_tail": result.stdout[-2000:],
            "stderr_tail": result.stderr[-2000:],
            "passed": result.returncode == 0,
        }
    except Exception as exc:
        return {"command": " ".join(cmd), "passed": False, "error": str(exc)}


def check_yolo_labels(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    yolo_root = root / "yolo"
    image_paths = sorted((yolo_root / "images").glob("*/*.png"))
    label_paths = sorted((yolo_root / "labels").glob("*/*.txt"))
    missing = []
    invalid = []
    for img in image_paths:
        rel = img.relative_to(yolo_root / "images")
        label = yolo_root / "labels" / rel.with_suffix(".txt")
        if not label.exists():
            missing.append(str(label))
            continue
        for line_no, line in enumerate(label.read_text(encoding="utf-8").splitlines(), start=1):
            parts = line.split()
            if len(parts) != 5:
                invalid.append({"label": str(label), "line": line_no, "reason": "expected 5 fields"})
                continue
            try:
                cls = int(parts[0])
                vals = [float(x) for x in parts[1:]]
                if cls < 0 or cls >= len(manifest.get("class_names", [])) or any(v < 0 or v > 1 for v in vals):
                    invalid.append({"label": str(label), "line": line_no, "reason": "out_of_range"})
            except Exception:
                invalid.append({"label": str(label), "line": line_no, "reason": "parse_error"})
    passed = bool(image_paths) and len(missing) == 0 and len(invalid) == 0
    return {
        "passed": passed,
        "image_count": len(image_paths),
        "label_count": len(label_paths),
        "missing_labels": missing[:10],
        "invalid_labels": invalid[:10],
    }


def check_eval_files(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    eval_files = manifest.get("eval_files", {})
    checks = {}
    for key in ["rag_qa", "llava_vqa", "agent_tasks"]:
        path = Path(eval_files.get(key, ""))
        if not path.is_absolute():
            path = Path(path)
        if not path.exists():
            checks[key] = {"passed": False, "reason": "missing", "path": str(path)}
            continue
        rows = read_jsonl(path)
        checks[key] = {"passed": len(rows) > 0, "count": len(rows), "path": str(path)}

    # VQA image references must exist.
    vqa_path = Path(eval_files.get("llava_vqa", ""))
    vqa_missing = []
    if vqa_path.exists():
        for row in read_jsonl(vqa_path):
            img = Path(row.get("image", ""))
            if not img.exists():
                vqa_missing.append(str(img))
    checks["llava_vqa"]["missing_images"] = vqa_missing[:10]
    checks["llava_vqa"]["passed"] = checks["llava_vqa"].get("passed", False) and not vqa_missing
    return checks


def compute_score(results: dict[str, Any]) -> tuple[float, str]:
    weights = {
        "manifest": 0.15,
        "rag_docs": 0.15,
        "yolo_labels": 0.20,
        "eval_files": 0.25,
        "business_smoke": 0.15,
        "quality_eval": 0.10,
    }
    score = 0.0
    for key, weight in weights.items():
        value = results.get(key, {})
        if key == "eval_files":
            passed = all(v.get("passed") for v in value.values()) if value else False
        else:
            passed = value.get("passed", False)
        if passed:
            score += weight
    if score >= 0.90:
        level = "pilot_candidate"
    elif score >= 0.75:
        level = "commercial_poc"
    elif score >= 0.60:
        level = "technical_demo"
    else:
        level = "incomplete"
    return round(score, 3), level


def write_reports(output_dir: Path, report: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "business_dataset_acceptance.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [
        "# Business Dataset Acceptance Report",
        "",
        f"- Passed: `{report['passed']}`",
        f"- Score: `{report['score']}`",
        f"- Release level: `{report['release_level']}`",
        f"- Dataset root: `{report['dataset_root']}`",
        "",
        "## Checks",
    ]
    for key, value in report["checks"].items():
        md.append(f"### {key}")
        md.append("```json")
        md.append(json.dumps(value, ensure_ascii=False, indent=2))
        md.append("```")
    (output_dir / "business_dataset_acceptance.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--dataset-root", default="data/business_field_service_demo")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--with-business-smoke", action="store_true")
    parser.add_argument("--with-quality-eval", action="store_true")
    parser.add_argument("--output-dir", default="outputs/business_dataset_acceptance")
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve()
    dataset_root = (repo / args.dataset_root).resolve()

    if args.generate or not (dataset_root / "manifest.json").exists():
        gen = run_cmd([sys.executable, "scripts/create_field_service_demo_dataset.py", "--output", str(dataset_root), "--overwrite"], repo)
        if not gen["passed"]:
            raise SystemExit(json.dumps(gen, ensure_ascii=False, indent=2))

    manifest_path = dataset_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}

    docs = manifest.get("documents", [])
    rag_docs_passed = all(Path(d["path"]).exists() for d in docs) and len(docs) >= 2

    checks: dict[str, Any] = {
        "manifest": {"passed": bool(manifest), "path": str(manifest_path), "name": manifest.get("name")},
        "rag_docs": {"passed": rag_docs_passed, "count": len(docs)},
        "yolo_labels": check_yolo_labels(dataset_root, manifest),
        "eval_files": check_eval_files(dataset_root, manifest),
        "business_smoke": {"passed": True, "mode": "not_requested"},
        "quality_eval": {"passed": True, "mode": "not_requested"},
    }

    if args.with_business_smoke:
        checks["business_smoke"] = run_cmd([sys.executable, "scripts/business_platform_smoke.py"], repo)
    if args.with_quality_eval:
        checks["quality_eval"] = run_cmd([sys.executable, "scripts/evaluate_quality.py", "--repo-root", ".", "--top-k", "4"], repo)

    score, level = compute_score(checks)
    report = {
        "passed": score >= 0.85,
        "score": score,
        "release_level": level,
        "dataset_root": str(dataset_root),
        "checks": checks,
    }
    write_reports(repo / args.output_dir, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
