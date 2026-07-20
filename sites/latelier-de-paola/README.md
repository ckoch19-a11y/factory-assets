# L'Atelier de Paola — vitrine + back-office

Site généré par le pipeline « URL → site » (registre `editorial`, style `steep`) depuis
https://www.latelier-de-paola.com — voir `BRIEF.md` (contenus, plan, entités) exécuté à la lettre.

## Stack

Vite + React 18 + Tailwind (tokens Steep dans `src/index.css`, mapping `tailwind.config.js`) ·
`@base44/sdk` (entités + auth) · `@tanstack/react-query` · composants copiés tels quels depuis la
bibliothèque Usine dans `src/components/library/` (personnalisation par props uniquement).

## Démarrer

```bash
npm install
cp .env.example .env   # renseigner VITE_BASE44_APP_ID (app Base44 cible)
npm run dev
```

Sans app id, la vitrine fonctionne sur les fallbacks du brief (aucune section cassée) ;
le back-office et le formulaire de contact nécessitent l'app Base44.

## Brancher l'app Base44

1. Créer/choisir l'app cible et déclarer les 5 entités de `base44/entities/*.jsonc`
   (SiteConfig, Prestation, Temoignage, SectionContenu, DemandeContact).
2. Activer la création anonyme/publique sur `DemandeContact` (formulaire du vitrine) —
   lecture publique sur les entités de contenu, écriture réservée aux admins.
3. Peupler les données initiales du brief :
   `BASE44_APP_ID=xxx BASE44_API_KEY=xxx npm run seed`
4. `/admin` est réservé au rôle `admin` (garde `ProtectedRoute`).

## Structure

- `src/pages/Home.jsx` — accueil, sections dans l'ordre du brief §3
- `src/pages/admin/` — back-office : tableau de bord, paramètres, contenus, prestations & tarifs, avis, demandes
- `src/content/fallbacks.js` — contenus du brief (fallbacks des sections + source du seed)
- `src/hooks/useContenu.js` — lecture des entités avec fallback
- `base44/entities/` — schémas JSON des entités
- `scripts/seed.mjs` — insertion des données initiales
