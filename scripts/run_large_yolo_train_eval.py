#!/usr/bin/env python3
"""Run large YOLO train/val experiments and save reproducible reports."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

TIER_DEFAULTS = {
    "smoke": {"epochs": 1, "imgsz": 320, "batch": 8},
    "dev": {"epochs": 30, "imgsz": 640, "batch": 16},
    "pilot": {"epochs": 80, "imgsz": 640, "batch": 16},
}


def run(cmd: List[str], log_path: Path, dry_run: bool = False) -> Dict[str, object]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if dry_run:
        log_path.write_text("DRY RUN:\n" + " ".join(cmd) + "\n", encoding="utf-8")
        return {"returncode": 0, "dry_run": True, "cmd": cmd}
    start = time.time()
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    duration = time.time() - start
    log_path.write_text(proc.stdout, encoding="utf-8")
    return {"returncode": proc.returncode, "duration_sec": duration, "cmd": cmd, "log": str(log_path)}


def read_last_results_csv(train_dir: Path) -> Dict[str, object]:
    path = train_dir / "results.csv"
    if not path.exists():
        return {"results_csv_found": False}
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    if not rows:
        return {"results_csv_found": True, "rows": 0}
    last = {k.strip(): v.strip() for k, v in rows[-1].items()}
    return {"results_csv_found": True, "last_row": last, "rows": len(rows)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="YOLO data.yaml")
    ap.add_argument("--model", default="weights/yolov8n.pt")
    ap.add_argument("--tier", choices=sorted(TIER_DEFAULTS), default="dev")
    ap.add_argument("--epochs", type=int)
    ap.add_argument("--imgsz", type=int)
    ap.add_argument("--batch", type=int)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--device", default=None)
    ap.add_argument("--project", default="outputs/large_dataset_train_test/yolo")
    ap.add_argument("--name", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    defaults = TIER_DEFAULTS[args.tier]
    epochs = args.epochs or defaults["epochs"]
    imgsz = args.imgsz or defaults["imgsz"]
    batch = args.batch or defaults["batch"]
    name = args.name or f"{Path(args.model).stem}_{args.tier}_e{epochs}"
    project = Path(args.project)
    train_dir = project / name
    report_dir = Path("outputs/large_dataset_train_test")
    report_dir.mkdir(parents=True, exist_ok=True)

    quality_log = report_dir / f"{name}_quality.log"
    quality_cmd = [sys.executable, "scripts/check_yolo_dataset_quality.py", "--data", args.data, "--output", str(report_dir / f"{name}_quality.json")]
    quality = run(quality_cmd, quality_log, dry_run=args.dry_run)

    train_cmd = [
        "yolo", "detect", "train",
        f"model={args.model}", f"data={args.data}", f"epochs={epochs}", f"imgsz={imgsz}", f"batch={batch}",
        f"workers={args.workers}", f"project={project}", f"name={name}", "exist_ok=True",
    ]
    if args.device is not None:
        train_cmd.append(f"device={args.device}")
    train = run(train_cmd, report_dir / f"{name}_train.log", dry_run=args.dry_run)

    best = train_dir / "weights" / "best.pt"
    val_cmd = [
        "yolo", "detect", "val",
        f"model={best}", f"data={args.data}", f"imgsz={imgsz}", f"workers={args.workers}",
        f"project={project}", f"name={name}_val", "exist_ok=True",
    ]
    val = run(val_cmd, report_dir / f"{name}_val.log", dry_run=args.dry_run or not best.exists())

    report = {
        "experiment": name,
        "tier": args.tier,
        "data": args.data,
        "model": args.model,
        "epochs": epochs,
        "imgsz": imgsz,
        "batch": batch,
        "quality": quality,
        "train": train,
        "val": val,
        "train_dir": str(train_dir),
        "best_weight": str(best),
        "metrics": read_last_results_csv(train_dir),
        "note": "Synthetic data validates learning pipeline. Use real/pseudo-real field data for final business accuracy claims.",
    }
    out_json = report_dir / f"{name}_report.json"
    out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    out_md = report_dir / f"{name}_report.md"
    out_md.write_text(
        f"# Large YOLO Train/Test Report: {name}\n\n"
        f"- Tier: {args.tier}\n"
        f"- Data: `{args.data}`\n"
        f"- Model: `{args.model}`\n"
        f"- Epochs: {epochs}\n"
        f"- Image size: {imgsz}\n"
        f"- Batch: {batch}\n"
        f"- Quality return code: {quality['returncode']}\n"
        f"- Train return code: {train['returncode']}\n"
        f"- Val return code: {val['returncode']}\n"
        f"- Train dir: `{train_dir}`\n"
        f"- Best weight: `{best}`\n\n"
        "## Metrics\n\n"
        f"```json\n{json.dumps(report['metrics'], indent=2, ensure_ascii=False)}\n```\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    ok = quality["returncode"] == 0 and train["returncode"] == 0 and val["returncode"] == 0
    raise SystemExit(0 if ok else 2)


if __name__ == "__main__":
    main()
