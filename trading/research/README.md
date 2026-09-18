# Étude

Tout le code qui produit les chiffres de `../docs/`. Reproductible de bout en bout.

## Ordre d'exécution

```bash
pip install numpy pandas scipy pyarrow
./00_fetch_data.sh            # récupère les sources publiques (~180 Mo)
python3 01_build_dataset.py   # panel propre + rapport d'intégrité
python3 02_event_study.py     # 450 tests : quels facteurs ont un edge
python3 03_refine.py          # 273 tests : sensibilité des paramètres
python3 04_backtest.py        # 40 configurations, sélection in-sample
python3 05_validate.py        # validation hors échantillon
python3 06_walkforward.py     # walk-forward ancré 1975-2018
python3 07_final.py           # analyse des deux modes de gestion
python3 08_shorts.py          # le short est-il récupérable ? (non)
python3 09_final_longonly.py  # version long seul + Sharpe déflaté
python3 10_sanity.py          # contrôles anti-fuite d'information
python3 11_controle_entree.py # contrôle contre l'entrée aléatoire
python3 12_crypto.py          # pourquoi le crypto s'inverse
python3 13_consolide.py       # tableau final
```

## Modules

| Fichier | Rôle |
|---|---|
| `lib/data.py` | chargement, normalisation, contrôles d'intégrité |
| `lib/features.py` | features techniques, toutes causales |
| `lib/backtest.py` | backtester event-driven, hypothèses conservatrices |
| `lib/stats.py` | Newey-West, bootstrap par blocs, Sharpe déflaté |
| `lib/pinecheck.py` | vérificateur statique Pine Script |

## Règle appliquée partout

Une feature à l'index *t* n'utilise que les barres ≤ *t*. Le signal dérivé de *t*
s'exécute à l'**ouverture de t+1**. Les contrôles de `10_sanity.py` vérifient que
cette règle tient : sur données aléatoires, 0 tirage positif sur 20.
