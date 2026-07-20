import React, { useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { base44 } from "@/api/base44Client";
import { BoutonPilule } from "@/components/admin/champs";

/* Demandes (brief §5) — boîte de réception des DemandeContact : lecture
   (coordonnées cliquables), action unique statut → « traitee », realtime. */
export default function AdminDemandes() {
  const qc = useQueryClient();
  const { data: demandes = [], isFetched } = useQuery({
    queryKey: ["admin-demandes"],
    queryFn: () => base44.entities.DemandeContact.list("-created_date"),
  });

  useEffect(() => {
    const unsub = base44.entities.DemandeContact.subscribe(() =>
      qc.invalidateQueries({ queryKey: ["admin-demandes"] })
    );
    return unsub;
  }, [qc]);

  const traiter = async (id) => {
    await base44.entities.DemandeContact.update(id, { statut: "traitee" });
    qc.invalidateQueries({ queryKey: ["admin-demandes"] });
  };

  return (
    <div>
      <h1 className="text-display-md">Demandes</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Les messages envoyés depuis le formulaire de contact du vitrine arrivent ici en temps réel.
      </p>
      <div className="mt-8 space-y-4">
        {demandes.map((d) => (
          <article key={d.id} className="bg-background border border-border rounded-card p-5">
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <p className="font-body-strong">{d.nom}</p>
              <div className="flex items-center gap-3">
                {d.created_date && (
                  <span className="text-xs text-subtle">
                    {new Date(d.created_date).toLocaleDateString("fr-FR", {
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                    })}
                  </span>
                )}
                {d.statut !== "traitee" ? (
                  <span className="rounded-full bg-accent text-accent-foreground text-xs px-3 py-1">nouvelle</span>
                ) : (
                  <span className="rounded-full bg-muted text-muted-foreground text-xs px-3 py-1">traitée</span>
                )}
              </div>
            </div>
            <div className="mt-2 flex gap-4 flex-wrap text-sm text-muted-foreground">
              {d.email && (
                <a href={`mailto:${d.email}`} className="hover:text-foreground">
                  {d.email}
                </a>
              )}
              {d.telephone && (
                <a href={`tel:${String(d.telephone).replace(/\s/g, "")}`} className="hover:text-foreground">
                  {d.telephone}
                </a>
              )}
            </div>
            <p className="mt-4 whitespace-pre-wrap">{d.message}</p>
            {d.statut !== "traitee" && (
              <div className="mt-4">
                <BoutonPilule onClick={() => traiter(d.id)}>Marquer traitée</BoutonPilule>
              </div>
            )}
          </article>
        ))}
        {isFetched && demandes.length === 0 && (
          <p className="text-muted-foreground bg-background border border-border rounded-card p-5">
            Aucune demande pour le moment.
          </p>
        )}
      </div>
    </div>
  );
}
