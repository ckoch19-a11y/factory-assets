# Ligne éditoriale — KORVEX « IA & agents IA sur mesure pour les PME » (v2, 01/10/2026)

**But** : des vues QUALIFIÉES (dirigeants de TPE/PME françaises) qui deviennent des conversations. Pas de la masse.
Chaque vidéo parle à UN type de dirigeant, d'UN problème concret, et lui montre ce qu'un agent IA change.
Étude source : `ETUDE-PERFORMANCE.md`. Avant d'écrire un jour : lire `stats/APPRENTISSAGES.md` et l'appliquer.

## 1. Les 5 créneaux et la diffusion (pas tout partout)
| # | Heure | Série | Thème | Diffusion |
|---|---|---|---|---|
| 1 | 07:45 | L'actu IA (news IA utile aux PME, ≤ 48 h) | papier | LinkedIn (profil de Calvin) + TikTok |
| 2 | 10:30 | Le chiffre (1-2 chiffres sourcés + ce que ça veut dire) | encre | TikTok |
| 3 | 12:30 | L'agent du métier (cas d'usage : métier différent chaque jour) | papier | Instagram + Facebook + TikTok |
| 4 | 17:30 | Avant / après (une tâche, le temps perdu, le temps avec l'agent) | encre | TikTok + Facebook |
| 5 | 19:30 | Le conseil KORVEX (méthode, erreur à éviter, ROI) | papier | Instagram + Facebook + TikTok |
Fréquences visées : TikTok 5/j, Instagram 2/j, Facebook 3/j, LinkedIn 1/j (aucun LinkedIn le week-end ; week-end = créneaux 3 et 5 seulement sur Instagram/Facebook).
Si `stats/APPRENTISSAGES.md` montre qu'un créneau/réseau sous-performe 2 semaines de suite → le dire dans le rapport final et proposer l'ajustement.

## 2. Métiers ciblés (rotation, jamais 2 fois le même dans la semaine pour le créneau 3)
artisans du bâtiment (plombier, électricien, couvreur), garages, cabinets comptables, agences/courtiers en assurance, agents immobiliers, commerces de proximité, restaurants, organismes de formation, transporteurs, cabinets médicaux/paramédicaux (sans données de santé), PME industrielles.
Dans chaque vidéo : le **métier** et le **problème** apparaissent dans le titre à l'écran, la voix ET la légende (c'est le référencement : les hashtags ne font plus la portée).

## 3. Le hook (0 à 1,5 s) — la seule chose qui compte pour la diffusion
Texte lisible dès l'image 0 + voix qui attaque immédiatement. Choisir un `hook_type` par vidéo et le noter dans le JSON :
- `metier` — « Garagistes : vos devis vous coûtent 6 h par semaine. »
- `chiffre` — « 66 %. C'est la part des tâches déjà confiées à des agents. »
- `question` — « Qui répond à vos clients quand vous êtes sur le chantier ? »
- `contre-intuitif` — « ChatGPT ne fera jamais vos devis. Un agent, si. »
- `perte` — « Chaque devis non relancé, c'est un client chez le concurrent. »
Pas de « Bonjour », pas de logo en ouverture, pas de mise en contexte avant le problème.
Varier les hook_types sur la journée (5 vidéos = au moins 4 hook_types différents).

## 4. Écriture
- 18-27 s, 2-3 scènes, voix ≤ 30 mots par scène. Une idée par vidéo.
- Voix (moteur Chatterbox) : écrire « IA » (lu automatiquement « i-a »). **Jamais** de sigles PME/TPE dans la voix : dire « petites entreprises », « dirigeants », « artisans ». Phrases de 10 à 25 mots (les phrases très courtes sont mal lues). Nombres en chiffres, « pour cent » géré automatiquement.
- À l'écran : groupes insécables avec espace insécable (« 24 h/24 », « 40 % »). `*mot*` = italique accent (une étoile de chaque côté d'un groupe de mots). Titres ≤ 3 lignes.
- Faits réels, sources datées dans `source`. Aucun chiffre inventé. Cas d'usage = ce qu'un agent FAIT (devis, relances, tri mails, RDV, saisie, SAV, veille, réponses clients). Pas de promesse chiffrée sur KORVEX (gain, prix). Aucun client nommé.
- Ton : direct, concret, vouvoiement, zéro jargon (« LLM », « prompt », « RAG » interdits à l'écran).

## 5. Légende et hashtags
- Ligne 1 = le hook reformulé avec métier + problème (mots-clés). Ligne 2 = la solution en une phrase. Ligne 3 = CTA unique : « Commentez AGENT avec votre métier : on vous montre ce qu'il ferait chez vous. »
- Hashtags (niche FR, pas #ia ni #business seuls) : Instagram 4-5, TikTok 3-5, LinkedIn 3, Facebook 2. Toujours 1 hashtag métier (#garagiste, #artisanbtp, #expertcomptable, #courtierassurance…) + 1 sujet (#agentia, #automatisation, #factureelectronique…) + 1 cible (#dirigeantpme, #tpe, #entrepreneur) + 1 local si pertinent (#dijon, #bourgogne).
- Champ JSON `hashtags` = {instagram:[…], tiktok:[…], linkedin:[…], facebook:[…]}.

## 6. Conformité
- Voix de synthèse réaliste → activer l'étiquette « contenu IA » sur TikTok et Meta à chaque publication (si le réglage existe dans `postiz integrations:settings`).
- Anti « contenu non original » : jamais deux vidéos du jour avec la même structure de scènes ; alterner thèmes papier/encre et types de scènes.

## 7. Champs JSON obligatoires par vidéo
`id, serie, creneau, theme, titre, source, metier, hook_type, reseaux[], scenes[], legende, hashtags{}`
