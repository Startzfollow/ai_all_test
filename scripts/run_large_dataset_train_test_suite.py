#!/usr/bin/env python3
"""One-command large dataset train/test suite.

This orchestrates scalable field-service YOLO data generation, data quality
checks, optional YOLO training, and optional multimodal sample preparation.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


def call(cmd: List[str]) -> Dict[str, object]:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout_tail": proc.stdout[-4000:]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", choices=["smoke", "dev", "pilot"], default="dev")
    ap.add_argument("--output", default=None)
    ap.add_argument("--model", default="weights/yolov8n.pt")
    ap.add_argument("--with-yolo-train", action="store_true")
    ap.add_argument("--docvqa-root", default=None)
    ap.add_argument("--infographicvqa-root", default=None)
    ap.add_argument("--llava-root", default=None)
    args = ap.parse_args()

    sizes = {"smoke": 64, "dev": 500, "pilot": 1500}
    out = Path(args.output or f"data/field_service_yolo_{args.tier}")
    report_dir = Path("outputs/large_dataset_train_test")
    report_dir.mkdir(parents=True, exist_ok=True)

    steps = []
    steps.append(call([sys.executable, "scripts/create_large_field_service_yolo_dataset.py", "--output", str(out), "--num-images", str(sizes[args.tier]), "--overwrite"]))
    steps.append(call([sys.executable, "scripts/check_yolo_dataset_quality.py", "--data", str(out / "data.yaml"), "--output", str(report_dir / f"{args.tier}_dataset_quality.json")]))
    if args.with_yolo_train:
        steps.append(call([sys.executable, "scripts/run_large_yolo_train_eval.py", "--data", str(out / "data.yaml"), "--model", args.model, "--tier", args.tier]))
    if args.docvqa_root or args.infographicvqa_root or args.llava_root:
        cmd = [sys.executable, "scripts/prepare_large_multimodal_samples.py", "--output", f"data/public_eval_large_{args.tier}"]
        if args.docvqa_root:
            cmd += ["--docvqa-root", args.docvqa_root]
        if args.infographicvqa_root:
            cmd += ["--infographicvqa-root", args.infographicvqa_root]
        if args.llava_root:
            cmd += ["--llava-root", args.llava_root]
        steps.append(call(cmd))

    report = {"tier": args.tier, "dataset_root": str(out), "steps": steps, "passed": all(s["returncode"] == 0 for s in steps)}
    (report_dir / f"large_dataset_suite_{args.tier}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (report_dir / f"large_dataset_suite_{args.tier}.md").write_text(
        f"# Large Dataset Suite Report ({args.tier})\n\n"
        f"- Passed: {report['passed']}\n"
        f"- Dataset root: `{out}`\n"
        f"- Steps: {len(steps)}\n\n"
        + "\n".join(f"## Step {i+1}\n\n- Return code: {s['returncode']}\n- Command: `{' '.join(s['cmd'])}`\n" for i, s in enumerate(steps)),
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report["passed"] else 2)


if __name__ == "__main__":
    main()
