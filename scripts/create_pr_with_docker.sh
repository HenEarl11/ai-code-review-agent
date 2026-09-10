#!/usr/bin/env bash
set -euo pipefail

# Usage:
# Ensure you are authenticated with GitHub CLI: `gh auth login`
# Then run: ./scripts/create_pr_with_docker.sh [base_branch]

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
BASE=${1:-main}

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found. Install GitHub CLI and authenticate (gh auth login)."
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "gh not authenticated. Run: gh auth login"
  exit 1
fi

cd "$ROOT"

echo "Running scanner and applying suggestions inside local docker image..."
docker run --rm -v "$ROOT":/app -w /app ai-review-backend:test bash -lc "python3 scripts/local_scan.py && python3 scripts/apply_suggestions.py"

branch=$(git branch --show-current)
if [ -z "$branch" ]; then
  echo "No branch detected after suggestions. Exiting."
  exit 1
fi

echo "Pushing branch $branch to origin..."
git push --set-upstream origin "$branch"

echo "Creating draft PR via gh..."
gh pr create --title "AI suggested fixes (${branch})" --body "Automated AI suggestions from local run. Please review before merging." --base "$BASE" --head "$branch" --draft

echo "Done."
