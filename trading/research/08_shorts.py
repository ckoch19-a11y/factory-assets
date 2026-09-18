"""Le cote short echoue avec la gestion commune. Question : est-ce que
l'edge directionnel mis en evidence par l'etude d'evenements (P8) est
recuperable avec une gestion PROPRE au short, ou pas du tout ?

Meme protocole : selection in-sample uniquement, validation OOS + BTC.
"""
from __future__ import annotations

import itertools
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
BASE = {
    "SPX": panel[(panel["symbol"] == "SPX") & (panel["date"] >= "1962-01-01")],
    "US500": panel[panel["asset_class"] == "equity_single"],
    "BTC": panel[panel["symbol"] == "BTCUSD"],
}
FEAT = {k: F.build_panel_features(v, 400)[
    ["symbol", "date", "open", "high", "low", "close", "atr14"]] for k, v in BASE.items()}

EXITS = {
    "objectif_1.5R": dict(exit_on_mean=False, target_r=1.5, trail_atr=0.0, max_bars=20),
    "objectif_2R":   dict(exit_on_mean=False, target_r=2.0, trail_atr=0.0, max_bars=20),
    "temps_5":       dict(exit_on_mean=False, target_r=0.0, trail_atr=0.0, max_bars=5),
    "temps_10":      dict(exit_on_mean=False, target_r=0.0, trail_atr=0.0, max_bars=10),
    "trailing_2ATR": dict(exit_on_mean=False, target_r=0.0, trail_atr=2.0, max_bars=40),
    "retour_moyenne": dict(exit_on_mean=True, target_r=0.0, trail_atr=0.0, max_bars=15),
}
STOPS = (2.0, 3.0, 4.0)
CONFIRM = (True, False)

CACHE = {}
def shorts_only(uni, kw):
    key = (uni, tuple(sorted((k, str(v)) for k, v in kw.items())))
    if key not in CACHE:
        fee = 10.0 if uni == "BTC" else 5.0
        t = B.run_panel(FEAT[uni], B.Config(fee_bps=fee, slip_bps=fee, **kw))
        CACHE[key] = t[t["side"] == "short"] if len(t) else t
    return CACHE[key]

def window(t, split):
    _, a, b = SPLITS[split]
    if not len(t):
        return t
    return t[(t["date_entree"] >= pd.Timestamp(a)) & (t["date_entree"] <= pd.Timestamp(b))]

rows = []
grid = list(itertools.product(EXITS.items(), STOPS, CONFIRM))
print(f"{len(grid)} configurations short evaluees...")
for (ename, ecfg), stop, conf in grid:
    kw = dict(stop_atr=stop, confirm=conf, allow_short=True, **ecfg)
    r = {"sortie": ename, "stop_atr": stop, "confirmation": conf}
    for split, (uni, a, b) in SPLITS.items():
        t = window(shorts_only(uni, kw), split)
        st = B.trade_stats(t)
        r[f"{split}_n"] = st.get("n_trades", 0)
        r[f"{split}_wr"] = st.get("win_rate_pct")
        r[f"{split}_espR"] = st.get("esperance_R")
    rows.append(r)
    print(".", end="", flush=True)

out = pd.DataFrame(rows)
out.to_csv(os.path.join(RESULTS, "11_shorts_grid.csv"), index=False)

isc = ["SPX_IS_espR", "US500_IS_espR"]
out["IS_min"] = out[isc].min(axis=1)
valid = out[(out["SPX_IS_n"] >= 40) & (out["US500_IS_n"] >= 200) & (out["IS_min"] > 0)]
pd.set_option("display.width", 240)
print(f"\n\n{len(valid)}/{len(out)} configurations short positives sur les DEUX univers in-sample")
if len(valid):
    v = valid.sort_values("IS_min", ascending=False)
    cols = ["sortie", "stop_atr", "confirmation", "SPX_IS_espR", "US500_IS_espR",
            "SPX_OOS_espR", "SPX_OOS_n", "US500_OOS_espR", "US500_OOS_n",
            "BTC_ALL_espR", "BTC_ALL_n"]
    print(v[cols].head(10).to_string(index=False))
    oosc = ["SPX_OOS_espR", "US500_OOS_espR", "BTC_ALL_espR"]
    v2 = v.dropna(subset=oosc)
    if len(v2):
        print(f"\nParmi elles, positives sur les 3 tests hors echantillon : "
              f"{int((v2[oosc] > 0).all(axis=1).sum())}/{len(v2)}")
else:
    print("AUCUNE configuration short n'est positive sur les deux univers in-sample.")

print("\n### Meilleures configurations short toutes periodes confondues (diagnostic) ###")
allc = ["SPX_IS_espR", "SPX_OOS_espR", "US500_IS_espR", "US500_OOS_espR", "BTC_ALL_espR"]
out["moy_toutes"] = out[allc].mean(axis=1)
out["n_positifs_sur_5"] = (out[allc] > 0).sum(axis=1)
print(out.sort_values("moy_toutes", ascending=False)[
    ["sortie", "stop_atr", "confirmation"] + allc + ["n_positifs_sur_5"]].head(8).to_string(index=False))

with open(os.path.join(RESULTS, "11_shorts_meta.json"), "w") as fh:
    json.dump({"n_configs": len(grid),
               "n_valides_IS": int(len(valid))}, fh, indent=2)
