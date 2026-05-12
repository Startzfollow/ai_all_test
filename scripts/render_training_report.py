#!/usr/bin/env python3
"""Render a markdown training report from experiment config and metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render markdown experiment report")
    parser.add_argument("--experiment-dir", required=True, help="Experiment directory")
    parser.add_argument("--output", required=True, help="Markdown output path")
    args = parser.parse_args()

    exp_dir = Path(args.experiment_dir)
    metrics_path = exp_dir / "results" / "metrics.json"
    examples_path = exp_dir / "results" / "examples.jsonl"
    metrics = load_json(metrics_path)

    training = metrics.get("training", {})
    metric_values = metrics.get("metrics", {})
    hardware = metrics.get("hardware", {})

    examples = []
    if examples_path.exists():
        with examples_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    examples.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
                if len(examples) >= 5:
                    break

    md = []
    md.append("# Experiment Results\n")
    md.append(f"## {metrics.get('experiment', exp_dir.name)}\n")
    md.append(f"- Status: `{metrics.get('status', 'unknown')}`")
    md.append(f"- Date: `{metrics.get('date')}`")
    md.append(f"- GPU: `{hardware.get('gpu')}`")
    md.append(f"- CUDA: `{hardware.get('cuda')}`")
    md.append(f"- Driver: `{hardware.get('driver')}`")
    md.append("")
    md.append("### Training\n")
    for key, value in training.items():
        md.append(f"- {key}: `{value}`")
    md.append("")
    md.append("### Metrics\n")
    md.append("| Metric | Value |")
    md.append("|---|---:|")
    for key, value in metric_values.items():
        md.append(f"| {key} | {value} |")
    md.append("")
    md.append("### Example Outputs\n")
    if examples:
        for idx, item in enumerate(examples, 1):
            md.append(f"#### Example {idx}")
            md.append(f"- Image: `{item.get('image')}`")
            md.append(f"- Question: {item.get('question')}")
            md.append(f"- Prediction: {item.get('prediction')}")
            md.append(f"- Reference: {item.get('reference')}")
            md.append("")
    else:
        md.append("No examples recorded yet.\n")
    md.append("### Integrity Note\n")
    md.append("Do not fabricate metrics. Replace `null` or `TBD` values only with measured results from local experiments.\n")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
