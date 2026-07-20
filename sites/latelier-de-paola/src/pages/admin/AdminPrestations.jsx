import React, { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { base44 } from "@/api/base44Client";
import { Champ, ChampZone, Interrupteur, BoutonPilule } from "@/components/admin/champs";

/* Prestations & tarifs (brief §5) — CRUD complet sur Prestation :
   création, édition, suppression, toggle visible. Toute la grille tarifaire
   s'édite ici (categorie = groupe du tableau B ; "carte-accueil" = cartes S3). */

function EditeurPrestation({ prestation, onMaj, onSupprime }) {
  const [form, setForm] = useState(prestation);
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
      await onMaj(prestation.id, patch);
      setEtat("ok");
    } catch {
      setEtat("erreur");
    }
  };

  return (
    <form onSubmit={enregistrer} className="bg-background border border-border rounded-card p-5 space-y-4">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <p className="font-body-strong">{prestation.nom}</p>
        <div className="flex items-center gap-4">
          <Interrupteur label="Visible" checked={form.visible} onChange={maj("visible")} />
          <Interrupteur label="Vedette" checked={form.vedette === true} onChange={maj("vedette")} />
        </div>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Champ label="Nom" value={form.nom} onChange={maj("nom")} />
        <Champ label="Catégorie (groupe de tarifs ou carte-accueil)" value={form.categorie} onChange={maj("categorie")} />
        <Champ label="Prix (verbatim)" value={form.prix} onChange={maj("prix")} />
        <Champ label="Durée" value={form.duree} onChange={maj("duree")} />
        <Champ label="Ordre dans le groupe" type="number" value={form.ordre} onChange={maj("ordre")} />
        <Champ label="Image (URL)" value={form.image_url} onChange={maj("image_url")} />
      </div>
      <ChampZone label="Description / détail" value={form.description} onChange={maj("description")} rows={2} />
      <div className="flex items-center gap-3">
        <BoutonPilule type="submit" disabled={etat === "envoi"}>
          {etat === "envoi" ? "Enregistrement…" : "Enregistrer"}
        </BoutonPilule>
        <BoutonPilule ghost onClick={() => onSupprime(prestation.id)}>
          Supprimer
        </BoutonPilule>
        {etat === "ok" && <span className="text-sm text-muted-foreground">Enregistré.</span>}
        {etat === "erreur" && <span className="text-sm text-accent-foreground">Échec — réessayez.</span>}
      </div>
    </form>
  );
}

export default function AdminPrestations() {
  const qc = useQueryClient();
  const { data: prestations = [], isFetched } = useQuery({
    queryKey: ["admin-prestations"],
    queryFn: () => base44.entities.Prestation.list("ordre"),
  });

  const invalider = () => {
    qc.invalidateQueries({ queryKey: ["admin-prestations"] });
    qc.invalidateQueries({ queryKey: ["prestations"] });
  };

  const creer = async () => {
    await base44.entities.Prestation.create({ nom: "Nouvelle prestation" });
    invalider();
  };
  const majPrestation = async (id, patch) => {
    await base44.entities.Prestation.update(id, patch);
    invalider();
  };
  const supprimer = async (id) => {
    await base44.entities.Prestation.delete(id);
    invalider();
  };

  const triees = [...prestations].sort(
    (a, b) => (a.categorie ?? "").localeCompare(b.categorie ?? "") || (a.ordre ?? 0) - (b.ordre ?? 0)
  );

  return (
    <div>
      <div className="flex items-end justify-between gap-4 flex-wrap">
        <h1 className="text-display-md">Prestations & tarifs</h1>
        <BoutonPilule onClick={creer}>Nouvelle prestation</BoutonPilule>
      </div>
      <p className="mt-2 text-sm text-muted-foreground">
        La grille des tarifs du vitrine est groupée par catégorie ; les cartes de la page d'accueil portent la
        catégorie « carte-accueil » (ordre 1 à 5).
      </p>
      <div className="mt-8 space-y-4">
        {triees.map((p) => (
          <EditeurPrestation key={p.id} prestation={p} onMaj={majPrestation} onSupprime={supprimer} />
        ))}
        {isFetched && triees.length === 0 && (
          <p className="text-muted-foreground bg-background border border-border rounded-card p-5">
            Aucune prestation — lancez le seed initial (<code>npm run seed</code>) pour importer la grille du brief.
          </p>
        )}
      </div>
    </div>
  );
}
