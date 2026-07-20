import React from "react";
import { Link } from "react-router-dom";
import { useSiteConfig } from "@/hooks/useContenu";
import { SITE_CONFIG_SEED } from "@/content/fallbacks";

/* CHOIX EXÉCUTANT : page requise par les liens légaux du footer (brief S10).
   Décrit factuellement le seul traitement du site : le formulaire de contact
   (entité DemandeContact). Aucune autre collecte n'est mise en place. */
export default function Confidentialite() {
  const { data: config } = useSiteConfig();
  const c = { ...SITE_CONFIG_SEED, ...config };

  return (
    <main className="bg-background min-h-screen py-section px-6">
      <div className="max-w-2xl mx-auto">
        <Link to="/" className="text-sm text-muted-foreground hover:text-foreground">
          ← Retour au site
        </Link>
        <h1 className="mt-6 text-display-md">Politique de confidentialité</h1>

        <h2 className="mt-10 text-2xl">Données collectées</h2>
        <p className="mt-3 text-muted-foreground leading-relaxed">
          Le formulaire de contact recueille les informations que vous saisissez : nom, email, téléphone et message.
          Elles servent uniquement à répondre à votre demande et ne sont ni cédées ni utilisées à d'autres fins.
        </p>

        <h2 className="mt-10 text-2xl">Conservation et accès</h2>
        <p className="mt-3 text-muted-foreground leading-relaxed">
          Les demandes sont conservées dans l'outil de gestion du salon, accessible aux seules personnes habilitées,
          le temps nécessaire à leur traitement.
        </p>

        <h2 className="mt-10 text-2xl">Vos droits</h2>
        <p className="mt-3 text-muted-foreground leading-relaxed">
          Vous pouvez demander l'accès, la rectification ou la suppression de vos données en écrivant à {c.email} ou
          en appelant le {c.telephone}.
        </p>

        <h2 className="mt-10 text-2xl">Réservation en ligne</h2>
        <p className="mt-3 text-muted-foreground leading-relaxed">
          La prise de rendez-vous s'effectue sur Planity, qui applique sa propre politique de confidentialité.
        </p>
      </div>
    </main>
  );
}
