# Brief — L'Atelier de Paola

> Pipeline « URL → site » · généré depuis https://www.latelier-de-paola.com (+ sous-pages tarifs, coupes, soins, contact, mentions légales, et fiche Planity publique).
> Bibliothèque : `https://base44.app/api/apps/6a5d5bf2e798592362f80150/functions/library` (recette `url-to-site`, styles, catalogue design).
> **Registre unique pour tout le site : `editorial`.** Style de référence : `steep`.
> Règle absolue : aucune donnée factuelle ci-dessous n'a été inventée ; tout ce qui manque est marqué « NON TROUVÉ — à confirmer par le client » (récapitulatif en §6).

---

## 1. Identité & ton

| Champ | Valeur |
|---|---|
| Nom | L'Atelier de Paola |
| Métier | Salon de coiffure — coiffeur visagiste, conseil en image, coiffure de mariage |
| Baseline d'origine | « Salon de coiffure Dijon : coiffeur, visagiste, conseil en image, coiffure mariage » |
| Fondatrice | Paola Sonza (directrice de publication du site ; « Paola, coiffeur visagiste ») |
| Équipe (source Planity) | Paola et Mélanie, épaulées par Bruno, Sati et Khalid — rôles exacts NON TROUVÉS, à confirmer |
| Adresse | 93 rue Jean-Jacques Rousseau, 21000 Dijon (quartier des Antiquaires, près de la place de la République) |
| Téléphone | 03 80 67 17 23 |
| Email | contact@latelier-de-paola.com |
| Horaires (site officiel) | Mardi 9 h 30 – 18 h · Mercredi–Vendredi 9 h – 18 h · Samedi 9 h – 17 h · Fermé dimanche et lundi (Planity indique jeudi jusqu'à 18 h 30 — à confirmer, cf. §6) |
| Réservation en ligne | https://www.planity.com/latelier-de-paola-21000-dijon |
| Facebook | https://www.facebook.com/latelier.depaola |
| Instagram | https://www.instagram.com/sonzapaola/ |
| Preuves | **4,9/5 — 1 063 avis** sur Planity (relevé juillet 2026) |
| Marques travaillées / vendues | Marcapar (coloration végétale), Sublimo, Chromalya, Umaï, Comme Avant |
| Engagements | Solid'Hair (don de cheveux pour perruques), Coiffeurs Justes (recyclage) |
| Différenciateurs | Coloration végétale Marcapar, balayage à l'argile blanche, décoloration sans ammoniaque, yoga du visage, épilation au fil, coiffure/maquillage de mariage (essais mentionnés sur le site), décor « brocante chic » |
| Public | Femmes, hommes, enfants (« autant à vous mesdemoiselles et mesdames, qu'à vous messieurs ») |
| Légal | SIRET 438 004 681 00013 · APE 9602A · TVA FR63438004681 |
| Zone desservie | Dijon et agglomération (salon de quartier — pas de zone élargie revendiquée) |

**Ton de la marque (3 adjectifs) : chaleureux, naturel, attentionné.**
Écriture : phrases courtes, tutoiement exclu (vouvoiement doux), vocabulaire concret (cheveu, soin, végétal), zéro jargon marketing, zéro superlatif criard. On parle comme une artisane qui conseille, pas comme une enseigne.

---

## 2. Style retenu

**Retenu : `steep`** (« Analytics serif sur papier chaud », mode clair). Justification : métier de contact → registre éditorial chaleureux ; le papier chaud, le serif retenu et l'unique accent pêche `#fbe1d1` collent exactement au positionnement « brocante chic + végétal + féminin » du salon, et la grille magazine met en valeur une vraie grille tarifaire.
**Écarté : `mindmarket`** (« Livre d'images chaleureux sur papier crème ») : chaleureux aussi, mais son esprit illustratif/ludique tire vers l'enfantin — inadapté à un salon au positionnement chic et apaisé. (Les styles sombres type `linear`/`mercury` sont hors sujet d'office : métier de contact, pas technique.)

**Articulation style ↔ composants (directive d'exécution, aucune décision à prendre)** :
1. Le DESIGN.md ci-dessous s'implémente en tokens CSS (`src/index.css` :root + `tailwind.config.js`) et régit tout ce qui n'est pas un composant bibliothèque : fonds de page, typo display, boutons, formulaires, radii.
2. Les composants copiés depuis la bibliothèque conservent leurs tokens `editorial` embarqués — on ne les réécrit pas (ils sont de la même famille chromatique : papier chaud, serif, accent chaud).
3. Partout où un composant expose une couleur par prop (`to` des transitions, `colors`…), utiliser les hex Steep : `#ffffff`, `#fafafb`, `#f2f2f3`, accent `#fbe1d1`, encre `#17191c`.

### DESIGN.md intégral (steep)

# DESIGN.md — Steep

> Analytics serif sur papier chaud · mode clair · inspiré de https://steep.app

L'analytics rendue éditoriale : titres serif (Signifier, graisse 400 à toutes les tailles — le serif chuchote l'autorité), canvas blanc quasi monochrome, et une seule pêche chaude (#fbe1d1) en ponctuation. Cartes 24px aux bords doux, contrôles pilule à plat, ombres à peine perceptibles. La page se lit comme un magazine produit.

## Palette

- **Blush Peach** `#fbe1d1` — Carte accent, surlignage chaud — seule surface chromatique, une fois par page max
- **Sienna Brown** `#5d2a1a` — Encre sur surfaces pêche, traits de graphiques — jamais en corps sur blanc
- **Ink Black** `#17191c` — Texte principal, bouton rempli — seule surface sombre
- **Slate Gray** `#777b86` — Liens, texte d'aide, footer
- **Ash Gray** `#979799` — Labels tertiaires, tags de catégorie
- **Mist Gray** `#f2f2f3` — Surfaces de cartes, fonds d'inputs
- **Fog White** `#fafafb` — Fond secondaire pour bandes alternées
- **Paper White** `#ffffff` — Canvas dominant

## Typographie

- **Display** : Signifier (fallback : Tiempos Headline, Source Serif 4, Georgia) — H1/H2 à 44/64/90px, toujours graisse 400 — la retenue est la signature ; tracking -0.025em à 90px
- **Corps** : Söhne (fallback : Inter, system-ui) — 14–26px avec demi-graisses 430/450/480 — hiérarchie fine sans passer au bold

- Échelle tierce mineure (1.2) depuis 15px — display 90px serif 400 interligne 1.3
- Demi-graisses Söhne (430/450/480) avant d'atteindre 500
- Liens sans soulignement au repos — la flèche → porte l'affordance

## Espacement

- Densité confortable, unité 4px
- Largeur max 1200px
- Écarts de section 80px, padding de carte 20px, gaps 8px

## Rayons de bordure

- images 12px
- inputs & petites cartes 16px
- cartes élevées 20px
- cartes 24px
- boutons 9999px

## À faire

- Serif 400 pour tout display — jamais de sans à ces tailles, jamais de bold serif
- La carte pêche #fbe1d1 une seule fois par page, posée sur blanc
- Chaque pilule remplie (#17191c) est accompagnée d'une pilule ghost sur la même ligne
- Deux radii structurels : 9999px boutons, 24px cartes

## À ne pas faire

- Pas de chromatique au-delà du duo pêche/brun — le système est 97% achromatique
- Pas d'ombres sur les cartes de contenu — seuls les artefacts produit flottants y ont droit
- Pas de radius sous 16px sur les cartes
- Le brun #5d2a1a jamais en corps sur blanc

## Application

Implémente ce système via des tokens CSS (`src/index.css` :root + .dark) mappés dans `tailwind.config.js`. Utilise les classes mappées (`bg-primary`, `font-heading`…) dans le JSX — jamais de valeurs en dur. Remplace les polices propriétaires par leurs fallbacks Google Fonts indiqués.

---

## 3. Plan de page (accueil — page unique à ancres)

Registre : **`editorial` partout** (prop `register="editorial"` sur chaque composant qui l'accepte). Une seule rupture de registre autorisée : le bandeau RDV final (règle ASSEMBLAGE §1). Ordre canonique hero → preuve → offre → confiance → conversion respecté.

### Composants transverses (montés une fois, hors flux de sections)

| Id composant | Contenus / props |
|---|---|
| `navigation/NavbarLisible` | `register="editorial"` · `nom="L'Atelier de Paola"` · `liens=[{label:"Prestations", href:"#prestations"}, {label:"Tarifs", href:"#tarifs"}, {label:"Le salon", href:"#salon"}, {label:"Contact", href:"#contact"}]` · `ctaLabel="Prendre rendez-vous"` · `onCta` → ouvre https://www.planity.com/latelier-de-paola-21000-dijon (nouvel onglet) · `onMenuMobile` → ouvre MenuOverlay |
| `navigation/MenuOverlay` | `register="editorial"` · mêmes `liens` que la navbar · `contact={adresse:"93 rue Jean-Jacques Rousseau, 21000 Dijon", telephone:"03 80 67 17 23", email:"contact@latelier-de-paola.com"}` |
| `navigation/ProgressionScroll` | `register="editorial"` · `seuil` par défaut |
| `effets/CurseurEtiquette` | `register="editorial"` · cibles : conteneur de la galerie S7 marqué `data-cursor="Le salon"`, cartes prestations S4 marquées `data-cursor="Voir les tarifs"` |

### Sections (dans l'ordre)

| # | Id composant | Registre | Contenus réels à injecter (par prop) |
|---|---|---|---|
| 1 | `heros/HeroHalo` | editorial | `badge="Coiffeur visagiste — Quartier des Antiquaires, Dijon"` · `title="Votre coiffure, au naturel."` · `subtitle="Coupes visagistes, colorations végétales Marcapar et coiffures de mariage, dans un salon à l'esprit brocante chic, à deux pas de la place de la République."` · `ctaPrimary="Prendre rendez-vous"` (`onPrimary` → Planity) · `ctaSecondary="Voir nos tarifs"` (`onSecondary` → ancre `#tarifs`) · `note="Coloration végétale · Partenaire Solid'Hair & Coiffeurs Justes"` |
| 2 | `avis/NoteGlobale` | editorial | `note=4.9` · `total=1063` · `plateformes=["Planity"]` · `mention="Note moyenne des avis clients vérifiés Planity — relevée en juillet 2026."` |
| 3 | `prestations/CartesPrestations` (ancre `#prestations`) | editorial | `kicker="Nos prestations"` · `title="Ce que nous faisons pour vos cheveux"` · `items=` voir tableau A ci-dessous (5 cartes, vedette = coloration végétale) · `ctaLabel="Toute la grille des tarifs"` · `onCta` → `#tarifs` |
| 4 | `prestations/TarifsListe` (ancre `#tarifs`) | editorial | `title="Nos tarifs"` · `note="Le soin est offert avec le shampooing, la coupe et le brushing. Prix TTC affichés en salon — les prestations techniques sont ajustées après diagnostic."` · `groups=` grille intégrale verbatim, tableau B ci-dessous |
| — | `transitions/PontCourbe` | editorial | Ferme la section 4. `variant="vague"` · `height=80` · `to=` couleur de fond de la section 5 (token embarqué du composant copié ; défaut Steep `#fafafb`) |
| 5 | `equipe/PortraitEditorial` | editorial | `name="Paola Sonza"` · `role="Fondatrice — coiffeuse visagiste"` · `bio="Dans son salon du quartier des Antiquaires, Paola pratique une coiffure de conseil : coupes visagistes, colorations 100 % végétales Marcapar, balayages à l'argile blanche et coiffures de mariage. Le décor est chiné, l'accueil attentionné, et les engagements concrets : les cheveux coupés sont donnés à Solid'Hair pour la confection de perruques, et le salon recycle avec Coiffeurs Justes."` · `signature="Paola"` · `image=` **NON TROUVÉ (portrait) — à fournir par la cliente** ; en attendant, utiliser la photo du salon https://www.latelier-de-paola.com/media/images/upload/1000060923.jpg · `imageAlt="Paola dans son salon, Dijon"` |
| 6 | `galeries/DefileHorizontal` (ancre `#salon`) | editorial | `title="Le salon"` · `images=[{src:"https://www.latelier-de-paola.com/media/images/upload/1000060923.jpg", legende:"L'Atelier de Paola — 93 rue Jean-Jacques Rousseau, Dijon"}, {src:"https://www.latelier-de-paola.com/media/images/upload/1000060924.jpg", legende:"Le salon"}, {src:"https://www.latelier-de-paola.com/media/images/upload/eab400ec-c0b3-4272-b2e4-35f29508ffe5-1-all-70534.jpg", legende:"L'esprit brocante chic"}, {src:"https://www.latelier-de-paola.com/media/images/upload/thumbnail-1000035009.webp", legende:"Le yoga du visage"}]` — légendes neutres à ajuster si le contenu réel des photos diffère (§6) |
| 7 | `avis/BandeauLogos` | editorial | `titre="Nos marques & nos engagements"` · `logos=[{texte:"Marcapar"}, {texte:"Sublimo"}, {texte:"Chromalya"}, {texte:"Umaï"}, {texte:"Comme Avant"}, {texte:"Solid'Hair"}, {texte:"Coiffeurs Justes"}]` (mode texte — logos images NON TROUVÉS) |
| — | `transitions/PontFondu` | editorial | Ferme la section 7. `filet=true` (fil doré éditorial) · `height=120` · `to=` couleur de fond du BandeauRdv copié (relever le token embarqué dans le fichier après copie) |
| 8 | `cta/BandeauRdv` | editorial (rupture matiérée assumée — la seule de la page) | `title="Prenez rendez-vous"` · `texte="Réservez en ligne en deux minutes, ou appelez-nous : nous prendrons le temps de vous conseiller."` · `ctaLabel="Réserver sur Planity"` · `onCta` → https://www.planity.com/latelier-de-paola-21000-dijon · `telephone="03 80 67 17 23"` · `note="Mardi 9 h 30 – 18 h · Mercredi–Vendredi 9 h – 18 h · Samedi 9 h – 17 h"` |
| 9 | Formulaire de contact (ancre `#contact`) — **snippet de la recette** `?pipeline=1`, étape `vitrine` : `src/components/vitrine/FormulaireContact.jsx` | editorial (stylé via tokens Steep : inputs fond `#f2f2f3` radius 16px, bouton pilule `#17191c`) | Champs : nom, email, téléphone, message → crée un enregistrement `DemandeContact` · intro courte : `"Une question, un projet de mariage, un conseil couleur ? Écrivez-nous, nous vous répondons vite."` · confirmation : `"Merci ! Nous revenons vers vous très vite."` |
| 10 | `footers/FooterMaison` | editorial | `nom="L'Atelier de Paola"` · `description="Salon de coiffure visagiste au cœur du quartier des Antiquaires — coupes, colorations végétales, mariage."` · `adresse="93 rue Jean-Jacques Rousseau, 21000 Dijon"` · `telephone="03 80 67 17 23"` · `email="contact@latelier-de-paola.com"` · `horaires=[{jours:"Mardi", heures:"9 h 30 – 18 h"}, {jours:"Mercredi – Vendredi", heures:"9 h – 18 h"}, {jours:"Samedi", heures:"9 h – 17 h"}, {jours:"Dimanche – Lundi", heures:"Fermé"}]` · `liens=[{label:"Prestations", href:"#prestations"}, {label:"Tarifs", href:"#tarifs"}, {label:"Le salon", href:"#salon"}, {label:"Prendre RDV", href:"https://www.planity.com/latelier-de-paola-21000-dijon"}]` · `legaux=[{label:"Mentions légales", href:"/mentions-legales"}, {label:"Politique de confidentialité", href:"/confidentialite"}]` · `copyright="© 2026 L'Atelier de Paola — SIRET 438 004 681 00013"` |

Enchaînements vérifiés : jamais deux figures identiques d'affilée (halo → bandeau stat → grille de cartes → liste à filets → portrait → défilé horizontal → marquee logos → bandeau plein → formulaire → footer) ; transitions posées aux deux changements de fond marqués (fin S4, fin S7) ; un seul `h1` (hero) ; une seule rupture (S8).

#### Tableau A — items de `CartesPrestations` (S3)

| categorie | nom | texte | prix | duree | vedette |
|---|---|---|---|---|---|
| Signature | Coloration végétale Marcapar | Des pigments 100 % végétaux qui respectent le cuir chevelu et la fibre. Une, deux ou trois applications selon le résultat recherché, après diagnostic. | à partir de 40 € | ≈ 1 h 30 (durée Planity) | true |
| Femmes | Coupe & brushing | Coupe visagiste personnalisée, shampooing et brushing — le soin est offert. | 36 € à 50 € | ≈ 30 min (durée Planity) | false |
| Hommes | Coupe homme | Coupe ciseaux ou tondeuse, au salon sans chichis. | 13 € à 25 € | ≈ 30 min (durée Planity) | false |
| Mariage | Coiffure de mariage | Chignon bohème ou romantique, tresses, coiffage naturel — essais mentionnés sur le site ; maquillage sur consultation. | sur consultation | NON TROUVÉ | false |
| Bien-être | Yoga du visage | Un moment de détente et de tonus pour le visage, en 10, 20 ou 30 minutes. | 15 € à 30 € | 10 à 30 min | false |

#### Tableau B — `groups` de `TarifsListe` (S4) — grille VERBATIM du site (juillet 2026)

Structure exacte à injecter (`label` de groupe · `items:[{name, price, detail?}]`) :

- **Shampooing / Brushing** *(soin offert)* — Cheveux courts `24 € à 26 €` · Cheveux mi-longs `26 € à 30 €` · Cheveux longs `30 € à 45 €` · Supplément boucles au fer `6 €`
- **Shampooing / Coupe / Brushing — Femmes** *(soin offert)* — Coupe cheveux courts `36 € à 38 €` · Coupe cheveux mi-longs `38 € à 40 €` · Coupe cheveux longs `40 € à 50 €`
- **Étudiantes** — Cheveux courts `26 €` · Cheveux mi-longs `28 € à 30 €` · Cheveux longs `30 € à 35 €`
- **Adolescentes (moins de 16 ans)** *(shampooing + coupe + brushing, soin offert)* — Forfait `20 € à 25 €`
- **Enfants** — Moins de 10 ans `16 €` · Moins de 3 ans `12 €`
- **Hommes** — Coupe ciseaux `25 €` · Étudiant `19 €` · Coupe tondeuse `13 €`
- **Techniques — Couleur** — Sans ammoniaque ou ton sur ton `34 €` · Décoloration `à partir de 35 €` · Supplément par 10 g `2 €`
- **Techniques — Patine** — Cheveux courts `20 €` · Cheveux longs `25 € à 30 €`
- **Techniques — Balayage** — Cheveux courts `20 € à 45 €` · Cheveux mi-longs `45 € à 70 €` · Cheveux longs `70 € à 110 €`
- **Techniques — Transformation** — Coupe transformation `45 € à 55 €` *(soin compris)*
- **La couleur végétale Marcapar** — Soin du cuir chevelu (huile apaisante, rafraîchissante ou stimulante + massage + masque à l'argile) `25 € à 30 €` · Coloration végétale 1 application `à partir de 40 €` · 2 applications `à partir de 56 €` · 3 applications ou plus `à partir de 68 €` · Sur cheveux longs (base 60 g), supplément par 10 g `2 €` · Lait végétal `25 € à 30 €`
- **Épilation au fil** — Sourcils `15 €` · Dessus de la bouche `10 €` · Sourcils + dessus de la bouche `20 €`
- **Maquillage** — Maquillage de mariage et de soirée `Nous consulter`
- **Yoga du visage** — 10 min `15 €` · 20 min `20 €` · 30 min `30 €`

---

## 4. Entités (contrat vitrine ↔ back-office)

Les 5 entités canoniques de la recette (`?pipeline=1`, étape `contenu`), adaptées au métier — structure globale inchangée. Le vitrine **lit**, le back-office **écrit** ; chaque section garde en fallback les contenus du §3.

### 4.1 `SiteConfig` (1 seul enregistrement)

Champs : `nom` (string, requis) · `slogan` · `description` · `adresse` · `telephone` · `email` · `horaires` (string) · `instagram` · `facebook` · `url_rdv` · `siret` · `tva` · `url_source` · `brief` (object, brief rejouable).

Enregistrement initial :
`{ nom:"L'Atelier de Paola", slogan:"Coiffeur visagiste, conseil en image, coiffure mariage — Dijon", description:"Salon de coiffure visagiste au cœur du quartier des Antiquaires : coupes, colorations végétales Marcapar, coiffures de mariage.", adresse:"93 rue Jean-Jacques Rousseau, 21000 Dijon", telephone:"03 80 67 17 23", email:"contact@latelier-de-paola.com", horaires:"Mardi 9h30–18h · Mercredi–Vendredi 9h–18h · Samedi 9h–17h", instagram:"https://www.instagram.com/sonzapaola/", facebook:"https://www.facebook.com/latelier.depaola", url_rdv:"https://www.planity.com/latelier-de-paola-21000-dijon", siret:"43800468100013", tva:"FR63438004681", url_source:"https://www.latelier-de-paola.com" }`

### 4.2 `Prestation`

Champs : `nom` (requis) · `description` · `prix` (string — les fourchettes et « à partir de » existent) · `duree` · `categorie` · `vedette` (bool, défaut false) · `ordre` (number, défaut 0) · `visible` (bool, défaut true) · `image_url`.

Enregistrements initiaux = **toutes les lignes du tableau B** (une Prestation par ligne, `categorie` = label du groupe, `ordre` = position dans le groupe, prix verbatim) **+** `vedette=true` sur « Coloration végétale 1 application ». La section S4 groupe par `categorie` ; la section S3 lit les 5 cartes du tableau A (les créer aussi, `categorie:"carte-accueil"`, ordre 1–5, pour que le back-office pilote les cartes d'accueil indépendamment de la grille).

### 4.3 `Temoignage`

Champs : `auteur` (requis) · `texte` (requis) · `note` (number, défaut 5) · `source` · `date` · `visible` (bool, défaut true).

Enregistrements initiaux (les seuls avis au texte vérifié — ne PAS en inventer d'autres) :
1. `{ auteur:"Avis client vérifié — Planity", texte:"Moment très agréable mené avec compétence et gentillesse.", note:5, source:"Planity", date:"2026-07-16" }`
2. `{ auteur:"Avis client vérifié — Planity", texte:"Première visite et je suis enchantée de ma coupe. Très bonne surprise.", note:5, source:"Planity", date:"2026-06-26" }`

(La page d'accueil n'affiche que la note agrégée S2 — ces témoignages alimentent le back-office et pourront nourrir une future section avis ; en ajouter depuis Planity via le back-office.)

### 4.4 `SectionContenu`

Champs : `cle` (requis) · `titre` · `sous_titre` · `texte` · `image_url` · `visible` (bool, défaut true).

Enregistrements initiaux (copie exacte des contenus du §3) : `hero` (badge en sous_titre, title en titre, subtitle en texte) · `note_globale` (mention) · `prestations` (kicker+title) · `tarifs` (title + note) · `apropos` (name/role/bio/signature du portrait) · `salon` (titre + 4 image_url/légendes → une entrée par photo : `salon_1`…`salon_4`) · `marques` (titre) · `cta_final` (title + texte + note horaires) · `contact` (intro + message de confirmation) · `footer` (description + copyright).

### 4.5 `DemandeContact`

Champs : `nom` (requis) · `email` · `telephone` · `message` (requis) · `statut` (enum `nouvelle`/`traitee`, défaut `nouvelle`). **Aucun enregistrement initial** — remplie par le formulaire S9, consultée dans le back-office. Création anonyme/publique à activer sur cette entité (réglage Base44 côté compte).

---

## 5. Back-office (`/admin`, sous ProtectedRoute — pattern ÉditeurEntite de la recette, étape `backoffice`)

Même niveau de design que le vitrine, en plus sobre (tokens Steep, sidebar).

| Écran | Route | Entité | Champs éditables |
|---|---|---|---|
| Tableau de bord | `/admin` | — | Compteurs (prestations visibles, avis, demandes) · badge « demandes nouvelles » (realtime `subscribe`) · lien « voir le site » |
| Paramètres | `/admin/parametres` | `SiteConfig` | nom, slogan, description, adresse, telephone, email, horaires, instagram, facebook, url_rdv, siret, tva (url_source et brief en lecture seule) |
| Contenus | `/admin/contenu` | `SectionContenu` | Par clé : titre, sous_titre, texte, image_url, visible |
| Prestations & tarifs | `/admin/prestations` | `Prestation` | nom, description, prix, duree, categorie, vedette, ordre, visible, image_url — création/suppression incluses (toute la grille tarifaire s'édite ici) |
| Avis | `/admin/avis` | `Temoignage` | auteur, texte, note, source, date, visible — création/suppression incluses |
| Demandes | `/admin/demandes` | `DemandeContact` | Lecture (nom, email cliquable mailto, téléphone cliquable tel, message, date) · action unique : statut → « traitee » |

---

## 6. Données manquantes / divergences — à confirmer par le client

1. **Tarifs divergents site ↔ Planity** (le site semble en retard) : coloration végétale 1 pose « à partir de 40 € » (site) vs « à partir de 66 € » (Planity) · ton sur ton « 34 € » (site) vs « à partir de 56 € » (Planity) · shampooing/brushing courts « 24–26 € » (site) vs « 26–28 € » (Planity). → Quelle grille fait foi ? Le brief injecte la grille du site officiel.
2. **Horaires du jeudi** : site = 9 h – 18 h · Planity = 9 h – 18 h 30.
3. **Équipe** : Paola, Mélanie, Bruno, Sati, Khalid (noms relevés sur Planity) — rôles et présence sur le site à valider ; **portrait photo de Paola NON TROUVÉ** (photo du salon utilisée en attendant).
4. **Photos** : seules 4 images exploitables trouvées ; galerie complète HD à fournir (le dossier `/media/images/gallery/12/` n'expose pas d'URLs unitaires). Légendes S6 neutres — à ajuster au contenu réel des photos.
5. **Prix mariage / chignon mariée** : « nous consulter » sur le site ; Planity affiche « chignons rapides 35–50 € » — à clarifier avant d'afficher.
6. **Ancienneté / année de création** : NON TROUVÉ — à confirmer (utile pour la preuve « depuis 20XX »).
7. **Détail « essais illimités » mariage** : mentionné sur le site — formulation exacte à valider avant de l'afficher comme promesse.
8. **Logos images** des marques/engagements : NON TROUVÉS — bandeau S7 en mode texte en attendant.
