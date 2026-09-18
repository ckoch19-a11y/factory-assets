"""Walk-forward ancre sur le S&P 500, 1962-2018.

A chaque frontiere de periode on re-selectionne la configuration en
n'utilisant QUE le passe, puis on la trade sur la periode suivante sans y
toucher. On concatene ensuite tous les segments hors echantillon.

C'est la simulation la plus proche de ce qu'on ferait vraiment : on ne
connait jamais l'avenir au moment de choisir.
"""
from __future__ import annotations

import itertools
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import data as D, features as F, stats as S, backtest as B  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
panel = pd.read_parquet(os.path.join(D.OUT, "panel_daily.parquet"))

EXIT_SCHEMES = {
    "retour_moyenne":        dict(exit_on_mean=True,  target_r=0.0, trail_atr=0.0, max_bars=20),
    "retour_moyenne_ou_2R":  dict(exit_on_mean=True,  target_r=2.0, trail_atr=0.0, max_bars=20),
    "objectif_2R":           dict(exit_on_mean=False, target_r=2.0, trail_atr=0.0, max_bars=20),
    "trailing_2ATR":         dict(exit_on_mean=False, target_r=0.0, trail_atr=2.0, max_bars=40),
    "temps_10_barres":       dict(exit_on_mean=False, target_r=0.0, trail_atr=0.0, max_bars=10),
}
GRID = [dict(stop_atr=s, confirm=c, **EXIT_SCHEMES[e])
        for e in EXIT_SCHEMES for s in (1.5, 2.0, 2.5, 3.0) for c in (True, False)]
LABELS = [f"{e}|stop{s}|conf{int(c)}"
          for e in EXIT_SCHEMES for s in (1.5, 2.0, 2.5, 3.0) for c in (True, False)]

spx = panel[(panel["symbol"] == "SPX") & (panel["date"] >= "1962-01-01")]
feat = F.build_panel_features(spx, 400)[
    ["symbol", "date", "open", "high", "low", "close", "atr14"]]

# tous les trades de toutes les configs, une seule fois
print(f"Pre-calcul de {len(GRID)} configurations sur 1962-2018...")
ALL = {}
for lab, kw in zip(LABELS, GRID):
    ALL[lab] = B.run_panel(feat, B.Config(**kw))
print("  fait.")

BOUNDS = [pd.Timestamp(f"{y}-01-01") for y in range(1975, 2019, 5)] + [pd.Timestamp("2019-01-01")]
MIN_TRAIN_TRADES = 40

segments, chosen = [], []
for i in range(len(BOUNDS) - 1):
    train_end, test_end = BOUNDS[i], BOUNDS[i + 1]
    best, best_score = None, -1e9
    for lab in LABELS:
        t = ALL[lab]
        tr = t[t["date_entree"] < train_end]
        if len(tr) < MIN_TRAIN_TRADES:
            continue
        # critere : esperance en R, penalisee si trop peu de trades
        score = tr["R"].mean() - 0.5 * tr["R"].std() / np.sqrt(len(tr))
        if score > best_score:
            best, best_score = lab, score
    if best is None:
        continue
    te = ALL[best]
    seg = te[(te["date_entree"] >= train_end) & (te["date_entree"] < test_end)].copy()
    seg["segment"] = f"{train_end.year}-{test_end.year - 1}"
    seg["config"] = best
    segments.append(seg)
    chosen.append({"segment": seg["segment"].iloc[0] if len(seg) else f"{train_end.year}-{test_end.year-1}",
                   "config_choisie": best,
                   "n_trades_apprentissage": int(len(ALL[best][ALL[best]["date_entree"] < train_end])),
                   "n_trades_test": int(len(seg)),
                   "esperance_R_test": round(float(seg["R"].mean()), 4) if len(seg) else None,
                   "win_rate_test": round(float((seg["R"] > 0).mean() * 100), 2) if len(seg) else None})

wf = pd.concat(segments, ignore_index=True)
wf.to_csv(os.path.join(RESULTS, "05_walkforward_trades.csv"), index=False)
ch = pd.DataFrame(chosen)
ch.to_csv(os.path.join(RESULTS, "05_walkforward_segments.csv"), index=False)

pd.set_option("display.width", 200)
print("\n### Configuration choisie a chaque frontiere (sans voir le futur) ###")
print(ch.to_string(index=False))

st = B.trade_stats(wf)
print("\n### Resultat cumule walk-forward, 100 % hors echantillon ###")
for k, v in st.items():
    print(f"  {k:22s} {v}")

# comparaison : la config figee retenue en 04, sur la meme periode
fixed = B.run_panel(feat, B.Config(stop_atr=3.0, confirm=True, **EXIT_SCHEMES["objectif_2R"]))
fixed = fixed[fixed["date_entree"] >= BOUNDS[0]]
print("\n### Reference : configuration figee objectif_2R/stop3/confirm, meme periode ###")
sf = B.trade_stats(fixed)
for k in ("n_trades", "win_rate_pct", "esperance_R", "profit_factor", "t_stat_R"):
    print(f"  {k:22s} {sf.get(k)}")

# test de permutation : l'esperance observee sort-elle du hasard ?
pval = S.block_bootstrap_pvalue(wf["R"], block=10, n_iter=5000)
print(f"\n  p-value bootstrap par blocs sur l'esperance walk-forward : {pval:.4f}")

with open(os.path.join(RESULTS, "05_walkforward_meta.json"), "w") as fh:
    json.dump({"stats_walkforward": {k: v for k, v in st.items() if k != "motifs"},
               "motifs": st.get("motifs", {}),
               "p_value_bootstrap": pval,
               "n_configs_grille": len(GRID),
               "frontieres": [str(b.date()) for b in BOUNDS]}, fh, indent=2)
