// Bibliothèque d'objets illustrés KORVEX — trait épais dessiné à l'écran (classe s), touches d'accent (classe f).
// viewBox 0 0 200 200. Chaque trait porte pathLength="1" pour l'animation « dessin ».
const L = (d) => `<path class="s" pathLength="1" d="${d}"/>`;
const C = (cx, cy, r) => `<circle class="s" pathLength="1" cx="${cx}" cy="${cy}" r="${r}"/>`;
const R = (x, y, w, h, rx = 14) => `<rect class="s" pathLength="1" x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}"/>`;
const F = (inner) => `<g class="f">${inner}</g>`;
window.OBJETS = {
  telephone: R(58, 18, 84, 164, 18) + L('M86 34h28') + C(100, 160, 7) + F(`<rect x="72" y="52" width="56" height="34" rx="8"/><rect x="72" y="94" width="40" height="10" rx="5"/>`),
  facture: L('M52 22h74l26 26v130H52z') + L('M126 22v26h26') + L('M70 80h60M70 102h60M70 124h40') + F(`<rect x="96" y="146" width="40" height="16" rx="6"/>`),
  pdf: L('M52 22h74l26 26v130H52z') + L('M126 22v26h26') + F(`<rect x="62" y="96" width="76" height="40" rx="8"/>`) + L('M70 152h60'),
  enveloppe: R(24, 52, 152, 100, 14) + L('M28 58l72 54 72-54') + F(`<circle cx="160" cy="54" r="16"/>`),
  calendrier: R(30, 40, 140, 132, 16) + L('M30 76h140M66 26v28M134 26v28') + F(`<rect x="52" y="94" width="26" height="22" rx="5"/><rect x="88" y="94" width="26" height="22" rx="5"/><rect x="124" y="130" width="26" height="22" rx="5"/>`),
  loupe: C(86, 86, 50) + L('M122 122l50 50') + F(`<circle cx="86" cy="86" r="22"/>`),
  globe: C(100, 100, 72) + L('M28 100h144M100 28c-30 40-30 104 0 144M100 28c30 40 30 104 0 144') + F(`<circle cx="148" cy="58" r="12"/>`),
  horloge: C(100, 104, 70) + L('M100 62v42l30 20') + L('M78 22h44') + F(`<circle cx="100" cy="104" r="9"/>`),
  euro: C(100, 100, 72) + L('M128 68a40 40 0 1 0 0 64') + L('M62 92h56M62 112h52') ,
  agent: R(42, 58, 116, 100, 30) + L('M100 58V34') + C(100, 28, 8) + L('M28 100v24M172 100v24') + F(`<circle cx="78" cy="104" r="11"/><circle cx="122" cy="104" r="11"/><rect x="80" y="130" width="40" height="8" rx="4"/>`),
  bulle: L('M36 46h128a14 14 0 0 1 14 14v66a14 14 0 0 1-14 14H90l-34 30v-30H36a14 14 0 0 1-14-14V60a14 14 0 0 1 14-14z') + F(`<circle cx="70" cy="94" r="9"/><circle cx="100" cy="94" r="9"/><circle cx="130" cy="94" r="9"/>`),
  graphique: L('M30 30v140h140') + L('M52 136l34-40 30 22 46-60') + F(`<circle cx="162" cy="58" r="11"/><rect x="52" y="150" width="20" height="14" rx="3"/><rect x="86" y="140" width="20" height="24" rx="3"/><rect x="120" y="128" width="20" height="36" rx="3"/>`),
  bouclier: L('M100 22l62 24v50c0 44-28 72-62 84-34-12-62-40-62-84V46z') + L('M72 102l20 20 38-42'),
  cadenas: R(46, 88, 108, 86, 16) + L('M68 88V64a32 32 0 0 1 64 0v24') + F(`<circle cx="100" cy="124" r="11"/><rect x="95" y="128" width="10" height="22" rx="4"/>`),
  etoile: L('M100 24l22 46 50 6-37 34 10 50-45-25-45 25 10-50-37-34 50-6z') + F(`<circle cx="100" cy="104" r="14"/>`),
  epingle: L('M100 180s-56-58-56-98a56 56 0 0 1 112 0c0 40-56 98-56 98z') + F(`<circle cx="100" cy="82" r="20"/>`),
  maison: L('M28 98l72-62 72 62') + L('M48 82v88h104V82') + F(`<rect x="86" y="120" width="28" height="50" rx="4"/>`),
  voiture: L('M28 130v-20l20-40h104l20 40v20a10 10 0 0 1-10 10H38a10 10 0 0 1-10-10z') + L('M48 110h104') + C(64, 142, 16) + C(136, 142, 16) + F(`<rect x="62" y="80" width="76" height="22" rx="6"/>`),
  cle: C(64, 136, 30) + L('M86 114l74-74M134 66l20 20M148 52l14 14') + F(`<circle cx="64" cy="136" r="10"/>`),
  casque: L('M30 140h140') + L('M44 140c0-42 24-74 56-74s56 32 56 74') + L('M100 66V48') + F(`<rect x="88" y="40" width="24" height="16" rx="6"/>`),
  cloche: L('M100 32c-34 0-50 26-50 58v30l-16 22h132l-16-22V90c0-32-16-58-50-58z') + L('M84 160a16 16 0 0 0 32 0') + F(`<circle cx="150" cy="48" r="16"/>`),
  check: C(100, 100, 72) + L('M66 102l24 24 46-52'),
  cible: C(100, 100, 72) + C(100, 100, 44) + F(`<circle cx="100" cy="100" r="18"/>`) + L('M150 50l-38 38'),
  aimant: L('M54 40v70a46 46 0 0 0 92 0V40') + L('M54 40h28v70a18 18 0 0 0 36 0V40h28') + F(`<rect x="54" y="40" width="28" height="22"/><rect x="118" y="40" width="28" height="22"/>`),
  eclair: L('M112 20L52 112h46l-12 68 62-96h-46z'),
  ecran: R(22, 34, 156, 108, 14) + L('M70 170h60M100 142v28') + F(`<rect x="40" y="54" width="60" height="12" rx="5"/><rect x="40" y="76" width="96" height="10" rx="5"/><rect x="40" y="96" width="78" height="10" rx="5"/>`),
  sablier: L('M54 24h92M54 176h92M64 24c0 46 72 52 72 76s-72 30-72 76M136 24c0 46-72 52-72 76s72 30 72 76') + F(`<path d="M76 160c8-14 40-14 48 0z"/>`),
};
window.objetSVG = (nom) => {
  const inner = window.OBJETS[nom];
  if (!inner) return '';
  return `<svg class="obj" viewBox="0 0 200 200" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" style="overflow:visible">${inner}</svg>`;
};
