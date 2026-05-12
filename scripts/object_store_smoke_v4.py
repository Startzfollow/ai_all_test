#!/usr/bin/env python3
"""Object store smoke test for local / MinIO-compatible pilot deployments."""
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.business.object_store_v4 import build_object_store_from_env  # noqa: E402


def main() -> int:
    out = ROOT / "outputs" / "object_store_v4_smoke"
    out.mkdir(parents=True, exist_ok=True)
    sample = out / "sample.txt"
    sample.write_text("field service ai ops object store smoke\n", encoding="utf-8")

    store = build_object_store_from_env()
    info1 = store.put_file("smoke/sample.txt", sample)
    info2 = store.put_text("reports/smoke_report.md", "# Smoke Report\n\nObject store OK.\n")
    read_back = store.get_text("reports/smoke_report.md")
    keys = store.list_keys()

    report = {
        "passed": store.exists(info1.uri) and "Object store OK" in read_back and len(keys) >= 2,
        "stored_objects": [info1.__dict__, info2.__dict__],
        "keys": keys,
    }
    (out / "object_store_smoke_v4.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
