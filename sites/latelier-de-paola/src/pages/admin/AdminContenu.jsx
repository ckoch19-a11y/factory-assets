import React, { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { base44 } from "@/api/base44Client";
import { Champ, ChampZone, Interrupteur, BoutonPilule } from "@/components/admin/champs";

/* Contenus (brief §5) — SectionContenu, édition par clé :
   titre, sous_titre, texte, image_url, visible. Pattern ÉditeurEntite de la recette. */

function EditeurSection({ section, onMaj }) {
  const [form, setForm] = useState(section);
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
      await onMaj(section.id, patch);
      setEtat("ok");
    } catch {
      setEtat("erreur");
    }
  };

  return (
    <form onSubmit={enregistrer} className="bg-background border border-border rounded-card p-5 space-y-4">
      <div className="flex items-center justify-between gap-4">
        <p className="font-body-strong text-sm uppercase tracking-widest text-subtle">{section.cle}</p>
        <Interrupteur label="Visible" checked={form.visible} onChange={maj("visible")} />
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Champ label="Titre" value={form.titre} onChange={maj("titre")} />
        <Champ label="Sous-titre" value={form.sous_titre} onChange={maj("sous_titre")} />
      </div>
      <ChampZone label="Texte" value={form.texte} onChange={maj("texte")} rows={3} />
      <Champ label="Image (URL)" value={form.image_url} onChange={maj("image_url")} />
      <div className="flex items-center gap-3">
        <BoutonPilule type="submit" disabled={etat === "envoi"}>
          {etat === "envoi" ? "Enregistrement…" : "Enregistrer"}
        </BoutonPilule>
        {etat === "ok" && <span className="text-sm text-muted-foreground">Enregistré.</span>}
        {etat === "erreur" && <span className="text-sm text-accent-foreground">Échec — réessayez.</span>}
      </div>
    </form>
  );
}

export default function AdminContenu() {
  const qc = useQueryClient();
  const { data: sections = [], isFetched } = useQuery({
    queryKey: ["admin-sections"],
    queryFn: () => base44.entities.SectionContenu.list(),
  });

  const majSection = async (id, patch) => {
    await base44.entities.SectionContenu.update(id, patch);
    qc.invalidateQueries({ queryKey: ["admin-sections"] });
    qc.invalidateQueries({ queryKey: ["sections"] });
  };

  const triees = [...sections].sort((a, b) => (a.cle > b.cle ? 1 : -1));

  return (
    <div>
      <h1 className="text-display-md">Contenus</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Chaque bloc correspond à une section du vitrine (clé). Masquer un bloc le retire de la page.
      </p>
      <div className="mt-8 space-y-4">
        {triees.map((s) => (
          <EditeurSection key={s.id} section={s} onMaj={majSection} />
        ))}
        {isFetched && triees.length === 0 && (
          <p className="text-muted-foreground bg-background border border-border rounded-card p-5">
            Aucun contenu — lancez le seed initial (<code>npm run seed</code>) pour peupler les sections depuis le
            brief.
          </p>
        )}
      </div>
    </div>
  );
}
