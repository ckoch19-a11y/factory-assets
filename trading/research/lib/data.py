"""Chargement et normalisation des sources de marche brutes.

Toutes les sources sont ramenees au meme schema :
    symbol, date (UTC, naive), open, high, low, close, volume, asset_class

Aucune donnee synthetique : si une source n'est pas disponible elle est
simplement absente du panel, et le rapport de build le signale.
"""
from __future__ import annotations

import gzip
import io
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

RAW = os.environ.get("MKT_RAW", "/tmp/mkt/raw")
OUT = os.environ.get("MKT_OUT", "/tmp/mkt/clean")

SCHEMA = ["symbol", "date", "open", "high", "low", "close", "volume", "asset_class"]


@dataclass
class Source:
    name: str
    path: str
    loader: str


def _finalise(df: pd.DataFrame, symbol: str, asset_class: str) -> pd.DataFrame:
    df = df.copy()
    df["symbol"] = symbol
    df["asset_class"] = asset_class
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None).dt.normalize()
    for c in ("open", "high", "low", "close", "volume"):
        if c not in df.columns:
            df[c] = np.nan
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["close"])
    df = df[df["close"] > 0]
    df = df.drop_duplicates(subset=["symbol", "date"], keep="last")
    df = df.sort_values("date").reset_index(drop=True)
    return df[SCHEMA]


def validate(df: pd.DataFrame) -> dict:
    """Controles d'integrite. On ne corrige pas en silence, on rapporte."""
    rep = {"symbol": df["symbol"].iloc[0], "rows": len(df)}
    rep["start"] = str(df["date"].min().date())
    rep["end"] = str(df["date"].max().date())
    ohlc = df[["open", "high", "low", "close"]].dropna()
    if len(ohlc):
        bad_hi = (ohlc["high"] < ohlc[["open", "close"]].max(axis=1) - 1e-9).sum()
        bad_lo = (ohlc["low"] > ohlc[["open", "close"]].min(axis=1) + 1e-9).sum()
        rep["bad_high"] = int(bad_hi)
        rep["bad_low"] = int(bad_lo)
        rep["flat_bars_pct"] = round(
            float((ohlc["high"] == ohlc["low"]).mean() * 100), 2
        )
    else:
        rep["bad_high"] = rep["bad_low"] = 0
        rep["flat_bars_pct"] = 100.0
    rep["has_ohlc"] = bool(df["high"].notna().any() and df["low"].notna().any())
    r = df["close"].pct_change()
    rep["max_abs_daily_move_pct"] = round(float(r.abs().max() * 100), 1) if len(r.dropna()) else 0.0
    # trous de calendrier anormaux (hors week-end pour les actions)
    gaps = df["date"].diff().dt.days.dropna()
    rep["max_gap_days"] = int(gaps.max()) if len(gaps) else 0
    return rep


# --------------------------------------------------------------------------
# Loaders specifiques
# --------------------------------------------------------------------------

def load_sp500_long() -> pd.DataFrame:
    """Indice S&P 500, barres journalieres 1950 -> 2018 (OHLCV)."""
    p = os.path.join(RAW, "sp500_long.csv")
    df = pd.read_csv(p)
    df.columns = [c.strip().strip('"').lower() for c in df.columns]
    df = df.rename(columns={"adj close": "adj_close"})
    df["date"] = pd.to_datetime(df["date"])
    return _finalise(df, "SPX", "equity_index")


def load_btc_minute(resample: str = "1D") -> pd.DataFrame:
    """BTC/USD Bitstamp 1 minute (2012 -> aujourd'hui) agrege en barres."""
    hist = os.path.join(RAW, "btc_1min_hist.csv.gz")
    latest = os.path.join(RAW, "btc_1min_latest.csv")
    frames = []
    with gzip.open(hist, "rt") as fh:
        frames.append(pd.read_csv(fh))
    if os.path.exists(latest):
        frames.append(pd.read_csv(latest))
    m = pd.concat(frames, ignore_index=True)
    m = m.drop_duplicates(subset=["timestamp"], keep="last")
    m["ts"] = pd.to_datetime(m["timestamp"], unit="s", utc=True).dt.tz_localize(None)
    m = m.set_index("ts").sort_index()
    # une minute sans transaction est reportee a plat : on l'ignore pour le volume
    agg = m.resample(resample).agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        volume=("volume", "sum"),
    ).dropna(subset=["close"])
    agg = agg.reset_index().rename(columns={"ts": "date"})
    sym = "BTCUSD" if resample == "1D" else f"BTCUSD_{resample}"
    out = _finalise(agg, sym, "crypto") if resample == "1D" else agg.assign(
        symbol=sym, asset_class="crypto"
    )[SCHEMA]
    return out


def load_sp500_cross() -> pd.DataFrame:
    """505 actions du S&P 500, barres journalieres 2013 -> 2018 (OHLCV)."""
    p = os.path.join(RAW, "sp500_5yr.csv")
    df = pd.read_csv(p)
    df = df.rename(columns={"Name": "symbol"})
    df["date"] = pd.to_datetime(df["date"])
    out = []
    for sym, g in df.groupby("symbol"):
        if len(g) < 250:
            continue
        out.append(_finalise(g, sym, "equity_single"))
    return pd.concat(out, ignore_index=True)


def load_vix() -> pd.DataFrame:
    p = os.path.join(RAW, "vix.csv")
    df = pd.read_csv(p)
    df.columns = [c.lower() for c in df.columns]
    return _finalise(df, "VIX", "volatility")


def load_coinmetrics(asset: str) -> pd.DataFrame:
    """Serie de cloture quotidienne CoinMetrics (pas d'OHLC)."""
    p = os.path.join(RAW, f"cm_{asset}.csv")
    df = pd.read_csv(p, usecols=lambda c: c in ("time", "PriceUSD", "volume_reported_spot_usd_1d"))
    df = df.rename(columns={"time": "date", "PriceUSD": "close",
                            "volume_reported_spot_usd_1d": "volume"})
    df = df.dropna(subset=["close"])
    df["open"] = df["high"] = df["low"] = np.nan
    return _finalise(df, asset.upper() + "_CM", "crypto_close_only")


def load_brent() -> pd.DataFrame:
    p = os.path.join(RAW, "brent.csv")
    df = pd.read_csv(p)
    df.columns = [c.lower() for c in df.columns]
    df = df.rename(columns={"price": "close"})
    df["open"] = df["high"] = df["low"] = np.nan
    return _finalise(df, "BRENT", "commodity_close_only")
