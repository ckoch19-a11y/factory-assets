import React from "react";
import { Link } from "react-router-dom";
import { useSiteConfig } from "@/hooks/useContenu";
import { SITE_CONFIG_SEED } from "@/content/fallbacks";

/* CHOIX EXÉCUTANT : page requise par les liens légaux du footer (brief S10).
   Contenu strictement factuel issu du brief §1 (légal, coordonnées, directrice
   de publication) ; l'hébergeur n'est pas documenté → placeholder neutre. */
export default function MentionsLegales() {
  const { data: config } = useSiteConfig();
  const c = { ...SITE_CONFIG_SEED, ...config };

  return (
    <main className="bg-background min-h-screen py-section px-6">
      <div className="max-w-2xl mx-auto">
        <Link to="/" className="text-sm text-muted-foreground hover:text-foreground">
          ← Retour au site
        </Link>
        <h1 className="mt-6 text-display-md">Mentions légales</h1>

        <h2 className="mt-10 text-2xl">Éditeur du site</h2>
        <p className="mt-3 text-muted-foreground leading-relaxed">
          {c.nom}
          <br />
          {c.adresse}
          <br />
          Téléphone : {c.telephone} · Email : {c.email}
        </p>
        <p className="mt-3 text-muted-foreground leading-relaxed">
          SIRET 438 004 681 00013 · APE 9602A · TVA intracommunautaire FR63438004681
        </p>
        <p className="mt-3 text-muted-foreground leading-relaxed">Directrice de publication : Paola Sonza.</p>

        <h2 className="mt-10 text-2xl">Hébergement</h2>
        <p className="mt-3 text-muted-foreground leading-relaxed">
          Hébergeur : NON TROUVÉ — à confirmer par le client.
        </p>

        <h2 className="mt-10 text-2xl">Propriété intellectuelle</h2>
        <p className="mt-3 text-muted-foreground leading-relaxed">
          L'ensemble des contenus de ce site (textes, photographies, identité visuelle) appartient à {c.nom}, sauf
          mention contraire. Toute reproduction sans autorisation est interdite.
        </p>
      </div>
    </main>
  );
}
