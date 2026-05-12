#!/usr/bin/env bash
set -euo pipefail

# Flatten an accidental nested repository layout:
#   repo-root/ai-fullstack-multimodal-agent-suite/<project files>
# into:
#   repo-root/<project files>
#
# Run from the outer repository root:
#   bash ai-fullstack-multimodal-agent-suite/scripts/flatten_repository.sh ai-fullstack-multimodal-agent-suite

PROJECT_DIR="${1:-ai-fullstack-multimodal-agent-suite}"

if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "Project directory not found: $PROJECT_DIR" >&2
  exit 1
fi

if [[ ! -d .git ]]; then
  echo "Run this script from the outer git repository root." >&2
  exit 1
fi

if [[ -f README.md || -d backend || -d frontend ]]; then
  echo "Root already appears to contain project files. Stop to avoid overwriting." >&2
  exit 1
fi

shopt -s dotglob nullglob
for item in "$PROJECT_DIR"/*; do
  base="$(basename "$item")"
  [[ "$base" == ".git" ]] && continue
  mv "$item" .
done
rmdir "$PROJECT_DIR"
rm -f ai-fullstack-multimodal-agent-suite-mini-demo.zip ai-fullstack-multimodal-agent-suite.zip 2>/dev/null || true
rm -rf output __pycache__ .pytest_cache 2>/dev/null || true

echo "Repository flattened. Review with: git status --short"
