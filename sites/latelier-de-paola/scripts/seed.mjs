/* Seed des données initiales du brief (§4) vers l'app Base44 cible.
   Usage : BASE44_APP_ID=xxx BASE44_API_KEY=xxx npm run seed
   CHOIX EXÉCUTANT : REST Base44 (POST /api/apps/<id>/entities/<Entité>, en-tête
   api_key) — un create par enregistrement, idempotence assurée par un contrôle
   « la table est-elle vide ? » avant insertion. */

import {
  SITE_CONFIG_SEED,
  TEMOIGNAGES_SEED,
  PRESTATIONS_SEED,
  SECTIONS_SEED,
} from "../src/content/fallbacks.js";

const APP_ID = process.env.BASE44_APP_ID;
const API_KEY = process.env.BASE44_API_KEY;
const BASE = process.env.BASE44_API_BASE || "https://app.base44.com";

if (!APP_ID || !API_KEY) {
  console.error("BASE44_APP_ID et BASE44_API_KEY sont requis. Exemple :");
  console.error("  BASE44_APP_ID=xxx BASE44_API_KEY=xxx npm run seed");
  process.exit(1);
}

const url = (entity) => `${BASE}/api/apps/${APP_ID}/entities/${entity}`;
const headers = { api_key: API_KEY, "Content-Type": "application/json" };

async function liste(entity) {
  const res = await fetch(url(entity), { headers });
  if (!res.ok) throw new Error(`${entity} GET → ${res.status} ${await res.text()}`);
  return res.json();
}

async function cree(entity, record) {
  const res = await fetch(url(entity), { method: "POST", headers, body: JSON.stringify(record) });
  if (!res.ok) throw new Error(`${entity} POST → ${res.status} ${await res.text()}`);
  return res.json();
}

async function seedEntite(entity, records) {
  const existants = await liste(entity);
  if (Array.isArray(existants) && existants.length > 0) {
    console.log(`↷ ${entity} : ${existants.length} enregistrement(s) déjà présents — seed ignoré.`);
    return;
  }
  for (const record of records) await cree(entity, record);
  console.log(`✓ ${entity} : ${records.length} enregistrement(s) créés.`);
}

async function main() {
  await seedEntite("SiteConfig", [SITE_CONFIG_SEED]);
  await seedEntite("Prestation", PRESTATIONS_SEED);
  await seedEntite("Temoignage", TEMOIGNAGES_SEED);
  await seedEntite("SectionContenu", SECTIONS_SEED);
  // DemandeContact : aucun enregistrement initial (brief §4.5).
  console.log("Seed terminé.");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
