#!/usr/bin/env python3
"""Create a deterministic field-service demo dataset for product acceptance.

The generated dataset is intentionally small and synthetic. It tests the full
business workflow without leaking private data or requiring external downloads:

- RAG manuals and FAQ documents
- YOLO-style image/label pairs
- LLaVA/VQA-style evaluation samples
- GUI Agent task samples
- A manifest that can be referenced by reports and business smoke tests
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception as exc:  # pragma: no cover - runtime dependency check
    raise SystemExit(
        "Pillow is required to generate demo images. Install with: pip install pillow"
    ) from exc


@dataclass(frozen=True)
class Box:
    cls: int
    x1: int
    y1: int
    x2: int
    y2: int

    def to_yolo(self, width: int, height: int) -> str:
        cx = ((self.x1 + self.x2) / 2) / width
        cy = ((self.y1 + self.y2) / 2) / height
        bw = (self.x2 - self.x1) / width
        bh = (self.y2 - self.y1) / height
        return f"{self.cls} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}"


NAMES = ["gauge", "warning_light", "serial_plate", "corrosion_marker"]


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def generate_image(path: Path, label_path: Path, idx: int, rng: random.Random) -> dict:
    width, height = 640, 480
    img = Image.new("RGB", (width, height), (245, 247, 250))
    draw = ImageDraw.Draw(img)

    # Equipment cabinet body
    draw.rounded_rectangle((45, 45, 595, 435), radius=18, fill=(225, 230, 235), outline=(80, 90, 105), width=3)
    draw.rectangle((80, 80, 560, 130), fill=(48, 60, 75))
    draw.text((96, 96), f"FIELD UNIT A-{idx:03d}", fill=(255, 255, 255))

    boxes: list[Box] = []

    # Gauges
    for g in range(2):
        cx = 180 + g * 210 + rng.randint(-8, 8)
        cy = 230 + rng.randint(-10, 10)
        r = 55
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(250, 250, 250), outline=(20, 35, 55), width=4)
        draw.line((cx, cy, cx + rng.randint(5, 40), cy - rng.randint(10, 45)), fill=(210, 20, 30), width=4)
        draw.text((cx - 25, cy + 65), "PRESS", fill=(20, 35, 55))
        boxes.append(Box(0, cx - r, cy - r, cx + r, cy + r))

    # Warning light. Alternate normal/alert states.
    light_color = (230, 45, 45) if idx % 3 == 0 else (60, 180, 80)
    lx, ly, lr = 510, 220, 28
    draw.ellipse((lx - lr, ly - lr, lx + lr, ly + lr), fill=light_color, outline=(80, 80, 80), width=3)
    boxes.append(Box(1, lx - lr, ly - lr, lx + lr, ly + lr))

    # Serial plate
    sx1, sy1, sx2, sy2 = 115, 350, 335, 395
    draw.rectangle((sx1, sy1, sx2, sy2), fill=(255, 255, 210), outline=(70, 70, 70), width=2)
    draw.text((sx1 + 12, sy1 + 12), f"SN: FS-{2026 + idx}-{idx:04d}", fill=(20, 20, 20))
    boxes.append(Box(2, sx1, sy1, sx2, sy2))

    # Optional corrosion marker
    corrosion = idx % 4 == 0
    if corrosion:
        cx1, cy1, cx2, cy2 = 430, 338, 522, 404
        draw.ellipse((cx1, cy1, cx2, cy2), fill=(155, 82, 40), outline=(105, 55, 20), width=2)
        draw.text((cx1 + 10, cy1 + 22), "RUST", fill=(255, 240, 220))
        boxes.append(Box(3, cx1, cy1, cx2, cy2))

    path.parent.mkdir(parents=True, exist_ok=True)
    label_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    label_path.write_text("\n".join(b.to_yolo(width, height) for b in boxes) + "\n", encoding="utf-8")

    return {
        "image": str(path),
        "label": str(label_path),
        "warning_light": "red" if idx % 3 == 0 else "green",
        "has_corrosion": corrosion,
        "object_count": len(boxes),
    }


def create_docs(root: Path) -> list[dict]:
    docs_dir = root / "rag_docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    manual = docs_dir / "field_unit_a_maintenance_manual.md"
    manual.write_text(
        """# Field Unit A Maintenance Manual

## Overview
Field Unit A is an industrial inspection cabinet used by field engineers.
It contains two pressure gauges, one warning light, and a serial plate.

## Warning Light Rules
- Green light means the unit is operating normally.
- Red light means the engineer should check pressure, cooling airflow, and the error log.
- If the red light remains active after restart, create a service ticket and attach photos.

## Corrosion Handling
Visible corrosion around the lower cabinet area should be recorded as a potential environmental issue.
The recommended action is to clean the surface, check sealing, and schedule preventive maintenance.

## RAG Answering Policy
When answering service questions, cite the manual section used as evidence.
If the provided documents do not contain an answer, say that the evidence is insufficient.
""",
        encoding="utf-8",
    )

    faq = docs_dir / "after_sales_troubleshooting_faq.md"
    faq.write_text(
        """# After-sales Troubleshooting FAQ

## What should I do when the warning light is red?
Check pressure readings, cooling airflow, and the local error log. Attach at least one cabinet photo to the service record.

## What should I do when corrosion is visible?
Record the corrosion location, upload an image, and schedule preventive maintenance. Do not classify corrosion as normal operation.

## Which files should be attached to a service report?
Attach the equipment image, inspection notes, benchmark result if a vision model is used, and the final generated report.
""",
        encoding="utf-8",
    )

    return [
        {"path": str(manual), "type": "manual", "topic": "maintenance"},
        {"path": str(faq), "type": "faq", "topic": "troubleshooting"},
    ]


def create_eval_files(root: Path, images_meta: list[dict], docs: list[dict]) -> dict:
    eval_dir = root / "eval"
    eval_dir.mkdir(parents=True, exist_ok=True)

    rag_rows = [
        {
            "question": "红色告警灯亮起时现场工程师应该检查什么？",
            "expected_keywords": ["pressure", "cooling airflow", "error log"],
            "source_hint": "after_sales_troubleshooting_faq.md",
        },
        {
            "question": "发现设备下方有腐蚀痕迹时应该如何处理？",
            "expected_keywords": ["corrosion", "preventive maintenance", "record"],
            "source_hint": "field_unit_a_maintenance_manual.md",
        },
        {
            "question": "服务报告应该包含哪些附件？",
            "expected_keywords": ["equipment image", "inspection notes", "benchmark result", "final generated report"],
            "source_hint": "after_sales_troubleshooting_faq.md",
        },
    ]
    rag_path = eval_dir / "rag_qa.jsonl"
    write_jsonl(rag_path, rag_rows)

    vqa_rows = []
    for row in images_meta[:6]:
        vqa_rows.append(
            {
                "image": row["image"],
                "question": "图中告警灯是什么颜色？",
                "answer": "红色" if row["warning_light"] == "red" else "绿色",
                "answer_en": row["warning_light"],
            }
        )
        vqa_rows.append(
            {
                "image": row["image"],
                "question": "图中是否存在腐蚀标记？",
                "answer": "是" if row["has_corrosion"] else "否",
                "answer_en": "yes" if row["has_corrosion"] else "no",
            }
        )
    vqa_path = eval_dir / "llava_vqa.jsonl"
    write_jsonl(vqa_path, vqa_rows)

    agent_rows = [
        {
            "task": "上传设备图片并查询红色告警灯的处理流程",
            "expected_steps": ["open_asset_upload", "upload_image", "open_rag", "query_warning_light", "generate_report"],
            "forbidden_actions": ["delete_project", "send_payment", "email_customer_without_review"],
        },
        {
            "task": "为存在腐蚀标记的设备生成售后巡检报告",
            "expected_steps": ["select_image", "run_visual_check", "query_corrosion_policy", "create_report"],
            "forbidden_actions": ["delete_asset", "overwrite_model", "auto_approve_invoice"],
        },
    ]
    agent_path = eval_dir / "agent_tasks.jsonl"
    write_jsonl(agent_path, agent_rows)

    return {
        "rag_qa": str(rag_path),
        "llava_vqa": str(vqa_path),
        "agent_tasks": str(agent_path),
    }


def create_dataset(root: Path, num_images: int, seed: int, overwrite: bool) -> dict:
    if root.exists() and overwrite:
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)

    docs = create_docs(root)

    images_meta = []
    train_count = max(1, int(num_images * 0.7))
    for idx in range(num_images):
        split = "train" if idx < train_count else "val"
        image_path = root / "yolo" / "images" / split / f"field_unit_{idx:04d}.png"
        label_path = root / "yolo" / "labels" / split / f"field_unit_{idx:04d}.txt"
        images_meta.append(generate_image(image_path, label_path, idx, rng))

    yolo_yaml = root / "yolo" / "data.yaml"
    yolo_yaml.write_text(
        "path: .\n"
        "train: images/train\n"
        "val: images/val\n"
        f"names:\n" + "".join(f"  {i}: {name}\n" for i, name in enumerate(NAMES)),
        encoding="utf-8",
    )

    eval_files = create_eval_files(root, images_meta, docs)

    manifest = {
        "name": "field_service_demo_dataset",
        "version": "v1",
        "scenario": "equipment_inspection_and_after_sales_support",
        "root": str(root),
        "seed": seed,
        "num_images": num_images,
        "class_names": NAMES,
        "documents": docs,
        "yolo": {
            "data_yaml": str(yolo_yaml),
            "train_images": train_count,
            "val_images": num_images - train_count,
            "label_format": "YOLO normalized xywh",
        },
        "eval_files": eval_files,
        "sample_images": images_meta[:3],
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    readme = root / "README.md"
    readme.write_text(
        f"""# Field Service Demo Dataset

This synthetic dataset validates the Business Platform V3 workflow without private data.

- Scenario: equipment inspection and after-sales support
- Images: {num_images}
- YOLO classes: {', '.join(NAMES)}
- RAG docs: {len(docs)}
- RAG QA samples: 3
- VQA samples: {len(images_meta[:6]) * 2}
- Agent tasks: 2

Main entry: `manifest.json`.
""",
        encoding="utf-8",
    )

    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/business_field_service_demo")
    parser.add_argument("--num-images", type=int, default=16)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    manifest = create_dataset(Path(args.output), args.num_images, args.seed, args.overwrite)
    print(json.dumps({"created": True, "manifest": str(Path(args.output) / "manifest.json"), "summary": manifest}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
