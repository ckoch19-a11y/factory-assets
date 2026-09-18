"""Features techniques, toutes causales (aucune information du futur).

Regle absolue : une feature a l'index t n'utilise que les barres <= t.
Le signal derive de t est execute a l'ouverture de t+1.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _wilder(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def true_range(df: pd.DataFrame) -> pd.Series:
    pc = df["close"].shift(1)
    if df["high"].notna().any():
        hi = df[["high", "close"]].max(axis=1)
        lo = df[["low", "close"]].min(axis=1)
        return pd.concat([hi - lo, (hi - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return (df["close"] - pc).abs()


def rsi(close: pd.Series, n: int) -> pd.Series:
    d = close.diff()
    up = _wilder(d.clip(lower=0), n)
    dn = _wilder((-d).clip(lower=0), n)
    rs = up / dn.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    return out.fillna(50.0).where(dn.notna() | up.notna())


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """df : une seule serie, triee par date, colonnes OHLCV."""
    f = df.copy().sort_values("date").reset_index(drop=True)
    c, h, l = f["close"], f["high"], f["low"]

    f["ret1"] = c.pct_change()
    f["logret"] = np.log(c).diff()

    # --- volatilite ---
    f["tr"] = true_range(f)
    f["atr14"] = _wilder(f["tr"], 14)
    f["atr_pct"] = f["atr14"] / c
    f["rv20"] = f["logret"].rolling(20).std() * np.sqrt(252)
    f["rv60"] = f["logret"].rolling(60).std() * np.sqrt(252)
    f["rv252"] = f["logret"].rolling(252).std() * np.sqrt(252)
    # regime de volatilite : rang percentile de rv20 sur 2 ans glissants
    f["vol_rank"] = f["rv20"].rolling(504, min_periods=252).rank(pct=True)
    f["vol_ratio"] = f["rv20"] / f["rv252"]

    # --- tendance ---
    for n in (10, 20, 50, 100, 200):
        f[f"sma{n}"] = c.rolling(n).mean()
        f[f"ema{n}"] = c.ewm(span=n, adjust=False, min_periods=n).mean()
    f["trend200"] = c / f["sma200"] - 1.0
    f["trend50"] = c / f["sma50"] - 1.0
    f["sma50_slope"] = f["sma50"].diff(20) / f["sma50"]
    f["sma200_slope"] = f["sma200"].diff(20) / f["sma200"]

    # momentum total sur fenetres (12-1 exclut le dernier mois)
    f["mom21"] = c.pct_change(21)
    f["mom63"] = c.pct_change(63)
    f["mom126"] = c.pct_change(126)
    f["mom252"] = c.pct_change(252)
    f["mom12_1"] = c.shift(21).pct_change(231)

    # --- extension / pullback (normalises par la volatilite) ---
    f["rsi2"] = rsi(c, 2)
    f["rsi3"] = rsi(c, 3)
    f["rsi14"] = rsi(c, 14)
    sd20 = c.rolling(20).std()
    f["z20"] = (c - f["sma20"]) / sd20.replace(0, np.nan)
    f["ext_atr20"] = (c - f["ema20"]) / f["atr14"].replace(0, np.nan)
    f["ext_atr50"] = (c - f["ema50"]) / f["atr14"].replace(0, np.nan)

    # distance au plus haut / plus bas glissants
    f["hh252"] = h.rolling(252).max() if h.notna().any() else c.rolling(252).max()
    f["ll252"] = l.rolling(252).min() if l.notna().any() else c.rolling(252).min()
    f["dd252"] = c / f["hh252"] - 1.0
    f["up252"] = c / f["ll252"] - 1.0
    f["hh20"] = (h if h.notna().any() else c).rolling(20).max()
    f["ll20"] = (l if l.notna().any() else c).rolling(20).min()

    # --- structure de barres ---
    dn = (f["ret1"] < 0).astype(int)
    grp = (dn != dn.shift()).cumsum()
    f["consec_down"] = dn.groupby(grp).cumsum() * dn
    up = (f["ret1"] > 0).astype(int)
    grpu = (up != up.shift()).cumsum()
    f["consec_up"] = up.groupby(grpu).cumsum() * up

    rng = (h - l) if h.notna().any() else pd.Series(np.nan, index=f.index)
    f["range_pct"] = rng / c
    f["range_compress"] = rng.rolling(5).mean() / rng.rolling(50).mean()
    # position de la cloture dans la barre : 0 = sur le bas, 1 = sur le haut
    f["close_loc"] = ((c - l) / rng.replace(0, np.nan)).clip(0, 1)

    # --- calendrier ---
    f["dow"] = f["date"].dt.dayofweek
    f["dom"] = f["date"].dt.day
    f["month"] = f["date"].dt.month

    # --- rendements futurs (pour l'etude statistique uniquement) ---
    for hz in (1, 3, 5, 10, 20):
        f[f"fwd{hz}"] = c.shift(-hz) / c - 1.0
        # normalise par la volatilite du jour : rend les actifs comparables
        f[f"fwd{hz}_z"] = f[f"fwd{hz}"] / (f["rv20"] / np.sqrt(252) * np.sqrt(hz))

    return f


def build_panel_features(panel: pd.DataFrame, min_bars: int = 400) -> pd.DataFrame:
    out = []
    for sym, g in panel.groupby("symbol", sort=False):
        if len(g) < min_bars:
            continue
        out.append(add_features(g))
    return pd.concat(out, ignore_index=True)
