# Repository Flatten Guide

## Why flatten

The current local tree may look like this:

```text
repo-root/
├── AGENTS.md
├── ai-fullstack-multimodal-agent-suite/
├── ai-fullstack-multimodal-agent-suite-mini-demo.zip
└── output/
```

For GitHub review, the project files should sit directly at repository root:

```text
repo-root/
├── backend/
├── frontend/
├── configs/
├── docs/
├── scripts/
├── README.md
└── pyproject.toml
```

This avoids the impression that the repository is just a temporary extracted package.

## Safe command

Run from the outer Git repository root:

```bash
bash ai-fullstack-multimodal-agent-suite/scripts/flatten_repository.sh ai-fullstack-multimodal-agent-suite
git status --short
git add .
git commit -m "chore: flatten repository structure"
git push
```

If the root already has `README.md`, `backend/`, or `frontend/`, the script stops to avoid overwriting files.

## Cleanup after flatten

```bash
make clean
git rm --cached -r '**/__pycache__' .pytest_cache 2>/dev/null || true
git rm --cached weights/*.pt weights/*.onnx weights/*.engine 2>/dev/null || true
git status --short
```
