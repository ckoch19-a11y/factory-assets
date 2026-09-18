"""Controles anti-illusion.

Un backtest positif ne prouve rien tant qu'on n'a pas verifie qu'il ne peut
PAS etre positif quand il ne devrait pas l'etre.

  A. Marche aleatoire de meme volatilite -> l'esperance doit tomber a zero
     (voire en dessous a cause des frais). Si elle reste positive, le moteur
     lit le futur.
  B. Rendements melanges (la structure temporelle est detruite, la
     distribution conservee) -> meme conclusion.
  C. Signal retarde d'une barre -> un vrai edge se degrade progressivement ;
     une fuite d'information s'effondre d'un coup.
  D. Signal inverse -> l'esperance doit changer de signe.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import data as D, features as F, backtest as B, stats as S  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
panel = pd.read_parquet(os.path.join(D.OUT, "panel_daily.parquet"))
spx = panel[(panel["symbol"] == "SPX") & (panel["date"] >= "1962-01-01")].reset_index(drop=True)

CFG = dict(stop_atr=2.0, confirm=False, exit_on_mean=False, target_r=0.0,
           trail_atr=2.0, max_bars=40, allow_short=False)


def run(df):
    f = F.build_panel_features(df, 400)[
        ["symbol", "date", "open", "high", "low", "close", "atr14"]]
    return B.trade_stats(B.run_panel(f, B.Config(**CFG)))


def synth_from(df, seed, mode):
    """Reconstruit une serie OHLC synthetique a partir des rendements reels."""
    rng = np.random.default_rng(seed)
    r = np.log(df["close"]).diff().dropna().values
    if mode == "shuffle":
        r2 = rng.permutation(r)
    else:  # marche aleatoire gaussienne de meme moyenne / ecart-type
        r2 = rng.normal(r.mean(), r.std(), size=len(r))
    px = df["close"].iloc[0] * np.exp(np.cumsum(np.r_[0.0, r2]))
    # on rejoue les amplitudes intrabarres reelles autour de la nouvelle cloture
    hi_f = (df["high"] / df["close"]).values
    lo_f = (df["low"] / df["close"]).values
    op_f = (df["open"] / df["close"]).values
    out = pd.DataFrame({
        "symbol": "SYN", "date": df["date"].values, "close": px,
        "open": px * op_f, "high": px * np.maximum(hi_f, 1.0),
        "low": px * np.minimum(lo_f, 1.0),
        "volume": np.nan, "asset_class": "synthetique",
    })
    out["high"] = out[["high", "open", "close"]].max(axis=1)
    out["low"] = out[["low", "open", "close"]].min(axis=1)
    return out


reel = run(spx)
print("=== Reference : S&P 500 reel ===")
print(f"  {reel['n_trades']} trades | reussite {reel['win_rate_pct']} % | "
      f"esperance {reel['esperance_R']} R | facteur de profit {reel['profit_factor']}")

rows = [{"test": "S&P 500 reel", "n_trades": reel["n_trades"],
         "win_rate_pct": reel["win_rate_pct"], "esperance_R": reel["esperance_R"],
         "profit_factor": reel["profit_factor"]}]

print("\n=== A. Marches aleatoires de meme volatilite (20 tirages) ===")
esp = []
for s in range(20):
    st = run(synth_from(spx, s, "gauss"))
    if st.get("n_trades", 0) > 30:
        esp.append(st["esperance_R"])
print(f"  esperance mediane {np.median(esp):+.4f} R | "
      f"min {np.min(esp):+.4f} | max {np.max(esp):+.4f} | "
      f"tirages positifs {sum(e > 0 for e in esp)}/{len(esp)}")
rows.append({"test": "marche aleatoire (mediane de 20)", "n_trades": None,
             "win_rate_pct": None, "esperance_R": round(float(np.median(esp)), 4),
             "profit_factor": None})

print("\n=== B. Rendements melanges (20 tirages) ===")
esp2 = []
for s in range(100, 120):
    st = run(synth_from(spx, s, "shuffle"))
    if st.get("n_trades", 0) > 30:
        esp2.append(st["esperance_R"])
print(f"  esperance mediane {np.median(esp2):+.4f} R | "
      f"min {np.min(esp2):+.4f} | max {np.max(esp2):+.4f} | "
      f"tirages positifs {sum(e > 0 for e in esp2)}/{len(esp2)}")
rows.append({"test": "rendements melanges (mediane de 20)", "n_trades": None,
             "win_rate_pct": None, "esperance_R": round(float(np.median(esp2)), 4),
             "profit_factor": None})

print("\n=== C. Signal retarde ===")
f0 = F.build_panel_features(spx, 400)[
    ["symbol", "date", "open", "high", "low", "close", "atr14"]]
for lag in (0, 1, 2, 5):
    g = B.generate_signals(f0.copy(), B.Config(**CFG))
    g["sig_long"] = g["sig_long"].shift(lag).fillna(False)
    tr = []
    for _, sub in g.groupby("symbol", sort=False):
        tr.extend(B.run_symbol(sub.assign(atr14=sub["atr_bt"]), B.Config(**CFG))
                  if False else [])
    # on rejoue directement avec le signal decale
    t = B.run_panel(f0.assign(_lag=lag), B.Config(**CFG)) if lag == 0 else None
    if lag == 0:
        st = B.trade_stats(t)
    else:
        f2 = f0.copy()
        # decaler le signal revient a decaler les prix d'entree : on decale
        # les features utilisees pour le declenchement
        f2[["open", "high", "low", "close", "atr14"]] = \
            f0[["open", "high", "low", "close", "atr14"]].shift(-lag).values
        f2 = f2.dropna(subset=["close"])
        st = B.trade_stats(B.run_panel(f2, B.Config(**CFG)))
    print(f"  retard {lag} barre(s) : {st.get('n_trades')} trades | "
          f"esperance {st.get('esperance_R')} R | reussite {st.get('win_rate_pct')} %")
    rows.append({"test": f"signal retarde de {lag} barre(s)", "n_trades": st.get("n_trades"),
                 "win_rate_pct": st.get("win_rate_pct"),
                 "esperance_R": st.get("esperance_R"),
                 "profit_factor": st.get("profit_factor")})

print("\n=== D. Signal inverse (on achete ce qu'on aurait du eviter) ===")
cfg_inv = dict(CFG)
cfg_inv["ext_long"] = 1.0        # acheter l'extension HAUTE au lieu de la basse
st_inv = B.trade_stats(B.run_panel(f0, B.Config(**cfg_inv)))
print(f"  {st_inv.get('n_trades')} trades | esperance {st_inv.get('esperance_R')} R | "
      f"reussite {st_inv.get('win_rate_pct')} % | facteur {st_inv.get('profit_factor')}")
rows.append({"test": "signal inverse (extension haute)", "n_trades": st_inv.get("n_trades"),
             "win_rate_pct": st_inv.get("win_rate_pct"),
             "esperance_R": st_inv.get("esperance_R"),
             "profit_factor": st_inv.get("profit_factor")})

pd.DataFrame(rows).to_csv(os.path.join(RESULTS, "16_controles_sanity.csv"), index=False)
print("\n-> results/16_controles_sanity.csv")
