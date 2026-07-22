# Rapport de contrôle QA / Conformité / Sécurité

**Date :** 2026-07-22
**App :** Gan Assurances Beaune — vitrine (`6a4cb1aba40261a50b1d5dbb`), type *vitrine*, secteur assurance
**Checkpoint correctifs :** Base44 `5418196` — *« QA pass: consent CNIL 6-month TTL, lazy team images, remove unused Link imports »*

> Note d'environnement : la doctrine formelle (`CERVEAU/` R1→R28, VERROUS, ECHECS, `scripts/qa.mjs`)
> n'existe ni dans ce repo (qui ne contient que des médias) ni dans l'app Base44. Le contrôle a donc
> été mené sur les 3 checklists du brief. Les correctifs de code vivent dans l'app Base44 (git S3),
> pas dans ce repo `factory-assets` : ce document est l'artefact de traçabilité.

---

## VERDICT : REFUSÉ

Deux blocants relèvent d'une **décision humaine (Calvin)** — je prépare, je ne publie pas. Aucun
blocant technique restant côté build/lint.

```
VERDICT: REFUSÉ
APP: 6a4cb1aba40261a50b1d5dbb (gan-assurances-beaune, vitrine)
QA technique:   1 écart   [perf initial au plafond]
Conformité:     3 écarts   [avis non vérifiés, hébergeur non nommé, consentement sans TTL]
Sécurité:       0 écart bloquant
Corrigés cette passe: 3     | Restants (bloquants pour Calvin): 2
Perf: 180,7 KB gz (entry+home) | LCP: non mesuré (preview bloqué) | Console: non mesuré | 390px: non mesuré
Preuves: gzip dist/assets/index-DmEgX31S.js = 180 671 o ; npm run lint = 0 err ; npm run build = exit 0
```

---

## Limite de cette passe : vérification à l'écran impossible

La politique réseau de l'environnement **bloque les domaines Base44** (403 CONNECT sur
`*.base44.app` et `preview-sandbox--*.base44-preview.app`, cf. `__agentproxy/status`).
Les items « Chrome sur le preview » (screenshots desktop + 390px, `read_console_messages`,
mesure DOM, LCP réel) **n'ont pas pu être exécutés**. Évidence retenue : analyse statique du
source + mesure du build (`npm run build` / `npm run lint` / gzip des chunks) exécutés dans le
sandbox Base44. **À faire avant publication** : dérouler la vérification navigateur (console 0
erreur desktop+mobile, 0 débordement à 390px, LCP < 2,5 s).

---

## CHECKLIST 1 — QA TECHNIQUE

| Item | Résultat | Preuve |
|---|---|---|
| `npm run build` | ✅ vert | exit_code 0 |
| ESLint bloquant | ✅ 0 (était 2) | `npm run lint` sans sortie après fix |
| Code-splitting pages | ✅ | `src/App.jsx` : 12 pages en `lazy(() => import())` |
| Prefetch pages en idle | ✅ non bloquant | `requestIdleCallback` après `load`, timeout 4 s |
| **JS initial home** | ⚠️ **au plafond** | entry `index-DmEgX31S.js` = **180 671 o gz** (~176,4 KiB) ; Home est *statique* dans l'entry → framer-motion embarqué |
| Images lazy hors hero | ✅ (corrigé) | images équipe passées en `loading="lazy"` |
| Console / 390px / LCP | ⛔ non mesuré | preview bloqué par la politique réseau |

**Écart 1 (non bloquant, décision d'investissement Calvin) — perf initial au plafond.**
La home charge 180,7 KB gz d'entrée (limite du brief : ≤ 180 KB gz/page). `framer-motion` (~48 KB gz)
est dans le bundle initial via `Layout.jsx` (toujours chargé) + `Hero.jsx`/`Reviews.jsx`. Descendre
nettement sous le plafond suppose de différer framer-motion ou de lazy-loader `Home` — refactor à
risque de régression d'animation (R18/R20), à trancher, pas à improviser.

## CHECKLIST 2 — NORMES & CONFORMITÉ

| Item | Résultat | Preuve |
|---|---|---|
| Mentions légales | ✅ | `pages/MentionsLegales.jsx` : éditeur, dir. publication (ORIAS 14003961), PI, RGPD, médiation |
| Politique de confidentialité | ✅ | `pages/Confidentialite.jsx` : responsable, données, finalités, durée, droits, consentement |
| Liens légaux au footer | ✅ | `Footer.jsx` → `/mentions-legales` + `/confidentialite` sur chaque page |
| Bandeau cookies / consentement | ✅ | `fx/ConsentBanner.jsx` : accepter/refuser à visibilité égale, aucun tracking avant accord |
| **Durée du consentement ≤ 6 mois** | ✅ (corrigé) | ajout `gan_consent_at` + expiration 182 j ; purge du choix périmé avant re-demande |
| Tracking gaté sur consentement | ✅ | `fx/VisitTracker.jsx` ne POST qu'après `gan_consent === "accepted"` ; aucune PII envoyée |
| `h1` unique par page | ✅ | Home via `Hero.jsx` (1 h1) ; autres pages via `PageHeader.jsx` (1 h1) |
| JSON-LD SEO local | ✅ valide | `SchemaOrg.jsx` : `InsuranceAgency` + adresse, tel, horaires, `priceRange €€`, geo |
| **Avis / données réelles (R5)** | 🔴 **à vérifier** | `pages/Avis.jsx` : 6 témoignages nominatifs + `aggregateRating 4,2/12`, présentés comme réels, **non marqués « Démo »** |
| **Hébergeur nommé (LCEN)** | 🔴 **à compléter** | Mentions : *« coordonnées de l'hébergeur disponibles sur demande »* — la loi impose l'identification |

**Écart 2 (BLOCANT — Calvin) — authenticité des avis.** Les 6 avis de `Avis.jsx` et la note
`4,2/5 (12 avis)` en JSON-LD doivent être **confirmés comme réels** (avis Google authentiques) ou
**marqués « Démo »**. Un `aggregateRating` non adossé à des avis vérifiables expose à une pénalité
Google et contrevient à R5. → Calvin confirme la source ou on bascule en démo.

**Écart 3 (BLOCANT — Calvin) — hébergeur.** Remplacer *« sur demande »* par le nom + adresse réels
de l'hébergeur (Base44 / prestataire). → Calvin fournit l'info, j'insère.

## CHECKLIST 3 — SÉCURITÉ

| Item | Résultat | Preuve |
|---|---|---|
| Aucun secret client | ✅ | grep `sk_live/api_key/secret/token/Bearer/AKIA` : rien ; `VITE_*` = appId/baseUrl publics |
| Client Base44 | ✅ | `base44Client.js` : `requiresAuth: false`, appId public ; webhook BO = URL de fonction publique (commentée) |
| Câblage vitrine→BO | ✅ | `BACKOFFICE_WEBHOOK` POST `{type,data}`, 0 secret, pattern base44-connect |
| Tracking sans PII | ✅ | `VisitTracker` n'envoie que `{jour,total,top_pages}` agrégés |
| Liens externes | ✅ | Google/`mailto`/`tel` avec `rel="noopener noreferrer"` sur les cibles `_blank` |
| `mailto` en clair | ⚠️ mineur | `beaune-centre@gan.fr` exposé en clair (footer, Agence, Contact) — e-mail pro, tolérable ; obfuscation possible si spam |

Aucun écart sécurité bloquant.

---

## Corrigés cette passe (checkpoint `5418196`)

1. **RGPD — expiration du consentement à 6 mois** (`fx/ConsentBanner.jsx`) : horodatage `gan_consent_at`,
   re-demande au-delà de 182 j, purge du choix périmé/legacy avant re-consentement. Rétro-compat
   `VisitTracker` préservée (string `gan_consent` inchangée).
2. **Perf — images d'équipe en `loading="lazy"` + `decoding="async"`** (`home/Team.jsx`) : 3 images
   sous la ligne de flottaison sorties du chemin critique.
3. **Lint — imports `Link` inutilisés supprimés** (`pages/Avis.jsx`, `home/Team.jsx`) : ESLint 2 → 0 erreur.

## Restants bloquants (décision Calvin, non publiables sans lui)

- [ ] **Avis** : confirmer réels (source Google) ou marquer « Démo ».
- [ ] **Hébergeur** : fournir le nom/adresse pour les mentions légales.

## Recommandé (non bloquant)

- [ ] Vérification navigateur à l'écran (console, 390px, LCP) — bloquée ici par la politique réseau.
- [ ] Arbitrer l'allègement du bundle initial (framer-motion) si l'on veut passer nettement sous 180 KB gz.
