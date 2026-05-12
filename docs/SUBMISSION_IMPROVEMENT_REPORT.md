# Submission Improvement Report

This document lists the repository changes that make the project more credible for challenge submission.

## Repository Hygiene

- Keep the project files at the repository root if possible.
- Remove generated files: `__pycache__/`, `.pytest_cache/`, `output/`, ZIP archives.
- Do not commit local model weights or raw datasets.
- Track small samples and reproducible logs instead of binary artifacts.

## Evidence Chain

For every major module, keep one runnable command and one output artifact:

| Module | Runnable Command | Evidence File |
|---|---|---|
| RAG | `python scripts/eval_rag.py` | `outputs/rag_eval_*.json` |
| GUI Agent | API request to `/api/agent/gui/plan` | `docs/demo_gui_agent_plan.md` |
| LLaVA | `python scripts/prepare_llava_cot_data.py ...` | `data/processed/*sample*.jsonl` |
| YOLO | `python scripts/benchmark_yolo.py ...` | `outputs/yolo_benchmark_*.json` |
| Fullstack | `pytest -q backend/tests` | GitHub Actions CI result |

## Recommended Challenge Wording

Use a truthful description:

> This is a recently organized and open-sourced AI fullstack engineering practice project. It covers RAG knowledge base QA, GUI Agent dry-run task planning, LLaVA-style multimodal data preparation and LoRA/QLoRA fine-tuning entrypoints, YOLO local inference and ONNX/TensorRT acceleration workflow, plus FastAPI and React fullstack delivery.

Avoid claiming production deployment, completed large-scale LLaVA fine-tuning, or measured TensorRT speedups unless the repository includes corresponding logs and metrics.
