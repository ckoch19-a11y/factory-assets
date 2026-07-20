/**
 * @library prestations/CartesPrestations
 * @description Grille de prestations avec carte vedette asymétrique (2 colonnes, fond inversé) — jamais quatre rectangles identiques. Prix, durée, badge « Démo » sur placeholders. Entrées en cascade au scroll.
 * @registers editorial, premium
 * @deps framer-motion
 * @props register? · kicker? · title? · items: [{categorie, nom, texte, prix, duree, vedette?, demo?}] · ctaLabel? · onCta?
 * @weight ~1.8 KB gz
 * Écrit maison pour l'usine — figure « vedette + satellites » (ASSEMBLAGE §2 : varier les figures).
 */
import React from "react";
import { motion, useReducedMotion } from "framer-motion";

const T = {
  editorial: {
    section: "bg-[#F7F1E8] text-[#1C1917]",
    kicker: "text-[#9A3412]",
    title: "text-[#1C1917]",
    serif: { fontFamily: "Georgia, 'Times New Roman', serif" },
    card: "bg-[#FFFBF4] border border-[#E5D9C6]",
    cardVedette: "bg-[#1C1917] text-[#F7F1E8] border border-[#1C1917]",
    cat: "text-[#9A3412]", catVedette: "text-[#E8C39A]",
    texte: "text-[#44403C]", texteVedette: "text-[#D6D3D1]",
    prix: "text-[#1C1917]", prixVedette: "text-[#F7F1E8]",
    duree: "text-[#78716C]", dureeVedette: "text-[#A8A29E]",
    badge: "bg-[#EFE6D8] text-[#78716C]", badgeVedette: "bg-white/10 text-[#D6D3D1]",
    cta: "rounded-full bg-[#1C1917] text-[#F7F1E8] hover:bg-[#33302B]",
  },
  premium: {
    section: "bg-[#0B0B10] text-zinc-100",
    kicker: "text-indigo-300",
    title: "text-white",
    serif: {},
    card: "bg-white/[0.04] border border-white/10 backdrop-blur",
    cardVedette: "bg-gradient-to-br from-indigo-500/20 to-violet-500/10 text-white border border-indigo-400/30",
    cat: "text-indigo-300", catVedette: "text-indigo-200",
    texte: "text-zinc-400", texteVedette: "text-zinc-300",
    prix: "text-white", prixVedette: "text-white",
    duree: "text-zinc-500", dureeVedette: "text-zinc-400",
    badge: "bg-white/10 text-zinc-400", badgeVedette: "bg-white/15 text-zinc-200",
    cta: "rounded-xl bg-gradient-to-r from-indigo-500 to-violet-500 text-white hover:opacity-90",
  },
};

const DEMO_ITEMS = [
  { categorie: "Signature", nom: "Prestation vedette", texte: "La prestation phare, décrite en une phrase concrète qui donne envie.", prix: "75 €", duree: "1 h 30", vedette: true, demo: true },
  { categorie: "Essentiel", nom: "Prestation courante", texte: "Le geste du quotidien, sans surprise.", prix: "32 €", duree: "45 min", demo: true },
  { categorie: "Essentiel", nom: "Autre prestation", texte: "Une deuxième entrée de gamme claire.", prix: "28 €", duree: "30 min", demo: true },
  { categorie: "Option", nom: "Complément", texte: "Le petit plus qui accompagne.", prix: "15 €", duree: "15 min", demo: true },
];

export default function CartesPrestations({
  register = "editorial", kicker = "Prestations", title = "Des tarifs clairs, dès le premier regard",
  items = DEMO_ITEMS, ctaLabel = "Toutes les prestations", onCta,
}) {
  const t = T[register] || T.editorial;
  const reduced = useReducedMotion();
  const anim = (i) =>
    reduced ? { initial: false } : {
      initial: { opacity: 0, y: 28 },
      whileInView: { opacity: 1, y: 0 },
      viewport: { once: true, amount: 0.25 },
      transition: { duration: 0.55, delay: i * 0.07, ease: [0.22, 1, 0.36, 1] },
    };

  return (
    <section aria-label="Prestations et tarifs" className={"relative py-24 px-6 " + t.section}>
      <div className="max-w-6xl mx-auto">
        <p className={"font-mono text-xs tracking-[0.25em] uppercase mb-3 " + t.kicker}>{kicker}</p>
        <h2 className={"text-3xl md:text-5xl tracking-tight max-w-2xl mb-14 " + t.title} style={t.serif}>{title}</h2>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-5 items-stretch">
          {items.map((item, i) => (
            <motion.article
              key={i}
              {...anim(i)}
              className={
                "rounded-2xl p-7 flex flex-col justify-between min-h-[220px] " +
                (item.vedette ? "md:col-span-2 md:row-span-1 " + t.cardVedette : t.card)
              }
            >
              <div>
                <div className="flex items-center justify-between gap-3 mb-4">
                  <span className={"font-mono text-[11px] tracking-[0.2em] uppercase " + (item.vedette ? t.catVedette : t.cat)}>
                    {item.categorie}
                  </span>
                  {item.demo && (
                    <span className={"text-[10px] px-2.5 py-1 rounded-full uppercase tracking-wide " + (item.vedette ? t.badgeVedette : t.badge)}>
                      Démo
                    </span>
                  )}
                </div>
                <h3 className={"text-xl mb-2 " + (item.vedette ? "text-2xl md:text-3xl" : "")} style={item.vedette ? t.serif : undefined}>
                  {item.nom}
                </h3>
                <p className={"text-sm leading-relaxed " + (item.vedette ? t.texteVedette : t.texte)}>{item.texte}</p>
              </div>
              <div className="flex items-end justify-between mt-6">
                <span className={"text-2xl font-semibold " + (item.vedette ? t.prixVedette : t.prix)}>{item.prix}</span>
                <span className={"text-xs " + (item.vedette ? t.dureeVedette : t.duree)}>{item.duree}</span>
              </div>
            </motion.article>
          ))}
        </div>

        {ctaLabel && (
          <div className="mt-12 text-center">
            <button onClick={onCta} className={"px-7 py-3.5 text-sm font-medium transition-all " + t.cta}>
              {ctaLabel} →
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
