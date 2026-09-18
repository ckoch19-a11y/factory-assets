"""Backtester event-driven, niveau trade.

Hypotheses explicites (toutes conservatrices) :
  - le signal est calcule sur la cloture de t, l'entree se fait a l'OUVERTURE de t+1 ;
  - stop et objectif sont verifies en intrabarre a partir de t+1 ;
  - si stop ET objectif sont touchables dans la meme barre, on suppose que le
    STOP est touche en premier (on ne sait pas dans quel ordre) ;
  - un gap au-dela du stop sort a l'ouverture, pas au prix du stop ;
  - frais + slippage preleves a l'entree ET a la sortie ;
  - une seule position ouverte par symbole a la fois.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class Config:
    # declenchement
    trend_len: int = 200
    ext_len: int = 20
    atr_len: int = 14
    ext_long: float = -1.0
    ext_short: float = 1.0
    require_slope_short: bool = True
    require_slope_long: bool = False
    confirm: bool = True          # exiger une barre de retournement
    allow_short: bool = True
    # gestion
    stop_atr: float = 2.0
    target_r: float = 2.0         # 0 = pas d'objectif fixe
    exit_on_mean: bool = True     # sortir au retour sur l'EMA rapide
    max_bars: int = 20            # sortie temporelle
    trail_atr: float = 0.0        # 0 = pas de trailing
    # couts
    fee_bps: float = 5.0          # par cote, en points de base
    slip_bps: float = 5.0         # par cote
    # risque
    risk_pct: float = 1.0         # % du capital risque par trade


def _cost(cfg: Config) -> float:
    return (cfg.fee_bps + cfg.slip_bps) / 10000.0


def generate_signals(f: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """Ajoute les colonnes sig_long / sig_short. Strictement causal."""
    d = f.copy()
    c = d["close"]
    sma = c.rolling(cfg.trend_len).mean()
    ema = c.ewm(span=cfg.ext_len, adjust=False, min_periods=cfg.ext_len).mean()
    slope = sma.diff(20)
    atr = d["atr14"] if cfg.atr_len == 14 else None
    if atr is None:
        from .features import _wilder, true_range
        atr = _wilder(true_range(d), cfg.atr_len)
    ext = (c - ema) / atr.replace(0, np.nan)

    up_regime = c > sma
    dn_regime = c < sma
    if cfg.require_slope_long:
        up_regime &= slope > 0
    if cfg.require_slope_short:
        dn_regime &= slope < 0

    sl = up_regime & (ext < cfg.ext_long)
    ss = dn_regime & (ext > cfg.ext_short) if cfg.allow_short else pd.Series(False, index=d.index)

    if cfg.confirm:
        sl = sl & (c > c.shift(1))
        ss = ss & (c < c.shift(1))

    d["sma_trend"] = sma
    d["ema_fast"] = ema
    d["atr_bt"] = atr
    d["ext_bt"] = ext
    d["sig_long"] = sl.fillna(False)
    d["sig_short"] = ss.fillna(False) if cfg.allow_short else False
    return d


def run_symbol(f: pd.DataFrame, cfg: Config, presignal: bool = False) -> list[dict]:
    """Rejoue une serie et renvoie la liste des trades.

    presignal=True : les colonnes sig_long / sig_short sont deja presentes et
    ne sont pas recalculees. Sert aux controles (signal retarde, entrees
    aleatoires) ou l'on veut la MEME gestion avec un declenchement different.
    """
    d = f.reset_index(drop=True) if presignal else generate_signals(f, cfg).reset_index(drop=True)
    if presignal and "atr_bt" not in d.columns:
        d = d.assign(atr_bt=d["atr14"], ema_fast=np.nan)
    o = d["open"].values
    h = d["high"].values
    l = d["low"].values
    c = d["close"].values
    atr = d["atr_bt"].values
    ema = d["ema_fast"].values
    sig_l = d["sig_long"].values
    sig_s = d["sig_short"].values
    dates = d["date"].values
    sym = d["symbol"].iloc[0]
    n = len(d)
    cost = _cost(cfg)

    # barres sans OHLC exploitable : on se rabat sur la cloture
    has_hl = np.isfinite(h) & np.isfinite(l)
    hh = np.where(has_hl, h, c)
    ll = np.where(has_hl, l, c)
    oo = np.where(np.isfinite(o), o, c)

    trades: list[dict] = []
    i = 0
    while i < n - 2:
        side = 1 if sig_l[i] else (-1 if sig_s[i] else 0)
        if side == 0 or not np.isfinite(atr[i]) or atr[i] <= 0:
            i += 1
            continue

        j = i + 1                       # barre d'entree
        entry_raw = oo[j]
        if not np.isfinite(entry_raw) or entry_raw <= 0:
            i += 1
            continue
        entry = entry_raw * (1 + side * cost)
        a = atr[i]
        stop = entry_raw - side * cfg.stop_atr * a
        risk = abs(entry_raw - stop)
        if risk <= 0:
            i += 1
            continue
        target = entry_raw + side * cfg.target_r * risk if cfg.target_r > 0 else np.nan
        best = entry_raw

        exit_px, exit_i, reason = np.nan, None, ""
        for k in range(j, min(j + cfg.max_bars + 1, n)):
            # 1) gap defavorable a l'ouverture : on sort au prix d'ouverture
            if (side == 1 and oo[k] <= stop) or (side == -1 and oo[k] >= stop):
                exit_px, exit_i, reason = oo[k], k, "gap_stop"
                break
            # 2) stop intrabarre (prioritaire : hypothese conservatrice)
            if (side == 1 and ll[k] <= stop) or (side == -1 and hh[k] >= stop):
                exit_px, exit_i, reason = stop, k, "stop"
                break
            # 3) objectif intrabarre
            if np.isfinite(target) and (
                (side == 1 and hh[k] >= target) or (side == -1 and ll[k] <= target)
            ):
                exit_px, exit_i, reason = target, k, "target"
                break
            # 4) retour sur la moyenne rapide (evalue en cloture)
            if cfg.exit_on_mean and k > j and np.isfinite(ema[k]):
                if (side == 1 and c[k] >= ema[k]) or (side == -1 and c[k] <= ema[k]):
                    exit_px, exit_i, reason = c[k], k, "retour_moyenne"
                    break
            # 5) trailing stop, resserre apres coup (jamais dans le mauvais sens)
            if cfg.trail_atr > 0 and np.isfinite(atr[k]):
                best = max(best, hh[k]) if side == 1 else min(best, ll[k])
                t = best - side * cfg.trail_atr * atr[k]
                stop = max(stop, t) if side == 1 else min(stop, t)

        termine = True
        if exit_i is None:
            # Deux cas a ne surtout pas confondre :
            #   - la duree maximale est atteinte : sortie legitime au temps ;
            #   - les donnees s'arretent avant : la position est ENCORE OUVERTE.
            # Compter une position ouverte comme un gain realise gonfle le
            # resultat. On la marque, et elle est exclue par defaut.
            if j + cfg.max_bars <= n - 1:
                exit_i = j + cfg.max_bars
                exit_px, reason = c[exit_i], "temps"
            else:
                exit_i = n - 1
                exit_px, reason = c[exit_i], "non_termine"
                termine = False

        exit_fill = exit_px * (1 - side * cost)
        gross_r = side * (exit_fill - entry) / risk
        ret_pct = side * (exit_fill - entry) / entry
        trades.append({
            "symbol": sym,
            "side": "long" if side == 1 else "short",
            "date_signal": pd.Timestamp(dates[i]),
            "date_entree": pd.Timestamp(dates[j]),
            "date_sortie": pd.Timestamp(dates[exit_i]),
            "bars": int(exit_i - j),
            "entree": float(entry_raw),
            "stop_initial": float(entry_raw - side * cfg.stop_atr * a),
            "sortie": float(exit_px),
            "R": float(gross_r),
            "ret_pct": float(ret_pct),
            "motif": reason,
            "termine": bool(termine),
            "atr_pct_entree": float(a / entry_raw),
        })
        i = exit_i + 1                  # pas de chevauchement sur un meme symbole

    return trades


def run_panel(feat: pd.DataFrame, cfg: Config, presignal: bool = False,
              inclure_non_termines: bool = False) -> pd.DataFrame:
    """inclure_non_termines : par defaut False.

    Une position encore ouverte a la derniere barre n'est pas un trade. La
    compter comme un gain realise flatte le resultat ; sur cet echantillon
    un seul trade de ce type gonflait l'esperance groupee de 7 % et faisait
    changer de signe celle d'un actif.
    """
    out = []
    for _, g in feat.groupby("symbol", sort=False):
        if len(g) < cfg.trend_len + 60:
            continue
        out.extend(run_symbol(g, cfg, presignal=presignal))
    if not out:
        return pd.DataFrame()
    t = pd.DataFrame(out).sort_values("date_entree").reset_index(drop=True)
    if not inclure_non_termines and "termine" in t.columns:
        t = t[t["termine"]].reset_index(drop=True)
    return t


def trade_stats(t: pd.DataFrame) -> dict:
    if t is None or not len(t):
        return {"n_trades": 0}
    R = t["R"]
    wins, losses = R[R > 0], R[R <= 0]
    gross_win, gross_loss = wins.sum(), abs(losses.sum())
    exp_R = float(R.mean())
    return {
        "n_trades": int(len(t)),
        "win_rate_pct": round(float((R > 0).mean() * 100), 2),
        "gain_moyen_R": round(float(wins.mean()), 3) if len(wins) else 0.0,
        "perte_moyenne_R": round(float(losses.mean()), 3) if len(losses) else 0.0,
        "ratio_gain_perte": round(float(wins.mean() / abs(losses.mean())), 2)
        if len(wins) and len(losses) and losses.mean() != 0 else None,
        "esperance_R": round(exp_R, 4),
        "profit_factor": round(float(gross_win / gross_loss), 3) if gross_loss > 0 else None,
        "t_stat_R": round(float(exp_R / (R.std(ddof=1) / np.sqrt(len(R)))), 2)
        if len(R) > 2 and R.std(ddof=1) > 0 else None,
        "duree_moy_barres": round(float(t["bars"].mean()), 1),
        "R_total": round(float(R.sum()), 1),
        "pire_trade_R": round(float(R.min()), 2),
        "motifs": t["motif"].value_counts().to_dict(),
    }


def equity_curve(t: pd.DataFrame, risk_pct: float = 1.0,
                 start: float = 10000.0) -> pd.Series:
    """Capital a risque fixe : chaque trade risque risk_pct % du capital courant."""
    if not len(t):
        return pd.Series(dtype=float)
    t = t.sort_values("date_sortie")
    eq, cur = [], start
    for r in t["R"].values:
        cur *= (1 + (risk_pct / 100.0) * r)
        eq.append(cur)
    return pd.Series(eq, index=pd.DatetimeIndex(t["date_sortie"]))
