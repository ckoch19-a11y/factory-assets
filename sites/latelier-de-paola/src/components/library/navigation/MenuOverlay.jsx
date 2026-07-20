/**
 * @library navigation/MenuOverlay
 * @description Menu plein écran en overlay — liens géants qui entrent en cascade, coordonnées en pied, fermeture Échap/clic/bouton. Focus déplacé à l'ouverture, scroll de page bloqué, aria-modal. La navigation immersive des sites primés, utilisable aussi comme menu mobile de NavbarLisible.
 * @registers editorial, premium
 * @deps framer-motion
 * @props register? · open: bool · onClose: fn · liens: [{label, href}] · contact?: {adresse?, telephone?, email?}
 * @weight ~1.6 KB gz
 * Écrit maison pour l'usine (équivalent framer des menus overlay gsap de React Bits).
 */
import React, { useEffect, useRef } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";

const T = {
  editorial: {
    fond: "bg-[#1C1917] text-[#F7F1E8]",
    serif: { fontFamily: "Georgia, 'Times New Roman', serif" },
    lien: "hover:text-[#E8C39A]",
    num: "text-[#9A3412]",
    meta: "text-[#A8A29E]",
    filet: "bg-gradient-to-r from-[#C9B28E] to-transparent",
  },
  premium: {
    fond: "bg-[#080810] text-white",
    serif: {},
    lien: "hover:text-indigo-300",
    num: "text-indigo-400",
    meta: "text-zinc-500",
    filet: "bg-gradient-to-r from-indigo-400/60 to-transparent",
  },
};

const DEMO_LIENS = [
  { label: "Accueil", href: "#" },
  { label: "Prestations", href: "#" },
  { label: "Réalisations", href: "#" },
  { label: "L'équipe", href: "#" },
  { label: "Contact", href: "#" },
];

export default function MenuOverlay({
  register = "editorial", open = false, onClose = () => {},
  liens = DEMO_LIENS, contact = { adresse: "12 rue de Démo, Dijon", telephone: "03 80 00 00 00", email: "contact@exemple.fr" },
}) {
  const t = T[register] || T.editorial;
  const reduced = useReducedMotion();
  const closeRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (e) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    closeRef.current?.focus();
    return () => { document.removeEventListener("keydown", onKey); document.body.style.overflow = ""; };
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          role="dialog"
          aria-modal="true"
          aria-label="Menu"
          className={"fixed inset-0 z-[100] flex flex-col " + t.fond}
          initial={reduced ? { opacity: 0 } : { clipPath: "inset(0 0 100% 0)" }}
          animate={reduced ? { opacity: 1 } : { clipPath: "inset(0 0 0% 0)" }}
          exit={reduced ? { opacity: 0 } : { clipPath: "inset(0 0 100% 0)" }}
          transition={{ duration: reduced ? 0.2 : 0.55, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="flex items-center justify-between px-6 md:px-10 h-16 shrink-0">
            <span className="text-lg" style={t.serif}>Menu</span>
            <button
              ref={closeRef}
              onClick={onClose}
              aria-label="Fermer le menu"
              className="w-10 h-10 inline-flex items-center justify-center text-2xl leading-none hover:opacity-70"
            >
              ×
            </button>
          </div>

          <nav aria-label="Navigation du menu" className="flex-1 flex items-center px-6 md:px-10">
            <ul className="space-y-2 md:space-y-4">
              {liens.map((l, i) => (
                <motion.li
                  key={i}
                  initial={reduced ? false : { opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: reduced ? 0 : 0.15 + i * 0.06, ease: [0.22, 1, 0.36, 1] }}
                  className="overflow-hidden"
                >
                  <a href={l.href} onClick={onClose} className={"group inline-flex items-baseline gap-4 transition-colors " + t.lien}>
                    <span className={"font-mono text-sm " + t.num}>{String(i + 1).padStart(2, "0")}</span>
                    <span className="text-4xl md:text-6xl tracking-tight" style={t.serif}>{l.label}</span>
                  </a>
                </motion.li>
              ))}
            </ul>
          </nav>

          <div className="px-6 md:px-10 pb-8 shrink-0">
            <div className={"h-px w-full mb-5 " + t.filet} />
            <div className={"flex flex-wrap gap-x-8 gap-y-2 text-sm " + t.meta}>
              {contact?.adresse && <span>{contact.adresse}</span>}
              {contact?.telephone && <a href={"tel:" + contact.telephone.replace(/\s/g, "")} className={"transition-colors " + t.lien}>{contact.telephone}</a>}
              {contact?.email && <a href={"mailto:" + contact.email} className={"transition-colors " + t.lien}>{contact.email}</a>}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
