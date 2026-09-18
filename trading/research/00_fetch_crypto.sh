#!/usr/bin/env bash
# Recupere l'OHLCV journalier des 10 actifs crypto depuis Speirsy11/crypto-dataset,
# reconstruit depuis les donnees publiques 1 minute de Binance.
#
# Les fichiers y sont stockes en Git LFS : un clone ordinaire ne rapporte que
# des pointeurs. On passe donc par media.githubusercontent.com, qui sert le
# contenu reel.
set -euo pipefail

REPO="Speirsy11/crypto-dataset"
TMP="${CRYPTO_TMP:-/tmp/cds}"
OUT="${CRYPTO_OUT:-/tmp/cdl}"
mkdir -p "$OUT"

echo "Arborescence du depot (pointeurs LFS seulement, ~5 Mo)"
rm -rf "$TMP"
git clone --depth 1 --filter=blob:none --sparse -q "https://github.com/$REPO.git" "$TMP"
git -C "$TMP" sparse-checkout set "data/interval_id=1d" metadata

echo "Telechargement du contenu reel des fichiers journaliers"
( cd "$TMP" && find data -name "*.parquet" ) \
  | sed "s|^|https://media.githubusercontent.com/media/$REPO/main/|" > /tmp/lfs_urls.txt
echo "  $(wc -l < /tmp/lfs_urls.txt) fichiers"
xargs -P 12 -I{} bash -c 'u="{}"; n="${u##*/}"; curl -sfL "$u" -o "'"$OUT"'/$n"' < /tmp/lfs_urls.txt

ok=0; bad=0
for f in "$OUT"/*.parquet; do
  if [ "$(head -c 4 "$f")" = "PAR1" ]; then ok=$((ok+1)); else bad=$((bad+1)); rm -f "$f"; fi
done
echo "  $ok fichiers parquet valides, $bad rejetes"
echo
echo "Etape suivante : python3 16_classement_crypto.py"
