"""Analyse groupee des 10 actifs Binance + correction pour tests multiples.

Un actif isole donne 50 a 85 trades : trop peu pour conclure. Mis en commun,
l'echantillon depasse 600 trades, et surtout la question devient la bonne :
"cette regle marche-t-elle sur le crypto ?" plutot que "quel actif a eu le
plus de chance ?".
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
BASE = B.Config(stop_atr=2.0, target_r=0.0, trail_atr=2.0, max_bars=40,
                confirm=False, exit_on_mean=False, allow_short=False,
                fee_bps=FEE, slip_bps=FEE)

FE = {}
for sym, g in CRYPTO.groupby("symbol"):
    f = F.build_panel_features(g.sort_values("date"), 300)[
        ["symbol","date","open","high","low","close","atr14"]]
    FE[sym] = B.generate_signals(f, BASE).assign(sig_short=False)

def trades(seuil=1.5, syms=None):
    out = []
    for sym, g in FE.items():
        if syms and sym not in syms: continue
        h = g.copy()
        h["sig_long"] = ((g["close"] > g["sma_trend"]) & (g["ext_bt"] > seuil)).fillna(False).values
        t = B.run_panel(h, BASE, presignal=True)
        if len(t): out.append(t)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()

T = trades()
st = B.trade_stats(T)
R = T["R"].values
print("### Echantillon groupe : 10 actifs crypto, 2017-2026 ###\n")
for k in ("n_trades","win_rate_pct","gain_moyen_R","perte_moyenne_R","ratio_gain_perte",
          "esperance_R","profit_factor","t_stat_R","duree_moy_barres","pire_trade_R"):
    print(f"  {k:20s} {st[k]}")
print(f"  motifs de sortie     {st['motifs']}")
print(f"  p-value bootstrap    {S.block_bootstrap_pvalue(pd.Series(R), 8, 6000):.4f}")

# --- correction pour tests multiples sur le classement par actif -----------
cl = pd.read_csv(os.path.join(RESULTS, "23_classement_crypto.csv"))
cl = cl[cl["actif"] != "BTC_2012"].copy()   # chevauche BTC, on ne compte pas deux fois
n = len(cl)
# Holm-Bonferroni sur les p-values bootstrap
cl = cl.sort_values("p_bootstrap").reset_index(drop=True)
cl["p_holm"] = [min(1.0, (n - i) * p) for i, p in enumerate(cl["p_bootstrap"])]
cl["significatif_5%"] = cl["p_holm"] < 0.05
print("\n" + "="*112)
print("### Correction Holm-Bonferroni : qui survit au fait qu'on ait teste 10 actifs ? ###\n")
print(cl[["actif","n_trades","esperance_R","t_stat","p_bootstrap","p_holm","significatif_5%"]].to_string(index=False))
print(f"\n  {int(cl['significatif_5%'].sum())}/{n} actifs restent significatifs apres correction.")
print("  Un actif non significatif seul n'est pas condamne : il manque de trades,")
print("  pas forcement d'edge. C'est le resultat groupe ci-dessus qui tranche.")

# --- proportion positive : test binomial ----------------------------------
from scipy.stats import binomtest
pos = int((cl["esperance_R"] > 0).sum())
bt = binomtest(pos, n, 0.5, alternative="greater")
print(f"\n  {pos}/{n} actifs a esperance positive. Sous l'hypothese 'aucun edge',")
print(f"  la probabilite d'en observer autant ou plus est de {bt.pvalue:.4f}.")

# --- correlation des trades entre actifs ----------------------------------
T2 = T.copy(); T2["mois"] = T2["date_entree"].dt.to_period("M")
piv = T2.pivot_table(index="mois", columns="symbol", values="R", aggfunc="mean")
cor = piv.corr().values
iu = np.triu_indices_from(cor, 1)
print(f"\n  Correlation moyenne des resultats mensuels entre actifs : {np.nanmean(cor[iu]):.2f}")
print("  Plus elle est basse, plus repartir sur plusieurs actifs reduit vraiment")
print("  le risque au lieu de le dupliquer.")

# --- concentration : le resultat tient-il sans les meilleurs trades ? -----
Rs = np.sort(R)
print("\n### Le resultat depend-il de quelques coups de chance ? ###")
for k in (0, 1, 3, 5, 10):
    if k == 0:
        print(f"  tous les trades                  esperance {R.mean():+.4f} R")
    else:
        print(f"  sans les {k:2d} meilleurs trades     esperance {Rs[:-k].mean():+.4f} R")

json.dump({"groupe": {k: v for k, v in st.items() if k != "motifs"},
           "motifs": st["motifs"],
           "actifs_significatifs_holm": int(cl["significatif_5%"].sum()),
           "actifs_positifs": pos, "n_actifs": n,
           "p_binomial": float(bt.pvalue),
           "correlation_moyenne_mensuelle": float(np.nanmean(cor[iu]))},
          open(os.path.join(RESULTS, "24_pool_crypto.json"), "w"), indent=2)
cl.to_csv(os.path.join(RESULTS, "25_holm_crypto.csv"), index=False)
T.to_csv(os.path.join(RESULTS, "trades_pool_crypto.csv"), index=False)
