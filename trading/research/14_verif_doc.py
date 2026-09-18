"""Verifie que chaque chiffre cite dans docs/ correspond aux CSV de results/.

A relancer apres toute modification de l'etude. Une documentation qui derive
des resultats est pire qu'une documentation absente.
"""
from __future__ import annotations

import json
import os
import sys

import pandas as pd

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
ok, ko = [], []


def chk(label, cond, got):
    (ok if cond else ko).append(f"{label} -> {got}")


c = pd.read_csv(os.path.join(R, "21_consolide.csv"))
pick = lambda u, e: c[(c.univers.str.contains(u)) & (c.entree.str.contains(e))].iloc[0]

r = pick("SPX", "Repli")
chk("S&P 500 repli : esperance +0,331 R", abs(r.esperance_R - 0.3309) < 1e-3, r.esperance_R)
chk("S&P 500 repli : reussite 48,45 %", abs(r.win_rate_pct - 48.45) < 0.01, r.win_rate_pct)
chk("S&P 500 repli : 291 trades", r.n_trades == 291, r.n_trades)
chk("S&P 500 repli : PF 2,01", abs(r.profit_factor - 2.005) < 0.01, r.profit_factor)

r = pick("BTC", "Impulsion")
chk("BTC impulsion : esperance +0,736 R", abs(r.esperance_R - 0.736) < 1e-3, r.esperance_R)
chk("BTC impulsion : reussite 56,72 %", abs(r.win_rate_pct - 56.72) < 0.01, r.win_rate_pct)
chk("BTC impulsion : 134 trades", r.n_trades == 134, r.n_trades)
chk("BTC impulsion : PF 3,85", abs(r.profit_factor - 3.852) < 0.01, r.profit_factor)
chk("500 actions repli : 11 293 trades", pick("US500", "Repli").n_trades == 11293, "")

wf = json.load(open(os.path.join(R, "05_walkforward_meta.json")))
m = wf["stats_walkforward"]
chk("Walk-forward : 314 trades", m["n_trades"] == 314, m["n_trades"])
chk("Walk-forward : reussite 45,2 %", abs(m["win_rate_pct"] - 45.22) < 0.01, m["win_rate_pct"])
chk("Walk-forward : esperance +0,212 R", abs(m["esperance_R"] - 0.2118) < 1e-3, m["esperance_R"])
chk("Walk-forward : t = 3,12", abs(m["t_stat_R"] - 3.12) < 0.01, m["t_stat_R"])
chk("Walk-forward : p = 0,0042", abs(wf["p_value_bootstrap"] - 0.0042) < 1e-3, wf["p_value_bootstrap"])

d = json.load(open(os.path.join(R, "00_data_summary.json")))
chk("Panel : 701 445 barres", d["total_bars"] == 701445, d["total_bars"])
chk("Panel : 507 instruments", d["symbols"] == 507, d["symbols"])
chk("Panel : 1950 -> 2026",
    d["date_min"] == "1950-01-03" and d["date_max"] == "2026-09-18",
    f'{d["date_min"]}..{d["date_max"]}')

s = json.load(open(os.path.join(R, "11_shorts_meta.json")))
chk("Short : 0 configuration rentable sur 36",
    s["n_configs"] == 36 and s["n_valides_IS"] == 0, f'{s["n_valides_IS"]}/{s["n_configs"]}')

rb = pd.read_csv(os.path.join(R, "13_robustesse_longonly.csv"))
v = rb[(rb["mode"] == "A_continuation") & (rb.univers.str.contains("SPX"))].iloc[0]
chk("Sharpe deflate S&P 500 : 95,8 %", abs(v.P_sharpe_reel_positif - 0.9583) < 1e-3,
    v.P_sharpe_reel_positif)
v = rb[rb.univers.str.contains("4h") & (rb["mode"] == "A_continuation")].iloc[0]
chk("BTC 4 h : Sharpe negatif", v.sharpe_par_trade < 0, v.sharpe_par_trade)

ce = pd.read_csv(os.path.join(R, "17_controle_entree.csv"))
chk("S&P 500 bat 30 tirages aleatoires sur 30",
    ce[ce.univers.str.contains("SPX")].iloc[0].p_value_vs_alea == 0.0, "30/30")
chk("BTC repli ne bat pas le hasard",
    ce[ce.univers.str.contains("BTC")].iloc[0].gain_vs_alea_R < 0,
    ce[ce.univers.str.contains("BTC")].iloc[0].gain_vs_alea_R)

cv = pd.read_csv(os.path.join(R, "18_crypto_variantes.csv"))
chk("BTC impulsion hors echantillon : +0,399 R",
    abs(cv[cv.variante.str.contains("1.5")].iloc[0].OOS_espR - 0.3992) < 1e-3, "")

dec = pd.read_csv(os.path.join(R, "14_par_decennie_longonly.csv"))
v = dec[(dec["mode"] == "A_continuation") & (dec.decennie == "1970s")].iloc[0]
chk("Annees 1970 negatives : -0,185 R", abs(v.esperance_R + 0.185) < 1e-3, v.esperance_R)

print(f"{len(ok)} chiffres conformes, {len(ko)} ecart(s)")
for x in ok:
    print("  OK    ", x)
for x in ko:
    print("  ECART ", x)
sys.exit(1 if ko else 0)
