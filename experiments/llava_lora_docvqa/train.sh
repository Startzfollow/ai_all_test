#!/usr/bin/env bash
set -euo pipefail

# LLaVA-style multi-GPU LoRA/QLoRA training launcher.
# This script intentionally keeps paths overrideable so it can run on different machines.

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1,2,3}"
export TOKENIZERS_PARALLELISM="${TOKENIZERS_PARALLELISM:-false}"
export WANDB_PROJECT="${WANDB_PROJECT:-ai-fullstack-llava-training}"

MODEL_PATH="${MODEL_PATH:-/mnt/PRO6000_disk/models/Qwen}"
DATA_PATH="${DATA_PATH:-data/processed/llava_cot_1k.jsonl}"
IMAGE_FOLDER="${IMAGE_FOLDER:-/mnt/PRO6000_disk/data}"
OUTPUT_DIR="${OUTPUT_DIR:-outputs/llava_lora_docvqa}"
TRAIN_SCRIPT="${TRAIN_SCRIPT:-scripts/train_llava_lora.py}"
DEEPSPEED_CONFIG="${DEEPSPEED_CONFIG:-configs/zero2.json}"
NPROC_PER_NODE="${NPROC_PER_NODE:-4}"
MASTER_PORT="${MASTER_PORT:-29501}"

mkdir -p "${OUTPUT_DIR}" experiments/llava_lora_docvqa/logs

if [[ ! -f "${DATA_PATH}" ]]; then
  echo "[ERROR] DATA_PATH does not exist: ${DATA_PATH}"
  echo "Create it first, for example:"
  echo "python scripts/prepare_llava_training_subset.py --input /mnt/PRO6000_disk/data/LLaVA-CoT-100k --output ${DATA_PATH} --limit 1000 --shuffle"
  exit 2
fi

if [[ ! -f "${TRAIN_SCRIPT}" ]]; then
  echo "[ERROR] Training entrypoint not found: ${TRAIN_SCRIPT}"
  echo "Set TRAIN_SCRIPT to your actual LLaVA training Python file."
  echo "Example: TRAIN_SCRIPT=/path/to/llava/train/train_mem.py bash experiments/llava_lora_docvqa/train.sh"
  exit 2
fi

LOG_FILE="experiments/llava_lora_docvqa/logs/train_$(date +%Y%m%d_%H%M%S).log"

echo "[INFO] Starting LLaVA-style training"
echo "[INFO] MODEL_PATH=${MODEL_PATH}"
echo "[INFO] DATA_PATH=${DATA_PATH}"
echo "[INFO] IMAGE_FOLDER=${IMAGE_FOLDER}"
echo "[INFO] OUTPUT_DIR=${OUTPUT_DIR}"
echo "[INFO] TRAIN_SCRIPT=${TRAIN_SCRIPT}"
echo "[INFO] Log: ${LOG_FILE}"

torchrun \
  --nproc_per_node="${NPROC_PER_NODE}" \
  --master_port="${MASTER_PORT}" \
  "${TRAIN_SCRIPT}" \
  --model_name_or_path "${MODEL_PATH}" \
  --data_path "${DATA_PATH}" \
  --image_folder "${IMAGE_FOLDER}" \
  --output_dir "${OUTPUT_DIR}" \
  --num_train_epochs "${NUM_TRAIN_EPOCHS:-1}" \
  --per_device_train_batch_size "${PER_DEVICE_TRAIN_BATCH_SIZE:-2}" \
  --gradient_accumulation_steps "${GRADIENT_ACCUMULATION_STEPS:-8}" \
  --learning_rate "${LEARNING_RATE:-2e-5}" \
  --weight_decay "${WEIGHT_DECAY:-0.0}" \
  --warmup_ratio "${WARMUP_RATIO:-0.03}" \
  --lr_scheduler_type "${LR_SCHEDULER_TYPE:-cosine}" \
  --logging_steps "${LOGGING_STEPS:-10}" \
  --save_steps "${SAVE_STEPS:-500}" \
  --save_total_limit "${SAVE_TOTAL_LIMIT:-3}" \
  --bf16 "${BF16:-true}" \
  --gradient_checkpointing "${GRADIENT_CHECKPOINTING:-true}" \
  --deepspeed "${DEEPSPEED_CONFIG}" \
  --lora_enable "${LORA_ENABLE:-true}" \
  --lora_r "${LORA_R:-64}" \
  --lora_alpha "${LORA_ALPHA:-128}" \
  2>&1 | tee "${LOG_FILE}"

echo "[INFO] Training finished. Collect evidence next:"
echo "python scripts/collect_training_evidence.py --experiment llava_lora_docvqa --config experiments/llava_lora_docvqa/config.yaml --metrics experiments/llava_lora_docvqa/results/metrics.json --log ${LOG_FILE}"
