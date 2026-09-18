"""Le crypto se comporte a l'envers des actions : l'entree sur repli n'y
apporte rien, l'entree sur extension HAUTE semble meilleure. Verification
en bonne et due forme avant d'en faire une recommandation.

Protocole : selection sur BTC 2012-2019, validation sur BTC 2020-2026.
Controle obligatoire contre l'entree aleatoire dans le meme regime.
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
               trail_atr=2.0, max_bars=40, allow_short=False,
               fee_bps=10.0, slip_bps=10.0)

UNIS = {
    "BTC": panel[panel["symbol"] == "BTCUSD"],
    "SPX": panel[(panel["symbol"] == "SPX") & (panel["date"] >= "1962-01-01")],
    "US500": panel[panel["asset_class"] == "equity_single"],
}
FE = {}
for k, v in UNIS.items():
    f = F.build_panel_features(v, 400)
    g = B.generate_signals(
        f[["symbol", "date", "open", "high", "low", "close", "atr14"]], CFG)
    g["sig_short"] = False
    g["hh50"] = f.groupby("symbol")["high"].transform(lambda s: s.rolling(50).max()).values
    FE[k] = g

SPLIT = {"BTC": ("2012-01-01", "2019-12-31", "2020-01-01", "2026-12-31")}


def stats_for(g, mask, a=None, b=None, fee=10.0):
    h = g.copy()
    h["sig_long"] = mask.fillna(False).values
    cfg = B.Config(stop_atr=2.0, confirm=False, exit_on_mean=False, target_r=0.0,
                   trail_atr=2.0, max_bars=40, allow_short=False,
                   fee_bps=fee, slip_bps=fee)
    t = B.run_panel(h, cfg, presignal=True)
    if len(t) and a:
        t = t[(t["date_entree"] >= pd.Timestamp(a)) & (t["date_entree"] <= pd.Timestamp(b))]
    return B.trade_stats(t)


def alea(g, taux, a, b, fee, n_iter=30):
    up = (g["close"] > g["sma_trend"]).fillna(False).values
    es, wr = [], []
    for s in range(n_iter):
        rng = np.random.default_rng(s)
        st = stats_for(g, pd.Series(up & (rng.random(len(g)) < taux)), a, b, fee)
        if st.get("n_trades", 0) > 15:
            es.append(st["esperance_R"])
            wr.append(st["win_rate_pct"])
    return es, wr


VARIANTES = {
    "repli (VRC)":           lambda g: (g["close"] > g["sma_trend"]) & (g["ext_bt"] < -1.0),
    "extension +0.5 ATR":    lambda g: (g["close"] > g["sma_trend"]) & (g["ext_bt"] > 0.5),
    "extension +1.0 ATR":    lambda g: (g["close"] > g["sma_trend"]) & (g["ext_bt"] > 1.0),
    "extension +1.5 ATR":    lambda g: (g["close"] > g["sma_trend"]) & (g["ext_bt"] > 1.5),
    "plus haut 50 barres":   lambda g: (g["close"] > g["sma_trend"]) & (g["close"] >= g["hh50"] * 0.999),
}

rows = []
g = FE["BTC"]
a_is, b_is, a_oos, b_oos = SPLIT["BTC"]
for name, fn in VARIANTES.items():
    m = fn(g)
    s_is = stats_for(g, m, a_is, b_is)
    s_oos = stats_for(g, m, a_oos, b_oos)
    taux = float(m.fillna(False).sum()) / max((g["close"] > g["sma_trend"]).sum(), 1)
    es_is, _ = alea(g, taux, a_is, b_is, 10.0)
    es_oos, _ = alea(g, taux, a_oos, b_oos, 10.0)
    rows.append({
        "variante": name,
        "IS_n": s_is.get("n_trades"), "IS_wr": s_is.get("win_rate_pct"),
        "IS_espR": s_is.get("esperance_R"),
        "IS_alea_median": round(float(np.median(es_is)), 4) if es_is else None,
        "IS_bat_alea": round(float(np.mean([e < s_is.get("esperance_R", -9) for e in es_is])), 2) if es_is else None,
        "OOS_n": s_oos.get("n_trades"), "OOS_wr": s_oos.get("win_rate_pct"),
        "OOS_espR": s_oos.get("esperance_R"), "OOS_pf": s_oos.get("profit_factor"),
        "OOS_alea_median": round(float(np.median(es_oos)), 4) if es_oos else None,
        "OOS_bat_alea": round(float(np.mean([e < s_oos.get("esperance_R", -9) for e in es_oos])), 2) if es_oos else None,
    })

out = pd.DataFrame(rows)
out.to_csv(os.path.join(RESULTS, "18_crypto_variantes.csv"), index=False)
pd.set_option("display.width", 250)
print("### BTC : quelle entree fonctionne ? (gestion identique, frais 40 bps A/R) ###")
print("  IS = 2012-2019 (choix)   OOS = 2020-2026 (verification)")
print("  *_bat_alea = part des 30 tirages aleatoires battus par la variante\n")
print(out.to_string(index=False))

print("\n\n### La meme variante sur actions, pour savoir si c'est propre au crypto ###\n")
rows2 = []
for name, fn in VARIANTES.items():
    for uni in ("SPX", "US500"):
        gg = FE[uni]
        st = stats_for(gg, fn(gg), fee=5.0)
        rows2.append({"variante": name, "univers": uni, "n": st.get("n_trades"),
                      "win_rate": st.get("win_rate_pct"), "espR": st.get("esperance_R"),
                      "pf": st.get("profit_factor")})
o2 = pd.DataFrame(rows2)
o2.to_csv(os.path.join(RESULTS, "19_variantes_actions.csv"), index=False)
print(o2.pivot_table(index="variante", columns="univers",
                     values=["espR", "win_rate", "n"]).round(3).to_string())
