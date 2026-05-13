#!/usr/bin/env python3
"""Check YOLO dataset quality before expensive training runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Install with: pip install pyyaml") from exc

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def load_data_yaml(path: Path) -> Dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def resolve_split(base: Path, value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else base / p


def parse_label_file(path: Path, num_classes: int) -> Tuple[List[int], List[str]]:
    classes: List[int] = []
    errors: List[str] = []
    if not path.exists():
        return classes, [f"missing_label:{path}"]
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 5:
            errors.append(f"bad_columns:{path}:{lineno}")
            continue
        try:
            cls = int(float(parts[0]))
            vals = [float(x) for x in parts[1:]]
        except ValueError:
            errors.append(f"bad_number:{path}:{lineno}")
            continue
        if cls < 0 or cls >= num_classes:
            errors.append(f"bad_class:{path}:{lineno}:{cls}")
        cx, cy, w, h = vals
        if not (0 <= cx <= 1 and 0 <= cy <= 1 and 0 < w <= 1 and 0 < h <= 1):
            errors.append(f"bbox_out_of_bounds:{path}:{lineno}:{vals}")
        if w * h < 0.00005:
            errors.append(f"very_small_bbox:{path}:{lineno}:{vals}")
        classes.append(cls)
    return classes, errors


def analyze(data_yaml: Path) -> Dict[str, object]:
    cfg = load_data_yaml(data_yaml)
    base = Path(cfg.get("path", data_yaml.parent)).expanduser()
    if not base.is_absolute():
        base = (data_yaml.parent / base).resolve()
    names = cfg.get("names", {})
    if isinstance(names, dict):
        class_names = [names[i] for i in sorted(names)]
    else:
        class_names = list(names)
    num_classes = len(class_names)

    report = {
        "data_yaml": str(data_yaml),
        "base": str(base),
        "num_classes": num_classes,
        "class_names": class_names,
        "splits": {},
        "class_instances": {name: 0 for name in class_names},
        "total_images": 0,
        "total_instances": 0,
        "empty_label_images": 0,
        "errors": [],
        "warnings": [],
    }

    for split in ["train", "val", "test"]:
        if split not in cfg:
            continue
        image_dir = resolve_split(base, cfg[split])
        label_dir = Path(str(image_dir).replace("/images/", "/labels/"))
        images = sorted([p for p in image_dir.rglob("*") if p.suffix.lower() in IMAGE_EXTS]) if image_dir.exists() else []
        split_instances = 0
        split_errors: List[str] = []
        empty = 0
        for img in images:
            label = label_dir / img.relative_to(image_dir).with_suffix(".txt")
            classes, errors = parse_label_file(label, num_classes)
            if not classes:
                empty += 1
            for cls in classes:
                if 0 <= cls < num_classes:
                    report["class_instances"][class_names[cls]] += 1
            split_instances += len(classes)
            split_errors.extend(errors)
        report["splits"][split] = {
            "image_dir": str(image_dir),
            "label_dir": str(label_dir),
            "images": len(images),
            "instances": split_instances,
            "empty_label_images": empty,
        }
        report["total_images"] += len(images)
        report["total_instances"] += split_instances
        report["empty_label_images"] += empty
        report["errors"].extend(split_errors)

    missing_classes = [k for k, v in report["class_instances"].items() if v == 0]
    if missing_classes:
        report["warnings"].append(f"missing_classes:{missing_classes}")
    if report["total_images"] < 100:
        report["warnings"].append("dataset_is_smoke_sized_not_quality_sized")
    if report["total_instances"] < report["num_classes"] * 50:
        report["warnings"].append("too_few_instances_for_quality_training")
    report["passed"] = len(report["errors"]) == 0 and not missing_classes
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="Path to YOLO data.yaml")
    ap.add_argument("--output", default="outputs/large_dataset_train_test/yolo_dataset_quality.json")
    args = ap.parse_args()

    report = analyze(Path(args.data))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = out.with_suffix(".md")
    md.write_text(
        "# YOLO Dataset Quality Report\n\n"
        f"- Passed: {report['passed']}\n"
        f"- Total images: {report['total_images']}\n"
        f"- Total instances: {report['total_instances']}\n"
        f"- Class instances: `{report['class_instances']}`\n"
        f"- Empty-label images: {report['empty_label_images']}\n"
        f"- Warnings: `{report['warnings']}`\n"
        f"- Errors: `{report['errors'][:20]}`\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if report["passed"] else 2)


if __name__ == "__main__":
    main()
