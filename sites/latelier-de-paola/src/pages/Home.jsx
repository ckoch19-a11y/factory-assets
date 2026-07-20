import React, { useState } from "react";
import NavbarLisible from "@/components/library/navigation/NavbarLisible";
import MenuOverlay from "@/components/library/navigation/MenuOverlay";
import ProgressionScroll from "@/components/library/navigation/ProgressionScroll";
import CurseurEtiquette from "@/components/library/effets/CurseurEtiquette";
import HeroHalo from "@/components/library/heros/HeroHalo";
import NoteGlobale from "@/components/library/avis/NoteGlobale";
import CartesPrestations from "@/components/library/prestations/CartesPrestations";
import TarifsListe from "@/components/library/prestations/TarifsListe";
import PontCourbe from "@/components/library/transitions/PontCourbe";
import PortraitEditorial from "@/components/library/equipe/PortraitEditorial";
import DefileHorizontal from "@/components/library/galeries/DefileHorizontal";
import BandeauLogos from "@/components/library/avis/BandeauLogos";
import PontFondu from "@/components/library/transitions/PontFondu";
import BandeauRdv from "@/components/library/cta/BandeauRdv";
import FooterMaison from "@/components/library/footers/FooterMaison";
import FormulaireContact from "@/components/vitrine/FormulaireContact";
import { usePrestations, useSection, useSections, useSiteConfig } from "@/hooks/useContenu";
import * as F from "@/content/fallbacks";

/* Accueil — plan du brief §3, dans l'ordre :
   hero → note globale → cartes prestations → tarifs (+PontCourbe) → portrait →
   galerie salon → bandeau marques (+PontFondu) → bandeau RDV (seule rupture) →
   formulaire de contact → footer. Registre editorial partout.
   Le contenu vient des entités (hooks) avec fallback intégral du brief. */

/* Les 5 cartes d'accueil (entité Prestation, categorie "carte-accueil").
   Le tag affiché (Signature, Femmes…) n'a pas de champ dédié dans l'entité
   (brief §4.2) : il vient du fallback, indexé par ordre — CHOIX EXÉCUTANT. */
function cartesAccueil(prestations) {
  const cartes = prestations
    .filter((p) => p.categorie === "carte-accueil" && p.visible !== false)
    .sort((a, b) => (a.ordre ?? 0) - (b.ordre ?? 0));
  if (!cartes.length) return F.CARTES_ACCUEIL.items;
  return cartes.map((p, i) => ({
    categorie: F.CARTES_ACCUEIL.tags[(p.ordre ?? i + 1) - 1] || "",
    nom: p.nom,
    texte: p.description,
    prix: p.prix,
    duree: p.duree,
    vedette: p.vedette === true,
  }));
}

/* La grille tarifaire (entité Prestation, categorie = label de groupe du tableau B),
   groupée par categorie dans l'ordre de référence du brief. */
function grouperTarifs(prestations) {
  const lignes = prestations.filter((p) => p.categorie !== "carte-accueil" && p.visible !== false);
  if (!lignes.length) return F.TARIFS.groups;
  const parGroupe = new Map();
  for (const p of lignes) {
    if (!parGroupe.has(p.categorie)) parGroupe.set(p.categorie, []);
    parGroupe.get(p.categorie).push(p);
  }
  const rang = (label) => {
    const i = F.TARIF_GROUPES_ORDRE.indexOf(label);
    return i === -1 ? Number.MAX_SAFE_INTEGER : i;
  };
  return [...parGroupe.keys()]
    .sort((a, b) => rang(a) - rang(b))
    .map((label) => ({
      label,
      items: parGroupe
        .get(label)
        .sort((a, b) => (a.ordre ?? 0) - (b.ordre ?? 0))
        .map((p) => ({ name: p.nom, price: p.prix, detail: p.description || undefined })),
    }));
}

export default function Home() {
  const [menuOuvert, setMenuOuvert] = useState(false);
  const { data: config } = useSiteConfig();
  const { data: prestations } = usePrestations();

  const hero = useSection("hero", { titre: F.HERO.title, sous_titre: F.HERO.badge, texte: F.HERO.subtitle });
  const noteGlobale = useSection("note_globale", { texte: F.NOTE_GLOBALE.mention });
  const secPrestations = useSection("prestations", {
    titre: F.CARTES_ACCUEIL.title,
    sous_titre: F.CARTES_ACCUEIL.kicker,
  });
  const secTarifs = useSection("tarifs", { titre: F.TARIFS.title, texte: F.TARIFS.note });
  const apropos = useSection("apropos", {
    titre: F.PORTRAIT.name,
    sous_titre: F.PORTRAIT.role,
    texte: F.PORTRAIT.bio,
    image_url: F.PORTRAIT.image,
  });
  const secSalon = useSection("salon", { titre: F.SALON.titre });
  const { data: sectionsData } = useSections();
  const salonEntites = (Array.isArray(sectionsData) ? sectionsData : [])
    .filter((s) => /^salon_\d+$/.test(s.cle) && s.visible !== false && s.image_url)
    .sort((a, b) => Number(a.cle.slice(6)) - Number(b.cle.slice(6)))
    .map((s) => ({ src: s.image_url, legende: s.texte }));
  const salonImages = salonEntites.length ? salonEntites : F.SALON.images;
  const secMarques = useSection("marques", { titre: F.MARQUES.titre });
  const ctaFinal = useSection("cta_final", {
    titre: F.CTA_FINAL.title,
    texte: F.CTA_FINAL.texte,
    sous_titre: F.CTA_FINAL.note,
  });
  const secContact = useSection("contact", {
    titre: F.CONTACT.titre,
    texte: F.CONTACT.intro,
    sous_titre: F.CONTACT.confirmation,
  });
  const secFooter = useSection("footer", { texte: F.FOOTER.description, sous_titre: F.FOOTER.copyright });

  const urlRdv = config.url_rdv || F.PLANITY_URL;
  const telephone = config.telephone || F.NAV.contact.telephone;
  const ouvrirRdv = () => window.open(urlRdv, "_blank", "noopener,noreferrer");
  const versTarifs = () => document.getElementById("tarifs")?.scrollIntoView();

  return (
    <>
      <NavbarLisible
        register="editorial"
        nom={config.nom || F.NAV.nom}
        liens={F.NAV.liens}
        ctaLabel={F.NAV.ctaLabel}
        onCta={ouvrirRdv}
        onMenuMobile={() => setMenuOuvert(true)}
      />
      <MenuOverlay
        register="editorial"
        open={menuOuvert}
        onClose={() => setMenuOuvert(false)}
        liens={F.NAV.liens}
        contact={{
          adresse: config.adresse || F.NAV.contact.adresse,
          telephone,
          email: config.email || F.NAV.contact.email,
        }}
      />
      <ProgressionScroll register="editorial" />
      <CurseurEtiquette register="editorial" />

      <main id="contenu">
        {/* S1 — Hero */}
        <HeroHalo
          register="editorial"
          badge={hero.sous_titre}
          title={hero.titre}
          subtitle={hero.texte}
          ctaPrimary={F.HERO.ctaPrimary}
          ctaSecondary={F.HERO.ctaSecondary}
          note={F.HERO.note}
          onPrimary={ouvrirRdv}
          onSecondary={versTarifs}
        />

        {/* S2 — Preuve : note agrégée Planity */}
        <NoteGlobale
          register="editorial"
          note={F.NOTE_GLOBALE.note}
          total={F.NOTE_GLOBALE.total}
          plateformes={F.NOTE_GLOBALE.plateformes}
          mention={noteGlobale.texte}
        />

        {/* S3 — Offre : cartes prestations (ancre #prestations).
            data-cursor : cible du CurseurEtiquette (brief, composants transverses). */}
        <div id="prestations" data-cursor="Voir les tarifs">
          <CartesPrestations
            register="editorial"
            kicker={secPrestations.sous_titre}
            title={secPrestations.titre}
            items={cartesAccueil(prestations)}
            ctaLabel={F.CARTES_ACCUEIL.ctaLabel}
            onCta={versTarifs}
          />
        </div>

        {/* S4 — Offre : grille tarifaire verbatim (ancre #tarifs).
            PontCourbe ferme la section (overlay bas) vers le fond de S5 (#F7F1E8,
            token embarqué de PortraitEditorial — relevé après copie, cf. brief). */}
        <div id="tarifs" className="relative">
          <TarifsListe
            register="editorial"
            title={secTarifs.titre}
            note={secTarifs.texte}
            groups={grouperTarifs(prestations)}
          />
          <PontCourbe to="#F7F1E8" variant="vague" height={80} />
        </div>

        {/* S5 — Confiance : portrait de la fondatrice */}
        <PortraitEditorial
          register="editorial"
          name={apropos.titre}
          role={apropos.sous_titre}
          bio={apropos.texte}
          image={apropos.image_url}
          imageAlt={F.PORTRAIT.imageAlt}
          signature={F.PORTRAIT.signature}
        />

        {/* S6 — Confiance : galerie du salon (ancre #salon) */}
        <div id="salon" data-cursor="Le salon">
          <DefileHorizontal register="editorial" title={secSalon.titre} images={salonImages} />
        </div>

        {/* S7 — Confiance : marques & engagements (mode texte — logos NON TROUVÉS).
            PontFondu ferme la section vers le fond du BandeauRdv (#1C1917, token
            embarqué relevé après copie), fil doré éditorial. */}
        <div className="relative">
          <BandeauLogos register="editorial" titre={secMarques.titre} logos={F.MARQUES.logos} />
          <PontFondu to="#1C1917" register="editorial" height={120} filet />
        </div>

        {/* S8 — Conversion : bandeau RDV (seule rupture de registre de la page) */}
        <BandeauRdv
          register="editorial"
          title={ctaFinal.titre}
          texte={ctaFinal.texte}
          ctaLabel={F.CTA_FINAL.ctaLabel}
          onCta={ouvrirRdv}
          telephone={telephone}
          note={ctaFinal.sous_titre}
        />

        {/* S9 — Conversion : formulaire de contact (ancre #contact) */}
        <section id="contact" aria-label="Formulaire de contact" className="bg-background py-section px-6">
          <div className="max-w-canvas mx-auto">
            <h2 className="text-display-md text-center">{secContact.titre}</h2>
            <div className="mt-8">
              <FormulaireContact intro={secContact.texte} confirmation={secContact.sous_titre} telephone={telephone} />
            </div>
          </div>
        </section>
      </main>

      {/* S10 — Footer */}
      <FooterMaison
        register="editorial"
        nom={config.nom || F.FOOTER.nom}
        description={secFooter.texte}
        adresse={config.adresse || F.FOOTER.adresse}
        telephone={telephone}
        email={config.email || F.FOOTER.email}
        horaires={F.FOOTER.horaires}
        liens={F.FOOTER.liens}
        legaux={F.FOOTER.legaux}
        copyright={secFooter.sous_titre}
      />
    </>
  );
}
