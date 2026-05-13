# YOLO Large Dataset Acceptance

## Acceptance levels

| Level | Dataset | Criteria |
|---|---|---|
| pipeline smoke | 64 synthetic images | train/val completes |
| dev learning check | 500 synthetic images | loss decreases, non-empty predictions, metrics exported |
| pilot readiness | 1500+ synthetic/real images | Precision/Recall/mAP targets are defined and measured |
| production candidate | real business validation set | meets customer-defined thresholds |

## Minimum dataset requirements

For a meaningful YOLO quality experiment:

- at least 100 images per class for early dev checks
- at least 200 instances per class for stable validation
- separate train/val/test splits
- negative samples
- no duplicated val/test images in train
- no missing classes in validation

## Recommended training matrix

| Model | Tier | Epochs | Image size | Purpose |
|---|---|---:|---:|---|
| yolov8n | smoke | 1 | 320 | pipeline check |
| yolov8n | dev | 30 | 640 | speed/accuracy baseline |
| yolov8s | dev | 30 | 640 | stronger baseline |
| yolov8s | pilot | 80 | 640/960 | pilot candidate |

## Safe wording

Use this wording after smoke/dev runs:

> The YOLO train/validation pipeline has been validated on a larger field-service dataset. Current results measure training stability, latency, and preliminary detection quality. Final business accuracy requires real field-service validation data.

Avoid:

> The detector is production-ready.

unless it has passed real validation-set acceptance.
