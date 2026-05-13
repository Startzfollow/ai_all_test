#!/usr/bin/env python3
"""Run the public-dataset training/test flow.

The script is intentionally safe by default: without ``--execute`` it prints the
commands and validates files. With ``--execute`` it runs supported lightweight
training/evaluation commands.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(cmd: list[str], cwd: Path, execute: bool) -> dict[str, Any]:
    record = {"cmd": cmd, "execute": execute, "returncode": None, "stdout_tail": "", "stderr_tail": ""}
    if not execute:
        record["returncode"] = 0
        return record
    proc = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, check=False)
    record["returncode"] = proc.returncode
    record["stdout_tail"] = proc.stdout[-4000:]
    record["stderr_tail"] = proc.stderr[-4000:]
    return record


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def find_coco_yaml(public_root: Path) -> Path | None:
    candidates = [
        public_root / "coco128" / "coco128.yaml",
        public_root / "coco128.yaml",
        public_root / "coco128" / "data.yaml",
    ]
    for c in candidates:
        if c.exists():
            return c
    matches = list(public_root.rglob("coco128*.yaml")) + list(public_root.rglob("data.yaml"))
    return matches[0] if matches else None


def ensure_business_dataset(repo: Path) -> Path | None:
    data_yaml = repo / "data/business_field_service_demo/yolo/data.yaml"
    return data_yaml if data_yaml.exists() else None


def yolo_train_test(repo: Path, public_root: Path, output_root: Path, execute: bool, model: str, dataset: str) -> dict[str, Any]:
    yolo_bin = shutil.which("yolo")
    if not yolo_bin:
        return {"name": "yolo_train_test", "status": "skipped", "reason": "yolo CLI not installed"}
    model_path = repo / model
    if not model_path.exists():
        return {"name": "yolo_train_test", "status": "skipped", "reason": f"model missing: {model}"}

    if dataset == "coco128":
        data_yaml = find_coco_yaml(public_root)
    elif dataset == "business":
        data_yaml = ensure_business_dataset(repo)
    else:
        data_yaml = None
    if data_yaml is None or not data_yaml.exists():
        return {"name": "yolo_train_test", "status": "skipped", "reason": f"dataset yaml missing for {dataset}"}

    project = output_root / "yolo"
    train_cmd = [
        yolo_bin, "detect", "train",
        f"model={model}",
        f"data={data_yaml}",
        "epochs=1", "imgsz=320", "batch=8", "workers=0",
        f"project={project}", "name=train_smoke", "exist_ok=True",
    ]
    val_cmd = [
        yolo_bin, "detect", "val",
        f"model={model}",
        f"data={data_yaml}",
        "imgsz=320", "batch=8", "workers=0",
        f"project={project}", "name=val_smoke", "exist_ok=True",
    ]
    return {
        "name": "yolo_train_test",
        "status": "executed" if execute else "planned",
        "dataset": dataset,
        "data_yaml": str(data_yaml),
        "model": model,
        "train": run(train_cmd, repo, execute),
        "val": run(val_cmd, repo, execute),
    }


def llava_dataset_test(repo: Path, public_root: Path, output_root: Path, execute: bool) -> dict[str, Any]:
    llava_files = [
        public_root / "llava_cot_sample/llava_train_sample.jsonl",
        public_root / "docvqa_sample/llava_eval.jsonl",
        public_root / "infographicvqa_sample/llava_eval.jsonl",
    ]
    ready = [p for p in llava_files if p.exists()]
    results = []
    for p in ready:
        cmd = [sys.executable, "scripts/validate_llava_dataset.py", "--input", str(p), "--max-errors", "20"]
        results.append({"file": str(p), "validation": run(cmd, repo, execute)})
    return {"name": "llava_dataset_test", "status": "executed" if execute else "planned", "ready_files": [str(p) for p in ready], "results": results}


def rag_public_test(repo: Path, output_root: Path, execute: bool) -> dict[str, Any]:
    # Use the existing business/deep scenario docs where available; public DocVQA documents are image-centric.
    docs_dir = repo / "data/business_field_service_demo/rag_docs"
    if not docs_dir.exists():
        docs_dir = repo / "examples/docs"
    cmd = [sys.executable, "scripts/eval_rag.py", "--documents-dir", str(docs_dir), "--top-k", "4"]
    return {"name": "rag_public_test", "status": "executed" if execute else "planned", "documents_dir": str(docs_dir), "eval": run(cmd, repo, execute)}


def mvtec_baseline_test(public_root: Path) -> dict[str, Any]:
    sample = public_root / "mvtec_ad_sample/anomaly_eval.jsonl"
    if not sample.exists():
        return {"name": "mvtec_baseline_test", "status": "skipped", "reason": "mvtec anomaly_eval.jsonl missing"}
    rows = [json.loads(line) for line in sample.read_text(encoding="utf-8").splitlines() if line.strip()]
    normal = sum(1 for r in rows if r.get("label") == "normal")
    anomaly = sum(1 for r in rows if r.get("label") == "anomaly")
    return {"name": "mvtec_baseline_test", "status": "counted", "samples": len(rows), "normal": normal, "anomaly": anomaly}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run public dataset train/test suite.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--public-root", default="data/public_eval")
    parser.add_argument("--output-root", default="outputs/public_dataset_pipeline")
    parser.add_argument("--suite", nargs="+", default=["rag", "llava", "yolo_business", "mvtec"], choices=["rag", "llava", "yolo_business", "yolo_coco128", "mvtec", "all"])
    parser.add_argument("--execute", action="store_true", help="Actually run training/test commands. Default is dry run/planning mode.")
    parser.add_argument("--model", default="weights/yolov8n.pt")
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve()
    public_root = (repo / args.public_root).resolve()
    output_root = (repo / args.output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    suites = set(args.suite)
    if "all" in suites:
        suites = {"rag", "llava", "yolo_business", "yolo_coco128", "mvtec"}

    results: list[dict[str, Any]] = []
    if "rag" in suites:
        results.append(rag_public_test(repo, output_root, args.execute))
    if "llava" in suites:
        results.append(llava_dataset_test(repo, public_root, output_root, args.execute))
    if "yolo_business" in suites:
        results.append(yolo_train_test(repo, public_root, output_root, args.execute, args.model, "business"))
    if "yolo_coco128" in suites:
        results.append(yolo_train_test(repo, public_root, output_root, args.execute, args.model, "coco128"))
    if "mvtec" in suites:
        results.append(mvtec_baseline_test(public_root))

    payload = {"generated_at": now_iso(), "execute": args.execute, "repo_root": str(repo), "public_root": str(public_root), "results": results}
    write_json(output_root / "public_train_test_report.json", payload)

    md = ["# Public Dataset Train/Test Report", "", f"Generated at: `{payload['generated_at']}`", "", f"Execute mode: `{args.execute}`", "", "| Test | Status | Notes |", "|---|---|---|"]
    for r in results:
        notes = r.get("reason") or r.get("dataset") or ""
        md.append(f"| {r.get('name')} | {r.get('status')} | {notes} |")
    (output_root / "public_train_test_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    failed = []
    for r in results:
        for key in ("train", "val", "eval"):
            if isinstance(r.get(key), dict) and r[key].get("returncode") not in (0, None):
                failed.append((r.get("name"), key, r[key].get("returncode")))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
