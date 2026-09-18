"""Quel actif crypto convient le mieux a VRC ?

On backteste le profil impulsion sur les 10 actifs, chacun sur TOUT son
historique disponible, avec la meme gestion et les memes couts.

Piege a eviter : tester 10 actifs et garder le meilleur est une selection.
Le meilleur d'un echantillon de 10 est flatteur meme si aucun n'a d'edge.
On regarde donc trois choses, pas une :
  1. l'esperance, mais corrigee du nombre d'actifs testes ;
  2. le fait de battre une entree ALEATOIRE dans le meme regime ;
  3. la stabilite dans le temps, moitie ancienne contre moitie recente.
"""
from __future__ import annotations

import os, sys, json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import data as D, features as F, backtest as B, stats as S  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
CRYPTO = pd.read_parquet("/tmp/mkt/clean/crypto_daily.parquet")

# BTC Bitstamp remonte a 2012, cinq ans avant Binance : on le garde a part
panel = pd.read_parquet(os.path.join(D.OUT, "panel_daily.parquet"))
btc_long = panel[panel["symbol"] == "BTCUSD"].copy()
btc_long["symbol"] = "BTC_2012"
CRYPTO = pd.concat([CRYPTO, btc_long[CRYPTO.columns.intersection(btc_long.columns)]],
                   ignore_index=True)

FEE = 10.0          # 10 bps par cote = 40 bps aller-retour, hypothese crypto
BASE = B.Config(stop_atr=2.0, target_r=0.0, trail_atr=2.0, max_bars=40,
                confirm=False, exit_on_mean=False, allow_short=False,
                fee_bps=FEE, slip_bps=FEE)
SEUIL_IMP = 1.5


def prep(g):
    f = F.build_panel_features(g, 300)[
        ["symbol", "date", "open", "high", "low", "close", "atr14"]]
    return B.generate_signals(f, BASE).assign(sig_short=False)


def run(g, mask):
    h = g.copy(); h["sig_long"] = mask.fillna(False).values
    t = B.run_panel(h, BASE, presignal=True)
    return B.trade_stats(t), t


def alea(g, taux, n=40):
    up = (g["close"] > g["sma_trend"]).fillna(False).values
    es = []
    for s in range(n):
        rng = np.random.default_rng(s)
        st, _ = run(g, pd.Series(up & (rng.random(len(g)) < taux)))
        if st.get("n_trades", 0) > 10:
            es.append(st["esperance_R"])
    return es


rows, trades_par_actif = [], {}
for sym, g0 in CRYPTO.groupby("symbol"):
    if len(g0) < 400:
        print(f"[ignore] {sym}: {len(g0)} barres, historique trop court")
        continue
    g = prep(g0.sort_values("date"))
    mask = (g["close"] > g["sma_trend"]) & (g["ext_bt"] > SEUIL_IMP)
    st, t = run(g, mask)
    if st.get("n_trades", 0) < 20:
        print(f"[ignore] {sym}: {st.get('n_trades',0)} trades seulement")
        continue
    trades_par_actif[sym] = t
    taux = float(mask.fillna(False).sum()) / max((g["close"] > g["sma_trend"]).sum(), 1)
    es = alea(g, taux)
    med_alea = float(np.median(es)) if es else np.nan
    bat = int(np.sum([e < st["esperance_R"] for e in es])) if es else 0

    # stabilite : premiere moitie contre seconde moitie du trades
    t2 = t.sort_values("date_entree").reset_index(drop=True)
    mid = len(t2) // 2
    e1 = float(t2["R"][:mid].mean()); e2 = float(t2["R"][mid:].mean())

    # achat-conservation sur la meme periode
    px = g.set_index("date")["close"]
    bh = S.perf_stats(px.pct_change().dropna(), 365)
    R = t["R"].values
    rows.append({
        "actif": sym,
        "debut": str(g["date"].min().date()), "fin": str(g["date"].max().date()),
        "annees": round((g["date"].max()-g["date"].min()).days/365.25, 1),
        "barres": len(g), "n_trades": st["n_trades"],
        "win_rate": st["win_rate_pct"], "gain_moy_R": st["gain_moyen_R"],
        "perte_moy_R": st["perte_moyenne_R"], "ratio_GP": st["ratio_gain_perte"],
        "esperance_R": st["esperance_R"], "profit_factor": st["profit_factor"],
        "t_stat": st["t_stat_R"], "R_total": st["R_total"],
        "alea_median_R": round(med_alea, 4), "bat_alea_sur_40": bat,
        "esp_1re_moitie": round(e1, 3), "esp_2e_moitie": round(e2, 3),
        "p_bootstrap": round(S.block_bootstrap_pvalue(pd.Series(R), 8, 4000), 4),
        "bh_CAGR_%": bh.get("CAGR_pct"), "bh_drawdown_%": bh.get("max_drawdown_pct"),
        "expo_%": round(float(t["bars"].sum()/len(g)*100), 1),
    })
    print(f"[ok] {sym:9s} {st['n_trades']:4d} trades  esp {st['esperance_R']:+.3f} R  "
          f"t={st['t_stat_R']}  bat alea {bat}/40")

out = pd.DataFrame(rows).sort_values("esperance_R", ascending=False)
out.to_csv(os.path.join(RESULTS, "23_classement_crypto.csv"), index=False)
pd.set_option("display.width", 260)
print("\n" + "="*130)
print("### Classement brut par esperance (a lire avec prudence : 10 actifs testes) ###\n")
cols = ["actif","annees","n_trades","win_rate","ratio_GP","esperance_R","profit_factor",
        "t_stat","alea_median_R","bat_alea_sur_40","esp_1re_moitie","esp_2e_moitie","p_bootstrap"]
print(out[cols].to_string(index=False))
for sym, t in trades_par_actif.items():
    t.to_csv(os.path.join(RESULTS, f"trades_crypto_{sym}.csv"), index=False)
