# Mode d'emploi

## 1. Installation

1. TradingView → **Éditeur Pine** (en bas de l'écran) → **Ouvrir** → *Nouvel
   indicateur*.
2. Coller le contenu de `pine/VRC_indicateur.pine`, remplacer tout.
3. **Enregistrer**, puis **Ajouter au graphique**.
4. Pour rejouer le backtest vous-même : même chose avec `pine/VRC_strategy.pine`,
   qui s'ouvre dans l'onglet *Testeur de stratégie*.

Vérifiez cette version avant toute autre chose : `strategy.commission` à 0,05 %
et `slippage` à 2 ticks. Un backtest TradingView sans frais ment.

## 2. Réglage — la seule chose à ne pas rater

| Vous tradez | Profil | Unité de temps |
|---|---|---|
| Indices, actions, ETF | **Actions / indices — achat du repli** | Journalier |
| BTC, ETH, majors crypto | **Crypto — achat de l'impulsion** | Journalier |

Deux règles non négociables, mesurées et pas supposées :

- **Se tromper de profil ramène l'espérance à zéro.** Profil actions sur BTC :
  +0,297 R contre +0,346 R pour une entrée au hasard — vous faites moins bien que
  le hasard. Profil crypto sur le S&P 500 : +0,038 R, soit rien.
- **Sous le journalier, l'espérance est négative.** BTC en 4 h : −0,072 R sur
  423 trades. Ce n'est pas un réglage à ajuster, c'est une unité de temps à ne pas
  utiliser. L'indicateur vous affiche un avertissement si vous le faites.

Les autres paramètres sont sur un plateau large : ne les touchez pas sans avoir
relancé l'étude. Ils n'ont pas été choisis pour maximiser le backtest, mais pour
se situer au centre d'une zone stable.

## 3. Le flux de travail

L'indicateur ne vous dit pas quoi faire. Il vous dit **où et quand regarder**, et
c'est déjà l'essentiel du travail.

```
    VRC                         Vous
 ───────────                 ──────────
 rond creux    ──────────▶   commencer à surveiller l'order flow
 (approche)                  et vérifier le contexte macro

 triangle      ──────────▶   le setup est armé. Entrée à l'OUVERTURE
 (signal)                    de la bougie suivante, pas avant

                ──────────▶  order flow + macro : vous confirmez,
                             vous réduisez, ou vous passez

 stop/objectif ──────────▶   niveaux fixes. Ils ne se négocient pas
```

**Point important** : le signal se valide à la **clôture** de la bougie journalière,
et l'entrée se fait à l'**ouverture de la suivante**. Tout le backtest repose
là-dessus. Entrer en cours de bougie parce que « le signal est en train de se
former » n'est pas la même stratégie, et ses résultats ne sont pas ceux-ci.

## 4. Ce que votre order flow doit confirmer

Vous arrivez avec une **direction** et un **niveau d'invalidation** déjà fixés. Votre
analyse d'order flow ne sert pas à choisir le sens : elle sert à répondre à une
seule question — *est-ce que le flux contredit le setup ?*

### Profil actions (achat du repli)

Le pari : la baisse est de la liquidation mécanique, pas de la vente informée.

| Confirme | Contredit |
|---|---|
| Delta négatif mais prix qui ne descend plus (absorption) | Delta négatif **et** prix qui cède à chaque vague |
| Volume en baisse sur la fin du repli | Volume en accélération à la baisse |
| Gros acheteurs passifs visibles sur le carnet aux niveaux | Carnet vide en dessous |
| Reprise depuis la zone de valeur de la veille | Cassure franche sous la zone de valeur |

### Profil crypto (achat de l'impulsion)

Le pari : la hausse est alimentée par du flux réel, pas seulement par des
liquidations de shorts.

| Confirme | Contredit |
|---|---|
| Delta cumulé positif et croissant | Prix qui monte avec un delta plat — squeeze |
| Open interest en hausse avec le prix | Open interest qui s'effondre — on ferme des shorts |
| Funding neutre ou légèrement positif | Funding extrême — tout le monde est déjà long |
| Volume au comptant qui suit les perpétuels | Hausse uniquement sur les perpétuels |

**Le funding extrême est le filtre le plus utile en crypto.** Une impulsion avec un
funding déjà très positif, c'est une entrée dans un trade que tout le monde a déjà.

## 5. Ce que la macro doit filtrer

La macro ne crée pas de signal ici. Elle sert à **réduire ou annuler** :

- **Événement à risque binaire dans les 48 h** (FOMC, CPI, NFP, décision de taux) :
  ne pas prendre le signal, ou diviser la taille par deux. Votre stop est calibré
  sur la volatilité normale, pas sur un gap d'annonce.
- **Régime de liquidité qui se contracte** (hausses de taux, resserrement) : les
  replis se transforment plus souvent en tendance baissière. C'est exactement le
  régime des années 1970 où la stratégie perd de l'argent.
- **Crypto** : les phases de désendettement généralisé cassent la logique
  d'impulsion. Un signal d'impulsion pendant une cascade de liquidations est un
  piège.
- **Corrélation** : si vos cinq signaux du jour sont cinq technos américaines, vous
  n'avez pas cinq positions, vous en avez une en cinq morceaux.

## 6. Gestion du risque

C'est cette partie qui décide de votre résultat, pas le signal.

| Règle | Valeur | Pourquoi |
|---|---|---|
| Risque par trade | **1 % du capital** | Le backtest entier suppose cela |
| Positions simultanées | **5 maximum** | Au-delà, les corrélations s'additionnent |
| Risque total ouvert | **5 %** | Perte maximale si tout part en même temps |
| Perte mensuelle → pause | **−8 %** | Au-delà, arrêtez et relisez votre journal |

**Calcul de la taille** — l'indicateur l'affiche, mais sachez le refaire :

```
taille = (capital × 1 %) ÷ (prix d'entrée − prix du stop)
```

Capital 5 000 €, entrée 100 €, stop 94 € : (5 000 × 0,01) ÷ 6 = **8,3 unités**.

Ce qui compte n'est pas le nombre d'unités, c'est que **toutes vos positions
risquent le même montant**. Un trade à 1 % et un autre à 4 %, c'est le second qui
décide de votre année.

## 7. Avoir assez de signaux

~7 signaux par an et par instrument. Sur un seul actif, vous ne tradez presque
jamais — et vous finirez par forcer des entrées qui ne sont pas dans le système.
C'est le mode d'échec le plus courant.

Construisez une liste de surveillance de **15 à 25 instruments** :

- 3-4 indices (S&P 500, Nasdaq, DAX, CAC 40)
- 10-12 grandes capitalisations liquides, secteurs variés
- 2-3 cryptos majeures en profil impulsion
- éventuellement or et pétrole

Cela donne 100 à 175 signaux par an, soit 2 à 3 par semaine. Assez pour travailler,
assez peu pour analyser chaque setup sérieusement.

Configurez les alertes TradingView sur la condition *VRC achat* pour chaque
instrument : vous ne surveillez rien, vous êtes prévenu.

## 8. Le journal

Sans journal, vous ne saurez jamais si vos confirmations order flow ajoutent de la
valeur ou en détruisent. À noter pour chaque trade :

| Champ | Pourquoi |
|---|---|
| Date, instrument, profil | base |
| Écart en ATR au signal | vérifier que vous prenez bien les setups |
| **Order flow : confirmé / neutre / contredit** | **le champ le plus important** |
| Contexte macro | identifier les régimes où vous perdez |
| Entrée, stop, sortie, R obtenu | la mesure |
| Respect du système : oui / non | séparer vos erreurs de celles du système |

Après 50 trades, comparez l'espérance des trades « order flow confirmé » à celle
des « neutre ». Si les deux sont identiques, votre analyse d'order flow ne sert à
rien sur cette échelle de temps et vous perdez du temps. Si les « confirmés » font
mieux, vous avez trouvé votre vrai edge — et il faut alors ne prendre que ceux-là.

**C'est exactement la même méthode que celle de cette étude, appliquée à vous.**

## 9. Les erreurs qui coûtent cher

1. **Changer les paramètres après une série de pertes.** Mesuré sur le S&P 500 :
   **7 pertes d'affilée** au pire, et un creux cumulé de **−7,0 R** (soit −7 % à
   1 % de risque par trade). Sur BTC : 5 pertes d'affilée, creux de −4,3 R. Ces
   séquences sont normales avec un taux de réussite proche de 48 %. Le système
   n'est pas cassé, c'est la distribution qui fait son travail.
2. **Entrer avant la clôture.** Ce n'est plus la stratégie mesurée ici.
3. **Déplacer le stop.** Toute l'espérance repose sur une perte moyenne de −0,64 R.
   Un seul stop élargi à −3 R efface quatre gains.
4. **Descendre en unité de temps pour avoir plus de signaux.** Espérance mesurée :
   négative.
5. **Activer le short en actions.** 0 configuration rentable sur 36.
6. **Augmenter le risque après des gains.** Le drawdown arrive toujours après la
   bonne série, jamais avant.

## 10. Avant de mettre de l'argent

Trois étapes, dans l'ordre :

1. **Rejouez le backtest vous-même** avec `VRC_strategy.pine` sur vos instruments.
   Ne me croyez pas sur parole : les chiffres doivent sortir de votre écran.
2. **Papier pendant 30 à 50 trades.** Objectif : vérifier que vous exécutez le
   système, pas qu'il est rentable — ça, c'est déjà mesuré.
3. **Commencez à un quart de la taille** pendant 20 trades de plus.

Deux faits à connaître, sans dramatisation : la majorité des particuliers qui
tradent activement perdent de l'argent, et un système avec une espérance positive
mais mal exécuté perd aussi. Ce qui sépare les deux, c'est la gestion du risque et
le journal — pas l'indicateur. L'indicateur est la partie facile, et c'est la seule
que j'ai pu faire à votre place.
