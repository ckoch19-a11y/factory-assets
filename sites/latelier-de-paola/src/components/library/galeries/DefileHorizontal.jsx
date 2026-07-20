/**
 * @library galeries/DefileHorizontal
 * @description Galerie à défilement horizontal en scroll-snap natif (zéro JS de scroll) avec fondus de bords et légendes. Le geste signature des sites de studio, sans lib lourde — fonctionne au doigt, à la molette et au clavier.
 * @registers editorial, premium
 * @deps aucune
 * @props register? · title? · images?: [{src, legende?}]
 * @weight ~1 KB gz
 * Écrit maison pour l'usine.
 */
import React from "react";

const T = {
  editorial: {
    section: "bg-[#F7F1E8] text-[#1C1917]",
    serif: { fontFamily: "Georgia, 'Times New Roman', serif" },
    legende: "text-[#78716C]",
    fondu: "from-[#F7F1E8]",
  },
  premium: {
    section: "bg-[#0B0B10] text-white",
    serif: {},
    legende: "text-zinc-500",
    fondu: "from-[#0B0B10]",
  },
};

const DEMO = [
  { src: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=900&q=80", legende: "Réalisation — démo 1" },
  { src: "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=900&q=80", legende: "Réalisation — démo 2" },
  { src: "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?w=900&q=80", legende: "Réalisation — démo 3" },
  { src: "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=900&q=80", legende: "Réalisation — démo 4" },
];

export default function DefileHorizontal({ register = "editorial", title = "Réalisations", images = DEMO }) {
  const t = T[register] || T.editorial;

  return (
    <section aria-label="Galerie de réalisations" className={"relative py-24 overflow-hidden " + t.section}>
      <div className="max-w-6xl mx-auto px-6 flex items-end justify-between mb-10">
        <h2 className="text-3xl md:text-5xl tracking-tight" style={t.serif}>{title}</h2>
        <span aria-hidden="true" className={"hidden md:inline text-[11px] uppercase tracking-[0.25em] " + t.legende}>Faire défiler →</span>
      </div>
      <div className="relative">
        <div
          className="flex gap-5 overflow-x-auto snap-x snap-mandatory px-6 md:px-[max(1.5rem,calc((100vw-72rem)/2))] pb-4"
          style={{ scrollbarWidth: "none" }}
          tabIndex={0}
          role="group"
          aria-label="Images défilantes"
        >
          {images.map((img, i) => (
            <figure key={i} className="snap-start shrink-0 w-[80vw] sm:w-[420px]">
              <img
                src={img.src}
                alt={img.legende || `Réalisation ${i + 1}`}
                loading="lazy"
                className="w-full h-[300px] sm:h-[380px] object-cover rounded-2xl"
              />
              {img.legende && (
                <figcaption className={"mt-3 text-xs uppercase tracking-[0.2em] " + t.legende}>{img.legende}</figcaption>
              )}
            </figure>
          ))}
        </div>
        <div aria-hidden="true" className={"pointer-events-none absolute inset-y-0 left-0 w-12 bg-gradient-to-r to-transparent " + t.fondu} />
        <div aria-hidden="true" className={"pointer-events-none absolute inset-y-0 right-0 w-12 bg-gradient-to-l to-transparent " + t.fondu} />
      </div>
    </section>
  );
}
