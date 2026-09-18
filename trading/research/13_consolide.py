"""Verification croisee sur ETH, puis tableau de resultats consolide."""
from __future__ import annotations

import json, os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import data as D, features as F, backtest as B, stats as S  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
panel = pd.read_parquet(os.path.join(D.OUT, "panel_daily.parquet"))

BASE = B.Config(stop_atr=2.0, confirm=False, exit_on_mean=False, target_r=0.0,
                trail_atr=2.0, max_bars=40, allow_short=False)

def prep(raw, fee):
    f = F.build_panel_features(raw, 400)
    g = B.generate_signals(f[["symbol","date","open","high","low","close","atr14"]], BASE)
    g["sig_short"] = False
    return g

def run(g, mask, fee, a=None, b=None):
    h = g.copy(); h["sig_long"] = mask.fillna(False).values
    cfg = B.Config(stop_atr=2.0, confirm=False, exit_on_mean=False, target_r=0.0,
                   trail_atr=2.0, max_bars=40, allow_short=False, fee_bps=fee, slip_bps=fee)
    t = B.run_panel(h, cfg, presignal=True)
    if len(t) and a:
        t = t[(t["date_entree"] >= pd.Timestamp(a)) & (t["date_entree"] <= pd.Timestamp(b))]
    return B.trade_stats(t), t

def alea_med(g, taux, fee, a=None, b=None, n=30):
    up = (g["close"] > g["sma_trend"]).fillna(False).values
    es = []
    for s in range(n):
        rng = np.random.default_rng(s)
        st, _ = run(g, pd.Series(up & (rng.random(len(g)) < taux)), fee, a, b)
        if st.get("n_trades", 0) > 15:
            es.append(st["esperance_R"])
    return es

REPLI = lambda g: (g["close"] > g["sma_trend"]) & (g["ext_bt"] < -1.0)
IMPUL = lambda g: (g["close"] > g["sma_trend"]) & (g["ext_bt"] > 1.5)

# --- verification croisee : ETH et SOL (cloture seule, stop evalue en cloture)
print("### Verification croisee sur ETH et SOL ###")
print("  Series sans OHLC : le stop ne peut etre evalue qu'en cloture.")
print("  Resultat indicatif, plus optimiste qu'en reel sur les meches.\n")
cross = []
for sym, label in (("ETH_CM", "ETH 2015-2026"), ("BTC_CM", "BTC CoinMetrics 2010-2026")):
    raw = panel[panel["symbol"] == sym]
    if len(raw) < 500:
        continue
    g = prep(raw, 10.0)
    for nom, fn in (("repli", REPLI), ("impulsion", IMPUL)):
        st, _ = run(g, fn(g), 10.0)
        taux = float(fn(g).fillna(False).sum()) / max((g["close"] > g["sma_trend"]).sum(), 1)
        es = alea_med(g, taux, 10.0)
        cross.append({"actif": label, "entree": nom, "n": st.get("n_trades"),
                      "win_rate": st.get("win_rate_pct"), "espR": st.get("esperance_R"),
                      "pf": st.get("profit_factor"),
                      "alea_median": round(float(np.median(es)), 4) if es else None,
                      "bat_alea": round(float(np.mean([e < st.get("esperance_R", -9) for e in es])), 2) if es else None})
cr = pd.DataFrame(cross)
cr.to_csv(os.path.join(RESULTS, "20_verif_croisee_crypto.csv"), index=False)
print(cr.to_string(index=False))

# --- tableau consolide final
print("\n\n" + "=" * 120)
print("### TABLEAU CONSOLIDE : la bonne entree pour chaque classe d'actifs ###\n")
CONF = [
    ("Indice actions",   "SPX 1962-2018",    panel[(panel["symbol"]=="SPX") & (panel["date"]>="1962-01-01")], 5.0),
    ("Actions US",       "US500 2013-2018",  panel[panel["asset_class"]=="equity_single"], 5.0),
    ("Crypto",           "BTC 2012-2026",    panel[panel["symbol"]=="BTCUSD"], 10.0),
]
fin = []
for classe, label, raw, fee in CONF:
    g = prep(raw, fee)
    for nom, fn in (("Repli (mean reversion)", REPLI), ("Impulsion (momentum)", IMPUL)):
        st, t = run(g, fn(g), fee)
        if not st.get("n_trades"):
            continue
        taux = float(fn(g).fillna(False).sum()) / max((g["close"] > g["sma_trend"]).sum(), 1)
        es = alea_med(g, taux, fee)
        R = t["R"].values
        fin.append({
            "classe": classe, "univers": label, "entree": nom,
            "n_trades": st["n_trades"], "win_rate_pct": st["win_rate_pct"],
            "gain_moyen_R": st["gain_moyen_R"], "perte_moyenne_R": st["perte_moyenne_R"],
            "ratio_gain_perte": st["ratio_gain_perte"],
            "esperance_R": st["esperance_R"], "profit_factor": st["profit_factor"],
            "t_stat": st["t_stat_R"],
            "alea_espR_median": round(float(np.median(es)), 4) if es else None,
            "gain_vs_alea_R": round(st["esperance_R"] - float(np.median(es)), 4) if es else None,
            "bat_alea_sur_30": int(np.sum([e < st["esperance_R"] for e in es])) if es else None,
            "p_bootstrap": round(S.block_bootstrap_pvalue(pd.Series(R), 10, 4000), 4),
        })
F_ = pd.DataFrame(fin)
F_.to_csv(os.path.join(RESULTS, "21_consolide.csv"), index=False)
pd.set_option("display.width", 260)
print(F_.to_string(index=False))
print("\n-> results/21_consolide.csv")
