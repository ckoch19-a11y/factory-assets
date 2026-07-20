/**
 * @library transitions/PontCourbe
 * @description Ferme une section par une courbe SVG (vague douce, arc ou diagonale) qui fond vers la couleur de la section suivante. Statique — zéro coût. À poser en DERNIER enfant de la section du dessus (la transition ferme, elle n'ouvre pas — cf. ASSEMBLAGE.md §3).
 * @registers editorial, premium
 * @deps aucune
 * @props to: couleur de la section suivante (hex) · variant?: "vague"|"arc"|"diagonale" ("vague") · height?: 80 (px) · flip?: bool (miroir horizontal)
 * @weight ~0.5 KB gz
 * Écrit maison pour l'usine.
 */
import React from "react";

const PATHS = {
  vague: "M0,64 C240,96 480,16 720,40 C960,64 1200,112 1440,72 L1440,120 L0,120 Z",
  arc: "M0,96 C480,24 960,24 1440,96 L1440,120 L0,120 Z",
  diagonale: "M0,110 L1440,30 L1440,120 L0,120 Z",
};

export default function PontCourbe({ to = "#0B0B10", variant = "vague", height = 80, flip = false, className = "" }) {
  return (
    <div
      aria-hidden="true"
      className={"pointer-events-none absolute bottom-0 left-0 right-0 " + className}
      style={{ height, transform: flip ? "scaleX(-1)" : undefined }}
    >
      <svg
        viewBox="0 0 1440 120"
        preserveAspectRatio="none"
        className="block h-full w-full"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path d={PATHS[variant] || PATHS.vague} fill={to} />
      </svg>
    </div>
  );
}
