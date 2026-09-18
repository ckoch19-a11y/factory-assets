# Méthodologie

## Le problème à éviter

Un backtest positif ne prouve rien. Avec assez d'essais, n'importe qui trouve une
règle qui a superbement marché sur le passé. Trois pièges tuent la plupart des
stratégies « backtestées » :

1. **La fuite d'information** — le code utilise sans le vouloir une donnée qui
   n'était pas disponible au moment de décider.
2. **Le sur-ajustement** — on a essayé 200 combinaisons et on présente la meilleure.
3. **La confusion signal / exposition** — la stratégie gagne parce qu'elle est
   acheteuse dans un marché qui monte, pas parce que le signal sert à quelque chose.

Chacun est traité explicitement ci-dessous. Le troisième est celui qui a le plus
changé les conclusions de cette étude.

## 1. Les données

| Source | Instrument | Période | Barres | OHLC réel |
|---|---|---|---:|---|
| `vijinho/sp500` | S&P 500 | 1950-2018 | 17 356 | oui (dès 1962) |
| `plotly/datasets` | 500 actions US | 2013-2018 | 618 377 | oui |
| `ff137/bitstamp-btcusd-minute-data` | BTC/USD | 2012-2026 | 7,7 M minutes | oui |
| `datasets/finance-vix` | VIX | 1990-2026 | 9 274 | oui |
| `coinmetrics/data` | BTC, ETH, SOL | 2010-2026 | 9 731 | clôture seule |
| `datasets/oil-prices` | Brent | 1987-2026 | 9 087 | clôture seule |

**Total : 701 445 barres, 507 instruments, 1950 → 2026.**

Le BTC est reconstruit depuis la minute : les barres journalières et 4 h sont
agrégées, ce qui donne un vrai OHLC plutôt qu'une série de clôtures.

Contrôles d'intégrité systématiques (`results/00_data_report.csv`) : cohérence
haut/bas, doublons de date, trous de calendrier, mouvements aberrants. Deux
constats retenus :

- Le S&P 500 avant 1962 ne comporte que des clôtures (17,6 % de barres plates).
  **Toute l'étude commence donc en 1962** pour cet instrument.
- 59 barres sur ~670 000 ont un haut ou un bas légèrement incohérent. Le
  backtester les borne au lieu de les corriger silencieusement.

## 2. L'étude d'événements, avant toute stratégie

On mesure d'abord la distribution des rendements futurs conditionnée à chaque
facteur. Une règle sans edge mesurable ici n'a aucune raison d'en avoir une fois
habillée en stratégie.

**450 tests** — 30 conditions × 5 horizons × 3 univers (`results/01_event_study.csv`).

Deux précautions statistiques, sans lesquelles les t-stats ne veulent rien dire :

- **Corrélation transversale.** 500 actions le même jour ne sont pas 500
  observations indépendantes. On agrège donc d'abord en un rendement quotidien de
  portefeuille, puis on teste la série temporelle contre la moyenne transversale
  du même jour. Cela neutralise le facteur marché commun.
- **Chevauchement des horizons.** Un rendement à 10 jours mesuré en *t* et en
  *t+1* partage 9 jours. On utilise des écarts-types de Newey-West.

## 3. Le raffinement : chercher un plateau, pas un pic

**273 tests supplémentaires** (`results/02_refine.csv`) sur la sensibilité aux
paramètres. Le critère n'est pas « quelle valeur donne le meilleur résultat »
mais « l'edge survit-il quand je bouge le paramètre ». Un paramètre dont l'edge
s'effondre dès qu'on le déplace de 10 % est du bruit.

Résultat : le seuil d'écart tient sur toute la plage −0,5 à −2,0 ATR, et la
longueur du filtre de tendance sur toute la plage 100 à 250 barres. Les valeurs
retenues (−1,0 et 200) sont au centre de ces plateaux, pas à leur maximum.

## 4. Le protocole de sélection, fixé d'avance

Décidé **avant** de regarder le moindre résultat :

- **Apprentissage** : S&P 500 1962-1999 et 500 actions US 2013-2015.
- **Vérification** : S&P 500 2000-2018 et 500 actions US 2016-2018.
- **BTC 2012-2026 n'entre jamais dans la sélection** — test inter-classe d'actifs,
  entièrement hors échantillon.

40 configurations de gestion évaluées (`results/03_selection_IS.csv`). Les deux
classements possibles (meilleure espérance médiane, meilleure espérance minimale)
sont tous deux reportés, pour ne pas choisir après coup celui qui arrange
(`results/04_validation_OOS.csv`).

## 5. Le walk-forward ancré

Le test le plus proche de la réalité : à chaque frontière de cinq ans, on
re-sélectionne la configuration **en n'utilisant que le passé**, puis on la trade
sur les cinq années suivantes sans y toucher. On concatène tous les segments.

S&P 500, 1975-2018, 9 segments, **100 % hors échantillon**
(`results/05_walkforward_*.csv`) :

```
314 trades · 45,2 % de réussite · gain/perte 1,97
espérance +0,212 R · facteur de profit 1,63 · t = 3,12
p-value bootstrap par blocs = 0,0042
```

Un seul segment sur neuf est négatif (1975-1979). À partir de 1990, le
walk-forward converge de façon stable vers la même configuration de gestion.

## 6. Les contrôles anti-illusion

`results/16_controles_sanity.csv`

| Contrôle | Attendu si le moteur est sain | Mesuré |
|---|---|---|
| Marche aléatoire de même volatilité | espérance ≤ 0 | −0,150 R, **0/20 tirages positifs** |
| Rendements mélangés | espérance ≤ 0 | −0,173 R, **1/20 tirages positifs** |
| Signal retardé de 1, 2, 5, 10 barres | dégradation progressive | 0,331 → 0,324 → 0,234 → 0,209 → 0,211 |

Le troisième point mérite une explication : une **fuite d'information** s'effondre
dès la première barre de retard, parce que l'information trichée disparaît d'un
coup. Un **vrai edge de timing** se dégrade progressivement et se stabilise. C'est
ce qu'on observe.

## 7. Le contrôle décisif : contre l'entrée aléatoire

C'est celui qui a changé les conclusions.

On compare la règle à des **entrées prises au hasard dans le même régime
haussier**, avec exactement la même gestion (même stop, même suiveur, même durée
maximale, mêmes frais) et le même nombre de trades. 30 tirages.

Si la règle ne bat pas nettement le hasard, alors le signal ne sert à rien : c'est
seulement le fait d'être acheteur dans une tendance haussière qui rapporte.

`results/17_controle_entree.csv` :

| Univers | Règle | Aléatoire (médiane) | Écart | Tirages battus |
|---|---:|---:|---:|---:|
| S&P 500 1962-2018 | +0,331 R | +0,089 R | **+0,242 R** | 30/30 |
| 500 actions 2013-2018 | +0,103 R | +0,022 R | **+0,081 R** | 30/30 |
| BTC 2012-2026 | +0,318 R | +0,346 R | **−0,028 R** | 9/30 |

**Sur BTC, l'entrée sur repli n'apporte rien.** Ce résultat négatif a déclenché
l'étude de la variante inverse (achat de l'impulsion), qui, elle, bat 30 tirages
sur 30 — en apprentissage 2012-2019 comme en vérification 2020-2026
(`results/18_crypto_variantes.csv`), et se retrouve indépendamment sur ETH
(`results/20_verif_croisee_crypto.csv`).

## 8. La correction pour tests multiples

Sharpe déflaté (Bailey & López de Prado). Il corrige le Sharpe observé du fait
qu'on a essayé plusieurs configurations et gardé la meilleure. La hauteur de barre
dépend de la **variance des Sharpe obtenus sur l'ensemble des configurations
essayées** — l'omettre est l'erreur classique qui rend le test inutilisable ; elle
est ici calculée empiriquement sur les 40 configurations de la grille.

| Configuration | Sharpe par trade | P(Sharpe réel > 0) |
|---|---:|---:|
| S&P 500, repli, mode A | 0,245 | **95,8 %** |
| S&P 500, repli, mode B | 0,268 | 87,7 % |
| BTC, impulsion, mode A | 0,449 | > 99,9 % |
| BTC, repli, mode A | 0,198 | 66,9 % |
| BTC 4 h | −0,069 | 0 % |

## 9. Ce que le backtester suppose

Toutes les hypothèses vont dans le sens défavorable :

- signal calculé sur la clôture de *t*, **entrée à l'ouverture de *t+1*** ;
- stop et objectif vérifiés en intrabarre ;
- si stop **et** objectif sont atteignables dans la même barre, on suppose que le
  **stop** part en premier — on ne sait pas dans quel ordre ils ont été touchés ;
- un gap au-delà du stop sort **au prix d'ouverture**, pas au prix du stop ;
- frais + slippage prélevés à l'entrée **et** à la sortie : 20 bps aller-retour en
  actions, 40 bps en crypto ;
- une seule position ouverte par instrument à la fois ;
- aucun signal n'est pris sur la barre de sortie du trade précédent.

## 10. Le décompte honnête des tests

| Étape | Tests |
|---|---:|
| Étude d'événements | 450 |
| Raffinement des paramètres | 273 |
| Grille de gestion | 40 |
| Grille short | 36 |
| Variantes crypto | 25 |
| **Total** | **824** |

Ce nombre est ce qui justifie le Sharpe déflaté, le walk-forward et le contrôle
contre l'entrée aléatoire. Sans eux, 824 essais produisent forcément quelques
résultats spectaculaires par pur hasard.
