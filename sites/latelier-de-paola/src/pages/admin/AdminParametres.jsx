import React, { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { base44 } from "@/api/base44Client";
import { Champ, ChampZone, BoutonPilule } from "@/components/admin/champs";
import { SITE_CONFIG_SEED } from "@/content/fallbacks";

/* Paramètres (brief §5) — SiteConfig, un seul enregistrement.
   url_source et brief en lecture seule. Crée l'enregistrement s'il n'existe pas. */
const CHAMPS = [
  ["nom", "Nom"],
  ["slogan", "Slogan"],
  ["adresse", "Adresse"],
  ["telephone", "Téléphone"],
  ["email", "Email"],
  ["horaires", "Horaires"],
  ["instagram", "Instagram"],
  ["facebook", "Facebook"],
  ["url_rdv", "Réservation en ligne (URL)"],
  ["siret", "SIRET"],
  ["tva", "TVA"],
];

export default function AdminParametres() {
  const qc = useQueryClient();
  const { data: config, isFetched } = useQuery({
    queryKey: ["admin-siteconfig"],
    queryFn: async () => (await base44.entities.SiteConfig.list())[0] ?? null,
  });

  const [form, setForm] = useState(null);
  const [etat, setEtat] = useState("idle"); // idle | envoi | ok | erreur

  useEffect(() => {
    if (isFetched && form === null) setForm(config ?? { ...SITE_CONFIG_SEED });
  }, [isFetched, config, form]);

  if (form === null) return <p className="text-muted-foreground">Chargement…</p>;

  const maj = (cle) => (valeur) => {
    setForm({ ...form, [cle]: valeur });
    setEtat("idle");
  };

  const enregistrer = async (e) => {
    e.preventDefault();
    setEtat("envoi");
    try {
      const { id, created_date, updated_date, created_by_id, ...patch } = form;
      if (config?.id) await base44.entities.SiteConfig.update(config.id, patch);
      else await base44.entities.SiteConfig.create(patch);
      qc.invalidateQueries({ queryKey: ["admin-siteconfig"] });
      qc.invalidateQueries({ queryKey: ["siteconfig"] });
      setEtat("ok");
    } catch {
      setEtat("erreur");
    }
  };

  return (
    <div>
      <h1 className="text-display-md">Paramètres</h1>
      <form onSubmit={enregistrer} className="mt-8 bg-background border border-border rounded-card p-5 space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {CHAMPS.map(([cle, label]) => (
            <Champ key={cle} label={label} value={form[cle]} onChange={maj(cle)} />
          ))}
        </div>
        <ChampZone label="Description" value={form.description} onChange={maj("description")} rows={3} />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Champ label="URL source (lecture seule)" value={form.url_source} readOnly />
          <Champ
            label="Brief rejouable (lecture seule)"
            value={form.brief ? "Présent — géré par le pipeline" : "—"}
            readOnly
          />
        </div>
        <div className="flex items-center gap-3">
          <BoutonPilule type="submit" disabled={etat === "envoi"}>
            {etat === "envoi" ? "Enregistrement…" : "Enregistrer"}
          </BoutonPilule>
          {etat === "ok" && <span className="text-sm text-muted-foreground">Enregistré.</span>}
          {etat === "erreur" && <span className="text-sm text-accent-foreground">Échec de l'enregistrement — réessayez.</span>}
        </div>
      </form>
    </div>
  );
}
