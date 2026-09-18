"""Raffinement : sensibilite aux parametres et test de la symetrie.

Objectif : chercher un PLATEAU, pas un pic. Un parametre dont l'edge
s'effondre des qu'on le bouge de 10 % est du bruit, pas un edge.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import data as D, features as F, stats as S  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
panel = pd.read_parquet(os.path.join(D.OUT, "panel_daily.parquet"))

UNI = {
    "US500": panel[panel["asset_class"] == "equity_single"],
    "SPX": panel[(panel["symbol"] == "SPX") & (panel["date"] >= "1962-01-01")],
    "BTC": panel[panel["symbol"] == "BTCUSD"],
}
FEAT = {k: F.build_panel_features(v, 400) for k, v in UNI.items()}
for k in FEAT:
    for c in FEAT[k].select_dtypes("float64").columns:
        FEAT[k][c] = FEAT[k][c].astype("float32")

rows = []
n_tests = 0


def rec(cat, param, val, uni, hz, res):
    global n_tests
    n_tests += 1
    if res.get("status") == "ok":
        rows.append({"categorie": cat, "parametre": param, "valeur": val,
                     "univers": uni, "horizon_j": hz, **res})


# ---------------------------------------------------------------- 1. seuil d'extension
print("1/5 Sensibilite du seuil d'extension (ext_ATR) cote LONG")
for thr in (-0.5, -0.75, -1.0, -1.25, -1.5, -2.0, -2.5):
    for uni, f in FEAT.items():
        m = (f["close"] > f["sma200"]) & (f["ext_atr20"] < thr)
        for hz in (5, 10, 20):
            rec("seuil_ext_long", "ext_atr20", thr, uni, hz,
                S.event_test(f, m.fillna(False), hz))

print("2/5 Sensibilite du seuil d'extension cote SHORT (symetrie)")
for thr in (0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5):
    for uni, f in FEAT.items():
        m = (f["close"] < f["sma200"]) & (f["ext_atr20"] > thr)
        for hz in (5, 10, 20):
            rec("seuil_ext_short", "ext_atr20", thr, uni, hz,
                S.event_test(f, m.fillna(False), hz))

# ---------------------------------------------------------------- 2. longueur du filtre de tendance
print("3/5 Sensibilite de la longueur du filtre de tendance")
for n in (100, 150, 200, 250):
    for uni, f in FEAT.items():
        sma = f.groupby("symbol")["close"].transform(lambda s: s.rolling(n).mean())
        for side, m, hz_list in (
            ("long", (f["close"] > sma) & (f["ext_atr20"] < -1), (5, 20)),
            ("short", (f["close"] < sma) & (f["ext_atr20"] > 1), (5, 20)),
        ):
            for hz in hz_list:
                rec(f"longueur_tendance_{side}", "n_sma", n, uni, hz,
                    S.event_test(f, m.fillna(False), hz))

# ---------------------------------------------------------------- 3. filtre de pente
print("4/5 Apport du filtre de pente")
for uni, f in FEAT.items():
    base_l = (f["close"] > f["sma200"]) & (f["ext_atr20"] < -1)
    base_s = (f["close"] < f["sma200"]) & (f["ext_atr20"] > 1)
    variants = {
        "long_sans_pente": base_l,
        "long_avec_pente": base_l & (f["sma200_slope"] > 0),
        "short_sans_pente": base_s,
        "short_avec_pente": base_s & (f["sma200_slope"] < 0),
    }
    for name, m in variants.items():
        for hz in (5, 10, 20):
            rec("filtre_pente", "variante", name, uni, hz,
                S.event_test(f, m.fillna(False), hz))

# ---------------------------------------------------------------- 4. confirmation de retournement
print("5/5 Apport d'une confirmation de retournement")
for uni, f in FEAT.items():
    g = f.groupby("symbol")
    prev_high = g["high"].shift(1)
    prev_low = g["low"].shift(1)
    base_l = (f["close"] > f["sma200"]) & (f["ext_atr20"] < -1)
    base_s = (f["close"] < f["sma200"]) & (f["ext_atr20"] > 1)
    variants = {
        "long_brut": base_l,
        "long_confirme_close>hautprec": base_l & (f["close"] > prev_high),
        "long_confirme_close_haut_barre": base_l & (f["close_loc"] > 0.5),
        "long_confirme_jour_hausse": base_l & (f["ret1"] > 0),
        "short_brut": base_s,
        "short_confirme_close<basprec": base_s & (f["close"] < prev_low),
        "short_confirme_jour_baisse": base_s & (f["ret1"] < 0),
    }
    for name, m in variants.items():
        for hz in (5, 10, 20):
            rec("confirmation", "variante", name, uni, hz,
                S.event_test(f, m.fillna(False), hz))

out = pd.DataFrame(rows)
out.to_csv(os.path.join(RESULTS, "02_refine.csv"), index=False)
with open(os.path.join(RESULTS, "02_refine_meta.json"), "w") as fh:
    json.dump({"n_tests": n_tests, "n_resultats": len(out)}, fh, indent=2)
print(f"\n{n_tests} tests, {len(out)} exploitables -> results/02_refine.csv")

pd.set_option("display.width", 200)
c = ["univers", "valeur", "horizon_j", "n_obs", "mean_excess_pct", "t_excess", "edge_hit_pts"]
for cat in ("seuil_ext_long", "seuil_ext_short"):
    print(f"\n### {cat} (horizon 20j) ###")
    sub = out[(out.categorie == cat) & (out.horizon_j == 20)]
    print(sub.pivot_table(index="valeur", columns="univers",
                          values=["t_excess", "edge_hit_pts"]).round(2).to_string())
