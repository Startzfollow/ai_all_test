#!/usr/bin/env python3
"""Sweep YOLO confidence and IoU thresholds.

This script measures latency and detection counts across threshold settings.
It does not replace mAP evaluation on a labeled validation set. Use it to find
candidate operating points before running a full accuracy evaluation.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_float_list(value: str) -> list[float]:
    return [float(item.strip()) for item in value.split(",") if item.strip()]


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Sweep YOLO conf/iou thresholds and record latency/detection counts.")
    parser.add_argument("--model", default="weights/yolov8n.pt", help="YOLO model path")
    parser.add_argument("--image", default="examples/images/demo.png", help="Input image path")
    parser.add_argument("--conf-values", default="0.15,0.25,0.35,0.50", help="Comma-separated confidence thresholds")
    parser.add_argument("--iou-values", default="0.45,0.60,0.70", help="Comma-separated IoU thresholds")
    parser.add_argument("--runs", type=int, default=10, help="Runs per threshold pair")
    parser.add_argument("--device", default=None, help="Optional device, for example cuda:0 or cpu")
    parser.add_argument("--output", default=None, help="Output JSON path")
    args = parser.parse_args()

    model_path = Path(args.model)
    image_path = Path(args.image)
    if not model_path.exists():
        raise FileNotFoundError(f"YOLO model not found: {model_path}")
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    try:
        from ultralytics import YOLO
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("ultralytics is required: pip install ultralytics") from exc

    model = YOLO(str(model_path))
    conf_values = parse_float_list(args.conf_values)
    iou_values = parse_float_list(args.iou_values)
    results: list[dict[str, Any]] = []

    # Warmup.
    model.predict(str(image_path), conf=conf_values[0], iou=iou_values[0], device=args.device, verbose=False)

    for conf in conf_values:
        for iou in iou_values:
            latencies: list[float] = []
            detection_counts: list[int] = []
            for _ in range(args.runs):
                start = time.perf_counter()
                prediction = model.predict(str(image_path), conf=conf, iou=iou, device=args.device, verbose=False)
                elapsed_ms = (time.perf_counter() - start) * 1000.0
                latencies.append(elapsed_ms)
                if prediction and getattr(prediction[0], "boxes", None) is not None:
                    detection_counts.append(len(prediction[0].boxes))
                else:
                    detection_counts.append(0)
            mean_ms = statistics.mean(latencies)
            row = {
                "conf": conf,
                "iou": iou,
                "runs": args.runs,
                "mean_ms": round(mean_ms, 4),
                "p50_ms": round(statistics.median(latencies), 4),
                "fps": round(1000.0 / mean_ms, 4) if mean_ms > 0 else None,
                "mean_detections": round(statistics.mean(detection_counts), 4),
                "min_detections": min(detection_counts),
                "max_detections": max(detection_counts),
            }
            results.append(row)
            print(row)

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": str(model_path),
        "image": str(image_path),
        "device": args.device,
        "results": results,
        "note": "This is a threshold/latency sweep, not a labeled mAP evaluation.",
    }

    output = Path(args.output) if args.output else Path("outputs/yolo_threshold_sweep.json")
    write_json(output, payload)
    print(f"Wrote sweep report: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
