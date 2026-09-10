#!/usr/bin/env bash
set -euo pipefail

# Simulate local-only PR workflow:
# 1. Run local scan (no backend required)
# 2. Create a branch with suggested changes
# 3. Show diff and branch name for a manual PR

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

echo "Running local scan..."
python3 scripts/local_scan.py

echo "Applying suggestions and creating branch..."
python3 scripts/apply_suggestions.py

echo "Branch list (local):"
git branch --show-current || true

echo "Recent commits (top 5):"
git --no-pager log --oneline -n 5 || true

echo "Show diff of current branch against main (if main exists locally):"
if git rev-parse --verify main >/dev/null 2>&1; then
  git --no-pager diff --name-only main...HEAD || true
else
  echo "No local main branch to compare against; show git status instead"
  git status --porcelain || true
fi

echo "Done. Create a PR from the created branch to main to see suggestions in the PR UI."
