"""Verifie que VRC2_indicateur.pine applique exactement la strategie mesuree.

Meme methode que pour VRC 1 : la machine a etats du .pine est retranscrite ici
barre par barre, et confrontee au backtester trade par trade, sur les 10 actifs
crypto. Les constantes sont lues DANS le fichier .pine, pas recopiees.
"""
from __future__ import annotations
import math, os, re, sys
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import data as D, features as F, backtest as B  # noqa: E402

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
PINE = os.environ.get("VRC2_PINE", os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pine", "VRC2_indicateur.pine"))
NA = float("nan")
_na = lambda x: x is None or (isinstance(x, float) and math.isnan(x))


def constantes():
    src = open(PINE, encoding="utf-8").read()
    def d(nom, fn="float"):
        m = re.search(rf"^{nom}\s*=\s*input\.{fn}\(\s*(-?[\d.]+)", src, re.M)
        if not m:
            raise SystemExit(f"parametre '{nom}' introuvable dans {PINE}")
        return float(m.group(1))
    return {"impThresh": d("impThresh"), "extThresh": d("extThresh"),
            "stopMult": d("stopMult"), "trailMult": d("trailMult"),
            "maxBars": int(d("maxBars", "int")), "coutBps": d("coutBps"),
            "trendLen": int(d("trendLen", "int"))}


def machine(df, sig, atr, stop_mult, trail_mult, max_bars, cout_bps):
    """Transcription fidele du bloc Position de VRC2_indicateur.pine."""
    o, h, l, c = (df[k].values for k in ("open", "high", "low", "close"))
    dates = df["date"].values
    pending = dir_ = 0
    entryPx = stopPx = riskPx = bestPx = atrAtSig = NA
    barsIn = 0; entry_i = None
    cU = cout_bps / 20000.0
    out = []
    for i in range(len(df)):
        justEntered = justExited = False
        if pending != 0 and dir_ == 0:
            dir_ = pending; entryPx = o[i]
            stopPx = o[i] - pending * stop_mult * atrAtSig
            riskPx = abs(o[i] - stopPx); bestPx = o[i]
            barsIn = 0; entry_i = i; pending = 0; justEntered = True
        if dir_ != 0:
            if not justEntered:
                barsIn += 1
            hitGap = (o[i] <= stopPx) if dir_ == 1 else (o[i] >= stopPx)
            hitStop = (l[i] <= stopPx) if dir_ == 1 else (h[i] >= stopPx)
            exitPx = NA; motif = ""
            if hitGap:
                exitPx, motif = o[i], "gap_stop"
            elif hitStop:
                exitPx, motif = stopPx, "stop"
            elif barsIn >= max_bars:
                exitPx, motif = c[i], "temps"
            if not _na(exitPx) and riskPx > 0:
                f0 = entryPx * (1.0 + dir_ * cU); f1 = exitPx * (1.0 - dir_ * cU)
                out.append({"date_entree": pd.Timestamp(dates[entry_i]),
                            "date_sortie": pd.Timestamp(dates[i]),
                            "bars": i - entry_i, "entree": float(entryPx),
                            "sortie": float(exitPx), "motif": motif,
                            "R": float(dir_ * (f1 - f0) / riskPx)})
                justExited = True; dir_ = 0; entryPx = stopPx = NA
            elif trail_mult > 0:
                bestPx = max(bestPx, h[i]) if dir_ == 1 else min(bestPx, l[i])
                tp = bestPx - dir_ * trail_mult * atr[i]
                stopPx = max(stopPx, tp) if dir_ == 1 else min(stopPx, tp)
        if dir_ == 0 and pending == 0 and not justExited and sig[i]:
            pending, atrAtSig = 1, atr[i]
    return out


K = constantes()
print("Constantes lues dans VRC2_indicateur.pine :")
for k, v in K.items():
    print(f"  {k:12s} {v}")
ATTENDU = {"impThresh": 2.0, "extThresh": -1.0, "stopMult": 1.5,
           "trailMult": 3.0, "maxBars": 40, "trendLen": 200}
for k, v in ATTENDU.items():
    if K[k] != v:
        raise SystemExit(f"DERIVE : le .pine donne {k}={K[k]}, l'etude a valide {v}")
print("\nLe .pine porte les valeurs validees par l'etude.\n")

CRYPTO = pd.read_parquet("/tmp/mkt/clean/crypto_daily.parquet")
FEE = K["coutBps"] / 4.0
rows, ecarts_tot = [], 0
for sym, g0 in CRYPTO.groupby("symbol"):
    f = F.build_panel_features(g0.sort_values("date"), 300)[
        ["symbol", "date", "open", "high", "low", "close", "atr14"]]
    cfg = B.Config(trend_len=K["trendLen"], stop_atr=K["stopMult"], target_r=0.0,
                   trail_atr=K["trailMult"], max_bars=K["maxBars"], confirm=False,
                   exit_on_mean=False, allow_short=False, fee_bps=FEE, slip_bps=FEE)
    g = B.generate_signals(f, cfg).assign(sig_short=False).reset_index(drop=True)
    g["sig_long"] = ((g["close"] > g["sma_trend"]) & (g["ext_bt"] > K["impThresh"])).fillna(False)
    ref = B.run_panel(g, cfg, presignal=True)
    pine = pd.DataFrame(machine(g, g["sig_long"].values, g["atr_bt"].values,
                                K["stopMult"], K["trailMult"], K["maxBars"], K["coutBps"]))
    e = []
    if len(ref) != len(pine):
        e.append(f"{len(ref)} vs {len(pine)} trades")
    elif len(ref):
        a = ref.reset_index(drop=True); b = pine.reset_index(drop=True)
        if not (a["date_entree"].values == b["date_entree"].values).all(): e.append("dates entree")
        if not (a["date_sortie"].values == b["date_sortie"].values).all(): e.append("dates sortie")
        dR = float(np.abs(a["R"].values - b["R"].values).max())
        if dR > 1e-9: e.append(f"R max {dR:.2e}")
        if not (a["motif"].values == b["motif"].values).all(): e.append("motifs")
    ecarts_tot += len(e)
    rows.append({"actif": sym, "trades_backtest": len(ref), "trades_pine": len(pine),
                 "esp_backtest": round(float(ref["R"].mean()), 6) if len(ref) else None,
                 "esp_pine": round(float(pine["R"].mean()), 6) if len(pine) else None,
                 "identique": "oui" if not e else "NON", "ecarts": "; ".join(e) or "-"})

out = pd.DataFrame(rows)
out.to_csv(os.path.join(RESULTS, "40_verif_pine2.csv"), index=False)
pd.set_option("display.width", 200)
print(out.to_string(index=False))
print(f"\n{len(out)} actifs verifies, {ecarts_tot} ecart(s).")
if ecarts_tot == 0:
    print("VRC2 applique exactement la strategie mesuree, couts compris.")
sys.exit(1 if ecarts_tot else 0)
