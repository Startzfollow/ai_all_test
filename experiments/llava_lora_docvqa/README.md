# LLaVA LoRA DocVQA Experiment

This experiment demonstrates a reproducible LLaVA-style multimodal fine-tuning workflow.

## Purpose

The experiment is designed to show that the project can handle:

- multimodal instruction data preparation
- dataset validation
- LoRA / QLoRA training
- DeepSpeed multi-GPU launch
- metrics and example-output recording
- evidence collection for GitHub submission and interviews

## Preparation

Create a small training subset first:

```bash
python scripts/prepare_llava_training_subset.py \
  --input /mnt/PRO6000_disk/data/LLaVA-CoT-100k \
  --output data/processed/llava_cot_1k.jsonl \
  --limit 1000 \
  --shuffle \
  --seed 42
```

Validate it:

```bash
python scripts/validate_llava_dataset.py \
  --input data/processed/llava_cot_1k.jsonl \
  --max-errors 20
```

## Training

```bash
bash experiments/llava_lora_docvqa/train.sh
```

Override paths through environment variables:

```bash
MODEL_PATH=/mnt/PRO6000_disk/models/Qwen \
DATA_PATH=data/processed/llava_cot_1k.jsonl \
IMAGE_FOLDER=/mnt/PRO6000_disk/data \
OUTPUT_DIR=outputs/llava_lora_docvqa \
CUDA_VISIBLE_DEVICES=0,1,2,3 \
bash experiments/llava_lora_docvqa/train.sh
```

## Evaluation

```bash
bash experiments/llava_lora_docvqa/eval.sh
```

## Evidence

```bash
python scripts/collect_training_evidence.py \
  --experiment llava_lora_docvqa \
  --config experiments/llava_lora_docvqa/config.yaml \
  --metrics experiments/llava_lora_docvqa/results/metrics.json
```

## Notes

This directory should contain scripts, configs, logs, metrics, and selected examples only. Checkpoints and raw datasets should remain local.
