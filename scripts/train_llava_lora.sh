#!/usr/bin/env bash
set -euo pipefail

# This script is a portable training entry template.
# Choose one of the following training backends:
# 1) LLaVA official training code
# 2) LLaMA-Factory with VLM support
# 3) Custom Transformers + PEFT training script

CONFIG=${CONFIG:-configs/llava_lora.yaml}
TRAIN_FILE=${TRAIN_FILE:-data/processed/llava_cot_train.jsonl}
MODEL_PATH=${MODEL_PATH:-/mnt/PRO6000_disk/models/Qwen}
OUTPUT_DIR=${OUTPUT_DIR:-outputs/llava_lora}
GPUS=${GPUS:-0,1,2,3}

mkdir -p "$OUTPUT_DIR"

echo "Using config: $CONFIG"
echo "MODEL_PATH=$MODEL_PATH"
echo "TRAIN_FILE=$TRAIN_FILE"
echo "OUTPUT_DIR=$OUTPUT_DIR"
echo "GPUS=$GPUS"

# Recommended flow:
# python scripts/prepare_llava_cot_data.py --input /mnt/PRO6000_disk/data/LLaVA-CoT-100k --output "$TRAIN_FILE"

# Placeholder command for LLaVA official repo style. Replace /path/to/LLaVA with your local clone if available.
# CUDA_VISIBLE_DEVICES=$GPUS deepspeed /path/to/LLaVA/llava/train/train_mem.py \
#   --model_name_or_path "$MODEL_PATH" \
#   --data_path "$TRAIN_FILE" \
#   --image_folder /mnt/PRO6000_disk/data/LLaVA-CoT-100k \
#   --lora_enable True \
#   --lora_r 16 \
#   --lora_alpha 32 \
#   --bf16 True \
#   --output_dir "$OUTPUT_DIR" \
#   --num_train_epochs 1 \
#   --per_device_train_batch_size 1 \
#   --gradient_accumulation_steps 8 \
#   --gradient_checkpointing True \
#   --deepspeed configs/zero2.json

cat <<'MSG'
Training command template generated successfully.
Next steps:
1. Confirm your local VLM base model path in configs/llava_lora.yaml.
2. Confirm the actual LLaVA/LLaMA-Factory training backend installed on this machine.
3. Uncomment and adapt the deepspeed/accelerate command in scripts/train_llava_lora.sh.
MSG
