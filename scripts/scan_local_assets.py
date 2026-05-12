#!/usr/bin/env python3
"""Scan local model and dataset directories and generate a lightweight inventory.

This script is intentionally conservative: it does not read private data content
beyond small structural metadata. It records paths, file counts, common model
artifacts, dataset-like files, and approximate sizes.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

MODEL_MARKERS = {
    "config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "generation_config.json",
    "pytorch_model.bin",
    "model.safetensors",
    "adapter_config.json",
}
MODEL_SUFFIXES = {".bin", ".safetensors", ".pt", ".pth", ".onnx", ".engine"}
DATA_SUFFIXES = {".json", ".jsonl", ".csv", ".parquet", ".arrow", ".yaml", ".yml", ".txt"}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


@dataclass
class AssetSummary:
    name: str
    path: str
    exists: bool
    kind: str
    file_count_sampled: int
    total_size_mb_sampled: float
    markers: list[str]
    notes: list[str]


def iter_files_limited(root: Path, max_files: int, max_depth: int) -> Iterable[Path]:
    if not root.exists():
        return
    root_depth = len(root.parts)
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        depth = len(current.parts) - root_depth
        if depth >= max_depth:
            dirnames[:] = []
        for filename in filenames:
            yield current / filename
            count += 1
            if count >= max_files:
                return


def summarize_dir(path: Path, kind_hint: str, max_files: int, max_depth: int) -> AssetSummary:
    markers: set[str] = set()
    notes: list[str] = []
    file_count = 0
    size_bytes = 0
    suffix_counts: dict[str, int] = {}

    if not path.exists():
        return AssetSummary(
            name=path.name,
            path=str(path),
            exists=False,
            kind="missing",
            file_count_sampled=0,
            total_size_mb_sampled=0.0,
            markers=[],
            notes=["path does not exist"],
        )

    for file_path in iter_files_limited(path, max_files=max_files, max_depth=max_depth):
        file_count += 1
        suffix = file_path.suffix.lower()
        suffix_counts[suffix] = suffix_counts.get(suffix, 0) + 1
        try:
            size_bytes += file_path.stat().st_size
        except OSError:
            pass
        if file_path.name in MODEL_MARKERS or suffix in MODEL_SUFFIXES:
            markers.add(file_path.name if file_path.name in MODEL_MARKERS else f"*{suffix}")
        if suffix in DATA_SUFFIXES:
            markers.add(f"*{suffix}")
        if suffix in IMAGE_SUFFIXES:
            markers.add("images")

    if any(m in markers for m in ["config.json", "tokenizer.json", "*.safetensors", "*.bin", "*.pt"]):
        inferred_kind = "model"
    elif "images" in markers or any(m in markers for m in ["*.json", "*.jsonl", "*.csv", "*.parquet"]):
        inferred_kind = "dataset"
    else:
        inferred_kind = kind_hint

    if file_count >= max_files:
        notes.append(f"scan truncated at {max_files} files")
    if suffix_counts:
        top_suffixes = sorted(suffix_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        notes.append("top suffixes: " + ", ".join(f"{k or '[no suffix]'}={v}" for k, v in top_suffixes))

    return AssetSummary(
        name=path.name,
        path=str(path),
        exists=True,
        kind=inferred_kind,
        file_count_sampled=file_count,
        total_size_mb_sampled=round(size_bytes / 1024 / 1024, 2),
        markers=sorted(markers),
        notes=notes,
    )


def scan_children(root: Path, kind_hint: str, max_files: int, max_depth: int) -> list[AssetSummary]:
    if not root.exists():
        return [summarize_dir(root, kind_hint, max_files, max_depth)]
    children = [p for p in root.iterdir() if not p.name.startswith(".")]
    summaries: list[AssetSummary] = []
    for child in sorted(children, key=lambda p: p.name):
        if child.is_dir():
            summaries.append(summarize_dir(child, kind_hint, max_files, max_depth))
        elif child.is_file():
            summaries.append(summarize_dir(child, kind_hint, max_files=1, max_depth=1))
    return summaries


def render_markdown(report: dict) -> str:
    lines = [
        "# Local Asset Inventory Report",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "## Models",
        "",
        "| Name | Kind | Exists | Sampled Files | Sampled Size MB | Markers |",
        "|---|---|---:|---:|---:|---|",
    ]
    for item in report["models"]:
        lines.append(
            f"| {item['name']} | {item['kind']} | {item['exists']} | "
            f"{item['file_count_sampled']} | {item['total_size_mb_sampled']} | "
            f"{', '.join(item['markers']) or '-'} |"
        )
    lines.extend([
        "",
        "## Datasets",
        "",
        "| Name | Kind | Exists | Sampled Files | Sampled Size MB | Markers |",
        "|---|---|---:|---:|---:|---|",
    ])
    for item in report["datasets"]:
        lines.append(
            f"| {item['name']} | {item['kind']} | {item['exists']} | "
            f"{item['file_count_sampled']} | {item['total_size_mb_sampled']} | "
            f"{', '.join(item['markers']) or '-'} |"
        )
    lines.extend([
        "",
        "## Notes",
        "",
        "This inventory is a structural scan only. It does not publish raw datasets or model weights.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan local model and dataset assets.")
    parser.add_argument("--models-root", default="/mnt/PRO6000_disk/models")
    parser.add_argument("--data-root", default="/mnt/PRO6000_disk/data")
    parser.add_argument("--output-dir", default="outputs/assets")
    parser.add_argument("--max-files-per-asset", type=int, default=500)
    parser.add_argument("--max-depth", type=int, default=3)
    args = parser.parse_args()

    models = scan_children(Path(args.models_root), "model_or_model_group", args.max_files_per_asset, args.max_depth)
    datasets = scan_children(Path(args.data_root), "dataset_or_data_file", args.max_files_per_asset, args.max_depth)

    report = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "models_root": args.models_root,
        "data_root": args.data_root,
        "models": [asdict(x) for x in models],
        "datasets": [asdict(x) for x in datasets],
    }

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "local_asset_inventory.json"
    md_path = output_dir / "local_asset_inventory.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"Models scanned: {len(models)}")
    print(f"Datasets scanned: {len(datasets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
