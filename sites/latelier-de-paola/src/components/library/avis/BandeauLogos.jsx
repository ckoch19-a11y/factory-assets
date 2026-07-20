/**
 * @library avis/BandeauLogos
 * @description Bandeau de logos partenaires/labels en défilement continu, fondu aux bords, pause au survol — la preuve sociale silencieuse (assureurs, marques, certifications RGE/Qualibat…). Accepte images ou texte. Reduced-motion : rangée statique.
 * @registers editorial, premium
 * @deps framer-motion
 * @props register? · titre?: "Ils nous font confiance" · logos: [{src?, alt?, texte?}] · vitesse?: 30 (s/boucle) · hauteur?: 32 (px logos)
 * @weight ~0.9 KB gz
 * Écrit maison pour l'usine (pattern marquee framer, sans lib).
 */
import React from "react";
import { motion, useReducedMotion } from "framer-motion";

const T = {
  editorial: { section: "bg-[#F7F1E8]", titre: "text-[#78716C]", texte: "text-[#44403C]", filtre: "grayscale opacity-60 hover:opacity-100 hover:grayscale-0" },
  premium: { section: "bg-[#0B0B10]", titre: "text-zinc-600", texte: "text-zinc-400", filtre: "grayscale opacity-50 invert hover:opacity-90" },
};

const DEMO_LOGOS = [
  { texte: "Partenaire Démo" }, { texte: "Label Démo" }, { texte: "Certification Démo" },
  { texte: "Marque Démo" }, { texte: "Réseau Démo" }, { texte: "Garantie Démo" },
];

function Logo({ logo, t, hauteur }) {
  return (
    <div className="flex items-center shrink-0 px-8">
      {logo.src ? (
        <img src={logo.src} alt={logo.alt || ""} loading="lazy" style={{ height: hauteur }} className={"w-auto transition-all duration-300 " + t.filtre} />
      ) : (
        <span className={"text-sm font-medium tracking-wide whitespace-nowrap " + t.texte}>{logo.texte}</span>
      )}
    </div>
  );
}

export default function BandeauLogos({
  register = "editorial", titre = "Ils nous font confiance — Démo",
  logos = DEMO_LOGOS, vitesse = 30, hauteur = 32,
}) {
  const t = T[register] || T.editorial;
  const reduced = useReducedMotion();
  const doubled = [...logos, ...logos];

  return (
    <section aria-label="Partenaires et labels" className={"py-12 " + t.section}>
      {titre && <p className={"text-center font-mono text-[11px] tracking-[0.25em] uppercase mb-7 " + t.titre}>{titre}</p>}
      {reduced ? (
        <div className="flex flex-wrap justify-center gap-y-4 max-w-5xl mx-auto px-6">
          {logos.map((l, i) => <Logo key={i} logo={l} t={t} hauteur={hauteur} />)}
        </div>
      ) : (
        <div
          className="overflow-hidden group"
          style={{ maskImage: "linear-gradient(to right, transparent, #000 12%, #000 88%, transparent)", WebkitMaskImage: "linear-gradient(to right, transparent, #000 12%, #000 88%, transparent)" }}
        >
          <motion.div
            className="flex w-max items-center"
            animate={{ x: ["0%", "-50%"] }}
            transition={{ duration: vitesse, repeat: Infinity, ease: "linear" }}
          >
            {doubled.map((l, i) => <Logo key={i} logo={l} t={t} hauteur={hauteur} />)}
          </motion.div>
        </div>
      )}
    </section>
  );
}
