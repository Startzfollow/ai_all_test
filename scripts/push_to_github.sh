#!/usr/bin/env bash
set -euo pipefail
REPO_NAME=${1:-ai-fullstack-multimodal-agent-suite}
VISIBILITY=${VISIBILITY:-public}

git init
if ! git config user.email >/dev/null; then
  git config user.email "you@example.com"
fi
if ! git config user.name >/dev/null; then
  git config user.name "Your Name"
fi

git add .
git commit -m "init: ai fullstack multimodal agent suite" || true

if command -v gh >/dev/null 2>&1; then
  gh repo create "$REPO_NAME" --"$VISIBILITY" --source=. --remote=origin --push
else
  echo "GitHub CLI not found. Create a repo on GitHub, then run:"
  echo "git remote add origin https://github.com/<your-name>/$REPO_NAME.git"
  echo "git branch -M main"
  echo "git push -u origin main"
fi
