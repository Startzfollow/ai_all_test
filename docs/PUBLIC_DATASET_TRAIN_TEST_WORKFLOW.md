# Public Dataset Training and Testing Workflow

This workflow adds a deeper training/test path for the business platform. It is designed to test whether the project can consume external/public datasets and convert them into model training and evaluation tasks.

## Stage 1: Prepare Public Dataset Manifests

```bash
python scripts/download_and_prepare_public_datasets.py \
  --datasets coco128 docvqa infographicvqa llava_cot \
  --output data/public_eval \
  --docvqa-root /mnt/PRO6000_disk/data/DocVQA \
  --infographicvqa-root /mnt/PRO6000_disk/data/InfographicVQA \
  --llava-root /mnt/PRO6000_disk/data/LLaVA-CoT-100k \
  --max-samples 128
```

This generates an inventory report:

```text
data/public_eval/public_dataset_inventory.json
data/public_eval/public_dataset_inventory.md
```

## Stage 2: Dry-Run Training/Test Plan

```bash
PYTHONPATH=. python scripts/run_public_dataset_train_test.py \
  --repo-root . \
  --suite all
```

The default mode is dry-run. It validates file presence and prints/plans commands without running GPU-heavy work.

## Stage 3: Execute Lightweight Tests

Run only the safe subset first:

```bash
PYTHONPATH=. python scripts/run_public_dataset_train_test.py \
  --repo-root . \
  --suite rag llava yolo_business mvtec \
  --execute
```

Optional COCO128 YOLO pipeline:

```bash
PYTHONPATH=. python scripts/run_public_dataset_train_test.py \
  --repo-root . \
  --suite yolo_coco128 \
  --model weights/yolov8n.pt \
  --execute
```

## Stage 4: Score the Public Dataset Suite

```bash
python scripts/evaluate_public_dataset_suite.py \
  --repo-root . \
  --min-score 0.65
```

Outputs:

```text
outputs/public_dataset_pipeline/public_train_test_report.json
outputs/public_dataset_pipeline/public_train_test_report.md
outputs/public_dataset_pipeline/public_dataset_suite_score.json
outputs/public_dataset_pipeline/public_dataset_suite_score.md
```

## Stage 5: Promote to Business Tasks

After the public dataset tests pass, connect them into the Business Platform V3 task system:

- RAG build task from DocVQA/field-service documents
- YOLO train/val task from COCO128 or business YOLO data
- LLaVA train-plan task from LLaVA-CoT/DocVQA/InfographicVQA samples
- Report generation task from the public dataset suite output

## What This Workflow Proves

It proves that the platform can:

1. discover public/local benchmark datasets;
2. create normalized manifests;
3. convert VQA samples into LLaVA-compatible JSONL;
4. validate model-training data;
5. run YOLO train/val smoke tests;
6. evaluate RAG and VQA assets;
7. generate a public dataset release-gate report.
