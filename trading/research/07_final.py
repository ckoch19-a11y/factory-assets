"""Analyse finale des deux configurations retenues.

Mode A "continuation" : trailing 2 ATR, stop 2 ATR, sans confirmation.
    -> choisi de facon repetee par le walk-forward depuis 1990.
Mode B "objectif"     : objectif 2R, stop 3 ATR, avec confirmation.
    -> taux de reussite plus eleve, moins de trades.

On mesure : par decennie, par actif, contre buy & hold, en Monte-Carlo,
et en Sharpe deflate du nombre de configurations essayees.
"""
from __future__ import annotations

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
                           target_r=0.0, trail_atr=2.0, max_bars=40),
    "B_objectif2R":   dict(stop_atr=3.0, confirm=True, exit_on_mean=False,
                           target_r=2.0, trail_atr=0.0, max_bars=20),
}

UNIVERSES = {
    "SPX 1962-2018 (indice)":
        panel[(panel["symbol"] == "SPX") & (panel["date"] >= "1962-01-01")],
    "US500 2013-2018 (500 actions)":
        panel[panel["asset_class"] == "equity_single"],
    "BTCUSD 2012-2026 (journalier)":
        panel[panel["symbol"] == "BTCUSD"],
    "BTCUSD 2012-2026 (4 heures)": p4h,
}

FEAT = {}
for k, v in UNIVERSES.items():
    f = F.build_panel_features(v, 400)
    FEAT[k] = f[["symbol", "date", "open", "high", "low", "close", "atr14"]]
    print(f"{k}: {len(FEAT[k]):,} barres")

# crypto : frais nettement plus eleves qu'en actions
FEES = {"BTCUSD 2012-2026 (journalier)": (10.0, 10.0),
        "BTCUSD 2012-2026 (4 heures)": (10.0, 10.0)}

summary, all_trades = [], {}
for mode, kw in MODES.items():
    for uni, f in FEAT.items():
        fee, slip = FEES.get(uni, (5.0, 5.0))
        cfg = B.Config(fee_bps=fee, slip_bps=slip, **kw)
        t = B.run_panel(f, cfg)
        all_trades[(mode, uni)] = t
        st = B.trade_stats(t)
        if not st.get("n_trades"):
            continue
        eq = B.equity_curve(t, risk_pct=1.0)
        ret = eq.pct_change().dropna()
        dd = float((eq / eq.cummax() - 1).min() * 100)
        summary.append({
            "mode": mode, "univers": uni,
            "n_trades": st["n_trades"], "win_rate_pct": st["win_rate_pct"],
            "gain_moyen_R": st["gain_moyen_R"], "perte_moyenne_R": st["perte_moyenne_R"],
            "ratio_gain_perte": st["ratio_gain_perte"],
            "esperance_R": st["esperance_R"], "profit_factor": st["profit_factor"],
            "t_stat_R": st["t_stat_R"], "R_total": st["R_total"],
            "duree_moy_barres": st["duree_moy_barres"],
            "capital_x_risque1pct": round(float(eq.iloc[-1] / 10000.0), 2),
            "drawdown_max_pct_risque1pct": round(dd, 2),
            "frais_bps_aller_retour": (fee + slip) * 2,
        })

S_ = pd.DataFrame(summary)
S_.to_csv(os.path.join(RESULTS, "06_final_summary.csv"), index=False)
pd.set_option("display.width", 260)
print("\n" + "=" * 130)
print("### SYNTHESE DES DEUX MODES ###\n")
print(S_.to_string(index=False))

# ------------------------------------------------------------- par decennie (SPX)
print("\n" + "=" * 130)
print("### Stabilite dans le temps : S&P 500 par decennie ###\n")
dec_rows = []
for mode in MODES:
    t = all_trades[(mode, "SPX 1962-2018 (indice)")]
    t = t.copy()
    t["decennie"] = (t["date_entree"].dt.year // 10 * 10).astype(int)
    for d, g in t.groupby("decennie"):
        dec_rows.append({"mode": mode, "decennie": f"{d}s", "n": len(g),
                         "win_rate": round(float((g["R"] > 0).mean() * 100), 1),
                         "esperance_R": round(float(g["R"].mean()), 3),
                         "R_total": round(float(g["R"].sum()), 1)})
dec = pd.DataFrame(dec_rows)
dec.to_csv(os.path.join(RESULTS, "07_par_decennie.csv"), index=False)
print(dec.pivot_table(index="decennie", columns="mode",
                      values=["n", "win_rate", "esperance_R"]).round(3).to_string())

# ------------------------------------------------------------- long vs short
print("\n" + "=" * 130)
print("### Decomposition long / short ###\n")
side_rows = []
for (mode, uni), t in all_trades.items():
    if not len(t):
        continue
    for side, g in t.groupby("side"):
        side_rows.append({"mode": mode, "univers": uni, "sens": side, "n": len(g),
                          "win_rate": round(float((g["R"] > 0).mean() * 100), 1),
                          "esperance_R": round(float(g["R"].mean()), 3)})
sd = pd.DataFrame(side_rows)
sd.to_csv(os.path.join(RESULTS, "08_long_short.csv"), index=False)
print(sd.to_string(index=False))

# ------------------------------------------------------------- Monte-Carlo + Sharpe deflate
print("\n" + "=" * 130)
print("### Robustesse statistique ###\n")
N_TRIALS = 40  # taille de la grille ayant servi a la selection
rob = []
for (mode, uni), t in all_trades.items():
    if len(t) < 50:
        continue
    R = t["R"].values
    rng = np.random.default_rng(11)
    # Monte-Carlo : on tire au sort l'ordre ET l'echantillon des trades
    sims = rng.choice(R, size=(3000, len(R)), replace=True)
    eq = np.cumprod(1 + 0.01 * sims, axis=1)
    dd = (eq / np.maximum.accumulate(eq, axis=1) - 1).min(axis=1)
    final = eq[:, -1]
    per_trade_sharpe = R.mean() / R.std(ddof=1) if R.std(ddof=1) > 0 else np.nan
    dsr = S.deflated_sharpe(per_trade_sharpe, len(R), N_TRIALS,
                            skew=float(pd.Series(R).skew()),
                            kurt=float(pd.Series(R).kurt() + 3))
    rob.append({
        "mode": mode, "univers": uni, "n_trades": len(R),
        "p_value_bootstrap": round(S.block_bootstrap_pvalue(pd.Series(R), 10, 4000), 4),
        "prob_perte_finale_MC": round(float((final < 1).mean()), 4),
        "drawdown_median_MC_pct": round(float(np.median(dd) * 100), 2),
        "drawdown_p95_MC_pct": round(float(np.percentile(dd, 5) * 100), 2),
        "sharpe_par_trade": round(float(per_trade_sharpe), 4),
        "prob_sharpe_reel_positif_deflate": round(dsr, 4),
    })
rb = pd.DataFrame(rob)
rb.to_csv(os.path.join(RESULTS, "09_robustesse.csv"), index=False)
print(rb.to_string(index=False))

# ------------------------------------------------------------- contre buy & hold
print("\n" + "=" * 130)
print("### Comparaison avec l'achat-conservation (meme periode) ###\n")
bh_rows = []
for uni in ("SPX 1962-2018 (indice)", "BTCUSD 2012-2026 (journalier)"):
    f = FEAT[uni]
    px = f.set_index("date")["close"]
    r = px.pct_change().dropna()
    bh = S.perf_stats(r)
    for mode in MODES:
        t = all_trades[(mode, uni)]
        if not len(t):
            continue
        eq = B.equity_curve(t, risk_pct=1.0)
        yrs = (t["date_sortie"].max() - t["date_entree"].min()).days / 365.25
        cagr = eq.iloc[-1] ** (1 / yrs) - 1
        dd = float((eq / eq.cummax() - 1).min())
        bh_rows.append({
            "univers": uni, "approche": f"strategie {mode} (risque 1%/trade)",
            "CAGR_pct": round(cagr * 100, 2),
            "drawdown_max_pct": round(dd * 100, 2),
            "MAR": round(cagr / abs(dd), 2) if dd < 0 else None,
            "temps_en_position_pct": round(
                float(t["bars"].sum() / len(f[f.symbol == f.symbol.iloc[0]]) * 100), 1),
        })
    bh_rows.append({"univers": uni, "approche": "achat-conservation",
                    "CAGR_pct": bh["CAGR_pct"], "drawdown_max_pct": bh["max_drawdown_pct"],
                    "MAR": bh["MAR"], "temps_en_position_pct": 100.0})
bhd = pd.DataFrame(bh_rows)
bhd.to_csv(os.path.join(RESULTS, "10_vs_buy_and_hold.csv"), index=False)
print(bhd.to_string(index=False))

for (mode, uni), t in all_trades.items():
    if len(t):
        safe = uni.split()[0].replace("/", "_")
        t.to_csv(os.path.join(RESULTS, f"trades_{mode}_{safe}.csv"), index=False)

with open(os.path.join(RESULTS, "06_final_meta.json"), "w") as fh:
    json.dump({"modes": MODES, "n_trials_selection": N_TRIALS,
               "frais_bps": {k: list(v) for k, v in FEES.items()},
               "frais_defaut_bps": [5.0, 5.0]}, fh, indent=2)
print("\n-> results/06_final_summary.csv et fichiers associes")
