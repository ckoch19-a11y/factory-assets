# VRC — Régime, Volatilité, Continuation

Indicateur TradingView + l'étude qui l'a produit.

## Le résultat central

**Les actions et le crypto fonctionnent à l'envers l'un de l'autre.** C'est la seule
chose vraiment intéressante que l'étude ait trouvée, et c'est ce que l'indicateur
exploite.

- **Actions / indices** : dans une tendance haussière, il faut acheter la **faiblesse**.
  Un écart marqué *sous* la moyenne rapide, mesuré en ATR, précède un rendement
  nettement supérieur à la moyenne. Acheter la force ne rapporte rien.
- **Crypto** : exactement l'inverse. Acheter le repli n'apporte rien de plus qu'une
  entrée au hasard dans la même tendance. C'est l'achat de la **force** qui paie.

| Univers | Entrée | Trades | Réussite | Gain/Perte | Espérance | PF | Bat le hasard |
|---|---|---:|---:|---:|---:|---:|---:|
| S&P 500 1962-2018 | repli | 291 | 48,5 % | 2,13 | **+0,331 R** | 2,01 | 30/30 |
| S&P 500 1962-2018 | impulsion | 341 | 39,6 % | 1,68 | +0,038 R | 1,10 | 0/30 |
| 500 actions US 2013-2018 | repli | 11 293 | 41,5 % | 1,80 | **+0,103 R** | 1,28 | 30/30 |
| 500 actions US 2013-2018 | impulsion | 14 178 | 38,7 % | 1,58 | −0,001 R | 1,00 | 0/30 |
| BTC 2012-2026 | repli | 87 | 44,8 % | 2,24 | +0,297 R | 1,82 | 10/30 |
| BTC 2012-2026 | impulsion | 134 | 56,7 % | 2,94 | **+0,736 R** | 3,85 | 30/30 |

« Bat le hasard » = nombre de tirages, sur 30, d'entrées **aléatoires dans le même
régime haussier avec exactement la même gestion**, que la règle surclasse. C'est le
contrôle qui compte : sans lui, on confond un signal avec le simple fait d'être
acheteur dans un marché qui monte.

## Base de mesure

701 445 barres · 507 instruments · 1950 → 2026 · frais et slippage inclus ·
entrée à l'ouverture de la barre suivant le signal.

| Source | Contenu |
|---|---|
| S&P 500 | OHLCV journalier, 1950-2018 (17 356 barres, tous les régimes) |
| 500 actions US | OHLCV journalier, 2013-2018 (618 377 barres) |
| BTC/USD Bitstamp | OHLCV **1 minute**, 2012-2026, agrégé en journalier et 4 h |
| VIX, Brent, ETH, SOL | séries de contrôle |

## Contenu

```
pine/VRC_indicateur.pine   l'indicateur (signaux, stop, objectif, tableau de bord)
pine/VRC_strategy.pine     la même logique en strategy, pour rejouer le backtest
research/                  toute l'étude, reproductible de bout en bout
results/                   chaque chiffre cité, en CSV
docs/01_methodologie.md    comment c'est mesuré, et pourquoi comme ça
docs/02_resultats.md       tous les résultats, y compris ceux qui déplaisent
docs/03_mode_emploi.md     utilisation avec order flow et macro, gestion du risque
```

## À lire avant d'utiliser

1. **Le profil doit correspondre à la classe d'actifs.** Profil actions sur une
   crypto — ou l'inverse — ramène l'espérance à zéro. C'est le réglage le plus
   important, loin devant tous les autres.
2. **Journalier uniquement.** En 4 h sur BTC, l'espérance mesurée est **négative**
   (−0,072 R sur 423 trades). Les frais mangent l'edge avant vous.
3. **L'edge crypto décroît.** Espérance BTC par période : 1,26 R (2012-2015) →
   0,73 → 0,47 → 0,28 R (2024-2026). Toujours positif, mais divisé par quatre en
   dix ans. Le marché se professionnalise.
4. **Pas de vente à découvert en actions.** 0 configuration rentable sur 36 testées.
5. **~7 signaux par an et par instrument.** C'est une approche de swing, pas de
   scalping. Pour avoir du flux, il faut une liste de surveillance.

## Reproduire l'étude

```bash
pip install numpy pandas scipy pyarrow
cd research
python3 01_build_dataset.py      # construit le panel (données à récupérer, voir docs)
python3 02_event_study.py        # quels facteurs ont un edge mesurable
python3 06_walkforward.py        # validation walk-forward ancrée
python3 10_sanity.py             # contrôles anti-fuite d'information
python3 11_controle_entree.py    # le contrôle décisif contre l'entrée aléatoire
python3 13_consolide.py          # tableau final
```
