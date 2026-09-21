# Audit Claude Code — usine KORVEX

Date : 2026-09-21
Dépôt audité : `ckoch19-a11y/factory-assets` (branche `claude/lucid-galileo-jtay6d`)
Statut : **à lire avant tout développement.** Aucune ligne de code produite.

---

## 0. Avertissement de périmètre — à lire en premier

L'étape 1 demandait de lire `CLAUDE.md`, `DEPOTS.md`, `.github/` et `tools/`.
**Aucun de ces fichiers n'existe dans le dépôt auquel cette session a accès.**

`factory-assets` contient 9 fichiers versionnés, et rien d'autre :

```
README.md
assurance/hero_gan_place.mp4      assurance/poster_gan_place.jpg
assurance/hero_vignoble.mp4       assurance/poster_vignoble.jpg
demenagement/hero_equipe.mp4      demenagement/poster_equipe.jpg
demenagement/hero_famille.mp4     demenagement/poster_famille.jpg
```

Pas de socle, pas de pages de démo, pas de `gates.yml`, pas de moteur de variation,
pas de poseur. Le backlog des 12 missions porte sur un **autre dépôt**.

Le compte expose deux dépôts : `factory-assets` et `ckoch19-a11y/application` (privé).
Le socle est vraisemblablement dans `application`. **Je n'ai pas pu y accéder** :
la session est verrouillée sur `factory-assets`, et la demande de rattachement
a été refusée par la politique de permissions.

Conséquence directe : **la section 2 (les 5 plus gros risques techniques avec
fichier et ligne) ne peut pas être produite comme demandée.** Citer des fichiers
et des numéros de ligne d'un code que je n'ai pas lu serait de l'invention.
Je livre à la place :

- la section 2 **appliquée au dépôt réellement accessible**, avec des mesures
  vérifiables (section 2.A) — et ce n'est pas du remplissage : ces défauts font
  échouer la mission 4 avant même qu'elle commence ;
- la **méthode exacte** que j'appliquerai au socle dès que j'y aurai accès (2.B).

**Ce qu'il te faut faire :** autoriser cette session sur `ckoch19-a11y/application`
(ou me dire où est le socle). Voir section 4.

---

## 1. Ce que cette session peut faire, qu'une session de chat ne peut pas

La différence n'est pas « je code mieux ». Elle est : **je peux vérifier mes
propres affirmations avant de te les livrer.** En chat, je produis du code
plausible et c'est toi qui découvres qu'il est faux. Ici, la boucle se ferme
avant toi.

| Capacité | Ce que ça change concrètement pour l'usine |
|---|---|
| **Exécution locale** | Je lance le code. Une page qui ne compile pas ne t'arrive jamais. J'ai mesuré les bitrates vidéo de ce dépôt en lisant les en-têtes MP4 — pas en les devinant. |
| **Navigateur piloté (Playwright + Chromium préinstallé)** | Je rends réellement une page dans un vrai moteur, je lis la console, je prends des captures 390/768/1440. C'est ce qui rend les missions 1, 2, 4 et 11 possibles. En chat, « l'écran blanc » est un récit ; ici c'est un test rouge. |
| **Intégration continue** | Un défaut détecté une fois devient un test permanent. Un écran blanc ne peut coûter cher **qu'une seule fois**. C'est le seul mécanisme qui transforme une leçon en garantie. |
| **Refactorisation multi-fichiers** | Je modifie 61 fichiers de manière cohérente et je vérifie l'ensemble après. Le point central de la mission 5. |
| **Hooks (pré-commit)** | Interdiction mécanique de commiter du code cassé, sans dépendre de ma discipline ni de la tienne. |
| **Sous-agents parallèles** | Les 8 directions artistiques de la mission 3 peuvent être explorées en parallèle, chacune dans son contexte, sans que l'une contamine l'autre. En chat, la direction n°5 ressemble toujours à la n°4 — c'est un effet de contexte partagé, pas un manque d'idées. |
| **Tâches planifiées** | La tournée hebdomadaire de la mission 12 tourne sans toi. |
| **Pull requests uniquement** | Tout passe par une PR relue. Rien ne part en production par accident. |

**Ce que je ne peux pas faire, et qu'il faut savoir :** je ne juge pas si un design
est beau. Je mesure qu'il est *différent* et qu'il *fonctionne*. Le critère
« aucune ne ressemble aux autres » de la mission 3 reste ton œil — voir section 3.

---

## 2.A. Risques techniques réels, mesurés, dans le dépôt accessible

Chiffres obtenus en lisant les boîtes `mvhd`/`tkhd`/`stsd` des fichiers MP4 :

```
assurance/hero_gan_place.mp4     1,82 Mo    5,0 s   1920x1080  H.264   3,0 Mb/s
assurance/hero_vignoble.mp4      2,62 Mo   10,0 s   1920x1080  H.264   2,2 Mb/s
demenagement/hero_equipe.mp4     0,95 Mo    7,8 s   1920x1080  H.264   1,0 Mb/s
demenagement/hero_famille.mp4    0,89 Mo   10,0 s   1920x1080  H.264   0,7 Mb/s
posters : 4 × JPEG baseline 1920x1080, de 73 Ko à 275 Ko
```

### Risque 1 — La mission 4 est perdue d'avance sur ces assets
`assurance/hero_gan_place.mp4` : 1,82 Mo, servi à l'identique sur mobile.
Aucune variante 720p/480p, aucun WebM/AV1, aucun `<source media=...>` possible.
Sur une 4G française médiane (~10 Mb/s réels), le transfert seul coûte ~1,5 s,
avant décodage et avant le reste de la page. Le poster `poster_gan_place.jpg`
(211 Ko, JPEG baseline) est **l'élément LCP réel** — c'est lui qu'il faut
optimiser en priorité, et il devrait peser moins de 100 Ko en AVIF.

Tu vas écrire une sonde qui exige LCP < 2,5 s, elle passera au rouge, et tu
n'auras aucun outil pour la faire passer au vert. **Une sonde qu'on ne peut pas
satisfaire est une sonde qu'on apprend à ignorer.**

### Risque 2 — Incohérence de qualité de 4× à définition égale
3,0 Mb/s contre 0,7 Mb/s pour du 1920x1080. Aucune cible commune. Les assets ne
sortent pas du même pipeline : `hero_vignoble.mp4` porte une piste timecode
`tmcd` et un commentaire encodeur `Lavc58.134.100`, résidus d'export absents
des trois autres. Rien n'est normalisé ni nettoyé avant commit.

### Risque 3 — Binaires lourds versionnés dans Git — irréversible
`.git` pèse déjà 7,4 Mo pour 7,1 Mo d'assets. Chaque ré-encodage d'un héros
ajoutera **son poids complet et définitif** à l'historique. À 20 clients × 2 héros
× 3 itérations, le clone devient hostile. Ce n'est pas urgent aujourd'hui ; c'est
incorrigible plus tard sans réécrire l'historique.

> **Correction (21/09) — la première version de cet audit proposait Git LFS.
> C'est faux ici, et l'objection de Calvin est décisive :** sur un dépôt synchronisé
> avec Base44, la synchro enverrait les fichiers *pointeurs* LFS au lieu des médias
> et casserait les visuels des sites en production. **Pas de LFS sur ce dépôt.**
> La bonne réponse est de sortir les binaires de Git : hébergement sur le stockage
> média Base44 ou un CDN, et dans le dépôt uniquement les scripts de génération,
> le manifeste de provenance et les références d'URL.

### Risque 4 — Provenance et droits non traçables (croise la mission 8)
Rien ne relie `hero_vignoble.mp4` à un client, une licence ou un prompt.
Le commit `e92a419` s'intitule *« V1 video IA Qwen »* : au moins un asset est
généré par IA, et cette information vit dans **un message de commit**, pas dans
un fichier de provenance consultable. À la question client « cette vidéo est-elle
libre de droits ? », il n'existe aujourd'hui aucune réponse vérifiable.
La mission 8 sonde les mentions légales des sites ; elle ne couvre pas ça.

### Risque 5 — Aucun garde-fou : n'importe quel fichier peut entrer
Pas de CI, pas de hook, pas de convention de nommage imposée. Un 4K de 40 Mo
peut être commité ce soir sans que rien ne l'arrête, et il sera dans l'historique
pour toujours. C'est exactement la mission 9, mais appliquée à ce dépôt-ci.

---

## 2.B. Méthode pour le socle, dès accès obtenu

Dans cet ordre, sans rien coder avant d'avoir fini :

1. Lire `CLAUDE.md`, `DEPOTS.md`, `.github/workflows/`, `tools/` — les règles avant le code.
2. Rendre chaque page de démo dans Chromium et **enregistrer ce qui casse**.
   Les défauts réels priment sur les défauts théoriques.
3. Chercher les causes connues d'écran blanc : imports de composants inexistants
   (la mission 10 y fait déjà allusion — c'est la cause n°1), `@tailwind` mal posé
   (ton skill `korvex-socle-pose` dit que ça a déjà cassé deux sites), accès à
   `window`/`document` au premier rendu, ErrorBoundary qui avale l'erreur en silence.
4. Lire le moteur de variation en cherchant une seule chose : **les familles dormantes**,
   c'est-à-dire les branches du tirage statistiquement inatteignables. C'est la
   cause mécanique de « ça ressemble au précédent », et la mission 6 la vise juste.
5. Mesurer le poids réel servi par page, en octets, pas en ressenti.
6. Puis seulement : classer les 5 risques, avec fichier et ligne.

---

## 3. Avis sur le backlog

Le backlog est bon : les critères de fini sont mesurables et l'ordre de l'étape 3
est défendable. Mes objections portent sur trois points d'ordre et cinq manques.

### Ordre : mettre la 3 avant la 1

Tu lances 2 → 1 → 3. **Je propose 2 → 3 → 1.**

Raison : la mission 1 fige des captures de référence sur les pages de démo, et la
mission 3 refond ces mêmes pages en 8 directions. Tu produirais des baselines
condamnées d'avance, tu paierais l'outillage deux fois, et surtout tu prendrais
l'habitude d'approuver des diffs visuels en masse. **C'est précisément ce qui tue
un test de non-régression visuelle** — une fois qu'on approuve sans regarder, il
ne protège plus rien. Le test visuel ne vaut que sur une cible stabilisée.

### Ordre : remonter la 5 en position 4

La mission 5 (socle en paquet versionné) est le plus gros retour sur investissement
de la liste et elle est en 5e position. Aujourd'hui, le poseur copie 61 fichiers :
un correctif de sécurité devra être appliqué à la main autant de fois qu'il y a de
sites. **Chaque site livré avant cette mission est une dette permanente.**
Elle ne coûte pas cher en code ; elle coûte cher en décision d'architecture.
Plus tu attends, plus la migration est lourde.

### Ordre : remonter la 9 tout de suite, sans lui faire confiance

Le hook pré-commit, c'est une demi-heure de travail et ça protège toutes les autres
missions. À faire dès maintenant. **Mais ne confonds pas hook et garantie :**
un hook pré-commit ne protège que les machines où il est installé, il se contourne
avec `--no-verify`, et il ne s'applique pas aux modifications faites depuis
l'interface GitHub ou depuis Base44. Hook = confort local. `gates.yml` = vérité.
Si une vérification compte vraiment, elle doit être dans la CI — le hook n'est
qu'un raccourci pour la découvrir plus tôt.

### Durcir le critère de la mission 2

« 0 erreur console, contenu visible » ne détecte pas l'écran blanc le plus fréquent
en React : le rendu qui *réussit* mais ne produit que des conteneurs vides, parce
qu'une ErrorBoundary a avalé l'erreur. Pas d'erreur console, `#root` non vide,
sonde verte, page blanche. Critères à exiger :

- échec sur l'évènement `pageerror` **et** sur tout `requestfailed` d'une ressource same-origin — pas seulement sur `console.error` ;
- au moins un `<h1>` présent et non vide ;
- longueur de texte visible au-dessus d'un seuil (≈ 200 caractères), texte réellement rendu, pas contenu du DOM ;
- au moins une image ou vidéo dont les dimensions naturelles sont non nulles ;
- hauteur de page > hauteur de la fenêtre au 1440.

### Rendre la mission 3 finissable

« Aucune ne ressemble aux autres » n'est pas testable : c'est un jugement, donc
la mission ne sera jamais « finie » au sens de la CI. Il faut un second critère,
mécanique, sinon tu obtiendras huit fois la même mise en page avec huit palettes
— le piège classique de la variation. Propose-toi un vecteur de traits par
direction (famille typographique, échelle typographique, palette en LCH, type de
grille, rayon de bordure, densité, nature du mouvement signature) et exige une
distance minimale entre chaque paire. **La machine garantit la diversité
structurelle ; ton œil garde le dernier mot sur le goût.** Les deux, pas l'un.

### Cinq manques

1. **Normalisation des médias, avant la mission 4.** Voir section 2.A, risque 1.
   Sans variantes mobiles ni posters modernes, la sonde LCP sera rouge en
   permanence. Fais l'outil de normalisation *avant* la sonde qui le réclame.
2. **Sonde d'accessibilité (axe-core).** Même exécution Playwright que la mission 2,
   coût marginal presque nul. Le RGAA ne contraint pas le privé, mais un champ de
   formulaire sans étiquette et un contraste insuffisant te font perdre des
   prospects réels. C'est de l'argent, pas de la conformité.
3. **Test de bout en bout du formulaire de contact.** Le défaut le plus coûteux
   commercialement n'est pas l'écran blanc — il se voit tout de suite. C'est le
   formulaire qui s'affiche parfaitement et n'envoie rien. Personne ne le remarque
   pendant des semaines, et ce sont des demandes clients perdues.
4. **Procédure de faux positif, dès la première sonde.** Ton skill `korvex-tournee`
   parle déjà de « faux positifs connus ». Câble ce mécanisme dans `gates.yml` dès
   le jour 1 : une liste d'exceptions datées et justifiées. Sans ça, en trois
   semaines tu relances la CI par réflexe et les sondes ne veulent plus rien dire.
5. **Budget de poids de page en octets.** LCP et CLS dépendent du réseau de la
   machine de test et varient d'une exécution à l'autre. Les octets transférés,
   non. C'est le seul chiffre non discutable, et le seul qui ne produira pas de
   faux positifs. Ajoute-le à la mission 4.

### Remarque sur la mission 10

« Composants posés mais inexistants » : si c'est avéré, c'est exactement la cause
n°1 d'écran blanc. La mission 2 les détectera donc au passage. La mission 10
devient en grande partie un sous-produit de la 2 — c'est une bonne nouvelle pour
ton planning, à condition de lancer la 2 d'abord. Ce qui est le cas.

---

## 4. Ce dont j'ai besoin pour continuer

**Bloquant :** accès au dépôt du socle, `calvinkoch-ai/usine-vitrine`
(confirmé par Calvin le 21/09 — ce n'est pas `ckoch19-a11y/application`).
Deux obstacles distincts, à lever tous les deux :

1. Le compte GitHub `calvinkoch-ai` n'est pas visible du tout par l'espace de
   travail : l'application GitHub de Claude n'y est pas installée.
2. Cette session est rattachée au propriétaire `ckoch19-a11y` et ne peut pas
   être repointée ailleurs ; il faut **ouvrir une nouvelle session** avec
   `calvinkoch-ai/usine-vitrine` en source initiale.

Sans ces deux points, les missions 1 à 12 sont hors d'atteinte : elles portent
toutes sur du code que je ne peux pas lire.

**Non bloquant, faisable ici et maintenant si tu le veux :** le dépôt
`factory-assets` a ses propres défauts, mesurés en section 2.A, et le risque 1
conditionne la mission 4. Un pipeline de normalisation des médias (variantes
390/768/1440, AV1 + H.264 de repli, posters AVIF, strip des métadonnées, cible
de bitrate commune, LFS, manifeste de provenance) est un chantier autonome,
utile, et qui retire un obstacle de la route de la mission 4.

Dis-moi lequel des deux tu débloques.
