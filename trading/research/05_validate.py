"""Validation hors echantillon des meilleures configurations in-sample.

On evalue DEUX classements in-sample (meilleure esperance mediane et
meilleure esperance minimale) pour ne pas choisir apres coup celui qui
arrange. Les deux sont reportes.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import data as D, features as F, stats as S, backtest as B  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
panel = pd.read_parquet(os.path.join(D.OUT, "panel_daily.parquet"))

SPLITS = {
    "SPX_IS":    ("SPX",   "1962-01-01", "1999-12-31"),
    "SPX_OOS":   ("SPX",   "2000-01-01", "2018-12-31"),
    "US500_IS":  ("US500", "2013-02-08", "2015-12-31"),
    "US500_OOS": ("US500", "2016-01-01", "2018-02-07"),
    "BTC_ALL":   ("BTC",   "2012-01-01", "2026-12-31"),
}
EXIT_SCHEMES = {
    "retour_moyenne":        dict(exit_on_mean=True,  target_r=0.0, trail_atr=0.0, max_bars=20),
    "retour_moyenne_ou_2R":  dict(exit_on_mean=True,  target_r=2.0, trail_atr=0.0, max_bars=20),
    "objectif_2R":           dict(exit_on_mean=False, target_r=2.0, trail_atr=0.0, max_bars=20),
    "trailing_2ATR":         dict(exit_on_mean=False, target_r=0.0, trail_atr=2.0, max_bars=40),
    "temps_10_barres":       dict(exit_on_mean=False, target_r=0.0, trail_atr=0.0, max_bars=10),
}

BASE = {
    "SPX": panel[(panel["symbol"] == "SPX") & (panel["date"] >= "1962-01-01")],
    "US500": panel[panel["asset_class"] == "equity_single"],
    "BTC": panel[panel["symbol"] == "BTCUSD"],
}
FEAT = {k: F.build_panel_features(v, 400)[
    ["symbol", "date", "open", "high", "low", "close", "atr14"]] for k, v in BASE.items()}


def evaluate(cfg_kw: dict, split: str) -> tuple[dict, pd.DataFrame]:
    uni, a, b = SPLITS[split]
    f = FEAT[uni]
    f = f[f["date"] <= b]
    t = B.run_panel(f, B.Config(**cfg_kw))
    if len(t):
        t = t[(t["date_entree"] >= pd.Timestamp(a)) & (t["date_entree"] <= pd.Timestamp(b))]
    return B.trade_stats(t), t


sel = pd.read_csv(os.path.join(RESULTS, "03_selection_IS.csv"))
esp = [c for c in sel.columns if c.endswith("_esperance_R") and "_IS_" in c]
sel["esp_min"] = sel[esp].min(axis=1)
sel["esp_med"] = sel[esp].median(axis=1)
cand = sel[sel["valide"] & (sel["esp_min"] > 0)]

top_med = cand.sort_values("esp_med", ascending=False).head(5)
top_min = cand.sort_values("esp_min", ascending=False).head(5)
picks = pd.concat([top_med.assign(classement="mediane"),
                   top_min.assign(classement="minimum")]).drop_duplicates(
    subset=["sortie", "stop_atr", "confirmation"])

rows = []
for _, r in picks.iterrows():
    kw = dict(stop_atr=float(r["stop_atr"]), confirm=bool(r["confirmation"]),
              **EXIT_SCHEMES[r["sortie"]])
    line = {"sortie": r["sortie"], "stop_atr": r["stop_atr"],
            "confirmation": bool(r["confirmation"]), "classement_IS": r["classement"]}
    for split in ("SPX_IS", "SPX_OOS", "US500_IS", "US500_OOS", "BTC_ALL"):
        st, _ = evaluate(kw, split)
        line[f"{split}_n"] = st.get("n_trades", 0)
        line[f"{split}_wr"] = st.get("win_rate_pct")
        line[f"{split}_espR"] = st.get("esperance_R")
        line[f"{split}_pf"] = st.get("profit_factor")
        line[f"{split}_t"] = st.get("t_stat_R")
    oos = [line["SPX_OOS_espR"], line["US500_OOS_espR"], line["BTC_ALL_espR"]]
    line["oos_min_espR"] = min([x for x in oos if x is not None], default=None)
    line["oos_moy_espR"] = float(np.mean([x for x in oos if x is not None]))
    rows.append(line)
    print(".", end="", flush=True)

out = pd.DataFrame(rows).sort_values("oos_min_espR", ascending=False)
out.to_csv(os.path.join(RESULTS, "04_validation_OOS.csv"), index=False)

pd.set_option("display.width", 260)
print("\n\n### Validation hors echantillon ###")
print("(IS = ayant servi a choisir | OOS et BTC = jamais vus lors du choix)\n")
cols = ["sortie", "stop_atr", "confirmation", "classement_IS",
        "SPX_IS_espR", "SPX_OOS_espR", "SPX_OOS_wr", "SPX_OOS_n",
        "US500_OOS_espR", "US500_OOS_wr", "US500_OOS_n",
        "BTC_ALL_espR", "BTC_ALL_wr", "BTC_ALL_n", "oos_min_espR"]
print(out[cols].to_string(index=False))
print("\n-> results/04_validation_OOS.csv")
