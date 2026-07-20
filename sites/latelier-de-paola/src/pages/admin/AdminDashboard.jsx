import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { base44 } from "@/api/base44Client";

/* Tableau de bord (brief §5) : compteurs, badge « demandes nouvelles »
   en temps réel (subscribe), lien « voir le site ». */
export default function AdminDashboard() {
  const qc = useQueryClient();
  const { data: prestations = [] } = useQuery({
    queryKey: ["admin-prestations"],
    queryFn: () => base44.entities.Prestation.list("ordre"),
  });
  const { data: avis = [] } = useQuery({
    queryKey: ["admin-avis"],
    queryFn: () => base44.entities.Temoignage.list("-created_date"),
  });
  const { data: demandes = [] } = useQuery({
    queryKey: ["admin-demandes"],
    queryFn: () => base44.entities.DemandeContact.list("-created_date"),
  });

  useEffect(() => {
    const unsub = base44.entities.DemandeContact.subscribe(() =>
      qc.invalidateQueries({ queryKey: ["admin-demandes"] })
    );
    return unsub;
  }, [qc]);

  const nouvelles = demandes.filter((d) => d.statut !== "traitee").length;
  const tuiles = [
    { label: "Prestations visibles", valeur: prestations.filter((p) => p.visible !== false).length, to: "/admin/prestations" },
    { label: "Avis", valeur: avis.length, to: "/admin/avis" },
    { label: "Demandes reçues", valeur: demandes.length, to: "/admin/demandes", badge: nouvelles },
  ];

  return (
    <div>
      <div className="flex items-end justify-between gap-4 flex-wrap">
        <h1 className="text-display-md">Tableau de bord</h1>
        <a href="/" className="text-sm text-muted-foreground hover:text-foreground">
          Voir le site →
        </a>
      </div>
      <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4">
        {tuiles.map((t) => (
          <Link key={t.label} to={t.to} className="bg-background border border-border rounded-card p-5 hover:bg-muted/50">
            <p className="text-sm text-muted-foreground">{t.label}</p>
            <p className="mt-2 font-heading text-4xl">{t.valeur}</p>
            {t.badge > 0 && (
              <p className="mt-2 inline-block rounded-full bg-accent text-accent-foreground text-xs px-3 py-1">
                {t.badge} nouvelle{t.badge > 1 ? "s" : ""}
              </p>
            )}
          </Link>
        ))}
      </div>
      <p className="mt-8 text-sm text-muted-foreground">
        Les contenus du site (textes, photos, tarifs, avis) s'éditent dans les écrans ci-contre — le vitrine
        reflète chaque modification.
      </p>
    </div>
  );
}
