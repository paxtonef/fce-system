#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/api"
export PYTHONPATH="$HOME/Desktop/fce-system/engine/src:$PYTHONPATH"
echo "🚀 FCE Backend → http://localhost:8000"
~/Desktop/fce-system/engine/.venv/bin/python -m uvicorn app.main:app --reload
