#!/usr/bin/env python3
"""Validate a LLaVA-style JSON/JSONL dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_records(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        records: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON at line {line_no}: {exc}") from exc
                if isinstance(obj, dict):
                    records.append(obj)
        return records

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def validate_record(record: dict[str, Any], idx: int) -> list[str]:
    errors: list[str] = []
    conversations = record.get("conversations")
    if not isinstance(conversations, list) or len(conversations) < 2:
        errors.append(f"record {idx}: conversations must be a list with at least 2 turns")
        return errors

    roles = []
    for turn_idx, turn in enumerate(conversations):
        if not isinstance(turn, dict):
            errors.append(f"record {idx} turn {turn_idx}: turn must be an object")
            continue
        role = turn.get("from")
        value = turn.get("value")
        roles.append(role)
        if role not in {"human", "gpt", "user", "assistant"}:
            errors.append(f"record {idx} turn {turn_idx}: unsupported role {role!r}")
        if not isinstance(value, str) or not value.strip():
            errors.append(f"record {idx} turn {turn_idx}: value must be a non-empty string")

    if not any(role in {"human", "user"} for role in roles):
        errors.append(f"record {idx}: missing human/user turn")
    if not any(role in {"gpt", "assistant"} for role in roles):
        errors.append(f"record {idx}: missing gpt/assistant turn")

    if "image" in record and record["image"] is not None and not isinstance(record["image"], str):
        errors.append(f"record {idx}: image must be a string if provided")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate LLaVA-style dataset schema")
    parser.add_argument("--input", required=True, help="Input JSON or JSONL dataset")
    parser.add_argument("--max-errors", type=int, default=50, help="Maximum errors to print")
    parser.add_argument("--summary", default=None, help="Optional summary JSON path")
    args = parser.parse_args()

    path = Path(args.input)
    records = load_records(path)
    all_errors: list[str] = []

    image_count = 0
    for idx, record in enumerate(records):
        if record.get("image"):
            image_count += 1
        all_errors.extend(validate_record(record, idx))

    summary = {
        "input": str(path),
        "records": len(records),
        "records_with_image": image_count,
        "errors": len(all_errors),
        "valid": len(all_errors) == 0,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    for err in all_errors[: args.max_errors]:
        print(f"[ERROR] {err}")

    if args.summary:
        with Path(args.summary).open("w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

    if all_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
