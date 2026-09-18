"""Verifie que le Pine Script applique EXACTEMENT la strategie backtestee.

Le compilateur TradingView n'est pas disponible ici. Ce qu'on peut faire, et
qui compte davantage, c'est verifier la LOGIQUE : la machine a etats du
fichier .pine est retranscrite ici barre par barre, en respectant le modele
d'execution de Pine (variables `var` persistantes, une passe par barre), puis
on compare trade par trade avec lib/backtest.py.

Si les deux divergent, c'est que l'indicateur ne fait pas ce que les chiffres
annonces mesurent. C'est le seul test qui peut le detecter.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import data as D, features as F, backtest as B  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
PINE = os.environ.get("VRC_PINE", os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pine", "VRC_indicateur.pine"))
NA = float("nan")


def constantes_du_pine() -> dict:
    """Lit les constantes de gestion DANS le fichier .pine.

    Sans cela, la transcription Python ci-dessous pourrait derailler du vrai
    fichier sans que rien ne le signale : on testerait alors une strategie que
    TradingView n'execute pas.
    """
    import re
    src = open(PINE, encoding="utf-8").read()

    def ternaire(nom):
        m = re.search(rf"^{nom}\s*=\s*isModeB\s*\?\s*([\d.]+)\s*:\s*([\d.]+)",
                      src, re.M)
        if not m:
            raise SystemExit(f"constante '{nom}' introuvable dans {PINE}")
        return float(m.group(1)), float(m.group(2))

    def defaut(nom, fn):
        m = re.search(rf"^{nom}\s*=\s*input\.{fn}\(\s*(-?[\d.]+)", src, re.M)
        if not m:
            raise SystemExit(f"parametre '{nom}' introuvable dans {PINE}")
        return float(m.group(1))

    b_stop, a_stop = ternaire("stopMult")
    b_tgt, a_tgt = ternaire("targetR")
    b_trail, a_trail = ternaire("trailMult")
    b_bars, a_bars = ternaire("maxBars")
    return {
        "A": dict(stop_atr=a_stop, target_r=a_tgt, trail_atr=a_trail,
                  max_bars=int(a_bars), confirm=False),
        "B": dict(stop_atr=b_stop, target_r=b_tgt, trail_atr=b_trail,
                  max_bars=int(b_bars), confirm=True),
        "repli": defaut("extThresh", "float"),
        "impulsion": defaut("impThresh", "float"),
        "cout_bps": defaut("coutBps", "float"),
    }


def _na(x) -> bool:
    return x is None or (isinstance(x, float) and math.isnan(x))


def pine_state_machine(df: pd.DataFrame, sig_long, sig_short, atr,
                       stop_mult: float, target_r: float, trail_mult: float,
                       max_bars: int, cout_bps: float) -> list[dict]:
    """Transcription fidele du bloc "Etat de position" de VRC_indicateur.pine.

    Chaque variable `var` du Pine est ici une variable locale persistante, et
    chaque bloc `if` est execute dans le meme ordre, une fois par barre.
    """
    o = df["open"].values
    h = df["high"].values
    l = df["low"].values
    c = df["close"].values
    dates = df["date"].values

    pending = 0
    dir_ = 0
    entryPx = stopPx = targetPx = riskPx = bestPx = atrAtSig = NA
    barsIn = 0
    trades: list[dict] = []
    cUnit = cout_bps / 20000.0

    for i in range(len(df)):
        justEntered = False
        justExited = False

        # 1) ouverture de la position armee a la barre precedente
        if pending != 0 and dir_ == 0:
            dir_ = pending
            entryPx = o[i]
            stopPx = o[i] - pending * stop_mult * atrAtSig
            riskPx = abs(o[i] - stopPx)
            targetPx = o[i] + pending * target_r * riskPx if target_r > 0 else NA
            bestPx = o[i]
            barsIn = 0
            pending = 0
            justEntered = True
            entry_i = i

        # 2) gestion de la position ouverte, barre d'entree incluse
        if dir_ != 0:
            if not justEntered:
                barsIn += 1
            hitGap = (o[i] <= stopPx) if dir_ == 1 else (o[i] >= stopPx)
            hitStop = (l[i] <= stopPx) if dir_ == 1 else (h[i] >= stopPx)
            hitTgt = (not _na(targetPx)) and (
                (h[i] >= targetPx) if dir_ == 1 else (l[i] <= targetPx))
            exitPx = NA
            motif = ""
            if hitGap:
                exitPx, motif = o[i], "gap_stop"
            elif hitStop:
                exitPx, motif = stopPx, "stop"
            elif hitTgt:
                exitPx, motif = targetPx, "target"
            elif barsIn >= max_bars:
                exitPx, motif = c[i], "temps"

            if (not _na(exitPx)) and riskPx > 0:
                fill0 = entryPx * (1.0 + dir_ * cUnit)
                fill1 = exitPx * (1.0 - dir_ * cUnit)
                trades.append({
                    "side": "long" if dir_ == 1 else "short",
                    "date_entree": pd.Timestamp(dates[entry_i]),
                    "date_sortie": pd.Timestamp(dates[i]),
                    "bars": i - entry_i,
                    "entree": float(entryPx),
                    "sortie": float(exitPx),
                    "R": float(dir_ * (fill1 - fill0) / riskPx),
                    "motif": motif,
                })
                justExited = True
                dir_ = 0
                entryPx = stopPx = targetPx = NA
            elif trail_mult > 0:
                bestPx = max(bestPx, h[i]) if dir_ == 1 else min(bestPx, l[i])
                trailPx = bestPx - dir_ * trail_mult * atr[i]
                stopPx = max(stopPx, trailPx) if dir_ == 1 else min(stopPx, trailPx)

        # 3) armement d'un nouveau signal, jamais sur la barre de sortie
        if dir_ == 0 and pending == 0 and not justExited:
            if sig_long[i]:
                pending, atrAtSig = 1, atr[i]
            elif sig_short[i]:
                pending, atrAtSig = -1, atr[i]

    return trades


# ---------------------------------------------------------------------------
panel = pd.read_parquet(os.path.join(D.OUT, "panel_daily.parquet"))

# Les constantes viennent du fichier .pine lui-meme, pas d'une copie.
K = constantes_du_pine()
print("Constantes lues dans VRC_indicateur.pine :")
print(f"  mode A     : {K['A']}")
print(f"  mode B     : {K['B']}")
print(f"  seuil repli    : {K['repli']}   seuil impulsion : {K['impulsion']}")
print(f"  cout A/R (bps) : {K['cout_bps']}\n")

ATTENDU = {"A": dict(stop_atr=2.0, target_r=0.0, trail_atr=2.0, max_bars=40, confirm=False),
           "B": dict(stop_atr=3.0, target_r=2.0, trail_atr=0.0, max_bars=20, confirm=True),
           "repli": -1.0, "impulsion": 1.5}
for k, v in ATTENDU.items():
    if K[k] != v:
        raise SystemExit(f"DERIVE : le .pine donne {k} = {K[k]}, "
                         f"l'etude a valide {v}. Refaire l'etude ou corriger le .pine.")
print("Le .pine porte bien les valeurs validees par l'etude.\n")

MODES = {"A - continuation (trailing)": K["A"], "B - objectif 2R": K["B"]}
PROFILS = {
    "actions (repli)":    lambda g: (g["close"] > g["sma_trend"]) & (g["ext_bt"] < K["repli"]),
    "crypto (impulsion)": lambda g: (g["close"] > g["sma_trend"]) & (g["ext_bt"] > K["impulsion"]),
}
UNIS = {
    "SPX 1962-2018": (panel[(panel["symbol"] == "SPX") & (panel["date"] >= "1962-01-01")], 5.0),
    "BTC 2012-2026": (panel[panel["symbol"] == "BTCUSD"], 10.0),
}

rows, total_ecarts = [], 0
for uni, (raw, fee) in UNIS.items():
    f = F.build_panel_features(raw, 400)[
        ["symbol", "date", "open", "high", "low", "close", "atr14"]]
    for mode, mk in MODES.items():
        for prof, pf in PROFILS.items():
            cfg = B.Config(stop_atr=mk["stop_atr"], target_r=mk["target_r"],
                           trail_atr=mk["trail_atr"], max_bars=mk["max_bars"],
                           confirm=False, exit_on_mean=False, allow_short=False,
                           fee_bps=fee, slip_bps=fee)
            g = B.generate_signals(f, cfg)
            mask = pf(g).fillna(False)
            if mk["confirm"]:
                mask = mask & (g["close"] > g["close"].shift(1)).fillna(False)
            g = g.copy()
            g["sig_long"] = mask.values
            g["sig_short"] = False

            ref = B.run_panel(g, cfg, presignal=True)
            pine = pd.DataFrame(pine_state_machine(
                g.reset_index(drop=True), g["sig_long"].values, g["sig_short"].values,
                g["atr_bt"].values, mk["stop_atr"], mk["target_r"], mk["trail_atr"],
                mk["max_bars"], fee * 4))

            n_ref, n_pine = len(ref), len(pine)
            ecarts = []
            if n_ref != n_pine:
                ecarts.append(f"nombre de trades {n_ref} vs {n_pine}")
            else:
                a = ref.reset_index(drop=True)
                b = pine.reset_index(drop=True)
                if not (a["date_entree"].values == b["date_entree"].values).all():
                    ecarts.append("dates d'entree differentes")
                if not (a["date_sortie"].values == b["date_sortie"].values).all():
                    ecarts.append("dates de sortie differentes")
                dR = float(np.abs(a["R"].values - b["R"].values).max()) if n_ref else 0.0
                if dR > 1e-9:
                    ecarts.append(f"ecart max sur R = {dR:.2e}")
                if not (a["motif"].values == b["motif"].values).all():
                    diff = int((a["motif"].values != b["motif"].values).sum())
                    ecarts.append(f"{diff} motif(s) de sortie differents")
            total_ecarts += len(ecarts)
            rows.append({
                "univers": uni, "mode": mode, "profil": prof,
                "trades_backtest": n_ref, "trades_pine": n_pine,
                "esperance_backtest": round(float(ref["R"].mean()), 6) if n_ref else None,
                "esperance_pine": round(float(pine["R"].mean()), 6) if n_pine else None,
                "identique": "oui" if not ecarts else "NON",
                "ecarts": "; ".join(ecarts) if ecarts else "-",
            })

out = pd.DataFrame(rows)
out.to_csv(os.path.join(RESULTS, "22_verif_pine_vs_backtest.csv"), index=False)
pd.set_option("display.width", 220)
print("### Machine a etats du Pine confrontee au backtester, trade par trade ###\n")
print(out.to_string(index=False))
print(f"\n{len(out)} combinaisons testees, {total_ecarts} ecart(s) au total.")
if total_ecarts == 0:
    print("Le Pine applique exactement la strategie mesuree, couts compris.")
sys.exit(1 if total_ecarts else 0)
