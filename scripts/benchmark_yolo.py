#!/usr/bin/env python3
"""Run a real local YOLO benchmark and write a JSON report.

This script does not invent acceleration numbers. If the model, image, or
runtime dependency is missing, it exits with a clear message. Use its output in
`docs/demo_yolo_benchmark.md` after running on the target machine.
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def run_command(command: List[str]) -> str:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"unavailable: {exc}"


def collect_hardware() -> Dict[str, Any]:
    hardware: Dict[str, Any] = {
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "processor": platform.processor(),
        "nvidia_smi": run_command(
            [
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total,temperature.gpu,utilization.gpu",
                "--format=csv,noheader",
            ]
        ),
    }
    try:
        import torch

        hardware["torch"] = torch.__version__
        hardware["cuda_available"] = bool(torch.cuda.is_available())
        hardware["cuda_version"] = getattr(torch.version, "cuda", None)
        if torch.cuda.is_available():
            hardware["cuda_device"] = torch.cuda.get_device_name(0)
    except Exception as exc:
        hardware["torch"] = f"unavailable: {exc}"
        hardware["cuda_available"] = False
    return hardware


def benchmark(args: argparse.Namespace) -> Dict[str, Any]:
    model_path = Path(args.model)
    image_path = Path(args.image)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report: Dict[str, Any] = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "model": str(model_path),
        "image": str(image_path),
        "imgsz": args.imgsz,
        "conf": args.conf,
        "warmup": args.warmup,
        "runs": args.runs,
        "device": args.device,
        "hardware": collect_hardware(),
        "ok": False,
        "latencies_ms": [],
    }

    if not model_path.exists():
        report["error"] = f"model not found: {model_path}"
        return report
    if not image_path.exists():
        report["error"] = f"image not found: {image_path}"
        return report

    try:
        from ultralytics import YOLO
    except Exception as exc:
        report["error"] = f"ultralytics import failed: {exc}"
        return report

    detector = YOLO(str(model_path))

    # Warmup.
    for _ in range(args.warmup):
        detector.predict(
            source=str(image_path),
            imgsz=args.imgsz,
            conf=args.conf,
            device=args.device,
            verbose=False,
        )

    latencies: List[float] = []
    detection_count = 0
    for _ in range(args.runs):
        start = time.perf_counter()
        results = detector.predict(
            source=str(image_path),
            imgsz=args.imgsz,
            conf=args.conf,
            device=args.device,
            verbose=False,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)
        detection_count = sum(len(result.boxes) for result in results)

    avg_latency = sum(latencies) / len(latencies)
    sorted_latencies = sorted(latencies)
    p50 = sorted_latencies[int(0.50 * (len(sorted_latencies) - 1))]
    p90 = sorted_latencies[int(0.90 * (len(sorted_latencies) - 1))]
    p95 = sorted_latencies[int(0.95 * (len(sorted_latencies) - 1))]

    report.update(
        {
            "ok": True,
            "backend": model_path.suffix.lower().lstrip(".") or "unknown",
            "avg_latency_ms": round(avg_latency, 3),
            "p50_latency_ms": round(p50, 3),
            "p90_latency_ms": round(p90, 3),
            "p95_latency_ms": round(p95, 3),
            "fps": round(1000.0 / avg_latency, 3) if avg_latency > 0 else None,
            "detections": int(detection_count),
            "latencies_ms": [round(item, 3) for item in latencies],
        }
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="weights/yolov8n.pt")
    parser.add_argument("--image", default="examples/images/demo.png")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--device", default="0")
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    report = benchmark(args)
    output_path = Path(args.output_dir) / f"yolo_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"\nBenchmark report saved to: {output_path}")
    if not report.get("ok"):
        sys.exit(1)


if __name__ == "__main__":
    main()
