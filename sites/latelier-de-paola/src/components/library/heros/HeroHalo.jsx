/**
 * @library heros/HeroHalo
 * @description Hero plein écran à double registre — éditorial matiéré (crème, grain, serif, composition asymétrique) ou sombre premium (halos, verre dépoli, filet lumineux, centré). Badge, titre, sous-titre, double CTA, note.
 * @registers editorial, premium
 * @deps framer-motion
 * @props register?: "editorial"|"premium" · badge? · title? · subtitle? · ctaPrimary? · ctaSecondary? · note? · onPrimary?: fn · onSecondary?: fn
 * @weight ~2.5 KB gz
 */
import React from "react";
import { motion, useReducedMotion } from "framer-motion";

/* Tokens embarqués — aucune dépendance à l'usine, copiable tel quel. */
const GRAIN =
  "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/><feColorMatrix type='saturate' values='0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)' opacity='0.5'/></svg>\")";
const SERIF = { fontFamily: "Georgia, 'Times New Roman', serif" };

export default function HeroHalo({
  register = "premium",
  badge = "Démo — Ouvert du mardi au samedi",
  title = "Un savoir-faire qui se voit dès la première visite",
  subtitle = "Sous-titre de démonstration : une phrase claire qui dit la valeur, sans jargon.",
  ctaPrimary = "Prendre rendez-vous",
  ctaSecondary = "Découvrir",
  note = "Démo — remplacer par vos textes",
  onPrimary,
  onSecondary,
}) {
  const reduce = useReducedMotion();
  const anim = (delay = 0) =>
    reduce
      ? { initial: false }
      : {
          initial: { opacity: 0, y: 24 },
          animate: { opacity: 1, y: 0 },
          transition: { duration: 0.6, delay },
        };

  if (register === "editorial") {
    return (
      <section
        aria-label="Section d'ouverture"
        className="relative min-h-screen flex items-center overflow-hidden bg-[#F7F1E8] text-[#1C1917]"
      >
        <div
          aria-hidden="true"
          className="absolute inset-0 bg-[radial-gradient(55%_45%_at_72%_18%,rgba(217,119,6,0.16),transparent)]"
        />
        <div
          aria-hidden="true"
          className="absolute inset-0 pointer-events-none"
          style={{ backgroundImage: GRAIN, opacity: 0.07 }}
        />
        <div className="relative w-full max-w-6xl mx-auto px-6 py-24 grid grid-cols-1 md:grid-cols-12 gap-10 items-end">
          <div className="md:col-span-8">
            <motion.span
              {...anim(0)}
              className="inline-block px-4 py-1.5 rounded-full border border-[#1C1917]/20 text-xs tracking-wide text-[#78716C]"
            >
              {badge}
            </motion.span>
            <motion.h1
              {...anim(0.08)}
              style={SERIF}
              className="mt-6 text-5xl md:text-7xl leading-[1.02] tracking-tight"
            >
              {title}
            </motion.h1>
            <motion.div {...anim(0.16)} className="mt-8 flex flex-wrap gap-3">
              <button
                onClick={onPrimary}
                className="px-7 py-3.5 rounded-full bg-[#1C1917] text-[#F7F1E8] text-sm font-medium hover:bg-[#33302B] transition-colors"
              >
                {ctaPrimary}
              </button>
              <button
                onClick={onSecondary}
                className="px-7 py-3.5 rounded-full border border-[#1C1917]/25 text-sm hover:bg-[#1C1917]/5 transition-colors"
              >
                {ctaSecondary}
              </button>
            </motion.div>
          </div>
          {/* Colonne droite composée — jamais vide */}
          <motion.aside
            {...anim(0.22)}
            className="md:col-span-4 md:pl-6 md:border-l border-[#C9B28E]/50"
          >
            <p className="text-[#44403C] leading-relaxed">{subtitle}</p>
            <div className="mt-6 h-px bg-gradient-to-r from-[#C9B28E] to-transparent" />
            <p className="mt-4 text-xs uppercase tracking-[0.2em] text-[#9A3412]">{note}</p>
          </motion.aside>
        </div>
      </section>
    );
  }

  /* ===== Sombre premium ===== */
  return (
    <section
      aria-label="Section d'ouverture"
      className="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#0B0B10] text-zinc-100"
    >
      <div
        aria-hidden="true"
        className="absolute -top-44 left-1/2 -translate-x-1/2 w-[85vmin] h-[85vmin] rounded-full bg-indigo-500/20 blur-3xl"
      />
      <div
        aria-hidden="true"
        className="absolute bottom-[-30vmin] right-[-10vmin] w-[60vmin] h-[60vmin] rounded-full bg-cyan-400/10 blur-3xl"
      />
      <div
        aria-hidden="true"
        className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-indigo-400/70 to-transparent"
      />
      <div className="relative text-center px-6 max-w-3xl">
        <motion.span
          {...anim(0)}
          className="inline-block px-4 py-1.5 rounded-full bg-white/[0.06] backdrop-blur-md border border-white/10 text-xs text-zinc-300"
        >
          {badge}
        </motion.span>
        <motion.h1
          {...anim(0.08)}
          className="mt-6 text-5xl md:text-7xl font-bold tracking-tight text-white"
        >
          {title}
        </motion.h1>
        <motion.p {...anim(0.16)} className="mt-6 text-lg text-zinc-400 leading-relaxed">
          {subtitle}
        </motion.p>
        <motion.div {...anim(0.24)} className="mt-9 flex flex-wrap gap-3 justify-center">
          <button
            onClick={onPrimary}
            className="px-7 py-3.5 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-500 text-white text-sm font-medium hover:opacity-90 transition-opacity"
          >
            {ctaPrimary}
          </button>
          <button
            onClick={onSecondary}
            className="px-7 py-3.5 rounded-xl border border-white/15 text-sm text-zinc-200 hover:bg-white/5 transition-colors"
          >
            {ctaSecondary}
          </button>
        </motion.div>
        <motion.p {...anim(0.3)} className="mt-10 text-[11px] uppercase tracking-[0.25em] text-zinc-600">
          {note}
        </motion.p>
      </div>
    </section>
  );
}
