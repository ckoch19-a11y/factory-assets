/**
 * @library navigation/ProgressionScroll
 * @description Barre de progression de lecture fixée en haut du viewport + bouton « remonter » qui apparaît après un écran. Le duo discret qui donne aux pages longues une sensation de maîtrise — scroll-driven via framer-motion, zéro re-render.
 * @registers editorial, premium
 * @deps framer-motion
 * @props register? · seuil?: 600 (px avant l'apparition du bouton remonter)
 * @weight ~0.8 KB gz
 * Écrit maison pour l'usine.
 */
import React, { useEffect, useState } from "react";
import { motion, useScroll, useSpring, useReducedMotion } from "framer-motion";

const T = {
  editorial: {
    barre: "bg-[#B45309]",
    bouton: "bg-[#1C1917] text-[#F7F1E8] hover:opacity-90",
  },
  premium: {
    barre: "bg-gradient-to-r from-indigo-500 to-violet-500",
    bouton: "bg-white/10 text-white border border-white/15 backdrop-blur hover:bg-white/20",
  },
};

export default function ProgressionScroll({ register = "editorial", seuil = 600 }) {
  const t = T[register] || T.editorial;
  const reduced = useReducedMotion();
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, { stiffness: 140, damping: 30, restDelta: 0.001 });
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const onScroll = () => setVisible(window.scrollY > seuil);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [seuil]);

  return (
    <>
      <motion.div
        aria-hidden="true"
        className={"fixed top-0 left-0 right-0 h-[3px] origin-left z-50 " + t.barre}
        style={{ scaleX: reduced ? 1 : scaleX }}
      />
      <button
        onClick={() => window.scrollTo({ top: 0, behavior: reduced ? "auto" : "smooth" })}
        aria-label="Remonter en haut de page"
        className={
          "fixed bottom-6 right-6 z-50 w-11 h-11 rounded-full grid place-items-center text-lg transition-all duration-300 " +
          t.bouton + " " + (visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4 pointer-events-none")
        }
      >
        ↑
      </button>
    </>
  );
}
