#!/usr/bin/env bash
# Prépare un conteneur neuf (≈1 min). Idempotent.
set -e; cd "$(dirname "$0")"
command -v ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg >/dev/null)
python3 -c "import piper, numpy, scipy" 2>/dev/null || pip install -q --break-system-packages piper-tts onnxruntime numpy scipy
[ -d node_modules/playwright ] || PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm i --silent --no-audit --no-fund
# Voix Chatterbox (CPU) + Whisper de contrôle — ~2 min, modèles ~3 Go téléchargés au 1er usage
[ "${KX_MOTEUR:-edge}" != cb ] || [ -x ~/.korvex-cb/bin/python ] || (python3 -m venv ~/.korvex-cb && ~/.korvex-cb/bin/pip install -q torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu && ~/.korvex-cb/bin/pip install -q chatterbox-tts) || echo "⚠ Chatterbox indisponible : repli Piper"
python3 -c "import edge_tts" 2>/dev/null || pip install -q --break-system-packages edge-tts
[ "${KX_MOTEUR:-edge}" != cb ] || python3 -c "import faster_whisper" 2>/dev/null || pip install -q --break-system-packages faster-whisper
command -v postiz >/dev/null || npm i -g --silent postiz >/dev/null 2>&1 || true
CH=$(ls -d /opt/pw-browsers/chromium-*/chrome-linux/chrome 2>/dev/null | head -1); echo "CHROME=$CH"
