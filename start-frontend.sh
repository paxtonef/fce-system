#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/fce-web"
echo "🌐 FCE Frontend → http://localhost:8765"
python3 -m http.server 8765
