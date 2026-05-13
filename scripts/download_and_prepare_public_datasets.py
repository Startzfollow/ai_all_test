#!/usr/bin/env python3
"""Download or prepare public datasets for the Field Service AI Ops platform.

This script intentionally supports both public internet datasets and local mounted
large datasets. It should not commit raw large datasets to Git. It creates small
manifests, LLaVA-compatible JSONL samples, and dataset summaries under
``data/public_eval``.

Examples
--------
Prepare local DocVQA / InfographicVQA / LLaVA roots and optionally COCO128:

    python scripts/download_and_prepare_public_datasets.py \
      --datasets coco128 docvqa infographicvqa llava_cot \
      --output data/public_eval \
      --docvqa-root /mnt/PRO6000_disk/data/DocVQA \
      --infographicvqa-root /mnt/PRO6000_disk/data/InfographicVQA \
      --llava-root /mnt/PRO6000_disk/data/LLaVA-CoT-100k \
      --max-samples 128

Prepare MVTec AD from a manually downloaded/extracted directory:

    python scripts/download_and_prepare_public_datasets.py \
      --datasets mvtec_ad \
      --mvtec-root /path/to/mvtec_anomaly_detection
"""
from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import sys
import urllib.request
import zipfile
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
TEXT_EXTS = {".md", ".txt", ".pdf", ".json", ".jsonl", ".csv", ".yaml", ".yml"}
COCO128_URL = "https://github.com/ultralytics/assets/releases/download/v0.0.0/coco128.zip"


@dataclass
class DatasetSummary:
    name: str
    status: str
    root: str
    images: int = 0
    annotation_files: int = 0
    llava_records: int = 0
    notes: list[str] | None = None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, payload: object) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict]) -> int:
    ensure_dir(path.parent)
    count = 0
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def list_files(root: Path, exts: set[str]) -> list[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in exts)


def sample_files(files: Sequence[Path], limit: int, seed: int) -> list[Path]:
    files = list(files)
    random.Random(seed).shuffle(files)
    return files[:limit]


def safe_rel(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def download_file(url: str, dest: Path, timeout: int = 60) -> None:
    ensure_dir(dest.parent)
    with urllib.request.urlopen(url, timeout=timeout) as response:  # nosec - user-controlled public dataset URL
        dest.write_bytes(response.read())


def prepare_coco128(output_root: Path, force: bool = False) -> DatasetSummary:
    target = output_root / "coco128"
    zip_path = output_root / "downloads" / "coco128.zip"
    notes: list[str] = []
    if target.exists() and not force:
        notes.append("target already exists; reuse local copy")
    else:
        ensure_dir(target.parent)
        try:
            download_file(COCO128_URL, zip_path)
            if target.exists():
                shutil.rmtree(target)
            ensure_dir(target)
            with zipfile.ZipFile(zip_path) as zf:
                zf.extractall(output_root)
            notes.append("downloaded and extracted COCO128")
        except Exception as exc:  # noqa: BLE001
            notes.append(f"download failed: {exc}")
            notes.append("manual fallback: download coco128.zip and extract it under data/public_eval")

    candidate_roots = [output_root / "coco128", target]
    images = []
    labels = []
    for root in candidate_roots:
        images.extend(list_files(root, IMAGE_EXTS))
        labels.extend(list_files(root, {".txt"}))
    summary = DatasetSummary(
        name="coco128",
        status="ready" if images else "missing_or_download_failed",
        root=str(target),
        images=len(set(images)),
        annotation_files=len(set(labels)),
        notes=notes,
    )
    write_json(target / "dataset_summary.json", asdict(summary) | {"generated_at": now_iso()})
    return summary


def create_vqa_rows(name: str, source_root: Path, images: Sequence[Path], limit: int) -> list[dict]:
    rows: list[dict] = []
    for idx, image in enumerate(images[:limit]):
        question = "What useful field-service information can be extracted from this image?"
        answer = "This sample is used for VQA pipeline validation; replace with ground-truth answers when annotations are available."
        rows.append(
            {
                "id": f"{name}_{idx:05d}",
                "dataset": name,
                "image": str(image),
                "question": question,
                "answer": answer,
                "source_relpath": safe_rel(image, source_root),
            }
        )
    return rows


def create_llava_rows(vqa_rows: Sequence[dict]) -> list[dict]:
    llava_rows = []
    for row in vqa_rows:
        llava_rows.append(
            {
                "id": row["id"],
                "image": row["image"],
                "conversations": [
                    {"from": "human", "value": f"<image>\n{row['question']}"},
                    {"from": "gpt", "value": row["answer"]},
                ],
                "metadata": {"dataset": row.get("dataset"), "source_relpath": row.get("source_relpath")},
            }
        )
    return llava_rows


def prepare_local_vqa_dataset(name: str, source_root: Path, output_root: Path, limit: int, seed: int) -> DatasetSummary:
    target = output_root / f"{name}_sample"
    notes: list[str] = []
    if not source_root.exists():
        summary = DatasetSummary(name=name, status="missing", root=str(source_root), notes=["local root does not exist"])
        write_json(target / "dataset_summary.json", asdict(summary) | {"generated_at": now_iso()})
        return summary

    images = sample_files(list_files(source_root, IMAGE_EXTS), limit, seed)
    annotation_files = list_files(source_root, {".json", ".jsonl", ".csv"})
    vqa_rows = create_vqa_rows(name, source_root, images, limit)
    llava_rows = create_llava_rows(vqa_rows)

    write_json(target / "manifest.json", {
        "name": name,
        "source_root": str(source_root),
        "target_root": str(target),
        "generated_at": now_iso(),
        "image_count": len(images),
        "annotation_file_count": len(annotation_files),
        "note": "Generated as a lightweight evaluation manifest. Replace placeholder answers with official annotations when available.",
    })
    write_jsonl(target / "vqa_eval.jsonl", vqa_rows)
    write_jsonl(target / "llava_eval.jsonl", llava_rows)

    summary = DatasetSummary(
        name=name,
        status="ready" if images else "empty",
        root=str(source_root),
        images=len(images),
        annotation_files=len(annotation_files),
        llava_records=len(llava_rows),
        notes=notes or ["local manifest prepared"],
    )
    write_json(target / "dataset_summary.json", asdict(summary) | {"generated_at": now_iso()})
    return summary


def prepare_mvtec(source_root: Path | None, output_root: Path, limit: int, seed: int) -> DatasetSummary:
    target = output_root / "mvtec_ad_sample"
    notes: list[str] = []
    if source_root is None or not source_root.exists():
        summary = DatasetSummary(
            name="mvtec_ad",
            status="missing",
            root=str(source_root) if source_root else "",
            notes=["MVTec AD requires manual download or an existing local root due dataset size/license workflow."],
        )
        write_json(target / "dataset_summary.json", asdict(summary) | {"generated_at": now_iso()})
        return summary

    images = sample_files(list_files(source_root, IMAGE_EXTS), limit, seed)
    rows = []
    for idx, image in enumerate(images):
        rel = safe_rel(image, source_root)
        parts = image.relative_to(source_root).parts if image.is_relative_to(source_root) else image.parts
        label = "anomaly" if "test" in parts and "good" not in parts else "normal"
        rows.append({"id": f"mvtec_{idx:05d}", "image": str(image), "label": label, "source_relpath": rel})
    write_json(target / "manifest.json", {
        "name": "mvtec_ad",
        "source_root": str(source_root),
        "generated_at": now_iso(),
        "sample_count": len(rows),
        "note": "MVTec AD is anomaly-detection oriented. This manifest supports scenario tests and baseline classification/anomaly pipelines.",
    })
    write_jsonl(target / "anomaly_eval.jsonl", rows)
    summary = DatasetSummary(name="mvtec_ad", status="ready" if rows else "empty", root=str(source_root), images=len(rows), notes=notes)
    write_json(target / "dataset_summary.json", asdict(summary) | {"generated_at": now_iso()})
    return summary


def prepare_llava_source(source_root: Path, output_root: Path, limit: int, seed: int) -> DatasetSummary:
    target = output_root / "llava_cot_sample"
    notes: list[str] = []
    if not source_root.exists():
        summary = DatasetSummary(name="llava_cot", status="missing", root=str(source_root), notes=["local LLaVA root does not exist"])
        write_json(target / "dataset_summary.json", asdict(summary) | {"generated_at": now_iso()})
        return summary

    candidates = list_files(source_root, {".jsonl", ".json"})
    random.Random(seed).shuffle(candidates)
    rows: list[dict] = []
    for file in candidates:
        try:
            if file.suffix == ".jsonl":
                for line in file.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if not line.strip():
                        continue
                    obj = json.loads(line)
                    rows.append(obj)
                    if len(rows) >= limit:
                        break
            else:
                obj = json.loads(file.read_text(encoding="utf-8", errors="ignore"))
                if isinstance(obj, list):
                    rows.extend(obj[: max(0, limit - len(rows))])
                elif isinstance(obj, dict):
                    for key in ("data", "train", "samples", "annotations"):
                        if isinstance(obj.get(key), list):
                            rows.extend(obj[key][: max(0, limit - len(rows))])
                            break
            if len(rows) >= limit:
                break
        except Exception as exc:  # noqa: BLE001
            notes.append(f"skip {file}: {exc}")

    normalized = []
    for idx, row in enumerate(rows[:limit]):
        image = row.get("image") or row.get("image_path") or row.get("img") or ""
        conversations = row.get("conversations")
        if not conversations:
            question = row.get("question") or row.get("instruction") or "Describe the image."
            answer = row.get("answer") or row.get("output") or row.get("response") or ""
            conversations = [{"from": "human", "value": f"<image>\n{question}"}, {"from": "gpt", "value": str(answer)}]
        normalized.append({"id": row.get("id", f"llava_{idx:05d}"), "image": image, "conversations": conversations, "metadata": {"source": "llava_cot"}})

    write_json(target / "manifest.json", {
        "name": "llava_cot",
        "source_root": str(source_root),
        "generated_at": now_iso(),
        "record_count": len(normalized),
        "candidate_files_scanned": len(candidates),
    })
    count = write_jsonl(target / "llava_train_sample.jsonl", normalized)
    summary = DatasetSummary(name="llava_cot", status="ready" if count else "empty", root=str(source_root), llava_records=count, annotation_files=len(candidates), notes=notes[:10])
    write_json(target / "dataset_summary.json", asdict(summary) | {"generated_at": now_iso()})
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Download or prepare public/local evaluation datasets.")
    parser.add_argument("--datasets", nargs="+", default=["coco128", "docvqa", "infographicvqa", "llava_cot"], choices=["coco128", "docvqa", "infographicvqa", "mvtec_ad", "llava_cot"])
    parser.add_argument("--output", default="data/public_eval")
    parser.add_argument("--docvqa-root", default="/mnt/PRO6000_disk/data/DocVQA")
    parser.add_argument("--infographicvqa-root", default="/mnt/PRO6000_disk/data/InfographicVQA")
    parser.add_argument("--mvtec-root", default="")
    parser.add_argument("--llava-root", default="/mnt/PRO6000_disk/data/LLaVA-CoT-100k")
    parser.add_argument("--max-samples", type=int, default=128)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    output = ensure_dir(Path(args.output))
    summaries: list[DatasetSummary] = []
    if "coco128" in args.datasets:
        summaries.append(prepare_coco128(output, force=args.force))
    if "docvqa" in args.datasets:
        summaries.append(prepare_local_vqa_dataset("docvqa", Path(args.docvqa_root), output, args.max_samples, args.seed))
    if "infographicvqa" in args.datasets:
        summaries.append(prepare_local_vqa_dataset("infographicvqa", Path(args.infographicvqa_root), output, args.max_samples, args.seed))
    if "mvtec_ad" in args.datasets:
        mvtec_root = Path(args.mvtec_root) if args.mvtec_root else None
        summaries.append(prepare_mvtec(mvtec_root, output, args.max_samples, args.seed))
    if "llava_cot" in args.datasets:
        summaries.append(prepare_llava_source(Path(args.llava_root), output, min(args.max_samples, 1000), args.seed))

    payload = {"generated_at": now_iso(), "output_root": str(output), "summaries": [asdict(s) for s in summaries]}
    write_json(output / "public_dataset_inventory.json", payload)

    md = ["# Public Dataset Inventory", "", f"Generated at: `{payload['generated_at']}`", "", "| Dataset | Status | Images | Annotation files | LLaVA records | Root |", "|---|---:|---:|---:|---:|---|"]
    for s in summaries:
        md.append(f"| {s.name} | {s.status} | {s.images} | {s.annotation_files} | {s.llava_records} | `{s.root}` |")
    (output / "public_dataset_inventory.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    missing = [s.name for s in summaries if s.status in {"missing", "missing_or_download_failed"}]
    if missing:
        print(f"WARNING: datasets not ready: {missing}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
