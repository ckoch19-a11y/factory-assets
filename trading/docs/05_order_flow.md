# Confirmer un signal VRC 2 : order flow, macro, et le reste

## La question à laquelle l'order flow doit répondre

L'indicateur achète la **force** : il entre quand le prix s'écarte de plus de
2 ATR au-dessus de sa moyenne rapide, dans une tendance haussière.

Son mode d'échec est toujours le même : **acheter une hausse qui n'est pas
portée par de l'argent neuf.** Un squeeze de vendeurs à découvert produit
exactement le même graphique qu'une vraie impulsion — et se retourne dès que
les liquidations sont terminées.

Ton analyse d'order flow ne sert donc pas à choisir le sens. Le sens est déjà
donné, le stop est déjà placé. Elle sert à répondre à **une seule question** :

> Cette hausse est-elle alimentée par de l'achat volontaire, ou par de l'achat
> forcé ?

Achat volontaire = on garde le signal. Achat forcé = on réduit ou on passe.

---

## 1. Les quatre indicateurs qui répondent vraiment

Classés par utilité réelle, pas par popularité.

### Open interest contre prix — le plus utile

| Ce que tu vois | Ce que ça veut dire | Décision |
|---|---|---|
| Prix ↑ **et** OI ↑ | De nouvelles positions s'ouvrent : argent neuf | **Confirme** |
| Prix ↑ **et** OI ↓ | Des positions se ferment : ce sont des vendeurs à découvert qui rachètent | **Contredit** |
| Prix ↑ et OI plat | Rotation, pas d'engagement nouveau | Neutre, taille réduite |

Une impulsion avec l'open interest en baisse est presque toujours un squeeze.
C'est le signal d'alarme le plus fiable et le plus simple à lire.

*Où regarder* : Coinglass, ou l'onglet Open Interest de TradingView
(`BTCUSDT.P` chez la plupart des fournisseurs).

### Funding rate — le filtre de foule

Le funding mesure ce que les longs paient aux shorts. Il dit qui est déjà
positionné.

| Funding (par 8 h) | Lecture | Décision |
|---|---|---|
| −0,01 % à +0,02 % | Neutre. Le marché n'est pas encombré | **Confirme** |
| +0,03 % à +0,05 % | Longs majoritaires, ça chauffe | Taille réduite de moitié |
| > +0,05 % | Tout le monde est déjà long. Tu arrives dernier | **Passe** |
| Négatif marqué avec prix ↑ | Les shorts paient pour rester short contre une hausse : carburant | **Confirme fortement** |

Le dernier cas est le meilleur contexte possible pour ce système : la hausse a
du carburant sous forme de positions short qui devront capituler.

### Delta au comptant contre delta perpétuel

Le delta cumulé (CVD) mesure la pression acheteuse agressive.

- **Comptant qui monte avec le prix** : de vrais acheteurs prennent livraison.
  C'est le meilleur signal de continuation.
- **Perpétuel qui monte, comptant plat ou négatif** : la hausse n'existe que
  sur les dérivés. Elle tient tant que le levier tient, pas plus.
- **Prix qui monte avec un delta comptant négatif** : distribution. Quelqu'un
  vend dans la hausse. C'est le pire cas.

*Où regarder* : Coinalyze, Velo, ou les indicateurs CVD de TradingView en
comparant `BINANCE:BTCUSDT` (comptant) et `BINANCE:BTCUSDT.P` (perpétuel).

### Zones de liquidation

Une impulsion qui se dirige vers un gros amas de liquidations de shorts va
souvent le chercher, le déclencher, puis retomber. Si ton niveau de
déclenchement projeté est **juste sous** un amas important, attends-toi à un
dépassement puis un retour : c'est exactement le contexte où un stop à 1,5 ATR
se fait toucher avant que le mouvement reparte.

Dans ce cas : soit tu passes, soit tu entres après le balayage, pas avant.

---

## 2. Comment t'en servir concrètement

L'indicateur te donne le **niveau de déclenchement projeté** avant que le
signal existe. C'est là qu'est tout l'intérêt : tu as le temps de préparer.

```
1. Le tableau de bord affiche « Déclenchement à 68 420, distance 1,8 % »
   → tu sais où et à peu près quand. Tu prépares.

2. Tu ouvres open interest + funding sur cet actif.
   → OI en hausse, funding à +0,01 % : contexte sain, tu es prêt.
   → OI en baisse, funding à +0,06 % : tu sais déjà que tu passeras.

3. Le prix atteint le niveau, la bougie journalière clôture au-dessus.
   → signal confirmé. Tu regardes le delta comptant de la journée.

4. Tu entres à l'ouverture de la bougie suivante, ou tu passes.
   Le stop est déjà calculé, la taille aussi.
```

**Le point important** : tu ne cherches pas une confirmation qui te fasse
entrer. Tu cherches une raison de **ne pas** entrer. Par défaut, le signal se
prend. L'order flow sert de veto, pas de déclencheur.

C'est une nuance décisive. Un trader qui cherche une confirmation finira
toujours par en trouver une.

---

## 3. La macro : ce qui mérite qu'on regarde

Beaucoup moins de choses qu'on ne le croit. Ce qui a un effet mesurable sur le
crypto à l'horizon de ce système (une à quatre semaines) :

| À surveiller | Pourquoi | Action |
|---|---|---|
| **FOMC, CPI américain** dans les 48 h | Gap de volatilité que ton stop n'anticipe pas | Taille divisée par deux, ou attendre |
| **Croissance de l'offre de stablecoins** | C'est le carburant du crypto. En contraction, les impulsions échouent plus souvent | Contexte général, pas un veto |
| **Flux des ETF spot** | Achat structurel indépendant du levier | Flux positifs soutenus = contexte favorable |
| **Dominance BTC** | En forte hausse, les altcoins sous-performent même en tendance | Privilégier BTC si la dominance monte |

Ce qui n'a **pas** d'effet mesurable et te fera perdre du temps : les
annonces de partenariats, les prévisions d'analystes, l'actualité
réglementaire quotidienne, et à peu près tout ce qui passe sur les réseaux.

---

## 4. Le piège de la corrélation

Les dix actifs ont une corrélation moyenne de **0,22** sur leurs résultats
mensuels. C'est faible, et c'est une bonne nouvelle : répartir sur plusieurs
actifs réduit vraiment le risque.

Mais cette corrélation moyenne cache le cas qui compte : **quand le marché
crypto part en tendance, tous les signaux arrivent en même temps.** Cinq
signaux le même jour sur cinq actifs, ce n'est pas cinq paris. C'est un seul
pari en cinq morceaux.

Règle : **maximum 5 positions simultanées, et pas plus de 2 ouvertes le même
jour.** La simulation de portefeuille de l'étude tourne sur ces contraintes :
c'est avec elles que les chiffres annoncés tiennent.

---

## 5. Ce que tu dois mesurer sur toi-même

C'est la partie que personne ne fait, et c'est celle qui rapporte le plus.

Note pour chaque signal, **même ceux que tu ne prends pas** :

| Champ | Pourquoi |
|---|---|
| Date, actif, prix de déclenchement | base |
| Open interest : hausse / baisse / plat | le facteur le plus discriminant |
| Funding au moment du signal | filtre de foule |
| Delta comptant : positif / négatif | qualité de l'achat |
| **Pris / passé, et pourquoi** | le champ central |
| Résultat en R | la mesure |

Après **50 signaux**, compare trois populations :

1. tous les signaux, sans filtre → c'est la référence, tu la connais : +0,69 R
2. ceux que ton order flow a confirmés
3. ceux que ton order flow a rejetés

**Trois résultats possibles, trois conclusions :**

- Les confirmés font mieux et les rejetés font moins bien → ton filtre
  fonctionne. Applique-le systématiquement, et tu as un edge personnel
  au-dessus du système.
- Les trois populations se ressemblent → ton analyse ne sert à rien à cette
  échelle de temps. Arrête d'y passer du temps et prends tous les signaux.
- Les rejetés font **mieux** que les confirmés → ton filtre est nuisible. Ça
  arrive plus souvent qu'on ne l'imagine : on rejette les signaux qui font
  peur, et ce sont souvent les meilleurs.

Le troisième cas est le plus fréquent chez les débutants. Ne le prends pas
personnellement : mesure-le, et corrige.

---

## 6. Ce qui ne servira à rien

Autant le dire tout de suite, pour t'éviter des mois :

- **Les indicateurs empilés.** Ajouter RSI, MACD, stochastique et Ichimoku
  au-dessus de VRC ne crée pas d'information : ce sont tous des
  transformations du même prix. L'étude en a testé une trentaine — presque
  aucun n'apporte quoi que ce soit une fois le régime et la volatilité pris en
  compte.
- **Descendre en unité de temps pour « affiner l'entrée ».** L'espérance
  mesurée sous le journalier est négative. Tu peux regarder le 1 h pour
  l'exécution, mais le signal reste journalier.
- **Les niveaux de Fibonacci, les vagues d'Elliott, les figures
  chartistes.** Aucun de ces outils n'est falsifiable : deux personnes y
  voient deux choses. Ce qui n'est pas falsifiable ne peut pas être mesuré, et
  ce qui ne peut pas être mesuré ne peut pas être amélioré.
- **Les groupes de signaux payants.** Si un signal est vendu, il est déjà dans
  le prix.

La seule chose qui ajoute vraiment de l'information à un signal de prix, c'est
une donnée **qui n'est pas du prix** : positionnement (OI, funding), flux
(delta, ETF, stablecoins), et contexte de liquidité. C'est exactement la liste
de la section 1.
