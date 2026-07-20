/**
 * @library footers/FooterMaison
 * @description Footer complet 4 colonnes : identité + coordonnées cliquables (tel/mail/adresse), horaires, navigation, liens légaux obligatoires (mentions, confidentialité, cookies). Filet lumineux en tête. Landmark footer, nav secondaire étiquetée.
 * @registers editorial, premium
 * @deps aucune
 * @props register? · nom? · description? · adresse? · telephone? · email? · horaires?: [{jours, heures}] · liens?: [{label, href}] · legaux?: [{label, href}] · copyright?
 * @weight ~1.3 KB gz
 * Écrit maison pour l'usine.
 */
import React from "react";

const T = {
  editorial: {
    footer: "bg-[#1C1917] text-[#D6D3D1]",
    filet: "bg-gradient-to-r from-transparent via-[#C9B28E] to-transparent",
    titre: "text-[#F7F1E8]",
    serif: { fontFamily: "Georgia, 'Times New Roman', serif" },
    label: "text-[#A8A29E]",
    lien: "hover:text-[#F7F1E8]",
    bas: "border-t border-white/10 text-[#78716C]",
  },
  premium: {
    footer: "bg-[#080810] text-zinc-400",
    filet: "bg-gradient-to-r from-transparent via-indigo-400/60 to-transparent",
    titre: "text-white",
    serif: {},
    label: "text-zinc-500",
    lien: "hover:text-white",
    bas: "border-t border-white/10 text-zinc-600",
  },
};

const DEMO = {
  horaires: [
    { jours: "Mardi — Vendredi", heures: "9 h – 19 h" },
    { jours: "Samedi", heures: "9 h – 17 h" },
    { jours: "Dimanche — Lundi", heures: "Fermé" },
  ],
  liens: [
    { label: "Prestations", href: "#" },
    { label: "Réalisations", href: "#" },
    { label: "L'équipe", href: "#" },
    { label: "Contact", href: "#" },
  ],
  legaux: [
    { label: "Mentions légales", href: "#" },
    { label: "Confidentialité", href: "#" },
    { label: "Cookies", href: "#" },
  ],
};

export default function FooterMaison({
  register = "editorial",
  nom = "Nom de l'enseigne",
  description = "Description de démonstration : une phrase qui situe l'activité et la ville.",
  adresse = "12 rue de Démo, 21000 Dijon",
  telephone = "03 80 00 00 00",
  email = "contact@exemple.fr",
  horaires = DEMO.horaires,
  liens = DEMO.liens,
  legaux = DEMO.legaux,
  copyright,
}) {
  const t = T[register] || T.editorial;
  const annee = new Date().getFullYear();

  return (
    <footer className={"relative " + t.footer}>
      <div aria-hidden="true" className={"h-px w-full " + t.filet} />
      <div className="max-w-6xl mx-auto px-6 py-16 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-10">
        <div>
          <p className={"text-xl mb-3 " + t.titre} style={t.serif}>{nom}</p>
          <p className="text-sm leading-relaxed">{description}</p>
        </div>

        <div>
          <p className={"font-mono text-[11px] tracking-[0.2em] uppercase mb-4 " + t.label}>Contact</p>
          <ul className="space-y-2.5 text-sm">
            <li>{adresse}</li>
            <li><a className={"transition-colors " + t.lien} href={"tel:" + telephone.replace(/\s/g, "")}>{telephone}</a></li>
            <li><a className={"transition-colors " + t.lien} href={"mailto:" + email}>{email}</a></li>
          </ul>
        </div>

        <div>
          <p className={"font-mono text-[11px] tracking-[0.2em] uppercase mb-4 " + t.label}>Horaires</p>
          <ul className="space-y-2.5 text-sm">
            {horaires.map((h, i) => (
              <li key={i} className="flex justify-between gap-4">
                <span>{h.jours}</span>
                <span className={t.label}>{h.heures}</span>
              </li>
            ))}
          </ul>
        </div>

        <nav aria-label="Navigation de pied de page">
          <p className={"font-mono text-[11px] tracking-[0.2em] uppercase mb-4 " + t.label}>Navigation</p>
          <ul className="space-y-2.5 text-sm">
            {liens.map((l, i) => (
              <li key={i}><a className={"transition-colors " + t.lien} href={l.href}>{l.label}</a></li>
            ))}
          </ul>
        </nav>
      </div>

      <div className={"px-6 py-6 " + t.bas}>
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
          <p>{copyright || `© ${annee} ${nom} — Tous droits réservés`}</p>
          <ul className="flex gap-5">
            {legaux.map((l, i) => (
              <li key={i}><a className={"transition-colors " + t.lien} href={l.href}>{l.label}</a></li>
            ))}
          </ul>
        </div>
      </div>
    </footer>
  );
}
