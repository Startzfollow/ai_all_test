# Dataset Training/Test Acceptance Gate

## Acceptance Levels

| Level | Requirement |
|---|---|
| `technical_demo` | scripts and manifests exist, at least one suite can be planned |
| `commercial_poc` | business dataset + at least two public/local dataset adapters are ready |
| `pilot_candidate` | RAG, LLaVA-data validation, and YOLO business train/val can run |
| `production_candidate` | public dataset metrics, model accuracy metrics, and training evidence are recorded |

## Minimum Gate for the Current Repository

```bash
python scripts/download_and_prepare_public_datasets.py \
  --datasets docvqa infographicvqa llava_cot \
  --output data/public_eval \
  --max-samples 128

PYTHONPATH=. python scripts/run_public_dataset_train_test.py \
  --repo-root . \
  --suite rag llava yolo_business mvtec

python scripts/evaluate_public_dataset_suite.py --repo-root . --min-score 0.65
```

## GPU Gate

When YOLO weights and a GPU environment are available:

```bash
PYTHONPATH=. python scripts/run_public_dataset_train_test.py \
  --repo-root . \
  --suite yolo_business \
  --model weights/yolov8n.pt \
  --execute
```

## Large-Scale Training Gate

When the real LLaVA training script is connected:

```bash
TRAIN_SCRIPT=/path/to/llava/train.py \
MODEL_PATH=/mnt/PRO6000_disk/models/Qwen \
DATA_PATH=data/public_eval/llava_cot_sample/llava_train_sample.jsonl \
IMAGE_FOLDER=/mnt/PRO6000_disk/data \
OUTPUT_DIR=outputs/llava_public_smoke \
CUDA_VISIBLE_DEVICES=0,1,2,3 \
bash experiments/llava_lora_docvqa/train.sh
```

After training, collect evidence:

```bash
python scripts/collect_training_evidence.py \
  --experiment llava_lora_docvqa \
  --config experiments/llava_lora_docvqa/config.yaml \
  --metrics experiments/llava_lora_docvqa/results/metrics.json \
  --log experiments/llava_lora_docvqa/logs/train_public_smoke.log
```
