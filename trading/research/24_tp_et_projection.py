"""Deux questions pratiques avant de reecrire l'indicateur.

1. Tu veux un TP place automatiquement. Le reglage retenu utilise un stop
   suiveur, donc pas d'objectif fixe. Un objectif fixe degrade-t-il, ou non ?

2. Tu veux voir A L'AVANCE ou le signal se declenchera. Le niveau projete est
   EMA20 + seuil x ATR14, calcule sur la barre en cours. Mais EMA et ATR
   bougent d'une barre a l'autre : quelle est la precision reelle de cette
   projection ?
"""
from __future__ import annotations
import os, sys, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import data as D, features as F, backtest as B, stats as S  # noqa: E402
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
CRYPTO = pd.read_parquet("/tmp/mkt/clean/crypto_daily.parquet")
FEE = 10.0
SEUIL, STOP, TRAIL = 2.0, 1.5, 3.0

FE = {}
for sym, g in CRYPTO.groupby("symbol"):
    f = F.build_panel_features(g.sort_values("date"), 300)[
        ["symbol","date","open","high","low","close","atr14"]]
    FE[sym] = B.generate_signals(f, B.Config(trend_len=200, fee_bps=FEE, slip_bps=FEE)).assign(sig_short=False)

def run(target_r, trail):
    cfg = B.Config(trend_len=200, stop_atr=STOP, target_r=target_r, trail_atr=trail,
                   max_bars=40, confirm=False, exit_on_mean=False, allow_short=False,
                   fee_bps=FEE, slip_bps=FEE)
    parts = []
    for sym, g in FE.items():
        h = g.copy()
        h["sig_long"] = ((g["close"] > g["sma_trend"]) & (g["ext_bt"] > SEUIL)).fillna(False).values
        t = B.run_panel(h, cfg, presignal=True)
        if len(t): parts.append(t)
    return pd.concat(parts, ignore_index=True)

print("### 1. Un objectif fixe degrade-t-il le reglage retenu ? ###\n")
rows = []
for tgt, tr, lib in [(0.0, TRAIL, "suiveur seul (retenu)"),
                     (2.0, TRAIL, "suiveur + objectif 2R"),
                     (3.0, TRAIL, "suiveur + objectif 3R"),
                     (4.0, TRAIL, "suiveur + objectif 4R"),
                     (6.0, TRAIL, "suiveur + objectif 6R"),
                     (2.0, 0.0,   "objectif 2R seul"),
                     (3.0, 0.0,   "objectif 3R seul")]:
    T = run(tgt, tr); R = T["R"].values
    T2 = T.copy(); T2["an"] = T2["date_entree"].dt.year
    pa = T2.groupby("an")["R"].sum()
    rows.append({"gestion": lib, "n": len(R), "win_rate": round(float((R>0).mean()*100),1),
                 "esperance_R": round(float(R.mean()),3),
                 "profit_factor": round(float(R[R>0].sum()/abs(R[R<=0].sum())),2),
                 "R_par_an": round(float(R.sum()/9.1),1),
                 "annees_pos": f"{int((pa>0).sum())}/{len(pa)}",
                 "motifs": dict(T["motif"].value_counts())})
d = pd.DataFrame(rows)
pd.set_option("display.width", 250)
print(d.to_string(index=False))
d.to_csv(os.path.join(RESULTS,"38_objectif_fixe.csv"), index=False)

print("\n" + "="*112)
print("### 2. Precision du niveau d'entree projete ###\n")
print("On calcule sur la barre t le niveau EMA20 + 2 x ATR14, puis on le compare")
print("au niveau reellement necessaire sur la barre t+1.\n")
err = []
for sym, g in FE.items():
    g = g.reset_index(drop=True)
    proj = g["ema_fast"] + SEUIL * g["atr_bt"]          # niveau calcule en t
    reel = (g["ema_fast"] + SEUIL * g["atr_bt"]).shift(-1)  # niveau vrai en t+1
    e = ((proj - reel) / g["close"]).dropna()
    err.append(pd.DataFrame({"symbol": sym, "err_pct": e*100}))
E = pd.concat(err)
print(f"  ecart median absolu   : {E['err_pct'].abs().median():.3f} % du prix")
print(f"  ecart moyen absolu    : {E['err_pct'].abs().mean():.3f} %")
print(f"  90e centile           : {E['err_pct'].abs().quantile(0.90):.3f} %")
print(f"  99e centile           : {E['err_pct'].abs().quantile(0.99):.3f} %")
atr_pct = pd.concat([ (FE[s]['atr_bt']/FE[s]['close']*100).dropna() for s in FE ])
print(f"\n  a comparer a l'ATR median : {atr_pct.median():.2f} % du prix")
print(f"  soit une erreur de projection de {E['err_pct'].abs().median()/atr_pct.median():.1%} d'ATR.")
print("\n  Conclusion : le niveau projete est fiable a une fraction d'ATR pres.")
print("  Il indique la zone, pas le tick exact - ce qui suffit pour preparer")
print("  l'analyse order flow avant le declenchement.")
json.dump({"err_median_pct": float(E['err_pct'].abs().median()),
           "err_p90_pct": float(E['err_pct'].abs().quantile(0.90)),
           "atr_median_pct": float(atr_pct.median())},
          open(os.path.join(RESULTS,"39_projection.json"),"w"), indent=2)
