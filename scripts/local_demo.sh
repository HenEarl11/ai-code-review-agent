#!/usr/bin/env bash
# local_demo.sh - build/run backend in Docker, run scan against test repo, then stop container

set -euo pipefail

BACKEND_IMAGE=${BACKEND_IMAGE:-ai-review-backend}
BACKEND_PORT=${BACKEND_PORT:-5001}
OLLAMA_URL=${AICR_OLLAMA_URL:-http://host.docker.internal:11434}
OLLAMA_MODEL=${AICR_OLLAMA_MODEL:-mistral}
SCAN_TARGET=${1:-test_repos/python-test-repo}

echo "Building backend image ($BACKEND_IMAGE)"
docker build -t "$BACKEND_IMAGE" ./backend

echo "Starting backend container"
docker rm -f ai-review-backend >/dev/null 2>&1 || true
docker run -d --name ai-review-backend -p ${BACKEND_PORT}:5000 \
  -e AICR_OLLAMA_URL="$OLLAMA_URL" -e AICR_OLLAMA_MODEL="$OLLAMA_MODEL" \
  "$BACKEND_IMAGE"

echo "Waiting for backend health on http://localhost:${BACKEND_PORT}/api/health"
for i in {1..30}; do
  if curl -sSf "http://localhost:${BACKEND_PORT}/api/health" >/dev/null 2>&1; then
    echo "Backend healthy"
    break
  fi
  sleep 2
done

echo "Running scan for $SCAN_TARGET"
chmod +x scripts/scan_repo.sh
./scripts/scan_repo.sh "$SCAN_TARGET" main "http://localhost:${BACKEND_PORT}"

echo "Stopping backend container"
docker rm -f ai-review-backend || true

echo "Demo complete. Results in scan_results/"
