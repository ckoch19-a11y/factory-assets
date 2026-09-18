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
python3 14_verif_doc.py       # la doc dit-elle bien ce que les CSV disent ?
python3 15_verif_pine.py      # le Pine applique-t-il bien la stratégie mesurée ?
```

## Les deux vérifications de fin

`14_verif_doc.py` recalcule 24 chiffres cités dans `../docs/` depuis les CSV de
`../results/` et sort en erreur au moindre écart. Une documentation qui dérive
des résultats est pire qu'une documentation absente.

`15_verif_pine.py` fait deux choses. Il lit les constantes de gestion **dans le
fichier `.pine` lui-même** et vérifie qu'elles valent bien ce que l'étude a
validé ; puis il rejoue la machine à états du Pine, transcrite ligne à ligne en
Python, et la compare trade par trade au backtester. Résultat attendu, et
obtenu : 8 combinaisons, 0 écart, espérances identiques à la 6ᵉ décimale.

Sans ce second script, rien ne garantirait que l'indicateur exécute la
stratégie dont on annonce les chiffres.

## Modules

| Fichier | Rôle |
|---|---|
| `lib/data.py` | chargement, normalisation, contrôles d'intégrité |
| `lib/features.py` | features techniques, toutes causales |
| `lib/backtest.py` | backtester event-driven, hypothèses conservatrices |
| `lib/stats.py` | Newey-West, bootstrap par blocs, Sharpe déflaté |
| `lib/pinecheck.py` | vérificateur statique Pine Script (v6) |

Le vérificateur Pine couvre : parenthèses, tabulations, caractères non ASCII
dans le code, appels réservés au niveau global, fonctions déclarées dans un
bloc, `var` indenté, blocs sans corps, `:=` sur un nom non déclaré,
**indentation des lignes de continuation** (Pine exige un nombre d'espaces qui
n'est pas un multiple de 4), **division entière involontaire** (`int / int`
tronque silencieusement), et trois règles propres à v6 : `na()`/`nz()` sur un
booléen, `if` sur un nombre sans comparaison, et appel `ta.*` à droite d'un
`and`/`or` (évaluation paresseuse).

Il est testé contre des fichiers volontairement cassés : chaque règle doit
déclencher sur son contrôle négatif.

## Règle appliquée partout

Une feature à l'index *t* n'utilise que les barres ≤ *t*. Le signal dérivé de *t*
s'exécute à l'**ouverture de t+1**. Les contrôles de `10_sanity.py` vérifient que
cette règle tient : sur données aléatoires, 0 tirage positif sur 20.
