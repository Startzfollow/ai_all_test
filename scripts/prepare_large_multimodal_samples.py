#!/usr/bin/env python3
"""Prepare larger multimodal samples from local public datasets.

The script is intentionally schema-tolerant: it scans JSON/JSONL files and tries
to normalize common DocVQA/InfographicVQA/LLaVA-style fields into a simple JSONL
format used by downstream train/test scripts.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional


def read_records(path: Path) -> Iterator[Dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    if path.suffix.lower() == ".jsonl":
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                yield obj
        return
    if path.suffix.lower() == ".json":
        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            return
        if isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict):
                    yield item
        elif isinstance(obj, dict):
            for key in ["data", "items", "questions", "annotations", "samples"]:
                val = obj.get(key)
                if isinstance(val, list):
                    for item in val:
                        if isinstance(item, dict):
                            yield item
            yield obj


def normalize(record: Dict[str, Any], dataset: str) -> Optional[Dict[str, Any]]:
    image = record.get("image") or record.get("image_path") or record.get("imageFilename") or record.get("image_filename")
    question = record.get("question") or record.get("query") or record.get("prompt")
    answer = record.get("answer") or record.get("answers") or record.get("label")
    conversations = record.get("conversations")
    if conversations and isinstance(conversations, list):
        human = next((x.get("value") for x in conversations if isinstance(x, dict) and x.get("from") in {"human", "user"}), None)
        assistant = next((x.get("value") for x in conversations if isinstance(x, dict) and x.get("from") in {"gpt", "assistant"}), None)
        question = question or human
        answer = answer or assistant
    if isinstance(answer, list):
        answer = answer[0] if answer else None
    if not question or not answer:
        return None
    return {
        "dataset": dataset,
        "image": image,
        "question": str(question),
        "answer": str(answer),
        "source_fields": sorted(record.keys())[:20],
    }


def collect(root: Path, dataset: str, limit: int, seed: int) -> List[Dict[str, Any]]:
    files = [p for p in root.rglob("*") if p.suffix.lower() in {".json", ".jsonl"}]
    rng = random.Random(seed)
    rng.shuffle(files)
    out: List[Dict[str, Any]] = []
    for f in files:
        for rec in read_records(f) or []:
            norm = normalize(rec, dataset)
            if norm:
                norm["source_file"] = str(f)
                out.append(norm)
                if len(out) >= limit:
                    return out
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="data/public_eval_large")
    ap.add_argument("--docvqa-root", default=None)
    ap.add_argument("--infographicvqa-root", default=None)
    ap.add_argument("--llava-root", default=None)
    ap.add_argument("--limit", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    all_records: List[Dict[str, Any]] = []
    sources = {
        "docvqa": args.docvqa_root,
        "infographicvqa": args.infographicvqa_root,
        "llava_cot": args.llava_root,
    }
    manifest = {"output": str(out), "limit": args.limit, "datasets": {}}
    for name, root in sources.items():
        if not root:
            continue
        p = Path(root)
        records = collect(p, name, args.limit, args.seed)
        target = out / f"{name}_sample.jsonl"
        target.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in records) + ("\n" if records else ""), encoding="utf-8")
        manifest["datasets"][name] = {"root": str(p), "records": len(records), "output": str(target)}
        all_records.extend(records)

    combined = out / "multimodal_combined_sample.jsonl"
    combined.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in all_records) + ("\n" if all_records else ""), encoding="utf-8")
    manifest["combined_records"] = len(all_records)
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
