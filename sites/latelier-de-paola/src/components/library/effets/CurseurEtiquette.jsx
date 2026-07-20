/**
 * @library effets/CurseurEtiquette
 * @description Pastille qui suit le curseur et affiche une étiquette contextuelle au survol des éléments marqués `data-cursor="Voir"` — la signature d'interaction des sites primés. Desktop pointeur fin uniquement ; inertie spring. Ne rend rien sur tactile ou reduced-motion.
 * @registers editorial, premium
 * @deps framer-motion
 * @props register?: "editorial"|"premium" · size?: 12 (pastille) — étiquette auto. Marquer les cibles avec data-cursor="Texte".
 * @weight ~1.0 KB gz
 * Écrit maison pour l'usine.
 */
import React, { useEffect, useState } from "react";
import { AnimatePresence, motion, useMotionValue, useReducedMotion, useSpring } from "framer-motion";

const TOKENS = {
  editorial: { dot: "#9A3412", label: "bg-[#1C1917] text-[#F7F1E8]" },
  premium: { dot: "#818CF8", label: "bg-white text-[#0B0B10]" },
};

export default function CurseurEtiquette({ register = "editorial", size = 12 }) {
  const reduced = useReducedMotion();
  const [enabled, setEnabled] = useState(false);
  const [label, setLabel] = useState("");
  const t = TOKENS[register] || TOKENS.editorial;

  const mx = useMotionValue(-100);
  const my = useMotionValue(-100);
  const x = useSpring(mx, { stiffness: 500, damping: 40, mass: 0.6 });
  const y = useSpring(my, { stiffness: 500, damping: 40, mass: 0.6 });

  useEffect(() => {
    const fine = window.matchMedia("(pointer: fine)").matches;
    if (!fine || reduced) return;
    setEnabled(true);

    const move = (e) => {
      mx.set(e.clientX);
      my.set(e.clientY);
      const target = e.target.closest?.("[data-cursor]");
      setLabel(target ? target.getAttribute("data-cursor") || "" : "");
    };
    window.addEventListener("mousemove", move, { passive: true });
    return () => window.removeEventListener("mousemove", move);
  }, [reduced, mx, my]);

  if (!enabled) return null;

  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 z-[9999]">
      <motion.div
        className="absolute rounded-full"
        style={{ x, y, width: size, height: size, marginLeft: -size / 2, marginTop: -size / 2, background: t.dot }}
      />
      <AnimatePresence>
        {label && (
          <motion.div
            key={label}
            className={"absolute px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap " + t.label}
            style={{ x, y, marginLeft: 14, marginTop: 14 }}
            initial={{ opacity: 0, scale: 0.7 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.7 }}
            transition={{ duration: 0.18 }}
          >
            {label}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
