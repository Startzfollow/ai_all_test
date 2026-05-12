# Platform V2 Architecture

## 1. Positioning

The next version upgrades the repository from a runnable AI demo into a
multimodal AI engineering platform that supports:

- local model and dataset registry
- reproducible experiment orchestration
- RAG quality evaluation
- YOLO latency and quality benchmarking
- LLaVA-style large-scale multimodal training workflow
- GUI Agent trace and safety evaluation
- smoke acceptance, quality gates, and release reporting

The goal is not only to prove that each module runs, but also to make the
system measurable, repeatable, and suitable for commercial PoC review.

## 2. Core Layers

| Layer | Responsibility |
|---|---|
| Asset Registry | Record local models, datasets, paths, usage, and publication policy |
| Experiment Recipes | Define repeatable RAG, YOLO, LLaVA, and Agent experiments |
| Execution Layer | Run dry-run or real experiments from YAML recipes |
| Evaluation Layer | Produce smoke reports, quality scores, and release gates |
| Evidence Layer | Collect logs, metrics, hardware info, git commit, and examples |
| Product Layer | FastAPI + React demo, CI, screenshots, and release checklist |

## 3. Why This Upgrade Matters

Smoke tests prove that the system is runnable. Commercial PoC review requires
more evidence:

1. What models and datasets are available?
2. Which experiment was run?
3. Which configuration was used?
4. What metrics were produced?
5. Which hardware and git commit produced the result?
6. What is still a demo, what is a PoC, and what is production-ready?

This upgrade introduces a registry-driven and report-driven workflow to answer
these questions directly.

## 4. Recommended Operating Flow

```bash
python scripts/scan_local_assets.py \
  --models-root /mnt/PRO6000_disk/models \
  --data-root /mnt/PRO6000_disk/data

python scripts/run_experiment.py \
  --config configs/experiments/rag_bge_reranker_v2.yaml \
  --list-commands

python scripts/evaluate_quality.py --repo-root . --top-k 4

python scripts/generate_platform_report.py --repo-root .
```

## 5. Release Levels

| Score | Level | Meaning |
|---|---|---|
| < 0.50 | incomplete | Not enough evidence |
| 0.50 - 0.65 | technical_demo | Runnable but accuracy is weak |
| 0.65 - 0.80 | commercial_poc | Suitable for business PoC discussion |
| 0.80 - 0.90 | pilot_candidate | Suitable for limited pilot |
| >= 0.90 | production_candidate | Candidate for production hardening |

## 6. Boundaries

This repository should not claim production readiness until the following are
available:

- real LLaVA/VQA training logs and evaluation metrics
- domain-specific YOLO validation set and mAP results
- stronger RAG embedding/reranker evaluation
- authentication and tenant isolation if used in a business setting
- monitoring, audit logs, error tracking, and backup strategy
