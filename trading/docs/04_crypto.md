# Crypto : quel actif, quel réglage, et ce que valent vraiment les chiffres

Base de mesure : **10 actifs crypto, 29 107 barres journalières, OHLCV
reconstruit depuis la minute Binance**, chacun sur tout son historique depuis
sa cotation. Plus BTC depuis 2012 via Bitstamp.

| Actif | Historique | Barres |
|---|---|---:|
| BTC, ETH | 2017-08 → 2026-09 | 3 318 |
| BNB | 2017-11 → 2026-09 | 3 237 |
| ADA, XRP, TRX | 2018 → 2026-09 | 3 020-3 075 |
| ZEC, DOGE | 2019 → 2026-09 | 2 631-2 737 |
| BCH | 2019-11 → 2026-09 | 2 485 |
| SOL | 2020-08 → 2026-09 | 2 228 |

Zéro anomalie OHLC, zéro trou de calendrier.

---

## 1. La réponse : BTC

Classement par **apport du signal** — l'espérance moins celle d'une entrée
**aléatoire** dans le même régime avec la même gestion. C'est la seule colonne
qui mesure la règle plutôt que l'exposition.

| Actif | Trades | Réussite | Espérance | Apport signal | Bat le hasard | 1ʳᵉ moitié | 2ᵉ moitié | p |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SOL | 25 | 44,0 % | +1,709 R | +1,178 R | 40/40 | +3,735 | **−0,160** | 0,053 |
| **BTC** | **38** | **44,7 %** | **+1,276 R** | **+0,845 R** | **40/40** | **+1,492** | **+1,060** | **0,0000** |
| BNB | 42 | 38,1 % | +1,209 R | +0,624 R | 40/40 | +1,935 | +0,482 | 0,101 |
| XRP | 36 | 30,6 % | +0,792 R | +0,448 R | 40/40 | +0,897 | +0,688 | 0,072 |
| ADA | 37 | 43,2 % | +0,740 R | +0,404 R | 40/40 | +0,389 | +1,072 | 0,123 |
| DOGE | 35 | 31,4 % | +1,334 R | +0,178 R | 31/40 | +2,592 | +0,147 | 0,119 |
| ETH | 39 | 46,2 % | +0,534 R | +0,177 R | 38/40 | +0,346 | +0,712 | 0,0003 |
| BCH | 30 | 23,3 % | −0,008 R | +0,007 R | 21/40 | −0,318 | +0,301 | 0,169 |
| TRX | 55 | 38,2 % | +0,086 R | −0,187 R | 5/40 | −0,355 | +0,512 | 0,411 |
| ZEC | 44 | 25,0 % | −0,135 R | −0,241 R | 1/40 | −0,486 | +0,217 | 0,415 |

**Pourquoi BTC et pas SOL**, qui affiche pourtant un apport supérieur :

- SOL passe de **+3,735 R** sur sa première moitié à **−0,160 R** sur la
  seconde. L'edge y a disparu. 25 trades seulement.
- BTC est le seul actif dont les **deux moitiés** sont fortement positives
  (+1,492 puis +1,060). C'est la définition même de la stabilité.
- BTC a le meilleur t (2,35) et la meilleure p-value (0,0000).
- Hors statistiques : c'est l'actif le plus liquide, donc les frais réels et
  le slippage y sont les plus faibles, et c'est celui pour lequel les données
  d'order flow (open interest, funding, delta comptant) sont les plus
  complètes et les plus fiables. Pour ta méthode, ça compte autant que le t.

**Répartition recommandée** : BTC en cœur, ETH et ADA en complément — ce sont
les deux autres dont la seconde moitié est meilleure que la première.
**À éviter : ZEC et TRX**, qui font moins bien que le hasard.

Une remarque honnête : ce classement dépend du réglage. Avec le réglage
précédent (seuil 1,5 / stop 2 / suiveur 2), c'était ETH qui sortait premier.
Ne prends donc pas ce tableau pour une vérité absolue sur les actifs — c'est
le résultat d'une règle donnée sur une période donnée.

---

## 2. Le réglage retenu, et pourquoi pas le plus rentable

Quatre réglages ont été simulés sur l'échantillon groupé, portefeuille de
5 positions maximum, 1 % de risque par trade.

| | Seuil | Stop | Suiveur | Trades | Réussite | Espérance | CAGR | Creux | MAR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A précédent | 1,5 | 2,0 | 2,0 | 633 | 40,9 % | +0,250 R | 17,3 % | −13,3 % | 1,30 |
| **B retenu** | **2,0** | **1,5** | **3,0** | **381** | **36,5 %** | **+0,693 R** | **27,0 %** | **−20,3 %** | **1,33** |
| C | 2,0 | 1,0 | 6,0 | 358 | 21,2 % | +1,560 R | 58,8 % | −20,3 % | 2,89 |
| D | 1,5 | 1,0 | aucun | 439 | 21,0 % | +1,918 R | 84,5 % | −26,3 % | 3,21 |

C et D rapportent deux à trois fois plus. Je ne les retiens pas, et voici
exactement pourquoi :

| | Années positives | Pire année | Trimestre médian | Risque d'une série de 15+ pertes |
|---|---|---:|---:|---:|
| A | 7/9 | −8,0 R | +0,1 R | 6 % |
| **B** | **8/9** | **−0,6 R** | **+2,8 R** | **10 %** |
| C | 6/9 | −17,2 R | **−1,1 R** | **81 %** |
| D | 6/9 | −21,6 R | **−3,2 R** | **88 %** |

**C et D ont un trimestre médian négatif.** Autrement dit : plus d'un
trimestre sur deux, tu perds de l'argent, et tout le résultat vient de rares
trimestres explosifs. Avec 88 % de chances de traverser une série de plus de
15 pertes consécutives, personne ne tient. Tu abandonnerais le système au
pire moment — juste avant le trimestre qui paie.

B est positif 8 années sur 9, sa pire année coûte 0,6 R, et son trimestre
médian rapporte 2,8 R. C'est un système qu'on peut **tenir**, et un système
qu'on ne tient pas ne rapporte rien, quels que soient ses chiffres.

### Année par année, réglage B

| Année | Espérance |
|---|---:|
| 2018 | −0,282 R |
| 2019 | +0,418 R |
| 2020 | +0,470 R |
| 2021 | +1,370 R |
| 2022 | +0,104 R |
| 2023 | +0,819 R |
| 2024 | +0,635 R |
| 2025 | +0,216 R |
| 2026 | +0,361 R |

2018 et 2022 sont les deux marchés baissiers crypto. B y reste à l'équilibre
là où C et D perdent lourdement. C'est ce qui fait la différence.

---

## 3. Les simulations

### Monte-Carlo, 5 000 tirages avec remise (réglage B)

| Mesure | Valeur |
|---|---:|
| Probabilité de finir en perte | **0 %** |
| Capital médian (1 % de risque) | ×10,2 |
| 5ᵉ centile | ×3,5 |
| 95ᵉ centile | ×36,0 |
| Creux médian | −15,5 % |
| Creux au 95ᵉ centile | −24,8 % |
| Pire creux observé sur 5 000 tirages | −41,4 % |

Un second Monte-Carlo permute l'**ordre** des trades sans les changer : le
résultat final est identique par construction, seul le chemin varie. Creux
médian −15,4 %, 95ᵉ centile −23,1 %. Conclusion : le creux de −20 % du
backtest n'est pas un accident de séquence, c'est la propriété du système.

### Sensibilité aux frais

| Frais aller-retour | Espérance B |
|---|---:|
| 0 bps | +0,748 R |
| 20 bps | +0,721 R |
| 40 bps (hypothèse retenue) | **+0,693 R** |
| 80 bps | +0,637 R |
| 160 bps | +0,525 R |

Même avec des frais quatre fois supérieurs à l'hypothèse, l'edge tient. Ce
n'est pas une stratégie qui vit de la finesse d'exécution.

### Risque de ruine selon la taille de position

| Risque par trade | Creux médian | Probabilité de perdre la moitié |
|---|---:|---:|
| 0,5 % | −8,0 % | 0 % |
| **1 %** | **−15,5 %** | **0 %** |
| 2 % | −29,0 % | 0 % |
| 5 % | −59,6 % | 7,6 % |
| 10 % | −86,5 % | 34,1 % |

### Stabilité des paramètres

216 configurations testées en apprentissage (avant 2023) puis vérification
(2023-2026) : **216 sur 216 positives des deux côtés.** L'edge ne dépend pas
d'un réglage précis, ce qui est le signe le plus fiable qu'il n'est pas le
fruit d'un sur-ajustement.

### Échantillon groupé

633 trades sur 10 actifs, réglage A : espérance +0,250 R, t = 4,40, facteur de
profit 1,69. **8 actifs sur 10 positifs** — sous l'hypothèse « aucun edge », la
probabilité d'en observer autant est de 5,5 %. Corrélation moyenne des
résultats mensuels entre actifs : **0,22**.

---

## 4. Pourquoi il n'y a pas de take profit fixe

Tu voulais un TP placé automatiquement. Voici la mesure, même échantillon,
même entrée, seule la sortie change :

| Gestion de sortie | Trades | Réussite | Espérance | R par an |
|---|---:|---:|---:|---:|
| **Suiveur 3 ATR seul (retenu)** | 381 | 36,5 % | **+0,693 R** | **29,0** |
| Suiveur + objectif 6R | 427 | 35,8 % | +0,447 R | 21,0 |
| Suiveur + objectif 4R | 471 | 34,8 % | +0,351 R | 18,2 |
| Suiveur + objectif 3R | 511 | 36,2 % | +0,297 R | 16,7 |
| Suiveur + objectif 2R | 586 | 38,7 % | +0,156 R | 10,1 |
| Objectif 2R seul | 578 | 41,0 % | +0,171 R | 10,9 |

**Un objectif à 2R divise l'espérance par 4,4.** Plus l'objectif est proche,
plus le résultat s'effondre — et le taux de réussite augmente, ce qui rend le
piège confortable.

La raison est structurelle : l'edge de ce système vit dans les **rares très
gros gagnants**. Le gain moyen est de 3,5 R, mais la médiane des gagnants est
bien plus basse. Couper à 2R, c'est supprimer précisément ce qui paie.

Ce que fait l'indicateur à la place : il trace en continu le **stop suiveur**,
qui est la vraie sortie, et affiche les paliers 1R / 2R / 3R comme repères
visuels. Aucun ordre n'est placé sur ces paliers.

Si tu veux malgré tout sécuriser, la moins mauvaise option mesurée est un
objectif à 6R sur une partie de la position — tu perds environ un tiers de
l'espérance au lieu des trois quarts.

---

## 5. Voir l'entrée à l'avance

L'indicateur trace le **niveau de déclenchement projeté** : le prix qui
déclencherait le signal, calculé comme `EMA20 + 2 × ATR14`, affiché même quand
rien ne se passe.

Précision mesurée sur les 10 actifs, en comparant le niveau calculé en *t* au
niveau réellement nécessaire en *t+1* :

| Mesure | Valeur |
|---|---:|
| Écart médian | 0,65 % du prix |
| Écart moyen | 0,99 % |
| 90ᵉ centile | 2,17 % |
| ATR médian, pour comparaison | 6,24 % du prix |

L'erreur médiane vaut **un dixième d'ATR**. C'est une zone, pas un tick — et
c'est amplement suffisant pour préparer ton analyse d'order flow avant que le
signal existe. Le tableau de bord affiche aussi le stop projeté et la taille de
position à placer, de sorte que tout le plan de trade est prêt avant le
déclenchement.

---

## 6. Ton objectif de 1 % par jour

Il faut le regarder en face, parce qu'il détermine tout le reste.

**Ce que 1 % par jour représente :**

| Horizon | Multiplicateur |
|---|---:|
| 1 an (365 j) | **×37,8**, soit +3 678 % |
| 1 an (252 j ouvrés) | ×12,3 |
| 5 ans | **×83 millions** |

Avec 1 000 € de départ, 1 %/jour pendant 5 ans donnerait 83 milliards d'euros.
Ce n'est pas une question de discipline ou de méthode : c'est arithmétiquement
impossible, et le marché n'est pas assez grand.

**Points de comparaison, sur toute leur histoire :**

| | Rendement annuel |
|---|---:|
| Renaissance Medallion, le meilleur fonds jamais mesuré | ~39 % |
| Berkshire Hathaway, 1965-2024 | ~19 % |
| Réglage B mesuré ici, à 1 % de risque | 27 % |
| Réglage D, le plus agressif testé | 84 % |
| **Objectif 1 %/jour** | **3 678 %** |

**Ce qu'il faudrait risquer pour y arriver :**

| Réglage | Espérance | Trades/an | Risque par trade requis |
|---|---:|---:|---:|
| A | +0,25 R | 70 | **21,3 %** |
| B | +0,69 R | 42 | **12,2 %** |
| C | +1,56 R | 40 | **5,7 %** |
| D | +1,92 R | 49 | **3,9 %** |

Or à 10 % de risque par trade, le creux médian simulé est déjà de **−86,5 %**
avec 34 % de chances de perdre la moitié du capital. À 12 %, la ruine n'est
pas un risque, c'est le résultat le plus probable.

**La conclusion n'est pas « vise moins haut pour te rassurer ».** C'est que
l'objectif exprimé en pourcentage par jour est le mauvais objectif. Il pousse
mécaniquement à augmenter la taille jusqu'à la ruine, parce que c'est le seul
levier qui reste quand l'espérance est ce qu'elle est.

**L'objectif qui marche** : maximiser l'espérance en R et le nombre de signaux
de qualité, garder le risque à 1 % et laisser la composition faire son
travail. 27 % par an pendant 10 ans, ça fait ×10,9. C'est déjà un résultat
que très peu de gens obtiennent.

À 17 ans, l'actif qui compte le plus dans ton capital, ce n'est pas l'argent :
c'est le temps de composition devant toi. Le ruiner à 20 ans pour tenter
1 %/jour est le seul moyen certain de perdre les deux.

---

## 7. Limites

1. **38 trades sur BTC** en 9 ans avec le réglage retenu. C'est peu. Le t de
   2,35 et la p-value de 0,0000 sont rassurants, mais 38 reste 38. L'échantillon
   groupé (381 trades) est la vraie base statistique.
2. **Un seul régime de fond.** 2017-2026 couvre deux marchés baissiers, mais
   le crypto n'a jamais connu de décennie perdue comme les actions dans les
   années 1970. Rien ne dit que cette stratégie y survivrait.
3. **L'edge crypto se referme.** Sur BTC depuis 2012, l'espérance passe de
   1,07 R sur la première moitié à 0,40 R sur la seconde. Elle reste positive,
   mais la tendance est claire.
4. **Le classement des actifs dépend du réglage.** Avec d'autres paramètres,
   l'ordre change. Ne fige pas ce tableau.
5. **Données Binance à partir de 2017.** Les premières années de chaque actif,
   souvent les plus favorables, manquent pour tous sauf BTC.
6. **Aucun chiffre ici n'inclut la fiscalité**, ni le fait que tu n'exécuteras
   pas parfaitement.
