"""Batterie de simulations sur les configurations candidates.

Une esperance elevee ne suffit pas a choisir. Ce qui decide, c'est ce qui
arrive quand on la vit vraiment : positions simultanees, sequences de pertes,
mauvaise annee, frais plus lourds que prevu, et taille de position trop
grande.

Contenu :
  1. portefeuille reel (positions simultanees plafonnees, pas de sequentiel)
  2. Monte-Carlo par reechantillonnage : distribution du resultat et du creux
  3. Monte-Carlo par permutation d'ordre : le resultat depend-il de l'ordre ?
  4. annee par annee, marches haussiers et baissiers separes
  5. sensibilite aux frais
  6. risque de ruine selon la fraction risquee
  7. serie perdante la plus longue attendue
"""
from __future__ import annotations

import os, sys, json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import data as D, features as F, backtest as B, stats as S  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
CRYPTO = pd.read_parquet("/tmp/mkt/clean/crypto_daily.parquet")

CANDIDATS = {
    "A_actuelle":   dict(seuil=1.5, stop=2.0, trail=2.0, maxb=40),
    "B_equilibre":  dict(seuil=2.0, stop=1.5, trail=3.0, maxb=40),
    "C_laisse_courir": dict(seuil=2.0, stop=1.0, trail=6.0, maxb=40),
    "D_agressive":  dict(seuil=1.5, stop=1.0, trail=0.0, maxb=40),
}

def build(fee):
    FE = {}
    for sym, g in CRYPTO.groupby("symbol"):
        f = F.build_panel_features(g.sort_values("date"), 300)[
            ["symbol","date","open","high","low","close","atr14"]]
        FE[sym] = B.generate_signals(f, B.Config(trend_len=200, fee_bps=fee, slip_bps=fee)).assign(sig_short=False)
    return FE

FE = build(10.0)

def trades(p, fee=10.0, FEx=None):
    src = FEx or FE
    cfg = B.Config(trend_len=200, stop_atr=p["stop"], target_r=0.0, trail_atr=p["trail"],
                   max_bars=p["maxb"], confirm=False, exit_on_mean=False, allow_short=False,
                   fee_bps=fee, slip_bps=fee)
    parts = []
    for sym, g in src.items():
        h = g.copy()
        h["sig_long"] = ((g["close"] > g["sma_trend"]) & (g["ext_bt"] > p["seuil"])).fillna(False).values
        t = B.run_panel(h, cfg, presignal=True)
        if len(t): parts.append(t)
    return pd.concat(parts, ignore_index=True).sort_values("date_entree").reset_index(drop=True)

def portefeuille(T, max_pos=5, risk=0.01, start=10000.0):
    """Positions simultanees plafonnees. Un signal arrivant a portefeuille
    plein est ignore, comme dans la realite."""
    ouvertes, realises, pris, rejetes = [], [], 0, 0
    for _, r in T.iterrows():
        ouvertes = [x for x in ouvertes if x > r["date_entree"]]
        if len(ouvertes) >= max_pos:
            rejetes += 1; continue
        ouvertes.append(r["date_sortie"]); realises.append((r["date_sortie"], r["R"])); pris += 1
    realises.sort()
    eq, courbe = start, []
    for d, R in realises:
        eq *= (1 + risk * R); courbe.append((d, eq))
    s = pd.Series([c[1] for c in courbe], index=pd.DatetimeIndex([c[0] for c in courbe]))
    dd = float((s/s.cummax()-1).min()*100) if len(s) else np.nan
    yrs = (s.index[-1]-s.index[0]).days/365.25 if len(s) > 1 else 1
    cagr = (s.iloc[-1]/start)**(1/yrs)-1 if len(s) and s.iloc[-1] > 0 else np.nan
    return {"pris": pris, "rejetes": rejetes, "capital_x": round(float(s.iloc[-1]/start),2) if len(s) else None,
            "CAGR_%": round(cagr*100,1), "dd_max_%": round(dd,1),
            "MAR": round(cagr/abs(dd/100),2) if dd < 0 else None}, s

def serie_perdante_max(R):
    m = c = 0
    for r in R:
        c = c+1 if r <= 0 else 0
        m = max(m, c)
    return m

rows, mc_rows, an_rows, cost_rows, ruine_rows = [], [], [], [], []
courbes = {}
for nom, p in CANDIDATS.items():
    T = trades(p); R = T["R"].values
    pf, courbe = portefeuille(T, max_pos=5)
    courbes[nom] = courbe
    rows.append({"config": nom, **p, "n_signaux": len(T),
                 "win_rate": round(float((R>0).mean()*100),1),
                 "esperance_R": round(float(R.mean()),3),
                 "gain_moy_R": round(float(R[R>0].mean()),2),
                 "perte_moy_R": round(float(R[R<=0].mean()),2),
                 "profit_factor": round(float(R[R>0].sum()/abs(R[R<=0].sum())),2),
                 "t_stat": round(float(R.mean()/(R.std(ddof=1)/np.sqrt(len(R)))),2),
                 "duree_moy_j": round(float(T["bars"].mean()),1),
                 "serie_perdante_max": serie_perdante_max(R), **pf})

    # --- Monte-Carlo : reechantillonnage avec remise
    rng = np.random.default_rng(42)
    n = len(R)
    sims = rng.choice(R, size=(5000, n), replace=True)
    eq = np.cumprod(1 + 0.01*sims, axis=1)
    dd = (eq/np.maximum.accumulate(eq, axis=1)-1).min(axis=1)*100
    fin = eq[:, -1]
    # --- Monte-Carlo : meme trades, ordre permute (le resultat final est
    #     identique, seul le CHEMIN change : c'est le creux qui varie)
    perm = np.array([rng.permutation(R) for _ in range(3000)])
    eqp = np.cumprod(1 + 0.01*perm, axis=1)
    ddp = (eqp/np.maximum.accumulate(eqp, axis=1)-1).min(axis=1)*100
    mc_rows.append({"config": nom,
                    "MC_prob_perte": round(float((fin<1).mean()),4),
                    "MC_capital_median_x": round(float(np.median(fin)),2),
                    "MC_capital_p5_x": round(float(np.percentile(fin,5)),2),
                    "MC_capital_p95_x": round(float(np.percentile(fin,95)),2),
                    "MC_dd_median_%": round(float(np.median(dd)),1),
                    "MC_dd_p95_%": round(float(np.percentile(dd,5)),1),
                    "MC_dd_pire_%": round(float(dd.min()),1),
                    "PERM_dd_median_%": round(float(np.median(ddp)),1),
                    "PERM_dd_p95_%": round(float(np.percentile(ddp,5)),1),
                    "prob_serie_perdante_sup_15": round(float(np.mean(
                        [serie_perdante_max(s) > 15 for s in sims[:600]])),3)})

    # --- annee par annee
    T2 = T.copy(); T2["an"] = T2["date_entree"].dt.year
    for an, g in T2.groupby("an"):
        an_rows.append({"config": nom, "annee": int(an), "n": len(g),
                        "win_rate": round(float((g["R"]>0).mean()*100),1),
                        "esperance_R": round(float(g["R"].mean()),3),
                        "R_total": round(float(g["R"].sum()),1)})

    # --- sensibilite aux frais
    for fee in (0.0, 5.0, 10.0, 20.0, 40.0):
        FEx = FE if fee == 10.0 else build(fee)
        Tf = trades(p, fee=fee, FEx=FEx)
        cost_rows.append({"config": nom, "frais_bps_AR": fee*4,
                          "esperance_R": round(float(Tf["R"].mean()),3),
                          "n": len(Tf)})

    # --- risque de ruine par taille de position
    for risk in (0.005, 0.01, 0.02, 0.05, 0.10):
        eqr = np.cumprod(1 + risk*sims, axis=1)
        ruine = float((eqr.min(axis=1) < 0.5).mean())     # -50 % = abandon
        ddr = (eqr/np.maximum.accumulate(eqr, axis=1)-1).min(axis=1)*100
        ruine_rows.append({"config": nom, "risque_par_trade_%": risk*100,
                           "prob_perdre_moitie": round(ruine,4),
                           "dd_median_%": round(float(np.median(ddr)),1),
                           "capital_median_x": round(float(np.median(eqr[:,-1])),2)})
    print(f"[{nom}] fait", flush=True)

pd.set_option("display.width", 260)
R1 = pd.DataFrame(rows); R1.to_csv(os.path.join(RESULTS,"29_sim_synthese.csv"), index=False)
R2 = pd.DataFrame(mc_rows); R2.to_csv(os.path.join(RESULTS,"30_sim_montecarlo.csv"), index=False)
R3 = pd.DataFrame(an_rows); R3.to_csv(os.path.join(RESULTS,"31_sim_annees.csv"), index=False)
R4 = pd.DataFrame(cost_rows); R4.to_csv(os.path.join(RESULTS,"32_sim_frais.csv"), index=False)
R5 = pd.DataFrame(ruine_rows); R5.to_csv(os.path.join(RESULTS,"33_sim_ruine.csv"), index=False)

print("\n"+"="*135); print("### 1. Synthese, portefeuille 5 positions maximum, risque 1 % ###\n")
print(R1.to_string(index=False))
print("\n"+"="*135); print("### 2. Monte-Carlo (5 000 tirages) ###\n")
print(R2.to_string(index=False))
print("\n"+"="*135); print("### 3. Annee par annee ###\n")
print(R3.pivot_table(index="annee", columns="config", values="esperance_R").round(3).to_string())
print("\n  Nombre de trades par an :")
print(R3.pivot_table(index="annee", columns="config", values="n").to_string())
print("\n"+"="*135); print("### 4. Sensibilite aux frais ###\n")
print(R4.pivot_table(index="frais_bps_AR", columns="config", values="esperance_R").round(3).to_string())
print("\n"+"="*135); print("### 5. Risque de ruine selon la taille de position ###\n")
print(R5.pivot_table(index="risque_par_trade_%", columns="config", values="prob_perdre_moitie").round(4).to_string())
print("\n  Creux median (%) :")
print(R5.pivot_table(index="risque_par_trade_%", columns="config", values="dd_median_%").round(1).to_string())
