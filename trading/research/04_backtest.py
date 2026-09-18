"""Backtest + selection des parametres.

Protocole fixe AVANT de regarder le moindre resultat :

  - Selection uniquement sur SPX 1962-1999 et US500 2013-2015 (in-sample).
  - Validation sur SPX 2000-2018 et US500 2016-2018 (out-of-sample).
  - BTC 2012-2026 n'entre JAMAIS dans la selection : c'est un test
    inter-classe d'actifs, entierement hors echantillon.

Critere de selection : esperance en R positive sur les DEUX univers
in-sample, puis meilleure esperance mediane. On ne cherche pas le maximum
global (c'est le meilleur moyen de sur-ajuster), on veut de la coherence.
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
SELECTION = ["SPX_IS", "US500_IS"]

print("Preparation des features...")
BASE = {
    "SPX": panel[(panel["symbol"] == "SPX") & (panel["date"] >= "1962-01-01")],
    "US500": panel[panel["asset_class"] == "equity_single"],
    "BTC": panel[panel["symbol"] == "BTCUSD"],
}
FEAT = {}
for k, v in BASE.items():
    f = F.build_panel_features(v, 400)
    FEAT[k] = f[["symbol", "date", "open", "high", "low", "close", "atr14"]].copy()
    print(f"  {k}: {len(FEAT[k]):,} barres")


def slice_feat(split: str) -> pd.DataFrame:
    uni, a, b = SPLITS[split]
    f = FEAT[uni]
    # on garde l'historique amont necessaire au calcul des moyennes longues,
    # mais on ne comptabilise que les trades ouverts dans la fenetre
    return f[f["date"] <= b], pd.Timestamp(a), pd.Timestamp(b)


EXIT_SCHEMES = {
    "retour_moyenne":        dict(exit_on_mean=True,  target_r=0.0, trail_atr=0.0, max_bars=20),
    "retour_moyenne_ou_2R":  dict(exit_on_mean=True,  target_r=2.0, trail_atr=0.0, max_bars=20),
    "objectif_2R":           dict(exit_on_mean=False, target_r=2.0, trail_atr=0.0, max_bars=20),
    "trailing_2ATR":         dict(exit_on_mean=False, target_r=0.0, trail_atr=2.0, max_bars=40),
    "temps_10_barres":       dict(exit_on_mean=False, target_r=0.0, trail_atr=0.0, max_bars=10),
}
STOPS = (1.5, 2.0, 2.5, 3.0)
CONFIRM = (True, False)

grid = list(itertools.product(EXIT_SCHEMES.items(), STOPS, CONFIRM))
print(f"\n{len(grid)} configurations a evaluer sur {len(SELECTION)} univers in-sample")

records = []
for (ename, ecfg), stop, conf in grid:
    cfg_kw = dict(stop_atr=stop, confirm=conf, **ecfg)
    row = {"sortie": ename, "stop_atr": stop, "confirmation": conf}
    ok = True
    for split in SELECTION:
        f, a, b = slice_feat(split)
        cfg = B.Config(**cfg_kw)
        t = B.run_panel(f, cfg)
        t = t[(t["date_entree"] >= a) & (t["date_entree"] <= b)] if len(t) else t
        st = B.trade_stats(t)
        if st.get("n_trades", 0) < 60:
            ok = False
        for k in ("n_trades", "win_rate_pct", "esperance_R", "profit_factor", "t_stat_R"):
            row[f"{split}_{k}"] = st.get(k)
    row["valide"] = ok
    records.append(row)
    print(".", end="", flush=True)

sel = pd.DataFrame(records)
sel.to_csv(os.path.join(RESULTS, "03_selection_IS.csv"), index=False)

esp_cols = [f"{s}_esperance_R" for s in SELECTION]
sel["esperance_min_IS"] = sel[esp_cols].min(axis=1)
sel["esperance_med_IS"] = sel[esp_cols].median(axis=1)
cand = sel[sel["valide"] & (sel["esperance_min_IS"] > 0)].copy()
cand = cand.sort_values("esperance_med_IS", ascending=False)

print(f"\n\n{len(cand)}/{len(sel)} configurations positives sur TOUS les univers in-sample")
print("\n### Top 12 in-sample ###")
show = ["sortie", "stop_atr", "confirmation"] + \
       [f"{s}_{m}" for s in SELECTION for m in ("n_trades", "win_rate_pct", "esperance_R")] + \
       ["esperance_min_IS"]
pd.set_option("display.width", 220)
print(cand[show].head(12).to_string(index=False))

with open(os.path.join(RESULTS, "03_selection_meta.json"), "w") as fh:
    json.dump({"n_configs_testees": len(grid),
               "n_configs_valides": int(len(cand)),
               "protocole": "selection sur SPX_IS + US500_IS uniquement",
               "splits": {k: list(v) for k, v in SPLITS.items()}}, fh, indent=2)
print("\n-> results/03_selection_IS.csv")
