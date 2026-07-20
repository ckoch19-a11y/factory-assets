/**
 * @library navigation/NavbarLisible
 * @description Navbar au contrat ASSEMBLAGE §5 : transparente sur le hero, elle prend fond + contraste dès le premier scroll (état scrolled) — lisible sur TOUS les fonds qu'elle traverse. Lien d'évitement clavier, aria-current, CTA persistant. Menu mobile délégué à MenuOverlay.
 * @registers editorial, premium
 * @deps aucune
 * @props register? · nom? · liens: [{label, href, actif?}] · ctaLabel? · onCta? · onMenuMobile?: fn (ouvre MenuOverlay)
 * @weight ~1.4 KB gz
 * Écrit maison pour l'usine — corrige le défaut « navbar blanche illisible sur fond noir ».
 */
import React, { useEffect, useState } from "react";

const T = {
  editorial: {
    haut: "text-[#F7F1E8]",
    scrolled: "bg-[#F7F1E8]/90 backdrop-blur-md border-b border-[#E5D9C6] text-[#1C1917] shadow-[0_2px_20px_rgba(120,80,40,0.06)]",
    serif: { fontFamily: "Georgia, 'Times New Roman', serif" },
    lien: "hover:opacity-70",
    actifHaut: "underline underline-offset-8 decoration-[#E8C39A]",
    actifScrolled: "underline underline-offset-8 decoration-[#9A3412]",
    ctaHaut: "rounded-full bg-[#F7F1E8] text-[#1C1917] hover:bg-white",
    ctaScrolled: "rounded-full bg-[#1C1917] text-[#F7F1E8] hover:bg-[#33302B]",
  },
  premium: {
    haut: "text-white",
    scrolled: "bg-[#0B0B10]/85 backdrop-blur-md border-b border-white/10 text-zinc-100",
    serif: {},
    lien: "hover:opacity-70",
    actifHaut: "underline underline-offset-8 decoration-indigo-300",
    actifScrolled: "underline underline-offset-8 decoration-indigo-400",
    ctaHaut: "rounded-xl bg-white text-[#0B0B10] hover:bg-zinc-200",
    ctaScrolled: "rounded-xl bg-gradient-to-r from-indigo-500 to-violet-500 text-white hover:opacity-90",
  },
};

const DEMO_LIENS = [
  { label: "Accueil", href: "#", actif: true },
  { label: "Prestations", href: "#" },
  { label: "Réalisations", href: "#" },
  { label: "Contact", href: "#" },
];

export default function NavbarLisible({
  register = "editorial", nom = "Enseigne", liens = DEMO_LIENS,
  ctaLabel = "Réserver", onCta, onMenuMobile,
}) {
  const t = T[register] || T.editorial;
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <a href="#contenu" className="sr-only focus:not-sr-only focus:absolute focus:z-[60] focus:top-3 focus:left-3 focus:px-4 focus:py-2 focus:bg-white focus:text-black focus:rounded-lg">
        Aller au contenu
      </a>
      <header
        className={"fixed top-0 inset-x-0 z-50 transition-colors duration-300 " + (scrolled ? t.scrolled : t.haut)}
      >
        <nav aria-label="Navigation principale" className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between gap-6">
          <a href="/" className="text-lg tracking-tight" style={t.serif}>{nom}</a>

          <ul className="hidden md:flex items-center gap-7 text-sm">
            {liens.map((l, i) => (
              <li key={i}>
                <a
                  href={l.href}
                  aria-current={l.actif ? "page" : undefined}
                  className={"transition-opacity " + t.lien + " " + (l.actif ? (scrolled ? t.actifScrolled : t.actifHaut) : "")}
                >
                  {l.label}
                </a>
              </li>
            ))}
          </ul>

          <div className="flex items-center gap-3">
            <button onClick={onCta} className={"hidden sm:inline-flex px-5 py-2.5 text-sm font-medium transition-all " + (scrolled ? t.ctaScrolled : t.ctaHaut)}>
              {ctaLabel}
            </button>
            <button
              onClick={onMenuMobile}
              aria-label="Ouvrir le menu"
              className="md:hidden inline-flex flex-col justify-center items-center gap-1.5 w-10 h-10"
            >
              <span className="block w-5 h-0.5 bg-current" />
              <span className="block w-5 h-0.5 bg-current" />
            </button>
          </div>
        </nav>
      </header>
    </>
  );
}
