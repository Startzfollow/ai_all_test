#!/usr/bin/env python3
"""Optional downloader for public evaluation assets.

This script keeps public datasets outside Git and records a local manifest.
The default downloader uses Ultralytics COCO128 because it is small and designed
for object-detection pipeline testing/debugging.
"""

from __future__ import annotations

import argparse
import json
import shutil
import urllib.request
import zipfile
from pathlib import Path


COCO128_URL = "https://ultralytics.com/assets/coco128.zip"


def download(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=60) as response, dst.open("wb") as f:
        shutil.copyfileobj(response, f)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="coco128", choices=["coco128"])
    parser.add_argument("--output", default="data/public/coco128")
    parser.add_argument("--url", default=COCO128_URL)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    output = Path(args.output)
    zip_path = output.parent / "coco128.zip"
    if output.exists() and not args.force:
        print(json.dumps({"downloaded": False, "reason": "already_exists", "root": str(output)}, indent=2))
        return

    if output.exists():
        shutil.rmtree(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    download(args.url, zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(output.parent)

    # Ultralytics archive usually extracts to data/public/coco128.
    root = output
    manifest = {
        "dataset": args.dataset,
        "source_url": args.url,
        "root": str(root),
        "purpose": "YOLO pipeline debug and baseline testing",
        "committed_to_git": False,
    }
    manifest_path = output.parent / "coco128_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
