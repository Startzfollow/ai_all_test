#!/usr/bin/env bash
set -euo pipefail

CI_MODE="${1:-}"
FAILED=0

check_absent() {
  local pattern="$1"
  local message="$2"
  if find . -path "$pattern" -print -quit | grep -q .; then
    echo "[FAIL] $message"
    find . -path "$pattern" | head -20
    FAILED=1
  else
    echo "[ OK ] $message"
  fi
}

check_glob_absent() {
  local pattern="$1"
  local message="$2"
  if find . -name "$pattern" -print -quit | grep -q .; then
    echo "[FAIL] $message"
    find . -name "$pattern" | head -20
    FAILED=1
  else
    echo "[ OK ] $message"
  fi
}

echo "== Repository hygiene check =="
check_glob_absent "__pycache__" "No Python __pycache__ directories"
check_glob_absent ".pytest_cache" "No pytest cache directories"
check_glob_absent "*.zip" "No ZIP archives committed"
check_glob_absent "*.pt" "No PyTorch weight files committed"
check_glob_absent "*.onnx" "No ONNX files committed"
check_glob_absent "*.engine" "No TensorRT engine files committed"

if [[ ! -f README.md ]]; then
  echo "[FAIL] README.md missing"
  FAILED=1
fi

if [[ ! -f QUICKSTART.md ]]; then
  echo "[FAIL] QUICKSTART.md missing"
  FAILED=1
fi

if [[ "$FAILED" -ne 0 ]]; then
  echo "Repository hygiene check failed. Clean generated files or untrack large model artifacts."
  exit 1
fi

echo "All repository hygiene checks passed."
