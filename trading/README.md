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
| 500 actions US 2013-2018 | repli | 11 124 | 40,7 % | 1,83 | **+0,095 R** | 1,25 | 30/30 |
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

## Crypto : quel actif, quel réglage

Mesuré sur **10 actifs crypto, 29 107 barres journalières** (OHLCV reconstruit
depuis la minute Binance), chacun depuis sa cotation, plus BTC depuis 2012.

**L'actif à privilégier est BTC.** Classé par *apport du signal* — l'espérance
moins celle d'une entrée aléatoire dans le même régime, seule mesure qui juge
la règle plutôt que l'exposition :

| Actif | Trades | Réussite | Espérance | Apport signal | 1ʳᵉ moitié | 2ᵉ moitié |
|---|---:|---:|---:|---:|---:|---:|
| SOL | 25 | 44,0 % | +1,709 R | +1,178 R | +3,735 | **−0,160** |
| **BTC** | **38** | **44,7 %** | **+1,276 R** | **+0,845 R** | **+1,492** | **+1,060** |
| BNB | 42 | 38,1 % | +1,209 R | +0,624 R | +1,935 | +0,482 |
| ETH | 39 | 46,2 % | +0,534 R | +0,177 R | +0,346 | +0,712 |
| ZEC | 44 | 25,0 % | −0,135 R | **−0,241 R** | −0,486 | +0,217 |

SOL affiche un apport supérieur mais son edge a disparu en seconde moitié.
BTC est le seul actif dont les deux moitiés sont fortement positives, avec le
meilleur t (2,35) et la meilleure p-value (0,0000) — et la meilleure liquidité,
donc les frais réels les plus bas et les données d'order flow les plus fiables.

**Réglage crypto retenu** : seuil 2 ATR, stop 1,5 ATR, suiveur 3 ATR.
381 trades, 36,5 % de réussite, gain/perte 3,8, espérance **+0,693 R**,
facteur de profit 2,20, **8 années positives sur 9**, pire année −0,6 R.

Deux réglages rapportaient deux à trois fois plus. Ils sont écartés parce que
leur **trimestre médian est négatif** et qu'ils ont 81 à 88 % de chances de
produire une série de plus de 15 pertes consécutives. Un système qu'on
n'arrive pas à tenir ne rapporte rien.

Détail complet : [docs/04_crypto.md](docs/04_crypto.md).

## Contenu

```
pine/VRC2_indicateur.pine  l'indicateur à jour : niveau d'entrée projeté, stop
                           suiveur, paliers en R, plan de trade, tableau de bord
pine/VRC2_strategy.pine    la même logique en strategy, pour rejouer le backtest
pine/VRC_indicateur.pine   version précédente, conservée pour référence
pine/VRC_strategy.pine     idem
research/                  toute l'étude, reproductible de bout en bout
results/                   chaque chiffre cité, en CSV
docs/01_methodologie.md    comment c'est mesuré, et pourquoi comme ça
docs/02_resultats.md       tous les résultats, y compris ceux qui déplaisent
docs/03_mode_emploi.md     utilisation et gestion du risque
docs/04_crypto.md          classement des actifs, réglages, simulations, 1 %/jour
docs/05_order_flow.md      quoi regarder pour confirmer ou annuler un signal
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
5. **1 % par jour est arithmétiquement hors d'atteinte.** Cela ferait ×37,8 par
   an, contre 27 % pour le réglage retenu et 39 % pour le meilleur fonds jamais
   mesuré. Y prétendre impose une taille de position qui mène à la ruine :
   voir [docs/04_crypto.md](docs/04_crypto.md) section 6.
6. **~7 signaux par an et par instrument.** C'est une approche de swing, pas de
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
