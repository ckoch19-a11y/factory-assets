"""Etude d'evenements : quels conditionnements changent vraiment la
distribution des rendements futurs ?

On teste AVANT de construire une strategie. Une regle qui n'a pas d'edge
mesurable ici n'a aucune raison d'en avoir une fois habillee en strategie.
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
HORIZONS = (1, 3, 5, 10, 20)

panel = pd.read_parquet(os.path.join(D.OUT, "panel_daily.parquet"))

UNIVERSES = {
    # 500 actions US, 2013-2018 : enorme echantillon transversal
    "US500": panel[panel["asset_class"] == "equity_single"],
    # indice S&P 500, 1962-2018 : 57 ans, tous les regimes de marche
    "SPX": panel[(panel["symbol"] == "SPX") & (panel["date"] >= "1962-01-01")],
    # BTC, 2012-2026 : actif jeune, tres volatil, regimes violents
    "BTC": panel[panel["symbol"] == "BTCUSD"],
}

print("Calcul des features...")
FEAT = {}
for name, p in UNIVERSES.items():
    f = F.build_panel_features(p, min_bars=400)
    for c in f.select_dtypes(include=["float64"]).columns:
        f[c] = f[c].astype("float32")
    FEAT[name] = f
    print(f"  {name:6s} {len(f):>8,} lignes  {f['symbol'].nunique():>4} symbole(s)  "
          f"{f['date'].min().date()} -> {f['date'].max().date()}")

# --------------------------------------------------------------------------
# Conditions candidates. Chacune a une justification economique, pas juste
# une combinaison qui "marche bien" sur l'historique.
# --------------------------------------------------------------------------
CONDITIONS = {
    # --- tendance (prime de momentum) ---
    "T1 tendance haussiere (C>SMA200)":
        lambda f: f["close"] > f["sma200"],
    "T2 tendance baissiere (C<SMA200)":
        lambda f: f["close"] < f["sma200"],
    "T3 momentum 12-1 positif":
        lambda f: f["mom12_1"] > 0,
    "T4 SMA200 en pente positive":
        lambda f: f["sma200_slope"] > 0,

    # --- retour a la moyenne pur (sans filtre) : controle ---
    "R1 RSI2 < 10 (sans filtre)":
        lambda f: f["rsi2"] < 10,
    "R2 3 cloture baissieres d'affilee":
        lambda f: f["consec_down"] >= 3,
    "R3 z-score 20j < -1.5":
        lambda f: f["z20"] < -1.5,

    # --- pullback DANS la tendance (momentum + retour a la moyenne) ---
    "P1 C>SMA200 & RSI2<10":
        lambda f: (f["close"] > f["sma200"]) & (f["rsi2"] < 10),
    "P2 C>SMA200 & RSI2<5":
        lambda f: (f["close"] > f["sma200"]) & (f["rsi2"] < 5),
    "P3 C>SMA200 & ext_ATR20 < -1":
        lambda f: (f["close"] > f["sma200"]) & (f["ext_atr20"] < -1),
    "P4 C>SMA200 & 3 baisses d'affilee":
        lambda f: (f["close"] > f["sma200"]) & (f["consec_down"] >= 3),
    "P5 C>SMA200 & z20 < -1.5":
        lambda f: (f["close"] > f["sma200"]) & (f["z20"] < -1.5),
    "P6 C>SMA200 & pente+ & RSI2<10":
        lambda f: (f["close"] > f["sma200"]) & (f["sma200_slope"] > 0) & (f["rsi2"] < 10),

    # --- pullback en tendance BAISSIERE (symetrie : rebond a vendre) ---
    "P7 C<SMA200 & RSI2>90":
        lambda f: (f["close"] < f["sma200"]) & (f["rsi2"] > 90),
    "P8 C<SMA200 & pente- & RSI2>90":
        lambda f: (f["close"] < f["sma200"]) & (f["sma200_slope"] < 0) & (f["rsi2"] > 90),

    # --- cassure / breakout ---
    "B1 nouveau plus haut 20j":
        lambda f: f["close"] >= f["hh20"] * 0.999,
    "B2 nouveau plus haut 252j":
        lambda f: f["close"] >= f["hh252"] * 0.999,
    "B3 nouveau plus bas 20j":
        lambda f: f["close"] <= f["ll20"] * 1.001,

    # --- regime de volatilite ---
    "V1 vol calme (rang<0.3)":
        lambda f: f["vol_rank"] < 0.3,
    "V2 vol elevee (rang>0.8)":
        lambda f: f["vol_rank"] > 0.8,
    "V3 compression de range (<0.7)":
        lambda f: f["range_compress"] < 0.7,

    # --- interactions tendance x volatilite ---
    "X1 C>SMA200 & vol calme":
        lambda f: (f["close"] > f["sma200"]) & (f["vol_rank"] < 0.5),
    "X2 C>SMA200 & vol extreme":
        lambda f: (f["close"] > f["sma200"]) & (f["vol_rank"] > 0.8),
    "X3 C>SMA200 & RSI2<10 & vol<0.8":
        lambda f: (f["close"] > f["sma200"]) & (f["rsi2"] < 10) & (f["vol_rank"] < 0.8),
    "X4 C>SMA200 & RSI2<10 & vol>0.8":
        lambda f: (f["close"] > f["sma200"]) & (f["rsi2"] < 10) & (f["vol_rank"] > 0.8),

    # --- structure de barre ---
    "S1 cloture dans le haut de barre (>0.8)":
        lambda f: f["close_loc"] > 0.8,
    "S2 cloture dans le bas de barre (<0.2)":
        lambda f: f["close_loc"] < 0.2,
    "S3 C>SMA200 & RSI2<10 & cloture>0.5":
        lambda f: (f["close"] > f["sma200"]) & (f["rsi2"] < 10) & (f["close_loc"] > 0.5),

    # --- calendrier ---
    "C1 tour du mois (jour>=28 ou <=3)":
        lambda f: (f["dom"] >= 28) | (f["dom"] <= 3),
    "C2 lundi":
        lambda f: f["dow"] == 0,
}

rows, n_tests = [], 0
for uni, f in FEAT.items():
    print(f"\n=== Univers {uni} ===")
    for cname, fn in CONDITIONS.items():
        try:
            mask = fn(f).fillna(False).astype(bool)
        except Exception as exc:
            print(f"  ! {cname}: {exc}")
            continue
        for hz in HORIZONS:
            n_tests += 1
            res = S.event_test(f, mask, hz)
            if res.get("status") != "ok":
                continue
            rows.append({"univers": uni, "condition": cname, "horizon_j": hz, **res})

out = pd.DataFrame(rows)
out.to_csv(os.path.join(RESULTS, "01_event_study.csv"), index=False)

print(f"\n{n_tests} tests effectues, {len(out)} exploitables.")
print("\n### Signaux les plus robustes (|t_excess| >= 3, tries par t) ###")
strong = out[out["t_excess"].abs() >= 3].copy()
strong["abs_t"] = strong["t_excess"].abs()
cols = ["univers", "condition", "horizon_j", "n_obs", "mean_excess_pct",
        "t_excess", "hit_rate", "hit_rate_base", "edge_hit_pts"]
print(strong.sort_values("abs_t", ascending=False)[cols].head(35).to_string(index=False))

with open(os.path.join(RESULTS, "01_event_study_meta.json"), "w") as fh:
    json.dump({"n_tests_effectues": n_tests,
               "n_resultats": len(out),
               "horizons": list(HORIZONS),
               "univers": {k: {"lignes": int(len(v)),
                               "symboles": int(v["symbol"].nunique()),
                               "debut": str(v["date"].min().date()),
                               "fin": str(v["date"].max().date())}
                           for k, v in FEAT.items()}}, fh, indent=2)
