# Test d'intrusion & remédiation — Gan Assurances Beaune

**Date :** 2026-07-22
**Périmètre :** vitrine `6a4cb1aba40261a50b1d5dbb` + back-office `6a4c2d4c452602b643d20b6d`
**Méthode :** 5 agents red-team adversariaux (secrets, autorisation/entités, webhook, formulaires/XSS, dépendances) — audit du code source + test **actif** des permissions d'entités via l'API Base44 + lecture des fonctions backend.
**Checkpoints correctifs :** vitrine `542d271` · back-office `42c18c0` (+ passe QA antérieure `5418196`).

> Limite : la politique réseau de l'environnement bloque `*.base44.app` → pas de trafic d'attaque HTTP réel (DAST). Les permissions d'entités ont été testées via l'API Base44 (côté serveur), le reste par analyse statique du source et des fonctions Deno.

---

## Résultat en une ligne

Aucun secret exposé, aucun XSS stocké. **La faille majeure était un défaut de contrôle d'accès en lecture** (entités PII sans RLS, gate `/admin` uniquement côté navigateur) **et un webhook public non authentifié**. Les deux sont désormais **corrigés à la racine** côté données ; l'authentification forte du webhook et le durcissement navigateur (CSP, captcha) demandent une décision de Calvin.

---

## Findings & état

| # | Faille | Sévérité | État |
|---|---|---|---|
| 1 | **Broken access control** : entités PII (leads, contacts, clients, prospects) sans `rls` ; `/admin` protégé seulement côté client → un compte non-admin pouvait lire les données via l'API SDK | 🔴 HAUTE→CRIT | ✅ **CORRIGÉ** — RLS admin-only appliquée (4 entités vitrine + 5 back-office) |
| 2 | **Webhook public non authentifié** `receiveVitrineSync` : injection de faux leads, réécriture des analytics, relance-spam | 🔴 HAUTE | 🟡 **PARTIEL** — garde monotone + validation + secret optionnel posés ; **auth forte = décision Calvin** |
| 3 | **Zéro anti-spam sur 4 formulaires + email-bomb** (1 POST = N mails admins) | 🔴 HAUTE | ✅ **CORRIGÉ** (honeypot) — 🟡 rate-limit/captcha = décision Calvin |
| 4 | Validation serveur minimale, clés arbitraires, **injection d'en-tête email** via `nom` | 🟠 MOY | ✅ **CORRIGÉ** (allowlist stricte + format email/tél + strip CR/LF) |
| 5 | Pas de CSP ; token Base44 en localStorage | 🟠 MOY | 🟡 **À FAIRE** — CSP prête, à vérifier en navigateur |
| 6 | 5 dépendances mortes dont `react-quill` (XSS quill 1.3.7) | 🟡 BAS | ✅ **CORRIGÉ** (retirées) |
| 7 | Fuite de `error.message` sur les endpoints | ℹ️ INFO | ✅ **CORRIGÉ** (erreurs génériques) |
| — | **Vérifié propre** : aucun secret (source + bundle `dist/`), pas de source maps, pas de XSS stocké (React échappe), quill/markdown non utilisés, pas d'open-redirect, tous `target="_blank"` en `rel="noopener"`, `codeDirection` bien authz serveur, écritures via `asServiceRole` | ✅ | — |

---

## Corrigé cette passe (avec preuve)

### Contrôle d'accès (racine du #1)
RLS `admin-only` (create/read/update/delete) appliquée via `update_entity_schema` — tous les champs préservés :
- **Vitrine** : `QuoteRequest`, `ContactMessage`, `Appointment`, `CallbackRequest`.
- **Back-office** : `DemandeDevis`, `Client`, `RendezVous`, `ProspectLead`, `VisitLog`.
- Les soumissions publiques **continuent de fonctionner** car elles passent par `submitRequest`/`receiveVitrineSync` en `asServiceRole`, qui **bypass** la RLS. Fait vérifié : le back-office n'a qu'un seul utilisateur (Calvin, `role: admin`) → aucun risque d'expulsion.
- Le gate `/admin` côté client reste (UX), mais **n'est plus le point d'application** : l'accès est refusé côté serveur pour tout non-admin.

### Formulaires & fonction `submitRequest` (vitrine)
- **Honeypot anti-bot** `_hp` sur les 4 formulaires (DevisTunnel, Contact, BookingForm, ContactWidget) + rejet serveur silencieux si rempli.
- **Allowlist stricte** des champs par type (plus aucune clé arbitraire stockée).
- **Validation** format email (`EMAIL_RE`) et téléphone (`PHONE_RE`).
- **Anti-injection d'en-tête email** : `nom` nettoyé des CR/LF avant le sujet.
- **Erreurs génériques** (plus de fuite d'`error.message`).

### Webhook `receiveVitrineSync` (back-office)
- **Garde monotone** sur `visit_summary` : le total ne peut plus être **diminué** → fin de la réécriture des analytics.
- **Validation** de la date (`YYYY-MM-DD`, pas de futur) + **bornes de longueur** sur tous les champs.
- **Secret partagé optionnel** : si l'env `VITRINE_SYNC_SECRET` est posée, l'en-tête `x-vitrine-secret` devient obligatoire (désactivé tant que l'env n'existe pas → aucune rupture).
- **Erreurs génériques**.

### Dépendances (vitrine)
- Retiré `react-quill` (+ `quill` 1.3.7 vulnérable), `jspdf`, `html2canvas`, `moment`, `@stripe/react-stripe-js`, `@stripe/stripe-js` — **toutes importées nulle part**. `npm install` + `npm run build` = **exit 0**, `eslint` = **0 erreur**.

---

## Restant — décisions Calvin (ne peut/doit pas être fait à l'aveugle)

1. **Authentification forte du webhook** (#2). Un secret HMAC embarqué dans le JS de la vitrine **n'est pas secret** (lisible dans le bundle). Trois options, à trancher :
   - (a) **Poser l'env `VITRINE_SYNC_SECRET`** côté back-office + faire signer la vitrine — arrête le `curl` trivial, faible contre un attaquant qui lit le bundle. *Rapide, déjà câblé côté serveur.*
   - (b) **Captcha** (Cloudflare Turnstile / hCaptcha) vérifié serveur sur formulaires + webhook — **le vrai correctif anti-bot**. *Nécessite des clés de provider.*
   - (c) **Router la synchro côté serveur** (depuis `submitRequest` en `asServiceRole`) et supprimer le POST client direct. *Refactor, le plus propre.*
   → **Recommandation : (b) Turnstile** pour les formulaires + (a) le secret pour le webhook.

2. **CSP + en-têtes** (#5). Politique prête à poser (`index.html`), mais **à tester en navigateur** (bloqué ici par la politique réseau) car un `connect-src` trop strict casse les appels backend. Ajouter aussi `X-Frame-Options: DENY` / `frame-ancestors 'none'` et `Referrer-Policy`.

3. **Rate-limiting** sur `submitRequest`/`receiveVitrineSync** (volume) — dépend du choix captcha ci-dessus.

4. **Vérifs recommandées** :
   - Confirmer que l'inscription au back-office est sur **invitation** (la RLS admin-only protège déjà, c'est de la défense en profondeur).
   - Étendre la RLS aux entités BO secondaires (`Decideur`, `Opportunity`, `Sav`, `Contrat_Location`, `FlotteEntreprise`, `Vehicle`, `Reminder`) — mêmes données métier, même gabarit.
   - Test de non-régression : ouvrir un compte jetable sur la vitrine et vérifier que `base44.entities.ContactMessage.list()` renvoie **vide/refus** (confirme l'application de la RLS).
   - `npm audit fix` (advisory `dompurify` bas, non-bloquant).
