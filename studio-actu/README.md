# Studio actu KORVEX — 5 vidéos/jour « IA & agents IA sur mesure pour les PME »

Pipeline : `jours/<date>.json` (écrit par la tâche planifiée après recherche) → `./lancer.sh <date>` → 5 MP4 9:16 (voix Piper fixe, musique originale, sous-titres, −14 LUFS) + cover + légende → Postiz (FB, IG, LinkedIn, TikTok).

- `./installer.sh` — prépare un conteneur neuf (ffmpeg, piper-tts, playwright 1.56.1, CLI postiz).
- `./lancer.sh [date]` — rend tout, sorties dans `sorties/<date>/`, `controle.png` = planche de contrôle.
- `LIGNE-EDITORIALE.md` — créneaux, séries, règles (à lire avant d'écrire un jour).
- `jours/2026-10-01.json` — exemple de référence du schéma.
- Voix : `KX_VOIX` (défaut fr_FR-tom-medium), `KX_VITESSE` (0.9), `KX_CTA` (phrase de fin).

Schéma d'une vidéo : `{id, serie, creneau, theme: papier|encre, titre, source, legende, scenes:[{type: hook|chiffre|points|texte, label, titre|valeur+legende|points[≤3], taille?, voix}]}`.
