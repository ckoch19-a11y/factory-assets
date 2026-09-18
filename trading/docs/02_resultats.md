# Résultats

Tous les chiffres de cette page sortent des CSV de `results/`. Rien n'est arrondi
en votre faveur.

Rappel de lecture : **R** = multiple du risque initial. Un trade à +2 R a rapporté
deux fois ce qui était risqué. L'**espérance en R** est la seule mesure qui compte,
parce qu'elle ne dépend ni de la taille de position ni du capital.

---

## 1. Le résultat principal

Même gestion des deux côtés, frais inclus, entrée à l'ouverture suivante.

| Univers | Entrée | Trades | Réussite | Gain moy. | Perte moy. | G/P | Espérance | PF | t | p |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| S&P 500 1962-2018 | repli | 291 | 48,45 % | +1,363 R | −0,639 R | 2,13 | **+0,331 R** | 2,01 | 4,18 | <0,001 |
| S&P 500 1962-2018 | impulsion | 341 | 39,59 % | +1,056 R | −0,629 R | 1,68 | +0,038 R | 1,10 | 0,66 | 0,224 |
| 500 actions 2013-2018 | repli | 11 293 | 41,45 % | +1,150 R | −0,637 R | 1,80 | **+0,103 R** | 1,28 | 9,12 | <0,001 |
| 500 actions 2013-2018 | impulsion | 14 178 | 38,74 % | +1,008 R | −0,639 R | 1,58 | −0,001 R | 1,00 | −0,11 | 0,465 |
| BTC 2012-2026 | repli | 87 | 44,83 % | +1,475 R | −0,659 R | 2,24 | +0,297 R | 1,82 | 1,85 | 0,019 |
| BTC 2012-2026 | impulsion | 134 | 56,72 % | +1,753 R | −0,596 R | 2,94 | **+0,736 R** | 3,85 | 5,20 | <0,001 |

Le croisement est net : chaque classe d'actifs a son entrée qui marche, et l'autre
qui ne marche pas. Ce n'est pas un résultat isolé qu'on pourrait attribuer au
hasard — c'est un motif symétrique qui se retrouve sur trois univers indépendants.

## 2. Contre l'entrée aléatoire — le seul contrôle qui compte

30 tirages d'entrées au hasard dans le **même régime haussier**, avec exactement la
même gestion et le même nombre de trades.

| Univers | Entrée validée | Aléatoire | Écart | Tirages battus |
|---|---:|---:|---:|---:|
| S&P 500 | +0,331 R | +0,089 R | +0,242 R | **30/30** |
| 500 actions US | +0,103 R | +0,022 R | +0,081 R | **30/30** |
| BTC (impulsion) | +0,736 R | +0,334 R | +0,402 R | **30/30** |
| BTC (repli) | +0,297 R | +0,322 R | −0,024 R | 10/30 |

Le taux de réussite de l'entrée aléatoire sur le S&P 500 est de 41,4 %, contre
48,5 % pour la règle. L'écart de 7 points ne vient pas de l'exposition : il vient
du moment choisi.

## 3. Validation hors échantillon

### Walk-forward ancré, S&P 500 1975-2018

Configuration re-choisie tous les 5 ans sans voir le futur, puis tradée telle
quelle. **100 % hors échantillon.**

```
314 trades · 45,2 % de réussite · gain/perte 1,97 · espérance +0,212 R
facteur de profit 1,63 · t = 3,12 · p bootstrap = 0,0042
```

| Segment | Trades | Réussite | Espérance |
|---|---:|---:|---:|
| 1975-1979 | 19 | 31,6 % | −0,316 R |
| 1980-1984 | 24 | 62,5 % | +0,310 R |
| 1985-1989 | 33 | 54,5 % | +0,396 R |
| 1990-1994 | 41 | 48,8 % | +0,072 R |
| 1995-1999 | 37 | 51,4 % | +0,599 R |
| 2000-2004 | 40 | 42,5 % | +0,095 R |
| 2005-2009 | 41 | 39,0 % | +0,103 R |
| 2010-2014 | 46 | 37,0 % | +0,294 R |
| 2015-2018 | 33 | 42,4 % | +0,162 R |

### BTC impulsion : apprentissage 2012-2019, vérification 2020-2026

| Seuil | Apprentissage | Vérification | Bat le hasard (vérif.) |
|---|---:|---:|---:|
| +0,5 ATR | +0,753 R | +0,218 R | 30/30 |
| +1,0 ATR | +0,871 R | +0,304 R | 30/30 |
| +1,5 ATR | +0,971 R | +0,399 R | 30/30 |

Monotone dans les deux périodes : le résultat ne dépend pas d'un réglage précis,
ce qui est le signe d'un effet réel plutôt que d'un pic de sur-ajustement.

### Vérification indépendante sur ETH

ETH 2015-2026 (clôtures seules, donc indicatif) : impulsion +1,103 R, bat 30/30
tirages aléatoires ; repli +0,081 R, bat 0/30. **Même sens que BTC, actif
différent, période différente.**

## 4. Stabilité dans le temps

### S&P 500, repli, par décennie

| Décennie | Trades | Réussite | Espérance | R cumulé |
|---|---:|---:|---:|---:|
| 1960s | 20 | 45,0 % | +0,369 R | +7,4 |
| **1970s** | 25 | **24,0 %** | **−0,185 R** | **−4,6** |
| 1980s | 61 | 59,0 % | +0,669 R | +40,8 |
| 1990s | 69 | 53,6 % | +0,381 R | +26,3 |
| 2000s | 46 | 47,8 % | +0,042 R | +1,9 |
| 2010s | 70 | 44,3 % | +0,350 R | +24,5 |

Cinq décennies sur six positives. **Les années 1970 sont franchement mauvaises** —
stagflation, marché sans direction, replis qui ne rebondissent pas. Un régime de ce
type reviendra ; il faut s'attendre à plusieurs années difficiles.

### BTC, impulsion, par période — l'edge se referme

| Période | Trades | Réussite | Espérance | R cumulé |
|---|---:|---:|---:|---:|
| 2012-2015 | 36 | 66,7 % | +1,262 R | +45,4 |
| 2016-2019 | 43 | 62,8 % | +0,726 R | +31,2 |
| 2020-2023 | 34 | 52,9 % | +0,472 R | +16,1 |
| **2024-2026** | 21 | **33,3 %** | **+0,281 R** | +5,9 |

**L'espérance a été divisée par quatre en dix ans, et le taux de réussite est passé
de 67 % à 33 %.** L'edge reste positif mais se referme à mesure que le marché se
professionnalise. Ne comptez pas sur les chiffres de 2012-2015 : la période qui
vous concerne est la dernière ligne.

## 4 bis. À quoi ressemble une mauvaise passe

Chiffres mesurés, pas estimés. C'est ce qu'il faut être capable de traverser.

| Configuration | Trades | Pertes d'affilée (max) | Pire trade | Pire creux cumulé |
|---|---:|---:|---:|---:|
| S&P 500, repli, mode A | 291 | **7** | −1,16 R | **−7,0 R** |
| S&P 500, repli, mode B | 119 | 5 | −1,09 R | −5,8 R |
| BTC, impulsion, mode A | 134 | 5 | −1,09 R | −4,3 R |

Le « pire trade » dépasse légèrement −1 R à cause des gaps d'ouverture : quand le
marché ouvre sous le stop, on sort au prix d'ouverture, pas au prix du stop. C'est
la seule façon dont une perte peut excéder le risque prévu, et le backtest la
modélise.

À 1 % de risque par trade, le pire creux du S&P 500 correspond à environ **−7 % de
capital**, étalé sur plusieurs mois. Si ce chiffre vous paraît insupportable,
baissez le risque par trade — pas les paramètres du signal.

## 5. Comparaison avec l'achat-conservation

| Univers | Approche | CAGR | Drawdown max | MAR | Temps exposé |
|---|---|---:|---:|---:|---:|
| S&P 500 1962-2018 | VRC repli, risque 1 %/trade | 20,0 % | −6,9 % | 2,89 | 22,5 % |
| S&P 500 1962-2018 | achat-conservation | 6,4 % | −56,8 % | 0,11 | 100 % |
| BTC 2012-2026 | VRC impulsion, risque 1 %/trade | 105,3 % | −4,2 % | 25,2 | 19,6 % |
| BTC 2012-2026 | achat-conservation | 57,1 % | −84,9 % | 0,67 | 100 % |

**Ces CAGR ne sont pas une promesse.** Ils supposent un risque constant de 1 % du
capital courant par trade, une exécution parfaite et une discipline sans faille sur
des décennies. Le chiffre qui a du sens ici est le **MAR** (rendement rapporté au
pire drawdown) et surtout le **temps exposé** : la stratégie obtient plus en étant
au marché un cinquième du temps. C'est là qu'est la vraie valeur, pas dans le CAGR.

## 6. Ce qui a été testé et rejeté

Autant que les résultats positifs.

| Idée testée | Verdict | Mesure |
|---|---|---|
| **Vente à découvert en actions** | **rejetée** | **0 configuration rentable sur 36** |
| Cassure de plus haut 20 j / 252 j | rejetée | excédent −0,34 % à 20 j, t = −2,07 |
| RSI(2) < 10 sans filtre de tendance | rejeté | BTC : excédent −3,3 % à 20 j, t = −2,67 |
| RSI(2) < 5 (plus extrême = mieux ?) | rejeté | pire que RSI(2) < 10 |
| Filtre de volatilité (éviter la vol haute) | rejeté | dégrade BTC de 4,6 points |
| Tour du mois, effet lundi | rejetés | excédent ≈ 0 partout |
| Clôture dans le haut/bas de barre | rejeté | ne se transporte pas d'un actif à l'autre |
| Confirmation par bougie de retournement | partiel | aide sur S&P 500, neutre ailleurs |
| **Unités de temps sous le journalier** | **rejetées** | **BTC 4 h : −0,072 R sur 423 trades** |

### Pourquoi le short échoue alors que le signal existe

L'étude d'événements montre un vrai edge directionnel à la vente : sur le S&P 500,
un rebond suracheté dans une tendance baissière est suivi d'un rendement à 10 jours
avec **42,8 % de réussite contre 58,0 % en référence** — 15 points d'écart, t = −3,21.

Le signal est réel. Il n'est simplement **pas récupérable avec un stop** : dans une
tendance baissière la volatilité explose, les rebonds sont violents, et le stop est
touché avant que la baisse ne reprenne. Taux de réussite effectif : 28 %.

C'est une leçon générale : *un edge statistique n'est pas un edge exploitable*. La
gestion fait partie de l'edge, pas de l'habillage.

## 7. Contrôles anti-illusion

| Contrôle | Résultat |
|---|---|
| Marche aléatoire de même volatilité (20 tirages) | espérance médiane −0,150 R, **0/20 positifs** |
| Rendements mélangés (20 tirages) | espérance médiane −0,173 R, **1/20 positifs** |
| Signal retardé 1 / 2 / 5 / 10 barres | 0,324 / 0,234 / 0,209 / 0,211 R — dégradation progressive |
| Sharpe déflaté, S&P 500 repli | P(Sharpe réel > 0) = **95,8 %** |
| Sharpe déflaté, BTC impulsion | P(Sharpe réel > 0) > **99,9 %** |

## 8. Les limites, sans enrobage

1. **Le S&P 500 s'arrête en 2018** dans les données accessibles. Le krach Covid de
   2020 et le marché baissier de 2022 ne sont pas dans le test actions. C'est le
   trou le plus gênant de l'étude.
2. **BTC ne compte que 134 trades** sur 14 ans en profil impulsion. C'est peu. Le
   t = 5,20 est rassurant, la vérification hors échantillon aussi, mais 134 reste
   134.
3. **Un seul actif crypto avec un vrai OHLC.** ETH et SOL n'ont que des clôtures :
   leur confirmation est indicative, pas probante.
4. **L'edge crypto se referme** (section 4). Rien ne garantit qu'il soit encore là
   dans trois ans.
5. **Le régime 1970 se reproduira.** Une stratégie qui achète les replis perd de
   l'argent dans un marché qui baisse lentement sans rebondir.
6. **Les 500 actions ne couvrent que 2013-2018**, c'est-à-dire un marché haussier
   ininterrompu. L'espérance de +0,103 R y est sans doute optimiste.
7. **Frais supposés : 20 bps aller-retour en actions, 40 bps en crypto.** Si votre
   courtier prend plus, retirez-le de l'espérance. En crypto, 40 bps
   représentent déjà environ 15 % de l'espérance par trade.
8. **Aucun de ces chiffres n'inclut la fiscalité**, ni le fait que vous n'exécuterez
   pas parfaitement.
