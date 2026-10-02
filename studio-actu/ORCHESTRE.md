# L'orchestre KORVEX — qui décide quoi, chaque matin

Deux tâches planifiées, zéro geste de Calvin :
- **Orchestre** (`taches/orchestre.md`, 20:30, cloud) produit le lot du lendemain et le dépose dans la régie.
- **Diffusion** (`taches/diffusion.md`, 21:50 + rattrapage 06:50, sur le Mac) pilote le Chrome de Calvin : programme chaque vidéo sur TikTok / Meta (Facebook + Instagram) / LinkedIn à son créneau, puis relève les stats des 7 derniers jours dans la régie.
Les posts sont programmés chez les réseaux eux-mêmes : ils partent à l'heure même si le Mac est éteint ensuite.
Régie **Studio KORVEX** https://claude.ai/artifact/CUgQUZ6Fmv9A3ft2ULHcWz — base `videos/<date>-<id>` (champs `diffusion`, `publie`, `stats` remplis automatiquement) et `orchestre/<date>` (état de chaque production).

## Les rôles
| Rôle | Qui | Livre |
|---|---|---|
| **Analyste** | agent (en parallèle du Veilleur) | lit `stats/export.json` (la base `videos` de la régie), lance `python3 analyse.py`, résume en 8 lignes : ce qui marche (offres, formats, accroches, métiers, réseaux, horaires), ce qui échoue, le volume recommandé |
| **Veilleur** | agent (en parallèle) | 8 à 10 faits datés et sourcés < 48 h utiles aux dirigeants de PME (IA, recherche par IA, facture électronique, impayés, local, cyber) + 1 problème concret par métier ciblé |
| **Chef d'orchestre** | la tâche | arbitre : volume du jour, mix d'offres, créneaux, réseaux, métiers ; écrit la feuille de route |
| **Scénariste + directeur artistique** | la tâche | écrit `jours/<date>.json` : pour chaque vidéo 2 accroches candidates, garde la meilleure (règle : chiffre ou perte concrète + métier, ≤ 9 mots à l'écran) ; choisit format démo, `objet`, thème, fond |
| **Contrôleur** | agent neuf (n'a pas vu l'écriture) | relit le JSON contre LIGNE-EDITORIALE.md et les sources (aucun chiffre sans source, aucun nom réel inventé, sigles, longueurs) puis la planche de contrôle ; renvoie une liste de corrections |
| **Planificateur** | script `planifier.py` | horaires par réseau, légendes + hashtags par réseau → `sorties/<date>/plan.json` prêt pour la régie |
| **Diffuseur** | tâche Diffusion (Chrome du Mac) | programme chaque vidéo sur chaque réseau, relève vues/likes/commentaires/partages/enregistrements, tient `taches/NOTES-UI.md` |

## Volume du jour (minimum 5)
Base 5 vidéos, tous les jours. On monte jusqu'à **8** seulement si les trois conditions sont vraies :
1. ≥ 80 % des vidéos des 7 derniers jours ont réellement été diffusées (vues en ligne par le Diffuseur, case « Publié ») — sinon produire plus ne sert à rien ;
2. les vues médianes des 7 derniers jours ne baissent pas par rapport aux 7 précédents (ou pas encore de données) ;
3. le Veilleur a ≥ 2 faits forts de moins de 24 h non encore traités.
+1 par condition remplie au-delà de la première (ex. 1+2 → 6 ; 1+2+3 → 7 ; 8 les jours d'actu exceptionnelle). `analyse.py` calcule la recommandation.

## Horaires (heure de Paris) et réseaux
Sources : Sprout Social 2026 (mar-jeu meilleurs, week-end le plus faible), Swello FR (LinkedIn 7-8 h, 10-11 h, 12-14 h), Buffer.
| Créneau | Usage | LinkedIn | Instagram | Facebook | TikTok |
|---|---|---|---|---|---|
| 07:45 | actu, chiffre | ✔ (1 seul LinkedIn par jour, lun-ven) | | | ✔ |
| 10:30 | chiffre / test | | | | ✔ |
| 12:30 | cas métier | | ✔ Reel | ✔ | ✔ |
| 15:00 | vidéo bonus n°6 | | | | ✔ |
| 17:30 | avant/après, démo | | | ✔ | ✔ |
| 19:30 | conseil, objection | | ✔ Reel | ✔ | ✔ |
| 21:00 | vidéo bonus n°7-8 | | | ✔ | ✔ |
Plafonds : TikTok 5-8/j, Instagram 2/j, Facebook 3/j, LinkedIn 1/j (aucun le week-end). Week-end : 5 vidéos, réseaux Instagram/Facebook/TikTok, créneaux 10:30-21:00 (les artisans regardent le soir). Après 2 semaines de stats, l'Analyste peut proposer de déplacer un créneau (jamais plus d'un changement par semaine).

## Hashtags
Règle : métier + sujet + cible + local, niche FR, jamais #ia ou #business seuls. Instagram 4-5, TikTok 3-5, LinkedIn 3, Facebook 2.
- Métiers : #artisanbtp #plombier #electricien #couvreur #garagiste #garageauto #expertcomptable #courtierassurance #agentimmobilier #commercant #restaurateur #organismedeformation #transporteur
- Offre A : #agentia #automatisation #assistantia · V : #siteweb #referencement #visibiliteweb · B : #factureelectronique #gestionentreprise #tresorerie #impayes · L : #referencementlocal #avisgoogle
- Cible : #dirigeantpme #tpe #entrepreneur #chefdentreprise
- Local : #dijon #cotedor #bourgogne #beaune #chalonsursaone
L'Analyste compare chaque semaine les vues par hashtag métier et remplace ceux qui ne rapportent rien.

## La boucle d'apprentissage
Chaque soir, le Diffuseur relève lui-même vues, likes, commentaires, partages et enregistrements dans les outils des réseaux (TikTok Studio, Meta Business Suite, LinkedIn) et les écrit dans la régie. Puis l'Orchestre : export de la base → `analyse.py` → `stats/APPRENTISSAGES.md` → décisions du lot suivant. Calvin peut toujours corriger un chiffre à la main dans la régie. Le dimanche, l'Analyste ajoute ≤ 3 « Ajustements appris » chiffrés en bas de LIGNE-EDITORIALE.md.
