#!/usr/bin/env bash
# Recupere les sources de marche utilisees par l'etude.
# Toutes sont publiques et librement accessibles. Aucune n'est redistribuee
# ici : le depot ne contient que le code et les resultats.
set -euo pipefail

RAW="${MKT_RAW:-/tmp/mkt/raw}"
mkdir -p "$RAW"
cd "$RAW"

get() { echo "  -> $2"; curl -fsSL "$1" -o "$2"; }

echo "S&P 500, journalier 1950-2018 (OHLCV)"
get "https://raw.githubusercontent.com/vijinho/sp500/master/csv/sp500.csv" sp500_long.csv

echo "500 actions du S&P 500, journalier 2013-2018 (OHLCV, ~30 Mo)"
get "https://raw.githubusercontent.com/plotly/datasets/master/all_stocks_5yr.csv" sp500_5yr.csv

echo "BTC/USD Bitstamp, 1 minute 2012-2025 (~94 Mo compresse)"
get "https://raw.githubusercontent.com/ff137/bitstamp-btcusd-minute-data/main/data/historical/btcusd_bitstamp_1min_2012-2025.csv.gz" btc_1min_hist.csv.gz

echo "BTC/USD Bitstamp, 1 minute, mise a jour courante (~50 Mo)"
get "https://raw.githubusercontent.com/ff137/bitstamp-btcusd-minute-data/main/data/updates/btcusd_bitstamp_1min_latest.csv" btc_1min_latest.csv

echo "VIX, journalier 1990-2026 (OHLC)"
get "https://raw.githubusercontent.com/datasets/finance-vix/main/data/vix-daily.csv" vix.csv

echo "CoinMetrics : BTC et ETH, cloture journaliere"
get "https://raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv" cm_btc.csv
get "https://raw.githubusercontent.com/coinmetrics/data/master/csv/eth.csv" cm_eth.csv

echo "Brent, cloture journaliere 1987-2026"
get "https://raw.githubusercontent.com/datasets/oil-prices/main/data/brent-daily.csv" brent.csv

echo
echo "Termine. $(du -sh "$RAW" | cut -f1) dans $RAW"
echo "Etape suivante : python3 01_build_dataset.py"
