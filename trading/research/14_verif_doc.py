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
chk("500 actions repli : 11 124 trades", pick("US500", "Repli").n_trades == 11124, "")

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


# ---------------------------------------------------------------- crypto
cl = pd.read_csv(os.path.join(R, "37_classement_final.csv")).set_index("actif")
chk("BTC : apport du signal +0,845 R", abs(cl.loc["BTC", "apport_signal_R"] - 0.845) < 1e-3,
    cl.loc["BTC", "apport_signal_R"])
chk("BTC : deux moities positives (1,492 / 1,060)",
    abs(cl.loc["BTC", "esp_1re_moitie"] - 1.492) < 1e-3 and abs(cl.loc["BTC", "esp_2e_moitie"] - 1.060) < 1e-3,
    f'{cl.loc["BTC","esp_1re_moitie"]} / {cl.loc["BTC","esp_2e_moitie"]}')
chk("SOL : effondrement 2e moitie a -0,160 R", abs(cl.loc["SOL", "esp_2e_moitie"] + 0.160) < 1e-3,
    cl.loc["SOL", "esp_2e_moitie"])
chk("ZEC et TRX sous le hasard",
    cl.loc["ZEC", "apport_signal_R"] < 0 and cl.loc["TRX", "apport_signal_R"] < 0,
    f'ZEC {cl.loc["ZEC","apport_signal_R"]}, TRX {cl.loc["TRX","apport_signal_R"]}')

sy = pd.read_csv(os.path.join(R, "29_sim_synthese.csv")).set_index("config")
chk("Reglage B : 381 trades, esperance +0,693 R",
    int(sy.loc["B_equilibre", "n_signaux"]) == 381 and abs(sy.loc["B_equilibre", "esperance_R"] - 0.693) < 1e-3,
    f'{int(sy.loc["B_equilibre","n_signaux"])} / {sy.loc["B_equilibre","esperance_R"]}')
chk("Reglage B : reussite 36,5 %, CAGR 27,0 %, creux -20,3 %",
    abs(sy.loc["B_equilibre", "win_rate"] - 36.5) < 0.05 and abs(sy.loc["B_equilibre", "CAGR_%"] - 27.0) < 0.05
    and abs(sy.loc["B_equilibre", "dd_max_%"] + 20.3) < 0.05, "ok")

rg = pd.read_csv(os.path.join(R, "36_regularite.csv")).set_index("config")
chk("B : 8 annees positives sur 9, pire annee -0,6 R",
    rg.loc["B_equilibre", "annees_positives"] == "8/9" and abs(rg.loc["B_equilibre", "pire_annee_R"] + 0.6) < 0.05,
    rg.loc["B_equilibre", "annees_positives"])
chk("C et D ont un trimestre median NEGATIF",
    rg.loc["C_laisse_courir", "R_median_par_trimestre"] < 0 and rg.loc["D_agressive", "R_median_par_trimestre"] < 0,
    f'C {rg.loc["C_laisse_courir","R_median_par_trimestre"]}, D {rg.loc["D_agressive","R_median_par_trimestre"]}')

tp = pd.read_csv(os.path.join(R, "38_objectif_fixe.csv")).set_index("gestion")
chk("Objectif 2R divise l'esperance par ~4,4",
    abs(tp.loc["suiveur seul (retenu)", "esperance_R"] / tp.loc["suiveur + objectif 2R", "esperance_R"] - 4.44) < 0.2,
    round(float(tp.loc["suiveur seul (retenu)", "esperance_R"] / tp.loc["suiveur + objectif 2R", "esperance_R"]), 2))

pr = json.load(open(os.path.join(R, "39_projection.json")))
chk("Projection : erreur mediane 0,65 % du prix", abs(pr["err_median_pct"] - 0.65) < 0.02, pr["err_median_pct"])

sf = pd.read_csv(os.path.join(R, "27_surface_etendue.csv"))
su = pd.read_csv(os.path.join(R, "26_surface_crypto.csv"))
chk("216 configurations positives en apprentissage ET verification",
    len(su) == 216 and int(((su.IS_esp > 0) & (su.OOS_esp > 0)).sum()) == 216,
    f"{int(((su.IS_esp>0)&(su.OOS_esp>0)).sum())}/{len(su)}")

ru = pd.read_csv(os.path.join(R, "33_sim_ruine.csv"))
b10 = ru[(ru.config == "B_equilibre") & (ru["risque_par_trade_%"] == 10.0)].iloc[0]
chk("A 10 % de risque : creux median -86,5 %, ruine 34,1 %",
    abs(b10["dd_median_%"] + 86.5) < 0.2 and abs(b10["prob_perdre_moitie"] - 0.341) < 0.005, "ok")

print(f"{len(ok)} chiffres conformes, {len(ko)} ecart(s)")
for x in ok:
    print("  OK    ", x)
for x in ko:
    print("  ECART ", x)
sys.exit(1 if ko else 0)
