from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, List


def gpu_snapshot() -> Dict[str, Any]:
    if not shutil.which("nvidia-smi"):
        return {"available": False, "gpus": [], "message": "nvidia-smi not found"}
    cmd = [
        "nvidia-smi",
        "--query-gpu=index,name,memory.total,memory.used,utilization.gpu,temperature.gpu,power.draw",
        "--format=csv,noheader,nounits",
    ]
    try:
        proc = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=10)
    except Exception as exc:
        return {"available": False, "gpus": [], "message": str(exc)}
    gpus: List[Dict[str, Any]] = []
    for line in proc.stdout.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 7:
            continue
        gpus.append(
            {
                "index": int(parts[0]),
                "name": parts[1],
                "memory_total_mb": float(parts[2]),
                "memory_used_mb": float(parts[3]),
                "utilization_gpu_percent": float(parts[4]),
                "temperature_c": float(parts[5]),
                "power_draw_w": None if parts[6] == "[Not Supported]" else float(parts[6]),
            }
        )
    return {"available": bool(gpus), "gpus": gpus, "captured_at": datetime.now(timezone.utc).isoformat()}


def platform_health() -> Dict[str, Any]:
    return {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "gpu": gpu_snapshot(),
        "logging": "stdout + database events",
        "alerts": "minimal: task failure events are persisted and exposed through the task result",
    }
