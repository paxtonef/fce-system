#!/usr/bin/env bash
set -euo pipefail
ROOT="$(dirname "$0")"
cd "$ROOT"
cleanup() { echo ""; echo "🛑 Stopping FCE..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit 0; }
trap cleanup INT TERM EXIT

cd "$ROOT/api"
export PYTHONPATH="$HOME/Desktop/fce-system/engine/src:$PYTHONPATH"
nohup ~/Desktop/fce-system/engine/.venv/bin/python -m uvicorn app.main:app --reload > /tmp/fce-backend.log 2>&1 &
BACKEND_PID=$!

cd "$ROOT/fce-web"
nohup python3 -m http.server 8765 > /tmp/fce-frontend.log 2>&1 &
FRONTEND_PID=$!

cd "$ROOT"
sleep 2
echo "✅ Backend  → http://localhost:8000  (PID: $BACKEND_PID)"
echo "✅ Frontend → http://localhost:8765  (PID: $FRONTEND_PID)"
open "http://localhost:8765" 2>/dev/null || echo "🌐 Open http://localhost:8765"
echo ""
echo "📋 Logs: tail -f /tmp/fce-backend.log /tmp/fce-frontend.log"
echo "Press Ctrl+C to stop"
wait
