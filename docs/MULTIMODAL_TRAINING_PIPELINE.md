# Multimodal Training Pipeline

This project supports a reproducible LLaVA-style multimodal training workflow. The goal is to keep a clear chain from data preparation to training, evaluation, evidence collection, and fullstack demo integration.

## Pipeline Overview

```text
Raw multimodal datasets
        |
        v
LLaVA-style JSON / JSONL conversion
        |
        v
Dataset validation and small-sample smoke test
        |
        v
LoRA / QLoRA / optional full-parameter training
        |
        v
Evaluation on VQA-style prompts
        |
        v
Training evidence collection
        |
        v
FastAPI inference endpoint and React demo integration
```

## Stage 1: Dataset Preparation

Use a small subset first:

```bash
python scripts/prepare_llava_training_subset.py \
  --input /mnt/PRO6000_disk/data/LLaVA-CoT-100k \
  --output data/processed/llava_cot_1k.jsonl \
  --limit 1000 \
  --shuffle \
  --seed 42
```

Then validate the output format:

```bash
python scripts/validate_llava_dataset.py \
  --input data/processed/llava_cot_1k.jsonl \
  --max-errors 20
```

## Stage 2: Smoke Test Training

Run a small experiment first to verify:

- model path is correct
- image path resolution is correct
- distributed training can start
- loss is finite
- checkpoints can be saved
- LoRA adapter can be loaded for inference

```bash
bash experiments/llava_lora_docvqa/train.sh
```

## Stage 3: Larger Training

After the smoke test succeeds, increase the dataset size:

```bash
python scripts/prepare_llava_training_subset.py \
  --input /mnt/PRO6000_disk/data/LLaVA-CoT-100k \
  --output data/processed/llava_cot_30k.jsonl \
  --limit 30000 \
  --shuffle \
  --seed 42
```

Then update `experiments/llava_lora_docvqa/config.yaml` and rerun training.

## Stage 4: Evaluation and Evidence

After training, update:

```text
experiments/llava_lora_docvqa/results/metrics.json
experiments/llava_lora_docvqa/results/examples.jsonl
```

Then collect evidence:

```bash
python scripts/collect_training_evidence.py \
  --experiment llava_lora_docvqa \
  --config experiments/llava_lora_docvqa/config.yaml \
  --metrics experiments/llava_lora_docvqa/results/metrics.json
```

Finally render a human-readable report:

```bash
python scripts/render_training_report.py \
  --experiment-dir experiments/llava_lora_docvqa \
  --output docs/EXPERIMENT_RESULTS.md
```

## Key Principle

Do not commit model checkpoints, raw private datasets, or generated large files to Git. Commit only configuration, scripts, logs, small examples, metrics, and reports.
