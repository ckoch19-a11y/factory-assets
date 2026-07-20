/**
 * @library cta/BandeauRdv
 * @description Bandeau de conversion final plein cadre, matiéré (grain + halo embarqués) — rupture de registre assumée en page éditoriale (cf. ASSEMBLAGE §1). Double action : bouton principal + téléphone cliquable. Entrée orchestrée au scroll.
 * @registers editorial, premium
 * @deps framer-motion
 * @props register? · title? · texte? · ctaLabel? · onCta? · telephone?: "03 80 00 00 00" · note?
 * @weight ~1.5 KB gz
 * Écrit maison pour l'usine.
 */
import React from "react";
import { motion, useReducedMotion } from "framer-motion";

const GRAIN =
  "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/><feColorMatrix type='saturate' values='0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)' opacity='0.5'/></svg>\")";

const T = {
  editorial: {
    section: "bg-[#1C1917] text-[#F7F1E8]",
    halo: "bg-[radial-gradient(50%_60%_at_70%_20%,rgba(217,119,6,0.25),transparent)]",
    serif: { fontFamily: "Georgia, 'Times New Roman', serif" },
    texte: "text-[#D6D3D1]",
    cta: "rounded-full bg-[#F7F1E8] text-[#1C1917] hover:bg-white",
    tel: "border border-[#F7F1E8]/25 rounded-full hover:bg-white/5 text-[#F7F1E8]",
    note: "text-[#A8A29E]",
  },
  premium: {
    section: "bg-[#0B0B10] text-white",
    halo: "bg-[radial-gradient(50%_60%_at_50%_0%,rgba(99,102,241,0.3),transparent)]",
    serif: {},
    texte: "text-zinc-400",
    cta: "rounded-xl bg-gradient-to-r from-indigo-500 to-violet-500 text-white hover:opacity-90",
    tel: "border border-white/15 rounded-xl hover:bg-white/5 text-zinc-200",
    note: "text-zinc-600",
  },
};

export default function BandeauRdv({
  register = "editorial",
  title = "Prêt·e à prendre rendez-vous ?",
  texte = "Texte de démonstration : une phrase qui lève la dernière hésitation, sans pression.",
  ctaLabel = "Réserver en ligne",
  onCta,
  telephone = "03 80 00 00 00",
  note = "Démo — réponse sous 24 h ouvrées",
}) {
  const t = T[register] || T.editorial;
  const reduced = useReducedMotion();
  const anim = (delay) =>
    reduced ? { initial: false } : {
      initial: { opacity: 0, y: 22 },
      whileInView: { opacity: 1, y: 0 },
      viewport: { once: true, amount: 0.4 },
      transition: { duration: 0.55, delay, ease: [0.22, 1, 0.36, 1] },
    };

  return (
    <section aria-label="Prendre rendez-vous" className={"relative overflow-hidden py-28 px-6 " + t.section}>
      <div aria-hidden="true" className={"absolute inset-0 " + t.halo} />
      <div aria-hidden="true" className="absolute inset-0 pointer-events-none" style={{ backgroundImage: GRAIN, opacity: 0.06 }} />
      <div className="relative max-w-3xl mx-auto text-center">
        <motion.h2 {...anim(0)} className="text-4xl md:text-6xl tracking-tight" style={t.serif}>
          {title}
        </motion.h2>
        <motion.p {...anim(0.08)} className={"mt-5 text-lg leading-relaxed " + t.texte}>
          {texte}
        </motion.p>
        <motion.div {...anim(0.16)} className="mt-10 flex flex-wrap gap-3 justify-center">
          <button onClick={onCta} className={"px-8 py-4 text-sm font-medium transition-all " + t.cta}>
            {ctaLabel}
          </button>
          {telephone && (
            <a href={"tel:" + telephone.replace(/\s/g, "")} className={"px-8 py-4 text-sm font-medium transition-colors " + t.tel}>
              {telephone}
            </a>
          )}
        </motion.div>
        {note && (
          <motion.p {...anim(0.24)} className={"mt-8 text-[11px] uppercase tracking-[0.25em] " + t.note}>
            {note}
          </motion.p>
        )}
      </div>
    </section>
  );
}
