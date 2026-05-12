#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from backend.app.business.task_queue import BusinessTaskRunner

parser = argparse.ArgumentParser(description="Run minimal business task worker")
parser.add_argument("--loop", action="store_true", help="Keep polling pending tasks")
parser.add_argument("--interval", type=float, default=5.0)
args = parser.parse_args()

runner = BusinessTaskRunner()
while True:
    result = runner.run_next()
    if result:
        print(result)
    elif not args.loop:
        print("no pending task")
        break
    time.sleep(args.interval)
