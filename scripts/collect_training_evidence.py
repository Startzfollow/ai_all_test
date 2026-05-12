#!/usr/bin/env python3
"""Collect reproducibility evidence for training experiments.

This script stores small text metadata only. It does not copy model checkpoints or raw datasets.
"""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


def run_command(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        return (result.stdout or "") + (result.stderr or "")
    except FileNotFoundError:
        return f"Command not found: {' '.join(cmd)}\n"


def get_python_packages() -> dict[str, str | None]:
    packages: dict[str, str | None] = {}
    for name in ["torch", "transformers", "deepspeed", "accelerate", "peft", "bitsandbytes", "numpy"]:
        try:
            module = __import__(name)
            packages[name] = getattr(module, "__version__", "unknown")
        except Exception:
            packages[name] = None
    try:
        import torch

        packages["torch_cuda_available"] = str(torch.cuda.is_available())
        packages["torch_cuda_version"] = torch.version.cuda
        packages["torch_device_count"] = str(torch.cuda.device_count())
    except Exception:
        packages["torch_cuda_available"] = None
    return packages


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect training evidence files")
    parser.add_argument("--experiment", required=True, help="Experiment name, for example llava_lora_docvqa")
    parser.add_argument("--config", default=None, help="Config file to copy")
    parser.add_argument("--metrics", default=None, help="Metrics JSON file to copy")
    parser.add_argument("--log", default=None, help="Training log file to tail and copy")
    parser.add_argument("--output-root", default="experiments", help="Experiment root directory")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.output_root) / args.experiment / "evidence" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "hardware.txt").write_text(run_command(["nvidia-smi"]), encoding="utf-8")
    (out_dir / "git.txt").write_text(
        run_command(["git", "rev-parse", "HEAD"]) + "\n" + run_command(["git", "status", "--short"]),
        encoding="utf-8",
    )

    software = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": get_python_packages(),
    }
    (out_dir / "software.json").write_text(json.dumps(software, indent=2), encoding="utf-8")

    if args.config and Path(args.config).exists():
        shutil.copy2(args.config, out_dir / Path(args.config).name)
    if args.metrics and Path(args.metrics).exists():
        shutil.copy2(args.metrics, out_dir / Path(args.metrics).name)
    if args.log and Path(args.log).exists():
        lines = Path(args.log).read_text(encoding="utf-8", errors="ignore").splitlines()[-200:]
        (out_dir / "train_tail.log").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"evidence_dir": str(out_dir)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
