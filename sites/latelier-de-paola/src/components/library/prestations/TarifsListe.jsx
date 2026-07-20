/**
 * @library prestations/TarifsListe
 * @description Liste de tarifs à filets pointillés (style carte de restaurant / institut) groupée par catégories. Éditorial : serif, filets pointillés chauds. Premium : lignes fines lumineuses, monospace discret pour les prix.
 * @registers editorial, premium
 * @deps framer-motion
 * @props register? · title? · note? · groups?: {label, items: {name, price, detail?}[]}[]
 * @weight ~2.4 KB gz
 */
import React from "react";
import { motion, useReducedMotion } from "framer-motion";

const DEFAULT_GROUPS = [
  {
    label: "Catégorie une — Démo",
    items: [
      { name: "Service simple", price: "25 €", detail: "30 min" },
      { name: "Service complet", price: "45 €", detail: "1 h" },
      { name: "Service premium", price: "65 €", detail: "1 h 30" },
    ],
  },
  {
    label: "Catégorie deux — Démo",
    items: [
      { name: "Option courte", price: "15 €" },
      { name: "Option longue", price: "35 €", detail: "sur rendez-vous" },
    ],
  },
];

export default function TarifsListe({
  register = "editorial",
  title = "Nos tarifs",
  note = "Tarifs de démonstration — à remplacer (Démo).",
  groups = DEFAULT_GROUPS,
}) {
  const reduce = useReducedMotion();
  const anim = (i) =>
    reduce
      ? { initial: false }
      : {
          initial: { opacity: 0, y: 16 },
          whileInView: { opacity: 1, y: 0 },
          viewport: { once: true, margin: "-60px" },
          transition: { duration: 0.45, delay: i * 0.06 },
        };

  if (register === "editorial") {
    return (
      <section className="bg-[#F7F1E8] text-[#1C1917] py-24 px-6">
        <div className="max-w-3xl mx-auto">
          <h2 style={{ fontFamily: "Georgia, 'Times New Roman', serif" }} className="text-4xl md:text-5xl tracking-tight text-center">
            {title}
          </h2>
          <div aria-hidden="true" className="mx-auto mt-5 h-px w-24 bg-gradient-to-r from-transparent via-[#C9B28E] to-transparent" />
          <div className="mt-12 space-y-10">
            {groups.map((g, gi) => (
              <motion.div key={g.label} {...anim(gi)}>
                <h3 className="text-xs uppercase tracking-[0.25em] text-[#9A3412]">{g.label}</h3>
                <ul className="mt-4 space-y-3">
                  {g.items.map((it) => (
                    <li key={it.name} className="flex items-baseline gap-3">
                      <span className="text-[15px]">{it.name}</span>
                      {it.detail && <span className="text-xs text-[#78716C]">({it.detail})</span>}
                      <span aria-hidden="true" className="flex-1 border-b border-dotted border-[#C9B28E] translate-y-[-3px]" />
                      <span style={{ fontFamily: "Georgia, serif" }} className="text-[17px]">{it.price}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
          <p className="mt-12 text-center text-xs text-[#78716C]">{note}</p>
        </div>
      </section>
    );
  }

  /* ===== Sombre premium ===== */
  return (
    <section className="bg-[#0B0B10] text-zinc-100 py-24 px-6">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-white text-center">{title}</h2>
        <div aria-hidden="true" className="mx-auto mt-5 h-px w-24 bg-gradient-to-r from-transparent via-indigo-400/60 to-transparent" />
        <div className="mt-12 space-y-10">
          {groups.map((g, gi) => (
            <motion.div key={g.label} {...anim(gi)}>
              <h3 className="text-xs uppercase tracking-[0.25em] text-indigo-300">{g.label}</h3>
              <ul className="mt-4 divide-y divide-white/[0.06]">
                {g.items.map((it) => (
                  <li key={it.name} className="flex items-baseline gap-3 py-3">
                    <span className="text-[15px] text-zinc-200">{it.name}</span>
                    {it.detail && <span className="text-xs text-zinc-500">({it.detail})</span>}
                    <span className="flex-1" />
                    <span className="font-mono text-[15px] text-white">{it.price}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
        <p className="mt-12 text-center text-xs text-zinc-600">{note}</p>
      </div>
    </section>
  );
}
