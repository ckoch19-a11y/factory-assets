"""Le contrôle qui tranche : ces configurations spectaculaires battent-elles
une entree ALEATOIRE dans le meme regime haussier, avec la meme gestion ?

Avec un stop serre et une detention de 40 jours en marche haussier crypto,
n'importe quelle entree longue produit des chiffres flatteurs. Si la regle ne
bat pas le hasard, l'esperance mesuree n'est pas un edge : c'est de
l'exposition.
"""
from __future__ import annotations

import os, sys, json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import data as D, features as F, backtest as B, stats as S  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
CRYPTO = pd.read_parquet("/tmp/mkt/clean/crypto_daily.parquet")
FEE = 10.0
SPLIT = pd.Timestamp("2023-01-01")

FE = {}
for sym, g in CRYPTO.groupby("symbol"):
    f = F.build_panel_features(g.sort_values("date"), 300)[
        ["symbol","date","open","high","low","close","atr14"]]
    FE[sym] = B.generate_signals(f, B.Config(trend_len=200, fee_bps=FEE, slip_bps=FEE)).assign(sig_short=False)

def run_cfg(masks, stop, trail, maxb):
    cfg = B.Config(trend_len=200, stop_atr=stop, target_r=0.0, trail_atr=trail,
                   max_bars=maxb, confirm=False, exit_on_mean=False, allow_short=False,
                   fee_bps=FEE, slip_bps=FEE)
    parts = []
    for sym, g in FE.items():
        h = g.copy(); h["sig_long"] = masks[sym]
        t = B.run_panel(h, cfg, presignal=True)
        if len(t): parts.append(t)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

def regle(seuil):
    return {s: ((g["close"] > g["sma_trend"]) & (g["ext_bt"] > seuil)).fillna(False).values
            for s, g in FE.items()}

def aleatoire(taux_par_sym, seed):
    rng = np.random.default_rng(seed)
    out = {}
    for s, g in FE.items():
        up = (g["close"] > g["sma_trend"]).fillna(False).values
        out[s] = up & (rng.random(len(g)) < taux_par_sym[s])
    return out

CANDIDATS = [
    ("actuelle",            1.5, 2.0, 2.0, 40),
    ("seuil2 stop1.5 tr3",  2.0, 1.5, 3.0, 40),
    ("seuil2 stop1 tr6",    2.0, 1.0, 6.0, 40),
    ("seuil1.5 stop1 sans", 1.5, 1.0, 0.0, 40),
    ("seuil1 stop1 sans",   1.0, 1.0, 0.0, 40),
    ("seuil2.5 stop1 tr6",  2.5, 1.0, 6.0, 40),
]

rows = []
for nom, seuil, stop, trail, maxb in CANDIDATS:
    m = regle(seuil)
    T = run_cfg(m, stop, trail, maxb)
    if not len(T): continue
    taux = {s: float(m[s].sum()) / max((FE[s]["close"] > FE[s]["sma_trend"]).sum(), 1) for s in FE}
    es, ns = [], []
    for seed in range(40):
        Ta = run_cfg(aleatoire(taux, seed), stop, trail, maxb)
        if len(Ta) > 30:
            es.append(float(Ta["R"].mean())); ns.append(len(Ta))
    med = float(np.median(es)) if es else np.nan
    bat = int(np.sum([e < T["R"].mean() for e in es])) if es else 0
    R = T["R"].values
    IS = T[T.date_entree < SPLIT]["R"]; OOS = T[T.date_entree >= SPLIT]["R"]
    rows.append({
        "configuration": nom, "seuil": seuil, "stop": stop, "trail": trail,
        "n_trades": len(T), "win_rate": round(float((R>0).mean()*100),1),
        "esperance_R": round(float(R.mean()),3),
        "IS_esp": round(float(IS.mean()),3), "OOS_esp": round(float(OOS.mean()),3),
        "alea_median_R": round(med,3),
        "alea_n_moyen": int(np.mean(ns)) if ns else 0,
        "ecart_vs_alea": round(float(R.mean())-med,3),
        "bat_alea_sur_40": bat,
    })
    print(f"[{nom:22s}] esp {R.mean():+.3f} R | alea {med:+.3f} | ecart {R.mean()-med:+.3f} | bat {bat}/40", flush=True)

out = pd.DataFrame(rows)
out.to_csv(os.path.join(RESULTS, "28_controle_surface.csv"), index=False)
pd.set_option("display.width", 240)
print("\n" + "="*120)
print("### La regle contre le hasard, gestion identique ###\n")
print(out.to_string(index=False))
print("\n  ecart_vs_alea est la SEULE colonne qui mesure l'apport du signal.")
print("  Une esperance elevee avec un ecart nul veut dire : c'est l'exposition")
print("  qui paie, pas la regle.")
