/**
 * @library transitions/PontFondu
 * @description Ferme une section par un dégradé de liaison vers la couleur de la suivante, avec option filet lumineux (premium) ou fil doré (éditorial) sur la ligne de jonction. La solution sobre quand la courbe serait trop décorative. Statique — zéro coût.
 * @registers editorial, premium
 * @deps aucune
 * @props to: couleur de la section suivante (hex) · register?: "editorial"|"premium" · height?: 120 (px) · filet?: bool (true) — ligne lumineuse à la jonction
 * @weight ~0.4 KB gz
 * Écrit maison pour l'usine.
 */
import React from "react";

const FILETS = {
  editorial: "linear-gradient(to right, transparent, #C9B28E, transparent)",
  premium: "linear-gradient(to right, transparent, rgba(129,140,248,0.7), transparent)",
};

export default function PontFondu({ to = "#0B0B10", register = "premium", height = 120, filet = true, className = "" }) {
  return (
    <div aria-hidden="true" className={"pointer-events-none absolute bottom-0 left-0 right-0 " + className} style={{ height }}>
      <div className="absolute inset-0" style={{ background: `linear-gradient(to bottom, transparent, ${to})` }} />
      {filet && (
        <div
          className="absolute bottom-0 left-0 right-0 h-px"
          style={{ background: FILETS[register] || FILETS.premium }}
        />
      )}
    </div>
  );
}
