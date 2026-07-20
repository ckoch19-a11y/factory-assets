/* Contenus du BRIEF.md (§1, §3, §4) — source unique de vérité pour :
   1. les fallbacks des sections (le vitrine n'est jamais cassé si une entité est vide) ;
   2. les données initiales des entités (scripts/seed.mjs).
   Aucune donnée inventée : tout provient du brief ; les manques y sont marqués
   « NON TROUVÉ — à confirmer par le client ». */

export const PLANITY_URL = "https://www.planity.com/latelier-de-paola-21000-dijon";

export const NAV = {
  nom: "L'Atelier de Paola",
  liens: [
    { label: "Prestations", href: "#prestations" },
    { label: "Tarifs", href: "#tarifs" },
    { label: "Le salon", href: "#salon" },
    { label: "Contact", href: "#contact" },
  ],
  ctaLabel: "Prendre rendez-vous",
  contact: {
    adresse: "93 rue Jean-Jacques Rousseau, 21000 Dijon",
    telephone: "03 80 67 17 23",
    email: "contact@latelier-de-paola.com",
  },
};

export const HERO = {
  badge: "Coiffeur visagiste — Quartier des Antiquaires, Dijon",
  title: "Votre coiffure, au naturel.",
  subtitle:
    "Coupes visagistes, colorations végétales Marcapar et coiffures de mariage, dans un salon à l'esprit brocante chic, à deux pas de la place de la République.",
  ctaPrimary: "Prendre rendez-vous",
  ctaSecondary: "Voir nos tarifs",
  note: "Coloration végétale · Partenaire Solid'Hair & Coiffeurs Justes",
};

export const NOTE_GLOBALE = {
  note: 4.9,
  total: 1063,
  plateformes: ["Planity"],
  mention: "Note moyenne des avis clients vérifiés Planity — relevée en juillet 2026.",
};

/* Tableau A du brief — les 5 cartes d'accueil (S3).
   NB : dans l'entité Prestation ces cartes portent categorie:"carte-accueil" (brief §4.2) ;
   le libellé affiché sur la carte (Signature, Femmes…) n'a pas de champ dédié — il reste
   piloté ici, indexé par `ordre` (CHOIX EXÉCUTANT). */
export const CARTES_ACCUEIL = {
  kicker: "Nos prestations",
  title: "Ce que nous faisons pour vos cheveux",
  ctaLabel: "Toute la grille des tarifs",
  tags: ["Signature", "Femmes", "Hommes", "Mariage", "Bien-être"],
  items: [
    {
      categorie: "Signature",
      nom: "Coloration végétale Marcapar",
      texte:
        "Des pigments 100 % végétaux qui respectent le cuir chevelu et la fibre. Une, deux ou trois applications selon le résultat recherché, après diagnostic.",
      prix: "à partir de 40 €",
      duree: "≈ 1 h 30 (durée Planity)",
      vedette: true,
    },
    {
      categorie: "Femmes",
      nom: "Coupe & brushing",
      texte: "Coupe visagiste personnalisée, shampooing et brushing — le soin est offert.",
      prix: "36 € à 50 €",
      duree: "≈ 30 min (durée Planity)",
      vedette: false,
    },
    {
      categorie: "Hommes",
      nom: "Coupe homme",
      texte: "Coupe ciseaux ou tondeuse, au salon sans chichis.",
      prix: "13 € à 25 €",
      duree: "≈ 30 min (durée Planity)",
      vedette: false,
    },
    {
      categorie: "Mariage",
      nom: "Coiffure de mariage",
      texte:
        "Chignon bohème ou romantique, tresses, coiffage naturel — essais mentionnés sur le site ; maquillage sur consultation.",
      prix: "sur consultation",
      duree: "", // NON TROUVÉ — à confirmer par le client (brief, tableau A)
      vedette: false,
    },
    {
      categorie: "Bien-être",
      nom: "Yoga du visage",
      texte: "Un moment de détente et de tonus pour le visage, en 10, 20 ou 30 minutes.",
      prix: "15 € à 30 €",
      duree: "10 à 30 min",
      vedette: false,
    },
  ],
};

/* Tableau B du brief — grille tarifaire VERBATIM du site (juillet 2026).
   L'annotation de groupe « (soin offert) » est portée par le label
   (TarifsListe n'a pas de champ de note de groupe — CHOIX EXÉCUTANT). */
export const TARIFS = {
  title: "Nos tarifs",
  note: "Le soin est offert avec le shampooing, la coupe et le brushing. Prix TTC affichés en salon — les prestations techniques sont ajustées après diagnostic.",
  groups: [
    {
      label: "Shampooing / Brushing (soin offert)",
      items: [
        { name: "Cheveux courts", price: "24 € à 26 €" },
        { name: "Cheveux mi-longs", price: "26 € à 30 €" },
        { name: "Cheveux longs", price: "30 € à 45 €" },
        { name: "Supplément boucles au fer", price: "6 €" },
      ],
    },
    {
      label: "Shampooing / Coupe / Brushing — Femmes (soin offert)",
      items: [
        { name: "Coupe cheveux courts", price: "36 € à 38 €" },
        { name: "Coupe cheveux mi-longs", price: "38 € à 40 €" },
        { name: "Coupe cheveux longs", price: "40 € à 50 €" },
      ],
    },
    {
      label: "Étudiantes",
      items: [
        { name: "Cheveux courts", price: "26 €" },
        { name: "Cheveux mi-longs", price: "28 € à 30 €" },
        { name: "Cheveux longs", price: "30 € à 35 €" },
      ],
    },
    {
      label: "Adolescentes (moins de 16 ans)",
      items: [{ name: "Forfait", price: "20 € à 25 €", detail: "shampooing + coupe + brushing, soin offert" }],
    },
    {
      label: "Enfants",
      items: [
        { name: "Moins de 10 ans", price: "16 €" },
        { name: "Moins de 3 ans", price: "12 €" },
      ],
    },
    {
      label: "Hommes",
      items: [
        { name: "Coupe ciseaux", price: "25 €" },
        { name: "Étudiant", price: "19 €" },
        { name: "Coupe tondeuse", price: "13 €" },
      ],
    },
    {
      label: "Techniques — Couleur",
      items: [
        { name: "Sans ammoniaque ou ton sur ton", price: "34 €" },
        { name: "Décoloration", price: "à partir de 35 €" },
        { name: "Supplément par 10 g", price: "2 €" },
      ],
    },
    {
      label: "Techniques — Patine",
      items: [
        { name: "Cheveux courts", price: "20 €" },
        { name: "Cheveux longs", price: "25 € à 30 €" },
      ],
    },
    {
      label: "Techniques — Balayage",
      items: [
        { name: "Cheveux courts", price: "20 € à 45 €" },
        { name: "Cheveux mi-longs", price: "45 € à 70 €" },
        { name: "Cheveux longs", price: "70 € à 110 €" },
      ],
    },
    {
      label: "Techniques — Transformation",
      items: [{ name: "Coupe transformation", price: "45 € à 55 €", detail: "soin compris" }],
    },
    {
      label: "La couleur végétale Marcapar",
      items: [
        {
          name: "Soin du cuir chevelu (huile apaisante, rafraîchissante ou stimulante + massage + masque à l'argile)",
          price: "25 € à 30 €",
        },
        { name: "Coloration végétale 1 application", price: "à partir de 40 €", vedette: true },
        { name: "2 applications", price: "à partir de 56 €" },
        { name: "3 applications ou plus", price: "à partir de 68 €" },
        { name: "Sur cheveux longs (base 60 g), supplément par 10 g", price: "2 €" },
        { name: "Lait végétal", price: "25 € à 30 €" },
      ],
    },
    {
      label: "Épilation au fil",
      items: [
        { name: "Sourcils", price: "15 €" },
        { name: "Dessus de la bouche", price: "10 €" },
        { name: "Sourcils + dessus de la bouche", price: "20 €" },
      ],
    },
    {
      label: "Maquillage",
      items: [{ name: "Maquillage de mariage et de soirée", price: "Nous consulter" }],
    },
    {
      label: "Yoga du visage",
      items: [
        { name: "10 min", price: "15 €" },
        { name: "20 min", price: "20 €" },
        { name: "30 min", price: "30 €" },
      ],
    },
  ],
};

/* Ordre de référence des groupes tarifaires (ordre du tableau B) — les groupes
   inconnus créés depuis le back-office s'ajoutent à la fin. */
export const TARIF_GROUPES_ORDRE = TARIFS.groups.map((g) => g.label);

export const PORTRAIT = {
  name: "Paola Sonza",
  role: "Fondatrice — coiffeuse visagiste",
  bio: "Dans son salon du quartier des Antiquaires, Paola pratique une coiffure de conseil : coupes visagistes, colorations 100 % végétales Marcapar, balayages à l'argile blanche et coiffures de mariage. Le décor est chiné, l'accueil attentionné, et les engagements concrets : les cheveux coupés sont donnés à Solid'Hair pour la confection de perruques, et le salon recycle avec Coiffeurs Justes.",
  signature: "Paola",
  // Portrait NON TROUVÉ — à fournir par la cliente ; photo du salon en attendant (brief S5).
  image: "https://www.latelier-de-paola.com/media/images/upload/1000060923.jpg",
  imageAlt: "Paola dans son salon, Dijon",
};

export const SALON = {
  titre: "Le salon",
  images: [
    {
      src: "https://www.latelier-de-paola.com/media/images/upload/1000060923.jpg",
      legende: "L'Atelier de Paola — 93 rue Jean-Jacques Rousseau, Dijon",
    },
    { src: "https://www.latelier-de-paola.com/media/images/upload/1000060924.jpg", legende: "Le salon" },
    {
      src: "https://www.latelier-de-paola.com/media/images/upload/eab400ec-c0b3-4272-b2e4-35f29508ffe5-1-all-70534.jpg",
      legende: "L'esprit brocante chic",
    },
    {
      src: "https://www.latelier-de-paola.com/media/images/upload/thumbnail-1000035009.webp",
      legende: "Le yoga du visage",
    },
  ],
};

export const MARQUES = {
  titre: "Nos marques & nos engagements",
  // Logos images NON TROUVÉS — mode texte en attendant (brief S7 / §6.8).
  logos: [
    { texte: "Marcapar" },
    { texte: "Sublimo" },
    { texte: "Chromalya" },
    { texte: "Umaï" },
    { texte: "Comme Avant" },
    { texte: "Solid'Hair" },
    { texte: "Coiffeurs Justes" },
  ],
};

export const CTA_FINAL = {
  title: "Prenez rendez-vous",
  texte: "Réservez en ligne en deux minutes, ou appelez-nous : nous prendrons le temps de vous conseiller.",
  ctaLabel: "Réserver sur Planity",
  telephone: "03 80 67 17 23",
  note: "Mardi 9 h 30 – 18 h · Mercredi–Vendredi 9 h – 18 h · Samedi 9 h – 17 h",
};

export const CONTACT = {
  titre: "Contact", // libellé de l'ancre de navigation (h2 de section — CHOIX EXÉCUTANT)
  intro: "Une question, un projet de mariage, un conseil couleur ? Écrivez-nous, nous vous répondons vite.",
  confirmation: "Merci ! Nous revenons vers vous très vite.",
};

export const FOOTER = {
  nom: "L'Atelier de Paola",
  description:
    "Salon de coiffure visagiste au cœur du quartier des Antiquaires — coupes, colorations végétales, mariage.",
  adresse: "93 rue Jean-Jacques Rousseau, 21000 Dijon",
  telephone: "03 80 67 17 23",
  email: "contact@latelier-de-paola.com",
  horaires: [
    { jours: "Mardi", heures: "9 h 30 – 18 h" },
    { jours: "Mercredi – Vendredi", heures: "9 h – 18 h" },
    { jours: "Samedi", heures: "9 h – 17 h" },
    { jours: "Dimanche – Lundi", heures: "Fermé" },
  ],
  liens: [
    { label: "Prestations", href: "#prestations" },
    { label: "Tarifs", href: "#tarifs" },
    { label: "Le salon", href: "#salon" },
    { label: "Prendre RDV", href: PLANITY_URL },
  ],
  legaux: [
    { label: "Mentions légales", href: "/mentions-legales" },
    { label: "Politique de confidentialité", href: "/confidentialite" },
  ],
  copyright: "© 2026 L'Atelier de Paola — SIRET 438 004 681 00013",
};

/* ————— Données initiales des entités (brief §4) — consommées par scripts/seed.mjs ————— */

export const SITE_CONFIG_SEED = {
  nom: "L'Atelier de Paola",
  slogan: "Coiffeur visagiste, conseil en image, coiffure mariage — Dijon",
  description:
    "Salon de coiffure visagiste au cœur du quartier des Antiquaires : coupes, colorations végétales Marcapar, coiffures de mariage.",
  adresse: "93 rue Jean-Jacques Rousseau, 21000 Dijon",
  telephone: "03 80 67 17 23",
  email: "contact@latelier-de-paola.com",
  horaires: "Mardi 9h30–18h · Mercredi–Vendredi 9h–18h · Samedi 9h–17h",
  instagram: "https://www.instagram.com/sonzapaola/",
  facebook: "https://www.facebook.com/latelier.depaola",
  url_rdv: PLANITY_URL,
  siret: "43800468100013",
  tva: "FR63438004681",
  url_source: "https://www.latelier-de-paola.com",
};

export const TEMOIGNAGES_SEED = [
  {
    auteur: "Avis client vérifié — Planity",
    texte: "Moment très agréable mené avec compétence et gentillesse.",
    note: 5,
    source: "Planity",
    date: "2026-07-16",
  },
  {
    auteur: "Avis client vérifié — Planity",
    texte: "Première visite et je suis enchantée de ma coupe. Très bonne surprise.",
    note: 5,
    source: "Planity",
    date: "2026-06-26",
  },
];

/* Prestations : les 5 cartes d'accueil (categorie "carte-accueil", ordre 1–5)
   + toutes les lignes du tableau B (categorie = label du groupe, ordre = position
   dans le groupe, prix verbatim, detail → description). */
export const PRESTATIONS_SEED = [
  ...CARTES_ACCUEIL.items.map((item, i) => ({
    nom: item.nom,
    description: item.texte,
    prix: item.prix,
    duree: item.duree,
    categorie: "carte-accueil",
    vedette: item.vedette,
    ordre: i + 1,
    visible: true,
  })),
  ...TARIFS.groups.flatMap((group) =>
    group.items.map((item, i) => ({
      nom: item.name,
      description: item.detail || "",
      prix: item.price,
      duree: "",
      categorie: group.label,
      vedette: Boolean(item.vedette), // vedette=true sur « Coloration végétale 1 application » (brief §4.2)
      ordre: i + 1,
      visible: true,
    }))
  ),
];

/* SectionContenu (brief §4.4) — mapping des champs :
   hero : badge→sous_titre, title→titre, subtitle→texte (mapping imposé par le brief) ;
   pour les autres clés (CHOIX EXÉCUTANT, documenté) : kicker/role/note/confirmation/copyright→sous_titre,
   texte principal→texte, légende de photo→texte de salon_N. */
export const SECTIONS_SEED = [
  { cle: "hero", titre: HERO.title, sous_titre: HERO.badge, texte: HERO.subtitle },
  { cle: "note_globale", texte: NOTE_GLOBALE.mention },
  { cle: "prestations", titre: CARTES_ACCUEIL.title, sous_titre: CARTES_ACCUEIL.kicker },
  { cle: "tarifs", titre: TARIFS.title, texte: TARIFS.note },
  {
    cle: "apropos",
    titre: PORTRAIT.name,
    sous_titre: PORTRAIT.role,
    texte: PORTRAIT.bio,
    image_url: PORTRAIT.image,
  },
  { cle: "salon", titre: SALON.titre },
  ...SALON.images.map((img, i) => ({ cle: `salon_${i + 1}`, texte: img.legende, image_url: img.src })),
  { cle: "marques", titre: MARQUES.titre },
  { cle: "cta_final", titre: CTA_FINAL.title, texte: CTA_FINAL.texte, sous_titre: CTA_FINAL.note },
  { cle: "contact", titre: CONTACT.titre, texte: CONTACT.intro, sous_titre: CONTACT.confirmation },
  { cle: "footer", texte: FOOTER.description, sous_titre: FOOTER.copyright },
];
