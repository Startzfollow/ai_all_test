# Public Dataset Integration

This project now supports a three-layer dataset strategy:

1. **Business synthetic datasets** for deterministic CI and end-to-end field-service workflow tests.
2. **Public benchmark datasets** for external validation and reproducible evaluation.
3. **Local large-scale training datasets** for LLaVA-style fine-tuning and model-quality improvement.

## Supported Dataset Adapters

| Dataset | Adapter mode | Primary use | Notes |
|---|---|---|---|
| COCO128 | optional download | YOLO train/val pipeline smoke test | Pipeline validation, not field-service accuracy |
| DocVQA | local root scan | document VQA / maintenance form understanding | Use official annotations when available |
| InfographicVQA | local root scan | chart/dashboard reasoning | Use official annotations when available |
| MVTec AD | local/manual root scan | industrial anomaly scenario validation | Anomaly detection, not pure object detection |
| LLaVA-CoT | local root scan | LLaVA-style training subset | Used for LoRA/QLoRA smoke training |

## Why We Keep Synthetic Business Data

The synthetic field-service dataset is still important because it provides a stable, small, GitHub-friendly dataset for:

- CI smoke tests
- business task validation
- frontend demonstrations
- RAG/YOLO/VQA/Agent workflow consistency
- release-gate checks without external downloads

Public datasets complement it by validating the model pipeline against broader benchmark data.

## Preparation Command

```bash
python scripts/download_and_prepare_public_datasets.py \
  --datasets coco128 docvqa infographicvqa llava_cot \
  --output data/public_eval \
  --docvqa-root /mnt/PRO6000_disk/data/DocVQA \
  --infographicvqa-root /mnt/PRO6000_disk/data/InfographicVQA \
  --llava-root /mnt/PRO6000_disk/data/LLaVA-CoT-100k \
  --max-samples 128
```

Optional MVTec AD:

```bash
python scripts/download_and_prepare_public_datasets.py \
  --datasets mvtec_ad \
  --mvtec-root /path/to/mvtec_anomaly_detection \
  --output data/public_eval
```

## Outputs

```text
data/public_eval/
├── public_dataset_inventory.json
├── public_dataset_inventory.md
├── coco128/
├── docvqa_sample/
│   ├── manifest.json
│   ├── vqa_eval.jsonl
│   └── llava_eval.jsonl
├── infographicvqa_sample/
│   ├── manifest.json
│   ├── vqa_eval.jsonl
│   └── llava_eval.jsonl
├── mvtec_ad_sample/
│   └── anomaly_eval.jsonl
└── llava_cot_sample/
    └── llava_train_sample.jsonl
```

## Data Governance

Do not commit raw public datasets or large local datasets. Commit only:

- preparation scripts
- small generated manifests
- evaluation summaries
- metrics and reports
- lightweight demo images when necessary

Large files should remain under local storage, MinIO/S3, or a dataset registry.
