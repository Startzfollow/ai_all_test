# Quality Evaluation Plan

Smoke tests prove that the system runs. Quality evaluation proves whether the system is useful enough for a business scenario.

This project now separates the two gates:

| Gate | Question | Expected Output |
|---|---|---|
| Product Smoke Acceptance | Can the system run end-to-end? | Pass / fail report |
| Quality Evaluation | Are answers, detections, plans and model outputs accurate enough? | Metric report and release level |

## Target Metrics

| Module | Metric | Demo Target | Commercial PoC Target | Pilot Target |
|---|---:|---:|---:|---:|
| RAG | Recall@3 / Recall@4 | >= 0.60 | >= 0.80 | >= 0.88 |
| RAG | Source coverage | >= 0.70 | >= 0.90 | >= 0.95 |
| RAG | Hallucination rate | manual check | <= 0.10 | <= 0.05 |
| YOLO | FPS | >= 20 | >= 30 | scenario-specific |
| YOLO | Precision | measured | >= 0.80 | >= 0.88 |
| YOLO | Recall | measured | >= 0.75 | >= 0.85 |
| YOLO | mAP50 | measured | >= 0.70 | >= 0.80 |
| LLaVA/VQA | Exact match / ANLS / keyword accuracy | baseline | improved over base | stable on domain set |
| GUI Agent | Task contract rate | >= 0.60 | >= 0.80 | >= 0.90 |
| GUI Agent | Unsafe action rate | 0 | 0 | 0 |

## Evaluation Commands

Run the quality evaluator:

```bash
python scripts/evaluate_quality.py --repo-root . --top-k 4
```

Run it as a CI/release gate:

```bash
python scripts/evaluate_quality.py --repo-root . --strict --min-score 0.65
```

Generate a YOLO threshold sweep:

```bash
python scripts/sweep_yolo_thresholds.py \
  --model weights/yolov8n.pt \
  --image examples/images/demo.png \
  --runs 10
```

## Output Files

The evaluator writes:

```text
outputs/quality/product_quality_report.json
outputs/quality/product_quality_report.md
```

The threshold sweep writes:

```text
outputs/yolo_threshold_sweep.json
```

## Release Level Mapping

| Score Range | Release Level | Meaning |
|---:|---|---|
| < 0.65 | technical_demo | Useful for competition demo and internal review |
| 0.65 - 0.80 | commercial_poc | Suitable for a scoped commercial proof of concept |
| 0.80 - 0.90 | pilot_release_candidate | Suitable for controlled pilot with human supervision |
| >= 0.90 | production_candidate | Requires monitoring, SLA, security review and rollback plan |

## Important Boundary

Do not claim production readiness from smoke-test pass alone. A system can pass every API smoke test while still answering inaccurately, hallucinating citations, missing objects, or planning unsafe GUI operations.
