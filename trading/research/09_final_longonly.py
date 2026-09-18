"""Analyse finale de la strategie retenue : LONG uniquement.

Le cote short a ete ecarte sur preuve (voir 08_shorts.py : 0/36
configurations rentables en actions). Il reste disponible en option pour
le crypto, ou il est positif, mais sans validation hors echantillon.
"""
from __future__ import annotations

import itertools
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import data as D, features as F, stats as S, backtest as B  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
panel = pd.read_parquet(os.path.join(D.OUT, "panel_daily.parquet"))
p4h = pd.read_parquet(os.path.join(D.OUT, "panel_4h.parquet"))

MODES = {
    "A_continuation": dict(stop_atr=2.0, confirm=False, exit_on_mean=False,
                           target_r=0.0, trail_atr=2.0, max_bars=40, allow_short=False),
    "B_objectif2R":   dict(stop_atr=3.0, confirm=True, exit_on_mean=False,
                           target_r=2.0, trail_atr=0.0, max_bars=20, allow_short=False),
}
UNIVERSES = {
    "SPX 1962-2018": panel[(panel["symbol"] == "SPX") & (panel["date"] >= "1962-01-01")],
    "US500 2013-2018": panel[panel["asset_class"] == "equity_single"],
    "BTC journalier 2012-2026": panel[panel["symbol"] == "BTCUSD"],
    "BTC 4h 2012-2026": p4h,
}
FEES = {"BTC journalier 2012-2026": 10.0, "BTC 4h 2012-2026": 10.0}

FEAT = {k: F.build_panel_features(v, 400)[
    ["symbol", "date", "open", "high", "low", "close", "atr14"]] for k, v in UNIVERSES.items()}


def portefeuille(t: pd.DataFrame, max_pos: int = 10, risk_pct: float = 1.0,
                 start: float = 10000.0):
    """Simulation de portefeuille : au plus `max_pos` positions simultanees,
    risque fixe par position. Un signal arrivant a portefeuille plein est
    IGNORE (c'est ce qui se passe en vrai)."""
    if not len(t):
        return pd.Series(dtype=float), 0
    t = t.sort_values("date_entree").reset_index(drop=True)
    open_until, eq, pts, pris = [], start, [], 0
    realised = []
    for _, r in t.iterrows():
        d_in, d_out = r["date_entree"], r["date_sortie"]
        open_until = [x for x in open_until if x > d_in]
        if len(open_until) >= max_pos:
            continue
        open_until.append(d_out)
        realised.append((d_out, r["R"]))
        pris += 1
    realised.sort()
    for d_out, R in realised:
        eq *= (1 + (risk_pct / 100.0) * R)
        pts.append((d_out, eq))
    s = pd.Series([p[1] for p in pts], index=pd.DatetimeIndex([p[0] for p in pts]))
    return s, pris


# --- variance des Sharpe sur la grille, necessaire au Sharpe deflate -------
EXIT_SCHEMES = {
    "retour_moyenne":       dict(exit_on_mean=True,  target_r=0.0, trail_atr=0.0, max_bars=20),
    "retour_moyenne_ou_2R": dict(exit_on_mean=True,  target_r=2.0, trail_atr=0.0, max_bars=20),
    "objectif_2R":          dict(exit_on_mean=False, target_r=2.0, trail_atr=0.0, max_bars=20),
    "trailing_2ATR":        dict(exit_on_mean=False, target_r=0.0, trail_atr=2.0, max_bars=40),
    "temps_10_barres":      dict(exit_on_mean=False, target_r=0.0, trail_atr=0.0, max_bars=10),
}
print("Distribution des Sharpe par trade sur la grille (pour le Sharpe deflate)...")
grid_sr = []
for e, s_, c_ in itertools.product(EXIT_SCHEMES, (1.5, 2.0, 2.5, 3.0), (True, False)):
    kw = dict(stop_atr=s_, confirm=c_, allow_short=False, **EXIT_SCHEMES[e])
    t = B.run_panel(FEAT["SPX 1962-2018"], B.Config(**kw))
    if len(t) > 30 and t["R"].std(ddof=1) > 0:
        grid_sr.append(t["R"].mean() / t["R"].std(ddof=1))
V = float(np.var(grid_sr, ddof=1))
print(f"  {len(grid_sr)} configurations, variance des Sharpe = {V:.6f}")

rows, robust, trades_store = [], [], {}
for mode, kw in MODES.items():
    for uni, f in FEAT.items():
        fee = FEES.get(uni, 5.0)
        t = B.run_panel(f, B.Config(fee_bps=fee, slip_bps=fee, **kw))
        trades_store[(mode, uni)] = t
        st = B.trade_stats(t)
        if not st.get("n_trades"):
            continue
        multi = f["symbol"].nunique() > 1
        eq, pris = portefeuille(t, max_pos=10 if multi else 1)
        dd = float((eq / eq.cummax() - 1).min() * 100) if len(eq) else np.nan
        rows.append({
            "mode": mode, "univers": uni,
            "n_signaux": st["n_trades"], "n_pris_portefeuille": pris,
            "win_rate_pct": st["win_rate_pct"],
            "gain_moyen_R": st["gain_moyen_R"], "perte_moyenne_R": st["perte_moyenne_R"],
            "ratio_gain_perte": st["ratio_gain_perte"],
            "esperance_R": st["esperance_R"], "profit_factor": st["profit_factor"],
            "t_stat_R": st["t_stat_R"], "R_total": st["R_total"],
            "duree_moy_barres": st["duree_moy_barres"],
            "capital_final_x": round(float(eq.iloc[-1] / 10000.0), 2) if len(eq) else None,
            "drawdown_max_pct": round(dd, 2) if np.isfinite(dd) else None,
            "cout_aller_retour_bps": fee * 4,
        })
        R = t["R"].values
        sr = R.mean() / R.std(ddof=1)
        rng = np.random.default_rng(11)
        sims = rng.choice(R, size=(4000, len(R)), replace=True)
        e2 = np.cumprod(1 + 0.01 * sims, axis=1)
        ddm = (e2 / np.maximum.accumulate(e2, axis=1) - 1).min(axis=1)
        robust.append({
            "mode": mode, "univers": uni, "n_trades": len(R),
            "p_value_bootstrap": round(S.block_bootstrap_pvalue(pd.Series(R), 10, 5000), 4),
            "prob_perte_finale_MC": round(float((e2[:, -1] < 1).mean()), 4),
            "drawdown_median_MC_pct": round(float(np.median(ddm) * 100), 2),
            "drawdown_p95_MC_pct": round(float(np.percentile(ddm, 5) * 100), 2),
            "sharpe_par_trade": round(float(sr), 4),
            "P_sharpe_reel_positif": round(S.deflated_sharpe(
                sr, len(R), len(grid_sr), V,
                skew=float(pd.Series(R).skew()),
                kurt=float(pd.Series(R).kurt() + 3)), 4),
        })

df = pd.DataFrame(rows)
rb = pd.DataFrame(robust)
df.to_csv(os.path.join(RESULTS, "12_final_longonly.csv"), index=False)
rb.to_csv(os.path.join(RESULTS, "13_robustesse_longonly.csv"), index=False)
pd.set_option("display.width", 250)
print("\n" + "=" * 125)
print("### STRATEGIE FINALE - LONG UNIQUEMENT ###\n")
print(df.to_string(index=False))
print("\n### Robustesse ###\n")
print(rb.to_string(index=False))

# --- annee par annee sur le SPX -------------------------------------------
print("\n" + "=" * 125)
print("### S&P 500 : resultat par decennie, long uniquement ###\n")
dr = []
for mode in MODES:
    t = trades_store[(mode, "SPX 1962-2018")].copy()
    t["dec"] = (t["date_entree"].dt.year // 10 * 10)
    for d, g in t.groupby("dec"):
        dr.append({"mode": mode, "decennie": f"{d}s", "n": len(g),
                   "win_rate": round(float((g["R"] > 0).mean() * 100), 1),
                   "esperance_R": round(float(g["R"].mean()), 3),
                   "R_total": round(float(g["R"].sum()), 1)})
dec = pd.DataFrame(dr)
dec.to_csv(os.path.join(RESULTS, "14_par_decennie_longonly.csv"), index=False)
print(dec.pivot_table(index="decennie", columns="mode",
                      values=["n", "win_rate", "esperance_R", "R_total"]).round(3).to_string())

# --- contre achat-conservation --------------------------------------------
print("\n" + "=" * 125)
print("### Contre l'achat-conservation ###\n")
bh = []
for uni in ("SPX 1962-2018", "BTC journalier 2012-2026"):
    f = FEAT[uni]
    r = f.set_index("date")["close"].pct_change().dropna()
    b0 = S.perf_stats(r)
    for mode in MODES:
        t = trades_store[(mode, uni)]
        eq, _ = portefeuille(t, max_pos=1)
        yrs = (t["date_sortie"].max() - t["date_entree"].min()).days / 365.25
        cagr = eq.iloc[-1] ** (1 / yrs) - 1
        d = float((eq / eq.cummax() - 1).min())
        bh.append({"univers": uni, "approche": f"{mode} (risque 1%/trade)",
                   "CAGR_pct": round(cagr * 100, 2), "drawdown_max_pct": round(d * 100, 2),
                   "MAR": round(cagr / abs(d), 2),
                   "temps_expose_pct": round(float(t["bars"].sum() / len(f) * 100), 1)})
    bh.append({"univers": uni, "approche": "achat-conservation",
               "CAGR_pct": b0["CAGR_pct"], "drawdown_max_pct": b0["max_drawdown_pct"],
               "MAR": b0["MAR"], "temps_expose_pct": 100.0})
bhd = pd.DataFrame(bh)
bhd.to_csv(os.path.join(RESULTS, "15_vs_buyhold_longonly.csv"), index=False)
print(bhd.to_string(index=False))

for (mode, uni), t in trades_store.items():
    if len(t):
        t.to_csv(os.path.join(RESULTS, f"trades_LO_{mode}_{uni.split()[0]}.csv"), index=False)
with open(os.path.join(RESULTS, "12_final_meta.json"), "w") as fh:
    json.dump({"modes": MODES, "variance_sharpe_grille": V,
               "n_configs_grille": len(grid_sr)}, fh, indent=2)
