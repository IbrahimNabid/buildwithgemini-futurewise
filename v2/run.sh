#!/usr/bin/env bash
set -e

# Always run from the repo root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PORT=${PORT:-8081}
export PYTHONPATH="$REPO_ROOT:$PYTHONPATH"
export DEMO_MODE="true"
export PROJECT_ID="${PROJECT_ID:-qwiklabs-gcp-04-7459370ad109}"
export GOOGLE_GENAI_USE_VERTEXAI="true"
export GOOGLE_CLOUD_PROJECT="${PROJECT_ID:-qwiklabs-gcp-04-7459370ad109}"
export GOOGLE_CLOUD_LOCATION="us-east1"

# Kill any existing process on PORT
fuser -k "${PORT}/tcp" 2>/dev/null || true
sleep 0.5

echo "Starting Futurewise v2 on http://localhost:${PORT} from $REPO_ROOT..."
exec "$REPO_ROOT/v2/backend/.venv/bin/python3" -m uvicorn v2.backend.main:app --host 0.0.0.0 --port "$PORT"
