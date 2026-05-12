#!/usr/bin/env python3
"""Capture browser screenshots for README evidence.

Prerequisite:
  pip install playwright
  python -m playwright install chromium

Run backend and frontend first, then execute this script.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontend-url", default="http://127.0.0.1:5173")
    parser.add_argument("--api-docs-url", default="http://127.0.0.1:8000/docs")
    parser.add_argument("--output-dir", default="docs/assets")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        guide = output_dir / "manual_screenshot_required.md"
        guide.write_text(
            "# Manual Screenshot Required\n\n"
            "Playwright is not installed, so automatic capture was skipped.\n\n"
            "Run:\n\n"
            "```bash\n"
            "pip install playwright\n"
            "python -m playwright install chromium\n"
            "python scripts/capture_demo_screenshots.py\n"
            "```\n\n"
            "Or manually capture:\n\n"
            "- docs/assets/api_docs.png from http://127.0.0.1:8000/docs\n"
            "- docs/assets/frontend_dashboard.png from http://127.0.0.1:5173\n"
            "- docs/assets/gui_agent_trace.png from the GUI Agent tab\n",
            encoding="utf-8",
        )
        print(f"Playwright not available: {exc}")
        print(f"Wrote guide to: {guide}")
        sys.exit(2)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1200})

        page.goto(args.api_docs_url, wait_until="networkidle")
        page.screenshot(path=str(output_dir / "api_docs.png"), full_page=True)

        page.goto(args.frontend_url, wait_until="networkidle")
        page.screenshot(path=str(output_dir / "frontend_dashboard.png"), full_page=True)

        try:
            page.get_by_text("GUI Agent Planner").click()
            page.get_by_text("生成动作计划").click()
            page.wait_for_timeout(500)
            page.screenshot(path=str(output_dir / "gui_agent_trace.png"), full_page=True)
        except Exception:
            page.screenshot(path=str(output_dir / "gui_agent_trace.png"), full_page=True)

        browser.close()

    print(f"Screenshots written to: {output_dir}")


if __name__ == "__main__":
    main()
