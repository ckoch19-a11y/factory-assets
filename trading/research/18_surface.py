"""Surface de parametres sur l'echantillon crypto groupe.

Protocole fixe d'avance :
  apprentissage = trades ouverts avant 2023-01-01
  verification  = trades ouverts a partir de 2023-01-01
On cherche un PLATEAU large, pas le maximum. Un maximum isole sur la surface
est du bruit ; une zone etendue ou tout marche est un edge.
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

def feats(trend_len):
    out = {}
    cfg = B.Config(trend_len=trend_len, fee_bps=FEE, slip_bps=FEE)
    for sym, g in CRYPTO.groupby("symbol"):
        f = F.build_panel_features(g.sort_values("date"), 300)[
            ["symbol","date","open","high","low","close","atr14"]]
        out[sym] = B.generate_signals(f, cfg).assign(sig_short=False)
    return out

CACHE = {}
def get(trend_len):
    if trend_len not in CACHE:
        CACHE[trend_len] = feats(trend_len)
    return CACHE[trend_len]

def evaluate(trend_len, seuil, stop, trail, maxb):
    FE = get(trend_len)
    cfg = B.Config(trend_len=trend_len, stop_atr=stop, target_r=0.0, trail_atr=trail,
                   max_bars=maxb, confirm=False, exit_on_mean=False, allow_short=False,
                   fee_bps=FEE, slip_bps=FEE)
    parts = []
    for sym, g in FE.items():
        h = g.copy()
        h["sig_long"] = ((g["close"] > g["sma_trend"]) & (g["ext_bt"] > seuil)).fillna(False).values
        t = B.run_panel(h, cfg, presignal=True)
        if len(t): parts.append(t)
    if not parts: return None
    T = pd.concat(parts, ignore_index=True)
    IS = T[T["date_entree"] < SPLIT]; OOS = T[T["date_entree"] >= SPLIT]
    if len(IS) < 60 or len(OOS) < 40: return None
    return {"trend_len": trend_len, "seuil": seuil, "stop_atr": stop,
            "trail_atr": trail, "max_bars": maxb,
            "IS_n": len(IS), "IS_esp": round(float(IS["R"].mean()), 4),
            "IS_wr": round(float((IS["R"]>0).mean()*100), 1),
            "OOS_n": len(OOS), "OOS_esp": round(float(OOS["R"].mean()), 4),
            "OOS_wr": round(float((OOS["R"]>0).mean()*100), 1),
            "tot_n": len(T), "tot_esp": round(float(T["R"].mean()), 4),
            "tot_t": round(float(T["R"].mean()/(T["R"].std(ddof=1)/np.sqrt(len(T)))), 2)}

GRID = list(itertools.product((150, 200, 250), (1.0, 1.5, 2.0), (1.5, 2.0, 3.0),
                              (1.5, 2.0, 2.5, 3.0), (20, 40)))
print(f"{len(GRID)} configurations...")
rows = []
for i, (tl, se, st_, tr, mb) in enumerate(GRID):
    r = evaluate(tl, se, st_, tr, mb)
    if r: rows.append(r)
    if i % 20 == 0: print(f"  {i}/{len(GRID)}", flush=True)

df = pd.DataFrame(rows)
df.to_csv(os.path.join(RESULTS, "26_surface_crypto.csv"), index=False)
pd.set_option("display.width", 250)
print(f"\n{len(df)}/{len(GRID)} configurations exploitables")
print(f"Configurations positives en apprentissage ET en verification : "
      f"{int(((df.IS_esp>0)&(df.OOS_esp>0)).sum())}/{len(df)}")

print("\n### Plateau : moyenne de l'esperance hors echantillon par parametre ###")
for p in ("trend_len","seuil","stop_atr","trail_atr","max_bars"):
    g = df.groupby(p).agg(OOS_esp_moy=("OOS_esp","mean"), IS_esp_moy=("IS_esp","mean"),
                          n_config=("OOS_esp","size"),
                          pct_positif=("OOS_esp", lambda s: round(float((s>0).mean()*100))))
    print(f"\n{p} :"); print(g.round(4).to_string())

print("\n### Meilleures configurations en VERIFICATION (hors echantillon) ###")
print(df.sort_values("OOS_esp", ascending=False).head(12).to_string(index=False))
print("\n### Reference : la configuration actuelle ###")
cur = df[(df.trend_len==200)&(df.seuil==1.5)&(df.stop_atr==2.0)&(df.trail_atr==2.0)&(df.max_bars==40)]
print(cur.to_string(index=False))
