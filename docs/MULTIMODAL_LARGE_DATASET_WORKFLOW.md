# Multimodal Large Dataset Workflow

This document explains how to use DocVQA, InfographicVQA, and LLaVA-CoT style data for larger training/testing runs.

## Local datasets

Expected local roots:

```text
/mnt/PRO6000_disk/data/DocVQA
/mnt/PRO6000_disk/data/InfographicVQA
/mnt/PRO6000_disk/data/LLaVA-CoT-100k
```

## Prepare normalized samples

```bash
python scripts/prepare_large_multimodal_samples.py \
  --output data/public_eval_large \
  --docvqa-root /mnt/PRO6000_disk/data/DocVQA \
  --infographicvqa-root /mnt/PRO6000_disk/data/InfographicVQA \
  --llava-root /mnt/PRO6000_disk/data/LLaVA-CoT-100k \
  --limit 5000
```

Generated files:

```text
data/public_eval_large/
├── docvqa_sample.jsonl
├── infographicvqa_sample.jsonl
├── llava_cot_sample.jsonl
├── multimodal_combined_sample.jsonl
└── manifest.json
```

## Connect to LLaVA LoRA training

Use the generated `llava_cot_sample.jsonl` or combined sample as the data path:

```bash
TRAIN_SCRIPT=/path/to/llava/train.py \
MODEL_PATH=/mnt/PRO6000_disk/models/Qwen \
DATA_PATH=data/public_eval_large/llava_cot_sample.jsonl \
IMAGE_FOLDER=/mnt/PRO6000_disk/data \
OUTPUT_DIR=outputs/llava_large_smoke \
CUDA_VISIBLE_DEVICES=0,1,2,3 \
bash experiments/llava_lora_docvqa/train.sh
```

## Evaluation advice

Use separate subsets:

- train subset for LoRA fitting
- validation subset for early stopping and prompt checking
- test subset for reporting

Track:

- exact match / keyword match
- ANLS for document VQA
- sample-level error cases
- base vs LoRA comparison
