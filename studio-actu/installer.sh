#!/usr/bin/env bash
# Prépare un conteneur neuf (≈1 min). Idempotent.
set -e; cd "$(dirname "$0")"
command -v ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg >/dev/null)
python3 -c "import piper, numpy, scipy" 2>/dev/null || pip install -q --break-system-packages piper-tts onnxruntime numpy scipy
[ -d node_modules/playwright ] || PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i --silent --no-audit --no-fund
command -v postiz >/dev/null || npm i -g --silent postiz >/dev/null 2>&1 || true
CH=$(ls -d /opt/pw-browsers/chromium-*/chrome-linux/chrome 2>/dev/null | head -1); echo "CHROME=$CH"
