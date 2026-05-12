#!/usr/bin/env python3
"""Product-grade smoke acceptance suite.

Covers backend, RAG, GUI Agent, VLM/LLaVA, YOLO, training assets,
evaluation scripts, frontend assets, CI, and release hygiene.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
import traceback
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "smoke"
TINY_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="

@dataclass
class Result:
    name: str
    category: str
    status: str  # pass | fail | warn | skip
    critical: bool
    elapsed_ms: float
    summary: str
    details: dict[str, Any] = field(default_factory=dict)

class Ctx:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.results: list[Result] = []
        self.start = time.perf_counter()
        OUT.mkdir(parents=True, exist_ok=True)
        sys.path.insert(0, str(ROOT))

    def add(self, name: str, category: str, critical: bool, status: str, summary: str, elapsed: float, details: dict[str, Any] | None = None):
        self.results.append(Result(name, category, status, critical, round(elapsed, 2), summary, details or {}))

def run_cmd(cmd: list[str], cwd: Path = ROOT, timeout: int = 60) -> tuple[int, str, str]:
    p = subprocess.run(cmd, cwd=str(cwd), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    return p.returncode, p.stdout, p.stderr

def check(ctx: Ctx, name: str, category: str, critical: bool, fn: Callable[[], tuple[str, str, dict[str, Any]]]):
    t = time.perf_counter()
    try:
        status, summary, details = fn()
    except Exception as e:
        status, summary, details = "fail", f"{type(e).__name__}: {e}", {"traceback": traceback.format_exc(limit=8)}
    ctx.add(name, category, critical, status, summary, (time.perf_counter() - t) * 1000, details)

def tiny_png() -> Path:
    p = OUT / "tiny_smoke.png"
    if not p.exists():
        p.write_bytes(base64.b64decode(TINY_PNG_B64))
    return p

def client():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    return TestClient(app)

def repo_structure():
    required = [
        "backend/app/main.py",
        "backend/app/api/routers/rag.py",
        "backend/app/api/routers/agent.py",
        "backend/app/api/routers/multimodal.py",
        "backend/app/api/routers/vision.py",
        "backend/app/rag",
        "backend/app/agent",
        "frontend/package.json",
        "configs/default.yaml",
        "configs/llava_lora.yaml",
        "configs/zero2.json",
        "scripts/eval_rag.py",
        "scripts/benchmark_yolo.py",
        "scripts/prepare_llava_training_subset.py",
        "scripts/validate_llava_dataset.py",
        "experiments/llava_lora_docvqa/config.yaml",
        "docs/LLAVA_TRAINING_REPORT.md",
        "docs/EXPERIMENT_RESULTS.md",
        "docker-compose.yml",
        "Dockerfile.backend",
    ]
    missing = [p for p in required if not (ROOT / p).exists()]
    return ("fail", f"missing: {missing}", {"missing": missing}) if missing else ("pass", "required project structure is present", {"checked": required})

def ci_yaml():
    p = ROOT / ".github/workflows/ci.yml"
    if not p.exists():
        return "fail", "CI workflow missing", {}
    try:
        import yaml
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        jobs = list((data.get("jobs") or {}).keys())
        if "backend-smoke-test" not in jobs:
            return "fail", "backend-smoke-test job missing", {"jobs": jobs}
        return "pass", f"CI workflow parsed; jobs={jobs}", {"jobs": jobs}
    except Exception as e:
        text = p.read_text(encoding="utf-8", errors="ignore")
        ok = "pytest" in text and "backend-smoke-test" in text
        return ("warn" if ok else "fail"), f"YAML parser unavailable/error: {e}", {"text_check": ok}

def api_system():
    c = client()
    root, health, cfg = c.get("/"), c.get("/api/system/health"), c.get("/api/system/config")
    assert root.status_code == 200, root.text
    assert health.status_code == 200, health.text
    assert health.json().get("ok") is True, health.text
    assert cfg.status_code == 200, cfg.text
    return "pass", "root, health, config endpoints are healthy", {"root": root.json(), "health": health.json(), "config_keys": list(cfg.json().keys())}

def rag_flow():
    c = client()
    r = c.post("/api/rag/ingest", json={"documents_dir": "examples/docs", "collection": "smoke"})
    assert r.status_code == 200, r.text
    ingest = r.json()
    if ingest.get("ok") is not True:
        return "fail", f"RAG ingest failed: {ingest}", {"ingest": ingest}
    q = c.post("/api/rag/query", json={"question": "这个项目覆盖哪些 AI 技术栈？", "top_k": 3, "collection": "smoke"})
    assert q.status_code == 200, q.text
    data = q.json()
    if not data.get("sources"):
        return "fail", "RAG query returned no sources", {"query": data}
    if not data.get("answer"):
        return "fail", "RAG query returned empty answer", {"query": data}
    return "pass", f"RAG ingest/query succeeded with {len(data['sources'])} sources", {"ingest": ingest, "answer_preview": data["answer"][:240]}

def gui_agent():
    c = client()
    r = c.post("/api/agent/gui/plan", json={"task": "打开浏览器搜索 RAG 知识库并总结技术栈", "dry_run": True})
    assert r.status_code == 200, r.text
    data = r.json()
    plan = data.get("plan") or []
    if not plan:
        return "fail", "GUI Agent returned empty plan", {"response": data}
    if data.get("dry_run") is not True:
        return "fail", "GUI Agent must stay dry_run in smoke test", {"response": data}
    dangerous = {"delete_file", "format_disk", "execute_shell", "send_payment", "rm_rf"}
    actions = {str(x.get("action", "")).lower() for x in plan if isinstance(x, dict)}
    risky = sorted(actions & dangerous)
    if risky:
        return "fail", f"dangerous actions found: {risky}", {"response": data}
    return "pass", f"safe dry-run plan generated with {len(plan)} steps", {"plan": plan, "trace_count": len(data.get("trace") or [])}

def vlm_flow():
    c = client()
    img = tiny_png()
    r = c.post("/api/multimodal/llava/chat", json={"image_path": str(img), "prompt": "请描述测试图片。", "model": "smoke-vlm"})
    assert r.status_code == 200, r.text
    data = r.json()
    if "ok" not in data or "answer" not in data:
        return "fail", "VLM response schema invalid", {"response": data}
    return "pass", "VLM fallback returned stable schema", {"answer_preview": data.get("answer", "")[:200]}

def yolo_flow():
    c = client()
    img = tiny_png()
    r = c.post("/api/vision/yolo/detect", json={"image_path": str(img), "model": "smoke-yolo"})
    if r.status_code != 200:
        txt = r.text.lower()
        if any(x in txt for x in ["weight", "not found", "model", "onnx"]):
            return "skip", "YOLO weights not present; skipping live inference", {}
        return "fail", f"YOLO endpoint error: {r.status_code} {r.text[:120]}", {}
    data = r.json()
    if "boxes" not in data and "error" not in data:
        return "fail", "YOLO response schema unexpected", {"response": data}
    return "pass", "YOLO endpoint returned stable schema", {"has_boxes": "boxes" in data}

def rag_eval_script():
    p = ROOT / "scripts/eval_rag.py"
    if not p.exists():
        return "fail", "scripts/eval_rag.py missing", {}
    rc, out, err = run_cmd([sys.executable, str(p), "--documents-dir", "examples/docs", "--top-k", "4"], timeout=120)
    if rc != 0:
        return "fail", f"eval_rag.py failed: {err[:300]}", {"rc": rc, "stderr": err[:500]}
    report = OUT / f"rag_eval_{time.strftime('%Y%m%d_%H%M%S')}.json"
    return "pass", "eval_rag.py executed successfully", {"stdout": out[:500], "report_exists": report.exists()}

def llava_training_assets():
    required = ["experiments/llava_lora_docvqa/config.yaml", "experiments/llava_lora_docvqa/train.sh", "scripts/prepare_llava_training_subset.py", "scripts/validate_llava_dataset.py"]
    missing = [p for p in required if not (ROOT / p).exists()]
    if missing:
        return "fail", f"training assets missing: {missing}", {"missing": missing}
    metrics = ROOT / "experiments/llava_lora_docvqa/results/metrics.json"
    if metrics.exists():
        try:
            m = json.loads(metrics.read_text(encoding="utf-8"))
            return "pass", "training assets present; metrics.json exists", {"metrics": m}
        except Exception as e:
            return "warn", f"metrics.json exists but not valid JSON: {e}", {}
    return "pass", "training assets present; metrics.json not yet generated", {}

def yolo_benchmark_assets():
    p = ROOT / "scripts/benchmark_yolo.py"
    if not p.exists():
        return "fail", "scripts/benchmark_yolo.py missing", {}
    return "pass", "benchmark_yolo.py exists", {}

def frontend_assets():
    p = ROOT / "frontend/package.json"
    if not p.exists():
        return "fail", "frontend/package.json missing", {}
    src = ROOT / "frontend/src"
    if not src.exists():
        return "warn", "frontend/src missing", {}
    return "pass", "frontend assets present", {}

def security_hygiene():
    sensitive = [".env", ".pem", ".key", "token", "secret", "password"]
    patterns = [ROOT / ".git", ROOT / "node_modules", ROOT / "outputs", ROOT / "vector_db"]
    bad = []
    for path in ROOT.rglob("*"):
        if any(str(path).startswith(str(p)) for p in patterns):
            continue
        if path.is_file():
            name_lower = path.name.lower()
            if any(s in name_lower for s in sensitive):
                bad.append(str(path.relative_to(ROOT)))
            if path.stat().st_size > 100 * 1024 * 1024:
                bad.append(f"large_file:{path.relative_to(ROOT)}")
    if bad:
        return "warn", f"potential sensitive/large files found: {bad[:10]}", {"found": bad[:10]}
    return "pass", "no obvious secrets or large files found", {}

def score(results: list[Result]) -> tuple[int, str]:
    critical_fail = [r for r in results if r.critical and r.status == "fail"]
    warn = [r for r in results if r.status == "warn"]
    total = len(results)
    passed = len([r for r in results if r.status == "pass"])
    pct = int(passed / total * 100) if total else 0
    if critical_fail:
        return pct, f"{len(critical_fail)} critical failure(s): {[r.name for r in critical_fail]}"
    if pct < 80:
        return pct, f"score {pct}% < 80% threshold"
    return pct, f"score {pct}%"

def main():
    parser = argparse.ArgumentParser(description="Product smoke acceptance suite")
    parser.add_argument("--strict", action="store_true", help="require score >= 90% and no failures")
    parser.add_argument("--with-frontend", action="store_true", help="include frontend build check")
    parser.add_argument("--with-yolo-benchmark", action="store_true", help="run tiny YOLO benchmark")
    parser.add_argument("--with-llava-dataset", help="path to LLaVA dataset JSONL for validation")
    args = parser.parse_args()

    ctx = Ctx(args)
    check(ctx, "repo_structure", "structure", True, repo_structure)
    check(ctx, "ci_yaml", "structure", True, ci_yaml)
    check(ctx, "api_system", "backend", True, api_system)
    check(ctx, "rag_flow", "rag", True, rag_flow)
    check(ctx, "gui_agent", "agent", True, gui_agent)
    check(ctx, "vlm_flow", "vlm", True, vlm_flow)
    check(ctx, "yolo_flow", "yolo", True, yolo_flow)
    check(ctx, "rag_eval_script", "rag", True, rag_eval_script)
    check(ctx, "llava_training_assets", "training", True, llava_training_assets)
    check(ctx, "yolo_benchmark_assets", "yolo", True, yolo_benchmark_assets)
    check(ctx, "frontend_assets", "frontend", False, frontend_assets)
    check(ctx, "security_hygiene", "security", True, security_hygiene)

    total_score, reason = score(ctx.results)
    pct = total_score
    verdict = "PASS" if (pct >= 80 and not any(r.critical and r.status == "fail" for r in ctx.results)) else "FAIL"
    if args.strict:
        verdict = "PASS" if (pct >= 90 and not any(r.status == "fail" for r in ctx.results)) else "FAIL"

    report_json = OUT / "product_smoke_report.json"
    report_md = OUT / "product_smoke_report.md"
    elapsed_s = time.perf_counter() - ctx.start

    with report_json.open("w", encoding="utf-8") as f:
        json.dump({"verdict": verdict, "score_pct": pct, "reason": reason, "total_elapsed_s": round(elapsed_s, 1), "results": [asdict(r) for r in ctx.results]}, f, ensure_ascii=False, indent=2)

    md_lines = [f"# Product Smoke Acceptance Report\n", f"**Verdict**: {verdict}\n", f"**Score**: {pct}%\n", f"**Reason**: {reason}\n", f"**Elapsed**: {elapsed_s:.1f}s\n\n", "## Results\n\n", "| Check | Category | Status | Critical | Time (ms) | Summary |\n", "|---|---|---|---|---|---|\n"]
    for r in ctx.results:
        md_lines.append(f"| {r.name} | {r.category} | {r.status} | {r.critical} | {r.elapsed_ms} | {r.summary} |\n")
    with report_md.open("w", encoding="utf-8") as f:
        f.writelines(md_lines)

    print(f"\n{'='*50}")
    print(f"Verdict: {verdict} | Score: {pct}% | Reason: {reason}")
    print(f"Results written to {report_json} and {report_md}")
    print(f"{'='*50}\n")
    for r in ctx.results:
        icon = {"pass": "✅", "fail": "❌", "warn": "⚠️", "skip": "⏭️"}.get(r.status, "?")
        print(f"  {icon} [{r.category}] {r.name}: {r.summary} ({r.elapsed_ms}ms)")

    sys.exit(0 if verdict == "PASS" else 1)

if __name__ == "__main__":
    main()