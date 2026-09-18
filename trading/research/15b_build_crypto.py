"""Consolide les fichiers journaliers crypto en un panel unique + controles."""
from __future__ import annotations
import glob, os, sys
import numpy as np, pandas as pd

SRC = os.environ.get("CRYPTO_OUT", "/tmp/cdl")
OUT = "/tmp/mkt/clean/crypto_daily.parquet"
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")

files = sorted(glob.glob(os.path.join(SRC, "*.parquet")))
if not files:
    raise SystemExit(f"aucun fichier dans {SRC} : lancer d'abord ./00_fetch_crypto.sh")
df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
df.columns = [c.lower() for c in df.columns]
df["date"] = pd.to_datetime(df["timestamp"], utc=True).dt.tz_localize(None).dt.normalize()
df["symbol"] = df["symbol"].str.replace("USDT", "", regex=False)
df = df.drop_duplicates(subset=["symbol", "date"]).sort_values(["symbol", "date"]).reset_index(drop=True)

bad_h = int((df["high"] < df[["open", "close"]].max(axis=1) - 1e-9).sum())
bad_l = int((df["low"] > df[["open", "close"]].min(axis=1) + 1e-9).sum())
rep = df.groupby("symbol").agg(barres=("close", "size"), debut=("date", "min"), fin=("date", "max"))
rep["annees"] = ((rep["fin"] - rep["debut"]).dt.days / 365.25).round(1)
rep["trous"] = [int((g["date"].diff().dt.days.dropna() > 1).sum()) for _, g in df.groupby("symbol")]
print(rep.to_string())
print(f"\n{len(df):,} barres | {df.symbol.nunique()} actifs | anomalies high={bad_h} low={bad_l}")
if bad_h or bad_l or rep["trous"].sum():
    print("ATTENTION : anomalies detectees, ne pas utiliser tel quel.")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
out = df[["symbol", "date", "open", "high", "low", "close", "volume"]].copy()
out["asset_class"] = "crypto"
out.to_parquet(OUT, index=False)
os.makedirs(RESULTS, exist_ok=True)
rep.to_csv(os.path.join(RESULTS, "22_data_crypto.csv"))
print(f"-> {OUT}")
