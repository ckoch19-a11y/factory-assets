"""Extension de la grille aux bords.

Trois parametres ressortaient a l'extremite de la grille precedente. Un
optimum au bord n'est pas un optimum : soit la vraie valeur est au-dela, soit
l'effet est monotone et il faut comprendre pourquoi. On elargit jusqu'a voir
le retournement.
"""
from __future__ import annotations

import itertools, os, sys, json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import data as D, features as F, backtest as B, stats as S  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
CRYPTO = pd.read_parquet("/tmp/mkt/clean/crypto_daily.parquet")
FEE = 10.0
SPLIT = pd.Timestamp("2023-01-01")

BASEF = {}
for sym, g in CRYPTO.groupby("symbol"):
    f = F.build_panel_features(g.sort_values("date"), 300)[
        ["symbol","date","open","high","low","close","atr14"]]
    BASEF[sym] = B.generate_signals(f, B.Config(trend_len=200, fee_bps=FEE, slip_bps=FEE)).assign(sig_short=False)

def evaluate(seuil, stop, trail, maxb):
    cfg = B.Config(trend_len=200, stop_atr=stop, target_r=0.0, trail_atr=trail,
                   max_bars=maxb, confirm=False, exit_on_mean=False, allow_short=False,
                   fee_bps=FEE, slip_bps=FEE)
    parts = []
    for sym, g in BASEF.items():
        h = g.copy()
        h["sig_long"] = ((g["close"] > g["sma_trend"]) & (g["ext_bt"] > seuil)).fillna(False).values
        t = B.run_panel(h, cfg, presignal=True)
        if len(t): parts.append(t)
    if not parts: return None
    T = pd.concat(parts, ignore_index=True)
    IS = T[T["date_entree"] < SPLIT]; OOS = T[T["date_entree"] >= SPLIT]
    if len(IS) < 40 or len(OOS) < 30: return None
    R = T["R"].values
    eq = np.cumprod(1 + 0.01*R); dd = float((eq/np.maximum.accumulate(eq)-1).min()*100)
    return {"seuil": seuil, "stop_atr": stop, "trail_atr": trail, "max_bars": maxb,
            "IS_n": len(IS), "IS_esp": round(float(IS["R"].mean()),4),
            "OOS_n": len(OOS), "OOS_esp": round(float(OOS["R"].mean()),4),
            "OOS_wr": round(float((OOS["R"]>0).mean()*100),1),
            "tot_n": len(T), "tot_esp": round(float(R.mean()),4),
            "tot_wr": round(float((R>0).mean()*100),1),
            "tot_t": round(float(R.mean()/(R.std(ddof=1)/np.sqrt(len(R)))),2),
            "R_par_an": round(float(R.sum()/9.1),1),
            "dd_seq_%": round(dd,1)}

# trail 0 = on laisse courir jusqu'a la sortie temporelle (pas de suiveur)
GRID = list(itertools.product((1.0,1.5,2.0,2.5,3.0,3.5), (1.0,1.25,1.5,2.0,2.5),
                              (2.0,3.0,4.0,5.0,6.0,0.0), (40,)))
print(f"{len(GRID)} configurations...")
rows = []
for i,(se,st_,tr,mb) in enumerate(GRID):
    r = evaluate(se,st_,tr,mb)
    if r: rows.append(r)
    if i % 30 == 0: print(f"  {i}/{len(GRID)}", flush=True)
df = pd.DataFrame(rows)
df.to_csv(os.path.join(RESULTS, "27_surface_etendue.csv"), index=False)
pd.set_option("display.width", 250)
print(f"\n{len(df)} configurations | positives IS et OOS : {int(((df.IS_esp>0)&(df.OOS_esp>0)).sum())}/{len(df)}")

print("\n### Effet de chaque parametre sur l'esperance hors echantillon ###")
for p in ("seuil","stop_atr","trail_atr"):
    g = df.groupby(p).agg(OOS=("OOS_esp","mean"), IS=("IS_esp","mean"),
                          trades_total=("tot_n","mean"), wr=("tot_wr","mean"),
                          R_par_an=("R_par_an","mean"))
    print(f"\n{p} (trail_atr 0 = aucun suiveur, sortie au temps) :")
    print(g.round(3).to_string())

print("\n### Top 15 hors echantillon ###")
print(df.sort_values("OOS_esp", ascending=False).head(15).to_string(index=False))
print("\n### Meilleur rendement ANNUEL en R (ce qui compte vraiment) ###")
print(df.sort_values("R_par_an", ascending=False).head(12).to_string(index=False))
