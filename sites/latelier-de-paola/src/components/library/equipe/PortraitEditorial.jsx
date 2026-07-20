/**
 * @library equipe/PortraitEditorial
 * @description Portrait unique mis en scène (figure « la personne », complémentaire de la grille d'équipe) : visuel décalé, biographie courte, signature. Éditorial : cadre à ombre terracotta, serif. Premium : portrait en verre dépoli, halo, filet lumineux.
 * @registers editorial, premium
 * @deps framer-motion
 * @props register? · name? · role? · bio? · image?: url · imageAlt? · signature?
 * @weight ~2.0 KB gz
 */
import React from "react";
import { motion, useReducedMotion } from "framer-motion";

export default function PortraitEditorial({
  register = "editorial",
  name = "Prénom Nom — Démo",
  role = "Fondatrice (placeholder)",
  bio = "Deux ou trois phrases de démonstration : le parcours, la manière de travailler, ce que les clients retrouvent à chaque visite. À personnaliser par prospect.",
  image = null,
  imageAlt = "Portrait — Démo",
  signature = "« Le détail fait la différence. » — Démo",
}) {
  const reduce = useReducedMotion();
  const ed = register === "editorial";
  const anim = (d = 0, x = 0) =>
    reduce
      ? { initial: false }
      : {
          initial: { opacity: 0, y: 18, x },
          whileInView: { opacity: 1, y: 0, x: 0 },
          viewport: { once: true, margin: "-60px" },
          transition: { duration: 0.55, delay: d },
        };

  const Visual = image ? (
    <img src={image} alt={imageAlt} loading="lazy" className="w-full h-full object-cover" />
  ) : (
    <div
      className={`w-full h-full grid place-items-center ${
        ed
          ? "bg-[radial-gradient(70%_70%_at_40%_30%,#EAD9BF,#C9A277)]"
          : "bg-[radial-gradient(70%_70%_at_40%_30%,rgba(99,102,241,0.35),#101018)]"
      }`}
    >
      <span className={`text-[11px] uppercase tracking-[0.25em] ${ed ? "text-[#7C5A32]" : "text-indigo-200/60"}`}>
        Portrait — Démo
      </span>
    </div>
  );

  if (ed) {
    return (
      <section className="bg-[#F7F1E8] text-[#1C1917] py-24 px-6">
        <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-12 gap-12 items-center">
          <motion.div {...anim(0, -20)} className="md:col-span-5">
            <div className="relative max-w-sm">
              <div aria-hidden="true" className="absolute inset-0 -translate-x-3 translate-y-3 rounded-2xl bg-[#9A3412]/20" />
              <div className="relative aspect-[4/5] rounded-2xl overflow-hidden border border-[#E5D9C6]">{Visual}</div>
            </div>
          </motion.div>
          <div className="md:col-span-7">
            <motion.p {...anim(0.06)} className="text-xs uppercase tracking-[0.25em] text-[#9A3412]">{role}</motion.p>
            <motion.h2 {...anim(0.12)} style={{ fontFamily: "Georgia, 'Times New Roman', serif" }} className="mt-3 text-4xl md:text-5xl tracking-tight">
              {name}
            </motion.h2>
            <motion.p {...anim(0.18)} className="mt-6 text-[#44403C] leading-relaxed max-w-xl">{bio}</motion.p>
            <motion.p {...anim(0.24)} style={{ fontFamily: "Georgia, serif" }} className="mt-8 text-lg italic text-[#78716C]">
              {signature}
            </motion.p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="relative bg-[#0B0B10] text-zinc-100 py-24 px-6 overflow-hidden">
      <div aria-hidden="true" className="absolute -top-24 right-[-10vmin] w-[50vmin] h-[50vmin] rounded-full bg-indigo-500/12 blur-3xl" />
      <div className="relative max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-12 gap-12 items-center">
        <motion.div {...anim(0, -20)} className="md:col-span-5">
          <div className="relative max-w-sm rounded-2xl p-2 bg-white/[0.04] border border-white/10 backdrop-blur">
            <div className="aspect-[4/5] rounded-xl overflow-hidden">{Visual}</div>
          </div>
        </motion.div>
        <div className="md:col-span-7">
          <motion.p {...anim(0.06)} className="text-xs uppercase tracking-[0.25em] text-indigo-300">{role}</motion.p>
          <motion.h2 {...anim(0.12)} className="mt-3 text-4xl md:text-5xl font-bold tracking-tight text-white">{name}</motion.h2>
          <motion.p {...anim(0.18)} className="mt-6 text-zinc-400 leading-relaxed max-w-xl">{bio}</motion.p>
          <motion.p {...anim(0.24)} className="mt-8 text-lg italic text-zinc-500">{signature}</motion.p>
        </div>
      </div>
    </section>
  );
}
