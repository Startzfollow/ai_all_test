#!/usr/bin/env bash
set -euo pipefail

# Evaluation launcher placeholder for local LLaVA/VQA evaluation.
# Keep it evidence-driven: write measured results to results/metrics.json and examples.jsonl.

MODEL_PATH="${MODEL_PATH:-/mnt/PRO6000_disk/models/Qwen}"
ADAPTER_PATH="${ADAPTER_PATH:-outputs/llava_lora_docvqa}"
EVAL_DATA="${EVAL_DATA:-data/processed/llava_cot_1k.jsonl}"
IMAGE_FOLDER="${IMAGE_FOLDER:-/mnt/PRO6000_disk/data}"
EVAL_SCRIPT="${EVAL_SCRIPT:-scripts/eval_llava_vqa.py}"
RESULTS_DIR="experiments/llava_lora_docvqa/results"

mkdir -p "${RESULTS_DIR}"

if [[ ! -f "${EVAL_SCRIPT}" ]]; then
  echo "[WARN] Evaluation entrypoint not found: ${EVAL_SCRIPT}"
  echo "Create or point EVAL_SCRIPT to your actual VQA evaluation script."
  echo "The repository keeps metrics.json as a template until measured values are available."
  exit 0
fi

python "${EVAL_SCRIPT}" \
  --model_name_or_path "${MODEL_PATH}" \
  --adapter_path "${ADAPTER_PATH}" \
  --eval_data "${EVAL_DATA}" \
  --image_folder "${IMAGE_FOLDER}" \
  --metrics_output "${RESULTS_DIR}/metrics.json" \
  --examples_output "${RESULTS_DIR}/examples.jsonl"
