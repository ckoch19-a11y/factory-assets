/**
 * @library avis/NoteGlobale
 * @description Bandeau de preuve sociale agrégée : grande note sur 5, étoiles, nombre d'avis et badges de plateformes — la synthèse qui rassure avant les témoignages détaillés. Placeholder marqué Démo, à brancher sur les vraies données.
 * @registers editorial, premium
 * @deps aucune
 * @props register? · note?: 4.9 · total?: 127 · plateformes?: ["Google", "Pages Jaunes"] · mention?
 * @weight ~0.9 KB gz
 * Écrit maison pour l'usine.
 */
import React from "react";

const T = {
  editorial: {
    section: "bg-white text-[#1C1917] border-y border-[#E7E0D5]",
    serif: { fontFamily: "Georgia, 'Times New Roman', serif" },
    etoile: "text-[#B45309]",
    muted: "text-[#78716C]",
    badge: "border border-[#E7E0D5] text-[#57534E]",
  },
  premium: {
    section: "bg-[#0E0E14] text-white border-y border-white/10",
    serif: {},
    etoile: "text-amber-400",
    muted: "text-zinc-500",
    badge: "border border-white/15 text-zinc-300",
  },
};

function Etoile({ remplie, demi, className }) {
  return (
    <svg viewBox="0 0 20 20" className={"w-5 h-5 " + className} aria-hidden="true">
      {demi && (
        <defs>
          <linearGradient id="demi-etoile"><stop offset="50%" stopColor="currentColor" /><stop offset="50%" stopColor="transparent" /></linearGradient>
        </defs>
      )}
      <path
        d="M10 1.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L10 14.9l-5.2 2.7 1-5.8L1.5 7.7l5.9-.9L10 1.5z"
        fill={demi ? "url(#demi-etoile)" : remplie ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="1.2"
      />
    </svg>
  );
}

export default function NoteGlobale({
  register = "editorial",
  note = 4.9,
  total = 127,
  plateformes = ["Google", "Pages Jaunes"],
  mention = "Démo — brancher sur vos vrais avis",
}) {
  const t = T[register] || T.editorial;
  const pleines = Math.floor(note);
  const demi = note - pleines >= 0.25 && note - pleines < 0.75;

  return (
    <section aria-label={`Note moyenne ${note} sur 5 basée sur ${total} avis`} className={"py-12 px-6 " + t.section}>
      <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-center gap-6 sm:gap-12 text-center sm:text-left">
        <p className="text-6xl tracking-tight" style={t.serif}>{note.toLocaleString("fr-FR")}</p>
        <div>
          <div className={"flex justify-center sm:justify-start gap-1 " + t.etoile} aria-hidden="true">
            {[0, 1, 2, 3, 4].map((i) => (
              <Etoile key={i} remplie={i < pleines} demi={i === pleines && demi} className={t.etoile} />
            ))}
          </div>
          <p className={"mt-2 text-sm " + t.muted}>{total} avis clients · {mention}</p>
        </div>
        <div className="flex gap-2">
          {plateformes.map((p) => (
            <span key={p} className={"px-3.5 py-1.5 rounded-full text-xs " + t.badge}>{p}</span>
          ))}
        </div>
      </div>
    </section>
  );
}
