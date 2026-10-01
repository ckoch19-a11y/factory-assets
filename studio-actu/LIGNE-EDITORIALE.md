# Ligne éditoriale — KORVEX : IA, sites lus par l'IA, back-offices (v3, 01/10/2026)

**But** : des vues QUALIFIÉES (dirigeants de TPE/PME françaises) qui deviennent des conversations. Pas de la masse.
Chaque vidéo parle à UN type de dirigeant, d'UN problème concret, et lui montre ce qu'une offre KORVEX change.
Études : `ETUDE-PERFORMANCE.md` (algorithmes, formats) et `OFFRES-ET-ANGLES.md` (offres, chiffres qui vendent, formulations, objections, banque de 25 sujets). Modèle de tous les formats : `exemples/demo-formats.json`. Avant d'écrire un jour : lire `stats/APPRENTISSAGES.md` et l'appliquer.

## 1. Les 5 créneaux et la diffusion (pas tout partout)
| # | Heure | Série | Thème | Diffusion |
|---|---|---|---|---|
| 1 | 07:45 | L'actu IA (news IA utile aux PME, ≤ 48 h) | papier | LinkedIn (profil de Calvin) + TikTok |
| 2 | 10:30 | Le chiffre (1-2 chiffres sourcés + ce que ça veut dire) | encre | TikTok |
| 3 | 12:30 | L'agent du métier (cas d'usage : métier différent chaque jour) | papier | Instagram + Facebook + TikTok |
| 4 | 17:30 | Avant / après (une tâche, le temps perdu, le temps avec l'agent) | encre | TikTok + Facebook |
| 5 | 19:30 | Le conseil KORVEX (méthode, erreur à éviter, ROI) | papier | Instagram + Facebook + TikTok |
Fréquences visées : TikTok 5/j, Instagram 2/j, Facebook 3/j, LinkedIn 1/j (aucun LinkedIn le week-end ; week-end = créneaux 3 et 5 seulement sur Instagram/Facebook).
**Mix d'offres chaque jour** (champ `offre` : A agent IA · V site lu par l'IA · B back-office/facture électronique · L local) : au moins 3 offres différentes sur les 5 vidéos ; sur la semaine ≈ A 35 %, V 30 %, B 25 %, L 10 %, puis ajuster selon les stats. La série du créneau peut accueillir n'importe quelle offre.
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
- Voix : Vivienne (voix neuronale, lue d'un seul trait par scène, sous-titres calés au mot). Écrire « IA », les nombres en chiffres (« 40 % », « 3 fois »), ponctuation soignée (elle fait les pauses). **Jamais** de sigles PME/TPE dans la voix : « petites entreprises », « dirigeants », « artisans ». Aucune musique pendant la parole (gérée par le moteur).
- À l'écran : groupes insécables avec espace insécable (« 24 h/24 », « 40 % »). `*mot*` = italique accent (une étoile de chaque côté d'un groupe de mots). Titres ≤ 3 lignes.
- Faits réels, sources datées dans `source`. Aucun chiffre inventé. Cas d'usage = ce qu'un agent FAIT (devis, relances, tri mails, RDV, saisie, SAV, veille, réponses clients). Pas de promesse chiffrée sur KORVEX (gain, prix). Aucun client nommé.
- Ton : direct, concret, vouvoiement, zéro jargon (« LLM », « prompt », « RAG » interdits à l'écran).

## 5. Légende et hashtags
- Ligne 1 = le hook reformulé avec métier + problème (mots-clés). Ligne 2 = la solution en une phrase. Ligne 3 = CTA unique adapté à l'offre : A « Commentez AGENT avec votre métier » · V « Commentez SITE : on teste le vôtre » · B « Commentez 2027 » ou « RELANCE » · L « Commentez VILLE ».
- Hashtags (niche FR, pas #ia ni #business seuls) : Instagram 4-5, TikTok 3-5, LinkedIn 3, Facebook 2. Toujours 1 hashtag métier (#garagiste, #artisanbtp, #expertcomptable, #courtierassurance…) + 1 sujet (#agentia, #automatisation, #factureelectronique…) + 1 cible (#dirigeantpme, #tpe, #entrepreneur) + 1 local si pertinent (#dijon, #bourgogne).
- Champ JSON `hashtags` = {instagram:[…], tiktok:[…], linkedin:[…], facebook:[…]}.

## 5 bis. Formats visuels — chaque vidéo doit avoir un visuel fort et différent
Types de scènes : `hook`, `chiffre`, `points`, `texte`, et les formats « démo » :
- `recherche` : conversation avec un assistant IA {label, question, reponse (**gras** = ce qui est cité), cite} — idéal pour l'offre V (« j'ai demandé à l'IA… »). Réponse illustrative et générique : jamais un vrai nom d'entreprise.
- `notifs` : téléphone qui reçoit des notifications {heure, label, notifs:[{app, heure, titre, texte}] ≤ 4} — idéal pour A (l'agent travaille pendant la nuit).
- `avantapres` : {label_avant, label_apres, avant[≤3], apres[≤3]} — idéal pour B.
- `kpis` : 2 à 4 tuiles chiffrées qui comptent {label, kpis:[{valeur, label}]} — chiffres sourcés uniquement.
Règles : chaque vidéo contient au moins 1 format démo OU un `chiffre` fort ; jamais 2 vidéos du jour avec la même suite de types de scènes.
Habillage : `theme` ∈ papier | encre | sable | ardoise et `fond` ∈ bandes | grille | halo | lignes | points — 5 combinaisons différentes chaque jour (si `fond` absent, le moteur en tire un).
La fin s'adapte à l'offre (A/V/B/L) : texte et voix de conclusion différents.

## 6. Conformité
- Voix de synthèse réaliste → activer l'étiquette « contenu IA » sur TikTok et Meta à chaque publication (si le réglage existe dans `postiz integrations:settings`).
- Anti « contenu non original » : jamais deux vidéos du jour avec la même structure de scènes ; alterner thèmes papier/encre et types de scènes.

## 7. Champs JSON obligatoires par vidéo
`id, serie, creneau, theme, fond, offre, titre, source, metier, hook_type, reseaux[], scenes[], legende, hashtags{}`
