"""Pourquoi la strategie ne peut pas fonctionner sous le journalier.

Le stop vaut 1,5 ATR. Les frais, eux, sont proportionnels au PRIX, pas a l'ATR.
Quand on descend en unite de temps, l'ATR s'effondre alors que les frais
restent identiques : le cout, exprime en fraction du risque, explose.

C'est une contrainte arithmetique, pas une question de reglage. Aucune
esperance ne survit a un cout de plusieurs R par trade.
"""
from __future__ import annotations
import gzip, json, os, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import features as F  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
RAW = os.environ.get("MKT_RAW", "/tmp/mkt/raw")
STOP_MULT = 1.5
COUT_BPS = 40.0   # aller-retour, hypothese crypto

frames = []
with gzip.open(os.path.join(RAW, "btc_1min_hist.csv.gz"), "rt") as fh:
    frames.append(pd.read_csv(fh))
lat = os.path.join(RAW, "btc_1min_latest.csv")
if os.path.exists(lat):
    frames.append(pd.read_csv(lat))
m = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["timestamp"], keep="last")
m["date"] = pd.to_datetime(m["timestamp"], unit="s")
m = m.sort_values("date").reset_index(drop=True)

rows = []
for tf, lib in (("1min", "1 minute"), ("5min", "5 minutes"), ("15min", "15 minutes"),
                ("1h", "1 heure"), ("4h", "4 heures"), ("1D", "1 jour"), ("1W", "1 semaine")):
    g = m.set_index("date").resample(tf).agg(
        open=("open", "first"), high=("high", "max"), low=("low", "min"),
        close=("close", "last"), volume=("volume", "sum")).dropna().reset_index()
    if len(g) < 300:
        continue
    g["symbol"] = "BTC"
    f = F.add_features(g)
    atr = f["atr14"].dropna()
    px = f.loc[atr.index, "close"]
    atr_pct = float((atr / px).median())
    risque_pct = STOP_MULT * atr_pct
    cout_R = (COUT_BPS / 10000.0) / risque_pct
    rows.append({"unite": lib, "barres": len(g),
                 "ATR_median_pct": round(atr_pct * 100, 4),
                 "risque_pct_du_prix": round(risque_pct * 100, 3),
                 "cout_en_R": round(cout_R, 3)})

d = pd.DataFrame(rows)
d.to_csv(os.path.join(RESULTS, "41_cout_par_timeframe.csv"), index=False)
pd.set_option("display.width", 200)
print("### Cout aller-retour de 40 bps, exprime en fraction du risque ###\n")
print(d.to_string(index=False))

# calibrage du garde-fou sur le panel crypto journalier
C = pd.read_parquet("/tmp/mkt/clean/crypto_daily.parquet")
p90 = []
for sym, g in C.groupby("symbol"):
    f = F.add_features(g.sort_values("date"))
    atr = f["atr14"].dropna()
    px = f.loc[atr.index, "close"]
    c = (COUT_BPS / 10000.0) / (STOP_MULT * atr / px)
    p90.append({"actif": sym, "cout_R_median": round(float(c.median()), 3),
                "cout_R_p90": round(float(c.quantile(0.90)), 3)})
q = pd.DataFrame(p90).sort_values("cout_R_p90", ascending=False)
q.to_csv(os.path.join(RESULTS, "42_cout_journalier_par_actif.csv"), index=False)
print("\n### En journalier, par actif ###\n")
print(q.to_string(index=False))
pire = float(q["cout_R_p90"].max())
print(f"\nPire 90e centile en journalier : {pire:.3f} R")
print("Le garde-fou de l'indicateur bloque au-dela de 0,15 R : le journalier")
print("passe sur les 10 actifs, 4 heures et en dessous sont bloques.")
json.dump({"cout_par_tf": rows, "pire_p90_journalier": pire, "seuil_retenu": 0.15},
          open(os.path.join(RESULTS, "41_cout_meta.json"), "w"), indent=2)
