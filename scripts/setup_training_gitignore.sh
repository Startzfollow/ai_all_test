#!/usr/bin/env bash
set -euo pipefail

# Append training-related ignore rules idempotently.

BLOCK_START="# --- training artifacts ---"
BLOCK_END="# --- end training artifacts ---"

if grep -q "${BLOCK_START}" .gitignore 2>/dev/null; then
  echo "[INFO] training artifact rules already exist in .gitignore"
  exit 0
fi

cat >> .gitignore <<'EOF'

# --- training artifacts ---
outputs/
checkpoints/
wandb/
runs/
*.ckpt
*.pt
*.pth
*.bin
*.safetensors
*.onnx
*.engine
*.trt
*.plan
*.log
!experiments/**/logs/.gitkeep
!experiments/**/results/*.json
!experiments/**/results/*.jsonl
!experiments/**/evidence/.gitkeep
!experiments/**/evidence/**/*.txt
!experiments/**/evidence/**/*.json
!experiments/**/evidence/**/*.yaml
# --- end training artifacts ---
EOF

echo "[INFO] appended training artifact rules to .gitignore"
