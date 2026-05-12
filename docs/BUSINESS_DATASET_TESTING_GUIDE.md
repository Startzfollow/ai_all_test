# Business Dataset Testing Guide

This guide explains how to test the Business Platform V3 with a dataset rather than only synthetic API calls.

## Recommended Dataset Strategy

Use a two-level strategy:

1. **Synthetic field-service dataset** for deterministic acceptance and CI.
2. **Optional public dataset** for object-detection pipeline debugging.

The synthetic dataset validates business logic. Public datasets validate external model tooling.

## Generate the Business Dataset

```bash
python scripts/create_field_service_demo_dataset.py \
  --output data/business_field_service_demo \
  --num-images 16 \
  --seed 42 \
  --overwrite
```

## Run Dataset Acceptance

```bash
python scripts/run_business_dataset_acceptance.py \
  --repo-root . \
  --dataset-root data/business_field_service_demo \
  --with-business-smoke \
  --with-quality-eval
```

Outputs:

```text
outputs/business_dataset_acceptance/business_dataset_acceptance.json
outputs/business_dataset_acceptance/business_dataset_acceptance.md
```

## Optional: Download COCO128 for YOLO Pipeline Debugging

```bash
python scripts/download_public_eval_assets.py \
  --dataset coco128 \
  --output data/public/coco128
```

COCO128 should not be committed to Git. Keep downloaded public datasets under `data/public/` or another ignored data directory.

## Acceptance Meaning

A passing dataset acceptance run means:

- RAG documents exist and have evaluation questions.
- YOLO images and labels are structurally valid.
- VQA samples reference existing images.
- Agent tasks contain expected and forbidden actions.
- Business smoke and quality evaluation can run against the repository.

It does **not** mean production accuracy is sufficient. Production accuracy requires real labeled business data and a larger evaluation set.
