#!/usr/bin/env python3
"""Prepare a small LLaVA-style JSONL subset from JSON/JSONL files.

The script is intentionally generic. It accepts either a file or a directory.
It keeps samples that already look like LLaVA-style records:

{
  "image": "path/to/image.jpg",
  "conversations": [
    {"from": "human", "value": "<image>\n..."},
    {"from": "gpt", "value": "..."}
  ]
}

It does not copy raw images or private datasets into the repository.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any, Iterable


def iter_json_records(path: Path) -> Iterable[dict[str, Any]]:
    if path.is_dir():
        for child in sorted(path.rglob("*")):
            if child.suffix.lower() in {".json", ".jsonl"}:
                yield from iter_json_records(child)
        return

    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
                if isinstance(obj, dict):
                    yield obj
        return

    if path.suffix.lower() == ".json":
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            for obj in data:
                if isinstance(obj, dict):
                    yield obj
        elif isinstance(data, dict):
            # Common dataset exports may wrap samples under these keys.
            for key in ("data", "train", "samples", "instances"):
                value = data.get(key)
                if isinstance(value, list):
                    for obj in value:
                        if isinstance(obj, dict):
                            yield obj
                    return
            yield data
        return


def is_llava_like(sample: dict[str, Any]) -> bool:
    conversations = sample.get("conversations")
    if not isinstance(conversations, list) or len(conversations) < 2:
        return False
    has_human = any(isinstance(x, dict) and x.get("from") in {"human", "user"} for x in conversations)
    has_assistant = any(isinstance(x, dict) and x.get("from") in {"gpt", "assistant"} for x in conversations)
    return has_human and has_assistant


def normalize_sample(sample: dict[str, Any]) -> dict[str, Any]:
    out = dict(sample)
    convs = []
    for item in sample.get("conversations", []):
        if not isinstance(item, dict):
            continue
        role = item.get("from")
        if role == "user":
            role = "human"
        if role == "assistant":
            role = "gpt"
        convs.append({"from": role, "value": str(item.get("value", ""))})
    out["conversations"] = convs
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a LLaVA-style JSONL training subset")
    parser.add_argument("--input", required=True, help="Input JSON/JSONL file or directory")
    parser.add_argument("--output", required=True, help="Output JSONL path")
    parser.add_argument("--limit", type=int, default=1000, help="Maximum number of records to write")
    parser.add_argument("--shuffle", action="store_true", help="Shuffle before taking the subset")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for shuffling")
    parser.add_argument("--summary", default=None, help="Optional summary JSON path")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    records = [normalize_sample(x) for x in iter_json_records(input_path) if is_llava_like(x)]
    total_valid = len(records)

    if args.shuffle:
        rng = random.Random(args.seed)
        rng.shuffle(records)

    selected = records[: args.limit]

    with output_path.open("w", encoding="utf-8") as f:
        for rec in selected:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    summary = {
        "input": str(input_path),
        "output": str(output_path),
        "total_valid_records": total_valid,
        "written_records": len(selected),
        "limit": args.limit,
        "shuffle": args.shuffle,
        "seed": args.seed,
    }

    summary_path = Path(args.summary) if args.summary else output_path.with_suffix(output_path.suffix + ".summary.json")
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
