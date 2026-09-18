"""Le controle decisif : le signal apporte-t-il quelque chose, ou est-ce que
c'est juste "etre long dans une tendance haussiere" qui rapporte ?

On compare, avec la MEME gestion (meme stop, meme suiveur, meme duree max,
memes frais) :
  - VRC : entree sur repli marque, mesure en ATR ;
  - entree ALEATOIRE dans le meme regime haussier, meme nombre de trades ;
  - entree sur extension HAUTE (le contraire du repli).

Si VRC ne bat pas nettement l'entree aleatoire, le signal ne sert a rien et
il faut le dire.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import data as D, features as F, backtest as B, stats as S  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
panel = pd.read_parquet(os.path.join(D.OUT, "panel_daily.parquet"))

CFG = B.Config(stop_atr=2.0, confirm=False, exit_on_mean=False, target_r=0.0,
               trail_atr=2.0, max_bars=40, allow_short=False)

UNIS = {
    "SPX 1962-2018": panel[(panel["symbol"] == "SPX") & (panel["date"] >= "1962-01-01")],
    "BTC 2012-2026": panel[panel["symbol"] == "BTCUSD"],
    "US500 2013-2018": panel[panel["asset_class"] == "equity_single"],
}

rows = []
for uni, raw in UNIS.items():
    f = F.build_panel_features(raw, 400)[
        ["symbol", "date", "open", "high", "low", "close", "atr14"]]
    g = B.generate_signals(f, CFG)
    g["sig_short"] = False

    # --- 1) VRC tel quel
    t_vrc = B.run_panel(g, CFG, presignal=True)
    s_vrc = B.trade_stats(t_vrc)
    n_ref = s_vrc["n_trades"]

    # --- 2) entree aleatoire dans le meme regime haussier
    up = (g["close"] > g["sma_trend"]).fillna(False).values
    taux = float(g["sig_long"].sum()) / max(up.sum(), 1)
    esp_alea, wr_alea, n_alea = [], [], []
    for seed in range(30):
        rng = np.random.default_rng(seed)
        h = g.copy()
        h["sig_long"] = up & (rng.random(len(g)) < taux)
        st = B.trade_stats(B.run_panel(h, CFG, presignal=True))
        if st.get("n_trades", 0) > 20:
            esp_alea.append(st["esperance_R"])
            wr_alea.append(st["win_rate_pct"])
            n_alea.append(st["n_trades"])

    # --- 3) entree sur extension haute (contraire du repli)
    h = g.copy()
    h["sig_long"] = ((g["close"] > g["sma_trend"]) & (g["ext_bt"] > 1.0)).fillna(False)
    s_inv = B.trade_stats(B.run_panel(h, CFG, presignal=True))

    # --- 4) signal retarde : on decale UNIQUEMENT le declenchement
    lag_res = {}
    for lag in (1, 2, 5, 10):
        h = g.copy()
        h["sig_long"] = g.groupby("symbol")["sig_long"].shift(lag).fillna(False)
        st = B.trade_stats(B.run_panel(h, CFG, presignal=True))
        lag_res[lag] = (st.get("esperance_R"), st.get("n_trades"))

    med = float(np.median(esp_alea))
    # position de VRC dans la distribution des tirages aleatoires
    pct = float(np.mean([e >= s_vrc["esperance_R"] for e in esp_alea]))
    rows.append({
        "univers": uni,
        "VRC_n": n_ref, "VRC_wr": s_vrc["win_rate_pct"], "VRC_espR": s_vrc["esperance_R"],
        "VRC_pf": s_vrc["profit_factor"],
        "alea_n_moyen": int(np.mean(n_alea)), "alea_wr_median": round(float(np.median(wr_alea)), 2),
        "alea_espR_median": round(med, 4),
        "alea_espR_min": round(float(np.min(esp_alea)), 4),
        "alea_espR_max": round(float(np.max(esp_alea)), 4),
        "gain_vs_alea_R": round(s_vrc["esperance_R"] - med, 4),
        "p_value_vs_alea": round(pct, 4),
        "extension_haute_espR": s_inv.get("esperance_R"),
        "extension_haute_n": s_inv.get("n_trades"),
        "retard_1b_espR": lag_res[1][0], "retard_2b_espR": lag_res[2][0],
        "retard_5b_espR": lag_res[5][0], "retard_10b_espR": lag_res[10][0],
    })
    print(f"[{uni}] fait")

out = pd.DataFrame(rows)
out.to_csv(os.path.join(RESULTS, "17_controle_entree.csv"), index=False)
pd.set_option("display.width", 250)

print("\n" + "=" * 118)
print("### VRC contre entree ALEATOIRE dans le meme regime, gestion identique ###\n")
print(out[["univers", "VRC_n", "VRC_wr", "VRC_espR", "alea_n_moyen", "alea_wr_median",
           "alea_espR_median", "alea_espR_min", "alea_espR_max",
           "gain_vs_alea_R", "p_value_vs_alea"]].to_string(index=False))
print("\n  p_value_vs_alea = part des 30 tirages aleatoires qui font aussi bien")
print("  que VRC. 0,00 signifie qu'aucun n'y arrive.")

print("\n" + "=" * 118)
print("### Degradation du signal quand on le retarde ###\n")
print(out[["univers", "VRC_espR", "retard_1b_espR", "retard_2b_espR",
           "retard_5b_espR", "retard_10b_espR"]].to_string(index=False))
print("\n  Un vrai edge de timing se degrade progressivement. Une fuite")
print("  d'information s'effondrerait des la premiere barre de retard.")

print("\n" + "=" * 118)
print("### Entree sur extension HAUTE (le contraire du repli) ###\n")
print(out[["univers", "VRC_espR", "extension_haute_espR", "extension_haute_n"]].to_string(index=False))
