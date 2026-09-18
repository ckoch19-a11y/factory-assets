"""Que faudrait-il pour tenir 1 % par jour ?

On ne discute pas d'opinion : on prend la meilleure configuration mesuree et
on calcule ce que l'objectif exige, puis ce qu'il coute.
"""
from __future__ import annotations
import os, sys, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import backtest as B  # noqa: E402
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")

print("### 1. Ce que represente 1 % par jour ###\n")
for j, lib in ((365,"jours calendaires"), (252,"jours ouvres")):
    x = 1.01**j
    print(f"  1 % par jour sur {j} {lib:18s} -> x{x:,.1f} par an, soit {100*(x-1):,.0f} %")
print(f"\n  Sur 5 ans (365 j/an) : x{1.01**(365*5):,.0f}")
print(f"  Avec 1 000 EUR de depart, cela ferait {1000*1.01**(365*5):,.0f} EUR en 5 ans.")
print("\n  A titre de comparaison, sur toute leur histoire :")
print("    Renaissance Medallion, le meilleur fonds connu : ~39 % par an avant frais")
print("    Berkshire Hathaway, 1965-2024                  : ~19 % par an")
print("    Le meilleur reglage mesure ici (D)             : ~92 % par an en backtest")

# --- combien faudrait-il risquer par trade ? -------------------------------
T = pd.read_csv(os.path.join(RESULTS, "trades_pool_crypto.csv"))
sim = pd.read_csv(os.path.join(RESULTS, "29_sim_synthese.csv"))
print("\n" + "="*100)
print("### 2. Quelle taille de position faudrait-il pour y arriver ? ###\n")
rows = []
for _, r in sim.iterrows():
    esp, n = r["esperance_R"], r["n_signaux"]
    trades_par_an = n / 9.1
    # croissance annuelle = (1 + risque*esperance) ^ trades_par_an
    cible = 1.01**365
    # risque tel que (1+risque*esp)^trades_par_an = cible
    risque = (cible**(1/trades_par_an) - 1) / esp
    rows.append({"config": r["config"], "esperance_R": esp,
                 "trades_par_an": round(trades_par_an,0),
                 "risque_requis_%": round(risque*100,1),
                 "dd_median_a_ce_risque_%": None})
d = pd.DataFrame(rows)

# creux median simule a ce niveau de risque
Rall = {}
for cfg in sim["config"]:
    f = {"A_actuelle":(1.5,2.0,2.0),"B_equilibre":(2.0,1.5,3.0),
         "C_laisse_courir":(2.0,1.0,6.0),"D_agressive":(1.5,1.0,0.0)}[cfg]
    Rall[cfg] = None
mc = pd.read_csv(os.path.join(RESULTS, "30_sim_montecarlo.csv")).set_index("config")
ruine = pd.read_csv(os.path.join(RESULTS, "33_sim_ruine.csv"))
print(d.to_string(index=False))
print("\n  Rappel des creux MEDIANS deja mesures selon le risque par trade :")
print(ruine.pivot_table(index="risque_par_trade_%", columns="config", values="dd_median_%").round(1).to_string())
print("\n  et la probabilite de perdre la moitie du capital :")
print(ruine.pivot_table(index="risque_par_trade_%", columns="config", values="prob_perdre_moitie").round(3).to_string())

print("\n" + "="*100)
print("### 3. Ce que le meilleur reglage donne vraiment, a 1 % de risque ###\n")
print(sim[["config","win_rate","esperance_R","CAGR_%","dd_max_%","MAR","serie_perdante_max"]].to_string(index=False))
print("\n  Le meilleur reglage mesure atteint 92 % par an en backtest, avec un creux")
print("  de -26 % et jusqu'a 23 pertes d'affilee. C'est deja un resultat hors norme,")
print("  et il reste 12 a 40 fois en dessous de 1 % par jour.")

json.dump({"x_par_an_365j": 1.01**365, "x_par_an_252j": 1.01**252,
           "x_5ans": 1.01**(365*5),
           "risque_requis": d.to_dict("records")},
          open(os.path.join(RESULTS, "34_objectif_1pct.json"), "w"), indent=2)
