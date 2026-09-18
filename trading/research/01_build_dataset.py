"""Construit le panel propre a partir des sources brutes + rapport d'integrite."""
from __future__ import annotations

import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import data as D  # noqa: E402

os.makedirs(D.OUT, exist_ok=True)
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
os.makedirs(RESULTS, exist_ok=True)

LOADERS = [
    ("SPX 1950-2018 (indice, OHLCV)", lambda: D.load_sp500_long()),
    ("BTCUSD 2012-2026 (1min -> 1D, OHLCV)", lambda: D.load_btc_minute("1D")),
    ("BTCUSD 2012-2026 (1min -> 4H, OHLCV)", lambda: D.load_btc_minute("4h")),
    ("VIX 1990-2026 (OHLC)", lambda: D.load_vix()),
    ("S&P500 505 actions 2013-2018 (OHLCV)", lambda: D.load_sp500_cross()),
    ("BTC CoinMetrics 2009-2026 (close)", lambda: D.load_coinmetrics("btc")),
    ("ETH CoinMetrics 2015-2026 (close)", lambda: D.load_coinmetrics("eth")),
    ("Brent 1987-2026 (close)", lambda: D.load_brent()),
]

frames, report, failures = [], [], []
for label, fn in LOADERS:
    try:
        df = fn()
    except Exception as exc:  # source manquante -> on le dit, on n'invente rien
        failures.append({"source": label, "error": f"{type(exc).__name__}: {exc}"})
        print(f"[ECHEC ] {label}: {exc}")
        continue
    frames.append(df)
    for sym, g in df.groupby("symbol"):
        report.append({"source": label, **D.validate(g)})
    print(f"[OK    ] {label}: {len(df):,} barres, {df['symbol'].nunique()} symbole(s)")

panel = pd.concat(frames, ignore_index=True)
panel = panel.sort_values(["symbol", "date"]).reset_index(drop=True)

daily = panel[~panel["symbol"].str.contains("_4h", case=False, na=False)]
intraday = panel[panel["symbol"].str.contains("_4h", case=False, na=False)]

daily.to_parquet(os.path.join(D.OUT, "panel_daily.parquet"), index=False)
if len(intraday):
    intraday.to_parquet(os.path.join(D.OUT, "panel_4h.parquet"), index=False)

rep = pd.DataFrame(report).sort_values(["source", "symbol"])
rep.to_csv(os.path.join(RESULTS, "00_data_report.csv"), index=False)

summary = {
    "total_bars": int(len(panel)),
    "daily_bars": int(len(daily)),
    "intraday_4h_bars": int(len(intraday)),
    "symbols": int(panel["symbol"].nunique()),
    "date_min": str(panel["date"].min().date()),
    "date_max": str(panel["date"].max().date()),
    "by_asset_class": panel.groupby("asset_class")["symbol"].nunique().to_dict(),
    "bars_by_asset_class": panel.groupby("asset_class").size().to_dict(),
    "sources_failed": failures,
}
with open(os.path.join(RESULTS, "00_data_summary.json"), "w") as fh:
    json.dump(summary, fh, indent=2)

print("\n=== PANEL ===")
print(json.dumps(summary, indent=2))
print("\nSymboles avec OHLC complet :",
      int(rep["has_ohlc"].sum()), "/", len(rep))
print("Anomalies high<max(o,c) :", int(rep["bad_high"].sum()),
      "| low>min(o,c) :", int(rep["bad_low"].sum()))
