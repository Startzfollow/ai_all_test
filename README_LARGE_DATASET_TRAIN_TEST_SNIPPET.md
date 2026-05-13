## Large Dataset Train/Test

This repository includes a scalable dataset workflow for moving beyond tiny smoke tests:

```bash
python scripts/create_large_field_service_yolo_dataset.py \
  --output data/field_service_yolo_dev \
  --num-images 500 \
  --overwrite

python scripts/check_yolo_dataset_quality.py \
  --data data/field_service_yolo_dev/data.yaml

python scripts/run_large_yolo_train_eval.py \
  --data data/field_service_yolo_dev/data.yaml \
  --model weights/yolov8n.pt \
  --tier dev
```

For multimodal datasets:

```bash
python scripts/prepare_large_multimodal_samples.py \
  --output data/public_eval_large \
  --docvqa-root /mnt/PRO6000_disk/data/DocVQA \
  --infographicvqa-root /mnt/PRO6000_disk/data/InfographicVQA \
  --llava-root /mnt/PRO6000_disk/data/LLaVA-CoT-100k \
  --limit 5000
```

This creates a three-layer data strategy:

1. tiny smoke data for CI
2. large synthetic business data for dev/pilot training
3. public/local large multimodal datasets for model evaluation and fine-tuning
