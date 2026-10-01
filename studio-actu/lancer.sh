#!/usr/bin/env bash
# ./lancer.sh 2026-10-02  → rend jours/<date>.json dans sorties/<date>/ + planches de contrôle
set -e; cd "$(dirname "$0")"; J=${1:-$(TZ=Europe/Paris date +%F)}
export CHROME=${CHROME:-$(ls -d /opt/pw-browsers/chromium-*/chrome-linux/chrome 2>/dev/null | head -1)}
python3 fabrique.py jours/$J.json --out sorties/$J --workers ${KX_WORKERS:-3}
for f in sorties/$J/*.mp4; do ffmpeg -v error -y -i "$f" -vf "fps=1/2.5,scale=180:320,tile=6x2" -frames:v 1 "${f%.mp4}.planche.png"; done
ffmpeg -v error -y $(for f in sorties/$J/*.planche.png; do echo -i $f; done) -filter_complex "vstack=inputs=$(ls sorties/$J/*.planche.png|wc -l)" sorties/$J/controle.png
python3 planifier.py jours/$J.json sorties/$J
echo "OK $J"; cat sorties/$J/$J-manifeste.json
