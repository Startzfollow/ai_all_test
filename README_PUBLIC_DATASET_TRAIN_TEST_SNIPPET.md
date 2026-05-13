## Public Dataset Training/Test Pipeline

This repository supports an additional public-dataset training/test workflow on top of the built-in field-service demo dataset.

```bash
python scripts/download_and_prepare_public_datasets.py \
  --datasets coco128 docvqa infographicvqa llava_cot \
  --output data/public_eval \
  --docvqa-root /mnt/PRO6000_disk/data/DocVQA \
  --infographicvqa-root /mnt/PRO6000_disk/data/InfographicVQA \
  --llava-root /mnt/PRO6000_disk/data/LLaVA-CoT-100k \
  --max-samples 128

PYTHONPATH=. python scripts/run_public_dataset_train_test.py \
  --repo-root . \
  --suite all

python scripts/evaluate_public_dataset_suite.py --repo-root . --min-score 0.65
```

Supported datasets:

- COCO128 for YOLO pipeline debugging
- DocVQA for document image question answering
- InfographicVQA for chart/dashboard reasoning
- MVTec AD for industrial anomaly scenario validation
- LLaVA-CoT for multimodal instruction fine-tuning samples
