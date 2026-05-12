#!/usr/bin/env python3
"""Run or dry-run YAML-defined experiments.

By default this script is safe: it lists commands and does not execute them.
Use --execute with --step, or --execute-all, only after reviewing commands.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Install with: pip install pyyaml") from exc


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid experiment config: {path}")
    return data


def get_commands(config: dict[str, Any]) -> dict[str, str]:
    commands = config.get("command_templates") or {}
    if not isinstance(commands, dict):
        raise ValueError("command_templates must be a mapping")
    return {str(k): str(v).strip() for k, v in commands.items()}


def write_run_record(output_dir: Path, record: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"experiment_run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a YAML-defined experiment.")
    parser.add_argument("--config", required=True, help="Path to experiment YAML")
    parser.add_argument("--step", help="Command template key to execute")
    parser.add_argument("--list-commands", action="store_true", help="List available commands")
    parser.add_argument("--execute", action="store_true", help="Execute --step")
    parser.add_argument("--execute-all", action="store_true", help="Execute all commands in order")
    parser.add_argument("--output-dir", default="outputs/experiments")
    args = parser.parse_args()

    config_path = Path(args.config)
    config = load_config(config_path)
    commands = get_commands(config)
    name = config.get("name", config_path.stem)

    if args.list_commands or (not args.execute and not args.execute_all):
        print(f"Experiment: {name}")
        print(f"Config: {config_path}")
        print("Available commands:")
        for key, command in commands.items():
            print(f"\n[{key}]\n{command}")
        if not args.execute and not args.execute_all:
            print("\nDry-run only. Use --execute --step <name> or --execute-all to run.")
        return 0

    if args.execute and not args.step:
        raise SystemExit("--execute requires --step")

    selected: list[tuple[str, str]]
    if args.execute_all:
        selected = list(commands.items())
    else:
        if args.step not in commands:
            raise SystemExit(f"Unknown step: {args.step}. Available: {', '.join(commands)}")
        selected = [(args.step, commands[args.step])]

    run_record: dict[str, Any] = {
        "experiment": name,
        "config": str(config_path),
        "started_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "steps": [],
    }

    for step_name, command in selected:
        print(f"\n=== Running step: {step_name} ===")
        print(command)
        result = subprocess.run(command, shell=True, text=True, env=os.environ.copy())
        run_record["steps"].append({
            "name": step_name,
            "command": command,
            "returncode": result.returncode,
        })
        if result.returncode != 0:
            run_record["status"] = "failed"
            path = write_run_record(Path(args.output_dir), run_record)
            print(f"Experiment failed. Record: {path}")
            return result.returncode

    run_record["status"] = "passed"
    run_record["finished_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    path = write_run_record(Path(args.output_dir), run_record)
    print(f"Experiment passed. Record: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
