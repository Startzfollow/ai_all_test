#!/usr/bin/env python3
"""Generate a consolidated platform report from available smoke, quality, and asset evidence."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover
        return {"error": f"failed to read {path}: {exc}"}


def find_latest(pattern: str, root: Path) -> Path | None:
    matches = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return matches[0] if matches else None


def score_release(quality_report: dict[str, Any] | None, smoke_report: dict[str, Any] | None) -> tuple[float, str]:
    score = 0.0
    if quality_report:
        score = float(
            quality_report.get("overall_score")
            or quality_report.get("overall", {}).get("quality_score")
            or 0.0
        )
    if smoke_report and smoke_report.get("summary", {}).get("pass_rate"):
        score = max(score, float(smoke_report["summary"]["pass_rate"]) * 0.6)

    if score >= 0.90:
        level = "production_candidate"
    elif score >= 0.80:
        level = "pilot_candidate"
    elif score >= 0.65:
        level = "commercial_poc"
    elif score >= 0.50:
        level = "technical_demo"
    else:
        level = "incomplete"
    return round(score, 3), level


def render_md(report: dict[str, Any]) -> str:
    lines = [
        "# Platform V2 Consolidated Report",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- Overall score: `{report['overall_score']}`",
        f"- Release level: `{report['release_level']}`",
        "",
        "## Evidence Sources",
        "",
        "| Evidence | Path | Status |",
        "|---|---|---|",
    ]
    for name, info in report["evidence"].items():
        lines.append(f"| {name} | `{info.get('path') or '-'}` | {info.get('status')} |")

    lines.extend([
        "",
        "## Recommended Next Actions",
        "",
    ])
    for item in report["next_actions"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate platform V2 consolidated report.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-dir", default="outputs/platform")
    args = parser.parse_args()

    root = Path(args.repo_root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    smoke_path = root / "outputs/smoke/product_smoke_report.json"
    quality_path = root / "outputs/quality/product_quality_report.json"
    asset_path = root / "outputs/assets/local_asset_inventory.json"
    yolo_path = find_latest("outputs/yolo_benchmark_*.json", root)

    smoke = read_json(smoke_path)
    quality = read_json(quality_path)
    assets = read_json(asset_path)
    yolo = read_json(yolo_path) if yolo_path else None

    score, level = score_release(quality, smoke)

    evidence = {
        "product_smoke": {"path": str(smoke_path), "status": "found" if smoke else "missing"},
        "quality_report": {"path": str(quality_path), "status": "found" if quality else "missing"},
        "asset_inventory": {"path": str(asset_path), "status": "found" if assets else "missing"},
        "latest_yolo_benchmark": {"path": str(yolo_path) if yolo_path else None, "status": "found" if yolo else "missing"},
    }

    next_actions = []
    if not assets:
        next_actions.append("Run scripts/scan_local_assets.py to generate local model and dataset inventory.")
    if not quality:
        next_actions.append("Run scripts/evaluate_quality.py to generate quality scores.")
    if not smoke:
        next_actions.append("Run scripts/product_smoke_acceptance.py to generate smoke acceptance evidence.")
    if not yolo:
        next_actions.append("Run YOLO benchmark or threshold sweep to attach real latency evidence.")
    if level in {"technical_demo", "commercial_poc"}:
        next_actions.append("Add real LLaVA training loss/metrics and domain-specific YOLO mAP before claiming pilot readiness.")
    if not next_actions:
        next_actions.append("Maintain evidence freshness and expand domain evaluation sets.")

    report = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "overall_score": score,
        "release_level": level,
        "evidence": evidence,
        "next_actions": next_actions,
    }

    json_path = output_dir / "platform_v2_report.json"
    md_path = output_dir / "platform_v2_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_md(report), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"Release level: {level}")
    print(f"Overall score: {score}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
