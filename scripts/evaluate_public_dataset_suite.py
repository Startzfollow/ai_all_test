#!/usr/bin/env python3
"""Aggregate public dataset preparation and train/test reports into a release gate."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def score_inventory(inv: dict[str, Any] | None) -> tuple[float, list[str]]:
    if not inv:
        return 0.0, ["public dataset inventory missing"]
    summaries = inv.get("summaries", [])
    if not summaries:
        return 0.0, ["no dataset summaries"]
    ready = [s for s in summaries if s.get("status") in {"ready", "counted"}]
    score = len(ready) / max(1, len(summaries))
    notes = [f"{s.get('name')}: {s.get('status')}" for s in summaries]
    return score, notes


def score_train_test(rep: dict[str, Any] | None) -> tuple[float, list[str]]:
    if not rep:
        return 0.0, ["public train/test report missing"]
    results = rep.get("results", [])
    if not results:
        return 0.0, ["no train/test results"]
    ok = 0
    notes = []
    for r in results:
        status = r.get("status")
        if status in {"planned", "executed", "counted"}:
            ok += 1
        notes.append(f"{r.get('name')}: {status}")
    return ok / max(1, len(results)), notes


def release_level(score: float) -> str:
    if score >= 0.90:
        return "production_candidate"
    if score >= 0.80:
        return "pilot_candidate"
    if score >= 0.65:
        return "commercial_poc"
    return "technical_demo"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--public-root", default="data/public_eval")
    parser.add_argument("--pipeline-output", default="outputs/public_dataset_pipeline")
    parser.add_argument("--min-score", type=float, default=0.65)
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve()
    inv = read_json(repo / args.public_root / "public_dataset_inventory.json")
    rep = read_json(repo / args.pipeline_output / "public_train_test_report.json")
    inv_score, inv_notes = score_inventory(inv)
    train_score, train_notes = score_train_test(rep)
    overall = round(0.45 * inv_score + 0.55 * train_score, 4)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_score": overall,
        "passed": overall >= args.min_score,
        "release_level": release_level(overall),
        "inventory_score": inv_score,
        "train_test_score": train_score,
        "inventory_notes": inv_notes,
        "train_test_notes": train_notes,
        "next_actions": [
            "Replace placeholder DocVQA/InfographicVQA answers with official annotations where available.",
            "Run YOLO COCO128/business training with --execute on a GPU machine.",
            "Connect MVTec AD root and add anomaly-detection metrics.",
            "Run LLaVA smoke training and record loss/metrics/examples.",
        ],
    }
    out_dir = repo / args.pipeline_output
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "public_dataset_suite_score.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = ["# Public Dataset Suite Score", "", f"Overall score: `{overall}`", f"Passed: `{payload['passed']}`", f"Release level: `{payload['release_level']}`", "", "## Inventory", ""]
    md.extend(f"- {n}" for n in inv_notes)
    md.extend(["", "## Train/Test", ""])
    md.extend(f"- {n}" for n in train_notes)
    md.extend(["", "## Next Actions", ""])
    md.extend(f"- {n}" for n in payload["next_actions"])
    (out_dir / "public_dataset_suite_score.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
