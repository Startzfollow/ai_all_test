#!/usr/bin/env python3
"""Database health check for V4 production-pilot deployments."""
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.business.db_health_v4 import check_database_health  # noqa: E402


def main() -> int:
    result = check_database_health()
    out = ROOT / "outputs" / "db_health_v4"
    out.mkdir(parents=True, exist_ok=True)
    (out / "db_health_v4.json").write_text(json.dumps(result.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    # Missing tables are a warning in CI because schema initialization may be run separately.
    return 0 if result.connected else 1


if __name__ == "__main__":
    raise SystemExit(main())
