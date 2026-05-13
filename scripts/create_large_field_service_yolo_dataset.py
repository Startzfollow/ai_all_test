#!/usr/bin/env python3
"""Create a larger synthetic YOLO dataset for the field-service scenario.

This dataset is intended for training-pipeline validation and dev/pilot quality
experiments. It is more realistic than the tiny CI demo dataset because it adds:

- configurable dataset size
- train/val/test splits
- multiple objects per image
- negative images
- lighting/noise/occlusion variation
- per-class instance statistics

It is still synthetic. Use it to validate the learning pipeline before moving to
real customer data or public industrial datasets.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required. Install with: pip install pillow") from exc

CLASSES = ["gauge", "warning_light", "serial_plate", "corrosion_marker"]
COLORS = {
    "gauge": (240, 240, 245),
    "warning_light": (255, 80, 50),
    "serial_plate": (220, 230, 240),
    "corrosion_marker": (145, 82, 42),
}


@dataclass
class Obj:
    cls: str
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2


def clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))


def yolo_line(obj: Obj, w: int, h: int) -> str:
    cls_id = CLASSES.index(obj.cls)
    x1, y1, x2, y2 = obj.bbox
    cx = ((x1 + x2) / 2) / w
    cy = ((y1 + y2) / 2) / h
    bw = (x2 - x1) / w
    bh = (y2 - y1) / h
    return f"{cls_id} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}"


def add_noise(img: Image.Image, rng: random.Random, intensity: int = 10) -> None:
    pix = img.load()
    w, h = img.size
    # Sample sparse pixels to keep generation fast.
    for _ in range((w * h) // 75):
        x, y = rng.randrange(w), rng.randrange(h)
        r, g, b = pix[x, y]
        delta = rng.randint(-intensity, intensity)
        pix[x, y] = (clamp(r + delta, 0, 255), clamp(g + delta, 0, 255), clamp(b + delta, 0, 255))


def draw_panel_background(draw: ImageDraw.ImageDraw, w: int, h: int, rng: random.Random) -> None:
    base = rng.randint(35, 75)
    draw.rectangle([0, 0, w, h], fill=(base, base + 8, base + 12))
    # Equipment panel
    margin = rng.randint(20, 50)
    draw.rounded_rectangle([margin, margin, w - margin, h - margin], radius=18, fill=(80, 90, 96), outline=(130, 140, 145), width=2)
    # Screw heads and seams
    for x in (margin + 20, w - margin - 20):
        for y in (margin + 20, h - margin - 20):
            draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(120, 120, 120), outline=(30, 30, 30))
    for _ in range(rng.randint(2, 5)):
        y = rng.randint(margin + 30, h - margin - 30)
        draw.line([margin + 10, y, w - margin - 10, y], fill=(55, 60, 64), width=1)


def sample_box(w: int, h: int, rng: random.Random, min_size: int = 36, max_size: int = 160) -> Tuple[int, int, int, int]:
    bw = rng.randint(min_size, min(max_size, max(min_size, w // 3)))
    bh = rng.randint(min_size, min(max_size, max(min_size, h // 3)))
    x1 = rng.randint(20, max(21, w - bw - 20))
    y1 = rng.randint(20, max(21, h - bh - 20))
    return x1, y1, x1 + bw, y1 + bh


def draw_gauge(draw: ImageDraw.ImageDraw, box: Tuple[int, int, int, int], rng: random.Random) -> None:
    x1, y1, x2, y2 = box
    draw.ellipse(box, fill=COLORS["gauge"], outline=(25, 25, 25), width=3)
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    r = min(x2 - x1, y2 - y1) // 2 - 6
    for i in range(0, 181, 30):
        ang = math.radians(180 + i)
        x_a = cx + int(math.cos(ang) * (r - 5))
        y_a = cy + int(math.sin(ang) * (r - 5))
        x_b = cx + int(math.cos(ang) * r)
        y_b = cy + int(math.sin(ang) * r)
        draw.line([x_a, y_a, x_b, y_b], fill=(0, 0, 0), width=2)
    needle = math.radians(rng.randint(200, 330))
    draw.line([cx, cy, cx + int(math.cos(needle) * (r - 12)), cy + int(math.sin(needle) * (r - 12))], fill=(200, 30, 30), width=3)
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(40, 40, 40))


def draw_warning_light(draw: ImageDraw.ImageDraw, box: Tuple[int, int, int, int], rng: random.Random) -> None:
    color = rng.choice([(255, 60, 40), (255, 190, 40), (255, 95, 20)])
    draw.ellipse(box, fill=color, outline=(40, 20, 20), width=3)
    x1, y1, x2, y2 = box
    draw.ellipse([x1 + 8, y1 + 6, x1 + 24, y1 + 22], fill=(255, 230, 190))
    draw.rectangle([x1 + 6, y2 - 12, x2 - 6, y2 + 5], fill=(60, 60, 60))


def draw_serial_plate(draw: ImageDraw.ImageDraw, box: Tuple[int, int, int, int], rng: random.Random) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=4, fill=COLORS["serial_plate"], outline=(25, 25, 25), width=2)
    code = f"SN-{rng.randint(1000,9999)}-{rng.choice(['A','B','C'])}"
    draw.text((x1 + 8, y1 + 6), code, fill=(20, 35, 50))
    draw.line([x1 + 8, y1 + 26, x2 - 8, y1 + 26], fill=(40, 50, 60), width=1)
    draw.text((x1 + 8, y1 + 32), rng.choice(["FIELD UNIT", "PUMP CTRL", "CABINET"]), fill=(30, 45, 55))


def draw_corrosion_marker(draw: ImageDraw.ImageDraw, box: Tuple[int, int, int, int], rng: random.Random) -> None:
    x1, y1, x2, y2 = box
    for _ in range(rng.randint(6, 14)):
        cx = rng.randint(x1, x2)
        cy = rng.randint(y1, y2)
        rx = rng.randint(5, max(6, (x2 - x1) // 3))
        ry = rng.randint(4, max(5, (y2 - y1) // 3))
        color = rng.choice([(120, 55, 30), (150, 82, 40), (95, 45, 25), (170, 100, 50)])
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=color)
    draw.rectangle(box, outline=(90, 40, 20), width=1)


def draw_object(draw: ImageDraw.ImageDraw, obj: Obj, rng: random.Random) -> None:
    if obj.cls == "gauge":
        draw_gauge(draw, obj.bbox, rng)
    elif obj.cls == "warning_light":
        draw_warning_light(draw, obj.bbox, rng)
    elif obj.cls == "serial_plate":
        draw_serial_plate(draw, obj.bbox, rng)
    elif obj.cls == "corrosion_marker":
        draw_corrosion_marker(draw, obj.bbox, rng)


def split_name(i: int, n: int, train_ratio: float, val_ratio: float) -> str:
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    if i < train_end:
        return "train"
    if i < val_end:
        return "val"
    return "test"


def generate(args: argparse.Namespace) -> Dict[str, object]:
    out = Path(args.output)
    if out.exists() and args.overwrite:
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    rng = random.Random(args.seed)
    size = args.image_size
    stats = {"images": 0, "instances": 0, "splits": {"train": 0, "val": 0, "test": 0}, "classes": {c: 0 for c in CLASSES}, "negative_images": 0}

    for split in ["train", "val", "test"]:
        (out / "images" / split).mkdir(parents=True, exist_ok=True)
        (out / "labels" / split).mkdir(parents=True, exist_ok=True)

    for i in range(args.num_images):
        split = split_name(i, args.num_images, args.train_ratio, args.val_ratio)
        img = Image.new("RGB", (size, size), (60, 65, 70))
        draw = ImageDraw.Draw(img)
        draw_panel_background(draw, size, size, rng)

        objects: List[Obj] = []
        is_negative = rng.random() < args.negative_ratio
        if not is_negative:
            obj_count = rng.randint(1, args.max_objects)
            # Balance classes while allowing randomness.
            for j in range(obj_count):
                cls = CLASSES[(i + j + rng.randint(0, len(CLASSES) - 1)) % len(CLASSES)]
                box = sample_box(size, size, rng)
                obj = Obj(cls=cls, bbox=box)
                draw_object(draw, obj, rng)
                objects.append(obj)
                stats["classes"][cls] += 1
        else:
            stats["negative_images"] += 1

        # Random occlusion and visual variation.
        if rng.random() < args.occlusion_prob:
            x1, y1, x2, y2 = sample_box(size, size, rng, min_size=20, max_size=80)
            draw.rectangle([x1, y1, x2, y2], fill=(rng.randint(35, 80), rng.randint(35, 80), rng.randint(35, 80)))
        if args.noise:
            add_noise(img, rng, intensity=args.noise_intensity)

        fname = f"field_service_{i:06d}.png"
        img_path = out / "images" / split / fname
        label_path = out / "labels" / split / fname.replace(".png", ".txt")
        img.save(img_path)
        label_path.write_text("\n".join(yolo_line(o, size, size) for o in objects) + ("\n" if objects else ""), encoding="utf-8")
        stats["images"] += 1
        stats["instances"] += len(objects)
        stats["splits"][split] += 1

    names_yaml = "\n".join(f"  {i}: {name}" for i, name in enumerate(CLASSES))
    data_yaml = f"""path: {out.resolve()}
train: images/train
val: images/val
test: images/test
names:
{names_yaml}
"""
    (out / "data.yaml").write_text(data_yaml, encoding="utf-8")
    manifest = {
        "dataset": "field_service_yolo_large",
        "synthetic": True,
        "output": str(out),
        "image_size": size,
        "seed": args.seed,
        **stats,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    readme = f"""# Large Field Service YOLO Dataset

Synthetic device-inspection dataset for dev/pilot YOLO training experiments.

- Images: {stats['images']}
- Instances: {stats['instances']}
- Splits: {stats['splits']}
- Classes: {stats['classes']}
- Negative images: {stats['negative_images']}

This dataset validates training behavior at scale. It is not a substitute for real customer field data.
"""
    (out / "README.md").write_text(readme, encoding="utf-8")
    return manifest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="data/field_service_yolo_large")
    p.add_argument("--num-images", type=int, default=500)
    p.add_argument("--image-size", type=int, default=640)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--train-ratio", type=float, default=0.70)
    p.add_argument("--val-ratio", type=float, default=0.15)
    p.add_argument("--max-objects", type=int, default=5)
    p.add_argument("--negative-ratio", type=float, default=0.08)
    p.add_argument("--occlusion-prob", type=float, default=0.25)
    p.add_argument("--noise", action="store_true", default=True)
    p.add_argument("--noise-intensity", type=int, default=10)
    p.add_argument("--overwrite", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    manifest = generate(args)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
