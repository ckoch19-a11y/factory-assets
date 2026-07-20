import { createClient } from "@base44/sdk";

// CHOIX EXÉCUTANT : dépôt autonome (hors app Base44) — l'app id cible vient de
// VITE_BASE44_APP_ID (fichier .env) et sera renseigné au déploiement. Tant qu'il
// est absent, les lectures échouent silencieusement et la vitrine affiche les
// fallbacks du brief (principe pipeline : le site n'est jamais cassé).
export const base44 = createClient({
  appId: import.meta.env.VITE_BASE44_APP_ID || "APP_ID_A_RENSEIGNER",
  requiresAuth: false,
});
