import React, { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { base44 } from "@/api/base44Client";
import { Champ, ChampZone, Interrupteur, BoutonPilule } from "@/components/admin/champs";

/* Avis (brief §5) — CRUD complet sur Temoignage : auteur, texte, note, source,
   date, visible. Ne jamais inventer d'avis : n'ajouter que des avis vérifiés
   (ex. relevés sur Planity). */

function EditeurAvis({ avis, onMaj, onSupprime }) {
  const [form, setForm] = useState(avis);
  const [etat, setEtat] = useState("idle");
  const maj = (cle) => (valeur) => {
    setForm({ ...form, [cle]: valeur });
    setEtat("idle");
  };

  const enregistrer = async (e) => {
    e.preventDefault();
    setEtat("envoi");
    try {
      const { id, created_date, updated_date, created_by_id, ...patch } = form;
      await onMaj(avis.id, patch);
      setEtat("ok");
    } catch {
      setEtat("erreur");
    }
  };

  return (
    <form onSubmit={enregistrer} className="bg-background border border-border rounded-card p-5 space-y-4">
      <div className="flex items-center justify-between gap-4">
        <p className="font-body-strong">{avis.auteur}</p>
        <Interrupteur label="Visible" checked={form.visible} onChange={maj("visible")} />
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Champ label="Auteur" value={form.auteur} onChange={maj("auteur")} />
        <Champ label="Note (sur 5)" type="number" value={form.note} onChange={maj("note")} />
        <Champ label="Source" value={form.source} onChange={maj("source")} />
        <Champ label="Date" type="date" value={form.date} onChange={maj("date")} />
      </div>
      <ChampZone label="Texte de l'avis" value={form.texte} onChange={maj("texte")} rows={3} />
      <div className="flex items-center gap-3">
        <BoutonPilule type="submit" disabled={etat === "envoi"}>
          {etat === "envoi" ? "Enregistrement…" : "Enregistrer"}
        </BoutonPilule>
        <BoutonPilule ghost onClick={() => onSupprime(avis.id)}>
          Supprimer
        </BoutonPilule>
        {etat === "ok" && <span className="text-sm text-muted-foreground">Enregistré.</span>}
        {etat === "erreur" && <span className="text-sm text-accent-foreground">Échec — réessayez.</span>}
      </div>
    </form>
  );
}

export default function AdminAvis() {
  const qc = useQueryClient();
  const { data: avis = [], isFetched } = useQuery({
    queryKey: ["admin-avis"],
    queryFn: () => base44.entities.Temoignage.list("-created_date"),
  });

  const invalider = () => {
    qc.invalidateQueries({ queryKey: ["admin-avis"] });
    qc.invalidateQueries({ queryKey: ["temoignages"] });
  };

  const creer = async () => {
    // Gabarit neutre à compléter avec un avis vérifié — jamais de faux avis.
    await base44.entities.Temoignage.create({ auteur: "À compléter", texte: "À compléter", note: 5 });
    invalider();
  };
  const majAvis = async (id, patch) => {
    await base44.entities.Temoignage.update(id, patch);
    invalider();
  };
  const supprimer = async (id) => {
    await base44.entities.Temoignage.delete(id);
    invalider();
  };

  return (
    <div>
      <div className="flex items-end justify-between gap-4 flex-wrap">
        <h1 className="text-display-md">Avis</h1>
        <BoutonPilule onClick={creer}>Nouvel avis</BoutonPilule>
      </div>
      <p className="mt-2 text-sm text-muted-foreground">
        N'ajoutez que des avis clients réels (relevés sur Planity, par exemple) — jamais d'avis inventés.
      </p>
      <div className="mt-8 space-y-4">
        {avis.map((a) => (
          <EditeurAvis key={a.id} avis={a} onMaj={majAvis} onSupprime={supprimer} />
        ))}
        {isFetched && avis.length === 0 && (
          <p className="text-muted-foreground bg-background border border-border rounded-card p-5">
            Aucun avis — lancez le seed initial (<code>npm run seed</code>) pour importer les deux avis vérifiés du
            brief.
          </p>
        )}
      </div>
    </div>
  );
}
