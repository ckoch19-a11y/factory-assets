import React, { useState } from "react";
import { base44 } from "@/api/base44Client";

/* Formulaire de contact — snippet de la recette (?pipeline=1, étape vitrine),
   stylé via les tokens Steep : inputs fond muted radius 16px, bouton pilule encre.
   Crée un enregistrement DemandeContact ; le back-office le consulte (/admin/demandes). */
export default function FormulaireContact({
  intro = "",
  confirmation = "Merci ! Nous revenons vers vous très vite.",
  telephone = "",
}) {
  const [form, setForm] = useState({ nom: "", email: "", telephone: "", message: "" });
  const [etat, setEtat] = useState("idle"); // idle | envoi | ok | erreur

  const champ = (nom) => (e) => setForm({ ...form, [nom]: e.target.value });

  const envoyer = async (e) => {
    e.preventDefault();
    setEtat("envoi");
    try {
      await base44.entities.DemandeContact.create(form);
      setEtat("ok");
    } catch {
      // CHOIX EXÉCUTANT : état d'erreur neutre (app cible non branchée ou réseau) —
      // le téléphone du salon reste proposé comme voie de secours.
      setEtat("erreur");
    }
  };

  if (etat === "ok") {
    return (
      <p className="text-center py-8 text-lg" role="status">
        {confirmation}
      </p>
    );
  }

  const classeInput =
    "w-full bg-muted rounded-input px-4 py-3 text-foreground placeholder:text-subtle border border-transparent focus:outline-none focus:border-foreground/30";

  return (
    <form onSubmit={envoyer} className="space-y-4 max-w-lg mx-auto">
      {intro && <p className="text-muted-foreground">{intro}</p>}
      <div>
        <label htmlFor="contact-nom" className="block text-xs uppercase tracking-widest text-subtle mb-1.5">
          Nom
        </label>
        <input id="contact-nom" required value={form.nom} onChange={champ("nom")} className={classeInput} autoComplete="name" />
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label htmlFor="contact-email" className="block text-xs uppercase tracking-widest text-subtle mb-1.5">
            Email
          </label>
          <input id="contact-email" type="email" value={form.email} onChange={champ("email")} className={classeInput} autoComplete="email" />
        </div>
        <div>
          <label htmlFor="contact-telephone" className="block text-xs uppercase tracking-widest text-subtle mb-1.5">
            Téléphone
          </label>
          <input id="contact-telephone" type="tel" value={form.telephone} onChange={champ("telephone")} className={classeInput} autoComplete="tel" />
        </div>
      </div>
      <div>
        <label htmlFor="contact-message" className="block text-xs uppercase tracking-widest text-subtle mb-1.5">
          Message
        </label>
        <textarea id="contact-message" required rows={5} value={form.message} onChange={champ("message")} className={classeInput} />
      </div>
      {etat === "erreur" && (
        <p className="text-sm text-accent-foreground bg-accent rounded-input px-4 py-3" role="alert">
          L'envoi n'a pas abouti. Réessayez dans un instant{telephone ? ` ou appelez-nous au ${telephone}` : ""}.
        </p>
      )}
      {/* Règle Steep : chaque pilule remplie est accompagnée d'une pilule ghost sur la même ligne. */}
      <div className="flex flex-col sm:flex-row gap-3 pt-2">
        <button
          type="submit"
          disabled={etat === "envoi"}
          className="flex-1 rounded-full bg-primary text-primary-foreground px-6 py-3 font-body-strong disabled:opacity-60"
        >
          {etat === "envoi" ? "Envoi…" : "Envoyer"}
        </button>
        {telephone && (
          <a
            href={`tel:${telephone.replace(/\s/g, "")}`}
            className="flex-1 text-center rounded-full border border-border bg-background text-foreground px-6 py-3 hover:bg-muted"
          >
            {telephone}
          </a>
        )}
      </div>
    </form>
  );
}
