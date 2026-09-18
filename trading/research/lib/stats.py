"""Statistiques honnetes pour signaux de marche.

Deux pieges que ce module traite explicitement :

1. Correlation transversale. 500 actions le meme jour ne sont pas 500
   observations independantes. On agrege donc d'abord en un rendement
   quotidien de portefeuille, puis on teste la serie temporelle.

2. Chevauchement des horizons. Un rendement a 10 jours mesure a t et a t+1
   partage 9 jours. Les t-stats naifs sont gonfles ; on utilise Newey-West.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def newey_west_se(x: np.ndarray, lags: int) -> float:
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    n = len(x)
    if n < 10:
        return float("nan")
    e = x - x.mean()
    g0 = (e @ e) / n
    s = g0
    for k in range(1, min(lags, n - 1) + 1):
        gk = (e[k:] @ e[:-k]) / n
        s += 2.0 * (1.0 - k / (lags + 1.0)) * gk
    s = max(s, 1e-18)
    return float(np.sqrt(s / n))


def tstat_nw(x: pd.Series, lags: int) -> tuple[float, float]:
    x = pd.Series(x).dropna()
    if len(x) < 10:
        return float("nan"), float("nan")
    se = newey_west_se(x.values, lags)
    if not np.isfinite(se) or se == 0:
        return float("nan"), float("nan")
    return float(x.mean() / se), float(x.mean())


def event_test(df: pd.DataFrame, mask: pd.Series, horizon: int,
               ret_col: str | None = None, min_dates: int = 60,
               mode: str = "auto") -> dict:
    """Test d'un signal contre une reference.

    mode "cross"  : plusieurs symboles. Reference = moyenne transversale du
                    meme jour. Neutralise le facteur marche commun.
    mode "series" : un seul symbole. Reference = moyenne inconditionnelle de
                    la serie. On teste si le conditionnement change la moyenne.
    """
    col = ret_col or f"fwd{horizon}"
    d = df.loc[:, ["date", "symbol", col]].copy()
    d["sig"] = mask.values if hasattr(mask, "values") else mask
    d = d.dropna(subset=[col])
    if mode == "auto":
        mode = "series" if d["symbol"].nunique() == 1 else "cross"
    if int(d["sig"].sum()) < 30:
        return {"n_obs": int(d["sig"].sum()), "status": "echantillon insuffisant"}

    lags = max(horizon - 1, 1)
    base_mean = float(d[col].mean())
    base_hit = float((d[col] > 0).mean())

    if mode == "cross":
        sig_daily = d[d["sig"]].groupby("date")[col].mean()
        base_daily = d.groupby("date")[col].mean()
        common = sig_daily.index.intersection(base_daily.index)
        if len(common) < min_dates:
            return {"n_obs": int(d["sig"].sum()), "n_dates": len(common),
                    "status": "trop peu de dates"}
        excess = sig_daily.loc[common] - base_daily.loc[common]
        abs_series = sig_daily.loc[common]
        n_dates = len(common)
    else:
        sig = d.loc[d["sig"]].set_index("date")[col].sort_index()
        if len(sig) < min_dates:
            return {"n_obs": int(d["sig"].sum()), "n_dates": len(sig),
                    "status": "trop peu de dates"}
        excess = sig - base_mean
        abs_series = sig
        n_dates = len(sig)

    t_ex, m_ex = tstat_nw(excess, lags)
    t_ab, m_ab = tstat_nw(abs_series, lags)
    hit = float((d.loc[d["sig"], col] > 0).mean())
    return {
        "n_obs": int(d["sig"].sum()),
        "n_dates": int(n_dates),
        "mean_fwd_pct": round(m_ab * 100, 4),
        "mean_base_pct": round(base_mean * 100, 4),
        "mean_excess_pct": round(m_ex * 100, 4),
        "t_absolu": round(t_ab, 2),
        "t_excess": round(t_ex, 2),
        "hit_rate": round(hit * 100, 2),
        "hit_rate_base": round(base_hit * 100, 2),
        "edge_hit_pts": round((hit - base_hit) * 100, 2),
        "status": "ok",
    }


def block_bootstrap_pvalue(x: pd.Series, block: int = 21, n_iter: int = 2000,
                           seed: int = 7) -> float:
    """p-value unilaterale : la moyenne observee peut-elle sortir du hasard ?

    Bootstrap par blocs : conserve l'autocorrelation locale de la serie.
    """
    x = pd.Series(x).dropna().values
    n = len(x)
    if n < block * 3:
        return float("nan")
    obs = x.mean()
    centred = x - obs
    rng = np.random.default_rng(seed)
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, n - block, size=(n_iter, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(n_iter, -1)[:, :n]
    sims = centred[idx].mean(axis=1)
    return float((sims >= abs(obs)).mean() if obs > 0 else (sims <= -abs(obs)).mean())


def deflated_sharpe(sr: float, n_obs: int, n_trials: int,
                    trials_sr_var: float, skew: float = 0.0,
                    kurt: float = 3.0) -> float:
    """Sharpe deflate (Bailey & Lopez de Prado, 2014).

    Corrige le Sharpe observe du fait qu'on a essaye n_trials configurations
    et garde la meilleure. trials_sr_var est la VARIANCE des Sharpe obtenus
    sur l'ensemble des configurations essayees : c'est elle qui fixe la
    hauteur de barre. L'omettre (erreur frequente) rend le test inutilisable.

    Retourne P(Sharpe reel > 0) compte tenu de la selection.
    """
    from scipy.stats import norm
    if n_obs < 20 or n_trials < 2 or not np.isfinite(trials_sr_var) or trials_sr_var <= 0:
        return float("nan")
    gamma = 0.5772156649
    n = float(n_trials)
    z1 = norm.ppf(1.0 - 1.0 / n)
    z2 = norm.ppf(1.0 - 1.0 / (n * np.e))
    sr0 = np.sqrt(trials_sr_var) * ((1 - gamma) * z1 + gamma * z2)
    denom = np.sqrt(max(1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr ** 2, 1e-9))
    z = (sr - sr0) * np.sqrt(n_obs - 1.0) / denom
    return float(norm.cdf(z))


def perf_stats(returns: pd.Series, periods_per_year: int = 252) -> dict:
    r = pd.Series(returns).dropna()
    if len(r) < 5:
        return {}
    eq = (1 + r).cumprod()
    yrs = len(r) / periods_per_year
    cagr = eq.iloc[-1] ** (1 / yrs) - 1 if yrs > 0 and eq.iloc[-1] > 0 else float("nan")
    vol = r.std() * np.sqrt(periods_per_year)
    sharpe = (r.mean() * periods_per_year) / vol if vol > 0 else float("nan")
    dd = eq / eq.cummax() - 1
    maxdd = float(dd.min())
    downside = r[r < 0].std() * np.sqrt(periods_per_year)
    return {
        "CAGR_pct": round(cagr * 100, 2),
        "vol_ann_pct": round(vol * 100, 2),
        "Sharpe": round(sharpe, 3),
        "Sortino": round((r.mean() * periods_per_year) / downside, 3) if downside > 0 else None,
        "max_drawdown_pct": round(maxdd * 100, 2),
        "MAR": round(cagr / abs(maxdd), 3) if maxdd < 0 else None,
        "n_periods": int(len(r)),
        "annees": round(yrs, 1),
    }
