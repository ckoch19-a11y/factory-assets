"""Choix du reglage, puis classement des actifs avec CE reglage.

C affiche un MAR deux fois superieur a B pour le meme creux. Avant de le
retenir, on verifie sa fragilite : un resultat porte par cinq trades n'est pas
un edge, c'est une loterie gagnee.
"""
from __future__ import annotations
import os, sys, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import data as D, features as F, backtest as B, stats as S  # noqa: E402
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
CRYPTO = pd.read_parquet("/tmp/mkt/clean/crypto_daily.parquet")
FEE = 10.0

FE = {}
for sym, g in CRYPTO.groupby("symbol"):
    f = F.build_panel_features(g.sort_values("date"), 300)[
        ["symbol","date","open","high","low","close","atr14"]]
    FE[sym] = B.generate_signals(f, B.Config(trend_len=200, fee_bps=FEE, slip_bps=FEE)).assign(sig_short=False)

CFG = {"A_actuelle":(1.5,2.0,2.0), "B_equilibre":(2.0,1.5,3.0),
       "C_laisse_courir":(2.0,1.0,6.0), "D_agressive":(1.5,1.0,0.0)}

def trades(seuil, stop, trail, syms=None):
    cfg = B.Config(trend_len=200, stop_atr=stop, target_r=0.0, trail_atr=trail,
                   max_bars=40, confirm=False, exit_on_mean=False, allow_short=False,
                   fee_bps=FEE, slip_bps=FEE)
    parts = []
    for sym, g in FE.items():
        if syms and sym not in syms: continue
        h = g.copy()
        h["sig_long"] = ((g["close"] > g["sma_trend"]) & (g["ext_bt"] > seuil)).fillna(False).values
        t = B.run_panel(h, cfg, presignal=True)
        if len(t): parts.append(t)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

print("### Fragilite : que reste-t-il sans les meilleurs trades ? ###\n")
rows = []
for nom,(se,st_,tr) in CFG.items():
    T = trades(se,st_,tr); R = np.sort(T["R"].values)
    line = {"config": nom, "n": len(R), "esperance": round(float(R.mean()),3)}
    for k in (1,3,5,10,20):
        line[f"sans_{k}_meilleurs"] = round(float(R[:-k].mean()),3)
    line["part_gain_top5_%"] = round(float(R[-5:][R[-5:]>0].sum()/R[R>0].sum()*100),1)
    line["part_gain_top20_%"] = round(float(R[-20:][R[-20:]>0].sum()/R[R>0].sum()*100),1)
    rows.append(line)
fr = pd.DataFrame(rows); fr.to_csv(os.path.join(RESULTS,"35_fragilite.csv"), index=False)
pd.set_option("display.width", 240)
print(fr.to_string(index=False))

print("\n" + "="*115)
print("### Repartition du risque : pire annee, pire trimestre ###\n")
rows = []
for nom,(se,st_,tr) in CFG.items():
    T = trades(se,st_,tr).copy()
    T["an"] = T["date_entree"].dt.year
    T["tri"] = T["date_entree"].dt.to_period("Q")
    pa = T.groupby("an")["R"].sum(); pt = T.groupby("tri")["R"].sum()
    rows.append({"config": nom,
                 "annees_positives": f"{int((pa>0).sum())}/{len(pa)}",
                 "pire_annee_R": round(float(pa.min()),1),
                 "trimestres_positifs": f"{int((pt>0).sum())}/{len(pt)}",
                 "pire_trimestre_R": round(float(pt.min()),1),
                 "R_median_par_trimestre": round(float(pt.median()),1)})
rg = pd.DataFrame(rows); rg.to_csv(os.path.join(RESULTS,"36_regularite.csv"), index=False)
print(rg.to_string(index=False))

# ---------------------------------------------------------------- choix
RETENU = ("B_equilibre", 2.0, 1.5, 3.0)
print(f"\n>>> Reglage retenu par defaut : {RETENU[0]} "
      f"(seuil {RETENU[1]} ATR, stop {RETENU[2]} ATR, suiveur {RETENU[3]} ATR)")

print("\n" + "="*115)
print("### Classement des actifs avec le reglage retenu ###\n")
rows = []
for sym in FE:
    T = trades(RETENU[1], RETENU[2], RETENU[3], syms=[sym])
    if len(T) < 15: continue
    R = T["R"].values
    g = FE[sym]
    up = (g["close"] > g["sma_trend"]).fillna(False).values
    m = ((g["close"] > g["sma_trend"]) & (g["ext_bt"] > RETENU[1])).fillna(False)
    taux = float(m.sum())/max(up.sum(),1)
    es = []
    for seed in range(40):
        rng = np.random.default_rng(seed)
        h = g.copy(); h["sig_long"] = up & (rng.random(len(g)) < taux)
        cfg = B.Config(trend_len=200, stop_atr=RETENU[2], target_r=0.0, trail_atr=RETENU[3],
                       max_bars=40, confirm=False, exit_on_mean=False, allow_short=False,
                       fee_bps=FEE, slip_bps=FEE)
        Ta = B.run_panel(h, cfg, presignal=True)
        if len(Ta) > 10: es.append(float(Ta["R"].mean()))
    med = float(np.median(es)) if es else np.nan
    T2 = T.sort_values("date_entree").reset_index(drop=True); mid = len(T2)//2
    rows.append({"actif": sym, "annees": round((g["date"].max()-g["date"].min()).days/365.25,1),
                 "n_trades": len(R), "win_rate": round(float((R>0).mean()*100),1),
                 "esperance_R": round(float(R.mean()),3),
                 "profit_factor": round(float(R[R>0].sum()/abs(R[R<=0].sum())),2),
                 "t_stat": round(float(R.mean()/(R.std(ddof=1)/np.sqrt(len(R)))),2),
                 "R_par_an": round(float(R.sum()/((g["date"].max()-g["date"].min()).days/365.25)),1),
                 "alea_R": round(med,3), "apport_signal_R": round(float(R.mean())-med,3),
                 "bat_alea": int(np.sum([e < R.mean() for e in es])),
                 "esp_1re_moitie": round(float(T2["R"][:mid].mean()),3),
                 "esp_2e_moitie": round(float(T2["R"][mid:].mean()),3),
                 "p_boot": round(S.block_bootstrap_pvalue(pd.Series(R), 8, 4000),4)})
cl = pd.DataFrame(rows).sort_values("apport_signal_R", ascending=False)
cl.to_csv(os.path.join(RESULTS,"37_classement_final.csv"), index=False)
print(cl.to_string(index=False))
print("\n  Classe par APPORT DU SIGNAL (esperance moins entree aleatoire),")
print("  pas par rendement brut : c'est la seule colonne qui mesure la regle.")
