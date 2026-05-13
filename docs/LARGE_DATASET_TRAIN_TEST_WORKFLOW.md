# Large Dataset Train/Test Workflow

This workflow upgrades the project from tiny smoke training to scalable dev/pilot training.

## Why this exists

The tiny business demo dataset validates the pipeline, but it is too small for model quality claims.

Use three tiers instead:

| Tier | Images | Epochs | Purpose |
|---|---:|---:|---|
| smoke | 64 | 1 | verify code path and data format |
| dev | 500 | 30 | verify learning behavior and threshold tuning |
| pilot | 1500+ | 80+ | prepare for pilot-quality evaluation |

## Generate a larger synthetic field-service YOLO dataset

```bash
python scripts/create_large_field_service_yolo_dataset.py \
  --output data/field_service_yolo_dev \
  --num-images 500 \
  --image-size 640 \
  --seed 42 \
  --overwrite
```

## Check YOLO dataset quality

```bash
python scripts/check_yolo_dataset_quality.py \
  --data data/field_service_yolo_dev/data.yaml
```

The checker validates:

- image count
- train/val/test split
- per-class instance count
- missing labels
- empty-label images
- bbox bounds
- class coverage

## Train and validate YOLO

```bash
python scripts/run_large_yolo_train_eval.py \
  --data data/field_service_yolo_dev/data.yaml \
  --model weights/yolov8n.pt \
  --tier dev
```

Outputs:

```text
outputs/large_dataset_train_test/
├── *_quality.json
├── *_train.log
├── *_val.log
├── *_report.json
└── *_report.md
```

## Prepare large multimodal samples

```bash
python scripts/prepare_large_multimodal_samples.py \
  --output data/public_eval_large \
  --docvqa-root /mnt/PRO6000_disk/data/DocVQA \
  --infographicvqa-root /mnt/PRO6000_disk/data/InfographicVQA \
  --llava-root /mnt/PRO6000_disk/data/LLaVA-CoT-100k \
  --limit 5000
```

This creates normalized JSONL samples for VQA and LLaVA-style training/evaluation experiments.

## One-command suite

```bash
python scripts/run_large_dataset_train_test_suite.py \
  --tier dev \
  --model weights/yolov8n.pt \
  --with-yolo-train \
  --docvqa-root /mnt/PRO6000_disk/data/DocVQA \
  --infographicvqa-root /mnt/PRO6000_disk/data/InfographicVQA \
  --llava-root /mnt/PRO6000_disk/data/LLaVA-CoT-100k
```

## Interpretation

Do not compare smoke mAP to production targets. Smoke verifies the pipeline only.

For business-quality claims, use at least the dev tier and report:

- Precision
- Recall
- mAP50
- mAP50-95
- latency / FPS
- per-class error cases

For production claims, use real or customer-representative field-service data.
