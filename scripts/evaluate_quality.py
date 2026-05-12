#!/usr/bin/env python3
"""Quality evaluation gate for the AI fullstack multimodal project.

This script is intentionally different from product_smoke_acceptance.py:

- smoke acceptance answers: "Does the system run?"
- quality evaluation answers: "How good is the system?"

The script uses only the Python standard library so it can run in CI and on
machines without model dependencies. When real metrics are available, it reads
and reports them. When metrics are missing, it marks the module as incomplete
instead of inventing numbers.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


TEXT_EXTENSIONS = {".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".csv"}
DEFAULT_RAG_CORPUS = [
    "README.md",
    "PROJECT_COVERAGE.md",
    "QUICKSTART.md",
    "docs",
    "examples/docs",
]


@dataclass
class ModuleResult:
    name: str
    status: str
    score: float | None
    metrics: dict[str, Any]
    issues: list[str]
    recommendations: list[str]


@dataclass
class QualityReport:
    generated_at: str
    repo_root: str
    overall_score: float
    release_level: str
    smoke_pass_required_before_release: bool
    modules: dict[str, ModuleResult]
    next_actions: list[str]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(read_text(path))
    except Exception:
        return {}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line_no, line in enumerate(read_text(path).splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            rows.append({"_error": f"line {line_no}: {exc}"})
            continue
        if isinstance(row, dict):
            rows.append(row)
        else:
            rows.append({"_error": f"line {line_no}: not a JSON object"})
    return rows


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def tokenize(text: str) -> set[str]:
    normalized = normalize_text(text)
    ascii_tokens = set(re.findall(r"[a-zA-Z0-9_./+-]{2,}", normalized))
    # Keep short Chinese spans as lightweight lexical features.
    zh_tokens = set(re.findall(r"[\u4e00-\u9fff]{2,}", normalized))
    return ascii_tokens | zh_tokens


def iter_text_files(repo_root: Path, entries: Iterable[str]) -> Iterable[Path]:
    for entry in entries:
        path = repo_root / entry
        if not path.exists():
            continue
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
            yield path
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix.lower() in TEXT_EXTENSIONS:
                    if any(part.startswith(".") for part in child.relative_to(repo_root).parts):
                        continue
                    yield child


def chunk_text(source: str, text: str, size: int = 1200, overlap: int = 160) -> list[dict[str, Any]]:
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        return []
    chunks: list[dict[str, Any]] = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunk = text[start:end]
        chunks.append(
            {
                "source": source,
                "chunk_id": idx,
                "text": chunk,
                "tokens": list(tokenize(chunk)),
            }
        )
        if end == len(text):
            break
        start = max(0, end - overlap)
        idx += 1
    return chunks


def build_lexical_corpus(repo_root: Path, corpus_entries: list[str]) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    for path in iter_text_files(repo_root, corpus_entries):
        rel = path.relative_to(repo_root).as_posix()
        chunks.extend(chunk_text(rel, read_text(path)))
    return chunks


def retrieve_lexical(query: str, chunks: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
    q_tokens = tokenize(query)
    scored: list[tuple[float, dict[str, Any]]] = []
    for chunk in chunks:
        c_tokens = set(chunk.get("tokens", []))
        overlap = len(q_tokens & c_tokens)
        source_bonus = 0.15 if any(tok in chunk.get("source", "").lower() for tok in q_tokens) else 0.0
        score = overlap + source_bonus
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]


def evaluate_rag(repo_root: Path, eval_set_path: Path, top_k: int) -> ModuleResult:
    issues: list[str] = []
    recommendations: list[str] = []
    rows = read_jsonl(eval_set_path)
    if not rows:
        issues.append(f"RAG eval set not found or empty: {eval_set_path}")
        recommendations.append("Create a business-specific QA eval set with query, expected_keywords and expected_source_contains.")
        return ModuleResult("rag", "missing_eval_set", 0.25, {"items": 0}, issues, recommendations)

    corpus = build_lexical_corpus(repo_root, DEFAULT_RAG_CORPUS)
    if not corpus:
        issues.append("No readable corpus files found for offline lexical RAG evaluation.")
        recommendations.append("Add docs/examples or run the real RAG pipeline before quality evaluation.")
        return ModuleResult("rag", "missing_corpus", 0.20, {"items": len(rows)}, issues, recommendations)

    evaluated = 0
    keyword_hits = 0
    source_hits = 0
    details: list[dict[str, Any]] = []

    for row in rows:
        if row.get("_error"):
            issues.append(str(row["_error"]))
            continue
        query = str(row.get("query", "")).strip()
        expected_keywords = [str(x).lower() for x in row.get("expected_keywords", [])]
        expected_sources = [str(x).lower() for x in row.get("expected_source_contains", [])]
        if not query:
            issues.append(f"RAG eval item missing query: {row}")
            continue
        top = retrieve_lexical(query, corpus, top_k)
        joined = "\n".join(chunk["text"].lower() for chunk in top)
        sources = [chunk["source"] for chunk in top]
        source_joined = "\n".join(sources).lower()
        keyword_hit = bool(expected_keywords) and all(keyword in joined for keyword in expected_keywords)
        source_hit = not expected_sources or any(src in source_joined for src in expected_sources)
        evaluated += 1
        keyword_hits += int(keyword_hit)
        source_hits += int(source_hit)
        details.append(
            {
                "id": row.get("id", f"rag_{evaluated}"),
                "query": query,
                "keyword_hit": keyword_hit,
                "source_hit": source_hit,
                "top_sources": sources[:top_k],
            }
        )

    if evaluated == 0:
        return ModuleResult("rag", "invalid_eval_set", 0.20, {"items": len(rows)}, issues, recommendations)

    recall_at_k = keyword_hits / evaluated
    source_coverage = source_hits / evaluated
    score = 0.70 * recall_at_k + 0.30 * source_coverage

    if recall_at_k < 0.80:
        issues.append(f"RAG recall@{top_k} is below target: {recall_at_k:.3f} < 0.800")
        recommendations.extend(
            [
                "Tune chunk_size/chunk_overlap and preserve source/page/section metadata.",
                "Use a stronger embedding model such as bge-m3 or bge-large-zh-v1.5 for Chinese/multilingual corpora.",
                "Add BM25 + dense hybrid retrieval and rerank top-20 results into top-5 context chunks.",
            ]
        )
    if source_coverage < 0.90:
        issues.append(f"RAG source coverage is below target: {source_coverage:.3f} < 0.900")
        recommendations.append("Force answers to include citations and return retrieved chunk source metadata.")

    return ModuleResult(
        "rag",
        "evaluated",
        round(score, 4),
        {
            "items": evaluated,
            f"recall_at_{top_k}": round(recall_at_k, 4),
            "source_coverage": round(source_coverage, 4),
            "details": details,
        },
        issues,
        recommendations,
    )


def evaluate_agent(repo_root: Path, eval_set_path: Path) -> ModuleResult:
    rows = read_jsonl(eval_set_path)
    issues: list[str] = []
    recommendations: list[str] = []
    if not rows:
        issues.append(f"Agent eval set not found or empty: {eval_set_path}")
        recommendations.append("Create data/eval/agent_tasks.jsonl with task, required_steps and forbidden_actions.")
        return ModuleResult("agent", "missing_eval_set", 0.30, {"items": 0}, issues, recommendations)

    trace_doc = repo_root / "docs" / "GUI_AGENT_TRACE.md"
    trace_exists = trace_doc.exists()
    if not trace_exists:
        issues.append("docs/GUI_AGENT_TRACE.md is missing.")
        recommendations.append("Document trace schema and dry-run safety rules for GUI Agent plans.")

    total = 0
    valid = 0
    unsafe = 0
    for row in rows:
        if row.get("_error"):
            issues.append(str(row["_error"]))
            continue
        total += 1
        task = str(row.get("task", "")).lower()
        required = [str(x).lower() for x in row.get("required_steps", [])]
        forbidden = [str(x).lower() for x in row.get("forbidden_actions", [])]
        # Offline proxy: verify the task definition itself is specific enough and safety constraints exist.
        has_required_contract = bool(required) and all(step for step in required)
        has_safety_contract = bool(forbidden)
        contains_unsafe_request = any(word in task for word in ["delete", "payment", "send email", "rm -rf", "转账", "付款", "删除"])
        if contains_unsafe_request:
            unsafe += 1
        if has_required_contract and has_safety_contract and not contains_unsafe_request:
            valid += 1

    if total == 0:
        return ModuleResult("agent", "invalid_eval_set", 0.25, {"items": 0}, issues, recommendations)

    task_contract_rate = valid / total
    unsafe_action_rate = unsafe / total
    score = 0.80 * task_contract_rate + 0.20 * (1.0 - unsafe_action_rate)
    if trace_exists:
        score = min(1.0, score + 0.05)

    if task_contract_rate < 0.80:
        issues.append(f"Agent task contract rate is low: {task_contract_rate:.3f}")
        recommendations.append("Add 20+ task cases with required_steps, forbidden_actions and expected trace fields.")
    if unsafe_action_rate > 0.0:
        issues.append(f"Unsafe task rate is non-zero: {unsafe_action_rate:.3f}")
        recommendations.append("High-risk operations must require explicit human confirmation and dry-run mode by default.")

    return ModuleResult(
        "agent",
        "evaluated",
        round(score, 4),
        {
            "items": total,
            "task_contract_rate": round(task_contract_rate, 4),
            "unsafe_action_rate": round(unsafe_action_rate, 4),
            "trace_doc_exists": trace_exists,
        },
        issues,
        recommendations,
    )


def recursive_find_numbers(data: Any, names: set[str]) -> list[float]:
    found: list[float] = []
    if isinstance(data, dict):
        for key, value in data.items():
            normalized_key = str(key).lower()
            if normalized_key in names and isinstance(value, (int, float)) and not isinstance(value, bool):
                found.append(float(value))
            found.extend(recursive_find_numbers(value, names))
    elif isinstance(data, list):
        for item in data:
            found.extend(recursive_find_numbers(item, names))
    return found


def newest_json(paths: list[Path]) -> Path | None:
    candidates: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix == ".json":
            candidates.append(path)
        elif path.is_dir():
            candidates.extend(path.rglob("*.json"))
    candidates = [p for p in candidates if p.exists()]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def evaluate_yolo(repo_root: Path) -> ModuleResult:
    issues: list[str] = []
    recommendations: list[str] = []
    benchmark_file = newest_json([repo_root / "outputs", repo_root / "experiments" / "yolo_acceleration"])
    quality_file_candidates = [
        repo_root / "outputs" / "yolo_quality_metrics.json",
        repo_root / "experiments" / "yolo_acceleration" / "quality_metrics.json",
    ]
    quality_file = next((p for p in quality_file_candidates if p.exists()), None)

    benchmark = read_json(benchmark_file) if benchmark_file else {}
    quality = read_json(quality_file) if quality_file else {}

    fps_values = recursive_find_numbers(benchmark, {"fps", "throughput_fps"})
    latency_values = recursive_find_numbers(benchmark, {"mean_ms", "avg_latency_ms", "latency_ms", "p50_ms"})
    detection_values = recursive_find_numbers(benchmark, {"detections", "num_detections", "detection_count"})

    fps = max(fps_values) if fps_values else None
    mean_latency = min(latency_values) if latency_values else None
    detections = max(detection_values) if detection_values else None

    precision = first_number(quality, ["precision", "precision_at_conf", "p"])
    recall = first_number(quality, ["recall", "r"])
    map50 = first_number(quality, ["map50", "mAP50", "map_50"])
    map5095 = first_number(quality, ["map50_95", "mAP50-95", "map_50_95"])

    performance_score = 0.0
    if fps is not None:
        performance_score = min(1.0, fps / 60.0)
    elif mean_latency is not None and mean_latency > 0:
        performance_score = min(1.0, 30.0 / mean_latency)
    else:
        issues.append("No YOLO benchmark JSON found under outputs/ or experiments/yolo_acceleration/.")
        recommendations.append("Run scripts/benchmark_yolo.py and keep the generated JSON report.")

    accuracy_values = [x for x in [precision, recall, map50] if x is not None]
    if accuracy_values:
        accuracy_score = sum(accuracy_values) / len(accuracy_values)
    else:
        accuracy_score = None
        issues.append("No YOLO accuracy metrics found. Speed benchmark alone does not prove detection quality.")
        recommendations.append("Create a labeled validation set and report Precision, Recall, mAP50 and mAP50-95.")

    if accuracy_score is None:
        score = 0.45 * performance_score + 0.15  # credit for runnable benchmark, but not quality-ready.
        status = "performance_only"
    else:
        score = 0.35 * performance_score + 0.65 * accuracy_score
        status = "evaluated"

    if map50 is not None and map50 < 0.70:
        issues.append(f"YOLO mAP50 is below commercial PoC target: {map50:.3f} < 0.700")
        recommendations.append("Fine-tune on domain data and sweep conf/iou thresholds before export.")

    return ModuleResult(
        "yolo",
        status,
        round(score, 4),
        {
            "benchmark_file": str(benchmark_file.relative_to(repo_root)) if benchmark_file else None,
            "quality_file": str(quality_file.relative_to(repo_root)) if quality_file else None,
            "fps": round(fps, 4) if fps is not None else None,
            "mean_latency_ms": round(mean_latency, 4) if mean_latency is not None else None,
            "detections": detections,
            "precision": precision,
            "recall": recall,
            "map50": map50,
            "map50_95": map5095,
        },
        issues,
        recommendations,
    )


def first_number(data: Any, keys: list[str]) -> float | None:
    wanted = {key.lower() for key in keys}
    values = recursive_find_numbers(data, wanted)
    if not values:
        return None
    # If values are percentages, normalize them to 0-1.
    value = values[0]
    return value / 100.0 if value > 1.0 and value <= 100.0 else value


def evaluate_llava(repo_root: Path, eval_set_path: Path) -> ModuleResult:
    issues: list[str] = []
    recommendations: list[str] = []
    metrics_path = repo_root / "experiments" / "llava_lora_docvqa" / "results" / "metrics.json"
    metrics = read_json(metrics_path)
    eval_rows = read_jsonl(eval_set_path)
    train_script = repo_root / "experiments" / "llava_lora_docvqa" / "train.sh"
    config = repo_root / "experiments" / "llava_lora_docvqa" / "config.yaml"
    evidence_dir = repo_root / "experiments" / "llava_lora_docvqa" / "evidence"

    assets_ready = sum([metrics_path.exists(), train_script.exists(), config.exists(), evidence_dir.exists()]) / 4.0
    eval_accuracy = first_number(metrics, ["eval_accuracy", "accuracy", "exact_match", "anls", "sample_accuracy"])
    final_loss = first_number(metrics, ["final_train_loss", "train_loss", "loss"])
    examples_path = repo_root / "experiments" / "llava_lora_docvqa" / "results" / "examples.jsonl"
    examples = read_jsonl(examples_path)

    if eval_accuracy is None:
        issues.append("No LLaVA/VQA accuracy metric found in experiments/llava_lora_docvqa/results/metrics.json.")
        recommendations.append("Run a 100-sample VQA eval set and record exact_match / keyword_match / ANLS.")
    if final_loss is None:
        issues.append("No final training loss found. Training may not have been executed yet.")
        recommendations.append("Run a 1k smoke training job and store the loss log outside large checkpoints.")
    if not eval_rows:
        issues.append(f"LLaVA eval set is missing or empty: {eval_set_path}")
        recommendations.append("Create data/eval/llava_vqa_100.jsonl with image, question and answer fields.")
    if not examples:
        recommendations.append("Add a few inference examples to experiments/llava_lora_docvqa/results/examples.jsonl after evaluation.")

    if eval_accuracy is not None:
        score = 0.70 * eval_accuracy + 0.30 * assets_ready
        status = "evaluated"
    else:
        score = 0.35 * assets_ready
        status = "training_assets_ready" if assets_ready >= 0.75 else "missing_assets"

    return ModuleResult(
        "llava",
        status,
        round(score, 4),
        {
            "metrics_file": str(metrics_path.relative_to(repo_root)) if metrics_path.exists() else None,
            "eval_set_items": len(eval_rows),
            "inference_examples": len([r for r in examples if not r.get("_error")]),
            "assets_ready_ratio": round(assets_ready, 4),
            "eval_accuracy": eval_accuracy,
            "final_train_loss": final_loss,
        },
        issues,
        recommendations,
    )


def release_level(score: float) -> str:
    if score >= 0.90:
        return "production_candidate"
    if score >= 0.80:
        return "pilot_release_candidate"
    if score >= 0.65:
        return "commercial_poc"
    return "technical_demo"


def collect_next_actions(modules: dict[str, ModuleResult]) -> list[str]:
    actions: list[str] = []
    for module in modules.values():
        for recommendation in module.recommendations[:3]:
            if recommendation not in actions:
                actions.append(f"[{module.name}] {recommendation}")
    return actions[:12]


def render_markdown(report: QualityReport) -> str:
    lines: list[str] = []
    lines.append("# Product Quality Evaluation Report")
    lines.append("")
    lines.append(f"Generated at: `{report.generated_at}`")
    lines.append(f"Repository: `{report.repo_root}`")
    lines.append("")
    lines.append("## Overall")
    lines.append("")
    lines.append(f"- Overall quality score: **{report.overall_score:.3f}**")
    lines.append(f"- Release level: **{report.release_level}**")
    lines.append("- Smoke acceptance should pass before using this quality report as a release gate.")
    lines.append("")
    lines.append("## Module Scores")
    lines.append("")
    lines.append("| Module | Status | Score | Main Metrics |")
    lines.append("|---|---:|---:|---|")
    for module in report.modules.values():
        metric_summary = compact_metrics(module.metrics)
        score = "N/A" if module.score is None else f"{module.score:.3f}"
        lines.append(f"| {module.name} | {module.status} | {score} | {metric_summary} |")
    lines.append("")
    lines.append("## Issues")
    lines.append("")
    any_issue = False
    for module in report.modules.values():
        for issue in module.issues:
            any_issue = True
            lines.append(f"- **{module.name}**: {issue}")
    if not any_issue:
        lines.append("- No blocking issue detected by this evaluator.")
    lines.append("")
    lines.append("## Recommended Next Actions")
    lines.append("")
    if report.next_actions:
        for idx, action in enumerate(report.next_actions, start=1):
            lines.append(f"{idx}. {action}")
    else:
        lines.append("No recommendations generated.")
    lines.append("")
    lines.append("## Release Interpretation")
    lines.append("")
    lines.append("- `technical_demo`: system runs, but quality evidence is not enough for a business pilot.")
    lines.append("- `commercial_poc`: enough evidence for a scoped PoC, not a production promise.")
    lines.append("- `pilot_release_candidate`: metrics and safety evidence are close to a controlled pilot.")
    lines.append("- `production_candidate`: requires monitoring, security review, rollback plan, SLA and real user validation.")
    lines.append("")
    return "\n".join(lines) + "\n"


def compact_metrics(metrics: dict[str, Any]) -> str:
    preferred = [
        "items",
        "recall_at_3",
        "recall_at_4",
        "source_coverage",
        "task_contract_rate",
        "unsafe_action_rate",
        "fps",
        "mean_latency_ms",
        "precision",
        "recall",
        "map50",
        "eval_accuracy",
        "final_train_loss",
        "assets_ready_ratio",
    ]
    parts: list[str] = []
    for key in preferred:
        if key in metrics and metrics[key] is not None:
            parts.append(f"{key}={metrics[key]}")
    return "; ".join(parts[:6]) if parts else "-"


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate product quality beyond smoke-test pass/fail.")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--output-dir", default="outputs/quality", help="Output directory for JSON/Markdown reports")
    parser.add_argument("--rag-eval-set", default="data/eval/rag_qa_sample.jsonl")
    parser.add_argument("--agent-eval-set", default="data/eval/agent_tasks_sample.jsonl")
    parser.add_argument("--llava-eval-set", default="data/eval/llava_vqa_sample.jsonl")
    parser.add_argument("--top-k", type=int, default=4, help="Top-k retrieval depth for offline RAG proxy evaluation")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when overall score is below --min-score")
    parser.add_argument("--min-score", type=float, default=0.65, help="Minimum score for strict mode")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    output_dir = (repo_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    modules = {
        "rag": evaluate_rag(repo_root, repo_root / args.rag_eval_set, args.top_k),
        "agent": evaluate_agent(repo_root, repo_root / args.agent_eval_set),
        "yolo": evaluate_yolo(repo_root),
        "llava": evaluate_llava(repo_root, repo_root / args.llava_eval_set),
    }

    weights = {"rag": 0.30, "agent": 0.20, "yolo": 0.25, "llava": 0.25}
    overall = 0.0
    for name, weight in weights.items():
        score = modules[name].score if modules[name].score is not None else 0.0
        overall += weight * score
    overall = round(overall, 4)

    report = QualityReport(
        generated_at=utc_now(),
        repo_root=str(repo_root),
        overall_score=overall,
        release_level=release_level(overall),
        smoke_pass_required_before_release=True,
        modules=modules,
        next_actions=collect_next_actions(modules),
    )

    report_dict = asdict(report)
    json_path = output_dir / "product_quality_report.json"
    md_path = output_dir / "product_quality_report.md"
    write_json(json_path, report_dict)
    md_path.write_text(render_markdown(report), encoding="utf-8")

    print(f"Quality report written to: {json_path}")
    print(f"Markdown report written to: {md_path}")
    print(f"Overall score: {overall:.3f}")
    print(f"Release level: {report.release_level}")

    if args.strict and overall < args.min_score:
        print(f"STRICT MODE FAILED: {overall:.3f} < {args.min_score:.3f}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
